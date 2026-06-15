"""
app.py — Streamlit frontend for the Sakila ML dashboard.

All data/logic lives in backend.py; this file only defines the user interface.
Three pages via the sidebar: Home, EDA, Prediction.

Run:  streamlit run app.py
"""
import streamlit as st

from backend import (
    get_daily_rentals_2005,
    get_benefit_by_store,
    get_top5_movies_by_store,
    plot_daily_rentals,
    plot_benefit_by_store,
    load_film_embeddings,
    find_similar_movies,
)

st.set_page_config(page_title="Sakila ML Dashboard", page_icon="🎬", layout="wide")


# ------------------------------- pages ----------------------------------
def home_page():
    st.title(":material/movie: Sakila Movie Rental Dashboard")
    st.subheader("Explore rentals, revenue and find similar movies")
    try:
        st.image(
            "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200",
            caption="Sakila — a sample movie rental business",
            use_container_width=True,
        )
    except Exception:
        st.info("🎥 Welcome to the Sakila dashboard.")
    st.write(
        "Use the sidebar to switch between **EDA** (exploratory analysis) "
        "and **Prediction** (find similar movies by description)."
    )



def eda_page():
    st.title(":material/bar_chart: Exploratory Data Analysis")
    st.markdown(
        "<p style = color:gray;'>"
        "Rental trends, store revenue and the most popular movies across both stores in 2005."
        "</p>",
        unsafe_allow_html=True,
    )

    # 1) Line plot — der Chart bringt seinen Titel selbst mit
    daily = get_daily_rentals_2005()
    st.plotly_chart(plot_daily_rentals(daily), use_container_width=True)

    # 2) Bar plot — ebenfalls mit eigenem Titel
    benefit = get_benefit_by_store()
    _, mid, _ = st.columns([1, 2, 1])
    mid.plotly_chart(plot_benefit_by_store(benefit), use_container_width=True)

    # 3) Dataframe — die braucht eine eigene Überschrift (hat keinen Chart-Titel)
    st.write("### Top 5 most rented movies by store (2005)")
    top = get_top5_movies_by_store()
    cols = st.columns(2)
    for col, store_id in zip(cols, sorted(top["store_id"].unique())):
        top5 = (
            top[top["store_id"] == store_id]
            .sort_values("Times Rented", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )
        col.write(f"**Store {store_id}**")
        col.dataframe(top5[["Title", "Times Rented"]], use_container_width=True)


def prediction_page():
    st.title(":material/auto_awesome: Find similar movies")
    st.write(
        "Enter a movie description below. The app embeds it with a Sentence "
        "Transformer and returns the **3 most similar movies** by description."
    )

    with st.spinner("Loading embedding model (first time only)..."):
        model, films, embeddings = load_film_embeddings()

    description = st.text_area(
        "Movie description:",
        placeholder="e.g. a typical american movie where the hero wins and gets the girl at the end..",
        height=140,
    )

    if st.button("Get Your Prediction"):
        if not description.strip():
            st.warning("No description -> no prediction, my friend.")
        else:
            results = find_similar_movies(description, model, films, embeddings, top_n=3)
            st.success("Top 3 most similar movies:")
            st.dataframe(results, use_container_width=True)


# ------------------------------- main -----------------------------------
def main():
    st.markdown("""
                <style>
                    html, body, .stApp, .stApp * { font-family: "Avenir", "Avenir Next", sans-serif !important;}
                    .stApp span[role="img"] { font-family: "Material Symbols Rounded" !important; }
                    
                    
                </style>
                """, unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "EDA", "Prediction"])

    if page == "Home":
        home_page()
    elif page == "EDA":
        eda_page()
    else:
        prediction_page()


if __name__ == "__main__":
    main()
