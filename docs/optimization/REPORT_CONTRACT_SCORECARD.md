# Report Contract Scorecard

Scores are planning signals for test coverage, not business metrics.

| report_code | strategy | url_test | output_path_test | selector_test | strategy_dispatch_test | readme_doc | score | risk | next_test_to_add |
|---|---|---|---|---|---|---|---|---|---|
| `applications` | marker history export | yes | yes | partial | yes | yes | baseline: 4/5 | stale history row or popover selector drift | selector contract test for popover marker and history download controls |
| `dds_expenses` | history export without marker | yes | yes | partial | yes | yes | baseline: 4/5 | reserve dropdown index and export-history refresh timing | selector contract test for reserve filter and export button |
| `p-fact` | history export without marker | yes | yes | partial | yes | yes | baseline: 4/5 | shared URL builder with separate output path | history-flow test proving `p-fact` stays separate from `dds_expenses` |
| `dds` | marker history export with payment date filter | yes | yes | partial | yes | yes | baseline: 4/5 | multiple search buttons on the page | selector contract test for date filter, search click, marker upload, and history download |
| `budget_rows` | marker history export with payment date filter | yes | yes | partial | yes | yes | baseline: 4/5 | future-month range and filename marker | full marker-flow test with min export ID guard |
| `contractors` | marker history export, one-shot | yes | yes | partial | yes | yes | baseline: 4/5 | one-shot overwrite behavior and stale file cleanup | test stale-file cleanup before marker download |
| `account_balances` | direct browser download after search | yes | yes | partial | yes | yes | baseline: 4/5 | local Downloads selection and month-end file naming | direct-download test with known-files baseline and selected filters |
| `cons_budget` | direct browser download after annual search | yes | yes | partial | yes | yes | baseline: 4/5 | dry-run planned path is date-stamped while live direct output is fixed `cons_budget.xlsx` | direct-download test for annual period and fixed output filename |
