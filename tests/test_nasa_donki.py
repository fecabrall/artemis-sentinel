from __future__ import annotations

from requests.exceptions import HTTPError, RequestException

from src.collectors import nasa_donki


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


def test_donki_live_when_request_succeeds(monkeypatch):
    payload = [
        {"flrID": "1", "beginTime": "t1", "peakTime": "t2", "classType": "C2.1", "sourceLocation": "N10", "activeRegionNum": 100},
        {"flrID": "2", "beginTime": "t3", "peakTime": "t4", "classType": "M1.6", "sourceLocation": "S01", "activeRegionNum": 101},
    ]
    monkeypatch.setattr(nasa_donki.requests, "get", lambda *args, **kwargs: _MockResponse(payload))
    result = nasa_donki.fetch_space_weather_events()
    assert result["source"] == "NASA_DONKI_LIVE"
    assert result["event_count"] == 2
    assert result["max_class_type"] == "M1.6"
    assert result["fallback_used"] is False


def test_donki_fallback_when_request_fails(monkeypatch):
    def _raise(*args, **kwargs):
        raise RequestException("down")

    monkeypatch.setattr(nasa_donki.requests, "get", _raise)
    result = nasa_donki.fetch_space_weather_events()
    assert result["source"] == "NASA_DONKI_FALLBACK"
    assert result["fallback_used"] is True


def test_donki_fallback_when_http_error(monkeypatch):
    monkeypatch.setattr(nasa_donki.requests, "get", lambda *args, **kwargs: _MockResponse({}, should_raise_http=True))
    result = nasa_donki.fetch_space_weather_events()
    assert result["source"] == "NASA_DONKI_FALLBACK"


def test_donki_fallback_when_json_invalid(monkeypatch):
    monkeypatch.setattr(nasa_donki.requests, "get", lambda *args, **kwargs: _MockResponse(ValueError("invalid json")))
    result = nasa_donki.fetch_space_weather_events()
    assert result["source"] == "NASA_DONKI_FALLBACK"


def test_donki_empty_list_is_valid_live(monkeypatch):
    monkeypatch.setattr(nasa_donki.requests, "get", lambda *args, **kwargs: _MockResponse([]))
    result = nasa_donki.fetch_space_weather_events()
    assert result["source"] == "NASA_DONKI_LIVE"
    assert result["event_count"] == 0


def test_donki_class_rank_order():
    assert nasa_donki._class_rank("M1.6") > nasa_donki._class_rank("C2.1")
    assert nasa_donki._class_rank("X1.0") > nasa_donki._class_rank("M9.9")


def test_donki_log_does_not_leak_api_key(monkeypatch, caplog):
    monkeypatch.setattr(nasa_donki, "NASA_API_KEY", "SECRET_KEY_123")

    def _raise(*args, **kwargs):
        raise RequestException("network error")

    monkeypatch.setattr(nasa_donki.requests, "get", _raise)
    _ = nasa_donki.fetch_space_weather_events()
    all_logs = " ".join(rec.getMessage() for rec in caplog.records)
    assert "SECRET_KEY_123" not in all_logs


def test_donki_sends_api_key_in_request_params_without_leak(monkeypatch, caplog):
    sent = {}

    def _capture_get(url, params=None, timeout=None, **kwargs):
        sent["url"] = url
        sent["params"] = params or {}
        sent["timeout"] = timeout
        return _MockResponse([])

    monkeypatch.setattr(nasa_donki, "NASA_API_KEY", "SECRET_KEY_ABC")
    monkeypatch.setattr(nasa_donki.requests, "get", _capture_get)

    result = nasa_donki.fetch_space_weather_events()

    assert sent["url"] == "https://api.nasa.gov/DONKI/FLR"
    assert sent["timeout"] == 15
    assert sent["params"]["api_key"] == "SECRET_KEY_ABC"
    assert "SECRET_KEY_ABC" not in str(result)

    all_logs = " ".join(rec.getMessage() for rec in caplog.records)
    assert "SECRET_KEY_ABC" not in all_logs

