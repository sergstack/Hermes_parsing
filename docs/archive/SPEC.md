# SPEC

## Goal
- Update project documentation to clearly define this repository as the Herm Finance Excel exporter.
- Document runtime and sensitive folders used by the exporter.
- Clarify that current exporter code under `app/` is separate from future Mart or analytics planning artifacts.
- Do not change application behavior.

## Current state
- The current implementation is a Python 3.11+ Playwright exporter for Herm Finance reports.
- Current data flow is config -> login/session -> report definitions -> Playwright UI/API download -> `exports/` -> logs.
- The main entry point is `python -m app.main`.
- The macOS wrapper is `./run_hermes.command`.
- Exported Excel files are saved under `exports/`.
- Runtime or local state folders exist or are referenced: `exports/`, `logs/`, `state/`, `output/`, `config/config.txt`.
- `state/herm_session.json` is browser session state and must be treated as sensitive runtime data.
- Planning artifacts currently mention a future Mart layer under `src/pipeline/mart`, `data/stage`, and `data/mart`.
- The folders `src/`, `data/stage`, and `data/mart` were not found during read-only recon.
- Existing exporter code is under `app/`.

## Requirements
- Update documentation only.
- Make the repository scope explicit: current scope is Herm Finance Excel export, not Mart build execution.
- Prefer updating `README.md`; use another existing documentation file only if it is a better fit.
- Add or update concise documentation for:
  - project scope;
  - runtime folders and sensitive files;
  - safe operating rules;
  - relationship to future Mart or analytics layer.
- Document the purpose and safety handling of:
  - `config/config.txt`
  - `state/`
  - `exports/`
  - `logs/`
  - `output/`
- Clarify that `exports/` is the current exporter output location.
- Clarify that `exports/` is raw source material for downstream analytics, not a Mart output.
- Clarify that Mart and analytics artifacts are planning material unless and until a separate implementation task creates the required `src/` and `data/` structure.
- State that the current repository is not responsible for stage/mart/report transformation, financial reconciliation, dashboarding, or database loading.
- Include safety rules:
  - do not commit runtime state;
  - do not open, print, or share session/config contents;
  - do not run a full export unless explicitly approved;
  - check `overwrite` before reruns.
- Preserve existing run commands:
  - `python -m app.main`
  - `./run_hermes.command`
- Preserve existing test discovery command:
  - `.venv/bin/python -m pytest --collect-only -q`
- Keep the documentation concise and operational.

## Constraints
- Do not change application code.
- Do not change exporter behavior.
- Do not change config.
- Do not change `.gitignore`.
- Do not move output folders.
- Do not rename `exports/` to `data/raw/`.
- Do not create Mart implementation files.
- Do not create `src/`, `data/stage`, `data/mart`, or other pipeline folders.
- Do not edit runtime secrets, browser session files, real exports, logs, or generated screenshots.
- Do not open or print `state/herm_session.json`.
- Do not open or print `config/config.txt`.
- Do not run the live exporter or any command that writes exports, logs, session state, or external system data.
- Do not install packages or update dependencies.
- Do not change planning docs unless strictly necessary and explained.

## Acceptance criteria
- `README.md` or another justified existing documentation file identifies the repository as the Herm Finance Excel exporter.
- Documentation lists the main run commands and current output location.
- Documentation explains runtime and sensitive folders, including `state/herm_session.json`.
- Documentation includes visible safe operating rules.
- Documentation states that Mart and analytics materials are future planning artifacts, not current runnable implementation.
- Documentation does not claim that `src/pipeline/mart`, `data/stage`, or `data/mart` exists.
- No application behavior changes are made.
- No runtime data, session files, exports, logs, or generated artifacts are modified.
- `git diff -- README.md`, `git status --short`, and `.venv/bin/python -m pytest --collect-only -q` are run, or any skipped command is reported with a reason.

## Risks
- Existing planning artifacts can mislead future agents into treating Mart work as already implemented.
- `state/herm_session.json` may contain sensitive browser session data.
- `config/config.txt` may contain local runtime settings.
- Changing output folder conventions without a separate implementation task could break current exporter workflow.
- Documentation-only changes cannot verify live Herm Finance behavior without running the exporter.
