# Tasks

## Preparation
- [ ] Read `SPEC.md`.
- [ ] Read `README.md`.
- [ ] Confirm the task is documentation-only.
- [ ] Confirm sensitive/runtime file contents are not needed.

## Documentation edits
- [ ] Update `README.md` with a clear `Project scope` section.
- [ ] Document current responsibility: Herm Finance authentication, report UI/API access, Excel export, and saving outputs under `exports/`.
- [ ] Document out-of-scope responsibilities: stage/mart/report transformation, financial reconciliation, dashboarding, and database loading.
- [ ] Document current data flow: config -> login/session -> report definitions -> Playwright UI/API download -> `exports/` -> logs.
- [ ] Add a `Runtime folders and sensitive files` section.
- [ ] Include `exports/`, `logs/`, `output/`, `state/`, `state/herm_session.json`, and `config/config.txt`.
- [ ] State that `state/herm_session.json` and `config/config.txt` are sensitive/local runtime files.
- [ ] Add safe operating rules for full exports, `overwrite`, session/config contents, and downstream Mart work.
- [ ] Add a `Future Mart / analytics layer` section.
- [ ] State that Mart planning artifacts do not mean Mart implementation currently exists.
- [ ] State that any Mart implementation requires a separate SPEC.
- [ ] Preserve existing useful README setup, run, output, and report details.

## Forbidden actions
- [ ] Do not change Python code.
- [ ] Do not change config.
- [ ] Do not change `.gitignore`.
- [ ] Do not move or rename `exports/`.
- [ ] Do not create `data/raw`, `data/stage`, `data/mart`, `src/`, or Mart implementation files.
- [ ] Do not open or print `state/herm_session.json`.
- [ ] Do not open or print `config/config.txt`.
- [ ] Do not run `python -m app.main`.
- [ ] Do not run `./run_hermes.command`.
- [ ] Do not change runtime/generated exports, logs, state, or output artifacts.

## Validation
- [ ] Run `git diff -- README.md`.
- [ ] Run `git status --short`.
- [ ] Run `.venv/bin/python -m pytest --collect-only -q`, or report why it was not run.
- [ ] Confirm no application behavior changed.
- [ ] Confirm no runtime/generated files were modified by this task.

## Acceptance mapping
- README states current project scope: documentation edits section.
- README separates exporter from future Mart planning: `Future Mart / analytics layer` task.
- Sensitive files are named without exposing contents: runtime/sensitive file tasks and forbidden actions.
- Runtime folders are documented: runtime folders section task.
- Safe operating rules are visible: safe operating rules task.
- No code or generated files changed: forbidden actions and validation tasks.
- Test collection reported: validation tasks.
