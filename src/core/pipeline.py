"""Orchestrates the full ETL + report pipeline."""

from src.core.extractor import from_csv
from src.core.transformer import clean_column_names, aggregate_sales
from src.core.reporter import generate_excel
from src.core.delivery import send_email


def run_pipeline(csv_path: str, recipient: str | None = None):
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
