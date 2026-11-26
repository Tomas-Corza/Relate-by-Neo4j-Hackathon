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
