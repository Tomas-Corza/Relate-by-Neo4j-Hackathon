# OpenClaw Nexus
Graph-powered marketing intelligence, built for the Relate by Neo4j Hackathon (November 2026).

## Problem
Marketing teams often evaluate advertising in isolation from orders, customer journeys, product costs and inventory. Nexus connects those records and provides auditable, descriptive recommendations instead of treating last-click revenue as causal lift.

## Run locally
Python 3.11 recommended, Linux x86-64/arm64, macOS arm64 or Windows x86-64 (Relate wheel availability).
```bash
git clone https://github.com/Tomas-Corza/Relate-by-Neo4j-Hackathon.git
cd Relate-by-Neo4j-Hackathon
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-preview.txt
python -m unittest discover -s tests -v
cd webapp
npm install
npm run build
cd ..
python -m uvicorn preview_api:app --host 127.0.0.1 --port 8000
```
Requires Node.js 22 (or compatible) and npm. Open http://127.0.0.1:8000 after building. The original Streamlit interface remains available with requirements.txt and streamlit run app.py.

Windows activation: `.venv\Scripts\activate`. No database server or API key required for the deterministic offline analyst. To enable optional OpenAI natural-language synthesis, set OPENAI_API_KEY in your shell; optionally set OPENAI_MODEL (default gpt-4.1-mini). Never commit credentials. The optional model sends synthetic evidence and the question to OpenAI.

## Architecture
Synthetic data → embedded Relate 1.2.0 → parameterized Cypher relationship traversal → reused attribution engine → campaign economics and inventory risk → read-only analyst → FastAPI → React dashboard (legacy Streamlit retained).

Relate is the actual data source for all dashboard analytics, not a decorative visualization. Each run creates and closes an isolated in-memory database to avoid shared thread or session state. Graph schema:
- Customer -HAS_TOUCH-> Touchpoint -FROM_CAMPAIGN-> Campaign -PROMOTES-> Product
- Customer -PLACED-> Order -CONTAINS-> Product

Cypher retrieves customer-linked touchpoints and purchases for attribution, joins orders to product costs, traverses campaign-to-product relationships for inventory risk, and retrieves individual journeys for visual exploration. Fixed query templates and parameterized customer IDs prevent arbitrary agent-generated database operations. There is no live advertising integration or write-capable agent.

## Demo walkthrough
1. Launch the app and inspect campaign economics.
2. Change attribution from linear to first-touch or last-touch and observe changes in allocated revenue.
3. Ask "Which campaigns have inventory risks?" to identify C2 and its low-stock promoted product.
4. Ask "Which campaigns have the best profitability?" to compare attributed gross profit less synthetic ad spend.
5. Explore customer U001 and inspect the linked touchpoints, campaigns, promoted products and purchases.
6. Expand the evidence and attribution audit to trace the results.

## Existing framework and new hackathon work
Author: Tomas Corza. Original project: https://github.com/Tomas-Corza/marketing-openclaw-ai

Reused verbatim: `attribution.py` is the original framework's `tools/multi_touch_attribution.py` (source blob SHA 83710c532ad965d83a81781875a05e22aebbc790). It provides timestamp validation, five attribution models (first touch, last touch, linear, position based, time decay), lookback windows, cent-preserving revenue allocation and conversion audits. This module is pre-existing and is not claimed as new competition work.

New for Nexus: `graph.py` implements embedded Relate, the synthetic graph schema, seed generation, Cypher evidence retrieval and campaign-level margin/spend analysis; `agent.py` implements read-only evidence-based question answering with optional OpenAI synthesis; `app.py` provides a new Streamlit interface with graph visualization and audit views; tests, CI, setup and deployment configuration are new. The original framework's modular, business-focused analytics approach informed the design. The original repository is unchanged. This is not a copy of its full dashboard.

## AI and third-party disclosure
Significant AI assistance: ChatGPT helped design the architecture, generate new code, tests, documentation and project thumbnail. The optional runtime OpenAI model summarizes graph-derived evidence; the offline mode is deterministic, not an LLM. Third-party tools: Relate (relate-db), React, Vite, Recharts, FastAPI, Uvicorn, Streamlit (legacy), pandas, OpenAI Python SDK, Python standard library and GitHub Actions. See their respective licenses. All records are synthetic; no employer or customer data is used.

## Limitations
Attribution is rule-based credit, not causal measurement. Gross profit excludes overhead, shipping, tax and returns. Data is fixed synthetic demo data, not live accounts; single-product orders simplify margin calculations. The agent cannot change budgets or execute financial actions. The public demo graph is recreated for each request; a persistent synthetic store can be downloaded or generated locally. Relate is an experimental dependency; verify CI and local execution before submission. No performance uplift is claimed.

## Deployment
Production uses the multi-stage Dockerfile and railway.toml to compile React and run FastAPI with Uvicorn on the assigned PORT. The Procfile is legacy. Live demo: https://openclaw-nexus-production-368d712a.up.railway.app (initial deployment and AI response manually verified by the author). GitHub Actions runs the integration tests on push. See https://github.com/Tomas-Corza/Relate-by-Neo4j-Hackathon/actions.

## Competition
https://relate.devpost.com/rules — public repository must have topic `relate`; add it in GitHub About settings if absent. Submit a working demo URL or a video of up to two minutes. Review final functionality, reuse disclosure, AI disclosure and applicable licenses before submitting.

## Public demo security and cost controls
The OpenAI key is read only in server-side Python from OPENAI_API_KEY. Never include it in source code, browser widgets, or screenshots. Configure it as a sealed Railway variable if supported. The public demo uses a global, atomic SQLite rolling quota shared across visitors in one service instance: 5 provider attempts per 60 seconds and 50 per 24 hours by default. Set NEXUS_REQUESTS_PER_MINUTE and NEXUS_REQUESTS_PER_DAY to adjust these values; zero disables provider calls. Attempts are reserved before contacting OpenAI, including failed requests. Questions are capped at 500 characters, completions at 500 tokens, retries disabled, and quota failures fall back to deterministic analysis. Error messages do not expose raw provider exceptions. NEXUS_QUOTA_DB defaults to /tmp/nexus-quota.sqlite3; mount a Railway volume and set it to /data/nexus-quota.sqlite3 to retain quota history across redeploys. Keep a single replica or use a shared external quota backend for multi-replica deployments. This is a shared public request limit, not an exact dollar cap or per-person authentication. Configure a dedicated OpenAI project with restricted endpoint access and provider-side rate limits/billing alerts as defense in depth. Quota storage records timestamps only.

## Executive dashboard edition
New hackathon UI modules `styles.py` and `ui_components.py` separate theme and reusable components from `app.py`. The interface includes eight navigable views, computed KPIs, Altair charts, inventory warnings, color-coded customer graphs, AI prompts and CSV exports. Corza Marketing branding is supplied by the author. Charts use the existing synthetic graph, not mockup figures. No fabricated time trends or causal forecasts. The original attribution module and Relate graph are preserved.

## Advanced graph intelligence and budget scenarios
New hackathon modules `intelligence.py` and `advanced_views.py` expose actual Relate node and edge counts, fixed Cypher queries with parameterized evidence, observed first-purchase touch sequences, customer-level historical revenue and gross profit, earliest-observed campaign cohorts, and all-five-model attribution sensitivity. The fixed-budget simulator shifts spend between paid campaigns under explicitly user-selected marginal gross-profit assumptions, flags low stock, preserves total spend and exports scenarios. It is not a forecast, causal experiment, or inventory demand model. Historical value is not predicted CLV. The original OpenClaw attribution module is unchanged and reused for each model comparison. New tests validate counts, revenue conservation, cohort coverage, path coverage, budget conservation and inventory warnings.

## Additional security hardening
Streamlit CORS and XSRF protection are enabled explicitly, detailed browser errors are hidden, and message sizes are bounded. Analyst output is rendered as plain text to avoid model-generated remote images and active links. A session cooldown supplements the atomic global quota; it is not an identity-based limit. OpenAI completion storage is explicitly disabled (provider abuse-monitoring retention may still apply). Do not submit confidential or personal data. CI uses read-only repository permissions and does not persist checkout credentials; a separate security workflow scans reachable commit patches for common credential formats and audits installed Python dependencies. Dependabot proposes weekly updates. See SECURITY.md for reporting guidance. These controls do not establish that the software is vulnerability-free.

## Premium interface
Grouped native Streamlit navigation, consistent chart formatting and legends, formatted campaign tables, enhanced KPI cards and branded dark styling. Navigation labels remain unchanged. All analytical functions, security controls and scenario assumptions are preserved.

## Visual graph workspace (November 25, 2026)
React customer timelines show actual timestamped Relate touchpoints and orders. Select a purchase to inspect the existing attribution engine's per-order allocations under the selected model. Business Connections renders a selectable relationship path from each fixed Cypher query result; raw records, exact queries and parameters remain expandable. These are query-result paths, not inferred causal edges or a full graph layout. No new third-party visual assets or graph libraries are used. Significant ChatGPT assistance includes this UI, API extension and tests; the pre-existing attribution module is unchanged. All data remains synthetic.

The Business Connections purchase-path view uses the existing Relate-derived path counts and campaign/channel mapping from the graph. It shows the five most frequent exact campaign sequences by default, with buyer counts and share of all purchasing customers; all paths and original records remain accessible. Repeated touches are preserved. This is descriptive sequence frequency, not conversion rate or causal attribution. ChatGPT assisted with this presentation refinement.

## Custom report builder
Reports supports three validated scopes: all-data campaign economics, recorded orders/customers, and attributed purchase credit. Choose metrics, dimensions, optional breakdown, exact-value filter, UTC purchase-date bounds, model and sorting; preview a table or single-metric chart and export precisely the resulting columns and rows as CSV. The JSON export records report settings for manual reproduction (no import yet). Fixed read-only Relate queries feed Python grouping, with complete touch history retained for attribution; no arbitrary Cypher. Undated spend and stock cannot be split by dates or purchased products. No new data or dependencies were added. ChatGPT assisted with the report engine, interface, tests and documentation.

## Dedicated advertising and profit dashboards
Advertising focuses on campaign investment, blended revenue/spend, attributed ROAS, fractional acquisition/conversion credit, CAC proxy, CPA and review signals. Profit analysis reconciles recorded order revenue and product costs to gross profit and recorded campaign spend to profit after ads, independently of attribution model; separately shows attributed campaign profitability and its reconciliation difference. Product profitability is before ads, not an invented allocation of spend. The existing fixed Relate queries supply all figures. No new data or dependencies; ChatGPT assisted with the interface, financial summary and tests.

## Inventory intelligence
The inventory workspace reads unique Product nodes and existing PROMOTES and CONTAINS relationships. It preserves all four original campaign rows while counting the three distinct products once (208 units). Shows stock snapshot, low-stock exposure, cost and list-price valuations, observed units sold (single-unit synthetic orders), product gross profit, linked campaigns and filtered inventory CSV. Campaign spend describes promoted-product exposure, not allocation to purchased products. No historical stock movements, turnover or stockout forecasts are invented. ChatGPT assisted with the interface, read-only product query, calculations and tests.

## Attribution sensitivity workspace
Revenue Sources compares the five existing attribution models using actual Relate-derived results. Metric-selectable grouped bars, a linear-baseline revenue heatmap, campaign revenue ranges, arithmetic mean, range/mean, profitability sign counts and revenue-rank ranges show model dependence. Ties share ranks; undefined ratios remain blank. CSV exports contain all model results and sensitivity statistics. The original attribution engine is unchanged; model agreement is not statistical confidence or causal evidence. ChatGPT assisted with this UI, descriptive calculations and tests; no new dependencies or synthetic records were added.

## Inspectable persistent graph and network explorer
Business Connections includes a selectable one- or two-hop neighborhood of the actual Relate graph, typed nodes, directed edges, properties, pan/zoom, filters and exact fixed queries. Layout is computed in the browser from queried nodes/edges, not inferred causal relationships. Download the synthetic .rl store from the same page or generate locally:

```bash
python store.py create nexus-demo.rl
python store.py inspect nexus-demo.rl
python store.py export nexus-demo.rl > nexus-graph.json
```

Creation refuses existing files; use a new filename to reseed. Inspect/export open read-only. The download creates an isolated temporary .rl file, closes it and returns its bytes; the public app still uses isolated in-memory graphs and does not accept user paths or uploads. Format is Relate 1.2.0, see https://relatedb.ai/docs/reference/api/python/. ChatGPT assisted with implementation, tests and documentation.

## Bounded investigation agent
The React AI Assistant now executes a deterministic, keyword-routed investigation with evidence-based selection of an illustrative budget scenario. Seven allowlisted analytical tools cover campaign economics, inventory, PROMOTES graph traversal, customer journeys, five-model sensitivity, recorded finances and budget simulation. Every completed tool returns its actual evidence, fixed Cypher templates and analysis parameters; IDs E1…E7 link findings to the execution trace. No generated Cypher, arbitrary tool calls or write actions. The router is not an autonomous LLM planner. Optional OpenAI synthesis uses one provider attempt per investigation under the existing shared quota, timeout, no-retry and token limits; unavailable synthesis falls back to deterministic findings. The legacy Streamlit analyst remains unchanged. The budget example automatically selects the weakest paid gross-profit/spend campaign and strongest available-stock alternative, with up to $300 and 50% assumed marginal efficiency; not a forecast or executed action. All data remains synthetic. ChatGPT assisted with this implementation, tests and docs.

## Connected intelligence benchmark
See [BENCHMARK.md](BENCHMARK.md) for the predefined three-arm, six-question local evaluation protocol, dry-run preparation, opt-in provider execution and human scoring. Completed provisional results are documented below. ChatGPT assisted with the protocol, runner, tests and UI. This measures context delivery and answer grounding, not intrinsic graph superiority.

## Business Connections navigation
The workspace defaults to business insights (low-stock campaign exposure and shared product relationships), with separate Graph explorer and Purchase paths views. Contextual graph buttons focus actual connected IDs. The graph starts with touchpoints hidden for clarity, uses compact columns and readable property labels; advanced filters and exact queries remain accessible. All six original evidence queries, purchase paths, and persistent store download remain available. No graph records or analytical formulas changed. ChatGPT assisted with this usability refinement.

## Business map
Business Connections now starts with a clickable aggregate map of actual stored entity counts and relationship types, then offers four business-oriented questions and four additional record queries. Only the selected question is shown. Product performance combines observed sales, unique product stock and associated campaign spend without attributing sales to campaigns. The full graph explorer remains optional, and readable business records are separate from collapsed developer query audits. No synthetic records, formulas or backend APIs were changed. ChatGPT assisted with the interface refinement.

## Guided demo
Start the optional six-step walkthrough on Overview to follow the existing synthetic inventory-risk case through Business Connections, Revenue Sources, AI Assistant, Budget Planning and Reports. The guide links existing workspaces and offers manual next/previous/exit controls; it does not automatically call AI, change budgets or export data. Starting resets attribution to linear. The $300 transfer at 50% efficiency is illustrative, not a forecast. All workspaces remain accessible independently. ChatGPT assisted with this usability feature.

### Completed benchmark (provisional AI-assisted evaluation)

The AI assistant page now includes the completed 18-response benchmark. Nexus used 93.46% fewer input tokens than the context-rich flat-data baseline with equal factual accuracy; weighted quality was 85.42% versus 89.17%, respectively. See [methodology, archived responses, scores and limitations](BENCHMARK.md#completed-run--november-25-2026-provisional-ai-assisted-scores). Independent human validation is pending; no general graph superiority or end-to-end latency claim is made.

## Local synthetic CSV import

Nexus can now validate five linked CSV tables and construct a new persistent Relate database with the same schema as the original demo. Reproduce the [original Nexus dataset and schema](examples/synthetic-import/README.md). Download the five CSV files as a ZIP from Business Connections or generate them locally:

```bash
python dataset_export.py nexus-original-csv
python dataset_import.py validate nexus-original-csv
python dataset_import.py import nexus-original-csv imported-demo.rl
python dataset_import.py summary imported-demo.rl --model linear
```

The summary uses the existing attribution, finance, inventory and customer-economics functions on the imported store. Invalid records or dangling relationships are rejected before any store is published. Existing stores are never overwritten. No AI API calls, public upload endpoint, production configuration changes or dashboard dataset switching. Use fictional data only. ChatGPT assisted with the implementation and tests.

The canonical export is generated directly from the existing Relate graph. Automated round-trip tests compare all stored nodes and relationships, five attribution models, recorded financials, inventory and selected customer journeys. The alternate small dataset remains an internal validation fixture only. No public uploads or dataset switching.

## Browser end-to-end validation

The React release workflow now includes Playwright Chromium tests against the built frontend and actual local FastAPI/Relate backend. Tests cover the ten workspaces, attribution switching, guided navigation, canonical ZIP and persistent store downloads, fixed-budget simulation, custom report exports, deterministic investigation, benchmark rendering and narrow-screen navigation. No external AI requests: the test server explicitly clears OPENAI_API_KEY. Existing backend and Docker checks remain in place.

Run locally after installing Python dependencies:

```sh
cd webapp
npm install
npm run build
npx playwright install chromium
npm run test:e2e
```

The harness starts its own localhost server on port 8765 and refuses to reuse an existing service. CI uploads the HTML report and failure traces/screenshots. This covers representative browser flows, not exhaustive cross-browser, accessibility, visual regression or live provider validation. ChatGPT assisted with the tests and CI configuration.
