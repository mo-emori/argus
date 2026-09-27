# argus Design Source v0.1

**Document Role:** `DESIGN_SOURCE`  
**Source Lineage:** `argus — Investment Agent System Design v0.1.7 FINAL`  
**Purpose:** 現在有効な設計事項、要求、制約、実現方式を保持し、Structured Design Dataを生成・同期する一次資料とする。  
**Note:** 本書の章構造は蓄積時の構造であり、argusの論理構造そのものを表すとは限らない。


**System Name:** `argus`  
**Display Name:** `argus`  
**Pronunciation:** アーガス  
**Project / Package Identifier:** `argus`  
**Development Folder:** `argus-dev`  
**Runtime Folder:** `argus`


**版の位置付け:** 本書だけで現在有効なLocal-first実装設計が成立する**初期実装Baseline / FINAL設計版**。Regression実行位置、Storage Critical時のPosition Watch、CorrectionとPaid Governanceの優先関係、Decision Impact、Environment Bindingを現行本文で定義する。\
**Status:** LOCAL_FIRST_DESIGN_FOR_IMPLEMENTATION\
**Post-freeze clarification:** `ARGUS-DA-0003` / `ARGUS-P-0022-v1` は、実装過程で明確になったRuntime Bootstrapの責務境界を本書へ追記する。既存の投資判断・State・Environment Binding契約を変更せず、Runtime IdentityをConfiguration等と混同しないための限定的なcanonical clarificationである。\
**Target runtime:** ユーザーPC上のLocal Agent Process。LLM推論はOpenAI
API等の外部Model
APIを呼び出す。実装・テストはCodexを主に使用する。Astraは通常Runtimeの必須依存とせず、必要な難所だけをピンポイントレビューする。\
**設計更新日:** 2026-09-07\
**実装・実機試験:**
未実施。本書の確定は実行能力・投資成果・常時監視の保証ではない。\
**Purpose:**
銘柄選定→独立分析→具体的売買提案→人間判断→実行結果受領→保有監視→再評価→承認付き改善を閉ループ化する。\
**Primary constraint:**
Local-first。PCは常時起動・常時オンラインではない。停止・スリープ・通信断を通常状態として扱い、復帰後に再試行・Catch-upできる構造とする。Market
/ Historical Data Sourceは外部利用可能。初期から常駐Server・Broker
APIを必須にしない。

本書の現行仕様では、投資ロジック、State、Validator、Queue、監査契約、およびRuntime / External Service / Human Correction / Verification境界を本文で定義する。Configurationは`config.json`へ集約し、頻繁に変更するUser StatusはConfigurationから分離する。User Statusは`FREE / NORMAL / BUSY`、内部制御値は`human_capacity = LARGE / MEDIUM / SMALL`とし、BUSYは期限付きLeaseを持てる。Status変更はJSON直接編集ではなくCLI / Trayから`StatusChangeCommand`として行う。Model BudgetはHard Gateに加えて使用量監視・警告・人間とのBudget Reviewを持つ。Local常駐UIはWindows Task Trayを初期候補とし、開発用コードと実行用コードは物理分離する。大容量Market / Historical Dataは`L:\emori\InvestmentAgentData`へ保存する。TDnet有料APIは費用要件不一致のため本システムの対象外とする。初回発注は未解決一件に直列化する。Investment Emergency Overrideは初期OFF、System Critical Overrideは初期UNCONFIGUREDとしSetup時にHumanが選択する。予算・運用上限等のユーザー設定は明示設定されるまでUNCONFIGUREDとして扱う。

------------------------------------------------------------------------

# 1. 目的

本システムの目的は、AIに投資判断を丸投げすることではない。

目的は以下である。

1.  市場全体から投資候補を探索する。
2.  複数の独立した評価枝で銘柄を分析する。
3.  投資判断に必要な根拠・反証・リスク・未解決点を統合する。
4.  人間に、認知負荷を抑えた形でBUY / ADD / HOLD / REDUCE / SELL /
    WATCH等の提案を行う。
5.  人間が最終判断し、証券会社で操作する。
6.  約定・操作結果をCopy & Pasteで受け取り、Portfolioを更新する。
7.  保有銘柄と非保有Watch銘柄を別の周期・優先度で監視する。
8.  システム自身の判断性能・コスト・通知負荷・探索枝を評価する。
9.  システム自身にBreak機構を持たせ、既存構造を前提としない改善提案を生成する。
10. 改善は「AI提案→ユーザー承認→システム修正→再検証」の順で行う。
11. 過去データと1か月の仮想運用で性能を検証した後に、実資金運用への移行可否を判断する。
12. 初期はLocalで実装し、常時監視が必要になった場合にServerへ低影響で移行可能な構造を維持する。

------------------------------------------------------------------------

# 2. 初期版の基本方針

## 2.1 Local-first / Intermittent Runtime

初期版はユーザーPC上のLocal Agent Processとして実装する。

PCが常時起動・常時オンラインであることを前提にしない。

通常発生しうる状態：

-   PC電源OFF
-   Sleep / Hibernate
-   Network offline
-   API timeout
-   外部Data Source障害
-   OpenAI API障害
-   Process停止・再起動

これらを「異常だから設計外」とせず、**処理失敗→Rollback /
未Commit→Retry→復帰後Catch-up** の通常経路として扱う。

初期実装では以下を必須化しない。

-   常駐Server / VPS
-   Broker API連携
-   Web Dashboard
-   分散Worker
-   外部Message Queue
-   Work Runtime

一方、以下はLocalでコードとして実装する。

-   Runner / Loop
-   Retry制御
-   Transaction boundary
-   Canonical State Writer
-   Deterministic Risk Validator
-   Decision Queue
-   State / Audit Log
-   External API adapters
-   Model API adapters

## 2.2 Persistent Loop + Retryable Transactional Jobs

初期実行モデルは本格Scheduler Frameworkではなく、**常駐Loop + wait +
retryable transactional job** とする。

概念：

``` python
while running:
    if should_run(job, now, last_success):
        run_with_retry(job.transaction)
    wait(loop_interval)
```

`run_with_retry()` は短時間のburst retryを行う。

``` python
for attempt in range(MAX_RETRY_COUNT):
    try:
        transaction()
        mark_success()
        break
    except RetryableError:
        rollback_uncommitted_local_changes()
        sleep(RETRY_INTERVAL)
else:
    mark_retry_pending()
```

MAX_RETRY_COUNT到達はJobの永久破棄を意味しない。次のLoop /
Due判定で再試行する。

非Retryable
Error（Schema不整合、Policy不備、認証設定欠落等）は無限Retryせず、`BLOCKED / CONFIG_REQUIRED / DATA_INVALID`
等として記録する。

## 2.3 Transaction Boundary

外部通信そのものをLocal DB Transactionで巻き戻せるとは仮定しない。

基本形：

``` text
External Read / API Call
  ↓
Stage Result + provenance
  ↓
Validate
  ↓
Acquire Writer Lock
  ↓
Re-read latest State
  ↓
Apply deterministic transition
  ↓
Atomic Commit
```

外部API呼出し後にLocal
Commitが失敗した場合、API利用コストや外部側の処理自体は巻き戻らない。再試行時はrequest_id
/ content_hash /
idempotency情報を利用し、重複計上・重複State適用を防ぐ。

Brokerへの売買は初期版では人間操作のため、Agent
Transaction内の外部副作用に含めない。

## 2.4 Loopによる定時実行

定時処理もLoopで表現する。

``` text
Loop
  ↓
should_run(now, last_success, schedule_rule)
  ↓
YES
  ↓
run_with_retry(transaction)
  ↓
record_success
```

PCが予定時刻に停止していた場合、復帰後に `last_successful_run`
とScheduleを比較し、未実行期間を検出する。

未実行Jobを無条件に古い条件のまま実行せず、必要に応じてRelevance /
Freshness / TTLを再評価して RUN / REANALYZE / EXPIRE / MERGE / DROP
を決める。

------------------------------------------------------------------------

## 2.5 Runner Single Instance / Retry Economy / Adapter Circuit Breaker

Local Runnerは`state_id`ごとに単一InstanceだけをActiveにする。

起動時にRunner lockを取得し、lock metadataへ少なくとも以下を記録する。

```text
state_id
host_id
pid
process_start_time
acquired_at
heartbeat_at
runner_version
```

Writer lockとRunner lockは目的を分ける。

- Runner lock：Loop、polling、Model API call、notification等の二重副作用を防ぐ。
- Writer lock：Canonical Stateの原子的更新を防護する。

Runner lockが存在する場合、PID存在確認、process start time、host、heartbeatを照合する。同一Host上で保持Processが生存していれば二重起動を拒否する。保持Processが存在しないことを機械確認できた場合のみstale lockとして回収する。確認不能時は無条件奪取せず`RUNNER_LOCK_RECOVERY_REQUIRED`とする。

Retryは固定間隔だけに依存しない。

```text
Retryable transient error
  ↓
short burst retry
  ↓
exponential backoff + jitter
  ↓
MAX_RETRY_COUNT
  ↓
RETRY_PENDING / next_retry_at
```

Adapter単位で連続失敗数、last_success_at、next_allowed_at、degraded_untilを保持する。閾値を超えた場合は`ADAPTER_DEGRADED`へ移行し、そのAdapterを必要とする通常Jobを一定時間起動しない。

Error分類例：

- timeout / temporary network error：Retryable
- HTTP 429 rate limit：Retryableだがprovider指示のRetry-Afterを優先
- provider 5xx：Retryable + Circuit Breaker対象
- insufficient quota / billing disabled：`BUDGET_OR_QUOTA_BLOCKED`。時間経過だけでは回復しない
- invalid API key / permission：`CONFIG_REQUIRED`
- Schema / Policy不整合：`DATA_INVALID / POLICY_NOT_READY`

高価な外部処理、とくにModel API出力は**Stage ResultとしてCommitとは別に永続化**する。

```text
External / Model API call
  ↓
Durable Stage Result
  ├ request_id
  ├ input_hash
  ├ model / provider
  ├ token / cost usage
  ├ output_hash
  └ provenance
  ↓
Validate
  ↓
Canonical State Commit
```

Local Commitだけが失敗した場合、同じinput_hashで有効なStage Resultが残っていればExternal / Model API callから再実行せずStageから再開する。これによりState上の冪等性だけでなく、不要な再課金も抑える。

## 2.6 Runtime Clock Policy

Due判定はtimezone付きWall Clockと`last_successful_run` / `scheduled_for`で行う。Sleep中に予定時刻を通過したことを復帰後に検出できることを優先する。

`wait()`、短時間timeout、retry delayの経過時間測定にはmonotonic clockを使う。

- Schedule / Due / Market calendar：Wall Clock (`Asia/Tokyo`)
- wait / timeout / retry interval：Monotonic Clock

OS時計の大幅変更、timezone変更、NTP補正が観測された場合は`CLOCK_DISCONTINUITY`を記録し、Due Jobを再評価する。

初期POCのSupported Runtime OSは**Windows**に固定し、exact edition / build / filesystem / Python versionをCV-00でManifestへ記録する。他OSは同じatomicity / locking / sleep semanticsを再試験するまでSupported扱いしない。

------------------------------------------------------------------------

# 3. システム全体像

Market → Stock Selection → Candidate Pool → Multi-branch Analysis →
Contradiction / Risk Review → Decision Report → Allocation → Proposed
Trade → Deterministic Risk Validator → Decision Queue → Human Approval →
Execution Slot確保 → Human Operation at Broker → Execution Result Paste
→ Portfolio Commit → Position / Candidate Watch → Re-analysis。

銘柄への興味や調査続行の意思表示は売買承認ではない。最終承認は、数量・注文条件・Policy・Validator結果が揃った具体的Tradeを対象とする。承認とExecution
Slot確保は§13.2の一つのCommitで成立する。承認後も発注直前の再検証を行う。

並列する改善ループ：Logs / Results / Costs / Human Load → Evaluation →
Break Proposal → Decision Queue → Human Approval → Approved Change →
Retest → Version Activation。

実行基盤：Local Runner → Due Check → Retryable Job → External Evidence /
Model API → Validate → Atomic State Commit。

------------------------------------------------------------------------

# 4. ファイル構成・正本・起動契約

初期実装はLocal filesystem上のJSON /
Markdownと決定論的Pythonコードを使う。LLM会話履歴や暗黙記憶を正本にしない。

  --------------------------------------------------------------------------------------------------------------
  ファイル／領域                               役割
  -------------------------------------------- -----------------------------------------------------------------
  SYSTEM.md                                    起動手順、正本の所在、適用版、実行入口、復旧手順

  Runtime Identity document                    state_id / environment / data_root_id等の不変なlogical instance identity。
                                               物理filenameとdiscovery methodは後続Contractで確定する

  portfolio.json                               一つの原子的Commit単位となるCanonical State。§13のEnvelope

  watchlist.json / decision_queue.json /       正本から再生成する表示・互換用Projection。独立更新しない
  runtime_state.json                           

  performance.json                             計算条件・参照Commit付きの派生結果

  config.json                                  人間が明示設定する運用Configurationの単一正本。Risk / Portfolio /
                                               Notification / Retry / Budget / Strategy / Watch / Selection等

  user_status.json                             頻繁に変更するUser Statusの正本。Configurationではない

  system/\*.md、schemas/、code/               selection / analysis / allocation / watch / sell / break /
                                               validationの規則、Schema、Validator・Reducer・Writerコード

  inbox/                                       受領原文。受領IDを付け、正本へ適用完了するまで保持

  evidence/                                    出典原文または許諾範囲の抜粋、取得情報、内容hash

  logs/decisions, executions, watch, break,    正本の監査Recordから生成するMarkdown。event_id /
  reviews, system                              commit_idで重複排除

  logs/application/YYYY-MM-DD/                 運用・障害解析用Application Log。詳細契約は§28

  reports/stock, portfolio, performance        人間向け表示

  validation/                                  capability_verification、試験入力、期待結果、実測結果、backtest /
                                               replay / paper計画
  --------------------------------------------------------------------------------------------------------------

## 4.0 Configuration / Status / Stateの分離

運用設定は原則として`config.json`一つへ集約する。設定値を`policy.json`、複数の設定ファイル、コード定数へ分散させない。

`config.json`は少なくとも以下の領域を持てる。

```text
runtime
model
budget
notification
portfolio_policy
risk_policy
strategy
watch
selection
break
backup
archive
```

一方、`status`はConfigurationではない。人間が現在の状態として頻繁に変更する値であり、`user_status.json`へ分離する。

```text
Configuration   = システムの動作規則        → config.json
User Status     = 人間の現在状態            → user_status.json
Domain State    = Portfolio等の現在事実      → portfolio.json
Runtime State   = Runner / Jobの実行状態     → Canonical State内のruntime領域 / Projection
Secret          = API key等                  → Environment Variable / OS secret store
```

これらの可変な運用情報・State・Secretとは別に、**Runtime Identity**をlogical instanceの不変なidentity artifactとして扱う。Runtime Identityは第6の可変Stateカテゴリではなく、通常運用で変更するConfigurationでもない。初期フィールド候補は`schema_version`、`state_id`、`environment`、`data_root_id`、`created_at`とし、厳密な型・受理形式・failure code・serializationは専用Contractで確定する。

Runtime Identity、Deployment Identity、Run Identityを混同しない。

```text
Runtime Identity      = state_id / environment / data_root_id等のlogical instance identity
Deployment Identity   = install path / code version / development・runtime tree等の配置Evidence
Run Identity          = run_id / pid / host / start time等の起動ごとのRuntime State
```

Runtime Identityへdata root path / drive letter、budget / notification / schedule、Secret値またはsecret reference、User Status、Domain State、Runtime State、provider plan tier、code/install pathを保存しない。`data_root_id`はlogical identityでありRuntime Identity側に属する。data root pathはmutableなlocatorでありConfiguration側に属する。path、drive letter、Volume GUID等からexpected identityを導出せず、environmentをdevelopment/runtime treeから推論しない。

Runtime Foundation Bootstrapの責務は次の4段階へ分ける。正式な個別Contractが未確定の段階で後続Capabilityの仕様を先取りしない。

1. `RUNTIME-IDENTITY-DOCUMENT`
2. `RUNTIME-CONFIG-MECHANISM`
3. `RUNTIME-ENTRY-RESOLUTION`
4. `RUNTIME-BOOTSTRAP-ORCHESTRATOR`

Secret referenceの形式・設定はConfiguration側で扱い、Secret値の解決は使用時のSubsystem / Job責務とする。Environment Binding integrationは、identity/configからexpected bindingを導出する純粋部分と、Orchestratorが既存Environment Binding APIを呼びfailureを写像する部分へ分ける。各Subsystemはtyped failureを保持し、上位境界で既存startup outcome / Incident体系へ写像する。全Subsystem共通の巨大failure enumを新設しない。

`config.json`は`config_version`を持ち、Run / Decision Recordには`config_hash`を保存する。判断時点の設定を後から再現できるようにする。Secretを`config.json`へ保存しない。

**Config Snapshot Contract:** 各Jobは開始時に有効な`config.json`を検証してimmutable snapshotを取得し、そのJobは終了まで同じsnapshotで実行する。Run / Stage / Decision Recordへ保存する`config_version` / `config_hash`はこのsnapshotのものとする。運用中のConfig変更は次のJob境界から有効とし、実行途中のJobへ動的注入しない。Budget limitを既存reservationより低く変更した場合、既存reservationは取り消さず、新規reservationを停止し`LIMIT_BELOW_EXISTING_RESERVATION`を表示する。

`user_status.json`の変更は簡易操作を前提とし、Policy変更・System Changeと同じ重い承認経路を要求しない。ただし**人間がJSONを直接編集することを通常操作としない**。CLI / Trayから`StatusChangeCommand`を投入し、Status Writerがversion照合・排他・atomic replaceを行う。変更時刻・変更前後・期限・Command IDは監査可能に残す。

`user_status.json`は少なくとも`status_version`を持つ。人間のStatus変更とRunnerによるLease期限切れ遷移が競合した場合、期限切れJobが読んだ`status_version`とCommit時の最新versionが異なれば自動遷移を破棄し、**最新の人間操作を優先**する。Last-write-winsへ依存しない。

Configurationの正本は`config.json`だが、Budget等の頻繁な運用変更も通常はCLIから行い、Schema検証・単位検証・変更差分確認後にConfig Writerが反映する。手編集は保守用の非常手段とする。

## 4.1 初期配置

ユーザーPC上では**開発用と実行用を物理的に分離**する。

```text
InvestmentAgent-Dev/      # Codex開発・試験・Git管理
InvestmentAgent/          # 実運用Runtime。稼働中の正本
```

絶対パスは実装時Manifestで固定する。開発環境のCodexや試験コードがRuntimeの`state/`、`config.json`、`user_status.json`を直接変更しないことを前提とする。

大容量データの物理保存先は初期値として次を採用する。

```text
L:\emori\InvestmentAgentData
```

外付けHDDは通常接続を前提とするが投資専用ではない。Investment Agentへ割り当て可能な**運用上の上限目安**は最大約2TBとするが、これは必要容量見積りでも予約領域でもない。実必要量は取得Dataset確定後のCVで再見積りする。絶対使用量だけでなく、Volume free space、directory別使用量、日次/週次増加率を監視し、Adapter暴走やLog loopを早期検知する。

`L:`というdrive letterの存在だけをStorage同一性の根拠にしない。Data Root直下に`data_root_marker.json`を置き、少なくとも`state_id`、`data_root_id`、`environment`（TEST / PAPER / LIVE）、`created_at`を記録する。起動時・再接続時にMarkerを照合し、`state_id` / `data_root_id` / `environment`のいずれかが期待値と不一致なら`DATA_STORAGE_IDENTITY_MISMATCH`または`ENVIRONMENT_BINDING_MISMATCH`として**書込みを停止**する。可能ならWindows Volume GUID / Volume Labelも補助識別子として記録する。

Canonical StateはLocal project
directory内の一つのBindingだけを正本とする。OneDrive /
Dropbox等の同期ストレージを使う場合も、初期版では
`logs / reports / backups / export`
の共有・バックアップ用途を基本とし、同期フォルダー上のDB / Canonical
Stateを複数Writerが直接更新する構成は採用しない。

正本は実行配置ごとに一つだけ選び、`storage_binding`
にbackend、絶対パスまたは安定ID、state_id、schema_versionを固定する。クラウド保存物・ローカルコピー・バックアップを同時に正本としない。配置を変更するときは書込停止、最新版照合、移行記録、起動Binding切替、旧Writer無効化を行う。

## 4.2 毎回の起動

1.  SYSTEM.mdと固定されたManifestを読む。
2.  実行ホスト、Local project path、network状態、使用可能Adapter、Model
    API設定を記録する。
3.  Bindingで正本を取得し、state_id、Schema、Commit、適用Policy / System
    / Code hashを照合する。
4.  inbox未処理、outbox未配信、UNKNOWN Order、Projection遅延を復旧する。
5.  有効Configuration、利用データ時刻、user_status、導出human_capacity、execution_slot、各Jobのlast_success
    / retry stateを読む。
6.  未実行期間・Retry Pending・未処理inboxを検出し、Relevance
    Check後にCatch-upする。
7.  通常Loopへ入る。

Process起動直後は`INIT`とする。前回が正常終了していないことを検出した場合は`RESUMING`へ移り、inbox、outbox、Stage、Commit、lock等を復旧・照合してから`RUNNING`へ進む。

正本を確定できなければ新しい空Portfolioを作らず、Fail Closedで起動を失敗させる。これはRuntimeの通常状態を追加する意味ではない。LLMの再起動や新規チャットでも同じ契約を使う。

Startup時のEnvironment Binding成功結果を後続writeの永続的なauthorization tokenとして再利用しない。write-capable boundaryは既存Environment Binding Contractのrevalidation規則に従う。将来の`RuntimeContext`はstartup binding tokenをwrite authorizationとして露出してはならない。

モデルsnapshotが観測できなければ `NOT_OBSERVABLE`
とする。コードhash・config hashの記録は権限分離の証明ではない。

------------------------------------------------------------------------

## 4.3 Human Interface Contract

v0.1.4のMVSでは、Human Commandの正規入口を**Local CLI**に固定する。Windows Task Trayは同じCommand Dispatcherを呼ぶ軽量UIとして追加可能とし、Local Web UIはDeferred Scopeとする。

Human I/Fは表示層であると同時にCommand / Factの入口であり、Canonical Stateを直接編集しない。

### Proposal提示

Runner / Decision QueueはHuman-visible Proposal Viewを生成する。

```text
proposal_id
revision
trade_hash
Recommendation
Declared Reason Weights
Counterarguments
valid_until / valid_if
Validator result
```

CLI例：

```text
agent proposals list
agent proposal show <proposal_id>
```

通知Adapterは「Proposalがあること」を知らせるだけで、承認そのものを代行しない。初期版ではConsole / Local notificationを候補とし、通知未実装でもCLIで未処理Proposalを確認できることをMVS必須条件とする。

### Human Approval / Rejection

承認はCanonical Stateを直接変更せず、`ApprovalCommand`としてWriter経路へ投入する。

最低項目：

```text
request_id
command_type = APPROVE / REJECT / WATCH / REANALYZE
proposal_id
proposal_revision
trade_hash
submitted_at
human_actor
```

`request_id`は一意で、同一Commandのreplayは冪等化する。APPROVEはproposal revision / trade_hash / TTL / valid_if / State / Policy / Validatorを再検証し、§13.3のexecution_slot / reservation取得と**同じAtomic Commit**で成立させる。条件が変化していれば承認を流用せず`SUPERSEDED / EXPIRED / REVALIDATION_REQUIRED`とする。

### Execution Paste

初期MVSのBroker実行結果入力もCLIを正規入口とする。

```text
agent execution paste
> <broker result text / structured fields>
```

入力原文はまず§12の`inbox/`へreceipt_id付きでDurable保存し、その後Fact parsing / validation / Commitへ進む。

将来、監視フォルダーやWeb UIを追加する場合も、同じ`ApprovalCommand` / `ExecutionFact` schemaへ変換し、Writerを迂回しない。

### CLI / Tray / Runner Process Model

CLI / TrayをRunnerの従属Clientにしない。CLIは短命Process、Trayは常駐UI ProcessまたはRunner同居UIとして実装可能だが、いずれも**共有Service Layer / Command Dispatcher**を呼ぶ。

```text
CLI --------┐
Tray -------+--> Shared Command / Service Layer
Runner -----┘        ├─ Status Writer
                     ├─ Config Writer
                     ├─ Approval / Revalidation Service
                     ├─ Fact Ingress
                     └─ Validator / Storage Service
```

Runnerが`RUNNING`でなくても、Status、Help、System Statusは利用可能にする。Execution Pasteは原則として`RUNNING`中だけ受け付け、非RUNNING時は現在実行可能状態でないことを示すErrorとして拒否する。停止中のExecution PasteをDurable受領するためだけの常駐受付機構は要求せず、Broker結果はSBI証券側に残るため、ARGUS起動後に入力する。CLI / TrayはRunner single-instance lockを取得しない。一方、Canonical / Status / Configの変更はそれぞれのWriter lock、version check、atomic replaceを必ず通る。

ApprovalはRunner固有実装へ複製せず、共有Service LayerのValidator / revalidation codeを利用する。これによりCLI / Tray / Runner間で承認条件が分岐しない。

### Runner Lifecycle Contract

Runnerの明示状態を次で管理する。

```text
INIT
RUNNING
RESUMING
END
```

- `INIT`：Process起動後、通常実行を開始する前の初期状態。
- `RUNNING`：通常実行可能状態。
- `RESUMING`：前回の異常終了等を検出し、継続可能な状態へ復旧するための起動時状態。
- `END`：Graceful Exitが完了した正常終了状態。

通常系は`INIT → RUNNING → END`、異常終了後の次回起動は`INIT → RESUMING → RUNNING`とする。同一の`RUNNING`を意味の異なる複数状態として定義しない。OS kill / crashはRuntime状態ではなくProcess終了事象であり、次回起動時の正常終了有無等の確認によって`RESUMING`への遷移を決める。

`Exit`は新規Job受付を止め、実行中のlocal transactionを安全点まで完了またはDurable Stageへ退避し、flush後にlockを解放して`END`へ遷移する。`Restart`はGraceful Exit完了後に新しいProcessを`INIT`から開始する。復旧不能条件はFail Closed、Incident、起動失敗として扱い、Runtimeの通常状態へ追加しない。

### CLI Command / Help Contract

ユーザーがコマンド名・引数を暗記することを前提にしない。初期版から`help`を必須とする。

```text
help
help status
help budget
help alerts
help system
```

主要コマンドの初期契約：

```text
status
status free
status normal
status busy 1h
status busy 3h
status busy today
status busy week
status busy forever

budget status
budget set daily <amount>
budget set monthly <amount>
budget set emergency <amount>
budget review

alerts
alert ack <alert_id>
incidents
system status
system version
help [command]
```

BUSYの期限日時はユーザーにISO時刻を手入力させず、CLI側が計算する。変更時には解決後の絶対時刻を必ずエコーする。

```text
STATUS = BUSY
Until  = 2026-09-13 00:00 JST
After  = NORMAL
```

### Windows Task Tray

Local Processは可能ならWindows Task Trayへ常駐させる。Trayは独自Business Logicを持たず、CLIと同じCommand Dispatcherへ接続する。

初期候補：

```text
Investment Agent
├─ STATUS
│  ├─ FREE
│  ├─ NORMAL
│  └─ BUSY > 1h / 3h / Today / This week / Until changed
├─ Budget Status
├─ Alerts
├─ System Status
├─ Open Console
├─ Restart
└─ Exit
```

Tray UI停止がRunner StateやCanonical Stateを破壊しないこと。Tray未実装でもCLIで全必須操作を実施できることをMVS成立条件とする。

## 4.4 Secret / Privacy Boundary

Secretをproject treeの通常ファイルへ保存しない。

初期方針：

- API key等のSecretはEnvironment VariableまたはOS-protected secret storeから取得する。
- `manifest.json` / `config.json`にはSecret値を書かず、secret name / provider / required statusだけを置く。
- `logs/`、`evidence/`、`reports/`、`backups/`へSecret値を出力しない。
- Exception / HTTP header / debug dumpにAuthorization headerを残さない。
- Secret scanning testをCVへ含める。

同期ストレージへのExportはAllowlist方式とする。

初期のShared / Sync対象：

```text
reports/redacted/
logs/reviews/redacted/
backups/encrypted/   # 有効化する場合のみ
```

初期の非同期対象：

```text
state/
inbox/
evidence/raw/
secrets/
runtime lock files
unredacted execution / account data
```

Portfolio実額、口座ID、Broker execution等はModel APIへ無条件送信しない。Agentごとに必要最小限のData Contractを定義し、銘柄分析Agentには原則として匿名化・集約されたPortfolio exposureだけを渡す。Allocation / Risk等、実額が必要な処理では送信項目をManifest / Logに記録する。

## 4.5 Backup / Restore Contract

BackupはCanonical Stateの代替WriterではなくRecovery用snapshotとする。

最低要件：

- Canonical StateのCommit ID / state_version / hashを含む。
- Policy / System / Schema / Code version参照を含む。
- 定期snapshotと重要Commit前後snapshotを作成可能にする。
- Backup作成失敗をCanonical Commit成功と混同しない。
- Secretを平文Backupへ含めない。

Restoreは通常Commitの巻き戻しではない。

古いsnapshotを復元した場合、Broker側現実との乖離可能性があるため必ず：

```text
Restore Snapshot
  ↓
RESTORE_RECOVERY
  ↓
RECONCILIATION_REQUIRED
  ↓
Broker / execution / cash / position照合
  ↓
必要なCorrection / missing Fact追加
  ↓
Reconciliation Complete
```

口座照合完了までは新規BUY / ADD Proposalを有効化しない。確認済み実約定を古いsnapshotで消したまま運用再開しない。

------------------------------------------------------------------------

## 4.6 Development / Runtime Deployment Contract

初期版のシステム更新は**自動Updaterを作らず、Runtime停止後の手動Deploy**とする。

```text
Devで実装・試験
  ↓
Acceptance Criteria / CV PASS確認
  ↓
Runtime Exit
  ↓
State / Config backup
  ↓
Runtime app/置換
  ↓
Schema / Version確認・必要ならMigration
  ↓
Validation
  ↓
Restart
```

更新の基本原則：

- `app/`更新で`state/`、`data/`、`config.json`、`user_status.json`を上書きしない。
- `SYSTEM_VERSION`、`CONFIG_SCHEMA_VERSION`、`STATE_SCHEMA_VERSION`を分離する。
- Codeが要求するSchemaとRuntime StateのSchemaが不一致なら`MIGRATION_REQUIRED`として通常Runnerを開始しない。
- Migration実行前にBackupを取得し、Migration結果を監査Logへ残す。
- 初期版では自動ダウンロード・自己置換・自動rollbackを必須にしない。

## 4.7 External Data Storage Contract

大容量Data Root：

```text
L:\emori\InvestmentAgentData\
├─ raw\
│  ├─ jquants\
│  ├─ edinet\
│  └─ news\
├─ normalized\
│  ├─ prices\
│  ├─ financials\
│  ├─ disclosures\
│  └─ securities\
├─ historical\
├─ archive\
├─ reports\
└─ backups\
```

Runtime内蔵SSD側には現在運用に必要な小容量情報を残す。

内蔵SSD上のCanonical State、直近Backup、Application Logについても、外付けData Rootとは別にvolume free、directory usage、daily / weekly growthを監視する。警告閾値は実測後にConfigurationで確定し、設計本文では固定しない。

```text
app/
config.json
user_status.json
state/
runtime_state / locks
queue / incident
current logs
```

External Data Storageが未接続・読書き不能の場合は`DATA_STORAGE_UNAVAILABLE`とする。Portfolio / User Status / System Statusは可能な範囲で利用可能とし、新規Data取得・Historical処理・Freshnessを必要とするBUY / ADD Proposalは停止または再評価待ちにする。復帰後はGap / cursor / last_successからCatch-upする。

保存形式の初期方針：

- Providerから取得したRaw Response / ZIP / XBRL / PDF等：原本または許諾された形式でimmutable保存。
- 時系列のNormalized Data：初期はJSONLを標準候補とする。
- 小さい単発Record / metadata：JSONを許容する。
- データ量・検索性能がボトルネックになった時点でSQLite / Parquet等への移行をBreak対象とする。
- Normalized DataからRawへのprovenance（provider、retrieved_at、source_id、content_hash等）を追跡可能にする。

WindowsのJunction / Symbolic Linkを補助的に使ってよいが、コードは`storage.data_root`を解決するStorage Manager経由でアクセスし、特定Drive letterへの直書きをBusiness Logicへ散在させない。

### Backup Location / Freshness

Canonical StateのBackupを着脱式HDDだけに依存させない。内蔵SSD側`backups/state/`へ直近N世代（初期値TBD）の復旧用snapshotを保持し、外付けHDD側は長期Backupとする。

```text
Internal SSD  = recent recovery snapshots
External HDD  = long-term backup / archive
```

`last_local_backup_at`と`last_external_backup_at`を別々に監視する。単発Backup失敗と継続無Backupを区別し、許容期間を超えた場合は`BACKUP_STALE` Warningを発生させる。外付けHDD停止中でもLocal Backupは継続する。

### Storage Pressure Degradation Order

Storage枯渇時は「書込み失敗したものから偶然止まる」実装にしない。重要度の低い大容量Dataから停止し、正本・監査・直近復旧情報を最後まで保護する。

```text
Stop first:
  News / optional raw acquisition
  Historical expansion
  Discovery bulk acquisition
  non-critical report generation

Then degrade:
  Application Log generation / retention
  Candidate-oriented raw acquisition
  non-critical archive / derived regeneration

Preserve last:
  Canonical State
  Human Decision / Correction / Execution Facts
  Decision / Audit / Incident
  current Queue / reservations
  recent local State Backup
  Position Watch Minimum Data
    - 保有銘柄の監視に必要な最小Market Data
    - 保有銘柄の必須Disclosure
    - 上記の最小Normalize / freshness判定
```

Application LogはCanonical State、Commit、Auditより低い保存優先度とし、保持量を有限にする。Application Log単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で別経路の状態表示またはIncidentへ観測可能にする。ただし同一Storageの障害がCanonical State、Atomic Commit、Auditまたは復旧可能性を危険にさらす場合は、既存のStorage Fail Closedを適用する。

`STORAGE_WARNING / STORAGE_CRITICAL`の閾値と縮退開始条件はConfiguration化し、Critical時に新規BUY / ADDを安全側に停止できる。Storage CriticalでもPosition Watch全体を無条件停止せず、保有Positionの重大Risk監視に必要なMinimum Dataset取得を優先保護する。Minimum Datasetさえ保存不能なら`POSITION_WATCH_DATA_UNAVAILABLE`をIncident化し、監視継続を装わない。 `POSITION_WATCH_DATA_UNAVAILABLE`はSystem Critical closed classには含めず、`severity = CRITICAL`、`priority = P0 / INVESTMENT`としてInvestment側のP0通知規則に従う。

------------------------------------------------------------------------

# 5. 独立した状態モデル

以下を別Entityとして管理し、一つの銘柄状態へ押し込まない。

  -----------------------------------------------------------------------
  Entity                              主な状態
  ----------------------------------- -----------------------------------
  Research                            DISCOVERED / CANDIDATE / ANALYZED /
                                      WATCH / ARCHIVED

  Thesis                              VALID / WEAKENED / INVALIDATED /
                                      UNKNOWN。改訂は履歴追加

  Proposal                            DRAFT / VALIDATED / QUEUED /
                                      APPROVED / REJECTED / EXPIRED /
                                      SUPERSEDED

  Order                               AWAITING_SUBMISSION / ORDER_OPEN /
                                      PARTIALLY_FILLED / CANCEL_PENDING /
                                      FILLED / CANCELLED / REJECTED /
                                      UNKNOWN

  Holding                             OPEN / CLOSED。数量の事実から導出

  Incident                            OPEN / ACKNOWLEDGED /
                                      RESOLVED。ProposalのTTLから独立
  -----------------------------------------------------------------------

同一銘柄に保有とCandidate、新旧Thesis、複数Decisionが併存できる。集計Positionはaccount_id＋instrument_id単位、内訳lot
/ trancheはDecisionとThesisへ多対一で紐付ける。保有数量ゼロでPosition
Watchを終了し、必要ならCandidate
Watchへ移す。すべての遷移を監査対象とする。

------------------------------------------------------------------------

# 6. 銘柄選定

## 6.1 母集団

例：東証上場銘柄。

初期版では投資対象市場を明示し、Universeを固定する。

## 6.2 一次フィルタ

LLMを使わず機械的に除外可能なものを先に落とす。

例：

-   流動性不足
-   必要データ欠損
-   上場直後
-   対象外商品
-   その他システム定義による除外

## 6.3 複数探索枝

単一の総合点で候補を作らない。

少なくとも以下の独立枝を持つ。

-   Value
-   Growth
-   Change
-   Quality
-   Event
-   Contrarian
-   Theme

各枝は独立に候補を出す。

各銘柄は以下のような探索特徴を保持する。

``` text
Ticker A

Value        ○
Growth       ×
Change       ○
Quality      ○
Event        ×
Contrarian   ○
Theme        △
```

共通除外は全枝に共通する対象外条件へ限定する。「必要データ欠損」は枝ごとに評価し、Value用指標の欠損だけでChange
/ Event候補まで除外しない。各枝はELIGIBLE / INELIGIBLE /
DATA_INSUFFICIENT /
NOT_EVALUATEDを記録し、候補は枝の和集合とする。欠損を0点へ変換しない。

------------------------------------------------------------------------

# 7. 銘柄分析

候補化した銘柄に対して、少なくとも以下を独立分析する。

-   Fundamental
-   Valuation
-   Bull
-   Bear
-   Macro
-   Risk
-   Technical
-   Portfolio Fit

各分析は、可能な範囲で他分析の結論を先に見ずに一次評価を行う。

分析後に統合処理を行う。

独立分析は同じ凍結Evidenceを参照してよいが、他枝の結論・統合Recommendationは一次評価の入力にしない。branch_id、入力hash、出力、未評価理由を保存する。別モデル／別Agentを必須とせず、論理的に隔離した呼出しで検証する。

------------------------------------------------------------------------

# 8. Contradiction Engine

統合処理の目的は「平均化」ではない。

各分析間の矛盾・未解決Relationを抽出する。

例：

``` text
Fundamental:
営業利益 +18%
→ positive

Bear:
営業CF -12%
→ earnings quality concern

Contradiction:
利益成長はcash conversionを伴っているか？
```

矛盾が重大な場合は追加調査を起動する。

追加調査には一回の検索数・時間・費用予算と停止条件を持たせる。未解決ならUNRESOLVEDを残し、重大な情報不足はBUY
/ ADD提案の発行を止める。予算未設定は無限調査を意味しない。

------------------------------------------------------------------------

# 9. 投資レポート

各銘柄レポートには以下を含む。

``` text
Company / Ticker
Current State
Strategy Class
Expected Holding Horizon

Summary
Bull
Bear
Valuation
Macro
Risk
Technical
Portfolio Fit

Contradictions
Unresolved Questions

Investment Thesis
Invalidators
Expected Events

Recommendation
Declared Reason Weights
Confidence

Suggested Allocation
Exit Conditions
```

------------------------------------------------------------------------

# 10. 人間向け判断表示

人間判断時には長文を必須にしない。

最上部に必ず以下を出す。

## 10.1 1行提案

例：

``` text
提案：A社をPortfolioの2%分購入
```

## 10.2 判断理由と重み

理由ごとの寄与度を%で表示する。

名称は **Declared Reason Weight** とする。
これは確率でも実測寄与でもなく、「AIが今回の判断時に宣言した寄与度」。

例：

``` text
35%  業績変曲点
25%  Valuation
20%  競合優位
12%  Portfolio diversification
 8%  Technical / timing
------------------------
100%
```

## 10.3 反対理由

例：

``` text
主な反対理由
- 円高リスク
- 次回決算まで40日
```

## 10.4 人間の選択肢

例：

``` text
[BUY]
[WATCH]
[REJECT]
[再分析]
```

売却系の場合：

``` text
[SELL ALL]
[REDUCE]
[HOLD]
[再分析]
```

------------------------------------------------------------------------

# 11. 人間の役割

初期版では人間の担当を以下に限定する。

1.  AI提案を判断する。
2.  判断通り証券会社で売買操作する。
3.  操作・約定結果をCopy & Pasteする。

Portfolio表を人間が手修正する運用は避ける。

------------------------------------------------------------------------

# 12. 約定結果Paste：事実受領と提案評価の分離

PasteはBrokerで起きた事実の入力であり、Proposalの有効性判定とは入口を分ける。

最低入力：account_id、instrument_id / ticker /
market、BUYまたはSELL、約定数量、約定単価、通貨、executed_atとtimezone、broker_order_id、broker_execution_id。手数料・税・受渡日・元Proposal
IDは取得状態を併記する。

1.  原文をreceipt_id、received_at、内容hash付きでinboxへ永続保存する。
2.  Schema、口座、売買方向、数量、単価、時刻、重複IDを決定論的に検査する。
3.  確認済みExecutionを§13のFact Eventへ変換しCommitする。
4.  TTL、承認内容、発注条件との逸脱は別のCompliance Recordへ残す。
5.  結果を「受領済み／適用済み／照合待ち」に区別して表示する。

**TTL失効、未承認、Policy変更を理由に、確認済みの実約定を取り込まない処理を禁止する。**
約定が期限内でPasteだけ遅れたケースと、約定そのものが期限後のケースを区別する。実約定がPolicy違反を生んでも事実を記録し、修復対象を生成する。

重複キーはbroker＋account_id＋broker_execution_id。部分約定はそれぞれ固有IDを持つ。注文全体の累計数量を新規約定数量として加算しない。IDなしは仮受領し、日時・口座・銘柄・方向・数量・価格等を照合する。同値だけで別約定を自動重複扱いしない。

実残高と矛盾する入力や方向不明は原文を保持して `RECONCILIATION_REQUIRED`
とし、推測でPortfolioへ適用しない。訂正・取消は元Executionを参照するCorrection
/ Reversal
Eventとして追加する。通知時間外でもユーザー起点のPasteへの受領応答は返す。

------------------------------------------------------------------------

# 13. Portfolio管理・Commit・発注待ち資源

Portfolioの事実状態・過去取引はBreakで変更しない。初期版では
`portfolio.json` をCurrent Canonical State Envelopeとする。履歴性の高いObservation / Audit / Stage Resultは§13.4のappend-only archiveへ分離し、Current Envelopeを無制限に肥大化させない。`state_version`
は注文・承認・予約・Queueの変更でも増える。旧 `portfolio_version` は
`state_version` へ移行し、保有数の変化だけを競合判定に使わない。

## 13.1 必須Schema

  ------------------------------------------------------------------------------------------------------------------------
  領域                                必須内容
  ----------------------------------- ------------------------------------------------------------------------------------
  Metadata                            state_id, schema_version, state_version, commit_id, committed_at, system_version,
                                      policy_version

  Facts                               accounts、cash
                                      ledger、positions、lots、確認済みexecutions、入出金・配当・税・手数料・Corporate
                                      Action・訂正Event

  Observations                        price / FX / sector /
                                      liquidityとas_of、published_at、retrieved_at、source_id、revision_id、content_hash

  Judgments                           immutable decisions、thesis revisions、role / horizonの分類履歴

  Workflow                            proposals、approvals、orders、reservations、execution_slot、watch
                                      registrations、decision_queue、incidents、user_status

  Commit support                      applied_event_ids、監査records、outbox、input references、previous_commit_id
  ------------------------------------------------------------------------------------------------------------------------

事実・観測・判断を別領域に置く。Judgmentは判断という行為ではなく、Decision、Thesis revision、分類等の判断結果を保持するデータとして扱う。時価やallocationは数量・観測価格から導出し、取得単価やCashと混同しない。金額計算は通貨ごとのDecimal
/ 最小通貨単位と明示した丸め規則を使う。

現金はledger balance、unsettled
receivables/payables、broker買付余力の観測、local reserved
cashを区別する。計算方式ごとに受渡・予約が既にBroker値に含まれるかを明示し、同じ約定代金や予約を二重控除しない。売却代金の利用可能時点はBroker条件が確認できたものだけ反映する。

Dividendは税引前・源泉税・実受領額を分け、Cashへ戻す。株式分割等は適用日と数量・簿価の変換を記録する。未確定手数料は見積額を別管理し、後日確定差分を追加する。現金・数量・簿価の保存則と口座照合結果を検証する。

## 13.2 Single Writerの実行契約

LLMはUpdate Requestを生成する。正本更新は固定されたReducer / Validator /
Commit Writerを通す。

初期ローカルBackendは、**全Writerが同じ排他ロックを取得し、ロック内で版照合から原子的置換まで実行する**。ロックだけをLLMの約束にせず、OS
/
filesystemの機構をコードから使う。別プロセスの競合・中断・再起動時の挙動はCV-07
/ 12 / 20で確認する。

1.  Factは永続inboxに受領済みとする。Commandはrequest_idを持つ。
2.  排他ロック取得後に正本を再読込し、expected_state_versionと比較する。
3.  Factはapplied_event_idsで冪等化し、最新状態へ適用する。Commandは最新状態・Policy・TTL・資源を再検証する。
4.  新Envelopeへ状態、applied_event_ids、監査Record、outboxをまとめて構築し、Schemaと整合性を検査する。
5.  同一filesystem内の一時ファイルへ書き、内容をflush / fsync後、atomic
    replaceし、利用可能な耐久化手段でディレクトリ更新も確定する。ロックはここまで保持する。
6.  Commit成功後にProjectionとMarkdownを生成し、outboxを配送する。再処理はevent_idで冪等化する。

旧版か新版のどちらかが読め、破損した中間状態を正本にしない。OS /
filesystem上で保証できない工程は未確認としてCVへ残す。クラウドBackendへ替える場合は同等の永続性とサーバー側conditional
write / CASを要求し、単なるread→version比較→writeで代用しない。

Commit前停止：inboxを再適用。Commit後・ログ前停止：applied_event_idsで二重計上を防ぎoutboxから再生成。ログ生成失敗はCommit済み事実を巻き戻さない。監査データを保持したsnapshot
/ archive手順なしにapplied IDsや履歴を削除しない。

Factの競合は再読込・重複判定して適用する。Commandの競合は再計算し、数量・注文条件等が変われば旧ProposalをSUPERSEDEDにして新ProposalをQueueへ戻す。承認を流用しない。

## 13.3 初回は未解決発注一件の直列運用

対象は全管理口座を通じて一件。承認Commitで `execution_slot`
を占有し、BUYは注文の最大支払額＋費用余裕、SELLは売却数量を予約する。必要現金は自由Cashを超えてはならず、SELL予約は未予約保有数量以下とする。

別Tradeの分析・重大Risk監視は継続するが、次の売買承認・発注案内は保留する。売買を要求しないHOLD
/ WATCHやIncident確認まで止めない。

発注前再検証後に人間がBroker操作する。発注報告を受けOrderをORDER_OPENへ進める。部分約定ごとに保有・Cash・残予約を更新する。未発注の中止は人間の未発注確認、発注済みの終了はBrokerの全約定・拒否・取消確定と約定照合を必要とする。

**TTL切れ・応答なし・アプリ停止だけでSlotや予約を解放しない。**
CANCEL_PENDING /
UNKNOWNでは維持する。取消確定数量と全約定累計を照合して残予約を解放する。取消後に遅れて届いた実約定も§12で受領し、不一致を照合対象にする。

100万円に対する70万円案A /
Bは、A承認Commit後にBを承認できない。Slotの原子的確保は直列運用でも省略しない。将来の複数注文化は予約状態機械の拡張と再試験を要する。

------------------------------------------------------------------------

## 13.4 Current Envelope / Append-only Archive / Compaction

「単一Canonical State」は全履歴を一つの巨大JSONへ無期限に埋め込む意味ではない。

初期Local構成を以下に分離する。

```text
state/portfolio.json
  = 現在の取引・Workflow状態 + recoveryに必要な直近参照

archive/events/YYYY-MM.*
  = 確定Fact Event / Correction / Corporate Action

archive/observations/YYYY-MM.*
  = price / FX / liquidity等の時系列Observation

archive/audit/YYYY-MM.*
  = immutable audit records

stage/YYYY-MM.*
  = Durable Stage Result / Model output provenance
```

Current Envelopeにはarchive recordのID / hash / range / high-water markを保持し、参照先なしに履歴を消さない。

Archiveはappend-onlyを基本とし、月次等でrotateする。CompactionはHuman-visibleな保守Jobとして以下を満たす場合のみ行う。

1. archive対象範囲のhash / record count / first-last IDを確定する。
2. 新archiveを作成し検証する。
3. Current Envelopeへarchive manifestをAtomic Commitする。
4. Recovery試験で再構成できることを確認する。
5. 古い重複ファイルはRetention Policyに従って後から削除する。

`applied_event_ids`は無期限に全IDを保持するのではなく、直近window + archive high-water mark / dedup indexで冪等性を維持できる構造へ発展可能とする。初期MVSでは件数が小さいため単純保持を許容するが、Archive / Compaction Contractを破らない。

SQLite等への移行時もCurrent State / immutable event history / observation history / audit / stageの論理分離を維持する。

------------------------------------------------------------------------

# 14. Portfolio内の役割

保有銘柄には役割を持たせる。

例：

-   INCOME
-   GROWTH
-   EVENT
-   DEFENSIVE
-   OTHER

------------------------------------------------------------------------

# 15. 高配当Core枠

長期運用では高配当株を一定割合保持できるようにする。

初期段階で比率固定はしない。

将来的な目安例：

``` text
Core / Income       30%
Long Growth         20%
Medium              25%
Short / Event       10%
Cash                 15%
```

比率はBacktest / Paper Trading / Breakで調整する。

高配当銘柄の評価では以下を重視する。

-   配当利回り
-   配当持続性
-   FCF
-   配当性向
-   財務健全性
-   事業構造
-   減配リスク

------------------------------------------------------------------------

# 15A. Portfolio Policy

Core /
Incomeと短中期投資の資金競合を管理する。数値は実装時のユーザー設定とし、未設定は
`status: UNCONFIGURED`、各値はnullで保持する。未設定Policyでは本番のBUY
/ ADD提案を有効化しない。

対象BucketはINCOME / GROWTH / EVENT / DEFENSIVE / OTHER /
CASH。各Bucketにtarget / min /
maxを必須定義する。利用しないBucketも、明示したゼロ配分などの設定を行い、未設定と区別する。値の範囲・集計・Modeは§15Bに従う。

配当金は税・費用を分けてCashへ戻し、次のAllocationで配分を判断する。自動DRIPは初期必須要件にしない。

------------------------------------------------------------------------

# 15B. Portfolio Policyの強制レベルと構築・回復

`target` はAllocationが考慮するSoft、`min / max`
は決定論的に適用するHardとする。Policy設定は `UNCONFIGURED / ACTIVE`
を持ち、未設定値を0や無制限へ暗黙変換しない。

役割BucketはINCOME / GROWTH / EVENT / DEFENSIVE / OTHER /
CASHの網羅的かつ相互排他的な集計とする。保有期間SHORT / MEDIUM /
LONGは別の分類軸とし、役割比率と足し合わせない。兼用銘柄は承認済み分類ルールでlot単位の役割を確定し、二重計上しない。

Policy有効化時に範囲、min ≤ target ≤ max、min合計 ≤ 1 ≤
max合計、通貨、評価分母、手数料、買付単位、実行可能性を検査する。資産ゼロや評価不能時はratio判定を成立したと扱わない。

## Mode

-   **NORMAL**：適用対象Hard制約を取引後状態で満たす。
-   **BOOTSTRAP**：初期Cashから段階構築するための、明示承認された一時的許容集合を使う。
-   **REPAIR**：価格変動・実約定・Thesis対応等で発生した違反から段階回復する。

BOOTSTRAP /
REPAIRは適用constraint_id、開始値、許容幅、期限、進捗目標、終了条件を設定に持つ。LLMがその場でModeを切り替えない。期限到来は停止・再承認対象となり、基準値をリセットして未達を隠さない。

上限制約の違反量を `max(0, exposure - max)`、下限制約を
`max(0, min - exposure)`
とする。比較は同じ価格・FX・評価時刻・分母規則で行う。

REPAIRの候補は、取引前に正常だった適用制約を新たに破らず、既存違反量を増やさず、対象違反の少なくとも一つを厳密に減らす。取引費用等による連動違反も計算する。非悪化だけの無進捗取引を回復と呼ばない。

BOOTSTRAPは未充足のBucket minと初期Cash
max等、開始時に列挙した例外だけを段階解消する。たとえばINCOME
min未達を改善する最初のBUYは、全minを一度に満たさなくても、承認済み構築規則と他のHard制約を満たせば許可できる。

売却の扱いは§17Aの制約別適用表による。risk-reducingというLLMのラベルだけで任意のHard制約を免除しない。許容中の違反もState
/ Log / 次回Allocationへ残す。

------------------------------------------------------------------------

# 16. 保持期間

単一の固定保持期間は採用しない。

3区分とする。

## SHORT

数日〜数週間

対象例： - イベント - 決算 - 価格乖離

## MEDIUM

数か月〜1年程度

対象例： - 業績変化 - テーマ - Valuation是正

## LONG / CORE

1年以上

対象例： - 配当 - Quality - 長期成長

保持期間は強制SELL条件ではなく「想定時間軸」。

------------------------------------------------------------------------

# 17. 売却・損切判断

損切りは単純な損失率のみで決めない。

以下の4種類を使う。

## 17.1 Thesis Stop

購入理由が崩壊。

最優先。

## 17.2 Risk Stop

Portfolio上のリスク増大。

例： - 特定業種への集中 - 相関上昇 - リスク上限超過

→ REDUCE候補。

## 17.3 Price Stop

急落を強制再分析Triggerとして扱う。

例：

``` text
-8% / day
-15% / 5 days
```

価格条件のみで即SELLは原則行わない。

## 17.4 Time / Opportunity Cost Stop

想定時間軸を超えて投資仮説が実現しない場合、資金を置き続ける価値を再評価する。

------------------------------------------------------------------------

# 17A. Hard Risk Policy / Deterministic Risk Validator

Hard Risk
Gateは、銘柄の魅力度を判断しない決定論的コードとする。入力はimmutable
proposed_trade、最新State、risk_policy、portfolio_policy、価格等のEvidence、評価時刻。出力はPASS
/ REJECT / ADJUST_REQUIRED /
DATA_INSUFFICIENT、constraint別理由と計算値。

初期運用は現物株のみ、信用・レバレッジ・空売り禁止。Single Position
Max、Sector Exposure Max、Cash min、Bucket
min/max、Liquidity、許容データ鮮度、注文金額上限、費用余裕、危機時ルールを設定対象とする。必要値未設定では
`POLICY_NOT_READY` とし、運用BUY /
ADDを有効化しない。テスト用値は本番設定と分離する。

  --------------------------------------------------------------------------------------------------------------------------------------------------------------
  制約                                       BUY / ADD                    SELL / REDUCE
  ------------------------------------------ ---------------------------- --------------------------------------------------------------------------------------
  口座・商品・正の数量・有効単位・承認一致   必須                         必須

  現金・費用・予約                           支払上限が自由Cash以下       費用を含め照合。売却で新たな借入を作らない

  保有数量・空売り禁止                       現物のみ                     予約を除く売却可能数量以下。免除不可

  単一銘柄・Sector上限                       NORMALまたは承認済みMode     超過25%→20%の縮小を許可可能。上限15%への一括回復は必須にしない

  役割Bucket min                             NORMALまたは構築・回復規則   指定した保有リスク縮小SELLはmin割れを許容し記録

  Cash max                                   Policyに従う                 現金化で超過してもリスク縮小SELLを妨げず修復対象にする

  Liquidity min                              購入Gate                     既存低流動性保有の縮小を一律拒否しない。発注可能性・注文上限・執行条件を別途必須確認

  鮮度・評価不能                             不足ならDATA_INSUFFICIENT    既知の数量減少と評価不能の影響を分離。必要な執行情報が不足ならPASSにしない
  --------------------------------------------------------------------------------------------------------------------------------------------------------------

SELLの例外は事前Policyのconstraint_idに限定する。指定Positionの数量・絶対Exposureが減り、空売りや新たな借入を作らず、例外外の違反を悪化させないことを機械計算する。売却後の他銘柄比率増加等も再評価し、Policy外の連動違反ならADJUST_REQUIREDとする。

結果にはtrade_hash、state_version、policy_hash、validator_code_hash、evidence_hash、evaluated_atを結び付ける。変更された数量や古いPASSを流用しない。通知前・最終承認Commit・発注前に必要な再検証を行う。

**CV-16A：計算が正しいこと。CV-16B：正本更新・承認・PASS表示の経路から迂回や改変ができないこと。**
同じLLMがPolicy、Code、State、PASS表示を自由に書ける構成ではCV-16BをPASSとしない。権限分離を確認できるまで、観測付き試験運用に限定し、強制された安全Gateと表示しない。必要ならWriter
/ Validatorの保護された実行境界をLocal化する。

Policy変更は銘柄提案と分離した承認対象。実約定の事実取り込みを、このProposal用Validatorで拒否しない。

------------------------------------------------------------------------

# 18. Watch構造

Watchを3種類に分ける。

## 18.1 Position Watch

保有中。

目的： - 投資仮説が維持されているか - Invalidatorが発生していないか -
重大Eventが発生していないか

短周期・高優先度。

## 18.2 Candidate Watch

分析済みだが未保有。

目的： - 買わなかった理由が解消されたか - Valuationが改善したか -
新Eventが発生したか

## 18.3 Market Watch

まだ候補化していない市場全体。

銘柄選定の入口。

------------------------------------------------------------------------

# 19. Allocation

「買うか」と「いくら買うか」は別判断にする。

入力：

``` text
Stock attractiveness
+
Portfolio State
+
Portfolio Policy
+
Cash
+
Existing exposure
+
Sector exposure
+
Correlation
+
Risk Policy
```

Portfolio Policyの `target / min / max`
はAllocationの明示的制約として扱う。

処理：

``` text
Analysis
  ↓
BUY attractiveness
  ↓
Allocation Engine
  ├─ Portfolio State
  ├─ Portfolio Policy
  ├─ Cash
  ├─ Existing Exposure
  └─ Risk
  ↓
Proposed Trade
  ↓
Deterministic Risk Validator
  ↓
Human Proposal
```

出力：

``` text
Suggested Allocation
```

現金維持も有効な選択肢。

最終出力は比率に加えて§25の具体的Tradeとする。支払可能額は現金の見かけ残高でなく、受渡条件・費用・予約を反映する。ValidatorからHumanへの表示は必ず§24のQueueを通す。

------------------------------------------------------------------------

# 20. 追加投資

余剰資金がある場合は、既存保有株への追加と新規候補を競争させる。

``` text
Available Cash
  ↓
Existing Positions
Candidate Watch
Cash Reserve
  ↓
Marginal Opportunity Ranking
  ↓
Allocation Proposal
  ↓
Human Decision
```

この概念フローのAllocation ProposalからHuman
Decisionまでには、§17AのValidatorと§24のQueueが必須。初回の同時発注数は§13.3に従う。

------------------------------------------------------------------------

# 21. User Status / Internal Human Capacity

ユーザーが直接操作する概念は **User Status** とし、以下の3値とする。

-   `FREE`
-   `NORMAL`
-   `BUSY`

これはConfigurationではなく、人間の現在状態である。IMのPresence Statusのように簡単に変更できる操作を前提とする。

```text
STATUS FREE    = 余裕あり
STATUS NORMAL  = 通常
STATUS BUSY    = 忙しい / 認知負荷をかけられない
```

内部ではStatus MapperによりHuman Capacityへ変換する。

```text
STATUS FREE    → human_capacity LARGE
STATUS NORMAL  → human_capacity MEDIUM
STATUS BUSY    → human_capacity SMALL
```

`human_capacity`は内部制御値であり、User Statusとは別概念とする。UIでは原則Statusを表示し、Capacityをユーザー入力項目にしない。

User StatusはAIが推定しない。ユーザーが明示的に変更する。ただしBUSYだけは**期限付きLease**を設定でき、期限切れ時は規則に従って自動遷移してよい。

初期Local版では`CRITICAL`等の追加User Statusを設けない。数週間〜1か月単位でHumanが完全に応答不能になる場合はRunnerを正常終了させ、Local Process停止中の監視継続を保証しない。将来Server常駐化し「Systemは稼働継続するがHumanは長期不在」という状態が必要になった場合に、`UNAVAILABLE`等のHuman Availability拡張をBreak / ADR対象として再検討する。

## 21.1 BUSYの非対称性

`FREE / NORMAL → BUSY`は通知や提案量が多いことでユーザー自身が忙しさに気づき、変更契機が自然に存在する。

`BUSY → NORMAL / FREE`は通知が抑制されるため、ユーザーがStatus変更を忘れる経路がある。BUSYが永久に残るSticky Stateを避けるため、初期UIではBUSY設定時に終了条件を選べるようにする。

```text
STATUS = BUSY

終了条件:
[ 1時間 ]
[ 3時間 ]
[ 今日いっぱい ]
[ 今週いっぱい ]
[ 変更するまで ]
```

期限付きBUSYの終了後は原則`NORMAL`へ戻す。`FREE`へ自動遷移しない。「忙しくなくなった」と「暇である」を同一視しないためである。

ユーザーが明示的に`BUSY → FREE`へ変更することは許容する。

## 21.2 BUSY Leaseの時刻規則

内部保存はtimezone付きISO 8601の**排他的終了時刻**`effective_until`を使う。

-   `1時間`：設定時刻 + 1時間
-   `3時間`：設定時刻 + 3時間
-   `今日いっぱい`：翌日00:00まで
-   `今週いっぱい`：**カレンダー週を日曜00:00開始〜土曜24:00終了と定義し、次の日曜00:00まで**
-   `変更するまで`：`effective_until = null`

したがって水曜日に「今週いっぱい」を選んだ場合、その週の土曜24:00までBUSYが有効であり、内部値は次の日曜00:00を`effective_until`として保持する。

例：

```json
{
  "status": "BUSY",
  "changed_at": "2026-09-09T10:00:00+09:00",
  "effective_until": "2026-09-13T00:00:00+09:00",
  "after": "NORMAL",
  "lease_type": "END_OF_WEEK"
}
```

期限なしの場合：

```json
{
  "status": "BUSY",
  "changed_at": "2026-09-09T10:00:00+09:00",
  "effective_until": null,
  "after": null,
  "lease_type": "UNTIL_CHANGED"
}
```

期限付きBUSYでは`after = NORMAL`を初期既定値とする。将来別の遷移を許す場合は設計変更として扱う。

Status変更は`StatusChangeCommand`としてStatus Writerへ投入する。`user_status.json`をユーザーが直接編集する通常運用は禁止する。

```text
Human CLI / Tray
  ↓
StatusChangeCommand
  ↓
Validate command / resolve lease
  ↓
Acquire Status Writer lock
  ↓
Check status_version
  ↓
Atomic replace
```

Lease期限切れは独立した`StatusLeaseJob`としてRunnerのDue判定対象にする。

```text
should_run = status == BUSY
             AND effective_until != null
             AND now >= effective_until
```

PC停止等で遅延した場合、契約上の`effective_until`と実際に遷移を適用した`applied_at`を両方記録する。期限切れJobが古い`status_version`を読んだ後に人間がStatusを再設定した場合、自動遷移はversion conflictとして破棄する。

## 21.3 Status Maintenance

通常の投資通知をBUSYで抑制しても、Statusそのものの維持通知まで抑制するとSticky Stateが再発する。そのためStatus Maintenanceは投資通知とは別classで扱う。

BUSY Lease終了時は、`BUSY → NORMAL`を先にState Transitionとして適用し、その後必要なら以下のような軽量通知を出せる。

```text
BUSY設定が終了しました
STATUS = NORMAL
[ FREE ] [ NORMAL ] [ BUSY ]
```

Status Maintenanceは投資P0とは別であり、売買Proposalを意味しない。頻度は抑制し、Lease終了やユーザー操作等のStatus変化時だけを基本とする。

Status Transition自体は期限到達後の最初のRunner機会に適用するが、Status Maintenance通知は§22のNotification Windowを破らない。**独自の配送機会を生成せず、次の許可Window内の配送へ相乗りする**。たとえば平日10:00にBUSY Leaseが切れた場合、StateはNORMALへ遷移し、通知は次の許可Windowで提示する。

------------------------------------------------------------------------

# 22. 通知可能時間・Emergencyの扱い

通知時刻は `Asia/Tokyo` で評価し、保存時刻はtimezone付きISO
8601とする。平日／土日は暦日で判定し、取引所営業日・取引可能時間は別管理する。

  STATUS   平日                                     土日
  -------- ---------------------------------------- ----------------
  FREE     12:00以上13:00未満、17:30以上24:00未満   通知可
  NORMAL   17:30以上24:00未満                       通知可
  BUSY     17:30以上24:00未満                       通知可、P0のみ

Investment Emergency Overrideは初期`disabled`とする。**BUSY中の平日日中でも重大Investment Riskの検知・記録・分析は続け、Investment P0の自動通知は17:30まで待つ。**「重大Risk監視の維持」は通知時間制約の上書きを意味しない。Local Process停止中の監視継続を保証する意味でもない。

System Critical OverrideはInvestment Emergency Overrideと別設定にする。初期値は`UNCONFIGURED`とし、初期Setup時にHumanが`ENABLED / DISABLED`を一度選択する。設計書の確定やDefault値をHuman同意とみなさない。

System Critical Overrideの対象は投資判断を要求しない以下の**closed class**に限定する。

```text
CANONICAL_STATE_CORRUPTION
DATA_STORAGE_IDENTITY_MISMATCH
ENVIRONMENT_BINDING_MISMATCH
MIGRATION_REQUIRED
RUNNER_LOCK_RECOVERY_REQUIRED
```

対象classの追加はConfiguration変更ではなくDesign / Change Proposal対象とする。AgentがInvestment EventをSystem Criticalとして迂回配送することを禁止する。`ENABLED`時のみBUSY / Notification WindowをOverrideして即時通知できる。`DISABLED`時もAlert / Incident記録は継続する。

System Criticalにも`dedup_key`、`renotify_after`、`max_popup_per_incident`を適用し、起動繰返し等によるPopup stormを防ぐ。

通常の不適切TradeをHard Risk Gateが拒否しただけなら内部修正対象とし、自動的にP0へ上げない。既保有資産の重大Incident、正本不整合、制御系故障を別classで管理する。

ユーザーが自ら開いた画面の閲覧や質問への応答は、自発的なPush通知と区別する。

------------------------------------------------------------------------

## 22.1 Notification Opportunity / Delivery Latency

Local版では「Eventを検知した時刻」と「Humanへ配送可能になった時刻」を分ける。

初期`emergency_override=false`では、通知窓を逃したP0も**次の許可Windowまで保持する**。PCが次のWindowでも停止していれば、さらに次のPC稼働かつ許可Windowまで待つ。起動直後だからという理由だけでUser Status / notification policyを破らない。

以下を別々に計測する。

```text
Event published
→ PC availability wait
→ polling wait
→ data acquisition
→ analysis
→ Queue wait
→ notification-window wait
→ delivery attempt
→ human response
→ market execution opportunity
```

P0の`first_detected_at`、`first_queue_ready_at`、`first_delivery_opportunity_at`、`delivered_at`を保存する。

実測最大通知遅延がStrategyの`required_latency`を満たさない場合、そのStrategyをLocalでSupportedとせず、Notification OverrideまたはServer移行をBreak対象とする。

------------------------------------------------------------------------

# 23. Status別の処理

## STATUS = FREE

内部capacity: LARGE

処理： - 新規BUY - ADD - SELL - Allocation - Break - 改善提案 -
通常Watch

## STATUS = NORMAL

内部capacity: MEDIUM

処理： - Position Watch - 有力Candidate - BUY / SELL - 重要ADD -
Portfolio Risk - 重大Break

## STATUS = BUSY

内部capacity: SMALL

処理： - Position Watch - 重大Risk - Thesis崩壊 - 重大SELL -
配当Core監視

原則停止： - 新規探索 - 通常Break - 細かな改善提案 - 通常Candidate通知

BUSYのLease終了時は§21に従い`NORMAL / MEDIUM`へ戻し、その時点でQueueを再評価する。Status変更そのものによって古いProposalをそのまま大量配送しない。

各Statusでの通知可否、通知時間帯、priority、Overrideは§22および§24.0のNotification Policyを正本とし、本節では再定義しない。BUSYという理由だけで通常通知を即時配送せず、BUSY専用の重大Risk Email通知も初期設計へ追加しない。

------------------------------------------------------------------------

# 24. Decision Queue・Incident・通知配送

## 24.0 Severity / Priority / Delivery Contract

`severity`と`priority`は別軸とする。

- `severity` = 事象自体の重大度（INFO / WARNING / CRITICAL）
- `priority` = 人間へいつ届けるべきか（P0〜P3等）

SeverityからPriorityへ暗黙変換せず、Alert生成時に両方を決定する。

| Class / Severity | 例 | Delivery |
|---|---|---|
| INFO | 完了通知、Status Maintenance | 通常Notification Windowに従い、独自配送機会を作らない |
| WARNING | Budget 85%、Adapter degraded、Backup failure、Storage growth warning | 通常Windowに従う。BUSY中はQueueへ蓄積しCLIでは確認可能 |
| CRITICAL / SYSTEM | §22 closed classのSystem障害 | Alert Queue。`system_critical_override=ENABLED`時のみBUSY / WindowをOverrideして即時Windows Popup。投資P0とは別管理 |
| P0 / INVESTMENT | 保有銘柄の重大Incident | §22のInvestment P0 Notification Policyに従う |

Windows Popupの表示成功をHuman acknowledgementとみなさない。Alert Queueが正本であり、`delivered_at`と`acknowledged_at`を分離する。


Alertは表示そのものを正本にせず、Durableな`Alert Queue`を正本とする。

```text
Alert/Event
  ↓
Alert Queue
  ↓
Notification Router
  ├─ CLI Adapter
  ├─ Windows Toast / Popup Adapter
  └─ Email Adapter   # Deferred / Optional
```


Windows Popupは配送手段であり、表示成功をHuman確認とみなさない。Alertは少なくとも`created / delivered / acknowledged / resolved`を区別し、`alert ack <id>`で明示確認可能にする。

Emailは初期必須としない。SMTP / OAuth / Secret / Retry / duplicate-send等の追加複雑性があるため、必要性が実測された場合にNotification Adapterとして追加する。

Human Decisionを要求する通常分析、Version
Conflict後の再提案、Event、Emergency、Breakの全Proposalを同じQueueへ入れる。各Agentから直接通知しない。

優先度はP0＝既保有の重大Risk等、P1＝重要再評価、P2＝通常投資機会、P3＝改善・低優先判断とする。情報のみのWatchは通知待ちProposalにせず記録する。Statusごとの対象は§23に従う。

配送順：Relevance → Duplicate → TTL / Validity → Priority → User Status / Capacity →
Notification time → Durable outbox → Human。

## 24.1 再評価

BUSY /
NORMALからの復帰時と配送直前に、期限切れProposalはEXPIRED、重要条件変更はREANALYZE、有効案件はRERANK、重複はMERGE、実質変化なしはKEEP
SILENTとする。期限切れProposalは監査履歴に残す。

**Proposalの失効でIncidentを削除しない。**
Incidentは対応不要になった証拠とRESOLVED理由が揃うまで保持し、必要なら新Proposalを生成する。ACKNOWLEDGEDは認知済みであり、売買承認・注文済み・解決済みを意味しない。

incident_id、dedup_key、last_material_change、last_notified_at、acknowledged_at、next_review_atを持つ。未応答P0は承認済み間隔で再通知対象へ戻す。再通知間隔・一回上限は試験前に設定し、未設定を無限通知として扱わない。

## 24.2 配送と障害

通知はnotification_idを持ち、送信試行・送信成功・配信確認・ユーザー認知を区別する。配送先が冪等化に対応する場合は同じIDで再試行する。送信直後停止で結果不明ならUNKNOWNと記録し、二重通知の可能性を隠さない。外部配送までexactly-onceとは保証しない。

通知失敗・時間待ち・Slot待ちでもIncident監視は続ける。発注待ちの案件に別SELLを自動承認せず、人間へ状況確認・取消判断をQueueで提示する。

------------------------------------------------------------------------

## 24.3 Human Decision Impact / Human Correction Contract

Human Decisionは通知Priorityとは別に`decision_impact = LOW | MEDIUM | HIGH`を持てる。これは誤入力の重大度を自動決定するものではない。**初期版では記録・表示・監査用metadataであり、CLIの承認手順や確認回数を`decision_impact`だけで分岐させない。** Paper運用で必要性を観測した場合に、再確認等をBreak / Change Proposalで追加する。

初期例：

- `LOW`：WATCH、REANALYZE、軽微な改善確認
- `MEDIUM`：通常REDUCE / ADD、Candidate昇格等
- `HIGH`：新規BUY、大幅SELL、Budget上限増額、Break / Paid Service承認等

Human入力は誤る可能性があるため、過去Recordを直接書換えず**Correction / Supersede**で訂正する。

```text
Original Human Command / Fact
  ↓
CorrectionCommand
  ↓
Validation + current execution-state check
  ↓
Correction Record append
  ↓
Old Record = SUPERSEDED / CORRECTED
  ↓
Current State再計算 / reservation・slot再評価
```

少なくともDecision、Execution Paste、Cash / Position Fact、Budget変更等のHuman入力にCorrection経路を持つ。User Statusは誤設定しても単純な最新Status変更で通常回復できるため、特別なCritical扱いをしない。

Decision訂正はBroker操作のRollbackを意味しない。まだ`AWAITING_SUBMISSION`ならCorrectionによりApprovalをSupersedeし、必要なreservation / slotを解放できる。すでにBroker注文・約定が存在する場合は事実を消さず、取消・反対売買・保有継続等を新しいHuman Decisionとして扱う。実約定Factは§12の非拒否原則を維持する。

Correction Recordは少なくとも`correction_id`、`target_record_id`、`reason`、`submitted_at`、`human_actor`、`before_hash`、`after_hash`を持つ。理由の初期候補に`HUMAN_INPUT_ERROR`を含める。

**CorrectionはSystem Governance Hard Ruleを迂回する権限ではない。** Correctionの結果として費用Commitmentが拡大する場合（Budget上限引上げ、Free→Paid、Plan Upgrade、Paid Add-on、有料Fallback有効化等）はCorrection Recordだけでは成立せず、§37A Paid External Service GovernanceのHuman Approval要件を満たす。Risk Policy、State Integrity、Environment Binding等のHard Ruleも同様にCorrectionより上位とする。

```text
Correction Command
  ↓
Correction Validation
  ↓
System Governance Hard Rules
  ├─ Paid Service Governance
  ├─ Risk Policy
  ├─ State Integrity
  └─ Environment Binding
  ↓
Commit
```

------------------------------------------------------------------------

# 25. Proposal TTL・承認対象

Proposalはproposal_id、revision、trade_hash、created_at、valid_until、機械評価可能なvalid_if、基準state_version、System
/ Policy / Evidence / Validator hashを持つ。

Tradeにはaccount、instrument、side、quantity、order_type、limit_price等の価格条件、発注期限、想定最大費用、理由、参照Thesisを含める。比率だけの「2%購入」表示で承認を完了させない。

人間の承認はそのProposal revision /
trade_hashに結び付ける。承認前の再検証でState差分があっても、条件不変かを再計算して確認する。数量・注文条件・Policy等の実質変更は新Proposalと再承認を要する。

TTLは新規承認・発注を許す期限。`valid_if`
は価格・新決算有無・Thesis状態・データ鮮度等を評価し、UNKNOWNをtrueにしない。期限切れ／条件違反ではEXPIRED、再分析を行う。

発注済み注文はProposal
TTLから独立する。必要な取消を人間へ依頼し、Broker取消確認までは残注文・予約を維持する。実約定の取り込みは§12による。

------------------------------------------------------------------------

## 25.1 After-close Approval → Next-session Execution

日本株では夜間にProposalを承認し、実発注が翌営業日になる経路を通常フローとして扱う。

```text
After-close Proposal
  ↓
Human Approval
  ↓
execution_slot / reservation確保
  ↓
AWAITING_SUBMISSION
  ↓
Next market-session pre-submit revalidation
  ↓
conditions unchanged → Broker operation
conditions changed → SUPERSEDE / new Proposal / re-approval
```

承認時の`limit_price`、最大支払額、valid_if、Evidence鮮度には翌営業日まで有効な条件を明示する。

翌営業日の発注前に少なくとも以下を再検証する。

- 最新取得可能価格と価格条件
- 新規Disclosure / Earnings / material newsの有無
- Thesis / Incident状態
- Portfolio / Cash / reservation
- Policy / Validator
- Proposal TTL / market-session validity

条件変更がTrade内容に影響する場合、承認済みTradeを黙って書き換えない。旧Proposalを`SUPERSEDED`にし、旧Slot / reservationの扱いを原子的に整理した上で新ProposalをDecision Queueへ戻す。

注文条件が不変でvalid_if内なら、同じ承認を利用して発注可能とする。発注済みOrderはProposal TTLとは独立する。


### Budget不足時のPre-submit Revalidation

Pre-submit revalidationを決定論的部分とModel / External interpretation依存部分に分ける。

```text
Deterministic:
- price / limit condition
- portfolio version / cash / reservation / slot
- policy / validator
- TTL / validity

Model / External interpretation dependent:
- new disclosure interpretation
- earnings interpretation
- material news assessment
- thesis / incident interpretation
```

Budget / quota / provider障害により後者を完了できない場合、決定論的部分だけを根拠に発注しない。

```text
PRE_SUBMIT_REVALIDATION_INCOMPLETE
  ↓
Trade = HOLD_FOR_REVALIDATION
  ↓
DO NOT SUBMIT
  ↓
System Incident / Alert
```

予約・Slotは`pre_submit_hold_ttl`の間だけ維持する。TTLを超えて再検証不能ならProposal / TradeをExpireし、reservationとslotを原子的に解放する。`pre_submit_hold_ttl`の運用値はUNCONFIGUREDから明示設定する。

------------------------------------------------------------------------

# 26. 定期処理

Local RunnerのLoopから周期条件に従って実行する。

初期案：

## Daily

-   Position Watch
-   Significant Event Check

## Weekly

-   Candidate Watch
-   Portfolio Review

## Monthly

-   Stock Selection
-   Performance Report
-   System Health Report

## Quarterly

-   Architecture-level Break

頻度は運用結果を見てBreakで変更する。

各Runはscheduled_for / started_at / finished_at /
statusを保存する。アプリ停止・端末休止・通信断中の実行は保証せず、未実行期間を検出して復旧時にGapとして記録する。市場データの全期間再取得が不可能なら欠落を隠さない。

------------------------------------------------------------------------

# 27. Event-driven処理

重要Eventは定期処理を待たない。

例：

-   Earnings
-   TDnet
-   Major price move
-   Important news
-   Dividend cut
-   Guidance revision
-   Large shareholder change
-   Regulation change

処理：

``` text
Event
  ↓
Evidence Update
  ↓
Watch
  ↓
Compare with Original Thesis
  ↓
Thesis unchanged / strengthened / weakened / invalidated
  ↓
Full Analysis if needed
  ↓
ADD / HOLD / REDUCE / SELL
  ↓
Human Decision
```

「Event-driven」は取得済みEventを次の月次／週次分析まで待たずに処理する意味であり、TDnet等の即時Pushを保証しない。取得手段がpollingなら取得間隔と遅延を明記する。最終提案はValidator
/ Queueを通す。

------------------------------------------------------------------------

# 28. Markdownログ

すべての重要判断を.mdとして保存する。

目的：

-   人間監査
-   Claude等の別AIによる独立監査
-   過去判断の再現
-   System version比較
-   Break材料
-   学習・評価材料

MarkdownのDecision / Audit Logとは別に、Runtime、Job、Adapter、Error等の運用・障害解析用Application Logを持つ。Application Logは`Asia/Tokyo`の日付境界によるDaily rotationとし、`logs/application/YYYY-MM-DD/`のように日付単位で管理可能な構造にする。Secret、Credential、Token等の機密情報を記録しない。§4.4に従い、API key、Authorization header、未redactのdebug dumpも記録しない。

Application LogはCanonical State、Fact、Event、Audit Recordの代替ではない。Application Logを削除しても、投資判断、状態、履歴等のCanonicalな設計情報が失われない責務境界とする。

Application LogはCanonical情報より低い保存優先度とし、保持量に上限を設ける。具体的な保持期間は未確定である。Application Log単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合は§4.7のStorage Fail Closedを適用する。

Application Logは、§4.1のTEST / PAPER / LIVE Environment Bindingおよび§4.6のDevelopment / Runtime物理分離に従い、環境間で混在させない。「分離すること」は確定要件であり、具体的なpartition、path、directory等の分離方法は未確定とする。

Application Logについて、次は未確定事項として保持する。

- 生成主体、Writer責務、書込経路。
- retentionの具体的期間、およびcleanup / deletionの実行方法。
- crash直前のLog durability保証範囲。
- Runtime / Job / Adapter / Errorごとの最低限の識別情報。
- TEST / PAPER / LIVE間のApplication Log分離方法。
- Development環境とRuntime環境のApplication Log分離方法。
- Secret、Credential、Token、API key、Authorization header、未redactのdebug dump以外に禁止またはmaskingする情報の範囲。
- filename、file format、schema、logging library。

------------------------------------------------------------------------

# 29. Decision Log形式

Decision Logは判断内容だけでなく、Data / Prompt / Tool
provenanceを保持する。

例：

``` markdown
# Decision 2026-09-06-001

## Environment
System Version:
Model:
Prompt / Rule Version:
Portfolio Snapshot ID:
Portfolio Version:

## Timing
Decision Created At:
Data Cutoff At:
Queue Entered At:
Human Notified At:
Human Decided At:

## Trigger
Weekly Candidate Watch

## Data Provenance
- source:
- retrieved_at:
- source_published_at:
- query:
- tool / retrieval method:

## Evidence

...

## Bull

...

## Bear

...

## Contradictions

...

## Investment Thesis

...

## Invalidators

...

## Recommendation
BUY

## Suggested Allocation
2%

## Declared Reason Weights
| Reason | Weight |
|---|---:|
| Earnings inflection | 35% |
| Valuation | 25% |
| Competitive advantage | 20% |
| Portfolio diversification | 12% |
| Technical / timing | 8% |

## Confidence
Declared Confidence:
Calibration Status:

## Counterarguments

...

## Human Decision
PENDING

## Execution
Execution ID:
Executed At:
Broker Result:
```

可能な場合、Prompt / Rule versionにはhashまたは一意なVersion
IDを持たせる。

監査Recordは§13のCommitへ含め、MarkdownはそのProjectionとする。追加必須項目：run_id、state_id
/
commit_id、design_version、schema_version、code_hash、policy_hash、model_snapshotまたはNOT_OBSERVABLE、Evidence原文参照とcontent_hash、revision
/ vintage、approval_id / trade_hash、receipt_id、executed_at /
received_at /
committed_at、取得失敗・欠損。URLだけでは後日変わるEvidenceを固定できない。外部監査に必要な利用可能範囲の原文を保存する。

------------------------------------------------------------------------

# 30. 別AIレビュー

Markdownログを、元の設計会話コンテキストを渡さずに別AIへ渡す。

レビュー項目：

1.  論理飛躍
2.  証拠不足
3.  見落とした反証
4.  数値的不整合
5.  Portfolioとの不整合
6.  結論とEvidenceの不整合
7.  Reason Weightの不整合
8.  追加すべき探索枝
9.  不要な探索枝
10. 未検証の前提

------------------------------------------------------------------------

# 31. Counterfactual記録

買った銘柄だけでなく、REJECT / WATCHした銘柄も追跡する。

例：

``` text
A BUY     → +30%
B REJECT  → +80%
C WATCH   → -20%
D REJECT  → -40%
```

目的：

-   選定能力
-   見逃し
-   False negative
-   Opportunity Cost

を評価する。

REJECT /
WATCHだけでなく、共通フィルタ除外・枝別欠損・未評価から事前規則で抽出したサンプルも追跡する。評価対象・基準日・観測期間を固定し、結果を見て対象を選び直さない。

------------------------------------------------------------------------

# 31A. Declared Reason Weightの記録と将来較正

Declared Reason Weightはまず**記録対象**とする。

個々の定性的理由へ実現リターンを因果配分できるとは仮定しない。

保存：

``` text
Decision
Factor Category
Declared Weight
Subsequent Return
Subsequent Risk Event
Outcome
Evaluation Horizon
```

初期運用：

``` text
N < 30
→ descriptive only
→ 正式な較正結果として扱わない

N >= 30
→ exploratory group analysis allowed
→ 統計的保証を意味しない

Calibration method
→ 十分なデータ蓄積後にBreakで決定
```

30件は統計的保証値ではなく、探索分析開始の暫定閾値。

初期分析では例えば、

-   Fundamentalを高WeightにしたDecision群
-   Valuationを高WeightにしたDecision群
-   Technicalを高WeightにしたDecision群

などの結果比較までとする。

将来的に回帰等を使う場合も、手法・必要N・交絡・多重比較等を別途設計する。

------------------------------------------------------------------------

# 32. Break

Breakは単なるPrompt改善ではない。

既存システムの前提そのものを疑う。

対象：

-   Agent構成
-   Scanner
-   Skill
-   Watch周期
-   Threshold
-   Allocation方式
-   Workflow
-   評価関数
-   人間通知方式
-   Cost
-   Objective

Portfolioの事実状態・過去取引履歴はBreakしない。

------------------------------------------------------------------------

# 33. Break階層

## B1 Parameter Break

対象： - threshold - period - score - frequency

## B2 Component Break

対象： - Agent - Skill - Scanner - Watch module

## B3 Architecture Break

対象： - Workflow - Agent graph - System structure

## B4 Objective Break

対象： - 最適化目的そのもの - 評価関数 - Risk/Return/Income/Human
Loadのバランス

------------------------------------------------------------------------

# 33A. Objective Break保護

B4 Objective Breakは通常Breakより強く保護する。

Objective / 評価関数を変更する場合：

``` text
B4 Proposal
  ↓
Decision Queue
  ↓
Human Review
  ↓
Freeze old objective
  ↓
Add new objective
  ↓
Measure old and new objectives in parallel
  ↓
Comparison period
  ↓
Decision Queue
  ↓
Human final approval
```

旧Objective / 旧評価指標を削除しない。

「成績が悪いので、成績が良く見える評価軸へ変更する」自己正当化を検出可能にする。

------------------------------------------------------------------------

# 34. Break変更の承認・実行契約

Break
Proposalにはchange_id、対象ファイルと版、完全なdiff、変更後hash、理由、期待効果、影響するStrategy、試験計画、rollback手順を含める。B1〜B4すべてHuman
Approvalを必要とする。

具体的なdiffと適用対象版に承認を結び付ける。承認後にdiffが変わる、または基準版が変わる場合は再提案する。LLMが自ら承認Recordを生成して適用可としてはならない。

適用前に候補版で検証し、成功証跡を付けて有効版ポインタを切り替える。実行中Runは開始時に固定したSystem
/ Policy / Code版を使う。新旧が混在した更新を禁止する。

Policy変更時は未発注Proposalを再評価する。発注済みOrder、既受領Fact、既存予約を遡って消さない。Schema移行が必要なら書込停止と移行検証を行う。

rollbackはCode / Policy /
将来の処理を対象とし、実約定・Cash・監査履歴を昔のsnapshotで上書きしない。誤適用Factは訂正Eventで修復する。B4では§33Aの新旧評価軸を保持する。

------------------------------------------------------------------------

# 35. System Version

システム変更は必ずVersion管理する。

例：

``` text
system v0.1.0
  ↓
Break #013 → Decision Queue → Human Approval
  ↓
system v0.1.1
```

全Decisionに以下を保存する。

``` text
decision_id
system_version
model
timestamp
input_snapshot
output
human_decision
```

同じRun内で使用版を固定する。版変更は§34の承認済み切替を通し、Proposal・注文・事実それぞれへの影響を区別する。

------------------------------------------------------------------------

# 36. システム評価

投資成績とシステム健全性を分離する。

## 36.1 投資成績

例：

-   Return
-   Max Drawdown
-   Volatility
-   Sharpe
-   Hit Rate
-   Turnover
-   Benchmark差
-   Income Yield

## 36.2 Agent / Branch評価

例：

-   Selection precision
-   Bull accuracy
-   Bear accuracy
-   Risk alert precision
-   Thesis invalidation accuracy
-   False positive
-   False negative
-   Missed opportunity

## 36.3 System Health

例：

``` text
Data acquisition       99.8%
Watch completion       99.1%
False alerts           3
Missed events          0
Human decisions        4
Expired decisions      1
Astra cost             ¥xxx
Human attention        21 min
Break proposals        2
Accepted               1
```

指標定義を評価前に固定する：資産評価時刻・価格種別、配当税費用の扱い、外部入出金調整（TWR等）、損益の実現／未実現、ベンチマークと配当込み／なし、欠測処理。比較条件を一致させる。見逃し率は確認可能な正解集合と分母を明示し、未知の未検出Eventを測定済みとしない。

------------------------------------------------------------------------

# 37. AIコストとHuman Attention Cost

各Agent / Branchについて以下を計測する。

-   Accuracy
-   Contribution
-   False positive
-   False negative
-   Execution cost
-   Human attention cost

AIコストが安くても人間通知を大量発生させるAgentは高コストとみなす。

AI費用・人間作業時間はOBSERVED / ESTIMATED /
UNAVAILABLEを分け、未取得値を0としない。

------------------------------------------------------------------------

# 37A. Data Source Policy

**Execution SystemはLocal-firstだが、Data
SourceはLocal-onlyを要求しない。**

以下は外部データソースを利用してよい。

``` text
Market / Historical Data
├─ price history
├─ fundamentals
├─ disclosures
├─ publication timestamps
├─ delisted companies
├─ historical index constituents
└─ corporate actions
```

外部データをLocal Agentが参照することは通常Runtimeの一部とする。

Quant Backtestに必要なpoint-in-time historical
dataが入手できるかは未確定であり、 Capability
Verificationで以下を確認する。

-   入手可能性
-   時点整合性
-   上場廃止銘柄の包含
-   historical universe
-   publication timestamp
-   corporate actions
-   ライセンス / 利用条件
-   Local Agent / Data Adapterからの利用可能性

十分なpoint-in-time dataを確保できない場合、Quant
Backtestの評価範囲を縮小し、その限界を明示する。

初期Provider方針：

```text
Structured Market / Financial Data : J-Quants Adapterを第一候補
Statutory Disclosure               : EDINET API Adapter
TDnet paid API                     : EXCLUDED
News / Web                         : 別Adapterとして後段導入
```

**TDnet有料APIは本システムの費用要件に適合しないため明確に除外する。** 将来の通常候補として保持せず、再導入にはBreak Proposalと人間承認を要求する。TDnet上の公開情報が必要な場合は、合法・許諾された別経路または他Providerで取得可能かを個別に確認する。

J-Quants、EDINET、Model API等の外部ServiceはProvider Adapterへ閉じ込め、Business LogicがProvider固有Schema / SDK / endpointへ直接依存しないようにする。

### External Service Gateway / Provider Abstraction

外部APIへの直接アクセスをBusiness Logicから禁止し、共通の`ExternalServiceGateway`境界を通す。

```text
Application / Agent
        ↓
Domain Service Interface
        ↓
ExternalServiceGateway
        ├─ MarketDataProvider      → JQuantsProvider
        ├─ DisclosureProvider      → EDINETProvider
        ├─ ModelProvider           → OpenAIProvider
        └─ NewsProvider            → Future Provider
```

Gateway共通責務：
- service enabled / configured確認
- Human approval / paid-service policy確認
- Secret参照
- rate limit / retry / circuit breaker
- cost / usage telemetry
- Budget Gate / reservation（有料・従量課金Service）
- request_id / provenance / audit
- Provider failureの正規化

Provider固有責務：
- endpoint / request / pagination
- Provider固有response validation
- Raw保存
- Canonical schemaへのNormalize
- 所定形式(JSON / JSONL等)でNormalized Dataを保存
- `FetchResult` / provenance返却

Market / Disclosure Providerの外部契約は、**取得→検証→Raw保存→Normalize→所定形式で保存**までを一つのAdapter責務としてカプセル化する。上位AgentはJ-QuantsやEDINET固有Responseを直接読まない。

Normalized schemaはProvider非依存とし、`source.provider`、`retrieved_at`、`raw_ref`等でprovenanceを保持する。Provider差替え時にSelection / Analysis Logicを変更しないことを目標とする。

### Paid External Service Governance

**新規有料Service、無料→有料Plan変更、有料Add-on、従量課金上限増額、有料Fallbackをユーザーの明示承認なしに有効化してはならない。**

有料Serviceを有効化する前に少なくとも次を提示・記録する。

```text
service_name
provider
purpose
pricing_model
initial_cost
recurring_cost
usage_based_cost
expected_monthly_cost
configured_upper_bound
cancellation / downgrade procedure
cheaper / free alternatives
introduced operational dependency
human_approval_ref
```

異常系は下表の処理に従う。システムは障害・Rate Limit・Budget不足を理由に勝手に有料PlanへUpgradeしたり、有料ProviderへFallbackしたりしない。必要なら`PAID_SERVICE_REQUIRED` / Budget Review / Break Proposalを生成し、人間判断を待つ。

異常時処理：

| 異常 | 判定・Error | 処理 |
|---|---|---|
| `paid=true`かつ有効化対象で`human_approval_ref`欠落 | Configuration Validation Error | 有料Serviceを開始しない |
| Pricing不明または上限見積不能 | `COST_ESTIMATE_UNAVAILABLE` | 対象Model Callを開始しない |
| いずれかのBudget階層を超過 | `BUDGET_EXCEEDED` | 対象Callを開始せず、新規探索・候補分析・通常Breakを停止する |

この原則は投資Data APIだけでなくOpenAI等のLLM APIにも適用する。Model APIは`ModelProvider` Wrapperを通し、Token / cost / pricing manifest / Budget reservation / Durable Stageを共通Governance下に置く。

### J-Quants Operational Gate

J-Quants FreeはAdapter構造試験・Schema確認・Historical test等の開発用途には利用可能だが、遅延データのためPaper Trading / Live相当運用のProvider要件を満たさない。

J-Quants Capability Verificationを2段階に分離する。

**Free段階で確定するもの:** authentication、endpoint / pagination、response schema、Raw保存、Normalize、provenance、Adapter構造、error classification、retry。

**Light以上で確定するもの:** current data coverage、actual update timing、plan rate limit下のUniverse-scale bulk acquisition、Provider update schedule wait、Strategy required latencyとの適合。

全銘柄を銘柄単位で反復取得する設計を避け、利用可能な日付指定・bulk取得を優先し、Rawへ保存した後にLocal Universe Filterを行う。

**Paper Trading Gate:** Free Adapter CV PASS → HumanによるLight以上の契約承認 → Light Capability CV PASS → Paper Trading開始。Lightを契約しただけではGateを満たさない。

TDnet由来情報のうちJ-Quantsで代替可能な範囲をCVで確定する。§27のTDnet由来Eventは取得経路未確定の暫定Eventとし、有料TDnet APIを前提にしない。

### Provider Selection ADR

Provider選定理由・比較・却下理由はDesign本体へ埋め込まず、`docs/adr/`のArchitecture Decision Recordで管理する。Designは採用Providerと契約境界だけを参照する。

現行のADRは`docs/adr/argus_architecture_decision_records_v0.1.md`に集約している。将来、個別ADRへ分割する場合も、既存ADRを後から書き換えて判断履歴を消さず、Supersede記録を残す。

ADRにはContext / Decision / Alternatives / Evaluation Criteria / Cost / Constraints / Consequences / Revisit Conditionsを残す。Provider変更時は既存ADRを書き換えて履歴を消さず、新ADRまたはSupersede記録を作成する。

契約・導入手順はDesign Documentとは別に運用文書化する。

将来の運用文書候補として、OpenAI API/Billing/Secret/Usage確認手順と、J-Quants/EDINET等の契約・登録・認証・変更手順を分離する構想がある。現repositoryに当該文書は未作成であり、存在する文書への参照として扱わない。

------------------------------------------------------------------------

# 37B. Model API Budget Gate

Model API費用は観測指標だけでなく**実行前Hard Gate**として扱う。

Budget Policyは少なくとも以下を持つ。

```text
status = UNCONFIGURED / ACTIVE
currency
pricing_manifest_version
monthly_limit
monthly_used
monthly_reserved
daily_limit
daily_used
daily_reserved
per_run_limit
per_job_type_limit
p0_emergency_reserve
p0_emergency_reserve_enabled
warning_thresholds
```

本番相当のModel API JobはBudget Policyが`UNCONFIGURED`なら開始しない。fixture / mocked provider / explicit test budgetは別Modeとして扱う。

各Model call前に、input size、max output、model、tool usage等から`estimated_max_cost`を計算しBudgetをreserveする。Call終了後にProviderが返すusageを記録し、reserveとの差を精算する。Pricingが不明、または上限見積り不能なら無制限として扱わず`COST_ESTIMATE_UNAVAILABLE`で止める。

Budget階層：

1. Per-call / Per-job ceiling
2. Per-run ceiling
3. Daily ceiling
4. Monthly ceiling

どれかを超えるCallは開始しない。

上限到達時：

```text
BUDGET_EXCEEDED
  ↓
new discovery / candidate analysis / normal Break停止
  ↓
既取得Dataによる決定論的Risk checkは継続
  ↓
P0監視でModel APIが必須ならpolicyで予約済みemergency budget内だけ許可
  ↓
Decision Queue / System Incidentへ通知候補
```

`p0_emergency_reserve`は未設定のまま本番開始しない。`enabled=true`ならreserve額必須、`enabled=false`ならP0でModel APIを使えなくなる可能性を初期設定時に明示確認する。明示的な0は許容するが、通常Budget超過を理由としてシステムが勝手に追加課金しない。

Catch-up処理は通常Runより先にCost Estimateを行い、停止期間分のJobを一括展開してBudgetを暴発させない。Candidate / Eventのdedup、freshness、relevanceをModel API callより前に決定論的に実行する。

System Healthにはmodel/provider/job_typeごとのtoken、observed cost、estimated cost、cache hit、retry avoided by stage reuseを記録する。

BudgetはHard Gateであると同時に**Runtime Health Sensor**として常時確認可能にする。

CLI：

```text
budget status
budget review
budget set daily <amount>
budget set monthly <amount>
budget set emergency <amount>
```

`budget status`は少なくともToday / Month / Emergency Reserveについてused / reserved / remaining / percentageを表示し、token usageをmodel / provider / job_type単位で集計できるようにする。

警告は初期値候補として段階制にする。数値はConfigで変更可能。

```text
< 70%   NORMAL
>=70%   NOTICE
>=85%   WARNING
>=95%   CRITICAL
100%    BUDGET_EXCEEDED
```

WARNING以上では単なる残量通知だけでなく`Budget Review Proposal`を作成可能にする。

```text
Budget Warning
  ↓
Usage / Top consumers / projected exhaustionを集計
  ↓
Budget Review
  ├─ Budget追加
  ├─ Watch / Analysis頻度低減
  ├─ cheaper model routing
  ├─ new discovery一時停止
  ├─ Break Proposal
  └─ 現状維持
  ↓
Human Decision
```

Budget追加は必ずHuman Commandで行い、Agent自身がlimitを増額しない。継続的にCost / Valueが悪いAgentやJobはB2 Component Break等の入力にする。

------------------------------------------------------------------------

# 38. Historical Validation

Historical Validationは2種類に分離する。

LLM自身の学習データ由来の未来知識を完全遮断できないことを明示する。

## 38.1 Quant Backtest

LLMの事前知識を判断に使わない、決定論的・数値的ロジックの検証。

目的：

-   Return
-   Drawdown
-   Allocation rule
-   Mechanical filter
-   Risk rule
-   Threshold

等の検証。

未来データを完全遮断する。

## 38.2 Model Historical Replay

LLMを使って過去時点を再現する。Astraを必須とせず、使用ModelをRun
Manifestへ記録する。

制約：

-   外部データはSimulation Date以前のみ
-   Replay中の通常Web検索は禁止
-   現在株価を取得しない
-   未来を明示的に参照しない

ただし、モデル内部の学習済み知識によるfuture
leakageは完全には排除できない。

したがって、Model Historical Replayは「完全なOut-of-sample
Backtest」とは呼ばない。

目的：

-   Workflow評価
-   分析枝評価
-   Decision format評価
-   Contradiction検出評価
-   過去情報だけを与えた場合のreasoning参考評価

検証開始前にデータ版、Universe、Strategy / Policy /
Code、学習・調整期間、評価期間、執行モデルを凍結する。LLM内部にある後年知識はPublication
Time Gateで除去できないため、Historical
Replayを純粋な未知未来の性能証明としない。

------------------------------------------------------------------------

# 39. Time Gate

Historical Data LayerはSimulation
Date時点で公表済みのデータだけを供給する。

``` text
Historical Data
  ↓
Publication Time Gate
published_at <= simulation_time
  ↓
Simulation
```

以下も考慮する。

-   生存者バイアス
-   上場廃止銘柄
-   当時の指数構成
-   後日修正された財務データ
-   発表時刻
-   市場取引時間

published_atだけでなくrevision /
vintageを保持する。後日修正した財務値に古い発表時刻を付けて供給しない。履歴版がないデータはPIT不適合と記録する。株式分割等の調整価格と実注文価格を混同しない。

------------------------------------------------------------------------

# 40. 真のOut-of-sample

LLMを含むシステムについて最も信頼できるOOSは、未来がまだ存在しない運用期間で得る。

``` text
Quant Backtest
      +
Model Historical Replay
      ↓
Paper Trading
      ↓
Continued Paper / Small Real Capital
```

Historical
ReplayでSystem改善を繰り返した結果を、同一期間だけで「OOS改善」と評価しない。

------------------------------------------------------------------------

# 41. 1か月Paper Trading

Historical Validation後、1か月間、仮想予算を持ってリアルタイム運用する。

例：

``` text
Initial Cash: ¥1,000,000
```

実資金は投入しない。

以下を記録する。

-   BUY / ADD / HOLD / REDUCE / SELL
-   Cash
-   Positions
-   Realized P/L
-   Unrealized P/L
-   Max Drawdown
-   Dividends
-   Human decisions
-   Notification count
-   Human attention time
-   Expired decisions
-   Break proposals
-   System changes
-   AI cost

Paper開始前に執行規則を凍結する。初回は現物・指値注文を基本とし、承認後に観測された取引可能時間内のデータだけを使う。単なる日足高安への指値接触だけで全量約定とせず、粒度・出来高・部分約定の判定規則を事前設定する。証拠不足は未約定／判定不能とする。仮想手数料・税・slippage・受渡を明示し、Paper
ExecutionにはSIMULATEDを付ける。実約定と同じ状態更新経路を通す。

------------------------------------------------------------------------

# 42. Paper Tradingの目的

最初の1か月Paper
Tradingは、**投資性能の証明ではなく運用性能の検証**を主目的とする。

Backtestでは再現しにくい以下を確認する。

-   データ取得遅延
-   IR取得失敗
-   データ欠損
-   Model API調査失敗
-   Agent間矛盾
-   処理時間
-   定期処理失敗
-   市場急変
-   人間不在
-   Human Capacity変化
-   通知過多
-   Decision TTL失効

1か月では十分に評価できないもの：

-   LONG / CORE戦略の最終性能
-   配当戦略の長期成果
-   稀頻度イベントへの統計的性能
-   Sharpe / Max Drawdownの安定推定
-   複数Break世代の長期改善性能

これらは3か月 / 6か月 / 12か月へ継続観測する。

------------------------------------------------------------------------

# 42A. Local版のリアルタイム性境界

初期Local版はリアルタイム売買システムを目的としない。

対象外：

``` text
HFT
Scalping
Intraday automatic stop execution
Millisecond / second level monitoring
Automatic broker-side emergency execution
```

Local PC停止・Sleep・Offline中は監視を保証しない。

急落等は、次にLocal Processが稼働し外部Data
Sourceへ接続できた観測タイミングで取得・Catch-upする。

``` text
Event発生
  ↓
PC OFF / Offlineなら未観測
  ↓
Local復帰
  ↓
Data Fetch
  ↓
Gap / Event検出
  ↓
Relevance Check
  ↓
Emergency Analysis if still relevant
```

要求レイテンシはStrategyごとに別途設定する。

``` text
Required Latency: Strategy Policy
Observed Local Availability / Polling Latency: 実測
Acceptable: 比較して判定
```

Localの可用性ではSHORT
Strategy要件を満たせない場合、SHORTを無理に有効化せず、Server移行候補とする。

レイテンシは次のように分解して測る。

```text
Event発生
→ 公開待ち
→ Provider update schedule wait
→ PC availability wait
→ polling wait
→ acquisition
→ analysis
→ Decision Queue wait
→ notification-window wait
→ delivery
→ human response
→ market opportunity
```

Provider側の更新時刻・反映遅延はLocal Runtimeでは短縮できない独立レイテンシとして記録する。日足Providerを使うPrice StopはIntraday Stopではなく、Provider更新後に検知するEmergency Re-analysis Triggerである。

------------------------------------------------------------------------

# 43. 初期運用の自動化境界

初期版ではAIが証券会社へBUY / SELL操作を行わない。

人間：

``` text
判断
  ↓
証券会社操作
  ↓
約定結果Paste
```

Local Agent：

``` text
提案
  ↓
ログ
  ↓
Paste受領
  ↓
Portfolio更新
  ↓
Watch開始
```

将来的に証券会社API連携を検討可能。

------------------------------------------------------------------------

# 44. Local → Server 移行方針

## Stage 1: Local

初期実装。

目的：

-   Agent / Tool開発
-   投資ロジック検証
-   Workflow検証
-   Human Load検証
-   Break検証
-   Paper Trading
-   Offline / Sleep / Retry / Catch-up検証

構成候補：

-   Python
-   Local JSON Canonical State
-   将来SQLite候補
-   Persistent Loop
-   Retryable Transactional Jobs
-   External Data Adapters
-   OpenAI API等のModel Adapter
-   Markdown generation

## Stage 2: Server

Localの非常時稼働が実際のStrategy /
Watch要件のボトルネックになった場合に移行する。

候補：

-   安価なVPS / Cloud Server
-   Always-on Runner
-   Market collectors
-   DB
-   API
-   Notification
-   Agent jobs

Localで定義したJob / Transaction / Adapter / Validator /
Reducerを、実行ホスト変更だけで再利用できる構造を目標とする。

``` text
Local Runner
    ↓
job.transaction()

Server Runner / cron / service
    ↓
same job.transaction()
```

Server化しても外部Data Source / Model API障害は残るため、Retry /
Idempotency / Transaction Boundaryを削除しない。

自宅旧PCの常時Server化は選択肢として残すが、騒音・電力・OS更新・生活環境への影響を含めて別途判断する。

安価VPSも選択肢として保持し、常時監視が必要になるまで固定費を発生させない。

------------------------------------------------------------------------

# 45. Server移行判断もBreak対象

LocalからServerへ移すかどうかは固定計画にしない。

例：

``` text
Local運用
  ↓
Availability / missed event / latencyを実測
  ↓
Break
  ↓
「常時稼働が必要」
  ↓
Human Approval
  ↓
Server化
```

移行判断では、月額費用だけでなく以下を比較する。

-   PC OFF時間
-   missed / delayed event
-   Strategy要求Latency
-   Human inconvenience
-   Server費用
-   保守負担
-   Security / API key管理
-   Backup
-   障害復旧
-   Localコード再利用率

------------------------------------------------------------------------

# 46. 非機能要件

## 46.1 再現性

過去Decisionの入力・根拠・計算・版を復元して追跡できること。LLM出力の完全一致は要求しない。

## 46.2 監査可能性

第三者AIへ.mdログを渡して独立レビューできること。

## 46.3 Human Load制御

Human Capacityが低い時も破綻しないこと。

## 46.4 Safe Degradation

STATUS = BUSY（human_capacity = SMALL）時には新規探索・通常Breakを止めても、保有銘柄の重大Risk監視は維持すること。

## 46.5 Version Traceability

どのSystem VersionがどのDecisionを出したか追跡可能であること。

## 46.6 State Integrity

Portfolio、Cash、取引履歴など事実状態をBreakで上書きしないこと。

再現性は、保存Evidenceによる判断根拠の追跡、同じ入力への決定論的計算、LLM文章の再生成を区別する。LLMの完全同文・同判断再現は保証しない。BUSYで維持する重大Risk監視の通知は§22に従う。

------------------------------------------------------------------------

# 46A. 設計レビュー工程

通常設計は本チャットで継続し、Astra全面レビューを必須工程としない。過去のReview実施履歴は§52の非Normativeな変更記録で管理する。

基本工程：

``` text
Design change
  ↓
Consistency Review
  ↓
Implementation / Test
  ↓
Observed Failure
  ↓
Revision
```

Astraは以下のような、探索深度が必要な難所へピンポイントで利用する。

-   複雑なState machineの反例探索
-   Validatorの抜け道探索
-   Break / Objective変更の自己正当化リスク
-   通常モデルで決着しないArchitecture問題

Astraを使用した場合も、自己レビューを実装可能性の保証とは扱わない。

すべてのDesign Review自体を監査ログとして保存する。

------------------------------------------------------------------------

# 46B. Local Capability / Reliability Verification：実機試験

設計確定後に、小さな検証用コード・試験入力を先に作り、機能ごとに実測する。全体実装の完了を試験開始条件にしない。

  ---------------------------------------------------------------------------------------------------
  ID                                  確認内容
  ----------------------------------- ---------------------------------------------------------------
  CV-00                               Local実行ホスト・project directory読書き・権限・API設定

  CV-01                               Loop /
                                      wait、Due判定、未実行検知、Process停止／Sleep／Offline復帰

  CV-02〜05                           Web、市場、J-Quants、EDINET、価格、決算資料の取得と鮮度・欠損。TDnet有料APIは対象外

  CV-06                               正本の永続保存と別Runからの最新版取得

  CV-07                               単一Envelopeの原子的・耐久的更新

  CV-08〜09                           Markdown生成、Queue・Incident永続化と再生成

  CV-10〜11                           Local通知または選定した通知Adapter、時間・User Status制御

  CV-12〜13                           別プロセス同時実行、排他・version競合・再計算

  CV-14                               Polling、last_success / cursor、Gap検出、取り逃し・Catch-up

  CV-15                               Source / query / 原文hash / Prompt / Code / Configの追跡

  CV-16A                              Validator計算、BOOTSTRAP / REPAIR / SELL例外

  CV-16B                              Validator / Config / State / PASS表示の迂回・改変防止

  CV-17〜19                           PIT歴史データ、上場廃止を含む当時Universe、発表時刻・revision

  CV-20                               書込中断、通信断、Sleep、Process kill、ログ未生成、未解決発注、再起動復元

  CV-21                               Retryable / Non-Retryable分類、MAX_RETRY後の次Cycle再試行、重複適用防止

  CV-22                               Human CLI Approval / Reject / Execution Paste、request_id冪等化、trade_hash照合、Slot同時Commit

  CV-23                               Budget Gate：per-job / per-run / daily / monthly、Catch-up暴発抑止、quota不足

  CV-24                               Secret非出力、同期Allowlist / Denylist、redaction、debug dump検査

  CV-25                               Runner二重起動拒否、stale lock回収、Process kill / heartbeat

  CV-26                               Durable Stage再利用、API成功後Commit失敗時の再課金回避

  CV-27                               Archive rotation / compaction / rebuild、Current Envelope肥大化境界

  CV-28                               Backup / Restore → RECONCILIATION_REQUIRED →照合完了までBUY/ADD停止

  CV-29                               Wall clock / monotonic分離、Sleep、時計変更、timezone変更

  CV-30                               After-close承認→翌営業日revalidation→同条件発注 / 条件変更時再承認

  CV-31                               Windows対象環境でatomic replace / lock / process-kill recoveryの保証範囲記録

  CV-32                               User Status：FREE/NORMAL/BUSY写像、BUSY Lease、今日/今週境界、期限切れNORMAL遷移

  CV-33                               Status Writer競合：人間の再設定とLease期限切れ同時発生、status_version、stale auto-transition rejection

  CV-34                               Budget枯渇中のpre-submit：Model依存再検証不能→HOLD_FOR_REVALIDATION→Incident→hold_ttl expiry / release

  CV-35                               Alert Queue / Windows Popup / ack / restart復元、Notification Window遵守、Status Maintenance相乗り

  CV-36                               CLI help / status / budget / system command、BUSY絶対終了時刻echo、Tray→同一Command Dispatcher

  CV-37                               `L:\emori\InvestmentAgentData`接続・切断・再接続、DATA_STORAGE_UNAVAILABLE、Catch-up、容量警告

  CV-38                               Dev / Runtime物理分離、Runtime停止→手動Deploy→Schema check→restart、state/data非上書き

  CV-39                               Raw / normalized provenance、JSONL追記、EDINET原本保持、Archive再生成
  CV-40                               Runner Lifecycle：INIT→RUNNING→END、異常終了後INIT→RESUMING→RUNNING、Graceful Exit→flush→lock release

  CV-41                               CLI / Tray / Runner共有Service：非RUNNING時Status/Help/System Status、Execution Paste拒否、同一Validator/Writer contract、Approval分岐なし

  CV-42                               Alert Severity/Priority：System Critical closed class、Override UNCONFIGURED/ENABLED/DISABLED、BUSY override、dedup / renotify suppression

  CV-43                               Config Snapshot：Job境界reload、同一Job config_hash固定、既存reservationよりBudget limit低下時の扱い

  CV-44                               Storage / Environment Identity：別Diskが同じL:を取得、state_id / data_root_id / environment mismatch→write拒否、正しいBinding再接続→復帰

  CV-45                               Paid Service Governance：approval欠如時Validation Error、自動Upgrade / paid fallback禁止、Budget増額再承認、Correction経由のCommitment拡大も同じ承認要件

  CV-46                               ExternalServiceGateway Contract：共通retry/cost/audit/error normalizationとProvider固有Adapter境界

  CV-47                               Backup / Storage Pressure：Local recent backup、external backup stale検知、縮退順序、Canonical/Audit保護、Storage CriticalでもPosition Watch Minimum Dataを優先維持

  CV-48                               J-Quants Free Adapter：auth、schema、raw/normalize/provenance、error/retry、bulk endpoint構造

  CV-49                               J-Quants Light Capability：current coverage、update timing、Universe bulk acquisition、rate-limit margin、Provider latency

  CV-50                               External Service Registry：expiry/auth failure/staleness/freshness degradation検知、HTTP成功でもstale dataをHealthy扱いしない
  ---------------------------------------------------------------------------------------------------

### Test Architecture Boundary

詳細なTest Fixture / Stub / Scenario / Dataset生成手順は本設計書へ埋め込まず、`docs/test/argus_test_strategy_v0.1.3.md`で管理する。本書ではTest Environment間の境界と必須GateだけをArchitecture Contractとして定義する。

```text
Design / ADR Complete
→ External Account / API Setup
→ Coding + Unit / Component / Contract Test
→ Historical Test
→ Real Provider Capability Verification
→ J-Quants Light Capability Verification
→ Realtime Paper Test
→ Live Readiness Review
```

投資関連ProviderはLocal Stub / Historical Providerを実装し、Business Logicから見てProduction Providerと同一Interfaceを満たす。LLMはBehavior / Integration Testでは実Providerを利用可能とするが、単純Pipeline / regressionではRecorded ModelResultを利用できる。

Test DataはProduction Data Rootから物理・論理分離し、Test/Paper/Liveそれぞれ異なる`state_id` / `environment` / storage markerを持つ。環境不一致のState/Data Rootを検出した場合は起動・writeを拒否する。

Historical Test Datasetは事前生成Batchで作成可能とし、`dataset_id`、source、as-of範囲、generator_version、content_hashをManifest化する。Historical Providerは`as_of_time`より未来のDataを返さない。具体的なDataset Layout、Fixture Case、Stub Error injection、Acceptance CriteriaはTest Strategy文書で定義する。

各試験は実行前にRequirement、Input、Expected、Acceptance
Criteria、実行環境、試行数を保存する。実行後はObserved、成功数/試行数、遅延分布、Evidence、PASS
/ PARTIAL / FAILを記録する。未実施は `NOT_RUN`
とし、設計記述やモデル自己申告でPASSにしない。

取得能力の測定とStrategy適合判定を分ける。要求遅延等が未設定なら能力値だけ記録し、Strategy適合はUNASSESSEDとする。実測結果に合わせて合格基準を後付けしない。必要な要件変更は明示した変更承認を通す。

### 個別確認の順序

1.  **CV-00**：Local project
    directoryでダミーJSONを読む・一フィールド変更・実ファイルで確認。API
    key等のSecretをログへ出さない。
2.  **CV-06 / 08 /
    09**：保存、別Run再読込、版更新、旧コピー検出、Queue復元。
3.  **CV-48 + CV-02〜05のFree適用部分**：J-Quants Freeで認証、Schema、Raw/Normalize、provenance、error/retry、bulk endpoint構造を確認する。Current update timingやLight rate limitはここでPASSにしない。
4.  **CV-49 + CV-02〜05のOperational部分**：Human承認後のJ-Quants Light以上でcurrent coverage、update timing、Universe規模取得、rate-limit margin、Provider latencyを確認し、Paper Trading Gateを判定する。
5.  **CV-16A / 16B**：固定入力の数値検査と迂回試験を別々に実行。
6.  **CV-01 / 10 / 11 / 14 / 21 / 23 / 25 / 26 / 29 / 33 / 34 / 35 / 36 / 37 / 40 / 42 / 43**：売買しないfixtureでLoop、wait、通信断、Sleep復帰、burst retry、Circuit Breaker、Budget Gate、Stage再利用、次Cycle retry、Catch-up、通知を確認する。
7.  **CV-07 / 12 / 13 / 20 / 31 / 41 / 44 / 45 / 46**：同版からの競合、中断位置ごとの復旧、Windows上のatomicity / lock挙動。
8.  **CV-22 / 24 / 36 / 41**：CLI承認・Execution Paste・help / status / budget command・Secret redaction・同期対象境界。
9.  **CV-27 / 28 / 37 / 38 / 39 / 47 / 50**：Archive / compaction / external storage / deploy / restore / reconciliation。
10. **RV-01〜08 / 11**：Paste、部分約定、予約、初期構築、段階売却。
11. **RV-12 / 13**：通知時計の境界条件、独立枝と欠損処理。
12. **RV-16**：売却後復元までのMVS。
13. **CV-17〜19 / RV-14 / 15 / CV-30**：履歴検証、Paper約定規則、版変更評価。

最初は機密を含まないダミー値・仮想注文を使う。Local試験の成功は24時間監視を意味しない。常時監視はServer移行後に別途検証する。

### Regression Verification Setの実行位置

RVはCVのような一回限りの能力確認順序ではなく、**成立済みCapabilityを変更で壊していないことを確認するRegression Set**として扱う。

```text
CV = Capability / Gate Verification
RV = Regression Verification
```

- `RV-01〜35`はMVS成立後にRegression Setへ登録する。
- 通常変更では、変更影響範囲に対応するAffected RVと、State / Funds / Writer / Approval等のCore RVを実行する。
- Release、Paper Trading Gate、Runtime / Schema / Provider / Governanceの重要変更前にはFull RV Setを実行する。
- どのRVをCore / Affected / Fullに含めるか、実行自動化、Fixture、所要時間はTest Strategy文書で定義する。
- `NOT_RUN`のRVを暗黙PASSとして扱わない。
- RV失敗時は、失敗した要件を変更してPASS化せず§46B.1 Development Validation Integrityに従う。

今回追加した`RV-30〜35`もMVS成立後のRegression Setであり、Human Correction、System Override、長期Human不在、Environment Binding、Historical Time Gateに関係する変更ではAffected RVとして必須実行する。



------------------------------------------------------------------------

## 46B.1 Development Validation Integrity

Codex等の実装Agentが`code/`、`config.json`、`state/`、`validation/`へ書込可能でも、試験基準を実装結果に合わせて自動変更してPASSを作らない。

各CV / RVについて以下を試験実行前に固定する。

```text
test_id
requirement_id
fixture_hash
expected_result / invariant
acceptance_criteria
validator / oracle version
created_at
approved_by
```

Acceptance Criteria / expected resultの変更は、失敗したTest Runとは別Commitで行い、変更理由とdiffを残す。安全・資金・State integrityに関わる基準変更は§34のChange Proposal / Human Approval対象とする。

Test Runは固定済み`validation_baseline_hash`を記録する。Test実行中にbaselineが変わった場合、そのRunをPASS判定に使わない。

CV-16BはRuntime権限分離だけでなく、この開発時Validation Integrityも満たして初めて強い意味でPASSとする。

------------------------------------------------------------------------

# 46C. Minimum Vertical Slice・完了条件

初回はValue＋Changeの選定、Fundamental / Valuation / Bear /
Riskの独立分析で縦一本を通す。最小限のPortfolio制約計算は省略しない。

1.  Evidence取得 → 候補 → 独立分析 → 矛盾抽出。
2.  Allocation → 数量・条件を含むTrade → Validator → Queue。
3.  Human承認 → Slot・資源確保 → Virtual BUY。
4.  BUY Paste → Commit → 保有・Cash・lot・ログ・Position Watch。
5.  Event / Thesis再評価 → SELL Proposal → Validator → Queue →
    Human承認。
6.  Virtual SELL → 売却約定Paste → Cash / 簿価 / 損益 / 残数量更新。
7.  全売却ならHolding CLOSED、Position Watch終了、必要なCandidate
    Watchへの切替、Slot解放。
8.  別Run・再起動から正本、Cash、履歴、Queue、Watch、outboxを復元して照合。

**RV-16がMVS完了試験。SELL Proposalの生成だけでは完了としない。**
重複Paste・部分約定・Commit後ログ前停止を同じ系列の異常系として検証する。

------------------------------------------------------------------------

### MVS追加前提

RV-16を開始する前に以下を必須とする。

1. Local CLIでProposalを表示できる。
2. `ApprovalCommand`をrequest_id / proposal revision / trade_hash付きで投入できる。
3. APPROVEとexecution_slot / reservationが一つのAtomic Commitで成立する。
4. CLI Execution Pasteがinbox Fact経路へ入る。
5. Model Budget PolicyがACTIVE、またはModelを使わないfixture Modeである。
6. Runner single-instance guardが有効。
7. Secretがproject / logs / backupへ平文出力されない。
8. Stage ResultをDurable保存し、Commit失敗時に再利用できる。
9. Backup / Restore recovery fixtureがある。
10. Windows対象環境のatomicity / locking制約がManifestへ記録されている。

------------------------------------------------------------------------

# 46D. Deferred Scope

- Local Web UI / GUI
- Remote approval UI
- Always-on external Push notification service

設計から削除しないが、Minimum Vertical Slice成功まで実装を延期する。

``` text
Deferred:
- Growth selection branch
- Quality selection branch
- Event selection branch
- Contrarian selection branch
- Theme selection branch
- Bull analysis
- Macro analysis
- Technical analysis
- Full Portfolio Fit analysis
- B3 Architecture Break automation
- B4 Objective Break operational cycle
- Statistical Reason Weight calibration
- Automatic DRIP
- Real-time intraday monitoring
- Broker API execution
- SQLite / dedicated Local DB migration
- Dedicated Server / VPS
- Dashboard
```

延期は「不要」を意味しない。 Vertical Slice / Capability Verification /
Breakの結果に基づき順次有効化する。

------------------------------------------------------------------------

# 46E. Local Failure / Safe Degradation

Local Process停止、PC
Sleep、Offline、情報取得不能、State更新失敗等になった場合：

1.  Portfolio事実状態を推測で更新しない。
2.  未確認Executionを約定済みとして扱わない。
3.  stale dataによる新規BUY / ADD提案を抑止する。
4.  Risk / SELL案件で必要情報が不足する場合は `DATA_INSUFFICIENT`
    を明示する。
5.  Retryable Errorは短時間retry後、`RETRY_PENDING`
    として次Cycleへ残す。
6.  復帰後にlast_success / cursor /
    inboxから未処理期間を検出してCatch-upする。
7.  Catch-up案件はRelevance
    Checkを通し、古いProposalをそのまま一斉通知しない。
8.  未解決Orderと予約を障害復旧時に保持し、Slotを勝手に空けない。
9.  Budget Gate超過・quota不足時は`BUDGET_EXCEEDED / BUDGET_OR_QUOTA_BLOCKED`とし、通常Model Jobを停止する。
10. Adapter Circuit Breaker中は同じ障害先を短周期で叩き続けず、`ADAPTER_DEGRADED`を記録する。
11. Secret漏出疑いを検出した場合は対象Adapterを停止し、`SECURITY_INCIDENT`として人間確認まで再利用しない。
12. Restore後は`RECONCILIATION_REQUIRED`を解除するまで新規BUY / ADDを停止する。

Local停止中に人間が証券会社で行った操作は、復旧後にExecution
Pasteで事実状態へ反映する。

------------------------------------------------------------------------

# 47. 段階別の成功条件

## 47.1 個別機能・MVS Gate

1.  実行環境、正本Binding、実際の能力と制約が記録されている。
2.  Fact /
    Proposalの分離、重複排除、原子的Commitと復旧が検証されている。
3.  具体的Tradeへの承認と、一件のSlot・資源確保が成立する。
4.  Validatorの計算結果と強制力を別々に判定している。
5.  全Human
    ProposalがQueueへ入り、TTL・Incident・User Status・通知時間が機能する。
6.  RV-16でBUYから全売却・再起動復元まで成立する。

## 47.2 Local版POC Gate

1.  §47.1を満たす。
2.  探索・分析枝を独立に追加し、矛盾・未評価・除外理由を保持できる。
3.  一行提案、Declared Reason
    Weight、反対理由、出典付き監査ログを生成できる。
4.  Position / Candidate / Market
    Watchを分離し、人間不在・BUSY・停止復旧時の挙動が確認されている。
5.  BOOTSTRAP / REPAIR / SELL例外を設定に従って扱い、違反を隠さない。
6.  Break提案から具体的diffへの承認、検証、版切替、rollbackを追跡できる。
7.  Objective変更時も旧評価軸を保持する。B4実装延期中は運用済みとしない。
8.  Quant Backtest / Historical Replay / prospective
    Paperを区別し、PIT範囲と不足を明示する。
9.  1か月Paperで運用性能を評価し、長期投資性能は未検証と明示する。
10. 通知・人間負荷・費用・失敗率・PC停止時間からStrategy適合とServer移行候補を判定する。

必須整合性GateのFAILを、他項目の成功件数で相殺しない。CV-16B不足の環境は「監督下の試験可能」と「Hard
Gate強制済み」を区別する。実資金開始には必要なGate、運用Policy、適合Strategyを確認した上で、別途ユーザーの開始判断を要する。本設計の確定は売買開始指示ではない。

------------------------------------------------------------------------

# 48. Local版初期段階で意図的にやらないこと

-   AIによる証券会社への直接売買
-   完全自動投資
-   高頻度取引
-   超短期スキャルピング
-   常時稼働保証
-   専用Server / VPS必須化
-   分散Agent orchestration
-   外部Message Queue必須化
-   同期ストレージ上のCanonical DBを複数端末から直接更新
-   最初からの最適Portfolio比率固定
-   Backtestだけを根拠に実資金運用へ移行
-   BreakによるPortfolio事実履歴の変更

------------------------------------------------------------------------

# 49. 実装順序と版管理

本書v0.1.7をLocal-first初期実装設計の**Baseline最終版**として使用する。Statusは
`LOCAL_FIRST_DESIGN_BASELINE_FINAL`。設計確定と、実装完了・試験合格・実資金開始は別の状態とする。

順序：設計確定 → 個別能力Probeと必要な小規模実装 → 個別試験 → MVS実装 →
RV-16 → Branch Expansion → Historical Validation → 1か月Paper Trading。

最初に構築するもの：SYSTEM.md / Manifest、`config.json`、`user_status.json`、Schema、Canonical
Envelope、起動・復旧、固定Reducer / Validator / Writer、Projection /
監査ログ、Queue / Incident /
通知、Paste、Slot・予約、最小探索枝・分析枝、BUY〜SELL〜復元。

試験計画・期待値を先に保存し、実測結果はEvidenceを伴って別Recordに残す。要件を勝手に削除・一般化しない。実装困難な項目はRequirement、Observed
limitation、Impact、Workaround、Server化要否を提示する。


### v0.1.7の着手順

```text
0. Design / ADR baseline確定、Test Strategyは別文書化
1. External Account / API setup（OpenAI、J-Quants Free、EDINET）
2. Dev / Runtime / Test Data物理分離、Windows Manifest、Secret bootstrap、config.json schema
3. Shared Command / Service Layer + Status Writer + CLI `status` / `help`
4. Runner single-instance + Lifecycle + clock + wait + StatusLeaseJob
5. Writer lock / Atomic Commit / recovery + Config Snapshot + Human Correction
6. ExternalServiceGateway + Paid Service Governance + Provider Registry
7. Local Stub Provider / Test Dataset Generatorの最小実装
8. Budget Gate + Usage Meter + Budget Review + Adapter Circuit Breaker
9. Alert Queue + Severity/Priority/System Override policy + Windows Popup + ack / Incident
10. Durable Stage Result + retry resume
11. External Data Storage + identity marker + growth monitor + dual-location State Backup
12. J-Quants Free Adapter / EDINET Adapter Capability Verification
13. CV fixture / frozen Acceptance Criteria
14. Deterministic Risk Validator + Decision Queue
15. Single-ticker Agent vertical slice + Historical Test
16. Human承認でJ-Quants Light導入 → Light Capability Verification
17. Realtime Paper Test
18. Live Readiness Review
19. Multi-branch analysis / selection拡張
```

投資分析Agentを先に増やさず、Human Approval / Cost / State integrity / Retry economyを先に閉じる。

### 版番号

-   現行Design Baselineは本書v0.1.7とする。
-   v0.1.7以降のv0.1系列変更は、実装で発見した契約欠陥の修正を中心とする。機能範囲または処理契約の拡張は原則v0.2系列で扱う。
-   Code / Schema / Policy / Data / Designの版は別管理し、Run Manifestで対応付ける。
-   過去Versionの差分と改番Provenanceは§52へ集約し、現行仕様の根拠として参照しない。

------------------------------------------------------------------------

# 49A. 実行主体レビューの継続規則

設計を変更するときは、実行時の曖昧さ、指示衝突、State、出力Schema、Tool依存、並列競合、再起動、Failure
mode、試験可能性を再レビューする。

A＝設計上可能、B＝参照した仕様上の保証、C＝推測、D＝実機確認が必要、E＝現配置では困難を区別する。Bには出典と保証範囲を、Dには試験を付ける。モデルの自己申告を実機結果としない。

特に、実約定の非拒否、Slotと承認の原子的確保、段階回復、QueueとIncidentの独立、BUSY中Emergencyの通知待ち、Validatorの計算と非迂回性を確認する。reviewer_model_snapshotが観測不能ならNOT_OBSERVABLEと記録する。

------------------------------------------------------------------------

# 50. 外部レビューで重点確認してほしい点

Claude / Astraレビューでは特に以下を確認する。

1.  設計上、Localの停止・Sleep・Offlineを暗黙に無視している箇所がないか。
2.  Capability Verification項目に不足がないか。
3.  JSONをCanonical Stateとした場合の整合性リスクは何か。
4.  Single Writer / optimistic version checkで不足する競合ケースは何か。
5.  Decision TTLとExecution Pasteの整合性に穴はないか。
6.  User Status / Capacity / Decision Queue / TTLの設計に矛盾はないか。
7.  BUSY解除・Lease終了時のQueue再評価で取り逃しが起きないか。
8.  Historical Replayで未来情報混入が起きる経路はないか。
9.  Quant BacktestとModel Historical Replayの境界は十分明確か。
10. Break機構が過学習・自己正当化を起こす経路はないか。
11. Objective Breakの保護策は十分か。
12. Declared Reason Weightが見せかけの説明になる経路はないか。
13. 損切り設計に欠けている枝はないか。
14. Hard Risk Policyに不足する項目はないか。
15. 高配当Core枠と短中期投資の競合処理は十分か。
16. 監査ログとして不足しているprovenanceはないか。
17. 1か月Paper Tradingで評価可能 / 不可能な項目の切り分けは妥当か。
18. 人間の認知負荷をさらに下げられるか。
19. Local→Serverの移行判断に必要な定量指標は何か。
20. Minimum Vertical Sliceの範囲は適切か。
21. Agent Runtime / Model API境界で曖昧になる指示はないか。
22. Local停止・Sleep・Offline・外部API障害時のSafe
    Degradationに不足はないか。
23. System VersionとPrompt / Tool / Data provenanceの追跡は十分か。
24. 初期版で削るべき機能ではなく「実装延期すべき機能」は何か。

------------------------------------------------------------------------

# 51. 現時点の設計原則まとめ

-   Local-first / intermittent runtime

-   JSONをCanonical Stateとする

-   Portfolio更新はSingle Writer

-   Human-in-the-loop

-   AIは提案、人間が売買実行

-   事実状態と判断ロジックを分離

-   Portfolio履歴は破壊しない

-   Decisionは上書きしない

-   複数探索枝を維持

-   Contradictionを平均化しない

-   BUYとAllocationを分離

-   損切りを単純価格率に限定しない

-   保持期間を戦略別に持つ

-   高配当Core枠を将来保持可能にする

-   ユーザー操作はStatus（FREE / NORMAL / BUSY）、内部ではhuman_capacityへ変換

-   通知可能時間を明示する

-   判断には1行提案＋Declared Reason Weightを出す

-   ProposalにはTTLを持たせる

-   ログはMarkdownで外部監査可能にする

-   見送った銘柄も追跡する

-   Breakは既存構造を前提としない

-   改善は必ずHuman Approvalを通す

-   Quant Backtest / Model Historical Replay / Paper Tradingを区別する

-   LocalでCapability / Reliability
    Verificationを行い、実測上の必要性が確認されてからServer化する

-   Astra全面レビューは通常工程の必須条件にしない

-   Astraは難所のピンポイントレビューに限定し、自己申告を実装保証と扱わない

-   Execution SystemはLocal-first、Data Source / Model APIは外部利用可能

-   Hard Risk Gateは投資判断をしないDeterministic
    Validatorとして定義する

-   Version conflict後は更新種別に応じてRetry / Recalculate /
    Expireを分ける

-   Declared Reason
    Weightは十分なNが溜まるまで説明記録であり公式較正指標としない

-   Review自体もversion管理・監査対象にする

-   Capability VerificationにはAcceptance Criteriaを持たせる

-   Local Availability / Polling LatencyとStrategy
    Requirementを比較して対応Strategy範囲を決める

-   Local停止・Offline時はStateを推測更新しない

-   実行モデルはPersistent Loop + waitを基本とする

-   外部アクセスを伴うJobはRetryable Transactionとして関数化する

-   MAX_RETRY_COUNT到達後もJobを永久破棄せず、次Cycleで再評価・再試行する

-   Retryable ErrorとNon-Retryable Errorを分離する

-   外部API副作用とLocal Atomic Commitを同一Rollback可能領域と誤認しない

-   should_run /
    last_successで周期実行と定時実行を同じRunner上に表現する

-   Server移行後もJob / Transaction契約を維持する

# 52. 変更記録・Provenance（非Normative）

本節は変更履歴と設計Provenanceの記録専用であり、現行仕様を定義しない。現行仕様は§1〜§51の本文を正とし、本節と矛盾する場合は本文を優先する。旧Version、旧Prompt、過去Reviewおよび過去の採否記録は、現行仕様のNormative dependencyではない。以下の回帰試験、運用設定、実装順序の記載も、各時点の採用内容を追跡するための履歴であり、現行要件は本文中の対応節を参照する。

  ------------------------------------------------------------------------------------------
  系列                                     内容
  ---------------------------------------- -------------------------------------------------
  草稿v0.1 → Claude Independent Review #1  設計思想・構造のレビュー

  草稿v0.2 → Claude Independent Review #2  改訂と再レビュー

  草稿v0.3 → Claude final consistency      Portfolio Policy、Queue経路の整合性
  review                                   

  草稿v0.3.1 → Astra Self Review           処理契約のCritical / Major指摘

  Claude OpusによるAstra Review評価        Criticalの妥当性、直列発注案、MVS完了条件を支持

  初期設計v0.1.0（予定草稿v0.3.2を改番）   Astra / Claude指摘を統合したWork-first版

  v0.1.1 Local-first update                Work運用を外し、Persistent Loop + Retryable
                                           Transaction + Catch-upへ実行基盤を置換

  v0.1.2 Local Runtime review               Human I/F、Budget Gate、Secret、Retry economy、Archive等を追加

  v0.1.3 Status redesign                    Configuration / User Status / Capacity分離、BUSY Lease追加

  v0.1.4 Implementation readiness update    Status Writer、CLI / Tray、Alert、Budget Review、Deploy、Storage、Data Provider方針を追加
  ------------------------------------------------------------------------------------------

  ---------------------------------------------------------------------------------------------
  Finding                  本書での処置                                 主な検証
  ------------------------ -------------------------------------------- -----------------------
  C01 事実受領とTTLの混同  §12 / 13で別経路、逸脱は別記録               RV-01 / 02

  C02 Commit・競合・障害   §4 /                                         RV-03 / 04
                           13で単一Envelope、排他、原子的置換、outbox   

  C03 承認〜約定の二重割当 §13.3 / 25で一件Slotと資源予約               RV-05 / 06

  C04 初期構築・段階回復   §15B / 17AでModeと制約別SELL適用             RV-07 / 08

  M01 起動・強制境界       §4 / 17A、CV-00 / 16B                        RV-09 / 10

  M02 Schema・資金・状態   §5 / 12 / 13 / 15B / 25                      RV-02 / 11

  M03 通知・Incident       §22 / 24、Override初期OFF                    RV-12

  M04 選定・分析契約       §6〜8 / 31、欠損と未評価の分離               RV-13

  M05 検証・約定・測定     §29 / 36〜42、事前固定規則                   RV-14

  M06 個別CVとMVS          §46B / 46C / 47 / 49                         RV-16

  M07 変更承認・復元       §33A / 34 / 35 / 46.1                        RV-15

  軽微：成功条件13の重複   §47の番号を整理                              文書静的確認
  ---------------------------------------------------------------------------------------------

本版は設計書の改訂。`capability_tests_executed: false`、`implementation_status: NOT_IMPLEMENTED`。修正が実装上有効であることは以下の試験で確認する。

v0.1.2追加レビュー：Claude Local-first reviewのCritical 3件・Moderate 7件・M03残件を本版へ統合した。

## 52.1 必須回帰試験

  -----------------------------------------------------------------------------------------------------------------------
  ID                      入力・障害                                   期待結果
  ----------------------- -------------------------------------------- --------------------------------------------------
  RV-01                   TTL内約定の遅延Paste／TTL後の実約定          双方を事実受領。逸脱判定を区別

  RV-02                   同じPaste、部分約定、取消、ID不明            二重計上なし。残予約正確。不明は照合待ち

  RV-03                   二つの実行が同じ版を読んで更新               片方だけCommit、他方は最新状態で再評価

  RV-04                   一時書込中／Commit後ログ前で停止             旧版か新版で復旧。ログ再生成、重複なし

  RV-05                   Cash100万円、A / B各70万円を承認             A確保後Bは保留。取消未確定なら資源維持

  RV-06                   承認後の数量・価格条件・Policy変更           古い承認を流用せず再Proposal

  RV-07                   現金からINCOME minを段階構築                 承認済み構築規則で進捗取引を許可、他制約維持

  RV-08                   上限超過25%→20%、低流動性の縮小、過大SELL    規則に合う段階縮小は許可、空売りは拒否

  RV-09                   新規Run、旧コピー、Binding不明               最新正本から復元。不明時に空Portfolioを作らない

  RV-10                   Validator省略、偽PASS、Policy改変            保護境界で拒否。できなければCV-16BをFAIL

  RV-11                   配当・税・費用・入出金・分割・訂正           保存則、簿価、Cash、口座照合が一致

  RV-12                   BUSY日中P0、TTL切れ、未応答、配送障害        Incident維持。時間遵守。再評価と重複制御

  RV-13                   Value用データ欠損、Change用データ有          Changeは評価可能。未評価を否定評価にしない

  RV-14                   引け後承認、指値接触、後日修正された歴史値   過去価格で架空約定せず、当時入手可能な版のみ供給

  RV-15                   System / Objective変更、適用失敗、rollback   承認diffと一致。旧評価保持。事実を巻き戻さない

  RV-16                   BUY→監視→SELL→全売却→再起動                  Cash・保有終了・Watch切替・履歴・Slotが整合

  RV-17                   同一Proposal承認Commandを2回投入               1回だけ承認Commit。Slot / reservation二重取得なし

  RV-18                   Model成功後、Canonical Commit前にProcess kill   Durable Stageを再利用し同一分析を再課金せず復旧

  RV-19                   Daily / Monthly Budget直前でCatch-up大量発生    上限超過Callを開始せず、残JobをBUDGET_EXCEEDEDで保持

  RV-20                   Runner二重起動、stale lock、強制終了             二重poll / API callなし。安全確認後だけlock回収

  RV-21                   古いBackupへRestore後に未反映約定あり            RECONCILIATION_REQUIRED、BUY/ADD停止、Fact追加で整合

  RV-22                   夜間承認後に翌朝価格・Disclosureが変化           発注前再検証し、Trade変更なら旧承認を流用せず再Proposal

  RV-23                   水曜にBUSY「今週いっぱい」を設定                 土曜24:00までBUSY、日曜00:00でNORMAL。Queueは再評価し大量配送しない

  RV-24                   Lease期限切れと同時に人間がBUSY再設定            古い自動遷移はversion conflictで破棄。最新の人間設定を維持

  RV-25                   Budget枯渇中に翌朝pre-submit                     Model依存再検証不能なら発注せずHOLD。hold_ttl後に予約/Slot解放

  RV-26                   BUSY Lease平日10:00終了                          StateはNORMALへ遷移。Maintenance通知は独自Windowを作らず次の許可Windowへ

  RV-27                   HDD未接続でRunner起動                            State/Status確認可。新規取得・Freshness依存BUY/ADD停止。再接続後Catch-up

  RV-28                   Runtime更新時にDev側appを置換                     State / Config / Dataを上書きせず、Schema不一致ならMIGRATION_REQUIRED

  RV-29                   Budget 85% / 95% / 100%到達                       段階Alert、Budget Review候補、100%でSafe Degradation。自動増額なし
  RV-30                               Human Decision誤入力：APPROVE→Correction→SUPERSEDED→reservation release、Broker未発注

  RV-31                               Human Fact誤入力：Execution/Cash/Position Correctionをappendし、旧Factを消さずCurrent State再計算

  RV-32                               System Critical：BUSY中、Override ENABLEDならclosed-class即時通知、DISABLEDならQueueのみ、再起動Popup stormなし

  RV-33                               長期Human不在：Local Runner PAUSE/STOPで新規投資処理停止、再開後Catch-up / reconciliation

  RV-34                               Test/Paper/Live環境分離：state_id / marker mismatchでcross-environment write拒否

  RV-35                               Historical Replay：as_of_time以降の未来DataをStub/Historical Providerが返さない
  -----------------------------------------------------------------------------------------------------------------------

すべて初期結果はNOT_RUN。試験数値はfixtureであり、実運用の投資比率・価格条件の推奨値ではない。

## 52.2 運用設定として残す項目

運用Configurationは原則`config.json`一つへ集約する。運用口座・対象市場、投資予算、Hard上限、Bucket配分、流動性基準、データ鮮度、通知先・再通知間隔、調査予算、Model APIの日次・月次・Job別Budget、P0 emergency reserve、Strategy要求遅延、利用データ契約、Backup retention、Archive rotationは、実装時に
`UNCONFIGURED`
から明示設定する。未設定時の動作は停止／限定試験と定義済みであり、AIが推奨値を勝手に本番採用しない。

User StatusはConfigurationではないため`config.json`に入れず、`user_status.json`へ分離する。Status変更はCLI / Tray経由の`StatusChangeCommand`を通常経路とし、JSON直接編集を要求しない。API key等のSecretも`config.json`に入れない。

大容量Data Rootの初期値は`L:\emori\InvestmentAgentData`とする。約2TBは外付けHDD上で利用可能な運用上限目安であり必要容量予測ではない。Soft/Hard thresholdはDataset実測後にCVで確定し、Alert threshold、Data retention、Backup retentionはConfigurationとして変更可能にする。

TDnet有料APIは除外する。J-Quants / EDINET / News / Model Provider等の利用可否と契約状態はExternal Service Registry / System Statusで確認可能にする。

External Service Registryは少なくとも以下を保持する。

```text
service_id
provider
plan_tier
enabled
paid
human_approval_ref
activated_at
renewal_or_expiry_at
last_successful_call_at
last_auth_success_at
expected_data_freshness
observed_data_freshness
health
```

期限接近、継続認証失敗、決済・契約失効、`last_successful_call_at`過期、Data freshness悪化を区別してWarning / Incident化する。HTTP成功だけでService Healthyとせず、Connectivity / Authentication / Contract / Freshness / Coverageの観点で評価する。

設計修正で決定した事項は、Fact /
Command分離、単一Commit、初回一件Slot、構築・回復Mode、Incident分離、Emergency
Override初期OFF、MVSの売却後復元、CV-16A / B分割である。

## 52.3 Local実装の開始位置

初期実装は**DevelopmentとRuntimeを物理分離**して開始する。

```text
InvestmentAgent-Dev/
├─ SYSTEM.md
├─ manifest.json
├─ config.example.json
├─ schemas/
├─ code/
├─ tests/
├─ validation/
├─ fixtures/
├─ testdata/              # 小容量Fixture / generated metadata。Production dataと分離
├─ docs/
│  ├─ common/openai_api_setup.md
│  ├─ investment/investment_data_services_setup.md
│  └─ test/investment_agent_test_strategy.md
└─ .git/

InvestmentAgent/
├─ SYSTEM.md
├─ manifest.json
├─ app/
├─ config.json
├─ user_status.json
├─ state/
├─ runtime/
├─ stage/current/
├─ inbox/
├─ logs/current/
├─ reports/current/
└─ backups/state/

L:\emori\InvestmentAgentData/
├─ raw/
│  ├─ jquants/
│  ├─ edinet/
│  └─ news/
├─ normalized/
├─ historical/
├─ archive/
├─ reports/
└─ backups/

L:\emori\InvestmentAgentTestData/
├─ datasets/
├─ provider_stub/
├─ historical/
└─ generated/
```

Test Data RootはProduction Data Rootとmarker / state_id / environmentを共有しない。

最初の実装対象：

```text
Command Layer
  ├─ help
  ├─ status
  ├─ budget
  ├─ alerts
  └─ system

Runner
  ├─ single instance
  ├─ loop / should_run / wait
  ├─ StatusLeaseJob
  ├─ retry classification
  └─ run_with_retry

Writer
  ├─ Status Writer
  ├─ Config Writer
  ├─ Canonical State Writer
  └─ Atomic Commit / version conflict

Runtime Services
  ├─ Budget Meter / Gate / Review
  ├─ Alert Queue / Notification Router
  ├─ Windows Tray / Toast Adapter
  ├─ Storage Manager
  └─ External Service Registry

Job
  ├─ external fetch
  ├─ durable stage
  ├─ validate
  └─ atomic local commit
```

CodexではまずCV-00 / 01 / 06 / 07 / 20〜39のうちRuntime基盤に関係する試験を通す最小コードから作り、投資分析Agentを後から載せる。

Shared Storageを導入する場合は、初期用途をBackup / Logs / Reports / Exportとする。Canonical Stateの同期共有は別途整合性設計と試験を行うまで有効化しない。

Server移行は、Local停止時間・監視遅延・取り逃し・Strategy要求を実測して必要になった時点でBreak Proposalとして扱う。

------------------------------------------------------------------------

## 52.4 v0.1.1 Local-first変更点

v0.1.0から投資ロジックそのものは原則変更していない。

主なArchitecture変更：

1.  Work-firstを廃止しLocal-firstへ変更。
2.  PCが常時起動・オンラインでないことを明示的なRuntime前提に追加。
3.  Scheduler中心ではなくPersistent Loop + waitを初期実行モデルとした。
4.  外部アクセス処理をRetryable Transactional Jobとして関数化。
5.  短時間Retry失敗後も次Cycleで再試行し、Jobを永久破棄しない。
6.  Retryable / Non-Retryable Errorを分離。
7.  外部API呼出しとLocal Atomic CommitのRollback境界を分離。
8.  `should_run / last_success`
    により周期実行・定時実行・停止後Catch-upを統一。
9.  Work→Local→ServerをLocal→Serverへ変更。
10. Astra全面レビューを通常工程から外し、難所のピンポイント利用へ変更。
11. Work Capability VerificationをLocal Capability / Reliability
    Verificationへ変更。
12. CV-21としてRetry / 次Cycle再試行 / 重複適用防止を追加。
13. Shared Storageは初期Canonical StateではなくBackup /
    Exchange用途とした。
14. Server化後もJob /
    Transaction契約を維持し、外部障害へのRetry設計を再利用する。


## 52.5 v0.1.2 Claude Local-first Review反映

v0.1.1から投資判断ロジックは変更せず、Local Runtimeの実装契約を追加した。

1. MVS Human I/FをLocal CLIに固定し、承認を`ApprovalCommand`としてWriter経路へ接続。
2. APPROVEとexecution_slot / reservationを同一Atomic Commitで成立させる経路を明文化。
3. Execution Pasteの正規入口をCLI→Durable inbox→Fact Commitとした。
4. Model APIのper-job / per-run / daily / monthly Hard Budget Gateを追加。
5. Budget未設定を本番Model Job停止条件とし、Budget / quota枯渇をSafe Degradationへ追加。
6. Environment Variable / OS secret store、同期Allowlist、Data minimizationをSecret / Privacy契約として追加。
7. Runner single-instance lock、stale lock recovery、heartbeatを追加。
8. Adapter-level exponential backoff / Circuit Breakerを追加。
9. Durable Stage Resultを追加し、API成功後Commit失敗時の再課金を回避。
10. Current Envelopeとappend-only Archiveを分離し、rotation / compaction契約を追加。
11. Backup / Restore後の`RECONCILIATION_REQUIRED`とBUY / ADD停止を追加。
12. PC availability waitとnotification-window waitをLatencyへ分解。
13. After-close承認→翌営業日pre-submit revalidationを通常経路として追加。
14. Codex実装時のAcceptance Criteria / expected result固定とbaseline hashを追加。
15. Supported Runtime OSをWindowsへ固定し、Wall Clock / Monotonic Clock方針を追加。
16. CV-22〜CV-31を追加。

## 52.6 v0.1.3 Configuration / User Status整理

v0.1.2から投資判断ロジックは変更せず、Configurationと人間状態の責務を分離した。

1. 運用Configurationを`config.json`一つへ集約。
2. Risk / Portfolio / Notification / Retry / Budget / Strategy / Watch / Selection等の設定値を分散させない方針を追加。
3. User StatusをConfigurationから分離し、`user_status.json`を正本とした。
4. User Statusを`FREE / NORMAL / BUSY`へ変更。
5. Internal Human Capacityを`LARGE / MEDIUM / SMALL`としてStatusから導出する形へ固定。
6. `FREE → LARGE`、`NORMAL → MEDIUM`、`BUSY → SMALL`のMapperを明文化。
7. BUSYが通知抑制によりSticky State化する非対称性を設計対象へ追加。
8. BUSYを期限付きLeaseとして扱えるようにし、`1時間 / 3時間 / 今日いっぱい / 今週いっぱい / 変更するまで`を初期プリセットとした。
9. 「今週いっぱい」は日曜00:00開始〜土曜24:00終了のカレンダー週と定義し、内部では次の日曜00:00を排他的`effective_until`として保存。
10. 期限付きBUSY終了後は`NORMAL`へ戻し、`FREE`へ自動遷移しない。
11. Status Maintenance通知を投資通知とは別classに分離し、BUSY Lease終了等のStatus変化を通知可能にした。
12. Status変更後のQueueは再評価し、滞留Proposalをそのまま大量配送しない。
13. `config_hash`をRun / Decision Recordへ保存し、判断時点のConfiguration再現性を確保。

## 52.7 v0.1.4 Implementation Readiness / Operations反映

v0.1.3から投資判断ロジックは変更せず、Local実装・日常運用に必要な契約を追加した。

1. `user_status.json`へ`status_version`を追加し、人間操作とLease期限切れの競合をStatus Writerで解決。
2. Status変更の通常操作をJSON編集からCLI / Tray `StatusChangeCommand`へ変更。
3. `help`、`status`、`budget`、`alerts`、`system`をMVS CLIの基本Commandとして追加。
4. BUSY Leaseの期限はCLI側で計算し、解決後の絶対終了時刻をエコーする。
5. Status Maintenanceは独自Notification Windowを作らず、State遷移後に次の許可Windowへ相乗り。
6. Model Budgetのusage / token / remainingをRuntime Healthとして表示し、段階Alertと`budget review`を追加。
7. Budget枯渇時のpre-submitをFail Closedとし、`HOLD_FOR_REVALIDATION` + Incident + hold TTLを追加。
8. `p0_emergency_reserve`を明示設定項目とし、未設定のまま本番開始しない。
9. Alert Queueを正本とし、CLI / Windows Popupを初期Notification Adapter、EmailをDeferredとした。
10. Local ProcessをWindows Task Trayへ格納可能とし、TrayとCLIを同一Command Dispatcherへ接続。
11. 開発用`InvestmentAgent-Dev`と実行用`InvestmentAgent`を物理分離し、手動Deploy契約を追加。
12. 初期更新をRuntime停止→Backup→app置換→Schema/Migration確認→Validation→再起動とした。
13. 大容量Data Rootを`L:\emori\InvestmentAgentData`へ固定し、運用目安約2TB、Soft Warning候補約1.8TBとした。
14. Raw / Normalized / Historical / Archiveを分離し、時系列Normalized DataはJSONLを初期標準候補とした。
15. External Data Storage未接続時の`DATA_STORAGE_UNAVAILABLE`縮退と復帰後Catch-upを追加。
16. Structured DataはJ-Quants、法定開示はEDINETを初期Provider候補とし、TDnet有料APIを明確に除外。
17. 契約・導入手順を`openai_api_setup.md`と`investment_data_services_setup.md`の2カテゴリへ分離して管理する方針を追加。
18. CV-33〜39、RV-24〜29を追加。



------------------------------------------------------------------------

## 52.8 v0.1.5 Runtime Boundary / External Service Governance反映

v0.1.5ではv0.1.4レビューおよび実装前検討を受け、以下を追加・確定した。

1. CLI / Tray / Runnerは共有Service Layerを利用し、Runner停止中でもStatus変更等の軽量Commandを処理可能にした。
2. Runner Lifecycleは後続レビューによりINIT / RUNNING / RESUMING / ENDへ簡素化した。
3. OS kill / crashを状態ではなく終了事象として扱い、次回起動時にRESUMINGで復旧する。
4. Alert SeverityとHuman Notification Priorityを別軸とし、SYSTEM CRITICALはInvestment P0とは別Classで即時通知可能にした。
5. Job開始時Config Snapshotを固定し、Run途中のConfig変更を次Jobから有効化する。
6. `L:\emori\InvestmentAgentData`はMarkerでStorage Identityを照合し、同一drive letterの別Diskへの誤書込みを防ぐ。
7. Storage監視を絶対容量だけでなくfree space / directory growth rateまで拡張した。
8. External APIを`ExternalServiceGateway` + Domain Provider AdapterでWrappingし、Business LogicからProvider固有APIを隔離した。
9. Market / Disclosure Adapterの責務を「取得→検証→Raw保存→Normalize→所定JSON保存」までとした。
10. OpenAI等のLLM APIもModelProvider Wrapper配下に置き、投資APIと共通のPaid Service Governanceを適用した。
11. 新規有料Service、Plan Upgrade、Add-on、Budget増額、有料FallbackはHuman explicit approvalなしに実施禁止とした。
12. Provider選定理由はDesignから分離しADRで管理する。
13. J-Quants Freeは開発/構造試験用、Paper Trading開始前にLight以上をHuman approval付きで導入するGateとした。
14. J-Quantsはbulk取得→Raw保存→Local filterを基本とし、rate limit成立性をCVで確認する。
15. Provider update schedule waitをLatency分解へ追加した。
16. TDnet有料APIの除外を維持し、TDnet由来情報のJ-Quants代替範囲をCVで確定する。


------------------------------------------------------------------------

## 52.9 v0.1.6 Design Completion / Implementation Baseline

v0.1.6ではv0.1.5レビューと実装開始前の運用検討を反映し、初期設計を一旦完成とする。

1. v0.1.5で新設したRuntime / External Service契約にCV-40〜50を追加し、設計契約とVerification Matrixを同期した。
2. Alert旧Severity記述を整理した。当時の変更記録であり、現行のNotification Window / Overrideは§22、Severity / Priority / deliveryは§24.0を正とする。
3. System Critical OverrideをInvestment P0から分離し、初期`UNCONFIGURED`→HumanがENABLED/DISABLEDを選択する契約とした。
4. System Critical対象をclosed classとし、Investment EventがOverride経路を迂回利用できないようにした。
5. System Criticalへdedup / renotify / popup上限制御を追加した。
6. Local版の長期Human不在は新Statusを追加せずRunnerを正常終了させる。Server化時にHuman UNAVAILABLE等を再検討する。
7. Human Decisionに`decision_impact`を追加し、Human入力誤りはRecord削除ではなくCorrection / Supersedeで回復する。
8. Broker操作済みFactはCorrectionで消さず、取消・反対売買等を新しいDecisionとして扱う。
9. Canonical State Backupを外付けHDD単一点にせず、内蔵SSDへ直近N世代を保持する。
10. Storage枯渇時の縮退順序を定義し、Raw / Historical等よりCanonical / Audit / recent backupを優先保護する。
11. External Service RegistryへPlan / approval / expiry / last success / freshness / healthを追加した。
12. J-Quants CVをFree Adapter VerificationとLight Operational Capability Verificationへ分離した。
13. Paper Trading開始条件を「Light契約」ではなく「Light Capability CV PASS」とした。
14. Test詳細を本設計から分離し、別`investment_agent_test_strategy.md`で管理する方針とした。
15. Architecture側にはLocal Stub Provider、Historical as-of境界、Test/Paper/Live分離、Test Dataset Generatorの存在だけを契約として残した。
16. 開発工程を`Design → Account Setup → Coding → Historical Test → Light CV → Realtime Paper → Live Readiness`として明示した。

以後v0.1系列では、実装により判明した契約矛盾・欠落の修正を中心とし、設計段階での機能追加を原則終了する。


------------------------------------------------------------------------

## 52.10 v0.1.7 Final Baseline Resolution

v0.1.7では初期実装前の最終レビュー残件を局所修正し、新しい大規模Scopeは追加していない。

1. `RV-01〜35`をMVS成立後のRegression Verification Setとして明示し、Affected / Core / Fullの実行位置を定義した。
2. Storage Pressureの`Preserve last`へPosition Watch Minimum Dataを追加し、Storage Criticalでも保有Positionの重大Risk監視に必要な最小Data取得・Normalizeを優先保護する。
3. Human CorrectionはPaid Service Governance、Risk Policy、State Integrity、Environment Bindingを迂回できないことを明示した。
4. `decision_impact`は初期版では記録・表示・監査用metadataとし、CLI挙動を分岐させない。
5. `data_root_marker.json`へ`environment = TEST | PAPER | LIVE`を追加し、`state_id` / `data_root_id` / `environment`不一致時のwriteを拒否する。
6. CV-44 / 45 / 47を上記契約へ追随させた。
7. Test Fixture / Stub / Dataset Generator / Historical Replayの詳細設計は別Test Strategy文書へ分離する方針を維持する。
8. System名を`argus`（アーガス）として確定し、Project / Package / Folderの命名基準を固定した。
9. `ENVIRONMENT_BINDING_MISMATCH`をSystem Critical closed classへ追加した。
10. `POSITION_WATCH_DATA_UNAVAILABLE`を`severity = CRITICAL` / `priority = P0 / INVESTMENT`として分類し、System OverrideではなくInvestment P0通知規則へ接続した。

本版をもって設計書の通常レビューサイクルを終了し、以降は実装・CV / RV・Historical / Realtime Paperで得られた**実測Evidence**を優先する。設計変更が必要になった場合は、実装上の観測・CV FAIL・Break / ADR等の具体的根拠から変更する。



## Final Freeze

本ファイルを`argus`初期実装のDesign Baseline正本とする。  
以降、レビューだけを理由に通常の設計改版を継続しない。変更は、実装上の観測、CV / RV結果、Historical / Realtime Paperの実測、Break / ADR等の具体的Evidenceを根拠として行う。
