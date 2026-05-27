# Scope Lock

## Allowed files
- `app/reports.py`
- `app/downloaders.py`
- `app/paths.py`
- `app/selectors.py`
- `tests/test_urls.py`
- `tests/test_downloaders.py`
- `tests/test_paths.py`
- `tests/test_main.py`
- `README.md`
- `SPEC.md`

## Forbidden files
- `plan.md`
- `tasks.md`
- `AGENTS.md`
- unrelated report modules
- files or branches from older Herm Finance flows unless explicitly required for `consolidated_plan_fact_monthly_report`

## Allowed actions
- Work only in the new branch for `consolidated_plan_fact_monthly_report`.
- Add or adjust the `consolidated_plan_fact_monthly_report` report definition.
- Add or adjust date-range and filter handling for the new report flow.
- Add or adjust path naming so the new branch writes to the target folder `cons_budget`.
- Add or adjust filename prefixing if needed for the new branch.
- Add or adjust tests for URL, path, and download behavior.
- Update documentation only if needed to reflect the new export flow.

## Forbidden actions
- Refactor unrelated export flows.
- Change existing Herm Finance behavior for other reports.
- Modify any older branch or flow unless it is required to support `consolidated_plan_fact_monthly_report`.
- Add new tools, workflows, or broad architectural changes.
- Modify data logic outside the `consolidated_plan_fact_monthly_report` flow.

## Public behavior
- Existing report flows must not change.
- Public behavior may change only for the `consolidated_plan_fact_monthly_report` flow.
