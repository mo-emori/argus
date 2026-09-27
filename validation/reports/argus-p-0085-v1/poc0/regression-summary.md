# ARGUS HSD Generation PoC-0 Regression Summary

## 判定

**PoC-0 PASS — STOP Human Review**

成功条件はHSD v0.1.4の合格ではなく、固定Oracleの既知欠陥をValidatorが検出することである。Critical expected finding 3件をすべて検出した。

| 指標 | 件数 |
|---|---:|
| Oracle | 8 |
| Expected findings | 3 |
| Detected | 3 |
| Missed | 0 |
| False positive | 0 |
| Review required | 1 |
| Detection rate | 100% |

## Gate別結果

- Gate-JP: 一般英語 `Data` を検出。正式概念 `Universe` と正式探索枝名は日本語文脈を確認してPASS。
- Gate-VALUE: 通知開始 `17:30` とBUSY Lease `1時間` の欠落を検出。`1か月Paper` はlabel近接を含め保存確認。
- Gate-STATE: Runner lifecycleの `INIT / RUNNING / RESUMING / END` を対象節内で保存確認。
- Gate-STRUCT: SDDの課題・目的labelを確認したが、HSDとの意味一致は機械判定せず `SEMANTIC_REVIEW_REQUIRED`。

## MISSED / FALSE_POSITIVE / REVIEW

- MISSED: なし
- FALSE_POSITIVE: なし
- REVIEW: `STRUCT-EXPLORATION-001` 1件

## 既知限界

- Gate-JPは固定Oracle tokenだけを判定し、全文のallowed terms governanceは実装していない。
- 条件付き許可語の日本語文脈は節内存在で確認し、厳密な初出距離や意味同一性は判定しない。
- Gate-VALUEのlabel proximityは文字距離による近似で、構文・意味関係を証明しない。
- Gate-STATEは指定Section内のidentifier存在を検査するが、遷移意味の完全性は証明しない。
- Gate-STRUCTは構造的存在だけを検査し、課題・目的・設計理由の意味保存はHuman/Semantic Reviewへ送る。
- Oracleは明確な少数事例だけであり、SDD全体の完全Oracleではない。

## 次段階

PoC-Aへ進むためのPoC-0機械条件は満たした。ただし本指示の終了条件に従いPoC-Aへは進まず、Human Reviewと明示承認を待つ。HSD、SDD、Design Sourceは変更していない。

## Verification

- Skill tests: 19 passed
- Repository tests: 215 passed（pytest cache作成権限warning 1件）
- Ruff: PASS
- Skill strict pyright: 0 errors
- Bandit: PASS
- pip-audit: No known vulnerabilities found
- Repository全体 pyright: 既存 `tests/component/test_data_root_marker_store_contract.py` のprivate usage / unknown lambda type 7件でFAIL（本PoC変更外）
