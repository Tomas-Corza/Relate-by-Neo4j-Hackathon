"""Recorded order economics, independent of attribution model."""
from collections import defaultdict
from graph import rows
def financial_summary(db):
    products=defaultdict(lambda:{"orders":0,"revenue":0,"cogs":0})
    for o in rows(db,"orders"):
        p=products[o["product"]]
        p["orders"]+=1
        p["revenue"]+=o["revenue"]
        p["cogs"]+=o["cost"]
    result=[]
    for name,p in sorted(products.items()):
        gross=p["revenue"]-p["cogs"]
        result.append(dict(product=name,**p,gross_profit=gross,gross_margin_pct=100*gross/p["revenue"] if p["revenue"] else None))
    revenue=sum(p["revenue"] for p in result)
    cogs=sum(p["cogs"] for p in result)
    spend=sum(c["spend"] for c in rows(db,"campaigns"))
    gross=revenue-cogs
    return dict(revenue=revenue,cogs=cogs,gross_profit=gross,spend=spend,profit_after_ads=gross-spend,
                gross_margin_pct=100*gross/revenue if revenue else None,margin_after_ads_pct=100*(gross-spend)/revenue if revenue else None,products=result)
