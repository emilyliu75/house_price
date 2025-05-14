import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text

from streamlit_app.config import engine

@st.cache_data(ttl=3600)
def load_borough_list() -> list[str]:
    """Fetch distinct borough names for the selector."""
    df = pd.read_sql(
        text("SELECT DISTINCT borough FROM clean_house_prices ORDER BY borough"),
        engine
    )
    return df["borough"].tolist()

@st.cache_data(ttl=3600)
def load_raw_price_data(borough_choice:str) -> pd.DataFrame:
    sql = text("""
        SELECT date, borough, property_type, new_build, price, estate_type
        FROM clean_house_prices
        WHERE borough = :borough_choice
    """)
    df = pd.read_sql(sql, engine, params={"borough_choice": borough_choice})
    df["year"] = pd.DatetimeIndex(df["date"]).year
    return df

def render():
    st.set_page_config(
        page_title="Borough Breakdown",
        page_icon="🏠",
        layout="wide"
    )
    boroughs = load_borough_list()
    # print(boroughs)
    borough_choice = st.selectbox('Select a borough', options=boroughs, index=0, help="Choose a borough to analyze")
    df = load_raw_price_data(borough_choice)

    estate_types = sorted(df["estate_type"].unique())
    estate_types_choice = st.selectbox('Select an estate type', options=['All'] + estate_types, index=0, help='choose an estate type to analyze')

    df_sel = df.copy()

    if estate_types_choice != "All":
        df_sel = df_sel[df_sel["estate_type"] == estate_types_choice]
    df_trend = (
        df_sel
        .groupby(['year', 'property_type'], as_index=False)
        .agg(
            avg_price=('price', 'mean'),
            n_sales=('price', 'count')
        )
    )
    df_trend['avg_price'] = df_trend['avg_price'].round()

    order = ['Detached', 'Semi-detached', 'Terraced', 'Flat']
    st.subheader(f"Average sale price in {borough_choice} (last 5 years)")
    chart = (
        alt.Chart(df_trend)
        .mark_line(point=True)
        .encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('avg_price:Q', title='Average price (£)'),
            color=alt.Color('property_type:N', title='property type', sort=['Detached', 'Semi-detached', 'Terraced', 'Flat'], scale=alt.Scale(domain=order)),
            tooltip=['year', 'avg_price', 'n_sales']
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    # pie chart for volumn
    st.markdown("#### Sales mix by property type")

    df_pies = (df_sel.groupby(["year", "property_type"], as_index=False)
                    .agg(n_sales=("price", "count"))
                    .sort_values(["year", "property_type"]))

    base = (
    alt.Chart(df_pies)
        .mark_arc(innerRadius=20)
        .encode(
            theta = alt.Theta("n_sales:Q", stack=True, title="Transactions"),
            color = alt.Color("property_type:N",
                              title="Property type",
                              sort=order,
                              scale=alt.Scale(domain=order)),
            tooltip=["year", "property_type", "n_sales"]
        ).properties(width=110, height=110)
)
    pies = base.facet(
        column=alt.Column("year:N",
                        header=alt.Header(title="Year", labelOrient="bottom")),
        columns=5      # show 5 pies in one row
    )

    st.altair_chart(pies, use_container_width=True)

if __name__ == "__main__":
    render()