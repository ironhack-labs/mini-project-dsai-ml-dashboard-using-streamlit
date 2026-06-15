![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# Mini Project | Data - Create a Machine Learning dashboard using Streamlit

## Mini Project Overview

This is a 2-day hands-on mini project where you need to create a streamlit application for the Sakila database. This application must contain three pages:

- Home
- EDA
- Prediction

## Instructions

### Dataset

In this project, you will be using the [Sakila](https://dev.mysql.com/doc/sakila/en/) database of movie rentals. You can follow the steps listed here to get the data locally: [Sakila sample database - installation](https://dev.mysql.com/doc/sakila/en/sakila-installation.html). You can work with two sql query files - `sakila-schema.sql` (creates the schema) + `sakila-data.sql` which inserts the data.

The ERD is pictured below - not all tables are shown, but many of the key fields you will be using are visible:

<br>

![DB schema](https://education-team-2020.s3-eu-west-1.amazonaws.com/data-analytics/database-sakila-schema.png)

<br><br>

## Requirements

### Home page

Must contain a title and an image of your choice.

### EDA page

Must contain the following plots:

- A line plot of daily rentals by each store in 2005
- A bar plot with the total benefit by each store
- A dataframe with the top five most rented movies by each store in 2005. Hint: use `st.dataframe(df)`

### Prediction page

<!-- Must contain a `st.text_area()` that will allow the user to input a movie description and get a prediction from the movie rating prediction model created yesterday.
It also must contain an `st.button("Get Your Prediction")` button. -->

Must contain a `st.text_area()` that will allow the user to input a movie description and get the top 3 most similar movies by description. Display the matches’ title and rating. It also must contain an `st.button(“Get Your Prediction”)` button. HINT: use the embedding model (Sentence Transformer) and the cosine similarity function.


## Submission

Upon completion, add your deliverables to git. Then commit git and push your branch to the remote.

---

## Running this project

The app reads from a portable SQLite database (`data/sakila.db`) so **no running MySQL
server is required**.

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Project structure
- `backend.py` — data loading, SQL queries, plots and the embedding logic
- `app.py` — Streamlit frontend (`main()` with sidebar navigation)
- `build_db.py` — one-time ETL: MySQL Sakila → portable `data/sakila.db`
- `data/sakila.db` — the database the app reads from

### Pages
- **Home** — title + image
- **EDA** — daily rentals per store (2005), total benefit per store, top-5 rented films per store
- **Prediction** — enter a movie description, get the 3 most similar films (Sentence Transformer + cosine similarity), with title and rating

### Rebuilding the database (optional)
`data/sakila.db` is already included. To regenerate it from a MySQL Sakila instance,
adjust the connection string in `build_db.py` and run:

```bash
python build_db.py
```
