"""Downloaded file integrity checks."""

from __future__ import annotations

from pathlib import Path


def validate_downloaded_file(path: Path, expected_ext: str = ".xlsx") -> Path:
    if not path.exists():
        raise RuntimeError(f"Downloaded file does not exist: {path}")
    if not path.is_file():
        raise RuntimeError(f"Downloaded path is not a file: {path}")
    if path.stat().st_size == 0:
        raise RuntimeError("Downloaded file is empty")

    safe_expected_ext = (
        expected_ext.lower() if expected_ext.startswith(".") else f".{expected_ext}"
    )
    if path.suffix.lower() != safe_expected_ext:
        raise RuntimeError(
            f"Downloaded file extension mismatch: expected {safe_expected_ext}, got {path.suffix}"
        )

    if safe_expected_ext == ".xlsx":
        with path.open("rb") as file_obj:
            if file_obj.read(2) != b"PK":
                raise RuntimeError("Downloaded .xlsx file is not a valid zip container")
    return path
