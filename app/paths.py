"""Filesystem paths and safe output placement."""

from __future__ import annotations

from pathlib import Path

from .dates import MonthPeriod


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_path(download_dir: Path, report_code: str, period: MonthPeriod, ext: str, prefix: str = "raw") -> Path:
    safe_ext = ext if ext.startswith(".") else f".{ext}"
    return download_dir / report_code / f"{prefix}_{period.label}{safe_ext}"


def existing_output_paths(download_dir: Path, report_code: str, period: MonthPeriod) -> list[Path]:
    return sorted((download_dir / report_code).glob(f"*_{period.label}.*"))


def normalize_download_name(filename: str, fallback_ext: str = ".bin") -> str:
    name = Path(filename).name
    suffix = Path(name).suffix
    if not suffix:
        # TODO: confirm the actual export extension if the UI does not expose it.
        suffix = fallback_ext
    return f"{Path(name).stem}{suffix}"
