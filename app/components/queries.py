import pandas as pd
from sqlalchemy import text
from src.db.connection  import get_engine
from src.utils.logger import get_logger

logger=get_logger("_name__")


def get_divergence_scores():
    sql = text("SELECT * FROM vw_divergence_scores")
    df = pd.read_sql(sql, get_engine())
    return df


def get_state_quarter_metrics():
    sql=text("SELECT * FROM vw_state_quarter_metrics")
    df = pd.read_sql(sql, get_engine())
    return df