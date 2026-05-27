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
- explicit rollback command

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
- `stages`

Stage-level fields:

- `stage`
- `duration_sec`
- `status`
- `error_code`

## Acceptance Threshold

A candidate can be accepted only when:

- success rate is not worse than baseline;
- failure count is not higher than baseline;
- average duration improves enough to justify the change;
- no report contract changes are introduced;
- dry-run and unit tests pass;
- live smoke, if explicitly approved, uses the live smoke protocol.
