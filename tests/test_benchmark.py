import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
import json
from benchmark import run, prepare

class BenchmarkTests(unittest.TestCase):
    def test_matched_inputs(self):
        p,refs,data=prepare()
        self.assertEqual(len(p["cases"]),6)
        self.assertEqual(sum(p["weights"].values()),100)
        self.assertEqual(refs["financials"]["revenue"],6970)
        for arms in data.values():
            self.assertEqual(set(arms),{"A","B","N"})
            self.assertNotIn("stock",arms["A"][0])
            self.assertEqual(len(arms["B"]["nodes"]),396)
            for t in arms["N"]:
                self.assertEqual(arms["B"]["analytical_tables"][t["tool"]],t["evidence"])
    def test_dry_run(self):
        with TemporaryDirectory() as d:
            out=Path(d)/"dry"
            run(out,"gpt-4.1-mini")
            self.assertEqual(json.loads((out/"manifest.json").read_text())["status"],"pending")
            self.assertFalse((out/"raw_responses.json").exists())
            self.assertEqual(len((out/"scorecard.csv").read_text().splitlines()),19)
