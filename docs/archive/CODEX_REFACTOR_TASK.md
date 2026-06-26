# Codex Refactor Task

## Mission

Complete the remaining safe offline code refactor for the Hermes exporter. This task changes production code, tests, and only the docs/contracts needed to keep behavior reproducible.

## Scope

- Inspect current code and tests without opening sensitive/runtime files.
- Identify concrete executable refactor batches.
- Execute all safe batches until no safe executable batch remains.
- Validate with offline tests and protected-path checks.

## Out Of Scope

- Live exporter runs.
- Production pipeline runs.
- Auth/session refresh.
- Changes to output schemas, report filters, filenames, credentials, or session handling.
- Opening `state/herm_session.json` or `config/config.txt`.
- Modifying `exports/`, `logs/`, `output/`, `downloads/`, `state/`, `.auth/`, or `config/config.txt`.

## Hard Safety Rules

- Use temp dirs, mocks, and pure-function tests only.
- Do not read or print sensitive file contents.
- Do not contact live systems.
- Keep diffs minimal and behavior-preserving unless a contract update is explicit.

## Execution Loop

1. Inspect safe source/test/docs.
2. Select the next pending safe batch.
3. Add/update tests for the behavior.
4. Implement the smallest refactor.
5. Run validation.
6. Check protected paths.
7. Mark the batch completed or blocked with evidence.

## Definition Of Done

A: all safe executable code refactor batches are completed and validated.

B: remaining batches are blocked by named safety, dependency, permission, or product-decision blockers.

## Forbidden Outputs

Do not stop with only a plan, checklist, recommendation, task-file update, or a final report while safe executable code work remains.

## Final Self-Check

- No safe executable code batch remains pending.
- No offline test gap remains that can be safely closed now.
- No duplicated/mixed responsibility area remains that can be safely improved without live access.
- Final report does not hide executable work as a next step.

## Executable Refactor Batches

| Batch | Status | Reason |
|---|---|---|
| Batch 1 - Separate export result classification from summary mutation | completed | Moved summary accounting to `RunSummary.record_result`; validated by `tests/test_orchestration.py`. |
| Batch 2 - Extract report output target resolution | completed | Added `resolve_report_output_target`; downloader still uses same filenames/paths/markers. |
| Batch 3 - Add output target contract tests | completed | Added offline tests for monthly marker, single report, and account balance target contracts. |
