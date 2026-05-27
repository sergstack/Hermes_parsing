# Baseline Summary Template

Use this template after an explicitly approved live-smoke baseline. Do not fill
it from dry-run-only data.

## Run Context

| Field | Value |
|---|---|
| baseline_id |  |
| commit_sha |  |
| run_date |  |
| approved_by |  |
| config_file | `config/config.local.txt` |
| output_dir |  |
| period |  |
| report_scope | `dds`, `dds_expenses`, `p-fact`, `account_balances` |
| live_export_confirmed | yes/no |

## Summary Table

| report_code | period | strategy | success | duration_sec | attempts | slowest_stage | error_code | output_size | notes |
|---|---|---|---|---:|---:|---|---|---:|---|
| `dds` |  | marker_history |  |  |  |  |  |  |  |
| `dds_expenses` |  | history |  |  |  |  |  |  |  |
| `p-fact` |  | history |  |  |  |  |  |  |  |
| `account_balances` |  | direct |  |  |  |  |  |  |  |

## Failure Artifacts

| report_code | failure_artifact_path | retained_locally | notes |
|---|---|---|---|
| `dds` |  |  |  |
| `dds_expenses` |  |  |  |
| `p-fact` |  |  |  |
| `account_balances` |  |  |  |

## Phase 9 Recommendation

Recommended parameter family:

```text
pending baseline review
```

Evidence:

```text
pending baseline review
```

Do not proceed when:

- success rate is below baseline expectation;
- failures are caused by selectors, login, or report contract issues;
- metrics are missing stage or attempt data;
- the proposed change would affect report URLs, filters, selectors, output names,
  retry policy, or business logic outside its phase scope.
