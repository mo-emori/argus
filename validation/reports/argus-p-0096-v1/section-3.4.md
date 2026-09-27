## 3.4 状態とデータ

状態、分類、事実、観測、判断、操作要求、正本、表示用データを同じ箱に入れてはならない。現在状態、運用Mode、重大度、優先度、Portfolio分類を一つの状態軸として扱うと遷移判断を誤る。現実の事実、時点付き観測、判断結果、変更要求を混同すれば、確認済みの事実を拒否したり履歴を壊したりする。外部呼出し結果、正本更新、表示用派生物を同じArtifactとして扱うと、再実行の要否と正本性も誤る。

本節では、状態を持つ概念と独立した分類軸を分け、データと操作要求の意味および更新経路を分離する。その上で、永続化段階とArtifactのAuthorityを区別し、事実を保存する単一正本と、再現可能で原子的な更新を成立させる。Identity、設定、Status、Fact、Observation、Judgment、Workflow、Stage、Projectionは、それぞれ生成元、利用先、保持条件、更新Authorityが異なる。

### 状態軸と分類軸

State、User Status、human_capacity、Runner State、Policy Mode、Holding Horizon、Role Bucket、severity、priorityは、それぞれ独立した意味と利用先を持つ。

| 対象 | 区分 | 意味・値 | 禁止・境界 | 主な利用先 | 参照先 |
|---|---|---|---|---|---|
| State | 現在状態 | DomainまたはRuntime対象の現在値と遷移履歴 | User Status、Policy Mode、単なる分類値を一括してStateと呼ばない | Canonical State、Proposal、Order等 | §4〜5、§13 |
| User Status | 人の現在状態 | `FREE / NORMAL / BUSY`。人が直接操作する | Configurationではなく、human_capacityの入力である | 通知、Queue、処理量制御 | §4.0、§21〜23 |
| human_capacity | 内部制御値 | `LARGE / MEDIUM / SMALL`。Status Mapperが導出する | 人の入力値でもUser Statusそのものでもない | Queueと処理範囲 | §21、§23 |
| Runner State | Runtime状態機械 | `INIT / RUNNING / RESUMING / END` | OS kill / crashは状態ではなく終了事象。User Statusとも別対象 | Runner Lifecycle | §4.2〜4.3 |
| Policy Mode | Policy状態 | `NORMAL / BOOTSTRAP / REPAIR` | Holding HorizonやRole Bucketではない | Portfolio制約の適用 | §15B |
| Holding Horizon | 分類 | `SHORT / MEDIUM / LONG / CORE`の想定時間軸 | 強制SELL状態ではなく、Role Bucketとも別軸 | Thesis、Time Stop | §16 |
| Role Bucket | Portfolio分類 | `INCOME / GROWTH / EVENT / DEFENSIVE / OTHER / CASH` | Holding Horizonと足し合わせず、lotを二重計上しない | Allocation、Policy | §14〜15B |
| severity | 重大度分類 | `INFO / WARNING / CRITICAL` | 人へ届ける時期を表すpriorityとは別軸 | Alert、Incident | §24.0 |
| priority | 配送優先度 | `P0〜P3` | severityから暗黙に導出しない | Decision / Alert Queue | §24.0 |

### 事実、観測、判断、要求、訂正、証拠

Fact、Observation、Judgment、Command、Correction、Evidenceは別のデータ種別であり、意味だけでなく更新経路も分ける。

| 対象 | 区分 | 意味 | 禁止・境界 | 主な利用先 | 参照先 |
|---|---|---|---|---|---|
| Fact | データ／事実 | 約定、Cash、Position、配当、税、費用等の確認済み現実 | TTLやPolicy違反があっても確認済みFactを拒否しない | Canonical Facts | §12〜13 |
| Observation | データ／観測 | price、FX、liquidity等の時点付き観測 | FactやJudgmentから分離し、`as_of`等のprovenanceを持つ | 分析、Risk、Watch | §13.1、§29 |
| Judgment | データ／判断 | Decision、Thesis revision、分類等の判断結果 | 判断行為ではなく結果を保持する。Factを上書きせず、変更は履歴追加とする | Report、Proposal、Audit | §5、§13.1、§29 |
| Command | 入力／変更要求 | `request_id`付きの人またはSystemからWriterへの変更要求 | Factは起きた現実、Proposalは判断候補であり、Commandではない | Status、Approval、Correction、Config | §4.0、§4.3、§24.3 |
| Correction | 入力／変更管理 | Human入力の誤りを、過去Recordの削除ではなく訂正履歴として追加する | Broker現実のRollbackではなく、Governanceを迂回しない | Decision、Execution、Cash等 | §24.3 |
| Evidence | データ／証拠 | 出典原文または許諾範囲の抜粋、取得情報、hash、vintage | URLだけで固定せず、Observationの根拠として保持する | Analysis、Audit、Replay | §4、§29、§38〜39 |

Fact・Observation・Judgment・Workflowの混同に加えて、並行更新や途中停止も正本を破損させ得る。確認済み現実はFactとして受け入れ、観測時点と出典はObservationに残し、判断の変更は新しいJudgmentとして追加し、操作はCommandとしてWriterへ渡す。Correctionも過去を消さず、訂正の経緯を残す。

### 永続化段階、正本、派生物

Durable Stage Result、Commit、Canonical State、Current Envelope、Projection、Artifact、Configuration、Runtime Identityは、同じ「成果物」という理由で統合しない。

| 対象 | 区分 | 意味 | 禁止・境界 | 主な利用先・実体 | 参照先 |
|---|---|---|---|---|---|
| Durable Stage Result | 中間Artifact | 外部呼出し結果をCommit前に永続化したもの | Canonical Stateではない | External / Model Jobの再開と再課金防止 | §2.5、§13.4 |
| Commit | Transaction結果 | 検証済み遷移を一つの原子的State versionとして確定する | 外部API副作用は同じRollback境界にない | Single Writer | §2.3、§13.2 |
| Canonical State | 正本Artifact | PortfolioとWorkflowの現在正本 | Projection、Markdown、Backup、会話履歴を正本にしない | `portfolio.json` | §4、§13 |
| Current Envelope | Canonical State構造 | 現在状態と復旧に必要な直近参照を持つ | 全履歴を無期限に埋め込まずarchiveを参照する | state / archive | §13.4 |
| Projection | 派生Artifact | Canonical Stateから再生成する表示・互換用データ | 独立更新しない | watchlist、queue、Markdown | §4、§13.2 |
| Artifact | 設計・運用成果物 | Identity、State、Log、Report、Validation record等 | ArtifactごとのAuthorityと正本性を区別する | Repository / Runtime | §4、§29、§46B |
| Configuration | 設定Artifact | 人が明示する動作規則の単一正本 | Status、State、Secret、Identityと分離する | `config.json` | §4.0 |
| Runtime Identity | Identity Artifact | logical instanceの不変な`state_id / environment / data_root_id`等 | Deployment Identity、Run Identity、path、設定値と分離する | Bootstrap / Binding | §4.0 |

Canonical StateはSingle Writerだけが原子的Commitによって更新する。Current Envelopeは現在値と復旧に必要な参照を保持し、古い履歴はarchiveへ委ねる。Projectionは正本から再生成できる表示であり、独自の更新Authorityを持たない。Durable Stage Resultは再開のための中間永続結果であって、検証済みFactでもCommit済みStateでもない。

### データごとの生成元、利用先、保持条件、Authority

Canonical Envelope、inbox、archive、Stage、Projectionは、Canonical Stateを安全に更新し、履歴を保持し、派生表示を作るための別々の構成要素である。RuntimeからAuditまでのCanonicalおよび派生データは、次の責務分離に従う。

| データ | 区分 | 生成元・更新Authority | 利用先 | 保持条件・禁止 | 参照先 |
|---|---|---|---|---|---|
| Runtime Identity | 不変Identity Artifact | Setup / Bootstrap | Binding、起動 | `state_id / environment / data_root_id`等を保持し、path、Secret、Status、Domain Stateを入れない | §4.0 |
| Configuration | 設定 | 人の明示設定、Config Writer | Job、Policy、Budget、通知等 | `config.json`を単一正本とし、version/hashとJob開始時のimmutable snapshotを持つ | §4.0 |
| User Status | 人の現在状態 | StatusChangeCommand | capacity、Queue、通知 | `user_status.json`と`status_version`を持ち、直接編集を通常操作にしない | §4.0、§21 |
| Facts | 事実データ | Broker結果、入出金、配当、税、手数料、Corporate Action、Correction | Portfolio、Cash、Position | 確認済み事実を拒否・破壊せず、過去へ上書きしない | §12〜13 |
| Observations | 観測データ | Provider Adapter | 分析、Risk、Watch | `as_of / published / retrieved / source / revision / hash`を保持する | §13.1、§29、§37A |
| Judgments | 判断データ | Agent、人 | Proposal、評価、監査 | immutable Decision、Thesis revision、Human Decisionとして保持する | §13.1、§29 |
| Workflow | 状態データ | Queue、Approval、Order、Reservation、Watch | 実行制御 | Proposal、Order、Incident等の独立状態を保持する | §5、§13.1 |
| Rawデータ | 外部原本 | Provider Adapter | Normalize、監査 | 許諾範囲でimmutable保存する | §4.7、§37A |
| 正規化データ | Provider非依存データ | Provider Adapter | Selection / Analysis | provenanceからRawデータへ追跡可能にする | §4.7、§37A |
| Durable Stage | 中間永続結果 | External / Model call | Validate / Commit再開 | 再課金・重複適用を防ぎ、Canonical Factとは区別する | §2.5、§13.4 |
| Audit / Decision Log | 監査Artifact | Canonical CommitからのProjection | 人・別AIによるレビュー、評価 | Markdownは正本ではなくProjectionである | §28〜30 |

Canonical Envelopeは正本の現在形を包み、inboxは更新要求を受け、Stageは外部処理やModel処理の中間結果を再開可能にし、Commitだけが検証済み変更を正本へ反映する。archiveは履歴を保持し、ProjectionはCommit済み正本から生成する。この分離によって、途中停止からの再開、重複適用の防止、監査時の追跡を両立する。

### Research lifecycle

発見、候補化、分析、監視、終了を一つの銘柄状態へ押し込むと、調査履歴と欠損理由が失われる。Research lifecycleは、`DISCOVERED / CANDIDATE / ANALYZED / WATCH / ARCHIVED`を持つ独立状態機械とする。

| 対象 | 遷移前 | 条件 | 記録・処理 | 遷移後 | 利用先 | 禁止・境界 | 参照先 |
|---|---|---|---|---|---|---|---|
| Research | 未登録 | ユニバース / branch探索で発見 | sourceと枝別状態を記録 | DISCOVERED | Candidate評価 | 枝別欠損を否定評価にしない | §5〜7 |
| Research | DISCOVERED | Candidate条件成立 | 候補として登録 | CANDIDATE | Candidate Watch対象になり得る | `DATA_INSUFFICIENT`を0点化しない | §5〜7 |
| Research | CANDIDATE | 独立分析完了 | branch結果と矛盾を保存 | ANALYZED | Report / Proposal生成可能 | 未評価理由を保存する | §5、§7〜9 |
| Research | ANALYZED | 継続監視判断 | Watchへ登録 | WATCH | Candidate Watch | 売買承認として扱わない | §5、§18 |
| Research | 任意 | 対象外または追跡終了 | 理由を記録 | ARCHIVED | Counterfactual sample対象になり得る | 履歴を削除しない | §5、§31 |

ARCHIVEDは履歴の削除ではない。未評価やデータ欠損を否定評価へ変換せず、発見元、枝ごとの状態、矛盾、終了理由を保持する。

### Thesis revision

投資仮説を上書きまたは二値化すると、弱化、失効、不明とEvidence履歴を区別できない。ThesisはrevisionとEvidence変化を状態遷移として保持し、`VALID / WEAKENED / INVALIDATED / UNKNOWN`をそれぞれ独立した状態として扱う。

| 対象 | 遷移前 | 条件 | 記録・処理 | 遷移後 | 利用先 | 禁止・境界 | 参照先 |
|---|---|---|---|---|---|---|---|
| Thesis | 未作成 | Analysisで投資仮説成立 | revisionとして保存 | VALID | Invalidator / イベント監視開始 | 旧revisionを上書きしない | §5、§9、§18 |
| Thesis | VALID | 反証またはイベントが一部悪化 | Evidence比較と再分析 | WEAKENED | HOLD / REDUCE等の候補 | データ不足時はUNKNOWNを検討する | §17、§27 |
| Thesis | VALID / WEAKENED | 購入理由が崩壊 | Thesis Stop判定 | INVALIDATED | 最優先のSELL / REDUCE再分析 | Priceだけで即SELLしない | §17.1、§27 |
| Thesis | 任意 | Evidence不足または矛盾未解決 | 不明状態を明示 | UNKNOWN | BUY / ADD停止になり得る | trueやVALIDへ推測しない | §5、§8、§17A |

弱化は失効ではなく、不明は偽でも有効でもない。各revisionと根拠Evidenceを保存することで、いつ何が変わり、どの判断候補へつながったかを追跡できる。

### Holding lifecycleと数量の正本

Holding状態をProposalやOrderから推測すると、部分約定や全売却後の監視終了を誤り得る。Holdingの遷移は確認済みExecution Factと数量に基づく。`未保有 / CLOSED`、`OPEN`、`partial SELL`、`全売却`は同じ意味ではない。partial SELLと全売却は遷移を起こす事象であり、結果の数量と整合処理を確認して状態を確定する。

| 対象 | 遷移前 | 条件 | Commitする更新 | 遷移後 | 利用先 | 禁止・境界 | 参照先 |
|---|---|---|---|---|---|---|---|
| Holding | 未保有 / CLOSED | BUY Execution Fact適用後に`quantity > 0` | Position、lot、Cashを更新 | OPEN | Position Watch開始 | 未確認Executionでは遷移しない | §5、§12、§46C |
| Holding | OPEN | Partial SELL後も`quantity > 0` | lot、Cash、P/Lを更新 | OPEN | Watch継続 | cumulative quantityを新規fillとして扱わない | §12〜13、§46C |
| Holding | OPEN | SELL後に`quantity = 0` | 全売却の整合をCommit | CLOSED | Position Watch終了。必要ならCandidate Watchへ | Slot / reservationの整合前に終了しない | §5、§13.3、§46C |

集計Positionの単位は`account_id + instrument_id`である。Proposalの作成やOrderの送信だけでは保有は変わらず、確認済みExecution Factを適用した数量だけがHolding遷移の根拠になる。

### 同一銘柄内で併存する履歴と関係

一つの銘柄を一つの状態へ平坦化しない。lot / trancheはDecisionとThesisへ多対一で紐付く。同一銘柄には、保有とCandidate、新旧Thesis、複数Decisionがそれぞれ併存できる。したがって、銘柄単位の上書きではなく、lot / tranche、Decision、Thesis、Research、Holdingを個別のIdentityと履歴で結び付ける。この関係モデルの詳細な利用先は§5で扱う。

以上の区別は、保存と復旧の前提でもある。正本、履歴、Stage、Projectionの責務を混ぜず、確認済みFactを失わず、各状態機械の遷移根拠を残すことで、再開後も同じAuthorityと正本性を維持できる。保存、バックアップ、検証、復旧、再開の具体的責務は3.5で扱う。
