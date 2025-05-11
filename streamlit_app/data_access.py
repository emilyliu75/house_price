import pandas as pd
from sqlalchemy import text
from utils.sql_utils import import_sql_query
from pathlib import Path
from .config import engine

def load_heatmap_data():
    sql = import_sql_query(Path(__file__).parents[1] / "etl/sql/heatmap_outcode.sql")
    return pd.read_sql(text(sql), engine)