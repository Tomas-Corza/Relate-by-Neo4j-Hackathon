"""Export the actual canonical synthetic Relate graph as importer-compatible CSVs."""
import argparse
import csv
import io
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from graph import demo_graph
from network import network
from dataset_import import SCHEMAS

def export_csvs(db):
    graph=network(db)
    links={}
    for edge in graph["edges"]:
        if edge["type"] not in ("PROMOTES","FROM_CAMPAIGN","CONTAINS"):
            continue
        key=(edge["type"],edge["source"])
        if key in links:
            raise ValueError("Unexpected multiple outgoing relationships")
        links[key]=edge["target"]
    # Each touch and order has one incoming customer edge; customers may have many.
    owners={}
    for edge in graph["edges"]:
        if edge["type"] in ("HAS_TOUCH","PLACED"):
            key=(edge["type"],edge["target"])
            if key in owners:
                raise ValueError("Unexpected multiple customer owners")
            owners[key]=edge["source"]
    data={table:[] for table in SCHEMAS}
    for node in graph["nodes"]:
        p=dict(node["properties"])
        kind=node["type"]
        if kind=="Product":
            table="products"
        elif kind=="Campaign":
            table="campaigns"
            p["product_id"]=links[("PROMOTES",p["id"])]
        elif kind=="Customer":
            table="customers"
        elif kind=="Touchpoint":
            table="touchpoints"
            p["customer_id"]=owners[("HAS_TOUCH",p["id"])]
            p["campaign_id"]=links[("FROM_CAMPAIGN",p["id"])]
        elif kind=="Order":
            table="orders"
            p["customer_id"]=owners[("PLACED",p["id"])]
            p["product_id"]=links[("CONTAINS",p["id"])]
        else:
            raise ValueError("Unexpected graph node")
        data[table].append(p)
    result={}
    for table,fields in SCHEMAS.items():
        stream=io.StringIO(newline="")
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(data[table],key=lambda r:r["id"]))
        result[table+".csv"]=stream.getvalue()
    return result

def canonical_csvs():
    with demo_graph() as db:
        return export_csvs(db)

def canonical_zip():
    stream=io.BytesIO()
    with ZipFile(stream,"w",compression=ZIP_DEFLATED) as archive:
        for filename,content in canonical_csvs().items():
            archive.writestr(filename,content)
    return stream.getvalue()

def export_demo(directory):
    directory=Path(directory)
    contents=canonical_csvs()
    directory.mkdir(parents=True,exist_ok=False)
    for filename,content in contents.items():
        (directory/filename).write_text(content,encoding="utf-8")
    return directory

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path,help="New output directory")
    args=parser.parse_args()
    print(export_demo(args.directory))
