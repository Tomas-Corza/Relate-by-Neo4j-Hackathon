"""New hackathon implementation: embedded Relate graph and evidence tools."""
import random
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
import relate
from attribution import attribute

CAMPAIGNS = [
    ("C1", "Search acquisition", "Google Ads", 1200, "P1"),
    ("C2", "Social discovery", "Meta Ads", 1800, "P2"),
    ("C3", "Retention email", "Email", 150, "P3"),
    ("C4", "Organic discovery", "Organic", 0, "P1"),
]
PRODUCTS = [("P1", "Everyday kit", 95, 35, 120), ("P2", "Limited edition", 150, 70, 3), ("P3", "Refill pack", 60, 20, 85)]

QUERIES = {
    "campaigns": """MATCH (c:Campaign)-[:PROMOTES]->(p:Product)
RETURN c.id AS campaign_id, c.name AS campaign, c.channel AS channel, c.spend AS spend,
p.name AS product, p.stock AS stock ORDER BY campaign_id""",
    "touches": """MATCH (u:Customer)-[:HAS_TOUCH]->(t:Touchpoint)-[:FROM_CAMPAIGN]->(c:Campaign)
RETURN u.id AS customer_id, t.id AS touchpoint_id, t.at AS occurred_at, c.channel AS channel, c.id AS campaign_id ORDER BY occurred_at""",
    "orders": """MATCH (u:Customer)-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN u.id AS customer_id, o.id AS conversion_id, o.at AS converted_at, o.revenue AS revenue, p.cost AS cost, p.name AS product ORDER BY converted_at""",
    "journey": """MATCH (u:Customer {id:$customer})-[:HAS_TOUCH]->(t:Touchpoint)-[:FROM_CAMPAIGN]->(c:Campaign)-[:PROMOTES]->(p:Product)
RETURN t.id AS touchpoint, t.at AS occurred_at, c.name AS campaign, p.name AS promoted_product ORDER BY occurred_at""",
    "customer_orders": """MATCH (u:Customer {id:$customer})-[:PLACED]->(o:Order)-[:CONTAINS]->(p:Product)
RETURN o.id AS order_id, o.at AS converted_at, o.revenue AS revenue, p.name AS product ORDER BY converted_at""",
    "risk": """MATCH (c:Campaign)-[:PROMOTES]->(p:Product)
WHERE p.stock < 10 AND c.spend > 0
RETURN c.id AS campaign_id, c.name AS campaign, c.spend AS spend, p.name AS product, p.stock AS stock ORDER BY spend DESC""",
}

def rows(db, name, params=None):
    return [dict(r) for r in db.execute(QUERIES[name], params or {})]

@contextmanager
def demo_graph():
    db = relate.connect(":memory:")
    try:
        seed(db)
        yield db
    finally:
        db.close()

def seed(db):
    rng = random.Random(42)
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    for pid, name, price, cost, stock in PRODUCTS:
        db.execute("CREATE (:Product {id:$id,name:$name,price:$price,cost:$cost,stock:$stock})",
                   dict(id=pid,name=name,price=price,cost=cost,stock=stock))
    for cid,name,channel,spend,pid in CAMPAIGNS:
        db.execute("MATCH (p:Product {id:$pid}) CREATE (c:Campaign {id:$id,name:$name,channel:$channel,spend:$spend})-[:PROMOTES]->(p)",
                   dict(id=cid,name=name,channel=channel,spend=spend,pid=pid))
    for i in range(1,81):
        uid = f"U{i:03}"
        db.execute("CREATE (:Customer {id:$id})", {"id":uid})
        for j in range(1, rng.randint(2,4)+1):
            campaign = rng.choices(["C1","C2","C3","C4"],weights=[4,5,2,2])[0]
            at = (base+timedelta(days=i%10+j)).isoformat()
            db.execute("MATCH (u:Customer {id:$uid}), (c:Campaign {id:$cid}) CREATE (u)-[:HAS_TOUCH]->(t:Touchpoint {id:$tid,at:$at})-[:FROM_CAMPAIGN]->(c)",
                       dict(uid=uid,cid=campaign,tid=f"T{i:03}-{j}",at=at))
        if i%4:
            for k in range(1, 3 if i%5==0 else 2):
                pid,name,price,cost,stock = rng.choice(PRODUCTS)
                at=(base+timedelta(days=i%10+5+k)).isoformat()
                db.execute("MATCH (u:Customer {id:$uid}), (p:Product {id:$pid}) CREATE (u)-[:PLACED]->(o:Order {id:$oid,at:$at,revenue:$revenue})-[:CONTAINS]->(p)",
                           dict(uid=uid,pid=pid,oid=f"O{i:03}-{k}",at=at,revenue=price))

def analyze(db, model="linear"):
    touches, orders = rows(db,"touches"), rows(db,"orders")
    result = attribute(touches,orders,model)
    touch_campaign = {r["touchpoint_id"]:r["campaign_id"] for r in touches}
    order_info = {r["conversion_id"]:r for r in orders}
    campaigns = {r["campaign_id"]:dict(r, revenue=0.0, gross_profit=0.0) for r in rows(db,"campaigns")}
    for a in result["allocations"]:
        c = campaigns[touch_campaign[a["touchpoint_id"]]]
        o = order_info[a["conversion_id"]]
        revenue = float(a["attributed_revenue"])
        c["revenue"] += revenue
        c["gross_profit"] += revenue * (o["revenue"]-o["cost"])/o["revenue"]
    for c in campaigns.values():
        c["revenue"] = round(c["revenue"],2)
        c["gross_profit"] = round(c["gross_profit"],2)
        c["roas"] = round(c["revenue"]/c["spend"],2) if c["spend"] else None
        c["profit_after_ads"] = round(c["gross_profit"]-c["spend"],2)
    return result,list(campaigns.values())

def evidence(db, model="linear"):
    attribution,campaigns = analyze(db,model)
    return {"totals":attribution["totals"],"campaigns":campaigns,"inventory_risks":rows(db,"risk"),
            "model":model,"limitation":"Synthetic data. Rule-based attribution is descriptive, not causal. Gross profit excludes overhead, tax and shipping."}
