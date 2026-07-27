"""Orchestrates the full ETL + report pipeline.

Extracts data from CSV (or SQL), transforms column names and aggregates
monthly sales, generates a styled Excel report, and optionally emails it.
"""

from src.core.extractor import from_csv
from src.core.transformer import clean_column_names, aggregate_sales
from src.core.reporter import generate_excel
from src.core.delivery import send_email


def run_pipeline(csv_path: str, recipient: str | None = None) -> str:
    """Run the end-to-end ETL pipeline.

    Steps:
        1. Read raw CSV into a DataFrame.
        2. Normalise column names.
        3. Aggregate sales by month.
        4. Write a styled Excel report.
        5. Optionally email the report to *recipient*.

    Args:
        csv_path: Path to the source CSV file.
        recipient: Optional email address to send the report to.

    Returns:
        Absolute path of the generated Excel file.
    """
    df = from_csv(csv_path)
    df = clean_column_names(df)
    report = aggregate_sales(df)
    path = generate_excel(report, "monthly_sales")

    if recipient:
        send_email(
            recipient=recipient,
            subject="Monthly Sales Report",
            body="Your automated report is attached.",
            attachment=path,
        )

    return path
