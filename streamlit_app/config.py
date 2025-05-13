# import os
# from dotenv import load_dotenv
# from etl.config.db_config import load_db_config
# from utils.db_utils import create_db_engine

# # Load local environment for dev; in production use Streamlit secrets
# load_dotenv(".env.dev", override=False)

# # Build and expose a single SQLAlchemy engine for all pages
# engine = create_db_engine(load_db_config()["target_database"])

# below is for deployment
import os
import streamlit as st
from dotenv import load_dotenv
from utils.db_utils import create_db_engine

load_dotenv()                              # so it works locally, too

params = {
    "user":     os.environ["SOURCE_DB_USER"],
    "password": os.environ["SOURCE_DB_PASSWORD"],
    "host":     os.environ["SOURCE_DB_HOST"],
    "port":     os.environ.get("SOURCE_DB_PORT", "5432"),
    "dbname":   os.environ["SOURCE_DB_NAME"],
    "schema":   os.environ.get("SOURCE_DB_SCHEMA", "public"),  # crucial
    # you can put extra flags here ↓↓↓
    "sslmode":  "require",
}


@st.cache_resource(show_spinner=False)
def get_engine() -> "sqlalchemy.Engine":
    # db_utils.create_db_engine() ignores unknown keys, so we pop sslmode
    sslmode = params.pop("sslmode", None)
    engine = create_db_engine(params)

    if sslmode:                       # add sslmode after the fact
        engine.url = engine.url.set(query={"sslmode": sslmode,
                                           **engine.url.query})
    return engine


engine = get_engine()