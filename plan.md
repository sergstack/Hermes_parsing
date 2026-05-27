# Plan

## Phase 1: Report definition
1. Add a dedicated branch for `consolidated_plan_fact_monthly_report`.
2. Encode the full-period dates from the request URL.
3. Map the strict UI filters from the screenshots.

## Phase 2: Output contract
1. Write exports to the `cons_budget` folder.
2. Choose a filename prefix that matches the branch contract.
3. Keep existing report outputs unchanged.

## Phase 3: UI/export flow
1. Apply the visible filters before export.
2. Click `Показать`.
3. Click `Экспортировать всё`.

## Phase 4: Tests and docs
1. Add focused tests for URL construction and filter behavior.
2. Add focused tests for path naming and output placement.
3. Update README only if the new flow needs user-facing documentation.
