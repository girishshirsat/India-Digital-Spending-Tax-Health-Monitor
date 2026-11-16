import pandas as pd

from src.config import PROCESSED_DIR
from src.clean.state_utils import build_dim_state

FILES = [
    "phonepe_state_quarter.parquet",
    "gst_state_quarter.parquet",
    "cpi_state_quarter.parquet",
]


def load(name):
    return pd.read_parquet(PROCESSED_DIR / name)


def test_no_unmapped_states():
    valid = set(build_dim_state()["state"])
    for name in FILES:
        states = set(load(name)["state"])
        assert states <= valid, f"{name}: unknown states {states - valid}"



def test_one_row_per_key():
    keys = {
        "phonepe_state_quarter.parquet": ["state", "year", "quarter"],
        "cpi_state_quarter.parquet": ["state", "year", "quarter"],
        "gst_state_quarter.parquet": ["state", "year", "quarter", "return_type"],
    }

    for name, key_columns in keys.items():
        df = load(name)

        duplicates = df.duplicated(key_columns).sum()

        assert duplicates == 0, (
            f"{name}: found {duplicates} duplicate rows "
            f"for key columns {key_columns}"
        )