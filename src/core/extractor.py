"""Data extraction from SQL and CSV sources."""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from src.core.config import settings


def from_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def from_sql(query: str) -> pd.DataFrame:
    if not settings.db_url:
        raise ValueError("DB_URL not configured")
    engine = create_engine(settings.db_url)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)
