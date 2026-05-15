# AGENTS.md

Version: v02
Status: active candidate
Scope: repository-level Codex instructions

## Purpose

This project implements financial data pipelines, analytics, reporting, and automation workflows.

The goal is to:

- automate ingestion and transformations;
- produce reliable analytical outputs;
- minimize manual work;
- keep financial logic deterministic;
- make workflows reusable and cron-ready when applicable;
- preserve data integrity, reproducibility, and auditability.

---

## Project-specific status

This file is a project-level `AGENTS.md`.

It adds repository-specific rules on top of the global Codex instructions.

Local project rules may clarify project behavior, but must not weaken:

- data integrity;
- reproducibility;
- financial-control requirements;
- explicit user instructions;
- global source discipline;
- global safety boundaries.

---

## Standard commands

Use existing commands before inventing alternatives.

Replace `[fill in]` before marking this file as fully active.

```bash
# Install
[fill in]

# Test
[fill in]

# Targeted test
[fill in]

# Lint
[fill in]

# Typecheck
[fill in]

# Build
[fill in]

# Run main pipeline
[fill in]

# Run smoke check
[fill in]
```

If a command is unknown:

- do not invent it;
- inspect existing files first, such as `README.md`, `pyproject.toml`, `package.json`, `Makefile`, `scripts/`, or project docs;
- if still unknown, report it as not found.

---

## Non-negotiable rules

- Do not invent data, files, commands, outputs, test results, or passing checks.
- Do not refactor unless required to complete the requested change.
- Do not change architecture without explicit request.
- Do not overwrite existing files unless instructed.
- Keep changes minimal and targeted.
- If information is missing, state assumptions explicitly.
- If something cannot be verified, say so clearly.
- Do not claim that tests, checks, scripts, or pipelines passed unless they were actually run and passed.
- Do not create speculative features, unused abstractions, or unnecessary configuration.

---

## Computation rules

- Python and SQL perform ALL numeric calculations.
- LLM must NOT calculate financial values.
- LLM is allowed only to:
  - interpret;
  - summarize;
  - classify;
  - generate text;
  - review outputs.

For financial or analytical work:

- calculations must be reproducible;
- formulas and transformations must be explicit;
- assumptions must be visible;
- periods and currencies must be identified;
- reasons for variances must not be invented.

---

## Mandatory data folder rule

For analytical and financial projects, always use the classic analytical folder structure:

```text
data/raw/ → data/stage/ → data/mart/ → data/report/
```

Rules:

- `data/raw/` is the input folder.
- Do not create a separate `input/` folder unless explicitly requested.
- Do not create separate export folders unless explicitly requested.
- Store final exports inside `data/report/`.
- `data/report/` is for final user-facing outputs only.
- Do not store intermediate data or source-of-truth data in `data/report/`.

---

## Data pipeline architecture

This project uses two separate but connected structures.

### File layer

- `data/raw/` — input folder: incoming source files, unchanged input data.
- `data/stage/` — cleaned and normalized intermediate files.
- `data/mart/` — deterministic analytical outputs ready for reporting.
- `data/report/` — final reports, summaries, exports, and LLM-generated text outputs.
- `data/sample/` — small test datasets for development and smoke tests.

### Database / SQL layer

- `raw.*` — loaded raw tables, no business logic.
- `stage.*` — normalized and cleaned working layer.
- `mart.*` — deterministic analytical and reporting-ready layer.
- `report` — presentation layer, summaries, LLM outputs.

### Layer rules

- Do NOT confuse the file layer with the database layer.
- `data/raw/` is the input folder.
- `data/raw/` is not the same as `raw.*`.
- Do NOT place business logic in `raw.*`.
- Do NOT write transformed files back to `data/raw/`.
- Do NOT skip `data/stage/` or `stage.*` without explicit reason.
- `data/mart/` and `mart.*` must be reproducible and deterministic.
- `data/report/` and report layer must not become the source of truth.

---

## SQL rules

- Prefer SQL for transformations and aggregations.
- Queries must be explicit, readable, and deterministic.
- Avoid hidden logic and implicit joins.
- Always consider duplicates and nulls.
- Use idempotent logic where possible.
- Do not place business logic in raw layers.
- Do not hide transformations in unclear CTE names or undocumented scripts.
- When changing joins, check row counts, duplicates, and null behavior.

---

## Python rules

Python is used for:

- orchestration;
- file processing;
- API calls;
- pipeline coordination;
- validation helpers;
- reproducible calculation scripts when SQL is not the right tool.

Rules:

- Do NOT duplicate SQL business logic in Python unless explicitly justified.
- Keep scripts simple and modular.
- Prefer clear functions over clever abstractions.
- Keep file paths explicit and aligned with the data layer rules.
- Do not add new dependencies without approval or clear necessity.
- For cron-ready workflows, prefer deterministic logs and stable outputs.

---

## Workflow rules

For non-trivial tasks, follow this sequence:

1. `SPEC.md`
2. `plan.md`
3. `tasks.md`
4. execution
5. testing
6. validation
7. documentation

Do NOT skip these steps unless the task is clearly trivial.

For trivial or narrowly scoped changes:

- do not create `SPEC.md`, `plan.md`, or `tasks.md` unless explicitly requested;
- make the smallest safe change;
- run the smallest relevant check if available;
- report what was and was not verified.

A task is non-trivial if it:

- affects multiple files or subsystems;
- changes data pipeline behavior;
- changes financial logic, metrics, reports, or calculations;
- changes scheduling, cron, orchestration, or production-like execution;
- changes project structure;
- affects skills, `AGENTS.md`, validation, or workflow rules;
- requires architecture, sequencing, or acceptance criteria.

---

## Skills structure rules

This project may use two skill scopes:

1. Global/user skills
2. Repository-specific skills

### Global/user skills

Use global skills for reusable workflows that apply across many projects:

- planning;
- scope control;
- implementation guard;
- smoke tests;
- pipeline validation;
- financial review;
- documentation updates;
- terminal workflows;
- browser / playwright workflows;
- Context7 documentation lookup.

Do not duplicate global skills inside the repository unless the project needs a modified project-specific version.

If a global skill is updated, restart Codex if required by the current runtime.

### Repository-specific skills

Create repository-specific skills only when the workflow is unique to this project.

Repository-specific skills must be created inside:

```text
.agents/skills/<skill-folder>/SKILL.md
```

Rules:

- The file name must be exactly `SKILL.md`.
- Each `SKILL.md` must include `name` and `description`.
- Do not create placeholder skill folders without a valid `SKILL.md`.
- Do not create duplicate skills with the same `name`.
- Keep skill descriptions short, specific, and trigger-oriented.
- Do not create repo skills for workflows already covered by global skills.

---

## Allowed skill groups

- `[PLAN]`
- `[CONTROL]`
- `[EXEC]`
- `[TEST]`
- `[CHECK]`
- `[THINK]`
- `[DOC]`
- `[FLOW]`
- `[TOOL]`

---

## Skill routing rules

Use skills whenever a matching workflow exists.

Do not improvise repeated workflows from scratch if a suitable skill exists.

Do not activate heavy skills for trivial changes.

### Mandatory skill triggers

Use `[PLAN] scaffold-project-structure` when:

- a new project, module, or workspace is being created;
- required project folders/files are missing.

Use `[PLAN] spec-writer` when:

- the task is new;
- requirements are unclear;
- the change affects multiple files or subsystems;
- the user asks for a structured task definition.

Use `[PLAN] plan-builder` when:

- `SPEC.md` exists and implementation has not started;
- the task has more than one meaningful step;
- architecture or execution order matters.

Use `[PLAN] task-breakdown` when:

- `plan.md` exists;
- implementation requires multiple actionable steps;
- `tasks.md` is missing, incomplete, or too abstract.

Use `[CONTROL] control-orchestrator` when:

- planning is complete;
- execution readiness needs control gates;
- scope-lock or implementation-guard may be required.

Use `[CONTROL] scope-lock` when:

- execution is about to begin;
- refactor, `AGENTS.md`, or multi-file changes are involved;
- allowed files, forbidden files, allowed actions, or forbidden actions must be fixed.

Use `[CONTROL] implementation-guard` when:

- `tasks.md` exists;
- scope-lock exists;
- execution is about to start.

Use `[EXEC] run-tasks` when:

- `tasks.md` exists and execution should proceed in order.

Use `[EXEC] minimal-change-implementer` when:

- code or SQL changes are required;
- the task should be implemented with minimal impact;
- refactoring is not the goal.

Use `[TEST] smoke-tests` when:

- code, SQL, ETL, or pipeline logic changed.

Use `[CHECK] check-orchestrator` when:

- execution and smoke-tests are complete;
- changed files, task scope, or test results indicate material validation may be needed.

Use `[CHECK] pipeline-validator` when:

- the task affects `data/raw`, `data/stage`, `data/mart`, `data/report`, or `data/sample`;
- the task affects `raw.*`, `stage.*`, `mart.*`, or `report`;
- joins, duplicates, missing data, idempotency, or schema transitions are relevant.

Use `[CHECK] pipeline-readiness` when:

- the result is intended for cron, scheduled use, or production-like execution.

Use `[CHECK] financial-reviewer` when:

- financial logic, metrics, reports, or calculations are affected.

Use `[CHECK] llm-report-judge` when:

- the output includes an LLM-generated report, summary, note, or insight layer.

Use `[CHECK] acceptance-check` when:

- implementation is complete;
- final completion requires comparison with `SPEC.md` or acceptance criteria.

Use `[THINK] second-opinion` when:

- the solution is uncertain;
- multiple approaches are possible;
- deeper reasoning is needed before finalizing.

Use `[DOC] update-docs` when:

- behavior, workflow, setup, or outputs changed.

Use `[FLOW] run-full-pipeline` when:

- the task requires an end-to-end workflow;
- multiple stages are needed from planning through validation and docs;
- the task is important enough that validation must not be skipped.

Use `[TOOL]` skills only when:

- a supporting tool capability is needed;
- the task cannot be completed reliably with the current context alone.

---

## Escalation rules

Start with the lowest-cost suitable workflow.

Escalate to deeper reasoning only when:

- the task is complex or ambiguous;
- the first result is incomplete or uncertain;
- architectural or analytical reasoning is required;
- validation reveals unresolved issues.

Use review/check mode before finalizing important outputs.

Do not escalate only because a task looks interesting.

---

## Validation rules

Before completing any task:

- Run smoke tests if code changed.
- Validate pipelines if data layer changed.
- Validate financial logic if calculations changed.
- Validate LLM outputs if reports were generated.
- Run acceptance-check when implementation must be compared to `SPEC.md` or acceptance criteria.

If validation cannot be performed, explicitly state why.

Do not claim validation was performed unless it was actually performed.

---

## Pipeline safety

For any pipeline changes:

- ensure idempotency;
- ensure no duplicate data is created;
- ensure joins are correct;
- ensure missing data is handled;
- ensure input files are read only from `data/raw` or `data/sample`;
- ensure intermediate transformed files are written to `data/stage`;
- ensure deterministic analytical outputs are written to `data/mart`;
- ensure final reports, summaries, exports, and LLM-generated text outputs are written only to `data/report`;
- ensure file transformations follow `data/raw → data/stage → data/mart → data/report` when files are used;
- ensure SQL transformations follow `raw.* → stage.* → mart.* → report` when database layers are used.

---

## Reporting rules

LLM-generated reports must:

- be grounded in actual data;
- not invent facts;
- highlight risks and anomalies;
- not perform calculations;
- distinguish facts, assumptions, anomalies, and recommendations;
- mention periods and currencies when relevant.

---

## Documentation rules

Update documentation when:

- behavior changes;
- pipeline changes;
- new components are added;
- setup or usage changes;
- output locations change;
- validation or execution workflow changes.

Keep documentation:

- concise;
- practical;
- executable.

Do not rewrite unrelated documentation.

---

## Output format

Final response must always use these sections, in this order:

1. changed files
2. commands run
3. test results
4. blockers
5. final summary

Section rules:

- `changed files`: list only files actually modified; if none, write `none`.
- `commands run`: list only commands actually executed; if none, write `none`.
- `test results`: report only tests actually run and their real outcomes; if none, write `not run`.
- `blockers`: list anything preventing completion; include material assumptions here if they affect completion; otherwise write `none`.
- `final summary`: 1–3 sentences, no hype.

Do not include extra final sections unless explicitly requested.

Progress updates are allowed during execution.

The final answer must still use only the required final output sections.

---

## Progress reporting rules

For non-trivial tasks, Codex must provide short progress updates during execution.

Progress updates are required when:

- starting a major phase of work;
- before running a command that may modify files, dependencies, environment, data, or generated outputs;
- before starting a potentially long-running process;
- after completing a meaningful milestone;
- when a blocker, uncertainty, failed command, or changed assumption appears.

Progress updates must be concise:

- one short message;
- no hidden reasoning;
- no step-by-step internal thought process;
- no repeated updates for small actions;
- no progress messages for trivial reads, searches, formatting, or tiny edits.

Use this format when practical:

```text
Progress: <phase> — <what is happening / what changed / what is blocked>
```

Progress updates do not replace the final required output format.

For Python scripts:

- Add progress indicators only when useful for long-running loops, file processing, API calls, batch jobs, or data pipelines.
- Prefer `logging` or phase-based status messages for cron-ready, batch, pipeline, or production-like workflows.
- Use `tqdm` only for interactive scripts or notebooks where a progress bar is useful and the dependency is already available.
- Do not add a new dependency only for progress reporting unless explicitly requested.
- Do not add progress indicators to tiny scripts, library functions, tests, or simple one-off helpers.
- Progress reporting must not change financial logic, numeric calculations, deterministic outputs, schemas, or file locations.

When unsure, prefer minimal phase logging over a visual progress bar.
