import pandas as pd 
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
import pymysql

def get_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='bootcamp2025',
        database='sakila'
    )

def daily_rentals_by_store():
    # daily rentals by each store in 2005
    conn = get_connection()
    query = """
    SELECT DATE(rental_date) AS "Rental Date", inv.store_id AS "Store ID", COUNT(*) AS "Rental Count"
    FROM rental AS re
    JOIN inventory AS inv ON re.inventory_id = inv.inventory_id
    JOIN store AS st ON inv.store_id = st.store_id
	WHERE YEAR(rental_date) = 2005
    GROUP BY DATE(rental_date), inv.store_id;
    """
    data = pd.read_sql(query, conn) # <-- here you get the DataFrame
    conn.close()
    return data # <-- returns a pandas DataFrame 


def total_revenue_by_store():
    conn = get_connection()
    query = """
    SELECT st.store_id AS "Store ID", SUM(py.amount) AS "Total Revenue Per Store"
	FROM payment AS py
    JOIN rental AS re ON py.rental_id = re.rental_id
    JOIN inventory AS inv ON re.inventory_id = inv.inventory_id
    JOIN store AS st ON inv.store_id = st.store_id
    GROUP BY st.store_id;
"""
    data = pd.read_sql(query, conn)
    conn.close()
    return data 



def top_five_by_store():
    conn = get_connection()
    query = """
    SELECT st.store_id AS "Store ID", film.title AS "Title", COUNT(inv.film_id) as "Rental Count"
	FROM rental AS re 
    JOIN inventory AS inv ON re.inventory_id = inv.inventory_id
    JOIN film ON inv.film_id = film.film_id
    JOIN store AS st ON inv.store_id = st.store_id
    WHERE YEAR(re.rental_date) = 2005
    GROUP BY st.store_id, film.title
    ORDER BY COUNT(inv.film_id) DESC;
    """
    data = pd.read_sql(query, conn) # <-- here you get the DataFrame
    conn.close()

    top_5 = data.groupby("Store ID").head(5)
    return top_5

def get_films_for_search():
    conn = get_connection()
    query = """
    SELECT title, description, rating, release_year
    FROM film;
    """
    data = pd.read_sql(query, conn)
    conn.close()
    return data
    