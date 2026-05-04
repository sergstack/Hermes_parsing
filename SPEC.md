# SPEC

## Goal
Add a Herm Finance export branch for `consolidated_plan_fact_monthly_report` that:
- uses the full period from the first day to the last day of the year shown in the request URL
- applies the strict filters shown in the screenshots
- exports the result through the existing project workflow

## Current state
- The source page is `https://herm.finance/budgeting/reports/consolidated_plan_fact_monthly_report`.
- The request provides an example URL with `dates_period[0]=2026-01-01` and `dates_period[1]=2026-12-31`.
- The desired UI flow is known from the screenshots:
  - period start and end dates
  - all statuses selected
  - level `3`
  - empty `ЦФО`
  - project `Azp_admin`
  - `ВГО` excluded
  - `План-факт` columns selected
  - deviation checkbox empty
  - `План/Факт/IN-OUT(текущий)` empty
  - `План/Факт/IN-OUT(предыдущий)` empty
  - report currency `EUR`
  - then `Показать`
  - then `Экспортировать всё`
- The output folder is `cons_budget`.
- The filename prefix is `cons_budget`.

## Requirements
- Add a branch for `consolidated_plan_fact_monthly_report`.
- Encode the full-period date range from the requested period start to end.
- Apply the filters shown in the screenshots as strictly as possible.
- Save files into `exports/cons_budget/`.
- Use the `cons_budget` filename prefix.
- Keep existing report flows unchanged.
- Add tests for the new branch definition and URL/filter behavior.

## Constraints
- Make the smallest necessary change.
- Do not alter unrelated report flows.
- Do not invent additional filters, file naming rules, or output folders.
- Preserve compatibility with the current launcher and export pipeline.

## Acceptance criteria
- The new branch opens `consolidated_plan_fact_monthly_report`.
- The branch uses the requested full period and strict filters.
- The branch saves into `exports/cons_budget/`.
- The branch uses the `cons_budget` filename prefix.
- The branch reaches `Показать` and `Экспортировать всё` in the documented flow.
- Tests cover the new report definition and URL construction.

## Risks
- The exact UI selectors for the new page may differ from the screenshots.
- The source may require additional interaction not visible in the screenshots.
