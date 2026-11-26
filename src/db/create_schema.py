
from sqlalchemy import text

from src.config import SQL_SCHEMA_DIR
from src.db.connection import get_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_sql_file(conn, path):
    sql = path.read_text(encoding="utf-8")
    conn.execute(text(sql))


def main():
    sql_files = [
        SQL_SCHEMA_DIR / "create_tables.sql",
        SQL_SCHEMA_DIR / "create_views.sql",
    ]

    try:
        engine = get_engine()

        with engine.begin() as conn:
            for path in sql_files:
                logger.info("Running %s", path.name)
                run_sql_file(conn, path)

    except Exception:
        logger.exception("Schema creation failed")
        raise

    logger.info("Schema created successfully")


if __name__ == "__main__":
    main()
