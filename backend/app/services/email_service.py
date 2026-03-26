"""Optional SMTP email; logs when not configured (dev-friendly)."""

import logging
import smtplib
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger("uvicorn.error")


def send_email_optional(to_addr: str, subject: str, body: str) -> None:
    """Send plain-text email if SMTP_HOST is set; otherwise log only."""
    settings = get_settings()
    host = getattr(settings, "SMTP_HOST", None) or ""
    if not host:
        logger.info("Email (SMTP not configured): to=%s subject=%s", to_addr, subject)
        return
    port = int(getattr(settings, "SMTP_PORT", 587) or 587)
    user = getattr(settings, "SMTP_USER", None) or ""
    password = getattr(settings, "SMTP_PASSWORD", None) or ""
    from_addr = getattr(settings, "SMTP_FROM", None) or user or "noreply@realstat.local"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    try:
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.sendmail(from_addr, [to_addr], msg.as_string())
    except Exception as exc:
        logger.warning("Email send failed: %s", exc)
