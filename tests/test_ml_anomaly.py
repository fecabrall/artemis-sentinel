"""Tests for local ML anomaly detector."""

from __future__ import annotations

from src.intelligence.ml_anomaly_detector import analyze_telemetry_anomalies
from src.telemetry.simulator import generate_mission_telemetry


def test_ml_module_returns_fields():
    df = generate_mission_telemetry(samples=80, anomaly_mode=False, seed=42)
    result = analyze_telemetry_anomalies(df)
    assert result["ml_source"] == "LOCAL_ML"
    assert "ml_model_name" in result
    assert "ml_anomaly_score" in result
    assert "ml_anomaly_count" in result
    assert "ml_anomaly_ratio" in result


def test_anomaly_mode_higher_ratio_than_normal():
    normal = analyze_telemetry_anomalies(generate_mission_telemetry(samples=120, anomaly_mode=False, seed=7))
    anomaly = analyze_telemetry_anomalies(
        generate_mission_telemetry(samples=120, anomaly_mode=True, seed=7),
        contamination=0.2,
    )
    assert anomaly["ml_anomaly_ratio"] >= normal["ml_anomaly_ratio"]
