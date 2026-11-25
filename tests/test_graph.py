import unittest
from graph import demo_graph, analyze, rows
from agent import investigate
from attribution import MODELS
from unittest.mock import patch
from decimal import Decimal

class GraphTests(unittest.TestCase):
    def test_all_models_conserve_revenue(self):
        with demo_graph() as db:
            for model in MODELS:
                result,campaigns=analyze(db,model)
                t=result["totals"]
                self.assertEqual(Decimal(t["total_revenue"]),Decimal(t["attributed_revenue"])+Decimal(t["unattributed_revenue"]))
                self.assertEqual(Decimal(t["attributed_revenue"]),sum(Decimal(str(c["revenue"])) for c in campaigns))
    def test_graph_paths_and_risk(self):
        with demo_graph() as db:
            self.assertTrue(rows(db,"journey",{"customer":"U001"}))
            self.assertTrue(rows(db,"customer_orders",{"customer":"U001"}))
            self.assertEqual(rows(db,"risk")[0]["campaign_id"],"C2")
    def test_offline_agent(self):
        with patch.dict("os.environ",{"OPENAI_API_KEY":""}):
            with demo_graph() as db:
                answer,evidence=investigate(db,"Show inventory risk")
                self.assertIn("C2",answer)
                self.assertTrue(evidence["inventory_risks"])
if __name__=="__main__":
    unittest.main()
