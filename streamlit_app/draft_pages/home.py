import streamlit as st
import pandas as pd
from sqlalchemy import text
from streamlit_app.config import engine

# Set a nice page title & icon
st.set_page_config(
    page_title="🏠 London House-Price Explorer",
    page_icon="🏠",
    layout="wide"
)

# ————————————————
# 1) Title & Intro
# ————————————————
st.title("🏠 London House-Price Explorer")
st.markdown(
    """
    **Welcome!**
    This dashboard lets you explore five years of London property transactions
    across Brent, Greenwich, Hackney, Wandsworth, and Westminster.

    Use the top menu to navigate between:
    - **Overview**: Yearly price trends by borough
    - **Price Heatmap**: Average price by outward postcode
    - **Borough Analysis**: Drill down on a single borough
    - **SDLT Effect**: Sales volumes before/during/after the stamp‐duty holiday
    - **Flips**: The biggest “flips” in under 24 months
    - **Top 10 Sales**: The highest‐value transactions
    """
)

# ————————————————
# 2) Key Summary Metrics
# ————————————————
# We’ll pull three headline numbers:
#   • Total number of transactions
#   • Overall average price
#   • Most expensive sale
@st.cache_data(ttl=3600)
def load_home_metrics():
    sql = text("""
        SELECT
          COUNT(*)             AS total_sales,
          ROUND(AVG(price))    AS avg_price,
          MAX(price)           AS top_price,
          MAX(date)            AS latest_sale_date
        FROM clean_house_prices;
    """)
    return pd.read_sql(sql, engine).iloc[0]

metrics = load_home_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total sales",     f"{metrics.total_sales:,}")
col2.metric("Avg. sale price","£" + f"{metrics.avg_price:,}")
col3.metric("Top sale price",  "£" + f"{metrics.top_price:,}")
col4.metric("Data through",    metrics.latest_sale_date.strftime("%Y-%m-%d"))

# ————————————————
# 3) Quick Trend Snapshot
# ————————————————
st.markdown("### 📈 5-Year Price Trend (All Boroughs Combined)")

@st.cache_data(ttl=3600)
def load_combined_trend():
    sql = text("""
        SELECT
            date_trunc('year', date)::date AS year,
            ROUND(AVG(price))             AS avg_price
        FROM clean_house_prices
        GROUP BY year
        ORDER BY year;
    """)
    df = pd.read_sql(sql, engine)
    df["year"] = pd.to_datetime(df["year"]).dt.year
    return df

trend = load_combined_trend()
st.line_chart(
    data=trend.set_index("year")["avg_price"],
    height=300,
    use_container_width=True
)

# ————————————————
# 4) Footer / Data Source
# ————————————————
st.markdown(
    """
    **Data source:** UK Land Registry Price Paid
    **Boroughs covered:** Brent, Greenwich, Hackney, Wandsworth, Westminster
    **Last updated:** whenever you rerun the ETL pipeline
    """
)

# if __name__ == "__main__":
#     render()