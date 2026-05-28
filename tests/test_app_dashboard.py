"""Dashboard syntax and safety checks."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_app_syntax():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    ast.parse(source)


def test_app_no_secret_strings():
    text = (ROOT / "app.py").read_text(encoding="utf-8").lower()
    assert "nasa_api_key=" not in text
    assert "smtp_app_password" not in text
