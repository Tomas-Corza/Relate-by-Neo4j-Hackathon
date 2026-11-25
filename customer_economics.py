"""Customer economics using existing multi-touch allocation weights."""
from collections import defaultdict
from attribution import parse_time

def customer_economics(touches, orders, result, campaigns):
    first = {}
    for order in orders:
        uid = order["customer_id"]
        key = (parse_time(order["converted_at"]), order["conversion_id"])
        if uid not in first or key < first[uid]:
            first[uid] = key
    first_ids = {key[1] for key in first.values()}
    by_touch = {t["touchpoint_id"]: t["campaign_id"] for t in touches}
    conversions, acquisitions = defaultdict(float), defaultdict(float)
    covered_first = set()
    for row in result["allocations"]:
        cid = by_touch[row["touchpoint_id"]]
        weight = float(row["weight"])
        conversions[cid] += weight
        if row["conversion_id"] in first_ids:
            acquisitions[cid] += weight
            covered_first.add(row["conversion_id"])
    def ratio(n, d):
        return n / d if d > 1e-9 else None
    spend = sum(c["spend"] for c in campaigns)
    revenue = sum(float(o["revenue"]) for o in orders)
    gross = sum(float(o["revenue"]) - float(o["cost"]) for o in orders)
    attributed = float(result["totals"]["attributed_revenue"])
    for c in campaigns:
        cid = c["campaign_id"]
        c["conversion_credit"] = conversions[cid]
        c["acquisition_credit"] = acquisitions[cid]
        c["cac_proxy"] = ratio(c["spend"], acquisitions[cid])
        c["cpa"] = ratio(c["spend"], conversions[cid])
        c["revenue_credit_pct"] = ratio(c["revenue"] * 100, attributed)
        c["spend_share_pct"] = ratio(c["spend"] * 100, spend)
    return {
        "first_observed_purchasers": len(first),
        "attributed_first_purchases": len(covered_first),
        "unattributed_first_purchases": len(first) - len(covered_first),
        "cac_proxy": ratio(spend, len(first)),
        "cpa": ratio(spend, result["totals"]["attributed_conversions"]),
        "observed_revenue_per_buyer": ratio(revenue, len(first)),
        "observed_gross_profit_per_buyer": ratio(gross, len(first)),
        "aov": ratio(revenue, len(orders)),
        "gross_margin_pct": ratio(gross * 100, revenue),
        "revenue_coverage_pct": ratio(attributed * 100, revenue),
        "conversion_coverage_pct": ratio(result["totals"]["attributed_conversions"] * 100, len(orders)),
    }
