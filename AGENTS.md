# Argus Repository Instructions

このファイルは、このリポジトリで Codex が作業するときの恒久的な開発指示である。

## 1. 正本と派生文書

設計の正本は、以下の Design Source とする。

- `docs/source/argus_design_source_v0.1.md`

以下は Design Source から変換・生成された派生文書であり、Design Source と同格の正本ではない。

- `docs/model/argus_structured_design_model_v0.1.md`
- `docs/design/argus_system_design_v0.1.md`
- `docs/test/argus_test_strategy_v0.1.3.md`
- `docs/adr/argus_architecture_decision_records_v0.1.md`

設計判断が必要な場合は Design Source を優先する。派生文書は、その目的に応じた構造化・表示・検証・意思決定履歴の View として参照するが、Design Source の内容を上書きする根拠にしない。Design Source、派生文書、実装の間に矛盾がある場合は、勝手に補完せず、矛盾の内容を報告する。

## 2. 開発原則

- Human-in-the-loop を維持する。
- Broker API による自動発注を実装しない。
- TEST / PAPER / LIVE の分離を破らない。
- Risk / Environment Binding / Approval / Cost Control は fail-closed とする。
- Canonical State は Single Writer + Atomic Commit とする。
- 外部 API を Business Logic から直接呼ばない。
- ExternalServiceGateway / Provider Adapter 境界を維持する。
- 新しい有料サービス、増額、有料 Fallback を勝手に追加しない。

## 3. データ

- 大容量 Data Root は `L:\emori\InvestmentAgentData` とする。
- drive letter のみを信用せず、marker identity を検証する。
- Raw immutable data を書き換えない。
- TEST / PAPER / LIVE 間で state または data を混在させない。

## 4. 実装作業

- 変更前に関連する設計文書とテスト戦略を確認する。
- 小さい単位で実装する。
- 実装と同時にテストを追加する。
- 既存テストを壊さない。
- 型チェックを維持する。
- 不要な依存パッケージを追加しない。
- 仕様にない機能を勝手に実装しない。

## 5. Verification

変更後は、原則として以下を実行する。

- `pytest`
- `ruff`
- `pyright`
- `bandit`
- `pip-audit`

失敗した場合は隠さず、結果を報告する。

## 6. Git

- ユーザーの既存の未コミット変更を勝手に削除または revert しない。
- unrelated なファイルを変更しない。
- `.pyc`、`__pycache__`、pytest cache などの生成物をコミット対象にしない。
- `git reset --hard`、`git clean` などの破壊的操作を勝手に実行しない。
