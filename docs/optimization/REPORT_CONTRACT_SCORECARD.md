# Report Contract Scorecard

Scores are planning signals for test coverage, not business metrics.

| report_code | strategy | url_test | output_path_test | selector_test | strategy_dispatch_test | readme_doc | score | risk | next_test_to_add |
|---|---|---|---|---|---|---|---|---|---|
| `applications` | marker history export | partial | partial | partial | partial | yes | baseline: 3/5 | stale history row or popover selector drift | dispatch test for marker, readiness poll, and history download ordering |
| `dds_expenses` | history export without marker | yes | partial | partial | yes | yes | baseline: 4/5 | reserve dropdown index and export-history refresh timing | selector contract test for reserve filter and export button |
| `p-fact` | history export without marker | yes | partial | partial | yes | yes | baseline: 4/5 | shared URL builder with separate output path | output-path and dispatch test proving `p-fact` stays separate from `dds_expenses` |
| `dds` | marker history export with payment date filter | yes | yes | partial | partial | yes | baseline: 4/5 | multiple search buttons on the page | dispatch test for date filter, search click, marker upload, and history download |
| `budget_rows` | marker history export with payment date filter | yes | yes | partial | partial | yes | baseline: 4/5 | future-month range and filename marker | full marker-flow test with min export ID guard |
| `contractors` | marker history export, one-shot | yes | partial | partial | partial | yes | baseline: 3/5 | one-shot overwrite behavior and stale file cleanup | test for repeat suppression and output filename contract |
| `account_balances` | direct browser download after search | yes | yes | partial | yes | yes | baseline: 4/5 | local Downloads selection and month-end file naming | file movement test with known-files baseline and direct-download dispatch |
| `cons_budget` | direct browser download after annual search | yes | yes | partial | partial | yes | baseline: 4/5 | annual period and fixed output filename | dispatch test for annual period, direct download, and non-month filename |
