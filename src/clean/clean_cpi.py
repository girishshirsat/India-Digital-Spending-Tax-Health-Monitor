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



def add_yoy(quarterly):
    data = quarterly.copy()

    prev = data.copy()
    prev["year"] = prev["year"] + 1
    prev = prev.rename(columns={"cpi_index": "cpi_prev"})

    q = data.merge(
        prev[["state", "year", "quarter", "cpi_prev"]],
        on=["state", "year", "quarter"],
        how="left"
    )

    q["cpi_yoy"] = np.where(
        q["cpi_prev"] > 0,
        (q["cpi_index"] / q["cpi_prev"] - 1) * 100,
        np.nan
    )

    logger.info(
        f"Calculated YoY inflation: {q['cpi_yoy'].notna().sum()} valid values "
        f"out of {len(q)} rows"
    )

    q = q.drop(columns=["cpi_prev"])

    return q


if __name__ == "__main__":
    cpi = load_cpi()
    print(cpi.shape)
    print(cpi.columns.tolist())

    quarterly = to_quarterly(cpi)
    print(quarterly.shape)
    print(quarterly["n_months"].value_counts())

    q = add_yoy(quarterly)
    print(q.shape)
    print(q["cpi_yoy"].describe())
    print(q["cpi_yoy"].isna().sum())