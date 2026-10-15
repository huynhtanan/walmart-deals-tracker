# walmart-deals-tracker

Python examples that pull Walmart.com products and Rollback deals, log them to SQLite day over day, and surface the deepest discounts.

Uses the [Walmart Search Scraper](https://apify.com/zet46/walmart-search-scraper) on Apify — pay-per-result at **$1 / 1,000 products**. New Apify accounts get free monthly credit that covers tens of thousands of items.

## What's in here

| Script | What it does |
|---|---|
| [`python/today_rollbacks.py`](python/today_rollbacks.py) | Lists all Rollback deals across a few search queries, sorted by discount %. |
| [`python/track_rollbacks.py`](python/track_rollbacks.py) | Logs one row per product per day into SQLite, prints today's deals + items whose Rollback got deeper + brand-new Rollbacks. |
| [`python/watch_product.py`](python/watch_product.py) | Watches a specific product by its `/ip/<slug>/<usItemId>` URL and prints price, wasPrice, badge, rating, seller, availability. |

## Quick start

```bash
pip install "apify-client>=3"
export APIFY_TOKEN=...   # from https://console.apify.com/settings/integrations

python python/today_rollbacks.py
```

Real output (ran today, 3 queries × top 30 each = 90 products, 11 of them Rollbacks):

```
Walmart Rollbacks across 3 search queries (90 products, 11 on Rollback)

- 44.6%  vacuum        Eureka MaxSwivel Deluxe Upright Vacuum with Swiv  $  49.86  (was $  89.99)  Walmart.com
- 34.1%  vacuum        Shark Navigator Lift-Away Upright Vacuum, Pet Fr  $ 118.00  (was $ 179.00)  Walmart.com
- 31.8%  vacuum        BISSELL PowerForce Helix Turbo Pet, Bagless, Upr  $  74.97  (was $ 109.99)  Walmart.com
- 25.2%  headphones    Skullcandy Smokin' Buds XT True Wireless in-Ear   $  14.88  (was $  19.88)  Walmart.com
- 23.8%  headphones    Apple AirPods 4                                   $  99.00  (was $ 129.99)  Walmart.com
- 21.0%  headphones    Skullcandy Crusher XT Wireless Foldable over-Ear  $  79.00  (was $ 100.00)  Walmart.com
- 15.5%  coffee maker  Keurig K-Duo Essentials Hot & Iced Single Serve   $ 109.00  (was $ 129.00)  Walmart.com
- 13.2%  coffee maker  Ninja Hot & Iced 10-Cup Drip Coffee Maker, 4 Bre  $  99.00  (was $ 114.00)  Walmart.com
- 13.0%  coffee maker  Hamilton Beach FlexBrew 5-in-1 Coffee Maker, Hot  $  87.00  (was $  99.96)  Walmart.com
- 11.4%  vacuum        BISSELL PowerForce Helix, Bagless, Upright Vacuu  $  59.76  (was $  67.48)  Walmart.com
- 10.0%  coffee maker  Keurig K-Express Essentials Black Single-Serve K  $  49.47  (was $  54.97)  Walmart.com
```

Full write-up on dev.to: [Track Walmart Rollback deals with Python + SQLite](https://dev.to/huynhtanan).

## Running once a day

Three options, pick any:

- **Apify Scheduler.** On the actor page click *Schedule actor*, pick a cron, save your input. Pull the latest completed dataset with `client.actor(...).last_run().get()` from any machine.
- **Local cron / Windows Task Scheduler.** `python track_rollbacks.py` every morning — each run also triggers a fresh scrape.
- **GitHub Actions.** 5-line workflow with `on: schedule: cron: "0 15 * * *"` and `APIFY_TOKEN` as a repo secret.

## Cost

Pay-per-result on Apify, `$1 per 1,000 products`.

- Top 60 of 5 queries daily: 300 products = **$0.30/day = ~$9/month**.
- Once a week: `~$1.20/month`.

Sponsored items, duplicates (by `usItemId` across pages), and items below `minRating` are not charged.

## Schema

Every row has the following fields:

```
usItemId, name, url, price, wasPrice, currency, rating, reviewCount,
image, category, seller, sellerId, availability, outOfStock, badge,
sponsored, fulfillment, position, page, query, brand, shortDescription,
scrapedAt
```

Not every row has every field — `price` and `wasPrice` can be `None` (seller-set "see price in cart", or no sale), `brand` / `shortDescription` are only populated for `/ip/` detail URLs. See the actor's [input + output schema](https://apify.com/zet46/walmart-search-scraper) for the full documentation.

## License

MIT. See [LICENSE](LICENSE).
