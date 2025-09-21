
# utils.py — shared helpers for Streamlit Sakila app
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# ---- DB CONFIG ----
DB_USER = os.getenv("SAKILA_USER", "root")
DB_PASS = os.getenv("SAKILA_PASS", "password")
DB_HOST = os.getenv("SAKILA_HOST", "localhost")
DB_PORT = int(os.getenv("SAKILA_PORT", "3306"))
DB_NAME = os.getenv("SAKILA_DB", "sakila")

CONN_STR = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@st.cache_resource(show_spinner=False)
def get_engine():
    from sqlalchemy import create_engine
    return create_engine(CONN_STR, pool_pre_ping=True)

@st.cache_data(show_spinner=False)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

# ---- NLP MODEL ----
@st.cache_resource(show_spinner=True)
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data(show_spinner=True)
def load_corpus():
    sql_films = "SELECT film_id, title, description, rating FROM film"
    df = run_query(sql_films)
    df["description"] = df["description"].fillna("").astype(str)
    return df

@st.cache_data(show_spinner=False)
def precompute_embeddings(texts: list[str]):
    model = load_model()
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    import numpy as np
    return np.asarray(embs)

def cosine_topk(query_vec, mat, k=3):
    sims = mat @ query_vec
    import numpy as np
    topk_idx = np.argpartition(-sims, k)[:k]
    topk_idx = topk_idx[np.argsort(-sims[topk_idx])]
    return topk_idx.tolist()
