# SPEC

## Goal
Add a Herm Finance export branch for `account_balance_report` that saves files into `exports/account_balances/` with filenames prefixed `acc_balance_YYYY-MM-DD`, where the date is the last day of the month.

## Current state
- The project already exports other Herm Finance sections.
- The source URL is `https://herm.finance/ledger/reports/account_balance_report`.
- The current implementation already has an `account_balances` report entry, but its filename behavior uses monthly naming and does not match the requested `acc_balance_YYYY-MM-DD` pattern.
- The exact live UI flow for this branch is unknown from the request.

## Requirements
- Create or adjust the `account_balances` branch so files are saved in `exports/account_balances/`.
- Use filenames with the prefix `acc_balance_YYYY-MM-DD`.
- Use the last day of the month for `YYYY-MM-DD`.
- Keep existing report flows unchanged.
- Add tests for the new filename/path behavior.

## Constraints
- Make the smallest necessary change.
- Do not change unrelated report flows.
- Do not invent extra UI steps or filters beyond what is already known.
- Keep compatibility with the current launcher and export pipeline.

## Acceptance criteria
- Running the `account_balances` branch creates files under `exports/account_balances/`.
- Saved filenames use the `acc_balance_YYYY-MM-DD` prefix with the month-end date.
- Existing tests continue to pass.
- New tests cover the report definition and path naming for `account_balances`.

## Risks
- The live Herm Finance UI may require additional interaction not yet documented.
- The naming convention may need to match the actual exported filename returned by the site.
- The branch may need a different flow than the current API export if the site behavior differs from the code path.
