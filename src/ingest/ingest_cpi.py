from datetime import date

import pandas as pd

from src.config import CPI_DIR, CPI_FILE, SNAPSHOT_DIR
from src.utils.helpers import write_manifest
from src.utils.logger import get_logger

logger = get_logger("ingest_cpi")

SNAPSHOT_FILE = SNAPSHOT_DIR / "cpi_general_combined.csv"
EXPECTED_ROWS = 3813


def ingest_cpi():
    """Filter General/Combined CPI rows from the big Excel into a small CSV."""
    xlsx_path = CPI_DIR / CPI_FILE

    if xlsx_path.exists():
        logger.info("Reading CPI Excel (91 MB, this can take a few minutes)...")
        df = pd.read_excel(xlsx_path, engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()
        logger.info(f"CPI Excel loaded: rows={len(df)}, cols={df.shape[1]}")

        mask = (
            (df["group"] == "General")
            & (df["subgroup"] == "General-Overall")
            & (df["sector"] == "Combined")
        )
        out = df[mask]

        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        out.to_csv(SNAPSHOT_FILE, index=False)

        downloaded_on = date.fromtimestamp(xlsx_path.stat().st_mtime).isoformat()
        write_manifest(CPI_DIR, "MoSPI state CPI (manual download)", len(out), downloaded_on)

    elif SNAPSHOT_FILE.exists():
        logger.warning("CPI Excel not found, using committed snapshot CSV")
        out = pd.read_csv(SNAPSHOT_FILE)

    else:
        logger.error(f"Missing {xlsx_path} and {SNAPSHOT_FILE}. See docs/ for steps.")
        raise FileNotFoundError(xlsx_path)

    logger.info(f"CPI General/Combined rows: {len(out)}")
    if len(out) != EXPECTED_ROWS:
        logger.warning(f"Expected {EXPECTED_ROWS} rows, found {len(out)}")
    return len(out)


if __name__ == "__main__":
    ingest_cpi()