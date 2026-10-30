import pandas as pd
from src.config import ROOT, STATE_LIST

def normalize_name(raw):
    row=raw.lower()
    row=row.replace("-"," ")
    row=row.replace("&", "and")
    row=" ".join(row.split())

    return row



def apply_mapping(df, source):
    mapping_path = ROOT / "src" / "clean" / "state_mapping.csv"

    m = pd.read_csv(mapping_path)

    m = m[m["source"] == source]

    mapping = dict(zip(m["clean_name"], m["canonical_state"]))

    df["state"] = df["state"].replace(mapping)

    return df



def build_dim_state():
    states = sorted([normalize_name(s) for s in STATE_LIST])
    sdf = pd.DataFrame({"state_id": range(1, len(states) + 1),"state": states})
    return sdf



if __name__ == "__main__":
    dim = build_dim_state()
    print(dim.shape)
    print(dim.head())
    print(dim["state"].is_unique)