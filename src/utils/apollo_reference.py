"""Read-only Apollo reference folder inventory utilities."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


APOLLO_CANDIDATE_NAMES = [
    "Apollo11",
    "Apollo_11",
    "apollo11",
    "apollo_11",
    "Apollo-11",
    "apollo-11",
    "apollo",
    "APOLLO11",
    "Apollo-11-master",
]


def _locate_apollo_folder(base_dir: Path) -> Path | None:
    for name in APOLLO_CANDIDATE_NAMES:
        candidate = base_dir / name
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def inspect_apollo_reference(base_dir: Path) -> dict[str, Any]:
    """Return read-only metadata about Apollo reference folder."""
    folder = _locate_apollo_folder(base_dir)
    if folder is None:
        return {"apollo_folder_found": False, "analysis_mode": "NOT_AVAILABLE"}

    files = [p for p in folder.rglob("*") if p.is_file()]
    ext_counter = Counter((p.suffix.lower() or "<no_ext>") for p in files)
    total_size = sum(p.stat().st_size for p in files)
    large_files = [
        str(p.relative_to(base_dir))
        for p in files
        if p.stat().st_size >= 5 * 1024 * 1024
    ]

    readme = next((p for p in files if p.name.lower().startswith("readme")), None)
    license_file = next(
        (
            p
            for p in files
            if p.name.lower() in {"license", "license.md", "license.txt", "copying"}
        ),
        None,
    )

    top_subfolders = sorted([p.name for p in folder.iterdir() if p.is_dir()])[:15]
    return {
        "apollo_folder_found": True,
        "apollo_folder_path": str(folder.relative_to(base_dir)),
        "files_count": len(files),
        "extensions": sorted(ext_counter.keys()),
        "extensions_top": dict(ext_counter.most_common(12)),
        "total_size_bytes": total_size,
        "top_subfolders": top_subfolders,
        "license_found": license_file is not None,
        "license_file": str(license_file.relative_to(base_dir)) if license_file else None,
        "readme_found": readme is not None,
        "readme_file": str(readme.relative_to(base_dir)) if readme else None,
        "large_files": large_files,
        "analysis_mode": "READ_ONLY_REFERENCE",
    }

