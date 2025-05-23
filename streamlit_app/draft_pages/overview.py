# streamlit_app/pages/overview.py

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text
from streamlit_app.config import engine

st.title("Overview of House Prices in London")

@st.cache_data(ttl=3600)
def load_raw_price_data() -> pd.DataFrame:
    sql = text("""
        SELECT date, borough, property_type, new_build, price
        FROM clean_house_prices
    """)
    df = pd.read_sql(sql, engine)
    df["year"] = pd.DatetimeIndex(df["date"]).year
    return df

def render():
    df = load_raw_price_data()

    # 1) Property-type dropdown
    all_types = sorted(df["property_type"].unique())
    type_choice = st.selectbox(
        "Filter by property type",
        options=["All"] + all_types,
        index=0,
        help="Choose one type or All"
    )

    # 2) New-build status dropdown
    # build_options = ["All", "New build", "Existing"]
    # build_choice = st.selectbox(
    #     "Filter by new-build status",
    #     options=build_options,
    #     index=0,
    #     help="Show only new builds, only existing, or All"
    # )

    # 3) Apply filters
    df_sel = df.copy()

    if type_choice != "All":
        df_sel = df_sel[df_sel["property_type"] == type_choice]

    # if build_choice == "New build":
    #     df_sel = df_sel[df_sel["new_build"] == "Y"]
    # elif build_choice == "Existing":
    #     df_sel = df_sel[df_sel["new_build"] == "N"]

    # 4) Aggregate by year & borough
    df_trend = (
        df_sel
        .groupby(["year", "borough"], as_index=False)
        .agg(
            avg_price=("price", "mean"),
            n_sales=("price", "count")
        )
    )
    df_trend["avg_price"] = df_trend["avg_price"].round()

    # 5) Plot
    st.subheader("Average sale price by year and borough")
    chart = (
        alt.Chart(df_trend)
           .mark_line(point=True)
           .encode(
               x=alt.X("year:O", title="Year"),
               y=alt.Y("avg_price:Q", title="Average price (£)"),
               color=alt.Color("borough:N", title="Borough"),
               tooltip=["year", "borough", "avg_price", 'n_sales']
           )
           .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    render()