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
pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```
Windows activation: `.venv\Scripts\activate`. No database server or API key required for the deterministic offline analyst. To enable optional OpenAI natural-language synthesis, set OPENAI_API_KEY in your shell; optionally set OPENAI_MODEL (default gpt-4.1-mini). Never commit credentials. The optional model sends synthetic evidence and the question to OpenAI.

## Architecture
Synthetic data → embedded Relate 1.2.0 → parameterized Cypher relationship traversal → reused attribution engine → campaign economics and inventory risk → read-only analyst → Streamlit dashboard.

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
Significant AI assistance: ChatGPT helped design the architecture, generate new code, tests, documentation and project thumbnail. The optional runtime OpenAI model summarizes graph-derived evidence; the offline mode is deterministic, not an LLM. Third-party tools: Relate (relate-db), Streamlit, pandas, OpenAI Python SDK, Python standard library and GitHub Actions. See their respective licenses. All records are synthetic; no employer or customer data is used.

## Limitations
Attribution is rule-based credit, not causal measurement. Gross profit excludes overhead, shipping, tax and returns. Data is fixed synthetic demo data, not live accounts; single-product orders simplify margin calculations. The agent cannot change budgets or execute financial actions. The graph is recreated each run and is not persistent. Relate is an experimental dependency; verify CI and local execution before submission. No performance uplift is claimed.

## Deployment
A Procfile is provided for a compatible Python host such as Railway; configure the service to install requirements and expose its assigned PORT. Live demo: https://openclaw-nexus-production-368d712a.up.railway.app (initial deployment and AI response manually verified by the author). GitHub Actions runs the integration tests on push. See https://github.com/Tomas-Corza/Relate-by-Neo4j-Hackathon/actions.

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
