import sys

from src.ingest.ingest_phonepe import ingest_phonepe
from src.ingest.ingest_ndap_gst import ingest_ndap_gst
from src.ingest.ingest_cpi import ingest_cpi
from src.utils.logger import get_logger

logger = get_logger("run_all")


def main():
    logger.info("Starting Module 1 ingestion")
    try:
        ingest_ndap_gst()   # manual file: fails fast if missing
        ingest_phonepe()    # automated: skips files already downloaded
        ingest_cpi()        # manual file: filters to the small snapshot CSV
    except FileNotFoundError as e:
        logger.error(f"Required file missing: {e}")
        sys.exit(1)
    logger.info("Ingestion finished")


if __name__ == "__main__":
    main()