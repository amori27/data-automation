from src.core.config import settings


def test_defaults():
    assert settings.report_dir == "data/reports"
    assert settings.smtp_port == 587
