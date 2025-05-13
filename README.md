# template for starting:
https://github.com/de-2502-a/etl-project-demo

# project setup:
- create a virtual venv: python -m venv .venv
- activate the virtual ven: activate .venv/bin/activate
- install the environment: pip install -e .
- create .env.dev and .env.test and fill the database info
- run python scripts/run_etl.py dev to run the pipeline
- run streamlit run streamlit_app/Home.py to start the steamlit visualization


# user stories:
As a London first-time buyer, I want to filter the dashboard by borough, property-type so that I can see typical prices for the kind of property I can actually afford.

As a government officer in relevant department, I want to see how the SDLT holiday has impacted the transcation volumns.

As a data analyst,I want to know how much is the average price sold in each outward code.


# Data source:
https://landregistry.data.gov.uk/app/ppd/?relative_url_root=%2Fapp%2Fppd

# Data cleaning:
Initial records:87,907
Removing null and duplicate values: 87,423
Removing non standard property type record: 81,917
Removing non standard transaction category records: 68,910
Final shape: 68,910, 9

# interesting discovery:
there's only one record for outward code N2, which seems a bit weird
It turned out that's from another borough

deployed on streamlit from the branch deployment:
https://londonhouse.streamlit.app/

reflection:
ETL pipeline to rerun automatically each month and append only new Land-Registry rows, so that the dashboard always stays current without manual work.
How could I deploy or adapt this project into automated cloud environment?