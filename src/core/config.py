"""Application configuration loaded from environment variables."""

import os


class Settings:
    """Pipeline settings with sensible defaults.

    All values can be overridden via environment variables.
    """

    db_url: str | None = os.getenv("DB_URL")
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_pass: str | None = os.getenv("SMTP_PASS")
    slack_webhook: str | None = os.getenv("SLACK_WEBHOOK_URL")
    report_dir: str = os.getenv("REPORT_DIR", "data/reports")


settings = Settings()
