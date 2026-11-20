import pandas as pd

from sqlalchemy import text
from src.db.connection import get_local_engine
from src.config import PROCESSED_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


UPSERT_FACT_UPI_STATE_QUARTER = """
INSERT INTO fact_upi_state_quarter(
    state_id, date_id, total_count, total_amount, big_drop
)
VALUES(
    :state_id, :date_id, :total_count, :total_amount, :big_drop
)
ON CONFLICT (state_id, date_id)
DO UPDATE SET
    total_count = EXCLUDED.total_count,
    total_amount = EXCLUDED.total_amount,
    big_drop = EXCLUDED.big_drop;
"""


def load_fact_upi_state_quarter(conn):

    # Step 1: Read processed parquet
    df = pd.read_parquet(
        PROCESSED_DIR / "phonepe_state_quarter.parquet"
    )

    expected = len(df)

    # Step 2: Fetch state IDs
    states = pd.read_sql(
        text("SELECT state_id, state_name FROM dim_state"),
        conn
    )

    # Step 3: Map state names with state IDs
    df = df.merge(
        states,
        left_on="state",
        right_on="state_name",
        how="left",
        validate="many_to_one"
    )

    # Step 4: Generate date IDs
    df["date_id"] = df["year"] * 10 + df["quarter"]

    # Step 5: Validate row count
    if len(df) != expected:
        raise ValueError(
            f"Row count changed after merge: "
            f"expected {expected}, got {len(df)}"
        )

    # Step 6: Validate state IDs
    
    if df["state_id"].isna().sum() > 0:

        missing_states = df.loc[
            df["state_id"].isna(), "state"
        ].unique().tolist()

        raise ValueError(
            f"Missing state IDs for: {missing_states}"
        )

    logger.info("IDs OK: %s rows", len(df))

    # Step 7: Select required columns
    df = df[
        [
            "state_id",
            "date_id",
            "total_count",
            "total_amount",
            "big_drop"
        ]
    ]

    # Step 8: Convert DataFrame to list of dictionaries
    rows = df.to_dict("records")

    # Step 9: Execute UPSERT
    conn.execute(
        text(UPSERT_FACT_UPI_STATE_QUARTER),
        rows
    )

    # Step 10: Fetch database totals
    result = conn.execute(
        text("""
            SELECT
                COUNT(*),
                SUM(total_amount)
            FROM fact_upi_state_quarter
        """)
    ).one()

    db_count, db_sum = result

    # Step 11: Calculate expected totals
    expected_count = len(df)
    expected_sum = int(df["total_amount"].sum())

    # Step 12: Validate database count
    if db_count != expected_count:
        raise ValueError(
            f"Database count mismatch: "
            f"expected {expected_count}, got {db_count}"
        )

    # Step 13: Validate database sum
    if int(db_sum or 0) != expected_sum:
        raise ValueError(
            f"Database sum mismatch: "
            f"expected {expected_sum}, got {db_sum}"
        )

    # Step 14: Log results
    logger.info(
        "Fact load verified: %s rows, total amount: %s",
        db_count,
        db_sum
    )

    return db_count



def main():
    logger.info("Starting facts load")

    try:
        engine = get_local_engine()

        with engine.begin() as conn:
            load_fact_upi_state_quarter(conn)

    except Exception:
        logger.exception("Failed to load facts")
        raise

    logger.info("Finished facts load")


if __name__ == "__main__":
    main()