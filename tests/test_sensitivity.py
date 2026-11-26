import unittest
from graph import demo_graph
from intelligence import compare_models
from sensitivity import sensitivity
from attribution import MODELS

class SensitivityTests(unittest.TestCase):
    def test_model_comparison_and_statistics(self):
        with demo_graph() as db:
            records=compare_models(db)
        self.assertEqual(len(records),20)
        for m in MODELS:
            r=[x for x in records if x["model"]==m]
            self.assertAlmostEqual(sum(x["attributed_revenue"] for x in r),6970,places=2)
            self.assertEqual(sum(x["spend"] for x in r),3150)
            self.assertIsNone(next(x for x in r if x["campaign_id"]=="C4")["roas"])
        stats=sensitivity(records)
        self.assertEqual(len(stats),4)
        for s in stats:
            r=[x for x in records if x["campaign_id"]==s["campaign_id"]]
            self.assertEqual(s["min_revenue"],min(x["attributed_revenue"] for x in r))
            self.assertEqual(s["max_revenue"],max(x["attributed_revenue"] for x in r))
            self.assertEqual(s["profitable_models"]+s["loss_models"]+s["break_even_models"],5)
            self.assertEqual(s["model_deltas"]["linear"],0)
            self.assertTrue(1<=s["best_rank"]<=s["worst_rank"]<=4)
    def test_zero_baseline_and_ties(self):
        records=[dict(model=m,campaign_id=c,campaign=c,channel=c,attributed_revenue=0,profit_after_ads=0) for m in MODELS for c in ("A","B")]
        for s in sensitivity(records):
            self.assertIsNone(s["range_pct_of_mean"])
            self.assertIsNone(s["model_deltas"]["linear"])
            self.assertEqual(s["best_rank"],1)
            self.assertEqual(s["worst_rank"],1)
            self.assertEqual(s["break_even_models"],5)
