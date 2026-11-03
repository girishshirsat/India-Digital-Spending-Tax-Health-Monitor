import pandas as pd
import json

from src.config import PHONEPE_DIR, STATE_LIST,YEARS, QUARTERS
from src.utils.logger import get_logger
from src.clean.state_utils import normalize_name

logger = get_logger(__name__)

# pd.set_option('display.float_format', lambda num: '%.0f' % num)

def load_one(state, year, quarter):
    path =PHONEPE_DIR/f"{state}/{year}/{quarter}.json"

    with open(path, "r", encoding="utf-8") as f:
        resp =json.load(f)

    rows = []

    for item in resp["data"]["transactionData"]:
        for instrument in item["paymentInstruments"]:
            if instrument["type"]=="TOTAL":
                count=instrument["count"]
                amount=int(instrument["amount"])
                rows.append({"state":state,"year":year,"quarter":quarter,"txn_type":item["name"],"count":count,"amount":amount})

    return pd.DataFrame(rows)



def load_all():
    frames=[]

    for state in STATE_LIST:
        for year in YEARS:
            for quarter in QUARTERS:
                try:
                    frames.append(load_one(state,year,quarter))
                except (FileNotFoundError, KeyError) as e:
                    logger.warning(f"Skipping {state} {year} Q{quarter}: {e}")
    df=pd.concat(frames, ignore_index=True)
    logger.info(f"Loaded {len(df)} rows from PhonePe")


    df["state"] = df["state"].apply(normalize_name)

    return df

def build_totals(df):
    grouped_df=df.groupby(["state","year","quarter"],as_index=False)[["count","amount"]].sum()
    totals_df = grouped_df.rename(columns={
        'count': 'total_count',
        'amount': 'total_amount'
    })

    return totals_df

def check_totals(totals):
    print("nulls:", totals.isna().sum())
    invalid_rows = (
        (totals["total_count"] <= 0) |
        (totals["total_amount"] <= 0)
    ).sum()

    print("zero or negative rows:", invalid_rows) 
    t = totals.sort_values(["state", "year", "quarter"]).copy()

    t["qoq"] = t.groupby("state")["total_amount"].pct_change()

    print("\nBiggest QoQ drops:")
    print(
        t.nsmallest(5, "qoq")[
            ["state", "year", "quarter", "qoq"]
        ]
    )


def flag_drops(totals):
    t = totals.sort_values(
        ["state", "year", "quarter"]
    ).copy()

    t["qoq"] = t.groupby("state")["total_amount"].pct_change()

    t["big_drop"] = t["qoq"] < -0.3

    return t[
        ["state", "year", "quarter", "total_count",
         "total_amount", "big_drop"]
    ]



if __name__ == "__main__":
    df = load_all()
    totals = flag_drops(build_totals(df))
    check_totals(totals)
    print(totals.shape, totals["big_drop"].sum())