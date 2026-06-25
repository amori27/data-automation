"""Excel report generation with openpyxl."""

from pathlib import Path
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from src.core.config import settings


HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def generate_excel(df: pd.DataFrame, title: str = "Report") -> str:
    out_dir = Path(settings.report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"{title}_{ts}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]

    for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for row_idx, row in df.iterrows():
        for col_idx, value in enumerate(row, 1):
            ws.cell(row=row_idx + 2, column=col_idx, value=value)

    wb.save(str(path))
    return str(path)
