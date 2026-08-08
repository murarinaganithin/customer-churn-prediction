import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re
import urllib.parse
import os

# 1. Scraping

# Categories we will scrape to get >= 60 books across >= 3 categories
CATEGORY_URLS = [
    "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "http://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
    "http://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "http://books.toscrape.com/catalogue/category/books/classics_6/index.html"
]

def scrape_books():
    books_data = []
    
    for cat_url in CATEGORY_URLS:
        current_url = cat_url
        while current_url:
            print(f"Scraping {current_url}")
            response = requests.get(current_url)
            if response.status_code != 200:
                print(f"Failed to fetch {current_url}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            category_name = soup.find('h1').text.strip()
            
            for article in soup.find_all('article', class_='product_pod'):
                # Title
                title = article.h3.a.get('title')
                
                # Price
                price_text = article.find('p', class_='price_color').text.strip()
                
                # Rating
                p_star = article.find('p', class_='star-rating')
                classes = p_star.get('class', [])
                rating_text = classes[1] if len(classes) > 1 else 'None'
                
                # Availability
                availability_text = article.find('p', class_='instock availability').text.strip()
                
                books_data.append({
                    'title': title,
                    'price': price_text,
                    'star_rating': rating_text,
                    'availability': availability_text,
                    'category': category_name
                })
                
            # Pagination
            next_btn = soup.find('li', class_='next')
            if next_btn:
                next_url_relative = next_btn.a.get('href')
                current_url = urllib.parse.urljoin(current_url, next_url_relative)
            else:
                current_url = None
                
    return pd.DataFrame(books_data)

# 2. Data Cleaning
def clean_data(df):
    df = df.copy()
    
    # price_gbp
    df['price_gbp'] = df['price'].str.extract(r'(\d+\.\d+)').astype(float)
    
    # rating
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    df['rating'] = df['star_rating'].map(rating_map).astype('Int64')
    
    # in_stock
    df['in_stock'] = df['availability'].str.lower().str.contains('in stock')
    
    # Data Cleaning Decisions (handling parsing failures):
    # - Fill missing ratings with the median rating
    # - Drop rows with missing price or in_stock since they are critical numeric/boolean fields that can't be easily imputed
    median_rating = df['rating'].median()
    df['rating'] = df['rating'].fillna(median_rating).astype(int)
    df = df.dropna(subset=['price_gbp', 'in_stock'])
    
    # price_inr (Fixed project rate: 1 GBP = 105.50 INR)
    df['price_inr'] = df['price_gbp'] * 105.50
    
    return df[['title', 'price_gbp', 'price_inr', 'rating', 'in_stock', 'category']]

# 3. Database Loading
def setup_database(df, db_path='books.db'):
    # Ensure db path exists or create in current directory
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS categories")
    
    # Create Categories table
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT UNIQUE
    )
    """)
    
    # Create Books table
    cursor.execute("""
    CREATE TABLE books (
        book_id INTEGER PRIMARY KEY,
        title TEXT,
        price_gbp REAL,
        price_inr REAL,
        rating INTEGER,
        in_stock INTEGER,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    """)
    
    # Insert categories
    categories = df[['category']].drop_duplicates()
    categories.to_sql('categories_temp', conn, if_exists='replace', index=False)
    cursor.execute("""
    INSERT INTO categories (category_name)
    SELECT category FROM categories_temp
    """)
    cursor.execute("DROP TABLE categories_temp")
    
    # Insert books
    df_db = pd.merge(df, pd.read_sql("SELECT category_id, category_name FROM categories", conn), 
                     left_on='category', right_on='category_name')
    
    df_db = df_db[['title', 'price_gbp', 'price_inr', 'rating', 'in_stock', 'category_id']]
    df_db['in_stock'] = df_db['in_stock'].astype(int) # sqlite doesn't have native boolean
    
    df_db.to_sql('books', conn, if_exists='append', index=False)
    
    conn.commit()
    return conn

# 4 & 5. SQL Queries & Pandas Verification
def run_queries(conn):
    queries = {
        "1. SELECT/WHERE": "SELECT title, price_gbp FROM books WHERE rating >= 4 LIMIT 5",
        "2. ORDER BY": "SELECT title, price_gbp FROM books ORDER BY price_gbp DESC LIMIT 5",
        "3. LIMIT": "SELECT title FROM books LIMIT 3",
        "4. DISTINCT": "SELECT DISTINCT rating FROM books ORDER BY rating",
        "5. IN/BETWEEN": "SELECT title, rating FROM books WHERE rating IN (1, 5) LIMIT 5",
        "6. JOIN": """
            SELECT c.category_name, b.title, b.rating
            FROM books b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.rating = 5
            ORDER BY c.category_name, b.title
            LIMIT 10
        """
    }
    
    print("\n--- SQL Query Results ---")
    for name, q in queries.items():
        print(f"\n{name}:\n{q}")
        df_res = pd.read_sql(q, conn)
        print(df_res)
        
    return queries

def verify_pandas_join(conn, df_clean):
    print("\n--- Pandas Merge vs SQL Join Verification ---")
    q_join = """
        SELECT c.category_name, b.title, b.rating
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.rating = 5
        ORDER BY c.category_name, b.title
        LIMIT 10
    """
    sql_join_res = pd.read_sql(q_join, conn)
    
    # using pd.merge in-memory
    df_books = pd.read_sql("SELECT * FROM books", conn)
    df_cats = pd.read_sql("SELECT * FROM categories", conn)
    
    merged = pd.merge(df_books, df_cats, on='category_id')
    filtered = merged[merged['rating'] == 5]
    selected = filtered[['category_name', 'title', 'rating']]
    sorted_pd = selected.sort_values(by=['category_name', 'title']).head(10).reset_index(drop=True)
    
    print("SQL Join Result:")
    print(sql_join_res)
    print("\nPandas Merge Result:")
    print(sorted_pd)
    
    print("\nMatch?", sql_join_res.equals(sorted_pd))
    assert sql_join_res.equals(sorted_pd), "Pandas merge result does not match SQL join result!"

if __name__ == "__main__":
    print("Starting pipeline...")
    df_raw = scrape_books()
    print(f"\nScraped {len(df_raw)} books.")
    
    df_clean = clean_data(df_raw)
    print(f"Cleaned data: {len(df_clean)} rows.")
    
    db_path = os.path.join(os.path.dirname(__file__), 'books.db')
    conn = setup_database(df_clean, db_path)
    print(f"Database populated successfully at {db_path}.")
    
    run_queries(conn)
    verify_pandas_join(conn, df_clean)
    
    conn.close()
    print("\nPipeline completed successfully.")
