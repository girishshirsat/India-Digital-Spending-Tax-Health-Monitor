import pandas as pd
from sqlalchemy import text

from src.config import ROOT, SQL_ANALYSIS_DIR
from src.db.connection import get_local_engine
from src.utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = ROOT / "output" / "query_results"


def run_query(conn, path):
    sql = path.read_text(encoding="utf-8")
    df = pd.read_sql(text(sql), conn)
    df.to_csv(OUTPUT_DIR / f"{path.stem}.csv", index=False)
    return len(df)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_local_engine()
    results = {}

    with engine.connect() as conn:
        for path in sorted(SQL_ANALYSIS_DIR.glob("*.sql")):
            if not path.read_text(encoding="utf-8").strip():
                logger.warning("%s is empty, skipped", path.name)
                continue
            try:
                results[path.name] = run_query(conn, path)
            except Exception:
                logger.exception("Query failed: %s", path.name)
                raise
            logger.info("%s: %s rows", path.name, results[path.name])

    logger.info("Ran %s queries", len(results))


if __name__ == "__main__":
    main()