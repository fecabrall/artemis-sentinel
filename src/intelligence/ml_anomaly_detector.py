"""Local ML anomaly detection for mission telemetry (IsolationForest)."""

from __future__ import annotations

from typing import Any

import numpy as pd

ML_FEATURE_COLUMNS = [
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
]

MODEL_NAME = "IsolationForest"


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    features = df[ML_FEATURE_COLUMNS].copy()
    return features.fillna(features.median(numeric_only=True))


def analyze_telemetry_anomalies(
    telemetry_df: pd.DataFrame,
    contamination: float | None = None,
) -> dict[str, Any]:
    """
    Detect multivariate anomalies in telemetry using local IsolationForest.

    Trains on the provided dataframe (same run). Not orbital prediction — operational ML layer.
    """
    if telemetry_df is None or telemetry_df.empty or len(telemetry_df) < 10:
        return {
            "ml_model_name": MODEL_NAME,
            "ml_source": "LOCAL_ML",
            "ml_anomaly_score": 0.0,
            "ml_anomaly_count": 0,
            "ml_anomaly_ratio": 0.0,
        }

    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        return _statistical_fallback(telemetry_df)

    features = _prepare_features(telemetry_df)
    n = len(features)
    rate = contamination if contamination is not None else (0.12 if n < 80 else 0.08)
    rate = max(0.02, min(0.25, rate))

    model = IsolationForest(
        n_estimators=100,
        contamination=rate,
        random_state=42,
        n_jobs=1,
    )
    model.fit(features.values)
    predictions = model.predict(features.values)
    scores = model.decision_function(features.values)

    anomaly_mask = predictions == -1
    anomaly_count = int(anomaly_mask.sum())
    anomaly_ratio = round(anomaly_count / n, 4)
    mean_score = float(-scores[anomaly_mask].mean()) if anomaly_count else 0.0

    return {
        "ml_model_name": MODEL_NAME,
        "ml_source": "LOCAL_ML",
        "ml_anomaly_score": round(mean_score, 4),
        "ml_anomaly_count": anomaly_count,
        "ml_anomaly_ratio": anomaly_ratio,
    }


def _statistical_fallback(telemetry_df: pd.DataFrame) -> dict[str, Any]:
    """Z-score based fallback when sklearn is unavailable."""
    features = _prepare_features(telemetry_df)
    z = (features - features.mean()) / features.std().replace(0, 1)
    anomaly_mask = (z.abs() > 2.5).any(axis=1)
    anomaly_count = int(anomaly_mask.sum())
    n = len(features)
    return {
        "ml_model_name": "ZScoreFallback",
        "ml_source": "LOCAL_ML",
        "ml_anomaly_score": 0.0,
        "ml_anomaly_count": anomaly_count,
        "ml_anomaly_ratio": round(anomaly_count / max(n, 1), 4),
    }
