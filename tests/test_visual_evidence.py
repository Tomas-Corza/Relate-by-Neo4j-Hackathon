import unittest
from preview_api import customers, graph_evidence

class VisualEvidenceTests(unittest.TestCase):
    def test_customer_purchase_credit(self):
        for model in ("first_touch","last_touch","linear","position_based","time_decay"):
            d=customers("U001",model)
            self.assertEqual(d["model"],model)
            self.assertTrue(d["journey"])
            self.assertTrue(d["orders"])
            self.assertEqual(d["params"],{"customer":"U001"})
            ids={t["touchpoint"] for t in d["journey"]}
            for order in d["orders"]:
                allocations=[a for a in d["allocations"] if a["conversion_id"]==order["order_id"]]
                self.assertTrue(all(a["touchpoint_id"] in ids for a in allocations))
                self.assertAlmostEqual(sum(float(a["attributed_revenue"]) for a in allocations),order["revenue"],places=2)
    def test_nonbuyer_and_risk(self):
        d=customers("U004","linear")
        self.assertFalse(d["orders"])
        self.assertFalse(d["allocations"])
        self.assertTrue(d["journey"])
        r=graph_evidence("risk","U001")
        self.assertTrue(any(x["campaign_id"]=="C2" and x["stock"]==3 for x in r["records"]))
