"""Rental and revenue exploration for the Sakila stores."""
import streamlit as st
from sakila import query

st.set_page_config(page_title="Explore", page_icon="📊", layout="wide")
st.title("📊 Explore the rentals")
st.caption("All figures are calculated from the supplied Sakila SQLite database.")

# Daily rentals: DATE() extracts the calendar day from SQLite's text timestamp.
daily = query("""
    SELECT DATE(r.rental_date) AS rental_day,
           i.store_id,
           COUNT(*) AS rentals
    FROM rental AS r
    JOIN inventory AS i ON i.inventory_id = r.inventory_id
    WHERE STRFTIME('%Y', r.rental_date) = '2005'
    GROUP BY DATE(r.rental_date), i.store_id
    ORDER BY rental_day, i.store_id
""")
if daily.empty:
    st.info("No rental records were found for 2005.")
else:
    # A wide/pivoted table makes each store a separate line in st.line_chart.
    daily_wide = (daily.pivot(index="rental_day", columns="store_id", values="rentals")
                  .fillna(0).rename(columns=lambda store: f"Store {store}"))
    daily_wide.index = __import__("pandas").to_datetime(daily_wide.index)
    st.subheader("Daily rentals by store — 2005")
    st.line_chart(daily_wide)
    st.caption(
        f"Data covers {len(daily_wide)} rental days from "
        f"{daily_wide.index.min():%d %b %Y} to {daily_wide.index.max():%d %b %Y}. "
        "The sample database contains gaps; dates without recorded rentals are not evidence "
        "of zero demand and are not fabricated."
    )

# Revenue follows the relational path payment -> rental -> inventory -> store.
revenue = query("""
    SELECT i.store_id, ROUND(SUM(p.amount), 2) AS revenue
    FROM payment AS p
    JOIN rental AS r ON r.rental_id = p.rental_id
    JOIN inventory AS i ON i.inventory_id = r.inventory_id
    GROUP BY i.store_id
    ORDER BY i.store_id
""")
st.subheader("Total revenue by store")
if not revenue.empty:
    revenue["store"] = revenue["store_id"].map(lambda x: f"Store {x}")
    st.bar_chart(revenue.set_index("store")[["revenue"]])
    st.dataframe(revenue[["store", "revenue"]].rename(columns={"revenue": "Revenue ($)"}),
                 hide_index=True, use_container_width=True)

# Rank within each store, restricted to rentals made during 2005.
top = query("""
    WITH film_rentals AS (
        SELECT i.store_id, f.title, COUNT(*) AS rentals
        FROM rental AS r
        JOIN inventory AS i ON i.inventory_id = r.inventory_id
        JOIN film AS f ON f.film_id = i.film_id
        WHERE STRFTIME('%Y', r.rental_date) = '2005'
        GROUP BY i.store_id, f.film_id, f.title
    ),
    ranked AS (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY store_id ORDER BY rentals DESC, title ASC
        ) AS position
        FROM film_rentals
    )
    SELECT store_id, title, rentals
    FROM ranked WHERE position <= 5
    ORDER BY store_id, position
""")
st.subheader("Top 5 most-rented films in 2005")
left, right = st.columns(2)
for store_id, column in [(1, left), (2, right)]:
    with column:
        st.markdown(f"**Store {store_id}**")
        store_top = top[top["store_id"] == store_id][["title", "rentals"]]
        st.dataframe(store_top, hide_index=True, use_container_width=True)
