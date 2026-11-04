import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from sakila import query

st.set_page_config(page_title="Find similar films", page_icon="🔎")
st.title("🔎 Find similar films")

st.write("Describe the kind of film you would like to watch, "
    "and we'll recommend the three closest matches.")



@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")
    pass


@st.cache_resource
def film_vectors():
    films = query("""
        SELECT
            title,
            description,
            rating
        FROM film
        ORDER BY film_id
    """)

    # Load the model
    model = load_model()

    # Get film descriptions
    descriptions = films["description"].fillna("").tolist()

    # Generate normalized embeddings
    embeddings = model.encode(
        descriptions,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return films, embeddings


# TODO 9: a st.text_area for the customer's description and a st.button("Get your recommendations").
#         When it is clicked: warn if the text is empty; otherwise embed it, compute the cosine similarity
#         with every film (a dot product, since the vectors are normalised), and show the top 3 films
#         with their title, rating and similarity.

rating_filter = st.selectbox(
    "Choose a film rating",
    ["All", "G", "PG", "PG-13", "R", "NC-17"]
)

user_text = st.text_area(
    "What kind of film are you looking for?",
    placeholder="I want an exciting adventure film about "
                "heroes exploring a mysterious world..."
)

# Get recommendations

if st.button("Get your recommendations"):

    if not user_text.strip():
        st.warning("Please enter a film description first.")

    else:
        # Load cached model and film embeddings
        model = load_model()
        films, embeddings = film_vectors()

        # Embed the customer description
        user_embedding = model.encode(
            user_text,
            normalize_embeddings=True
        )

        # Calculate similarity to all films
        similarities = np.dot(embeddings, user_embedding)

        # Create a copy of the film data
        results = films.copy()
        results["similarity"] = similarities

        # Apply rating filter
        if rating_filter != "All":
            results = results[
                results["rating"] == rating_filter
            ]

        # Select the three most similar films
        top_3 = results.sort_values(
            "similarity",
            ascending=False
        ).head(3)

        # Display recommendations
        st.subheader("🍿 Your Top 3 Recommendations")

        if top_3.empty:
            st.info("No films match the selected rating.")
        else:
            for rank, (_, film) in enumerate(
                top_3.iterrows(), start=1
            ):
                st.markdown(f"### {rank}. {film['title']}")
                st.write(f"**Rating:** {film['rating']}")
                st.write(
                    f"**Similarity:** {film['similarity']:.2%}"
                )
                st.write(
                    f"**Description:** {film['description']}"
                )
                st.divider()
