# ARGUS HSD Planning Artifact v0.1

- Artifact ID: `ARGUS-HSD-PLANNING-v0.1`
- Planning hash: `e3b59df6d6b4de9a41d3c329d3603f7d7e4bf675de92f42df841a27c1329d696`
- SDD SHA-256: `0acc60f6bff9ae27fea86310b0160e2b344e9671a795798feb763334ddeebf40`
- Approval: **PENDING**
- Stop: **STOP Human Review**

## Summary

- Section Context: 39
- Coverage Unit: 951
- Planning FAIL / WARNING / REVIEW_REQUIRED: 0 / 3 / 2
- Design reason sections / Premise sections: 2 / 7
- Semantic candidates / Confirmed states: 825 / 51
- Assignment REVIEW_REQUIRED: 114
- Diagram NEEDED / REVIEW / NOT_NEEDED: 9 / 3 / 27

## Section Overview

| ID | Section | P | Problem | Purpose | Reason | Exact | State | Candidate | Actor | Boundary | Coverage | Assignment Review | Owner | Diagram | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 0 | 設計環境 | 0 | 5 | 5 | 0 | 0 | 1 | 9 | 1 | 2 | 30 | 12 | Design Authority | NOT_NEEDED | REVIEW_REQUIRED |
| 1.1 | システムの目的 | 1 | 1 | 1 | 0 | 0 | 0 | 6 | 3 | 0 | 10 | 0 | システムの目的 | NOT_NEEDED | REVIEW_REQUIRED |
| 1.2 | 全体構成 | 0 | 2 | 2 | 15 | 0 | 2 | 20 | 2 | 0 | 21 | 3 | 全体構成 | REVIEW | REVIEW_REQUIRED |
| 1.3 | HumanとARGUSの役割分担 | 0 | 2 | 2 | 0 | 0 | 0 | 22 | 4 | 0 | 17 | 9 | Human / ARGUS | REVIEW | REVIEW_REQUIRED |
| 1.4 | 全体処理 | 0 | 2 | 2 | 0 | 0 | 0 | 17 | 4 | 0 | 20 | 0 | 全体処理 | NEEDED | REVIEW_REQUIRED |
| 2.1 | 候補探索 | 1 | 2 | 2 | 0 | 0 | 0 | 3 | 1 | 0 | 12 | 3 | Selection | NOT_NEEDED | REVIEW_REQUIRED |
| 2.2 | 分析・反証・判断材料 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 10 | 0 | Analysis | NOT_NEEDED | REVIEW_REQUIRED |
| 2.3 | 資金配分とリスク検証 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 7 | 0 | Risk Validator | NOT_NEEDED | REVIEW_REQUIRED |
| 2.4 | Humanの判断 | 0 | 3 | 3 | 0 | 0 | 1 | 21 | 2 | 0 | 24 | 3 | Human | NOT_NEEDED | REVIEW_REQUIRED |
| 2.5 | 売買と売買結果 | 0 | 2 | 2 | 0 | 0 | 2 | 23 | 3 | 0 | 23 | 0 | Execution Ingress | NEEDED | REVIEW_REQUIRED |
| 2.6 | ポートフォリオ管理 | 1 | 7 | 7 | 0 | 7 | 1 | 26 | 1 | 0 | 44 | 3 | Portfolio | NOT_NEEDED | REVIEW_REQUIRED |
| 2.7 | 監視と再評価 | 0 | 2 | 2 | 0 | 0 | 0 | 12 | 3 | 0 | 26 | 16 | Watch | NEEDED | REVIEW_REQUIRED |
| 3.1 | 起動 | 0 | 2 | 2 | 0 | 0 | 0 | 25 | 1 | 2 | 33 | 0 | Bootstrap | NOT_NEEDED | REVIEW_REQUIRED |
| 3.2 | 継続実行 | 0 | 4 | 4 | 0 | 0 | 0 | 17 | 2 | 1 | 27 | 6 | Runner | NEEDED | REVIEW_REQUIRED |
| 3.3 | 中断・再開 | 0 | 2 | 2 | 0 | 0 | 5 | 15 | 0 | 0 | 15 | 0 | Runner Recovery | NEEDED | REVIEW_REQUIRED |
| 3.4 | 状態とデータ | 0 | 8 | 8 | 0 | 0 | 5 | 59 | 2 | 1 | 73 | 3 | Canonical Writer | NEEDED | REVIEW_REQUIRED |
| 3.5 | 保存・バックアップ・復旧 | 0 | 3 | 3 | 0 | 4 | 0 | 23 | 3 | 1 | 40 | 0 | Storage Manager | NOT_NEEDED | REVIEW_REQUIRED |
| 3.6 | Deployment | 0 | 3 | 3 | 0 | 0 | 3 | 14 | 1 | 1 | 20 | 3 | Deployment | NOT_NEEDED | REVIEW_REQUIRED |
| 4.1 | 外部サービスとの境界 | 0 | 2 | 2 | 0 | 0 | 0 | 14 | 1 | 0 | 15 | 3 | ExternalServiceGateway | REVIEW | REVIEW_REQUIRED |
| 4.2 | Provider | 1 | 2 | 2 | 0 | 0 | 0 | 7 | 1 | 0 | 23 | 0 | Provider Adapter | NOT_NEEDED | REVIEW_REQUIRED |
| 4.3 | 費用・利用量 | 1 | 1 | 1 | 0 | 4 | 0 | 7 | 1 | 0 | 13 | 0 | Budget Gate | NOT_NEEDED | REVIEW_REQUIRED |
| 4.4 | 外部障害 | 0 | 2 | 2 | 0 | 0 | 0 | 30 | 2 | 0 | 24 | 3 | Failure Controller | NOT_NEEDED | REVIEW_REQUIRED |
| 5.1 | CLI / Human Interface | 0 | 3 | 3 | 0 | 10 | 3 | 19 | 2 | 0 | 28 | 3 | Human Interface | NOT_NEEDED | REVIEW_REQUIRED |
| 5.2 | Humanの対応状態 | 0 | 2 | 2 | 0 | 0 | 8 | 16 | 1 | 0 | 12 | 3 | Status Mapper | NEEDED | REVIEW_REQUIRED |
| 5.3 | 判断待ち | 0 | 1 | 1 | 0 | 0 | 0 | 13 | 0 | 0 | 8 | 0 | Decision Queue | NEEDED | REVIEW_REQUIRED |
| 5.4 | 通知 | 0 | 4 | 4 | 0 | 10 | 5 | 41 | 1 | 0 | 32 | 0 | Notification Router | NOT_NEEDED | REVIEW_REQUIRED |
| 5.5 | Incidentと復旧 | 0 | 1 | 1 | 0 | 0 | 4 | 11 | 0 | 0 | 7 | 0 | Incident Manager | NOT_NEEDED | REVIEW_REQUIRED |
| 6.1 | Fail Closed | 0 | 5 | 5 | 11 | 0 | 1 | 40 | 3 | 3 | 50 | 17 | Safety Gate | NOT_NEEDED | REVIEW_REQUIRED |
| 6.2 | TEST / PAPER / LIVE | 0 | 1 | 1 | 0 | 2 | 0 | 5 | 1 | 0 | 9 | 0 | Environment Binding | NOT_NEEDED | REVIEW_REQUIRED |
| 6.3 | 正本状態の保護 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 9 | 0 | Canonical Writer | NEEDED | REVIEW_REQUIRED |
| 6.4 | 投資リスク | 0 | 1 | 1 | 0 | 2 | 1 | 11 | 0 | 0 | 12 | 0 | Risk Validator | NOT_NEEDED | REVIEW_REQUIRED |
| 6.5 | Secret・データ保護 | 0 | 1 | 1 | 0 | 0 | 0 | 12 | 3 | 1 | 11 | 0 | Security Boundary | NOT_NEEDED | REVIEW_REQUIRED |
| 7.1 | 検証 | 2 | 6 | 6 | 0 | 0 | 7 | 182 | 3 | 5 | 97 | 6 | Verification | NOT_NEEDED | REVIEW_REQUIRED |
| 7.2 | Historical / PAPER / LIVE | 0 | 4 | 4 | 0 | 0 | 1 | 38 | 4 | 1 | 35 | 3 | Historical / PAPER / LIVE | NOT_NEEDED | REVIEW_REQUIRED |
| 7.3 | 判断結果の評価 | 0 | 3 | 3 | 0 | 0 | 0 | 7 | 0 | 0 | 19 | 3 | 判断結果の評価 | NOT_NEEDED | REVIEW_REQUIRED |
| 7.4 | 変更管理 | 1 | 3 | 3 | 0 | 0 | 1 | 36 | 1 | 1 | 37 | 0 | 変更管理 | NOT_NEEDED | REVIEW_REQUIRED |
| 8 | 機能一覧 | 0 | 3 | 3 | 0 | 6 | 0 | 4 | 2 | 0 | 26 | 3 | 機能一覧 | NOT_NEEDED | REVIEW_REQUIRED |
| 9 | 用語・詳細仕様への参照 | 0 | 3 | 3 | 0 | 0 | 0 | 5 | 2 | 1 | 16 | 6 | 用語・詳細仕様への参照 | NOT_NEEDED | REVIEW_REQUIRED |
| 10 | 継続検討事項 | 0 | 2 | 2 | 0 | 0 | 0 | 11 | 1 | 0 | 16 | 3 | 継続検討事項 | NOT_NEEDED | REVIEW_REQUIRED |

## Section Details

### 0 設計環境

- Problem: 成果物の役割、正本、対象版、生成範囲が不明だと、後続工程がAuthorityを誤る。 / 表・locator・派生Artifactの読み方が不明だと、Source本文の代替や独立正本として誤用され得る。
- Purpose: Structured Design Dataの文書境界と正本関係を明示する。 / 構造化単位、Source locator、Authority競合時の読み方を定義する。
- Exact values: —
- Assignment review: 12
- Semantic review: 4 review / 4 rejected
- Major coverage: SDD-L0005, SDD-L0007, SDD-L0009, SDD-L0013, SDD-L0014, SDD-L0015, SDD-L0016, SDD-L0017, SDD-L0018, SDD-L0022, SDD-L0024, SDD-L0026
- Source locators: SDD line 1017, SDD line 1019, SDD line 1021, SDD line 1023, SDD line 1027, SDD line 1082, SDD line 1084, SDD line 1086, SDD line 1090, SDD line 1092, SDD line 1094, SDD line 1098
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 1.1 システムの目的

- Problem: 目的と実現手段の対応が不明だと、個別機構が何を保護するか追跡できない。
- Purpose: 設計上の目的・問題を、その実現手段とSource位置へ接続する。
- Exact values: —
- Assignment review: 0
- Semantic review: 4 review / 2 rejected
- Major coverage: SDD-L0220, SDD-L0222, SDD-L0224, SDD-L0228, SDD-L0229, SDD-L0230, SDD-L0231, SDD-L0232, SDD-L0233, SDD-L0234
- Source locators: SDD line 220, SDD line 222, SDD line 224, SDD line 228, SDD line 229, SDD line 230, SDD line 231, SDD line 232, SDD line 233, SDD line 234
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 1.2 全体構成

- Problem: Design Source内の目的、前提、処理、保護機構が分散していると、設計全体の因果と閉ループを追跡しにくい。 / 採用機構だけでは、どの前提・失敗を防ぐ設計かを後工程が判断できない。
- Purpose: 目的から実現手段までの関係と、中核処理の接続を一つの構造として示す。 / 問題、理由、方針、実現機構、保護対象の因果を保持する。
- Exact values: —
- Assignment review: 3
- Semantic review: 12 review / 6 rejected
- Major coverage: SDD-L0212, SDD-L0214, SDD-L0216, SDD-L1616, SDD-L1618, SDD-L1620, SDD-L1624, SDD-L1625, SDD-L1626, SDD-L1627, SDD-L1628, SDD-L1629
- Source locators: SDD line 1616, SDD line 1618, SDD line 1620, SDD line 1624, SDD line 1625, SDD line 1626, SDD line 1627, SDD line 1628, SDD line 1629, SDD line 1630, SDD line 1631, SDD line 1632
- Cross references: —
- Unresolved: —
- Diagram: REVIEW / component/sequence / 境界または責務比較

### 1.3 HumanとARGUSの役割分担

- Problem: 人、ARGUS、Broker、Agentの権限をRuntime componentや処理機能と混同すると、Human-in-the-loopと更新境界が崩れる。 / 提案・判断・状態更新・外部実行のAuthorityが曖昧になると、自動売買やWriter迂回が成立し得る。
- Purpose: 設計上の権限主体を、その意味と実行主体・処理責務との関係によって区別する。 / 権限主体の許可操作と、Runtime / UI componentである実行主体の処理責務を分離し、Human-in-the-loopとSingle Writer境界を維持する。
- Exact values: —
- Assignment review: 9
- Semantic review: 3 review / 19 rejected
- Major coverage: SDD-L0043, SDD-L0045, SDD-L0047, SDD-L0051, SDD-L0052, SDD-L0053, SDD-L0054, SDD-L0056, SDD-L0262, SDD-L0264, SDD-L0266, SDD-L0270
- Source locators: SDD line 262, SDD line 264, SDD line 266, SDD line 270, SDD line 271, SDD line 272, SDD line 273, SDD line 274, SDD line 275, SDD line 43, SDD line 45, SDD line 47
- Cross references: —
- Unresolved: —
- Diagram: REVIEW / component/sequence / 境界または責務比較

### 1.4 全体処理

- Problem: 個別定義だけでは、CommandからCommit、PolicyからGate、IncidentからNotificationまでの接続を読み違え得る。 / Selectionから評価・改善までの順序と保護境界が分断されると、閉ループの欠落を見逃す。
- Purpose: 主要概念間の非同義関係と処理接続を明示する。 / 中核処理を入力、主体、出力、次処理、保護機構として接続する。
- Exact values: —
- Assignment review: 0
- Semantic review: 7 review / 10 rejected
- Major coverage: SDD-L0158, SDD-L0160, SDD-L0162, SDD-L0164, SDD-L0173, SDD-L0238, SDD-L0240, SDD-L0242, SDD-L0246, SDD-L0247, SDD-L0248, SDD-L0249
- Source locators: SDD line 158, SDD line 160, SDD line 162, SDD line 164, SDD line 173, SDD line 238, SDD line 240, SDD line 242, SDD line 246, SDD line 247, SDD line 248, SDD line 249
- Cross references: —
- Unresolved: —
- Diagram: NEEDED / flowchart / 処理順または分岐

### 2.1 候補探索

- Problem: 単一総合点や枝間の結論共有は、反証・欠損・異なる探索観点を消し得る。 / 探索・分析の枝を早期統合すると、枝固有の欠損、反証、矛盾が失われ得る。
- Purpose: 独立した探索・分析と矛盾保持を経て、根拠を追跡できる具体的Trade候補を作る。 / UniverseからReportまでの入力・規則・出力を分離し、分析根拠を追跡可能にする。
- Exact values: —
- Assignment review: 3
- Semantic review: 2 review / 1 rejected
- Major coverage: SDD-L0409, SDD-L0411, SDD-L0413, SDD-L0417, SDD-L0419, SDD-L0421, SDD-L0425, SDD-L0426, SDD-L0427, SDD-L0428, SDD-L0429, SDD-L0430
- Source locators: SDD line 409, SDD line 411, SDD line 413, SDD line 417, SDD line 419, SDD line 421, SDD line 425, SDD line 426, SDD line 427, SDD line 428, SDD line 429, SDD line 430
- Cross references: 2.2
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 2.2 分析・反証・判断材料

- Problem: 投資分析固有語を一般語の意味で解釈すると、探索集合、矛盾、仮説、Risk制約の役割を誤る。
- Purpose: 分析・Allocation・Risk・監視Dataの概念をSource上の役割で定義する。
- Exact values: —
- Assignment review: 0
- Semantic review: 1 review / 0 rejected
- Major coverage: SDD-L0177, SDD-L0179, SDD-L0181, SDD-L0185, SDD-L0186, SDD-L0187, SDD-L0188, SDD-L0189, SDD-L0190, SDD-L0191
- Source locators: SDD line 177, SDD line 179, SDD line 181, SDD line 185, SDD line 186, SDD line 187, SDD line 188, SDD line 189, SDD line 190, SDD line 191
- Cross references: 2.3
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 2.3 資金配分とリスク検証

- Problem: 投資魅力度と取引量・Hard Risk判定を同じ判断へ混在させると、Policy制約を迂回し得る。
- Purpose: 「買うか」「いくら買うか」「機械制約を満たすか」を別処理として接続する。
- Exact values: —
- Assignment review: 0
- Semantic review: 1 review / 0 rejected
- Major coverage: SDD-L0434, SDD-L0436, SDD-L0438, SDD-L0442, SDD-L0443, SDD-L0445, SDD-L0447
- Source locators: SDD line 434, SDD line 436, SDD line 438, SDD line 442, SDD line 443, SDD line 445, SDD line 447
- Cross references: 2.4, 6.4
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 2.4 Humanの判断

- Problem: 判断候補、Human権限行使、外部取引、問題状態、配送対象を同一Workflowとして扱うと、承認流用や状態消失が起き得る。 / 提案・承認・発注・約定事実を同一状態として扱うと、承認流用、二重資源確保、事実拒否が起き得る。
- Purpose: 各Entityの役割と状態関係を区別する。 / 各EntityとTransaction境界を分離し、承認とBroker現実を正しく関連付ける。
- Exact values: —
- Assignment review: 3
- Semantic review: 19 review / 1 rejected
- Major coverage: SDD-L0103, SDD-L0105, SDD-L0107, SDD-L0111, SDD-L0112, SDD-L0113, SDD-L0114, SDD-L0115, SDD-L0116, SDD-L0117, SDD-L0118, SDD-L0604
- Source locators: SDD line 103, SDD line 105, SDD line 107, SDD line 111, SDD line 112, SDD line 113, SDD line 114, SDD line 115, SDD line 116, SDD line 117, SDD line 118, SDD line 604
- Cross references: 2.5
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 2.5 売買と売買結果

- Problem: 未解決OrderのSlotやreservationをTTL・停止だけで解放すると、同じ資源を別Tradeへ二重割当し得る。 / Brokerで成立した事実をProposalの有効性判定と混同すると、TTL失効やPolicy変更を理由に現実の約定を失い得る。
- Purpose: Broker上の確定事実と整合するまでOrder状態と資源予約を保持する。 / 事実受領とCompliance評価を分離し、PortfolioをBroker現実へ一致させる。
- Exact values: —
- Assignment review: 0
- Semantic review: 16 review / 5 rejected
- Major coverage: SDD-L0630, SDD-L0632, SDD-L0634, SDD-L0638, SDD-L0639, SDD-L0640, SDD-L0641, SDD-L0642, SDD-L0643, SDD-L0644, SDD-L0646, SDD-L0650
- Source locators: SDD line 630, SDD line 632, SDD line 634, SDD line 638, SDD line 639, SDD line 640, SDD line 641, SDD line 642, SDD line 643, SDD line 644, SDD line 646, SDD line 650
- Cross references: 2.6
- Unresolved: —
- Diagram: NEEDED / flowchart / 処理順または分岐

### 2.6 ポートフォリオ管理

- Problem: 魅力度だけではPortfolio制約、Cash、役割配分、Thesis崩壊を扱えない。 / RoleとHorizonを一つの比率軸へ混在させると、lotの二重計上が起き得る。
- Purpose: Allocationと売却判断を明示Policyと決定論的制約へ接続する。 / Portfolioの役割分類と想定時間軸を独立した軸として示す。
- Exact values: 8%, 15%, 30%, 20%, 25%, 10%, 15%
- Assignment review: 3
- Semantic review: 23 review / 1 rejected
- Major coverage: SDD-L0678, SDD-L0680, SDD-L0682, SDD-L0686, SDD-L0688, SDD-L0690, SDD-L0694, SDD-L0695, SDD-L0699, SDD-L0701, SDD-L0703, SDD-L0707
- Source locators: SDD line 1823, SDD line 1825, SDD line 1827, SDD line 1831, SDD line 1832, SDD line 1833, SDD line 1834, SDD line 1835, SDD line 1836, SDD line 678, SDD line 680, SDD line 682
- Cross references: 2.7
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 2.7 監視と再評価

- Problem: 保有・候補・市場を同じ周期で扱うこと、およびLocal停止中も監視できると誤認することは、重大Riskの見逃しや能力の過大表示につながる。 / Event取得、Thesis差分、再分析、通知を一段階として扱うと、Data不足やLatency境界を隠し得る。
- Purpose: 監視対象別の優先度と、取得から通知までの観測可能なLatency境界を明示する。 / EventからHuman判断候補までの処理順序と各段階の失敗動作を分離する。
- Exact values: —
- Assignment review: 16
- Semantic review: 6 review / 6 rejected
- Major coverage: SDD-L0769, SDD-L0771, SDD-L0773, SDD-L0777, SDD-L0778, SDD-L0779, SDD-L0781, SDD-L0783, SDD-L0789, SDD-L0790, SDD-L0791, SDD-L0792
- Source locators: SDD line 1343, SDD line 1345, SDD line 1347, SDD line 1351, SDD line 1352, SDD line 1353, SDD line 1354, SDD line 1356, SDD line 1358, SDD line 1360, SDD line 769, SDD line 771
- Cross references: —
- Unresolved: —
- Diagram: NEEDED / flowchart / 処理順または分岐

### 3.1 起動

- Problem: 起動時責務を一つの機構へ集約すると、Identity・Config・Bindingの失敗原因とAuthorityが曖昧になる。 / 安全・費用・State基盤より投資分析を先行すると、成立条件を検証できない実装が積み上がる。
- Purpose: 起動Subsystemの責務と呼出し順を固定し、typed failureを境界ごとに保持する。 / 依存関係に沿ってRuntime基盤から段階的に実装・確認する。
- Exact values: —
- Assignment review: 0
- Semantic review: 23 review / 2 rejected
- Major coverage: SDD-L1107, SDD-L1109, SDD-L1111, SDD-L1115, SDD-L1116, SDD-L1117, SDD-L1118, SDD-L1120, SDD-L1122, SDD-L1537, SDD-L1539, SDD-L1541
- Source locators: SDD line 1107, SDD line 1109, SDD line 1111, SDD line 1115, SDD line 1116, SDD line 1117, SDD line 1118, SDD line 1120, SDD line 1122, SDD line 1537, SDD line 1539, SDD line 1541
- Cross references: 3.2
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 3.2 継続実行

- Problem: Local停止、外部副作用、並行更新、再試行が重なると、処理喪失・二重適用・重複課金が起き得る。 / 外部API成功後にLocal Commitが失敗すると、再実行時に外部呼出し・課金・副作用が重複し得る。
- Purpose: 中断を通常条件として扱い、JobとCanonical Commitを安全に再開・復旧できるRuntimeを成立させる。 / 外部副作用を再実行せず、保存済みStageから安全にJobを再開できるようにする。
- Exact values: —
- Assignment review: 6
- Semantic review: 5 review / 12 rejected
- Major coverage: SDD-L0298, SDD-L0300, SDD-L0302, SDD-L0321, SDD-L0323, SDD-L0325, SDD-L0329, SDD-L0330, SDD-L0331, SDD-L0332, SDD-L0333, SDD-L0334
- Source locators: SDD line 1316, SDD line 1318, SDD line 1320, SDD line 1324, SDD line 1326, SDD line 1328, SDD line 1332, SDD line 1333, SDD line 1334, SDD line 1335, SDD line 1337, SDD line 298
- Cross references: 3.3
- Unresolved: —
- Diagram: NEEDED / flowchart / 処理順または分岐

### 3.3 中断・再開

- Problem: 初期化、通常実行、異常終了後の復旧、正常終了を混同すると、不明な正本での再開やCrashの状態化が起き得る。 / Schedule時刻と経過時間を同じClockで扱うと、Sleepや時計変更後のDue判定を誤り得る。
- Purpose: Runtimeの通常系と異常終了後の起動時復旧を簡潔な状態機械として固定する。 / Wall Clockとmonotonic clockの用途を分離し、復帰後Catch-upを成立させる。
- Exact values: —
- Assignment review: 0
- Semantic review: 3 review / 2 rejected
- Major coverage: SDD-L0306, SDD-L0308, SDD-L0310, SDD-L0314, SDD-L0315, SDD-L0316, SDD-L0317, SDD-L0344, SDD-L0346, SDD-L0348, SDD-L0352, SDD-L0353
- Source locators: SDD line 306, SDD line 308, SDD line 310, SDD line 314, SDD line 315, SDD line 316, SDD line 317, SDD line 344, SDD line 346, SDD line 348, SDD line 352, SDD line 353
- Cross references: 3.5
- Unresolved: —
- Diagram: NEEDED / flowchart / 処理順または分岐

### 3.4 状態とデータ

- Problem: 現在状態、運用Mode、重大度、優先度、Portfolio分類を一つの状態軸へ混在させると遷移判断を誤る。 / 現実の事実、時点付き観測、判断結果、変更要求を混同すると、事実拒否や履歴破壊が起き得る。
- Purpose: 状態を持つ概念と独立した分類軸を区別する。 / Dataと操作要求の意味および更新経路を分離する。
- Exact values: —
- Assignment review: 3
- Semantic review: 46 review / 3 rejected
- Major coverage: SDD-L0066, SDD-L0068, SDD-L0070, SDD-L0074, SDD-L0075, SDD-L0076, SDD-L0077, SDD-L0078, SDD-L0079, SDD-L0080, SDD-L0081, SDD-L0082
- Source locators: SDD line 139, SDD line 141, SDD line 143, SDD line 147, SDD line 148, SDD line 149, SDD line 150, SDD line 151, SDD line 152, SDD line 153, SDD line 154, SDD line 1730
- Cross references: —
- Unresolved: —
- Diagram: NEEDED / stateDiagram / 状態遷移

### 3.5 保存・バックアップ・復旧

- Problem: Runtime Artifactの正本性と派生性が不明だと、ProjectionやBackupを独立更新し得る。 / 古いsnapshotをそのまま正本へ戻すと、Brokerで成立した実約定やCashとの差異を消し得る。
- Purpose: Artifactごとの生成元、利用先、保持条件、不変条件を定義する。 / Restore後に必ずReconciliationを行い、確認済み差分をEventとして再Commitする。
- Exact values: 2TB, 1.8TB, 2TB, 1.8TB
- Assignment review: 0
- Semantic review: 18 review / 5 rejected
- Major coverage: SDD-L1126, SDD-L1128, SDD-L1130, SDD-L1134, SDD-L1135, SDD-L1136, SDD-L1137, SDD-L1138, SDD-L1139, SDD-L1140, SDD-L1141, SDD-L1142
- Source locators: SDD line 1126, SDD line 1128, SDD line 1130, SDD line 1134, SDD line 1135, SDD line 1136, SDD line 1137, SDD line 1138, SDD line 1139, SDD line 1140, SDD line 1141, SDD line 1142
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 3.6 Deployment

- Problem: Job途中でConfigurationが変わると、同一Runの判断条件と費用上限を再現できない。 / 分析機能を安全基盤より先に実装したり、DeploymentでState / Config / Dataを上書きしたりすると、検証不能なRuntimeが成立し得る。
- Purpose: Job開始時snapshotと変更適用境界を固定する。 / Authority・Cost・State integrity・Recoveryを先行させ、停止・Backup・Schema確認を伴う配備順を固定する。
- Exact values: —
- Assignment review: 3
- Semantic review: 8 review / 3 rejected
- Major coverage: SDD-L1169, SDD-L1171, SDD-L1173, SDD-L1177, SDD-L1178, SDD-L1179, SDD-L1529, SDD-L1531, SDD-L1533, SDD-L1571, SDD-L1573, SDD-L1575
- Source locators: SDD line 1169, SDD line 1171, SDD line 1173, SDD line 1177, SDD line 1178, SDD line 1179, SDD line 1529, SDD line 1531, SDD line 1533, SDD line 1571, SDD line 1573, SDD line 1575
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 4.1 外部サービスとの境界

- Problem: Provider固有依存、無断課金、外部障害、Storage誤Bindingは、Business Logicと正本を危険にする。 / Providerごとの契約・Schema・障害を上位Logicが直接扱うと、依存差替えと共通Governanceが困難になる。
- Purpose: Gateway、Adapter、Budget、Identity、縮退順序により外部依存を統制する。 / 外部Serviceの利用目的、境界、出力、障害・制約をProvider単位で明示する。
- Exact values: —
- Assignment review: 3
- Semantic review: 8 review / 6 rejected
- Major coverage: SDD-L0801, SDD-L0803, SDD-L0805, SDD-L0809, SDD-L0811, SDD-L0813, SDD-L0817, SDD-L0818, SDD-L0819, SDD-L0820, SDD-L0821, SDD-L0823
- Source locators: SDD line 801, SDD line 803, SDD line 805, SDD line 809, SDD line 811, SDD line 813, SDD line 817, SDD line 818, SDD line 819, SDD line 820, SDD line 821, SDD line 823
- Cross references: 4.2, 4.3, 4.4
- Unresolved: —
- Diagram: REVIEW / component/sequence / 境界または責務比較

### 4.2 Provider

- Problem: drive letterだけのBindingや偶発的な容量枯渇は、別Diskへの誤書込みや重要Dataの先行喪失を招き得る。 / 契約、承認、期限、認証、鮮度、Healthを追跡できないと、失効Serviceやstale Dataを利用し得る。
- Purpose: marker identityを検証し、容量圧迫時に重要度順で安全に縮退する。 / 外部ServiceのLifecycleと運用状態を判定できるRegistry属性を定義する。
- Exact values: —
- Assignment review: 0
- Semantic review: 6 review / 1 rejected
- Major coverage: SDD-L0870, SDD-L0872, SDD-L0874, SDD-L0876, SDD-L0878, SDD-L0882, SDD-L0886, SDD-L0887, SDD-L0888, SDD-L0889, SDD-L0890, SDD-L0892
- Source locators: SDD line 1840, SDD line 1842, SDD line 1844, SDD line 1848, SDD line 1849, SDD line 1850, SDD line 1851, SDD line 1852, SDD line 1853, SDD line 1854, SDD line 870, SDD line 872
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 4.3 費用・利用量

- Problem: 課金条件・上限・Fallbackが暗黙だと、Human承認なしの費用Commitment拡大が起き得る。
- Purpose: 有料Serviceの有効化とModel Callを事前承認・Budget reservation・Hard Gateで統制する。
- Exact values: 70%, 85%, 95%, 100%
- Assignment review: 0
- Semantic review: 6 review / 1 rejected
- Major coverage: SDD-L0834, SDD-L0836, SDD-L0838, SDD-L0840, SDD-L0842, SDD-L0849, SDD-L0853, SDD-L0854, SDD-L0855, SDD-L0857, SDD-L0862, SDD-L0864
- Source locators: SDD line 834, SDD line 836, SDD line 838, SDD line 840, SDD line 842, SDD line 849, SDD line 853, SDD line 854, SDD line 855, SDD line 857, SDD line 862, SDD line 864
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 4.4 外部障害

- Problem: Local停止、Provider障害、Storage不在、破損、入力矛盾は通常運用中に発生し、誤った継続や事実推測につながり得る。 / 異なる失敗を一律Retryまたは一律停止すると、無限Retry、危険継続、復旧不能が起き得る。
- Purpose: 失敗分類から安全な停止・Retry・Reconciliationへ追跡可能にする。 / 失敗条件から状態、即時処理、復旧条件、人の関与までを追跡可能にする。
- Exact values: —
- Assignment review: 3
- Semantic review: 28 review / 2 rejected
- Major coverage: SDD-L1243, SDD-L1245, SDD-L1247, SDD-L1251, SDD-L1253, SDD-L1255, SDD-L1259, SDD-L1260, SDD-L1261, SDD-L1262, SDD-L1263, SDD-L1264
- Source locators: SDD line 1243, SDD line 1245, SDD line 1247, SDD line 1251, SDD line 1253, SDD line 1255, SDD line 1259, SDD line 1260, SDD line 1261, SDD line 1262, SDD line 1263, SDD line 1264
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 5.1 CLI / Human Interface

- Problem: CLI、Tray、Runnerが独自LogicやWriter経路を持つと、同じ操作で異なる検証・更新結果が生じ得る。 / Human操作の入口とWriter / Serviceが不明確だと、検証経路の分岐や直接更新が起き得る。
- Purpose: Human操作を共有Command / Service Layerへ統一し、非RUNNING時にもStatus、Help、System Statusの安全な操作入口を保つ。 / 各Commandの入力、処理、出力、更新主体、失敗動作を固定する。
- Exact values: 1時, 3時, 1時, 1時, 3時, 3時, 00:00, 00:00, 00:00, 24:00
- Assignment review: 3
- Semantic review: 8 review / 3 rejected
- Major coverage: SDD-L1183, SDD-L1185, SDD-L1187, SDD-L1191, SDD-L1193, SDD-L1195, SDD-L1199, SDD-L1200, SDD-L1201, SDD-L1202, SDD-L1203, SDD-L1204
- Source locators: SDD line 1183, SDD line 1185, SDD line 1187, SDD line 1191, SDD line 1193, SDD line 1195, SDD line 1199, SDD line 1200, SDD line 1201, SDD line 1202, SDD line 1203, SDD line 1204
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 5.2 Humanの対応状態

- Problem: 人の処理能力、通知可能時間、Proposal validity、Incident解決状態を混同すると、通知過多または重大案件の消失が起き得る。 / 人の状態とSystem内部capacityを同一視すると、人の意思に反する自動遷移や処理量制御が起き得る。
- Purpose: Human loadを制御しながら、Durableな判断・通知経路を維持する。 / Human入力のStatusから内部capacityを一方向に導出し、通知・処理量を制御する。
- Exact values: —
- Assignment review: 3
- Semantic review: 6 review / 0 rejected
- Major coverage: SDD-L0472, SDD-L0474, SDD-L0476, SDD-L0480, SDD-L0482, SDD-L0484, SDD-L0488, SDD-L0489, SDD-L0490, SDD-L0492, SDD-L0498, SDD-L0500
- Source locators: SDD line 472, SDD line 474, SDD line 476, SDD line 480, SDD line 482, SDD line 484, SDD line 488, SDD line 489, SDD line 490, SDD line 492, SDD line 498, SDD line 500
- Cross references: —
- Unresolved: —
- Diagram: NEEDED / stateDiagram / 状態遷移

### 5.3 判断待ち

- Problem: 復帰・配送前にProposalを再評価しないと、期限切れ・重複・条件変更済み判断を提示し得る。
- Purpose: Proposalの再評価結果と対応動作を区別する。
- Exact values: —
- Assignment review: 0
- Semantic review: 13 review / 0 rejected
- Major coverage: SDD-L0504, SDD-L0506, SDD-L0508, SDD-L0512, SDD-L0513, SDD-L0514, SDD-L0515, SDD-L0516
- Source locators: SDD line 504, SDD line 506, SDD line 508, SDD line 512, SDD line 513, SDD line 514, SDD line 515, SDD line 516
- Cross references: 5.4
- Unresolved: —
- Diagram: NEEDED / stateDiagram / 状態遷移

### 5.4 通知

- Problem: Alert記録、配送成功、Human認知、問題解決を同一状態として扱うと対応状況を誤る。 / 事象の重大度から配送優先度を暗黙導出すると、InvestmentとSystemの通知境界を迂回し得る。
- Purpose: 配送試行とHuman認知を独立して追跡する。 / severityの意味と配送上の扱いを明示する。
- Exact values: 85%, 12:00, 13:00, 17:30, 24:00, 17:30, 24:00, 17:30, 24:00, 17:30
- Assignment review: 0
- Semantic review: 29 review / 1 rejected
- Major coverage: SDD-L0535, SDD-L0537, SDD-L0539, SDD-L0543, SDD-L0544, SDD-L0545, SDD-L0546, SDD-L0547, SDD-L0551, SDD-L0553, SDD-L0555, SDD-L0559
- Source locators: SDD line 535, SDD line 537, SDD line 539, SDD line 543, SDD line 544, SDD line 545, SDD line 546, SDD line 547, SDD line 551, SDD line 553, SDD line 555, SDD line 559
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 5.5 Incidentと復旧

- Problem: Proposalの失効や通知認知をIncident解決とみなすと、未解決問題が消失する。
- Purpose: 問題の検知、認知、解決、再通知をDurableな状態遷移として管理する。
- Exact values: —
- Assignment review: 0
- Semantic review: 2 review / 0 rejected
- Major coverage: SDD-L0520, SDD-L0522, SDD-L0524, SDD-L0528, SDD-L0529, SDD-L0530, SDD-L0531
- Source locators: SDD line 520, SDD line 522, SDD line 524, SDD line 528, SDD line 529, SDD line 530, SDD line 531
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 6.1 Fail Closed

- Problem: 運用規則、個別制約、後続許可、判定主体を同義扱いすると、Fail Closedの適用点が曖昧になる。 / 個別の安全機構だけを見ると、何をどの失敗から保護するかという横断関係が見えにくい。
- Purpose: PolicyからConstraint、Validator、Gate結果への関係を定義する。 / 安全機構、保護対象、防止する失敗、関連設計要素を対応付ける。
- Exact values: —
- Assignment review: 17
- Semantic review: 29 review / 9 rejected
- Major coverage: SDD-L0122, SDD-L0124, SDD-L0126, SDD-L0130, SDD-L0131, SDD-L0132, SDD-L0133, SDD-L0134, SDD-L0135, SDD-L1060, SDD-L1062, SDD-L1064
- Source locators: SDD line 1060, SDD line 1062, SDD line 1064, SDD line 1068, SDD line 1069, SDD line 1070, SDD line 1071, SDD line 1072, SDD line 1073, SDD line 1074, SDD line 1075, SDD line 1076
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 6.2 TEST / PAPER / LIVE

- Problem: 仮想約定規則を結果後に変更したり実取引と別更新経路にしたりすると、Paper評価の比較可能性が失われる。
- Purpose: Paper期間の資金境界、約定規則、Fact経路を事前固定し、投資性能証明ではなく運用性能を検証する。
- Exact values: 1か月, 12か月
- Assignment review: 0
- Semantic review: 5 review / 0 rejected
- Major coverage: SDD-L1490, SDD-L1492, SDD-L1494, SDD-L1498, SDD-L1499, SDD-L1500, SDD-L1501, SDD-L1503, SDD-L1505
- Source locators: SDD line 1490, SDD line 1492, SDD line 1494, SDD line 1498, SDD line 1499, SDD line 1500, SDD line 1501, SDD line 1503, SDD line 1505
- Cross references: 7.2
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 6.3 正本状態の保護

- Problem: 複数更新主体や途中停止は、version競合、部分書込み、二重適用を発生させ得る。
- Purpose: 最新Stateの再読込からAtomic Replaceまでを一つの決定論的Commit境界にする。
- Exact values: —
- Assignment review: 0
- Semantic review: 2 review / 0 rejected
- Major coverage: SDD-L0391, SDD-L0393, SDD-L0395, SDD-L0399, SDD-L0400, SDD-L0401, SDD-L0402, SDD-L0403, SDD-L0405
- Source locators: SDD line 391, SDD line 393, SDD line 395, SDD line 399, SDD line 400, SDD line 401, SDD line 402, SDD line 403, SDD line 405
- Cross references: —
- Unresolved: —
- Diagram: NEEDED / stateDiagram / 状態遷移

### 6.4 投資リスク

- Problem: BUYとSELLへ同じ制約適用を行うと、Risk縮小SELLを妨げるか、必要制約を免除し得る。
- Purpose: 制約ごとにBUY / ADDとSELL / REDUCEの適用差と例外を固定する。
- Exact values: 25%, 20%
- Assignment review: 0
- Semantic review: 8 review / 1 rejected
- Major coverage: SDD-L0451, SDD-L0453, SDD-L0455, SDD-L0459, SDD-L0460, SDD-L0461, SDD-L0462, SDD-L0463, SDD-L0464, SDD-L0465, SDD-L0466, SDD-L0468
- Source locators: SDD line 451, SDD line 453, SDD line 455, SDD line 459, SDD line 460, SDD line 461, SDD line 462, SDD line 463, SDD line 464, SDD line 465, SDD line 466, SDD line 468
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 6.5 Secret・データ保護

- Problem: 人・System・外部Service・Environment・Storage・Data種別の境界が暗黙だと、禁止された越境が起き得る。
- Purpose: 境界ごとの許可経路と制約を明示する。
- Exact values: —
- Assignment review: 0
- Semantic review: 9 review / 3 rejected
- Major coverage: SDD-L0279, SDD-L0281, SDD-L0283, SDD-L0287, SDD-L0288, SDD-L0289, SDD-L0290, SDD-L0291, SDD-L0292, SDD-L0293, SDD-L0294
- Source locators: SDD line 279, SDD line 281, SDD line 283, SDD line 287, SDD line 288, SDD line 289, SDD line 290, SDD line 291, SDD line 292, SDD line 293, SDD line 294
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 7.1 検証

- Problem: Capability、Regression、MVS、PIT、CAS、Fail Closedを名称だけで扱うと、判定範囲を過大表示し得る。 / 設計記述や自己申告を実測PASSと扱うこと、および部品試験だけで閉ループ完了と誤認することは、未成立Capabilityを運用へ進め得る。
- Purpose: 検証・実装上の中核概念と相互差異を定義する。 / 凍結基準によるCapability / Regression検証とMVS Gateを定義する。
- Exact values: —
- Assignment review: 6
- Semantic review: 148 review / 9 rejected
- Major coverage: SDD-L0195, SDD-L0197, SDD-L0199, SDD-L0203, SDD-L0204, SDD-L0205, SDD-L0206, SDD-L0207, SDD-L0208, SDD-L0962, SDD-L0964, SDD-L0966
- Source locators: SDD line 1364, SDD line 1366, SDD line 1368, SDD line 1372, SDD line 1374, SDD line 1376, SDD line 1380, SDD line 1381, SDD line 1382, SDD line 1383, SDD line 1384, SDD line 1385
- Cross references: 7.2
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 7.2 Historical / PAPER / LIVE

- Problem: 個別部品の成功だけでは、BUYから全売却、再起動復元までの閉ループ成立を証明できない。 / 未来情報、架空約定、短期間の結果を実資金性能の証明と誤認すると、未検証のRiskをLiveへ持ち込む。
- Purpose: 最小の投資枝でState、Human Approval、Fact、Watch、復旧を端から端まで検証する。 / 検証種別ごとの能力限界と、次段階へ進むGateを固定する。
- Exact values: —
- Assignment review: 3
- Semantic review: 28 review / 9 rejected
- Major coverage: SDD-L0994, SDD-L0996, SDD-L0998, SDD-L1002, SDD-L1003, SDD-L1004, SDD-L1005, SDD-L1006, SDD-L1007, SDD-L1008, SDD-L1009, SDD-L1011
- Source locators: SDD line 1002, SDD line 1003, SDD line 1004, SDD line 1005, SDD line 1006, SDD line 1007, SDD line 1008, SDD line 1009, SDD line 1011, SDD line 1013, SDD line 1466, SDD line 1468
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 7.3 判断結果の評価

- Problem: 判断根拠・版・時刻を追跡できないこと、および成績に合わせて目的や評価軸を変更することは、監査と比較可能性を失わせる。 / 判断の入力版、Evidence、時刻、実行条件を追跡できないと、後日監査・再現・比較が成立しない。
- Purpose: Decision provenance、分離した評価軸、承認付きBreakを成立させる。 / Decision provenanceの構造と正本・Projection境界を示す。
- Exact values: —
- Assignment review: 3
- Semantic review: 6 review / 1 rejected
- Major coverage: SDD-L0898, SDD-L0900, SDD-L0902, SDD-L0906, SDD-L0908, SDD-L0910, SDD-L0912, SDD-L0914, SDD-L0916, SDD-L0920, SDD-L0922, SDD-L0924
- Source locators: SDD line 898, SDD line 900, SDD line 902, SDD line 906, SDD line 908, SDD line 910, SDD line 912, SDD line 914, SDD line 916, SDD line 920, SDD line 922, SDD line 924
- Cross references: 7.4
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 7.4 変更管理

- Problem: 変更階層、承認対象、Rollback境界が曖昧だと、Objectiveの自己正当化や事実履歴の巻戻しが起き得る。 / 変更後に成立済みCapabilityを再確認しないと、局所修正がState・Funds・Approval等の不変条件を破り得る。
- Purpose: Breakを影響範囲別に分類し、具体的diff・再承認・Version切替へ拘束する。 / 変更影響に応じたAffected / Core / Full回帰集合で不変条件を検証する。
- Exact values: —
- Assignment review: 0
- Semantic review: 35 review / 0 rejected
- Major coverage: SDD-L0939, SDD-L0941, SDD-L0943, SDD-L0947, SDD-L0948, SDD-L0949, SDD-L0950, SDD-L0952, SDD-L0954, SDD-L0956, SDD-L0958, SDD-L1433
- Source locators: SDD line 1433, SDD line 1435, SDD line 1437, SDD line 1439, SDD line 1443, SDD line 1444, SDD line 1445, SDD line 1446, SDD line 1447, SDD line 1448, SDD line 1449, SDD line 1450
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 8 機能一覧

- Problem: Domain状態とHuman-facing出力のSchemaが自由文章だけだと、遷移・必須項目・関連Entityが曖昧になる。 / 分析結果を自由文章だけで提示すると、反証、Thesis、具体的Trade、Human選択肢が欠落し得る。
- Purpose: Domain対象ごとの状態機械と、Report / Audit / Registry等の出力構造を明示する。 / Human判断に必要なReport構造と必須内容を固定する。
- Exact values: 100%, 35%, 25%, 20%, 12%, 8%
- Assignment review: 3
- Semantic review: 3 review / 1 rejected
- Major coverage: SDD-L1722, SDD-L1724, SDD-L1726, SDD-L1781, SDD-L1783, SDD-L1785, SDD-L1789, SDD-L1790, SDD-L1791, SDD-L1792, SDD-L1793, SDD-L1794
- Source locators: SDD line 1722, SDD line 1724, SDD line 1726, SDD line 1781, SDD line 1783, SDD line 1785, SDD line 1789, SDD line 1790, SDD line 1791, SDD line 1792, SDD line 1793, SDD line 1794
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 9 用語・詳細仕様への参照

- Problem: ARGUS固有語を未定義または同義として扱うと、Entity、状態、権限、処理の境界を誤解し得る。 / 表の存在や代表節の確認だけでは、無名文章、意味型混在、Source欠落を見逃し得る。
- Purpose: 重要用語を概念種別ごとに定義し、相違と利用関係を示す。 / Structured Design Data全体をGate A〜Nで検証し、構造化完了の根拠を記録する。
- Exact values: —
- Assignment review: 6
- Semantic review: 4 review / 1 rejected
- Major coverage: SDD-L0035, SDD-L0037, SDD-L0039, SDD-L1667, SDD-L1669, SDD-L1671, SDD-L1675, SDD-L1677, SDD-L1679, SDD-L1683, SDD-L1684, SDD-L1685
- Source locators: SDD line 1667, SDD line 1669, SDD line 1671, SDD line 1675, SDD line 1677, SDD line 1679, SDD line 1683, SDD line 1684, SDD line 1685, SDD line 1686, SDD line 1687, SDD line 1688
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

### 10 継続検討事項

- Problem: 未決の値・方式・Providerを確定設計として扱うと、Sourceにない前提が後工程へ固定される。 / Source内のTBD、UNCONFIGURED、Provider候補を確定値として扱うと、未承認設計が固定される。
- Purpose: 確定範囲と未確定範囲を分離し、確定に必要なEvidenceまたはHuman判断を示す。 / 未確定事項の現在状態と確定に必要なものを保持する。
- Exact values: —
- Assignment review: 3
- Semantic review: 11 review / 0 rejected
- Major coverage: SDD-L1031, SDD-L1033, SDD-L1035, SDD-L1039, SDD-L1041, SDD-L1043, SDD-L1047, SDD-L1048, SDD-L1049, SDD-L1050, SDD-L1051, SDD-L1052
- Source locators: SDD line 1031, SDD line 1033, SDD line 1035, SDD line 1039, SDD line 1041, SDD line 1043, SDD line 1047, SDD line 1048, SDD line 1049, SDD line 1050, SDD line 1051, SDD line 1052
- Cross references: —
- Unresolved: —
- Diagram: NOT_NEEDED /  / 図による改善根拠を未検出

## Coverage Reconciliation

- Baseline / Current / Delta: 1000 / 951 / -49
- Dispositions: {'MERGED': 73, 'SAME': 927}
- MISSING: 0

## Human Review

配置、assignment confidence、semantic candidate、coverage reconciliation、primary owner、cross reference、diagram planを確認し、承認する場合は別のmachine-readable approval artifactでplanning hashを指定する。本Artifact自身はPENDINGであり、Codexは承認しない。

**STOP Human Review**
