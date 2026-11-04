"""Shared SQLite access for all Streamlit pages."""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DATABASE = Path(__file__).resolve().parents[1] / "data" / "sakila.db"

@st.cache_data(show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    """Execute a read-only analytical query and cache its DataFrame result."""
    if not DATABASE.exists():
        raise FileNotFoundError(f"Sakila database not found: {DATABASE}")
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as connection:
        return pd.read_sql_query(sql, connection)
