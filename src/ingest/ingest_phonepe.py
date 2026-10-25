
import json
import time
import requests

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
from src.utils.logger import get_logger, LOG_DIR
from src.utils.helpers import write_manifest


logger = get_logger("ingest_phonepe")


def fetch_json(state, year, quarter):
    """Fetch one PhonePe JSON file. Return data or None on failure."""

    url = PHONEPE_URL.format(
        state=state,
        year=year,
        quarter=quarter,
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

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_WAIT)

    logger.error(f"Failed after {MAX_RETRIES} attempts: {url}")
    return None


def save_json(data, state, year, quarter):
    """Save downloaded JSON data to the raw PhonePe directory."""

    path = PHONEPE_DIR / state / str(year) / f"{quarter}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.debug(f"Saved PhonePe data: {path}")
    return path


def ingest_phonepe(states=STATE_LIST, years=YEARS):
    """Download PhonePe data, skip existing files, and record failures."""

    saved = 0
    skipped_existing = 0
    failed = 0
    failed_urls = []

    for state in states:
        for year in years:
            for quarter in QUARTERS:
                path = PHONEPE_DIR / state / str(year) / f"{quarter}.json"

                if path.exists():
                    skipped_existing += 1
                    continue

                data = fetch_json(state, year, quarter)

                if data is None:
                    failed += 1
                    failed_urls.append(
                        PHONEPE_URL.format(
                            state=state,
                            year=year,
                            quarter=quarter,
                        )
                    )
                    continue

                save_json(data, state, year, quarter)
                saved += 1
                time.sleep(0.2)

    logger.info(
        f"PhonePe done: saved={saved}, "
        f"skipped_existing={skipped_existing}, failed={failed}"
    )

    if failed_urls:
        failed_urls_path = LOG_DIR / "failed_urls.txt"
        failed_urls_path.parent.mkdir(parents=True, exist_ok=True)

        with open(failed_urls_path, "w", encoding="utf-8") as f:
            f.write("\n".join(failed_urls))

        logger.warning(
            f"Wrote {len(failed_urls)} failed URLs to {failed_urls_path}"
        )

    # Preserve the existing manifest date if no new files were downloaded.
    manifest_path = PHONEPE_DIR / "_manifest.json"

    if saved > 0 or not manifest_path.exists():
        file_count = sum(
            1
            for p in PHONEPE_DIR.rglob("*.json")
            if p.name != "_manifest.json"
        )

        write_manifest(
            PHONEPE_DIR,
            "PhonePe Pulse (master)",
            file_count,
        )

        logger.info(f"Manifest updated: {manifest_path}")
    else:
        logger.info("No new files downloaded; existing manifest preserved.")


if __name__ == "__main__":
    ingest_phonepe()
