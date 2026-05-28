"""Application configuration and path management."""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
FALLBACK_DIR = DATA_DIR / "fallback"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

DB_PATH = DATABASE_DIR / "artemis_sentinel.db"
LOG_FILE_PATH = LOGS_DIR / "artemis_sentinel.log"
POWER_FALLBACK_PATH = FALLBACK_DIR / "nasa_power_fallback.json"
DONKI_FALLBACK_PATH = FALLBACK_DIR / "donki_fallback.json"

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
MISSION_NAME = os.getenv("MISSION_NAME", "ARTEMIS SENTINEL")
DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "28.5721"))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "-80.6480"))

_mission_seed_raw = os.getenv("MISSION_RANDOM_SEED", "").strip()
MISSION_RANDOM_SEED: int | None = int(_mission_seed_raw) if _mission_seed_raw.isdigit() else None

EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() in {"1", "true", "yes"}
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
SEND_EXCEL_ATTACHMENT = os.getenv("SEND_EXCEL_ATTACHMENT", "false").lower() in {"1", "true", "yes"}

_SENSITIVE_PATTERNS = [
    (re.compile(r"(api_key\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(NASA_API_KEY\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(SMTP_APP_PASSWORD\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(password\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(token\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(secret\s*=\s*)([^\s&\"']+)", re.IGNORECASE), r"\1***MASKED***"),
]


def mask_sensitive_text(text: str) -> str:
    """Mask secrets in arbitrary text (logs, URLs, messages)."""
    if not text:
        return text
    masked = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def nasa_api_key_status() -> dict[str, str | bool]:
    """Return safe status about NASA API key configuration (never returns the key)."""
    configured = bool(NASA_API_KEY and NASA_API_KEY != "DEMO_KEY")
    mode = "REAL_CONFIGURED" if configured else "DEMO_KEY_FALLBACK"
    return {"configured": configured, "mode": mode}


def ensure_project_directories() -> None:
    """Create required project directories."""
    for directory in [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        REPORTS_DIR,
        FALLBACK_DIR,
        DATABASE_DIR,
        LOGS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


ensure_project_directories()
