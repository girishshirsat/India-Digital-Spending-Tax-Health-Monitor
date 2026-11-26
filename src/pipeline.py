
from src.clean.clean_gst import run_gst
from src.clean.clean_phonepe import run_phonepe
from src.clean.clean_cpi import run_cpi

from src.db import create_schema
from src.db import load_dimensions
from src.db import load_facts
from src.db import run_queries

from src.utils.logger import get_logger


logger = get_logger(__name__)


def run_pipeline():

    steps = [
        ("clean phonepe", run_phonepe),
        ("clean gst", run_gst),
        ("clean cpi", run_cpi),
        ("create schema", create_schema.main),
        ("load dimensions", load_dimensions.main),
        ("load facts", load_facts.main),
        ("run queries", run_queries.main),
    ]

    for step_name, function in steps:
        logger.info("Starting step: %s", step_name)

        try:
            function()
            logger.info("Completed step: %s", step_name)

        except Exception:
            logger.exception("Pipeline failed at step: %s", step_name)
            raise


if __name__ == "__main__":
    run_pipeline()
