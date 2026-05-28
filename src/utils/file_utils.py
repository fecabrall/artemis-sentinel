"""File utility functions with safe error handling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import ensure_project_directories
from src.logger import setup_logger

logger = setup_logger(__name__)


def ensure_directories() -> None:
    """Ensure project directories exist."""
    ensure_project_directories()


def read_json(path: Path) -> dict[str, Any]:
    """Read JSON from path, returning an empty dict on failure."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning("JSON file not found: %s", path)
    except json.JSONDecodeError:
        logger.error("Invalid JSON content in %s", path)
    except OSError as exc:
        logger.error("Unable to read JSON %s: %s", path, exc)
    return {}


def write_json(path: Path, data: dict[str, Any]) -> bool:
    """Write dictionary to JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=True)
        return True
    except OSError as exc:
        logger.error("Unable to write JSON %s: %s", path, exc)
        return False


def save_dataframe_csv(df: pd.DataFrame, path: Path) -> bool:
    """Save DataFrame as CSV with safe error handling."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return True
    except Exception as exc:  # pragma: no cover - defensive safeguard
        logger.error("Unable to save CSV %s: %s", path, exc)
        return False
