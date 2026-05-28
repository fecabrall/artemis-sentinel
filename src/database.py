"""SQLite persistence layer for ARTEMIS Sentinel."""

from __future__ import annotations

import json
import sqlite3
from typing import Any
from uuid import uuid4

import pandas as pd

from src.config import DB_PATH, MISSION_NAME
from src.logger import setup_logger
from src.utils.datetime_utils import utc_now_iso

logger = setup_logger(__name__)


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, col_type: str) -> None:
    cursor.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cursor.fetchall()}
    if column not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def init_db() -> None:
    """Initialize SQLite tables."""
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                timestamp TEXT,
                mission_elapsed_min INTEGER,
                phase TEXT,
                battery_percent REAL,
                oxygen_percent REAL,
                fuel_percent REAL,
                cabin_pressure_kpa REAL,
                cabin_temperature_c REAL,
                radiation_msv REAL,
                communication_latency_ms REAL,
                signal_strength_percent REAL,
                engine_temperature_c REAL,
                velocity_m_s REAL,
                altitude_km REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                timestamp TEXT,
                metric TEXT,
                severity TEXT,
                message TEXT,
                value REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                mission_name TEXT,
                generated_at TEXT,
                risk_score REAL,
                risk_level TEXT,
                mission_status TEXT,
                critical_alerts INTEGER,
                warning_alerts INTEGER,
                info_alerts INTEGER,
                telemetry_samples INTEGER,
                external_power_source TEXT,
                external_donki_source TEXT,
                main_risk_factors_json TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS external_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                record_type TEXT,
                source TEXT,
                payload_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                status TEXT,
                detail TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                level TEXT,
                message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        for column, col_type in [
            ("telemetry_source", "TEXT"),
            ("ml_model_name", "TEXT"),
            ("ml_source", "TEXT"),
            ("ml_anomaly_score", "REAL"),
            ("ml_anomaly_count", "INTEGER"),
            ("ml_anomaly_ratio", "REAL"),
            ("email_status", "TEXT"),
            ("apollo_analysis_mode", "TEXT"),
        ]:
            _ensure_column(cursor, "mission_summary", column, col_type)
        conn.commit()


def new_run_id() -> str:
    return str(uuid4())


def save_telemetry(df: pd.DataFrame, run_id: str) -> None:
    """Persist telemetry rows."""
    created_at = utc_now_iso()
    payload = df.copy()
    payload["run_id"] = run_id
    payload["created_at"] = created_at
    with _connect() as conn:
        payload.to_sql("telemetry", conn, if_exists="append", index=False)


def save_alerts(alerts_df: pd.DataFrame, run_id: str) -> None:
    """Persist alerts rows."""
    if alerts_df.empty:
        return
    created_at = utc_now_iso()
    payload = alerts_df.copy()
    payload["run_id"] = run_id
    payload["created_at"] = created_at
    with _connect() as conn:
        payload.to_sql("alerts", conn, if_exists="append", index=False)


def save_external_data(run_id: str, power_data: dict[str, Any], donki_data: dict[str, Any], apollo: dict[str, Any]) -> None:
    """Persist external sources metadata (no secrets)."""
    created_at = utc_now_iso()
    rows = [
        ("power", power_data.get("source"), power_data),
        ("donki", donki_data.get("source"), donki_data),
        ("apollo", apollo.get("analysis_mode"), apollo),
    ]
    with _connect() as conn:
        for record_type, source, payload in rows:
            conn.execute(
                """
                INSERT INTO external_data (run_id, record_type, source, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, record_type, source, json.dumps(payload, ensure_ascii=True), created_at),
            )
        conn.commit()


def save_email_notification(run_id: str, status: str, detail: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO email_notifications (run_id, status, detail, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, status, detail, utc_now_iso()),
        )
        conn.commit()


def save_mission_summary(summary_dict: dict[str, Any], run_id: str) -> None:
    """Persist mission summary row."""
    payload = {
        "run_id": run_id,
        "mission_name": summary_dict.get("mission_name", MISSION_NAME),
        "generated_at": summary_dict.get("generated_at", utc_now_iso()),
        "risk_score": summary_dict.get("risk_score"),
        "risk_level": summary_dict.get("risk_level"),
        "mission_status": summary_dict.get("mission_status"),
        "critical_alerts": summary_dict.get("critical_alerts"),
        "warning_alerts": summary_dict.get("warning_alerts"),
        "info_alerts": summary_dict.get("info_alerts"),
        "telemetry_samples": summary_dict.get("telemetry_samples"),
        "external_power_source": summary_dict.get("external_power_source"),
        "external_donki_source": summary_dict.get("external_donki_source"),
        "main_risk_factors_json": json.dumps(summary_dict.get("main_risk_factors", []), ensure_ascii=True),
        "telemetry_source": summary_dict.get("telemetry_source"),
        "ml_model_name": summary_dict.get("ml_model_name"),
        "ml_source": summary_dict.get("ml_source"),
        "ml_anomaly_score": summary_dict.get("ml_anomaly_score"),
        "ml_anomaly_count": summary_dict.get("ml_anomaly_count"),
        "ml_anomaly_ratio": summary_dict.get("ml_anomaly_ratio"),
        "email_status": summary_dict.get("email_status"),
        "apollo_analysis_mode": summary_dict.get("apollo_analysis_mode"),
    }
    with _connect() as conn:
        pd.DataFrame([payload]).to_sql("mission_summary", conn, if_exists="append", index=False)


def load_latest_telemetry() -> pd.DataFrame:
    """Load telemetry from latest run_id."""
    with _connect() as conn:
        latest = pd.read_sql_query(
            "SELECT run_id FROM mission_summary ORDER BY id DESC LIMIT 1",
            conn,
        )
        if latest.empty:
            return pd.DataFrame()
        run_id = latest.iloc[0]["run_id"]
        return pd.read_sql_query(
            "SELECT * FROM telemetry WHERE run_id = ? ORDER BY mission_elapsed_min",
            conn,
            params=(run_id,),
        )


def load_latest_alerts() -> pd.DataFrame:
    """Load alerts from latest run."""
    with _connect() as conn:
        latest = pd.read_sql_query(
            "SELECT run_id FROM mission_summary ORDER BY id DESC LIMIT 1",
            conn,
        )
        if latest.empty:
            return pd.DataFrame()
        run_id = latest.iloc[0]["run_id"]
        return pd.read_sql_query(
            "SELECT * FROM alerts WHERE run_id = ? ORDER BY id",
            conn,
            params=(run_id,),
        )


def load_latest_summary() -> pd.DataFrame:
    """Load latest summary row."""
    with _connect() as conn:
        return pd.read_sql_query(
            "SELECT * FROM mission_summary ORDER BY id DESC LIMIT 1",
            conn,
        )
