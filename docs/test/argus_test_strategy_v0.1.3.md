# argus --- Test Strategy v0.1.3

**System:** `argus`\
**Document Type:** Test Strategy / Verification Design\
**Status:** IMPLEMENTATION BASELINE\
**Reference Design:**
`argus — Investment Agent System Design v0.1.7 FINAL`\
**Date:** 2026-09-09

------------------------------------------------------------------------

# 1. 目的

本書は、argusの設計契約を「実装できるはず」ではなく、実行結果とEvidenceによって検証するための試験戦略を定義する。

目的： 1. Capability Verification（CV）とRegression
Verification（RV）の実行位置を固定する。 2. TEST / PAPER /
LIVEを分離し、試験が実運用State/Dataを汚染しないようにする。 3. Local
Stub / Historical Provider / Real Provider / Model
Providerの使い分けを定義する。 4. Historical
Testで未来情報混入を防止する。 5. Test
Datasetを再現可能な形で生成・固定する。 6.
Codex等の実装Agentが、実装結果に合わせてExpected ResultやAcceptance
Criteriaを書き換えることを防止する。 7. Historical Test、Real Provider
CV、Realtime Paper、Live Readinessを別Gateとして扱う。 8.
今固定する必要がない細部は、暗黙仕様にせず明示的に`TBD`として管理する。

本書は投資成果を保証するものではない。試験対象はSystem Contract、Runtime
Capability、Data Integrity、Provider
Capability、運用成立性、および限定されたStrategy適合性である。

## Terminology / Abbreviations

本書および関連するTest Artifactでは、次の略語を使用する。

| 略語 | Expansion | argusでの意味 |
|---|---|---|
| `EB` | Environment Binding | Runtimeが使用しようとしているData Rootについて、期待された`state_id / data_root_id / environment`とのBindingを検証する領域。主にTest ID prefixとして使用する。 |
| `CV` | Capability Validation | 個々のUnit TestがPASSすることではなく、argusが必要とするSystem Capabilityが統合環境・対象環境で実際に成立することを検証するもの。L0 PASSだけを理由にCV PASSとしてはならない。 |
| `RV` | Recovery / Resilience Validation | 異常、競合、中断、再起動、復旧、外部障害等の条件下で、Systemが安全性・整合性・fail-closed behaviorを維持できることをScenarioとして検証するもの。通常系Unit Test PASSだけを理由にRV PASSとしてはならない。 |
| `ADR` | Architecture Decision Record | Architecture上の重要な判断、選択肢、理由、制約、将来の見直し条件を記録する文書。 |
| `PIT` | Point-in-Time | Historical Validation / Replayにおいて、対象時点で実際に利用可能だった情報だけを使用する制約。 |

`MVS`は本書および参照するSystem Designで正式なExpansionが明示されていないため、本節ではExpansionを定義しない。

Test Levelの名称と意味は§4を正本とし、次のように参照する。

| Level | 名称 |
|---|---|
| `L0` | Unit |
| `L1` | Component |
| `L2` | Adapter Contract |
| `L3` | Scenario |
| `L4` | Historical Replay |
| `L5` | Real Provider CV |
| `L6` | Realtime Paper |
| `L7` | Live Readiness |

Test IDの基本形は`<Capability Area>-<Test Level>-<Sequence>`と読む。例えば`EB-L0-024`では、`EB`がEnvironment Binding、`L0`がUnit level、`024`が当該Capability Area / Level内のTest sequenceを表す。Sequence番号自体へこれ以上の意味を持たせず、既存Test IDのrenameや新しいprefix体系の定義には使用しない。

Test Level、CV、RVは互いに同義ではない。Unit / Contract TestのPASSは、そのTestが直接観測した範囲の成立を示すにとどまり、Capability ValidationまたはRecovery / Resilience Validation全体のPASSを意味しない。例えばL0 comparisonのPASSだけを理由に、対応するCVまたはRVをPASSとしてはならない。

# 2. 上位原則

## 2.1 Evidence First

試験結果は`NOT_RUN / PASS / PARTIAL / FAIL / BLOCKED / UNASSESSED`のいずれかとする。
設計記述、LLM自己評価、Code Review成功、Test
Codeの存在だけでは`PASS`にしない。`PASS`にはObserved
ResultとEvidenceを必要とする。

## 2.2 Requirement / Test / Implementationの分離

``` text
Requirement / Contract
        ↓
Frozen Test Baseline
        ↓
Implementation
        ↓
Execution
        ↓
Observed Evidence
        ↓
PASS / PARTIAL / FAIL
```

実装結果に合わせてExpected Resultを変更しない。要件変更が必要ならTest
Runとは別変更として扱う。

新規L0〜L3の決定論的Testは、原則としてImplementation前に一度実行し、対象Capabilityが未実装または意図的に破壊された状態で`FAIL / ERROR`になることを確認する（RED
Check）。例外は`red_check_required = false`と理由をBaselineへ記録する。Capability
Probe、Static
Scan、既存CapabilityへのRegression追加など、意味のあるREDを構成できないTestへ形式的なFAILを強制しない。

Frozen BaselineはImplementation
Agentから論理的に独立させる。通常の実装変更とBaseline変更を同一変更として扱わず、Baseline変更には`approval_ref`、baseline
version更新、再hashを要求する。各Test Runは実行開始時にFrozen
Baselineのhashを再計算し、記録済み`validation_baseline_hash`と一致しないRunをPASS判定に使用しない。

## 2.3 Fail Closed

State Integrity、Environment Binding、Deterministic Risk
Validator、Human Approval / Execution Slot、Paid Service
Governance、Secret / Privacy、Required Data Freshness、Pre-submit
Revalidation、Restore /
Reconciliationで必要な検証が成立しない場合は安全側へ停止する。

## 2.4 TEST専用迂回路を作らない

TESTでは異常注入・時間操作・Stub・固定Datasetを利用できる。一方、Business
LogicがTEST専用の別経路を持ち、本番契約を迂回する構造にはしない。

------------------------------------------------------------------------

# 3. Test Environment

## 3.1 Environment Class

`TEST / PAPER / LIVE`

**TEST** - Unit / Component / Contract / Scenario / Historical
Replay用。 - Local Stub、Recorded Model Result、Historical
Providerを利用可能。 - 実Broker操作を行わない。 - Production State/Data
Rootへwriteしない。

**PAPER** - Real Providerと実時間を利用する仮想運用。 -
Broker実発注を行わない。 - Human
Decision、Notification、PC停止、API遅延等を実運用に近い条件で観測する。

**LIVE** - 実資金運用。 - 開始にはLive Readiness
ReviewとHuman開始判断を必要とする。

## 3.2 Environment Binding

各Environmentは少なくとも`state_id / data_root_id / environment / storage marker / Canonical State / Decision Queue / Execution Facts / Budget usage / Runtime locks`を共有しない。

`state_id / data_root_id / environment`不一致時は起動またはwriteを拒否する。
TEST→PAPER/LIVE、PAPER→LIVEへのState/Data直接流用は原則禁止。必要ArtifactはExport/Import契約を別途定義する。

## 3.3 初期物理配置

``` text
argus/
├─ tests/
├─ validation/
├─ fixtures/
├─ testdata/
└─ docs/test/

L:\emori\InvestmentAgentTestData\
├─ datasets\
├─ provider_stub\
├─ historical\
└─ generated\

L:\emori\InvestmentAgentData\   # Production
```

Test Data RootとProduction Data Rootはmarker / state_id /
environmentを共有しない。 `argus`への名称統一に伴うData Root
Renameは`TBD`。初期実装で既存Design
BaselineのPathを変更する必要はない。Path
renameだけを理由に既存`data_root_id`を変更しない。新しいRootを別Identityとして作成する場合だけ、新しい`data_root_id`を発行し、明示的な移行手順とEnvironment
Binding検証を通す。

# 4. Test Level

  ----------------------------------------------------------------------------
  Level        名称         主目的                                外部API
  ------------ ------------ ------------------------------------- ------------
  L0           Unit         純粋関数・Validator・Reducer等        原則なし

  L1           Component    Writer / Queue / Budget / Storage等   原則Stub

  L2           Adapter      Provider/Gateway契約、Raw→Normalize   Stub +
               Contract                                           fixture

  L3           Scenario     複数Componentを跨ぐ状態遷移・障害     Stub中心

  L4           Historical   過去時点でのSystem/Agent挙動          Historical
               Replay                                             Provider +
                                                                  Model

  L5           Real         J-Quants / EDINET / OpenAI等の実能力  Real
               Provider CV                                        

  L6           Realtime     実時間での仮想運用                    Real
               Paper                                              

  L7           Live         LIVE開始前の総合Gate                  Real +
               Readiness                                          Review
  ----------------------------------------------------------------------------

L0〜L3は決定論的・高速な回帰を優先する。L4以降は時間・コスト・Provider依存が増えるため、L0〜L3の代替にはしない。

# 5. Provider Test Strategy

Business LogicはProvider実装を直接識別しない。

``` text
Domain Logic
    ↓
ExternalServiceGateway
    ↓
Provider Interface
    ├─ Local Stub Provider
    ├─ Historical Provider
    └─ Real Provider
```

Stubが本番と異なる戻り値Schemaを持つことを禁止する。

## 5.1 Market Data

``` text
TEST normal logic  → LocalMarketDataStubProvider
Historical Replay → LocalHistoricalMarketDataProvider
Real Provider CV  → JQuantsProvider (Free / Light)
Realtime Paper    → JQuantsProvider (Light以上、Gate PASS後)
```

## 5.2 Disclosure

``` text
TEST normal logic  → LocalDisclosureStubProvider
Historical Replay → LocalHistoricalDisclosureProvider
Real Provider CV  → EDINETProvider
Realtime Paper    → EDINETProvider
```

## 5.3 Model Provider

**Deterministic Test:**
`RecordedModelProvider → frozen ModelResult fixture`
用途はPipeline、State transition、Queue、Budget accounting、Error
handling、Regression。

**Behavior / Integration Test:** `OpenAIProvider → Real Model API`
用途はAnalysis quality、Structured output成立性、Prompt/Schema
interaction、Historical Replay behavior、Cost/token/latency観測。

Real Model API試験もCost Gateを通し、Test BudgetはPAPER/LIVE
Budgetと分離する。 Model
snapshotが観測できない場合、完全再現可能とは扱わず`NOT_OBSERVABLE`をEvidenceへ残す。

------------------------------------------------------------------------

# 6. Test Data Architecture

## 6.1 Small Fixture

Git管理可能な小容量固定データ。Portfolio、Cash、Proposal、Execution、Config、User
Status、数日分Market Data、Disclosure数件、Recorded ModelResult等。

## 6.2 Raw Provider Fixture

ProviderのRaw形式を固定し、`Raw → Response Validation → Normalize → Persistence → Provenance`をAdapter単体で検証する。Secret/Account
ID等は除去する。

## 6.3 Historical Dataset

特定期間・Universeを固定した再利用可能Dataset。

## 6.4 Generated Failure Fixture

初期候補：
`HTTP 429 / HTTP 500 / timeout / invalid JSON / missing field / duplicate / out-of-order date / stale data / empty result / partial response / pagination途中失敗 / schema drift / disk full / storage disconnect / clock discontinuity`

具体的生成方式は`TBD`。

# 7. Test Dataset Generator

Historical Datasetは事前生成Batchで作成する。

``` text
Source Data
  ↓
Range / Universe Selection
  ↓
Raw Acquisition
  ↓
Availability-time / as-of Processing
  ↓
Normalize
  ↓
Dataset Freeze
  ↓
Manifest + Hash
```

Manifest最低項目：

``` text
dataset_id
dataset_schema_version
created_at
generator_version
source_provider
source_plan_tier
start_time
end_time
universe_definition
as_of_policy
raw_content_hash
normalized_content_hash
file_manifest_hash
known_limitations
```

Dataset作成後に内容が変わった場合、同じ`dataset_id`で上書きしない。

以下はImplementation Detailとして`TBD`：
`CLI command name / Python module layout / parallelism / compression / incremental update / dataset retention`。

# 8. Historical Time Gate / Look-ahead Prevention

Historical Replayでは`as_of_time`を必須入力とする。

``` text
Historical Clock = T
        ↓
Provider query
        ↓
available_at <= T のDataだけ返す
```

単に`record_date <= T`では不十分。`event_date / publication_time / provider_available_time / retrieved_at / revision_time`を区別する。
当時未公開の決算、後日修正値、未来の上場/廃止情報を返さない。RV-35で強制する。

LLM自身が学習済み知識として未来情報を知る可能性はData Provider Time
Gateとは別問題。Historical Model ReplayでのModel Knowledge
Leakage対策・評価方法は`TBD`。最低限、Promptでas-of制約を明示し、保存Evidence外の未来事実を根拠にした場合はLeakage候補として記録する。

# 9. Test Baseline / Oracle

各CV/RV実行前に固定する。

``` text
test_id
requirement_id
test_level
environment
fixture_id / dataset_id
fixture_hash
input
expected_result / invariant
acceptance_criteria
validator / oracle version
config_hash
code baseline
created_at
approved_by
approval_ref
red_check_required
pre_implementation_run_id
```

これらから`validation_baseline_hash`を生成する。Run中にBaselineが変わった場合、そのRunをPASS判定に使わない。

Baseline metadataは§18.1のcanonical JSONで保存する。Baseline recordは自己参照hashを避けるため、次のEnvelopeを持つ。

``` text
validation_baseline_hash
hash_payload
```

`validation_baseline_hash`は`hash_payload`だけを§18.1のcanonical JSON規則でserializationしたbytesに対するSHA-256とする。Baseline file全体のartifact hashと`validation_baseline_hash`を混同しない。

Baselineには`baseline_version`を必須化する。同じBaseline versionを上書きせず、Requirement / Expected / Acceptance Criteria / Test入力を変更する場合はHuman `approval_ref`を得て新しいBaseline versionを作成する。

必須metadata fieldが当該Testへ適用されない場合は、次の明示表現を使用する。

``` json
{
  "applicability": "NOT_APPLICABLE",
  "value": null
}
```

`NOT_APPLICABLE`をmissing、unknown、not configuredと混同しない。Fixtureを使わないL0 Testの`fixture_id / fixture_hash`、Datasetを使わないTestの`dataset_id`、Runtime Configurationを使わないTestの`config_hash`等に使用できる。

`requirement_id`はTest IDから追跡可能な安定IDとする。Environment Binding / L0 Marker JSON validationでは、`EB-L0-001 / 002 / 003 / 004 / 008 / 011 / 014 / 015 / 016`を`ENVIRONMENT-BINDING-MARKER-JSON`へtraceする。

Contractから期待結果が完全に決定される決定論的Test用のExact Oracleとして`EXACT_CONTRACT_ORACLE-v1`を定義する。このOracleは、参照Contractのhash、Test input、期待する型・値・error code・invariantを完全一致で判定し、実装結果から期待値を導出しない。

`pre_implementation_run_id`はBaseline Freeze時に予約し、そのBaselineのRED Checkで同じIDを使用する。形式は次とする。

``` text
RUN-<CAPABILITY-ID>-RED-<YYYYMMDDTHHMMSSffffffZ>
```

IDはUTC、microsecond 6桁、Windows filename-safeとする。既存IDと衝突した場合は上書きせずBaseline Freezeを停止する。

## 9.1 Baseline Protection

`validation/baselines/`は通常のImplementation
Changeから保護する。初期Local運用では最低限、Baseline変更を通常Code
Changeと別Commit/Changeとして扱い、Humanの`approval_ref`、baseline
version更新、hash更新を要求する。Test RunnerはRun開始時にBaseline
hashを再計算し、不一致なら`BLOCKED`とする。Run
Evidenceへ実行時hashを保存する。新規L0〜L3で`red_check_required = true`の場合、Baseline確定時点の`pre_implementation_run_id`が存在し、結果が`FAIL / ERROR`であることを確認する。

Dirty working treeでもBaseline Freezeを許可する。ただし`code baseline`はGit commitだけで表現せず、最低限次を保持する。

``` text
git_head_commit
working_tree_state = CLEAN / DIRTY
tracked_diff_sha256
capability_input_untracked_files[]
  path
  sha256
```

`tracked_diff_sha256`は、repository rootで次のcommandが出力するbytesに対するSHA-256とする。

``` text
git diff --binary --full-index --no-ext-diff --no-color --src-prefix=a/ --dst-prefix=b/ HEAD --
```

Capability入力となるuntracked Contract / Test / Fixture等はworkspace-relative pathとfile bytesのSHA-256を個別に記録する。Baseline Freeze後、Run開始時にこれらを再計算し、一致しないRunは`BLOCKED`または新しいBaselineに対する別Runとして扱う。

pre-commit hook、read-only
mount、別repository等による追加の物理保護方式は`TBD`とするが、上記はGate
A以前のHard Contractとする。

### 9.1.1 Test Baseline Coverage Extension

Critical Path Review等で、Frozen Testの既存Oracleが誤っているのではなく、確定済みContract requirementを検出するTest caseが不足していたことが判明した場合、その変更を`TEST_BASELINE_COVERAGE_EXTENSION`と分類する。既存Oracleのsemantic correctionである`TEST_BASELINE_CORRECTION`とは区別する。

`TEST_BASELINE_COVERAGE_EXTENSION`では、既存Frozen Test、Baseline、RED/GREEN Run、Review、およびEvidenceをimmutableのまま保持し、新しいFrozen Test versionとHuman `approval_ref`を持つ新しいBaseline versionでsupersedeする。追加TestはContract requirementから導出し、既存assertion / Oracleを弱めず、既存Testの削除および既存behavior expectationの変更を行わない。

Coverage extensionで追加するTestが現在のProductionの未実装または誤実装behaviorを検出する場合は`RED_REQUIRED`とする。Contract-required behaviorが現在のProductionですでに正しく実装され、Reviewでregression coverage不足だけが判明した場合は`RED_EXCEPTION_ALLOWED`とし、`red_check_required = false`を使用できる。Productionを人工的に壊してREDを作ってはならない。この扱いは§2.2の既存CapabilityへのRegression追加およびsemantically meaninglessなREDの例外を具体化するものであり、別のRED規則体系を作らない。

`RED_EXCEPTION_ALLOWED`のcoverage-extension recordまたはBaselineは、最低限次を保持する。

``` text
classification = TEST_BASELINE_COVERAGE_EXTENSION
red_check_required = false
reason
contract_requirement_ref
prior_review_finding_ref
current_production_behavior_evidence_ref
artificial_red_semantically_meaningless_reason
approval_ref
superseded_frozen_test_ref
superseded_baseline_ref
```

EB-L1-DATA-ROOT-MARKER-STOREのFINDING-02は、validなreload結果がintended Markerと異なる場合に`MarkerReloadVerificationFailed`を返すContract behaviorがProductionにすでに存在し、Frozen Test v0.2にそのregression Oracleだけが不足しているため、`TEST_BASELINE_COVERAGE_EXTENSION`かつ`RED_EXCEPTION_ALLOWED`として扱う。次Baseline候補は`EB-L1-DATA-ROOT-MARKER-STORE-v0.3`とし、v0.2を変更または上書きしない。

### 9.1.2 Baseline Revision RED

Freeze済みBaselineをsupersedeするrevision cycleでは、RED evidenceをBaseline全体でall-or-nothingに扱わず、Test IDごとに扱う。新旧Frozen Baselineのtest identityとtest contentを機械的に比較し、次を導出する。

- unchanged_test_ids: Test ID、Test Binding identity、およびOracle contentが同一のTest。対応するprior Formal RED evidenceがvalidであれば、それをTest ID単位で継承できる。
- delta_test_ids: 追加、内容変更、Test Binding変更、またはOracle変更があるTest。新しいRevision RED evidenceを必要とする。
- removed Test IDはdeltaに含め、requirement削除またはoracle weakeningの理由とHuman approvalを要求する。

membershipの正本はFrozen BaselineからFrozen Baselineへの機械diffである。Humanによる意味分類はこの導出結果を説明・reviewする補助情報であり、delta membershipを上書きしない。

Revision REDは、current worktreeからProductionを削除、rename、stash、または意図的に破壊して作らない。次の二つのrecorded stateをimmutable Git commit/refで特定し、git worktreeまたは同等の非変更isolated checkoutで、改訂後のFrozen Testのうちdelta testsだけを実行する。full rerunは、security policy、別のrequired gate、または独立reviewが別途要求する場合に限り追加する。

1. prior_production_git_ref: invalidated cycleのprior Productionを含むrecorded state。
2. pre_implementation_git_ref: 対象Production implementationが存在しないrecorded state。

改訂後test sourceが過去commitに存在しない場合は、改訂後Freeze commit/refからtestと必要最小test-only fixture/configをtemporary isolated checkoutへ導入する。Productionと実行contextは対象recorded stateのbytesを保持し、overlay path、source ref、hash、command、cleanupをEvidenceに記録する。このoverlayはProductionを変更しないtest harnessであり、未reviewのscript/codeが必要な場合は実行せずBLOCKEDとする。Revision REDに使用するBaselineとrecorded stateは再現可能なimmutable Git commit/refを持たなければならない。commit/push authorityはHumanにあり、test lifecycleはそれを自動化しない。

deltaの分類はSECURITY_INVARIANT / ADDITIVE / TIGHTENING / BINDING_CHANGE / RELAXING / RESTATEMENTとする。SECURITY_INVARIANTは明示的なfull RED evidenceを必須とし、分類によるwaiverを認めない。ADDITIVE / TIGHTENING / BINDING_CHANGEは新しいobligationであり、inherited REDだけで通過しない。RELAXING / RESTATEMENTは、binding/oracleの比較と実測結果が一致する場合だけRevision RED inheritance pathの対象にできる。security-sensitiveまたはnew-obligation deltaを分類名だけでwaiveしない。

delta Testごとの観測判定は次のとおりとする。ここでREDは事前固定されたexpected failureであり、環境障害やwrong-reason failureではない。

- prior ProductionでGREEN、pre-implementationでRED: RELAXING / RESTATEMENT候補のRevision RED evidenceはPASS。現在Productionに対するGREENへ進む。
- prior ProductionでRED、pre-implementationでRED: 実質的な新規obligation。Implementation workとその後のGREENが必要。
- pre-implementationでGREEN: vacuous、unbound、またはbinding-defectiveとしてBLOCKED。
- どちらかでERROR、environment/configuration failure、wrong-reason failure: 分類・解消するまでBLOCKED。

Revision REDは、Production存在後に改訂されたTestの「時系列上test-before-productionであった」という性質を再生成しないし、そのようにclaimしてはならない。代わりに、frozen delta review、generating/implementation Actorと異なるindependent reviewer、non-vacuityとbinding check、および二つのrecorded stateのObserved Revision RED resultsでpost-hoc weakeningを防ぐ。初回cycleのFormal RED semanticsは変更しない。waiverの連続回数上限はv0.1で導入せず、必要なら将来governanceで検討する。

初回cycleまたはnew obligationを導入するcycleの次gateはFormal REDとする。既存Frozen Baselineのeligible revision cycleは本節を優先し、Revision REDを次gateにできる。本節の採用前に作成されたADR、Baseline、Freeze、Pre-RED等の履歴recordに「次gate = Formal RED」または同趣旨の記載がある場合、その記載は作成時点の履歴として保持し、当該revision cycleの現在のgate routingには使用しない。個別Revision RED evidenceは、競合した履歴recordと本節による解消を明示する。

## 9.2 Oracle

Oracle種別：
`Exact / Invariant / Schema / State-transition / Quantitative Threshold / Human Review`

LLM文章の完全一致をOracleにしない。Behavior
TestではSchema成立、根拠参照、禁止事項違反、未来情報Leakage、Contradiction保持等の観測可能Contractを優先する。LLM
Quality Rubricは`TBD`。

Human Review
Oracleを使う場合は、最低限`reviewer / review_criteria_version / reviewed_at / decision / reason / evidence_refs`をEvidenceへ保存する。Human
Reviewは決定論的Testの代替ではない。

# 10. CV Mapping

設計書のCV-00〜50を正本とし、本書は主Test LevelとGate位置を割り当てる。

  ----------------------------------------------------------------------
  CV                     主Test Level           主な対象
  ---------------------- ---------------------- ------------------------
  CV-00                  L1/L5                  Windows Runtime / API
                                                bootstrap

  CV-01                  L3                     Loop / Sleep / Offline /
                                                Catch-up

  CV-02〜05              L2/L5                  Web / Market / J-Quants
                                                / EDINET

  CV-06〜09              L1/L3                  Persistence / Envelope /
                                                Queue

  CV-10〜11              L3/L6                  Notification / Status /
                                                Time

  CV-12〜13              L3                     Concurrency / version
                                                conflict

  CV-14〜15              L2/L3                  Polling / provenance

  CV-16A                 L0/L3                  Validator calculation

  CV-16B                 L3/L7                  Validator bypass
                                                resistance

  CV-17〜19              L4                     PIT / Historical
                                                Universe / revision

  CV-20〜21              L3                     Crash / Retry / Recovery

  CV-22                  L3                     Human CLI / Approval /
                                                Paste

  CV-23〜24              L1/L3                  Budget / Secret

  CV-25〜31              L1/L3                  Runner / Stage / Archive
                                                / Restore / Clock

  CV-32〜36              L1/L3                  Status / Alert / CLI

  CV-37〜39              L2/L3                  External Storage /
                                                Deploy / Raw-Normalized

  CV-40〜43              L1〜L3                 Lifecycle / Shared
                                                Service / Alert / Config
                                                Snapshot

  CV-44                  L3                     Storage / Environment
                                                Identity、write拒否

  CV-45                  L1/L3                  Paid Service Governance

  CV-46                  L2/L3                  ExternalServiceGateway
                                                Contract

  CV-47                  L3                     Backup / Storage
                                                Pressure / Position
                                                Watch Minimum Data

  CV-48                  L5                     J-Quants Free

  CV-49                  L5                     J-Quants Light

  CV-50                  L2/L5/L6               Service Registry /
                                                Freshness
  ----------------------------------------------------------------------

詳細Test Case IDへの分割は実装時`TBD`。CV Requirementを弱化しない。

## 10.1 J-Quants Free Gate --- CV-48

Authentication、Endpoint、Pagination、Schema、Raw保存、Normalize、Provenance、Error/Retry、Bulk
endpoint
structureを確認する。Freeで観測できないLight固有CapabilityをPASSにしない。

## 10.2 J-Quants Light Gate --- CV-49

Human契約承認後にCurrent coverage、Actual update timing、Universe-scale
acquisition、Rate-limit margin、Provider latency、Strategy
requirementとの比較を確認する。 CV-49はProbeではなく**Realtime
Paper開始Gate**。不達時に実測値に合わせAcceptance
Criteriaを変更してPASS化しない。

## 10.3 EDINET Gate

Authentication、Document list/acquisition、Raw
retention、Normalize、freshness、error handlingを検証。具体Endpoint
Case一覧は`TBD`。

# 11. RV Strategy

設計書のRV-01〜35を正本とする。RVは成立済みCapabilityが変更で壊れていないことを検証する。

## 11.1 Core RV

Coreは番号先行で選ばない。**変更箇所に関係なく、破壊された場合に資金・正本・承認・予約・Slot・Execution
Fact・Restore/Reconciliation・Environment
Bindingの整合性を損なう共通経路**を通るRVをCoreとする。

初期候補：`RV-01,02,03,04,05,06,09,10,11,16,17,20,21,25,29,30,31,34`

`RV-25`と`RV-29`はFunds /
reservation共通経路に関係するためCore候補へ含める。最終集合はこの基準に従いMVS成立時`TBD`。

## 11.2 Affected RV

``` text
Status / Notification change → RV-12 / 23 / 24 / 26 / 32 / 33
Budget / Model change        → RV-18 / 19 / 25 / 29
Historical / Provider change → RV-13 / 14 / 35
Deployment / Storage change  → RV-20 / 21 / 27 / 28 / 34
```

## 11.3 Full RV

`RV-01〜35`すべて。

必須候補： - Paper開始前 - LIVE Readiness前 - State Schema変更 -
Runtime/Writer変更 - Validator/Risk Policy変更 - Provider
Architecture変更 - Paid Governance変更 - Restore/Migration変更

実行時間が大きい場合の分割方法は`TBD`。

# 12. Failure Injection

TEST環境で意図的に再現する。

``` text
Process kill
Writer競合
stale lock
API timeout / 429 / 5xx
quota exhausted
invalid API key
schema drift
partial page
duplicate execution paste
disk unavailable / disk full
wrong data root / data_root_id mismatch
state_id mismatch
environment mismatch / ENVIRONMENT_BINDING_MISMATCH
POSITION_WATCH_DATA_UNAVAILABLE
BACKUP_STALE
LIMIT_BELOW_EXISTING_RESERVATION
COST_ESTIMATE_UNAVAILABLE
clock jump
sleep / resume
commit failure after API success
notification delivery failure
```

障害注入Framework/libraryは`TBD`。

# 13. Historical Validation

`Quant Backtest / Model Historical Replay / System Historical Scenario Test`を分離する。

**Quant Backtest:**
決定論的ルール・Portfolio計算等。LLM品質の証明には使わない。

**Model Historical Replay:**
当時入手可能なEvidenceをModelへ渡し、分析・Recommendation・Contradiction等を観測。Model未来知識の可能性を明示。

**System Historical Scenario Test:**

``` text
Historical Clock
→ Historical Provider
→ Selection
→ Analysis
→ Validator
→ Queue
→ Virtual Human Decision
→ Virtual Execution
→ State transition
```

Historical銘柄・期間・Scenario選定基準は`TBD`。結果を見て成功しやすい期間だけ採用しないよう、Dataset/Scenarioは実行前に固定する。

# 14. Realtime Paper Test

開始条件： 1. 必須CV PASS。 2. J-Quants Lightを利用する場合CV-49 PASS。
3. `environment = PAPER`。 4. Broker実発注経路無効。 5. Budget Policy
ACTIVE。 6. Secret / Storage / Backup / Alert / Recovery成立。 7. Full
RV必要範囲PASS。 8. HumanがPaper開始を承認。

初期期間は設計書どおり**1か月**を基本とする。

主計測：
`Provider update latency / PC unavailable time / missed-delayed acquisition / Catch-up / Notification window wait / Proposal件数 / Notification件数 / Human response time / Queue滞留 / TTL expiry / Human Load / Model cost-token / retry-failure rate / stale data / Position Watch / noisy alerts / System操作負荷`

1か月Paperだけでは長期Alpha、長期Drawdown、Regime耐性、長期配当性能、長期Portfolio最適性を証明しない。
具体的成功閾値はProvider CapabilityとStrategy
Requirement確定後に事前設定するため`TBD`。実測後の後付けは禁止。

# 15. Human Load Test

最低計測候補：

``` text
proposals/day
notifications/day
P0/day
queue_depth
median decision latency
p95 decision latency
expired_without_action
duplicate/superseded proposals
manual correction count
minutes/day spent on argus
```

許容閾値は`TBD`。Paperで実測し、過負荷ならNotification / Selection /
Watch Frequency等のB1 Parameter Break候補とする。

# 16. Cost Test

TestでもCost Governanceを無効化しない。
`provider / model / job_type / input_tokens / output_tokens / cached_tokens / estimated_cost / actual_cost / reserved_budget / settled_budget`を記録する。Test
BudgetとPAPER/LIVE Budgetを分離する。

**Test Budget Policyが`ACTIVE`でない場合、Real Model
APIを使うTestを開始しない。** Cost
estimateが取得できない場合も開始せず`BLOCKED`とする。API
Call前に最大費用を見積り・reserveし、Call後にobserved
usageでsettleする。

`TBD-12`はReal Model Testの実行頻度を決める項目でありBudget
Gateを延期する項目ではない。少なくともL4 Historical ReplayでReal Model
APIを初めて使用する前に、Test Budget上限と`TBD-12`を解決する。

# 17. Security / Secret Test

最低限： - API KeyがGit tracked fileに存在しない。 - Log / exception /
debug dumpにSecretがない。 - Raw HTTP headerを無加工保存しない。 -
FixtureにSecretを含めない。 - Backupに平文Secretを含めない。 -
TESTからLIVE Secretを誤使用しない。 - Environment Binding
mismatch時にwriteしない。

Secret scanning toolは`TBD`。

# 18. Test Result / Evidence Format

各Run最低項目：

``` text
test_run_id
test_id
requirement_id
validation_baseline_hash
environment
started_at
finished_at
code_version / commit
config_hash
dataset_id / fixture_hash
provider / plan / model
attempt_count
observed_result
metrics
evidence_refs
status
failure_class
notes
```

Human-readable SummaryはMarkdown生成。

``` text
validation/
├─ baselines/
├─ runs/
├─ evidence/
└─ reports/
```

Exact serialization / filename ruleは§18.1で定義する。

## 18.1 Serialization / Filename Contract

Baseline / Run metadataはhuman-readableかつmachine-readableなcanonical JSONとする。Raw command output等のEvidenceはUTF-8 textとする。追加Frameworkや外部serialization dependencyを必須にしない。

### Directory

``` text
validation/
├─ baselines/<capability-slug>/
│  └─ <baseline-version>.baseline.json
├─ runs/<capability-slug>/
│  └─ <test-run-id>.run.json
├─ evidence/<capability-slug>/<test-run-id>/
│  └─ <tool>-output.txt
└─ reports/<capability-slug>/
   └─ latest.md
```

Baseline / Run / Evidenceは物理分離する。`reports/`はBaseline / Run / Evidenceから再生成可能なProjectionであり、判定の正本にしない。

`capability-slug`、Baseline version、Run ID、Evidence filenameにはASCII英数字、dot、underscore、hyphenだけを使用し、space、colon、slash、backslash、Windows予約文字を使用しない。

### Canonical JSON

Canonical JSONを次に固定する。

``` text
encoding       = UTF-8
BOM            = none
newline        = LF
indent         = 2 spaces
object key     = Unicode code pointによる昇順で再帰的にsort
ensure_ascii   = false
final newline  = required
NaN / Infinity = prohibited
duplicate key  = prohibited
```

同じ論理値は同じbytesへserializationされなければならない。`validation_baseline_hash`は§9の`hash_payload`をこの規則でserializationしたbytesから計算する。

### Timestamp / ID

metadata timestampはUTC固定の次の形式とする。

``` text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

filenameおよびRun ID内では次のcolonなし形式を使う。

``` text
YYYYMMDDTHHMMSSffffffZ
```

Run IDはCapability、phase、UTC timestampを含む。RED Checkでは§9の`pre_implementation_run_id`を使用する。

### Hash / Reference

SHA-256は次の文字列表現へ固定する。

``` text
sha256:<64 lowercase hexadecimal characters>
```

Artifact参照は最低限次を持つ。

``` text
path
sha256
```

Pathはworkspace root基準のrelative pathとし、separatorは`/`を使用する。RunはBaselineをrelative path、`validation_baseline_hash`、Baseline artifact SHA-256で参照する。Runは各Evidenceをrelative path、SHA-256、kind / toolで参照する。EvidenceからRunへの逆参照は必須にせず、Run recordを参照の正本とする。

### Revision RED Evidence Record

Revision RED record v0.1は少なくとも次を保持する。referenceは可能な限りpath/refとSHA-256を持ち、per-test resultはstateごとにGREEN / RED / ERROR / BLOCKED、observed reason、raw Evidence refを記録する。

    record_id
    capability
    old_baseline_ref
    new_baseline_ref
    invalidation_ref_or_reason
    delta_test_ids
    unchanged_test_ids
    delta_classification
    prior_formal_red_evidence_ref
    prior_production_git_ref
    pre_implementation_git_ref
    per_delta_test_results
      test_id
      prior_production_result
      pre_implementation_result
    non_vacuity_result
    revised_freeze_ref
    reviewer
    decision
    reason
    timestamp

### UTF-8 Text Evidence

Raw stdout / stderr等はUTF-8、BOMなし、LF、final newlineありの`.txt`として保存する。stdout / stderrを結合する場合、Run metadataへcapture方式を記録する。Raw outputをBaseline metadataへ埋め込まない。

Run metadataには§18の既存必須項目に加え、最低限次を保存する。

``` text
record_type
serialization_version
capability_id
phase
command.cwd
command.argv
exit_code
baseline.path
baseline.validation_baseline_hash
baseline.artifact_sha256
code_baseline
red_check_outcome（RED Checkの場合）
```

Test processの`FAIL`とtest collection等の`ERROR`を区別する必要がある場合、`status`は§19の集合に従い、詳細を`observed_result`へ記録する。例えば意図した未実装Capabilityによるcollection errorは`status = FAIL`、`observed_result = ERROR`として記録できる。

# 19. PASS / PARTIAL / FAIL Policy

**PASS:** 事前固定Acceptance Criteriaを満たしEvidenceが存在。\
**PARTIAL:**
Test自体は実行できたが、要求範囲の一部についてしかEvidenceを得られなかった。Gate通過に使わない。\
**FAIL:** Acceptance Criteria不達、Contract/Integrity違反。\
**BLOCKED:**
前提条件が成立せずTest自体を実行できない。外部契約、API障害、未実装Dependency、Budget
Policy未設定、Baseline hash不一致等を含む。\
**UNASSESSED:** Capability値は測れたがStrategy Requirement等が未設定。

例：J-Quants FreeのままLight-only
CV-49を実行できない→`BLOCKED`。Lightで試験実行済みだがupdate
timingの十分な観測数がない→`PARTIAL`。Provider
latencyは測定済みだがStrategy要求Latency未設定→`UNASSESSED`。

# 20. Test Change Control

``` text
Test implementation bug
→ Test Code Fix
→ same baseline requirement

Requirement change
→ Change Proposal / Design update
→ new baseline
→ Retest
```

安全・資金・State Integrity・Paid
Governanceに関するExpected/Acceptance変更はHuman
Approvalなしに行わない。失敗Runを削除しない。

Freeze済みBaseline、finalize済みRun、finalize済みEvidenceはimmutableとする。同一filename / IDの上書き、Evidenceの差替え、失敗・BLOCKED・無効なRED Runの削除を行わない。

Baselineを変更する場合は新しいBaseline version、Human `approval_ref`、新しいhashを使用する。Run / Evidenceは一時ファイルへ書き、必要項目とhashを確定してからfinal filenameへ確定する。finalize後の訂正は旧Artifactを保持したまま新しいRun / Evidenceとして追加する。

`validation/reports/`は再生成可能なProjectionであり更新可能とする。Reportの更新によって参照元Baseline / Run / Evidenceを変更しない。

# 21. Development Workflowとの接続

``` text
Design FINAL
  ↓
Test Strategy v0.1
  ↓
External Accounts / API Keys
  ↓
argus-dev bootstrap
  ↓
L0/L1基盤Test
  ↓
Provider Stub / Dataset Generator
  ↓
L2/L3
  ↓
MVS成立
  ↓
Historical Dataset Freeze
  ↓
Test Budget上限 + TBD-12解決（Real ModelをL4で使用する場合）
  ↓
L4 Historical
  ↓
L5 J-Quants Free / EDINET
  ↓
Human approval → J-Quants Light
  ↓
CV-49
  ↓
L6 Realtime Paper
  ↓
L7 Live Readiness
```

J-Quants / EDINET API
Keyは取得済みだが、Secret値は本書・Git・Fixtureへ記録しない。

Test execution
orderについては本節を正本とし、`MVS成立 → Historical Dataset Freeze → L4 Historical Replay`の順とする。Dataset
Generator自体はMVS前に実装・試験してよい。

# 22. Implementation Detail --- TBD Register

  -------------------------------------------------------------------------------
  ID             項目                                             現時点
  -------------- ------------------------------------------------ ---------------
  TBD-01         Python test framework / plugin詳細               TBD

  TBD-02         tests/以下の具体的file/module構造                TBD

  TBD-03         Fixture factory/class構造                        TBD

  TBD-04         Dataset Generator CLI                            TBD

  TBD-05         Dataset圧縮形式                                  TBD

  TBD-06         Failure Injection実装方式                        TBD

  TBD-07         LLM Quality Rubric                               TBD

  TBD-08         Historical Model Knowledge Leakage評価法         TBD

  TBD-09         Historical銘柄・期間・Scenario                   TBD

  TBD-10         Core RV最終集合                                  TBD

  TBD-11         Full RVの分割・並列実行                          TBD

  TBD-12         Real Model Test実行頻度                          TBD

  TBD-13         Secret scanning tool                             TBD

  TBD-14         Test Result serialization / filename             RESOLVED（§18.1：canonical
                                                                  JSON metadata、UTF-8 text
                                                                  Evidence、Capability別directory、
                                                                  UTC ID、SHA-256 reference、
                                                                  finalized artifact immutable）

  TBD-15         Paper Human Load許容閾値                         TBD

  TBD-16         Paper成功閾値                                    TBD

  TBD-17         CI導入有無・CI構成                               TBD

  TBD-18         Coverage target                                  TBD

  TBD-19         Test Dataset retention                           TBD

  TBD-20         `InvestmentAgentTestData`のargus名称へのRename   TBD

  TBD-21         Baseline物理保護方式（pre-commit / read-only /   TBD
                 separate repo等）                                

  TBD-22         Static Analysis tool version / rule              TBD
                 configuration                                    

  TBD-23         Claude Code Review Contractのversion / prompt    TBD
                 format                                           

  TBD-24         pip-audit定期実行頻度（週次 / Gate前 / 両方）    TBD（Gate
                                                                  E以前に解決）
  -------------------------------------------------------------------------------

TBDは「忘れてよい」ではない。各項目は、その値が必要になる最初のImplementation
/
Gateより前に解決する。個別に解決期限が既知のTBDはRegisterの値欄へ期限を併記する。次回のTBD
Register構造見直し時に、`Resolve Before`列を独立列として追加するかを検討する。

# 23. Initial Test Artifact Structure

``` text
argus/
├─ docs/
│  └─ test/
│     └─ argus_test_strategy_v0.1.md
├─ tests/
│  ├─ unit/
│  ├─ component/
│  ├─ contract/
│  ├─ scenario/
│  └─ integration/
├─ fixtures/
│  ├─ market/
│  ├─ disclosures/
│  ├─ portfolio/
│  ├─ execution/
│  └─ model/
├─ validation/
│  ├─ baselines/
│  ├─ runs/
│  ├─ evidence/
│  └─ reports/
└─ testdata/
   └─ generated/
```

Directory構造は初期推奨でHard
Contractではない。Codexは合理的変更を提案可能。ただしEnvironment分離、Baseline/Evidence分離、FixtureのProduction非混入はHard
Contract。

# 24. Static Analysis / Code Review Strategy

静的解析とLLM Code Reviewは代替関係ではなく、異なるFailure
Modeを検出する。

## 24.1 Required Static Analysis

Python主体の初期実装では以下をRequired Tool Setとする。

``` text
Ruff
  → lint / import / common bug / style

Pyright
  → type consistency

Bandit
  → Python security pattern

pip-audit
  → dependency vulnerability
```

Tool version、詳細rule set、severity thresholdは`TBD-22`で固定する。

機械的に判定可能な事項をClaude Reviewだけに委ねない。

### 24.1.1 Suppression Governance

Static
Analysisの抑制は、Findingを消すための無制限な迂回路として使用しない。

対象例：

``` text
# noqa
# type: ignore
# nosec
tool configuration exclusion
rule disable
severity threshold relaxation
```

通常Moduleで新しいsuppressionを追加する場合、理由をCode /
Evidence上で追跡可能にする。

Critical Path
Moduleでは、新しいsuppression追加またはrule/configの緩和を**原則禁止**する。不可避な場合のみHuman
`approval_ref`を要求し、対象Finding、理由、代替案、影響範囲をEvidenceへ残す。

既存suppressionを変更・削除した場合も差分を記録する。

Static Analysis Evidenceには少なくとも以下を追加する。

``` text
suppression_count
suppression_added
suppression_removed
suppression_refs
```

### 24.1.2 Affected GateとRepository Healthの分離

Required Static Analysisは、次の二層を混同せずに実行・記録する。

1. **Affected Required Static Analysis**
   - Current Capability / Changeが責任を負うGate判定である。
   - 今回変更したProduction code、今回のFrozen Test、変更Productionから直接影響を受けるtest / module、およびContractまたは本Strategyが明示するaffected scopeを含む。
   - Current Changeが新規diagnosticを導入した場合、または既存diagnosticの件数、severity、rule、対象scopeを悪化させた場合はGate failureとする。
   - diagnosticのCurrent Changeへの帰属を一意に判定できない場合はfail-closedで`BLOCKED`とする。
2. **Repository Health Static Analysis**
   - repository全体を可能な限り継続観測し、既存diagnostic、technical debt、別Capability由来failureを見失わないためのhealth checkである。
   - 非cleanな結果はEvidenceとResultへ明記し、無条件に無視しない。
   - Current Changeと因果関係がなく、canonical evidenceまたはbaselineにより既知性を確認できるpre-existing diagnosticだけは、Repository Health findingとしてCurrent Capability Gateから分離できる。

「pre-existing」という申告だけでは分離を認めない。分離するdiagnosticには最低限、次を追跡可能にする。

``` text
diagnostic_id / rule
owner_or_source_capability
source_artifact_path
source_artifact_hash
first_observed_evidence_ref
current_observation_evidence_ref
status
resolution_policy
current_change_relation
count_and_severity_delta
```

Current Capability Gateから分離できるのは、次をすべて満たす場合だけとする。

- source artifactがCurrent Change開始前から存在し、そのpathとhashまたは同等のcanonical provenanceを確認できる。
- Current Changeが当該artifactを変更していない。
- diagnosticのrule、location、件数、severityおよび原因がCurrent Changeから独立している。
- Current Change前後で件数、severity、rule、対象scopeが悪化していない。
- owner / source capability、初回観測Evidence、status、resolution policyがcanonicalに記録される。
- Affected Required Static Analysisは当該diagnosticを含まずPASSしている。

superseded / immutable testは存在しないものとして扱わない。historical evidenceとして保持し、Repository Health scanの観測対象にできる。一方、後続Changeの都合で書き換えず、Current Capabilityのaffected scopeへ自動的に混入させない。既知diagnosticはRepository Health debtとして追跡し、将来の明示的なTest Baseline Correctionまたはcleanup Capabilityで解消する。

この分離はsuppressionではない。`type: ignore`、`Any`、`getattr`、tool config exclusion、rule disable、severity緩和等によりCurrent Changeのdiagnosticを隠すことを許可しない。repo-wide analysis自体は可能な限り実行し、そのraw outputと判定根拠をEvidenceへ保存する。Current GateがPASSしてもRepository Healthが非cleanなら、Run / Resultへ明記する。

`EB-L1-TEST-ENVIRONMENT-GUARD`のP-0015で観測されたPyright 7 diagnosticsは、immutableかつsupersededな`tests/component/test_data_root_marker_store_contract.py`（SHA-256 `1b9d148906a374027559b172989fbfceaf70adb5a0c0b23b0d607e43dd1a394b`）だけに存在し、P-0015の変更対象`src/argus/runtime/environment_guard.py`および当該Frozen Testのaffected Pyrightは0 diagnosticsである。P-0015はsource testを変更しておらず、7件のrule / location / count / severityを増加または悪化させていない。このため7件をRepository Health known debtへ分類し、P-0015再検証時のCurrent Capability Gateから分離できる。P-0015履歴自体は変更せず、別RunでGREENを再検証する。

## 24.2 Canonical Implementation / Verification Order

新規L0〜L3 Capabilityの基本順序は以下を正本とする。

``` text
Requirement / Contract
  ↓
Test Code
  ↓
Static Analysis of Test Code
  ↓
Baseline Freeze
  ↓
RED Check
  ↓
Implementation
  ↓
Required Static Analysis
  ↓
GREEN Test
  ↓
Affected CV / RV
  ↓
Claude Code Review（Critical Path）
  ↓
Finding disposition
  ↓
Gate / Commit
```

`red_check_required = false`の例外は§2.2に従う。

既存Frozen Baselineのrevisionは§9.1.2に従い、Baseline Freeze → Revision RED → Implementationまたはcurrent Production GREENとする。Revision REDは初回cycleのRED Checkを置き換えず、時系列上のtest-before-productionをclaimしない。

### 24.2.1 Expected Static RED

Pre-RED Static Analysisでは、確定済みContractに定義されているがProductionに未実装のsymbolをTest Codeが直接参照することで、Pyright等がdiagnosticを返す場合がある。次をすべて満たすdiagnosticだけを`EXPECTED_STATIC_RED`として許容し、Static Analysis of Test Code工程を完了扱いにできる。

1. root causeがContractに定義済みの未実装Production symbolまたは未実装Production型fieldである。
2. その他の許容diagnosticが、そのroot causeから機械的に派生したunknown-type diagnosticである。
3. Test Code自身の型誤り、syntax error、import path誤り、pytest / interpreter / configuration errorではない。
4. suppression、`Any`、`getattr`、`type: ignore`等で未実装APIを迂回していない。
5. Contract path / hash、未実装symbol、root diagnostic、派生diagnostic countをEvidenceへ保存する。

`EXPECTED_STATIC_RED`はStatic AnalysisのPASSではない。Pre-RED工程に限った明示的な完了状態であり、Production Implementation後のRequired Static Analysis / GREEN判定には使用しない。Implementation後は同じdiagnosticを許容せず、通常のRequired Static AnalysisをPASSさせる。

root causeを未実装Production APIへ一意に帰属できない場合、Test CodeのStatic Analysis工程は未完了とし、Baseline Freezeへ進まない。

既存Capabilityの通常変更では、Baseline/REDを新規作成しない場合がある。その場合も以下を最低順序とする。

``` text
Code Change
  ↓
Ruff
  ↓
Pyright
  ↓
Bandit
  ↓
Unit / Component Test
  ↓
Affected CV / RV
  ↓
Claude Code Review（Critical Pathの場合）
```

Dependency変更時は`pip-audit`を必須とする。

さらに、依存を変更していなくても脆弱性は後から公表されるため、`pip-audit`を定期実行する。定期頻度は`TBD-24`。Gate
E（Paper Ready）およびGate F（Live
Readiness）では直近の`pip-audit`結果を必須Evidenceとする。

## 24.3 Claude Code Review

Claude Reviewは**Semantic Static / Contract Review**として使用する。

最低Review観点：

``` text
Design contract violation
State integrity
Writer bypass
Validator / Hard-rule bypass
Fail-closed violation
Concurrency / race
Idempotency
Retry / Durable Stage consistency
Security / secret boundary
Cost / Paid Service Governance
Environment isolation
Historical future-data leakage
Test integrity / acceptance weakening
```

Critical-path ChangeではClaude ReviewをRequiredとする。

初期Critical Path：

-   Canonical Writer
-   Deterministic Risk Validator
-   Approval
-   Slot / Reservation
-   Human Correction
-   Budget Gate
-   Paid Service Governance
-   Environment Binding
-   ExternalServiceGateway / Provider boundary
-   Historical Time Gate
-   Restore / Migration

Critical
Path判定を人間の記憶だけに依存させない。`module/path → critical domain → applicable contract reference`のMappingをReview
Contractに保持する。具体的pathは実装構造確定時に設定する。

### 24.3.1 Minimum Review Input Contract

Claudeへ最低限以下を入力する。

``` text
change diff
changed file full text
directly related files required to understand the change
applicable Design Contract excerpts
applicable Test Strategy excerpts
affected CV / RV
Static Analysis result
Automated Test result
code commit / change identifier
```

設計書全文を毎回入力することは要求しない。Review
Contractは観点ごとに参照すべきDesign/Test
ContractをMappingし、変更Domainに必要なContract excerptだけを選択する。

概念：

``` text
Changed Module / Domain
        ↓
Critical Path Map
        ↓
Review Concern
        ↓
Contract Reference Map
        ↓
Design §xx / Test Strategy §yy / affected CV-RV
```

Contract Reference Mapの初期例：

``` text
Canonical Writer / bypass
  → DesignのSingle Writer / optimistic version / canonical commit契約

Fail Closed / Budget Gate
  → DesignのFail Closed / Budget Policy / pre-submit revalidation契約

Historical future-data leakage
  → DesignのHistorical Time / PIT契約 + Test Strategy §8

Environment Binding
  → DesignのStorage Identity / Environment Binding契約 + Test Strategy §3

Test integrity / acceptance weakening
  → Test Strategy §2.2 / §9.1 / §20 / §24.1.1
```

正確なDesign section番号・Review
prompt形式は`TBD-23`で固定するが、上記Minimum Input ContractとReference
Mappingの存在自体はHard Contractとする。

### 24.3.2 Review Scope Boundary

Claude
Reviewは静的な契約整合・意味構造のReviewであり、以下を単独では判定しない。

``` text
runtime behavior
actual execution success
performance / latency
real provider behavior
real market-data quality
actual notification delivery
actual recovery behavior
investment performance
```

これらはAutomated Test、CV/RV、Real Provider CV、Historical
Replay、Paper等のObserved Evidenceで判定する。

Claudeの`NO_FINDING`はSystem/Testの`PASS`を意味しない。Claude
Findingも決定論的Test結果を上書きしない。

## 24.4 Claude Finding Disposition

Claude Review結果には最低限以下を保存する。

``` text
reviewer_model
review_contract_id
review_contract_version
reviewed_at
code_commit
review_input_manifest_hash
contract_refs
findings
severity
rationale
evidence_refs
review_source_ref
review_source_record_sha256
```

`review_input_manifest_hash`は、Review開始前に確定したReview Input Manifest artifact自体のSHA-256とする。複数artifact hashの文字列連結等から暗黙生成しない。Manifestは§18.1のcanonical JSONとし、最低限、Capability、Review Contract、Contract、Frozen Test、Production、Baseline、GREEN Run、relevant Evidence、code commit、working tree stateをpathとhashで列挙する。

`reviewed_at`は推測値やReviewerが本文中で自己申告した時刻ではなく、取得可能なexternal observer provenanceを正本とする。Claude Code session JSONLが利用可能な場合、Review response本文を保持するrecordのtimestampを`reviewed_at`とする。external observer metadataが取得不能な場合はReview provenanceをincompleteとして扱い、Critical Path CapabilityをCloseしない。

`review_source_ref`は最低限、次を保持する。

``` text
source_type
log_path
session_id
record_id
message_id
```

Claude Code session JSONLでは、`review_source_record_sha256`をReview response本文を保持するoriginal JSONL record 1件のraw bytesに対して計算する。trailing LFは含めず、JSON parse後の再serialization、Review本文のcopy、追記され得るsession log全体のhashを使用しない。表現は§18.1の`sha256:<64 lowercase hex>`とする。

Reviewer-reported provenanceとexternal-observer provenanceは区別して記録し、両方が存在する場合はexternal-observer provenanceを時刻・message identityの正本として優先する。

Findingは以下のいずれかで閉じる。

``` text
FIXED
RISK_ACCEPTED
DESIGN_CHANGE
DISPROVED_WITH_EVIDENCE
```

`CRITICAL` Findingが未解決のままGateを通過しない。

`MAJOR / MODERATE / MINOR`は必ずDispositionを持つ。単に無視してCloseしない。どのSeverityを将来Hard
Blockへ追加するかは実測後にBreakで変更可能。

## 24.5 Static Analysis / Review Evidence

各Required Toolについて以下を保存する。

``` text
tool
tool_version
rule_config_ref
rule_config_hash
execution_command
code_commit
executed_at
exit_status
result
diagnostic_error_count
diagnostic_warning_count
finding_count_by_severity
suppression_count
suppression_added
suppression_removed
suppression_refs
report_ref
```

Raw stdout / stderrは§18.1のEvidence側へ保存し、Static Analysis recordまたはRun metadataからrelative pathとSHA-256で参照する。

`EXPECTED_STATIC_RED`の場合は上記に加えて次を保存する。

``` text
expected_static_red = true
contract_ref
contract_hash
root_cause
root_diagnostic_count
derived_unknown_type_diagnostic_count
```

通常PASSの場合は`expected_static_red = false`とする。Expected Static REDをsuppression countの減少やrule緩和によって作らない。

Claude Reviewも同じRelease / Change Evidenceへ関連付ける。

Static Analysis
rule/configを緩和した結果だけで既存Findingが消えた場合、それを通常のCode
Fixと同一視しない。Critical Pathでの緩和は§24.1.1のHuman
Approval対象とする。

------------------------------------------------------------------------

# 24.6 Runtime Identity Corrective Test Binding Amendment

Runtime Identity corrected revised candidate は `tests/unit/test_runtime_identity_contract.py` の historical `RI-L0-001..028` binding をbyte-for-byte維持し、`tests/unit/test_runtime_identity_critical_path_corrections.py` の F1-F4 obligationへ新規 canonical Test ID `RI-L0-029..034` を割り当てる。旧 revised Freeze が同一IDへ historical obligation と corrective case を混在させた granularity error を訂正し、per-obligation Revision REDを可能にする。

| Finding | Canonical Test ID | Supplemental function | Delta class | Decision / Contract clause |
|---|---|---|---|---|
| F1 | `RI-L0-029` | `test_ri_l0_029_invalid_rfc3339_boundaries_are_rejected_without_repair` | `SECURITY_INVARIANT` | invalid inputをrepairせずfail closedに拒否する新規境界。prior Productionで `+05:60`、`-05:60`、`T24:00` がRED |
| F1 | `RI-L0-030` | `test_ri_l0_030_valid_rfc3339_boundaries_remain_accepted` | `RESTATEMENT` | historical `RI-L0-015` accepted-RFC3339 obligationの境界control。prior ProductionでGREEN |
| F2 | `RI-L0-031` | `test_ri_l0_031_pathologically_deep_json_is_a_typed_malformed_failure` | `SECURITY_INVARIANT` | decoder recursionをpublic API外へ漏らさない新規typed fail-closed境界。prior ProductionでRED |
| F3 | `RI-L0-032` | `test_ri_l0_032_serializer_maps_unrepresentable_utc_edges_to_value_error` | `SECURITY_INVARIANT` | out-of-range UTC conversionをbounded failureにする新規fail-closed境界。prior ProductionでRED |
| F3 | `RI-L0-033` | `test_ri_l0_033_serializer_supports_representable_datetime_range_edges` | `RESTATEMENT` | historical `RI-L0-024` canonical serializer obligationのrange control。prior ProductionでGREEN |
| F4 | `RI-L0-034` | `test_ri_l0_034_returns_first_defect_detected_by_validation_pipeline` | `RESTATEMENT` | Human Design Authority clarification。global error precedenceまたは新規security obligationを追加せず、prior ProductionでGREEN |

Corrected Pre-RED は両 test file を static verification の対象とし、Test ID の union が exactly `RI-L0-001..034`、primary historical binding が exactly `RI-L0-001..028`、corrective binding が exactly `RI-L0-029..034` であることを機械確認する。historical IDのbinding/oracleは変更しない。canonical ADR、Contract、本 amendment、両 test file、新しいbaseline invalidation record、static configurationをcandidate inputとしてhashする。

F1-F3 の新規 fail-closed obligation `RI-L0-029`、`RI-L0-031`、`RI-L0-032` は `SECURITY_INVARIANT` とし、Revision RED executionをmandatoryかつnon-waivableとする。`RI-L0-030` と `RI-L0-033` は既存成功意味の境界control、`RI-L0-034` はF4 clarificationであり `RESTATEMENT` とする。historical `RI-L0-002`、`015`、`016`、`020`、`024`、`026` は unchanged/inherited であってdelta membershipに含めない。

本 specification revision では Formal/Revision RED または corrective GREEN を実行しない。既存 corrective observations を Revision RED に昇格させない。gate order は revised Pre-RED candidate validation → revised Freeze → Human commit checkpoint → Revision RED とする。

# 25. Completion Gates

## Gate A --- Test Foundation Ready

-   Test Runner動作。
-   TEST Environment Binding成立。
-   Fixture読込成立。
-   Baseline / Run / Evidenceを分離保存。
-   Baseline変更に`approval_ref`を要求し、Run時hash照合が機械的に成立。
-   新規L0〜L3の代表TestでRED Check Evidenceを保存できる。
-   Secret非混入。
-   L0/L1代表Test実行可能。
-   Required Static Analysisを実行可能。

## Gate B --- MVS Verification Ready

-   Required CV fixture存在。
-   Core Runtime CV実行可能。
-   Provider Stubが同一Interface。
-   主要Failure Injection再現可能。
-   RV-16実行可能。
-   Required Static Analysisが対象Changeで完了し、unresolved High /
    Critical Findingなし。
-   Critical Path変更に対するClaude Review Evidenceが存在。
-   unresolved `CRITICAL` Claude Findingなし。
-   `MAJOR / MODERATE / MINOR` FindingはすべてDispositionを持つ。

## Gate C --- Historical Ready

-   Dataset Generator成立。
-   Dataset Manifest / Hash成立。
-   Historical Clock成立。
-   `as_of_time` Time Gate成立。
-   RV-35 PASS。

## Gate D --- Real Provider Ready

-   J-Quants Free / EDINET Real Adapter CV実行。
-   Raw / Normalize / Provenance成立。
-   Service Registry / Freshness観測成立。

## Gate E --- Paper Ready

-   J-Quants Free CV PASS後、HumanがLightを明示承認。
-   CV-49 J-Quants Light Capability PASS。
-   必須CV PASS。
-   Full RV必要範囲PASS。
-   PAPER Environment Binding成立。
-   Broker実発注無効。
-   Budget / Alert / Backup / Recovery成立。
-   Required Static Analysisが完了し、unresolved High / Critical
    Findingなし。
-   Critical Path全体のRequired Claude Reviewが完了。
-   unresolved `CRITICAL` Claude Findingなし。
-   Claude Findingに未Disposition項目なし。
-   直近`pip-audit`結果が存在し、unresolved High / Critical
    vulnerabilityなし。
-   Human開始承認。

## Gate F --- Live Readiness

-   1か月Paper結果Review。
-   Human Load Review。
-   Cost Review。
-   Provider latency / Strategy fit Review。
-   unresolved Critical / P0 Incidentなし。
-   必須CV/RV PASS。
-   Required Static Analysisを最終対象Baselineで再確認し、unresolved
    High / Critical Findingなし。
-   Critical Path全体のRequired Claude Reviewが完了。
-   unresolved `CRITICAL` Claude Findingなし。
-   Claude Findingに未Disposition項目なし。
-   直近`pip-audit`結果が存在し、unresolved High / Critical
    vulnerabilityなし。
-   LIVE固有ConfigurationをHuman確認。
-   Humanが実資金開始を別途判断。

# 26. v0.1.3 Revision Summary

v0.1.2までの変更に加え、本版では前回Reviewの残件を閉じた。

1.  Gate BへRequired Static Analysis完了、unresolved High /
    Criticalなしを追加。
2.  Gate BへCritical Path変更のClaude Review Evidence、unresolved
    `CRITICAL`なし、その他FindingのDisposition完了を追加。
3.  Gate E / FへRequired Static Analysis完了条件を追加。
4.  Gate E / FへCritical Path全体のClaude Review完了、unresolved
    `CRITICAL`なし、未Disposition Findingなしを追加。
5.  Gate E / Fへ直近`pip-audit` Evidenceとunresolved High / Critical
    vulnerabilityなしを追加。
6.  `TBD-24`としてpip-audit定期実行頻度をTBD Registerへ登録し、Gate
    E以前に解決することを明記。
7.  個別解決期限が既知のTBDはRegisterへ期限を併記する運用を追加。
8.  Suppression Governance（Critical
    Pathでの抑制・rule緩和を原則禁止、例外はHuman
    approval）をRevision履歴上の独立契約として明示。
9.  Minimum Review Input Contract / Contract Reference
    MapをRevision履歴上の独立契約として明示。
10. Review Scope BoundaryをRevision履歴上の独立契約として明示。
11. Claude Finding
    Disposition（`FIXED / RISK_ACCEPTED / DESIGN_CHANGE / DISPROVED_WITH_EVIDENCE`）をRevision履歴上の独立契約として明示。
12. RED Checkを含むCanonical Implementation / Verification
    OrderをRevision履歴上の独立契約として明示。
13. pip-audit定期実行をRevision履歴上の独立契約として明示。
14. Gate EのJ-Quants条件をFinal Designと一致させ、Free CV PASS → Human
    Light approval → CV-49 PASS → Paperを必須化。
15. Required Static AnalysisをAffected GateとRepository Healthへ分離し、Current Change attribution、pre-existing diagnosticの証明、superseded / immutable artifact、known debt追跡の規則を追加。

------------------------------------------------------------------------

# 27. Final Principle

argusのTestは、設計を正しいと証明するための儀式ではない。

``` text
Design Hypothesis
      ↓
Implementation
      ↓
Measurement
      ↓
Evidence
      ↓
Keep / Fix / Break
```

CV / RV / Historical /
Paperの実測が設計想定と衝突した場合、実測を隠したりAcceptance
Criteriaを後付け変更して設計を守らない。

**実測Evidenceを設計仮説より上位に置く。**
