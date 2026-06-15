"""
backend.py — data loading, processing and plotting logic.

I kept the streamlit frontend in the app.py for a clean separation according to the workflow given in 
the Streamlit lesson: 
    -> backend.py for python logic
    -> app.py for the UI

After some problems with the running MySQL-Server I had a check-in with AI and decided to follow the tip of
having the data read from a portable SQLite file called data/sakila.db (built by build_db.py) so I don't need 
a running MySQL server at all.
"""
import sqlite3

import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = "data/sakila.db"


# ------------------------------------------------------------------ #
# Data loading
# ------------------------------------------------------------------ #
@st.cache_data  # update since st.cache deprecated
def run_query(query: str) -> pd.DataFrame:
    """Run a read-only SQL query against the SQLite database and cache the result."""
    con = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql(query, con)
    finally:
        con.close()


def get_daily_rentals_2005() -> pd.DataFrame:
    """Daily rental counts per store in 2005 (one column per store)."""
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
    pivot = df.pivot(index="Day", columns="store_id", values="Rentals").fillna(0)
    pivot.index = pd.to_datetime(pivot.index)
    pivot.columns = [f"Store {c}" for c in pivot.columns]
    return pivot


def get_benefit_by_store() -> pd.DataFrame:
    """Total benefit (sum of payments) per store."""
    return run_query(
        """
        SELECT s.store_id, ROUND(SUM(p.amount), 2) AS Benefit
        FROM payment p
        JOIN staff s ON p.staff_id = s.staff_id
        GROUP BY s.store_id
        """
    )


def get_top5_movies_by_store() -> pd.DataFrame:
    """Rental counts per (store, film) in 2005 — frontend slices the top 5 per store."""
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
# Plots ((matplotlib figures -> super ugly, changed to .plotly), displayed with st.plotly)
# ------------------------------------------------------------------ #
def plot_daily_rentals(pivot):
    fig = px.line(
        pivot,                                  # wide-form: Index = x-axis, every column = 1 line // still not sure about this
        labels={"value": "Rentals", "variable": "Store", "Day": "Date"},
        title="Daily Rentals by Store for 2005",
        template="plotly_white",                # clean look
    )
    fig.update_layout(
        title_x=0.5,                            # Titel zentrieren
        font=dict(family="Avenir, 'Avenir Next', sans-serif"),
        hovermode="x unified",                  # tooltip while hover, fancy stuff
        legend_title_text="",
    )
    return fig


def plot_benefit_by_store(df):
    df = df.copy()
    df["Store"] = "Store " + df["store_id"].astype(str)
    fig = px.bar(
        df,
        x="Store",
        y="Benefit",
        color="Store",
        text="Benefit",
        title="Total Benefit by Store",
        template="plotly_white",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,        # Label darf über die Achse hinaus -> nicht mehr abgeschnitten
    )
    fig.update_yaxes(range=[0, df["Benefit"].max() * 1.15])  # extra Luft über den Balken
    fig.update_layout(
        title_x=0.5,
        font=dict(family="Avenir, 'Avenir Next', sans-serif"),
        showlegend=False,
        height=450,              # größere Figur ("figsize")
        bargap=0.5,              # Balkenbreite/Abstand: höher = schmalere Balken
    )
    return fig


# ------------------------------------------------------------------ #
# Prediction: semantic movie search
# ------------------------------------------------------------------ #
@st.cache_resource  # cache the model + embeddings once for the whole session
def load_film_embeddings():
    """Load films and encode their descriptions with a Sentence Transformer."""
    films = run_query("SELECT film_id, title, description, rating FROM film")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(films["description"].tolist(), show_progress_bar=False)
    return model, films, embeddings


def find_similar_movies(description, model, films, embeddings, top_n=3) -> pd.DataFrame:
    """Return the top_n films whose description is most similar to the input text."""
    query_embedding = model.encode([description])
    sims = cosine_similarity(query_embedding, embeddings)[0]
    top_idx = sims.argsort()[::-1][:top_n]
    results = films.iloc[top_idx][["title", "rating"]].copy()
    results["similarity"] = sims[top_idx].round(3)
    return results.reset_index(drop=True)
