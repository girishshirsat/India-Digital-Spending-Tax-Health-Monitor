from sqlalchemy import text

from src.clean.state_utils import build_dim_state
from src.db.connection import get_local_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)

UPSERT_DIM_STATE = """
INSERT INTO dim_state (state_id, state_name)
VALUES (:state_id, :state_name)
ON CONFLICT (state_id)
DO UPDATE SET state_name = EXCLUDED.state_name;
"""


def load_dim_state(engine):
    df = build_dim_state()
    df = df.rename(columns={"state": "state_name"})
    rows = df.to_dict("records")

    with engine.begin() as conn:
        conn.execute(text(UPSERT_DIM_STATE), rows)
        count = conn.execute(text("SELECT COUNT(*) FROM dim_state")).scalar()

    logger.info("Loaded dim_state; total rows: %s", count)
    return count


def main():
    logger.info("Starting dim_state load")
    try:
        engine = get_local_engine()
        load_dim_state(engine)
    except Exception:
        logger.exception("Failed to load dim_state")
        raise
    logger.info("Finished dim_state load")


if __name__ == "__main__":
    main()
