import pytest

from app.file_integrity import validate_downloaded_file


def test_missing_file_rejected(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        validate_downloaded_file(tmp_path / "missing.xlsx")


def test_zero_byte_file_rejected(tmp_path):
    path = tmp_path / "empty.xlsx"
    path.write_bytes(b"")

    with pytest.raises(RuntimeError, match="empty"):
        validate_downloaded_file(path)


def test_extension_mismatch_rejected(tmp_path):
    path = tmp_path / "report.csv"
    path.write_text("data", encoding="utf-8")

    with pytest.raises(RuntimeError, match="extension mismatch"):
        validate_downloaded_file(path, ".xlsx")


def test_html_renamed_as_xlsx_rejected(tmp_path):
    path = tmp_path / "report.xlsx"
    path.write_text("<html>login</html>", encoding="utf-8")

    with pytest.raises(RuntimeError, match="valid zip"):
        validate_downloaded_file(path)


def test_xlsx_zip_magic_accepted(tmp_path):
    path = tmp_path / "report.xlsx"
    path.write_bytes(b"PK\x03\x04xlsx payload")

    assert validate_downloaded_file(path) == path


def test_non_xlsx_expected_extension_accepts_non_empty_file(tmp_path):
    path = tmp_path / "report.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")

    assert validate_downloaded_file(path, ".csv") == path
