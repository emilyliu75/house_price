"""
Extract raw house-price CSVs for five London boroughs (last five years).
No cleaning here – just load and tag with `borough` column.
"""

from __future__ import annotations
import os
import timeit
import pandas as pd
import logging
from typing import List
from utils.logging_utils import setup_logger, log_extract_success

logger = setup_logger(__name__, "extract_data.log", level=logging.DEBUG)

EXPECTED_PER_ROW  = 0.0001
TYPE_DESCRIPTION  = "HOUSE-PRICE CSVs (raw)"

RAW_FILES = {
    "Brent":        "unclean_brent.csv",
    "Greenwich":    "unclean_greenwich.csv",
    "Hackney":      "unclean_hackney.csv",
    "Wandsworth":   "unclean_wandsworth.csv",
    "Westminster":  "unclean_westminster.csv",
}


def _load_one(borough: str, filename: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "../../data/raw", filename)
    df = pd.read_csv(path)
    df["borough"] = borough         # tag for downstream grouping
    return df


def extract_house_prices() -> pd.DataFrame:
    t0 = timeit.default_timer()

    frames: List[pd.DataFrame] = [
        _load_one(b, f) for b, f in RAW_FILES.items()
    ]
    combined = pd.concat(frames, ignore_index=True)

    log_extract_success(
        logger, TYPE_DESCRIPTION, combined.shape,
        timeit.default_timer() - t0, EXPECTED_PER_ROW
    )
    return combined
