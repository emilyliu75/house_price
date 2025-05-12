import pytest
import pandas as pd
import numpy as np
from datetime import date

from etl.transform.clean_house_prices import remove_missing, select_and_rename, standardise_types, map_codes, remove_other_types, build_address, deduplicate, remove_non_standard_transaction, clean_house_prices

def test_remove_missing():
    df = pd.DataFrame({
        'price_paid': [100000, None, 2000],
        'deed_date': ['2023-01-01', None, '2023-03-01'],
        'postcode': ['SW1A 1AA', 'SW1A 1AB', None],
    })
    result = remove_missing(df)
    assert len(result) == 1
    assert result.iloc[0]['price_paid'] == 100000

def test_select_and_rename():
    raw = pd.DataFrame({
        ' PRICE_PAID ': [123],
        'Deed_Date': ['2022-02-02'],
        'POSTCODE': ['W1'],
        'property_type': ['F'],
        'new_build': ['Y'],
        'estate_type': ['L'],
        'saon': ['1'],
        'paon': ['2'],
        'street': ['Main St'],
        'borough': ['Hackney'],
        'transaction_category': ['A'],
        'non_essential_column': ['X']
    })
    out = select_and_rename(raw)
    expected_cols = [
        'price', 'date', 'postcode', 'property_type', 'new_build',
        'estate_type', 'saon', 'paon', 'street', 'borough',
        'transaction_category'
    ]
    assert list(out.columns) == expected_cols
    assert out.iloc[0]['price'] == 123
    assert out.iloc[0]['transaction_category'] == 'A'

def test_standardise_types():
    df = pd.DataFrame({
        'price': ['100', 'foo'],
        'date': ['2021-03-03', 'not a date'],
    })
    std = standardise_types(df.copy())
    assert std['price'].iloc[0] == 100
    assert pd.isna(std['price'].iloc[1])
    assert std['date'].iloc[0] == date(2021, 3, 3)
    assert pd.isna(std['date'].iloc[1])

def test_map_codes():
    df = pd.DataFrame({
        'property_type': ['F', 'S', 'X'],
        'estate_type': ['L', 'F', 'Z'],
    })
    mapped = map_codes(df.copy())
    assert mapped['property_type'].tolist() == ['Flat', 'Semi-detached', 'X']
    assert mapped['estate_type'].tolist() == ['Leasehold', 'Freehold', 'Z']

def test_remove_other_types():
    df = pd.DataFrame({'property_type': ['Flat', 'Other', 'Detached']})
    cleaned = remove_other_types(df)
    assert 'Other' not in cleaned['property_type'].values
    assert set(cleaned['property_type']) == {'Flat', 'Detached'}

def test_remove_non_standard_transaction():
    df = pd.DataFrame({'transaction_category': ['A', 'B', 'C', None]})
    cleaned = remove_non_standard_transaction(df)
    assert 'B' not in cleaned['transaction_category'].values
    # None rows remain (only B removed)
    assert cleaned['transaction_category'].isna().sum() == 1

def test_build_address():
    df = pd.DataFrame({
        'saon': ['1', None],
        'paon': ['2', ''],
        'street': ['Main St', 'High Rd'],
    })
    out = build_address(df.copy())
    # First row: '1, 2 Main St'
    assert out.iloc[0]['address'] == '1, 2 Main St'
    # Second row: only 'High Rd'
    assert out.iloc[1]['address'] == 'High Rd'
    # saon/paon/street columns removed
    for col in ['saon', 'paon', 'street']:
        assert col not in out.columns

def test_deduplicate():
    df = pd.DataFrame({'a': [1, 1, 2], 'b': [3, 3, 4]})
    out = deduplicate(df)
    assert len(out) == 2

def test_clean_house_prices_pipeline():
    raw = pd.DataFrame({
        'price_paid': ['500', None, '1000'],
        'deed_date': ['2020-01-01', 'not a date', '2020-01-02'],
        'postcode': ['E1', 'E2', 'E3'],
        'property_type': ['F', 'O', 'S'],
        'new_build': ['Y', 'N', 'Y'],
        'estate_type': ['L', 'F', 'L'],
        'saon': ['1', '2', ''],
        'paon': ['a', '', 'b'],
        'street': ['St1', 'St2', ''],
        'borough': ['Br', 'Br', 'Br'],
        'transaction_category': ['A', 'B', 'A'],
    })
    cleaned = clean_house_prices(raw)
    # Only keep rows: non-missing, non-Other, category != B, valid date
    # That leaves only price_paid='500' -> one row
    assert len(cleaned) == 2
    row = cleaned.iloc[0]
    assert row['price'] == 500.0
    assert row['date'] == date(2020, 1, 1)
    assert row['transaction_category'] == 'A'
    assert 'address' in cleaned.columns