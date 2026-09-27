## 6.5 Secret・データ保護

境界ごとの許可経路と制約を明示する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 責務の分け方

人・System・外部Service・Environment・Storage・Data種別の境界が暗黙だと、禁止された越境が起き得る。

### 境界での受け渡し

| 観点 | 設計上の内容 |
|---|---|
| problems | 人・System・外部Service・Environment・Storage・Data種別の境界が暗黙だと、禁止された越境が起き得る。 |
| purposes | 境界ごとの許可経路と制約を明示する。 |
| processes | Human/System、Provider、Commit、Dev/Runtime、TEST/PAPER/LIVE、Storage、`Data`、履歴境界。 ／ ／ 人／システム ／ 人の判断・承認・Broker操作 ／ ARGUSの提案・自動処理 ／ Proposal Viewとtyped Command / Fact。通知表示を承認とみなさない ／ §4.3、§11〜12、§24 ／ ／ ／ ARGUS／外部サービス ／ Domain / Application ／ Provider API / SDK / Schema ／ ExternalServiceGatewayとProvider Adapterのみ。Business Logicから直接呼ばない ／ §37A ／ ／ ／ 外部副作用／Local Commit ／ API利用コスト、外部応答 ／ Canonical State ／ Durable Stage、provenance、idempotency。外部副作用をRollback可能と仮定しない ／ §2.3、§2.5 ／ ／ ／ 開発／実行 ／ `InvestmentAgent-Dev` ／ `InvestmentAgent` Runtime ／ Runtime停止、Backup、手動Deploy、Schema確認。state/data/configを上書きしない ／ §4.1、§4.6 ／ ／ ／ TEST／PAPER／LIVE ／ 各環境のState/`Data` Root ／ 他環境 ／ 異なるstate_id / environment / marker。Mismatch時は起動・write拒否 ／ §4.1、§46B ／ ／ ／ 内蔵SSD／外付けData Root ／ 現在State、Runtime、recent backup ／ Raw / normalized / historical / archive ／ Storage Managerとmarker identityで接続。drive letterだけを信用しない ／ §4.1、§4.7 ／ ／ ／ 事実／観測／判断 ／ Facts ／ Observations / Judgments ／ Canonical Envelope内で領域分離し、導出値と事実を混同しない ／ §13.1 ／ ／ ／ Current State／履歴 ／ `state/portfolio.json` ／ append-only archive / stage ／ ID、hash、range、high-water markで参照し、Compactionで履歴を消さない ／ §13.4 ／ |
| actors_authorities | Human ／ ARGUS ／ Broker |
| boundaries | Human/System、Provider、Commit、Dev/Runtime、TEST/PAPER/LIVE、Storage、`Data`、履歴境界。 |

### 権限を越えないために

境界ごとの許可経路と制約を明示する。 Human/System、Provider、Commit、Dev/Runtime、TEST/PAPER/LIVE、Storage、`Data`、履歴境界。 ／ 人／システム ／ 人の判断・承認・Broker操作 ／ ARGUSの提案・自動処理 ／ Proposal Viewとtyped Command / Fact。通知表示を承認とみなさない ／ §4.3、§11〜12、§24 ／ ／ ARGUS／外部サービス ／ Domain / Application ／ Provider API / SDK / Schema ／ ExternalServiceGatewayとProvider Adapterのみ。Business Logicから直接呼ばない ／ §37A ／ ／ 外部副作用／Local Commit ／ API利用コスト、外部応答 ／ Canonical State ／ Durable Stage、provenance、idempotency。外部副作用をRollback可能と仮定しない ／ §2.3、§2.5 ／ ／ 開発／実行 ／ `InvestmentAgent-Dev` ／ `InvestmentAgent` Runtime ／ Runtime停止、Backup、手動Deploy、Schema確認。state/data/configを上書きしない ／ §4.1、§4.6 ／ ／ TEST／PAPER／LIVE ／ 各環境のState/`Data` Root ／ 他環境 ／ 異なるstate_id / environment / marker。Mismatch時は起動・write拒否 ／ §4.1、§46B ／ ／ 内蔵SSD／外付けData Root ／ 現在State、Runtime、recent backup ／ Raw / normalized / historical / archive ／ Storage Managerとmarker identityで接続。drive letterだけを信用しない ／ §4.1、§4.7 ／ ／ 事実／観測／判断 ／ Facts ／ Observations / Judgments ／ Canonical Envelope内で領域分離し、導出値と事実を混同しない ／ §13.1 ／ ／ Current State／履歴 ／ `state/portfolio.json` ／ append-only archive / stage ／ ID、hash、range、high-water markで参照し、Compactionで履歴を消さない ／ §13.4 ／ Human ARGUS Broker Human/System、Provider、Commit、Dev/Runtime、TEST/PAPER/LIVE、Storage、`Data`、履歴境界。
