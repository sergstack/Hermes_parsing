# Codex Refactor Risks

| Risk | Control | Validation |
|---|---|---|
| Stopping after planning | Execute batches until completed/blocked | Final report batch table |
| Untested behavior change | Add/update tests with each code batch | `.venv/bin/python -m pytest -q` |
| Live command accidentally run | Keep validation offline-only | Commands-run evidence |
| Sensitive file opened | Use git metadata only for protected paths | No command opens sensitive paths |
| Runtime/generated path modified | Use temp dirs and mocks | `git status --short .auth downloads state logs exports output config/config.txt` |
| Output schema drift | Do not change report filenames/schema without approval | Tests and diff review |
| Broad refactor causing regression | Keep batches small | Per-batch validation |
| Docs diverging from code | Update docs only for behavior/contract changes | Final diff review |
| Tests only checking happy path | Include failure/edge cases for touched code | Test names and assertions |
| Final report hiding remaining work | Require completed/blocked batch status | Acceptance check |
