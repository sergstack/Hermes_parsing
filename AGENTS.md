# AGENTS.md

Make only the smallest necessary changes.

## Core rules

- Do not refactor unless required to complete the requested change.
- Do not invent files, commands, outputs, results, or passing tests.
- State assumptions explicitly when information is missing.
- If something cannot be verified, say so.
- Keep responses concise and factual.
- For complex or ambiguous tasks, investigate only as needed before making changes.
- Ask a clarifying question only when the task cannot be completed safely or correctly without it.

## Data and analytics rules

- Python and SQL perform ALL numeric calculations.
- LLM is ONLY allowed to interpret results, summarize, classify, and generate text.
- NEVER use LLM for numeric calculations, financial metrics, or aggregations.
- Always clearly separate raw vs stage vs mart vs report layers.
- Do NOT mix layers or data types without explicit transformation logic.
- Prefer reusable pipelines over one-off scripts.
- Design solutions to be compatible with scheduled execution when applicable.
- Do not introduce unnecessary complexity or new tools without clear justification.
- Maintain data integrity as highest priority.

## Project rules

- Preserve current Herm Finance flows unless the task explicitly requires a change.
- Treat UI selectors, waits, and API polling as fragile contracts.
- Avoid mass selector changes unless backed by evidence or a test.
- Keep public entrypoints stable during refactors when possible.
- Prefer minimal diffs and small, reviewable steps.

## Verification

- Run the smallest relevant check available for the change.
- If tests cannot be run, state why.
- For documentation-only changes, verify internal consistency.

## Useful commands

- `python -m pytest`
- `ruff check .`
- `ruff format --check .`
- `python -m app.main`

## Done criteria

- The change is minimal and matches the request.
- Verification was run or the blocker was stated.
- No unrelated behavior was changed.
