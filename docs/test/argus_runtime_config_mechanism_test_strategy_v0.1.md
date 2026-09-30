# argus Runtime Config Mechanism Test Strategy v0.1

**System:** `argus`  
**Document Type:** Capability Test Strategy / Verification Design  
**Status:** `DRAFT`  
**Capability:** `RUNTIME-CONFIG-MECHANISM`  
**Authoritative Contract:** `docs/contracts/argus_runtime_config_mechanism_contract_v0.1.md`  
**Contract Review:** `ARGUS-RUNTIME-CONFIG-CONTRACT-REREVIEW-20260930-001` / `RUNTIME_CONFIG_CONTRACT_REVIEW_PASS`  
**Test Strategy Review:** `ARGUS-RUNTIME-CONFIG-TEST-STRATEGY-REVIEW-20260930-001` / `RUNTIME_CONFIG_TEST_STRATEGY_REVIEW_CHANGES_REQUIRED`  
**Date:** 2026-09-30

---

## 1. 目的と権威

本書は、Runtime Config Mechanism v0.1 Contractから将来のtest candidateへ要求する検証設計を導出する。Contractを唯一のbehavior oracleとし、テスト容易性、既存実装、一般的な設定機構の慣行から意味を追加しない。

Contractと本書が矛盾する場合はContractを優先し、本書を修正する。Design Source、派生文書、実装との矛盾は推測で解消せず報告する。本書はContract、test code、production code、Runtime Identity、Entry Resolution、Bootstrapを変更しない。

本書の作成時点ではtest codeを作成せず、Baseline Freeze、Formal RED、GREEN、Capability Registry transition、CV/RV status変更を実行しない。

## 2. ScopeとTest Level

| Level | 境界 | 許可される観測 |
|---|---|---|
| L0 | `bytes`に対するpure JSON parse/validation。filesystem accessなし | public state、validated snapshot、ordered typed diagnostics、purity/determinism |
| L1 | explicit absolute `config.json` pathのloadとrelative `data_root` resolution | public state、runtime snapshot、ordered typed diagnostics、filesystem operation boundary |

`L0` / `L1`はARGUS Test Levelであり、architecture layer番号ではない。L0でfilesystem fixtureを使ってはならない。L1は一時directory等の隔離されたfixtureを使用し、既存の実データrootを参照・変更しない。

### 2.1 Test Binding（test/implementation coordination convention）

Contract semanticsは本書のAuthoritative Contractが定めるbehaviorであり、唯一のbehavior oracleである。Test Bindingは、future test candidateとfirst implementationが同じconcrete interfaceで合流するために本書が選ぶcoordination conventionであって、Contractのsemantic guaranteeではない。Test Bindingを将来変更しても、それだけではContract semanticsの改訂を意味しない。逆に、bindingの名前・型・配置を理由にContract外のbehaviorを追加してはならない。

既存の`argus.runtime.runtime_identity`およびruntime componentの命名・value-object styleに合わせ、v0.1の最小bindingを次とする。

```text
module: argus.runtime.runtime_config

parse_runtime_config(data: bytes) -> RuntimeConfigResult
load_runtime_config(config_path: pathlib.Path) -> RuntimeConfigResult

RuntimeConfigState:
  CONFIGURED | UNCONFIGURED | INVALID | ERROR

RuntimeConfigDiagnosticCode:
  CONFIG_NOT_FOUND | CONFIG_READ_ERROR | DATA_ROOT_RESOLUTION_ERROR |
  MALFORMED_JSON | JSON_ROOT_NOT_OBJECT | DUPLICATE_KEY | MISSING_FIELD |
  UNKNOWN_KEY | INVALID_FIELD_TYPE | UNSUPPORTED_CONFIG_VERSION |
  INVALID_DATA_ROOT

RuntimeConfigDiagnostic:
  code: RuntimeConfigDiagnosticCode
  field_name: str | None

ValidatedRuntimeConfig:
  config_version: int
  data_root: str

RuntimeConfigSnapshot:
  config_version: int
  data_root: str
  config_path: pathlib.Path
  data_root_path: pathlib.Path

RuntimeConfigResult:
  state: RuntimeConfigState
  snapshot: ValidatedRuntimeConfig | RuntimeConfigSnapshot | None
  diagnostics: tuple[RuntimeConfigDiagnostic, ...]
```

`parse_runtime_config`はL0 target、`load_runtime_config`はL1 targetである。value objectはvalue equalityを持つimmutable objectとし、testは上記のobservable fieldsだけをoracleに使う。L0/L1ごとのsnapshot shape、result invariant、diagnostic order、programmer-error boundaryを含むbehaviorはContractどおりであり、このbindingはexception type/message、private helper、internal call graph、filesystem abstraction、fault-injection hookを定めない。`pathlib.Path`はexplicit pathを渡し、Contractが定めるpath valueを観測するためのconcrete carrierであって、新しいpath semanticsを追加しない。

## 3. Test ID規約

- `RC-L0-NNN`: pure parse/validation requirement。
- `RC-L1-NNN`: filesystem/component requirement。
- `RC-X-NNN`: level横断の境界、governance、workflow requirement。
- IDは一度割り当てた意味を再利用しない。削除時も別要件へ振り替えない。
- parameterized caseは同じrequirement IDを共有できるが、case IDで入力境界を識別する。
- test function名または明示metadataからTest IDを機械抽出できること。

## 4. 共通Exact Oracle

### 4.1 Result invariant

すべての通常resultについて、次をexactにassertする。

| State | Snapshot | Diagnostics |
|---|---|---|
| `CONFIGURED` | levelに対応する完全なsnapshotが1個 | empty ordered tuple |
| `UNCONFIGURED` | none | non-empty ordered tuple |
| `INVALID` | none | non-empty ordered tuple |
| `ERROR` | none | non-empty ordered tuple |

partial snapshot、Contract外のpublic state、Contract外のdiagnostic codeを許可しない。parser/filesystem例外は通常resultの外へ漏らさない。public API input type違反とL1 invocation boundary違反はprogrammer errorであり、Configuration state/codeを本書で発明しない。

`RuntimeConfigDiagnostic`のequality oracleは`code`と`field_name`だけである。OS error text、localized message、stack trace、path textの値・文面・有無を固定しない。

### 4.2 Terminal oracle

terminal condition後は後続phase/operationを実行しない。spy/fake/monkeypatchによる観測は、禁止された後続callが0回であることをassertするためだけに用い、private implementation sequenceを固定しない。

- malformed、最初のduplicate、non-object rootの後はstructural/type/value validationを行わない。
- missing/unknownが1件以上ならtype/value validationを行わない。
- type errorが1件以上ならvalue validationを行わない。
- L1 `CONFIG_NOT_FOUND` / `CONFIG_READ_ERROR`後はL0 parseとData Root resolutionを行わない。
- L0 `INVALID`後はData Root resolutionを行わない。
- `DATA_ROOT_RESOLUTION_ERROR`後はsnapshotを生成しない。
- terminal `INVALID` / `ERROR`でfallback、repair、migration、creation、write、Bootstrap/Entry Resolutionへの遷移を行わない。

## 5. L0 Test RequirementsとExact Oracles

| Test ID | Contract | Requirement / exact oracle |
|---|---|---|
| `RC-L0-001` | §4, §5.2, §6.2 | minimal bytes `{"config_version":1,"data_root":"data"}`は`CONFIGURED`。snapshotは`config_version == 1`かつ`data_root == "data"`、diagnosticsはempty。 |
| `RC-L0-002` | §4 | `config_version`のinteger valueはexactly `1`だけを受理する。`1` successをpositive controlにする。 |
| `RC-L0-003` | §4, §5.4 | integer `0`, `2`, `-1`等のunsupported versionは`INVALID` + exactly `UNSUPPORTED_CONFIG_VERSION(config_version)`。 |
| `RC-L0-004` | §4, §6.2 | required key欠損をcanonical order (`config_version`, `data_root`) で全件`MISSING_FIELD`として返す。missingがあれば後続phaseへ進まない。 |
| `RC-L0-005` | §4, §6.2, §12 | unknown keyを破棄せず、input encounter orderで全件`UNKNOWN_KEY`として返す。将来fieldも先取り受理しない。 |
| `RC-L0-006` | §4, §6.1-6.2 | JSON escape decoding後のkeyでduplicateを判定し、input encounter orderの最初のduplicateだけを`DUPLICATE_KEY(decoded_key)`として返す。terminalでありlast-value-winsを許可しない。 |
| `RC-L0-007` | §6.1-6.2 | invalid UTF-8、UTF-8 BOM、truncated JSON、trailing non-whitespace、`NaN`、`Infinity`、`-Infinity`等は`INVALID` + exactly `MALFORMED_JSON(None)`。root前後のRFC 8259 whitespaceはpositive caseとして受理する。 |
| `RC-L0-008` | §4, §6.2 | `config_version`のstring、float、null、array、object、JSON booleanは`INVALID_FIELD_TYPE(config_version)`。coercionしない。type errorはcanonical orderで全件収集する。 |
| `RC-L0-009` | §4, §6.2 | `data_root`のnon-string型は`INVALID_FIELD_TYPE(data_root)`。複数type errorはcanonical orderで返し、value phaseへ進まない。 |
| `RC-L0-010` | §4.1, §5.4 | non-emptyでU+0000を含まず、先頭が`/`/`\`でなく、先頭2 code pointがASCII letter + `:`でないstringを受理する。`.`、`..`、それらをcomponentに含むpath、両separator、config directory外へlexically到達し得るrelative pathも受理する。input stringを補正せずsnapshotに保持する。 |
| `RC-L0-011` | §4.1, §5.4 | empty、U+0000含有、先頭`/`、先頭`\`（UNC/deviceを含む）、先頭ASCII letter + `:`（drive-absolute/drive-relativeを含む）は`INVALID_DATA_ROOT(data_root)`。trim、separator変換、env展開、`~`展開をしない。 |
| `RC-L0-012` | §5.4, §6.2 | JSON rootがobject以外なら`INVALID` + exactly `JSON_ROOT_NOT_OBJECT(None)`でterminal。 |
| `RC-L0-013` | §6.2 | phase precedenceとdiagnostic orderを複合入力でassertする: malformed > duplicate > root > missing/unknown > type > value。各terminal/stop条件の後続validationは0回。 |
| `RC-L0-014` | §6.1, §9 | filesystem、environment、CLI、clock、network、process state、global cacheを参照せず、I/Oと外部状態変更を行わない。代表success/failureでfilesystem APIs等をfail-on-callにし、call 0回、input bytes不変をassertする。 |
| `RC-L0-015` | §6.1, §10 | 同じbytesへの反復実行は同じresult valueとdiagnostic orderを返し、directory enumeration、env/CLI order、clock、randomnessに依存しない。 |
| `RC-L0-016` | §4, §5.2, §10 | key orderと許可whitespaceはsnapshot meaningを変えない。canonical serializationやcanonical bytesはassertしない。default、trim、case/separator normalizationをassertしない。 |
| `RC-L0-017` | §5.1-5.3, §6.2 | L0はsuccess時のみ`CONFIGURED`; failureは`INVALID`。`UNCONFIGURED`やfilesystem由来`ERROR`を返さない。result invariantを満たす。 |

`RC-L0-010`のpositive matrixはContractの3個の文字列規則だけをoracleとする。Windows予約名、末尾dot/space、component length等、Contractが定義しないpath validityをnegative caseにしない。

## 6. L1 Test RequirementsとExact Oracles

| Test ID | Contract | Requirement / exact oracle |
|---|---|---|
| `RC-L1-001` | §7.1-7.2 | explicit absolute pathのfinal componentがexactly `config.json`で、fileが存在しreadableかつvalidなら1回のloadで`CONFIGURED` + complete `RuntimeConfigSnapshot`。 |
| `RC-L1-002` | §7.2 | explicit `config.json`のgenuine absence（missing parentを含む）は`UNCONFIGURED` + exactly `CONFIG_NOT_FOUND(None)`。terminalでparse/resolution/writeを行わない。 |
| `RC-L1-003` | §7.2 | genuine absenceではないgenericなload/read failureは`ERROR` + exactly `CONFIG_READ_ERROR(None)`。OS固有のfilesystem entry typeやerrno別の追加分類をassertしない。 |
| `RC-L1-004` | §7.2 | loaded bytesのL0 failureはstate/code/orderを変更せず`INVALID`として伝播し、Data Root resolutionを行わない。 |
| `RC-L1-005` | §7.2-7.3 | `config_path`はfilesystem照会なしでabsolute normalized lexical pathとなり、baseはそのparent。`data_root_path = lexical_normalize(config_path.parent / validated.data_root)`をplatform path semanticsで得る。 |
| `RC-L1-006` | §7.2-7.3, §10 |異なるcurrent working directoryから同じexplicit path/bytes/platform semanticsで実行しても、`config_path`と`data_root_path`を含むresultは同じ。CWDをbaseまたはnormalization sourceにしない。 |
| `RC-L1-007` | §7.3 | Data Root targetの不存在を許可し`CONFIGURED`とする。target、parent、marker等を作成・変更しない。 |
| `RC-L1-008` | §7.3 | targetの種類、permission、read/write可否をsuccess条件にせず、target filesystem queryを行わない。これらを`DATA_ROOT_RESOLUTION_ERROR`へ写像しない。 |
| `RC-L1-009` | §7.3 | symlink/junction/reparse targetを追跡してcanonical targetへ解決しない。snapshotはabsolute normalized **lexical** pathを保持する。lexical resolverへのtarget-query 0回oracleは全platformで必須とする。native symlink/junction/reparse fixtureを補助caseに使い、platform/権限により信頼して構成できない場合だけ、その補助caseのskip理由を記録する。 |
| `RC-L1-010` | §7.3 | L0 success後、join/lexical normalizationのplatform path operationが完了できずabsolute lexical resultを生成できない場合だけ、`ERROR` + exactly `DATA_ROOT_RESOLUTION_ERROR(data_root)`。snapshotなし。 |
| `RC-L1-011` | §7.3 | `DATA_ROOT_RESOLUTION_ERROR`はContractが定めるjoin/lexical-normalization failureだけを検証する。Test Bindingでは既存のpublic Python stdlib path operation `os.path.normpath`をmonkeypatch/fake boundaryとし、§6注記のinput-based triggerで失敗させる。専用のproduction fault-injection APIを要求しない。target absence/type/permission、symlink、Marker、Environment Bindingを使ってこのcodeを発生させず、platformで自然再現できない場合もContract外のpath-invalid ruleを発明しない。 |
| `RC-L1-012` | §5.2, §7.2 | success snapshotは`config_version == 1`、original validated `data_root`、absolute normalized lexical `config_path`、absolute normalized lexical `data_root_path`を持つimmutable value。同じinvocation後のfile変更で変化しない。 |
| `RC-L1-013` | §7.1 | 一つのexplicit pathから一つのfileだけを読み、auto-discovery、fallback、merge、override、profile、inheritanceを行わない。 |
| `RC-L1-014` | §7.1, §5.3 | relative input pathまたはfinal componentが`config.json`でない入力はprogrammer error。exact exception type/messageはContract未定義のため固定しないが、Configuration resultへ分類せずfilesystem accessしない。 |
| `RC-L1-015` | §7.2, §8 | terminal outcome後に後続stepを実行せず、config file/Data Rootを作成、変更、修復、migrationしない。`INVALID` / `ERROR`をsuccess扱いしない。 |
| `RC-L1-016` | §10 | 同じexplicit path、loaded bytes、platform path semanticsに対するsnapshotは決定論的で、env/CLI、clock、randomness、directory enumerationに依存しない。 |

`RC-L1-003`のportable testでは、明示pathに通常fileを用意した上で、既存のpublic Python stdlib dependency boundaryである`Path.read_bytes`をmonkeypatchし、そのpathのreadを失敗させる。observable oracleは`ERROR` + exactly `CONFIG_READ_ERROR(None)`とし、OS固有entryの構築、symlink作成権限、private関数名・call graphをassertしない。これはTest Bindingに限定したtesting techniqueであり、Contract semanticsまたはproduction requirementではない。productionにtest専用parameter、hook、adapter、fault modeを追加しない。

`RC-L1-010` / `011`はContractが許す狭いcode境界を検証する。OS固有の任意のinvalid filenameをportable requirementにしない。portable testでは`load_runtime_config`を呼び、validな`data_root` marker value `__ARGUS_TEST_DATA_ROOT_RESOLUTION_FAILURE__`を含むpath-like入力を受けた場合だけ`OSError`をraiseし、それ以外はoriginal operationへdelegateするtest fakeで`os.path.normpath`をmonkeypatchする。これによりfakeは意図したData Root lexical normalizationだけを失敗させ、`config_path`のvalidation/normalizationや無関係のpath operationに干渉しない。observable oracleは`ERROR` + exactly `DATA_ROOT_RESOLUTION_ERROR(data_root)`とし、private関数名・call graphはassertしない。これはTest Bindingに限定したtesting techniqueであり、Contract semanticsまたはproduction requirementではない。productionにtest専用parameter、hook、adapter、fault modeを追加しない。

## 7. Level横断Boundary Requirements

| Test ID | Contract | Requirement / exact oracle |
|---|---|---|
| `RC-X-001` | §3, §8, §11 | Runtime Identityを読み書きせず、identity fieldをsnapshotに持たず、`data_root_id`/`environment`を推論しない。 |
| `RC-X-002` | §3, §8, §11 | Entry Resolution、Bootstrap orchestration、Environment Binding、process termination、exit code、retry、Incident、notification、degraded/normal-loop transitionを実行・確定しない。 |
| `RC-X-003` | §2-3, §12 | `config_hash`、secret、governance/domain configをschema/snapshot/APIへ追加しない。unknown keyとしてContractどおり拒否する以上の将来semanticsをtestしない。 |
| `RC-X-004` | §12 | absolute `data_root`、ARGUS_HOME/HOME base、env/CLI precedence、multi-source、discovery、profiles、reload、migration、secret retrievalは`OUT_OF_SCOPE / DEFERRED`。v0.1 success behaviorとしてtestしない。 |

## 8. Contract-to-Test Traceability Matrix

| Contract section / requirement group | Test IDs | Coverage |
|---|---|---|
| §1 Purpose / capability ownership | `RC-X-001`, `RC-X-002` | config load/validation/snapshotとlocator/resolutionだけを所有 |
| §2 Authority and compatibility | `RC-X-001`, `RC-X-003`, `RC-X-004` | separation、immutable snapshot、typed failure、deferred provenance |
| §3 Responsibility boundary | `RC-X-001`..`RC-X-004` | owns / does-not-ownを完全に区別 |
| §4 Exact schema | `RC-L0-001`..`RC-L0-006`, `RC-L0-008`, `RC-L0-009`, `RC-L0-016` | 2 required keys、types、exact version、no normalization/default |
| §4.1 `data_root` semantics | `RC-L0-010`, `RC-L0-011`, `RC-L1-005`..`RC-L1-011` | exact relative-string rulesとlexical resolution |
| §5.1 Public state | `RC-L0-017`, `RC-L1-001`..`RC-L1-004`, `RC-L1-010` | closed mutually-exclusive states |
| §5.2 Snapshot shapes | `RC-L0-001`, `RC-L0-010`, `RC-L1-005`, `RC-L1-012` | L0/L1 complete immutable snapshots |
| §5.3 Result invariants | `RC-L0-017`, `RC-L1-001`..`RC-L1-004`, `RC-L1-010`, `RC-L1-012`, `RC-L1-014` | snapshot/diagnostics/exception boundary |
| §5.4 Diagnostics | `RC-L0-003`..`RC-L0-013`, `RC-L1-002`..`RC-L1-004`, `RC-L1-010`, `RC-L1-011` | full closed code set、state、field_name |
| §6.1 L0 input/purity | `RC-L0-007`, `RC-L0-014`, `RC-L0-015` | strict JSON input、no external access/state change |
| §6.2 phases/order | `RC-L0-001`..`RC-L0-013`, `RC-L0-017` | phase precedence、collection order、terminal behavior |
| §7.1 invocation | `RC-L1-001`, `RC-L1-013`, `RC-L1-014` | explicit absolute single `config.json` only |
| §7.2 load behavior | `RC-L1-001`..`RC-L1-005`, `RC-L1-012`, `RC-L1-015` | absence/read/parse/resolution sequenceとterminal behavior |
| §7.3 resolution | `RC-L1-005`..`RC-L1-012` | parent base、CWD independence、lexical-only、narrow error |
| §8 failure/terminal | `RC-L0-013`, `RC-L0-017`, `RC-L1-002`..`RC-L1-004`, `RC-L1-015`, `RC-X-002` | no auto-correction/upper-layer action |
| §9 terminology | §2、`RC-L0-014`, `RC-L1-001` | L0 filesystemなし / L1 filesystemあり |
| §10 determinism | `RC-L0-015`, `RC-L0-016`, `RC-L1-006`, `RC-L1-016` | defined deterministic inputs only |
| §11 adjacent capabilities | `RC-X-001`, `RC-X-002` | Identity/Entry/Bootstrap非所有 |
| §12 exclusions/deferred | `RC-L0-005`, `RC-X-003`, `RC-X-004` | future field rejectionとfuture behavior非要求 |
| §13 acceptance boundary | §1、§10-§14 | strategy-only、no freeze/code/status transition |

上表の各Contract sectionは少なくとも1個のTest IDまたは本書のgovernance sectionに対応する。future test candidateのPre-REDでは、Test ID集合 `RC-L0-001..017`, `RC-L1-001..016`, `RC-X-001..004`（合計37 requirement IDs）の欠損、unexpected ID、意味の重複再利用を機械検査する。

## 9. review MINOR findingsの扱い

Contract reviewで残った六つのMINOR noteはnon-blockingであり、note本文は本書のoracleではない。

- Contractにobservable behaviorとして既に確定した部分は、上記の該当Test IDで検証する。
- Contractにstate、code、field、order、exception type、path rule等が定義されていない部分は`OUT_OF_SCOPE / DEFERRED`とし、期待値を発明しない。
- MINORを根拠にContractのclosed state/code setを拡張しない。
- 将来MINOR dispositionがContractを変更した場合だけ、明示的なContract/Test Strategy revisionとして再traceする。baselineへ黙って取り込まない。

`ARGUS-RUNTIME-CONFIG-TEST-STRATEGY-REVIEW-20260930-001`の五つのMINOR findingも再確認対象とする。Contractですでに決定済みの意味に対するwording/traceability correctionだけを本書へ反映し、新しいstate、code、field、order、API semantics、platform semanticsは追加しない。findingの解消に新しいDesign Authority decisionが必要な場合は、v0.1 Test Strategyをblockせず`NON_BLOCKING_DEFERRED_PENDING_DESIGN_AUTHORITY`として記録し、将来の明示revisionで扱う。review record本文がreview-delta jobの入力artifactに含まれない場合も、個別findingの内容を推測して本書へ取り込まず、同じdispositionで非ブロッキングにdeferする。

## 10. Pre-RED Validation Requirements

future test candidateはBaseline Freeze前に次をすべて満たす。

1. UTF-8 decode、Python syntax compile、`ast.parse`が成功する。
2. AST/static inventoryで37 requirement IDsを100% coverし、missing/unexpected/reused IDがない。parameterized複数functionの同一IDは意図とcase coverageを記録する。
3. 本書§8のContract-to-Test mappingとtest inventoryの双方向traceabilityが完全である。
4. fixture/test helperを含むtest candidateにRuffを実行し、test code自身のlint failureが0である。
5. Pyrightをtest candidateに実行する。test code自身のtype/config/import defectは0である。
6. production symbolが意図的に未実装であるためだけに生じるPyright diagnosticは`EXPECTED_STATIC_RED`として分離できる。root missing production import/symbol数と、それだけから機械的に派生するunknown-type diagnosticsを記録する。
7. `EXPECTED_STATIC_RED`はPASSではない。syntax error、誤ったtest import path、pytest/config error、unrelated missing dependency、独立したtest type errorを含む場合はPre-RED failureとする。
8. `Any`、`getattr`、`type: ignore`、rule suppression、config exclusionによってabsent APIやtest defectを隠さない。
9. Contract、本書、test candidate、`pyproject.toml`等の使用したstatic configurationについてpathとSHA-256を記録する。
10. scope checkとして、Contract/production/Runtime Identity/Entry Resolution/Bootstrapが変更されていないこと、test candidate以外のunrelated changeを取り込んでいないことを記録する。

Pre-RED final resultは、全checkが満たされた場合だけ`PRE_RED_PASS_BASELINE_FREEZE_READY`とする。

## 11. Formal RED Acceptance Criteria

Formal REDはHuman-authorized Baseline Freeze後にのみ実行する。

- frozen test baselineは、Runtime Config production implementationが意図的に存在しないことに直接帰属する理由でfailする。
- expected failureのphase、test IDs、root causeがfreeze recordと一致する。
- production実装前は、意図的に存在しない`argus.runtime.runtime_config` moduleまたは§2.1のproduction symbolだけを原因とするimport/module/collection failureを`EXPECTED_RED`として許可する。これはPre-REDがfrozen test candidateのsyntax、static validity、Test ID inventory、双方向traceability、およびtest dependency/configurationの健全性を先に確立し、freeze recordのexpected absent-production root causeと一致する場合に限る。
- syntax error、malformed test、fixture construction defect、missing test dependency、pytest/static configuration defect、baseline drift、permission、unrelated environment failure、unrelated existing test failureは`UNEXPECTED_FAILURE`であり、RED signalを無効にして`FORMAL_RED_BLOCKED`とする。意図したproduction moduleが存在しない段階でtest collection成功を要求しない。
- expected failureを一件含んでいてもunrelated failureが混在すればaccepted REDにしない。
- unexpectedly pass、wrong reasonでfail、Contract/Test Strategy/test hash driftはaccepted REDにしない。
- testをskip/xfail/weakeningしてREDを作らない。

accepted resultは、frozen testがexpected absent-production reasonでfailし、その他のblocking failureが0である場合だけ`FORMAL_RED_ACCEPTED`とする。

## 12. GREEN Acceptance Criteria

GREENはFormal RED accepted後の別jobで判定する。

- frozen Contract/Test Strategy/test codeのhashがbaselineと一致する。
- `RC-L0-001..017`, `RC-L1-001..016`, `RC-X-001..004`が全件PASSし、requirement ID自体のskip/xfail/unexpected warningがない。`RC-L1-009`のnative filesystem補助caseだけは、必須のplatform-independent oracleがPASSしたうえで、環境上構成不能のevidence付きskipを許可する。
- scoped Ruff、Pyright、BanditがPASSする。repository-wide resultとcurrent change attributionを分離して記録する。
- repository policyに従い`pytest`, `ruff`, `pyright`, `bandit`, `pip-audit`を実行し、失敗・known debt・environment limitationを隠さない。dependency変更がなくても`pip-audit` resultを記録する。
- expected static REDは残存させない。production implementation後の同じdiagnosticはfailureである。
- Contract外のfeature追加、test weakening、fallback/auto-correction、Identity/Entry/Bootstrap advancementがない。
- public state、typed code、field_name、ordered diagnostics、terminal no-call、filesystem no-writeがexact oracleに一致する。

GREEN evidenceはcommand、tool/version、config hash、exit status、raw report reference/hash、test count、covered IDs、code/worktree identityを保持する。

## 13. Independent Review Expectations

GREEN candidateはimplementation authorとは独立したsemantic reviewを受ける。review inputは少なくともContract、本書、frozen tests、implementation diff/full changed files、Pre-RED/Freeze/RED/GREEN evidence、static analysis result、worktree/code identityを含む。

reviewは次を重点確認する。

- Contractからのsemantic drift、特にrelative pathの追加制限またはabsolute path受理。
- `UNCONFIGURED`と`ERROR`の誤分類。
- terminal condition後のparse/resolution/write/fallback。
- target existence/access/canonical-target解決の混入。
- diagnostic orderまたは`field_name`の非決定性。
- purity/CWD independenceの破壊。
- deferred feature、Runtime Identity、Entry Resolution、Bootstrapの先取り。
- test weakening、private implementationへの過剰結合、failure injectionによるinvented semantics。

reviewerは`FINDINGS`または`NO_FINDINGS`を返し、automated GREENを上書きしない。各findingはseverity、Contract/Test ID reference、evidence、dispositionを持つ。unresolved critical/major semantic findingがある状態をcompletionとしない。

## 14. Baseline Freeze Inputs（将来job）

Formal RED前のHuman-authorized freezeは、Runtime Identity workflowと同じく少なくとも次をpath + SHA-256で固定する。

1. reviewed Runtime Config Contract。
2. approved Runtime Config Test Strategy（本書の将来approved revision）。
3. complete future test codeと直接必要なfixture/helper。
4. accepted Pre-RED evidence (`PRE_RED_PASS_BASELINE_FREEZE_READY`)。
5. static/lint/type configuration（例: `pyproject.toml`）。
6. Test ID inventoryとtraceability result（37/37）。
7. Git HEAD、working-tree status、tracked diff hash、capability inputとなるuntracked file hashes。
8. reserved Formal RED run ID、expected absent-production root cause、production module/symbol presence state。
9. Human approval reference、freeze timestamp、baseline ID/version、freeze rule。

freeze ruleは「Contract、Test Strategy、test codeをproduction implementationにpassさせるためだけに変更しない。変更は理由・Human approval・新hash・再Pre-REDを伴うgoverned baseline revisionとする」とする。

本JOBでは上記入力を列挙するだけであり、hash計算、baseline/evidence artifact作成、approval、freezeを実行しない。

## 15. 明示的OUT_OF_SCOPE / DEFERRED

次はv0.1 test requirementにしない。

- absolute `data_root` support。
- `ARGUS_HOME` / HOME等のbase。
- `config_hash`。
- `secret_refs`、secret retrieval。
- env/CLI precedence。
- multi-source merge、fallback、auto-discovery。
- profiles、inheritance、includes。
- dynamic reload、watcher、Job-boundary application policy。
- migration/self-update config migration。
- governance/domain configuration。
- Runtime Identity、Entry Resolution、Bootstrap orchestration、Environment Binding verification。
- process exit、retry、Incident、notification、degraded/normal-loop transition。
- config writer/editor、atomic replace、audit history。
- Contractで定義されないrich path validity/canonicalization。

unknown key rejection、absolute-like `data_root` rejection等、Contractがv0.1で明示するnegative behaviorはdeferred featureの実装テストではなく、closed v0.1 boundaryのテストとしてL0に含める。

## 16. Draft Completion Criterion

本書は、Contract全sectionのtraceability、37 stable requirement IDs、L0/L1 exact oracle、terminal behavior、Pre-RED/Formal RED/GREEN、independent review、future baseline-freeze inputsを定義した時点でdraft completeとする。approval、test implementation、freeze、RED/GREEN executionは後続の明示jobに残す。
