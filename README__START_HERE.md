# START HERE — Deep Safe Offline Refactor

This folder contains the execution package for Codex.

Codex must read these files first:

1. `README__START_HERE.md`
2. `CODEX_EXECUTION_BRIEF.md`
3. `ACCEPTANCE_CRITERIA.md`
4. `VALIDATION_PLAN.md`
5. `RISK_REGISTER.md`
6. `JUDGE_CHECKLIST.md`
7. `FINAL_REPORT_TEMPLATE.md`

## Mission

Execute a deep safe offline refactor of the project.

The goal is not to create another plan.
The goal is to complete all safe offline refactor batches or explicitly prove that remaining batches are blocked.

## Definition of Done

A. All safe offline refactor batches are completed, tested, and documented.

OR

B. All remaining batches are explicitly blocked with specific evidence.

## Hard Safety Rules

Do not open:

- `state/herm_session.json`
- `config/config.txt`
- files containing credentials, tokens, cookies, auth/session state, or personal sensitive data.

Do not run:

- live exporter;
- production exporter;
- commands contacting live systems;
- commands requiring credentials/session;
- commands writing to runtime/generated paths.

Do not modify:

- `exports`
- `logs`
- `output`
- `state`
- `config/config.txt`

Live validation is outside scope unless separately approved.
