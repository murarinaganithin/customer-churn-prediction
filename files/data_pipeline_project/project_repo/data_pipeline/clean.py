"""
Step 2 and 3: Clean the scraped data and add the INR price column.

What we do to each row:
  - price:        "£51.77" -> price_gbp = 51.77 (float)
  - star_rating:  "Three"  -> rating = 3 (int, 1-5)
  - availability: "In stock (22 available)" -> in_stock = True (bool)
  - price_inr = price_gbp * 105.50   (fixed project rate, 1 GBP = 105.50 INR)

If a row's price or rating cannot be parsed (bad/unexpected text), we do
NOT crash the whole pipeline. Instead:
  - we try to fix it with median imputation for the numeric price, since
    price is the field most queries depend on and a missing price would
    break the currency conversion step too,
  - but if the star rating text is not one of One..Five, we drop the row,
    since a guessed rating would be misleading in a "top rated books"
    style query. This is stated here as the design decision the
    assignment asks us to justify.
"""

import csv
import os
import statistics

GBP_TO_INR = 105.50  # fixed, project-defined baseline rate (see README)

WORD_TO_NUM = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

INPUT_PATH = os.path.join("data", "raw_scraped_books.csv")
OUTPUT_PATH = os.path.join("data", "cleaned_books.csv")


def parse_price(price_text):
    """'£51.77' -> 51.77. Returns None if it can't be parsed."""
    try:
        cleaned = price_text.replace("£", "").replace(",", "").strip()
        return round(float(cleaned), 2)
    except (ValueError, AttributeError):
        return None


def parse_rating(star_text):
    """'Three' -> 3. Returns None if it's not a recognised word."""
    return WORD_TO_NUM.get(star_text.strip()) if star_text else None


def parse_in_stock(availability_text):
    """'In stock (22 available)' -> True, 'Out of stock' -> False."""
    if not availability_text:
        return False
    return "in stock" in availability_text.lower()


def load_raw_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean_rows(raw_rows):
    parsed_rows = []
    dropped = 0

    for row in raw_rows:
        price_gbp = parse_price(row["price"])
        rating = parse_rating(row["star_rating"])
        in_stock = parse_in_stock(row["availability"])

        if rating is None:
            # can't safely guess a star rating -> drop the row
            dropped += 1
            continue

        parsed_rows.append(
            {
                "title": row["title"].strip(),
                "category": row["category"].strip(),
                "price_gbp": price_gbp,  # may be None here, fixed below
                "rating": rating,
                "in_stock": in_stock,
            }
        )

    # median-impute any missing prices, now that we know the good values
    known_prices = [r["price_gbp"] for r in parsed_rows if r["price_gbp"] is not None]
    if known_prices:
        median_price = round(statistics.median(known_prices), 2)
    else:
        median_price = 0.0

    imputed = 0
    for r in parsed_rows:
        if r["price_gbp"] is None:
            r["price_gbp"] = median_price
            imputed += 1
        r["price_inr"] = round(r["price_gbp"] * GBP_TO_INR, 2)

    print(f"Cleaned {len(parsed_rows)} rows (dropped {dropped}, price-imputed {imputed})")
    return parsed_rows


def save_clean_rows(rows, path):
    fieldnames = ["title", "category", "price_gbp", "price_inr", "rating", "in_stock"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    raw_rows = load_raw_rows(INPUT_PATH)
    clean = clean_rows(raw_rows)
    save_clean_rows(clean, OUTPUT_PATH)
    print(f"Saved cleaned data to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
