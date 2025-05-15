### template for starting:
https://github.com/de-2502-a/etl-project-demo

### Data source: HM Land Registry Open Data
https://landregistry.data.gov.uk/app/ppd/?relative_url_root=%2Fapp%2Fppd
### project setup:
- create a virtual venv: python -m venv .venv
- activate the virtual ven: activate .venv/bin/activate
- install the environment: pip install -e .
- create .env.dev and .env.test and fill the database info
- run python scripts/run_etl.py dev to run the pipeline
- run streamlit run streamlit_app/Home.py to start the steamlit visualization


### Data cleaning:
1. Initial records:87,907
2. Removing null and duplicate values: 87,423
3. Removing non standard property type record: 81,917
4. Removing non standard transaction category records: 68,910

**Final shape: 68,910, 9**

### interesting discovery:
there's only one record for outward code N2, which seems a bit weird
It turned out that's from another borough

### would you go about optimising query execution and performance if the dataset continues to increase?
I added indexes on postcode, date, borough - the columns that I need to use to filter data to optimising the performance.
Creating views so that it can save time on execution.
I used st.cache_data to for caching to eliminate round-trips on every interation

### What error handling and logging have you included in your code and how this could be leveraged?
My utils.logging_utils.setup_logger() is used for logging, so that errors can be easily spotted in the log.
DatabaseConfigError, DatabaseConnectionError
### Are there any security or privacy issues that you need to consider and how would you mitigate them?
Don't commit .env file to git
Put any credentials in a file that won't be committed.
### How this project could be deployed or adapted into an automated cloud environment using the AWS services you have covered?
I could use CloudFormation or Terraform modules for RDS, ESC service.
GitHub Actions to build the Docker image, pushes to ECR, then updates the ECS service.

### user stories:
As a London first-time buyer, I want to filter the dashboard by borough, property-type so that I can see typical prices for the kind of property I can actually afford.

As a government officer in relevant department, I want to see how the SDLT holiday has impacted the transcation volumns.

As a data analyst,I want to know how much is the average price sold in each outward code.
### committing history:
https://github.com/emilyliu75/house_price/commits/main/

### deployed on streamlit from the branch deployment:
https://londonhouse.streamlit.app/

### reflection:
- ETL pipeline to rerun automatically each month and append only new Land-Registry rows, so that the dashboard always stays current without manual work.
- How could I deploy or adapt this project into automated cloud environment?