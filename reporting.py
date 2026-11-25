"""Read-only custom reports over Relate query results. Never allocate aggregate spend to dates."""
from collections import defaultdict
from datetime import date, timedelta
from graph import rows, QUERIES
from attribution import attribute, parse_time
from customer_economics import customer_economics

DIMENSIONS=("channel","campaign","product","customer","day","week","month","cohort")
ORDER_METRICS=("revenue","gross_profit","orders","purchasing_customers","average_order_value","repeat_purchase_rate")
CREDIT_METRICS=("attributed_revenue","attributed_gross_profit","conversion_credit","acquisition_credit")
CAMPAIGN_METRICS=("attributed_revenue","attributed_gross_profit","conversion_credit","acquisition_credit","spend","profit_after_ads","roas","cpa","cac_proxy","inventory")
def ratio(a,b):
    return a/b if b>1e-9 else None
def report(db, cfg):
    mode=cfg["scope"]; dims=[cfg["dimension"]]+([cfg["breakdown"]] if cfg["breakdown"] else [])
    metrics=cfg["metrics"]
    allowed={"orders":ORDER_METRICS,"attribution":CREDIT_METRICS,"campaigns":CAMPAIGN_METRICS}[mode]
    permitted={"orders":("product","customer","day","week","month","cohort"),"attribution":DIMENSIONS,"campaigns":("channel","campaign")}[mode]
    if len(set(dims))!=len(dims) or any(d not in permitted for d in dims) or not metrics or len(set(metrics))!=len(metrics) or any(m not in allowed for m in metrics):
        raise ValueError("Choose compatible and distinct dimensions and metrics.")
    if cfg["sort"] not in metrics:
        raise ValueError("Sort metric must be selected.")
    if cfg["filter_dimension"] and cfg["filter_dimension"] not in permitted:
        raise ValueError("Filter dimension is not available for this report.")
    if bool(cfg["filter_dimension"]) != bool(cfg["filter_value"]):
        raise ValueError("Choose both a filter dimension and value, or neither.")
    start,end=cfg["start"],cfg["end"]
    if start and end and start>end: raise ValueError("Start date must precede end date.")
    if mode=="campaigns" and (start or end): raise ValueError("Campaign spend and inventory are all-data snapshots; date filters are unavailable.")
    touches,orders,campaigns=(rows(db,k) for k in ("touches","orders","campaigns"))
    by_campaign={c["campaign_id"]:c for c in campaigns}
    by_touch={t["touchpoint_id"]:t for t in touches}
    first_touch={}
    for t in sorted(touches,key=lambda t:(parse_time(t["occurred_at"]),t["touchpoint_id"])):
        first_touch.setdefault(t["customer_id"],t["campaign_id"])
    first_order={}
    for o in sorted(orders,key=lambda o:(parse_time(o["converted_at"]),o["conversion_id"])):
        first_order.setdefault(o["customer_id"],o["conversion_id"])
    selected=[o for o in orders if (not start or parse_time(o["converted_at"]).date()>=start) and (not end or parse_time(o["converted_at"]).date()<=end)]
    by_order={o["conversion_id"]:o for o in selected}
    def dimensions(o,c=None):
        dt=parse_time(o["converted_at"]).date()
        cohort=by_campaign.get(first_touch.get(o["customer_id"]),{}).get("channel","No observed touch")
        return {"channel":c["channel"] if c else "Unattributed","campaign":c["campaign"] if c else "Unattributed","product":o["product"],"customer":o["customer_id"],"day":dt.isoformat(),"week":(dt-timedelta(days=dt.weekday())).isoformat(),"month":dt.strftime("%Y-%m"),"cohort":cohort}
    groups=defaultdict(lambda:{"revenue":0.0,"gross_profit":0.0,"orders":0,"buyers":set(),"buyer_orders":defaultdict(int),"attributed_revenue":0.0,"attributed_gross_profit":0.0,"conversion_credit":0.0,"acquisition_credit":0.0,"spend":0.0,"stocks":[]})
    def group(d):
        if cfg["filter_dimension"] and d[cfg["filter_dimension"]]!=cfg["filter_value"]: return None
        return groups[tuple(d[k] for k in dims)]
    if mode=="orders":
        for o in selected:
            g=group(dimensions(o))
            if g is None: continue
            g["revenue"]+=o["revenue"];g["gross_profit"]+=o["revenue"]-o["cost"];g["orders"]+=1
            g["buyers"].add(o["customer_id"]);g["buyer_orders"][o["customer_id"]]+=1
    else:
        result=attribute(touches,orders,cfg["model"])
        if mode=="campaigns":
            for c in campaigns:
                g=group({"channel":c["channel"],"campaign":c["campaign"]})
                if g is not None:g["spend"]+=c["spend"];g["stocks"].append(c["stock"])
        for a in result["allocations"]:
            o=by_order.get(a["conversion_id"])
            if o is None:continue
            c=by_campaign[by_touch[a["touchpoint_id"]]["campaign_id"]]
            g=group(dimensions(o,c))
            if g is None:continue
            rev=float(a["attributed_revenue"])
            g["attributed_revenue"]+=rev
            g["attributed_gross_profit"]+=rev*(o["revenue"]-o["cost"])/o["revenue"] if o["revenue"] else 0
            g["conversion_credit"]+=a["weight"]
            if first_order[o["customer_id"]]==o["conversion_id"]:g["acquisition_credit"]+=a["weight"]
    output=[]
    for key,g in groups.items():
        g.update(purchasing_customers=len(g["buyers"]),average_order_value=ratio(g["revenue"],g["orders"]),repeat_purchase_rate=ratio(100*sum(n>1 for n in g["buyer_orders"].values()),len(g["buyers"])),profit_after_ads=g["attributed_gross_profit"]-g["spend"],roas=ratio(g["attributed_revenue"],g["spend"]),cpa=ratio(g["spend"],g["conversion_credit"]),cac_proxy=ratio(g["spend"],g["acquisition_credit"]),inventory=g["stocks"][0] if len(g["stocks"])==1 else None)
        output.append(dict(zip(dims,key))|{m:round(g[m],6) if isinstance(g[m],float) else g[m] for m in metrics})
    output.sort(key=lambda r:tuple(r[d] for d in dims))
    output.sort(key=lambda r:(r[cfg["sort"]] is None, -(r[cfg["sort"]] or 0) if cfg["descending"] else (r[cfg["sort"]] or 0)))
    dates=[parse_time(o["converted_at"]).date().isoformat() for o in orders]
    return {"columns":dims+metrics,"records":output,"available_start":min(dates,default=None),"available_end":max(dates,default=None),"queries":{k:QUERIES[k] for k in ("touches","orders","campaigns")},"notes":["UTC purchase dates; attribution retains complete touch history and the existing 30-day lookback.","Cohort means earliest recorded channel, not verified acquisition. Repeat purchase rate means multiple orders within the selected group and period. Distinct buyers are not additive across groups.","Attributed reports exclude orders without eligible touches. Fractional credits are descriptive, not causal.","Spend and inventory are undated campaign totals/snapshots. Inventory is blank for groups with multiple campaigns to avoid double counting. CAC is a first-observed-purchase proxy; zero denominators are blank."] }
