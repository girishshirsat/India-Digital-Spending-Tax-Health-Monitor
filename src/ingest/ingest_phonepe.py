import requests
import time

from src.utils.logger import get_logger
from src.config import PHONEPE_URL, TIMEOUT, MAX_RETRIES, RETRY_WAIT

logger = get_logger("ingest_phonepe")


def fetch_json(state, year, quarter):
    url = PHONEPE_URL.format(state=state, year=year, quarter=quarter)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                logger.warning(f"Not found, skipped: {state} {year} Q{quarter}")
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

        time.sleep(RETRY_WAIT)

    logger.error(f"Failed after {MAX_RETRIES} attempts: {url}")
    return None


if __name__ == "__main__":
    data = fetch_json("maharashtra", 2024, 4)
    print(type(data), list(data.keys()) if data else None)
    print(fetch_json("maharashtra", 2025, 1))