"""
Transform raw London house-price data.

Keeps just ten columns:
price_paid, deed_date, postcode, property_type, new_build,
estate_type, saon, paon, street, borough
"""

import pandas as pd
import logging
from utils.logging_utils import setup_logger

# creates a module-level logger named after the module (etl.transform.transform_house_prices)
logger = setup_logger(__name__, "transform_data.log")

# a dictionary that maps raw column names to the cleaned ones
KEEP_AND_RENAME = {
    "price_paid":   "price",
    "deed_date":    "date",
    "postcode":     "postcode",
    "property_type":"property_type",
    "new_build":    "new_build",
    "estate_type":  "estate_type",
    "saon":         "saon",
    "paon":         "paon",
    "street":       "street",
    "borough":      "borough",
    'transaction_category': 'transaction_category',
}

# lookup tables for mapping raw codes to human-readable text
PROP_TYPE_MAP = {
    "F": "Flat",
    "S": "Semi-detached",
    "D": "Detached",
    "T": "Terraced",
    "O": "Other",
}

ESTATE_TYPE_MAP = {
    "L": "Leasehold", "F": "Freehold",
}
MANDATORY = ["price_paid", "deed_date", "postcode"]

def remove_missing(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=MANDATORY)

def select_and_rename(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: c.strip().lower())
    present = df.columns.intersection(KEEP_AND_RENAME)
    missing = set(KEEP_AND_RENAME) - set(present)
    if missing:
        logger.warning("Missing cols: %s", ", ".join(sorted(missing)))
    return (
        df.loc[:, present]
          .rename(columns={c: KEEP_AND_RENAME[c] for c in present})
    )



def standardise_types(df: pd.DataFrame) -> pd.DataFrame:
    # convert price / date to numeric / date for analysis
    # errors="coerce" → non-convertible values (e.g. "—" or "N/A") become NaN instead of raising an exception.
    if "price" in df:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "date" in df:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df


def map_codes(df: pd.DataFrame) -> pd.DataFrame:
    if "property_type" in df:
        df["property_type"] = df["property_type"].map(PROP_TYPE_MAP).fillna(df["property_type"])
    if "estate_type" in df:
        df["estate_type"]   = df["estate_type"].map(ESTATE_TYPE_MAP).fillna(df["estate_type"])
    return df

def remove_other_types(df: pd.DataFrame) -> pd.DataFrame:
    """Drop all rows where property_type == 'Other'."""
    return df[df["property_type"] != "Other"]

def build_address(df: pd.DataFrame) -> pd.DataFrame:
    """Compose saon + paon + street then drop the parts."""
    def make(row):
        raw_parts = [row.get("saon"), row.get("paon"), row.get("street")]
        parts = [str(p).strip() for p in raw_parts if pd.notna(p) and str(p).strip()]
        if not parts:
            return None
        return ", ".join(parts[:-1]) + (" " if len(parts) > 1 else "") + parts[-1]

    df["address"] = df.apply(make, axis=1)
    return df.drop(columns=["saon", "paon", "street"], errors="ignore")


def remove_invalid_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where date could not be parsed (NaT)."""
    return df.dropna(subset=["date"])

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    logger.info("Removed %d duplicate rows", before - len(df))
    return df

def remove_non_standard_transaction(df: pd.DataFrame) -> pd.DataFrame:
     return df[df["transaction_category"] != "B"]

def clean_house_prices(df_raw: pd.DataFrame) -> pd.DataFrame:
    logger.info("▶︎ Cleaning house-price data …")

    df = (
        df_raw
        .pipe(remove_missing)
        .pipe(select_and_rename)
        .pipe(standardise_types)
        .pipe(map_codes)
        .pipe(remove_other_types)
        .pipe(build_address)
        .pipe(remove_invalid_dates)
        .pipe(deduplicate)
        .pipe(remove_non_standard_transaction)
    )

    logger.info("✓ Clean complete - final shape %s", df.shape)
    print("Columns after cleaning:", df.columns.tolist())

    return df