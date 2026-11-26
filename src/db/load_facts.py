import math

import pandas as pd
from sqlalchemy import text

from src.config import PROCESSED_DIR
from src.db.connection import get_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)


UPSERT_FACT_UPI = """
INSERT INTO fact_upi_state_quarter (
    state_id, date_id, total_count, total_amount, big_drop
)
VALUES (
    :state_id, :date_id, :total_count, :total_amount, :big_drop
)
ON CONFLICT (state_id, date_id)
DO UPDATE SET
    total_count = EXCLUDED.total_count,
    total_amount = EXCLUDED.total_amount,
    big_drop = EXCLUDED.big_drop;
"""

UPSERT_FACT_UPI_TYPE = """
INSERT INTO fact_upi_state_quarter_type (
    state_id, date_id, txn_type_id, txn_count, txn_amount
)
VALUES (
    :state_id, :date_id, :txn_type_id, :txn_count, :txn_amount
)
ON CONFLICT (state_id, date_id, txn_type_id)
DO UPDATE SET
    txn_count = EXCLUDED.txn_count,
    txn_amount = EXCLUDED.txn_amount;
"""

UPSERT_FACT_GST = """
INSERT INTO fact_gst_state_quarter (
    state_id, date_id, return_type_id, eligible, on_time, late,
    total_filed, filing_pct, invalid_negative, suspect_zero_eligible
)
VALUES (
    :state_id, :date_id, :return_type_id, :eligible, :on_time, :late,
    :total_filed, :filing_pct, :invalid_negative, :suspect_zero_eligible
)
ON CONFLICT (state_id, date_id, return_type_id)
DO UPDATE SET
    eligible = EXCLUDED.eligible,
    on_time = EXCLUDED.on_time,
    late = EXCLUDED.late,
    total_filed = EXCLUDED.total_filed,
    filing_pct = EXCLUDED.filing_pct,
    invalid_negative = EXCLUDED.invalid_negative,
    suspect_zero_eligible = EXCLUDED.suspect_zero_eligible;
"""

UPSERT_FACT_CPI = """
INSERT INTO fact_cpi_state_quarter (
    state_id, date_id, cpi_yoy, n_months, cpi_yoy_negative
)
VALUES (
    :state_id, :date_id, :cpi_yoy, :n_months, :cpi_yoy_negative
)
ON CONFLICT (state_id, date_id)
DO UPDATE SET
    cpi_yoy = EXCLUDED.cpi_yoy,
    n_months = EXCLUDED.n_months,
    cpi_yoy_negative = EXCLUDED.cpi_yoy_negative;
"""


def add_ids(conn, df):
    """Add state_id and date_id. Fails if a row is lost, doubled or unmatched."""
    expected = len(df)

    states = pd.read_sql(
        text("SELECT state_id, state_name FROM dim_state"), conn
    )
    df = df.merge(
        states,
        left_on="state",
        right_on="state_name",
        how="left",
        validate="many_to_one",
    )
    df["date_id"] = df["year"] * 10 + df["quarter"]

    if len(df) != expected:
        raise ValueError(
            f"Row count changed after merge: expected {expected}, got {len(df)}"
        )
    if df["state_id"].isna().any():
        missing = df.loc[df["state_id"].isna(), "state"].unique().tolist()
        raise ValueError(f"Missing state IDs for: {missing}")

    return df


def add_lookup_id(conn, df, table, id_col, name_col):
    """Add txn_type_id or return_type_id. Same checks as add_ids."""
    expected = len(df)

    lookup = pd.read_sql(
        text(f"SELECT {id_col}, {name_col} FROM {table}"), conn
    )
    df = df.merge(lookup, on=name_col, how="left", validate="many_to_one")

    if len(df) != expected:
        raise ValueError(
            f"Row count changed after merge: expected {expected}, got {len(df)}"
        )
    if df[id_col].isna().any():
        missing = df.loc[df[id_col].isna(), name_col].unique().tolist()
        raise ValueError(f"Missing {id_col} for: {missing}")

    return df


def to_rows(df):
    # Postgres needs None for a missing value. A float NaN would be stored as
    # a real NaN number, and it would break the filing_pct CHECK.
    return df.astype(object).where(df.notna(), None).to_dict("records")


def verify_totals(conn, df, table, column):
    """Compare row count and sum in the table with the DataFrame."""
    db_count, db_sum = conn.execute(
        text(f"SELECT COUNT(*), SUM({column}) FROM {table}")
    ).one()

    expected_count = len(df)
    expected_sum = df[column].sum()

    if db_count != expected_count:
        raise ValueError(
            f"{table} row count mismatch: expected {expected_count}, got {db_count}"
        )

    if pd.api.types.is_integer_dtype(df[column].dtype):
        sums_match = int(db_sum or 0) == int(expected_sum)
    else:
        # float columns can differ in the last digits
        sums_match = db_sum is not None and math.isclose(
            float(db_sum), float(expected_sum), rel_tol=1e-9, abs_tol=1e-9
        )

    if not sums_match:
        raise ValueError(
            f"{table} {column} mismatch: expected {expected_sum}, got {db_sum}"
        )

    logger.info("%s verified: %s rows, %s = %s", table, db_count, column, db_sum)
    return db_count


def load_fact_upi_state_quarter(conn):
    df = pd.read_parquet(PROCESSED_DIR / "phonepe_state_quarter.parquet")
    df = add_ids(conn, df)
    df = df[["state_id", "date_id", "total_count", "total_amount", "big_drop"]]

    conn.execute(text(UPSERT_FACT_UPI), to_rows(df))
    return verify_totals(conn, df, "fact_upi_state_quarter", "total_amount")


def load_fact_upi_state_quarter_type(conn):
    df = pd.read_parquet(PROCESSED_DIR / "phonepe_by_type.parquet")
    df = df.rename(columns={"count": "txn_count", "amount": "txn_amount"})
    df = add_ids(conn, df)
    df = add_lookup_id(conn, df, "dim_txn_type", "txn_type_id", "txn_type")
    df = df[["state_id", "date_id", "txn_type_id", "txn_count", "txn_amount"]]

    conn.execute(text(UPSERT_FACT_UPI_TYPE), to_rows(df))
    return verify_totals(conn, df, "fact_upi_state_quarter_type", "txn_amount")


def load_fact_gst_state_quarter(conn):
    df = pd.read_parquet(PROCESSED_DIR / "gst_state_quarter.parquet")
    df = add_ids(conn, df)
    df = add_lookup_id(conn, df, "dim_return_type", "return_type_id", "return_type")
    df = df[
        [
            "state_id", "date_id", "return_type_id", "eligible", "on_time",
            "late", "total_filed", "filing_pct", "invalid_negative",
            "suspect_zero_eligible",
        ]
    ].copy()

    # Counts are float64 in parquet because of NULLs. Int64 keeps the NULLs
    # and raises an error if any value is not a whole number.
    count_cols = ["eligible", "on_time", "late", "total_filed"]
    df[count_cols] = df[count_cols].astype("Int64")

    conn.execute(text(UPSERT_FACT_GST), to_rows(df))
    return verify_totals(conn, df, "fact_gst_state_quarter", "total_filed")


def load_fact_cpi_state_quarter(conn):
    df = pd.read_parquet(PROCESSED_DIR / "cpi_state_quarter.parquet")
    df = add_ids(conn, df)
    df = df[["state_id", "date_id", "cpi_yoy", "n_months", "cpi_yoy_negative"]]

    conn.execute(text(UPSERT_FACT_CPI), to_rows(df))
    return verify_totals(conn, df, "fact_cpi_state_quarter", "cpi_yoy")


def check_type_totals_match(conn):
    """The 5 types of a state-quarter must add up to its total."""
    total, by_type = conn.execute(
        text(
            """
            SELECT
                (SELECT SUM(total_amount) FROM fact_upi_state_quarter),
                (SELECT SUM(txn_amount) FROM fact_upi_state_quarter_type)
            """
        )
    ).one()
    if total != by_type:
        raise ValueError(f"UPI totals differ: total={total}, by_type={by_type}")
    logger.info("UPI total and by-type total match: %s", total)


def main():
    logger.info("Starting facts load")
    try:
        engine = get_engine()
        with engine.begin() as conn:  
            counts = {
                "fact_upi_state_quarter": load_fact_upi_state_quarter(conn),
                "fact_upi_state_quarter_type": load_fact_upi_state_quarter_type(conn),
                "fact_gst_state_quarter": load_fact_gst_state_quarter(conn),
                "fact_cpi_state_quarter": load_fact_cpi_state_quarter(conn),
            }
            check_type_totals_match(conn)
    except Exception:
        logger.exception("Failed to load facts")
        raise
    logger.info("Finished facts load: %s", counts)


if __name__ == "__main__":
    main()