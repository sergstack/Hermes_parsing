"""Output file helpers for downloaded Herm Finance exports."""

from __future__ import annotations

import shutil
import tempfile
import re
from zipfile import ZipFile, ZIP_DEFLATED
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


def repair_xlsx_dimension(path: Path) -> None:
    """Fix incorrect worksheet dimension metadata in Herm Finance XLSX exports."""
    with ZipFile(path) as src:
        sheet_xml = src.read("xl/worksheets/sheet1.xml").decode("utf-8")
        cell_refs = re.findall(r'<c[^>]* r="([A-Z]+)(\d+)"', sheet_xml)
        if not cell_refs:
            return
        max_col = max(_column_number(col) for col, _ in cell_refs)
        max_row = max(int(row) for _, row in cell_refs)
        ref = f"A1:{_column_name(max_col)}{max_row}"
        updated_sheet_xml = re.sub(
            r'<dimension ref="[^"]+"\s*/>',
            f'<dimension ref="{ref}"/>',
            sheet_xml,
            count=1,
        )
        if updated_sheet_xml == sheet_xml:
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp_path = Path(tmp.name)
        try:
            with ZipFile(tmp_path, "w", ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    data = updated_sheet_xml.encode("utf-8") if item.filename == "xl/worksheets/sheet1.xml" else src.read(item.filename)
                    dst.writestr(item, data)
            tmp_path.replace(path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def _column_number(name: str) -> int:
    number = 0
    for char in name:
        number = number * 26 + ord(char) - ord("A") + 1
    return number


def _column_name(number: int) -> str:
    chars: list[str] = []
    while number:
        number, remainder = divmod(number - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))
