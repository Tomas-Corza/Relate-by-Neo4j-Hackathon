import csv
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'webapp'/'src'/'benchmark-data'

class BenchmarkArchiveTests(unittest.TestCase):
    def test_archived_results_reproduce(self):
        raw=json.loads((ARCHIVE/'raw_responses.json').read_text())
        results=json.loads((ARCHIVE/'results.json').read_text())
        manifest=json.loads((ARCHIVE/'manifest.json').read_text())
        protocol=json.loads((ROOT/'benchmark_protocol.json').read_text())
        with (ARCHIVE/'scorecard.csv').open(newline='') as f:
            ratings={r['response_id']:r for r in csv.DictReader(f)}
        self.assertEqual(manifest['status'],'complete')
        self.assertEqual(len(raw),18)
        self.assertEqual(len(ratings),18)
        self.assertEqual(len({r['response_id'] for r in raw}),18)
        self.assertEqual({r['resolved_model'] for r in raw},{'gpt-4.1-mini-2025-04-14'})
        self.assertEqual(set(ratings),{r['response_id'] for r in raw})
        for arm,totals in {'A':(2205,1323,12.869),'B':(291095,2121,34.843),'N':(19044,2209,22.325)}.items():
            rows=[r for r in raw if r['arm']==arm]
            self.assertEqual(len(rows),6)
            self.assertEqual({r['question_id'] for r in rows},{c['id'] for c in protocol['cases']})
            self.assertTrue(all(r['status']=='ok' and r['response'] for r in rows))
            self.assertEqual(sum(r['input_tokens'] for r in rows),totals[0])
            self.assertEqual(sum(r['output_tokens'] for r in rows),totals[1])
            self.assertAlmostEqual(sum(r['elapsed_seconds'] for r in rows),totals[2])
            review=[ratings[r['response_id']] for r in rows]
            for r,s in zip(rows,review):
                self.assertEqual(r['question_id'],s['question_id'])
                self.assertTrue(s['review_notes'].strip())
                self.assertTrue(all(float(s[k]) in (0,.5,1) for k in protocol['weights']))
            for k in protocol['weights']:
                self.assertAlmostEqual(results[arm]['criteria_pct'][k],100*sum(float(s[k]) for s in review)/6,places=2)
            self.assertAlmostEqual(results[arm]['weighted_score'],sum(sum(float(s[k])*w for k,w in protocol['weights'].items()) for s in review)/6,places=2)
