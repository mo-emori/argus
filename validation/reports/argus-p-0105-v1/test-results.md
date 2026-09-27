# Test Results

Executed at `2026-09-25T15:37:12.2806580+09:00`.

| Check | Result |
|---|---|
| P-0104 Unicode/protected-value regression | PASS — 6 passed |
| Skill pytest | PASS — 155 passed; cache-write warning only |
| Repository pytest | PASS — 215 passed; cache-write warning only |
| Ruff | PASS |
| Changed-scope strict Pyright | PASS — 0 errors |
| Bandit | PASS |
| pip-audit | PASS — no known vulnerabilities |
| Active Human-facing Renderer scan | PASS |
| `git diff --check` | PASS |
| Repository-wide Pyright | BASELINE FINDINGS — 7 pre-existing unrelated errors in `tests/component/test_data_root_marker_store_contract.py` |
