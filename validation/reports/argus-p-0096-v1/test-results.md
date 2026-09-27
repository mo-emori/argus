# Test Results

| 検証 | 結果 |
|---|---|
| canonical authorization / binding | PASS |
| Section 3.4 provenance | PASS |
| Section 3.4 Mechanical Gate | PASS（mechanical repair 2回） |
| Section 3.4 Human-facing Gate | PASS |
| Section 3.4 Semantic Preservation Re-gate | PASS（110 PRESERVED） |
| Section 3.4 handoff independent review | PASS（35/35） |
| Section 3.5 Writer precondition | STOP（CONTEXT_INSUFFICIENT） |
| R-01〜R-04 | PASS |
| R-05 | FAIL |
| R-06 | NOT_RUN |
| Assembly Review | NOT_RUN |
| Skill pytest | PASS、96 tests |
| Repository pytest | PASS、215 tests |
| Ruff | PASS（既存cacheへのアクセス拒否警告あり） |
| Skill strict Pyright | PASS、0 errors |
| Repository Pyright | FAIL、既存test fileの7 errors |
| Bandit | PASS |
| pip-audit | PASS、known vulnerability 0件 |
| active Renderer scan | PASS、0件 |

Repository Pyrightの7件は既存の`tests/component/test_data_root_marker_store_contract.py`に限定され、本PoCの変更差分ではない。
