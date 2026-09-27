# ARGUS 構造化設計データ v0.1

## 1. 文書情報と権限

**課題：** 成果物の役割、正本、対象版、生成範囲が不明だと、後続工程がAuthorityを誤る。  

**目的：** Structured Design Dataの文書境界と正本関係を明示する。  

**対象：** 文書の役割、状態、Design Source、対象設計、生成対象外。

| 項目 | 内容 |
|---|---|
| 文書の役割 | Design Sourceに記述された設計を、設計要素、型、関係、処理、状態、責務、境界として再構成し、実装・Testで原則として直接参照する設計Artifact |
| 状態 | 人による確認待ち |
| 設計内容の唯一の一次資料 | `docs/source/argus_design_source_v0.1.md` |
| Design SourceのSHA-256 | `feff970e4dc59c599c7fc5e48c5f77b87e7806aa156e87f8dd26bdae36609681` |
| 対象設計 | `argus` Local-first初期実装Baseline / v0.1.7 Final Freeze |
| 生成対象外 | Human System Design、実装、試験結果、Design Sourceにない追加設計 |

### 1.1 読み方

**課題：** 表・locator・派生Artifactの読み方が不明だと、Source本文の代替や独立正本として誤用され得る。  

**目的：** 構造化単位、Source locator、Authority競合時の読み方を定義する。  

**対象：** 本書の表、設計元位置、Design SourceとStructured Design DataのAuthority境界。

**規則：**
- 本書はDesign Source本文を複製せず、分散した記述を設計意味ごとに統合する。各表の行は同じ意味型の集合とし、処理、状態機械、規則、制約、データ、主体、境界、失敗・復旧、検証、変更管理を分離して表現する。
- 各主要要素の「設計元位置」は根拠となるDesign Sourceの章節を示す。設計元位置は設計内容の代替ではなく、Sourceとの意味照合と文脈確認に用いる。本書とDesign Sourceに不一致がある場合はDesign Sourceを優先し、人が確認する。
- 本書を使い捨ての生成中間物として扱わない。設計変更時はDesign Sourceと本書を同期変更し、不一致時はDesign SourceをAuthorityとして解消する。

## 2. 用語・概念体系

**課題：** ARGUS固有語を未定義または同義として扱うと、Entity、状態、権限、処理の境界を誤解し得る。  

**目的：** 重要用語を概念種別ごとに定義し、相違と利用関係を示す。  

**対象：** 主体、状態、Data、Workflow、Policy、Commit、分析・検証概念。

### 2.1 権限主体

**課題：** 人、ARGUS、Broker、Agentの権限をRuntime componentや処理機能と混同すると、Human-in-the-loopと更新境界が崩れる。  

**目的：** 設計上の権限主体を、その意味と実行主体・処理責務との関係によって区別する。  

**対象：** 人、ARGUS、Broker、Agent / LLM。

| 権限主体 | 概念種別 | Source上の意味 | 他概念との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| 人 | 主体・最終権限者 | 投資、Broker操作、有料Service、Policy、Break、実資金開始を最終判断する主体 | ARGUSの提案・自動処理と分離する | 承認、拒否、操作、Paste、設定 | §1、§11、§34、§37A、§43、§47 |
| ARGUS | システム主体 | 探索、分析、提案、検証、Queue、状態更新、監視、評価を行うLocal-firstシステム | Brokerではなく、人の最終判断を代替しない | 全Runtime / Domain処理 | §1〜3、§43 |
| Broker | 外部主体 | 人の売買操作を受け、注文・約定等の現実を成立させる | ARGUSの初期自動実行対象ではない | Order、Execution Fact | §12〜13、§43 |
| Agent / LLM | システム内判断生成主体 | 分析、提案、Update Request、Reviewを生成する | 固定Writer / Validatorと異なり、Canonical State更新権限を持たない | 分析、Break、別AI Review | §7〜9、§13.2、§30 |

**規則：**
- 権限主体は人、ARGUS、Broker、Agent / LLMとする。Runtime / UI componentは実行主体として別に扱う。
- Analysis、Allocation、Selection、Retry制御、Failure分類は処理責務であり、主体として分類しない。
- 役割、責務、権限は主体と同列の主体分類ではない。
- 役割は主体またはPortfolio lotの機能的位置付けとして、主体表・処理表・境界表の属性または関係に置く。
- 責務は主体が担当する処理として、主体表・処理表・境界表の属性または関係に置く。
- 権限は主体へ許可された操作として、主体表・処理表・境界表の属性または関係に置く。

### 2.2 State、Status、Mode、分類

**課題：** 現在状態、運用Mode、重大度、優先度、Portfolio分類を一つの状態軸へ混在させると遷移判断を誤る。  

**目的：** 状態を持つ概念と独立した分類軸を区別する。  

**対象：** State、User Status、human_capacity、Runner State、Policy Mode、Holding Horizon、Role Bucket、severity、priority。

| 用語 | 概念種別 | 定義 | 他用語との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| State | 現在状態 | DomainまたはRuntime対象の現在値と遷移履歴 | User Status、Policy Mode、単なる分類値を一括してStateと呼ばない | Canonical State、Proposal、Order等 | §4〜5、§13 |
| User Status | 人の現在状態 | `FREE / NORMAL / BUSY`。人が直接操作する | Configurationではなく、human_capacityの入力である | 通知・Queue・処理量制御 | §4.0、§21〜23 |
| human_capacity | 内部制御値 | `LARGE / MEDIUM / SMALL`。Status Mapperが導出する | 人の入力値ではなく、Statusそのものでもない | Queueと処理範囲 | §21、§23 |
| Runner State | Runtime状態機械 | `INIT / RUNNING / RESUMING / END` | OS kill / crashは状態ではなく終了事象であり、User Statusとも別対象 | Runner Lifecycle | §4.2〜4.3 |
| Policy Mode | Policy状態 | `NORMAL / BOOTSTRAP / REPAIR` | Holding HorizonやRole Bucketではない | Portfolio制約の適用 | §15B |
| Holding Horizon | 分類 | `SHORT / MEDIUM / LONG / CORE`の想定時間軸 | 強制SELL状態ではなく、Role Bucketとも別軸 | Thesis、Time Stop | §16 |
| Role Bucket | Portfolio分類 | `INCOME / GROWTH / EVENT / DEFENSIVE / OTHER / CASH` | Holding Horizonと足し合わせず、lotを二重計上しない | Allocation、Policy | §14〜15B |
| severity | 重大度分類 | `INFO / WARNING / CRITICAL` | 人へ届ける時期を表すpriorityとは別軸 | Alert / Incident | §24.0 |
| priority | 配送優先度 | `P0〜P3` | severityから暗黙導出しない | Decision / Alert Queue | §24.0 |

### 2.3 Fact、Observation、Judgment、Command

**課題：** 現実の事実、時点付き観測、判断結果、変更要求を混同すると、事実拒否や履歴破壊が起き得る。  

**目的：** Dataと操作要求の意味および更新経路を分離する。  

**対象：** Fact、Observation、Judgment、Command、Correction、Evidence。

| 用語 | 種別1（構造上の役割） | 種別2（意味上の役割） | 定義 | 他用語との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|---|
| Fact | データ | 事実 | 約定、Cash、Position、配当、税、費用等の確認済み現実 | TTLやPolicy違反でも確認済みFactを拒否しない | Canonical Facts | §12〜13 |
| Observation | データ | 観測 | price、FX、liquidity等の時点付き観測 | FactやJudgmentと分離し、as_of等のprovenanceを持つ | 分析、Risk、Watch | §13.1、§29 |
| Judgment | データ | 判断 | Decision、Thesis revision、分類等の判断結果 | 判断という行為ではなく判断結果を保持する。Factを上書きせず、変更は履歴追加する | Report、Proposal、Audit | §5、§13.1、§29 |
| Command | 入力 | 変更要求 | request_id付きの人またはSystemからWriterへの変更要求 | Factは起きた現実、Proposalは判断候補であり、Commandと異なる | Status、Approval、Correction、Config | §4.0、§4.3、§24.3 |
| Correction | 入力 | 変更管理 | Human入力の誤りを過去Record削除でなく訂正履歴として追加する | Broker現実のRollbackではなく、Governanceを迂回しない | Decision / Execution / Cash等 | §24.3 |
| Evidence | データ | 証拠 | 出典原文または許諾範囲の抜粋、取得情報、hash、vintage | URLだけで固定せず、Observationの根拠となる | Analysis、Audit、Replay | §4、§29、§38〜39 |

### 2.4 Proposal、Approval、Order、Incident、Alert

**課題：** 判断候補、Human権限行使、外部取引、問題状態、配送対象を同一Workflowとして扱うと、承認流用や状態消失が起き得る。  

**目的：** 各Entityの役割と状態関係を区別する。  

**対象：** Proposal、Approval、Order、Execution Fact、Incident、Alert、Notification、Decision Queue。

| 用語 | 概念種別 | 定義 | 他用語との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| Proposal | Workflow状態を持つ判断候補 | revision、trade_hash、TTL、valid_if等へ拘束された具体的提案 | 興味・Watch登録、Approval、Order、Incidentと別Entity | Decision Queue | §5、§10、§25 |
| Approval | Human Command・権限行使 | 人が特定Proposal revision / trade_hashを承認する | Broker発注・約定を意味せず、再検証とSlot確保が必要 | Approval Service | §4.3、§13.3、§25 |
| Order | Workflow状態を持つ外部取引単位 | 発注待ち、発注済み、部分約定、取消等を表す | Proposal TTLから独立し、Holdingとも別Entity | Broker execution管理 | §5、§13.3、§25 |
| Execution Fact | Fact | Brokerで実際に成立した約定等 | Order / Proposalの妥当性判定と入口を分ける | inbox→Commit | §12 |
| Incident | Durableな問題状態 | `OPEN / ACKNOWLEDGED / RESOLVED`を持つ | Proposal失効で消えず、Alert配送状態とも別 | Risk / System問題追跡 | §5、§24.1 |
| Alert | Durable Queue item | Event / Incident等をHumanへ伝えるための記録 | Popup等の配送手段そのものではない | Alert Queue、Router | §24.0 |
| Notification | 配送試行 | notification_idを持つ外部提示 | delivered、acknowledged、resolvedを混同しない | CLI / Windows Popup等 | §24.2 |
| Decision Queue | Workflow / 安全機構 | 全Human Proposalを再評価・順位付け・配送制御する単一経路 | 各Agentから直接通知させない | Proposal、Break、Emergency | §24 |

### 2.5 Policy、Constraint、Gate、Validator

**課題：** 運用規則、個別制約、後続許可、判定主体を同義扱いすると、Fail Closedの適用点が曖昧になる。  

**目的：** PolicyからConstraint、Validator、Gate結果への関係を定義する。  

**対象：** Policy、Constraint、Gate、Deterministic Risk Validator、Budget Gate、Time Gate。

| 用語 | 概念種別 | 定義 | 他用語との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| Policy | 設定された規則集合 | Risk、Portfolio、Budget、Notification等の運用規則 | 個別Constraintを含み、未設定時はUNCONFIGUREDになり得る | Config、Validator | §4.0、§15A〜17A、§37B |
| Constraint | 制約 | Tradeや状態が満たすべき個別条件 | target等のSoft指標とmin/max等のHard条件を区別する | Allocation、Risk | §15B、§17A |
| Gate | 判定境界 | 後続処理の開始・継続を許可または拒否する | ValidatorはGate判断を生成する決定論的機構 | Risk、Budget、Paper開始 | §17A、§37B、§46〜47 |
| Deterministic Risk Validator | 判定機構・安全機構 | Trade、State、Policy、Evidenceを機械計算して結果を返す | 投資魅力度を判断せず、LLMから保護された境界を要する | Proposal、承認、発注前 | §17A |
| Budget Gate | Gate・安全機構 | estimated_max_costと各Budget階層をCall前に判定する | 費用観測だけでなく実行前Hard Gate | Model API Job | §37B |
| Time Gate | Gate・安全機構 | published_at / revision / vintageをsimulation_time以下へ制限する | LLM内部の未来知識までは除去できない | Historical validation | §39 |

### 2.6 Stage、Commit、Canonical State、Projection、Artifact

**課題：** 外部結果、正本更新、表示用派生物を同じArtifactとして扱うと、再実行や正本性を誤る。  

**目的：** 永続化段階とArtifactのAuthorityを区別する。  

**対象：** Durable Stage Result、Commit、Canonical State、Current Envelope、Projection、Artifact、Configuration、Runtime Identity。

| 用語 | 概念種別 | 定義 | 他用語との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| Durable Stage Result | 中間Artifact | 外部呼出し結果をCommit前に永続化したもの | Canonical Stateではなく、再開・再課金防止に用いる | External / Model Job | §2.5、§13.4 |
| Commit | Transaction結果 | 検証済み遷移を一つの原子的State versionとして確定する | 外部API副作用は同じRollback境界にない | Single Writer | §2.3、§13.2 |
| Canonical State | 正本Artifact | PortfolioとWorkflowの現在正本 | Projection、Markdown、Backup、会話履歴を正本にしない | `portfolio.json` | §4、§13 |
| Current Envelope | Canonical State構造 | 現在状態と復旧に必要な直近参照を持つ | 全履歴を無期限に埋め込まずarchiveを参照する | state / archive | §13.4 |
| Projection | 派生Artifact | Canonical Stateから再生成する表示・互換用データ | 独立更新しない | watchlist、queue、Markdown | §4、§13.2 |
| Artifact | 設計・運用成果物 | Identity、State、Log、Report、Validation record等 | 各ArtifactのAuthorityと正本性を区別する | Repository / Runtime | §4、§29、§46B |
| Configuration | 設定Artifact | 人が明示する動作規則の単一正本 | Status、State、Secret、Identityと分離する | `config.json` | §4.0 |
| Runtime Identity | Identity Artifact | logical instanceの不変なstate_id / environment / data_root_id等 | Deployment Identity、Run Identity、pathや設定値と分離する | Bootstrap / Binding | §4.0 |

### 2.7 相互関係の要点

**課題：** 個別定義だけでは、CommandからCommit、PolicyからGate、IncidentからNotificationまでの接続を読み違え得る。  

**目的：** 主要概念間の非同義関係と処理接続を明示する。  

**対象：** Approval、Command、Fact、Policy、Stage、Incident、Status、Role、責務、権限。

**関係：**
- Human ApprovalはProposalを対象とするCommandであり、OrderやExecution Factそのものではない。
- CommandはWriterへ状態変更を要求し、Factは現実として受領される。Fact取込はProposal Validatorで拒否しない。
- PolicyはConstraintを提供し、ValidatorがTradeへ適用し、Gate結果が後続処理を制御する。
- Stageは外部結果を保持し、Validate後のCommitがCanonical Stateを更新し、Projectionが人向け表示を作る。
- Incidentは問題の解決状態、Alertは通知対象、Notificationは配送試行であり、それぞれ独立して追跡する。
- User Statusは人の現在状態、human_capacityは導出値、Policy Modeは制約適用状態であり、同じ状態機械ではない。
- Role、責務、権限はそれぞれ位置付け、担当処理、許可操作であり、同義として扱わない。

**設計元位置：** §4〜5、§12〜13、§15B、§17A、§21〜25、§37B。

### 2.8 分析・Risk・市場概念

**課題：** 投資分析固有語を一般語の意味で解釈すると、探索集合、矛盾、仮説、Risk制約の役割を誤る。  

**目的：** 分析・Allocation・Risk・監視Dataの概念をSource上の役割で定義する。  

**対象：** Universe、Candidate Pool、Contradiction、Thesis、Allocation、Hard Risk Policy、Position Watch Minimum Data。

| 用語 | 概念種別 | Source上の意味 | 他概念との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| Universe | 対象集合 | 初期版で明示・固定する投資対象市場の銘柄母集団 | Candidate Poolや保有銘柄集合とは異なる | 一次Filter、複数探索枝 | §6.1 |
| Candidate Pool | Workflow上の対象集合 | 各探索枝が候補化した銘柄の和集合 | Universe全体ではなく、枝別状態と欠損理由を持つ | 独立分析の入力 | §6.3〜7 |
| Contradiction | 分析関係 | 分析枝間の矛盾または未解決Relation | 単なる負の評価や平均化結果ではない | 追加調査、Report | §8 |
| Thesis | 状態を持つJudgment | 投資理由とInvalidatorを伴う投資仮説 | Research、Proposal、Holdingとは別Entityでrevision履歴を持つ | Watch、Sell判断 | §5、§9、§17〜18 |
| Allocation | 処理 | 魅力度とPortfolio / Cash / Policy / Riskから取引量を決める | 「買うか」のAnalysisと分離する | Proposed Trade生成 | §19〜20 |
| Hard Risk Policy | Policy / Constraint集合 | 現物、Cash、Exposure、Bucket、Liquidity、Freshness、費用等の機械適用制約 | 銘柄魅力度を評価せず、Deterministic Risk Validatorが適用する | BUY / ADD / SELL / REDUCE Gate | §17A |
| Position Watch Minimum Data | Data集合 | Storage Critical時にも保有Positionの重大Risk監視へ必要な最小Market Data、必須Disclosure、Normalize / freshness判定 | Candidate / Discovery向けDataより優先保護する | Storage縮退 | §4.7 |

### 2.9 検証・実装概念

**課題：** Capability、Regression、MVS、PIT、CAS、Fail Closedを名称だけで扱うと、判定範囲を過大表示し得る。  

**目的：** 検証・実装上の中核概念と相互差異を定義する。  

**対象：** CV、RV、MVS、PIT、CAS、Fail Closed。

| 用語 | 概念種別 | Source上の意味 | 他概念との違い・関係 | 主な利用箇所 | 設計元位置 |
|---|---|---|---|---|---|
| CV | 検証種別 | Capability / Gate Verification | RVのような変更後回帰ではなく、実環境能力と契約成立を確認する | CV-00〜50 | §46B |
| RV | 検証種別 | 成立済みCapabilityを変更で壊していないことのRegression Verification | NOT_RUNをPASSとしない | RV-01〜35 | §46B |
| MVS | 実装・検証範囲 | BUYからSELL、全売却、restart復元までを通すMinimum Vertical Slice | 個別Component成功やSELL Proposal生成だけでは完了しない | RV-16 | §46C |
| PIT | Data品質 | simulation時点で利用可能だったpoint-in-time Data | 後日revisionや現在Universeを混入させない | Historical Validation | §37A、§39 |
| CAS | 永続化機構候補 | cloud Backendで要求するserver-side conditional write / compare-and-swap | LocalのOS / filesystem lock＋atomic replaceを単純read→writeへ弱めるものではない | 将来Backend | §13.2 |
| Fail Closed | 安全動作 | 必須Policy、Cost、Identity、Data等が成立しないとき後続の危険操作を許可しない | Fact受領まで拒否する意味ではない | Risk / Budget / Binding | §17A、§37B、§46E |

## 3. 設計の目的、前提、全体関係

**課題：** Design Source内の目的、前提、処理、保護機構が分散していると、設計全体の因果と閉ループを追跡しにくい。  

**目的：** 目的から実現手段までの関係と、中核処理の接続を一つの構造として示す。  

**対象：** Human-in-the-loop、投資判断閉ループ、Local-first運用、状態保全、検証、改善。

### 3.1 目的から実現手段への関係

**課題：** 目的と実現手段の対応が不明だと、個別機構が何を保護するか追跡できない。  

**目的：** 設計上の目的・問題を、その実現手段とSource位置へ接続する。  

**対象：** Human-in-the-loop、閉ループ、Local-first、状態保全、認知負荷、段階移行、改善。

| 設計要素 | 型 | 目的・問題 | 実現手段と関係 | 設計元位置 |
|---|---|---|---|---|
| Human-in-the-loop投資支援 | 目的・権限 | AIへの投資判断の丸投げを避け、人が最終判断とBroker操作を行う | ARGUSは探索、独立分析、矛盾抽出、具体的提案、監視、評価を行い、人は承認・拒否と実操作を行う | §1、§3、§10〜12、§43 |
| 投資判断閉ループ | 機能・処理 | 選定から結果評価までを分断しない | 銘柄選定→分析→提案→人間判断→約定事実受領→Portfolio更新→Watch→再評価→改善 | §1、§3、§6〜20 |
| Local-first継続運用 | 前提・方針 | PC停止、Sleep、Offline、外部API障害が通常発生する | Persistent Loop、Retryable Transactional Job、未Commit、再試行、復帰後Catch-upを通常経路にする | §2、§26〜27、§42A、§46E |
| 事実状態の保全 | 安全機構 | 中断、競合、Break、誤入力でPortfolio事実を破壊しない | Single Writer、Atomic Commit、immutable Fact、Correction/Supersede、Backup後の照合 | §4、§12〜13、§24.3、§34、§46.6 |
| 認知負荷の制御 | 要求 | 提案・通知が人の処理能力を超えない | User Status→human_capacity、Decision Queue、TTL、通知時間、重要度と優先度の分離 | §10、§21〜25、§46.3 |
| 検証後の段階移行 | 方針・制約 | Backtestだけで実資金へ移行しない | Quant Backtest、Model Historical Replay、Paper Tradingを区別し、実資金開始は別の人間判断とする | §38〜42、§47 |
| 承認付き改善 | 変更管理 | システムが自己正当化して目的や規則を変更することを防ぐ | Break Proposal→Decision Queue→Human Approval→試験→Version Activation。B4は新旧目的を並行測定 | §30〜35、§46A |

### 3.2 中核処理の接続

**課題：** Selectionから評価・改善までの順序と保護境界が分断されると、閉ループの欠落を見逃す。  

**目的：** 中核処理を入力、主体、出力、次処理、保護機構として接続する。  

**対象：** Candidate生成からVersion更新までの投資判断Lifecycle。

| 順序 | 権限主体 | 実行主体 | 入力 | 処理 | 出力・次の処理 | 主要な保護 |
|---:|---|---|---|---|---|---|
| 1 | ARGUS | Agent Runtime | Market / Historical Data、設定、前回状態 | 機械的Filterと複数探索枝で候補を作る | Candidate Pool | 枝別の欠損を0点化せず、共通除外を限定する |
| 2 | Agent / LLM | Agent Runtime | Candidate、凍結Evidence | 分析枝を論理的に隔離して一次評価する | 枝別分析結果 | 他枝の結論と統合Recommendationを一次入力にしない |
| 3 | Agent / LLM | Agent Runtime | 枝別分析結果 | Contradiction、反証、未解決点を抽出する | 統合Reportまたは追加調査 | 調査予算と停止条件。重大不足ではBUY / ADDを止める |
| 4 | ARGUS | Validator | Report、Portfolio、Policy、Cash、Risk | Allocation後に具体的Tradeを作り、Deterministic Risk Validatorへ渡す | VALIDATED Proposalまたは拒否・調整・情報不足 | 魅力度判断とHard Risk判定を分離する |
| 5 | ARGUS | Queue / Router | Proposal、TTL、valid_if、Validator結果 | Decision Queueで再評価、重複排除、優先順位、通知条件を処理する | Human-visible Proposal | 各Agentから直接通知しない |
| 6 | 人 | Human Interface | 具体的Tradeと反対理由 | APPROVE / REJECT / WATCH / REANALYZEを選ぶ | Human Command | 承認はproposal revisionとtrade_hashへ拘束する |
| 7 | ARGUS | 共有Service / Writer | ApprovalCommand、最新State、Policy、資源 | 再検証し、承認とexecution_slot / reservationを同一Commitで成立させる | AWAITING_SUBMISSION | 条件変化時は旧承認を流用しない |
| 8 | 人 | Broker system | 発注案内 | Brokerで売買操作する | Broker上の注文・約定 | ARGUSは初期版でBroker操作を行わない |
| 9 | ARGUS | Fact Ingress / Writer | 人がPasteしたBroker結果 | 原文永続化→Schema検査→Fact化→Atomic Commit | Portfolio、Cash、lot、Order、Audit更新 | TTL失効等を理由に確認済み実約定を拒否しない |
| 10 | ARGUS | Runner / Agent Runtime | 更新済みPortfolio、Event、Watch設定 | Position / Candidate / Market Watchと再分析 | HOLD / ADD / REDUCE / SELL等の新Proposal | Local停止中の監視は保証しない |
| 11 | ARGUS / 人 | Runner / Human Interface | Logs、Results、Costs、Human Load | 評価→Break Proposal→人の承認→再試験 | 新Versionまたは却下 | 過去Factと旧Objectiveを消さない |

**設計元位置：** §3、§6〜13、§17A、§18〜20、§24〜25、§27、§32〜36。

## 4. 権限主体、実行主体、処理責務、境界

**課題：** 提案・判断・状態更新・外部実行のAuthorityが曖昧になると、自動売買やWriter迂回が成立し得る。  

**目的：** 権限主体の許可操作と、Runtime / UI componentである実行主体の処理責務を分離し、Human-in-the-loopとSingle Writer境界を維持する。  

**対象：** 権限主体としての人、ARGUS、Broker、Agent / LLM、および実行主体としての固定Writer / Validator、Provider Adapter、CLI / Tray、Runner。

| 権限主体 | 実行主体 | 実行すること・処理責務 | 実行しないこと・権限境界 | 主な入出力 | 設計元位置 |
|---|---|---|---|---|---|
| 人 | Human Interface（CLI / Trayを含む） | 提案判断、Policy・費用・Break承認、Broker操作、結果Paste、Status変更、実資金開始判断 | 判断権限をARGUSへ丸投げしない。通常操作でCanonical JSONを直接編集しない | Proposal受領、Command・Fact提供 | §1、§10〜12、§21、§24.3、§34、§37A、§43、§47 |
| ARGUS | Runner | Loop、Due Check、Retry、Job起動、Lease・Queue等を運用する | Brokerで自動売買せず、二重Instanceで動かない | Job schedule→Run / Stage / State | §2、§4.3、§26 |
| ARGUS | 固定Reducer / Validator / Writer | 決定論的遷移、Schema・Policy検査、排他、版照合、Atomic Commitを行う | 投資魅力度を判断せず、Writerを迂回させない | Command / Fact→Canonical State | §13.2、§17A、§46B |
| ARGUS | Provider Adapter / ExternalServiceGateway | 外部Service呼出し、検証、Raw保存、Normalize、Stage保存を行う | Provider固有APIをBusiness Logicへ露出しない | Request→Raw / Normalized / Stage | §37A〜37B |
| Agent / LLM | Agent Runtime / Model Provider | 分析、Update Request、Proposal、Reviewを生成する | Canonical Stateを直接更新しない。Hard Risk PASSやHuman Approvalを自己付与しない | Evidence入力、判断候補出力 | §7〜9、§13.2、§17A、§30、§46B.1 |
| Broker | Broker system | 人の操作を受け、注文・約定・取消等の現実を成立させる | 初期版ではARGUSから直接操作されない | Human operation→Broker result | §2.3、§12〜13、§25、§43 |

### 4.1 明示的な境界

**課題：** 人・System・外部Service・Environment・Storage・Data種別の境界が暗黙だと、禁止された越境が起き得る。  

**目的：** 境界ごとの許可経路と制約を明示する。  

**対象：** Human/System、Provider、Commit、Dev/Runtime、TEST/PAPER/LIVE、Storage、Data、履歴境界。

| 境界 | 左側 | 右側 | 越境方法と制約 | 設計元位置 |
|---|---|---|---|---|
| 人／システム | 人の判断・承認・Broker操作 | ARGUSの提案・自動処理 | Proposal Viewとtyped Command / Fact。通知表示を承認とみなさない | §4.3、§11〜12、§24 |
| ARGUS／外部サービス | Domain / Application | Provider API / SDK / Schema | ExternalServiceGatewayとProvider Adapterのみ。Business Logicから直接呼ばない | §37A |
| 外部副作用／Local Commit | API利用コスト、外部応答 | Canonical State | Durable Stage、provenance、idempotency。外部副作用をRollback可能と仮定しない | §2.3、§2.5 |
| 開発／実行 | `InvestmentAgent-Dev` | `InvestmentAgent` Runtime | Runtime停止、Backup、手動Deploy、Schema確認。state/data/configを上書きしない | §4.1、§4.6 |
| TEST／PAPER／LIVE | 各環境のState/Data Root | 他環境 | 異なるstate_id / environment / marker。Mismatch時は起動・write拒否 | §4.1、§46B |
| 内蔵SSD／外付けData Root | 現在State、Runtime、recent backup | Raw / normalized / historical / archive | Storage Managerとmarker identityで接続。drive letterだけを信用しない | §4.1、§4.7 |
| 事実／観測／判断 | Facts | Observations / Judgments | Canonical Envelope内で領域分離し、導出値と事実を混同しない | §13.1 |
| Current State／履歴 | `state/portfolio.json` | append-only archive / stage | ID、hash、range、high-water markで参照し、Compactionで履歴を消さない | §13.4 |

## 5. Runtime、Transaction、復旧

**課題：** Local停止、外部副作用、並行更新、再試行が重なると、処理喪失・二重適用・重複課金が起き得る。  

**目的：** 中断を通常条件として扱い、JobとCanonical Commitを安全に再開・復旧できるRuntimeを成立させる。  

**対象：** Runner状態、Retryable Job、Clock、Catch-up、外部呼出しとLocal Commitの境界。

### 5.1 Runtime状態と状態遷移

**課題：** 初期化、通常実行、異常終了後の復旧、正常終了を混同すると、不明な正本での再開やCrashの状態化が起き得る。  

**目的：** Runtimeの通常系と異常終了後の起動時復旧を簡潔な状態機械として固定する。  

**対象：** Runnerの`INIT / RUNNING / RESUMING / END`状態。

| 状態 | Event・条件 | 処理 | 次状態 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|
| INIT | Identity・Binding・Schema・Lock検証成功、前回正常終了 | Runner lock取得、通常実行準備 | RUNNING | 正本不明等はFail Closedで起動失敗 | §4.2、§4.3 |
| INIT | 前回の正常終了を確認できない | 復旧対象を特定 | RESUMING | OS kill / crash自体は状態にしない | §4.2、§4.3 |
| RESUMING | lock、inbox、outbox、Stage、Commitの復旧・照合成功 | Due / Gap / Queueを再評価 | RUNNING | 復旧不能時はIncident化して起動失敗 | §4.2、§4.3、§13.2 |
| RUNNING | Exit要求 | 新規Job受付停止、実行中処理を安全点またはDurable Stageへ退避、flush、lock解放 | END | Crash時はENDへ遷移せず、次回INITで検出 | §4.3 |

### 5.2 Retryable Jobの処理

**課題：** 外部API成功後にLocal Commitが失敗すると、再実行時に外部呼出し・課金・副作用が重複し得る。  

**目的：** 外部副作用を再実行せず、保存済みStageから安全にJobを再開できるようにする。  

**対象：** 外部Data / Model APIを利用してCanonical Stateへ結果を反映するRetryable Job。

| No. | 権限主体 | 実行主体 | 入力・前提 | 処理責務 | 出力 | 次処理 | 失敗・例外 |
|---:|---|---|---|---|---|---|---|
| 1 | ARGUS | Runner | Wall Clock、last_success、scheduled_for、schedule rule | Dueを判定する | RUN対象または非対象 | 前処理 | Clock discontinuity時はDueを再評価 |
| 2 | ARGUS | 未確定 | Due Job | Relevance、Freshness、重複、Budget、Adapter状態を検査 | 実行許可または停止理由 | 外部呼出し | 不成立ならCallを開始しない |
| 3 | ARGUS | Gateway / Adapter | 許可済みrequest | External / Model APIを呼び、request_id、input/output hash、provider/model、usage、provenance付きStageを保存 | Durable Stage Result | Validate | transient failureはRetry分類へ |
| 4 | ARGUS | Validator / Writer | 検証済みStage | Writer lock取得、最新State再読込、決定論的遷移構築 | 新Envelope候補 | Commit | version競合時は再計算 |
| 5 | ARGUS | Writer | 新Envelope候補 | Schema・整合性検査、一時file、flush / fsync、Atomic Replace | Canonical Commit | Projection / outbox | Commit前停止はinbox / Stageから再開 |
| 6 | ARGUS | Projection / Router | Commit済みState | Projection、Markdown、outbox配送 | Human view / notification attempt | Job完了 | event_idで冪等再生成 |
| 7 | ARGUS | 未確定 | Retryable Error | Retry制御：burst retry→backoff＋jitter→上限時にRETRY_PENDING / next_retry_at | 次回再試行状態 | 次Cycle | MAX_RETRYで永久破棄しない |
| 8 | ARGUS | 未確定 | Schema、Policy、認証、quota等 | Failure分類：Non-Retryable stateを記録 | BLOCKED / CONFIG_REQUIRED / DATA_INVALID / POLICY_NOT_READY / BUDGET_OR_QUOTA_BLOCKED | 人または設定修復 | 無限Retryしない |

**復旧：** API成功後にLocal Commitだけが失敗した場合は同一input_hashのStageから再開し、再課金を避ける。Commit前停止はinbox再適用、Commit後ログ前停止はapplied_event_ids / outboxから再生成する。  

**設計元位置：** §2.2〜2.6、§13.2、§46E。

### 5.3 ClockとCatch-up

**課題：** Schedule時刻と経過時間を同じClockで扱うと、Sleepや時計変更後のDue判定を誤り得る。  

**目的：** Wall Clockとmonotonic clockの用途を分離し、復帰後Catch-upを成立させる。  

**対象：** Schedule、timeout、retry、clock discontinuity、last_success、cursor。

| 用途 | 時刻 | 規則 |
|---|---|---|
| Schedule、Due、Market calendar | timezone付きWall Clock、`Asia/Tokyo` | Sleep中の予定時刻通過を復帰後に検出する |
| wait、timeout、retry interval | monotonic clock | OS時計変更の影響を避ける |
| 時計・timezoneの大幅変更 | Wall Clock観測 | `CLOCK_DISCONTINUITY`を記録しDue Jobを再評価する |
| 停止期間の復帰 | `last_success` / cursor / inbox | RUN / REANALYZE / EXPIRE / MERGE / DROPをFreshnessとTTLにより決める |

**設計元位置：** §2.4、§2.6、§26、§42A。

## 6. Canonical State、データ、Commit

**課題：** Fact・Observation・Judgment・Workflowの混同、並行更新、途中停止により正本が破損し得る。  

**目的：** 事実を保存する単一正本と、再現可能で原子的な更新を成立させる。  

**対象：** Canonical Envelope、inbox、archive、Stage、Projection。

### 6.1 データ区分と利用関係

**課題：** Identity、設定、Status、Fact、Observation、Judgment、Workflow、Stage、Projectionを混在させると正本性を失う。  

**目的：** Dataごとの生成元、利用先、保持条件、更新Authorityを区別する。  

**対象：** RuntimeからAuditまでのCanonicalおよび派生Data。

| データ | 型 | 生成元 | 利用先 | 保持・制約 | 設計元位置 |
|---|---|---|---|---|---|
| Runtime Identity | 不変Identity Artifact | Setup / Bootstrap | Binding、起動 | state_id / environment / data_root_id等。path、Secret、Status、Domain Stateを入れない | §4.0 |
| Configuration | 設定 | 人の明示設定、Config Writer | Job、Policy、Budget、通知等 | `config.json`単一正本、version/hash、Job開始時immutable snapshot | §4.0 |
| User Status | 人の現在状態 | StatusChangeCommand | capacity、Queue、通知 | `user_status.json`、status_version、直接編集を通常操作にしない | §4.0、§21 |
| Facts | 事実データ | Broker結果、入出金、配当、税、手数料、Corporate Action、Correction | Portfolio、Cash、Position | 確認済み事実を拒否・破壊・過去へ上書きしない | §12〜13 |
| Observations | 観測データ | Provider Adapter | 分析、Risk、Watch | as_of / published / retrieved / source / revision / hashを保持 | §13.1、§29、§37A |
| Judgments | 判断データ | Agent、人 | Proposal、評価、監査 | immutable Decision、Thesis revision、Human Decision | §13.1、§29 |
| Workflow | 状態データ | Queue、Approval、Order、Reservation、Watch | 実行制御 | Proposal、Order、Incident等の独立状態を保持 | §5、§13.1 |
| Raw Data | 外部原本 | Provider Adapter | Normalize、監査 | 許諾範囲でimmutable保存 | §4.7、§37A |
| Normalized Data | Provider非依存データ | Provider Adapter | Selection / Analysis | provenanceからRawへ追跡可能 | §4.7、§37A |
| Durable Stage | 中間永続結果 | External / Model call | Validate / Commit再開 | 再課金・重複適用防止。Canonical Factとは区別 | §2.5、§13.4 |
| Audit / Decision Log | 監査Artifact | Canonical CommitからProjection | 人・別AIレビュー、評価 | Markdownは正本でなくProjection | §28〜30 |

### 6.2 Single Writer Commit

**課題：** 複数更新主体や途中停止は、version競合、部分書込み、二重適用を発生させ得る。  

**目的：** 最新Stateの再読込からAtomic Replaceまでを一つの決定論的Commit境界にする。  

**対象：** Fact / Commandの受領、Writer lock、検証、Envelope生成、Commit、Projection。

| 順序 | 入力・前提 | Writer処理 | 出力 | 失敗時 |
|---:|---|---|---|---|
| 1 | Durable inbox Factまたは一意request_idのCommand | 受領済みを確認 | 適用候補 | 原文を失わない |
| 2 | 共通Writer lock | lock内で最新正本再読込とexpected_state_version比較 | 競合判定 | Factは再読込・冪等適用、Commandは再計算 |
| 3 | 最新State、Policy、TTL、資源 | applied_event_ids、Schema、整合性を検査 | 新Envelope | 条件変化したCommandはSUPERSEDED / 再Proposal |
| 4 | 新Envelope | 一時ファイル書込、flush / fsync、Atomic Replace | 新commit_id / state_version | 旧版か新版の一方だけを正本にする |
| 5 | Commit済みState | Projection、Markdown、outbox配送 | 表示・通知 | 失敗してもCommit済みFactを巻き戻さない |

**設計元位置：** §13.2。

## 7. 投資探索、分析、提案

**課題：** 単一総合点や枝間の結論共有は、反証・欠損・異なる探索観点を消し得る。  

**目的：** 独立した探索・分析と矛盾保持を経て、根拠を追跡できる具体的Trade候補を作る。  

**対象：** Universe、Candidate、分析枝、Contradiction、Report、Allocation、Risk Gate。

### 7.1 探索と分析の構成

**課題：** 探索・分析の枝を早期統合すると、枝固有の欠損、反証、矛盾が失われ得る。  

**目的：** UniverseからReportまでの入力・規則・出力を分離し、分析根拠を追跡可能にする。  

**対象：** Universe、一次Filter、探索枝、分析枝、Contradiction Engine、投資Report。

| 段階 | 設計要素の型 | 入力 | 規則 | 出力 | 設計元位置 |
|---|---|---|---|---|---|
| Universe | 設定・前提 | 明示した対象市場 | 初期Universeを固定 | 選定母集団 | §6.1 |
| 一次Filter | 処理 | Universeと必要Data | 流動性不足、対象外商品等をLLMなしで除外。枝固有欠損を共通除外にしない | 枝別評価対象 | §6.2〜6.3 |
| 探索枝 | 構成・処理 | 枝別Data | Value / Growth / Change / Quality / Event / Contrarian / Themeを独立評価 | 候補の和集合、ELIGIBLE等の状態 | §6.3 |
| 分析枝 | 構成・処理 | Candidateと凍結Evidence | Fundamental / Valuation / Bull / Bear / Macro / Risk / Technical / Portfolio Fitを隔離 | branch_id、input hash、出力、未評価理由 | §7 |
| Contradiction Engine | 処理・安全機構 | 枝別分析 | 平均化せず矛盾・未解決Relationを抽出 | 追加調査またはUNRESOLVED | §8 |
| 投資Report | Artifact | 分析、矛盾、Thesis、Invalidator | Recommendation、Reason Weight、Confidence、Allocation、Exit条件を構造化 | Human / Allocation入力 | §9〜10 |

### 7.2 AllocationとHard Riskの関係

**課題：** 投資魅力度と取引量・Hard Risk判定を同じ判断へ混在させると、Policy制約を迂回し得る。  

**目的：** 「買うか」「いくら買うか」「機械制約を満たすか」を別処理として接続する。  

**対象：** Analysis、Allocation、具体的Trade、Deterministic Risk Validator。

| 処理・機能 | 入力・前提 | 操作・判定 | 出力・状態変化 |
|---|---|---|---|
| Analysis | 独立分析結果、矛盾、Evidence | 「買うか」を評価する | 投資判断と根拠 |
| Allocation | 投資判断、Portfolio State、Policy、Cash、Exposure、Correlation、Risk | 「いくら買うか」を決める。現金維持も有効な結果とする | account、instrument、side、quantity、order type、価格条件、期限、最大費用、Thesisを含む具体的Trade |

**判定：** Deterministic Risk Validatorは魅力度を判断せず、immutable proposed_trade、最新State、Policy、Evidence、評価時刻を入力し、`PASS / REJECT / ADJUST_REQUIRED / DATA_INSUFFICIENT`とconstraint別計算を返す。結果はtrade_hash、state_version、policy_hash、validator code hash、evidence hash、evaluated_atへ拘束される。  

**設計元位置：** §17A、§19〜20、§25。

### 7.3 Hard Risk制約とSELL例外

**課題：** BUYとSELLへ同じ制約適用を行うと、Risk縮小SELLを妨げるか、必要制約を免除し得る。  

**目的：** 制約ごとにBUY / ADDとSELL / REDUCEの適用差と例外を固定する。  

**対象：** Cash、数量、Exposure、Bucket、Liquidity、Freshness制約。

| 制約 | BUY / ADD | SELL / REDUCE | 例外・保護 |
|---|---|---|---|
| 口座・商品・数量・単位・承認一致 | 必須 | 必須 | 免除しない |
| Cash・費用・予約 | 最大支払額が自由Cash以下 | 費用照合し新規借入を作らない | 二重控除を避ける |
| 保有数量・空売り禁止 | 現物のみ | 未予約の売却可能数量以下 | 免除不可 |
| Position / Sector上限 | NORMALまたは承認済みMode | 25%→20%等の段階縮小を許容可能 | 一括回復を強制しない |
| Bucket min | NORMALまたは構築・回復規則 | 指定したRisk縮小SELLのmin割れを許容し記録 | LLMラベルだけで免除しない |
| Cash max | Policy準拠 | 現金化による超過でRisk縮小SELLを妨げない | 修復対象に残す |
| Liquidity min | 購入Gate | 低流動性保有の縮小を一律拒否しない | 執行可能性等は別途確認 |
| 鮮度・評価不能 | 不足ならDATA_INSUFFICIENT | 既知の数量減少と評価不能を分離 | 必要執行情報不足をPASSにしない |

**設計元位置：** §15B、§17A。

## 8. 人間状態、Queue、通知

**課題：** 人の処理能力、通知可能時間、Proposal validity、Incident解決状態を混同すると、通知過多または重大案件の消失が起き得る。  

**目的：** Human loadを制御しながら、Durableな判断・通知経路を維持する。  

**対象：** Status、Capacity、Queue、Incident、Alert、Notification。

### 8.1 User StatusとCapacity

**課題：** 人の状態とSystem内部capacityを同一視すると、人の意思に反する自動遷移や処理量制御が起き得る。  

**目的：** Human入力のStatusから内部capacityを一方向に導出し、通知・処理量を制御する。  

**対象：** `FREE / NORMAL / BUSY`、`LARGE / MEDIUM / SMALL`、BUSY Lease。

| User Status | 内部capacity | 主な処理 | 抑制する処理 |
|---|---|---|---|
| FREE | LARGE | 新規BUY、ADD、SELL、Allocation、Break、通常Watch | 特記なし |
| NORMAL | MEDIUM | Position Watch、有力Candidate、BUY / SELL、重要ADD、重大Break | 低優先提案 |
| BUSY | SMALL | Position Watch、重大Risk、Thesis崩壊、重大SELL、配当Core監視 | 新規探索、通常Break、通常Candidate通知 |

**規則：**
- User Statusは人だけが明示変更する。
- 期限付きBUSYは1時間、3時間、今日いっぱい、今週いっぱい、変更するまでを持ち、期限後はNORMALへ戻りFREEへ自動遷移しない。
- 「今週いっぱい」は日曜00:00開始〜土曜24:00終了、内部の排他的終了は次の日曜00:00である。
- 人の再設定とLease Jobが競合した場合、status_version不一致の自動遷移を捨て、人の最新操作を優先する。

**関係：** 通知可否、通知時間帯、priority、Overrideは§8.5〜8.7のNotification Policyに従い、本節では再定義しない。BUSYという理由だけで通常通知を即時配送せず、BUSY専用の重大Risk Email通知を新設しない。  

**設計元位置：** §21〜23。

### 8.2 Proposal再評価結果

**課題：** 復帰・配送前にProposalを再評価しないと、期限切れ・重複・条件変更済み判断を提示し得る。  

**目的：** Proposalの再評価結果と対応動作を区別する。  

**対象：** EXPIRED、REANALYZE、RERANK、MERGE、KEEP SILENT。

| 結果 | 判定条件 | 動作 | 履歴 |
|---|---|---|---|
| EXPIRED | TTL失効 | 配送・承認対象から外す | 監査履歴に残す |
| REANALYZE | 重要条件変更 | 再分析する | 旧Proposalとの関係を保持 |
| RERANK | 有効だが優先度再評価が必要 | Queue内順位を更新 | Proposalは維持 |
| MERGE | 実質的重複 | 重複を統合 | 元参照を保持 |
| KEEP SILENT | 実質変化なし | 通知を増やさず保持 | 記録を維持 |

### 8.3 Incident状態機械

**課題：** Proposalの失効や通知認知をIncident解決とみなすと、未解決問題が消失する。  

**目的：** 問題の検知、認知、解決、再通知をDurableな状態遷移として管理する。  

**対象：** IncidentのOPEN、ACKNOWLEDGED、RESOLVED状態。

| 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|
| 未生成 | 問題検知 | incident_id、dedup_key、review情報を記録 | OPEN | 必要ならProposal / Alert生成 | Proposal TTLとは独立 | §24.1 |
| OPEN | 人が認知 | acknowledged_atを記録 | ACKNOWLEDGED | 再通知規則を再評価 | 認知を承認・注文・解決とみなさない | §24.1 |
| OPEN / ACKNOWLEDGED | 対応不要の証拠と解決理由が成立 | resolved理由を記録 | RESOLVED | 関連Proposalを再評価 | Proposal失効だけでは遷移しない | §24.1 |
| OPEN / ACKNOWLEDGED | next_review_at到来、未応答P0 | Relevanceと再通知上限を検査 | 同状態 | Alert再投入可能 | 間隔未設定を無限通知にしない | §24.1 |

### 8.4 AlertとNotification配送状態

**課題：** Alert記録、配送成功、Human認知、問題解決を同一状態として扱うと対応状況を誤る。  

**目的：** 配送試行とHuman認知を独立して追跡する。  

**対象：** Alert / Notificationのcreated、delivered、acknowledged、resolved、UNKNOWN状態。

| 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|
| 未生成 | Alert対象Event | Durable Alert Queueへ記録 | created | Router対象になる | 表示自体を正本にしない | §24.0 |
| created | Window、Status、priorityが配送許可 | Adapterへnotification_id付き送信 | deliveredまたはUNKNOWN | delivered_at記録 | 送信直後停止で結果不明ならUNKNOWN | §24.2 |
| delivered | 人が`alert ack` | acknowledged_atを記録 | acknowledged | Incident認知へ接続可能 | Popup表示成功をACKにしない | §24.0〜24.2 |
| acknowledged | 解決条件成立 | resolved_atを記録 | resolved | Queue表示更新 | Human認知だけで自動解決しない | §24.0〜24.2 |
| UNKNOWN | 再確認・再試行条件成立 | 同一IDで再試行可能 | deliveredまたはUNKNOWN | 二重通知可能性を記録 | 外部配送のexactly-onceを保証しない | §24.2 |

### 8.5 Severity分類

**課題：** 事象の重大度から配送優先度を暗黙導出すると、InvestmentとSystemの通知境界を迂回し得る。  

**目的：** severityの意味と配送上の扱いを明示する。  

**対象：** INFO、WARNING、CRITICAL / SYSTEM、CRITICAL / INVESTMENT。

| severity / class | 意味・例 | 配送規則 |
|---|---|---|
| INFO | 完了、Status Maintenance | 通常Windowに従い独自配送機会を作らない |
| WARNING | Budget 85%、Adapter degraded、Backup failure、Storage growth | 通常Window。BUSY中は蓄積しCLI確認可能 |
| CRITICAL / SYSTEM | closed classのSystem障害 | Override ENABLED時だけBUSY / Windowを越えて即時Popup |
| CRITICAL / INVESTMENT | 保有銘柄の重大Incident | Investment P0 Policyに従い、System Overrideを使わない |

### 8.6 Priority分類

**課題：** Humanへ届ける優先度が不明だと、BUSY時の抑制と重大案件の保持を両立できない。  

**目的：** priorityごとの対象とBUSY時の扱いを固定する。  

**対象：** P0〜P3。

| priority | 対象 | BUSY時 |
|---|---|---|
| P0 | 既保有の重大Risk等 | 配送候補。ただしNotification Windowは§22に従う |
| P1 | 重要再評価 | Queueへ保持 |
| P2 | 通常投資機会 | Queueへ保持 |
| P3 | 改善・低優先判断 | Queueへ保持 |

**処理：** Relevance→Duplicate→TTL / Validity→Priority→User Status / Capacity→Notification time→Durable outbox→Human。  

**設計元位置：** §22〜24。

### 8.7 Notification WindowとOverride

**課題：** 通知時間とOverride対象が曖昧だと、Human設定の迂回または重大System障害の遅延が起き得る。  

**目的：** Status別WindowとInvestment / System Overrideの独立境界を定義する。  

**対象：** FREE / NORMAL / BUSYのWindow、Investment Emergency、System Critical。

| Status | 平日 | 土日 |
|---|---|---|
| FREE | 12:00以上13:00未満、17:30以上24:00未満 | 通知可 |
| NORMAL | 17:30以上24:00未満 | 通知可 |
| BUSY | 17:30以上24:00未満 | 通知可、P0のみ |

| Override | 初期状態 | 対象 | Window外の動作 | 禁止 | 設計元位置 |
|---|---|---|---|---|---|
| Investment Emergency | disabled | Investment P0 | Risk検知・記録・分析を続け、通知は17:30まで保持 | System Critical経路の利用 | §22 |
| System Critical | UNCONFIGURED→人がENABLED / DISABLEDを選択 | `CANONICAL_STATE_CORRUPTION`、`DATA_STORAGE_IDENTITY_MISMATCH`、`ENVIRONMENT_BINDING_MISMATCH`、`MIGRATION_REQUIRED`、`RUNNER_LOCK_RECOVERY_REQUIRED` | ENABLED時だけ即時通知可能 | closed class外のEventを迂回配送 | §22、§24.0 |

## 9. Proposal、承認、Order、Execution Fact

**課題：** 提案・承認・発注・約定事実を同一状態として扱うと、承認流用、二重資源確保、事実拒否が起き得る。  

**目的：** 各EntityとTransaction境界を分離し、承認とBroker現実を正しく関連付ける。  

**対象：** Proposal、ApprovalCommand、Order、reservation、Execution Fact。

### 9.1 Proposal状態

**課題：** Proposalの作成・検証・待機・承認・失効・置換を区別しないと、古い判断を発注へ流用し得る。  

**目的：** Proposal lifecycleの状態と主な遷移条件を定義する。  

**対象：** DRAFT、VALIDATED、QUEUED、APPROVED、REJECTED、EXPIRED、SUPERSEDED。

| 状態 | 意味 | 主な遷移条件 |
|---|---|---|
| DRAFT | 作成中 | 分析・Allocation結果から生成 |
| VALIDATED | Validator済み | PASS等とhash拘束成立 |
| QUEUED | Human判断待ち | Decision Queueへ登録 |
| APPROVED | 人が具体的revision / trade_hashを承認 | 最新State等の再検証とSlot / reservation同一Commit |
| REJECTED | 人が拒否 | REJECT Command |
| EXPIRED | TTLまたはvalid_if失効 | 配送前・発注前評価 |
| SUPERSEDED | 実質条件変更で置換 | 数量、価格、Policy等の変更 |

### 9.2 Order状態と予約

**課題：** 未解決OrderのSlotやreservationをTTL・停止だけで解放すると、同じ資源を別Tradeへ二重割当し得る。  

**目的：** Broker上の確定事実と整合するまでOrder状態と資源予約を保持する。  

**対象：** Order状態、execution_slot、BUY費用予約、SELL数量予約。

| 状態 | 意味 | 資源の扱い |
|---|---|---|
| AWAITING_SUBMISSION | 承認後、Broker未操作 | execution_slotとBUY最大支払額＋費用余裕またはSELL数量を保持 |
| ORDER_OPEN | Brokerへ発注済み | Slot・残予約を保持 |
| PARTIALLY_FILLED | 一部約定 | FactごとにPosition / Cash / 残予約更新 |
| CANCEL_PENDING | 取消依頼、未確定 | 予約を解放しない |
| FILLED | 全約定 | 累計数量照合後に終了処理 |
| CANCELLED / REJECTED | Broker確定 | 全約定累計と取消数量を照合して残予約解放 |
| UNKNOWN | 状況不明 | TTLや停止だけでSlot / reservationを解放しない |

**規則：**
- 全管理口座を通じ初回は未解決発注一件に直列化する。
- 別Tradeの分析・重大Risk監視、売買を要求しないHOLD / WATCH、Incident確認は継続する。

**設計元位置：** §5、§13.3、§25。

### 9.3 Execution Pasteの事実処理

**課題：** Brokerで成立した事実をProposalの有効性判定と混同すると、TTL失効やPolicy変更を理由に現実の約定を失い得る。  

**目的：** 事実受領とCompliance評価を分離し、PortfolioをBroker現実へ一致させる。  

**対象：** Broker結果原文、Execution Fact、Compliance Record、Reconciliation状態。

| No. | 権限主体 | 実行主体 | 入力・前提 | 処理責務 | 出力 | 次処理 | 失敗・例外 |
|---:|---|---|---|---|---|---|---|
| 1 | ARGUS | Fact Ingress | RUNNING中のBroker結果原文 | receipt_id、received_at、content hash付きでinboxへDurable保存 | 受領済み原文 | Parse / Validate | 非RUNNING時は実行可能状態でないErrorとして拒否する。通知時間外でもRUNNING中なら受領応答を返す |
| 2 | ARGUS | Parser / Validator | inbox原文 | account、instrument、side、quantity、price、currency、executed_at / timezone、broker IDsを決定論的検査 | 確認済みFact候補または照合待ち | Fact Commit | 矛盾・方向不明は推測しない |
| 3 | ARGUS | Canonical Writer | 確認済みExecution | Fact Eventへ変換しSingle Writer Commit | Portfolio / Cash / Order更新 | Compliance評価 | 重複IDは冪等化する |
| 4 | ARGUS | 未確定 | Factと元Proposal / Approval | Compliance処理：TTL、承認内容、発注条件との差を評価 | Compliance Record | 表示 | 逸脱しても確認済みFactを拒否しない |
| 5 | ARGUS | Human Interface | receipt / commit / reconciliation状態 | 受領済み、適用済み、照合待ちを区別 | 状態表示 | 必要時Reconciliation | 同値だけで別約定を重複扱いしない |

**規則：**
- 重複キーはbroker＋account_id＋broker_execution_idとし、部分約定は固有ID単位で扱う。IDなしは仮受領し、同値だけで別約定を自動重複扱いしない。
- Correction / Reversalは元Executionを参照する追加Eventとする。

**失敗時：** 矛盾・方向不明は`RECONCILIATION_REQUIRED`とし、推測適用しない。  

**設計元位置：** §12。

## 10. Portfolio Policy、役割、保持、売却

**課題：** 魅力度だけではPortfolio制約、Cash、役割配分、Thesis崩壊を扱えない。  

**目的：** Allocationと売却判断を明示Policyと決定論的制約へ接続する。  

**対象：** Role Bucket、Holding Horizon、Policy Mode、Stop条件。

### 10.1 Portfolio分類軸

**課題：** RoleとHorizonを一つの比率軸へ混在させると、lotの二重計上が起き得る。  

**目的：** Portfolioの役割分類と想定時間軸を独立した軸として示す。  

**対象：** Role BucketとHolding Horizon。

| 分類軸 | 値集合 | 意味 | 他軸との関係 | 設計元位置 |
|---|---|---|---|---|
| Role Bucket | INCOME / GROWTH / EVENT / DEFENSIVE / OTHER / CASH | Portfolio内の役割。網羅的・相互排他的 | Holding Horizonと足し合わせずlotを二重計上しない | §14〜15B |
| Holding Horizon | SHORT / MEDIUM / LONG / CORE | 想定時間軸 | 強制SELL状態ではなくRole Bucketと別軸 | §16 |

### 10.2 Policy状態

**課題：** 未設定Policyを0または無制限として扱うと、未承認Tradeが有効になり得る。  

**目的：** Policyの有効化と欠落時のFail Closed遷移を定義する。  

**対象：** Portfolio PolicyのUNCONFIGURED / ACTIVE状態。

| 対象 | 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| Portfolio Policy | UNCONFIGURED | 必須Bucket、target / min / max、評価規則等を人が設定しvalidation成功 | Policy hashを確定 | ACTIVE | 本番BUY / ADD Gate評価可能 | nullを0や無制限へ変換しない | §15A〜15B |
| Portfolio Policy | ACTIVE | 必須値欠落・不正変更 | Fail Closed | UNCONFIGUREDまたは変更拒否 | 本番BUY / ADD停止 | 実約定Fact取込は拒否しない | §15A〜17A |

### 10.3 Policy Mode

**課題：** 初期構築や違反回復を通常制約の場当たり的免除として扱うと、違反を恒久化し得る。  

**目的：** 一時的な構築・回復を明示条件と終了条件へ拘束する。  

**対象：** NORMAL、BOOTSTRAP、REPAIR。

| Mode | 適用場面 | 必須設定 | 許可範囲 | 禁止・終了条件 | 設計元位置 |
|---|---|---|---|---|---|
| NORMAL | 通常運用 | 有効Policy | 取引後に適用Hard制約を満たすTrade | Hard違反Tradeを許可しない | §15B |
| BOOTSTRAP | 初期Cashから段階構築 | constraint_id、開始値、許容幅、期限、進捗、終了条件 | 開始時列挙した未充足だけを段階解消 | LLMがその場でMode変更、期限時の基準reset | §15B |
| REPAIR | 価格・Fact等で生じた違反回復 | 同上 | 新規違反なし、既存違反非悪化、対象違反を厳密に減らすTrade | 無進捗取引を回復と呼ばない | §15B |

### 10.4 売却・再分析判定

**課題：** 売却判断を価格変化だけへ縮約すると、Thesis崩壊、Portfolio Risk、Opportunity Costを見落とす。  

**目的：** 売却・再分析の判定入力と次処理を種類別に分離する。  

**対象：** Thesis Stop、Risk Stop、Price Stop、Time / Opportunity Stop。

| 判定 | 判定入力 | 条件 | 結果・次処理 | 例外・禁止 | 設計元位置 |
|---|---|---|---|---|---|
| Thesis Stop | Thesis、Invalidator、Evidence | 購入理由崩壊 | 最優先のSELL / REDUCE再分析 | 事実を消さない | §17.1 |
| Risk Stop | Exposure、Sector、Correlation、上限 | Portfolio Risk増大 | 主にREDUCE候補 | Risk labelだけでHard制約免除不可 | §17.2、§17A |
| Price Stop | Price change | 例として-8% / day、-15% / 5 days | 強制再分析 | 価格だけで即SELLしない | §17.3 |
| Time / Opportunity Stop | Horizon、Thesis実現、代替機会 | 想定時間軸超過で未実現 | 資金継続価値を再評価 | Horizonを自動SELL期限にしない | §17.4 |

### 10.5 Policy Constraint

**前提：** `target`、`min / max`、Policy Modeは、Allocationと決定論的Validatorで異なる強制レベルを持つ。  

**課題：** targetとmin / max、通常運用と構築・回復を同じ強制条件として扱うと、AllocationまたはRecoveryが成立しない。  

**目的：** Soft target、Hard制約、BOOTSTRAP / REPAIR進捗条件を分離する。  

**対象：** Portfolio Policy、Policy Constraint、NORMAL / BOOTSTRAP / REPAIR Mode。

**定義：**
- `target`はAllocationが考慮するSoft値である。
- `min / max`は決定論的に適用するHard制約である。

**制約：**
- Policy有効化時に範囲、`min ≤ target ≤ max`、min合計≤1≤max合計、通貨、評価分母、手数料、買付単位、実行可能性を検査する。
- BOOTSTRAP / REPAIRはconstraint_id、開始値、許容幅、期限、進捗目標、終了条件を設定に持つ。
- REPAIR候補は、取引前に正常だった適用制約を新たに破らず、既存違反量を増やさず、対象違反の少なくとも一つを厳密に減らす。

**判定：** 資産ゼロまたは評価不能の場合は、ratio判定を成立と扱わない。  

**禁止：**
- LLMがその場でPolicy Modeを切り替えない。
- 非悪化だけの無進捗取引を回復と呼ばない。
- 期限到来時に基準値をリセットして未達を隠さない。

**設計元位置：** §15B。

## 11. Watch、Event、監視限界

**課題：** 保有・候補・市場を同じ周期で扱うこと、およびLocal停止中も監視できると誤認することは、重大Riskの見逃しや能力の過大表示につながる。  

**目的：** 監視対象別の優先度と、取得から通知までの観測可能なLatency境界を明示する。  

**対象：** Position Watch、Candidate Watch、Market Watch、Event、Latency区間。

| Watch | 対象 | 目的 | 周期・優先 | 終了・移行 |
|---|---|---|---|---|
| Position Watch | 保有銘柄 | Thesis、Invalidator、重大Event | 短周期・高優先 | 数量ゼロで終了し、必要ならCandidate Watchへ |
| Candidate Watch | 分析済み非保有銘柄 | 見送り理由解消、Valuation、新Event | Positionより低い | 候補状態に応じ更新 |
| Market Watch | 未候補市場全体 | 銘柄選定入口 | 定期Selection | Candidate化 |

**定義：** Event-drivenは取得済みEventを次の週次・月次まで待たずに処理する意味である。  

**留意点：**
- 外部Providerの即時PushやLocal停止中の監視を保証しない。
- Event処理順は§20.2で構造化する。

| Latency区間 | 起点→終点 | 独立して記録する理由 |
|---|---|---|
| 公開 | Event発生→Provider公開 | ARGUSが短縮できない |
| Provider更新 | 公開→Provider反映 | Provider plan / schedule依存 |
| Local availability | Provider反映→PC稼働 | Local-first制約 |
| Polling / acquisition | PC稼働→Data取得 | Watch周期・通信依存 |
| Analysis / Queue | 取得→Queue ready | 処理・Budget依存 |
| Notification window | Queue ready→delivery opportunity | Status / 時刻Policy依存 |
| Human / Market | delivery→response→market opportunity | 人と取引時間の外部条件 |

**設計元位置：** §18、§22.1、§27、§42A。

## 12. 外部サービス、Cost、Storage

**課題：** Provider固有依存、無断課金、外部障害、Storage誤Bindingは、Business Logicと正本を危険にする。  

**目的：** Gateway、Adapter、Budget、Identity、縮退順序により外部依存を統制する。  

**対象：** J-Quants、EDINET、Model API、News / Web Provider、Data Root。

### 12.1 外部サービス関係

**課題：** Providerごとの契約・Schema・障害を上位Logicが直接扱うと、依存差替えと共通Governanceが困難になる。  

**目的：** 外部Serviceの利用目的、境界、出力、障害・制約をProvider単位で明示する。  

**対象：** J-Quants、EDINET、TDnet有料API、Model API、News / Web Provider。

| サービス | 利用目的 | 境界 | 出力 | 障害・制約 | 設計元位置 |
|---|---|---|---|---|---|
| J-Quants | Structured Market / Financial Data | JQuantsProvider | Raw、Normalized、provenance | Freeは開発用、Paper前にHuman承認付きLight以上＋Capability PASS | §37A |
| EDINET API | 法定開示 | EDINETProvider | 原本、Normalized、provenance | Adapter CVとFreshness評価 | §37A |
| TDnet有料API | 対象外 | 利用しない | なし | 費用要件不一致。再導入はBreak＋Human Approval | §37A |
| OpenAI等Model API | 推論 | ModelProvider | Stage Result、usage、cost | Budget reservation、Paid Governance、Circuit Breaker | §37A〜37B |
| News / Web Provider | 将来のNews取得 | NewsProvider | Raw / normalized evidence | 後段導入、Provider未確定 | §37A |

**責務：**

| 実行主体（Component） | 入力・対象 | 責務 | 出力 | 境界・禁止 | 失敗時 |
|---|---|---|---|---|---|
| ExternalServiceGateway | Application / AgentからDomain Service Interfaceを経た外部Service要求 | enabled / configured、Human approval / paid-service policy、Secret、rate limit / retry / Circuit Breaker、cost / usage、Budget Gate / reservation、request_id / provenance / auditを共通管理する | Provider Adapterへ渡す統制済み要求、共通telemetry / audit | Business Logicから外部APIへ直接アクセスしない | Provider failureを正規化する |
| Provider Adapter | Provider固有endpoint、request、pagination、response | response validation、Raw保存、Canonical schemaへのNormalize、所定形式での保存を担う | `FetchResult`、provenance、Raw / Normalized Data | 上位AgentはProvider固有Responseを直接読まない | Provider固有失敗をGatewayで扱える形へ渡す |

**設計元位置：** §37A。

### 12.2 Paid ServiceとModel Budget

**前提：** Model API費用は観測指標だけでなく実行前Hard Gateとして扱い、有料Service全般をHuman Approval下に置く。  

**課題：** 課金条件・上限・Fallbackが暗黙だと、Human承認なしの費用Commitment拡大が起き得る。  

**目的：** 有料Serviceの有効化とModel Callを事前承認・Budget reservation・Hard Gateで統制する。  

**対象：** Paid Service Governance、Budget Policy、Model Call、Budget reservation。

**規則：**
- 新規有料Service、Free→Paid、Add-on、従量課金上限増額、有料Fallbackは明示Human Approvalなしに有効化しない。
- 本番相当のModel API JobはBudget Policyが`UNCONFIGURED`なら開始しない。
- P0 emergency reserveは本番開始前に有効・無効と金額または明示的な0を確定する。
- Catch-upは通常Runより前にCost Estimateを行い、dedup、freshness、relevanceをModel API call前に決定論的に評価する。
- 上限到達時も既取得Dataによる決定論的Risk checkは継続する。

**異常時処理：**

| 異常 | 判定・Error | 処理 |
|---|---|---|
| paidかつ有効なのにhuman_approval_refがない | Configuration Validation Error | 有料Serviceを開始しない |
| Pricing不明・上限見積不能 | `COST_ESTIMATE_UNAVAILABLE` | 対象Model Callを開始しない |
| いずれかのBudget階層を超過 | `BUDGET_EXCEEDED` | 対象Callを開始せず、新規探索・候補分析・通常Breakを停止する |

**禁止：**
- Correction経由で費用Commitment拡大の承認要件を迂回しない。
- 上限到達を理由に自動増額しない。
- 障害、Rate Limit、Budget不足を理由に有料Planへ自動Upgradeまたは有料ProviderへFallbackしない。

**判定：** per-call / per-job、per-run、daily、monthlyの全階層を実行前Hard Gateとし、estimated_max_costをreserveして実usageで精算する。  

**未確定事項：** 使用率閾値の候補は70% NOTICE、85% WARNING、95% CRITICAL、100% BUDGET_EXCEEDED。  

**設計元位置：** §24.3、§37A〜37B。

### 12.3 Storage Identityと縮退順序

**前提：** 大容量Data Root初期値は`L:\emori\InvestmentAgentData`。  

**課題：** drive letterだけのBindingや偶発的な容量枯渇は、別Diskへの誤書込みや重要Dataの先行喪失を招き得る。  

**目的：** marker identityを検証し、容量圧迫時に重要度順で安全に縮退する。  

**対象：** Data Root、marker、Environment Binding、Storage Pressure Degradation、Position Watch Minimum Data。

**規則：**
- `data_root_marker.json`のstate_id、data_root_id、environmentを照合する。
- drive letterだけでData Rootの同一性を判断しない。

**失敗時：** 不一致は`DATA_STORAGE_IDENTITY_MISMATCH`または`ENVIRONMENT_BINDING_MISMATCH`としてwriteを停止する。

| 縮退順序 | 対象 | 動作 |
|---:|---|---|
| 1 | News / optional raw、Historical expansion、Discovery bulk、non-critical report | 最初に停止 |
| 2 | Application Log、Candidate raw、non-critical archive / derived regeneration | Canonical情報より先に縮退。Application Logは保持量を有限にする |
| 3 | Canonical State、Human Decision / Correction / Execution Fact、Audit / Incident、Queue / reservation、recent local backup | 最後まで保護 |
| 4 | Position Watch Minimum Data | 重大Risk監視のため最後まで取得・Normalizeを優先 |
| 5 | Minimum Dataも保存不能 | `POSITION_WATCH_DATA_UNAVAILABLE`をInvestment P0 Incident化し、監視継続を装わない |

**Application Log境界：** 単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合はStorage Fail Closedを適用する。外付けData Rootに加え、内蔵SSD上のCanonical State、直近Backup、Application Logについてvolume free、directory usage、growthを監視する。警告閾値とApplication Logの具体的保持期間・cleanup方法は未確定である。

**設計元位置：** §4.1、§4.7。

## 13. 監査、評価、変更管理

**課題：** 判断根拠・版・時刻を追跡できないこと、および成績に合わせて目的や評価軸を変更することは、監査と比較可能性を失わせる。  

**目的：** Decision provenance、分離した評価軸、承認付きBreakを成立させる。  

**対象：** Log、評価、Counterfactual、B1〜B4、System Version。

### 13.1 Decision provenance

**課題：** 判断の入力版、Evidence、時刻、実行条件を追跡できないと、後日監査・再現・比較が成立しない。  

**目的：** Decision provenanceの構造と正本・Projection境界を示す。  

**対象：** Decision / Audit Record、Markdown Projection。

**規則：** URLだけを固定Evidenceとせず、MarkdownはCanonical Audit RecordからのProjectionとする。  

**留意点：** Decision provenanceの属性は§26.5で領域別に構造化する。  

**設計元位置：** §28〜29。

### 13.2 評価軸

**課題：** 投資成績、Agent精度、System Health、Cost、Counterfactualを混在させると、改善効果を誤認する。  

**目的：** 評価対象ごとの指標と混同禁止対象を分離する。  

**対象：** 投資、Agent / Branch、System、Cost、Counterfactual、Reason Weight。

| 評価対象 | 指標例 | 混同しない対象 |
|---|---|---|
| 投資成績 | Return、Drawdown、Volatility、Sharpe、Hit Rate、Income Yield | System Health |
| Agent / Branch | precision、Bull/Bear accuracy、Risk alert、false positive/negative、missed opportunity | Portfolio収益そのもの |
| System Health | Data acquisition、Watch completion、false alert、missed event、expired decision、cost、attention | 投資成果 |
| Cost | observed / estimated / unavailableのAI費用、人間作業時間 | 未取得値を0にしない |
| Counterfactual | BUYだけでなくREJECT / WATCH / 除外Sample | 結果を見た後の対象選び直し |
| Declared Reason Weight | 宣言寄与度と後続結果 | 確率・因果寄与・正式較正。N<30はdescriptive only |

**設計元位置：** §31、§31A、§36〜37。

### 13.3 BreakとVersion

**課題：** 変更階層、承認対象、Rollback境界が曖昧だと、Objectiveの自己正当化や事実履歴の巻戻しが起き得る。  

**目的：** Breakを影響範囲別に分類し、具体的diff・再承認・Version切替へ拘束する。  

**対象：** B1〜B4、Break Proposal、Human Approval、Rollback、System Version。

| Break | 対象 | 保護 |
|---|---|---|
| B1 Parameter | threshold、period、score、frequency | Human Approval、diff、試験 |
| B2 Component | Agent、Skill、Scanner、Watch module | 同上 |
| B3 Architecture | Workflow、Agent graph、System structure | 同上 |
| B4 Objective | Objective、評価関数、Risk / Return / Income / Human Load | 旧Objectiveを凍結保持し、新旧を並行測定後に再度Human Approval |

**データ：** すべてのBreak Proposalはchange_id、対象版、完全diff、変更後hash、理由、期待効果、影響Strategy、試験計画、rollbackを持つ。  

**規則：** 承認後にdiffまたは基準版が変われば再承認する。  

**境界：** RollbackはCode / Policy / 将来処理を対象とし、実約定、Cash、監査履歴を過去snapshotで上書きしない。  

**設計元位置：** §32〜35。

## 14. 検証、段階Gate、実装範囲

**課題：** 設計記述や自己申告を実測PASSと扱うこと、および部品試験だけで閉ループ完了と誤認することは、未成立Capabilityを運用へ進め得る。  

**目的：** 凍結基準によるCapability / Regression検証とMVS Gateを定義する。  

**対象：** CV、RV、MVS、Deferred Scope。

### 14.1 検証の型と権限

**課題：** 異なる検証種別を同じPASSとして扱うと、Capability、回帰、過去評価、運用評価の限界を誤認する。  

**目的：** 各検証の確認対象、判定制約、Authorityを分離する。  

**対象：** CV、RV、Quant Backtest、Model Historical Replay、Paper Trading、Live Readiness。

| 検証 | 目的 | 判定上の制約 | 設計元位置 |
|---|---|---|---|
| CV | Local能力・契約・Gateway・Storage等のCapability / Gate確認 | 事前固定Requirement、Input、Expected、Acceptance Criteriaで実測する | §46B |
| RV | 成立済みCapabilityを変更で壊していないことの回帰 | Core / Affected / FullをTest Strategyで定義。NOT_RUNはPASSでない | §46B Regression Verification Set |
| Quant Backtest | 決定論的数値Logic検証 | 未来Dataを完全遮断 | §38.1、§39 |
| Model Historical Replay | 過去時点Workflow / reasoning参考評価 | 学習済み未来知識を完全排除できず、純粋OOSと呼ばない | §38.2〜40 |
| Paper Trading | prospectiveな運用性能検証 | 実資金なし。執行規則を事前FreezeしSIMULATEDを付ける | §41〜42 |
| Live Readiness | 実資金開始可否の確認 | 設計確定と別。最終的に人が開始判断する | §47 |

**規則：**
- Acceptance Criteria / oracleを失敗結果に合わせて変更しない。
- Test Runはvalidation_baseline_hashを記録する。
- 実行中にbaselineが変わったTest RunはPASSに使わない。

**設計元位置：** §46B.1。

### 14.2 Minimum Vertical Slice

**課題：** 個別部品の成功だけでは、BUYから全売却、再起動復元までの閉ループ成立を証明できない。  

**目的：** 最小の投資枝でState、Human Approval、Fact、Watch、復旧を端から端まで検証する。  

**対象：** Value＋Change選定と最小分析枝によるVirtual Trade lifecycle。

| No. | 権限主体 | 実行主体 | 入力・前提 | 処理責務 | 出力 | 次処理 | 失敗・例外 |
|---:|---|---|---|---|---|---|---|
| 1 | Agent / LLM | Agent Runtime | Value＋Change Data | Selection / Analysis：Fundamental / Valuation / Bear / Riskを独立分析し矛盾抽出 | Candidate Report | Allocation | 枝欠損を否定評価にしない |
| 2 | ARGUS | Validator | Report、State、Policy | Allocation：具体的Tradeを作成しRisk判定、Queue登録 | Validated Proposal | Human Approval | Policy未設定等はFail Closed |
| 3 | 人 | Approval Service | Proposal | Human ApprovalとSlot / reservationを同一Commit | AWAITING_SUBMISSION | Virtual BUY | 競合時は旧承認を流用しない |
| 4 | ARGUS | Fact Ingress / Writer | BUY Paste | CommitしPosition、Cash、lot、Logを更新 | Holding OPEN | Position Watch | 重複Pasteを二重適用しない |
| 5 | Agent / LLM / 人 | Agent Runtime / Human Interface | Event、Thesis、Holding | Watch / Analysis：再評価→SELL Proposal→Validator→Queue→Approval | 承認済みSELL | Virtual SELL | Data不足を明示 |
| 6 | ARGUS | Fact Ingress / Writer | SELL Paste | Cash、cost basis、P/L、remaining quantity更新 | 更新済みHolding | Close判定 | 部分約定を保持 |
| 7 | ARGUS | Writer / Watch component | remaining quantity=0 | Holding CLOSED、Position Watch終了、必要なCandidate Watch、Slot解放 | Closed lifecycle | Restart検証 | Broker / reservation不整合を残さない |
| 8 | ARGUS | Runner / Recovery Service | 別Runまたはrestart | State、Cash、history、Queue、Watch、outboxを復元・照合 | 復元済みSystem | RV-16判定 | 不明時に空Stateを作らない |

**判定：** RV-16が完了試験であり、SELL Proposal生成だけでは完了しない。  

**設計元位置：** §46C。

### 14.3 初期対象外とDeferred

**課題：** 初期対象外と後段実装を区別しないと、禁止機能を先行実装するか、必要機能を設計から削除し得る。  

**目的：** 初期版で行わない機能とMVS後へ延期する機能を明示する。  

**対象：** 自動売買・常時稼働等の対象外と、追加分析枝・DB・Dashboard等のDeferred Scope。

**留意点：**
- 初期対象外はBroker API自動発注、完全自動投資、HFT、Scalping、intraday automatic stop、millisecond / second監視、常時稼働保証、初期Server / VPS、分散Agent、外部Message Queue、同期Storage上の複数Writer Canonical DB。
- Growth等の追加枝、Bull / Macro / Technical、B3 / B4自動化、統計的Reason Weight較正、DRIP、SQLite、Dashboard等は設計から削除せずMVS後へ延期する。

**設計元位置：** §42A、§46D、§48。

## 15. 未確定事項

**課題：** 未決の値・方式・Providerを確定設計として扱うと、Sourceにない前提が後工程へ固定される。  

**目的：** 確定範囲と未確定範囲を分離し、確定に必要なEvidenceまたはHuman判断を示す。  

**対象：** Runtime Identity、Backup世代、PIT Data、Provider、Policy値、Storage形式等の未確定事項。

### 15.1 Source内で未確定のまま保持する事項

**課題：** Source内のTBD、UNCONFIGURED、Provider候補を確定値として扱うと、未承認設計が固定される。  

**目的：** 未確定事項の現在状態と確定に必要なものを保持する。  

**対象：** Identity形式、Backup世代、PIT能力、Provider、Policy値、Storage方式等。

| 事項 | 状態 | 確定に必要なもの | 設計元位置 |
|---|---|---|---|
| Runtime Identityの物理filename、discovery、厳密型等 | 後続Contractで確定 | 専用Contract | §4.0、§4ファイル表 |
| 内蔵SSDのrecent backup世代数N | TBD | 運用設定・CV | §4.7 Backup Location |
| point-in-time historical dataの十分性 | 未確定 | Provider Capability Verification | §37A、§38〜39 |
| News / Web Provider | 将来Provider | 合法性、許諾、契約、Capability確認 | §37A |
| Strategyごとのrequired latency | 運用設定 | Strategy Policyと実測 | §22.1、§42A |
| 各Policy数値、Budget、通知、Retention等 | UNCONFIGURED | 人の明示設定 | §4.0、§15A〜17A、§22、§37B |
| SQLite / Parquet、Server移行 | 将来Break候補 | 容量・検索性能・可用性・Latencyの実測 | §4.7、§44〜45 |
| Reason Weightの正式較正方法 | 将来検討 | 十分なN、手法、交絡、多重比較設計 | §31A |
| System Critical Override | 初期UNCONFIGURED | Setup時のHuman選択 | §22 |
| Application Log保持期間 | 未確定 | 運用要件、容量実測、Human設定 | §28 |

## 16. 設計横断の保護関係

**課題：** 個別の安全機構だけを見ると、何をどの失敗から保護するかという横断関係が見えにくい。  

**目的：** 安全機構、保護対象、防止する失敗、関連設計要素を対応付ける。  

**対象：** Approval、Commit、Binding、Risk、Queue、Stage、Backup、Budget、Time Gate、Validation Integrity。

| 安全機構 | 保護対象 | 防止する失敗 | 関係する設計要素 | 設計元位置 |
|---|---|---|---|---|
| Human Approval | 資金、Policy、費用、System変更 | 無断売買・無断課金・自己変更 | Proposal、Paid Governance、Break | §1、§24.3、§34、§37A |
| Single Writer + Atomic Commit | Canonical State | 競合、部分書込、二重適用 | Fact / Command、Envelope、outbox | §13.2 |
| Environment Binding | TEST / PAPER / LIVE State/Data | cross-environment write | Runtime Identity、marker、Data Root | §4.1、§46B |
| Deterministic Risk Validator | Cash、Position、Hard Policy | LLMによるGate迂回 | Trade、Policy、State、Evidence | §17A |
| Decision Queue | Human attention、Proposal validity | 直接通知、期限切れ判断、通知Storm | Status、TTL、Incident、outbox | §21〜25 |
| Durable Stage | Costと再実行整合性 | API成功後Commit失敗の再課金 | Provider call、transaction | §2.5 |
| Correction / Supersede | 事実履歴とHuman input | 過去Record破壊、Broker現実の巻戻し | Decision、Execution、Budget | §24.3 |
| Backup + Reconciliation | Broker現実との一致 | 古いsnapshotからの危険な再開 | Restore、BUY / ADD Gate | §4.5 |
| Budget Gate | 費用上限 | 無制限Call、Catch-up暴発 | Model Provider、Job | §37B |
| Time Gate / vintage | Historical評価 | look-ahead、後日改訂値混入 | Backtest、Replay、Dataset | §38〜40 |
| Validation Integrity | 試験結果の信頼性 | 基準後付け、偽PASS | CV / RV、baseline、oracle | §46B.1 |

## 17. Configuration、Identity、Artifact

**課題：** Identity、Configuration、Status、State、Secret、Artifactを混在させると、誤Binding・権限逸脱・秘密漏洩が起き得る。  

**目的：** 各情報種別の正本、更新主体、保持内容、失敗動作を分離する。  

**対象：** Runtime Identity、Configuration、User / Domain / Runtime State、Secret、Runtime Artifact。

### 17.1 情報種別の分離規則

**課題：** 正本、更新主体、格納内容が異なる情報を同一Artifactへ置くと、変更権限と復旧条件が曖昧になる。  

**目的：** 情報種別ごとの正本・更新主体・包含範囲・失敗動作を固定する。  

**対象：** Runtime Identity、Configuration、User / Domain / Runtime State、Secret。

| 情報 | 正本 | 更新主体 | 含むもの | 含めないもの | 失敗時 | 設計元位置 |
|---|---|---|---|---|---|---|
| Runtime Identity | 物理形式は後続Contract | Bootstrap / 専用機構 | schema_version、state_id、environment、data_root_id、created_at候補 | path、drive letter、Budget、Secret、Status、Domain / Runtime State、plan tier、code path | 解決不能なら通常起動しない | §4.0 |
| Configuration | `config.json` | Config Writer | runtime、model、budget、notification、portfolio / risk policy、strategy、watch、selection、break、backup、archive | Secret値、User Status、Domain State | Schema・必須値不備はCONFIG_REQUIRED等 | §4.0 |
| User Status | `user_status.json` | Status Writer | status_version、status、changed_at、BUSY lease | Policy、Budget、Portfolio Fact | version競合時は古い自動遷移を破棄 | §4.0、§21 |
| Domain State | `portfolio.json` Envelope | Canonical State Writer | Fact、Observation、Judgment、Workflow、Commit support | 会話履歴、暗黙記憶 | 正本不明ならRECOVERY_REQUIRED | §4、§13 |
| Runtime State | Canonical runtime領域 / Projection | Runner / Writer | Run、Job、retry、lock等 | User Status、Runtime Identity | 復旧時にlatest Stateから再構成 | §4.0 |
| Secret | Environment Variable / OS-protected store | 使用Subsystem | API key等のSecret値 | project、config、log、evidence、report、backup | 漏出疑いでAdapter停止、SECURITY_INCIDENT | §4.4、§46E |

### 17.2 Runtime Foundation Bootstrapの責務順

**課題：** 起動時責務を一つの機構へ集約すると、Identity・Config・Bindingの失敗原因とAuthorityが曖昧になる。  

**目的：** 起動Subsystemの責務と呼出し順を固定し、typed failureを境界ごとに保持する。  

**対象：** Identity Document、Config Mechanism、Entry Resolution、Bootstrap Orchestrator。

| 順序 | Subsystem | 責務 | 明示的境界 | 設計元位置 |
|---:|---|---|---|---|
| 1 | `RUNTIME-IDENTITY-DOCUMENT` | logical instance identityを提供する | 可変Configurationやpathを格納しない | §4.0 |
| 2 | `RUNTIME-CONFIG-MECHANISM` | Configurationを読込・検証しsnapshot化する | Secret値解決は使用時Subsystem責務 | §4.0 |
| 3 | `RUNTIME-ENTRY-RESOLUTION` | 起動対象とBinding入力を解決する | environmentをdirectoryから推論しない | §4.0 |
| 4 | `RUNTIME-BOOTSTRAP-ORCHESTRATOR` | 各Subsystemを順序付け、Environment Binding APIを呼ぶ | startup tokenを永続write authorizationにしない | §4.0、§4.2 |

**規則：** typed failureはSubsystemごとに保持し、上位境界で既存startup outcome / Incidentへ写像する。  

**禁止：** 全Subsystem共通の巨大failure enumは新設しない。

### 17.3 Runtime Artifactと役割

**課題：** Runtime Artifactの正本性と派生性が不明だと、ProjectionやBackupを独立更新し得る。  

**目的：** Artifactごとの生成元、利用先、保持条件、不変条件を定義する。  

**対象：** SYSTEM.md、Canonical State、Projection、inbox、evidence、logs、reports、validation、archive、stage。

| Artifact / 領域 | 型 | 生成・更新元 | 利用先 | 保持条件・不変条件 | 設計元位置 |
|---|---|---|---|---|---|
| `SYSTEM.md` | 起動Artifact | 配備工程 | 人、Runner | 起動手順、正本、版、入口、復旧を示す | §4 |
| `portfolio.json` | Canonical State | Single Writer | 全Domain処理 | 一つのAtomic Commit単位 | §4、§13 |
| `watchlist.json` / `decision_queue.json` / `runtime_state.json` | Projection | Canonical Stateから再生成 | UI、互換利用 | 独立更新しない | §4 |
| `performance.json` | 派生結果 | 評価処理 | Report | 計算条件と参照Commitを持つ | §4、§36 |
| `inbox/` | Durable入力 | Fact ingress | Parser、Writer | 適用完了まで受領原文を保持 | §4、§12 |
| `evidence/` | 根拠Artifact | Provider / acquisition | Analysis、Audit | source、時刻、hash、許諾範囲原文 | §4、§29 |
| `logs/decisions`等 | Audit Projection | Commit records | 人、別AI | event_id / commit_idで重複排除し、Application Logで代替しない | §4、§28〜30 |
| `logs/application/YYYY-MM-DD/` | Application Log | 生成主体・Writer実装は未確定 | 運用・障害解析 | `Asia/Tokyo`境界のDaily rotation。Canonical情報より低優先で有限保持。単独書込失敗はCanonical処理を失敗させない。Secret / Credential / Token等を記録しない | §2.6、§4、§28 |
| `reports/` | Human-facing Artifact | Analysis / Evaluation | 人 | 正本ではない | §4、§9〜10 |
| `validation/` | 検証Artifact | Test process | Gate判断 | 計画、入力、期待、実測、Evidenceを分離 | §4、§46B |
| `archive/events` | append-only Fact履歴 | Compaction / Writer | Rebuild、Audit | hash / range / high-water mark | §13.4 |
| `archive/observations` | append-only観測履歴 | Acquisition / archive | Analysis、Replay | revision / vintageを保持 | §13.4、§39 |
| `archive/audit` | append-only監査履歴 | Commit | Review | 過去Recordを削除しない | §13.4 |
| `stage/` | Durable Stage | External / Model call | Validate、Commit再開 | request/input/output hashとusage | §2.5、§13.4 |

**定義：** Application LogはRuntime、Job、Adapter、Error等の運用・障害解析用記録であり、Canonical State、Fact、Event、Audit Recordとは別Artifactである。  

**規則：**
- Application Logは`Asia/Tokyo`の日付境界でDaily rotationし、日付単位で管理可能にする。
- Secret、Credential、Token、API key、Authorization header、未redactのdebug dumpを記録しない。
- Application LogをCanonical State、Fact、Event、Audit Recordの代替にせず、削除しても投資判断、状態、履歴等のCanonicalな設計情報を失わない。
- Application LogはCanonical State、Commit、Auditより低い保存優先度とし、有限の保持上限を持つ。単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合はStorage Fail Closedを適用する。
- TEST / PAPER / LIVEのRuntime IdentityおよびDevelopment / Runtimeの物理分離に従い、Application Logを相互に混在させない。

**未確定事項：**
- 生成主体、Writer責務、書込経路。
- retentionの具体的期間、およびcleanup / deletionの実行方法。
- crash直前のLog durability保証範囲。
- Runtime / Job / Adapter / Errorごとの最低限の識別情報。
- TEST / PAPER / LIVE間、およびDevelopment / Runtime間を分離する具体的なpartition / path方式。
- 既知の禁止対象以外に禁止またはmaskingする情報の範囲。
- filename、file format、schema、logging library。

### 17.4 Config Snapshot規則

**課題：** Job途中でConfigurationが変わると、同一Runの判断条件と費用上限を再現できない。  

**目的：** Job開始時snapshotと変更適用境界を固定する。  

**対象：** Config version/hash、運用中変更、Budget limit低下。

| 規則 | 対象 | 適用条件 | 必須動作 | 禁止動作 | 不成立時 | 設計元位置 |
|---|---|---|---|---|---|---|
| Job単位snapshot | 全Job | Job開始時 | 検証済みimmutable snapshotを取得し、Run / Stage / Decisionへversion/hashを記録 | 実行途中へ新Configを動的注入しない | Job開始を拒否またはCONFIG_REQUIRED | §4.0 |
| Config変更境界 | 運用中Job | 人がConfig変更 | 次Jobから有効化 | 実行中Jobの条件を暗黙変更しない | 旧snapshotで当該Job完了 | §4.0 |
| Limit低下 | Budget reservation | 新limitが既存reservation未満 | 既存予約を維持し新規reservation停止 | 既存予約を暗黙取消しない | `LIMIT_BELOW_EXISTING_RESERVATION`表示 | §4.0 |

## 18. CLI、Human Interface、日常運用

**課題：** CLI、Tray、Runnerが独自LogicやWriter経路を持つと、同じ操作で異なる検証・更新結果が生じ得る。  

**目的：** Human操作を共有Command / Service Layerへ統一し、非RUNNING時にもStatus、Help、System Statusの安全な操作入口を保つ。  

**対象：** Status、Budget、Proposal、Approval、Execution Paste、Alert、System操作。

### 18.1 Command入口と処理

**課題：** Human操作の入口とWriter / Serviceが不明確だと、検証経路の分岐や直接更新が起き得る。  

**目的：** 各Commandの入力、処理、出力、更新主体、失敗動作を固定する。  

**対象：** Help、Status、Budget、Proposal、Approval、Execution、Alert、System Command。

| Command群 | 権限主体 | 入力 | 処理 | 出力 | 実行主体（Writer / Service） | 失敗時 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| `help [command]` | 人 | 任意command名 | 利用可能操作と引数を表示 | Help | Shared Service | 不明commandを説明 | §4.3 |
| `status free/normal/busy ...` | 人 | Statusとlease preset | 絶対終了時刻計算、echo、version検査 | Status更新 | Status Writer | version conflict時は再読込 | §4.3、§21 |
| `budget status/review/set` | 人 | 閲覧または金額 | usage / reservation / remaining表示、変更検証 | Budget表示またはConfig変更 | Budget Service / Config Writer | 自動増額しない | §4.3、§37B |
| `proposals list/show` | 人 | proposal_id等 | QueueのHuman viewを表示 | Proposal detail | Decision Queue | 利用不能時は実行可能状態でないことを示す | §4.3 |
| Approval / Rejection | 人 | request_id、command_type、proposal revision、trade_hash等 | 最新State / Policy / TTL / Validator再検証 | 承認CommitまたはSUPERSEDED等 | Approval Service / Writer | 条件変化で旧承認を流用しない | §4.3、§25 |
| `execution paste` | 人 | Broker原文 / structured fields | RUNNING中だけinbox Durable保存後にFact parsing | receipt、適用状態 | Fact Ingress / Writer | 非RUNNING時は実行可能状態でないErrorとして拒否。不明・矛盾は照合待ち | §4.3、§12 |
| `alerts` / `alert ack` / `incidents` | 人 | ID等 | Durable Queue閲覧・認知記録 | 状態表示 | Alert / Incident Service | Popup表示をACKにしない | §4.3、§24 |
| `system status/version` | 人 | なし | Runtime / Service状態を集約 | System status | Shared Service | 観測不能をNOT_OBSERVABLEと表示 | §4.3、§29 |

**規則：**
- CLIは短命Process、Trayは常駐UI ProcessまたはRunner同居UIとできるが、どちらも共有Command / Service Layerを呼ぶ。
- 非RUNNING時でもStatus、Help、System Statusは利用可能にする。
- Execution PasteはRUNNING中だけ受け付け、非RUNNING時のDurable受領機構を要求しない。

**境界：** CLI / TrayはRunner lockを取得せず、各Writer lockを通る。  

**不変条件：** Tray停止はCanonical / Runner Stateを破壊しない。  

**設計元位置：** §4.3。

### 18.2 BUSY Lease入力の解決

**課題：** 相対的なBUSY指定と適用時刻を区別しないと、週境界やRunner停止後の状態遷移を誤り得る。  

**目的：** presetを絶対終了時刻へ解決し、契約時刻と実適用時刻を追跡する。  

**対象：** 1時間、3時間、今日、今週、変更するまでのBUSY Lease。

| 入力preset | `effective_until` | 期限後 | 規則 |
|---|---|---|---|
| 1時間 | 設定時刻＋1時間 | NORMAL | timezone付き排他的終了時刻 |
| 3時間 | 設定時刻＋3時間 | NORMAL | 同上 |
| 今日いっぱい | 翌日00:00 JST | NORMAL | CLIが絶対時刻をecho |
| 今週いっぱい | 次の日曜00:00 JST | NORMAL | 週は日曜00:00〜土曜24:00 |
| 変更するまで | null | 自動遷移なし | lease_type=`UNTIL_CHANGED` |

**規則：**
- Lease期限到達後の最初のRunner機会にStatus Transitionを適用し、契約上のeffective_untilと実applied_atを両方記録する。
- Status Maintenance通知は独自Windowを作らず、次の許可Windowへ相乗りする。

**設計元位置：** §21.1〜21.3。

## 19. 失敗、縮退、復旧

**課題：** Local停止、Provider障害、Storage不在、破損、入力矛盾は通常運用中に発生し、誤った継続や事実推測につながり得る。  

**目的：** 失敗分類から安全な停止・Retry・Reconciliationへ追跡可能にする。  

**対象：** Runtime、Adapter、State、Storage、Budget、Secret、Clock。

### 19.1 Failure / Recovery対応

**課題：** 異なる失敗を一律Retryまたは一律停止すると、無限Retry、危険継続、復旧不能が起き得る。  

**目的：** 失敗条件から状態、即時処理、復旧条件、人の関与までを追跡可能にする。  

**対象：** Network、Provider、Budget、Identity、State、Storage、Backup、Execution、Secret、Clockの失敗。

| 失敗 | 発生条件 | 影響対象 | 状態・分類 | Retry可否 | 即時処理 | 復旧条件・処理 | 人の関与 | 設計元位置 |
|---|---|---|---|---|---|---|---|---|
| transient network / timeout | 一時通信失敗 | 外部Job | Retryable | 可 | burst retry→backoff+jitter | next_retry_at後または次Cycle | 原則不要 | §2.5、§46E |
| HTTP 429 | rate limit | Provider Job | Retryable | 可 | Provider Retry-After優先 | Circuit状態とBudget再検査後再試行 | 原則不要 | §2.5 |
| Provider 5xx連続 | 外部障害 | Adapter利用Job | ADAPTER_DEGRADED | 可 | Circuit Breakerで一定時間通常Job停止 | next_allowed_at後にhealth再評価 | 継続時確認 | §2.5 |
| quota / billing不足 | 契約・費用不足 | 有料Job | BUDGET_OR_QUOTA_BLOCKED | 時間だけでは不可 | 新規Call停止 | Budget / 契約を人が解決 | 必須 | §2.5、§37B |
| invalid key / permission | 認証失敗 | Adapter | CONFIG_REQUIRED | 不可 | Adapter停止 | 人がSecret / permission修正 | 必須 | §2.5 |
| Schema / Policy不整合 | 検証失敗 | Job / State | DATA_INVALID / POLICY_NOT_READY | 無限Retry不可 | Commit・BUY/ADD等を停止 | 正しいData / Policyを用意 | 場合により必須 | §2.2、§17A |
| Runner lock不明 | lock ownerを機械確認不能 | Runner | RUNNER_LOCK_RECOVERY_REQUIRED | 自動奪取不可 | 二重起動拒否 | host / pid / start time / heartbeat確認 | 必須の場合あり | §2.5 |
| Canonical State不明・破損 | 最新正本を確定不能 | 全write | RECOVERY_REQUIRED / System Critical | 不可 | 空Portfolio生成禁止 | Backup、Commit、Broker照合 | 必須 | §4.2、§22 |
| Data Root不在 | HDD未接続・read/write不能 | Data acquisition | DATA_STORAGE_UNAVAILABLE | 復帰後可 | State / Status閲覧を可能範囲で継続、Freshness依存BUY/ADD停止 | 正しいStorage再接続、cursorからCatch-up | 必要時 | §4.7 |
| Storage identity不一致 | markerとexpected不一致 | write | DATA_STORAGE_IDENTITY_MISMATCH / ENVIRONMENT_BINDING_MISMATCH | 不可 | write停止、System Critical記録 | 正しいBindingを確認 | 必須 | §4.1、§22 |
| Storage不足 | warning / critical閾値到達 | Data保存 | STORAGE_WARNING / CRITICAL | 条件次第 | 定義済み縮退順序を適用 | 容量回復、Integrity確認 | Critical時確認 | §4.7 |
| Position Watch最小Data不能 | Minimum Datasetも保存不能 | 保有監視 | POSITION_WATCH_DATA_UNAVAILABLE、CRITICAL / P0 INVESTMENT | 復帰後可 | Incident化、監視継続を表示しない | Data取得・保存能力回復 | 通知規則に従う | §4.7 |
| Backup stale | 許容期間超過 | Recovery能力 | BACKUP_STALE Warning | 再作成可 | Local / externalを別評価 | 正常Backup成功 | 継続時確認 | §4.7 |
| Pre-submit Model再検証不能 | Budget / quota / provider障害 | 承認済みTrade | HOLD_FOR_REVALIDATION | hold期間内可 | DO NOT SUBMIT、Incident | hold_ttl内に再検証、超過時Expire＋予約解放 | 必要時 | §25.1 |
| Execution入力矛盾 | 実残高不整合・方向不明 | Portfolio適用 | RECONCILIATION_REQUIRED | 推測不可 | 原文保持、Commit保留 | Broker / account照合、Correction / missing Fact | 必須 | §12 |
| Restore | 古いsnapshot復元 | Canonical State | RESTORE_RECOVERY→RECONCILIATION_REQUIRED | 照合後 | BUY / ADD停止 | execution / cash / position照合、必要Fact追加 | 必須 | §4.5 |
| Secret漏出疑い | scan / log等で検知 | Adapter / credential | SECURITY_INCIDENT | 再利用不可 | 対象Adapter停止 | Human確認、Secret rotation等 | 必須 | §46E |
| Clock discontinuity | OS時刻・timezone大幅変化 | Due判定 | CLOCK_DISCONTINUITY | 再評価 | 記録 | Due Job再評価 | 原則不要 | §2.6 |

### 19.2 Backup / Restore処理

**課題：** 古いsnapshotをそのまま正本へ戻すと、Brokerで成立した実約定やCashとの差異を消し得る。  

**目的：** Restore後に必ずReconciliationを行い、確認済み差分をEventとして再Commitする。  

**対象：** Backup snapshot、Restore、Broker照合、Correction / missing Fact、通常運用復帰。

| 順序 | 権限主体 | 実行主体 | 前提・入力 | 処理責務 | 判定・状態変化 | 出力 | 失敗時 | 次処理 |
|---:|---|---|---|---|---|---|---|---|
| 1 | ARGUS | Backup Job | Canonical commit | commit_id、state_version、hash、版参照付きsnapshot作成 | Backup成功とCanonical Commit成功を分離 | recent / long-term snapshot | Secretを平文で含めない | freshness監視 |
| 2 | 人 | Recovery Service | 復元対象snapshot | 古いsnapshotを配置 | RESTORE_RECOVERY | 復旧State | 実約定を消したまま再開しない | Reconciliation |
| 3 | ARGUS | 未確定 | Broker / execution / cash / position | Reconciliation処理：現実とsnapshotを照合 | RECONCILIATION_REQUIRED | 差分 | 不明を推測しない | Correction / missing Fact |
| 4 | ARGUS | Writer | 確認済み差分 | EventとしてCommit | Reconciliation Complete | 整合State | 不整合残存時はBUY/ADD停止継続 | 通常運用 |

**規則：**
- 内蔵SSDは直近N世代（NはTBD）の復旧snapshot、外付けHDDは長期Backupを担う。
- `last_local_backup_at`と`last_external_backup_at`を別々に監視する。

**設計元位置：** §4.5、§4.7。

### 19.3 Safe Degradation規則

**課題：** 能力低下時に事実推測やstale BUY、予約解放、古いProposal配送を行うと、資金・State整合性を損なう。  

**目的：** 能力不足時に維持する安全動作と禁止動作を固定する。  

**対象：** Fact適用、BUY / ADD、Order reservation、Catch-up。

| 規則 | 対象 | 適用条件 | 必須動作 | 禁止動作 | 例外 | 不成立時 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| 事実非推測 | Portfolio | Local failure全般 | 確認済みFactだけを適用 | 推測更新、未確認Executionを約定済み扱い | なし | RECONCILIATION_REQUIRED | §46E |
| stale BUY抑止 | BUY / ADD | Freshness不足 | 提案停止または再評価待ち | stale dataで有効化 | SELLは必要情報と既知数量を分離評価 | DATA_INSUFFICIENT | §4.7、§46E |
| 未解決Order保全 | Slot / reservation | 障害復旧、UNKNOWN | 予約・Slotを保持 | 停止やTTLだけで解放 | hold_ttl規則が明示されたpre-submitのみ | Incident / Human確認 | §13.3、§46E |
| Catch-up再評価 | 遅延Job | 復帰時 | freshness、relevance、TTL、dedupをModel call前に評価 | 古いProposal一斉通知 | なし | DROP / MERGE / EXPIRE等 | §2.4、§46E |

## 20. 定期処理、Event処理、評価時刻

**課題：** 周期JobとEvent処理の時刻・順序・再開条件が曖昧だと、欠落、古い分析、即時性の過大表示が起き得る。  

**目的：** 定期処理とEvent処理の入力、出力、失敗・復旧、次処理を明示する。  

**対象：** Daily / Weekly / Monthly / Quarterly Job、Event取得、Watch、再分析、Queue。

### 20.1 定期Job

**課題：** 周期、入力、出力、失敗時の扱いが不明確だと、停止期間の欠落や古い処理結果を隠し得る。  

**目的：** 周期別Jobの役割と、復帰後に再評価するためのRun記録を固定する。  

**対象：** Daily、Weekly、Monthly、Quarterly Job。

| 周期 | Job | 主入力 | 出力 | 失敗・復旧 | 設計元位置 |
|---|---|---|---|---|---|
| Daily | Position Watch、Significant Event Check | Holding、Thesis、Provider Data | Incident / Proposal / Log | Gap記録、復帰後Catch-up | §26 |
| Weekly | Candidate Watch、Portfolio Review | Candidate、Portfolio、Policy | 再分析・Allocation候補 | Relevance再評価 | §26 |
| Monthly | Stock Selection、Performance Report、System Health Report | Universe、Result、Run telemetry | Candidate、Report | 未取得期間を隠さない | §26 |
| Quarterly | Architecture-level Break | Logs、評価、制約 | B3等のProposal | Human Approval必須 | §26、§32〜34 |

**規則：**
- 各Runはscheduled_for、started_at、finished_at、statusを保存する。
- 頻度は運用結果に基づくBreakで変更する。

### 20.2 Event処理

**課題：** Event取得、Thesis差分、再分析、通知を一段階として扱うと、Data不足やLatency境界を隠し得る。  

**目的：** EventからHuman判断候補までの処理順序と各段階の失敗動作を分離する。  

**対象：** Event、Adapter、Watch、Analysis、Decision Queue。

| 順序 | 権限主体 | 実行主体 | 前提・入力 | 処理責務 | 判定・状態変化 | 出力 | 失敗時 | 次処理 |
|---:|---|---|---|---|---|---|---|---|
| 1 | ARGUS | Adapter | Earnings、Disclosure、price move、news等 | Event / Evidence取得 | provenance検証 | Evidence Update | pollingなら遅延を記録 | Watch |
| 2 | ARGUS | Watch component | Evidence、Original Thesis | 差分比較 | unchanged / strengthened / weakened / invalidated | Thesis revision候補 | Data不足を明示 | 必要時Full Analysis |
| 3 | Agent / LLM | Agent Runtime | Eventと凍結Evidence | Analysis：独立分析・Contradiction | Recommendation生成可否 | ADD / HOLD / REDUCE / SELL候補 | 重大不足でBUY/ADD停止 | Allocation / Validator |
| 4 | ARGUS | Queue / Router | validated Proposal | Status / TTL / Window評価 | Human判断待ち | Human view | Event-drivenを即時Push保証としない | Human Decision |

**データ：** Eventの例はEarnings、TDnet由来情報、Major price move、Important news、Dividend cut、Guidance revision、Large shareholder change、Regulation change。  

**制約：** TDnet有料APIは利用せず、取得経路は未確定である。  

**設計元位置：** §27、§37A。

## 21. 検証体系と具体的Verification

**課題：** 各検証IDの確認対象が曖昧だと、未実施や部分成功を全体PASSへ昇格できる。  

**目的：** CVとRVの確認対象、不変条件、判定限界を明示する。  

**対象：** CV-00〜50とRV-01〜35。

### 21.1 Capability Verification

**課題：** 設計上の存在だけでCapability成立と判定すると、実環境の制約や失敗挙動を見逃す。  

**目的：** CVごとに確認対象、必須確認、判定上の注意を固定し、実測Evidenceで判定する。  

**対象：** CV-00〜50。

| ID | 検証対象 | 必須確認 | 判定上の注意 |
|---|---|---|---|
| CV-00 | Local host / path / permission / API設定 | Manifestへ対象環境を記録 | SecretをLogへ出さない |
| CV-01 | Loop / wait / Due / Sleep / Offline復帰 | 未実行検知とCatch-up | 常時監視の証明ではない |
| CV-02〜05 | Web、市場、J-Quants、EDINET、価格、決算資料 | 取得、鮮度、欠損 | TDnet有料APIは対象外 |
| CV-06 | 正本永続化 | 別Runから最新版取得 | 旧copyを正本化しない |
| CV-07 | Atomic State | 原子的・耐久的更新 | Windows / filesystem保証範囲を記録 |
| CV-08〜09 | Markdown / Queue / Incident | 永続化と再生成 | Projectionを正本にしない |
| CV-10〜11 | Notification | Adapter、時刻、Status制御 | 配送とACKを分離 |
| CV-12〜13 | 競合 | 排他、version conflict、再計算 | 同版からの同時更新を試す |
| CV-14 | Polling / cursor | Gap、取り逃し、Catch-up | 欠落を隠さない |
| CV-15 | Provenance | source、query、hash、Prompt、Code、Config | 後日追跡可能にする |
| CV-16A | Validator計算 | BOOTSTRAP / REPAIR / SELL例外 | 数値正当性 |
| CV-16B | Validator強制力 | 迂回・改変防止、Validation Integrity | 未確認ならHard Gate強制済みと表示しない |
| CV-17〜19 | PIT Data | delisted、historical universe、publication / revision | future leakageを検出 |
| CV-20 | 中断復旧 | write、通信、Sleep、kill、log、Order、restart | 二重適用なし |
| CV-21 | Retry分類 | MAX_RETRY後の次Cycle、冪等性 | 永久破棄しない |
| CV-22 | Human CLI | Approval / Reject / Paste / request_id / trade_hash / Slot Commit | 具体的Tradeへ拘束 |
| CV-23 | Budget Gate | job / run / daily / monthly、Catch-up、quota | 上限超過Callを開始しない |
| CV-24 | Secret / Privacy | 非出力、Allowlist / Denylist、redaction | debug dumpも検査 |
| CV-25 | Runner lock | 二重起動、stale、heartbeat | 安全確認なしに奪取しない |
| CV-26 | Durable Stage | Commit失敗後再利用 | 再課金回避 |
| CV-27 | Archive | rotation / compaction / rebuild | Current Envelope肥大化境界 |
| CV-28 | Restore | Reconciliation完了までBUY/ADD停止 | 古いFactで再開しない |
| CV-29 | Clock | wall / monotonic、Sleep、timezone | CLOCK_DISCONTINUITY |
| CV-30 | After-close | 翌営業日revalidation | Trade変更時再承認 |
| CV-31 | Windows | atomic replace / lock / kill recovery | Supported範囲をManifest化 |
| CV-32 | Status / Lease | Mapping、今日・週境界、NORMAL遷移 | FREEへ自動遷移しない |
| CV-33 | Status競合 | 人の再設定対Lease expiry | stale auto-transition拒否 |
| CV-34 | Pre-submit budget failure | HOLD、Incident、hold_ttl、release | 不完全再検証で発注しない |
| CV-35 | Alert | Queue、Popup、ACK、restart、Window | Maintenance相乗り |
| CV-36 | CLI | help / status / budget / system、絶対時刻echo | Command暗記を前提にしない |
| CV-37 | External Data Storage | 接続・切断・再接続、容量警告 | 復帰後Catch-up |
| CV-38 | Dev / Runtime分離 | 手動Deploy、Schema、state/data非上書き | Runtime停止後に更新 |
| CV-39 | Raw / Normalized | provenance、JSONL、原本、再生成 | Raw immutable |
| CV-40 | Runner Lifecycle | INIT→RUNNING→END、異常終了後INIT→RESUMING→RUNNING、Graceful Exit | Crashを状態にせず次回起動で復旧 |
| CV-41 | Shared Service | 非RUNNING時Status / Help / System Status、Execution Paste拒否、同一Validator / Writer | CLI / Tray / Runner分岐なし |
| CV-42 | Severity / Priority | closed class、Override三状態、dedup | Investment Event迂回禁止 |
| CV-43 | Config Snapshot | Job境界、hash固定、limit低下 | 途中注入禁止 |
| CV-44 | Storage / Environment Identity | 別Disk同一L:、marker mismatch、復帰 | mismatch write拒否 |
| CV-45 | Paid Governance | approval欠如、upgrade / fallback、Correction | Commitment拡大は再承認 |
| CV-46 | Gateway | retry / cost / audit / errorとAdapter境界 | Business Logic直接依存禁止 |
| CV-47 | Backup / Pressure | local backup、stale、縮退順序、Minimum Data | Canonical / Audit保護 |
| CV-48 | J-Quants Free | auth、schema、raw / normalize、retry、bulk構造 | Operational能力をPASSにしない |
| CV-49 | J-Quants Light | coverage、update timing、bulk、rate limit、latency | Human契約承認後に実測 |
| CV-50 | Service Registry | expiry、auth、stale、freshness、health | HTTP成功だけでHealthyにしない |

**規則：** 各CVは実行前にrequirement、input、expected、acceptance criteria、環境、試行数を固定し、実行後にobserved、成功数、遅延分布、Evidence、PASS / PARTIAL / FAILを記録する。  

**留意点：** 未実施はNOT_RUNである。  

**設計元位置：** §46B〜46B.1。

### 21.2 Regression Verification

**前提：** RV-01〜35はMVS成立後のRegression Setである。  

**課題：** 変更後に成立済みCapabilityを再確認しないと、局所修正がState・Funds・Approval等の不変条件を破り得る。  

**目的：** 変更影響に応じたAffected / Core / Full回帰集合で不変条件を検証する。  

**対象：** RV-01〜35。

| ID群 | 主な検証対象 | 期待する不変条件 |
|---|---|---|
| RV-01〜02 | TTLとExecution、重複、部分約定、取消 | 確認済みFactを受領し、二重計上せず予約整合 |
| RV-03〜04 | 同版競合、中断位置 | 一方だけCommit、旧版か新版で復旧、Log再生成 |
| RV-05〜06 | Cash競合、条件変更 | A確保後B保留、古い承認を流用しない |
| RV-07〜08 | BOOTSTRAP / REPAIR / SELL | 進捗取引許可、段階縮小、空売り拒否 |
| RV-09〜10 | Binding、Validator迂回 | 空Portfolioを作らず、偽PASSを拒否 |
| RV-11〜16 | Cash保存則、通知、枝欠損、Time Gate、Change、MVS | Fact・State・評価・全売却復元の整合 |
| RV-17〜22 | Command冪等、Stage、Budget、Runner、Restore、翌朝再検証 | 二重取得・再課金・危険再開・承認流用なし |
| RV-23〜29 | BUSY、Status競合、pre-submit、Storage、Deploy、Budget段階 | 時刻境界、Human優先、安全縮退、自動増額なし |
| RV-30 | Decision Correction | 未発注ApprovalをSupersedeしreservation解放 |
| RV-31 | Fact Correction | 旧Factを消さずappendしCurrent State再計算 |
| RV-32 | System Critical Override | ENABLED即時、DISABLED Queue、storm抑止 |
| RV-33 | 長期Human不在 | PAUSE / STOP、再開後Catch-up / reconciliation |
| RV-34 | Environment分離 | state_id / marker mismatchでcross-write拒否 |
| RV-35 | Historical Provider | as_of_time以降Dataを返さない |

**規則：** 通常変更はAffected RVとCore RV、Release / Paper Gate / Runtime・Schema・Provider・Governance重要変更前はFull RVを実行する。  

**禁止：** NOT_RUNをPASSにしない。  

**設計元位置：** §46B Regression Verification Set。

## 22. Historical、Paper、Liveへの段階移行

**課題：** 未来情報、架空約定、短期間の結果を実資金性能の証明と誤認すると、未検証のRiskをLiveへ持ち込む。  

**目的：** 検証種別ごとの能力限界と、次段階へ進むGateを固定する。  

**対象：** Quant Backtest、Model Replay、Paper、Live Readiness。

### 22.1 Historical Dataの条件

**課題：** 後日改訂値、現在Universe、未来価格を過去時点へ混入すると、Historical評価が過大になる。  

**目的：** Simulation時点で利用可能だったDataだけを供給する条件を定義する。  

**対象：** Publication time、revision / vintage、Universe、price、Model knowledge。

| 制約 | 判定入力 | 成立条件 | 不成立時 | 設計理由 | 設計元位置 |
|---|---|---|---|---|---|
| Publication Time Gate | published_at、simulation_time | published_at≤simulation_time | Dataset不適合 | future data遮断 | §39 |
| Revision / vintage | Data revision | 当時利用可能版を供給 | PIT不適合と記録 | 後日修正値の遡及混入防止 | §39 |
| Universe | 当時構成、delisted | 当時の投資可能集合 | 評価範囲縮小・限界明示 | survivor bias防止 | §37A、§39 |
| Price | adjusted / actual | 用途を区別 | 架空Executionを生成しない | 分割調整価格と注文価格の混同防止 | §39、§41 |
| Model knowledge | Model snapshot | 完全遮断不能を明示 | Replayを完全OOSと呼ばない | 学習済み未来知識の限界 | §38.2〜40 |

### 22.2 Paper Execution規則

**課題：** 仮想約定規則を結果後に変更したり実取引と別更新経路にしたりすると、Paper評価の比較可能性が失われる。  

**目的：** Paper期間の資金境界、約定規則、Fact経路を事前固定し、投資性能証明ではなく運用性能を検証する。  

**対象：** 仮想予算、order、fee、tax、slippage、settlement、SIMULATED Execution。

| 規則 | 対象 | 適用条件 | 必須動作 | 禁止動作 | 不成立時 | 設計元位置 |
|---|---|---|---|---|---|---|
| 実資金禁止 | 1か月Paper | Paper期間 | 仮想予算で運用 | Broker実売買 | Gate FAIL | §41 |
| Execution事前Freeze | 仮想約定 | Paper開始前 | order、fee、tax、slippage、settlement規則を固定 | 結果に合わせ変更 | Run無効 | §41 |
| 指値約定 | limit order | 承認後の取引可能Data | 粒度、volume、partial fill規則で判定 | 日足high/low接触だけで全量約定 | 未約定または判定不能 | §41 |
| Fact経路共通化 | SIMULATED Execution | 約定判定成立 | 実約定と同じState更新経路を通す | 特別な直接更新 | 検証FAIL | §41 |

**留意点：** LONG / CORE、配当長期成果、稀Event、安定Sharpe / Drawdown、複数Break世代は1か月で十分評価できず、3 / 6 / 12か月へ継続観測する。  

**設計元位置：** §41〜42。

### 22.3 段階Gate

**課題：** 前段階の能力・契約・検証限界を満たさず次段階へ進むと、未成立条件をPaperまたはLiveへ持ち込む。  

**目的：** 各段階の前提、完了条件、次段階、決定権限を固定する。  

**対象：** Design、Runtime foundation、MVS、Historical、J-Quants Paper、1か月Paper、Live。

| 段階 | 前提 | 完了条件 | 次段階 | 権限 |
|---|---|---|---|---|
| Design Baseline | v0.1.7 Final Freeze | 設計・ADR・Test Strategy境界確定 | Account / API setup | Human review |
| Runtime foundation | 小規模実装 | CVの該当Capability PASS | MVS | Test oracle |
| MVS | CLI、Writer、Budget、Lock、Stage、Backup等 | RV-16でBUY→SELL→restart成立 | Branch expansion | 固定Gate |
| Historical | PIT Dataset、frozen rule | QuantとReplayを区別し限界記録 | Realtime Paper | Validation baseline |
| J-Quants Paper Gate | Free Adapter CV PASS、Human Light契約承認 | Light Capability CV PASS | Paper開始 | Human＋CV |
| 1か月Paper | frozen execution rule | 運用性能評価 | Continued Paper / Live Readiness | Gate review |
| Live | 必須Gate、Policy、Strategy適合 | 別途Human開始判断 | 小額実資金候補 | 人だけが決定 |

**設計元位置：** §37A、§40〜42、§46C、§47、§49。

## 23. 実装順序、Deployment、Version

**課題：** 分析機能を安全基盤より先に実装したり、DeploymentでState / Config / Dataを上書きしたりすると、検証不能なRuntimeが成立し得る。  

**目的：** Authority・Cost・State integrity・Recoveryを先行させ、停止・Backup・Schema確認を伴う配備順を固定する。  

**対象：** v0.1.7着手順、手動Deployment、Version lineage。

### 23.1 v0.1.7着手順

**課題：** 安全・費用・State基盤より投資分析を先行すると、成立条件を検証できない実装が積み上がる。  

**目的：** 依存関係に沿ってRuntime基盤から段階的に実装・確認する。  

**対象：** Design baseline、Runtime foundation、MVS、Historical、Paper、Live、Multi-branch expansion。

| 順序 | 実装・確認対象 | 依存理由 |
|---:|---|---|
| 0 | Design / ADR baseline、Test Strategy分離 | Authorityと試験基準を先に固定 |
| 1 | OpenAI、J-Quants Free、EDINET setup | 外部Capability準備 |
| 2 | Dev / Runtime / Test Data分離、Windows Manifest、Secret、Config Schema | Environment安全境界 |
| 3 | Shared Service、Status Writer、CLI status / help | Human操作入口 |
| 4 | Runner single instance、Lifecycle、clock、wait、Lease | Runtime基盤 |
| 5 | Writer lock、Atomic Commit、recovery、Config Snapshot、Correction | State integrity |
| 6 | Gateway、Paid Governance、Service Registry | 外部依存境界 |
| 7 | Stub Provider、Test Dataset Generator | 安全な試験入力 |
| 8 | Budget Gate、Usage、Review、Circuit Breaker | 費用・Retry制御 |
| 9 | Alert Queue、Severity / Priority、Override、Popup、ACK | Human通知経路 |
| 10 | Durable Stage、retry resume | 再課金・復旧 |
| 11 | External Storage、marker、growth、dual backup | Data保全 |
| 12 | J-Quants Free / EDINET Adapter CV | Provider構造確認 |
| 13 | CV fixture、frozen criteria | Validation Integrity |
| 14 | Risk Validator、Decision Queue | Trade安全Gate |
| 15 | Single-ticker slice、Historical Test | End-to-end MVS |
| 16 | Human承認でJ-Quants Light、Capability Verification | Paper Provider Gate |
| 17〜18 | Realtime Paper、Live Readiness | 運用実測後の判断 |
| 19 | Multi-branch expansion | 基盤成立後に拡張 |

**規則：** 投資分析Agentを先に増やさず、Human Approval、Cost、State integrity、Retry economyを先に閉じる。  

**設計元位置：** §49。

### 23.2 手動Deployment処理

**課題：** 稼働中更新や部分置換は、State破損、Schema不整合、復旧不能を引き起こし得る。  

**目的：** Runtime停止、Backup、Code置換、Schema確認を順序化して安全に配備する。  

**対象：** Dev code、Runtime code、Migration、Validation、Backup、Runtime process。

| 順序 | 権限主体 | 実行主体 | 前提・入力 | 処理責務 | 判定・状態変化 | 出力 | 失敗時 | 次処理 |
|---:|---|---|---|---|---|---|---|---|
| 1 | 人 | 未確定 | Dev code | 実装・試験 | Acceptance / CV判定 | 候補版 | FAILならDeployしない | Runtime停止 |
| 2 | 人 / ARGUS | Runner | RUNNING Runtime | Graceful Exit | END | lock解放 | crashなら次回起動時RESUMING | Backup |
| 3 | ARGUS | Backup Job | State / Config | Snapshot | 復旧可能性確認 | Backup | 失敗をCommit成功と混同しない | app置換 |
| 4 | 人 | Deployment mechanism（詳細未確定） | Runtime `app/` | Code置換 | State / Config / Data非上書き | 新app | 部分更新禁止 | Schema確認 |
| 5 | ARGUS | Migration / Validation component | Code要求Schema、State Schema | version照合、必要時Migration | MIGRATION_REQUIREDまたはvalid | Migration audit | 不一致ならRunner開始しない | Restart |

**規則：** SYSTEM_VERSION、CONFIG_SCHEMA_VERSION、STATE_SCHEMA_VERSIONを分離する。  

**留意点：** 自動download、self-replace、自動rollbackは初期必須ではない。  

**設計元位置：** §4.6。

### 23.3 Version管理

**課題：** 現行Baselineと過去の変更履歴を混同すると、旧要件を現行仕様として再導入し得る。  

**目的：** 現行仕様に必要なVersion管理規則だけを保持する。  

**対象：** 現行Design BaselineおよびCode / Schema / Policy / Data / Design version。

**規則：**
- Code / Schema / Policy / Data / DesignのVersionは別管理し、Run Manifestで対応付ける。
- v0.1.7以降のv0.1系列変更は実装で判明した契約欠陥修正を中心とし、新機能は原則v0.2系列で扱う。
- 過去Version、Prompt、Reviewの変更履歴はDesign Source §52の非NormativeなProvenanceであり、本Structured Design Dataには現行設計として取り込まない。

**設計元位置：** §49、§52、Final Freeze。

## 24. 設計理由と明示的禁止事項

**課題：** 結論と禁止事項だけを列挙すると、設計判断の原因、保護対象、例外境界を後工程が誤解し得る。  

**目的：** 問題から対策までの因果と、破ってはならない規則を追跡可能にする。  

**対象：** Local-first境界、Commit境界、Risk、Approval、Notification、Backup、Validation。

### 24.1 問題から対策への因果

**課題：** 採用機構だけでは、どの前提・失敗を防ぐ設計かを後工程が判断できない。  

**目的：** 問題、理由、方針、実現機構、保護対象の因果を保持する。  

**対象：** Runtime、API、Writer、Risk、Approval、Fact、通知、Backup、Data、Cost、Storage、Break、Validation。

| 問題・前提 | なぜ問題か | 採用方針 | 実現機構 | 防止・保護するもの | 設計元位置 |
|---|---|---|---|---|---|
| PCは常時稼働・Onlineではない | Schedule取り逃し、処理中断、古い判断が起きる | 停止・Sleep・Offlineを通常条件とする | Loop、last_success、Retry、Durable Stage、Catch-up | Job永久喪失、重複課金、stale Proposal | §2、§42A、§46E |
| 外部API副作用はLocalでRollback不能 | API costや外部処理とState Commitがずれる | StageとCommit境界を分ける | request_id、hash、idempotency、Stage再利用 | 重複Call、重複State適用 | §2.3、§2.5 |
| 複数WriterはJSON正本を破損し得る | version競合、部分書込、二重資源確保 | Single Writer＋Atomic Commit | OS lock、再読込、version check、fsync、atomic replace | Canonical integrity、Cash、reservation | §13.2 |
| 投資魅力度判断とHard Riskが同一LLMにある | Policy迂回や偽PASSが可能 | 決定論的Validatorを分離する | 固定code、hash拘束、CV-16A / B | 資金・Risk Policy | §17A |
| 承認と資源確保が別Commit | 同じCash / Positionを複数Tradeへ割当可能 | ApprovalとSlot / reservationを同一Commit | 初回一件直列＋Writer | 二重割当 | §13.3、§25 |
| PasteがProposal妥当性に従属すると現実を失う | TTL失効やPolicy変更後の実約定が消える | Fact ingressとProposal評価を分離する | inbox、Fact Event、Compliance Record | Broker現実とPortfolio一致 | §12 |
| BUSYは通知抑制で解除忘れが起きる | Sticky BUSYでQueueが長期滞留する | 期限付きLeaseとNORMAL復帰 | presets、effective_until、StatusLeaseJob | Human availabilityの誤固定 | §21 |
| Popup成功は人の認知ではない | 対応済みと誤判定する | DeliveryとACKを分離する | Durable Alert Queue、alert ack | Incident取り逃し | §24 |
| Backup復元はBroker現実を巻戻せない | 復元後Stateが実口座と乖離する | Restore後Reconciliation必須 | BUY/ADD停止、missing Fact / Correction | 危険な運用再開 | §4.5 |
| Historical Dataは後日改訂・survivor biasを含み得る | 過大なBacktest評価になる | PIT、revision、vintage、当時Universeを要求 | Time Gate、Dataset Manifest | look-ahead bias | §37A、§38〜40 |
| LLMの学習済み未来知識は遮断不能 | Replayを真のOOSと誤認する | QuantとModel Replayを分離し限界表示 | prospective Paperへ接続 | 不当な性能主張 | §38〜40 |
| 費用障害時の自動Paid fallback | 無断課金と依存増加になる | Paid GovernanceをHard Rule化 | approval_ref、Registry、Budget Gate | 費用Authority | §37A〜37B |
| Storage枯渇が偶然の順序で機能停止する | Stateや監視がRaw Dataより先に壊れ得る | 明示的縮退順序 | Stop first / Preserve last、Minimum Data | Canonical / Audit / Position Watch | §4.7 |
| Breakが評価軸を都合よく変更し得る | 成績悪化を評価変更で隠せる | B4を強く保護する | 旧Objective freeze、新旧並行、二段Human Approval | 評価の一貫性 | §33A |
| Test基準を実装結果へ合わせ得る | 偽PASSが成立する | baseline / oracleをRun前Freeze | hash、別Commit、Human Approval | Validation Integrity | §46B.1 |

### 24.2 明示的禁止規則

**課題：** 禁止境界が暗黙だと、便利な近道として自動売買、直接編集、複数Writer、無断課金等が導入され得る。  

**目的：** 安全性とAuthorityを守る禁止動作、必須動作、違反時の結果を固定する。  

**対象：** Broker操作、Fact、Canonical State、Writer、Secret、Policy、Slot、Approval、Budget、Historical Data、Break、Test、Override。

| 規則 | 対象 | 適用条件 | 必須動作 | 禁止動作 | 例外 | 違反・不成立時 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| Broker自動操作禁止 | ARGUS | 初期版 | 人へ具体的Tradeを提示 | Broker APIでBUY / SELL | 将来検討はBreak対象 | Scope違反 | §43、§48 |
| 確認済みFact拒否禁止 | Execution ingress | 実約定確認済み | Factを記録し逸脱を別記録 | TTL、未承認、Policy変更を理由に破棄 | なし | State integrity違反 | §12 |
| Canonical直接編集禁止 | Human I/F / Agent | 通常運用 | Command / Writer経路を通す | Portfolio表、JSON、Projectionの手修正 | 手編集はConfig保守非常手段のみ | Audit / version不成立 | §4.0、§11、§13.2 |
| 複数Writer禁止 | Canonical State | 全更新 | 共通lockとSingle Writer使用 | 同期Storage上で複数端末直接更新 | 同等CAS Backendへの将来移行 | Commit拒否 | §4.1、§13.2 |
| 空Portfolio生成禁止 | Startup | 正本不明 | Fail Closedの起動失敗 / Incident | 新規空Stateで継続 | なし | 起動停止 | §4.2 |
| Secret出力禁止 | Log / Evidence / Report / Backup | 常時 | redaction / Allowlist | key、Authorization header、debug dump保存 | なし | SECURITY_INCIDENT | §4.4 |
| 未設定値の暗黙変換禁止 | Policy / Budget | UNCONFIGURED / null | 明示設定を要求 | 0、無制限、推奨値へ自動変換 | 明示的0はPolicyが許す範囲 | Fail Closed | §15A〜17A、§37B |
| Slot自動解放禁止 | Order / reservation | TTL切れ、無応答、停止、UNKNOWN | Broker状態確認まで保持 | 時間経過だけで解放 | pre_submit_hold_ttlの明示規則 | Incident / Human確認 | §13.3、§25.1 |
| 承認流用禁止 | Proposal / Trade | revision、数量、価格、Policy等の実質変更 | 新Proposalと再承認 | 古いApprovalで発注 | valid_if内でTrade不変なら利用可 | SUPERSEDED | §25〜25.1 |
| 自動Budget増額禁止 | Agent / System | 上限到達 | Budget Reviewを提示 | limit増額、Paid upgrade / fallback | Human Commandのみ | BUDGET_EXCEEDED等 | §37A〜37B |
| 未来Data禁止 | Historical Provider | simulation | as_of以前だけ供給 | 現在株価、future Web、後日版混入 | LLM内部知識は限界表示 | Run不適合 | §38〜39 |
| BreakによるFact変更禁止 | Change / Rollback | 全Break | Code / Policy / 将来処理を変更 | Portfolio、実約定、Cash、Auditを過去へ上書き | 誤FactはCorrection Event | Change拒否 | §32〜34 |
| Test基準後付け禁止 | CV / RV | Test失敗後 | 別Commit・理由・承認で変更 | 同Run中にcriteriaを合わせる | なし | RunをPASSに使わない | §46B.1 |
| System Override迂回禁止 | Investment Event | 通知Window外 | Investment P0 Policyへ保持 | System Criticalに偽装 | closed class追加はChange Proposal | Configuration / Design違反 | §22、§24.0 |

## 25. 構造化品質Gate

**課題：** 表の存在や代表節の確認だけでは、無名文章、意味型混在、Source欠落を見逃し得る。  

**目的：** Structured Design Data全体をGate A〜Nで検証し、構造化完了の根拠を記録する。  

**対象：** Source複製、単独完全性、用語、共通Header、Process、State、表、意味型、関係、具体性、Authority、全節走査、Source照合。

### 25.1 Structured Design Data自身の状態

**課題：** 成果物の正本関係、構造化範囲、未確定事項、生成対象外が不明だと、後続工程がAuthorityを誤る。  

**目的：** Structured Design Data自身の変換状態と境界を明示する。  

**対象：** Source複製、用語、型、locator、Authority、未確定事項、Human System Design。

| 確認対象 | 結果 | 根拠 |
|---|---|---|
| Design Source本文複製 | なし | Source全文、付録、詳細層、連続章節コピーを含めていない |
| 用語・概念体系 | 作成済み | §2で主体、状態、Fact、Command、Workflow、Policy、Commit等を関係付き整理 |
| 型別構造 | 作成済み | 処理、状態、規則、制約、データ、主体、Service、Gate、Failure、Boundary、Verification、Changeを分離 |
| Source locator | 保持 | 各主要表・処理・規則に設計元位置を付与 |
| Authority / 責務 / 境界 | 変化なし | §4、§16、§24で明示 |
| 未確定事項 | 未確定のまま保持 | §15でTBD、UNCONFIGURED、候補、将来検討を分離 |
| Human System Design | 未生成 | 本書は構造化設計データで停止 |

### 25.2 Gate A〜R

**課題：** 現在の追加要件を不十分なGateだけで判定すると、派生ラベル、同一型反復、Prompt Artifactの不備を見逃す。  

**目的：** Structured Design DataとPrompt Artifactの完成条件をGate A〜Rで検証する。  

**対象：** 構造化、意味型、関係、Authority、Source照合、Prompt Artifact、変更範囲。

| Gate ID | Gate名 | Codex判定 | Codex確認結果 | 意思決定機構判定 | 指摘・根拠 |
|---|---|---|---|---|---|
| A | Source複製 | PASS | Source全文、大規模連続本文、Source本文を収容する層、付録を含めない | PENDING | Human Review待ち |
| B | 単独完全性 | PASS | Source本文コピーなしで用語、処理、状態、Data、Constraint、Failure、Verificationを取得できる | PENDING | Human Review待ち |
| C | 用語 | PASS | §2で分類軸を分け、Universe、Hard Risk、CV / RV / MVS / PIT等を使用前に定義した | PENDING | Human Review待ち |
| D | 前提・課題・目的・対象 | PASS | 設計内容を持つ章・節・小節で共通Headerを順序どおりに置き、前提はSourceにある場合だけ記載し、課題と目的を非同義に分離した | PENDING | Human Review待ち |
| E | 標準意味型 | PASS | 表外の設計文は標準語彙または明示承認された異常時処理でラベル付けした | PENDING | Human Review待ち |
| F | 同一意味型統合 | PASS | 同一節の同一意味型は単一ラベル配下の箇条書きまたは表へ統合した | PENDING | Human Review待ち |
| G | Process | PASS | 中核Lifecycle、Retryable Job、Execution Paste、MVS、Bootstrap、Event、Restore、Deployを処理表へ分解した | PENDING | Human Review待ち |
| H | State | PASS | Runtime、User Status、Policy、Research、Thesis、Proposal、Order、Holding、Incident、Notificationを対象別に分離した | PENDING | Human Review待ち |
| I | 表の意味 | PASS | 状態、分類、severity、priority等を別表とし、行集合・列属性を統一した | PENDING | Human Review待ち |
| J | 無名文章 | PASS | 表前後を含むすべての設計文へ意味型を明示した | PENDING | Human Review待ち |
| K | 型分離 | PASS | Gateway責務、Budget、Storage、Break、Version等を意味型ごとに分離した | PENDING | Human Review待ち |
| L | 関係 | PASS | 課題→目的→手段、I-P-O、状態遷移、Authority、Policy→Constraint、Failure→Recovery、Data producer / consumerを追跡可能にした | PENDING | Human Review待ち |
| M | 具体性 | PASS | 数値、時刻、閾値、例外、禁止、失敗動作、未確定、設計理由を保持した | PENDING | Human Review待ち |
| N | Authority | PASS | 人、ARGUS、LLM、Writer、Broker、外部Serviceの責務・権限・境界を維持した | PENDING | Human Review待ち |
| O | 全節走査 | PASS | 全見出しを個別に走査し、共通Header、同義反復、標準ラベル、同一型統合、Process、State、表後文章を確認した | PENDING | Human Review待ち |
| P | Source照合 | PASS | Sourceを先頭から最後まで意味照合し、欠落をSourceコピーでなく該当構造へ補完した | PENDING | Human Review待ち |
| Q | Prompt Artifact | REVIEW | 現存Transformation Promptは旧Structured Design Modelを出力対象とし、旧Prompt v0.1.4 / v0.1.5をNormativeに継承する。現在SDDのArtifact Role、意味型「異常時処理」、自己完結性との整合を現物から証明できない | PENDING | Prompt改版は今回の変更禁止範囲。Design Authority判断待ち |
| R | 変更範囲 | PASS | 今回はDesign SourceとStructured Design Dataだけを変更した | PENDING | Human Review待ち |

## 26. Domain状態機械と出力Schema

**課題：** Domain状態とHuman-facing出力のSchemaが自由文章だけだと、遷移・必須項目・関連Entityが曖昧になる。  

**目的：** Domain対象ごとの状態機械と、Report / Audit / Registry等の出力構造を明示する。  

**対象：** Research、Thesis、Holding、投資Report、Decision / Audit Record、Service Registry、Storage形式。

### 26.1 Research状態機械

**課題：** 発見、候補化、分析、監視、終了を一つの銘柄状態へ押し込むと、調査履歴と欠損理由が失われる。  

**目的：** Research lifecycleを独立状態機械として定義する。  

**対象：** DISCOVERED、CANDIDATE、ANALYZED、WATCH、ARCHIVED。

| 対象 | 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| Research | 未登録 | Universe / branch探索で発見 | sourceと枝別状態を記録 | DISCOVERED | Candidate評価対象 | 枝別欠損を否定評価にしない | §5〜7 |
| Research | DISCOVERED | Candidate条件成立 | 候補として登録 | CANDIDATE | Candidate Watch対象になり得る | DATA_INSUFFICIENTを0点化しない | §5〜7 |
| Research | CANDIDATE | 独立分析完了 | branch結果と矛盾を保存 | ANALYZED | Report / Proposal生成可能 | 未評価理由を保存 | §5、§7〜9 |
| Research | ANALYZED | 継続監視判断 | Watch登録 | WATCH | Candidate Watch | 売買承認とは扱わない | §5、§18 |
| Research | 任意 | 対象外・追跡終了 | 理由を記録 | ARCHIVED | Counterfactual sample対象になり得る | 履歴を削除しない | §5、§31 |

### 26.2 Thesis状態機械

**課題：** 投資仮説を上書きまたは二値化すると、弱化・失効・不明とEvidence履歴を区別できない。  

**目的：** Thesis revisionとEvidence変化を状態遷移として保持する。  

**対象：** VALID、WEAKENED、INVALIDATED、UNKNOWN。

| 対象 | 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| Thesis | 未作成 | Analysisで投資仮説成立 | revisionとして保存 | VALID | Invalidator / Event監視開始 | 旧revisionを上書きしない | §5、§9、§18 |
| Thesis | VALID | 反証・Eventが一部悪化 | Evidence比較と再分析 | WEAKENED | HOLD / REDUCE等の候補 | Data不足時はUNKNOWNを検討 | §17、§27 |
| Thesis | VALID / WEAKENED | 購入理由崩壊 | Thesis Stop判定 | INVALIDATED | 最優先のSELL / REDUCE再分析 | Priceだけで即SELLしない | §17.1、§27 |
| Thesis | 任意 | Evidence不足・矛盾未解決 | 不明状態を明示 | UNKNOWN | BUY / ADD停止になり得る | trueやVALIDへ推測しない | §5、§8、§17A |

### 26.3 Holding状態機械

**課題：** Holding状態をProposalやOrderから推測すると、部分約定や全売却後の監視終了を誤り得る。  

**目的：** 確認済みExecution Factと数量に基づくHolding遷移を定義する。  

**対象：** 未保有 / CLOSED、OPEN、partial SELL、全売却。

| 対象 | 前状態 | 事象・条件 | 処理 | 次状態 | 副作用 | 失敗・例外 | 設計元位置 |
|---|---|---|---|---|---|---|---|
| Holding | 未保有 / CLOSED | BUY Execution Fact適用後quantity>0 | Position / lot / Cash更新 | OPEN | Position Watch開始 | 未確認Executionでは遷移しない | §5、§12、§46C |
| Holding | OPEN | Partial SELL後quantity>0 | lot、Cash、P/L更新 | OPEN | Watch継続 | cumulative quantityを新規fill扱いしない | §12〜13、§46C |
| Holding | OPEN | SELL後quantity=0 | 全売却整合をCommit | CLOSED | Position Watch終了、必要ならCandidate Watch | Slot / reservation整合前に終了しない | §5、§13.3、§46C |

**定義：** lot / trancheはDecisionとThesisへ多対一で紐付き、同一銘柄には保有とCandidate、新旧Thesis、複数Decisionが併存できる。  

**規則：** 集計Positionはaccount_id＋instrument_id単位とする。  

**設計元位置：** §5。

### 26.4 Human-facing投資Report

**課題：** 分析結果を自由文章だけで提示すると、反証、Thesis、具体的Trade、Human選択肢が欠落し得る。  

**目的：** Human判断に必要なReport構造と必須内容を固定する。  

**対象：** Identity、Analysis、Contradiction、Thesis、Recommendation、Trade、Human view。

| 構造 | 必須内容 | 関係・制約 | 設計元位置 |
|---|---|---|---|
| Identity / State | Company / Ticker、Current State、Strategy Class、Expected Holding Horizon | 対象と時間軸を明示 | §9 |
| Analysis | Summary、Bull、Bear、Valuation、Macro、Risk、Technical、Portfolio Fit | 独立枝の結果を統合 | §7〜9 |
| Contradiction | Contradictions、Unresolved Questions | 平均化せず未解決を残す | §8〜9 |
| Thesis | Investment Thesis、Invalidators、Expected Events | Watch / Sell判断へ接続 | §9、§17〜18 |
| Recommendation | Recommendation、Declared Reason Weights、Confidence | Weightは確率・実測寄与でない | §9〜10、§31A |
| Trade | Suggested Allocation、Exit Conditions | 比率だけで承認を完了せず具体的Tradeへ接続 | §9、§19、§25 |
| Human view | 1行提案、理由weight、主な反対理由、選択肢 | 長文閲覧を必須にしない | §10 |

**規則：** Declared Reason Weightは合計100%の宣言寄与度として表示する。  

**留意点：** Source例は35%業績変曲点、25% Valuation、20%競合優位、12% Portfolio diversification、8% Technical / timingであるが、実運用固定比率ではない。  

**設計元位置：** §10.2、§29、§31A。

### 26.5 Decision / Audit Record

**課題：** 判断結果だけを保存すると、入力環境、時刻、Trigger、Evidence、Human Decision、欠損を追跡できない。  

**目的：** Decisionを再現・監査するための領域と保持項目を定義する。  

**対象：** Environment、Timing、Trigger、Data Provenance、Reasoning、Human / Execution、Missingness。

| 領域 | 保持項目 | 目的・制約 | 設計元位置 |
|---|---|---|---|
| Environment | system / design / schema version、model、Prompt / Rule version、code / policy / config hash、state / commit / snapshot ID | 判断時点の実行条件を追跡 | §29 |
| Timing | created、data cutoff、queue entered、notified、human decided、executed、received、committed | EventからCommitまでの遅延を分解 | §22.1、§29 |
| Trigger | Weekly Candidate Watch等 | 判断開始理由 | §29 |
| Data Provenance | source、retrieved_at、published_at、query、tool、content hash、revision / vintage、原文参照 | URLだけに依存しない | §29 |
| Reasoning output | Evidence、Bull、Bear、Contradiction、Thesis、Invalidator、Recommendation、Allocation、Weight、Confidence、Counterargument | 結論と根拠を監査 | §29〜30 |
| Human / Execution | Human Decision、approval_id、trade_hash、Execution ID、Broker Result、receipt_id | 提案・承認・Factを関連付ける | §29 |
| Missingness | 取得失敗、欠損、model snapshot NOT_OBSERVABLE | 不明を成功・0として扱わない | §29、§37 |

### 26.6 高配当CoreとAllocation例

**課題：** 将来目安例を確定Policyと誤認すると、未承認比率を本番制約へ固定し得る。  

**目的：** 高配当Core方針、評価観点、例示値、確定性を分離する。  

**対象：** Core目的、配分例、評価観点、調整、配当Cash、DRIP。

| 項目 | 設計内容 | 確定性 | 設計元位置 |
|---|---|---|---|
| Core目的 | 長期運用で高配当株を一定割合保持可能にする | 方針確定、比率未固定 | §15 |
| 将来目安例 | Core / Income 30%、Long Growth 20%、Medium 25%、Short / Event 10%、Cash 15% | 例であり本番Policy値ではない | §15 |
| 評価観点 | 配当利回り、持続性、FCF、配当性向、財務健全性、事業構造、減配Risk | 評価要素 | §15 |
| 調整 | Backtest / Paper / Breakで調整 | Human-approved change | §15、§34 |
| 配当Cash | 税引前、源泉税、実受領を分けCashへ戻す | Fact処理 | §13.1、§15A |
| DRIP | 初期必須でない | Deferred | §15A、§46D |

### 26.7 External Service Registry

**課題：** 契約、承認、期限、認証、鮮度、Healthを追跡できないと、失効Serviceやstale Dataを利用し得る。  

**目的：** 外部ServiceのLifecycleと運用状態を判定できるRegistry属性を定義する。  

**対象：** Service identity、plan、approval、時刻、接続、鮮度、health。

| 属性 | 意味 | 判定・利用 | 設計元位置 |
|---|---|---|---|
| service_id / provider | Service identity | Adapter / Gateway選択 | §4.0、§37A |
| plan_tier / paid / enabled | 契約・有効状態 | Paid GovernanceとConfiguration Validation | §4.0、§37A |
| human_approval_ref | 費用Authority根拠 | paid有効化時必須 | §37A |
| activated_at / renewal_or_expiry_at | Lifecycle時刻 | 期限接近・失効Warning | §4.0、§37A |
| last_successful_call_at / last_auth_success_at | 接続・認証観測 | 継続失敗と過期を区別 | §4.0、§37A |
| expected / observed_data_freshness | 鮮度契約と実測 | HTTP成功でもstaleならHealthyにしない | §4.0、§37A |
| health | Connectivity / Authentication / Contract / Freshness / Coverageの総合状態 | Warning / Incidentへ接続 | §4.0、§37A |

### 26.8 Storage容量と形式

**課題：** 容量目安、警告候補、保存形式を確定値として混同すると、不適切な閾値や形式を固定し得る。  

**目的：** Storageの既定値、候補値、監視量、形式、将来移行条件を区別する。  

**対象：** Data Root、2TB目安、1.8TB候補、usage / growth、Raw、JSONL、JSON、SQLite / Parquet。

| 項目 | 設計内容 | 状態・制約 | 設計元位置 |
|---|---|---|---|
| Data Root | `L:\emori\InvestmentAgentData` | 初期物理保存先。marker照合必須 | §4.1、§4.7 |
| 利用上限目安 | 最大約2TB | 必要容量見積・予約領域ではない | §4.1 |
| Soft Warning候補 | 約1.8TB | 候補値。最終thresholdはDataset実測後CVで設定 | §4.7 |
| 監視量 | absolute usage、volume free、directory usage、daily / weekly growth | Adapter暴走・Log loop検知 | §4.1 |
| Raw | Response、ZIP、XBRL、PDF等 | 原本または許諾形式でimmutable | §4.7 |
| Normalized time series | JSONL初期標準候補 | Provider非依存schemaとprovenance | §4.7、§37A |
| Small metadata | JSON許容 | 小容量単発Record | §4.7 |
| 将来形式 | SQLite / Parquet候補 | 容量・検索性能がbottleneck時にBreak | §4.7 |
