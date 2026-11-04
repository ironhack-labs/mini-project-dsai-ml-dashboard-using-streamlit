import streamlit as st
import pandas as pd
from sakila import query

st.set_page_config(page_title="Explore", page_icon="📊", layout="wide")
st.title("📊 Explore the rentals")
st.write(
    "Explore rental trends, store revenue, and the most popular "
    "films across Sakila's two DVD rental stores."
)
# TODO 4: a line chart of the daily rentals of each store in 2005.
#   - rental has rental_date; inventory links each rental (inventory_id) to a store (store_id).
#   - In SQLite, DATE(rental_date) gives the day and STRFTIME('%Y', rental_date) the year.
#   - st.line_chart draws one line per column: pivot the result so that each store is a column.
st.header("📈 Daily Rentals by Store (2005)")
daily_rentals = query("""
    SELECT
        DATE(r.rental_date) AS rental_day,
        i.store_id,
        COUNT(*) AS total_rentals
    FROM rental r
    JOIN inventory i
        ON r.inventory_id = i.inventory_id
    WHERE r.rental_date >= '2005-01-01'
      AND r.rental_date < '2006-01-01'
    GROUP BY DATE(r.rental_date), i.store_id
    ORDER BY rental_day, i.store_id
""")

# Pivot: one column per store
daily_pivot = daily_rentals.pivot(
    index="rental_day",
    columns="store_id",
    values="total_rentals"
)

daily_pivot = daily_pivot.rename(
    columns={1: "Store 1", 2: "Store 2"}
)

daily_pivot.index = pd.to_datetime(daily_pivot.index)

st.line_chart(daily_pivot)

st.caption(
    "The Sakila sample database contains rental records on only "
    "40 days between 24 May and 23 August 2005. "
    "Missing dates reflect gaps in the sample data."
)

# TODO 5: a bar chart of the total revenue of each store (payment -> rental -> inventory).
st.header("💰 Total Revenue by Store")

revenue = query("""
    SELECT
        i.store_id,
        ROUND(SUM(p.amount), 2) AS total_revenue
    FROM payment p
    JOIN rental r
        ON p.rental_id = r.rental_id
    JOIN inventory i
        ON r.inventory_id = i.inventory_id
    GROUP BY i.store_id
    ORDER BY i.store_id
""")

revenue_chart = revenue.set_index("store_id")

st.bar_chart(revenue_chart)

st.dataframe(
    revenue,
    hide_index=True,
    use_container_width=True
)

# TODO 6: the top 5 most rented films of each store in 2005, one st.dataframe per store, side by side.
st.header("🎬 Top 5 Most Rented Films by Store (2005)")

top_films = query("""
    SELECT
        i.store_id,
        f.title AS film_title,
        COUNT(*) AS rental_count
    FROM rental r
    JOIN inventory i
        ON r.inventory_id = i.inventory_id
    JOIN film f
        ON i.film_id = f.film_id
    WHERE r.rental_date >= '2005-01-01'
      AND r.rental_date < '2006-01-01'
    GROUP BY i.store_id, f.film_id, f.title
    ORDER BY rental_count DESC, film_title ASC
""")

# Select top 5 for each store
top_5 = (
    top_films.groupby("store_id", group_keys=False)
    .head(5)
)

# Create two side-by-side columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏬 Store 1")
    st.dataframe(
        top_5[top_5["store_id"] == 1][
            ["film_title", "rental_count"]
        ],
        hide_index=True,
        use_container_width=True
    )

with col2:
    st.subheader("🏬 Store 2")
    st.dataframe(
        top_5[top_5["store_id"] == 2][
            ["film_title", "rental_count"]
        ],
        hide_index=True,
        use_container_width=True
    )

