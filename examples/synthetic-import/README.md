# Local synthetic CSV example

This intentionally different dataset is fictional. It contains two products, three campaigns, three customers, four touchpoints and three orders. Two campaigns promote the same product, one product is low stock, and one purchase has no observed touch.

From the repository root with dependencies installed:

```sh
python dataset_import.py validate examples/synthetic-import
python dataset_import.py import examples/synthetic-import imported-demo.rl
python dataset_import.py summary imported-demo.rl --model last_touch
python store.py export imported-demo.rl > imported-network.json
```

Expected: 15 nodes, 17 edges, 43 units of inventory, $210 recorded revenue, $80 COGS, $80 spend, $50 profit after ads, $130 attributed revenue and $80 unattributed revenue. No API key or provider call is needed.

## Format

The five filenames and exact headers in this folder are the schema. Each ID must be globally unique, 1–64 ASCII alphanumeric/dot/underscore/hyphen characters, beginning with an alphanumeric character. All links must reference an existing record of the appropriate type. Product and campaign names must be unique (case-insensitive). No personal identifiers, email addresses, extra columns or real customer data. The tool is intended for synthetic data only; it does not automatically detect personal data in free-text fields.

Each order is one unit of exactly one product. Product unit cost is constant across all orders. Spend and stock are snapshots, not time series. Prices and order revenues must be positive; cost/spend may be zero. All monetary fields are nonnegative amounts with at most two decimal places, up to nine integer digits; stock is a nonnegative integer. Timestamp offsets are required and normalized to UTC. Missing touchpoints are allowed and purchases without eligible touches remain unattributed. The standard attribution lookback is 30 days. Purchases need not equal list price. Returns, discounts as separate fields, multi-unit baskets and historical costs are not supported. Up to 5,000 rows and 2 MiB per file; products, campaigns and customers require at least one row. Event files may contain headers only.

The importer validates before writing, builds a temporary single-file Relate store, checks counts, commits and reopens read-only, computes a summary, and publishes using a no-overwrite hard link on the same local filesystem. Existing .rl files are never replaced. A filesystem that does not support hard links will reject publication. The public demo and dashboard still use the original isolated synthetic seed; no upload endpoint or dataset switching is provided by this milestone. Local summaries use the existing analytics; not all dashboard views support arbitrary IDs yet.

ChatGPT assisted with importer implementation, tests, sample data and documentation.
