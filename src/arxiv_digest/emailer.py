"""Build an email message and send it via SMTP."""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import Config

log = logging.getLogger(__name__)


def build_message(cfg: Config, subject: str, body: str, attachment_path: str | None = None):
    msg = MIMEMultipart("alternative")
    msg["From"] = cfg.username
    msg["To"] = ", ".join(e.strip() for e in cfg.to_emails.split(","))
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    if attachment_path and os.path.exists(attachment_path):
        basename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=basename)
        part["Content-Disposition"] = f'attachment; filename="{basename}"'
        msg.attach(part)
    return msg


def send(cfg: Config, subject: str, body: str, attachment_path: str | None = None) -> None:
    msg = build_message(cfg, subject, body, attachment_path)
    with smtplib.SMTP(cfg.smtp_server, cfg.smtp_port) as server:
        server.starttls()
        server.login(cfg.username, cfg.password)
        server.send_message(msg)
    log.info("Email sent to %s", cfg.to_emails)