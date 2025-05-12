"""
Extract raw house-price CSVs for five London boroughs (last five years).
"""

import os
import timeit
import pandas as pd
import logging
from typing import List
from utils.logging_utils import setup_logger, log_extract_success


# creates a module-level logger named after the module (etl.extract.extract_house_prices)
logger = setup_logger(__name__, "extract_data.log", level=logging.DEBUG)

# this is a performance budget: 0.0001 s per row. If extraction goes slower, the helper can emit a warning.
EXPECTED_PER_ROW  = 0.0001

#  this is a readable description of the data type
TYPE_DESCRIPTION  = "HOUSE-PRICE CSVs (raw)"

# lookup table, maps borough names to CSV filenames
RAW_FILES = {
    "Brent":        "unclean_brent.csv",
    "Greenwich":    "unclean_greenwich.csv",
    "Hackney":      "unclean_hackney.csv",
    "Wandsworth":   "unclean_wandsworth.csv",
    "Westminster":  "unclean_westminster.csv",
}

# signalling 'private/internal'. Avoids accidental import such as `from extract import *` (wildcards skip names that start with `_`)
def _load_one(borough: str, filename: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "../../data/raw", filename)
    df = pd.read_csv(path)
    df["borough"] = borough         # tag for downstream grouping
    return df


def extract_house_prices() -> pd.DataFrame:
    try:
        start_time = timeit.default_timer()

        frames: List[pd.DataFrame] = [
            _load_one(b, f) for b, f in RAW_FILES.items()
        ]
        combined = pd.concat(frames, ignore_index=True)
        extract_execution_time = timeit.default_timer() - start_time
        log_extract_success(
            logger, TYPE_DESCRIPTION, combined.shape,
            extract_execution_time, EXPECTED_PER_ROW
        )
        return combined
    except Exception as e:
        logger.setLevel(logging.ERROR)
        logger.error(f"Error to extract data: {e}")
        raise Exception(f"Error to extract data: {e}")
