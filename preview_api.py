"""Local-only React preview; production Streamlit entry point is unchanged."""
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from graph import demo_graph, analyze, rows
from intelligence import graph_counts, customer_value
from customer_economics import customer_economics
app = FastAPI(title="Nexus local preview", docs_url=None, redoc_url=None, openapi_url=None)
Model = Literal["first_touch","last_touch","linear","position_based","time_decay"]
@app.get("/api/overview")
def overview(model: Model = "linear"):
    with demo_graph() as db:
        result, campaigns = analyze(db, model)
        nodes, edges = graph_counts(db)
        customers, _ = customer_value(db)
        economics = customer_economics(rows(db,"touches"), rows(db,"orders"), result, campaigns)
        return {"economics":economics,"totals":result["totals"],"campaigns":campaigns,"nodes":nodes,"edges":edges,
                "risks":rows(db,"risk"),"purchasers":sum(c["orders"]>0 for c in customers),
                "repeat":sum(c["orders"]>1 for c in customers),"model":model}
dist = Path(__file__).parent / "webapp" / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
