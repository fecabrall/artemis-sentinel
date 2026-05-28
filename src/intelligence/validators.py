"""Telemetry validation rules."""

from __future__ import annotations

from typing import Any

import pandas as pd


def validate_telemetry_row(row: dict[str, Any] | pd.Series) -> list[dict[str, Any]]:
    """Validate one telemetry row and return alert objects."""
    data = row.to_dict() if isinstance(row, pd.Series) else row
    timestamp = data.get("timestamp")
    alerts: list[dict[str, Any]] = []

    def add_alert(metric: str, severity: str, message: str, value: Any) -> None:
        alerts.append(
            {
                "timestamp": timestamp,
                "metric": metric,
                "severity": severity,
                "message": message,
                "value": value,
            }
        )

    phase = str(data.get("phase", "")).upper()

    def latency_limits_for_phase(telemetry_phase: str) -> tuple[float, float]:
        """Return (warning_threshold, critical_threshold)."""
        if telemetry_phase in {"TRANS_LUNAR_INJECTION"}:
            return 3800.0, 7000.0
        if telemetry_phase in {"CRUISE"}:
            return 3300.0, 6500.0
        if telemetry_phase in {"LUNAR_ORBIT"}:
            return 3500.0, 6700.0
        if telemetry_phase in {"DESCENT"}:
            return 3200.0, 6200.0
        if telemetry_phase in {"LAUNCH"}:
            return 3000.0, 6000.0
        # Default for PRE_LAUNCH and LANDING
        return 2500.0, 5000.0

    # Temperatura/pressão e demais métricas independem da fase
    checks = [
        ("battery_percent", data.get("battery_percent"), [(20, "CRITICAL"), (35, "WARNING")], "baixo"),
        ("oxygen_percent", data.get("oxygen_percent"), [(25, "CRITICAL"), (40, "WARNING")], "baixo"),
        ("fuel_percent", data.get("fuel_percent"), [(10, "CRITICAL"), (25, "WARNING")], "baixo"),
        ("radiation_msv", data.get("radiation_msv"), [(1.5, "CRITICAL"), (0.8, "WARNING")], "alto"),
        ("signal_strength_percent", data.get("signal_strength_percent"), [(35, "CRITICAL"), (55, "WARNING")], "baixo"),
        ("engine_temperature_c", data.get("engine_temperature_c"), [(1000, "CRITICAL"), (850, "WARNING")], "alto"),
    ]

    for metric, value, limits, direction in checks:
        if value is None:
            continue
        critical_limit, warning_limit = limits[0], limits[1]
        if direction == "baixo":
            if value < critical_limit[0]:
                add_alert(metric, critical_limit[1], f"{metric} em nível crítico", value)
            elif value < warning_limit[0]:
                add_alert(metric, warning_limit[1], f"{metric} abaixo do ideal", value)
        else:
            if value > critical_limit[0]:
                add_alert(metric, critical_limit[1], f"{metric} em nível crítico", value)
            elif value > warning_limit[0]:
                add_alert(metric, warning_limit[1], f"{metric} acima do ideal", value)

    # Latência de comunicação depende do regime/fase (espera-se latência maior nas fases distantes)
    latency_value = data.get("communication_latency_ms")
    if latency_value is not None:
        warning_th, critical_th = latency_limits_for_phase(phase)
        if latency_value > critical_th:
            add_alert(
                "communication_latency_ms",
                "CRITICAL",
                f"communication_latency_ms em nível crítico (fase {phase})",
                latency_value,
            )
        elif latency_value > warning_th:
            add_alert(
                "communication_latency_ms",
                "WARNING",
                f"communication_latency_ms acima do ideal (fase {phase})",
                latency_value,
            )

    pressure = data.get("cabin_pressure_kpa")
    if pressure is not None:
        if pressure < 80 or pressure > 120:
            add_alert("cabin_pressure_kpa", "CRITICAL", "Pressão de cabine crítica", pressure)
        elif pressure < 90 or pressure > 110:
            add_alert("cabin_pressure_kpa", "WARNING", "Pressão de cabine fora da faixa ideal", pressure)

    temp = data.get("cabin_temperature_c")
    if temp is not None:
        if temp < 10 or temp > 35:
            add_alert("cabin_temperature_c", "CRITICAL", "Temperatura de cabine crítica", temp)
        elif temp < 18 or temp > 28:
            add_alert("cabin_temperature_c", "WARNING", "Temperatura de cabine fora da faixa ideal", temp)

    return alerts


def validate_telemetry_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate full telemetry DataFrame and return alerts DataFrame."""
    all_alerts: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        all_alerts.extend(validate_telemetry_row(row))
    if not all_alerts:
        return pd.DataFrame(columns=["timestamp", "metric", "severity", "message", "value"])
    return pd.DataFrame(all_alerts)
