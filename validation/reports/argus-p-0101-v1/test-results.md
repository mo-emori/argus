# ARGUS-P-0101-v1 Test Results

- HSD Generation Skill pytest: 138 passed
- Repository pytest: 215 passed
- Ruff: PASS
- Changed-script strict Pyright: 0 errors
- Bandit: PASS
- pip-audit: No known vulnerabilities found
- Active Renderer scan: 0 findings（Skill pytest）
- Repository Pyright: 7 pre-existing errors in `tests/component/test_data_root_marker_store_contract.py`; P-0101起因ではない

pytestは既存`.pytest_cache`へのアクセス警告を1件報告したが、テスト結果への影響はない。

