
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

from src.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


def get_local_engine():
    return create_engine(os.getenv("LOCAL_DB_URL"))


def get_neon_engine():
    return create_engine(os.getenv("NEON_DB_URL"))


def get_engine():
    target = os.getenv("DB_TARGET", "local").strip().lower()

    logger.info("DB_TARGET received: %s", target)

    if target == "local":
        return get_local_engine()
    elif target == "neon":
        return get_neon_engine()
    else:
        raise ValueError(
            f"Invalid DB_TARGET: '{target}'. Choose 'local' or 'neon'."
        )
