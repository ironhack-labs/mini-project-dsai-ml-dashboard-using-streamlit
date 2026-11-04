"""Offline validation of the Sakila SQL pipeline (no Streamlit/model dependency)."""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "sakila.db"

def read(sql):
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(sql, con)

def main():
    kpi = read("""
        SELECT (SELECT COUNT(*) FROM film) films,
               (SELECT COUNT(*) FROM customer) customers,
               (SELECT COUNT(*) FROM rental) rentals,
               (SELECT ROUND(SUM(amount), 2) FROM payment) revenue
    """).iloc[0]
    assert tuple(kpi[["films", "customers", "rentals"]]) == (1000, 599, 16044)
    assert round(float(kpi["revenue"]), 2) == 67416.51
    daily = read("""
        SELECT DATE(r.rental_date) day, i.store_id, COUNT(*) rentals
        FROM rental r JOIN inventory i USING(inventory_id)
        WHERE STRFTIME('%Y', r.rental_date) = '2005'
        GROUP BY DATE(r.rental_date), i.store_id ORDER BY day
    """)
    assert daily["day"].nunique() == 40
    assert daily["day"].min() == "2005-05-24"
    assert daily["day"].max() == "2005-08-23"
    revenue = read("""
        SELECT i.store_id, ROUND(SUM(p.amount), 2) revenue
        FROM payment p JOIN rental r USING(rental_id)
        JOIN inventory i USING(inventory_id)
        GROUP BY i.store_id ORDER BY i.store_id
    """)
    assert revenue["revenue"].round(2).tolist() == [33679.79, 33726.77]
    leaders = read("""
        SELECT i.store_id, f.title, COUNT(*) rentals
        FROM rental r JOIN inventory i USING(inventory_id)
        JOIN film f USING(film_id)
        WHERE STRFTIME('%Y', r.rental_date) = '2005'
        GROUP BY i.store_id, f.film_id, f.title
        ORDER BY i.store_id, rentals DESC, f.title
    """)
    expected = {1: ("LOVE SUICIDES", 20), 2: ("IDOLS SNATCHERS", 20)}
    for store, (title, count) in expected.items():
        row = leaders[leaders.store_id == store].iloc[0]
        assert (row.title, int(row.rentals)) == (title, count)
    print("PASS — database KPI, daily rentals, revenue and leading-film checkpoints")
    print(f"KPI: {int(kpi.films):,} films | {int(kpi.customers):,} customers | "
          f"{int(kpi.rentals):,} rentals | ${kpi.revenue:,.2f}")
    print(revenue.to_string(index=False))
    print(f"2005 rental days: {daily.day.nunique()} ({daily.day.min()} to {daily.day.max()})")
    print("Store leaders:", expected)

if __name__ == "__main__":
    main()
