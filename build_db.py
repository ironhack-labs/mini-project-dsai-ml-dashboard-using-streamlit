"""
build_db.py — one-time ETL.

Pulls the tables we need from the bootcamp MySQL container (Sakila) and writes
them into a portable local SQLite file (data/sakila.db) so the Streamlit app
runs anywhere without a running MySQL server.

Run once:  python build_db.py
"""
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

MYSQL_URL = "mysql+pymysql://root:bootcamp123@127.0.0.1:3306/sakila"
SQLITE_PATH = "data/sakila.db"

# Only the tables the dashboard needs
TABLES = {
    "film": "SELECT film_id, title, description, rating, rental_rate FROM film",
    "inventory": "SELECT inventory_id, film_id, store_id FROM inventory",
    "rental": "SELECT rental_id, rental_date, inventory_id FROM rental",
    "payment": "SELECT payment_id, staff_id, amount, payment_date FROM payment",
    "staff": "SELECT staff_id, store_id FROM staff",
    "store": "SELECT store_id, manager_staff_id FROM store",
}


def main():
    engine = create_engine(MYSQL_URL)
    conn = sqlite3.connect(SQLITE_PATH)
    for name, query in TABLES.items():
        df = pd.read_sql(query, engine)
        # store datetimes as ISO strings -> SQLite-friendly and easy to filter
        for col in ("rental_date", "payment_date"):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).astype(str)
        df.to_sql(name, conn, if_exists="replace", index=False)
        print(f"  {name}: {len(df)} rows")
    conn.close()
    engine.dispose()
    print(f"Done -> {SQLITE_PATH}")


if __name__ == "__main__":
    main()
