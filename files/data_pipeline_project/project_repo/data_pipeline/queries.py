"""
Step 5 and 6: Run SQL queries against books.db, then reproduce the join
query with pandas instead of SQL, to show both approaches agree.

The 5 queries below collectively use every clause the assignment asks for:
  Q1  SELECT / WHERE
  Q2  ORDER BY / LIMIT
  Q3  DISTINCT
  Q4  WHERE ... BETWEEN
  Q5  JOIN (books + categories) -- top rated books per category
"""

import sqlite3
import pandas as pd

DB_PATH = "books.db"
LOG_PATH = "query_outputs.txt"

QUERIES = {
    "Q1_in_stock_books (SELECT/WHERE)": """
        SELECT title, price_gbp, in_stock
        FROM books
        WHERE in_stock = 1
        LIMIT 5;
    """,
    "Q2_cheapest_books (ORDER BY/LIMIT)": """
        SELECT title, price_gbp
        FROM books
        ORDER BY price_gbp ASC
        LIMIT 5;
    """,
    "Q3_distinct_categories (DISTINCT)": """
        SELECT DISTINCT category_name
        FROM categories
        ORDER BY category_name;
    """,
    "Q4_midrange_price_books (WHERE BETWEEN)": """
        SELECT title, price_gbp
        FROM books
        WHERE price_gbp BETWEEN 20 AND 30
        ORDER BY price_gbp;
    """,
    "Q5_top_rated_books_per_category (JOIN)": """
        SELECT c.category_name, b.title, b.rating, b.price_inr
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.rating >= 4
        ORDER BY c.category_name, b.rating DESC
        LIMIT 10;
    """,
}


def run_sql_queries(conn):
    """Run every query above, print + log results, and return the join
    query's dataframe separately so we can compare it to pandas.merge."""
    lines = []
    join_query_df = None

    for name, sql in QUERIES.items():
        df = pd.read_sql(sql, conn)
        lines.append(f"--- {name} ---")
        lines.append(sql.strip())
        lines.append(df.to_string(index=False))
        lines.append("")
        print(f"--- {name} ---")
        print(df.to_string(index=False))
        print()

        if name.startswith("Q5"):
            join_query_df = df

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return join_query_df


def reproduce_join_with_pandas(conn):
    """Same result as Q5, but built with pandas.merge on in-memory
    DataFrames instead of a SQL JOIN, to show the two approaches match."""
    books_df = pd.read_sql("SELECT * FROM books", conn)
    categories_df = pd.read_sql("SELECT * FROM categories", conn)

    merged = pd.merge(books_df, categories_df, on="category_id", how="inner")
    merged = merged[merged["rating"] >= 4]
    merged = merged.sort_values(["category_name", "rating"], ascending=[True, False])
    merged = merged[["category_name", "title", "rating", "price_inr"]].head(10)
    return merged.reset_index(drop=True)


def main():
    conn = sqlite3.connect(DB_PATH)

    sql_join_result = run_sql_queries(conn)

    pandas_join_result = reproduce_join_with_pandas(conn)
    print("--- Same JOIN, built with pandas.merge (no SQL) ---")
    print(pandas_join_result.to_string(index=False))

    # sanity check: both approaches should agree on the same rows
    sql_titles = list(sql_join_result["title"])
    pandas_titles = list(pandas_join_result["title"])
    match = sql_titles == pandas_titles
    print(f"\nSQL JOIN and pandas.merge return the same book order/titles: {match}")

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n--- Same JOIN, built with pandas.merge (no SQL) ---\n")
        f.write(pandas_join_result.to_string(index=False))
        f.write(f"\n\nSQL JOIN and pandas.merge return the same book order/titles: {match}\n")

    conn.close()


if __name__ == "__main__":
    main()
