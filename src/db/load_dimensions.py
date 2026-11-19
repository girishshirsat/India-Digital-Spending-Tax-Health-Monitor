from sqlalchemy import text

from src.clean.state_utils import build_dim_state
from src.config import YEARS, QUARTERS
from src.db.connection import get_local_engine
from src.utils.logger import get_logger


logger = get_logger(__name__)


UPSERT_DIM_STATE = """
INSERT INTO dim_state (state_id, state_name)
VALUES (:state_id, :state_name)
ON CONFLICT (state_id)
DO UPDATE SET state_name = EXCLUDED.state_name;
"""

UPSERT_DIM_DATE = """
INSERT INTO dim_date (date_id, year, quarter)
VALUES (:date_id, :year, :quarter)
ON CONFLICT (date_id)
DO UPDATE SET
    year = EXCLUDED.year,
    quarter = EXCLUDED.quarter;
"""

UPSERT_DIM_TXN_TYPE = """
INSERT INTO dim_txn_type (txn_type_id, txn_type)
VALUES (:txn_type_id, :txn_type)
ON CONFLICT (txn_type_id)
DO UPDATE SET txn_type = EXCLUDED.txn_type;
"""

UPSERT_DIM_RETURN_TYPE = """
INSERT INTO dim_return_type (return_type_id, return_type)
VALUES (:return_type_id, :return_type)
ON CONFLICT (return_type_id)
DO UPDATE SET return_type = EXCLUDED.return_type;
"""


def load_dim_state(conn):
    df = build_dim_state()
    df = df.rename(columns={"state": "state_name"})
    rows = df.to_dict("records")

    conn.execute(text(UPSERT_DIM_STATE), rows)
    count = conn.execute(
        text("SELECT COUNT(*) FROM dim_state")
    ).scalar()

    logger.info("Loaded dim_state; total rows: %s", count)
    return count


def load_dim_date(conn):
    rows = [
        {
            "date_id": year * 10 + quarter,
            "year": year,
            "quarter": quarter
        }
        for year in YEARS
        for quarter in QUARTERS
    ]

    conn.execute(text(UPSERT_DIM_DATE), rows)
    count = conn.execute(
        text("SELECT COUNT(*) FROM dim_date")
    ).scalar()

    logger.info("Loaded dim_date; total rows: %s", count)
    return count


def load_dim_txn_type(conn):
    rows = [
        {"txn_type_id": 1, "txn_type": "Financial Services"},
        {"txn_type_id": 2, "txn_type": "Merchant payments"},
        {"txn_type_id": 3, "txn_type": "Peer-to-peer payments"},
        {"txn_type_id": 4, "txn_type": "Recharge & bill payments"},
        {"txn_type_id": 5, "txn_type": "Others"}
    ]

    conn.execute(text(UPSERT_DIM_TXN_TYPE), rows)
    count = conn.execute(
        text("SELECT COUNT(*) FROM dim_txn_type")
    ).scalar()

    logger.info("Loaded dim_txn_type; total rows: %s", count)
    return count


def load_dim_return_type(conn):
    rows = [
        {"return_type_id": 1, "return_type": "GSTR-1"},
        {"return_type_id": 2, "return_type": "GSTR-3B"}
    ]

    conn.execute(text(UPSERT_DIM_RETURN_TYPE), rows)
    count = conn.execute(
        text("SELECT COUNT(*) FROM dim_return_type")
    ).scalar()

    logger.info("Loaded dim_return_type; total rows: %s", count)
    return count


def main():
    logger.info("Starting dim load")

    try:
        engine = get_local_engine()

        with engine.begin() as conn:
            load_dim_state(conn)
            load_dim_date(conn)
            load_dim_txn_type(conn)
            load_dim_return_type(conn)

    except Exception:
        logger.exception("Failed to load dimensions")
        raise

    logger.info("Finished dim load")


if __name__ == "__main__":
    main()
