# Sakila DVD Rentals — Streamlit Lab

A three-page Streamlit dashboard built on the supplied Sakila SQLite database.

## What the application does

1. **Home:** four management KPIs (films, customers, rentals, lifetime revenue).
2. **Explore:** daily store rentals in 2005, total revenue by store, and each store's five most-rented films in 2005.
3. **Find similar films:** semantic recommendations using `sentence-transformers/all-MiniLM-L6-v2` and cosine similarity.

## Reproducible setup

Run these commands from this `your-code` directory (the database remains in the sibling `data/` directory):

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run Home.py
```

The first recommendation request downloads the MiniLM model if it is not already cached. Internet access is therefore required once for model acquisition. The SQL pages do not require a model or API key.

## Validation

```bash
python check_app.py
```

The automated Streamlit `AppTest` checks each page without opening a browser. The recommendation check downloads/loads the model and can take longer on first run.

## Data and SQL pipeline

- `Home.py`: scalar subqueries calculate catalogue, customer, rental and payment totals.
- `pages/1_Explore.py`: `rental -> inventory` identifies the store for each rental; SQLite `DATE()` and `STRFTIME()` extract day/year. The daily data is pivoted so each store is one chart series.
- Revenue follows `payment -> rental -> inventory`, grouping payment amounts by store.
- Film ranking follows `rental -> inventory -> film`, filters rental dates to 2005 and uses `ROW_NUMBER()` partitioned by store to return five deterministic results per store.
- `pages/2_Find_similar_films.py`: the model and film vectors are cached with `st.cache_resource`; all 1,000 descriptions are embedded once. Normalised embeddings make a dot product equivalent to cosine similarity.

## Expected database checkpoints

| KPI | Expected |
|---|---:|
| Films | 1,000 |
| Customers | 599 |
| Rentals | 16,044 |
| Revenue | $67,416.51 |

Store revenue is approximately $33,679.79 (Store 1) and $33,726.77 (Store 2). The 2005 rental sample has 40 recorded days between 24 May and 23 August 2005; missing dates are gaps in the sample, not synthetic zero observations. Store 1's leading film is **LOVE SUICIDES** (20 rentals), and Store 2's is **IDOLS SNATCHERS** (20 rentals).

The exact top-five lists use a deterministic title sort to break ties.

## Project structure

```text
Lab_Streamlit/
├── data/
│   ├── sakila.db
│   └── LICENSE-sakila.txt
└── your-code/
    ├── Home.py
    ├── sakila.py
    ├── check_app.py
    ├── requirements.txt
    └── pages/
        ├── 1_Explore.py
        └── 2_Find_similar_films.py
```

## Notes

- `sakila.py` resolves the database path relative to its own location, so launch the app from `your-code` as shown above.
- Streamlit reruns the script after interactions. Cached database reads, model loading and film embeddings prevent expensive work from repeating.
- No external API key is required. The sentence-transformer model is downloaded from its model host on first use.
- Database: Sakila SQLite distribution maintained by jOOQ; see `data/LICENSE-sakila.txt`.
