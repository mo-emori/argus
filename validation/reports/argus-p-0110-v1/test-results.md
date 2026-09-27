# Test results

| Check | Result |
|---|---|
| P-0104 / P-0107 / P-0109 targeted regressions | PASS — 14 passed |
| Skill pytest | PASS — 163 passed |
| Repository pytest | PASS — 215 passed |
| Phase A Context Unicode handoff | PASS — strict UTF-8 3/3, candidates 0 |
| Ruff | PASS; inaccessible cache-directory warnings only |
| Changed-scope strict Pyright | N/A — no Python source changed by P-0110 |
| Repository-wide Pyright | BASELINE FINDINGS — 7 pre-existing unrelated errors in `tests/component/test_data_root_marker_store_contract.py` |
| Bandit | PASS |
| pip-audit | PASS — no known vulnerabilities |
| Active Writer/Renderer architecture scan | PASS — 34 passed |
| `git diff --check` | PASS; unrelated existing LF/CRLF warnings only |
| Artifact integrity | PASS — Design Source, SDD, Contexts, Coverage map, P-0108/P-0109 evidence, and canonical Full HSD unchanged |

Pytest emitted only the existing cache-directory access warning. No failing test or newly introduced type/security finding was hidden.
