import logging
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from etl.config.db_config import load_db_config
from utils.db_utils import create_db_engine
from utils.logging_utils import setup_logger
from utils.sql_utils import import_sql_query
from pathlib import Path

SQL_DIR = Path(__file__).parents[1] / "sql"

logger = setup_logger(__name__, "database_query.log", level=logging.DEBUG)

TARGET_TABLE = "emily_capstone"


def enrich_database(schema: str = 'public', engine=None):
    engine = create_db_engine(load_db_config()["target_database"])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        _apply_indexes(session)
        _create_views(session)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Post-load enrichment failed: %s", e)
        raise
    finally:
        session.close()


def _apply_indexes(session):
    #  speed up lookups in Streamlit where you filter or group by postcode, date or borough
    index_sql = [
        f'CREATE INDEX IF NOT EXISTS idx_{TARGET_TABLE}_postcode ON {TARGET_TABLE}(postcode);',
        f'CREATE INDEX IF NOT EXISTS idx_{TARGET_TABLE}_date     ON {TARGET_TABLE}(date);',
        f'CREATE INDEX IF NOT EXISTS idx_{TARGET_TABLE}_borough  ON {TARGET_TABLE}(borough);',
    ]
    for sql in index_sql:
        session.execute(text(sql))
        logger.info("Index applied: %s", sql.split('ON')[0].strip())


def _create_views(session):
    #  view 1: average price by outward code
    avg_sql = import_sql_query(SQL_DIR / "v_avg_price_outcode.sql")
    session.execute(text(avg_sql))
    logger.info("View v_avg_price_outcode created / replaced")


    # view 2: repeat‐sale flips within 24 months
    flips_sql = import_sql_query(SQL_DIR / "v_flips_24m.sql")
    session.execute(text(flips_sql))
    logger.info("View v_flips_24m created / replaced")