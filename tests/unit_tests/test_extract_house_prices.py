import os
import pytest
import pandas as pd
import timeit

from etl.extract.extract_house_prices import (
    _load_one,
    extract_house_prices,
    RAW_FILES,
    TYPE_DESCRIPTION,
    EXPECTED_PER_ROW,
    logger,
)
from utils.logging_utils import log_extract_success

@pytest.fixture
def mock_log_extract_success(mocker):
    return mocker.patch("etl.extract.extract_house_prices.log_extract_success")

@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("etl.extract.extract_house_prices.logger")

def test_log_extract_success_customers(
    mocker,
    mock_log_extract_success,
    mock_logger
):
    mock_execution_time = 0.5
    mock_df = pd.DataFrame({
        'price_paid': [100, 200, 300],
        'deed_date': ['2020-01-01', '2020-02-01', '2020-03-01'],
        'postcode': ['SW1A 1AA', 'SW1A 1AB', 'SW1A 1AC'],
        'property_type': ['F', 'S', 'D'],
        'new_build': ['Y', 'N', 'Y'],
        'estate_type': ['L', 'F', 'L'],
        'saon': ['1', '2', '3'],
        'paon': ['A', 'B', 'C'],
        'street': ['Main St', 'High St', 'Broadway'],
        'borough': ['Brent', 'Greenwich', 'Hackney'],
        'transaction_category': ['A', 'B', 'C'],
    })
    mocker.patch(
        "etl.extract.extract_house_prices.pd.read_csv",
        return_value=mock_df
    )

    # Mock timeit.default_timer to control the execution time
    mock_start_time = 100.0
    mock_end_time = 100.5
    mocker.patch(
        "etl.extract.extract_house_prices.timeit.default_timer",
        side_effect=[mock_start_time, mock_end_time]
    )

    # Call the function
    df = extract_house_prices()

    # Assertions
    mock_log_extract_success.assert_called_once_with(
        mock_logger,
        TYPE_DESCRIPTION,
        df.shape,
        mock_execution_time,
        EXPECTED_PER_ROW
    )

# def test_log_house_prices_error(mocker, mock_logger):
#     # Mock pd.read_csv to raise an exception
#     mocker.patch(
#         "etl.extract.extract_house_prices.pd.read_csv",
#         side_effect=Exception(
#             f"Failed to load CSV file: {FILE_PATH}"
#         )
#     )

#     # Call the function and assert exception
#     with pytest.raises(
#         Exception,
#         match=f"Failed to load CSV file: {FILE_PATH}"
#     ):
#         extract_house_prices()

#     # Verify that the error was logged
#     mock_logger.error.assert_called_once_with(
#          f"Error loading {FILE_PATH}: Failed to load CSV file: {FILE_PATH}"
#     )