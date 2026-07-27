"""Data transformation and aggregation.

Provides column-name normalisation and monthly sales aggregation.
"""

import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise DataFrame column names.

    Strips whitespace, lowercases, and replaces spaces with underscores.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with cleaned column names (mutated in place).
    """
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def aggregate_sales(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Aggregate sales data by calendar month.

    Creates a ``month`` period column and computes ``total_sales`` (sum of
    ``amount``) and ``total_orders`` (unique ``order_id`` count).

    Args:
        df: Input DataFrame with at least *date_col*, ``amount``, and ``order_id``.
        date_col: Name of the date column (default ``"date"``).

    Returns:
        One-row-per-month aggregated DataFrame.
    """
    df[date_col] = pd.to_datetime(df[date_col])
    df["month"] = df[date_col].dt.to_period("M")
    return df.groupby("month").agg(
        total_sales=("amount", "sum"),
        total_orders=("order_id", "nunique"),
    ).reset_index()
