import streamlit as st 
from backend import get_connection, daily_rentals_by_store, total_revenue_by_store, top_five_by_store, get_films_for_search
from matplotlib import pylab as plt 
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def get_film_embeddings(_model, descriptions):
    return _model.encode(descriptions)


def main():
    # Home section
    st.title("Sakila Video Rental Dashboard")
    st.image("https://patch.com/img/cdn20/users/22887410/20180806/021129/styles/raw/public/processed_images/548991d-1533578743-3854.jpg?width=1200")

    #EDA section

    # DAILY RENTALS BY STORE

    st.header("Daily Rentals by Store: 2005")
    daily_rentals = daily_rentals_by_store()  # This IS a DataFrame

    # Split the data by store
    store_1 = daily_rentals[daily_rentals['Store ID'] == 1]
    store_2 = daily_rentals[daily_rentals['Store ID'] == 2]
    store_1 = store_1.sort_values('Rental Date')
    store_2 = store_2.sort_values('Rental Date')

    # Plot both lines
    plt.figure(figsize=(10, 10))
    plt.plot(store_1['Rental Date'], store_1['Rental Count'], label='Store 1', color='#FF6B6B')
    plt.plot(store_2['Rental Date'], store_2['Rental Count'], label='Store 2', color='#4ECDC4')
    plt.title("Daily Rentals By Store: 2005")
    st.pyplot(plt)


    # TOTAL REVENUE BY STORE

    st.header("Total Revenue by Store: 2005")
    # bar plot 
    total_revenue = total_revenue_by_store() # create the dataframe
    plt.figure(figsize=(10, 7))
    plt.bar(total_revenue["Store ID"].astype(str), total_revenue["Total Revenue Per Store"], color=['#FF6B6B', '#4ECDC4'], edgecolor='black', linewidth=1.5)
    plt.title("Total Revenue by Store: 2005")
    plt.xlabel('Store')
    plt.ylabel('Total Revenue')
    st.pyplot(plt)


    # TOP 5 MOVIES BY STORE 

    st.header("Top 5 Movie Rentals by Store")
    top_5 = top_five_by_store()
    st.dataframe(top_5)

    # SEARCH FUNCTION    
    films = get_films_for_search()


   # Load model and encode descriptions (cached)
    model = load_model()
    film_embeddings = get_film_embeddings(model, films["description"].tolist())
    #UI
    st.header("Search for Movies")
    user_input = st.text_area("What kind of movie do you want to watch?")

    if st.button("Search"):
        # encodes single user input to 1 vector
        user_embedding = model.encode([user_input])
        # Compute cosine similarities
        similarities = cosine_similarity(user_embedding, film_embeddings)
                    # compares that one user vector against all 1000 and returns a similarity score for each.
        # Get indices of top 3 highest scores
        top_3_indices = similarities[0].argsort()[-3:][::-1]
        # argsort() returns: [0, 1, 2, 3, 4] (indices in order of score, low to high)
        # [-3:] = "last 3 items" --> [2, 3, 4] (the 3 highest scores)
        # [::-1] = "reverse it" --> [4, 3, 2] (now highest first)

        # Use those indices to get the films
        top_3_films = films.iloc[top_3_indices]
        # iloc lets you select rows by their index position (0, 1, 2, etc.).
        # So if top_3_indices is [633, 292, 845] then films.iloc[top_3_indices] 
        # Grabs rows 633, 292, and 845 from the films DataFrame — which are your top 3 matching movies.

        st.write("Top 3 Matches:")
        st.dataframe(top_3_films[['title', 'rating']])


if __name__ == '__main__':
    main()