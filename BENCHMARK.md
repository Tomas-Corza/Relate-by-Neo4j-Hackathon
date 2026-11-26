# Connected intelligence benchmark (predefined protocol v1.0)

## Research question
Does task-specific graph-derived context improve answers compared with campaign metrics alone or context-rich flat inputs? The three arms use the same provider model, question, system instruction and completion limit. B has all flat records and the same derived tables/parameters as N; N uses the actual executed Nexus trace. This compares context packaging and retrieval workflows, NOT inherent graph database superiority. A intentionally has less information. N's router is deterministic, not an autonomous LLM tool planner. B includes relationship IDs as flat rows, and may outperform N. No result is assumed.

Six synthetic cases are defined in benchmark_protocol.json. Expected facts and exact graph-derived references are captured before any provider call. References for sensitivity and scenario use the same existing analytical implementation, so this tests answer grounding, not independently validated algorithm correctness. Questions are development-set examples, not held-out generalization evidence.

## Reproduce
```bash
python benchmark.py benchmark-dry
# Creates protocol, reference answers, full inputs and blank scorecard. No network.
# Set OPENAI_API_KEY in your local environment, never in source.
python benchmark.py benchmark-run --live
# Up to 18 billable calls, no retries, sequential, same model, 500 completion tokens each.
# Review blind_responses.json against reference_answers.json and complete scorecard.csv.
python benchmark.py benchmark-run --score
```
Use a dedicated local API project and review input sizes and pricing before opting in. The benchmark is not a public endpoint and does not use the public demo quota; its hard attempt count is 18 per explicitly started run. No key is saved. Provider errors remain in raw results; incomplete runs cannot be scored as complete. Output directory must be new for each run.

## Human scoring
Use 0 (fails), 0.5 (partial), 1 (meets) for each criterion; score without viewing arm mapping, and record rationale. Evidence formatting can reveal arms, so blinding is partial. Ideally use two independent reviewers and report disagreements separately. Accuracy: correct required facts and numeric values (within one cent for money). Relationship identification: correct connected entities and direction where relevant, no invented connections; for financial-only tasks assess correct revenue-cost-spend reconciliation. Evidence completeness: references sufficient to verify required facts; record IDs or E IDs accepted equally. Recommendation quality: actionable, appropriately qualified next step or explanation matching question; no demand for recommendations where not asked. Unsupported claims avoidance: 1 if none, 0.5 for minor unsupported claims, 0 for material invented facts, causal claims, forecasts or claims of actions taken. Explicit uncertainty is not fabrication, but missing facts still reduce accuracy/completeness. Weights are 30/25/20/15/10. Report per-arm mean and each criterion, raw responses, model version, tokens, elapsed time and all failures. No significance claim from six single trials; no fabricated uplift. Publish results only after human scoring. This is a protocol, not a completed experiment.

## Completed run — November 25, 2026 (provisional AI-assisted scores)

The initial live run recorded 18 authentication failures and is excluded from quality comparisons. After authentication was corrected, a new output directory (`benchmark-run-2`) completed 18/18 requests. All successful calls resolved to `gpt-4.1-mini-2025-04-14`. The protocol and scoring rubric were unchanged. ChatGPT applied the rubric before the arm mapping was revealed; evidence formats make blinding partial. These are AI-assisted scores, not independently human-validated results. Human review remains pending; the original protocol's human-scoring requirement for final publication is not yet fulfilled.

| Metric | A: metrics only | B: context-rich flat | N: Nexus |
|---|---:|---:|---:|
| Weighted quality | 38.33% | 89.17% | 85.42% |
| Factual accuracy | 33.33% | 83.33% | 83.33% |
| Evidence completeness | 33.33% | 91.67% | 100% |
| Input tokens | 2,205 | 291,095 | 19,044 |
| Output tokens | 1,323 | 2,121 | 2,209 |
| Mean API duration (seconds) | 2.145 | 5.807 | 3.721 |
| At 500-token cap | 0 | 1 | 2 |
| Successful calls | 6 | 6 | 6 |

Nexus used **93.46% fewer input tokens** and had **35.93% lower mean provider-request duration** than B, with equal factual accuracy and 3.75 percentage points lower weighted quality. B was the strongest quality baseline. Durations exclude context preparation and database queries; these data do not establish end-to-end speed or actual billed savings. No optimized flat retrieval comparator was evaluated, so the observed difference cannot be attributed uniquely to graph technology. Financial invariance errors and hypothetical scenario wording need improvement. The output cap likely truncated some responses; finish reasons were not recorded.

Artifacts: [raw responses](webapp/src/benchmark-data/raw_responses.json), [scores](webapp/src/benchmark-data/results.json), [scorecard with AI-assisted rationale](webapp/src/benchmark-data/scorecard.csv), [reference answers](webapp/src/benchmark-data/reference_answers.json), [manifest](webapp/src/benchmark-data/manifest.json). They contain synthetic records only; no provider credentials. The archived scorecard has been normalized to the original CSV columns, removing the spreadsheet parser's index.

Reproduce the score aggregation offline (no API requests): copy the archived data to a new directory, copy `benchmark_protocol.json` there as `protocol.json`, and run `python benchmark.py <directory> --score`. Reproduce context inputs with a separate dry run. The dashboard derives usage and mean latency from the archived raw responses; it does not run the benchmark on page load.
