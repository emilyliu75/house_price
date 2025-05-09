import pandas as pd
import altair as alt
import sqlalchemy
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv('.env.dev')
engine = sqlalchemy.create_engine(
    f"postgresql://{os.getenv('TARGET_DB_USER')}:{os.getenv('TARGET_DB_PASSWORD')}"
    f"@{os.getenv('TARGET_DB_HOST')}:{os.getenv('TARGET_DB_PORT')}/"
    f"{os.getenv('TARGET_DB_NAME')}"
)

heat = pd.read_sql("""
    SELECT LEFT(postcode,4) AS code, AVG(price) AS avg_price
    FROM clean_house_prices
    GROUP BY code
""", engine)

st.title("Average price by outward-code")
st.altair_chart(
    alt.Chart(heat).mark_rect().encode(
        x="code:N", y="1:N", color="avg_price:Q",
        tooltip=["code", "avg_price"]
    ).properties(height=120),
    use_container_width=True
)