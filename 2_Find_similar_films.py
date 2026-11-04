"""Semantic film search using cached SentenceTransformer embeddings."""
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from sakila import query

st.set_page_config(page_title="Find similar films", page_icon="🔎", layout="wide")
st.title("🔎 Find similar films")
st.write(
    "Describe the kind of story a customer wants. The app compares the meaning of that "
    "description with all film synopses and returns the closest matches."
)

@st.cache_resource(show_spinner="Loading the sentence-embedding model…")
def load_model():
    """Load the compact MiniLM model once per Streamlit server process."""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource(show_spinner="Preparing film descriptions…")
def film_vectors():
    """Fetch and embed all film descriptions once; vectors are L2-normalised."""
    films = query("""
        SELECT film_id, title, description, rating
        FROM film
        ORDER BY film_id
    """)
    model = load_model()
    vectors = model.encode(
        films["description"].fillna("").tolist(),
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return films, vectors

request = st.text_area(
    "What kind of film is the customer looking for?",
    placeholder="A thoughtful drama about a monk who discovers a shark in Australia",
    height=110,
)
if st.button("Get your recommendations", type="primary"):
    if not request.strip():
        st.warning("Please enter a film description before requesting recommendations.")
    else:
        try:
            model = load_model()
            films, vectors = film_vectors()
            query_vector = model.encode(
                [request.strip()],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )[0]
            # Normalised embeddings make the dot product equal cosine similarity.
            similarities = vectors @ query_vector
            best = np.argsort(similarities)[::-1][:3]
            st.subheader("Your three closest matches")
            for rank, index in enumerate(best, start=1):
                film = films.iloc[int(index)]
                score = float(similarities[index])
                st.markdown(
                    f"**{rank}. {film['title']}** · Rating: {film['rating']}  "
                    f"· Similarity: `{score:.3f}`"
                )
                st.caption(film["description"])
        except Exception as exc:
            st.error(
                "The recommendation model could not be loaded. Check that "
                "`sentence-transformers` is installed and that the model can be "
                f"downloaded. Technical detail: {exc}"
            )

with st.expander("How does semantic matching work?"):
    st.markdown(
        "The app encodes each film synopsis and the customer's request as vectors. "
        "Each vector is normalised to unit length, so their dot product is cosine "
        "similarity. The three highest scores are returned. This is semantic matching, "
        "not a guarantee of genre, plot or suitability."
    )
