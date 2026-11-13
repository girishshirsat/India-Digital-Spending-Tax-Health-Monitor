import pandas as pd
import numpy as np

from src.config import NDAP_DIR, NDAP_FILE, PROCESSED_DIR
from src.utils.logger import get_logger
from src.clean.state_utils import normalize_name, apply_mapping


logger=get_logger(__name__)

SHORT_NAMES = ["country", "fyear", "month", "state_code", "state", "return_type", "info","eligible", "on_time", "late", "total_filed", "filing_pct"]



def load_gst():
    gstdata=pd.read_csv(NDAP_DIR/NDAP_FILE)
    
    gstdata = gstdata.rename(columns={
    "Country": "country",
    "Year": "fyear",
    "Month": "month",
    "State Code": "state_code",
    "State": "state",
    "Return Type": "return_type",
    "Additional Info": "info",
    "Number Of Tax Payers Eligible To File (UOM:Number), Scaling Factor:1": "eligible",
    "Number Of Tax Payers Filed By Due Date (UOM:Number), Scaling Factor:1": "on_time",
    "Number Of Tax Payers Filed After Due Date (UOM:Number), Scaling Factor:1": "late",
    "Total Returns Filed (UOM:Number), Scaling Factor:1": "total_filed",
    "Filing Percentage (UOM:%(Percentage)), Scaling Factor:1": "filing_pct", })


    missing = set(SHORT_NAMES) - set(gstdata.columns)
    if missing:
        raise ValueError(f"Columns not renamed: {missing}")



    logger.info(f"Loaded {len(gstdata)} GST rows")
    return gstdata


def clean_states(gstdata):

    df = gstdata.copy()
    initial_rows = len(df)

    df["state"] = df["state"].apply(normalize_name)
    df = apply_mapping(df, source="ndap")

 
    df_clean = df[df["state_code"] != 97].copy()


    dropped_rows = initial_rows - len(df_clean)
    logger.info(f"Dropped {dropped_rows} rows (state_code == 97). Remaining: {len(df_clean)}")

    return df_clean



COUNT_COLS = ["eligible", "on_time", "late", "total_filed"]


def merge_dadra_daman(df):
    before = len(df)
    merged = df.groupby(["state","return_type","month"])[COUNT_COLS].sum(min_count=1).reset_index()
    logger.info(f"length before merge {before}, length after merge {len(merged)}")
    return merged


def to_quarters(df):
    data = df.copy()
    initial_rows = len(data)

    dt = pd.to_datetime(data["month"], format="%B, %Y")
    # data["year"] = dt.dt.year
    # data["quarter"] = dt.dt.quarter

    data["year"] = dt.dt.year.astype("int64")
    data["quarter"] = dt.dt.quarter.astype("int64")

    data = data[data["year"].between(2018, 2024)].copy()
    logger.info(f"Dropped {initial_rows - len(data)} rows outside 2018-2024 window")

    group_cols = ["state", "year", "quarter", "return_type"]
    quarterly = data.groupby(group_cols, as_index=False)[COUNT_COLS].sum(min_count=1)

    assert not quarterly.duplicated(subset=group_cols).any(), "Duplicate quarter rows found"
    logger.info(f"Aggregated to {len(quarterly)} quarterly rows")


    return quarterly



def add_metrics(df):
    data = df.copy()

    
    data["invalid_negative"] = data["on_time"] < 0
    neg_count = int(data["invalid_negative"].sum())

   
    data["suspect_zero_eligible"] = (data["eligible"] == 0) & (data["total_filed"] > 0)
    suspect_count = int(data["suspect_zero_eligible"].sum())

    data.loc[data["invalid_negative"], "on_time"] = np.nan
  
   
    valid_eligible = data["eligible"].where(data["eligible"] != 0)
    data["filing_pct"] = (data["on_time"] / valid_eligible) * 100

   
  
    logger.info(
        f"Flagged {neg_count} invalid_negative rows and {suspect_count} suspect_zero_eligible rows"
    )

    return data


def save_gst(df):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / "gst_state_quarter.parquet"
    df.to_parquet(path, index=False)
    logger.info(f"Saved GST state-quarter table: {len(df)} rows")
   

def run_gst():
    g = load_gst()
    g = clean_states(g)
    g = merge_dadra_daman(g)  
    g = to_quarters(g)       
    g = add_metrics(g)       
    save_gst(g)
    return g


if __name__ == "__main__":
    run_gst()