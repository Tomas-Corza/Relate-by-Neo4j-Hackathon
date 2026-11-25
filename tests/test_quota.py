import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from quota import reserve

class QuotaTests(unittest.TestCase):
    def test_rolling_limits(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {"NEXUS_REQUESTS_PER_MINUTE":"2","NEXUS_REQUESTS_PER_DAY":"3"}):
            p=str(Path(d)/"quota.db")
            self.assertTrue(reserve(p,100000)[0])
            self.assertTrue(reserve(p,100001)[0])
            self.assertFalse(reserve(p,100002)[0])
            self.assertTrue(reserve(p,100061)[0])
            self.assertFalse(reserve(p,100122)[0])
            self.assertTrue(reserve(p,186401)[0])
    def test_concurrent_reservations(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {"NEXUS_REQUESTS_PER_MINUTE":"3","NEXUS_REQUESTS_PER_DAY":"50"}):
            p=str(Path(d)/"quota.db")
            with ThreadPoolExecutor(max_workers=8) as ex:
                outcomes=list(ex.map(lambda _: reserve(p,100000)[0], range(12)))
            self.assertEqual(sum(outcomes),3)
    def test_disabled(self):
        with patch.dict(os.environ, {"NEXUS_REQUESTS_PER_DAY":"0"}):
            self.assertFalse(reserve()[0])
