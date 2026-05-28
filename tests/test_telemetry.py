from src.telemetry.simulator import generate_mission_telemetry


REQUIRED_COLUMNS = {
    "timestamp",
    "mission_elapsed_min",
    "phase",
    "battery_percent",
    "oxygen_percent",
    "fuel_percent",
    "cabin_pressure_kpa",
    "cabin_temperature_c",
    "radiation_msv",
    "communication_latency_ms",
    "signal_strength_percent",
    "engine_temperature_c",
    "velocity_m_s",
    "altitude_km",
}


def test_generate_telemetry_shape_and_columns():
    df = generate_mission_telemetry(samples=50, seed=42)
    assert len(df) == 50
    assert REQUIRED_COLUMNS.issubset(df.columns)


def test_generate_telemetry_anomaly_mode_returns_valid_dataframe():
    df = generate_mission_telemetry(samples=50, anomaly_mode=True, seed=7)
    assert len(df) == 50
    assert REQUIRED_COLUMNS.issubset(df.columns)
