# Hermes Optimization Roadmap

## Current Architecture

The exporter is a Python CLI around Playwright. `app.main` loads config, expands
report periods, supports dry-run planning, and dispatches live exports through
`download_report_for_month`. Report contracts live in `app.reports`; fragile UI
selectors live in `app.selectors`; browser/session lifecycle is split between
`app.browser` and `app.auth`; API polling and browser-download file movement are
in `app.export_api` and `app.export_files`.

Dry-run is the safe non-live validation path. It builds planned report URLs and
output paths without opening a browser, logging in, or exporting from Herm
Finance.

## Reliability Risks

- UI selectors and Element/DevExtreme timing are fragile contracts.
- History-download flows can accidentally pick stale files unless baselines and
new-row checks are explicit.
- Browser downloads that rely on `~/Downloads` are sensitive to local state.
- Existing exceptions are mostly strings, making failure classification harder.
- Output integrity is checked only for non-empty files.

## Stability Risks

- Several report strategies share one large downloader function.
- Waits are fixed in multiple places and are difficult to compare objectively.
- Manual login and persisted session state are intentionally local and cannot be
validated in CI.
- Report URL, output-path, selector, and dispatch contracts need independent
tests before strategy refactors.

## Speed Bottlenecks

- Fixed sleeps after search/export add wall-clock time even when the UI is ready.
- History polling can reopen panels repeatedly.
- Monthly sequential execution is simple and safe but slow for large ranges.
- Download readiness waits are not yet measured by stage.

## Phased PR Roadmap

### Phase 1: Metrics Foundation

Add deterministic metrics containers for stage, attempt, and run-level timing.
Keep this pure and unwired to live downloader behavior.

Acceptance:

- Metrics objects serialize to stable JSON.
- Tests cover success and failure-code representation.
- No Playwright dependency in the metrics module.
- Existing dry-run and tests still pass.

### Phase 2: Error Taxonomy

Introduce stable error codes for timeout, selector, export-history, API polling,
empty file, and auth/session failures.

The error taxonomy provides stable error codes for later metrics, retry policy,
and failure packages. It is intentionally not wired into downloader behavior in
this PR.

Acceptance:

- Error codes are testable without live export.
- Existing exception messages remain understandable.
- No report contract changes.

### Phase 3: Report Contract Test Coverage

Fill gaps in URL, output path, selector, and strategy dispatch tests for every
report definition.

Acceptance:

- Each report has URL and output-path tests.
- Each strategy has at least one dispatch/order test.
- README report table remains aligned with `REPORT_DEFINITIONS`.

### Phase 4: Strategy Split

Extract behavior-preserving strategy helpers from the downloader only after
contracts are covered.

Acceptance:

- Existing tests pass unchanged or with focused additions.
- Strategy selection is explicit and tested.
- No selector, URL, filter, or output name changes.

### Phase 5: Retry Policy and File Integrity

Make retries observable and add deterministic file-integrity checks beyond
non-empty files where safe.

Acceptance:

- Retry attempts record error codes and stage timing.
- Failed files are not reported as successful.
- Integrity checks are reversible and do not depend on live export.

### Phase 6: Parameter Tuning

Use collected metrics to tune waits, polling intervals, and timeout values in
small PRs.

Acceptance:

- Each tuning PR compares baseline and candidate metrics.
- No live-run defaults change without evidence.
- Rollback is a single config/code revert.

### Phase 7: Speed Optimization

Only after reliability metrics and contracts exist, reduce fixed sleeps or add
controlled concurrency for independent reports.

Acceptance:

- Success rate is not lower than baseline.
- Runtime improvement is measured by report and stage.
- Concurrency never shares unsafe browser/session state without explicit tests.

## Testing Strategy

- Unit tests for metrics serialization, URL construction, output paths, and
  helper functions.
- Contract tests for report definitions, selectors, and dispatch ordering.
- Smoke tests through dry-run only for CI and local safe validation.
- Live smoke protocol only by explicit owner approval, using a local config and
  never in CI.
- Artifact validation for downloaded file existence, extension, and non-empty
  content before later workbook-level checks are added.

## Rollback Strategy

- Keep each phase in one focused PR.
- Avoid mixing formatting, docs, contracts, and behavior changes.
- Revert the phase PR if metrics or tests introduce noise.
- For tuning PRs, revert only the parameter change and keep the metrics that
  revealed the issue.

## Live Smoke Protocol

Live smoke is forbidden by default. If explicitly approved later:

1. Use a private local config that is never committed.
2. Run one report and one period only.
3. Capture metrics, logs, output path, and error code if any.
4. Do not change selectors, URLs, filters, or output names during the run.
5. Compare against dry-run plan before and after the run.

## Codex Iterative Parameter Tuning Approach

Codex should use metrics as evidence, not guesswork:

1. Record baseline by report, period, attempt, and stage.
2. Change one parameter at a time.
3. Compare candidate metrics to baseline.
4. Keep the change only when acceptance thresholds are met.
5. Report assumptions, raw metric files, and rollback commands.
