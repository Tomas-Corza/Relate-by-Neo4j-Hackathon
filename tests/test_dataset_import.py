import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dataset_import import load_dataset, import_dataset, summarize_store
from attribution import MODELS
from store import inspect_store

SAMPLE=Path(__file__).resolve().parents[1]/"examples"/"synthetic-import"

class DatasetImportTests(unittest.TestCase):
    def test_import_and_reopen(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)/"sample.rl"
            data=import_dataset(SAMPLE,output)
            self.assertEqual(sum(data["nodes"].values()),15)
            self.assertEqual(sum(data["edges"].values()),17)
            self.assertEqual(data["financials"]["revenue"],210)
            self.assertEqual(data["financials"]["cogs"],80)
            self.assertEqual(data["financials"]["profit_after_ads"],50)
            self.assertEqual(data["inventory"]["total_units"],43)
            self.assertEqual(data["inventory"]["exposed_spend"],60)
            self.assertEqual(data["attribution"]["attributed_revenue"],"130.00")
            self.assertEqual(data["attribution"]["unattributed_revenue"],"80.00")
            self.assertEqual(data, summarize_store(output))
            self.assertEqual(data["nodes"],inspect_store(output)["nodes"])
            for model in MODELS:
                result=summarize_store(output,model)
                self.assertEqual(result["financials"],data["financials"])
                self.assertEqual(result["attribution"]["attributed_revenue"],"130.00")
            with self.assertRaises(ValueError):
                import_dataset(SAMPLE,output)
            self.assertEqual(data,summarize_store(output))

    def test_invalid_input_never_creates_store(self):
        cases=[
            ("products.csv","P102,Reading light,50,20,3","P101,Reading light,50,20,3"),
            ("products.csv","Reading light","Desk lamp"),
            ("products.csv",",50,20,3",",50,20,-3"),
            ("campaigns.csv","C102,Social lighting","U101,Social lighting"),
            ("campaigns.csv",",60,P102",",60,P999"),
            ("campaigns.csv",",60,P102",",NaN,P102"),
            ("orders.csv",",80\n",",0\n"),
            ("orders.csv",",80\n",",80.001\n"),
            ("orders.csv","U103,P101","U999,P101"),
            ("touchpoints.csv","C102,2026","C999,2026"),
            ("touchpoints.csv","12:00:00Z","12:00:00"),
            ("customers.csv","id\n","id,email\n"),
            ("customers.csv","U103\n","U103,extra\n"),
        ]
        for filename,old,new in cases:
            with self.subTest(filename=filename,new=new), TemporaryDirectory() as directory:
                source=Path(directory)/"csv"
                shutil.copytree(SAMPLE,source)
                file=source/filename
                content=file.read_text()
                self.assertIn(old,content)
                file.write_text(content.replace(old,new,1))
                output=Path(directory)/"bad.rl"
                with self.assertRaises(ValueError):
                    import_dataset(source,output)
                self.assertFalse(output.exists())

    def test_staging_failure_does_not_publish(self):
        with TemporaryDirectory() as directory:
            output=Path(directory)/"failed.rl"
            with patch("dataset_import.summarize_store",side_effect=ValueError("verification failed")):
                with self.assertRaises(ValueError):
                    import_dataset(SAMPLE,output)
            self.assertEqual(list(Path(directory).iterdir()),[])

    def test_empty_event_tables(self):
        with TemporaryDirectory() as directory:
            source=Path(directory)/"csv"
            shutil.copytree(SAMPLE,source)
            for filename in ("touchpoints.csv","orders.csv"):
                file=source/filename
                file.write_text(file.read_text().splitlines()[0]+"\n")
            self.assertEqual(load_dataset(source)["orders"],[])
            report=import_dataset(source,Path(directory)/"empty.rl")
            self.assertEqual(report["financials"]["revenue"],0)
            self.assertEqual(report["attribution"]["total_conversions"],0)
