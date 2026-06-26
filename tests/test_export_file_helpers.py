from unittest.mock import patch
from io import BytesIO
from zipfile import ZipFile

from app.export_api import (
    candidate_export_names,
    poll_ready_export_row,
)
from app.export_files import (
    determine_extension,
    move_download,
    repair_xlsx_dimension,
    save_export_bytes,
)


def _xlsx_bytes(payload: str = "payload") -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as zf:
        zf.writestr("xl/workbook.xml", payload)
    return buffer.getvalue()


def test_determine_extension_uses_filename_suffix():
    assert determine_extension("report.xlsx", "https://example.test/download") == ".xlsx"


def test_determine_extension_falls_back_to_url_suffix():
    assert determine_extension("download", "https://example.test/file.csv") == ".csv"


def test_determine_extension_falls_back_to_bin():
    assert determine_extension("download", "https://example.test/file") == ".bin"


def test_move_download_overwrites_existing_target(tmp_path):
    source = tmp_path / "source.xlsx"
    target = tmp_path / "nested" / "target.xlsx"
    source.write_bytes(_xlsx_bytes("new"))
    target.parent.mkdir()
    target.write_bytes(_xlsx_bytes("old"))

    move_download(source, target)

    assert not source.exists()
    assert target.read_bytes() == _xlsx_bytes("new")


def test_save_export_bytes_uses_content_disposition_filename(tmp_path):
    output_path = tmp_path / "target.xlsx"

    data = _xlsx_bytes()
    saved = save_export_bytes(output_path, data, 'attachment; filename="server.xlsx"')

    assert saved == output_path
    assert output_path.read_bytes() == data


def test_repair_xlsx_dimension_uses_actual_cells(tmp_path):
    workbook = tmp_path / "book.xlsx"
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<dimension ref="A1:C1"/>'
        '<sheetData>'
        '<row r="1"><c r="A1"><v>1</v></c></row>'
        '<row r="4"><c r="L4"><v>2</v></c></row>'
        '</sheetData>'
        '</worksheet>'
    )
    with ZipFile(workbook, "w") as zf:
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/workbook.xml", "<workbook/>")

    repair_xlsx_dimension(workbook)

    with ZipFile(workbook) as zf:
        repaired = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert '<dimension ref="A1:L4"/>' in repaired


def test_candidate_export_names_for_monthly_file():
    assert candidate_export_names("raw_2026-03.xlsx") == [
        "raw_2026-03.xlsx",
        "2026-03-01.xlsx",
        "2026-03.xlsx",
    ]


def test_candidate_export_names_includes_extra_name_first():
    assert candidate_export_names("contractors.xlsx", "contractors_ready.xlsx") == [
        "contractors_ready.xlsx",
        "contractors.xlsx",
    ]


def test_poll_ready_export_row_selects_newest_matching_ready_row(mock_session):
    rows = [
        {"id": 100, "status_id": "ready", "original_file_name": "raw_2026-03.xlsx"},
        {"id": 101, "status_id": "pending", "original_file_name": "raw_2026-03.xlsx"},
        {"id": 102, "status_id": "ready", "original_file_name": "2026-03.xlsx"},
    ]
    with patch("app.export_api.load_export_rows", return_value=rows) as load_rows:
        selected = poll_ready_export_row(
            mock_session,
            "https://herm.finance",
            "raw_2026-03.xlsx",
            timeout_ms=100,
            min_row_id=100,
        )

    assert selected["id"] == 102
    load_rows.assert_called_once_with(mock_session, "https://herm.finance")
