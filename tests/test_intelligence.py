import unittest
from graph import demo_graph, analyze
from intelligence import customer_value,path_insights,graph_counts,compare_models,scenario

class IntelligenceTests(unittest.TestCase):
    def test_graph_counts_and_value(self):
        with demo_graph() as db:
            nodes,edges=graph_counts(db)
            self.assertEqual(nodes["Customer"],80)
            self.assertEqual(nodes["Order"],72)
            self.assertEqual(edges["CONTAINS"],72)
            people,cohorts=customer_value(db)
            self.assertEqual(sum(p["revenue"] for p in people),6970)
            self.assertEqual(sum(c["customers"] for c in cohorts),80)
            self.assertEqual(sum(p["purchasing_customers"] for p in path_insights(db)),60)
            self.assertEqual(len(compare_models(db)),20)
    def test_scenario_conserves_spend_and_zero_identity(self):
        with demo_graph() as db:
            _,campaigns=analyze(db)
            result,_=scenario(campaigns,"C2","C1",0,.5)
            self.assertTrue(all(r["baseline_profit"]==r["scenario_profit"] for r in result))
            result,_=scenario(campaigns,"C2","C1",300,.5)
            self.assertEqual(sum(r["baseline_spend"] for r in result),sum(r["scenario_spend"] for r in result))
            _,warnings=scenario(campaigns,"C1","C2",100,.5)
            self.assertTrue(warnings)
            with self.assertRaises(ValueError): scenario(campaigns,"C2","C1",1900,.5)
