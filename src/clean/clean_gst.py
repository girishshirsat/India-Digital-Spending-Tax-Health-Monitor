import pandas as pd

from src.config import NDAP_DIR, NDAP_FILE
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


if __name__ == "__main__":
    gstdata = load_gst()
    gstdata_clean = clean_states(gstdata)
    print(gstdata_clean.head())
    print(gstdata_clean.shape)
    print(gstdata_clean["state"].nunique())
    print(gstdata_clean["state"].value_counts().head(3))