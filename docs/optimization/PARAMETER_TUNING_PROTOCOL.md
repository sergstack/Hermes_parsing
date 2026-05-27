# Parameter Tuning Protocol

## Parameters To Tune

- `timeout_ms`
- `slow_mo`
- `pre_search_wait_ms`
- `wait_after_export_ms`
- API polling interval
- history refresh polling interval
- load-state waits such as `domcontentloaded` and `networkidle`
- retry count and retry backoff

## Safe Experiment Mode

- Default to dry-run and unit tests.
- Use synthetic or mocked timing tests before live runs.
- Use `app.experiments.ExperimentResult` for deterministic baseline/candidate
  scoring before any live smoke is considered.
- Tune one parameter per PR.
- Keep report URLs, filters, selectors, and output names unchanged.
- Record baseline and candidate metrics with the same report, period, and local
  environment.

## Forbidden Live-Run Defaults

- Do not run live Herm Finance export in CI.
- Do not enable live export as a default validation step.
- Do not change a live-run default after one anecdotal run.
- Do not commit private config, session state, exports, or logs.

## Scoring Formula

Use Python or SQL to calculate score from collected metrics:

```text
score = success_rate * 100 - avg_duration_sec - retry_penalty - failure_penalty
```

Suggested penalties:

- retry penalty: count of retries multiplied by a fixed penalty.
- failure penalty: count of failed attempts multiplied by a larger fixed penalty.

## Baseline vs Candidate Comparison

Each tuning PR must include:

- baseline commit and candidate commit
- report codes tested
- periods tested
- environment notes
- metrics file or summarized table
- score calculation script or command
- serialized experiment result for baseline and candidate
- explicit rollback command

Scores must use stable error codes from the exporter taxonomy rather than raw
exception strings, so failure counts remain comparable across refactors.

## Required Metrics Fields

Run-level fields:

- `schema_version`
- `status`
- `dry_run`
- `attempts`

Attempt-level fields:

- `report_code`
- `period`
- `attempt`
- `status`
- `error_code`
- `duration_sec`
- `output_path`
- `file_size`
- `stages`

Stage-level fields:

- `stage`
- `duration_sec`
- `status`
- `error_code`

## Live Baseline Gate

Wait and polling optimization requires an explicitly approved live-smoke
baseline. Dry-run metrics can verify schema and plumbing, but they are not
evidence for changing Herm Finance waits, polling intervals, timeouts, or retry
policy.

Before any optimization PR, create a baseline summary using:

- `docs/experiments/live_smoke_baseline_plan.md`
- `docs/experiments/baseline_summary_template.md`

The first approved baseline must use one completed month and the minimal report
scope:

- `dds`
- `dds_expenses`
- `p-fact`
- `account_balances`

## Experiment Result Fields

The pure experiment model records:

- `experiment_id`
- `report_code`
- `period`
- `variant`
- `success`
- `duration_sec`
- `retry_count`
- `failure_count`
- `score`

Candidate comparison must reject candidates whose success rate is worse than
baseline or whose failure count is higher than baseline, even when duration is
lower.

## Acceptance Threshold

A candidate can be accepted only when:

- success rate is not worse than baseline;
- failure count is not higher than baseline;
- average duration improves enough to justify the change;
- no report contract changes are introduced;
- dry-run and unit tests pass;
- live smoke, if explicitly approved, uses the live smoke protocol.
