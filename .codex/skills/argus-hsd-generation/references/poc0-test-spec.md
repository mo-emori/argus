# PoC-0 Gate Regression Test Specification

## Purpose

SHA固定した既知失敗 HSD v0.1.4 に対し、事前固定Oracleの既知欠陥を4種類の機械Gateが検出できるか確認する。HSDの修正、再生成、PoC-A、Writer実行は行わない。

## Input gate

`failure_fixture_v0.1.4.json` の3入力pathとSHAを実測し、HSDヘッダ内のSDD / Design Source SHAとも照合する。一件でも不一致なら以降を実行しない。

## Frozen oracle

Validator実行前に `poc0_oracle_v0.1.json` を固定する。OracleはGate、scope、期待結果、critical、根拠locatorを持つ。実行後に期待結果を変更しない。

## Regression classification

- `DETECTED`: expected `FAIL` と actual `FAIL` が一致
- `MISSED`: expected `FAIL` だが actual が `FAIL` でない
- `FALSE_POSITIVE`: expected `PASS` だが actual が `FAIL`
- `REVIEW`: expected または actual が `REVIEW`
- `CONFIRMED`: expected `PASS` と actual `PASS` が一致

Critical expected finding が一件でも `MISSED` なら PoC-0 は FAIL とする。Detection rateだけで合否を決めない。

## Gate boundary

- Gate-JP: Oracle指定tokenを `UNCONDITIONAL / CONDITIONAL / PROHIBITED / UNCLASSIFIED` に分類する。正式語を単純allowlist化しない。
- Gate-VALUE: accepted representationとlabelの同一節内近接を検査する。欠落はFAIL、文脈不明はREVIEW。
- Gate-STATE: Oracle指定Section内だけでstate / identifierを検査する。
- Gate-STRUCT: 構造ラベルの機械存在を検査し、意味一致は `SEMANTIC_REVIEW_REQUIRED` とする。

## Stop

Validation ReportとRegression Summaryを出力したら `STOP Human Review` とする。

