# Hackathon submission guide

Prepared for the Relate by Neo4j Hackathon. Official rules: https://relate.devpost.com/rules. Deadline: December 11, 2026, 6:00 PM PST, subject to the official contest clock. This guide is a preparation aid; it does not submit the entry.

## Entry information

**Project title:** OpenClaw Nexus

**Pitch:** Connected marketing intelligence that uses embedded Relate to connect campaigns, customer journeys, orders, product costs and inventory, enabling evidence-backed decisions instead of isolated advertising metrics.

**Repository:** https://github.com/Tomas-Corza/Relate-by-Neo4j-Hackathon

**Working demo:** https://openclaw-nexus-production-368d712a.up.railway.app/

**Author:** Tomas Corza

## Suggested Devpost description

Marketing decisions often depend on data scattered across advertising, orders, inventory and customer interactions. OpenClaw Nexus connects these records with embedded Relate, so a business can see not only how a campaign performs, but which product it promotes, whether stock is available, what customers purchased and how the result changes across attribution assumptions.

Nexus uses fixed Cypher traversals of an actual graph containing 396 nodes and 622 relationships. Its investigation agent executes allowlisted analytical tools, exposes their evidence, and optionally synthesizes findings using OpenAI. It also provides profitability reconciliation, customer journeys, inventory analysis, hypothetical budget planning, custom reports, and downloadable persistent Relate and CSV data.

In a six-question synthetic evaluation, Nexus used 93.46% fewer input tokens than a context-rich flat-data baseline, with equal factual accuracy and lower overall weighted quality (85.42% versus 89.17%). Scoring was AI-assisted and remains provisional; the experiment does not establish statistical significance or intrinsic graph superiority.

The primary React interface runs with FastAPI and embedded Relate. The public demo uses isolated in-memory graphs; a downloadable single-file Relate store and local CSV round-trip make the original dataset inspectable and reproducible. No API key is required for deterministic analysis.

Nexus is new hackathon work that reuses the author's earlier multi-touch attribution module. Significant ChatGPT assistance includes design, code, tests, documentation, thumbnail and provisional benchmark scoring. Runtime OpenAI synthesis is optional. The [README](README.md) contains complete technology and reuse disclosures.

## Two-minute video outline

Record the actual application; use original narration and only owned or appropriately licensed media.

| Time | Show | Suggested narration |
|---|---|---|
| 0:00–0:15 | Overview, inventory warning | “Marketing metrics alone miss connected business risks. Nexus links advertising to inventory, purchases and customer journeys with embedded Relate.” |
| 0:15–0:35 | Business Connections, C2 → P2; shared product example | “This campaign spent $1,800 while its promoted product has just three units left. These are actual stored graph relationships.” |
| 0:35–0:55 | Revenue Sources sensitivity | “The campaign loses money across all five attribution models. Recorded financial totals do not change when attribution changes.” |
| 0:55–1:15 | AI Assistant, execute investigation, expand evidence | “Nexus selects and executes bounded graph-derived analytical tools, then returns the evidence behind its findings. The deterministic mode needs no AI key.” |
| 1:15–1:32 | Benchmark panel | “In our limited synthetic test, Nexus used 93.46% fewer input tokens than the broad flat-data baseline. Quality was slightly lower overall, with equal factual accuracy; scoring is provisional.” |
| 1:32–1:48 | Budget Planning, $300 C2 → C3 at 50% | “This hypothetical fixed-budget transfer models a $285.27 improvement. It is a scenario, not a forecast or an executed change.” |
| 1:48–2:00 | Reports or Business Connections downloads | “Judges can run the app, inspect the persistent Relate store and rebuild the same graph from CSV. OpenClaw Nexus makes connected decisions auditable.” |

The guided demo selects C1 as the example destination; for the specific $285.27 benchmark figure above, manually select C3 (Retention email), amount $300, efficiency 50%, and linear attribution. Rehearse and verify all numbers before recording. Record at most two minutes; a working demo link is also permitted by the official rules. The overview checklist specifically encourages a persistent store and video.

## Submission checklist

- [x] Public GitHub repository and required `relate` topic verified when this documentation was prepared.
- [x] Working Relate integration, setup instructions and disclosed storage modes.
- [x] Downloadable persistent graph and reproducible canonical CSV data.
- [x] Implementation, reused attribution module and AI/tool disclosures documented.
- [x] Integration, production Docker and Chromium browser checks passed on the previous merged implementation (PR #31).
- [ ] Author verifies rights and licensing for code, branding, images and video materials. No repository-wide license is added by this documentation; an open-source license is encouraged by the rules, not mandatory.
- [ ] Author confirms eligibility, team information and project start date.
- [ ] Author verifies the final live demo and downloads in a logged-out browser.
- [ ] Add optional `relate-neo4j-hackathon` topic if desired; keep required `relate` topic and public visibility through winner announcement.
- [ ] Record and upload the final video if including one, and verify accessibility without login/payment.
- [ ] Paste final description and links into Devpost, check all required fields, and submit before the deadline.

Do not claim human-validated benchmark scores, general graph superiority, causal business lift, billed savings, or an autonomous write-capable agent. Independent benchmark review is optional for the contest; the project's own protocol requires human scoring before finalizing those scores. Until then keep the provisional label.
