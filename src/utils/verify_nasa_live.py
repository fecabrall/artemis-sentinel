"""Optional manual smoke test for NASA LIVE collectors (not used in pytest)."""

from __future__ import annotations

from src.collectors.nasa_donki import fetch_space_weather_events
from src.collectors.nasa_power import fetch_nasa_power_data
from src.config import nasa_api_key_status


def main() -> None:
    """Run live NASA collectors and print safe summary only."""
    key_status = nasa_api_key_status()
    print(f"NASA_API_KEY configured: {key_status['configured']}")
    print(f"NASA_API_KEY mode: {key_status['mode']}")

    power = fetch_nasa_power_data()
    print(f"POWER source: {power.get('source')}")
    print(f"POWER records_count: {power.get('records_count')}")
    print(f"POWER missing_ratio: {power.get('missing_ratio')}")

    donki = fetch_space_weather_events()
    print(f"DONKI source: {donki.get('source')}")
    print(f"DONKI event_count: {donki.get('event_count')}")
    print(f"DONKI max_class_type: {donki.get('max_class_type')}")


if __name__ == "__main__":
    main()
