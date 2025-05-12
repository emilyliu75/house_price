# one-off install (development mode)
pip install -e .

# run the pipeline in dev environment
python scripts/run_etl.py dev

# launch the Streamlit dashboard
streamlit run streamlit_app/app.py

# run unit tests against the test DB
ENV=test pytest

# To check database connection:
 for dev: python scripts/test_db_connection.py dev
 for test: python scripts/test_db_connection.py test


# user stories:
As a London first-time buyer, I want to filter the dashboard by borough, property-type so that I can see typical prices for the kind of property I can actually afford.

As a data analyst, I want the ETL pipeline to rerun automatically each month and append only new Land-Registry rows, so that the dashboard always stays current without manual work.

interesting discovery:
there's only one record for outward code N2, which seems a bit weird
It turned out that's from another borough