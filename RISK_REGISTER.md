# Risk Register — Deep Safe Offline Refactor

| Risk | Impact | Control |
|---|---|---|
| Codex stops after planning | No real refactor is done | Acceptance criteria require source/test changes or explicit blocker |
| Sensitive file opened | Credentials/session exposure | Never open `state/herm_session.json` or `config/config.txt` |
| Live exporter runs | Live system contact/runtime mutation | Live validation is out of scope |
| Runtime/generated files changed | Data corruption or noisy diff | Protected path checks after every batch |
| Full pytest triggers side effects | Runtime mutation | Inspect tests; run subset if full pytest unsafe |
| Behavior changes silently | Regression | Add characterization tests before/with refactor |
| Output schema changes | Downstream breakage | Output schema changes are out of scope |
| Broad restructuring breaks imports | Project instability | Small batches only |
| Formatting-only diff hides changes | Hard review | No broad formatting-only diffs |
| New dependency destabilizes env | Install/runtime risk | Avoid new dependencies |
| Remaining work hidden as “next step” | Premature stop | Final report forbidden if safe batch remains |
| Live risks remain unvalidated | False confidence | Explicitly document live validation as separate approval scope |
