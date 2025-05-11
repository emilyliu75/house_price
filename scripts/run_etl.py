import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.config.env_config import setup_env
from etl.extract.extract import extract_data
from etl.transform.transform import transform_data
from etl.load.load import load_data


def main():
    run_env_setup()

    print("Extracting data...")
    extracted_data = extract_data()
    print("Data extraction complete.")

    # transform
    print("Transforming …")
    tidy_df = transform_data(extracted_data)

    # load
    print("Loading …")
    load_data(tidy_df)

    # finishing
    print(
        f"ETL pipeline run successfully in "
        f'{os.getenv("ENV", "error")} environment!'
    )
def run_env_setup():
    print("Setting up environment...")
    setup_env(sys.argv)
    print("Environment setup complete.")


if __name__ == "__main__":
    main()
