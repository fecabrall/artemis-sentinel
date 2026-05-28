"""Timezone-aware datetime helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return ISO-8601 UTC timestamp string."""
    return utc_now().isoformat()


def utc_now_compact() -> str:
    """Return compact timestamp for filenames (YYYYMMDD_HHMMSS)."""
    return utc_now().strftime("%Y%m%d_%H%M%S")
