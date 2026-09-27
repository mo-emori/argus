# Test results

| Check | Result |
|---|---|
| Context Unicode boundary regression | PASS — 4 passed |
| P-0104/P-0107/P-0102/P-0100 targeted regression | PASS — 53 passed |
| Skill pytest | PASS — 163 passed |
| Repository pytest | PASS — 215 passed |
| 39 Context read-only scan | PASS — strict UTF-8 39/39, candidates 0 |
| Ruff | PASS; inaccessible cache-directory warnings only |
| Changed-scope strict Pyright | PASS — 0 errors |
| Repository-wide Pyright | BASELINE FINDINGS — 7 pre-existing unrelated errors in `tests/component/test_data_root_marker_store_contract.py` |
| Bandit | PASS |
| pip-audit | PASS — no known vulnerabilities |
| Active Human-facing Renderer scan | PASS — 40 tests passed |
| `git diff --check` | PASS; unrelated existing LF/CRLF warnings only |
| P-0108 evidence unchanged | PASS — 16 files, tree digest `6ffde0c70a7b02f0f13d2d22a890306837a1b0d11d546ecdb6a22535c65e2c31` |

The first new fixture attempted to manufacture U+301C corruption by strict CP932 decoding, but that byte sequence is invalid in strict CP932. The fixture was corrected to the real reversible `§` UTF-8/CP932 case; no production rule was relaxed. Final runs are all green except the documented repository-wide Pyright baseline.
