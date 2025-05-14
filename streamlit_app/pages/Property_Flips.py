import streamlit as st
import pandas as pd
from sqlalchemy import text

from streamlit_app.config import engine

@st.cache_data(ttl=3600)
def get_top_flips(limit: int = 5000) -> pd.DataFrame:
    sql = text(f"""
        SELECT
          postcode,
          address,
          sale_date,
          next_date,
          sale_price,
          next_price,
          months_between,
          pct_gain
        FROM v_flips_24m
        ORDER BY pct_gain DESC
        LIMIT :n;
    """)
    return pd.read_sql(sql, engine, params={"n": limit})

def render():
    st.set_page_config(
        page_title="Property Flips",
        page_icon="🏠",
        layout="wide"
    )
    st.subheader("Top property flips (≤ 24 months)")
    df = get_top_flips()
    if df.empty:
        st.warning("No flip records found.")
        return

    # format numbers
    df["sale_price"] = df["sale_price"].map("£{:,}".format)
    df["next_price"] = df["next_price"].map("£{:,}".format)
    df["pct_gain"]   = df["pct_gain"].map("{:.0f}%".format)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "postcode":        {"header": "Postcode"},
            "address":         {"header": "Address"},
            "sale_date":       {"header": "Sale date"},
            "next_date":       {"header": "Resale date"},
            "sale_price":      {"header": "Sale price"},
            "next_price":      {"header": "Resale price"},
            "months_between":  {"header": "Months btwn"},
            "pct_gain":        {"header": "% gain"}
        }
    )

if __name__ == "__main__":
    render()