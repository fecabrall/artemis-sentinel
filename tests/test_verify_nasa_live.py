"""Tests for optional NASA live verifier (mocked)."""

from __future__ import annotations

from unittest.mock import patch

from src.utils import verify_nasa_live


@patch("src.utils.verify_nasa_live.fetch_nasa_power_data")
@patch("src.utils.verify_nasa_live.fetch_space_weather_events")
def test_verify_main_safe_output(mock_donki, mock_power, capsys):
    mock_power.return_value = {"source": "NASA_POWER_LIVE", "records_count": 5, "missing_ratio": 0.1}
    mock_donki.return_value = {"source": "NASA_DONKI_LIVE", "event_count": 0, "max_class_type": None}
    verify_nasa_live.main()
    out = capsys.readouterr().out
    assert "api_key=" not in out.lower()
    assert "NASA_API_KEY mode:" in out
