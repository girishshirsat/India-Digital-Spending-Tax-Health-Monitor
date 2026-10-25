
import requests
import time
import json

from src.utils.logger import get_logger
from src.config import (
    PHONEPE_URL,
    PHONEPE_DIR,
    STATE_LIST,
    YEARS,
    QUARTERS,
    TIMEOUT,
    MAX_RETRIES,
    RETRY_WAIT,
)

logger = get_logger("ingest_phonepe")


def fetch_json(state, year, quarter):
    """Fetch one PhonePe JSON file. Return data or None on failure."""

    url = PHONEPE_URL.format(
        state=state,
        year=year,
        quarter=quarter
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                logger.warning(
                    f"Not found, skipped: {state} {year} Q{quarter}"
                )
                return None

            logger.warning(
                f"Attempt {attempt}/{MAX_RETRIES} got status "
                f"{response.status_code}: {state} {year} Q{quarter}"
            )

        except requests.RequestException as e:
            logger.warning(
                f"Attempt {attempt}/{MAX_RETRIES} failed: "
                f"{state} {year} Q{quarter} ({e})"
            )

        # Wait only if another attempt remains
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_WAIT)

    logger.error(f"Failed after {MAX_RETRIES} attempts: {url}")
    return None


def save_json(data, state, year, quarter):
    """Save JSON data to the raw PhonePe data directory."""

    path = (
        PHONEPE_DIR
        / state
        / str(year)
        / f"{quarter}.json"
    )

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    logger.debug(f"Saved PhonePe data: {path}")

    return path


def ingest_phonepe(states=STATE_LIST, years=YEARS):
    """Download and save PhonePe files that are not already present."""

    saved = 0
    skipped_existing = 0
    failed = 0
    failed_urls = []

    for state in states:
        for year in years:
            for quarter in QUARTERS:

                path = (
                    PHONEPE_DIR
                    / state
                    / str(year)
                    / f"{quarter}.json"
                )

                # Skip files that have already been downloaded
                if path.exists():
                    skipped_existing += 1
                    continue

                # Download the JSON data
                data = fetch_json(state, year, quarter)

                # Handle failed or missing downloads
                if data is None:
                    failed += 1

                    url = PHONEPE_URL.format(
                        state=state,
                        year=year,
                        quarter=quarter
                    )

                    failed_urls.append(url)

                else:
                    # Save successfully downloaded data
                    save_json(data, state, year, quarter)
                    saved += 1

                    # Brief pause between successful downloads
                    time.sleep(0.2)

    logger.info(
        f"PhonePe done: saved={saved}, "
        f"skipped_existing={skipped_existing}, failed={failed}"
    )


if __name__ == "__main__":
    ingest_phonepe(states=["goa", "ladakh"], years=[2024])
