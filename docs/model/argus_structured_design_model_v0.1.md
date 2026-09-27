# argus Structured Design Model v0.1

**Document Role:** `STRUCTURED_DESIGN_MODEL`  
**Status:** `HUMAN_REVIEW_REQUIRED`  
**Source Lineage:** Structure Analysis v0.2 migrated by `ARGUS-P-0034-v1`  
**Purpose:** Design Source等から抽出した環境、因果、機能、関係、用語、実現方式を構造化し、System Designその他のViewを生成する中心データとする。  
**Representation:** 現在はMarkdown。将来のgraph表現を妨げないよう、stable analysis ID、型付き関係、確度、sourceを維持する。

## 1. 入力と継承

| Role | Path | SHA-256 |
|---|---|---|
| Design Source | `docs/source/argus_design_source_v0.1.md` | `234504a7dba9b4435729af079c04bdca8f624b544acbb594ea94b9fa4fcf6d6e` |
| ADR | `docs/adr/argus_architecture_decision_records_v0.1.md` | `bef921af342a42d6e39411f0b311ff1643d9016f18ea66ddae71e15a81656549` |
| Test正本 | `docs/test/argus_test_strategy_v0.1.3.md` | `f2faf8d7247a1b75060bb502deacd425268fffd62c6b57db0ac5c224654dacb8` |
| Environment Binding Contract | `docs/contracts/argus_environment_binding_contract_v0.1.md` | `90171ac4a5a0c3940cd4198515f89655b674e7b3aa5a5b7dcb293f698317fa8a` |
| Runtime Identity Contract | `docs/contracts/argus_runtime_identity_document_contract_v0.1.md` | `cb5af0d15cf7d1e2bca0a6300960ea80a7d1abe88775c108cd472db867764e5e` |
| Capability state | `docs/development/argus_capability_registry.md` | `3da43ded84f882d998a2c95dbb59a5d394185c3e3f8c57f2087775afcae04f11` |
| 先行モデル | Structure Analysis v0.2移行前実体 | `0b0d5d7e81c3247174b7961fb3b1f0959fe3a3436eed5d62f3e8d6a07c55e53b` |

先行分析の45情報要素、6主分類+横断分類、型付き関係、二つの論理階層候補、重点分析、確度、Human Review Pointsを継承する。

## 2. 環境

環境は設計の前提であり、CurrentとFutureを混同しない。

| ID | 時点 | 対象 | 環境・制約 | 設計への意味 | Source | 確度 |
|---|---|---|---|---|---|---|
| ENV-001 | Current | Human | 平日日中09:00–17:30は仕事。多忙時は残業があり、即時応答を常時前提にしない | 判断待ち、通知時間、期限、再開可能性が必要 | ARGUS-P-0034-v1; Design Source §21–24 | EXPLICIT |
| ENV-002 | Current | Runtime | Windows 11ローカルPC、Python、internet接続あり、WSL不使用 | Windows native boundary、intermittent runtime、local filesystemを前提にする | ARGUS-P-0034-v1; Design Source §2, §46B | EXPLICIT |
| ENV-003 | Current | Market data | J-Quantsを第一Provider候補とし、FreeとLightのGateを分ける | plan/latency/rate limitをCapability検証する | ADR-001; Design Source §37A | EXPLICIT |
| ENV-004 | Current | Disclosure | EDINET APIを法定開示の第一Providerとする | 原本保存と正規化が必要 | ADR-002 | EXPLICIT |
| ENV-005 | Current candidate | Model | OpenAI APIを初期候補とするがModelProvider経由とする | cost、secret、能力差、交換可能性を境界で扱う | ADR-005 | EXPLICIT |
| ENV-006 | Excluded | Disclosure | TDnet有料APIを初期通常候補から除外 | 未承認費用を前提にしない | ADR-002 | EXPLICIT |
| ENV-007 | Future | Runtime | 将来的なcloud runtime構想 | local固有依存を合理的範囲で隔離する背景。ただし現時点の実装必須要件ではない | ARGUS-P-0034-v1; Design Source §44 | EXPLICIT |

## 3. 設計理解の因果モデル

主要領域は次の型を使って結ぶ。すべてのrowが全段を持つとは限らず、根拠不足は確度で表す。

```text
環境 → 課題 → 目的 → 要求・制約 → 設計原則 → 機能 → 実現方式 → 効果
```

| ID | 環境 | 課題 | 目的 | 要求・制約 | 設計原則 | 機能 | 現在の実現方式 | 効果 | Source / 確度 |
|---|---|---|---|---|---|---|---|---|---|
| CAUSE-001 | Humanは常時応答できない | 判断依頼が埋もれたり期限切れになる | 限られた時間で重要判断を処理する | 即時応答を前提にしない | Human-in-the-loopを耐久状態で支える | 判断待ち・通知・期限管理 | User Status、Decision Queue、TTL | Human負荷を抑えつつ判断を失わない | Design Source §21–25 / EXPLICIT |
| CAUSE-002 | local PCは停止・通信断がある | 処理抜け、二重実行、途中状態が残る | 安全に停止・再開する | 副作用と再試行を制御 | retryable transaction | 継続実行 | Runner、Job、Durable Stage | 再開性とretry costを改善 | Design Source §2 / EXPLICIT |
| CAUSE-003 | drive letter/pathはidentityではない | 別diskへ誤書込みする | environmentとData Rootを照合 | write前にfresh verification | locatorとidentityを分離 | 保存先検証 | Environment Binding | 誤接続・誤書込みをfail-closedにする | EB Contract / EXPLICIT |
| CAUSE-004 | 外部serviceは変更・終了・障害・値上げがある | 変更影響が全moduleへ広がる | 外部依存を局所化する | Business Logicから固有APIを直接呼ばない | 変化点を交換可能なboundaryへ隔離 | 外部data/model取得 | Gateway + Provider Adapter | 差替え中心の変更、回帰範囲・保守負荷の縮小 | ADR-003–005 / EXPLICIT |
| CAUSE-005 | 複数処理がstateを更新する | 一部だけ更新され正しい状態が不明になる | 一貫したcurrent stateを保つ | partial write禁止 | single authority + atomicity | state更新 | Single Writer + Atomic Commit | corruptionとlost updateを防ぐ | Design Source §13 / EXPLICIT |
| CAUSE-006 | AI分析は偏り得る | 反対材料が消え、よい理由だけで判断する | 独立観点と矛盾を残す | final decisionはHuman | evidenceとdecisionを分離 | 判断材料作成 | independent analysis、Contradiction Engine、Report | 再評価可能な判断材料になる | Design Source §6–11 / EXPLICIT |

## 4. 機能・ステップ分類

分類語彙:

- **機能分類:** 投資、実行基盤、状態/データ、外部接続、運用、安全、検証。
- **ステップ分類:** 自動処理、AI処理、ルール処理、人間判断、人間操作、人間入力、外部処理、状態反映。
- **アクター:** Human、argus、AI、External Service。AIはargusが利用する分析主体であり、最終authorityではない。

`FN-*`はこのModel内で安定して参照する分析用IDであり、CanonicalなCapability IDやAPI識別子ではない。

| 機能ID | 機能名 | Formal Name | 機能分類 | ステップ分類 | アクター / ロール | やらないこと | 入力 → 出力 | 効果 | 実現方式 / Source |
|---|---|---|---|---|---|---|---|---|---|
| FN-001 | 候補形成 | Candidate Discovery | 投資 | 自動処理 | argus / 調査対象を絞る | 最終投資判断 | Universe data → candidates | 分析対象を現実的な数にする | filters/branches; Design §6 |
| FN-002 | 独立分析 | Independent Analysis | 投資 | AI処理 | AI / 複数観点を分析 | 発注 | candidate evidence → branch outputs | 同調前の観点を残す | analysis branches; Design §7 |
| FN-003 | 矛盾保持・統合 | Contradiction Preservation | 投資 | AI処理+ルール処理 | argus/AI / 不一致を保持・統合 | 反対理由の平均化・削除 | branch outputs → Report | 弱点を含む判断材料 | Contradiction Engine; Design §8–10 |
| FN-004 | リスク検証 | Deterministic Risk Validator | 安全 | ルール処理 | argus / hard rule検査 | 魅力度だけで上限変更 | proposal/state → pass/failure | AIから独立した制約 | Risk Validator; Design §17A |
| FN-005 | 人間の判断 | Human Decision | 投資 | 人間判断 | Human / 承認・却下・保留 | 大量情報の機械整理 | Report/proposal → decision | 最終authorityをHumanに保持 | Decision Queue; Design §10–11, §24–25 |
| FN-006 | 証券会社での売買 | Broker Operation | 投資 | 人間操作 | Human / 証券会社アプリで操作 | Broker API自動発注 | approved proposal → external action | 自動注文riskを排除 | Manual operation; Design §12, §43 |
| FN-007 | 売買結果入力 | Execution Fact Intake | 状態/データ | 人間入力 | Human / 実際の結果を入力 | proposalから約定を推測 | broker fact → Execution Fact | decisionと事実を分離 | paste/validation; Design §12 |
| FN-008 | Portfolio反映 | Portfolio Commit | 状態/データ | 状態反映 | argus / 正本更新 | partial update | verified fact → Portfolio state | state一貫性 | Single Writer/Atomic Commit; Design §13 |
| FN-009 | 起動条件確認 | Runtime Bootstrap | 実行基盤 | 自動処理+ルール処理 | argus / identity/config/recovery確認 | 不明な条件で通常運転 | manifest/state → verified context | safe startup | Bootstrap; Design §4.2 |
| FN-010 | 外部サービス取得 | External Service Access | 外部接続 | 外部処理+自動処理 | External Service/argus / data取得と正規化 | Business Logicから固有API直呼び | request → raw/normalized result | 変更影響局所化 | Gateway/Adapter; ADR-003 |
| FN-011 | 判断待ち管理 | Decision Queue | 運用 | 自動処理 | argus / priority/TTL/notification管理 | Human判断の代替 | proposals/incidents → durable queue | Human負荷と欠落を抑制 | Queue/User Status; Design §21–25 |
| FN-012 | Capability検証 | Capability Verification | 検証 | ルール処理+人間判断 | Codex/Reviewer/Human / evidenceで判定 | Test PASSだけでclose | requirement/artifacts → evidence/decision | traceability | Test Strategy §24–25 |

**Counts:** 機能entry 12。ステップ分類8。アクター4。ロール12。これは代表的な構造entryであり、全機能のclosed setではない。

## 5. 用語・固有名詞対応表

| Formal Name / English | 日本語表示名 | 意味 | Human Viewでの用例 | 使用上の注意 | Canonical Source |
|---|---|---|---|---|---|
| Runtime Identity | 実行主体の識別情報（Runtime Identity） | どの論理的なargus実体かを示す不変identity | このPCで動くargusの実行主体を確認する | pathや設定値と同一視しない | Runtime Identity Contract §2–3 |
| Environment Binding | 実行環境と保存先の組合せ確認（Environment Binding） | expected identity/environmentとData Root Markerを照合する | TEST用の保存先であることを確認する | drive letterをidentityにしない | EB Contract §2, §5 |
| Runtime Config | 実行設定（Runtime Config） | runtimeで適用する変更可能な設定 | 実行設定を読み込む | state、status、secretと分離 | Design §4.0 |
| Entry Resolution | 起動先の解決（Entry Resolution） | 起動時に使用するruntime資源を決める | 正しい起動先を決める | exact仕様は未確定 | Bootstrap Contract §11 |
| Bootstrap Orchestrator | 起動処理の統合（Bootstrap Orchestrator） | 通常運転前の検証・復旧を統合する | 安全確認後に通常運転へ移る | exact API/一部順序は未確定 | Design §4.2; Bootstrap Contract |
| Runner | 継続実行管理（Runner） | LoopとJobを単一起動で管理する実行主体 | 重複起動を防いで継続処理する | Human Viewでは役割説明を先に置く | Design §2.5, §4.3 |
| Persistent Loop | 継続実行ループ（Persistent Loop） | 定期処理を繰り返すruntime loop | 定期的な処理を継続する | 一回のJobと区別 | Design §2.2, §2.4 |
| Job | 処理単位（Job） | retry/commit境界を持つ一つの作業 | 一つの処理単位を再試行する | 一般語なので初出で意味を示す | Design §2.2–2.3 |
| Durable Stage | 再開用の途中成果（Durable Stage） | 再開可能にするため保存した高価な途中成果 | 外部処理の結果を途中成果として残す | 物理storage tierを意味しない | Design §2.2–2.3 |
| Single Writer | 単一書込み主体（Single Writer） | Canonical Stateを更新できる唯一の境界 | 一つの書込み主体だけが正本を更新する | process数そのものとは限らない | Design §13.2 |
| Atomic Commit | 状態の一括確定（Atomic Commit） | 関係状態を全部または一つも反映しない確定操作 | 状態を途中形なしで一括確定する | Git commitと混同しない | Design §13.2, §46.6 |
| Portfolio commit | ポートフォリオへの確定反映 | 照合済み売買事実をPortfolio stateへ反映する | 売買結果をポートフォリオへ確定反映する | Atomic Commitの一般概念と文脈を分ける | Design §12–13 |
| cost commitment | 費用発生の確定 | 有料契約・増額等の金銭的commitment | 新しい費用発生には人間の承認が必要 | state commitとは無関係 | ADR-004 |
| Canonical State | 正本状態（Canonical State） | 現在の投資状態について唯一の正とするstate | 正本状態を一貫して更新する | 文書全体のCanonical Sourceとは別概念 | Design §4, §13 |
| Raw data | 取得原本（Raw data） | Providerから取得した未改変data | 取得原本を上書きせず保存する | immutable原則を伴う | ADR-006 |
| Normalized data | 共通形式データ（Normalized data） | Provider非依存schemaへ変換したdata | 共通形式へ変換して分析へ渡す | Rawと分離 | ADR-003, ADR-006 |
| ExternalServiceGateway | 外部サービス共通窓口（ExternalServiceGateway） | 外部callの共通統制境界 | 外部サービスを共通窓口経由で使う | 固有Adapterと分離 | ADR-003 |
| Provider Adapter | 提供元別接続部（Provider Adapter） | Provider固有API/schemaを隔離するadapter | 提供元ごとの差を接続部へ閉じ込める | Providerそのものと区別 | ADR-001–003, ADR-005 |
| Provider | 外部サービス提供元 | 市場data、開示、model等の供給主体 | 外部サービス提供元の障害 | 文脈に応じ対象を明示 | ADR-001–005 |
| Report | 投資判断資料（Report） | 根拠・反対理由・前提等を統合した出力 | 人間向けの投資判断資料を作る | 判断そのものではない | Design §9–10 |
| Decision Queue | 判断待ち一覧（Decision Queue） | Human判断待ちを耐久化するstate/process | 判断待ち一覧へ登録する | 単なるUI listではない | Design §24–25 |
| Human Decision | 人間の判断（Human Decision） | proposalへの承認・却下・保留等 | 人間が提案を判断する | Execution Factと分離 | Design §10–12 |
| Execution Fact | 実際の売買結果（Execution Fact） | Broker操作後に実際に起きた事実 | 実際の売買結果を入力する | proposal/approvalと分離 | Design §12 |
| Portfolio | ポートフォリオ（Portfolio） | 保有、現金、commit、policy等のdomain state | ポートフォリオ全体で配分する | 単なる銘柄一覧ではない | Design §13–16 |
| Position Watch | 保有銘柄の監視（Position Watch） | existing positionの変化監視 | 保有銘柄の前提変化を監視する | state viewとprocessの両面 | Design §18.1 |
| Candidate Watch | 投資候補の監視（Candidate Watch） | 未保有候補の変化監視 | 投資候補の条件変化を監視する | 「接続する」等の曖昧語を避ける | Design §18.2 |
| Market Watch | 市場全体の監視（Market Watch） | market-wide event/regime監視 | 市場全体の変化を監視する | individual security監視と区別 | Design §18.3 |
| Deterministic Risk Validator | 決定論的リスク検証器 | modelと独立してhard risk ruleを検査する | リスク上限違反を規則で拒否する | AI評価と区別 | Design §17A |
| Human Approval | 人間の明示承認（Human Approval） | 投資・費用・重大変更をHuman authorityへ拘束 | 明示承認がない費用変更を拒否する | Human Decisionとの対象差を示す | Design §25, §34; ADR-004 |
| User Status | 利用者の対応状況（User Status） | FREE/NORMAL/BUSY等のHuman availability state | 利用者の対応状況に合わせ通知量を変える | system healthではない | Design §21–23 |
| Budget Gate | 費用上限の検査（Budget Gate） | external/model costを呼出し前に制約する | 費用上限を超える呼出しを止める | approvalとusage accountingを伴う | Design §37B |
| Fail Closed | 安全確認不能時の停止（Fail Closed） | 必要条件を確認できない時に依存動作を拒否する | 確認できなければ開始・書込みを止める | system全停止とは限らない | Test Strategy §2.3 |
| test | テスト | requirementへの適合を検証する活動 | テスト結果と証拠を保存する | identifier内の英語は保持可 | Test Strategy |
| risk | リスク | 損失、安全、運用等の望ましくない可能性 | リスク上限 | Hard Risk等のFormal Nameは併記可 | Design §17A |
| plane | 別の観点・層 | 構造を混同しないための独立view | 開発状況は論理構造と別の観点で扱う | 一般本文では原則「観点」「層」へ言換え | Analysis v0.1 |
| Watch | 監視 | 対象変化を検知し再評価へつなぐ概念 | 保有銘柄の監視 | Formal Nameの括弧内にのみ残す | Design §18 |

**Entry count:** 36

## 6. 情報分類

v0.1の分類を維持する。

1. **人間中心の投資システム:** 候補形成、根拠形成、人間判断、実行事実、Portfolio lifecycle。
2. **実行基盤:** startup identity/config/binding、継続実行、transaction reliability。
3. **状態・データ基盤:** marker、Canonical State、raw/normalized/archive、domain/operational state。
4. **外部接続と費用統制:** Gateway、Adapter、cost/rate/retry/audit。
5. **人間・システム運用:** attention、approval、notification、incident、recovery。
6. **検証・学習・進化統制:** test/CV/RV、historical/paper、evaluation、Break/version/deferred scope。
7. **横断的関心事:** Fail Closed、approval、environment isolation、state integrity、provenance、cost。

## 7. 型付き関係

| From | 関係型 | To | 人間向けの意味 |
|---|---|---|---|
| 候補形成 | 処理順序 | 独立分析 | 詳しく調べる候補を複数観点へ渡す |
| 独立分析 | 入出力 | 矛盾保持 | 分析間の不一致を消さず残す |
| 矛盾保持 | 構成 | 投資判断資料 | 反対理由を判断資料の一部にする |
| 投資判断資料 | 入出力 | 人間の判断 | 資料は判断材料であり判断自体ではない |
| 人間の判断 | 処理順序 | 実際の売買結果 | 人間のBroker操作後に事実を入力する |
| 実際の売買結果 | 状態遷移 | ポートフォリオ | 照合済み事実でstateを更新する |
| Environment Binding | 検証 | Data Root | 実行環境と保存先の組合せを確認する |
| Environment Binding | 制約 | 書込み境界 | fresh verificationなしの書込みを拒否する |
| 単一書込み主体 | 制約 | 正本状態 | 一つの境界だけが正本を更新する |
| 取得原本 | 入出力 | 共通形式データ | 原本を検証・変換して分析可能にする |
| 外部サービス共通窓口 | 包含 | 提供元別接続部 | 共通統制の下へ固有接続を置く |
| 起動処理の統合 | 処理順序 | 継続実行ループ | 起動検証成功後だけ通常運転へ進む |
| Capability lifecycle | 検証 | production capability | ContractからReviewまで証拠で確認する |

因果関係型も保持する。

| From | 関係型 | To | 意味 |
|---|---|---|---|
| 環境 | 発生させる（causes） | 課題 | runtimeやHumanの条件から困りごとが生じる |
| 課題 | 動機付ける（motivates） | 目的 | 解決したい理由を与える |
| 目的 | 導出する（derives） | 要求・制約 | 成立に必要な条件を導く |
| 要求・制約 | 導く（guides） | 設計原則 | solution選択の判断軸になる |
| 機能 | 実現される（realized_by） | 実現方式 | 交換可能な現在方式で機能を実装する |
| 実現方式 | 生み出す（produces） | 効果 | 採用結果として改善をもたらす |

## 8. 課題・目的・方針・対策

| 領域 | 課題（人間の言葉） | 目的 | 現在の方針 | 現在の対策 |
|---|---|---|---|---|
| 人間統制 | AIのもっともらしい提案が、そのまま注文として扱われると困る。 | 最終判断を人間に残す | 提案・判断・実行事実を分離 | 人間の判断、Execution Fact、自動発注禁止 |
| 実行継続 | PC停止後に処理が抜けたり二度行われたりすると困る。 | 安全に再開する | retryable transactional job | Runner、Durable Stage、recovery |
| 起動同一性 | 別の実行主体や古い設定なのに通常運転が始まると困る。 | 起動前提を確定する | identity/config/state/secret分離 | Runtime Identity、Config、Entry Resolution、Bootstrap |
| 保存先 | 「いつものL:」が別diskだった、という事故が起きると困る。 | environmentとData Rootを照合 | pathはlocator、UUIDはidentity | Environment Binding |
| 状態完全性 | 現金だけ変わるなど正本の一部だけが更新されると困る。 | 一貫した正本を保つ | Single Writer + Atomic Commit | 単一書込み主体、状態の一括確定 |
| 投資根拠 | 反対材料が消え、よい理由だけで判断することになると困る。 | 独立観点と矛盾を見せる | independent analysis | 矛盾保持、Report、reason weights |
| 人間負荷 | 通知が多すぎて急ぐ判断が埋もれると困る。 | capacityに応じて届ける | status/queue分離 | User Status、Decision Queue、TTL |
| 費用 | 知らない間に高いplanや有料fallbackへ移ると困る。 | 費用をHuman control下に置く | paid service fail-closed | Budget Gate、approval ref |
| 検証 | 未来情報や未review変更を「確認済み」と扱うと困る。 | requirementから結果まで追跡 | Evidence First | Baseline、RED/GREEN、CV/RV、Review |

## 9. 論理階層候補

```text
argus
├─ 人間中心の投資システム
│  ├─ 候補形成
│  ├─ 根拠形成
│  ├─ 人間判断と売買結果
│  └─ ポートフォリオ管理・監視・再評価
├─ 実行・状態基盤
│  ├─ 起動基盤
│  ├─ 継続実行
│  └─ 状態・データ永続化
├─ 外部接続と費用統制
├─ 人間・システム運用
├─ 検証・学習・進化統制
└─ 横断的な安全制約
```

投資の時間的循環はこの責務treeと別viewで示す。v0.1の代替案を維持する。

## 10. 起動・実行基盤

- **包含:** Runtime Identity、Config、Entry Resolution、Environment Binding、Bootstrap Orchestrator。
- **起動順:** system/manifest → host等記録 → binding/正本照合 → recovery → config/current state → missed work → normal loop。
- **実行依存:** Runner → Loop → Job → Service/Gateway、Durable Stage、Single Writer。
- **開発依存:** Environment Binding → Runtime Identity → Config → Entry Resolution → Bootstrap → integration → Investment MVS。

この四関係を一本のflowへ統合しない。一部のexact startup sub-orderと後続3 Capability詳細は未確定。

## 11. 投資領域

包含上は候補形成、根拠形成、人間判断と実際の売買結果、Portfolio lifecycleに分ける。処理上は候補→分析→矛盾保持/統合→判断資料→risk validation→人間判断→売買結果→Portfolio→三つの監視→再評価の循環を持つ。Reportはoutput、Human Decisionはdecision、Execution Factはexternal fact、Portfolioはdomain state、Watchはstate viewとmonitoring processの複合である。

## 12. 安全・運用

Fail Closed、Environment Binding、Risk Validator、Human Approval、Single Writer/Atomic Commit、Budget Gate、provenanceは単一subsystemへ閉じ込めない。主なownerとstartup/write/proposal/external call/changeへの作用先を併記する。

## 13. 外部サービス領域

### 13.1 課題から効果まで

- **環境:** J-Quants、EDINET、Model API等はsystem外部で運営される。
- **課題:** service終了、API変更、料金・上限変更、障害が各moduleへ直接埋め込まれると、変更影響がsystem全体へ広がる。
- **目的:** 外部依存の変更影響を局所化する。
- **要求・制約:** Business Logicから固有SDK/schema/endpointを直接参照しない。無承認の有料fallbackをしない。Raw/provenanceを保持する。
- **設計原則:** 変化する外部依存を交換可能な境界の外へ隔離する。
- **機能:** 市場data、開示、model、newsの取得と正規化。
- **現在の実現方式:** `ExternalServiceGateway` + domain `Provider Adapter`。
- **効果:** 新しい接続moduleの作成と差替えを中心に対応でき、他moduleの変更、回帰範囲、保守負荷を減らす。

### 13.2 serviceごとの状態

| Service | 現在の位置付け | 主な境界 | Source |
|---|---|---|---|
| J-Quants | Market data第一候補。Freeは開発、Light以上はHuman approval後の運用Gate | `MarketDataProvider` | ADR-001 |
| EDINET | 法定開示第一Provider | `DisclosureProvider` | ADR-002 |
| OpenAI API | 初期Model Provider候補 | `ModelProvider` | ADR-005 |
| News Provider | Future Provider | `NewsProvider` | Design Source §37A |
| TDnet paid API | 初期通常候補から除外 | N/A | ADR-002 |

### 13.3 過去データとの共通抽象化

Test Strategy §5は`Provider Interface`の下にLocal Stub、Historical、Real Providerを置き、Design Source §46Bも投資関連Providerが同一interfaceを満たすと明示する。したがって「Business Logicから見た取得interfaceを共有する」根拠は`EXPLICIT`である。

一方、外部serviceの全共通責務（secret、rate limit、paid approval等）をHistorical Providerにも同一に適用することまでは根拠がない。共通なのはdomain取得interfaceであり、Gateway operational policyまで同一かは`UNKNOWN`としてHuman Reviewへ残す。

## 14. 実現方式評価基準候補

今回は採点せず、将来のHuman-in-the-loop方式比較で使う軸を構造化する。

| 評価軸 | 意味 | 根拠区分 |
|---|---|---|
| 要求適合性 | requirementを満たす度合い | Design Source / Test Strategyに明示 |
| 制約適合性 | safety、environment、cost等の制約に従う度合い | 明示 |
| 再利用性 | 複数機能・環境で再利用できる度合い | 候補 |
| 変更容易性 | requirement/provider変更へ局所変更で対応できる度合い | ADR-003に明示 |
| コード規模 | 実装・保守対象量 | 候補 |
| 実装複雑性 | build/testに必要な複雑さ | 候補 |
| 運用複雑性 | setup、監視、復旧の複雑さ | Design Sourceに概念あり |
| 価格 | 初期・固定・従量費 | ADR-004に明示 |
| 信頼性 | failure時も要求品質を保つ度合い | 明示 |
| テスト容易性 | deterministic test/failure injectionのしやすさ | Test Strategyに明示 |
| 性能 | latency、throughput、resource use | Design Sourceに概念あり |
| 運用性 | Humanが状態把握・操作・復旧できる度合い | Design Sourceに概念あり |
| 交換可能性 / 特定service依存度 | 実現方式を別provider/backendへ替えられる度合い | ADR-003/005に明示 |

## 15. 未確定事項とHuman Review Points

- 責務treeとinvestment lifecycle viewの主従。
- StartupとContinuous Executionの正式境界。
- Environment Bindingの所属と横断作用の見せ方。
- stateの集中分類とdomain別ownershipのどちらを前面に出すか。
- Watchをstate view/processへさらに分割するか。
- Safetyの独立viewと各領域annotationの併用方法。
- Human OperationsとSystem Operationsの分割。
- shared/common servicesの正式catalogとownership。
- 後続Runtime Capabilityの表示粒度。
- 「処理単位（Job）」等、Formal Name併記頻度の最終判断。
- Historical ProviderへGatewayのoperational policyをどこまで共通適用するか。
- 実現方式評価基準候補のうち、Canonicalな必須基準へ昇格するもの。
- Design Sourceの「利用データ時刻」がdata自体のas-of時刻だけを指すか、処理時刻も含むか。

主要構造を分析不能にする矛盾は検出していない。これらはHuman judgment事項でありBLOCKEDではない。
