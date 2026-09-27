# Test Results

Executed at `2026-09-25T14:23:52.5149617+09:00`.

| Check | Result |
|---|---|
| Skill pytest | PASS — 148 passed; cache-write warning only |
| Repository pytest | PASS — 215 passed; cache-write warning only |
| Ruff | PASS |
| Changed-scope strict Pyright | PASS — 0 errors |
| Bandit | PASS |
| pip-audit | PASS — no known vulnerabilities |
| Active Renderer scan | PASS |
| P-0101 English Writer provenance/content binding | PASS |
| Repository-wide Pyright | BASELINE FINDINGS — 7 pre-existing unrelated errors in `tests/component/test_data_root_marker_store_contract.py` |

The pipeline result is nevertheless `FAIL` because the repaired translation failed protected-value preservation.
