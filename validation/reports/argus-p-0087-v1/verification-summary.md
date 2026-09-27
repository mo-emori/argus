# ARGUS-P-0087-v1 Verification Summary

## Outcome

P-0086 の Human Review 指摘 F-01〜F-05 を Planning phase 内で修正した。HSD 本文、Writer、Freeze は実行していない。Planning Artifact は `PENDING` であり、実行境界は `STOP Human Review` である。

## Corrective evidence

- F-01: SDD §16 と §24.1 の明示的因果表だけを design reason として抽出した。2/39 Section に存在し、希薄性を WARNING とした。
- F-02: `前提` を明示する label/table row のみを premise とした。7/39 Section に存在し、真の不在を補完せず WARNING とした。
- F-03: semantic candidate を型と disposition に分離した。`API / OS / SHA` は `technical_term / REJECTED`、明示状態は `formal_state / CONFIRMED`、未知候補は `REVIEW_REQUIRED` とした。
- F-04: 旧 Coverage 1000 Unit を全件照合した。`SAME=927`、`MERGED=73`、`MISSING=0`。P-0086 の946件に加え、未配置だった SDD §14.3 の5 labelを配置して現行951件とした。現行固有は2件である。
- F-05: design reason、premise、semantic noise、baseline差分、assignment confidence の各 review signal を JSON/Markdown に表示した。

## Tests

- `pytest -q`: 215 passed。pytest cache の access warning 1件あり。
- Skill regression: 46 passed。PoC-0 PASS、INV-01〜INV-07 を維持。
- Deterministic regeneration: PASS。SHA-256 `44805F025F4E83D2FF08C3187F51AC417EC9F4278B26B6E499D319B002AD1D36`。
- `ruff check .`: PASS。既存の読み取り不能 cache に対する warning あり。
- `bandit -r src .codex/skills/argus-hsd-generation/scripts -q`: PASS。
- `pip-audit`: PASS、known vulnerability なし。
- `pyright`: FAIL。今回の変更外の `tests/component/test_data_root_marker_store_contract.py` に private API usage 1件と unknown lambda type 6件、計7件。

## Human Review signals

- Planning FAIL / WARNING / REVIEW_REQUIRED: 0 / 3 / 2
- Assignment REVIEW_REQUIRED: 114
- Semantic candidate: 825（confirmed state 51、rejected/review-required 725）
- Planning approval: PENDING

**STOP Human Review**
