"""Reproducibility and risk calibration tests."""

from __future__ import annotations

from src.intelligence.risk_engine import calculate_risk_score
from src.intelligence.validators import validate_telemetry_dataframe
from src.telemetry.simulator import generate_mission_telemetry


def test_normal_with_seed_not_no_go_without_critical():
    df = generate_mission_telemetry(samples=120, anomaly_mode=False, seed=12345)
    alerts = validate_telemetry_dataframe(df)
    risk = calculate_risk_score(df, alerts)
    assert risk["critical_alerts"] == 0
    assert risk["mission_status"] != "NO-GO"


def test_anomaly_with_seed_generates_critical():
    df = generate_mission_telemetry(samples=120, anomaly_mode=True, seed=12345)
    alerts = validate_telemetry_dataframe(df)
    risk = calculate_risk_score(df, alerts)
    assert risk["critical_alerts"] > 0
    assert risk["mission_status"] in {"NO-GO", "WARNING"}


def test_seed_reproducible_telemetry():
    a = generate_mission_telemetry(samples=50, seed=99)
    b = generate_mission_telemetry(samples=50, seed=99)
    assert a.equals(b)
