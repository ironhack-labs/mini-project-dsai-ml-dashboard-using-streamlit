import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


st.title("Movie Recommendations")

conn = sqlite3.connect("sqlite-sakila.db")

query = """
SELECT title, description, rating
FROM film
WHERE description IS NOT NULL;
"""

df = pd.read_sql(query, conn)
conn.close()

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_embeddings = model.encode(df["description"].tolist())

user_input = st.text_area("Describe a movie:")
if st.button("Get Your Prediction"):
    if user_input.strip():
        query_embedding = model.encode([user_input])
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        top_n = 3
        top_movies = np.argsort(similarities)[::-1][:top_n] #np.argsort() sorts by the values but returns original index positions only
        recommendations = df.iloc[top_movies][["title", "rating"]]
        st.dataframe(recommendations.reset_index(drop=True), hide_index=True)