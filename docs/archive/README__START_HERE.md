# START HERE — Hermes Refactor Codex Package

This folder contains the execution package for Codex.

Codex must read the files in this order:

1. `README__START_HERE.md`
2. `CODEX_EXECUTION_BRIEF.md`
3. `ACCEPTANCE_CRITERIA.md`
4. `VALIDATION_PLAN.md`
5. `RISK_REGISTER.md`
6. `FINAL_REPORT_TEMPLATE.md`
7. `PROMPT__paste_into_codex.md`

## Mission

Safely analyze the repository and create a deep refactoring foundation without damaging existing functionality, sensitive runtime files, generated outputs, or live/exporter behavior.

## Hard Safety Rules

Do not open:

- `state/herm_session.json`
- `config/config.txt`
- any file that appears to contain tokens, cookies, credentials, session state, auth state, or personal sensitive data.

Do not run:

- live exporter;
- production exporter;
- commands that contact live systems;
- commands that require credentials/session;
- commands that write to runtime/generated paths.

Do not modify:

- `exports`
- `logs`
- `output`
- `state`
- `config/config.txt`

## Required Result

Create:

```text
REFACTOR_PLAN.md
```

The file must contain:

1. Purpose
2. Non-Negotiable Safety Rules
3. Current Repository Map
4. Functional Baseline
5. Sensitive and Runtime Files Policy
6. Current Architecture Diagnosis
7. Target Architecture
8. Refactor Principles
9. Phased Migration Plan
10. Test and Validation Strategy
11. Batch Checklist
12. Rollback Strategy
13. Risk Register
14. Acceptance Criteria
15. Open Questions
