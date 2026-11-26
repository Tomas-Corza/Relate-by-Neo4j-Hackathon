# Reproduce the original Nexus dataset

The canonical example is the **same original synthetic business** used by the public dashboard, investigation agent and benchmark. Export the five CSV files directly from the actual seeded Relate graph, or download the ZIP from Business Connections → Developer audit and reproducibility.

```sh
python dataset_export.py nexus-original-csv
python dataset_import.py validate nexus-original-csv
python dataset_import.py import nexus-original-csv nexus-rebuilt.rl
python dataset_import.py summary nexus-rebuilt.rl --model linear
python store.py export nexus-rebuilt.rl > nexus-rebuilt-network.json
```

Expected: 80 customers, 237 touchpoints, 4 campaigns, 3 products, 72 orders, 396 nodes and 622 relationships. Recorded revenue $6,970, COGS $2,770, gross profit $4,200, spend $3,150, profit after ads $1,050; inventory 208 units. No AI API calls required. The exporter refuses an existing output directory. No separately maintained copy of canonical data is used.

The smaller lighting dataset is now strictly an internal fixture under tests/fixtures/import-small. Automated parity tests compare original and reconstructed nodes, relationships, financials, inventory, customer journeys and all five attribution models.

## Format

The five generated filenames and exact headers defined in dataset_import.py are the schema. Each ID must be globally unique, 1–64 ASCII alphanumeric/dot/underscore/hyphen characters, beginning with an alphanumeric character. All links must reference an existing record of the appropriate type. Product and campaign names must be unique (case-insensitive). No personal identifiers, email addresses, extra columns or real customer data. The tool is intended for synthetic data only; it does not automatically detect personal data in free-text fields.

Each order is one unit of exactly one product. Product unit cost is constant across all orders. Spend and stock are snapshots, not time series. Prices and order revenues must be positive; cost/spend may be zero. All monetary fields are nonnegative amounts with at most two decimal places, up to nine integer digits; stock is a nonnegative integer. Timestamp offsets are required and normalized to UTC. Missing touchpoints are allowed and purchases without eligible touches remain unattributed. The standard attribution lookback is 30 days. Purchases need not equal list price. Returns, discounts as separate fields, multi-unit baskets and historical costs are not supported. Up to 5,000 rows and 2 MiB per file; products, campaigns and customers require at least one row. Event files may contain headers only.

The importer validates before writing, builds a temporary single-file Relate store, checks counts, commits and reopens read-only, computes a summary, and publishes using a no-overwrite hard link on the same local filesystem. Existing .rl files are never replaced. A filesystem that does not support hard links will reject publication. The public demo and dashboard still use the original isolated synthetic seed; no upload endpoint or dataset switching is provided by this milestone. Local summaries use the existing analytics; not all dashboard views support arbitrary IDs yet.

ChatGPT assisted with importer implementation, tests, sample data and documentation.
