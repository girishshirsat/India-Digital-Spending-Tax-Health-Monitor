import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_local_engine():
    return create_engine(os.getenv("LOCAL_DB_URL"))

def get_neon_engine():
    return create_engine(os.getenv("NEON_DB_URL"))