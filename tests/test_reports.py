import unittest
from preview_api import custom_report, ReportRequest
from fastapi import HTTPException
class ReportTests(unittest.TestCase):
    def test_campaign_reconciliation(self):
        d=custom_report(ReportRequest(metrics=["attributed_revenue","spend"],sort="spend"))
        self.assertEqual(d["columns"],["channel","attributed_revenue","spend"])
        self.assertAlmostEqual(sum(r["attributed_revenue"] for r in d["records"]),6970,places=2)
        self.assertEqual(sum(r["spend"] for r in d["records"]),3150)
    def test_breakdown_and_all_models(self):
        for model in ("linear","first_touch","last_touch","position_based","time_decay"):
            d=custom_report(ReportRequest(scope="attribution",dimension="channel",breakdown="product",metrics=["attributed_revenue","conversion_credit"],sort="attributed_revenue",model=model))
            self.assertAlmostEqual(sum(r["attributed_revenue"] for r in d["records"]),6970,places=2)
            self.assertAlmostEqual(sum(r["conversion_credit"] for r in d["records"]),72,places=4)
    def test_orders_dates_filter(self):
        d=custom_report(ReportRequest(scope="orders",dimension="day",metrics=["orders","revenue"],sort="revenue"))
        self.assertEqual(sum(r["orders"] for r in d["records"]),72)
        self.assertEqual(sum(r["revenue"] for r in d["records"]),6970)
        day=d["records"][0]["day"]
        r=custom_report(ReportRequest(scope="orders",dimension="day",metrics=["orders"],sort="orders",start=day,end=day,filter_dimension="day",filter_value=day))
        self.assertEqual(len(r["records"]),1)
        self.assertEqual(r["records"][0]["orders"],d["records"][0]["orders"])
    def test_invalid_combinations(self):
        for cfg in [dict(scope="orders",dimension="day",metrics=["spend"],sort="spend"),dict(scope="campaigns",dimension="channel",metrics=["spend"],sort="spend",start="2026-11-01"),dict(scope="orders",dimension="day",breakdown="day",metrics=["orders"],sort="orders")]:
            with self.assertRaises(HTTPException) as e:custom_report(ReportRequest(**cfg))
            self.assertEqual(e.exception.status_code,422)
