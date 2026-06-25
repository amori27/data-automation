import pandas as pd
from src.core.reporter import generate_excel
from pathlib import Path


def test_generate_excel(tmp_path, monkeypatch):
    monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
    df = pd.DataFrame({"month": ["2026-01"], "total": [500]})
    path = generate_excel(df, "test")
    assert Path(path).exists()
    assert Path(path).suffix == ".xlsx"
