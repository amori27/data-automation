"""Data extraction from SQL and CSV sources.

Provides convenience wrappers around pandas for reading data from
local CSV files or a remote SQL database.
"""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from src.core.config import settings


def from_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV file into a DataFrame.

    Args:
        path: Filesystem path to the CSV file.

    Returns:
        pandas DataFrame with the CSV contents.
    """
    return pd.read_csv(path)


def from_sql(query: str) -> pd.DataFrame:
    """Execute a SQL *query* against the configured database.

    Args:
        query: Raw SQL query string.

    Raises:
        ValueError: If ``DB_URL`` is not configured.

    Returns:
        pandas DataFrame with the query results.
    """
    if not settings.db_url:
        raise ValueError("DB_URL not configured")
    engine = create_engine(settings.db_url)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)
