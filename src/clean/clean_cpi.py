import pandas as pd
import numpy as np

from src.config import SNAPSHOT_DIR, PROCESSED_DIR
from src.utils.logger import get_logger
from src.clean.state_utils import normalize_name, apply_mapping

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




def merge_territories(q):
    data = q.copy()
    data["state"] = data["state"].apply(normalize_name)
    data = apply_mapping(data, "cpi")

    merged = data.groupby(["state", "year", "quarter"], as_index=False).agg(
        cpi_yoy=("cpi_yoy", "mean"),
        n_months=("n_months", "min"),
    )
    logger.info(f"Merged Dadra and Daman CPI: {len(q)} to {len(merged)} rows")
    return merged



def finish_cpi(m):
    data = m.copy()

    # Keep data from 2018 to 2024
    data = data[data["year"].between(2018, 2024)].copy()

    # Flag negative year-over-year inflation
    data["cpi_yoy_negative"] = data["cpi_yoy"] < 0

    # Match PhonePe column data types
    data["year"] = data["year"].astype("int64")
    data["quarter"] = data["quarter"].astype("int64")

    logger.info(
        f"Finalized CPI data: {len(data)} rows, "
        f"{data['cpi_yoy_negative'].sum()} negative inflation values"
    )

    return data


def save_cpi(df):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / "cpi_state_quarter.parquet"
    df.to_parquet(path, index=False)
    logger.info(f"Saved CPI state-quarter table: {len(df)} rows")


def run_cpi():
    cpi = load_cpi()
    quarterly = to_quarterly(cpi)
    q = add_yoy(quarterly)
    merged = merge_territories(q)
    final = finish_cpi(merged)
    save_cpi(final)
    return final


if __name__ == "__main__":
    run_cpi()