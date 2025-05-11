import pandas as pd
import logging

from sqlalchemy import Table, MetaData, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from etl.config.db_config import load_db_config, DatabaseConfigError
from utils.db_utils import create_db_engine, DatabaseConnectionError
from utils.logging_utils import setup_logger
from etl.load.post_load_enrichment import enrich_database


TARGET_TABLE = "clean_house_prices"

# set up a module‐level logger
logger = setup_logger(__name__, "database_query.log", level=logging.INFO)


def load_data(df_clean: pd.DataFrame) -> None:
    """
    1) Drop any existing clean_house_prices table (CASCADE to remove views).
    2) Create a fresh table via pandas.to_sql(if_exists='fail').
    3) If it already exists, perform an upsert instead.
    4) Run post-load enrichment (indexes & views).
    """
    try:
        # load connection info
        cfg = load_db_config()["target_database"]
        engine = create_db_engine(cfg)

        # 1) drop old table + dependents
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {TARGET_TABLE} CASCADE;"))
            logger.info("Dropped old table (and dependents) if it existed: %s", TARGET_TABLE)

        # 2) create fresh table
        df_clean.to_sql(
            TARGET_TABLE,
            engine,
            if_exists="fail",  # will raise ValueError if somehow still exists
            index=False
        )
        logger.info("Created table %s with %d rows", TARGET_TABLE, len(df_clean))

    except ValueError:
        # 3) table existed → do an upsert
        logger.warning("%s already exists, performing upsert", TARGET_TABLE)
        _upsert(df_clean, engine)

    except (DatabaseConfigError, DatabaseConnectionError) as e:
        logger.error("DB config/connection error: %s", e)
        raise

    except Exception as e:
        logger.error("Unexpected error in load_data: %s", e)
        raise

    # 4) post‐load: recreate indexes & views
    enrich_database()


def _upsert(df: pd.DataFrame, engine) -> None:
    """
    Upsert rows based on a composite key of (date, postcode, address, price).
    Adjust `key_cols` as needed for your schema.
    """
    metadata = MetaData()
    table = Table(TARGET_TABLE, metadata, autoload_with=engine)

    rows = df.to_dict(orient="records")
    insert_stmt = insert(table).values(rows)

    # define your composite primary key columns here
    key_cols = ["date", "postcode", "address", "price"]

    # all other columns will be updated on conflict
    update_cols = {
        c.name: insert_stmt.excluded[c.name]
        for c in table.columns
        if c.name not in key_cols
    }

    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=key_cols,
        set_=update_cols
    )

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        session.execute(upsert_stmt)
        session.commit()
        logger.info("Upserted %d rows into %s", len(rows), TARGET_TABLE)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("Upsert failed: %s", e)
        raise
    finally:
        session.close()