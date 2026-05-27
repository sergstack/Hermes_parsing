# Tasks

## 1. Report branch
- [ ] Add `consolidated_plan_fact_monthly_report` to the report registry.
- [ ] Encode the full period from the request URL.
- [ ] Apply the strict UI filters from the screenshots.

## 2. Output contract
- [ ] Save files under `exports/cons_budget/`.
- [ ] Set a filename prefix that matches the branch contract.
- [ ] Keep existing report outputs unchanged.

## 3. UI flow
- [ ] Click `Показать` after filters are set.
- [ ] Click `Экспортировать всё` after results are shown.
- [ ] Confirm the export path is compatible with the current launcher.

## 4. Validation
- [ ] Add tests for the report URL and filter mapping.
- [ ] Add tests for the output path and filename contract.
- [ ] Run the smallest relevant checks for the new branch.

## 5. Documentation
- [ ] Update README only if the new flow needs user-facing documentation.
