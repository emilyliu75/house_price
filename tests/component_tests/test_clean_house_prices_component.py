import os
import pandas as pd
from etl.transform.clean_house_prices import clean_house_prices


def test_clean_house_prices():
    base_path = os.path.dirname(__file__)
    test_data_path = os.path.join(base_path, '../test_data/test_house_prices.csv')
    expected_data_path = os.path.join(
        base_path,
        '../test_data/expected_house_prices.csv'
    )

    df = pd.read_csv(test_data_path)
    expected_df = pd.read_csv(expected_data_path, parse_dates=['date'])
    expected_df['date'] = expected_df['date'].dt.date

    result = clean_house_prices(df)

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)