from sqlalchemy import create_engine, text
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.env_config import setup_env
from config.db_config import load_db_config, build_db_url


def check_connection():
    config = load_db_config()
    source_url = build_db_url(config['source_database'])

    engine = create_engine(source_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connected to source DB:", result.scalar())


if __name__ == "__main__":
    setup_env(sys.argv)  # Load .env.dev, .env.test, or .env
    check_connection()