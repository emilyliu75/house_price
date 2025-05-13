# streamlit_app/pages/sdlt.py

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text

from streamlit_app.config import engine

@st.cache_data(ttl=3600)
def get_monthly_volumes_by_borough() -> pd.DataFrame:
    """
    Returns a DataFrame with:
      - month: first day of month (DATE)
      - borough: borough name
      - n_sales: number of transactions in that month & borough
    for the last five years.
    """
    sql = text("""
        SELECT
          (date_trunc('month', date))::date AS month,
          borough,
          COUNT(*)                        AS n_sales
        FROM emily_capstone
        WHERE date >= CURRENT_DATE - INTERVAL '5 years'
        GROUP BY month, borough
        ORDER BY month, borough;
    """)
    df = pd.read_sql(sql, engine)
    # Ensure month is a datetime64 for Altair
    df["month"] = pd.to_datetime(df["month"])
    return df

def render():
    st.set_page_config(
        page_title="Stamp Duty Holiday Impact",
        page_icon="🏠",
        layout="wide"
    )
    st.subheader("Monthly Sales Volume by Borough (5-year view)")
    st.markdown(
        """
        - Stamp Duty Holiday was introduced in July 2020 and ended in September 2021.
        """
    )

    df = get_monthly_volumes_by_borough()
    if df.empty:
        st.info("No data available.")
        return

    # Create a multi-line chart: one line per borough
    chart = (
        alt.Chart(df)
           .mark_line(point=False)
           .encode(
               x=alt.X("month:T", title="Month"),
               y=alt.Y("n_sales:Q", title="Number of Sales"),
               color=alt.Color("borough:N", title="Borough"),
               tooltip=[
                   alt.Tooltip("month:T", title="Month"),
                   alt.Tooltip("borough:N", title="Borough"),
                   alt.Tooltip("n_sales:Q", title="Sales")
               ]
           )
           .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    render()
