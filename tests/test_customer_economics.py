import unittest
from attribution import attribute, MODELS
from customer_economics import customer_economics

class EconomicsTests(unittest.TestCase):
    def test_fractional_credit_and_unattributed(self):
        touches=[dict(touchpoint_id="t1",customer_id="u1",channel="A",campaign_id="a",occurred_at="2026-01-01T00:00:00Z"),dict(touchpoint_id="t2",customer_id="u1",channel="B",campaign_id="b",occurred_at="2026-01-02T00:00:00Z")]
        orders=[dict(conversion_id=i,customer_id=u,converted_at=d,revenue=100,cost=40) for i,u,d in [("o1","u1","2026-01-03T00:00:00Z"),("o2","u1","2026-01-04T00:00:00Z"),("o3","u2","2026-01-05T00:00:00Z")]]
        for model in MODELS:
            r=attribute(touches,orders,model)
            cs=[dict(campaign_id="a",spend=20,revenue=0),dict(campaign_id="b",spend=30,revenue=0)]
            for c in cs:
                c["revenue"]=sum(float(a["attributed_revenue"]) for a in r["allocations"] if a["channel"]==c["campaign_id"].upper())
            e=customer_economics(touches,orders,r,cs)
            self.assertAlmostEqual(sum(c["acquisition_credit"] for c in cs),1)
            self.assertAlmostEqual(sum(c["conversion_credit"] for c in cs),2)
            self.assertAlmostEqual(sum(c["revenue_credit_pct"] for c in cs),100)
            self.assertEqual(e["unattributed_first_purchases"],1)
            self.assertEqual(e["cac_proxy"],25)
            self.assertEqual(e["cpa"],25)
            self.assertEqual(e["observed_revenue_per_buyer"],150)
            self.assertAlmostEqual(e["revenue_coverage_pct"],200/3)
            self.assertEqual(e["gross_margin_pct"],60)

if __name__=="__main__":
    unittest.main()
