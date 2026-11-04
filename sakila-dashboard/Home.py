import streamlit as st

st.title("Sakila Movie Dashboard")

st.write("""
This project presents an exploratory analysis of the **Sakila movie rental database**,
focusing on rental activity, store performance, and movie recommendations.

Below is the database schema, illustrating the relationships between different tables included.
""")

st.image(
    "sakila_db_scheme.png",
    caption="Sakila Database Schema",
    use_container_width=True
)

st.markdown("""
For more information about the database, its structure and contents,
visit the [official Sakila documentation](https://dev.mysql.com/doc/sakila/en/).
""")