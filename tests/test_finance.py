import unittest
from graph import demo_graph
from finance import financial_summary
from preview_api import overview

class FinanceTests(unittest.TestCase):
    def test_financial_reconciliation(self):
        with demo_graph() as db:
            f=financial_summary(db)
        self.assertEqual(f["revenue"],6970)
        self.assertEqual(f["spend"],3150)
        self.assertEqual(sum(p["orders"] for p in f["products"]),72)
        self.assertEqual(sum(p["cogs"] for p in f["products"]),f["cogs"])
        self.assertEqual(sum(p["gross_profit"] for p in f["products"]),f["gross_profit"])
        self.assertEqual(f["revenue"]-f["cogs"]-f["spend"],f["profit_after_ads"])
        self.assertAlmostEqual(f["profit_after_ads"],1050,places=0)
    def test_financials_independent_of_attribution(self):
        a=overview("linear")
        for model in ("first_touch","last_touch","position_based","time_decay"):
            b=overview(model)
            self.assertEqual(a["financials"],b["financials"])
            self.assertAlmostEqual(sum(c["revenue"] for c in b["campaigns"]),b["financials"]["revenue"],places=2)
