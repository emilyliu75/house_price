import pandas as pd
import streamlit as st
import altair as alt
from sqlalchemy import text

# 👉 Reuse the engine you built in streamlit_app/config.py
from streamlit_app.config import engine

@st.cache_data(ttl=3600)
def get_heatmap_data() -> pd.DataFrame:
    sql = text("""
        SELECT
          split_part(postcode, ' ', 1) AS outcode,
          ROUND(AVG(price))            AS avg_price,
          COUNT(*)                     AS n_sales
        FROM clean_house_prices
        GROUP BY outcode
        ORDER BY avg_price DESC;
    """)
    return pd.read_sql(sql, engine)

@st.cache_data(ttl=3600)
def get_all_data() -> pd.DataFrame:
    sql = text("""
        SELECT
          date, postcode, price, property_type,address
        FROM clean_house_prices
    """)
    return pd.read_sql(sql, engine)

def render():
    st.set_page_config(
        page_title="Outward Code Analysis",
        page_icon="🏠",
        layout="wide"
    )
    df = get_heatmap_data()
    st.subheader("Average sale price by outward code (last 5 years)")
    st.markdown(
        """
        - Outward code is the first part of a postcode (e.g., SE10, W1A).
        """
    )
    chart = (
        alt.Chart(df)
           .mark_bar()
           .encode(
               x=alt.X("outcode:N", sort="-y", title="Outward code"),
               y=alt.Y("avg_price:Q",  title="Average price (£)"),
               tooltip=["outcode", "avg_price", "n_sales"]
           )
    )
    st.altair_chart(chart, use_container_width=True)

    # search by postcode
    st.subheader("Search by postcode")
    # Input field
    user_postcode = st.text_input("Enter a full or partial postcode (e.g., SE10 or W1A 1AA):").strip().upper()

    # Filter results
    if user_postcode:
        df_all = get_all_data()

        filtered_df = df_all[df_all['postcode'].str.startswith(user_postcode)]

        if not filtered_df.empty:
            st.success(f"{len(filtered_df)} transactions found for '{user_postcode}'")
            st.dataframe(filtered_df.sort_values("date", ascending=False), hide_index=True)
        else:
            st.warning("No transactions found for the entered postcode.")

if __name__ == "__main__":
    render()