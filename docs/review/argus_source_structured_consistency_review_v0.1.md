# ARGUS Design Source / Structured Design Data 整合性レビュー v0.1

## Summary

**レビュー対象：**

- `docs/source/argus_design_source_v0.1.md`
- `docs/model/argus_structured_design_data_v0.1.md`

**総合判定：** `FAIL`

| 判定 | 件数 |
|---|---:|
| FAIL | 2 |
| REVIEW | 7 |
| INFO | 4 |

| Severity | 件数 |
|---|---:|
| HIGH | 5 |
| MEDIUM | 3 |
| LOW | 5 |

Claude独立レビューへは、既知のFAILと未確定事項を含むレビュー入力として進める。実装・Test参照用Baselineの承認へは進めず、Human ReviewでFAIL 2件の扱いを決定する。

Codex判定は自己チェック結果であり、Human Reviewまたは意思決定機構の最終判定ではない。

## Phase 1 — Application Log同期追記

Design Source §28をApplication Log契約の正本とし、§4の物理配置表は§28を参照する構造へ整理した。Structured Design Dataでは§17.3へ同じ設計意味と未確定事項を構造化した。Sourceに存在しない値、方式、日数、Libraryは確定していない。

### 確定済み事項

- Application Logは運用・障害解析用である。
- Runtime、Job、Adapter、Error等を記録対象とする。
- Daily rotationとし、日付単位で管理可能な構造を持つ。
- 物理構造は`logs/application/YYYY-MM-DD/`として表現する。
- Secret、Credential、Token、API key、Authorization header、未redactのdebug dumpを記録しない。
- Canonical State、Fact、Event、Audit / Decision / Execution Record等の代替にしない。
- Application Logを削除してもCanonicalな投資判断、Portfolio State、Fact、Event、Auditを失わない。

### 未確定事項

- 生成主体、Writer責務、書込経路。
- 書込み失敗時の本処理への影響。
- Daily rotationの日付境界とtimezone。
- retention期間、cleanup / deletion方法。
- Log肥大化、disk full、Storage Criticalとの接続。
- crash直前のdurability保証範囲。
- Runtime / Job / Adapter / Errorごとの最低限識別情報。
- TEST / PAPER / LIVE間の分離方法。
- Development環境とRuntime環境の分離方法。
- 既知の禁止対象以外の禁止・masking範囲。
- filename、file format、schema、logging library。

## P-0067変更事項

| 項目 | Codex判定 | 確認結果 |
|---|---|---|
| Runtime lifecycle | PASS | Source §4.2〜4.3とStructured Data §2.2 / §5.1で`INIT / RUNNING / RESUMING / END`に統一。正常系と異常終了後の遷移も一致 |
| Execution Paste | PASS | RUNNING中のみ受理し、非RUNNING時はError拒否。停止中Durable受領の旧契約なし |
| Status / Help / System Status | PASS | 非RUNNINGでも利用可能として一致 |
| 概念分類 | PASS | Structured Data §2.3で構造上／意味上の2軸を分離。Source §13.1でJudgmentを判断結果Dataとして明示 |
| Notification Policy | FAIL | 現行値はSource §22にあり§24.0が参照する一方、Source §58の履歴記述は§24.0を正本と宣言。正本位置の記述が競合 |
| Paid Service異常系 | PASS | Source §37AとStructured Data §12.2でapproval欠落、Pricing不明、Budget超過を異常時処理として分離 |
| Analysis / Allocation分類 | FAIL | Structured Data §14.2と§20.2に、Analysis / Allocationを`実行主体`または`主体`列へ置く旧分類が残存 |
| Gate表 | PASS | Gate ID、Gate名、Codex判定、Codex確認結果、意思決定機構判定、指摘・根拠を分離。意思決定機構判定は全18件PENDING |
| 設計元位置Scope | PASS | §8.1、§9.3、§12.2、§14.1、§14.3、§18.1、§19.2、§23.3はいずれもSection直下 |

## Application Log

| 観点 | 判定 | 確認結果 | 実装前の扱い |
|---|---|---|---|
| 目的 | PASS | 運用・障害解析用 | 確定済み |
| 対象 | PASS | Runtime / Job / Adapter / Error等 | 確定済み |
| Rotation | PASS | Daily rotation | 確定済み |
| 時刻境界 | REVIEW | 日付境界・timezone未確定 | 実装前に決定が必要 |
| Writer | REVIEW | 生成主体・Writer責務・書込経路未確定 | 実装前に責務境界が必要 |
| Failure | REVIEW | Log書込失敗時の本処理への影響未確定 | State / Safety処理との関係を実装前に決定 |
| Retention | REVIEW | 保持期間は未確定として明示 | 運用設定または後続Contractで決定 |
| Cleanup | REVIEW | cleanup / deletion方法未確定 | retentionと同時に決定 |
| Storage | REVIEW | disk full / Storage Critical縮退順序との接続未確定 | Storage Contractとの接続が必要 |
| Durability | REVIEW | crash直前の保証範囲未確定 | 本処理の成功判定と分離して決定 |
| Identity | REVIEW | Runtime / Job / Adapter / Errorの最低限識別情報未確定 | SchemaまたはLogging Contractで決定 |
| Environment | REVIEW | TEST / PAPER / LIVE間のLog分離方法未確定 | Environment Bindingを弱化しない方式が必要 |
| Dev/Runtime | REVIEW | Development / Runtime間のLog分離方法未確定 | Deployment Contractと同期して決定 |
| Security | REVIEW | Secret等の既知禁止対象は明示済み。その他のmasking範囲は未確定 | Privacy Contractと同期して決定 |
| Audit境界 | PASS | Canonical / Fact / Event / Audit等の代替でなく、削除しても正本情報を失わない | 確定済み |

上表のREVIEWは、未定義であること自体をFAILとしたものではない。実装前の意思決定点を示す。

## Source ↔ Structured Data不整合

### ASD-CONS-001

- Severity: HIGH
- 判定: FAIL
- Source位置: §7、§19、§20
- Structured Data位置: §14.2 Minimum Vertical Slice、§20.2 Event処理
- 問題: `Selection / Analysis`、`Allocation / Validator`、`Analysis`が`実行主体`または`主体`列に残っている。
- 根拠: P-0067はAnalysis / AllocationをActorではなく処理・機能・分類として扱い、SourceにないActorを推測しないことを要求する。Structured Data §7.2では修正済みだが、他表へ同型問題が残存する。
- 修正候補: Actorと処理機能を別列に分け、SourceでActorが確定している場合だけActorを記載する。SourceにActorがなければ未確定として保持する。
- Human判断要否: あり。各処理のActorをSourceへ追加するか、Structured Dataの列構造だけを修正するか決定が必要。

### ASD-CONS-002

- Severity: HIGH
- 判定: FAIL
- Source位置: §22、§24.0、§58 v0.1.6 Design Completion / Implementation Baseline
- Structured Data位置: §8.5〜8.7
- 問題: Source §22がNotification WindowとOverride値を定義し、§24.0は§22を参照している一方、Sourceの変更履歴はSeverity / Priority / Notification Windowの正本を§24.0へ一本化したと記載している。正本位置の宣言と現在の配置が一致しない。
- 根拠: 同じ値の重複定義は解消されているが、どの節がNormativeな正本かについて文書内部の説明が競合する。
- 修正候補: §22をNotification Window / Overrideの正本、§24.0をSeverity / Priority /配送契約の正本とする等、責務境界をHuman判断で確定し、履歴記述とlocatorを同期する。
- Human判断要否: あり。

## 文書内部矛盾

### Design Source

- `ASD-CONS-002`のNotification Policy正本位置に関する矛盾を検出した。
- Runtime lifecycle、Execution Paste、Judgment、Paid Service、Application Logについて、現在仕様と競合する内部定義は検出しなかった。

### Structured Design Data

- `ASD-CONS-001`のActor / 処理機能分類の不統一を検出した。
- Gate表のCodex判定と意思決定機構判定は分離されている。
- Application Logの確定事項と未確定事項の間に値の不正確定は検出しなかった。

## 旧仕様残存

| 検索対象 | 判定 | 結果 |
|---|---|---|
| PAUSED / STOPPED / EXIT_REQUESTED | PASS | 現行Runner状態としての残存なし |
| RECOVERY_REQUIRED | INFO | Runner通常状態としての残存なし。Error code、startup outcome、Incident分類としての利用は正当 |
| OS kill / crash | PASS | 状態ではなく終了事象として扱う |
| Runner停止中Execution Paste Durable受領 | PASS | 旧契約なし。非RUNNING時拒否へ統一 |
| 旧Judgment分類 | PASS | 判断結果Dataへ統一 |
| User Status側の通知時刻再定義 | PASS | §23は§22 / §24.0を参照し値を再定義しない |
| Paid Service失敗の規則配下混在 | PASS | 異常時処理として同階層化 |
| Application LogをAudit正本とする前提 | PASS | 残存なし |

## Source意味保存

### 判定

- 条件、閾値、期間、状態、例外、禁止、優先順位について、全文走査で大規模な欠落またはHard条件の弱化は検出しなかった。
- Runtime、Execution Paste、Paid Governance、Environment Binding、Single Writer、Risk、Approval / RevalidationのAuthorityとFail Closed条件は保持されている。
- 未確定事項を確定値へ昇格した箇所は検出しなかった。
- P-0069で許可されたApplication Log以外のSource外機能追加は検出しなかった。
- `ASD-CONS-001`は意味欠落ではなく、Structured Data内の分類軸不整合である。
- `ASD-CONS-002`は通知値の不一致ではなく、Normativeな正本位置の矛盾である。

## 重複正本チェック

| 対象 | 判定 | 結果 |
|---|---|---|
| Notification Policy | FAIL | 値の重複はないが、Sourceの正本位置宣言が競合 |
| User Status / human_capacity | PASS | 状態・capacityを定義し、通知Policyは参照 |
| Runtime lifecycle | PASS | §4.2〜4.3を正本とし他箇所は要約・検証参照 |
| Retry | PASS | Runtime契約とFailure / Verificationの役割が分離 |
| Budget | PASS | Paid GovernanceとModel Budget Gateの責務が分離 |
| Risk | PASS | Policy、Constraint、Validator、Gateを分離 |
| Approval / Revalidation | PASS | Human Command、再検証、Slot Commitの関係を保持 |
| Environment Binding | PASS | Identity、Data Root marker、write revalidationを分離 |
| Configuration | PASS | `config.json`を単一正本としStatus / Secret / Identityを分離 |
| Canonical State / Projection | PASS | Single Writer正本と再生成可能Projectionを分離 |
| Application Log / Audit | PASS | §28とStructured Data §17.3を正本とし、配置表は参照・要約 |
| Execution Paste | PASS | RUNNING中受理とFact ingressを一貫して保持 |

## 個別指摘一覧

| ID | Severity | 判定 | 要点 |
|---|---|---|---|
| ASD-CONS-001 | HIGH | FAIL | Analysis / AllocationのActor誤分類残存 |
| ASD-CONS-002 | HIGH | FAIL | Notification Policy正本位置の内部矛盾 |
| LOG-001 | MEDIUM | REVIEW | Application Log Writer責務・書込経路未確定 |
| LOG-002 | HIGH | REVIEW | Log書込失敗時の本処理への影響未確定 |
| LOG-003 | MEDIUM | REVIEW | rotation境界、timezone、retention、cleanup未確定 |
| LOG-004 | HIGH | REVIEW | Storage Critical接続とcrash durability未確定 |
| LOG-005 | HIGH | REVIEW | 識別情報、TEST/PAPER/LIVE、Dev/Runtime分離未確定 |
| LOG-006 | MEDIUM | REVIEW | 既知禁止対象外のmasking範囲未確定 |
| LOG-007 | LOW | REVIEW | filename、format、schema、logging library未確定 |
| INFO-001 | LOW | INFO | RECOVERY_REQUIRED系文字列はError / Incidentとして正当 |
| INFO-002 | LOW | INFO | Gate A〜Rの意思決定機構判定は全件PENDING |
| INFO-003 | LOW | INFO | Structured Design Dataの持続的Artifact位置づけは整合 |
| INFO-004 | LOW | INFO | 全文意味保存で上記以外の重大欠落を検出せず |

## Claude Review引継ぎ

独立Reviewerへ次を重点確認させる。

1. `ASD-CONS-001`の全同型箇所を特定し、ActorをSourceへ追加せず列構造だけで解消可能か。
2. `ASD-CONS-002`について、§22と§24.0のどちらを何の正本とするか。
3. Application Log書込失敗をCanonical CommitやRisk処理の失敗へ伝播させる範囲。
4. Storage Critical時にApplication Logをどの順序で縮退させるか。
5. TEST / PAPER / LIVEおよびDevelopment / Runtime間のLog分離をEnvironment Bindingへどう接続するか。
6. Daily rotationのtimezone、最低限識別情報、retention / cleanupをどのContractで確定するか。
7. Security / Privacy上、既知禁止対象以外にmaskingすべき情報があるか。

## 停止状態

Human System Design、Transformation Prompt、実装、Testは変更していない。Claude独立レビュー前、Human Review待ちとして停止する。
