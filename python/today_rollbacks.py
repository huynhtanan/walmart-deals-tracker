"""Print every Rollback deal across several Walmart searches, sorted by discount %.

Usage:
    export APIFY_TOKEN=...
    python today_rollbacks.py
"""
import os
from apify_client import ApifyClient

QUERIES = ["coffee maker", "headphones", "vacuum"]
MAX_PER_QUERY = 30

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("zet46/walmart-search-scraper").call(run_input={
    "queries": QUERIES,
    "maxItemsPerQuery": MAX_PER_QUERY,
    "includeSponsored": False,
})
items = list(client.dataset(run.default_dataset_id).iterate_items())

rollbacks = [
    i for i in items
    if i.get("badge") == "Rollback" and i.get("wasPrice") and i.get("price")
]
rollbacks.sort(key=lambda x: -(x["wasPrice"] - x["price"]) / x["wasPrice"])

print(f"Walmart Rollbacks across {len(QUERIES)} search queries "
      f"({len(items)} products, {len(rollbacks)} on Rollback)")
print()
for r in rollbacks:
    pct = (r["wasPrice"] - r["price"]) / r["wasPrice"] * 100
    seller = (r.get("seller") or "")[:28]
    print(f'-{pct:>5.1f}%  {r["query"]:12}  {r["name"][:48]:48}  '
          f'${r["price"]:>7.2f}  (was ${r["wasPrice"]:>7.2f})  {seller}')
