import os
import pandas as pd
import logging
from sqlalchemy import text, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from etl.config.db_config import load_db_config, DatabaseConfigError
from utils.db_utils import create_db_engine, DatabaseConnectionError
from utils.logging_utils import setup_logger
from utils.sql_utils import import_sql_query
from etl.load.post_load_enrichment import enrich_database

TARGET_TABLE = "emily_capstone"

# Configure the logger
logger = setup_logger(__name__, "database_query.log", level=logging.INFO)


def load_data(df_clean: pd.DataFrame) -> None:
    """
    1) Drop any existing clean_house_prices table (cascade to drop dependents)
    2) Create fresh via pandas.to_sql(if_exists='fail')
    3) If it still exists, fall back to an INSERT … ON CONFLICT DO NOTHING
    4) Run post-load enrichment (indexes + views)
    """
    schema = os.getenv("TARGET_DB_SCHEMA", "public")
    try:
        # load connection info and build an Engine
        cfg = load_db_config()["target_database"]
        engine = create_db_engine(cfg)

        # 1) DROP old table + dependent views/indexes, committed immediately
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {schema}.{TARGET_TABLE} CASCADE;"))
            logger.info("Dropped old table (and dependents) if it existed: %s", TARGET_TABLE)

        # 2) Try to create brand-new table
        df_clean.to_sql(
            TARGET_TABLE,
            engine,
            if_exists="fail",  # raises ValueError if table still exists
            index=False,
            schema=schema
        )
        logger.info("Created table %s with %d rows", TARGET_TABLE, len(df_clean))

    except ValueError:
        # 3) Table still exists → bulk insert, skipping duplicates
        logger.warning("%s already exists, inserting new rows only (DO NOTHING on conflict)", TARGET_TABLE)
        _insert_ignore_duplicates(df_clean, engine)

    except (DatabaseConfigError, DatabaseConnectionError) as e:
        logger.error("DB config/connection problem: %s", e)
        raise

    except Exception as e:
        logger.error("Unexpected error in load_data: %s", e)
        raise

    # 4) Post-load enrichment (indexes & views)

    enrich_database(schema, engine)


def _insert_ignore_duplicates(df: pd.DataFrame, conn):
    """
    Insert every row from df; skip those that already exist.
    Assumes the table has a composite primary key on (date, postcode, price, borough)
    or another suitable unique constraint.
    """
    metadata = MetaData()
    table = Table(TARGET_TABLE, metadata, autoload_with=conn)
    rows = df.to_dict(orient="records")

    insert_stmt = insert(table).values(rows)
    insert_stmt = insert_stmt.on_conflict_do_nothing()   # ← skip duplicates


    Session = sessionmaker(bind=conn)
    session = Session()
    try:
        session.execute(insert_stmt)
        session.commit()
        logger.info("Inserted %d rows (duplicates ignored)", len(rows))
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("Bulk insert failed: %s", e)
        raise
    finally:
        session.close()
