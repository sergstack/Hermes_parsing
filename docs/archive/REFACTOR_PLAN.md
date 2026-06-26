# Hermes Refactor Plan

## 1. Purpose

Create a safe foundation for future refactoring of the Herm Finance monthly Excel exporter without changing current behavior.

This plan is based on safe inspection of repository files only. It does not require opening `state/herm_session.json` or `config/config.txt`, and it does not require running the live exporter.

## 2. Non-Negotiable Safety Rules

- Do not run `python -m app.main` or `./run_hermes.command` during refactor planning.
- Do not open, print, commit, move, or modify `state/herm_session.json`.
- Do not open, print, commit, move, or modify `config/config.txt`.
- Do not modify runtime/generated paths: `exports/`, `logs/`, `output/`, `state/`, or `config/config.txt`.
- Do not change output schemas, filenames, report filters, report periods, or destination folders without an explicit scoped task.
- Do not introduce dependencies as part of refactor planning.
- Do not mix the current exporter with any future Mart or analytics pipeline without a separate `SPEC.md`.
- Treat `.venv/bin/python -m pytest --collect-only -q` as import/test discovery only, not full behavior validation.

## 3. Current Repository Map

Safe inspection found the following relevant project areas:

| Area | Current role | Notes |
|---|---|---|
| `app/` | Main Python package for the Herm Finance exporter | Contains auth, browser, config, date, downloader, export flow, export history, logging, output writer, path, report definition, and entrypoint modules |
| `app/main.py` | Export orchestration entrypoint | Reads config, initializes logging, ensures login, delegates report-period selection, iterates report definitions and periods, saves session state |
| `app/config.py` | Runtime config parser | Reads `config/config.txt` by default; resolves relative runtime paths from project root |
| `app/auth.py` | Session reuse and manual login | Uses Playwright storage state; writes session state through `save_session_state` |
| `app/browser.py` | Playwright lifecycle | Starts/stops Chromium browser context |
| `app/reports.py` | Report definitions and URL builders | Defines report codes, filters, URL builders, export directories, naming, and UI behavior flags |
| `app/downloaders.py` | Compatibility facade for report download flow | Keeps existing helper names while delegating extracted responsibilities |
| `app/export_flows.py` | Playwright UI export primitives | Contains export button, filename marker, and export-history download UI helpers |
| `app/export_history.py` | Export history row matching and polling | Contains candidate filename matching, ready-row polling, and ready-by-name waiting |
| `app/output_writer.py` | Output file writing helpers | Contains extension detection, download moves, and byte-save behavior |
| `app/orchestration.py` | Pure run-period selection helpers | Contains consolidated budget period and report-specific period selection |
| `app/run_summary.py` | Run summary accounting | Contains `RunSummary` |
| `app/paths.py` | Project-relative path and output helpers | Resolves project paths, builds output paths, creates directories |
| `app/dates.py` | Month period helpers | Builds completed-month ranges and budget-row range through current-year December |
| `app/logging_utils.py` | Logging setup | Writes `logs/herm_export.log` when the exporter runs |
| `tests/` | Unit tests and mocks | Tests URL builders, config/path resolution, date logic, and selected downloader helper behavior |
| `README.md` | Operational documentation | Documents exporter scope, runtime/sensitive paths, run commands, report methods, outputs, and known behavior |
| `requirements.txt` | Dependency metadata | Currently lists Playwright |
| `SPEC.md`, `plan.md`, `tasks.md` | Previous documentation task artifacts | Describe the README scope clarification already completed |
| `scope-lock.md`, `implementation-guard.md` | Previous control artifacts | Restrict earlier task scope to README documentation |
| `docs/codex/` | Codex execution package | Contains task contract, validation plan, risk register, report template, and paste prompt |
| `config/config.txt.example` | Safe config example | Safe to inspect if needed; real `config/config.txt` remains sensitive |
| `exports/`, `logs/`, `output/`, `state/` | Runtime/generated paths | Contents must not be inspected or modified during planning |

No `src/`, `data/raw/`, `data/stage/`, `data/mart/`, or `data/report/` implementation folders were found during safe inventory.

## 4. Functional Baseline

Current documented responsibility:

- Authenticate to Herm Finance with Playwright.
- Open configured Herm Finance report UI/API endpoints.
- Export Excel files.
- Save generated files under `exports/`.
- Write run logs under `logs/`.

Current documented data flow:

```text
config/config.txt
-> login/session
-> report definitions
-> Playwright UI/API download
-> exports/
-> logs/
```

Current entrypoints:

- Main module: `python -m app.main`.
- macOS wrapper: `./run_hermes.command`.

Safe validation observed during the offline refactor:

- `.venv/bin/python -m pytest --collect-only -q` collected 46 tests successfully.
- `.venv/bin/python -m pytest -q` passed with 46 tests.
- Live exporter was not run.

Behavior protected for future refactors:

- Report URL parameters in `app/reports.py`.
- Report codes and export directories.
- File prefixes and special filenames:
  - `demands_YYYY-MM.xlsx`
  - `p-fact_YYYY-MM.xlsx`
  - `dds_YYYY-MM.xlsx`
  - `raw_YYYY-MM.xlsx`
  - `contractors.xlsx`
  - `acc_balance_YYYY-MM-DD.xlsx`
  - `cons_budget.xlsx`
- Existing `overwrite=false` skip behavior.
- Existing session reuse and manual login fallback behavior.

## 5. Sensitive and Runtime Files Policy

Protected paths:

| Path | Policy |
|---|---|
| `config/config.txt` | Sensitive local runtime config; do not open, print, modify, commit, or use in tests |
| `state/herm_session.json` | Sensitive browser/session state; do not open, print, modify, commit, or use in tests |
| `state/` | Runtime browser/session state; do not mutate during planning/refactor checks |
| `exports/` | Generated Excel outputs; treat as runtime output and raw source material, not Mart output |
| `logs/` | Runtime logs; do not mutate except during intentional exporter runs |
| `output/` | Debug/generated artifacts; do not mutate during planning/refactor checks |

Safe substitutes:

- Use `config/config.txt.example` for documenting config shape.
- Use mocks, fixtures, and temporary directories in tests.
- Use `pytest --collect-only` for safe discovery.
- Add characterization tests around pure functions before touching live/exporter code.

## 6. Current Architecture Diagnosis

The current repository is a compact exporter with a mostly flat `app/` package.

Observed strengths:

- Report definitions are centralized in `app/reports.py`.
- Config parsing is typed through `AppConfig`.
- Project-relative path resolution is isolated in `app/paths.py`.
- Date range logic is isolated in `app/dates.py`.
- Unit tests already cover URL builders, date ranges, config/path resolution, and selected downloader helper behavior.
- Runtime and sensitive file handling is documented in `README.md`.

Observed coupling and refactor pressure:

- `app/downloaders.py` combines UI selectors, API calls, polling, retry behavior, file naming, filesystem writes, and result reporting.
- `app/main.py` combines orchestration, report-period selection, login/session lifecycle, and summary accounting.
- `app/auth.py` owns both session-state detection and manual login interaction.
- Output writes are distributed across `_move_download`, `_save_export_bytes`, `_download_from_history`, `_save_download`, and directory creation helpers.
- Network/live behavior is embedded in Playwright page evaluation calls and browser navigation.
- Tests focus on pure helpers and selected mocks, but they do not yet characterize full report-flow contracts or filesystem side effects.

Risk boundaries found by safe inspection:

- Network/live integrations: `page.goto`, Playwright downloads, `fetch` calls through `page.evaluate`, export status polling, and Herm Finance API endpoints.
- Session state: `config.session_file`, `load_session_state`, `save_session_state`, Playwright `storage_state`.
- Runtime writes: `logs/herm_export.log`, `exports/...`, temporary download files, final export files, and session storage state.
- Configuration boundary: `read_config("config/config.txt")`.

## 7. Target Architecture

The target should preserve current behavior while separating side-effect-heavy code from deterministic contracts.

Offline target modules now introduced:

```text
app/
  main.py                  # thin CLI/orchestration entrypoint
  config.py                # typed config loading and validation
  dates.py                 # pure period logic
  reports.py               # report catalog and URL/filter contracts
  paths.py                 # project/runtime path policy
  auth.py                  # auth/session lifecycle only
  browser.py               # Playwright lifecycle only
  downloaders.py           # temporary compatibility facade during migration
  export_flows.py          # UI export flow primitives
  export_history.py        # export queue/history polling and selection
  output_writer.py         # final file naming, temp move, overwrite policy
  orchestration.py         # pure report-period selection helpers
  run_summary.py           # run result accounting
```

Implemented characterization test structure:

```text
tests/
  test_report_contracts.py
  test_export_file_helpers.py
  test_orchestration.py
```

Do not create Mart or analytics implementation folders as part of exporter refactoring. If analytics work is requested later, define a separate `SPEC.md` and use the repository data-layer rules explicitly.

## 8. Refactor Principles

- Preserve public behavior first; improve structure second.
- Add characterization tests before moving logic.
- Move one responsibility at a time.
- Keep `app/downloaders.py` as a compatibility facade until migrated code is covered.
- Keep report definitions stable unless the task explicitly changes business/export rules.
- Keep output paths and filenames stable.
- Keep all live/network operations behind boundaries that can be mocked.
- Keep filesystem writes isolated and test them with temporary directories.
- Do not use real credentials, real session files, or real exports in tests.
- Prefer pure functions for URL construction, date ranges, path decisions, and output naming.

## 9. Phased Migration Plan

### Phase 0 — Characterization Baseline

- Status: completed offline.
- Added focused tests for report catalog invariants: codes, export directories, filename prefixes, repeat behavior, special cases.
- Added tests for report-period selection.
- Added tests for output helper behavior using `tmp_path`.
- Added tests for API export row selection and candidate filename matching.
- Do not run the live exporter in this phase.

### Phase 1 — Extract Output Writing

- Status: completed offline.
- Moved extension detection, move behavior, and byte-save behavior into `app/output_writer.py`.
- Kept existing `app/downloaders.py` helper names as imported compatibility aliases.
- Validated with full offline pytest.

### Phase 2 — Extract Export History and API Polling

- Status: completed offline.
- Moved row matching and polling logic into `app/export_history.py`.
- Kept Playwright/API row loading injectable for tests.
- Validated ready/fail behavior, old-row filtering, and filename candidate matching through existing and new tests.

### Phase 3 — Extract UI Export Flows

- Status: completed offline.
- Extracted reusable UI export primitives into `app/export_flows.py`.
- Kept selectors and wait behavior unchanged.
- Existing mock-based downloader tests cover key selectors and call behavior.

### Phase 4 — Thin Orchestration

- Status: completed offline.
- Split run summary into `app/run_summary.py`.
- Split report-period selection into `app/orchestration.py`.
- Kept `python -m app.main` as the unchanged public entrypoint.
- Added tests for regular reports, `budget_rows`, and `cons_budget` period selection.

### Phase 5 — Documentation and Safe Full Validation Decision

- Status: completed offline.
- Updated README with current code layout.
- Full offline pytest was safe and passed.
- Live exporter remains blocked unless explicitly approved and preceded by config/overwrite/output-impact checks that do not expose sensitive file contents.

## 10. Test and Validation Strategy

Safe checks for planning and structural refactors:

```bash
git status --short
git diff --name-only
.venv/bin/python -m pytest --collect-only -q
git status --short exports logs output state config/config.txt
```

Targeted tests added during offline refactor:

- Report contract tests for each `REPORT_DEFINITIONS` entry.
- Existing URL builder tests for protected query parameters remain in place.
- Period selection tests for completed months, budget rows, contractors, and consolidated budget.
- Output writer tests with `tmp_path`.
- Export queue tests with mocked rows.
- Existing UI flow tests with mocked Playwright `Page` remain in place.

Validation escalation:

- Run full unit tests only after confirming they do not call `python -m app.main`, launch a real browser, contact Herm Finance, read real config, read real session state, or write runtime folders.
- Run live exporter only with explicit approval and a written pre-run checklist.

What `pytest --collect-only` proves:

- Tests are importable and discoverable.

What it does not prove:

- Herm Finance login works.
- Exports download successfully.
- Output files are correct.
- UI selectors still match the live site.
- Runtime files remain unchanged during full execution.

## 11. Batch Checklist

Use this checklist for each future refactor batch:

- [ ] Confirm scope and allowed files.
- [ ] Confirm `config/config.txt` and `state/herm_session.json` are not needed.
- [ ] Run `git status --short`.
- [ ] Add or update characterization tests first.
- [ ] Make one small structural change.
- [ ] Run the smallest relevant tests.
- [ ] Run `.venv/bin/python -m pytest --collect-only -q`.
- [ ] Check `git diff --name-only`.
- [ ] Check `git status --short exports logs output state config/config.txt`.
- [ ] Document skipped validation and residual risk.
- [ ] Stop if a runtime/generated path changes unexpectedly.

## 12. Rollback Strategy

- Keep each refactor batch small enough to revert independently.
- Avoid moving code and changing behavior in the same batch.
- Keep old function names as wrappers during extraction when callers still depend on them.
- If tests fail after extraction, revert only the latest extraction batch.
- If runtime/generated files change unexpectedly, stop and inspect git status without opening sensitive contents.
- Do not use destructive git commands unless explicitly approved.
- Preserve `README.md` documented run commands and output locations unless a separate task changes them.

## 13. Risk Register

| Risk | Impact | Control |
|---|---|---|
| Live exporter accidentally runs | May contact Herm Finance and mutate logs, session state, exports, or external state | Do not run `python -m app.main` or `./run_hermes.command` without explicit approval |
| Sensitive session is opened | May expose auth/session material | Never open or print `state/herm_session.json` |
| Sensitive config is opened | May expose credentials or local runtime settings | Never open or print `config/config.txt` |
| Runtime output is modified | May corrupt exports or logs | Exclude runtime paths and check `git status --short exports logs output state config/config.txt` |
| Test collection is mistaken for behavior validation | False confidence | Clearly label collect-only as import/discovery validation |
| Downloader extraction changes behavior | Export regressions | Add characterization tests before moving code |
| Filename or output path changes silently | Downstream breakage | Protect report contract tests and output writer tests |
| UI selectors change during refactor | Live export failure | Keep selectors unchanged and covered by mock tests |
| API polling behavior changes | Wrong file may be downloaded | Preserve old-row filtering and ready/fail handling tests |
| Future analytics scope is mixed into exporter refactor | Architecture confusion | Require separate `SPEC.md` for Mart/analytics implementation |

## 14. Acceptance Criteria

This refactor foundation is complete when:

- [x] `REFACTOR_PLAN.md` exists.
- [x] The plan documents repository map, functional baseline, current risks, and target architecture.
- [x] The plan documents protected sensitive/runtime paths.
- [x] The plan documents phased migration steps.
- [x] The plan documents validation and rollback strategy.
- [x] No live exporter was run.
- [x] `state/herm_session.json` was not opened or modified.
- [x] `config/config.txt` was not opened or modified.
- [x] Runtime/generated paths were not modified.
- [x] `.venv/bin/python -m pytest --collect-only -q` passes after creating the plan.
- [x] `git status --short exports logs output state config/config.txt` shows no runtime/generated changes after creating the plan.
- [x] Safe offline refactor batches from this plan were completed.
- [x] Characterization tests were added or improved before behavior-preserving refactor work.

## 15. Open Questions

- Should `app/downloaders.py` remain as a long-term facade or be fully split once broader flow-level tests exist?
- Is there a stable expected manifest for all generated export files that can be used for contract tests without inspecting real exports?
- Should future live validation use a dry-run mode, a sandbox account, or a dedicated output directory before touching production-like exports?
