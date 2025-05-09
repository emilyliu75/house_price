import pandas as pd
from etl.transform.clean_house_prices import clean_house_prices

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    return clean_house_prices(df)