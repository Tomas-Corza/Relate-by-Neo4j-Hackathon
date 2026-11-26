import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from graph import demo_graph
from network import network
from store import create_store,inspect_store

class NetworkTests(unittest.TestCase):
    def test_network_matches_graph(self):
        with demo_graph() as db:
            g=network(db)
        self.assertEqual(len(g["nodes"]),396)
        self.assertEqual(len(g["edges"]),622)
        ids={n["id"] for n in g["nodes"]}
        self.assertEqual(len(ids),396)
        self.assertTrue(all(e["source"] in ids and e["target"] in ids for e in g["edges"]))
        self.assertIn({"source":"C2","target":"P2","type":"PROMOTES"},g["edges"])
    def test_persistent_reopen(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/"demo.rl"
            first=create_store(path)
            self.assertTrue(path.is_file())
            self.assertEqual(sum(first["nodes"].values()),396)
            self.assertEqual(sum(first["edges"].values()),622)
            self.assertEqual(first,inspect_store(path))
            with self.assertRaises(ValueError):create_store(path)
