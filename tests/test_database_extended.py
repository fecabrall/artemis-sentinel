"""Extended SQLite persistence tests."""

from __future__ import annotations

import sqlite3

from src.database import init_db, new_run_id, save_external_data, save_mission_summary
from src.telemetry.simulator import generate_mission_telemetry


def test_tables_exist(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("src.database.DB_PATH", db_file)
    init_db()
    with sqlite3.connect(db_file) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"telemetry", "alerts", "mission_summary", "external_data", "email_notifications"}.issubset(tables)


def test_external_data_persisted_without_secrets(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("src.database.DB_PATH", db_file)
    init_db()
    run_id = new_run_id()
    power = {"source": "NASA_POWER_FALLBACK", "records_count": 1}
    donki = {"source": "NASA_DONKI_FALLBACK", "event_count": 0}
    apollo = {"analysis_mode": "READ_ONLY_REFERENCE"}
    save_external_data(run_id, power, donki, apollo)
    save_mission_summary({"run_id": run_id, "risk_score": 1.0, "risk_level": "LOW", "mission_status": "GO"}, run_id)
    with sqlite3.connect(db_file) as conn:
        payload = conn.execute("SELECT payload_json FROM external_data WHERE record_type='donki'").fetchone()[0]
    assert "api_key" not in payload.lower()
    assert "NASA_API_KEY" not in payload
