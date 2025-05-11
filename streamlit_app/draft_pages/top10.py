import streamlit as st
import pandas as pd
from sqlalchemy import text

from streamlit_app.config import engine

@st.cache_data(ttl=3600)
def get_top10() -> pd.DataFrame:
    sql = text("""
        SELECT
          date,
          borough,
          postcode,
          address,
          property_type,
          price
        FROM clean_house_prices
        ORDER BY price DESC
        LIMIT 10;
    """)
    return pd.read_sql(sql, engine)

def render():
    st.subheader("Top 10 most-expensive transactions")
    df = get_top10()
    df["price"] = df["price"].map("£{:,}".format)
    st.table(df.set_index("price"))

if __name__ == "__main__":
    render()