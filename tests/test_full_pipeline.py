"""Comprehensive tests for the data automation pipeline.

Covers every component: extraction, transformation, reporting,
delivery, pipeline orchestration, configuration, and the FastAPI endpoints.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.core.extractor import from_csv, from_sql
from src.core.transformer import clean_column_names, aggregate_sales
from src.core.reporter import generate_excel
from src.core.delivery import send_email, send_slack
from src.core.pipeline import run_pipeline
from src.core.config import Settings, settings
from src.models.schemas import PipelineRequest, PipelineResponse


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class TestExtractor:
    """Tests for CSV and SQL data extraction."""

    def test_from_csv_basic(self, tmp_path: Path) -> None:
        csv = tmp_path / "data.csv"
        csv.write_text("a,b\n1,2\n3,4\n5,6")
        df = from_csv(str(csv))
        assert len(df) == 3
        assert list(df.columns) == ["a", "b"]

    def test_from_csv_single_row(self, tmp_path: Path) -> None:
        csv = tmp_path / "one.csv"
        csv.write_text("x\n99")
        df = from_csv(str(csv))
        assert len(df) == 1
        assert df["x"].iloc[0] == 99

    def test_from_csv_empty(self, tmp_path: Path) -> None:
        csv = tmp_path / "empty.csv"
        csv.write_text("col1,col2\n")
        df = from_csv(str(csv))
        assert len(df) == 0

    def test_from_sql_no_db_url(self) -> None:
        with patch("src.core.extractor.settings") as mock_s:
            mock_s.db_url = None
            with pytest.raises(ValueError, match="DB_URL not configured"):
                from_sql("SELECT 1")


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------

class TestTransformer:
    """Tests for column cleaning and sales aggregation."""

    def test_clean_column_names(self) -> None:
        df = pd.DataFrame({" First Name ": [1], " LAST SALE ": [2]})
        cleaned = clean_column_names(df)
        assert "first_name" in cleaned.columns
        assert "last_sale" in cleaned.columns

    def test_clean_preserves_data(self) -> None:
        df = pd.DataFrame({" Col A": [10, 20]})
        cleaned = clean_column_names(df)
        assert cleaned["col_a"].tolist() == [10, 20]

    def test_aggregate_sales(self) -> None:
        df = pd.DataFrame({
            "date": ["2026-01-15", "2026-01-20", "2026-02-10"],
            "amount": [100, 200, 300],
            "order_id": [1, 2, 3],
        })
        result = aggregate_sales(df)
        assert len(result) == 2
        assert result["total_sales"].sum() == 600
        assert result["total_orders"].sum() == 3

    def test_aggregate_sales_same_month(self) -> None:
        df = pd.DataFrame({
            "date": ["2026-03-01", "2026-03-15", "2026-03-28"],
            "amount": [50, 50, 50],
            "order_id": [1, 1, 2],
        })
        result = aggregate_sales(df)
        assert len(result) == 1
        assert result["total_sales"].iloc[0] == 150
        assert result["total_orders"].iloc[0] == 2  # unique order_ids

    def test_aggregate_sales_empty(self) -> None:
        df = pd.DataFrame({"date": [], "amount": [], "order_id": []})
        result = aggregate_sales(df)
        assert len(result) == 0

    def test_aggregate_custom_date_col(self) -> None:
        df = pd.DataFrame({
            "order_date": ["2026-06-01", "2026-06-05"],
            "amount": [10, 20],
            "order_id": [1, 2],
        })
        result = aggregate_sales(df, date_col="order_date")
        assert len(result) == 1
        assert result["total_sales"].iloc[0] == 30


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class TestReporter:
    """Tests for Excel report generation."""

    def test_generate_excel(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        df = pd.DataFrame({"month": ["2026-01"], "total": [500]})
        path = generate_excel(df, "test")
        assert Path(path).exists()
        assert Path(path).suffix == ".xlsx"

    def test_filename_contains_title(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        df = pd.DataFrame({"col": [1]})
        path = generate_excel(df, "myreport")
        assert "myreport_" in Path(path).name

    def test_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        deep = tmp_path / "a" / "b" / "c"
        monkeypatch.setattr("src.core.config.settings.report_dir", str(deep))
        df = pd.DataFrame({"x": [1]})
        path = generate_excel(df, "deep")
        assert Path(path).exists()

    def test_period_column_stringified(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        df = pd.DataFrame({"month": [pd.Period("2026-01")], "val": [1]})
        path = generate_excel(df, "period")
        assert Path(path).exists()


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------

class TestDelivery:
    """Tests for email and Slack delivery (mocked)."""

    def test_send_email_smtp_not_configured(self) -> None:
        with patch("src.core.delivery.settings") as mock_s:
            mock_s.smtp_server = None
            mock_s.smtp_user = None
            mock_s.smtp_pass = None
            with pytest.raises(ValueError, match="SMTP not configured"):
                send_email("a@b.com", "subj", "body")

    @patch("src.core.delivery.smtplib.SMTP")
    def test_send_email_with_attachment(self, MockSMTP, tmp_path: Path) -> None:
        att = tmp_path / "report.xlsx"
        att.write_bytes(b"fake-xlsx")
        with patch("src.core.delivery.settings") as mock_s:
            mock_s.smtp_server = "smtp.test.com"
            mock_s.smtp_port = 587
            mock_s.smtp_user = "user@test.com"
            mock_s.smtp_pass = "pass"
            mock_s.smtp_port = 587
            ctx = MagicMock()
            MockSMTP.return_value.__enter__ = MagicMock(return_value=ctx)
            MockSMTP.return_value.__exit__ = MagicMock(return_value=False)
            send_email("r@b.com", "Hi", "Body", str(att))
            ctx.send_message.assert_called_once()

    def test_send_slack_no_webhook(self) -> None:
        with patch("src.core.delivery.settings") as mock_s:
            mock_s.slack_webhook = None
            with pytest.raises(ValueError, match="Slack webhook not configured"):
                send_slack("hello")

    @patch("src.core.delivery.httpx.post")
    def test_send_slack_success(self, mock_post) -> None:
        send_slack("test msg", webhook="https://hooks.slack.com/test")
        mock_post.assert_called_once_with(
            "https://hooks.slack.com/test", json={"text": "test msg"}
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class TestPipeline:
    """Integration test for the full ETL pipeline."""

    def test_run_pipeline(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        csv = tmp_path / "sales.csv"
        csv.write_text("date,amount,order_id\n2026-01-15,100,1\n2026-02-10,200,2")
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        path = run_pipeline(str(csv))
        assert path is not None
        assert Path(path).exists()

    def test_run_pipeline_creates_xlsx(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        csv = tmp_path / "data.csv"
        csv.write_text("date,amount,order_id\n2026-03-01,50,1\n2026-03-02,75,2")
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        path = run_pipeline(str(csv))
        assert path.endswith(".xlsx")

    @patch("src.core.pipeline.send_email")
    def test_run_pipeline_with_recipient(self, mock_email, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        csv = tmp_path / "s.csv"
        csv.write_text("date,amount,order_id\n2026-01-01,10,1")
        monkeypatch.setattr("src.core.config.settings.report_dir", str(tmp_path))
        path = run_pipeline(str(csv), recipient="boss@company.com")
        mock_email.assert_called_once()
        assert "boss@company.com" in mock_email.call_args.kwargs["recipient"]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:
    """Verify configuration defaults."""

    def test_report_dir(self) -> None:
        assert settings.report_dir == "data/reports"

    def test_smtp_port(self) -> None:
        assert settings.smtp_port == 587

    def test_smtp_server(self) -> None:
        assert "smtp" in settings.smtp_server

    def test_settings_defaults(self) -> None:
        s = Settings()
        assert s.slack_webhook is None
        assert s.db_url is None


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TestSchemas:
    """Validate Pydantic model construction."""

    def test_pipeline_request(self) -> None:
        req = PipelineRequest(source="csv", source_path="/tmp/data.csv")
        assert req.source == "csv"
        assert req.recipient is None

    def test_pipeline_response(self) -> None:
        resp = PipelineResponse(report_path="/tmp/report.xlsx", rows=100)
        assert resp.rows == 100


# ---------------------------------------------------------------------------
# FastAPI endpoints
# ---------------------------------------------------------------------------

from src.main import app

client = TestClient(app)


class TestFastAPI:
    """Tests for the FastAPI application endpoints."""

    def test_health(self) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @patch("src.main.run_pipeline")
    def test_run_endpoint(self, mock_run) -> None:
        mock_run.return_value = "/tmp/report.xlsx"
        resp = client.post("/run", json={
            "source": "csv",
            "source_path": "/tmp/data.csv",
        })
        assert resp.status_code == 200
        assert resp.json()["report_path"] == "/tmp/report.xlsx"
