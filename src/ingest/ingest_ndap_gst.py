from datetime import date

import pandas as pd

from src.config import NDAP_DIR, NDAP_FILE
from src.utils.helpers import write_manifest
from src.utils.logger import get_logger

logger = get_logger("ingest_ndap_gst")

EXPECTED_ROWS = 7828
EXPECTED_COLS = 12


def ingest_ndap_gst():
    """Validate the manually downloaded NDAP GST CSV and record a manifest."""
    path = NDAP_DIR / NDAP_FILE

    if not path.exists():
        logger.error(f"Missing file: {path}. See docs/ for download steps.")
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    rows, cols = df.shape
    logger.info(f"NDAP GST loaded: rows={rows}, cols={cols}")

    if cols != EXPECTED_COLS:
        logger.warning(f"Expected {EXPECTED_COLS} columns, found {cols}")
    if rows != EXPECTED_ROWS:
        logger.warning(f"Expected {EXPECTED_ROWS} rows, found {rows}")

    # Use the file's last-modified date as the download date
    downloaded_on = date.fromtimestamp(path.stat().st_mtime).isoformat()
    write_manifest(
        NDAP_DIR,
        "NDAP GST returns (manual download)",
        rows,
        downloaded_on,
    )
    return rows


if __name__ == "__main__":
    ingest_ndap_gst()