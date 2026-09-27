# argus Runtime Foundation Bootstrap Contract v0.1

**Document Type:** Draft Contract / Gap Analysis  
**Version:** `0.1`  
**Status:** `DRAFT / DESIGN_DECISION_REQUIRED`  
**Source Prompt:** `ARGUS-P-0021-v1`  
**Created At:** `2026-09-20T11:05:49.902727Z`

## 1. Purpose and authority

Runtime Bootstrapとは、PC起動時の自動起動だけではなく、argus processが通常Runtime Loopへ入る前に、実行環境、正本、Configuration、Secret、Storage Binding、Recovery状態を安全に確定する起動処理である。

本書は実装開始のためのACCEPTED Contractではない。System Designに規定済みの要求を抽出し、実装可能な要求とDesign Authority判断が必要なGapを分離するDraftである。Gapを推測で補完してはならない。

正本の優先関係:

1. `docs/source/argus_design_source_v0.1.md`
2. `docs/test/argus_test_strategy_v0.1.3.md`
3. `docs/adr/argus_architecture_decision_records_v0.1.md`
4. Environment Bindingの詳細については`docs/contracts/argus_environment_binding_contract_v0.1.md`

Environment BindingのCLOSED Capabilityを変更・複製しない。

## 2. Canonical sources

| Artifact | Relevant section | SHA-256 |
|---|---|---|
| System Design v0.1.7 FINAL | §2.5、§2.6、§4〜4.7、§46E、§49、§52.3 | `5b661e32c958e491875d713f72a265d2016357b44c090fff42dc29fad6444fc0` |
| Environment Binding Contract v0.1 | §2、§4、§5.2、§7、§8、§9.4〜9.5 | `c37471bfc8b955a28be45088d234a48fc13937f5bed77a09f055d65857d77426` |
| Test Strategy v0.1.3 | §3、§18、§24、§25 Gate A | `f2faf8d7247a1b75060bb502deacd425268fffd62c6b57db0ac5c224654dacb8` |
| ADR v0.1 | ADR-003、ADR-004、ADR-006 | `f0fac76a09c418a4eaca9ede1c8cb60f7a1544b38537f2043a4a43f444338c16` |
| Foundation Readiness Assessment | 全体 | `1011916cfdcdcc07593b1d27dfa78b5fc8a27099f4278b9cc4f791640f25e2c7` |

## 3. Existing implementation boundary

現在存在するProduction:

- `src/argus/runtime/environment.py`
- `src/argus/runtime/data_root_locator.py`
- `src/argus/runtime/data_root_marker.py`
- `src/argus/runtime/environment_binding.py`
- `src/argus/runtime/data_root_marker_store.py`
- `src/argus/runtime/environment_guard.py`

これらはEnvironment、Marker、Store、Binding comparison、TEST startup/write guardを提供する。次は存在しない。

- Runtime Manifest loader/validator
- `config.json` loader/schema/validator
- Secret bootstrap
- Canonical State loader/recovery orchestrator
- Runner lock implementation
- unified Runtime Bootstrap orchestrator/result model

## 4. Canonical startup sequence

System Design §4.2「毎回の起動」のnormative sequenceは次の7段階である。順序を変更して実装してはならない。

1. `SYSTEM.md`と固定されたManifestを読む。
2. 実行ホスト、Local project path、network状態、使用可能Adapter、Model API設定を記録する。
3. Bindingで正本を取得し、`state_id`、Schema、Commit、適用Policy / System / Code hashを照合する。
4. inbox未処理、outbox未配信、UNKNOWN Order、Projection遅延を復旧する。
5. 有効Configuration、利用データ時刻、`user_status`、導出`human_capacity`、`execution_slot`、各Jobの`last_success / retry state`を読む。
6. 未実行期間、Retry Pending、未処理inboxを検出し、Relevance Check後にCatch-upする。
7. 通常Loopへ入る。

正本を確定できない場合、新しい空Portfolioを作らず`RECOVERY_REQUIRED`とする。

### 4.1 規定済み依存関係

- §4.1: Development `InvestmentAgent-Dev/`とRuntime `InvestmentAgent/`を物理分離する。絶対pathは実装時Manifestで固定する。
- §4.0: Configuration、User Status、Domain State、Runtime State、Secretを分離する。
- §4.4: SecretはEnvironment VariableまたはOS-protected secret storeから取得し、Manifest/Configには値を書かない。
- §4.6: System/Config Schema/State Schema versionを分離し、不一致時は`MIGRATION_REQUIRED`として通常Runnerを開始しない。
- §2.5: Runner lockは通常Loopの二重副作用を防ぎ、確認不能な既存lockは`RUNNER_LOCK_RECOVERY_REQUIRED`とする。
- §4.7 / ADR-006: external Data RootのidentityはMarkerで検証し、未接続は`DATA_STORAGE_UNAVAILABLE`とする。
- Environment Binding Contract §5.2 / §8: startup時とwrite boundaryでfresh verificationを行い、BindingFailure時はsuccessへ進めない。

### 4.2 未確定のsequence接続

次の詳細順序はcanonical文書から一意に決まらない。

- Manifest validationとConfig validationのどちらを先に完了するか。
- ExpectedEnvironmentBindingとDataRootLocatorをManifest/Config/別Runtime inputのどこから構築するか。
- Runner lock取得がCanonical State recoveryの前か後か。
- Secret availability checkをManifest、Config、Adapter discoveryのどの境界で行うか。
- inbox/outbox recoveryをread-only validationとして行う範囲と、Writer lock取得後に行う範囲。
- Bootstrap successから通常Loopへ渡すimmutable contextの型とlifetime。

これらはDesign Authority decision前にTest Oracleへしてはならない。

## 5. Requirement / Gap Matrix

分類:

- `CONTRACT_READY`: 現正本だけでrequirementの意味が一意。
- `PARTIALLY_SPECIFIED`: high-level requirementはあるがpublic API/schema/orderが不足。
- `UNSPECIFIED`: 実装Oracleを作るための決定がない。
- `CONFLICTING`: 正本間で両立しない。今回該当なし。

| # | Requirement | Classification | Canonical source | Current implementation | Missing decision | DA required |
|---:|---|---|---|---|---|---|
| 1 | Runtime Bootstrapの責務境界 | `PARTIALLY_SPECIFIED` | Design §4.2 | なし | orchestrator input/outputとside-effect boundary | YES |
| 2 | `SYSTEM.md`の役割 | `CONTRACT_READY` | Design §4 | なし | content schemaは別途必要だがroleは一意 | NO for role |
| 3 | Manifest filename=`manifest.json` | `CONTRACT_READY` | Design §52.3、§4.4 | なし | なし | NO |
| 4 | Manifest schema/required fields | `UNSPECIFIED` | Design §4.1/§52.3は存在のみ | なし | exact fields/types/unknown-field/version rules | YES |
| 5 | Supported Runtime OS=Windows | `CONTRACT_READY` | Design §2.6 | なし | exact edition/build/filesystemはCV-00で記録 | NO |
| 6 | host/path/network/adapter/model record | `PARTIALLY_SPECIFIED` | Design §4.2 step 2 | なし | record type、required/optional、hash/provenance | YES |
| 7 | Dev/Runtime physical separation | `CONTRACT_READY` | Design §4.1/§4.6/§52.3 | EB locator/guardのみ | deploy/runtime root enforcement mechanism | YES for implementation API |
| 8 | project/runtime path semantics | `PARTIALLY_SPECIFIED` | Design §4.1 | `DataRootLocator`はData Rootのみ | normalization、relative/absolute policy、junction handling | YES |
| 9 | `state_id` expected source | `UNSPECIFIED` | EB Contract §4: Runtime inject、Data Root由来禁止 | `ExpectedEnvironmentBinding`型のみ | Manifest/Canonical State/other authorityの選択 | YES |
| 10 | Data Root locator source | `UNSPECIFIED` | Design §4.7、EB Contract §2 | `DataRootLocator`型 | Manifest/Config/CLI inputの選択 | YES |
| 11 | ExpectedEnvironmentBinding construction source | `UNSPECIFIED` | EB Contract §4で具体形式を未定義 | constructor実装済み | external authorityとload API | YES |
| 12 | startup Binding API integration | `PARTIALLY_SPECIFIED` | EB Contract §5.2/§8/§9.4 | TEST用`verify_test_environment_startup`、generic load/verify | PAPER/LIVEを含むbootstrap call boundary | YES |
| 13 | Environment closed set TEST/PAPER/LIVE | `CONTRACT_READY` | Design §4.1、EB Contract | `Environment` | なし | NO |
| 14 | `config.json` filenameとdomain areas | `CONTRACT_READY` | Design §4/§4.0 | なし | field詳細は別row | NO |
| 15 | initial config schema | `UNSPECIFIED` | Design §4.0はdomain listのみ | なし | exact schema/version/unknown-field/default rules | YES |
| 16 | `UNCONFIGURED` external representation | `PARTIALLY_SPECIFIED` | Design冒頭、各Policy section | なし | JSON value/tag、field-specific applicability | YES |
| 17 | `config_version` required | `CONTRACT_READY` | Design §4.0 | なし | type/initial valueは未定 | YES for schema detail |
| 18 | `config_hash` canonicalization | `UNSPECIFIED` | Design §4.0は保存要求のみ | なし | serialization、algorithm input、prefix representation | YES |
| 19 | Config validation failure | `PARTIALLY_SPECIFIED` | Design §2.5/§4.6 | なし | malformed/schema/domain failure codesとaggregation | YES |
| 20 | Config Snapshot at Job boundary | `CONTRACT_READY` | Design §4.0 | なし | bootstrapとJob factoryのAPI接続は後段 | NO for invariant |
| 21 | `user_status.json` | `PARTIALLY_SPECIFIED` | Design §4.0、§21 | なし | exact schema、initialization、missing/corrupt handling | YES |
| 22 | Canonical State acquisition | `PARTIALLY_SPECIFIED` | Design §4/§13/§4.2 | なし | loader/result/API、read consistency | YES |
| 23 | Schema/Commit/Policy/System/Code hash comparison | `PARTIALLY_SPECIFIED` | Design §4.2 step 3 | なし | sources、comparison order、failure mapping | YES |
| 24 | Secret source | `PARTIALLY_SPECIFIED` | Design §4.4 | なし | Env var/OS storeの初期必須subsetとadapter boundary | YES |
| 25 | secret reference metadata | `PARTIALLY_SPECIFIED` | Design §4.4: name/provider/required status | なし | Manifest/Config locationとschema | YES |
| 26 | missing/invalid Secret failure | `PARTIALLY_SPECIFIED` | Design §2.5: invalid key=`CONFIG_REQUIRED` | なし | missing secret code、aggregation、redaction-safe detail | YES |
| 27 | Adapter/Model/network availability | `PARTIALLY_SPECIFIED` | Design §4.2 step 2、ADR-003 | なし | probe禁止/許可、offline success条件、result type | YES |
| 28 | inbox/outbox/UNKNOWN/Projection recovery | `PARTIALLY_SPECIFIED` | Design §4.2 step 4 | なし | per-item recovery API、write boundary、partial failure | YES |
| 29 | execution_slot/Job runtime state read | `PARTIALLY_SPECIFIED` | Design §4.2 step 5 | なし | Canonical State schemaとmissing/corrupt semantics | YES |
| 30 | Catch-up + Relevance Check | `PARTIALLY_SPECIFIED` | Design §4.2 step 6、§46E | なし | bootstrapはplan作成までか実行までか | YES |
| 31 | Runner lock validation | `CONTRACT_READY` | Design §2.5 | なし | platform adapter/APIは未実装 | YES for module contract |
| 32 | cannot determine canonical state=`RECOVERY_REQUIRED` | `CONTRACT_READY` | Design §4.2 | なし | bootstrap result modelへのmapping | YES for type |
| 33 | schema mismatch=`MIGRATION_REQUIRED` | `CONTRACT_READY` | Design §4.6 | なし | version compatibility matrix | YES |
| 34 | Binding/storage failure mapping | `CONTRACT_READY` | EB Contract §7 | EB modules実装済み | Bootstrapはfailureを保持し通常Loop拒否 | NO |
| 35 | unified Bootstrap result/failure model | `UNSPECIFIED` | scattered status/error namesのみ | なし | success type、failure collection/precedence/details | YES |
| 36 | unsupported runtime/Manifest mismatch failure | `UNSPECIFIED` | Windows support requirementのみ | なし | error codes、detail、whether migration/config remediation | YES |
| 37 | Runner lock acquisition order | `PARTIALLY_SPECIFIED` | Design §2.5/§4.2 | なし | state identity取得とのorder and ownership | YES |
| 38 | `CONFIG_REQUIRED` Bootstrap mapping | `PARTIALLY_SPECIFIED` | Design §2.5 | なし | missing config/secret/adapter configのclosed taxonomy | YES |

Counts: `CONTRACT_READY=12`, `PARTIALLY_SPECIFIED=18`, `UNSPECIFIED=8`, `CONFLICTING=0`。

## 6. Manifest gap analysis

### Defined

- canonical filename is `manifest.json`（§52.3）。
- Runtime absolute paths are fixed by implementation-time Manifest（§4.1）。
- Supported OS is Windows; edition/build/filesystem/Python version are recorded by CV-00（§2.6）。
- Manifest/Config may contain secret name/provider/required status, never secret values（§4.4）。
- Development and Runtime deployments are physically separate（§4.1/§4.6）。

### Not defined

- schema version and exact serialization.
- required/optional fields and unknown-field policy.
- Runtime root / project root path normalization and relocation rules.
- `state_id`, `environment`, Data Root locator, ExpectedEnvironmentBinding source fields.
- `SYSTEM_VERSION`, schema versions, System/Policy/Code hashes and their authoritative sources.
- supported Windows constraints and mismatch failure code.

Manifestは単独CapabilityとしてContract clarificationが必要である。

## 7. Config gap analysis

### Defined

- `config.json` is the single Configuration source.
- top-level conceptual areas: runtime/model/budget/notification/portfolio_policy/risk_policy/strategy/watch/selection/break/backup/archive.
- it carries `config_version`; Run/Decision stores `config_hash`.
- Job start obtains an immutable validated Config Snapshot; changes apply from the next Job.
- Secret values are prohibited.

### Not defined

- initial exact JSON schema and field types.
- `config_version` initial value and compatibility rules.
- canonical serialization/hash input and `config_hash` representation.
- unknown fields, defaults, missing fields, duplicate keys.
- external representation and per-field semantics of `UNCONFIGURED`.
- validation error model and startup aggregation.

Config Schema / ValidationをManifestと分離してContract化する必要がある。

## 8. Secret gap analysis

### Defined

- obtain Secret from Environment Variable or OS-protected secret store.
- do not store values in project/Manifest/Config/log/evidence/report/backup.
- Manifest/Config stores only secret name/provider/required status.
- secret scanning is a CV requirement.
- invalid API key/permission maps to`CONFIG_REQUIRED` at adapter error classification.

### Not defined

- whether Environment Variables, OS store, or both are mandatory for first implementation.
- SecretProvider interface and lookup order.
- reference schema and normalization.
- missing secret failure code/detail and multiple-missing aggregation.
- safe diagnostic/redaction contract.

Secret Bootstrapは独立Contractが必要である。

## 9. Environment Binding integration

### Reusable without change

- `Environment`, `DataRootLocator`, `ExpectedEnvironmentBinding`.
- `load_and_verify_environment_binding()` and exact failure model.
- TEST-specific `verify_test_environment_startup()`.
- fail-closed rule: BindingFailureをsuccessへ変換せず、通常Runtime/writeへ進めない。

### Missing integration decisions

- Expected bindingのauthoritative external source。Environment Binding Contract §4はData Rootからの導出を禁止し、config/manifest具体形式を意図的に未定義としている。
- Data Root locatorのauthoritative source。
- generic Runtime BootstrapがTEST/PAPER/LIVEで呼ぶpublic API。
- verified bindingをBootstrap success contextへ含めるか、startup validation recordだけに保持するか。
- external Data Root unavailable時にread-only Runtimeを許可する範囲。Environment Binding failure自体はsuccessにしてはならない。

したがって、既存Environment Binding ContractだけではBootstrap integrationを実装できない。

## 10. Failure / Result model

| Required state/failure | Existing definition | Bootstrap treatment that is already fixed | Remaining gap |
|---|---|---|---|
| Success | なし | 通常Loopへ進めるのは全mandatory gate成功後 | success type/context fields |
| `CONFIG_REQUIRED` | Design §2.5 | invalid key/permission等は通常Jobへ進めない | config/secret failure taxonomy |
| `RECOVERY_REQUIRED` | Design §4.2 | canonical stateを確定できなければempty Portfolioを作らない | exact result type/detail |
| `DATA_STORAGE_IDENTITY_MISMATCH` | EB Contract §7 | startup failureとして保持し書込拒否 | Bootstrap wrapper mapping不要か要検討 |
| `ENVIRONMENT_BINDING_MISMATCH` | EB Contract §7 | startup failureとして保持し書込拒否 | 同上 |
| `DATA_STORAGE_UNAVAILABLE` | EB Contract §7 / Design §4.7 | Data依存処理を縮退・停止 | Bootstrap全体failureかdegraded readinessかの境界 |
| `MIGRATION_REQUIRED` | Design §4.6 | schema不一致で通常Runnerを開始しない | compatibility matrix/detail |
| `RUNNER_LOCK_RECOVERY_REQUIRED` | Design §2.5 | lock所有者を確認不能なら奪取しない | Bootstrap order/result type |
| Secret missing | 明示codeなし | fail-closedが必要 | code、detail、multiple failures |
| Unsupported runtime / Manifest mismatch | 明示codeなし | Windows以外をSupported扱いしない | exact code/remediation/result |

新しいenum/classを本Draftで確定しない。Design Authorityがclosed taxonomy、複数failureの保持方法、priority/aggregation、success contextを決定する。

## 11. Capability decomposition

`RUNTIME-FOUNDATION-BOOTSTRAP`全体は一つの初回RED Capabilityとして大きすぎる。少なくとも次に分割する。

1. **Runtime Manifest / Runtime Identity**
   - Manifest schema、Windows runtime identity、Dev/Runtime path separation。
2. **Config Schema / Validation**
   - Config parse/schema/domain validation、version/hash、UNCONFIGURED representation。
3. **Secret Bootstrap Boundary**
   - Secret reference/provider、availability validation、redaction-safe failure。
4. **Startup Environment Binding Integration**
   - external expected binding/locator sourceとstartup verification接続。既存comparison/store/guardは再実装しない。
5. **Runtime Bootstrap Orchestrator**
   - §4.2 sequence、Canonical State/recovery、Runner lock、readiness resultを統合。

正式Capability ID、順序、Contract boundaryはDesign Authority + Humanが決定する。本書からCapability Registryへ自動登録しない。

## 12. Testability boundary

### L0/L1で実Disk/APIなしに検証可能

- Manifest bytes → parse/schema/domain validation → typed manifest/failure。
- Config bytes → parse/schema/domain validation/canonical hash → snapshot/failure。
- Secret reference → fake SecretProvider → availability/redaction-safe failure。
- injected Manifest/Config/Expected Binding/Locator/State reader/lock adapterを使うorchestration order。
- each fail-closed branchが通常Loop readinessを返さないこと。
- duplicate Environment Binding comparison/parser testは追加しない。

### 後段L2/L3/CVへ送る

- real Windows host/build/filesystem detection。
- real Environment Variable / OS-protected secret store integration。
- actual process/heartbeat Runner lock stale recovery。
- physical Dev/Runtime separation and deploy。
- real Disk disconnect/reconnect、junction/reparse、device replacement。
- network/adapter/model availability probe。
- Canonical State/inbox/outbox recovery with actual Writer/Atomic Commit。
- Catch-up execution and Relevance Check behavior。

## 13. Design Authority decisions required

Frozen Test / REDへ進む前に、少なくとも次を決定する。

1. Manifest v1 exact schema、serialization、unknown-field/version policy。
2. Runtime root/project root/Data Root path semantics。
3. `state_id`、`environment`、DataRootLocator、ExpectedEnvironmentBindingのauthoritative external source。
4. Config v1 exact schema、`UNCONFIGURED` representation、version compatibility。
5. `config_hash` canonicalization and representation。
6. SecretProvider初期要件（Environment Variable / OS store）、reference schema、lookup order。
7. Missing secret、unsupported runtime、Manifest mismatchのfailure code/detail。
8. Bootstrap success contextとfailure model。複数failureを集合で保持するか、順序で停止するか。
9. Manifest/Config/Secret/Binding/State/Runner lockのexact execution order。
10. `DATA_STORAGE_UNAVAILABLE`時のBootstrap failureとdegraded read-only readinessの境界。
11. inbox/outbox/UNKNOWN/Projection recoveryをBootstrap内で実行する範囲。
12. 上記5分割の正式Capability IDと実装順。

## 14. Acceptance readiness

- Overall Runtime Bootstrap Contract ready for implementation: `NO`
- Frozen Test / RED for overall orchestrator: `DO NOT START`
- Reason: 8 `UNSPECIFIED` items and 18 `PARTIALLY_SPECIFIED` items require Design Authority decisions.
- Existing Environment Binding tests/capabilities: remain `CLOSED`; no changes required.
- CV-44: `PARTIAL` maintained.
- RV-34: `NOT_RUN` maintained.
- Recommended next action: Design Authority chooses the first decomposed capability and supplies its exact Contract decisions.

## 15. No-change declaration

This Draft does not change Production, Frozen Test, Baseline, Run/Evidence, Test Strategy, existing Environment Binding Contract, Capability Registry, Improvement Backlog, or Development Progress.
