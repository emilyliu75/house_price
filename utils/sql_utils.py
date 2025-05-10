import logging
from utils.logging_utils import setup_logger
from utils.db_utils import QueryExecutionError

logger = setup_logger(__name__, 'database_query.log', level=logging.DEBUG)


def import_sql_query(filename):
    try:
        with open(filename, 'r') as file:
            imported_query = file.read().replace('\n', ' ').strip()
            logger.info(f"Successfully imported query from {filename}")
            return imported_query
    except FileNotFoundError as e:
        logger.setLevel(logging.ERROR)
        logger.error(f"Failed to import query: {filename} not found")
        raise QueryExecutionError(f"Failed to import query: {e}")