# Implementation Guard

## Gate checks
- `SPEC.md` exists and describes the `consolidated_plan_fact_monthly_report` export request.
- The requested target output folder is `cons_budget`.
- `plan.md` exists and provides an implementation sequence.
- `tasks.md` exists and is already executable.
- Acceptance criteria are explicit in `SPEC.md`.
- `scope-lock.md` is present and limits changes to the `consolidated_plan_fact_monthly_report` flow, including the `cons_budget` output folder.
- Validation strategy is defined: add focused tests for report definition, path naming, and export behavior.

## Readiness
- Execution may start.

## Blockers
- None.
