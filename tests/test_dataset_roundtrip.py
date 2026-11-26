import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import relate
from attribution import MODELS
from graph import demo_graph, analyze, rows
from network import network
from finance import financial_summary
from inventory import inventory_summary
from dataset_import import import_dataset, load_dataset, summarize_store, SCHEMAS
from dataset_export import export_demo, canonical_zip
from preview_api import demo_csv

class CanonicalRoundtripTests(unittest.TestCase):
    def test_original_dataset_roundtrip(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            csv_dir=export_demo(root/"csv")
            counts={k:len(v) for k,v in load_dataset(csv_dir).items()}
            self.assertEqual(counts,{"products":3,"campaigns":4,"customers":80,"touchpoints":237,"orders":72})
            output=root/"original.rl"
            summary=import_dataset(csv_dir,output)
            self.assertEqual(sum(summary["nodes"].values()),396)
            self.assertEqual(sum(summary["edges"].values()),622)
            self.assertEqual(summary["financials"]["revenue"],6970)
            self.assertEqual(summary["financials"]["profit_after_ads"],1050)
            self.assertEqual(summary["inventory"]["total_units"],208)
            with demo_graph() as original:
                rebuilt=relate.connect(str(output),read_only=True)
                try:
                    self.assertEqual(network(original),network(rebuilt))
                    self.assertEqual(financial_summary(original),financial_summary(rebuilt))
                    self.assertEqual(inventory_summary(original),inventory_summary(rebuilt))
                    for model in MODELS:
                        self.assertEqual(analyze(original,model),analyze(rebuilt,model))
                    for customer in ("U001","U005","U080"):
                        for query in ("journey","customer_orders"):
                            self.assertEqual(rows(original,query,{"customer":customer}),rows(rebuilt,query,{"customer":customer}))
                finally:
                    rebuilt.close()

    def test_download_matches_local_export(self):
        with TemporaryDirectory() as directory:
            csv_dir=export_demo(Path(directory)/"csv")
            response=demo_csv()
            self.assertEqual(response.media_type,"application/zip")
            self.assertIn("nexus-original-csv.zip",response.headers["content-disposition"])
            with ZipFile(io.BytesIO(response.body)) as archive:
                self.assertEqual(set(archive.namelist()),{k+".csv" for k in SCHEMAS})
                for name in archive.namelist():
                    self.assertEqual(archive.read(name),(csv_dir/name).read_bytes())
