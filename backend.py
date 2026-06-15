"""
backend.py — all the data and logic for the dashboard.

The Streamlit UI lives in app.py; this file only holds the Python logic, the way
the Streamlit lesson suggests (backend = logic, app = UI).

The data is read from a small local SQLite file (data/sakila.db, created by
build_db.py). That means the app needs no running MySQL server to work.
"""
import sqlite3

import plotly.express as px
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Path to the local database file the app reads from.
DB_PATH = "data/sakila.db"


# ------------------------------------------------------------------ #
# Data loading (SQLite)
# ------------------------------------------------------------------ #
@st.cache_data  # remembers the result so the same query does not hit the DB again
def run_query(query: str) -> pd.DataFrame:
    """Open the SQLite database, run one SQL query, and return the rows as a DataFrame."""
    con = sqlite3.connect(DB_PATH)          # open a connection to the .db file
    try:
        return pd.read_sql(query, con)      # run the query, get the result as a table
    finally:
        con.close()                         # always close the connection, even on error


def get_daily_rentals_2005() -> pd.DataFrame:
    """How many rentals each store had per day in 2005."""
    # rental tells us WHEN something was rented; inventory tells us WHICH STORE the
    # rented copy belongs to. We join them, keep only 2005, and count per day + store.
    df = run_query(
        """
        SELECT date(r.rental_date) AS Day, i.store_id, COUNT(*) AS Rentals
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        WHERE strftime('%Y', r.rental_date) = '2005'
        GROUP BY day, i.store_id
        ORDER BY day
        """
    )
    # Reshape from long to wide: one row per day, one column per store (easier to plot).
    pivot = df.pivot(index="Day", columns="store_id", values="Rentals").fillna(0)
    pivot.index = pd.to_datetime(pivot.index)            # turn date strings into real dates
    pivot.columns = [f"Store {c}" for c in pivot.columns]  # rename 1/2 -> "Store 1"/"Store 2"
    return pivot


def get_benefit_by_store() -> pd.DataFrame:
    """Total money earned (sum of all payments) per store."""
    # payment holds the amounts; staff tells us which store a payment belongs to.
    # We join them and add up the amounts for each store.
    return run_query(
        """
        SELECT s.store_id, ROUND(SUM(p.amount), 2) AS Benefit
        FROM payment p
        JOIN staff s ON p.staff_id = s.staff_id
        GROUP BY s.store_id
        """
    )


def get_top5_movies_by_store() -> pd.DataFrame:
    """How often each film was rented per store in 2005."""
    # Chain of joins: rental -> inventory (gives store + film_id) -> film (gives the title).
    # We count the rentals per film per store; the UI later keeps only the top 5 per store.
    return run_query(
        """
        SELECT i.store_id, f.title AS Title, COUNT(*) AS "Times Rented"
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        WHERE strftime('%Y', r.rental_date) = '2005'
        GROUP BY i.store_id, f.title
        """
    )


# ------------------------------------------------------------------ #
# Plots (Plotly figures, shown with st.plotly_chart)
# ------------------------------------------------------------------ #
def plot_daily_rentals(pivot):
    # Line chart: one line per store over time.
    fig = px.line(
        pivot,
        labels={"value": "Rentals", "variable": "Store", "Day": "Date"},
        template="plotly_white",
    )
    fig.update_layout(
        title=dict(text="Daily Rentals by Store for 2005",
                   x=0.5, xanchor="center", xref="container"),
        font=dict(family="Avenir, 'Avenir Next', sans-serif"),
        hovermode="x unified",
        height=450,
        legend_title_text="",
    )
    return fig


def plot_benefit_by_store(df):
    # Bar chart: one bar per store with the total benefit on top.
    df = df.copy()
    df["Store"] = "Store " + df["store_id"].astype(str)
    fig = px.bar(
        df,
        x="Store",
        y="Benefit",
        color="Store",
        text="Benefit",
        template="plotly_white",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,        # let the value label show outside the plot (no cut-off)
    )
    fig.update_yaxes(range=[0, df["Benefit"].max() * 1.15])  # add headroom above the bars
    fig.update_layout(
        title=dict(text="Total Benefit by Store",
                   x=0.5, xanchor="center", xref="container"),
        font=dict(family="Avenir, 'Avenir Next', sans-serif"),
        showlegend=False,
        height=450,
        bargap=0.5,
    )
    return fig


# ------------------------------------------------------------------ #
# Prediction: find similar movies with embeddings
# ------------------------------------------------------------------ #
@st.cache_resource  # load the model and build the embeddings only once per session
def load_film_embeddings():
    """Load all films and turn every film description into a number vector (an embedding)."""
    films = run_query("SELECT film_id, title, description, rating FROM film")
    # This model maps a piece of text to a vector. Texts with a similar meaning get
    # similar vectors, even if they use different words.
    model = SentenceTransformer("all-MiniLM-L6-v2")
    # Encode every film description once. This is the slow part, so we cache it.
    embeddings = model.encode(films["description"].tolist(), show_progress_bar=False)
    return model, films, embeddings


def find_similar_movies(description, model, films, embeddings, top_n=3) -> pd.DataFrame:
    """Take the user's text and return the top_n films with the most similar description."""
    # Turn the user's input into a vector, in the same "meaning space" as the films.
    query_embedding = model.encode([description])
    # Cosine similarity = how close two vectors point in the same direction (1 = identical).
    sims = cosine_similarity(query_embedding, embeddings)[0]
    # argsort sorts low -> high, so we reverse ([::-1]) and take the first top_n indices.
    top_idx = sims.argsort()[::-1][:top_n]
    # Pick those films and attach their similarity score.
    results = films.iloc[top_idx][["title", "rating", "description"]].copy()
    results["similarity"] = sims[top_idx].round(3)
    results = results[["title", "rating", "similarity", "description"]]  # column order
    return results.reset_index(drop=True)
