
# Sakila Streamlit (Multi-page)

## Quickstart
```bash
pip install -r requirements.txt
# Set env (or edit utils.py)
export SAKILA_USER=root
export SAKILA_PASS=password
export SAKILA_HOST=127.0.0.1
export SAKILA_PORT=3306
export SAKILA_DB=sakila
streamlit run app.py
```

Pages:
- EDA: Daily rentals by store (2005/2006), revenue by store, top-5 rentals per store.
- Prediction: Embedding search over film descriptions (all-MiniLM-L6-v2).
