import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text
from streamlit_app.config import engine
from datetime import datetime

st.set_page_config(
    page_title="London House-Price Explorer",
    page_icon="🏠",
    layout="wide"
)
st.title("🏠 London House-Price Explorer")
st.markdown(
    """
    **Welcome!**
    This dashboard lets you explore five years of London property transactions
    across Brent, Greenwich, Hackney, Wandsworth, and Westminster.

    Use the side menu to navigate between:
    - **Home Page**: Yearly price trends
    - **Borough Breakdown**: Drill down on a single borough
    - **Outward Code**: Average price by outward postcode
    - **Property Filps**: The biggest “flips” in under 24 months
    - **Stamp Duty Holiday Impact**: Sales volumes before/during/after the stamp‐duty holiday
    """
)

@st.cache_data(ttl=3600)
def load_home_metrics():
    sql = text("""
        SELECT
          COUNT(*)             AS total_sales,
          ROUND(AVG(price))    AS avg_price,
          MIN(date)           AS date_from
        FROM clean_house_prices;
    """)
    return pd.read_sql(sql, engine).iloc[0]
metrics = load_home_metrics()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total sales number",     f"{metrics.total_sales:,}")
col2.metric("Avg. sale price","£" + f"{metrics.avg_price:,}")
col3.metric("Start Date",    metrics.date_from.strftime("%Y-%m-%d"))
end_date = datetime.strptime('2024-12-31', "%Y-%m-%d")
col4.metric("End Date", end_date.strftime("%Y-%m-%d"))

st.markdown("### 📈 5-Year Price Trend ")

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
    # overview


    df = load_raw_price_data()

    # 1) Property-type dropdown
    all_types = sorted(df["property_type"].unique())
    type_choice = st.selectbox(
        "Filter by property type",
        options=["All"] + all_types,
        index=0,
        help="Choose one type or All"
    )


    # 2) Apply filters
    df_sel = df.copy()

    if type_choice != "All":
        df_sel = df_sel[df_sel["property_type"] == type_choice]


    # 3) Aggregate by year & borough
    df_trend = (
        df_sel
        .groupby(["year", "borough"], as_index=False)
        .agg(
            avg_price=("price", "mean"),
            n_sales=("price", "count")
        )
    )
    df_trend["avg_price"] = df_trend["avg_price"].round()

    # 4) Plot
    st.subheader("Average sale price by year and borough")
    order = ['Westminster', 'Wandsworth', 'Brent', 'Hackney', 'Greenwich']
#     order = (
#     df_trend[df_trend['year'] == 2020]
#     .groupby('borough')['avg_price']
#     .mean()
#     .sort_values(ascending=False)
#     .index.tolist()
# )
    chart = (
        alt.Chart(df_trend)
           .mark_line(point=True)
           .encode(
               x=alt.X("year:O", title="Year"),
               y=alt.Y("avg_price:Q", title="Average price (£)"),
               color=alt.Color("borough:N", title="Borough", sort=order),
               tooltip=["year", "borough", "avg_price", 'n_sales']
           )
           .properties(height=800)
    )
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    render()
