from __future__ import annotations

from requests.exceptions import HTTPError, RequestException

from src.collectors import nasa_power
from src.collectors.nasa_power import _normalize_power_metric


class _MockResponse:
    def __init__(self, payload, should_raise_http: bool = False):
        self._payload = payload
        self._raise_http = should_raise_http

    def raise_for_status(self):
        if self._raise_http:
            raise HTTPError("boom")

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_nasa_power_minus_999_is_none():
    assert _normalize_power_metric(-999) is None
    assert _normalize_power_metric(-999.0) is None
    assert _normalize_power_metric("-999") is None
    assert _normalize_power_metric("-999.00") is None
    assert _normalize_power_metric("") is None


def test_nasa_power_valid_value_is_converted():
    assert _normalize_power_metric(12.5) == 12.5
    assert _normalize_power_metric("3.2") == 3.2


def test_nasa_power_live_when_request_succeeds(monkeypatch):
    payload = {
        "properties": {
            "parameter": {
                "T2M": {"20260520": 25.0},
                "PRECTOTCORR": {"20260520": 0.1},
                "WS2M": {"20260520": 5.0},
                "RH2M": {"20260520": 70},
            }
        }
    }

    monkeypatch.setattr(nasa_power.requests, "get", lambda *args, **kwargs: _MockResponse(payload))
    result = nasa_power.fetch_nasa_power_data()
    assert result["source"] == "NASA_POWER_LIVE"
    assert result["fallback_used"] is False
    assert result["records_count"] == 1


def test_nasa_power_fallback_when_request_fails(monkeypatch):
    def _raise(*args, **kwargs):
        raise RequestException("net down")

    monkeypatch.setattr(nasa_power.requests, "get", _raise)
    result = nasa_power.fetch_nasa_power_data()
    assert result["source"] == "NASA_POWER_FALLBACK"
    assert result["fallback_used"] is True


def test_nasa_power_fallback_when_http_error(monkeypatch):
    monkeypatch.setattr(
        nasa_power.requests,
        "get",
        lambda *args, **kwargs: _MockResponse(payload={}, should_raise_http=True),
    )
    result = nasa_power.fetch_nasa_power_data()
    assert result["source"] == "NASA_POWER_FALLBACK"


def test_nasa_power_fallback_when_json_invalid(monkeypatch):
    monkeypatch.setattr(
        nasa_power.requests,
        "get",
        lambda *args, **kwargs: _MockResponse(payload=ValueError("invalid json")),
    )
    result = nasa_power.fetch_nasa_power_data()
    assert result["source"] == "NASA_POWER_FALLBACK"


def test_nasa_power_fallback_when_missing_ratio_high(monkeypatch):
    payload = {
        "properties": {
            "parameter": {
                "T2M": {"20260520": -999, "20260521": -999},
                "PRECTOTCORR": {"20260520": -999, "20260521": -999},
                "WS2M": {"20260520": -999, "20260521": -999},
                "RH2M": {"20260520": -999, "20260521": -999},
            }
        }
    }
    monkeypatch.setattr(nasa_power.requests, "get", lambda *args, **kwargs: _MockResponse(payload))
    result = nasa_power.fetch_nasa_power_data()
    assert result["source"] == "NASA_POWER_FALLBACK"

