## 3.5 保存・バックアップ・復旧

Runtime Artifactの正本性と派生性が不明だと、ProjectionやBackupを独立更新し得る。また、古いsnapshotをそのまま正本へ戻すと、Brokerで成立した実約定やCashとの差異を消し得る。さらに、容量目安、警告候補、保存形式を確定値として混同すると、不適切な閾値や形式を固定し得る。

このため、本節では、Artifactごとの生成元、利用先、保持条件、不変条件を定義する。Restore後には必ずReconciliationを行い、確認済み差分を`Event`として再Commitする。Storageについては、既定値、候補値、監視量、形式、将来移行条件を区別する。

### 3.5.1 保存対象とAuthority

保存対象は、`SYSTEM.md`、Canonical State、Projection、`inbox/`、`evidence/`、logs、`reports/`、`validation/`、archive、`stage/`である。各Artifactの生成元、利用先、保持条件および不変条件は次のとおりとする。

| Artifact | 種別 | 生成元 | 利用先 | 保持条件・不変条件 | 参照 |
|---|---|---|---|---|---|
| `SYSTEM.md` | 起動Artifact | 配備工程 | 人、Runner | 起動手順、正本、版、入口、復旧を示す | §4 |
| `portfolio.json` | Canonical State | Single Writer | 全Domain処理 | 一つのAtomic Commit単位 | §4、§13 |
| `watchlist.json` / `decision_queue.json` / `runtime_state.json` | Projection | Canonical Stateから再生成 | UI、互換利用 | 独立更新しない | §4 |
| `performance.json` | 派生結果 | 評価処理 | Report | 計算条件と参照Commitを持つ | §4、§36 |
| `inbox/` | Durable入力 | Fact ingress | Parser、Writer | 適用完了まで受領原文を保持 | §4、§12 |
| `evidence/` | 根拠Artifact | Provider / acquisition | Analysis、Audit | source、時刻、hash、許諾範囲原文 | §4、§29 |
| `logs/decisions`等 | Audit Projection | Commit records | 人、別AI | `event_id` / `commit_id`で重複排除し、Application Logで代替しない | §4、§28〜30 |
| `logs/application/YYYY-MM-DD/` | Application Log | 生成主体・Writer実装は未確定 | 運用・障害解析 | `Asia/Tokyo`境界のDaily rotation。Canonical情報より低優先で有限保持。単独書込失敗はCanonical処理を失敗させない。Secret / Credential / Token等を記録しない | §2.6、§4、§28 |
| `reports/` | Human-facing Artifact | Analysis / Evaluation | 人 | 正本ではない | §4、§9〜10 |
| `validation/` | 検証Artifact | Test process | Gate判断 | 計画、入力、期待、実測、Evidenceを分離 | §4、§46B |
| `archive/events` | append-only Fact履歴 | Compaction / Writer | Rebuild、Audit | hash / range / high-water mark | §13.4 |
| `archive/observations` | append-only観測履歴 | Acquisition / archive | Analysis、Replay | revision / vintageを保持 | §13.4、§39 |
| `archive/audit` | append-only監査履歴 | Commit | Review | 過去Recordを削除しない | §13.4 |
| `stage/` | Durable Stage | External / Model call | Validate、Commit再開 | request/input/output hashとusage | §2.5、§13.4 |

### 3.5.2 Application Log

Application Logは、Runtime、Job、Adapter、Error等の運用・障害解析用記録である。Canonical State、Fact、`Event`、Audit Recordとは別Artifactであり、これらの代替にしない。Application Logを削除しても、投資判断、状態、履歴等のCanonicalな設計情報を失ってはならない。

Application Logは`Asia/Tokyo`の日付境界でDaily rotationし、日付単位で管理可能にする。保存優先度はCanonical State、Commit、Auditより低く、有限の保持上限を持つ。ただし、retentionの具体的期間とcleanup / deletionの実行方法は未確定である。

Application Log単独の書込み失敗は、Canonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合は、Storage Fail Closedを適用する。

Application Logには、Secret、Credential、Token、API key、Authorization header、未redactのdebug dumpを記録しない。既知の禁止対象以外に禁止またはmaskingする情報の範囲は未確定である。

Application Logは、TEST / PAPER / LIVEのRuntime Identity分離、およびDevelopment / Runtimeの物理分離に従い、相互に混在させない。これらを分離する具体的なpartition / path方式は未確定である。

次の事項も未確定とし、確定仕様として扱わない。

- 生成主体、Writer責務、書込経路
- crash直前のLog durability保証範囲
- Runtime / Job / Adapter / Errorごとの最低限の識別情報
- filename、file format、schema、logging library

### 3.5.3 Backup

BackupはCanonical commitを入力として、ARGUSのBackup Jobが`commit_id`、`state_version`、hash、版参照付きsnapshotを作成する。Backup成功とCanonical Commit成功は分離し、出力はrecent / long-term snapshotとする。snapshotにSecretを平文で含めず、freshnessを監視する。

| 媒体 | 責務 |
|---|---|
| 内蔵SSD | 直近N世代の復旧snapshot。NはTBD |
| 外付けHDD | 長期Backup |

鮮度は`last_local_backup_at`と`last_external_backup_at`を別々に監視する。

### 3.5.4 Restore / Reconciliation

復旧の対象は、Backup snapshot、Restore、Broker照合、Correction / missing Fact、通常運用復帰である。古いsnapshotをそのまま正本へ戻すと、Brokerで成立した実約定やCashとの差異を消し得るため、Restore後には必ずReconciliationを行い、確認済み差分を`Event`として再Commitする。

| 手順 | 主体 | 実行担当 | 入力 | 処理 | 状態 | 出力 | 禁止・不変条件 | 次 |
|---|---|---|---|---|---|---|---|---|
| 1 | ARGUS | Backup Job | Canonical commit | `commit_id`、`state_version`、hash、版参照付きsnapshot作成 | Backup成功とCanonical Commit成功を分離 | recent / long-term snapshot | Secretを平文で含めない | freshness監視 |
| 2 | 人 | Recovery Service | 復元対象snapshot | 古いsnapshotを配置 | RESTORE_RECOVERY | 復旧State | 実約定を消したまま再開しない | Reconciliation |
| 3 | ARGUS | 未確定 | Broker / execution / cash / position | Reconciliation処理：現実とsnapshotを照合 | RECONCILIATION_REQUIRED | 差分 | 不明を推測しない | Correction / missing Fact |
| 4 | ARGUS | Writer | 確認済み差分 | `Event`としてCommit | Reconciliation Complete | 整合State | 不整合残存時はBUY/ADD停止継続 | 通常運用 |

設計元は§4.5および§4.7とする。

### 3.5.5 `Data Root`、容量監視および保存形式

初期の`Data Root`は`L:\emori\InvestmentAgentData`とする。ただし、drive letterだけを根拠に保存先を受け入れず、markerを照合して保存先のidentityを確認する。

| 管理項目 | 値または形式 | 扱い | 設計参照 |
|---|---|---|---|
| `Data Root` | `L:\emori\InvestmentAgentData` | 初期物理保存先とし、marker照合を必須とする | §4.1、§4.7 |
| 利用上限目安 | 最大約2TB | 必要容量の見積値でも予約領域でもない | §4.1 |
| Soft Warning | 約1.8TB | 候補値であり、最終thresholdはDatasetの実測後にCVで設定する | §4.7 |
| 監視量 | absolute usage、volume free、directory usage、daily / weekly growth | Adapterの暴走やLog loopの検知に用いる | §4.1 |
| Raw | Response、ZIP、XBRL、PDF等 | 原本または許諾された形式のままimmutableに保持する | §4.7 |
| Normalized time series | JSONLを初期標準候補とする | Provider非依存schemaとprovenanceを保持する | §4.7、§37A |
| Small metadata | JSONを許容する | 小容量の単発Recordに用いる | §4.7 |
| 将来形式 | SQLite / Parquetを候補とする | 容量または検索性能がbottleneckになった時点を移行判断の契機とする | §4.7 |

容量目安、警告候補および保存形式を確定値として混同してはならない。2TBは利用上限の目安、1.8TBはSoft Warningの候補であり、いずれもDatasetの実測に先立って容量計画や閾値を固定する根拠にはならない。Raw、JSONL、JSON、SQLiteおよびParquetも用途と移行条件を伴う選択肢として管理し、候補を無条件の標準へ昇格させない。
