"""Data transformation and aggregation."""

import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def aggregate_sales(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df[date_col] = pd.to_datetime(df[date_col])
    df["month"] = df[date_col].dt.to_period("M")
    return df.groupby("month").agg(
        total_sales=("amount", "sum"),
        total_orders=("order_id", "nunique"),
    ).reset_index()
