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

def render():
    df = get_heatmap_data()
    st.subheader("Average sale price by outward code (last 5 years)")
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

if __name__ == "__main__":
    render()