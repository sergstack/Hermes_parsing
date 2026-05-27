"""Filesystem helpers for export downloads."""

from __future__ import annotations

import shutil
from pathlib import Path
from urllib.parse import urlparse

from .browser import ensure_parent_dir
from .file_integrity import validate_downloaded_file
from .paths import normalize_download_name


def determine_extension(downloaded_name: str, url: str | None = None) -> str:
    parsed = Path(downloaded_name)
    if parsed.suffix:
        return parsed.suffix
    if url:
        suffix = Path(urlparse(url).path).suffix
        if suffix:
            return suffix
    return ".bin"


def move_download(download_path: Path, output_path: Path) -> None:
    ensure_parent_dir(output_path)
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(download_path), str(output_path))
    validate_downloaded_file(output_path, output_path.suffix)


def save_export_bytes(output_path: Path, data: bytes, disposition: str) -> Path:
    suggested = normalize_download_name(
        disposition.split("filename=")[-1].strip('"; ')
        if "filename=" in disposition
        else output_path.name
    )
    ext = determine_extension(suggested)
    final_path = output_path.with_suffix(ext)
    ensure_parent_dir(final_path)
    final_path.write_bytes(data)
    return validate_downloaded_file(final_path, final_path.suffix)


def latest_downloaded_file(download_dir: Path, pattern: str = "*.xlsx") -> Path | None:
    candidates = [path for path in download_dir.glob(pattern) if path.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    return candidates[0]


def move_latest_download(
    download_dir: Path, output_path: Path, pattern: str = "*.xlsx"
) -> Path:
    latest = latest_downloaded_file(download_dir, pattern)
    if latest is None:
        raise RuntimeError(f"No downloaded file found in {download_dir}")
    ensure_parent_dir(output_path)
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(latest), str(output_path))
    return validate_downloaded_file(output_path, output_path.suffix)


def move_latest_download_since(
    download_dir: Path,
    output_path: Path,
    known_files: set[Path],
    pattern: str = "*.xlsx",
) -> Path:
    candidates = [
        path
        for path in download_dir.glob(pattern)
        if path.is_file() and path not in known_files
    ]
    if not candidates:
        raise RuntimeError(f"No new downloaded file found in {download_dir}")
    candidates.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    latest = candidates[0]
    ensure_parent_dir(output_path)
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(latest), str(output_path))
    return validate_downloaded_file(output_path, output_path.suffix)
