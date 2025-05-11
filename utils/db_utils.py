from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
from utils.logging_utils import setup_logger


class DatabaseConnectionError(Exception):
    pass


class QueryExecutionError(Exception):
    pass


# Configure the logger
logger = setup_logger(__name__, "database.log", level=logging.DEBUG)


def get_db_connection(connection_params):
    try:
        engine = create_db_engine(connection_params)
        connection = engine.connect()
        logger.setLevel(logging.INFO)
        logger.info("Successfully connected to the database.")
        return connection
    except OperationalError as e:
        logger.setLevel(logging.ERROR)
        logger.error(f"Operational error when connecting to the database: {e}")
        raise DatabaseConnectionError(
            f"Operational error when connecting to the database: {e}"
        )
    except SQLAlchemyError as e:
        logger.setLevel(logging.ERROR)
        logger.error(f"Failed to connect to the database: {e}")
        raise DatabaseConnectionError(
            f"Failed to connect to the database: {e}"
        )
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def create_db_engine(connection_params):
    url = f"postgresql://{connection_params['user']}:{connection_params['password']}@{connection_params['host']}:{connection_params['port']}/{connection_params['dbname']}"
    return create_engine(url, echo=False, hide_parameters=True)


