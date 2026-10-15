"""Daily Walmart Rollback tracker.

Logs one row per product per day into SQLite, then prints:
  - today's deepest Rollbacks
  - items where the Rollback got deeper vs. the previous run
  - items that became Rollback today (weren't on sale yesterday)

Run once a day via Apify Scheduler, local cron, or Windows Task Scheduler.

Usage:
    export APIFY_TOKEN=...
    python track_rollbacks.py
"""
import os
import sqlite3
from datetime import date
from pathlib import Path

from apify_client import ApifyClient

QUERIES = ["coffee maker", "headphones", "vacuum", "monitor", "office chair"]
MAX_PER_QUERY = 60
DB = Path("walmart_rollbacks.sqlite3")


def scrape():
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor("zet46/walmart-search-scraper").call(run_input={
        "queries": QUERIES,
        "maxItemsPerQuery": MAX_PER_QUERY,
        "includeSponsored": False,
    })
    return list(client.dataset(run.default_dataset_id).iterate_items())


def write(con, items, today):
    con.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            run_date      TEXT,
            us_item_id    TEXT,
            query         TEXT,
            name          TEXT,
            price         REAL,
            was_price     REAL,
            badge         TEXT,
            seller        TEXT,
            rating        REAL,
            review_count  INTEGER,
            url           TEXT,
            PRIMARY KEY (run_date, us_item_id)
        )""")
    for it in items:
        if it.get("sponsored"):
            continue
        con.execute(
            "INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (today, it["usItemId"], it.get("query"), it["name"],
             it.get("price"), it.get("wasPrice"), it.get("badge"),
             it.get("seller"), it.get("rating"),
             it.get("reviewCount"), it["url"]),
        )


def section(title):
    print()
    print(title)
    print("-" * len(title))


def report(con, today):
    section(f"Rollbacks on {today} (top 20 by discount %)")
    for row in con.execute("""
        SELECT name, price, was_price,
               ROUND(100.0 * (was_price - price) / was_price, 1) AS pct,
               seller
        FROM prices
        WHERE run_date = ? AND badge = 'Rollback' AND price < was_price
        ORDER BY pct DESC LIMIT 20""", (today,)):
        name, price, was, pct, seller = row
        print(f"  -{pct:>5}%  {name[:60]:60}  ${price:>7.2f}  (was ${was:>7.2f})  {(seller or '')[:24]}")

    section("Rollbacks that got DEEPER vs. previous run")
    for row in con.execute("""
        WITH t AS (
            SELECT us_item_id, name, price, was_price, badge, run_date,
                   LAG(price) OVER (PARTITION BY us_item_id ORDER BY run_date) AS prev_price
            FROM prices)
        SELECT name, prev_price, price, was_price,
               ROUND(100.0 * (prev_price - price) / prev_price, 1) AS dropped_today
        FROM t
        WHERE badge = 'Rollback' AND run_date = ? AND prev_price IS NOT NULL
          AND price < prev_price
        ORDER BY dropped_today DESC LIMIT 10""", (today,)):
        name, prev_price, price, was, drop = row
        print(f"  -{drop:>5}%  {name[:55]:55}  ${prev_price:>7.2f} -> ${price:>7.2f}  (list ${was:>7.2f})")

    section("New Rollbacks today")
    for row in con.execute("""
        WITH t AS (
            SELECT us_item_id, badge, run_date,
                   LAG(badge) OVER (PARTITION BY us_item_id ORDER BY run_date) AS prev_badge
            FROM prices)
        SELECT p.name, p.price, p.was_price, p.url
        FROM t JOIN prices p USING (us_item_id, run_date)
        WHERE t.badge = 'Rollback'
          AND (t.prev_badge IS NULL OR t.prev_badge != 'Rollback')
          AND t.run_date = ?
        ORDER BY (p.was_price - p.price) / p.was_price DESC LIMIT 10""", (today,)):
        name, price, was, url = row
        if not was:
            continue
        pct = (was - price) / was * 100
        print(f"  -{pct:>5.1f}%  {name[:55]:55}  ${price:>7.2f}  (was ${was:>7.2f})")


def main():
    items = scrape()
    today = date.today().isoformat()
    print(f"Scraped {len(items)} Walmart products on {today}")
    with sqlite3.connect(DB) as con:
        write(con, items, today)
        report(con, today)


if __name__ == "__main__":
    main()
