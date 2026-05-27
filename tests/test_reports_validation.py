import pytest

from app.reports import ReportDefinition, validate_report_definition


def test_validate_report_definition_accepts_existing_definitions():
    report = ReportDefinition(
        code="demo",
        url_path="/demo",
        build_url=lambda base_url, period: base_url,
        export_dir="demo",
    )

    validate_report_definition(report)


def test_validate_report_definition_rejects_conflicting_export_flows():
    report = ReportDefinition(
        code="demo",
        url_path="/demo",
        build_url=lambda base_url, period: base_url,
        export_dir="demo",
        export_endpoint="/api/export",
        use_export_marker=True,
    )

    with pytest.raises(ValueError, match="cannot be combined"):
        validate_report_definition(report)
