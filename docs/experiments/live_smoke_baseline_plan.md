# Live Smoke Baseline Plan

This plan prepares Phase 9 wait and polling optimization. It is measurement-only.
Do not change waits, polling intervals, timeouts, retry policy, selectors, report
URLs, filters, output names, or business logic while collecting this baseline.

## Approval Gate

Live Herm Finance export is not approved by default.

Before running any live command, obtain explicit approval for this exact task:

```text
Approved: run Hermes live-smoke baseline for dds, dds_expenses, p-fact, and account_balances for one completed month.
```

Without that approval, run only local tests and dry-run validation.

## Preflight Checks

Run from `main` or the measurement branch before any approved live smoke:

```bash
git status --short --branch
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m app.main --config config/config.example.txt --dry-run --reports dds --headless true
git ls-files | grep -E '(^config/config\.txt$|^config/config\.local\.txt$|^state/|^exports/|^logs/|\.env$|\.env\.|cookies|session|storageState)' || true
```

Expected private/runtime grep output: empty.

## Live Scope

Use one completed month only. Do not run all reports or all periods.

Approved report set:

- `dds`
- `dds_expenses`
- `p-fact`
- `account_balances`

Recommended live settings:

- private config file: `config/config.local.txt`
- `headless=false` for first validation
- `overwrite=false`
- temporary output directory configured in the private config when possible
- one report per command so a failure package is easier to inspect

## Live Command Template

Do not run these commands without explicit approval.

```bash
python3 -m app.main \
  --config config/config.local.txt \
  --reports dds \
  --headless false \
  --overwrite false
```

Repeat only for approved report codes. Do not broaden scope during the same
baseline run.

## Required Baseline Fields

For every report run, capture:

- `report_code`
- `period`
- strategy
- success or failure
- attempt count
- total duration seconds
- stage durations
- `error_code`
- retry count
- output path
- file size
- integrity status
- failure artifact path when failed

## Artifacts

Runtime artifacts must stay untracked:

- `logs/summary.json`
- `logs/run_metrics.json`
- `logs/failures/**`
- configured temporary export directory
- `state/**`
- private config files

Copy only redacted summary values into the baseline summary. Do not commit live
Herm Finance files, private config, browser state, screenshots, page HTML, or
raw logs.

## Phase 9 Gate

Phase 9 optimization may start only after this baseline exists and shows where
time is spent. Do not optimize from dry-run-only data.
