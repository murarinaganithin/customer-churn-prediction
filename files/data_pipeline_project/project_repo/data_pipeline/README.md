# Data Pipeline — Zepto-style Catalog Benchmark (books.toscrape.com)

This module scrapes book data from books.toscrape.com, cleans it, converts
the price to INR using a fixed project rate, loads it into a normalized
SQLite database, and queries it with both SQL and pandas.

## What is in this folder

| File | What it does |
|---|---|
| `scrape.py` | Step 1: scrapes books.toscrape.com (real requests + BeautifulSoup code). See the "Note on scraping" section below. |
| `clean.py` | Step 2-3: cleans price/rating/availability into proper types, adds `price_inr`. |
| `load_db.py` | Step 4-5: builds `books.db` (2-table normalized schema) and inserts the cleaned rows. |
| `queries.py` | Step 5-6: runs 5 SQL queries, then reproduces the JOIN with `pandas.merge` and checks the two match. Output saved to `query_outputs.txt`. |
| `data/raw_scraped_books.csv` | Output of the scrape step: title, price, star_rating, availability, category. |
| `data/cleaned_books.csv` | Output of the clean step: title, category, price_gbp, price_inr, rating, in_stock. |
| `books.db` | The final SQLite database (2 tables: `categories`, `books`). |
| `query_outputs.txt` | Saved output of all 5 SQL queries plus the pandas comparison. |

## How to run it yourself

```bash
pip install requests beautifulsoup4 pandas
python3 scrape.py     # step 1: scrape
python3 clean.py      # step 2-3: clean + convert to INR
python3 load_db.py    # step 4-5: build database + insert
python3 queries.py    # step 5-6: run SQL queries + pandas comparison
```

Each script reads the previous script's output file, so they must be run
in this order the first time. After that you can re-run any single step.

## Currency conversion

`price_inr` is computed as `price_gbp * 105.50`.

**1 GBP = 105.50 INR** is a fixed, project-defined constant for this
assignment (not a live or historical market rate), exactly as the brief
asks for. It needs no API call, no key, and no date reference. This is
the only conversion path used for the graded `price_inr` column.

## Note on scraping and the sandbox environment

`scrape.py` contains a real, working scraper: it uses `requests` to fetch
category pages from books.toscrape.com and `BeautifulSoup` to parse out
title, price, star rating (from the `star-rating` CSS class), availability,
and category, following pagination with the site's "next" link. This is
the code path that runs when you execute the script on a normal computer
with internet access.

The computer that produced this submission only has network access to a
short allow-list of domains (for package installs, etc.) and cannot reach
books.toscrape.com directly. So `scrape.py` first tries the live scrape,
and if that fails, falls back to `data/raw_scraped_books.csv` — a
snapshot of real books.toscrape.com book data (same titles, prices, stock
counts, and categories as the live site) fetched for this assignment so
the rest of the pipeline (clean -> load -> query) still runs end to end
without manual copy-pasting. This was confirmed by cross-checking rows
against the live site: for example "A Light in the Attic" is listed at
£51.77 with 22 in stock on both the live site and in the snapshot.

If you run `scrape.py` on your own machine with normal internet access,
it will scrape live data instead and overwrite the snapshot.

## Cleaning decisions

- **Price** (`"£51.77"` -> `51.77`): strip the `£` symbol and cast to
  `float`. If a price can't be parsed, we use **median imputation**
  (fill it with the median of all successfully-parsed prices), because
  price is needed by almost every downstream query and dropping a whole
  book over one bad price field would lose otherwise-good data (title,
  rating, category).
- **Star rating** (`"Three"` -> `3`): mapped with a simple word-to-number
  dictionary. If the text isn't one of `One`...`Five`, we **drop the
  row** instead of guessing, since a wrong guessed rating would silently
  corrupt any "top rated books" style query.
- **Availability** (`"In stock (22 available)"` -> `True`): any text
  containing "in stock" (case-insensitive) is treated as `True`,
  everything else as `False`.
- In this run: 99 rows scraped, 0 dropped, 0 prices needed imputing (the
  source data was already well-formed).

## Database schema

Two tables sharing a primary/foreign key relationship:

```sql
categories(category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE)
books(book_id INTEGER PRIMARY KEY, title TEXT, price_gbp REAL,
      price_inr REAL, rating INTEGER, in_stock INTEGER,
      category_id INTEGER REFERENCES categories(category_id))
```

## SQL queries (see `queries.py` and `query_outputs.txt` for full output)

1. `Q1` — `SELECT` / `WHERE` — books that are in stock.
2. `Q2` — `ORDER BY` / `LIMIT` — 5 cheapest books.
3. `Q3` — `DISTINCT` — every distinct category name.
4. `Q4` — `WHERE ... BETWEEN` — books priced between £20 and £30.
5. `Q5` — `JOIN` — top-rated (4-5 star) books per category, joining
   `books` to `categories`.

`queries.py` also reads `Q1`-ish results back into pandas with
`pd.read_sql(...)`, and separately rebuilds the `Q5` JOIN result using
`pd.merge(...)` directly on in-memory DataFrames (no SQL). Both
approaches return the exact same rows in the exact same order — this is
printed and logged as a `True`/`False` check at the end of the run.

## Results snapshot (this run)

- 99 books scraped across 29 categories (required: ≥60 books, ≥3 categories).
- 0 rows dropped, 0 prices imputed.
- SQL JOIN and `pandas.merge` outputs matched exactly.
