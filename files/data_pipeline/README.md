# Data Pipeline: Books Scraper & Database Loader

This module scrapes book data from `books.toscrape.com`, cleans the data, loads it into a normalized SQLite database, and executes SQL queries for verification.

## Installation & Setup

1. Install the required Python packages (we assume Python 3.8+ is installed):
```bash
pip install -r requirements.txt
```

2. Run the pipeline script:
```bash
python pipeline.py
```

## Process Overview

### Scraping
The script scrapes four specific categories from `books.toscrape.com` to ensure we collect at least 60 books across at least 3 categories.
- Mystery
- Historical Fiction
- Travel
- Classics

For each book, we extract: `title`, `price` (as listed), `star_rating` (as text), `availability` (as listed text), and `category`.

### Data Cleaning Decisions
- **Price (`price_gbp`)**: The currency symbol `£` is stripped, and the remaining value is cast to a `float`.
- **Rating (`rating`)**: The text values (e.g., 'One', 'Two') are converted to integers 1-5. Missing ratings (if any fail to parse) are imputed using the median rating of the dataset.
- **Availability (`in_stock`)**: The text is parsed to a boolean (`True` if it contains 'in stock', `False` otherwise).
- **INR Price (`price_inr`)**: Calculated using the project's fixed baseline conversion rate of `1 GBP = 105.50 INR`. This is a fixed project-defined constant with no date reference and requires no external API call.
- **Handling Parsing Failures**: If any critical fields (`price_gbp`, `in_stock`) fail to parse or are completely missing, those rows are dropped to avoid breaking the pipeline, as they are not reliably imputable. Ratings are median-imputed.

### Database Schema
We use a normalized SQLite schema with two tables sharing a primary/foreign key relationship:
- `categories`: Contains `category_id` (PK) and `category_name` (UNIQUE).
- `books`: Contains `book_id` (PK), `title`, `price_gbp`, `price_inr`, `rating`, `in_stock`, and `category_id` (FK to `categories`).

### Queries
The script executes 5 required SQL queries covering:
- `SELECT/WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `IN/BETWEEN`
- A `JOIN` between the two tables

The output of the join query is also verified against an equivalent `pd.merge()` operation in memory to ensure data integrity and equivalence.
