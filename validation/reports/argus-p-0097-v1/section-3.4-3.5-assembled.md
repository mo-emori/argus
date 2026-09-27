## 3.4 状態とデータ

本節では、状態を持つ対象、分類軸、事実や判断を表すデータ、変更要求、正本、派生物を分け、それぞれの生成元、利用先、保持条件、更新Authorityを定める。これらの境界を維持することで、事実を保存する単一正本と、再現可能かつ原子的な更新を成立させる。本節で定める正本と履歴が、3.5で扱う耐久化と復旧の対象になる。

### 状態軸と分類軸

現在状態、運用Mode、重大度、優先度、Portfolio分類を一つの状態軸へ混在させると、誤った遷移判断を招く。状態を持つ概念と独立した分類軸を区別し、次の各項目を別の意味と更新経路で扱う。

| 概念 | 意味と値 | 境界・不変条件 | 主な利用先 | 設計上の参照 |
|---|---|---|---|---|
| State | DomainまたはRuntime対象の現在値と遷移履歴 | User Status、Policy Mode、単なる分類値を一括してStateと呼ばない | Canonical State、Proposal、Order等 | §4〜5、§13 |
| User Status | 人の現在状態。`FREE / NORMAL / BUSY`を人が直接操作する | Configurationではなく、human_capacityの入力である | 通知、Queue、処理量制御 | §4.0、§21〜23 |
| human_capacity | Status Mapperが導出する内部制御値。`LARGE / MEDIUM / SMALL` | 人の入力値ではなく、Statusそのものでもない | Queueと処理範囲 | §21、§23 |
| Runner State | Runtime状態機械。`INIT / RUNNING / RESUMING / END` | OS kill / crashは状態ではなく終了事象であり、User Statusとも別対象である | Runner Lifecycle | §4.2〜4.3 |
| Policy Mode | Policy状態。`NORMAL / BOOTSTRAP / REPAIR` | Holding HorizonやRole Bucketではない | Portfolio制約の適用 | §15B |
| Holding Horizon | `SHORT / MEDIUM / LONG / CORE`で表す想定時間軸の分類 | 強制SELL状態ではなく、Role Bucketとも別軸である | Thesis、Time Stop | §16 |
| Role Bucket | `INCOME / GROWTH / EVENT / DEFENSIVE / OTHER / CASH`で表すPortfolio分類 | Holding Horizonと足し合わせず、lotを二重計上しない | Allocation、Policy | §14〜15B |
| severity | `INFO / WARNING / CRITICAL`で表す重大度分類 | 人へ届ける時期を表すpriorityとは別軸である | Alert / Incident | §24.0 |
| priority | `P0〜P3`で表す配送優先度 | severityから暗黙導出しない | Decision / Alert Queue | §24.0 |

### データ種別と変更要求

現実の事実、時点付き観測、判断結果、変更要求を混同すると、確認済み事実の拒否や履歴破壊が起き得る。データと操作要求の意味および更新経路を分離し、`Fact`、`Observation`、`Judgment`、`Command`、`Correction`、`Evidence`を相互に置き換えない。

| 種別 | 区分と意味 | 内容・生成条件 | 更新時の境界 | 主な利用先 | 設計上の参照 |
|---|---|---|---|---|---|
| Fact | データとして保持する事実 | 約定、Cash、Position、配当、税、費用等の確認済み現実 | TTLやPolicy違反があっても確認済みFactを拒否しない | Canonical Facts | §12〜13 |
| Observation | データとして保持する観測 | price、FX、liquidity等の時点付き観測 | FactやJudgmentと分離し、as_of等のprovenanceを持つ | 分析、Risk、Watch | §13.1、§29 |
| Judgment | データとして保持する判断結果 | Decision、Thesis revision、分類等 | 判断という行為ではなく結果を保持する。Factを上書きせず、変更は履歴として追加する | Report、Proposal、Audit | §5、§13.1、§29 |
| Command | 変更要求としての入力 | request_id付きで、人またはSystemからWriterへ渡す | Factは起きた現実、Proposalは判断候補であり、Commandとは異なる | Status、Approval、Correction、Config | §4.0、§4.3、§24.3 |
| Correction | 変更管理としての入力 | Human入力の誤りを、過去Recordの削除ではなく訂正履歴として追加する | Broker現実のRollbackではなく、Governanceを迂回しない | Decision / Execution / Cash等 | §24.3 |
| Evidence | データとして保持する証拠 | 出典原文または許諾範囲の抜粋、取得情報、hash、vintage | URLだけで固定せず、Observationの根拠とする | Analysis、Audit、Replay | §4、§29、§38〜39 |

### 永続化段階とArtifact Authority

外部結果、正本更新、表示用派生物を同じArtifactとして扱うと、再実行の要否や正本性を誤る。永続化段階とArtifactのAuthorityを区別し、どの成果物が正本で、誰がどの境界で更新できるかを固定する。

| 対象 | 位置付け | 内容または確定条件 | Authority境界・不変条件 | 利用先または実体 | 設計上の参照 |
|---|---|---|---|---|---|
| Durable Stage Result | 中間Artifact | 外部呼出し結果をCommit前に永続化したもの | Canonical Stateではなく、再開と再課金防止に用いる | External / Model Job | §2.5、§13.4 |
| Commit | Transaction結果 | 検証済み遷移を一つの原子的State versionとして確定する | 外部APIの副作用は同じRollback境界にない。Single Writerが担う | Canonical Stateの更新 | §2.3、§13.2 |
| Canonical State | 正本Artifact | PortfolioとWorkflowの現在正本 | Projection、Markdown、Backup、会話履歴を正本にしない | `portfolio.json` | §4、§13 |
| Current Envelope | Canonical State構造 | 現在状態と、復旧に必要な直近参照を持つ | 全履歴を無期限に埋め込まず、archiveを参照する | state / archive | §13.4 |
| Projection | 派生Artifact | Canonical Stateから再生成する表示・互換用データ | 独立更新しない | watchlist、queue、Markdown | §4、§13.2 |
| Artifact | 設計・運用成果物 | Identity、State、Log、Report、Validation record等 | ArtifactごとにAuthorityと正本性を区別する | Repository / Runtime | §4、§29、§46B |
| Configuration | 設定Artifact | 人が明示する動作規則の単一正本 | Status、State、Secret、Identityと分離する | `config.json` | §4.0 |
| Runtime Identity | Identity Artifact | logical instanceの不変なstate_id / environment / data_root_id等 | Deployment Identity、Run Identity、path、設定値と分離する | Bootstrap / Binding | §4.0 |

永続化境界で扱う`Canonical Envelope`、`inbox`、`archive`、`Stage`、`Projection`も同一視しない。それぞれの役割を保ったまま、正本への入力、履歴参照、中間結果、派生表示を区別する。

### `Canonical Data`と派生データの更新

`Fact`、`Observation`、`Judgment`、`Workflow`の混同に、並行更新や途中停止が重なると、正本が破損し得る。また、`Identity`、設定、`Status`、`Fact`、`Observation`、`Judgment`、`Workflow`、`Stage`、`Projection`を混在させれば正本性を失う。単一正本を維持して更新を原子的かつ再現可能にし、データごとの生成元、利用先、保持条件、更新Authorityを区別する。対象はRuntimeからAuditまでの`Canonical Data`および派生データである。

| データ／Artifact | 性質 | 生成元 | 利用先 | 保持条件・境界 | 設計上の参照 |
|---|---|---|---|---|---|
| Runtime Identity | 不変Identity Artifact | Setup / Bootstrap | Binding、起動 | state_id / environment / data_root_id等を持ち、path、Secret、Status、Domain Stateを入れない | §4.0 |
| Configuration | 設定 | 人の明示設定、Config Writer | Job、Policy、Budget、通知等 | `config.json`を単一正本とし、version/hashとJob開始時のimmutable snapshotを持つ | §4.0 |
| User Status | 人の現在状態 | StatusChangeCommand | capacity、Queue、通知 | `user_status.json`とstatus_versionを用い、直接編集を通常操作にしない | §4.0、§21 |
| Facts | 事実データ | Broker結果、入出金、配当、税、手数料、Corporate Action、Correction | Portfolio、Cash、Position | 確認済み事実を拒否、破壊、過去への上書きの対象にしない | §12〜13 |
| Observations | 観測データ | Provider Adapter | 分析、Risk、Watch | as_of / published / retrieved / source / revision / hashを保持する | §13.1、§29、§37A |
| Judgments | 判断データ | Agent、人 | Proposal、評価、監査 | immutable Decision、Thesis revision、Human Decisionとして保持する | §13.1、§29 |
| Workflow | 状態データ | Queue、Approval、Order、Reservation、Watch | 実行制御 | Proposal、Order、Incident等の独立状態を保持する | §5、§13.1 |
| `Raw Data` | 外部原本 | Provider Adapter | Normalize、監査 | 許諾範囲でimmutable保存する | §4.7、§37A |
| `Normalized Data` | Provider非依存データ | Provider Adapter | Selection / Analysis | provenanceからRawへ追跡可能にする | §4.7、§37A |
| Durable Stage | 中間永続結果 | External / Model call | Validate / Commitの再開 | 再課金と重複適用を防ぎ、Canonical Factとは区別する | §2.5、§13.4 |
| Audit / Decision Log | 監査Artifact | Canonical Commitから生成するProjection | 人または別AIによるレビュー、評価 | Markdownは正本ではなくProjectionである | §28〜30 |

### 情報種別ごとの正本、更新主体、失敗動作

正本、更新主体、格納内容が異なる情報を同一Artifactへ置くと、変更権限と復旧条件が曖昧になる。情報種別ごとに正本、更新主体、包含範囲、禁止対象、失敗時動作を固定する。この境界で区別する情報種別は、`Runtime Identity`、`Configuration`、`User / Domain / Runtime State`、`Secret`である。

| 情報種別 | 物理形式 | 更新主体 | 格納内容 | 格納しない内容 | 失敗時動作 | 設計上の参照 |
|---|---|---|---|---|---|---|
| Runtime Identity | 物理形式は後続Contractで定める | Bootstrap / 専用機構 | schema_version、state_id、environment、data_root_id、created_at候補 | path、drive letter、Budget、Secret、Status、Domain / Runtime State、plan tier、code path | 解決不能なら通常起動しない | §4.0 |
| Configuration | `config.json` | Config Writer | runtime、model、budget、notification、portfolio / risk policy、strategy、watch、selection、break、backup、archive | Secret値、User Status、Domain State | Schemaまたは必須値の不備はCONFIG_REQUIRED等とする | §4.0 |
| User Status | `user_status.json` | Status Writer | status_version、status、changed_at、BUSY lease | Policy、Budget、Portfolio Fact | version競合時は古い自動遷移を破棄する | §4.0、§21 |
| Domain State | `portfolio.json` Envelope | Canonical State Writer | Fact、Observation、Judgment、Workflow、Commit support | 会話履歴、暗黙記憶 | 正本不明ならRECOVERY_REQUIREDとする | §4、§13 |
| Runtime State | Canonical runtime領域 / Projection | Runner / Writer | Run、Job、retry、lock等 | User Status、Runtime Identity | 復旧時にlatest Stateから再構成する | §4.0 |
| Secret | Environment Variable / OS-protected store | 使用Subsystem | API key等のSecret値 | project、config、log、evidence、report、backup | 漏出の疑いがあればAdapterを停止し、SECURITY_INCIDENTとする | §4.4、§46E |

### Research lifecycle

発見、候補化、分析、監視、終了を一つの銘柄状態へ押し込むと、調査履歴と欠損理由が失われる。Research lifecycleを独立した状態機械とし、`DISCOVERED`、`CANDIDATE`、`ANALYZED`、`WATCH`、`ARCHIVED`の遷移と履歴を保持する。

| 現在状態 | 遷移条件 | 保存内容 | 次状態 | 利用先 | 禁止・失敗時動作 | 設計上の参照 |
|---|---|---|---|---|---|---|
| 未登録 | `Universe` / branch探索で発見 | sourceと枝別状態を記録 | DISCOVERED | Candidate評価対象 | 枝別欠損を否定評価にしない | §5〜7 |
| DISCOVERED | Candidate条件成立 | 候補として登録 | CANDIDATE | Candidate Watch対象になり得る | DATA_INSUFFICIENTを0点化しない | §5〜7 |
| CANDIDATE | 独立分析完了 | branch結果と矛盾を保存 | ANALYZED | Report / Proposal生成可能 | 未評価理由を保存する | §5、§7〜9 |
| ANALYZED | 継続監視判断 | Watch登録 | WATCH | Candidate Watch | 売買承認とは扱わない | §5、§18 |
| 任意 | 対象外または追跡終了 | 理由を記録 | ARCHIVED | Counterfactual sample対象になり得る | 履歴を削除しない | §5、§31 |

### Thesis revision lifecycle

投資仮説を上書きまたは二値化すると、弱化、失効、不明とEvidence履歴を区別できない。Thesis revisionとEvidenceの変化を状態遷移として保持し、`VALID`、`WEAKENED`、`INVALIDATED`、`UNKNOWN`を明示する。

| 現在状態 | 遷移条件 | 保存処理 | 次状態 | 利用先または次の判断 | 禁止・失敗時動作 | 設計上の参照 |
|---|---|---|---|---|---|---|
| 未作成 | Analysisで投資仮説成立 | revisionとして保存 | VALID | Invalidator / `Event`監視開始 | 旧revisionを上書きしない | §5、§9、§18 |
| VALID | 反証または`Event`が一部悪化 | Evidence比較と再分析 | WEAKENED | HOLD / REDUCE等の候補 | データ不足時はUNKNOWNを検討する | §17、§27 |
| VALID / WEAKENED | 購入理由崩壊 | Thesis Stop判定 | INVALIDATED | 最優先のSELL / REDUCE再分析 | Priceだけで即SELLしない | §17.1、§27 |
| 任意 | Evidence不足または矛盾未解決 | 不明状態を明示 | UNKNOWN | BUY / ADD停止になり得る | trueやVALIDへ推測しない | §5、§8、§17A |

### Holding lifecycleと履歴関係

Holding状態をProposalやOrderから推測すると、部分約定や全売却後の監視終了を誤り得る。Holdingは確認済みExecution Factと数量に基づいて遷移させ、未保有 / `CLOSED`、`OPEN`、partial SELL、全売却を区別する。

| 現在状態 | 遷移条件 | 更新内容 | 次状態 | 後続処理 | 禁止・不変条件 | 設計上の参照 |
|---|---|---|---|---|---|---|
| 未保有 / CLOSED | BUY Execution Fact適用後にquantity>0 | Position / lot / Cashを更新 | OPEN | Position Watch開始 | 未確認Executionでは遷移しない | §5、§12、§46C |
| OPEN | Partial SELL後もquantity>0 | lot、Cash、P/Lを更新 | OPEN | Watch継続 | cumulative quantityを新規fillとして扱わない | §12〜13、§46C |
| OPEN | SELL後にquantity=0 | 全売却の整合をCommit | CLOSED | Position Watchを終了し、必要ならCandidate Watchへ移る | Slot / reservationの整合前に終了しない | §5、§13.3、§46C |

lot / trancheはDecisionとThesisへ多対一で紐付く。同一銘柄では、保有とCandidate、新旧Thesisが併存でき、複数Decisionも併存できる。したがって、銘柄単位の一状態へ履歴を縮約してはならない。集計Positionの単位は、account_idとinstrument_idを組み合わせた複合単位とする。Holding lifecycleとこれらの履歴関係の基礎参照は§5である。

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
