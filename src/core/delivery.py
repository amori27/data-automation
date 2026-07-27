"""Report delivery via Email and Slack.

Provides SMTP-based email with optional attachments and Slack webhook
notifications.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import httpx
from src.core.config import settings


def send_email(
    recipient: str,
    subject: str,
    body: str,
    attachment: str | None = None,
) -> None:
    """Send an email via SMTP with an optional file attachment.

    Args:
        recipient: Destination email address.
        subject: Email subject line.
        body: Plain-text email body.
        attachment: Optional path to a file to attach.

    Raises:
        ValueError: If SMTP is not configured.
    """
    if not all([settings.smtp_server, settings.smtp_user, settings.smtp_pass]):
        raise ValueError("SMTP not configured")

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment:
        with open(attachment, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={attachment}")
            msg.attach(part)

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)


def send_slack(message: str, webhook: str | None = None) -> None:
    """Post a *message* to Slack via an incoming webhook.

    Args:
        message: Text payload.
        webhook: Override webhook URL (falls back to ``settings.slack_webhook``).

    Raises:
        ValueError: If no webhook URL is available.
    """
    url = webhook or settings.slack_webhook
    if not url:
        raise ValueError("Slack webhook not configured")
    httpx.post(url, json={"text": message})
