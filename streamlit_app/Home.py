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

# import os
# import sys

# # Ensure project root is on sys.path so we can import etl/, utils/, config/, streamlit_app/…
# proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if proj_root not in sys.path:
#     sys.path.insert(0, proj_root)

# import streamlit as st

# from streamlit_app.pages.overview          import render as render_overview
# from streamlit_app.pages.heatmap           import render as render_heatmap
# from streamlit_app.pages.borough_analysis  import render as render_borough
# from streamlit_app.pages.sdlt_effect   import render as render_sdlt
# from streamlit_app.pages.flips         import render as render_flips
# # from streamlit_app.pages.home          import render as render_home
# # from streamlit_app.pages.top10         import render as render_top10

# # If you add more pages, just import them here and add to PAGES
# # PAGES = {
# #     "Overview":           render_overview,
# #     "Price heatmap":      render_heatmap,
# #     "Borough breakdown":  render_borough,
# #     "SDLT effect":        render_sdlt,
# #     "Flips":              render_flips,
# #     # "Top 10":             render_top10,
# # }

# st.title("London House-Price Explorer")
# render_overview()
# Sidebar for navigation
# selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Call the appropriate render function
# PAGES[selection]()
