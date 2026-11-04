"""Home page for the Sakila DVD-rental management dashboard."""
import streamlit as st
from sakila import query

st.set_page_config(page_title="Sakila DVD Rentals", page_icon="🎬", layout="wide")
st.title("🎬 Sakila DVD Rentals")
st.image(
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1600&q=80",
    caption="A data-driven view of the two Sakila rental stores",
    use_container_width=True,
)
st.write(
    "Monitor catalogue size, customer activity, rental trends and store revenue, "
    "then discover films that match a customer's description."
)

metrics = query("""
    SELECT
        (SELECT COUNT(*) FROM film) AS films,
        (SELECT COUNT(*) FROM customer) AS customers,
        (SELECT COUNT(*) FROM rental) AS rentals,
        (SELECT COALESCE(SUM(amount), 0) FROM payment) AS revenue
""").iloc[0]

cols = st.columns(4)
cols[0].metric("Films", f"{int(metrics['films']):,}")
cols[1].metric("Customers", f"{int(metrics['customers']):,}")
cols[2].metric("Rentals", f"{int(metrics['rentals']):,}")
cols[3].metric("Revenue", f"${metrics['revenue']:,.2f}")
