# Live Baseline Execution Checklist

This checklist is for collecting the Phase 9 live-smoke baseline only. It does
not approve live export by itself.

## Approval Gate

Do not run live Herm Finance export until the user provides this exact approval:

```text
Approved: run Hermes live-smoke baseline for dds, dds_expenses, p-fact, and account_balances for one completed month.
```

If approval is absent, stop after local checks and report the missing approval.

## Preflight Commands

Run before any approved live command:

```bash
git switch main
git pull --ff-only origin main
git status --short --branch
python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m app.main --config config/config.example.txt --dry-run --reports dds --headless true
git ls-files | grep -E '(^config/config\.txt$|^config/config\.local\.txt$|^state/|^exports/|^logs/|\.env$|\.env\.|cookies|session|storageState)' || true
```

Expected private/runtime grep output: empty.

## Private Config Check

Do not print private config contents.

Check existence only:

```bash
test -f config/config.local.txt
```

Stop if the file is missing.

## Approved Scope

Reports:

- `dds`
- `dds_expenses`
- `p-fact`
- `account_balances`

Period:

- one completed month only

Run mode:

- one report per command
- `--headless false`
- `--overwrite false`
- private config only
- temporary output directory in private config when possible

Do not run all reports, all periods, or parallel exports.

## Live Command Templates

Do not run these commands without explicit approval.

```bash
python3 -m app.main --config config/config.local.txt --reports dds --headless false --overwrite false
python3 -m app.main --config config/config.local.txt --reports dds_expenses --headless false --overwrite false
python3 -m app.main --config config/config.local.txt --reports p-fact --headless false --overwrite false
python3 -m app.main --config config/config.local.txt --reports account_balances --headless false --overwrite false
```

## Metrics Files To Inspect

After each report command, inspect local runtime artifacts only:

- `logs/summary.json`
- `logs/run_metrics.json`
- `logs/failures/**` when present
- output file metadata only: path basename or normalized relative path, file size,
  integrity status

Do not commit those runtime files.

## Failure Artifact Locations

Failure artifacts are expected under:

```text
logs/failures/<run_id>/<report_code>_<period>/
```

Inspect only metadata needed for the redacted baseline summary:

- artifact directory exists: yes/no
- summary error code
- summary stage
- whether screenshot/page HTML exists locally

Do not commit screenshots, page HTML, traces, logs, exports, state, or private
config.

## Post-Run Summary Steps

Create a committed redacted summary:

```text
docs/experiments/baseline_summary_<YYYY-MM-DD>.md
```

Required columns:

```text
report_code | period | strategy | success | duration_sec | attempts | slowest_stage | error_code | output_size | notes
```

Include:

- approval text
- commit SHA
- run date
- approved report scope
- whether failure artifacts exist
- Phase 9 recommendation or explicit block reason

Exclude:

- private config contents
- browser state
- cookies/session files
- raw exports
- raw logs
- screenshots and HTML
- full private absolute paths when a basename or normalized relative path is enough

## Stop Conditions

Stop immediately if any of these occurs:

- explicit live approval is missing
- `config/config.local.txt` is missing
- login/session requires action not covered by the approval
- a command would run more than one approved report at once
- a command would run more than one completed month
- report URL/filter/selector/output name changes seem necessary
- private/runtime files would be committed
- tests or dry-run fail after one safe local retry

## Phase 9 Optimization Gate

Do not optimize waits, polling intervals, timeouts, or retry policy until a live
baseline summary exists and identifies one safe parameter family.
