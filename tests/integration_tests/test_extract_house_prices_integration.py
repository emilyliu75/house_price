import timeit
from etl.extract.extract_house_prices import extract_house_prices, EXPECTED_PER_ROW


def test_extract_house_prices_returns_all_data():
    expected_shape = (87907, 71)
    # Call the function to get the DataFrame
    df = extract_house_prices()

    # Verify the dimensions of the DataFrame
    assert df.shape == expected_shape, (
        f"Expected DataFrame shape to be {expected_shape}, but got {df.shape}"
    )


def test_extract_customers_performance():
    execution_time = timeit.timeit(
        "extract_house_prices()",
        globals=globals(),
        number=1
    )

    # Call the function to get the DataFrame
    df = extract_house_prices()

    # Load time per row
    actual_execution_time_per_row = execution_time / df.shape[0]

    # Assert that the execution time is within an acceptable range
    assert actual_execution_time_per_row <= EXPECTED_PER_ROW, (
        f"Expected execution time to be less than or equal to "
        f"{str(EXPECTED_PER_ROW)} seconds, but got "
        f"{str(actual_execution_time_per_row)} seconds"
    )
