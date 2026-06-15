"""
app.py — Streamlit frontend for the Sakila ML dashboard.

All data/logic lives in backend.py; this file only builds the user interface.
Three pages, chosen from the sidebar: Home, EDA, Prediction.

Run:  streamlit run app.py
"""
import os

import streamlit as st

# Bring in the data + plotting + prediction helpers from the backend.
from backend import (
    get_daily_rentals_2005,
    get_benefit_by_store,
    get_top5_movies_by_store,
    plot_daily_rentals,
    plot_benefit_by_store,
    load_film_embeddings,
    find_similar_movies,
)

# Page-wide settings: browser tab title, icon, and a wide layout.
st.set_page_config(page_title="Sakila ML Dashboard", page_icon="🎬", layout="wide")


# ------------------------------- pages ----------------------------------
def home_page():
    # Landing page: title, a short intro, a hero image, and a footer.
    st.title(":material/movie: Sakila Movie Rental Dashboard")
    st.write(
        "Welcome to the **Sakila Movie Rental Dashboard** — an interactive tool for "
        "exploring a classic movie-rental business. The dataset captures rentals, payments, "
        "inventory and films across two stores. On the **EDA** page you can dig into daily "
        "rental trends, compare each store's total revenue, and see which titles topped the "
        "charts in 2005, all visualised with interactive Plotly charts. The **Prediction** "
        "page goes further: type any movie description and it returns the three most similar "
        "films, powered by sentence-transformer embeddings and cosine similarity. Together "
        "the app combines SQL data analysis, data visualisation and modern NLP to turn raw "
        "rental records into insight."
    )
    # Show the local title image if it exists, otherwise a simple fallback message.
    image_path = "assets/cinema.jpg"
    if os.path.exists(image_path):
        st.image(
            image_path,
            caption="A grand old movie palace — the world Sakila's rental business lived in",
            use_container_width=True,
        )
    else:
        st.info(":material/movie: Welcome to the Sakila dashboard.")
    st.write(
        "Use the sidebar to switch between **EDA** (exploratory analysis) "
        "and **Prediction** (find similar movies by description)."
    )

    # Footer line (author + date).
    st.divider()
    st.markdown(
        "<p style='text-align:center;'>Built by Daniel V. · June 2026</p>",
        unsafe_allow_html=True,
    )



def eda_page():
    # Exploratory analysis page: two charts plus a top-5 table per store.
    st.title(":material/bar_chart: Exploratory Data Analysis")
    st.markdown(
        "<p>"
        "Rental trends, store revenue and the most popular movies across both stores in 2005."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 1) Line chart: daily rentals per store (the chart carries its own title).
    daily = get_daily_rentals_2005()
    st.plotly_chart(plot_daily_rentals(daily), use_container_width=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 2) Bar chart: total benefit per store (also self-titled).
    benefit = get_benefit_by_store()
    st.plotly_chart(plot_benefit_by_store(benefit), use_container_width=True)

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 3) Table: top 5 rented films per store. Needs its own heading (no chart title).
    st.write("### Top 5 most rented movies by store (2005)")
    top = get_top5_movies_by_store()
    cols = st.columns(2)  # one column per store, side by side
    for col, store_id in zip(cols, sorted(top["store_id"].unique())):
        # Keep only this store's rows, sort by rentals, take the top 5.
        top5 = (
            top[top["store_id"] == store_id]
            .sort_values("Times Rented", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )
        col.write(f"**Store {store_id}**")
        col.dataframe(top5[["Title", "Times Rented"]], use_container_width=True)


def prediction_page():
    # Prediction page: user types a description, we return the most similar films.
    st.title(":material/auto_awesome: Find similar movies")
    st.write(
        "Enter a movie description below. The app embeds it with a Sentence "
        "Transformer and returns the **3 most similar movies** by description."
    )

    # Load the model + film embeddings once (cached in the backend).
    with st.spinner("Loading embedding model (first time only)..."):
        model, films, embeddings = load_film_embeddings()

    # Text box for the user's movie description.
    description = st.text_area(
        "Movie description:",
        placeholder="e.g. a typical american movie where the hero wins and gets the girl at the end..",
        height=140,
    )

    # Only run the search after the button is clicked.
    if st.button("Get Your Prediction"):
        if not description.strip():
            st.warning("No description -> no prediction, my friend.")
        else:
            # Find the 3 closest films and show them with nice column headers.
            results = find_similar_movies(description, model, films, embeddings, top_n=3)
            st.success("Top 3 most similar movies:")
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "title": st.column_config.TextColumn("Title"),
                    "rating": st.column_config.TextColumn("Rating"),
                    "similarity": st.column_config.NumberColumn("Similarity Score"),
                    "description": st.column_config.TextColumn("Description", width="large"),
                },
            )


# ------------------------------- main -----------------------------------
def main():
    # Inject custom CSS (font, icon fix, gray paragraphs).
    st.markdown("""
                <style>
                    html, body, .stApp, .stApp * { font-family: "Avenir", "Avenir Next", sans-serif !important;}
                    .stApp span[role="img"] { font-family: "Material Symbols Rounded" !important; }
                    .stApp p { color: gray; }
                </style>
                """, unsafe_allow_html=True)

    # Sidebar navigation: pick which page to show.
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to ->", ["Home", "EDA", "Prediction"])

    if page == "Home":
        home_page()
    elif page == "EDA":
        eda_page()
    else:
        prediction_page()


if __name__ == "__main__":
    main()
