import pandas as pd

from src.intelligence.validators import validate_telemetry_dataframe
from src.intelligence.risk_engine import (
    calculate_risk_score,
    classify_risk,
    decide_mission_status,
)
from src.telemetry.simulator import generate_mission_telemetry


def test_classify_risk_ranges():
    assert classify_risk(10) == "LOW"
    assert classify_risk(30) == "MODERATE"
    assert classify_risk(60) == "HIGH"
    assert classify_risk(90) == "CRITICAL"


def test_high_score_classifies_as_critical():
    telemetry_df = pd.DataFrame([{"dummy": 1}])
    alerts_df = pd.DataFrame(
        [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "WARNING"},
            {"severity": "WARNING"},
        ]
    )
    result = calculate_risk_score(telemetry_df, alerts_df)
    assert result["risk_level"] in {"HIGH", "CRITICAL"}


def test_three_critical_alerts_force_no_go():
    status = decide_mission_status("LOW", critical_alerts_count=3, warning_alerts_count=0)
    assert status == "NO-GO"


def test_critical_risk_without_critical_alerts_not_no_go():
    status = decide_mission_status("CRITICAL", critical_alerts_count=0, warning_alerts_count=20)
    assert status == "WARNING"


def test_critical_risk_with_one_critical_alert_is_no_go():
    status = decide_mission_status("CRITICAL", critical_alerts_count=1, warning_alerts_count=0)
    assert status == "NO-GO"


def test_many_warnings_repeated_nao_devem_causar_critical():
    # 100 warnings da mesma métrica (sem critical) não devem explodir o score.
    alerts_df = pd.DataFrame(
        [{"timestamp": "2026-05-26T12:00:00", "metric": "communication_latency_ms", "severity": "WARNING", "message": "", "value": 4000.0}]
        * 100
    )
    telemetry_df = pd.DataFrame([{"dummy": 1}])
    result = calculate_risk_score(telemetry_df, alerts_df)
    assert 0.0 <= result["risk_score"] <= 100.0
    assert result["risk_level"] in {"LOW", "MODERATE", "HIGH"}
    assert result["mission_status"] != "NO-GO"


def test_muitos_criticos_geram_no_go():
    alerts_df = pd.DataFrame(
        [
            {"timestamp": "t", "metric": "battery_percent", "severity": "CRITICAL", "message": "", "value": 10},
            {"timestamp": "t", "metric": "oxygen_percent", "severity": "CRITICAL", "message": "", "value": 20},
            {"timestamp": "t", "metric": "cabin_pressure_kpa", "severity": "CRITICAL", "message": "", "value": 70},
            {"timestamp": "t", "metric": "radiation_msv", "severity": "CRITICAL", "message": "", "value": 2.0},
        ]
    )
    telemetry_df = pd.DataFrame([{"dummy": 1}])
    result = calculate_risk_score(telemetry_df, alerts_df)
    assert result["critical_alerts"] >= 3
    assert result["mission_status"] == "NO-GO"


def test_anomaly_mode_gera_mais_risco_que_modo_normal():
    normal_df = generate_mission_telemetry(samples=120, anomaly_mode=False, seed=123)
    normal_alerts = validate_telemetry_dataframe(normal_df)
    normal_result = calculate_risk_score(normal_df, normal_alerts)

    anomaly_df = generate_mission_telemetry(samples=120, anomaly_mode=True, seed=123)
    anomaly_alerts = validate_telemetry_dataframe(anomaly_df)
    anomaly_result = calculate_risk_score(anomaly_df, anomaly_alerts)

    assert normal_result["critical_alerts"] == 0
    assert anomaly_result["critical_alerts"] > 0
    assert anomaly_result["risk_score"] >= normal_result["risk_score"]
    assert anomaly_result["mission_status"] == "NO-GO"
    assert normal_result["mission_status"] != "NO-GO"
