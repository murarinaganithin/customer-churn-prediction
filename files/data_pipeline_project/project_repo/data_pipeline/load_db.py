"""
Step 4 and 5: Build a normalized SQLite database and load the cleaned data.

Two tables, sharing a primary/foreign key relationship:
  categories(category_id PK, category_name UNIQUE)
  books(book_id PK, title, price_gbp, price_inr, rating, in_stock,
        category_id FK -> categories.category_id)

We put each category name in its own row exactly once, and every book
points at its category by id. This is the normalization the task asks
for: category names are not repeated as text on every single book row.
"""

import csv
import os
import sqlite3

CLEAN_CSV_PATH = os.path.join("data", "cleaned_books.csv")
DB_PATH = "books.db"

SCHEMA = """
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock INTEGER NOT NULL,
    category_id INTEGER REFERENCES categories(category_id)
);
"""


def load_clean_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_database(rows, db_path):
    # start fresh every run, so this script can be re-run safely
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    # 1) insert each distinct category once and remember its id
    category_ids = {}
    distinct_categories = sorted({row["category"] for row in rows})
    for name in distinct_categories:
        cur.execute(
            "INSERT INTO categories (category_name) VALUES (?)", (name,)
        )
        category_ids[name] = cur.lastrowid

    # 2) insert each book, pointing at its category's id
    for row in rows:
        cur.execute(
            """
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                1 if row["in_stock"] == "True" else 0,
                category_ids[row["category"]],
            ),
        )

    conn.commit()
    return conn


def main():
    rows = load_clean_rows(CLEAN_CSV_PATH)
    conn = build_database(rows, DB_PATH)
    n_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    n_categories = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    print(f"Loaded {n_books} books across {n_categories} categories into {DB_PATH}")
    conn.close()


if __name__ == "__main__":
    main()
