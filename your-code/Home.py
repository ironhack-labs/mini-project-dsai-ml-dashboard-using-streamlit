"""The home page. Run the whole app from the your-code folder:

    streamlit run Home.py
"""

import streamlit as st

from sakila import query       # query("SELECT ...") returns a DataFrame, cached

st.set_page_config(page_title="Sakila DVD Rentals", page_icon="🎬", layout="wide")

st.title("🎬 Sakila DVD Rental Dashboard")
st.image(
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
    width=700
)

# TODO 2: one sentence for the store managers: what this dashboard is for.
st.write(
    "This dashboard helps store managers monitor inventory, "
    "customers, rental activity, and revenue."
)

st.divider()

# TODO 3: four st.metric numbers in four st.columns: the number of films, customers and rentals,
#         and the total revenue (the sum of payment.amount). One SQL query can return all four.

# metrics from the Sakila database
films = query("SELECT COUNT(*) AS total FROM film")
customers = query("SELECT COUNT(*) AS total FROM customer")
rentals = query("SELECT COUNT(*) AS total FROM rental")
revenue = query("SELECT SUM(amount) AS total FROM payment")

#extract values
total_films = int(films["total"].iloc[0])
total_customers = int(customers["total"].iloc[0])
total_rentals = int(rentals["total"].iloc[0])
total_revenue = float(revenue["total"].iloc[0] or 0)


# Four metrics side by side
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎞️ Total Films", f"{total_films:,}")

with col2:
    st.metric("👥 Total Customers", f"{total_customers:,}")

with col3:
    st.metric("📀 Total Rentals", f"{total_rentals:,}")

with col4:
    st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
