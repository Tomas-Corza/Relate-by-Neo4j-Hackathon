"""New graph-derived intelligence and explicit scenario assumptions."""
from collections import defaultdict, Counter
from decimal import Decimal
import math
from graph import rows, analyze
from attribution import MODELS, parse_time

def customer_value(db):
    """Observed customer value by earliest recorded touch, not predicted CLV."""
    touches, orders = rows(db,"touches"), rows(db,"orders")
    journeys=defaultdict(list)
    purchases=defaultdict(list)
    for t in touches: journeys[t["customer_id"]].append(t)
    for o in orders: purchases[o["customer_id"]].append(o)
    customers=[]
    cohorts=defaultdict(lambda: {"customers":0,"purchasers":0,"repeat_customers":0,"orders":0,"revenue":0,"gross_profit":0})
    for uid in sorted(set(journeys)|set(purchases)):
        history=sorted(journeys[uid],key=lambda t:(parse_time(t["occurred_at"]),t["touchpoint_id"]))
        bought=purchases[uid]
        first_order=min((parse_time(o["converted_at"]) for o in bought),default=None)
        eligible=[t for t in history if first_order is None or parse_time(t["occurred_at"])<=first_order]
        campaign=eligible[0]["campaign_id"] if eligible else "Unattributed"
        revenue=sum(o["revenue"] for o in bought)
        margin=sum(o["revenue"]-o["cost"] for o in bought)
        item={"customer_id":uid,"first_observed_campaign":campaign,"orders":len(bought),"revenue":revenue,"gross_profit":margin}
        customers.append(item)
        c=cohorts[campaign]
        c["customers"]+=1
        c["purchasers"]+=bool(bought)
        c["repeat_customers"]+=len(bought)>1
        c["orders"]+=len(bought)
        c["revenue"]+=revenue
        c["gross_profit"]+=margin
    summaries=[]
    for campaign,c in sorted(cohorts.items()):
        summaries.append(dict(c, campaign_id=campaign, observed_revenue_per_customer=round(c["revenue"]/c["customers"],2),
                              observed_gross_profit_per_customer=round(c["gross_profit"]/c["customers"],2),
                              observed_purchase_rate=round(c["purchasers"]/c["customers"],4),
                              repeat_rate_among_buyers=round(c["repeat_customers"]/c["purchasers"],4) if c["purchasers"] else None))
    return customers,summaries

def path_insights(db):
    """Sequence of recorded campaign touches before the first observed purchase."""
    touches,orders=rows(db,"touches"),rows(db,"orders")
    by_customer=defaultdict(list)
    first={}
    for o in orders:
        uid=o["customer_id"]; at=parse_time(o["converted_at"])
        first[uid]=min(first.get(uid,at),at)
    for t in touches: by_customer[t["customer_id"]].append(t)
    paths=Counter()
    for uid,at in first.items():
        eligible=sorted((t for t in by_customer[uid] if parse_time(t["occurred_at"])<=at),key=lambda t:(parse_time(t["occurred_at"]),t["touchpoint_id"]))
        path=" → ".join(t["campaign_id"] for t in eligible) or "No observed touch"
        paths[path]+=1
    return [{"path":p,"purchasing_customers":n} for p,n in paths.most_common()]

def graph_counts(db):
    # Count actual stored nodes and relationships via read-only Cypher.
    result={}
    for label in ("Customer","Touchpoint","Campaign","Product","Order"):
        result[label]=int(next(iter(db.execute(f"MATCH (n:{label}) RETURN count(n) AS total")))["total"])
    edges={}
    for rel in ("HAS_TOUCH","FROM_CAMPAIGN","PROMOTES","PLACED","CONTAINS"):
        edges[rel]=int(next(iter(db.execute(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS total")))["total"])
    return result,edges

def compare_models(db):
    result=[]
    for model in MODELS:
        _,campaigns=analyze(db,model)
        for c in campaigns:
            result.append({"model":model,"campaign_id":c["campaign_id"],"campaign":c["campaign"],"attributed_revenue":c["revenue"],"profit_after_ads":c["profit_after_ads"]})
    return result

def scenario(campaigns, source_id, target_id, transfer, efficiency):
    """Fixed-budget sensitivity analysis, not a forecast or inventory sales model.

    Source loss assumes historical gross profit per dollar; target gain assumes
    historical gross profit per dollar times a user-selected marginal factor.
    """
    transfer=float(transfer); efficiency=float(efficiency)
    if not math.isfinite(transfer) or not math.isfinite(efficiency) or transfer<0 or not 0<=efficiency<=1:
        raise ValueError("Invalid scenario assumptions")
    by_id={c["campaign_id"]:c for c in campaigns}
    if source_id==target_id or source_id not in by_id or target_id not in by_id:
        raise ValueError("Choose two different campaigns")
    source,target=by_id[source_id],by_id[target_id]
    if source["spend"]<=0 or target["spend"]<=0 or transfer>source["spend"]:
        raise ValueError("Transfer must be within the source paid budget")
    output=[]
    for c in campaigns:
        spend=float(c["spend"]); gross=float(c["gross_profit"])
        after_spend=spend; after_gross=gross
        if c["campaign_id"]==source_id:
            after_spend-=transfer
            after_gross-=transfer*gross/spend
        elif c["campaign_id"]==target_id:
            after_spend+=transfer
            after_gross+=transfer*gross/spend*efficiency
        output.append({"campaign_id":c["campaign_id"],"campaign":c["campaign"],"baseline_spend":round(spend,2),
                       "scenario_spend":round(after_spend,2),"baseline_profit":round(gross-spend,2),
                       "scenario_profit":round(after_gross-after_spend,2),"stock":c["stock"]})
    warnings=[]
    if target["stock"]<10 and transfer>0: warnings.append("Target promotes a low-stock product; do not increase spend without inventory review.")
    return output,warnings
