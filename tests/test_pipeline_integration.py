from __future__ import annotations

from src import pipeline


def test_pipeline_runs_with_fallback_without_internet(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "fetch_nasa_power_data",
        lambda: {
            "source": "NASA_POWER_FALLBACK",
            "records": [],
            "records_count": 0,
            "missing_records": 0,
            "missing_ratio": 0.0,
            "fallback_used": True,
            "fallback_reason": "TEST",
        },
    )
    monkeypatch.setattr(
        pipeline,
        "fetch_space_weather_events",
        lambda: {
            "source": "NASA_DONKI_FALLBACK",
            "event_count": 0,
            "max_class_type": None,
            "max_class_rank": 0.0,
            "events": [],
            "fallback_used": True,
            "fallback_reason": "TEST",
        },
    )
    result = pipeline.run_artemis_pipeline(samples=60, anomaly_mode=False)
    assert result["summary"]["external_power_source"] == "NASA_POWER_FALLBACK"
    assert result["summary"]["external_donki_source"] == "NASA_DONKI_FALLBACK"
    assert result["summary"]["mission_status"] != "NO-GO"


def test_pipeline_anomaly_has_higher_or_equal_risk(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "fetch_nasa_power_data",
        lambda: {
            "source": "NASA_POWER_FALLBACK",
            "records": [],
            "records_count": 0,
            "missing_records": 0,
            "missing_ratio": 0.0,
            "fallback_used": True,
            "fallback_reason": "TEST",
        },
    )
    monkeypatch.setattr(
        pipeline,
        "fetch_space_weather_events",
        lambda: {
            "source": "NASA_DONKI_FALLBACK",
            "event_count": 0,
            "max_class_type": None,
            "max_class_rank": 0.0,
            "events": [],
            "fallback_used": True,
            "fallback_reason": "TEST",
        },
    )

    normal = pipeline.run_artemis_pipeline(samples=80, anomaly_mode=False)
    anomaly = pipeline.run_artemis_pipeline(samples=80, anomaly_mode=True)
    assert anomaly["summary"]["risk_score"] >= normal["summary"]["risk_score"]
    assert anomaly["summary"]["critical_alerts"] > 0
    assert anomaly["summary"]["mission_status"] == "NO-GO"

