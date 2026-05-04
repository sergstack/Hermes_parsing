"""Filesystem paths and safe output placement."""

from __future__ import annotations

from pathlib import Path

from .dates import MonthPeriod


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_path(
    download_dir: Path,
    report_code: str,
    period: MonthPeriod,
    ext: str,
    prefix: str = "raw",
    use_end_date: bool = False,
) -> Path:
    safe_ext = ext if ext.startswith(".") else f".{ext}"
    date_label = period.end.strftime("%Y-%m-%d") if use_end_date else period.label
    return download_dir / report_code / f"{prefix}_{date_label}{safe_ext}"


def build_output_directory(download_dir: Path, report_code: str) -> Path:
    return download_dir / report_code


def existing_output_paths(
    download_dir: Path, report_code: str, period: MonthPeriod
) -> list[Path]:
    directory = download_dir / report_code
    # Primary pattern: matches "prefix_YYYY-MM.ext" (most reports)
    results = set(directory.glob(f"*_{period.label}.*"))
    # Also match "prefix_YYYY-MM-DD.ext" (e.g. acc_balance_2025-01-31.xlsx)
    # because some reports use end-of-month date instead of YYYY-MM label.
    results |= set(directory.glob(f"*_{period.label}-??.*"))
    return sorted(results)


def normalize_download_name(filename: str, fallback_ext: str = ".bin") -> str:
    name = Path(filename).name
    suffix = Path(name).suffix
    if not suffix:
        # TODO: confirm the actual export extension if the UI does not expose it.
        suffix = fallback_ext
    return f"{Path(name).stem}{suffix}"
