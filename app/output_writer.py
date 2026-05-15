"""Output file helpers for downloaded Herm Finance exports."""

from __future__ import annotations

import shutil
from pathlib import Path
from urllib.parse import urlparse

from .paths import normalize_download_name


def determine_extension(downloaded_name: str, url: str | None = None) -> str:
    parsed = Path(downloaded_name)
    if parsed.suffix:
        return parsed.suffix
    if url:
        suffix = Path(urlparse(url).path).suffix
        if suffix:
            return suffix
    # TODO: confirm the actual export extension when Herm Finance does not provide one.
    return ".bin"


def move_download(download_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(download_path), str(output_path))


def save_export_bytes(output_path: Path, data: bytes, disposition: str) -> Path:
    suggested = normalize_download_name(
        disposition.split("filename=")[-1].strip('\"; ') if "filename=" in disposition else output_path.name
    )
    ext = determine_extension(suggested)
    final_path = output_path.with_suffix(ext)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_bytes(data)
    if final_path.stat().st_size == 0:
        raise RuntimeError("Downloaded file is empty")
    return final_path
