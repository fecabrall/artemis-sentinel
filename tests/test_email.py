"""Tests for optional SMTP notifications."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.notifications import email_report


def test_email_disabled_returns_skipped(monkeypatch):
    monkeypatch.setattr(email_report, "EMAIL_ENABLED", False)
    out = email_report.send_mission_email({"mission_status": "NO-GO"})
    assert out["status"] == "skipped"


def test_email_missing_config(monkeypatch):
    monkeypatch.setattr(email_report, "EMAIL_ENABLED", True)
    monkeypatch.setattr(email_report, "SMTP_USER", "")
    out = email_report.send_mission_email({"mission_status": "NO-GO"})
    assert out["status"] == "missing_config"


@patch("src.notifications.email_report.smtplib.SMTP")
def test_email_starttls_and_no_password_in_logs(mock_smtp, monkeypatch, caplog):
    monkeypatch.setattr(email_report, "EMAIL_ENABLED", True)
    monkeypatch.setattr(email_report, "SMTP_USER", "user@example.com")
    monkeypatch.setattr(email_report, "SMTP_APP_PASSWORD", "super-secret")
    monkeypatch.setattr(email_report, "ALERT_EMAIL_TO", "ops@example.com")

    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server

    out = email_report.send_mission_email({"mission_status": "NO-GO", "risk_level": "CRITICAL", "run_id": "r1"})
    assert out["status"] == "sent"
    server.starttls.assert_called_once()
    assert "super-secret" not in caplog.text
