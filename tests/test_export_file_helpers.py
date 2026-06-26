from pathlib import Path
from datetime import date
from unittest.mock import MagicMock
from zipfile import ZipFile

from app.downloaders import (
    _candidate_export_names,
    _determine_extension,
    _move_download,
    _poll_ready_export_row,
    _save_export_bytes,
    resolve_report_output_target,
)
from app.dates import MonthPeriod
from app.output_writer import repair_xlsx_dimension


def test_determine_extension_uses_filename_suffix():
    assert _determine_extension("report.xlsx", "https://example.test/download") == ".xlsx"


def test_determine_extension_falls_back_to_url_suffix():
    assert _determine_extension("download", "https://example.test/file.csv") == ".csv"


def test_determine_extension_falls_back_to_bin():
    assert _determine_extension("download", "https://example.test/file") == ".bin"


def test_move_download_overwrites_existing_target(tmp_path):
    source = tmp_path / "source.xlsx"
    target = tmp_path / "nested" / "target.xlsx"
    source.write_text("new", encoding="utf-8")
    target.parent.mkdir()
    target.write_text("old", encoding="utf-8")

    _move_download(source, target)

    assert not source.exists()
    assert target.read_text(encoding="utf-8") == "new"


def test_save_export_bytes_uses_content_disposition_filename(tmp_path):
    output_path = tmp_path / "target.xlsx"

    saved = _save_export_bytes(output_path, b"payload", 'attachment; filename="server.xlsx"')

    assert saved == output_path
    assert output_path.read_bytes() == b"payload"


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
    assert _candidate_export_names("raw_2026-03.xlsx") == [
        "raw_2026-03.xlsx",
        "2026-03-01.xlsx",
        "2026-03.xlsx",
    ]


def test_candidate_export_names_includes_extra_name_first():
    assert _candidate_export_names("contractors.xlsx", "contractors_ready.xlsx") == [
        "contractors_ready.xlsx",
        "contractors.xlsx",
    ]


def test_poll_ready_export_row_selects_newest_matching_ready_row(mock_session):
    rows = [
        {"id": 100, "status_id": "ready", "original_file_name": "raw_2026-03.xlsx"},
        {"id": 101, "status_id": "pending", "original_file_name": "raw_2026-03.xlsx"},
        {"id": 102, "status_id": "ready", "original_file_name": "2026-03.xlsx"},
    ]
    load_rows = MagicMock(return_value=rows)

    selected = _poll_ready_export_row(
        mock_session,
        "https://herm.finance",
        "raw_2026-03.xlsx",
        timeout_ms=100,
        min_row_id=100,
        load_rows=load_rows,
    )

    assert selected["id"] == 102
    load_rows.assert_called_once_with(mock_session, "https://herm.finance")


def test_resolve_report_output_target_for_monthly_marker_report(tmp_path):
    period = MonthPeriod(date(2026, 3, 1), date(2026, 3, 31))

    target = resolve_report_output_target(tmp_path, "applications", period)

    assert target.export_file_name == "demands_2026-03.xlsx"
    assert target.output_path == tmp_path / "demands" / "demands_2026-03.xlsx"
    assert target.export_marker == "demands_2026-03"


def test_resolve_report_output_target_for_single_report(tmp_path):
    period = MonthPeriod(date(2026, 3, 1), date(2026, 3, 31))

    target = resolve_report_output_target(tmp_path, "contractors", period)

    assert target.export_file_name == "contractors.xlsx"
    assert target.output_path == tmp_path / "contractors" / "contractors.xlsx"
    assert target.export_marker == "contractors_2026-03"


def test_resolve_report_output_target_for_account_balances_uses_period_end(tmp_path):
    period = MonthPeriod(date(2026, 3, 1), date(2026, 3, 31))

    target = resolve_report_output_target(tmp_path, "account_balances", period)

    assert target.export_file_name == "acc_balance_2026-03-31.xlsx"
    assert target.output_path == tmp_path / "account_balances" / "acc_balance_2026-03-31.xlsx"
