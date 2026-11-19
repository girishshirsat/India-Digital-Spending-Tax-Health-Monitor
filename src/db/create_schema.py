from sqlalchemy import text

from src.config import SQL_SCHEMA_DIR
from src.db.connection import get_local_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_sql_file(engine, path):
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))


def main():
    path = SQL_SCHEMA_DIR / "create_tables.sql"
    logger.info("Running %s", path.name)
    try:
        engine = get_local_engine()
        run_sql_file(engine, path)
    except Exception:
        logger.exception("Schema creation failed")
        raise
    logger.info("Schema created")


if __name__ == "__main__":
    main()