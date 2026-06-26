# Scope Lock

## Allowed files
- `README.md` may be updated during execution.
- `SPEC.md`, `plan.md`, and `tasks.md` may be read during execution.
- `scope-lock.md` and `implementation-guard.md` may be read during execution.

## Forbidden files
- Python application files under `app/` must not be changed.
- Test files under `tests/` must not be changed.
- `config/config.txt` must not be opened, printed, or changed.
- `state/herm_session.json` must not be opened, printed, or changed.
- `.gitignore` must not be changed.
- Dependency files must not be changed.
- Runtime/generated folders must not be changed:
  - `exports/`
  - `logs/`
  - `output/`
  - `state/`
- Mart or analytics implementation folders must not be created:
  - `src/`
  - `data/raw/`
  - `data/stage/`
  - `data/mart/`

## Allowed actions
- Read `SPEC.md`, `plan.md`, `tasks.md`, `scope-lock.md`, and `implementation-guard.md`.
- Read `README.md`.
- Edit `README.md` only for the documentation described in `SPEC.md`.
- Run safe validation commands:
  - `git diff -- README.md`
  - `git status --short`
  - `.venv/bin/python -m pytest --collect-only -q`

## Forbidden actions
- Do not change application behavior.
- Do not change Python code.
- Do not change config.
- Do not change `.gitignore`.
- Do not run the live exporter:
  - `python -m app.main`
  - `./run_hermes.command`
- Do not open or print sensitive runtime file contents:
  - `state/herm_session.json`
  - `config/config.txt`
- Do not move, rename, or rewrite `exports/`.
- Do not create Mart or data pipeline implementation files.
- Do not install packages or update dependencies.
- Do not modify runtime/generated exports, logs, state, or debug output.

## Public behavior
- Public application behavior must not change.
- Only documentation behavior changes are allowed.

## Notes
- This is a documentation-only scope clarification task.
- Approval required before execution: no.
- Live exporter validation is intentionally out of scope because it can touch Herm Finance, logs, session state, and exports.
