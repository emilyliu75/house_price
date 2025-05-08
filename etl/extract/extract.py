import pandas as pd
from etl.extract.extract_house_prices import extract_house_prices

def extract_data() -> pd.DataFrame:
    return extract_house_prices()