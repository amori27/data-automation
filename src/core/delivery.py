"""Report delivery via Email and Slack."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import httpx
from src.core.config import settings


def send_email(recipient: str, subject: str, body: str, attachment: str | None = None):
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


def send_slack(message: str, webhook: str | None = None):
    url = webhook or settings.slack_webhook
    if not url:
        raise ValueError("Slack webhook not configured")
    httpx.post(url, json={"text": message})
