import pandas as pd

from src.config import SNAPSHOT_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

CPI_FILE_SNAPSHOT = "cpi_general_combined.csv"
KEEP_COLS = ["year", "month_code", "state", "index"]


def load_cpi():
    cpi = pd.read_csv(SNAPSHOT_DIR / CPI_FILE_SNAPSHOT)
    cpi = cpi[KEEP_COLS].copy()
    logger.info(f"Loaded {len(cpi)} CPI rows")
    return cpi


if __name__ == "__main__":
    cpi = load_cpi()
    print(cpi.shape)
    print(cpi.columns.tolist())