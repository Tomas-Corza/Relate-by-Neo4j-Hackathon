"""Local opt-in benchmark; never called by the public app."""
import argparse
import csv
import hashlib
import json
import os
import random
import time
from pathlib import Path
from graph import demo_graph, analyze, rows
from network import network
from finance import financial_summary
from inventory import inventory_summary
from intelligence import compare_models, scenario
from sensitivity import sensitivity
from investigation import execute

PROTOCOL=Path(__file__).with_name("benchmark_protocol.json")
ARMS=("A","B","N")
SYSTEM=("Answer only from supplied synthetic evidence. Cite record IDs or evidence IDs. "
        "Distinguish facts, assumptions and recommendations. If evidence is insufficient, say so. "
        "Do not claim causal effects, net income, forecasts or executed changes. Be concise.")

def inputs(db,case):
    _,campaigns=analyze(db,"linear")
    trace_answer,trace=execute(db,case["question"],"linear")
    # B deliberately receives the same derived facts plus full flat raw records.
    # Strip graph-specific trace metadata but preserve analytical outputs.
    g=network(db)
    flat={"nodes":[dict(type=n["type"],**n["properties"]) for n in g["nodes"]],
          "relationships":g["edges"],"orders":rows(db,"orders"),"touches":rows(db,"touches"),
          "campaigns":campaigns,"analytical_tables":{t["tool"]:t["evidence"] for t in trace},
          "analysis_parameters":{t["tool"]:t["parameters"] for t in trace}}
    # A has metrics only, no promoted product or inventory fields.
    a=[{k:c[k] for k in ("campaign_id","campaign","channel","spend","revenue","gross_profit","profit_after_ads","roas")} for c in campaigns]
    return {"A":a,"B":flat,"N":trace}

def references(db):
    _,cs=analyze(db,"linear")
    paid=[c for c in cs if c["spend"]>0]
    source=min(paid,key=lambda c:c["gross_profit"]/c["spend"])
    target=max((c for c in paid if c["campaign_id"]!=source["campaign_id"] and c["stock"]>=10),key=lambda c:c["gross_profit"]/c["spend"])
    amount=min(300,source["spend"])
    records,warnings=scenario(cs,source["campaign_id"],target["campaign_id"],amount,.5)
    return {"campaigns":cs,"inventory":inventory_summary(db),"financials":financial_summary(db),
      "U001_journey":rows(db,"journey",{"customer":"U001"}),"U001_orders":rows(db,"customer_orders",{"customer":"U001"}),
      "sensitivity":sensitivity(compare_models(db)),
      "scenario":{"source":source["campaign_id"],"target":target["campaign_id"],"amount":amount,"efficiency":.5,
      "profit_delta":round(sum(r["scenario_profit"]-r["baseline_profit"] for r in records),2),"records":records,"warnings":warnings}}

def prepare():
    protocol=json.loads(PROTOCOL.read_text())
    with demo_graph() as db:
        refs=references(db)
        data={c["id"]:inputs(db,c) for c in protocol["cases"]}
    return protocol,refs,data

def save(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")

def run(out,model,live=False):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    protocol,refs,data=prepare()
    save(out/"protocol.json",protocol)
    save(out/"reference_answers.json",refs)
    save(out/"inputs.json",data)
    jobs=[(c,arm) for c in protocol["cases"] for arm in ARMS]
    random.Random(42).shuffle(jobs)
    save(out/"manifest.json",{"status":"pending" if not live else "running","model":model,"attempt_limit":len(jobs),
      "protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"seed":42,"max_completion_tokens":500,
      "note":"Single trial per arm/question; no causal or statistical significance claim."})
    metrics=list(protocol["weights"])
    with (out/"scorecard.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["response_id","question_id",*metrics,"review_notes"])
        for i,(c,arm) in enumerate(jobs,1):w.writerow([f"R{i:02}",c["id"],*[""]*len(metrics),""])
    if not live:return
    if not os.getenv("OPENAI_API_KEY"):raise RuntimeError("Set OPENAI_API_KEY locally before --live.")
    from openai import OpenAI
    client=OpenAI(timeout=60,max_retries=0)
    results=[]
    for i,(case,arm) in enumerate(jobs,1):
        rid=f"R{i:02}"
        payload=json.dumps({"question":case["question"],"evidence":data[case["id"]][arm]},ensure_ascii=False)
        start=time.monotonic()
        try:
            response=client.chat.completions.create(model=model,store=False,max_completion_tokens=500,messages=[{"role":"system","content":SYSTEM},{"role":"user","content":payload}])
            usage=response.usage
            r={"response_id":rid,"question_id":case["id"],"arm":arm,"status":"ok","response":response.choices[0].message.content,
               "resolved_model":response.model,"input_tokens":usage.prompt_tokens if usage else None,"output_tokens":usage.completion_tokens if usage else None}
        except Exception as exc:
            r={"response_id":rid,"question_id":case["id"],"arm":arm,"status":"error","error_type":type(exc).__name__}
        r["elapsed_seconds"]=round(time.monotonic()-start,3)
        results.append(r)
        save(out/"raw_responses.json",results)
    save(out/"blind_responses.json",[{k:v for k,v in r.items() if k not in ("arm","resolved_model","elapsed_seconds","input_tokens","output_tokens")} for r in results])
    manifest=json.loads((out/"manifest.json").read_text());manifest["status"]="complete" if all(r["status"]=="ok" for r in results) else "incomplete";save(out/"manifest.json",manifest)

def score(out):
    out=Path(out)
    protocol=json.loads((out/"protocol.json").read_text())
    responses=json.loads((out/"raw_responses.json").read_text())
    weights=protocol["weights"]
    with (out/"scorecard.csv").open(newline="") as f: ratings=list(csv.DictReader(f))
    byid={r["response_id"]:r for r in responses}
    if len(ratings)!=len(byid) or set(r["response_id"] for r in ratings)!=set(byid):
        raise ValueError("Scorecard must contain every response exactly once.")
    sums={arm:[] for arm in ARMS}
    for r in ratings:
        original=byid[r["response_id"]]
        if original["status"]!="ok":raise ValueError("Incomplete runs cannot be scored as complete.")
        values={k:float(r[k]) for k in weights}
        if any(v not in (0,.5,1) for v in values.values()):raise ValueError("Use 0, 0.5 or 1 only.")
        if not r["review_notes"].strip():raise ValueError("Document scoring rationale for each response.")
        sums[original["arm"]].append(values)
    result={arm:{"n":len(v),"criteria_pct":{k:round(100*sum(x[k] for x in v)/len(v),2) for k in weights},
      "weighted_score":round(sum(sum(x[k]*weights[k] for k in weights) for x in v)/len(v),2)} for arm,v in sums.items()}
    save(out/"results.json",result)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    p.add_argument("--model",default="gpt-4.1-mini")
    p.add_argument("--live",action="store_true",help="Explicitly authorize up to 18 billable provider attempts")
    p.add_argument("--score",action="store_true")
    a=p.parse_args()
    if a.score: print(json.dumps(score(a.output),indent=2))
    else: run(a.output,a.model,a.live)
