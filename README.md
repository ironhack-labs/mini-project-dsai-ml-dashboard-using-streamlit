![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# Lab | A Streamlit Dashboard for Sakila

## Introduction

The two stores of Sakila, the DVD-rental business whose database you queried in Week 2, want a dashboard their managers can open in a browser: what they rent, where and when, and a tool that finds films similar to the one a customer describes. You build it with Streamlit, as a three-page app on top of the same database, with no server to install: the database is a single SQLite file in this repository.

**This lab practises** turning analysis into an app. You will use, from today's **Streamlit: From Notebook to App** lesson: pages, `st.columns`, `st.metric`, charts and tables, `@st.cache_data` and `@st.cache_resource`, and buttons and their rerun behaviour; from Week 2, SQL joins and aggregations; and from Week 7, sentence embeddings and cosine similarity.

**By the end, you can:**

1. Build a multi-page Streamlit app that queries a database and shows metrics, charts and tables.
2. Apply sentence embeddings inside an app, with caching, to answer a user's free-text request.

**Time:** about 2.5 hours, plus the stretch. **Prerequisites:** SQL from Week 2, embeddings from Week 7, and today's lesson.

## Getting started

```bash
pip install streamlit sentence-transformers        # pandas and numpy you already have
cd your-code
streamlit run Home.py
```

The app opens in your browser with a sidebar listing three pages: **Home**, **Explore** and **Find similar films**. They are empty: your job is to fill them. `your-code/sakila.py` is given: `query("SELECT ...")` runs SQL on `data/sakila.db` and returns a DataFrame, cached. The schema is the same as in Week 2 (`film`, `rental`, `inventory`, `payment`, `store`, `customer`...). SQLite has two small differences from MySQL: dates are text, so use `DATE(rental_date)` for the day and `STRFTIME('%Y', rental_date)` for the year.

**First checkpoint:** `python check_app.py` (from `your-code`) runs every page without a browser and prints what it found. Before you start, it prints `no title | no image`, `0 line chart(s)` and `no text area or button yet`.

## Page 1: Home (`Home.py`)

1. A title and an image of your choice.
2. One sentence that tells the store managers what the dashboard is for.
3. Four `st.metric` numbers, side by side: the number of films, customers and rentals, and the total revenue.

**Checkpoint:** `Films 1,000`, `Customers 599`, `Rentals 16,044` and `Revenue $67,416.51`.

## Page 2: Explore (`pages/1_Explore.py`)

1. A **line chart of the daily rentals of each store in 2005**, one line per store. Hint: `st.line_chart` draws one line per column, so pivot your query's result with the stores as columns.
2. A **bar chart of the total revenue of each store**: `payment` → `rental` → `inventory`.
3. The **top 5 most rented films of each store in 2005**, as two `st.dataframe` tables side by side.

**Checkpoint:** the line chart shows rentals on 40 days between 24 May and 23 August 2005 (the sample database has gaps; say so in a caption). The two stores earn almost the same: about $33,680 and $33,727. The most rented films of 2005 are *LOVE SUICIDES* (20 rentals) in store 1 and *IDOLS SNATCHERS* (20) in store 2.

## Page 3: Find similar films (`pages/2_Find_similar_films.py`)

A customer describes the kind of film they want; the page returns the three films whose description is closest in meaning.

1. `load_model()`: load `all-MiniLM-L6-v2`, cached with `@st.cache_resource`.
2. `film_vectors()`: read the title, description and rating of every film, and embed the 1,000 descriptions, normalised. Cache it too: the embeddings must be computed once, not at every click.
3. A `st.text_area` and a `st.button("Get your recommendations")`. When the button is clicked: warn if the text is empty; otherwise embed the text, compute the cosine similarity with every film (a dot product of normalised vectors), and show the top three with their title, rating and similarity.

**Checkpoint:** for *A thoughtful drama about a monk who discovers a shark in Australia*, the top three are *Wanda Chamber*, *Fantasia Park* and *Louisiana Harry*, with similarities of about 0.68, 0.67 and 0.66. Sakila's descriptions are generated from a small vocabulary (*A Thoughtful Drama of a Monk And a Shark who must ... in Australia*), so the similarities are high for many films.

**Final checkpoint:** `python check_app.py` finds a title, an image and four metrics, one line chart, one bar chart, two tables, and three recommendations.

## Stretch

Choose one:

- **Deploy it.** Push your repository to GitHub and deploy the app on [Streamlit Community Cloud](https://share.streamlit.io), with `your-code/Home.py` as the main file and a `requirements.txt` at the root of the repository. Put the public URL in your README.
- **Filters.** Add a film category filter to the Explore page (`category` and `film_category`), and show how the top films change.
- **Better recommendations.** Embed the title and the category together with the description, or let the user choose the rating (G, PG...) before searching, and compare the results.

## Deliverables

- Your repository with the completed `Home.py` and the two pages, and a screenshot of each page in your README (or the public URL if you deployed it).

## Submission

Upon completion, add your deliverables to git. Then commit git and push your branch to the remote.

## Data

`data/sakila.db` is the Sakila sample database, originally created by Mike Hillyer for MySQL (BSD licence), in the SQLite version maintained by jOOQ at [github.com/jOOQ/sakila](https://github.com/jOOQ/sakila) under the BSD 2-Clause licence (see `data/LICENSE-sakila`). The image on the home page of the reference solution comes from [Unsplash](https://unsplash.com/license), whose licence allows free use.
