import os
import pandas as pd
import sqlalchemy
import streamlit as st
import altair as alt
from dotenv import load_dotenv
from utils.db_utils import create_db_engine
import sys
# Ensure the utils module is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
# local dev: load .env.dev so TARGET_DB_* are defined
load_dotenv(".env.dev", override=False)

# url = (
#     f"postgresql://{os.getenv('TARGET_DB_USER')}:{os.getenv('TARGET_DB_PASSWORD')}"
#     f"@{os.getenv('TARGET_DB_HOST')}:{os.getenv('TARGET_DB_PORT')}/{os.getenv('TARGET_DB_NAME')}"
# )
# engine = sqlalchemy.create_engine(url)
engine = create_db_engine({
    "user": os.getenv("TARGET_DB_USER"),
    "password": os.getenv("TARGET_DB_PASSWORD"),
    "host": os.getenv("TARGET_DB_HOST"),
    "port": os.getenv("TARGET_DB_PORT"),
    "dbname": os.getenv("TARGET_DB_NAME"),
})

# caches the query result for one hour
@st.cache_data(ttl=3600)
def load_heat_data():
    return pd.read_sql("""
        SELECT split_part(postcode,' ',1) AS outcode,
               AVG(price)                 AS avg_price,
               COUNT(*)                   AS n_sales
        FROM   clean_house_prices
        GROUP  BY outcode
    """, engine)

heat = load_heat_data()

st.subheader("Average sale price by outward code (last 5 years)")
chart = (
    alt.Chart(heat)
    .mark_bar()
    .encode(
        x=alt.X('outcode:N', sort='-y', title='Outward code'),
        y=alt.Y('avg_price:Q', title='Average price (£)'),
        tooltip=['outcode','avg_price','n_sales']
    )
)
st.altair_chart(chart, use_container_width=True)

