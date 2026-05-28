"""NASA DONKI collector with secure key handling and fallback."""

from __future__ import annotations

from datetime import datetime, timedelta

from src.utils.datetime_utils import utc_now, utc_now_iso
from typing import Any

import requests

from src.config import DONKI_FALLBACK_PATH, NASA_API_KEY
from src.logger import setup_logger
from src.utils.file_utils import read_json, write_json

logger = setup_logger(__name__)


def _class_rank(class_type: str | None) -> float:
    """Convert class type (C/M/X) into sortable numeric rank."""
    if not class_type:
        return 0.0
    text = str(class_type).strip().upper()
    if len(text) < 2:
        return 0.0
    prefix = text[0]
    try:
        magnitude = float(text[1:])
    except ValueError:
        return 0.0
    base = {"C": 100.0, "M": 200.0, "X": 300.0}.get(prefix, 0.0)
    return round(base + magnitude, 3)


def _minimal_fallback() -> dict[str, Any]:
    events = [
        {
            "event_id": "FLR-FALLBACK-001",
            "begin_time": "2026-05-20T10:20Z",
            "peak_time": "2026-05-20T10:35Z",
            "class_type": "C2.1",
            "source_location": "N15E20",
            "active_region": "AR-FALLBACK",
        },
        {
            "event_id": "FLR-FALLBACK-002",
            "begin_time": "2026-05-24T03:10Z",
            "peak_time": "2026-05-24T03:24Z",
            "class_type": "M1.4",
            "source_location": "S08W11",
            "active_region": "AR-FALLBACK-2",
        },
    ]
    max_event = max(events, key=lambda e: _class_rank(e.get("class_type")))
    return {
        "source": "NASA_DONKI_FALLBACK",
        "event_count": len(events),
        "max_class_type": max_event.get("class_type"),
        "max_class_rank": _class_rank(max_event.get("class_type")),
        "events": events,
        "fallback_used": True,
        "fallback_reason": "LOCAL_FALLBACK",
        "collected_at": utc_now_iso(),
    }


def _load_or_create_fallback(reason: str) -> dict[str, Any]:
    fallback_data = read_json(DONKI_FALLBACK_PATH)
    if fallback_data and "events" in fallback_data:
        events = fallback_data.get("events", [])
        max_event = max(events, key=lambda e: _class_rank(e.get("class_type")), default={})
        fallback_data["source"] = "NASA_DONKI_FALLBACK"
        fallback_data["event_count"] = len(events)
        fallback_data["max_class_type"] = max_event.get("class_type")
        fallback_data["max_class_rank"] = _class_rank(max_event.get("class_type"))
        fallback_data["fallback_used"] = True
        fallback_data["fallback_reason"] = reason
        fallback_data["collected_at"] = utc_now().isoformat()
        return fallback_data
    fallback_data = _minimal_fallback()
    fallback_data["fallback_reason"] = reason
    write_json(DONKI_FALLBACK_PATH, fallback_data)
    return fallback_data


def fetch_space_weather_events(
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Fetch solar flare events from NASA DONKI with fallback."""
    end_dt = utc_now().date() if end_date is None else datetime.strptime(end_date, "%Y-%m-%d").date()
    start_dt = (end_dt - timedelta(days=13)) if start_date is None else datetime.strptime(start_date, "%Y-%m-%d").date()

    url = "https://api.nasa.gov/DONKI/FLR"
    params = {
        "startDate": start_dt.isoformat(),
        "endDate": end_dt.isoformat(),
        "api_key": NASA_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("DONKI payload inválido")
        events = []
        for event in payload:
            events.append(
                {
                    "event_id": event.get("flrID", "UNKNOWN"),
                    "begin_time": event.get("beginTime"),
                    "peak_time": event.get("peakTime"),
                    "class_type": event.get("classType", "UNKNOWN"),
                    "source_location": event.get("sourceLocation"),
                    "active_region": str(event.get("activeRegionNum", "UNKNOWN")),
                }
            )
        max_event = max(events, key=lambda e: _class_rank(e.get("class_type")), default={})
        return {
            "source": "NASA_DONKI_LIVE",
            "event_count": len(events),
            "max_class_type": max_event.get("class_type"),
            "max_class_rank": _class_rank(max_event.get("class_type")),
            "events": events,
            "fallback_used": False,
            "fallback_reason": None,
            "collected_at": utc_now_iso(),
        }
    except (requests.exceptions.RequestException, ValueError, TypeError, KeyError):
        # Nunca incluir query string com api_key no log.
        logger.warning("NASA DONKI request/payload falhou; usando fallback")
        return _load_or_create_fallback(reason="REQUEST_OR_PAYLOAD_ERROR")
