"""Production FastAPI and React workspace backed by embedded Relate."""
from pathlib import Path
from typing import Literal
from datetime import date
from reporting import report
from finance import financial_summary
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
from collections import OrderedDict
from fastapi.staticfiles import StaticFiles
from graph import demo_graph, analyze, rows, QUERIES
from intelligence import graph_counts, customer_value, path_insights, compare_models, scenario
from agent import investigate
from customer_economics import customer_economics
app = FastAPI(title="OpenClaw Nexus", docs_url=None, redoc_url=None, openapi_url=None)
Model = Literal["first_touch","last_touch","linear","position_based","time_decay"]
@app.get("/api/overview")
def overview(model: Model = "linear"):
    with demo_graph() as db:
        result, campaigns = analyze(db, model)
        nodes, edges = graph_counts(db)
        customers, _ = customer_value(db)
        economics = customer_economics(rows(db,"touches"), rows(db,"orders"), result, campaigns)
        return {"financials":financial_summary(db),"economics":economics,"totals":result["totals"],"campaigns":campaigns,"nodes":nodes,"edges":edges,
                "risks":rows(db,"risk"),"purchasers":sum(c["orders"]>0 for c in customers),
                "repeat":sum(c["orders"]>1 for c in customers),"model":model}
# Fixed read-only query names and bounded input. No arbitrary Cypher.
QueryName = Literal["campaigns","touches","orders","journey","customer_orders","risk"]
@app.get("/_stcore/health")
def health():
    return {"status":"ok"}

@app.get("/api/audit")
def audit(model: Model = "linear"):
    with demo_graph() as db:
        result, _ = analyze(db, model)
        return {"result":result,"comparison":compare_models(db)}

@app.get("/api/customers")
def customers(customer: str = Query("U001", pattern=r"^U(00[1-9]|0[1-7][0-9]|080)$"), model: Model = "linear"):
    with demo_graph() as db:
        people, cohorts = customer_value(db)
        journey=rows(db,"journey",{"customer":customer})
        orders=rows(db,"customer_orders",{"customer":customer})
        result,_=analyze(db,model)
        order_ids={o["order_id"] for o in orders}
        return {"people":people,"cohorts":cohorts,"journey":journey,"orders":orders,
                "allocations":[a for a in result["allocations"] if a["conversion_id"] in order_ids],
                "conversions":[a for a in result["conversions"] if a["conversion_id"] in order_ids],
                "model":model,"queries":{k:QUERIES[k] for k in ("journey","customer_orders")},"params":{"customer":customer}}

@app.get("/api/evidence")
def graph_evidence(name: QueryName = "risk", customer: str = Query("U001", pattern=r"^U(00[1-9]|0[1-7][0-9]|080)$")):
    with demo_graph() as db:
        params={"customer":customer} if name in ("journey","customer_orders") else {}
        return {"records":rows(db,name,params),"query":QUERIES[name],"params":params,"paths":path_insights(db),"path_campaigns":[{"campaign_id":c["campaign_id"],"channel":c["channel"],"campaign":c["campaign"]} for c in rows(db,"campaigns")]}

class ReportRequest(BaseModel):
    scope: Literal["orders","attribution","campaigns"]="campaigns"
    model: Model="linear"
    dimension: Literal["channel","campaign","product","customer","day","week","month","cohort"]="channel"
    breakdown: Literal["channel","campaign","product","customer","day","week","month","cohort"] | None=None
    metrics: list[Literal["revenue","gross_profit","orders","purchasing_customers","average_order_value","repeat_purchase_rate","attributed_revenue","attributed_gross_profit","conversion_credit","acquisition_credit","spend","profit_after_ads","roas","cpa","cac_proxy","inventory"]]=Field(min_length=1,max_length=10)
    start: date | None=None
    end: date | None=None
    filter_dimension: Literal["channel","campaign","product","customer","day","week","month","cohort"] | None=None
    filter_value: str | None=Field(default=None,max_length=100)
    sort: str=Field(max_length=40)
    descending: bool=True

@app.post("/api/reports")
def custom_report(body: ReportRequest):
    try:
        with demo_graph() as db:
            return report(db,body.model_dump())
    except ValueError as exc:
        raise HTTPException(422,str(exc))

class BudgetRequest(BaseModel):
    model: Model = "linear"
    source: Literal["C1","C2","C3"]
    target: Literal["C1","C2","C3"]
    amount: float = Field(ge=0,le=1800,allow_inf_nan=False)
    efficiency: float = Field(ge=0,le=1,allow_inf_nan=False)

@app.post("/api/budget")
def budget(body: BudgetRequest):
    with demo_graph() as db:
        _, campaigns=analyze(db,body.model)
        try:
            result,warnings=scenario(campaigns,body.source,body.target,body.amount,body.efficiency)
        except ValueError:
            raise HTTPException(422,"Invalid budget assumptions")
        return {"records":result,"warnings":warnings}

class AnalystRequest(BaseModel):
    model: Model = "linear"
    question: str = Field(min_length=1,max_length=500)

# The existing SQLite quota is still authoritative. A bounded in-process
# cooldown provides additional protection without storing questions or keys.
_recent=OrderedDict()
_lock=Lock()
@app.post("/api/analyst")
def analyst(body: AnalystRequest, request: Request):
    origin=request.headers.get("origin")
    if origin and urlsplit(origin).netloc != request.headers.get("host"):
        raise HTTPException(403,"Cross-origin requests are not allowed")
    if not body.question.strip():
        raise HTTPException(422,"Enter a question")
    key=request.client.host if request.client else "unknown"
    with _lock:
        now=monotonic()
        if now-_recent.get(key,-1000000)<15:
            raise HTTPException(429,"Please wait 15 seconds between analyst requests")
        _recent[key]=now
        _recent.move_to_end(key)
        while len(_recent)>2048:
            _recent.popitem(last=False)
    try:
        with demo_graph() as db:
            answer,context=investigate(db,body.question,body.model)
            return {"answer":answer,"context":context,"model":body.model}
    except Exception:
        raise HTTPException(503,"Analyst request failed. Dashboard remains available.")

@app.middleware("http")
async def secure_response(request, call_next):
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"]="no-store"
    return response

dist = Path(__file__).parent / "webapp" / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
