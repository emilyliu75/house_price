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
    "borough":      "borough",   # added in extract step
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


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    logger.info("Removed %d duplicate rows", before - len(df))
    return df


def clean_house_prices(df_raw: pd.DataFrame) -> pd.DataFrame:
    logger.info("▶︎ Cleaning house-price data …")

    df = (
        df_raw
        .pipe(remove_missing)
        .pipe(select_and_rename)
        .pipe(standardise_types)
        .pipe(map_codes)
        .pipe(build_address)
        .pipe(deduplicate)
    )

    logger.info("✓ Clean complete - final shape %s", df.shape)
    return df



# def normalise_headers(df: pd.DataFrame) -> pd.DataFrame:
#     # change all column names to lower case and strip whitespace
#     return df.rename(columns=lambda c: c.strip().lower())

# def _normalise_cols(df: pd.DataFrame) -> pd.DataFrame:
#     # change all column names to lower case and strip whitespace
#     return df.rename(columns=lambda c: c.strip().lower())



# def transform_house_prices(df_raw: pd.DataFrame) -> pd.DataFrame:
#     # so that you can spot when the transform starts.
#     logger.info("▶︎ Transform - keep 10 cols, map codes, de-duplicate")

#     # normalise headers
#     df_raw = _normalise_cols(df_raw)

#     # 1️⃣  select & rename (tolerant of missing columns)

#     # present is the columns that exist in the raw data and in KEEP_AND_RENAME
#     # missing is the columns that are in KEEP_AND_RENAME but not in the raw data
#     present = df_raw.columns.intersection(KEEP_AND_RENAME)
#     missing = set(KEEP_AND_RENAME) - set(present)
#     if missing:
#         logger.warning("Missing cols dropped: %s", ", ".join(sorted(missing)))

#     df = (
#         df_raw
#         .loc[:, present]
#         .rename(columns={c: KEEP_AND_RENAME[c] for c in present})
#     )

#     # 2️⃣  map codes → human text
#     if "property_type" in df:
#         df["property_type"] = df["property_type"].map(PROP_TYPE_MAP).fillna(df["property_type"])
#     if "estate_type" in df:
#         df["estate_type"] = df["estate_type"].map(ESTATE_TYPE_MAP).fillna(df["estate_type"])

#     # 3️⃣  convert price / date to numeric / date for analysis
#     if "price" in df:
#         df["price"] = pd.to_numeric(df["price"], errors="coerce")
#     if "date" in df:
#         df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date


#     # 4️⃣  drop rows lacking mandatory fields
#     df = df.dropna(subset=[c for c in ("price", "date") if c in df.columns])

#     # 5️⃣  de-duplicate considering ONLY the ten kept cols
#     before = len(df)
#     df = df.drop_duplicates()
#     logger.info("Removed %d duplicate rows", before - len(df))
#     logger.info("✓ Transform complete - final shape %s", df.shape)
#     return df