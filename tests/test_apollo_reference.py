from pathlib import Path

from src.utils.apollo_reference import inspect_apollo_reference


def test_apollo_reference_not_found(tmp_path: Path):
    result = inspect_apollo_reference(tmp_path)
    assert result["apollo_folder_found"] is False
    assert result["analysis_mode"] == "NOT_AVAILABLE"


def test_apollo_reference_found_and_metadata(tmp_path: Path):
    apollo = tmp_path / "Apollo11"
    apollo.mkdir()
    (apollo / "README.md").write_text("# test", encoding="utf-8")
    (apollo / "LICENSE").write_text("license", encoding="utf-8")
    sub = apollo / "Comanche055"
    sub.mkdir()
    (sub / "A.agc").write_text("hello", encoding="utf-8")
    (sub / "binary.bin").write_bytes(b"\x00\x01\x02")

    result = inspect_apollo_reference(tmp_path)
    assert result["apollo_folder_found"] is True
    assert result["readme_found"] is True
    assert result["license_found"] is True
    assert result["files_count"] >= 4
    assert result["analysis_mode"] == "READ_ONLY_REFERENCE"

