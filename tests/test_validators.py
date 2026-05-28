from src.intelligence.validators import validate_telemetry_row


def test_validate_healthy_row_has_few_or_zero_alerts():
    row = {
        "timestamp": "2026-05-26T12:00:00",
        "battery_percent": 92,
        "oxygen_percent": 88,
        "fuel_percent": 85,
        "cabin_pressure_kpa": 101,
        "cabin_temperature_c": 23,
        "radiation_msv": 0.3,
        "communication_latency_ms": 900,
        "signal_strength_percent": 90,
        "engine_temperature_c": 700,
    }
    alerts = validate_telemetry_row(row)
    assert len(alerts) == 0


def test_validate_critical_row_raises_critical_alerts():
    row = {
        "timestamp": "2026-05-26T12:10:00",
        "battery_percent": 12,
        "oxygen_percent": 18,
        "fuel_percent": 5,
        "cabin_pressure_kpa": 70,
        "cabin_temperature_c": 42,
        "radiation_msv": 1.9,
        "communication_latency_ms": 6200,
        "signal_strength_percent": 20,
        "engine_temperature_c": 1105,
    }
    alerts = validate_telemetry_row(row)
    severities = [a["severity"] for a in alerts]
    assert "CRITICAL" in severities
    assert severities.count("CRITICAL") >= 4
