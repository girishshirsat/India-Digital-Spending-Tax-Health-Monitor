
import math
import pandas as pd

from sqlalchemy import text

from src.db.connection import get_local_engine
from src.config import PROCESSED_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# SQL: FACT UPI STATE QUARTER
# ============================================================

UPSERT_FACT_UPI_STATE_QUARTER = """
INSERT INTO fact_upi_state_quarter(
    state_id,
    date_id,
    total_count,
    total_amount,
    big_drop
)
VALUES(
    :state_id,
    :date_id,
    :total_count,
    :total_amount,
    :big_drop
)
ON CONFLICT (state_id, date_id)
DO UPDATE SET
    total_count = EXCLUDED.total_count,
    total_amount = EXCLUDED.total_amount,
    big_drop = EXCLUDED.big_drop;
"""




def add_ids(conn, df):

    expected = len(df)

    # Fetch state IDs
    states = pd.read_sql(
        text("SELECT state_id, state_name FROM dim_state"),
        conn
    )

    # Map state names to state IDs
    df = df.merge(
        states,
        left_on="state",
        right_on="state_name",
        how="left",
        validate="many_to_one"
    )

    # Generate date ID
    df["date_id"] = df["year"] * 10 + df["quarter"]

    # Check row count
    if len(df) != expected:
        raise ValueError(
            f"Row count changed after merge: "
            f"expected {expected}, got {len(df)}"
        )

    # Check missing state IDs
    if df["state_id"].isna().sum() > 0:

        missing_states = df.loc[
            df["state_id"].isna(), "state"
        ].unique().tolist()

        raise ValueError(
            f"Missing state IDs for: {missing_states}"
        )

    logger.info("IDs mapped successfully: %s rows", len(df))

    return df




def verify_totals(conn, df, table, column):

    # Fetch database count and sum
    query = text(f"""
        SELECT
            COUNT(*),
            SUM({column})
        FROM {table}
    """)

    result = conn.execute(query).one()

    db_count, db_sum = result

    # Expected values from DataFrame
    expected_count = len(df)
    expected_sum = df[column].sum()

    # Check row count
    if db_count != expected_count:
        raise ValueError(
            f"{table} row count mismatch: "
            f"expected {expected_count}, got {db_count}"
        )

    # Check total sum
    if pd.api.types.is_integer_dtype(df[column].dtype):
        sums_match = int(db_sum or 0) == int(expected_sum)
    else:
        sums_match = (
            db_sum is not None
            and math.isclose(
                float(db_sum),
                float(expected_sum),
                rel_tol=1e-9,
                abs_tol=1e-9
            )
        )

    if not sums_match:
        raise ValueError(
            f"{table} {column} mismatch: "
            f"expected {expected_sum}, got {db_sum}"
        )

    logger.info(
        "%s verified: %s rows, %s = %s",
        table,
        db_count,
        column,
        db_sum
    )

    return db_count




def load_fact_upi_state_quarter(conn):

    # Read processed data
    df = pd.read_parquet(
        PROCESSED_DIR / "phonepe_state_quarter.parquet"
    )

    # Add shared IDs
    df = add_ids(conn, df)

    # Select required table columns
    df = df[
        [
            "state_id",
            "date_id",
            "total_count",
            "total_amount",
            "big_drop"
        ]
    ]

    # Convert DataFrame into records
    rows = df.to_dict("records")

    # Execute UPSERT
    conn.execute(
        text(UPSERT_FACT_UPI_STATE_QUARTER),
        rows
    )

    # Verify database totals
    db_count = verify_totals(
        conn,
        df,
        "fact_upi_state_quarter",
        "total_amount"
    )

    return db_count



def main():

    logger.info("Starting facts load")

    try:
        engine = get_local_engine()

        with engine.begin() as conn:

            db_count = load_fact_upi_state_quarter(conn)

    except Exception:
        logger.exception("Failed to load facts")
        raise

    logger.info(
        "Finished facts load: %s rows",
        db_count
    )


if __name__ == "__main__":
    main()
