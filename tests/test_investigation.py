import unittest
from unittest.mock import patch
from graph import demo_graph
from investigation import execute,run_investigation

class InvestigationTests(unittest.TestCase):
    def test_connected_investigation(self):
        with demo_graph() as db:
            answer,trace=execute(db,"Which marketing investments should I reconsider and why?")
        tools={t["tool"]:t for t in trace}
        self.assertEqual(len(tools),6)
        self.assertIn({"source":"C2","target":"P2"},tools["graph_traversal"]["evidence"])
        self.assertEqual(tools["inventory_analysis"]["evidence"]["exposed_spend"],1800)
        self.assertEqual(len(tools["attribution_sensitivity"]["evidence"]),4)
        self.assertEqual(tools["financial_analysis"]["evidence"]["revenue"],6970)
        scenario=tools["budget_simulation"]["evidence"]["records"]
        self.assertEqual(sum(r["baseline_spend"] for r in scenario),sum(r["scenario_spend"] for r in scenario))
        self.assertTrue(all(t["status"]=="completed" and t["queries"] for t in trace))
        self.assertIn("[E1]",answer)
    def test_customer_and_offline(self):
        with patch.dict("os.environ",{"OPENAI_API_KEY":""}):
            with demo_graph() as db:
                result=run_investigation(db,"Show customer U001 journey")
        self.assertEqual(result["mode"],"deterministic")
        t=next(t for t in result["trace"] if t["tool"]=="customer_journey")
        self.assertEqual(t["parameters"],{"customer":"U001"})
        self.assertTrue(t["evidence"]["touchpoints"])
        self.assertTrue(t["evidence"]["orders"])
