# Plan

## Scope assumptions
- `SPEC.md` is the source of truth for this task.
- This is a documentation-only change.
- The current repository scope to document is Herm Finance Excel export.
- Mart and analytics implementation is out of scope for this task.
- Runtime and sensitive files must be named only by path; their contents must not be opened or exposed.

## Affected files / areas
- Planning artifacts:
  - `SPEC.md`
  - `plan.md`
  - `tasks.md`
- Execution target:
  - `README.md`
- Read-only verification:
  - `git diff -- README.md`
  - `git status --short`
  - `.venv/bin/python -m pytest --collect-only -q`

## Steps
1. Read `SPEC.md` and confirm documentation-only scope.
2. Read the existing `README.md` without opening sensitive runtime files.
3. Identify the smallest README location for scope and operations notes.
4. Add concise documentation for current project scope.
5. Add concise documentation for runtime folders and sensitive files.
6. Add concise safe operating rules.
7. Add concise clarification that Mart and analytics artifacts are future planning material, not current implementation.
8. Preserve existing setup, run, output, and report documentation.
9. Verify the README diff is limited to documentation scope.
10. Run safe validation commands listed in `SPEC.md`, or report why any command was not run.
11. Report changed files, commands run, validation results, blockers, and summary.

## Dependencies
- Step 2 depends on Step 1.
- Steps 4 through 7 depend on Step 3.
- Step 9 depends on documentation edits being complete.
- Step 10 depends on Step 9.
- Step 11 depends on validation results.

## Risks
- Opening or printing `state/herm_session.json` or `config/config.txt` could expose sensitive runtime data.
- Running the live exporter could modify logs, session state, exports, or external Herm Finance state.
- Changing output folder conventions could break the current exporter workflow.
- Over-editing README could obscure existing useful operational instructions.

## Validation strategy
- Use `git diff -- README.md` to verify only intended documentation changed.
- Use `git status --short` to confirm no runtime/generated files were changed by the task.
- Use `.venv/bin/python -m pytest --collect-only -q` only as safe test discovery, not full runtime validation.
- Do not run `python -m app.main` or `./run_hermes.command`.
