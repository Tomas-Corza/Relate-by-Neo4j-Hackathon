"""Local-only synthetic CSV importer for the existing Nexus Relate schema."""
import argparse
import csv
import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory

import relate
from attribution import MODELS, parse_time
from graph import analyze, rows
from finance import financial_summary
from inventory import inventory_summary
from intelligence import graph_counts
from customer_economics import customer_economics

SCHEMAS = {
    "products": ("id", "name", "price", "cost", "stock"),
    "campaigns": ("id", "name", "channel", "spend", "product_id"),
    "customers": ("id",),
    "touchpoints": ("id", "customer_id", "campaign_id", "at"),
    "orders": ("id", "customer_id", "product_id", "at", "revenue"),
}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ROWS = 5000
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}")
MONEY = re.compile(r"[0-9]{1,9}(?:\.[0-9]{1,2})?")
INTEGER = re.compile(r"[0-9]{1,9}")

def fail(table, line, reason):
    raise ValueError(f"{table}.csv line {line}: {reason}")

def load_dataset(directory):
    """Validate all five files before creating any database."""
    directory = Path(directory)
    data, all_ids = {}, set()
    for table, fields in SCHEMAS.items():
        path = directory / (table + ".csv")
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f"{table}.csv missing or exceeds 2 MiB")
        records = []
        names = set()
        try:
            with path.open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, strict=True)
                if tuple(reader.fieldnames or ()) != fields:
                    fail(table, 1, "expected header " + ",".join(fields))
                for row in reader:
                    line = reader.line_num
                    if len(records) >= MAX_ROWS:
                        fail(table, line, "maximum 5000 rows per file")
                    if None in row or any(v is None or not v.strip() for v in row.values()):
                        fail(table, line, "missing, blank or extra fields")
                    row = {k: v.strip() for k, v in row.items()}
                    if any(len(v)>120 or any(ord(c)<32 or ord(c)==127 for c in v) for v in row.values()):
                        fail(table, line, "fields must be printable and at most 120 characters")
                    if not ID.fullmatch(row["id"]) or row["id"] in all_ids:
                        fail(table, line, "invalid or duplicate globally unique id")
                    if row["id"] == "Unattributed":
                        fail(table, line, "reserved id")
                    all_ids.add(row["id"])
                    if table in ("products", "campaigns"):
                        # Existing financial/inventory queries group by product name.
                        name = row["name"].casefold()
                        if name in names:
                            fail(table, line, "duplicate name")
                        names.add(name)
                    for key in ("price", "cost", "spend", "revenue"):
                        if key in row:
                            if not MONEY.fullmatch(row[key]):
                                fail(table, line, f"{key} must be nonnegative currency with at most two decimals")
                            amount = Decimal(row[key])
                            if key in ("price", "revenue") and amount == 0:
                                fail(table, line, f"{key} must be positive")
                            # Preserve canonical integer money values; fractional cents-safe values remain floats.
                            row[key] = int(amount) if amount == amount.to_integral_value() else float(amount)
                    if "stock" in row:
                        if not INTEGER.fullmatch(row["stock"]):
                            fail(table, line, "stock must be a nonnegative integer")
                        row["stock"] = int(row["stock"])
                    if "at" in row:
                        try:
                            dt = parse_time(row["at"])
                            if not 1901 <= dt.year <= 9998:
                                raise ValueError("timestamp outside supported years")
                            row["at"] = dt.isoformat()
                        except (ValueError, OverflowError):
                            fail(table, line, "timestamp must be ISO-8601 with explicit timezone, UTC year 1901–9998")
                    row["_line"] = line
                    records.append(row)
        except (csv.Error, UnicodeError, InvalidOperation) as exc:
            raise ValueError(f"{table}.csv: invalid CSV or encoding") from exc
        if table in ("products", "campaigns", "customers") and not records:
            raise ValueError(f"{table}.csv must contain at least one record")
        data[table] = records
    ids = {table: {r["id"] for r in records} for table, records in data.items()}
    for table, links in {
        "campaigns": {"product_id": "products"},
        "touchpoints": {"customer_id": "customers", "campaign_id": "campaigns"},
        "orders": {"customer_id": "customers", "product_id": "products"},
    }.items():
        for record in data[table]:
            for field, target in links.items():
                if record[field] not in ids[target]:
                    fail(table, record["_line"], f"{field} does not reference a known {target} record")
    return {t: [{k:v for k,v in row.items() if k!="_line"} for row in records]
            for t,records in data.items()}

def write_graph(db, data):
    queries = {
        "products": "CREATE (:Product {id:$id,name:$name,price:$price,cost:$cost,stock:$stock})",
        "campaigns": "MATCH (p:Product {id:$product_id}) CREATE (c:Campaign {id:$id,name:$name,channel:$channel,spend:$spend})-[:PROMOTES]->(p)",
        "customers": "CREATE (:Customer {id:$id})",
        "touchpoints": "MATCH (u:Customer {id:$customer_id}), (c:Campaign {id:$campaign_id}) CREATE (u)-[:HAS_TOUCH]->(t:Touchpoint {id:$id,at:$at})-[:FROM_CAMPAIGN]->(c)",
        "orders": "MATCH (u:Customer {id:$customer_id}), (p:Product {id:$product_id}) CREATE (u)-[:PLACED]->(o:Order {id:$id,at:$at,revenue:$revenue})-[:CONTAINS]->(p)",
    }
    for table, query in queries.items():
        for record in data[table]:
            db.execute(query, record)
    nodes, edges = graph_counts(db)
    expected_nodes = {label:len(data[table]) for label,table in
                      zip(("Product","Campaign","Customer","Touchpoint","Order"),SCHEMAS)}
    expected_edges = {"PROMOTES":len(data["campaigns"]),
                      "HAS_TOUCH":len(data["touchpoints"]),"FROM_CAMPAIGN":len(data["touchpoints"]),
                      "PLACED":len(data["orders"]),"CONTAINS":len(data["orders"])}
    if nodes != expected_nodes or edges != expected_edges:
        raise ValueError("Imported graph counts do not match validated records")
    db.commit()

def summarize_store(path, model="linear"):
    path = Path(path)
    if not path.is_file() or path.suffix != ".rl":
        raise ValueError("Existing .rl store required")
    db = relate.connect(str(path), read_only=True)
    try:
        nodes,edges = graph_counts(db)
        attribution,campaigns = analyze(db,model)
        economics = customer_economics(rows(db,"touches"),rows(db,"orders"),attribution,campaigns)
        return {"model":model,"nodes":nodes,"edges":edges,"financials":financial_summary(db),
                "inventory":inventory_summary(db),"attribution":attribution["totals"],
                "campaigns":campaigns,"customer_economics":economics,
                "limitations":"Synthetic single-unit purchases, fixed product cost and spend snapshots; attribution is descriptive, not causal."}
    finally:
        db.close()

def import_dataset(directory, output):
    """Stage a new store, verify reopening and analytics, then publish without overwrite."""
    output = Path(output)
    if output.suffix != ".rl" or output.exists() or output.is_symlink():
        raise ValueError("Choose a new .rl file; existing files are never overwritten")
    data = load_dataset(directory)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".nexus-import-", dir=output.parent) as temp:
        stage = Path(temp) / "dataset.rl"
        db = relate.connect(str(stage))
        try:
            write_graph(db, data)
        finally:
            db.close()
        report = summarize_store(stage)
        # Same filesystem, atomic no-clobber publication; local filesystems only.
        os.link(stage, output)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    validate=sub.add_parser("validate",help="Validate CSVs without creating a graph")
    validate.add_argument("directory",type=Path)
    build=sub.add_parser("import",help="Create a new persistent .rl store")
    build.add_argument("directory",type=Path)
    build.add_argument("output",type=Path)
    inspect=sub.add_parser("summary",help="Analyze an existing store read-only")
    inspect.add_argument("path",type=Path)
    inspect.add_argument("--model",choices=MODELS,default="linear")
    args=parser.parse_args()
    try:
        if args.command=="validate":
            result={"status":"valid","records":{k:len(v) for k,v in load_dataset(args.directory).items()}}
        elif args.command=="import":
            result=import_dataset(args.directory,args.output)
        else:
            result=summarize_store(args.path,args.model)
    except (ValueError,OSError) as exc:
        parser.exit(2,f"Import error: {exc}\n")
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=="__main__":
    main()
