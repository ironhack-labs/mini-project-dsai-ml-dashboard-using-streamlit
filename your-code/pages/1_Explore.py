import streamlit as st

from sakila import query

st.set_page_config(page_title="Explore", page_icon="📊", layout="wide")
st.title("📊 Explore the rentals")

# TODO 4: a line chart of the daily rentals of each store in 2005.
#   - rental has rental_date; inventory links each rental (inventory_id) to a store (store_id).
#   - In SQLite, DATE(rental_date) gives the day and STRFTIME('%Y', rental_date) the year.
#   - st.line_chart draws one line per column: pivot the result so that each store is a column.

# TODO 5: a bar chart of the total revenue of each store (payment -> rental -> inventory).

# TODO 6: the top 5 most rented films of each store in 2005, one st.dataframe per store, side by side.
