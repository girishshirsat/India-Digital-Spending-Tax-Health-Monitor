import pandas as pd
import numpy as np

from src.config import SNAPSHOT_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

CPI_FILE_SNAPSHOT = "cpi_general_combined.csv"
KEEP_COLS = ["year", "month_code", "state", "index"]


def load_cpi():
    cpi = pd.read_csv(SNAPSHOT_DIR / CPI_FILE_SNAPSHOT)
    cpi = cpi[KEEP_COLS].copy()
    logger.info(f"Loaded {len(cpi)} CPI rows")
    return cpi


def to_quarterly(cpi):
    data = cpi.copy()

    data["quarter"] = (data["month_code"] - 1) // 3 + 1

    quarterly = data.groupby(
        ["state", "year", "quarter"], as_index=False
    ).agg(
        cpi_index=("index", "mean"),
        n_months=("index", "count")
    )

    quarterly.loc[quarterly["n_months"] < 2, "cpi_index"] = np.nan

    logger.info(f"Converted CPI data to quarterly: {len(quarterly)} rows")

    return quarterly

if __name__ == "__main__":
    cpi = load_cpi()
    print(cpi.shape)
    print(cpi.columns.tolist())

    quarterly = to_quarterly(cpi)
    print(quarterly.shape)
    print(quarterly["n_months"].value_counts())