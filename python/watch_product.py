"""Watch a specific Walmart product by its /ip/<slug>/<usItemId> URL.

Usage:
    export APIFY_TOKEN=...
    python watch_product.py https://www.walmart.com/ip/.../12345678
"""
import os
import sys

from apify_client import ApifyClient


def main(urls):
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor("zet46/walmart-search-scraper").call(run_input={
        "productUrls": urls,
    })
    for it in client.dataset(run.default_dataset_id).iterate_items():
        print("-" * 72)
        print(f"{it['name']}")
        print(f"  usItemId    : {it['usItemId']}")
        print(f"  brand       : {it.get('brand')}")
        print(f"  category    : {it.get('category')}")
        print(f"  price       : ${it.get('price'):.2f}" if it.get("price") else "  price       : --")
        if it.get("wasPrice"):
            was = it["wasPrice"]
            price = it.get("price") or was
            pct = (was - price) / was * 100
            print(f"  wasPrice    : ${was:.2f}  (-{pct:.1f}% off)")
        print(f"  badge       : {it.get('badge')}")
        print(f"  seller      : {it.get('seller')}")
        print(f"  rating      : {it.get('rating')} ({it.get('reviewCount')} reviews)")
        print(f"  availability: {it.get('availability')}")
        print(f"  url         : {it['url']}")


if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("usage: python watch_product.py <walmart /ip/ URL> [...]")
        sys.exit(1)
    main(urls)
