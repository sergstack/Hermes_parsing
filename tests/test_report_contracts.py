from app.reports import REPORT_DEFINITIONS


def test_report_catalog_contracts():
    expected = {
        "applications": ("demands", "demands", True, True),
        "dds_expenses": ("p-fact", "p-fact", True, False),
        "dds": ("dds", "dds", True, True),
        "budget_rows": ("budget_rows", "raw", True, True),
        "cons_budget": ("cons_budget", "cons_budget", False, False),
        "contractors": ("contractors", "contractors", False, False),
        "account_balances": ("account_balances", "raw", True, False),
    }

    assert set(REPORT_DEFINITIONS) == set(expected)
    for code, (export_dir, file_prefix, repeat_each_month, use_export_marker) in expected.items():
        report = REPORT_DEFINITIONS[code]
        assert report.export_dir == export_dir
        assert report.file_prefix == file_prefix
        assert report.repeat_each_month is repeat_each_month
        assert report.use_export_marker is use_export_marker


def test_report_api_endpoint_contracts():
    assert REPORT_DEFINITIONS["contractors"].export_endpoint == "/api/resources/contractor/export"
    for code, report in REPORT_DEFINITIONS.items():
        if code != "contractors":
            assert report.export_endpoint is None
