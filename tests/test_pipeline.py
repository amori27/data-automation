from src.core.pipeline import run_pipeline


def test_run_pipeline(tmp_path, monkeypatch):
    csv = tmp_path / "sales.csv"
    csv.write_text("date,amount,order_id\n2026-01-15,100,1\n2026-02-10,200,2")
    monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))

    path = run_pipeline(str(csv))
    assert path is not None
