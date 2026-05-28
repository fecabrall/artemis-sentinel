"""NASA POWER collector with robust fallback and sanitization."""

from __future__ import annotations

from datetime import datetime, timedelta

from src.utils.datetime_utils import utc_now, utc_now_iso
from typing import Any

import requests

from src.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, POWER_FALLBACK_PATH
from src.logger import setup_logger
from src.utils.file_utils import read_json, write_json

logger = setup_logger(__name__)


def _minimal_fallback(latitude: float, longitude: float) -> dict[str, Any]:
    today = utc_now().date()
    records = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        records.append(
            {
                "date": day.isoformat(),
                "temperature_c": 25.0 + (i * 0.4),
                "precipitation_mm": round((i % 3) * 0.2, 2),
                "wind_speed_m_s": 4.5 + (i * 0.25),
                "humidity_percent": 68 + i,
                "data_quality": "FALLBACK",
            }
        )
    return {
        "source": "NASA_POWER_FALLBACK",
        "latitude": latitude,
        "longitude": longitude,
        "records": records,
        "records_count": len(records),
        "missing_records": 0,
        "missing_ratio": 0.0,
        "fallback_used": True,
        "fallback_reason": "LOCAL_FALLBACK",
        "collected_at": utc_now_iso(),
    }


def _normalize_power_metric(value: Any) -> float | None:
    """Convert NASA POWER missing values (-999 / -999.0) into None."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None

    # NASA POWER uses -999 to indicate missing/invalid values.
    if abs(f + 999.0) < 1e-6:
        return None
    return f


def _load_or_create_fallback(
    latitude: float,
    longitude: float,
    reason: str,
) -> dict[str, Any]:
    fallback_data = read_json(POWER_FALLBACK_PATH)
    if fallback_data and "records" in fallback_data:
        records = fallback_data.get("records", [])
        for rec in records:
            rec["data_quality"] = "FALLBACK"
        fallback_data["source"] = "NASA_POWER_FALLBACK"
        fallback_data["records_count"] = len(records)
        fallback_data["missing_records"] = 0
        fallback_data["missing_ratio"] = 0.0
        fallback_data["fallback_used"] = True
        fallback_data["fallback_reason"] = reason
        fallback_data["collected_at"] = utc_now().isoformat()
        return fallback_data
    fallback_data = _minimal_fallback(latitude, longitude)
    fallback_data["fallback_reason"] = reason
    write_json(POWER_FALLBACK_PATH, fallback_data)
    return fallback_data


def fetch_nasa_power_data(
    start_date: str | None = None,
    end_date: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict[str, Any]:
    """Fetch daily weather data from NASA POWER API with fallback."""
    lat = latitude if latitude is not None else DEFAULT_LATITUDE
    lon = longitude if longitude is not None else DEFAULT_LONGITUDE

    end_dt = utc_now().date() if end_date is None else datetime.strptime(end_date, "%Y%m%d").date()
    start_dt = (end_dt - timedelta(days=6)) if start_date is None else datetime.strptime(start_date, "%Y%m%d").date()

    params = {
        "parameters": "T2M,PRECTOTCORR,WS2M,RH2M",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_dt.strftime("%Y%m%d"),
        "end": end_dt.strftime("%Y%m%d"),
        "format": "JSON",
    }

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        parameter_data = payload["properties"]["parameter"]
        dates = sorted(parameter_data["T2M"].keys())

        records = []
        for date_key in dates:
            temp = _normalize_power_metric(parameter_data["T2M"].get(date_key))
            precip = _normalize_power_metric(parameter_data["PRECTOTCORR"].get(date_key))
            wind = _normalize_power_metric(parameter_data["WS2M"].get(date_key))
            humidity = _normalize_power_metric(parameter_data["RH2M"].get(date_key))

            missing_fields = [v is None for v in (temp, precip, wind, humidity)]
            if all(missing_fields):
                data_quality = "MISSING"
            elif any(missing_fields):
                data_quality = "PARTIAL"
            else:
                data_quality = "OK"

            records.append(
                {
                    "date": datetime.strptime(date_key, "%Y%m%d").strftime("%Y-%m-%d"),
                    "temperature_c": temp,
                    "precipitation_mm": precip,
                    "wind_speed_m_s": wind,
                    "humidity_percent": humidity,
                    "data_quality": data_quality,
                }
            )

        missing_count = sum(1 for r in records if r.get("data_quality") in {"MISSING", "PARTIAL"})
        missing_ratio = (missing_count / len(records)) if records else 1.0
        if records and (missing_count / len(records)) >= 0.7:
            logger.warning(
                "NASA POWER retornou muitos dados ausentes; usando fallback (%s/%s)",
                missing_count,
                len(records),
            )
            return _load_or_create_fallback(lat, lon, reason="HIGH_MISSING_RATIO")

        return {
            "source": "NASA_POWER_LIVE",
            "latitude": lat,
            "longitude": lon,
            "records": records,
            "records_count": len(records),
            "missing_records": missing_count,
            "missing_ratio": round(missing_ratio, 4),
            "fallback_used": False,
            "fallback_reason": None,
            "collected_at": utc_now_iso(),
        }
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        logger.warning("NASA POWER request/payload falhou; usando fallback")
        return _load_or_create_fallback(lat, lon, reason="REQUEST_OR_PAYLOAD_ERROR")
