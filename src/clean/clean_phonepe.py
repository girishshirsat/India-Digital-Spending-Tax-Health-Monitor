import pandas as pd
import json

from src.config import PHONEPE_DIR, STATE_LIST,YEARS, QUARTERS
from src.utils.logger import get_logger

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

    return df

def build_totals(df):
    grouped_df=df.groupby(["state","year","quarter"],as_index=False)[["count","amount"]].sum()
    totals_df = grouped_df.rename(columns={
        'count': 'total_count',
        'amount': 'total_amount'
    })

    return totals_df



if __name__ == "__main__":
    df = load_all()
    totals = build_totals(df)
    print(df.shape, totals.shape)
    print(totals.duplicated(["state", "year", "quarter"]).sum())