
import streamlit as st
import pandas as pd
from utils import run_query

st.title("🧭 Exploratory Data Analysis")

tab1, tab2, tab3 = st.tabs(["📈 Daily rentals", "💰 Revenue by store", "🏆 Top-5 rentals"])

# 1) Daily rentals by store
with tab1:
    with st.expander("Filters", expanded=True):
        year = st.selectbox("Year", options=[2005, 2006], index=0, help="Sakila has data in 2005–2006; the brief focuses on 2005.")

    st.subheader("Daily rentals by store")
    sql_daily = '''
        SELECT DATE(r.rental_date) AS rental_day, s.store_id, COUNT(*) AS rentals
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN store s ON i.store_id = s.store_id
        WHERE YEAR(r.rental_date) = :year
        GROUP BY rental_day, s.store_id
        ORDER BY rental_day
    '''
    df_daily = run_query(sql_daily, {"year": year})
    if not df_daily.empty:
        pivot = df_daily.pivot(index="rental_day", columns="store_id", values="rentals").fillna(0)
        pivot.columns = [f"Store {c}" for c in pivot.columns]
        st.line_chart(pivot)
    else:
        st.info("No rental data found for the selected year.")


# 2) Total revenue by store
with tab2:
    st.subheader("Total revenue by store")
    sql_rev = '''
        SELECT s.store_id, ROUND(SUM(p.amount), 2) AS total_revenue
        FROM payment p
        JOIN staff stf ON p.staff_id = stf.staff_id
        JOIN store s ON stf.store_id = s.store_id
        GROUP BY s.store_id
        ORDER BY s.store_id
    '''
    df_rev = run_query(sql_rev)
    if not df_rev.empty:
        df_rev_display = df_rev.set_index("store_id").rename_axis("Store ID")
        st.bar_chart(df_rev_display)
        st.dataframe(df_rev, width='stretch')
    else:
        st.info("No payment data found.")


# 3) Top 5 most rented movies by each store in selected year
with tab3:
    st.subheader(f"Top 5 most rented movies by store in {year}")
    sql_top = '''
        SELECT s.store_id, f.film_id, f.title, COUNT(*) AS rentals_{year}
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN store s ON i.store_id = s.store_id
        JOIN film f ON i.film_id = f.film_id
        WHERE YEAR(r.rental_date) = :year
        GROUP BY s.store_id, f.film_id, f.title
    '''.replace("{year}", str(year))
    df_top = run_query(sql_top, {"year": year})
    if not df_top.empty:
        out_rows = []
        for sid, g in df_top.groupby("store_id", sort=True):
            top5 = g.sort_values(by=f"rentals_{year}", ascending=False).head(5)
            out_rows.append(top5)
        df_top5 = pd.concat(out_rows, ignore_index=True)
        st.dataframe(df_top5, width='stretch')
    else:
        st.info("No rentals for that year.")

