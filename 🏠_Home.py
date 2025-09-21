
# app.py — Streamlit Sakila (multi-page)
import streamlit as st
import pandas as pd
from utils import run_query

st.set_page_config(page_title="Sakila ML Dashboard", page_icon="🎬", layout="wide")

col1, col2 = st.columns([1,2])
with col1:
    st.image("https://education-team-2020.s3-eu-west-1.amazonaws.com/data-analytics/database-sakila-schema.png", caption="Sakila (partial) ERD")
with col2:
    st.title("🎬 Sakila ML Dashboard")
    st.markdown(
        """
        Welcome! This multi-page app explores the classic MySQL Sakila movie rental database and adds a lightweight NLP similarity tool.

        Pages:
        - EDA – Daily rentals by store (2005), revenue by store, and top-rented films per store.
        - Prediction – Type a movie description to find the top-3 most similar films (with MPAA rating).
        """
    )

st.markdown("---")
st.subheader("Connection check")
try:
    _ = run_query("SELECT 1 AS ok")
    st.success("Connected to Sakila successfully ✅")
except Exception as e:
    st.error("Could not connect to the database. Check credentials and that MySQL is running.")
    with st.expander("Error details"):
        st.exception(e)