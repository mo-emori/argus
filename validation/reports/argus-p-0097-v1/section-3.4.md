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
