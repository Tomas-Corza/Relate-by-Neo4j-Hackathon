"""Inventory snapshot and campaign exposure from stored Relate relationships."""
from graph import rows
from finance import financial_summary

def inventory_summary(db):
    campaigns=rows(db,"campaigns")
    historical={p["product"]:p for p in financial_summary(db)["products"]}
    products=[]
    for p in rows(db,"products"):
        linked=[c for c in campaigns if c["product"]==p["product"]]
        hist=historical.get(p["product"],{})
        products.append(dict(p,inventory_cost=p["stock"]*p["unit_cost"],
            listed_sales_value=p["stock"]*p["price"],
            unit_margin_pct=100*(p["price"]-p["unit_cost"])/p["price"] if p["price"] else None,
            observed_units_sold=hist.get("orders",0),observed_revenue=hist.get("revenue",0),
            observed_gross_profit=hist.get("gross_profit",0),
            campaign_spend=sum(c["spend"] for c in linked),campaign_ids=[c["campaign_id"] for c in linked],
            status="Out of stock" if p["stock"]==0 else "Low stock" if p["stock"]<10 else "Available"))
    return {"products":products,"total_units":sum(p["stock"] for p in products),
        "inventory_cost":sum(p["inventory_cost"] for p in products),
        "listed_sales_value":sum(p["listed_sales_value"] for p in products),
        "low_stock_products":sum(p["stock"]<10 for p in products),
        "exposed_spend":sum(c["spend"] for c in campaigns if c["stock"]<10),
        "total_spend":sum(c["spend"] for c in campaigns),"campaign_relationships":len(campaigns)}
