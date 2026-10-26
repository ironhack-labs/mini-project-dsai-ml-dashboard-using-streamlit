"""The home page. Run the whole app from the your-code folder:

    streamlit run Home.py
"""

import streamlit as st

from sakila import query       # query("SELECT ...") returns a DataFrame, cached

st.set_page_config(page_title="Sakila DVD Rentals", page_icon="🎬", layout="wide")

# TODO 1: a title (st.title) and an image of your choice (st.image, with a URL or a file).

# TODO 2: one sentence for the store managers: what this dashboard is for.

# TODO 3: four st.metric numbers in four st.columns: the number of films, customers and rentals,
#         and the total revenue (the sum of payment.amount). One SQL query can return all four.
