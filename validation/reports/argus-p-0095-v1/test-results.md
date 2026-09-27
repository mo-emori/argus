# Test Results

| 検証 | 結果 |
|---|---|
| P-0095 provenance gate | PASS |
| P-0095 mechanical gate | PASS（Repair 2回後） |
| P-0095 human-facing gate | PASS |
| active renderer scan | PASS、0件 |
| skill pytest | PASS、83 tests |
| repository pytest | PASS、215 tests |
| Ruff repository check | PASS（アクセス拒否対象の cache 警告あり） |
| skill Pyright | PASS、0 errors |
| repository Pyright | FAIL、既存 `tests/component/test_data_root_marker_store_contract.py` の7 errors |
| Bandit `src` | PASS |
| pip-audit | PASS、known vulnerability 0件 |

Pytest は既存 `.pytest_cache` を更新できない警告を出したが、テスト結果には影響しない。Repository Pyright の7件は本 PoC の変更範囲外であり、隠さず既知残件として記録する。

