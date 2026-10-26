import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from sakila import query

st.set_page_config(page_title="Find similar films", page_icon="🔎")
st.title("🔎 Find similar films")


@st.cache_resource
def load_model():
    """TODO 7: load and return the sentence embedding model all-MiniLM-L6-v2 (Week 7, Day 2)."""
    pass


@st.cache_resource
def film_vectors():
    """TODO 8: read the title, description and rating of every film, embed the descriptions
    (normalised), and return the DataFrame and the vectors."""
    pass


# TODO 9: a st.text_area for the customer's description and a st.button("Get your recommendations").
#         When it is clicked: warn if the text is empty; otherwise embed it, compute the cosine similarity
#         with every film (a dot product, since the vectors are normalised), and show the top 3 films
#         with their title, rating and similarity.
