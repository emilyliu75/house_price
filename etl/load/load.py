from sqlalchemy import create_engine
from config.db_config import load_db_config, build_db_url

def load_data(df, table_name="clean_house_prices"):
    target_cfg = load_db_config()["target_database"]
    engine = create_engine(build_db_url(target_cfg))
    df.to_sql(table_name, engine, if_exists="replace", index=False)
