"""Operational risk scoring and decision engine."""

from __future__ import annotations

from typing import Any

import pandas as pd


def classify_risk(score: float) -> str:
    """Classify normalized risk score."""
    if score <= 24:
        return "LOW"
    if score <= 49:
        return "MODERATE"
    if score <= 74:
        return "HIGH"
    return "CRITICAL"


def decide_mission_status(
    risk_level: str,
    critical_alerts_count: int,
    warning_alerts_count: int,
) -> str:
    """
    Decide mission status from risk and alert counts.

    Regras NO-GO:
    - >= 3 alertas críticos, ou
    - risk_level CRITICAL com pelo menos 1 alerta crítico.

    risk_level CRITICAL sem alertas críticos degrada para WARNING
    (evita NO-GO apenas por warnings repetidos ou fatores externos).
    """
    if critical_alerts_count >= 3:
        return "NO-GO"

    base_status = {
        "LOW": "GO",
        "MODERATE": "GO WITH CAUTION",
        "HIGH": "WARNING",
        "CRITICAL": "NO-GO",
    }.get(risk_level, "WARNING")

    if base_status == "NO-GO" and critical_alerts_count == 0:
        base_status = "WARNING"

    if warning_alerts_count >= 8 and base_status in {"GO", "GO WITH CAUTION"}:
        return "WARNING"
    return base_status


def _score_space_weather(space_weather_data: dict[str, Any] | None) -> tuple[float, list[str]]:
    if not space_weather_data:
        return 0.0, []
    score = 0.0
    factors: list[str] = []
    for event in space_weather_data.get("events", []):
        class_type = str(event.get("class_type", "")).upper()
        if class_type.startswith("X"):
            score += 12
            factors.append(f"Evento solar severo {class_type}")
        elif class_type.startswith("M"):
            score += 6
            factors.append(f"Evento solar moderado {class_type}")
        elif class_type.startswith("C"):
            score += 2
            factors.append(f"Evento solar leve {class_type}")
    return score, factors


def _score_weather(power_data: dict[str, Any] | None) -> tuple[float, list[str]]:
    if not power_data:
        return 0.0, []
    records = power_data.get("records", [])
    if not records:
        return 0.0, []

    avg_wind = sum(float(r.get("wind_speed_m_s", 0) or 0) for r in records) / len(records)
    avg_rain = sum(float(r.get("precipitation_mm", 0) or 0) for r in records) / len(records)

    score = 0.0
    factors: list[str] = []
    if avg_wind > 8:
        score += 12
        factors.append("Vento médio elevado no local de lançamento")
    elif avg_wind > 6:
        score += 6
        factors.append("Vento moderado no local de lançamento")

    if avg_rain > 3:
        score += 10
        factors.append("Precipitação média elevada")
    elif avg_rain > 1:
        score += 4
        factors.append("Precipitação moderada")

    return score, factors


def calculate_risk_score(
    telemetry_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
    space_weather_data: dict[str, Any] | None = None,
    power_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate normalized risk score and final mission decision."""
    _ = telemetry_df
    if alerts_df is None or alerts_df.empty:
        critical_alerts = warning_alerts = info_alerts = 0
        critical_effective = warning_effective = 0
    else:
        critical_alerts = int((alerts_df["severity"] == "CRITICAL").sum())
        warning_alerts = int((alerts_df["severity"] == "WARNING").sum())
        info_alerts = int((alerts_df["severity"] == "INFO").sum())

        # Diminishing returns por métrica: dezenas de warnings repetidos da mesma métrica
        # não devem explodir o score linearmente.
        if "metric" not in alerts_df.columns:
            alerts_df = alerts_df.copy()
            alerts_df["metric"] = "unknown"
        grouped = alerts_df.groupby(["metric", "severity"]).size()
        critical_effective = 0
        warning_effective = 0
        for metric in alerts_df["metric"].unique():
            c_count = int(grouped.get((metric, "CRITICAL"), 0))
            w_count = int(grouped.get((metric, "WARNING"), 0))
            critical_effective += min(c_count, 3)
            warning_effective += min(w_count, 4)

    sample_count = max(len(telemetry_df), 1) if telemetry_df is not None else 120
    # Volume de amostras: muitas leituras não devem inflar warnings repetidos.
    warning_cap_by_volume = max(6, int(10 + (480 / sample_count)))
    warning_effective = min(warning_effective, warning_cap_by_volume)

    # Pesos: críticos pesam muito mais que warnings (com cap).
    score_alerts = (critical_effective * 35.0) + (warning_effective * 4.0) + (info_alerts * 0.2)

    factors: list[str] = []
    sw_score, sw_factors = _score_space_weather(space_weather_data)
    weather_score, weather_factors = _score_weather(power_data)

    # Fatores externos são secundários vs. alertas operacionais.
    score = score_alerts + sw_score + weather_score
    score = max(0.0, min(100.0, score))

    factors.extend(sw_factors[:3])
    factors.extend(weather_factors[:2])

    if critical_alerts:
        factors.append(f"{critical_alerts} alertas críticos detectados")
    if warning_alerts:
        factors.append(f"{warning_alerts} alertas de atenção")

    if critical_effective == 0 and warning_effective == 0 and not factors:
        factors = ["Operação estável sem fatores críticos relevantes"]

    normalized_score = float(max(0.0, min(100.0, round(score, 2))))
    risk_level = classify_risk(normalized_score)
    mission_status = decide_mission_status(risk_level, critical_alerts, warning_alerts)

    # Defensivo: não deixar score negativo ou NaN
    if normalized_score != normalized_score:  # NaN check
        normalized_score = 0.0

    return {
        "risk_score": normalized_score,
        "risk_level": risk_level,
        "mission_status": mission_status,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "info_alerts": info_alerts,
        "main_risk_factors": factors if factors else ["Sem fatores adicionais"],
    }
