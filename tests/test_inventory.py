import unittest
from graph import demo_graph
from inventory import inventory_summary
from preview_api import overview

class InventoryTests(unittest.TestCase):
    def test_unique_stock_and_relationships(self):
        with demo_graph() as db:
            d=inventory_summary(db)
        self.assertEqual(len(d["products"]),3)
        self.assertEqual(d["campaign_relationships"],4)
        self.assertEqual(d["total_units"],208)
        self.assertEqual(d["low_stock_products"],1)
        self.assertEqual(d["exposed_spend"],1800)
        self.assertEqual(d["total_spend"],3150)
        self.assertEqual(d["inventory_cost"],6110)
        self.assertEqual(d["listed_sales_value"],16950)
        self.assertEqual(sum(p["observed_units_sold"] for p in d["products"]),72)
        self.assertEqual(sum(p["observed_revenue"] for p in d["products"]),6970)
        p=next(p for p in d["products"] if p["product_id"]=="P1")
        self.assertEqual(set(p["campaign_ids"]),{"C1","C4"})
        self.assertEqual(p["stock"],120)
    def test_original_campaigns_retained(self):
        d=overview("linear")
        self.assertEqual(len(d["campaigns"]),4)
        self.assertEqual(set(c["campaign_id"] for c in d["campaigns"]),{"C1","C2","C3","C4"})
        self.assertEqual(d["inventory"],overview("last_touch")["inventory"])
