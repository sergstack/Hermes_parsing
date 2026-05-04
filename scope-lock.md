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
- unrelated report modules unless required for `account_balances`

## Allowed actions
- Adjust the `account_balances` report definition.
- Add or adjust path naming so exports go to `exports/account_balances/`.
- Add or adjust filename logic so the prefix is `acc_balance_YYYY-MM-DD` using month-end dates.
- Add or adjust tests for URL, path, and download behavior.
- Update documentation only if needed to reflect the new export flow.

## Forbidden actions
- Refactor unrelated export flows.
- Change existing Herm Finance behavior for other reports.
- Add new tools, workflows, or broad architectural changes.
- Modify data logic outside the `account_balances` flow.

## Public behavior
- Existing report flows must not change.
- Public behavior may change only for the `account_balances` flow.
