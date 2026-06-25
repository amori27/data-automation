import pandas as pd
from src.core.transformer import clean_column_names, aggregate_sales


def test_clean_column_names():
    df = pd.DataFrame({"First Name ": [1], "  Last Sale " : [2]})
    cleaned = clean_column_names(df)
    assert "first_name" in cleaned.columns
    assert "last_sale" in cleaned.columns


def test_aggregate_sales():
    df = pd.DataFrame({
        "date": ["2026-01-15", "2026-01-20", "2026-02-10"],
        "amount": [100, 200, 300],
        "order_id": [1, 2, 3],
    })
    result = aggregate_sales(df)
    assert len(result) == 2
    assert "total_sales" in result.columns
    assert result["total_sales"].sum() == 600


def test_aggregate_sales_empty():
    df = pd.DataFrame({"date": [], "amount": [], "order_id": []})
    result = aggregate_sales(df)
    assert len(result) == 0
