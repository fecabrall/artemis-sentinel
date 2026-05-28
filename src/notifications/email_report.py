"""Optional SMTP email notifications for mission summary."""

from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from src.config import (
    ALERT_EMAIL_TO,
    EMAIL_ENABLED,
    SEND_EXCEL_ATTACHMENT,
    SMTP_APP_PASSWORD,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    mask_sensitive_text,
)
from src.logger import setup_logger

logger = setup_logger(__name__)


def send_mission_email(
    summary: dict[str, Any],
    report_path: str | None = None,
) -> dict[str, str]:
    """
    Send mission summary email if enabled.

    Returns status: skipped | missing_config | sent | failed
    """
    if not EMAIL_ENABLED:
        return {"status": "skipped", "detail": "EMAIL_ENABLED=false"}

    if not SMTP_USER or not SMTP_APP_PASSWORD or not ALERT_EMAIL_TO:
        logger.warning("E-mail não enviado: configuração SMTP incompleta")
        return {"status": "missing_config", "detail": "SMTP credentials or recipient missing"}

    subject = f"ARTEMIS Sentinel — {summary.get('mission_status', 'N/A')} ({summary.get('risk_level', 'N/A')})"
    html = f"""
    <h2>ARTEMIS Sentinel — Resumo da Missão</h2>
    <p><strong>Status:</strong> {summary.get('mission_status')}</p>
    <p><strong>Risco:</strong> {summary.get('risk_level')} (score {summary.get('risk_score')})</p>
    <p><strong>Alertas críticos:</strong> {summary.get('critical_alerts')}</p>
    <p><strong>Alertas de atenção:</strong> {summary.get('warning_alerts')}</p>
    <p><strong>Run ID:</strong> {summary.get('run_id')}</p>
    <p><em>Telemetria simulada — não é predição orbital real.</em></p>
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html", "utf-8"))

    if SEND_EXCEL_ATTACHMENT and report_path and Path(report_path).exists():
        with Path(report_path).open("rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=Path(report_path).name)
        part["Content-Disposition"] = f'attachment; filename="{Path(report_path).name}"'
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_USER, [ALERT_EMAIL_TO], msg.as_string())
        logger.info("E-mail de missão enviado com sucesso")
        return {"status": "sent", "detail": "ok"}
    except Exception as exc:  # noqa: BLE001
        safe_msg = mask_sensitive_text(str(exc))
        logger.warning("Falha ao enviar e-mail: %s", safe_msg)
        return {"status": "failed", "detail": safe_msg}
