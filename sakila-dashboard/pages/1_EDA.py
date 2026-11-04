import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("Exploratory Data Analysis")

st.write("Analyzing movie rentals")

st.subheader("Daily Rentals by Store")

conn = sqlite3.connect("sqlite-sakila.db")

query = """
SELECT
    DATE(r.rental_date) AS rental_day,
    i.store_id,
    COUNT(*) AS total_rentals
FROM rental AS r
JOIN inventory AS i
    ON r.inventory_id = i.inventory_id
WHERE strftime('%Y', r.rental_date) = '2005'
GROUP BY rental_day, i.store_id
ORDER BY rental_day;
"""
df = pd.read_sql(query, conn)
chart_df = df.pivot(index="rental_day",columns="store_id",values="total_rentals")
st.line_chart(chart_df)



st.subheader("Total Revenue by Store (2005)")

query_revenue = """
SELECT
    i.store_id,
    ROUND(SUM(p.amount), 2) AS total_revenue
FROM payment p
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON r.inventory_id = i.inventory_id
WHERE strftime('%Y', p.payment_date) = '2005'
GROUP BY i.store_id
ORDER BY i.store_id;
"""
df_revenue = pd.read_sql(query_revenue, conn)
df_revenue["store"] = "Store " + df_revenue["store_id"].astype(str)
fig = px.bar(
    df_revenue,
    x="store",
    y="total_revenue",
    text_auto=",.2f"
)
fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_title=None,
    yaxis_title="Revenue",
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)


st.subheader("Top 5 Most Rented Movies by Store (2005)")

st.subheader("Store 1 - Top 5 Movies")

query_store1 = """
SELECT
    f.title,
    COUNT(*) AS total_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE i.store_id = 1
    AND strftime('%Y', r.rental_date) = '2005'
GROUP BY f.film_id, f.title
ORDER BY total_rentals DESC, f.title
LIMIT 5;
"""

df_store1 = pd.read_sql(query_store1, conn)
df_store1.index = range(1, len(df_store1) + 1)
st.dataframe(df_store1)

st.subheader("Store 2 - Top 5 Movies")

query_store2 = """
SELECT
    f.title,
    COUNT(*) AS total_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE i.store_id = 2
    AND strftime('%Y', r.rental_date) = '2005'
GROUP BY f.film_id, f.title
ORDER BY total_rentals DESC, f.title
LIMIT 5;
"""

df_store2 = pd.read_sql(query_store2, conn)
df_store2.index = range(1, len(df_store2) + 1)
st.dataframe(df_store2)

conn.close()