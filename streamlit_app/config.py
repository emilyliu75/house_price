import os
from dotenv import load_dotenv
from etl.config.db_config import load_db_config
from utils.db_utils import create_db_engine

# Load local environment for dev; in production use Streamlit secrets
load_dotenv(".env.dev", override=False)

# Build and expose a single SQLAlchemy engine for all pages
engine = create_db_engine(load_db_config()["target_database"])