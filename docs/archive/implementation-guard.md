# Implementation Guard

## Gate checks
- `SPEC.md` exists: pass.
- `SPEC.md` is clear enough for execution: pass.
- `plan.md` exists: pass.
- `plan.md` is actionable and ordered: pass.
- `tasks.md` exists: pass.
- `tasks.md` is executable: pass.
- Acceptance criteria are explicit: pass.
- Scope lock is present: pass.
- Validation strategy is defined: pass.

## Scope consistency
- Scope is limited to README documentation for the Herm Finance Excel exporter.
- Current exporter behavior under `app/` is out of scope for changes.
- Runtime and sensitive file contents are out of scope for reading or printing.
- Future Mart and analytics implementation is out of scope.
- Validation is limited to README diff, git status, and safe pytest collection.

## Allowed execution
- Read `README.md` and planning/control artifacts.
- Update `README.md` with concise sections for:
  - project scope;
  - runtime folders and sensitive files;
  - safe operating rules;
  - future Mart / analytics relationship.
- Run:
  - `git diff -- README.md`
  - `git status --short`
  - `.venv/bin/python -m pytest --collect-only -q`

## Blocked or forbidden execution
- Do not edit Python code, tests, config, `.gitignore`, dependencies, runtime files, or generated outputs.
- Do not run `python -m app.main`.
- Do not run `./run_hermes.command`.
- Do not open or print `state/herm_session.json`.
- Do not open or print `config/config.txt`.
- Do not create `src/`, `data/raw/`, `data/stage/`, `data/mart`, or Mart implementation files.

## Known missing inputs
- None for documentation execution.
- Live Herm Finance behavior remains unverified by design.

## Guard status
- Ready for execution.
- No blockers to starting `run-tasks`.

## Execution readiness
- Ready for execution: yes.
- Next required step: `run-tasks`.

## Residual blockers
- none.
