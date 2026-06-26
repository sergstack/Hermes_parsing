# Risk Register — Hermes Refactor Foundation

| Risk | Impact | Control |
|---|---|---|
| Live exporter accidentally runs | May contact live systems or mutate external/runtime state | Do not run exporter commands; inspect scripts before executing |
| Sensitive session file is opened | May expose session/auth data | Never open `state/herm_session.json` |
| Sensitive config is opened | May expose credentials or tokens | Never open `config/config.txt` |
| Runtime/generated files are modified | May corrupt outputs or state | Exclude `exports`, `logs`, `output`, `state`, `config/config.txt`; check git status after |
| Test collection is mistaken for full validation | False sense of safety | Document that collect-only verifies import/collection, not behavior |
| Full tests trigger side effects | Runtime or live mutations | Run full/scoped tests only after confirming they are safe |
| Deep refactor changes behavior | Functional regression | First create refactor plan and characterization test strategy |
| Broad code movement breaks imports | Project instability | Stage migration in small batches |
| Output schema changes silently | Downstream breakage | Mark output contracts as protected until explicitly changed |
| README safety rules are ignored | Safety regression | Mirror rules in `REFACTOR_PLAN.md` |
| New dependencies are introduced | Environment instability | Do not add dependencies in this phase |
| Unrelated formatting causes noisy diff | Harder review and rollback | Do not reformat whole repository |
| Missing project map leads to bad architecture | Poor refactor direction | Build repository map before proposing target architecture |
| Hidden coupling is missed | Refactor breaks runtime behavior | Search for IO/config/state/export boundaries |
| Assumptions become undocumented decisions | Future confusion | Document all assumptions in `REFACTOR_PLAN.md` and final report |
