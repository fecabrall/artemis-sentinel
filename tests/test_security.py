"""Security regression tests — no secrets in versioned artifacts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.config import mask_sensitive_text, nasa_api_key_status

ROOT = Path(__file__).resolve().parent.parent
NASA_KEY_PATTERN = re.compile(r"[A-Za-z0-9]{30,}")


def test_env_example_uses_demo_key():
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "NASA_API_KEY=DEMO_KEY" in content
    assert "NASA_API_KEY=" in content
    lines = [line for line in content.splitlines() if line.startswith("NASA_API_KEY=")]
    assert lines == ["NASA_API_KEY=DEMO_KEY"]


def test_nasa_api_key_status_never_returns_key():
    status = nasa_api_key_status()
    assert "configured" in status
    assert "mode" in status
    assert "api_key" not in status
    assert "NASA_API_KEY" not in str(status.values())


def test_mask_sensitive_text():
    raw = "api_key=SECRET123&NASA_API_KEY=ABC&SMTP_APP_PASSWORD=xyz&password=p&token=t&secret=s"
    masked = mask_sensitive_text(raw)
    assert "SECRET123" not in masked
    assert "api_key=***MASKED***" in masked
    assert "NASA_API_KEY=***MASKED***" in masked


@pytest.mark.parametrize(
    "rel_path",
    [
        "README.md",
        ".env.example",
        "docs/RELATORIO_TECNICO_ARTEMIS_SENTINEL.md",
    ],
)
def test_versioned_docs_no_hardcoded_long_keys(rel_path):
    path = ROOT / rel_path
    if not path.exists():
        pytest.skip(f"{rel_path} not present")
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("NASA_API_KEY=") and "DEMO_KEY" not in line:
            pytest.fail(f"Possible real NASA key line in {rel_path}")
        if line.strip().startswith("SMTP_APP_PASSWORD=") and line.strip() != "SMTP_APP_PASSWORD=":
            pytest.fail(f"Possible SMTP password in {rel_path}")


def test_readme_recommends_revoke():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Segurança da NASA_API_KEY" in readme
    assert "revogue" in readme.lower()
