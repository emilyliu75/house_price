import os
import pandas as pd
import logging
from sqlalchemy import text, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from etl.config.db_config import load_db_config, DatabaseConfigError
from utils.db_utils import get_db_connection, DatabaseConnectionError
from utils.logging_utils import setup_logger
from utils.sql_utils import import_sql_query
from etl.load.post_load_enrichment import enrich_database

TARGET_TABLE = "clean_house_prices"

# Configure the logger
logger = setup_logger(__name__, "database_query.log", level=logging.INFO)


def load_data(df_clean: pd.DataFrame) -> None:
    """Entry-point called by run_etl.py"""
    conn = None
    try:
        conn = get_db_connection(load_db_config()["target_database"])

        # create table if it doesn't exist
        df_clean.to_sql(TARGET_TABLE, conn, if_exists="fail", index=False)
        logger.info("Table %s created with %d rows", TARGET_TABLE, len(df_clean))

    except ValueError:
        logger.info("Table exists – inserting new rows only (DO NOTHING on conflict)")
        _insert_ignore_duplicates(df_clean, conn)

    except (DatabaseConfigError, DatabaseConnectionError) as e:
        logger.error("DB connection problem: %s", e)
        raise

    finally:
        if conn is not None:
            conn.close()
            logger.info("Database connection closed")

    enrich_database()


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
