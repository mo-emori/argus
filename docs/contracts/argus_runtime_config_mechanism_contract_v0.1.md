# argus Runtime Config Mechanism Contract v0.1

**Status:** `CONTRACT DRAFT`  
**Capability:** `RUNTIME-CONFIG-MECHANISM`  
**Scope:** L0 pure JSON parse/validation; L1 explicit `config.json` load and relative Data Root resolution  
**Design Authority:** Runtime Config Mechanism v0.1 decisions supplied for this draft

## 1. Purpose

Runtime Config Mechanism v0.1は、明示された単一の`config.json`を読み込み、閉じた最小schemaとして検証し、immutable snapshotとData Root locatorを提供する。

本Capabilityはconfig load/validation/snapshotとdata-root locator/resolutionを所有する。process終了、通常Runtime Loopへの遷移、縮退判断は所有せず、上位判断は`RUNTIME-BOOTSTRAP-ORCHESTRATOR`が所有する。

## 2. Authority and compatibility boundary

Design Source §4.0の次の要求を維持する。

- Configurationの正本は`config.json`一つである。
- Configuration、Runtime Identity、User Status、Domain State、Runtime State、Secretを混同しない。
- data root pathはmutable locatorでありConfiguration側に属する。
- validated Configurationをimmutable snapshotとして扱う。
- typed failureをCapability境界で保持し、上位境界でstartup outcomeへ写像する。

Design Source §4.0の将来の広い運用Configuration、secret reference、Run/Stage/Decision provenance、Job境界のConfiguration適用は削除・再定義しない。Design Authorityのv0.1境界決定に従い、Runtime Config v0.1 schemaと動作から外して§12へ延期する。

Design SourceのRun/Decision Recordに対する`config_hash`保存要求は、Runtime Config v0.1のfield、snapshot field、hash APIまたはcanonicalization規則を意味しない。exact semanticsはprovenanceを所有するCapabilityが定義する。本Contractは`config_hash`を生成しない。

## 3. Responsibility boundary

| Concern | Runtime Config v0.1 |
|---|---|
| `config.json` load/validation/snapshot | Owns |
| `data_root` locator/resolution | Owns |
| Runtime Identity / `data_root_id` | Does not own |
| Runtime Entry Resolution | Does not own |
| Bootstrap orchestration/process termination | Does not own |
| Environment Binding verification | Does not own |
| Secret reference/value retrieval | Does not own |
| Paid-service/human-approval governance | Does not own |
| Domain/investment configuration | Does not own |
| provenance / `config_hash` | Does not own |

`data_root`はfilesystem locatorでありRuntime Identityの`data_root_id`ではない。path、drive letter、Volume GUID、Volume LabelまたはMarkerからRuntime Identityを導出してはならない。

## 4. Exact v0.1 schema

JSON rootはobjectであり、次の2 keyだけをexactly once含む。

```json
{
  "config_version": 1,
  "data_root": "data"
}
```

canonical field orderは`config_version`、`data_root`である。

| Field | JSON type | Exact rule |
|---|---|---|
| `config_version` | integer | exactly `1`; JSON booleanはintegerではない |
| `data_root` | string | §4.1を満たすnon-empty relative path |

両fieldはrequiredである。default補完、coercion、trim、case/separator変換、unknown key破棄を行わない。

### 4.1 `data_root` semantics

`data_root`は`config.json`を格納するdirectoryに対するrelative filesystem pathである。v0.1はabsolute-path formを受理も定義もしない。

L0は次を要求する。

- empty stringでなくU+0000を含まない。
- 最初のcode pointが`/`または`\`ではない。
- 最初の2 code pointがASCII letter（`A`-`Z`または`a`-`z`）と`:`の組合せではない。

上記の文字列規則をすべて満たす場合だけrelative `data_root`として受理し、それ以外は`INVALID_DATA_ROOT`とする。先頭`/`または`\`の拒否にはrooted、UNC、device pathを含み、ASCII letter + `:`の拒否にはdrive-absoluteとdrive-relativeを含む。separatorは`/`と`\`の両方を認識し、trim、separator変換、環境変数展開、`~`展開を行わない。

`.`、`..`およびそれらをcomponentとして含むrelative pathは受理する。v0.1は`data_root`がconfig directory配下に留まることを要求しない。上記以外のWindows filename/path validityはL0の判定対象にしない。L0はpathの存在、種類、accessibility、symlink/junction/reparse target、Marker、Environment Bindingを検査しない。

## 5. Result, snapshot, and diagnostics

### 5.1 Public state

公開stateは次のclosed setだけである。

```text
CONFIGURED
UNCONFIGURED
INVALID
ERROR
```

| State | Meaning |
|---|---|
| `CONFIGURED` | schemaに適合し、要求levelのsnapshot生成が完了 |
| `UNCONFIGURED` | L1で明示された`config.json`が存在しない |
| `INVALID` | bytesは取得できたがJSON/schema/domain ruleに不適合 |
| `ERROR` | filesystem/component operation failureでload/resolution未完了 |

stateはmutually exclusiveであり、non-`CONFIGURED`をsuccessとして扱わない。

### 5.2 Snapshot shapes

L0 success:

```text
ValidatedRuntimeConfig
  config_version: int = 1
  data_root: str
```

`data_root`はvalidated input stringを補正せず保持する。

L1 success:

```text
RuntimeConfigSnapshot
  config_version: int = 1
  data_root: str
  config_path: absolute normalized path to config.json
  data_root_path: absolute normalized lexical path
```

L1 snapshotは同じload invocationで読んだbytesと解決結果を一つのimmutable valueとして固定する。fileの後続変更でsnapshotを変更しない。dynamic reloadと次Jobへの適用は対象外である。

### 5.3 Result invariants

```text
RuntimeConfigResult
  state: RuntimeConfigState
  snapshot: ValidatedRuntimeConfig | RuntimeConfigSnapshot | none
  diagnostics: ordered tuple[RuntimeConfigDiagnostic, ...]
```

- `CONFIGURED`: snapshotあり、diagnosticsはempty。
- その他: snapshotなし、diagnosticsはnon-empty。
- partial snapshotを返さない。
- parser/filesystem例外を通常resultとして外へ漏らさない。public API input type違反はprogrammer errorである。

### 5.4 Minimal typed diagnostic codes

| Code | State | `field_name` |
|---|---|---|
| `CONFIG_NOT_FOUND` | `UNCONFIGURED` | none |
| `CONFIG_READ_ERROR` | `ERROR` | none |
| `DATA_ROOT_RESOLUTION_ERROR` | `ERROR` | `data_root` |
| `MALFORMED_JSON` | `INVALID` | none |
| `JSON_ROOT_NOT_OBJECT` | `INVALID` | none |
| `DUPLICATE_KEY` | `INVALID` | decoded duplicate key |
| `MISSING_FIELD` | `INVALID` | missing canonical field |
| `UNKNOWN_KEY` | `INVALID` | decoded unknown key |
| `INVALID_FIELD_TYPE` | `INVALID` | canonical field |
| `UNSUPPORTED_CONFIG_VERSION` | `INVALID` | `config_version` |
| `INVALID_DATA_ROOT` | `INVALID` | `data_root` |

`RuntimeConfigDiagnostic`は`code`と上表の`field_name`だけをExact Oracle対象とする。OS error text、localized message、stack trace、path textはpublic equality semanticsへ含めない。code setはcomponent-local closed setであり、Bootstrap/Incident/Binding/governance taxonomyを兼ねない。

## 6. L0 pure parse/validation contract

### 6.1 Input and purity

L0 inputは`bytes`である。

- strict UTF-8。UTF-8 BOMは拒否する。
- root前後のRFC 8259 JSON whitespaceは許可する。
- 単一root後のnon-whitespace trailing dataを拒否する。
- `NaN`、`Infinity`、`-Infinity`を拒否する。
- duplicateはJSON escape decoding後のkeyで判定する。

L0はpure operationであり、filesystem、environment variable、CLI、clock、network、process state、global cacheを参照せず、I/Oと外部状態変更を行わない。input bytesを変更しない。同じbytesに同じresult value/orderを返す。

### 6.2 Validation phases and deterministic order

```text
bytes / strict UTF-8 / duplicate-aware JSON parse
  -> root
  -> required / unknown keys
  -> field types
  -> field values
  -> ValidatedRuntimeConfig
```

1. malformed JSONはterminalで`MALFORMED_JSON`を1件返す。
2. duplicate keyはterminalで、input encounter orderの最初のduplicateに`DUPLICATE_KEY`を1件返す。last-value-winsは禁止する。
3. non-object rootはterminalで`JSON_ROOT_NOT_OBJECT`を1件返す。
4. missing fieldをcanonical orderで全件、その後unknown keyをinput encounter orderで全件収集する。存在すれば後続phaseへ進まない。
5. type errorをcanonical orderで全件収集する。存在すればvalue phaseへ進まない。
6. value errorをcanonical orderで全件収集する。

successは`CONFIGURED` + `ValidatedRuntimeConfig`、failureは`INVALID` + ordered diagnosticsである。L0は`UNCONFIGURED`またはfilesystem由来`ERROR`を返さない。

## 7. L1 filesystem/component contract

### 7.1 Invocation boundary

callerは対象`config.json`のabsolute pathを明示する。relative pathは受理せず、current working directory、parent directory、registry、environment variable、executable location等から補完または自動探索しない。pathの最終componentはexactly `config.json`とする。これらの違反はprogrammer errorでありConfiguration stateではない。

一つの明示pathから一つのfileだけを読み、fallback、merge、override、profile、inheritanceを使わない。

### 7.2 Load behavior

1. absolute input pathをfilesystemへ照会せずnormalized lexical pathへ変換し、これをsnapshotと後続stepの`config_path`とする。この変換はcurrent working directoryを参照しない。
2. 明示された`config_path`にconfig fileが存在しないことをload/read操作が報告した場合だけ、`UNCONFIGURED` + `CONFIG_NOT_FOUND`でterminalとする。欠損したparentを含め、そのpathにconfig fileがない場合はgenuine absenceである。
3. bytesを一回のload invocationとして読む。directory、dangling symlink、その他config fileとして読めない既存entry、permission failure、およびabsence以外のload/read failureは`ERROR` + `CONFIG_READ_ERROR`とする。OS errnoの個別列挙には依存せず、「明示pathのconfig fileのabsence」か「それ以外のload/read failure」かで分類する。
4. bytesをL0へ渡す。L0 failureは内容/orderを変えず`INVALID`。
5. L0 successの`data_root`を§7.3で解決する。
6. 解決成功時だけ`CONFIGURED` + `RuntimeConfigSnapshot`。

terminal outcome後は後続stepを実行しない。config file/Data Rootを作成、変更、修復、migrationしない。

### 7.3 Relative Data Root resolution

baseは§7.2 step 1で確定したabsolute normalized lexical `config_path`のparent directoryである。解決中にcurrent working directoryを参照せず、Runtime Identity、Runtime Entry、Marker locationをbaseにしない。

```text
data_root_path = lexical_normalize(config_path.parent / validated.data_root)
```

`/`と`\`を実行platformのfilesystem path semanticsに従って解釈し、`config_path.parent`との結合後に`.`と`..`をlexicalに正規化する。結果はabsolute normalized lexical pathである。target存在を要求せず、作成せず、filesystemへtargetを照会せず、symlink/junction/reparse targetを追跡してcanonicalizeしない。

`DATA_ROOT_RESOLUTION_ERROR`は、L0 success後、この結合またはlexical normalizationを実行platformのpath operationが完了できず、absolute lexical resultを生成できない場合だけ返す。targetの不存在、種類、permission、read/write可否、symlink/junction/reparse target、MarkerまたはEnvironment Bindingの状態をこのcodeへ写像しない。

Data Root存在、Marker identity、`state_id/data_root_id/environment`比較、read/write可否はRuntime Config success条件ではなく、Environment Bindingと上位orchestrationの責務である。

## 8. Failure and terminal behavior

- `CONFIGURED`はcomponent successだけでありBootstrap/Binding/normal-loop readinessではない。
- `UNCONFIGURED`はmissing `config.json`だけ。空object、missing field、`null`、空文字は`INVALID`。
- `INVALID`で自動補正、migration、fallbackを行わない。
- `ERROR`にmissing fileを含めない。
- process termination、exit code、retry、Incident、notification、degraded mode、normal-loop遷移を決めない。
- Bootstrapはstate/diagnosticを保持して上位startup outcomeへ写像する。exact mapping/process actionはBootstrap Contractが定義する。

## 9. L0/L1 terminology

L0/L1はARGUS Test Level conventionでありarchitectureのphysical/logical番号ではない。

| Level | Boundary |
|---|---|
| L0 | filesystem accessなしのpure JSON parse/validation |
| L1 | file loadとrelative `data_root` resolutionを含むcomponent behavior |

## 10. Determinism

- L0 diagnostic orderは§6.2、L1 terminal orderは§7.2に固定する。
- 同じbytesに対するL0 valueは決定論的である。
- 同じexplicit path、loaded bytes、platform path semanticsに対するL1 snapshotは決定論的である。
- directory enumeration、env/CLI order、clock、randomnessへ依存しない。
- canonical JSON serializationは定義しない。input key order/whitespaceをsnapshot meaningへ含めない。

## 11. Adjacent capabilities

Runtime ConfigはRuntime Identityを読み書きせず、identity fieldを保持せず、`data_root`から`data_root_id`/`environment`を推論しない。Runtime Identity frozen baseline/Contract/testsを変更しない。

Runtime Entry Resolutionの起動対象、runtime tree、Manifest、code entry point、Expected Bindingを解決しない。

BootstrapはRuntime Config resultを他のmandatory gateと統合する上位Capabilityである。本ContractはBootstrap call order、unified context、failure precedence、exit behaviorを実装・確定しない。

## 12. Explicit exclusions and deferred items

- `config_hash` field/generation/canonicalization/serialization/algorithm/provenance write。
- `secret_refs`、Secret value retrieval。
- env override、CLI override/precedence。
- multi-source merge、fallback、automatic directory-tree discovery。
- profiles、inheritance、includes。
- dynamic reload、watcher、Job-boundary reload/application policy。
- config migration framework、self-update config migration。
- domain/investment configuration。
- runtime governance field/decision（`paid=true`、`human_approval_ref`等）。
- Budget、notification、portfolio/risk policy、strategy、watch、selection、break、backup、archive fields。
- Runtime Identity、Entry Resolution、Bootstrap orchestration、Environment Binding verification。
- config writer、CLI edit、atomic replace、audit history。
- absolute `data_root`、`ARGUS_HOME`/HOME等のalternative base root、ならびにより豊富なpath validity、canonicalization、symlink/junction/reparse semantics（v0.2以降のreview candidate）。

将来のself-update/evolutionはconfiguration structure/handlingを変更し得る。v0.1 consumerはunknown keyを拒否し、将来fieldを先取り受理しない。

## 13. Acceptance boundary

本書はContractだけを定義する。Test Strategy、Frozen Test、test code、production code、Runtime Identity、Entry Resolution、Bootstrap実装を作成・変更しない。

本Contract draftはTest design/実装の自動承認、Capability Registry transition、CV/RV status変更を意味しない。
