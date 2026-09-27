## 3.5 保存・バックアップ・復旧

本節は、前節で定めた正本と派生物の区別を、保存、バックアップ、復旧および容量管理に適用する。Runtime Artifactの正本性と派生性が曖昧なままでは、ProjectionやBackupが独立に更新され、正本と異なる状態を持ち得る。このため、各Artifactについて生成元、利用先、保持条件および不変条件を明確にし、Storageの既定値、候補値、監視量、保存形式ならびに将来の移行条件を区別する。

### 3.5.1 保存対象とAuthority

保存管理の対象は、`SYSTEM.md`、Canonical State、Projection、`inbox/`、`evidence/`、`logs/`、`reports/`、`validation/`、`archive/`および`stage/`である。これらは同じ保存場所に存在し得ても、Authority、生成経路、利用目的および保持要件を相互に置き換えてはならない。

| 対象 | 種別と生成元 | 利用先 | 保持条件・不変条件 | 設計参照 |
|---|---|---|---|---|
| `SYSTEM.md` | 配備工程で生成する起動Artifact | 人、Runner | 起動手順、正本、版、入口および復旧方法を示す | §4 |
| `portfolio.json` | Single Writerが更新するCanonical State | 全Domain処理 | 一つのAtomic Commitを更新単位とする | §4、§13 |
| `watchlist.json` / `decision_queue.json` / `runtime_state.json` | Canonical Stateから再生成するProjection | UI、互換利用 | 独立に更新しない | §4 |
| `performance.json` | 評価処理が生成する派生結果 | Report | 計算条件と参照Commitを保持する | §4、§36 |
| `inbox/` | Fact ingressによるDurable入力 | Parser、Writer | 適用完了まで受領原文を保持する | §4、§12 |
| `evidence/` | Provider / acquisitionが生成する根拠Artifact | Analysis、Audit | source、時刻、hashおよび許諾範囲内の原文を保持する | §4、§29 |
| `logs/decisions`等 | Commit recordsから生成するAudit Projection | 人、別AI | `event_id` / `commit_id`で重複を排除し、Application Logで代替しない | §4、§28〜30 |
| `logs/application/YYYY-MM-DD/` | 生成主体とWriter実装は未確定のApplication Log | 運用、障害解析 | `Asia/Tokyo`の日付境界でDaily rotationし、Canonical情報より低い優先度で有限保持する。単独の書込み失敗をCanonical処理へ波及させず、Secret等を記録しない | §2.6、§4、§28 |
| `reports/` | Analysis / Evaluationが生成するHuman-facing Artifact | 人 | 正本として扱わない | §4、§9〜10 |
| `validation/` | Test processが生成する検証Artifact | Gate判断 | 計画、入力、期待、実測およびEvidenceを分離する | §4、§46B |
| `archive/events` | Compaction / Writerが追記するappend-only Fact履歴 | Rebuild、Audit | hash、rangeおよびhigh-water markを保持する | §13.4 |
| `archive/observations` | Acquisition / archiveが追記する観測履歴 | Analysis、Replay | revisionおよびvintageを保持する | §13.4、§39 |
| `archive/audit` | Commitが追記する監査履歴 | Review | 過去Recordを削除しない | §13.4 |
| `stage/` | External / Model callのDurable Stage | Validate、Commit再開 | request、input、outputのhashおよびusageを保持する | §2.5、§13.4 |

Application LogはRuntime、Job、Adapter、Error等の運用・障害解析に用いる記録であり、Canonical State、Fact、`Event`およびAudit Recordとは別のArtifactである。Application Logをこれらの代替にしてはならず、Application Logを削除しても、投資判断、状態、履歴その他のCanonicalな設計情報が失われない構造とする。

Application Logは`Asia/Tokyo`の日付境界でDaily rotationし、日付単位で管理可能にする。保存優先度はCanonical State、CommitおよびAuditより低く、具体的な期間は未確定であるものの、有限の保持上限を設ける。Application Log単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、その失敗自体は可能な範囲で観測可能にする。ただし、同一Storageの障害がCanonicalな安全性を損なう場合はStorage Fail Closedを適用する。

Application Logには、Secret、Credential、Token、API key、Authorization headerおよび未redactのdebug dumpを記録してはならない。また、TEST / PAPER / LIVEのRuntime Identity分離とDevelopment / Runtimeの物理分離に従い、分離されたApplication Logを相互に混在させない。

Application Logについては、生成主体、Writer責務、書込み経路、retentionの具体的期間、cleanup / deletionの実行方法、crash直前のLog durability保証範囲、Runtime / Job / Adapter / Errorごとの最低限の識別情報、環境間およびDevelopment / Runtime間を分離する具体的なpartition / path方式、既知の禁止対象以外に禁止またはmaskingする情報の範囲、filename、file format、schemaならびにlogging libraryが未確定である。これらを確定仕様として扱ってはならない。

### 3.5.2 BackupとRestore

バックアップ対象はCanonical commitに結び付ける。ARGUSのBackup Jobは、`commit_id`、`state_version`、hashおよび版参照を付けたsnapshotを作成する。Backup成功とCanonical Commit成功は別の結果として扱い、recent snapshotとlong-term snapshotを保存する。snapshotにSecretを平文で含めてはならず、freshnessを監視する。

内蔵SSDは直近N世代の復旧snapshotを担い、外付けHDDは長期Backupを担う。Nは未確定であり、固定値として扱わない。ローカルと外部のバックアップ鮮度は、`last_local_backup_at`と`last_external_backup_at`を用いて別々に監視する。

古いsnapshotをそのまま正本へ戻すと、Brokerで成立した実約定やCashとの差異を消すおそれがある。したがって、Backup snapshotの配置だけで通常運用へ復帰してはならない。復旧は、Restore、Broker照合、Correction / missing Factの反映を経て、通常運用へ戻る一連の手順として扱う。このBackup、RestoreおよびReconciliationの接続は§4.5および§4.7に基づき、前節で確立した正本性と保存境界を前提とする。

1. 人がRecovery Serviceを用いて復元対象snapshotを配置し、状態を`RESTORE_RECOVERY`とする。この時点の復旧Stateで実約定を消したまま再開してはならず、必ずReconciliationへ進む。
2. ARGUSはBroker、execution、cashおよびpositionの現実とsnapshotを照合し、状態を`RECONCILIATION_REQUIRED`とする。Reconciliation処理の実装主体は未確定である。不明な差分を推測せず、Correctionまたはmissing Factとして扱う。
3. ARGUSのWriterは確認済み差分だけを`Event`としてCommitする。Reconciliation Completeとなり整合Stateを確認できた場合に限り通常運用へ戻す。不整合が残る間は`BUY/ADD`の停止を継続する。

Restore後のReconciliationと、確認済み差分の`Event`としての再Commitは必須である。これにより、復元したsnapshotが履歴を巻き戻すための新たな正本になることを防ぎ、復旧後も正本性、履歴および更新Authorityを維持する。

### 3.5.3 `Data Root`、容量監視および保存形式

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
