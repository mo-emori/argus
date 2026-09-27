# argus — Environment Binding Contract v0.1

**Status:** ACCEPTED FOR GATE A IMPLEMENTATION  
**Created:** 2026-09-13  
**Clarified:** 2026-09-16 — Binding failure naming/representation、Locator module dependency、L0 comparison contract  
**Clarified:** 2026-09-18 — L1 Marker Storeのload結果、filesystem failure mapping、atomic initialization、load-and-verify contract  
**Clarified:** 2026-09-20 — TEST Environment Guard、write-boundary reverification、Windows lexical path containment  
**Scope:** Gate AのTEST Environment Binding、および将来のPAPER / LIVE Environment Bindingに共通するMarker、検証結果、failure mapping、初期化、Test Contractを定義する。

------------------------------------------------------------------------

# 1. 上位文書との関係

本書は、次の正本を変更または置換せず、Environment Bindingの実装に必要な詳細を具体化する補足Contractである。

1. `docs/source/argus_design_source_v0.1.md`
   - §4.1のData Root Marker / Storage Identity
   - §4.2の起動時Binding照合
   - §46BのCV-44
   - §46B.1のDevelopment Validation Integrity
   - §52.1のRV-34
2. `docs/test/argus_test_strategy_v0.1.3.md`
   - §2.2のRequirement / Test / Implementation分離
   - §2.3のFail Closed
   - §3のTest Environment / Environment Binding
   - §9のFrozen Baseline
   - §12のFailure Injection
   - §24.2のCanonical Implementation / Verification Order
   - §24.3のCritical Path Review
   - §25のGate A
3. `docs/adr/argus_architecture_decision_records_v0.1.md`
   - ADR-006のData Persistence Boundary / Storage Identity

本書はSystem Design v0.1.7で追加された`environment` BindingをADR-006の`state_id / data_root_id`契約へ加え、Gate A向けの厳密な検証規則を定義する。

上位文書と本書に矛盾が見つかった場合、実装で推測補完しない。上位文書または本書を明示的に改訂してからBaselineを固定する。

Environment BindingはCritical Pathであり、fail-closedとする。Human Correctionその他の経路から迂回できない。

------------------------------------------------------------------------

# 2. IdentityとLocator

Identityは次の値で構成する。

- `state_id`: Canonical State Identity
- `data_root_id`: Data Root logical Identity
- `environment`: `TEST / PAPER / LIVE`

次の値はIdentityではない。

- filesystem path
- drive letter
- Windows Volume GUID
- Windows Volume Label

PathはData Rootへ到達するためのLocatorとして扱う。Volume GUID / Volume Labelは将来Diagnostic Evidenceとして取得可能な設計にするが、Gate AのPrimary verificationには使用しない。

Volume GUID / Volume Labelの一致だけでBindingを成功させてはならず、取得不能または値の変化だけでGate AのPrimary verificationを失敗させてはならない。

------------------------------------------------------------------------

# 3. Data Root Marker

Data Root直下の固定名を使用する。

```text
data_root_marker.json
```

## 3.1 必須フィールド

Markerは次の5フィールドだけを持つJSON objectとする。

```json
{
  "schema_version": 1,
  "state_id": "00000000-0000-4000-8000-000000000000",
  "data_root_id": "00000000-0000-4000-8000-000000000000",
  "environment": "TEST",
  "created_at": "2026-09-13T00:00:00Z"
}
```

| Field | External type | Contract |
|---|---|---|
| `schema_version` | JSON integer | 初期値かつ現在の対応値は`1`。JSON booleanは拒否する |
| `state_id` | string | canonical lowercase + hyphen形式のUUID v4 |
| `data_root_id` | string | canonical lowercase + hyphen形式のUUID v4 |
| `environment` | string | `TEST / PAPER / LIVE`のいずれか |
| `created_at` | string | 本書§3.3のtimezone-aware RFC3339 |

必須フィールドの欠落を拒否する。unknown fieldを拒否する。duplicate JSON keyを拒否する。

## 3.2 UUID

UUIDは次のcanonical lowercase + hyphen形式だけを受理する。

```text
xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
```

`x`はlowercase hexadecimal digit、`y`はUUID variantを満たすlowercase hexadecimal digitとする。UUID v4としてparse可能でも、入力文字列がcanonical lowercase + hyphen形式でなければ拒否する。検証時に大文字、小文字、hyphen、brace、URN表現を暗黙正規化して受理しない。

## 3.3 RFC3339 timestamp

`created_at`は次を満たす。

- date/time separatorは`T`
- timezone必須
- timezoneは`Z`または`±HH:MM`
- 小数秒は省略、または1〜6桁
- 実在する暦日時である
- secondは`00`〜`59`

次を拒否する。

- naive datetime
- offset秒を含むtimezone
- leap second
- space separator
- 7桁以上の小数秒

保存時はUTCへ正規化し、timezoneを`Z`で表記する。小数秒が0の場合は小数部を出力しない。小数秒がある場合はmicrosecondの6桁を出力する。

## 3.4 JSON serialization

保存形式を次に固定する。

- UTF-8
- BOMなし
- 改行はLF
- 2-space indent
- final newlineあり
- unknown fieldなし

key orderを次に固定する。

1. `schema_version`
2. `state_id`
3. `data_root_id`
4. `environment`
5. `created_at`

## 3.5 Schema validation

Gate Aでは外部JSON Schema dependencyを追加しない。Pythonコードで決定論的にvalidationする。

SchemaまたはDomain validationの失敗時に、default値の補完、無効値の修正、新しいUUIDの生成、local timezoneの補完、unknown fieldの破棄を行わない。

------------------------------------------------------------------------

# 4. Contract上の型

実装上の具体的なclass配置は§8に従う。最低限、次の意味を持つ型を定義する。

```text
DataRootMarker
  schema_version: integer
  state_id: UUID
  data_root_id: UUID
  environment: Environment
  created_at: timezone-aware datetime

MarkerValidationErrorCode
  MALFORMED_JSON
  JSON_ROOT_NOT_OBJECT
  MISSING_FIELD
  UNKNOWN_FIELD
  DUPLICATE_FIELD
  INVALID_FIELD_TYPE
  UNSUPPORTED_SCHEMA_VERSION
  INVALID_STATE_ID
  INVALID_DATA_ROOT_ID
  INVALID_ENVIRONMENT
  INVALID_CREATED_AT

MarkerValidationError
  code: MarkerValidationErrorCode
  field_name: string or None

MarkerValidationFailure
  errors: non-empty ordered tuple of MarkerValidationError

ExpectedEnvironmentBinding
  state_id: UUID
  data_root_id: UUID
  environment: Environment

DataRootLocator
  path: Path

LoadedDataRootMarker
  marker: DataRootMarker
  marker_content_hash: 64-character lowercase SHA-256 hexadecimal string

VerifiedEnvironmentBinding
  expected: ExpectedEnvironmentBinding
  marker: DataRootMarker
  locator: DataRootLocator
  marker_content_hash: 64-character lowercase SHA-256 hexadecimal string

BindingFailureClass
  DATA_STORAGE_UNAVAILABLE
  DATA_STORAGE_IDENTITY_MISMATCH
  ENVIRONMENT_BINDING_MISMATCH

BindingFailureCode
  DATA_ROOT_MISSING
  DATA_ROOT_ACCESS_DENIED
  DEVICE_UNAVAILABLE
  MARKER_READ_FAILED
  MARKER_MISSING
  MALFORMED_JSON
  JSON_ROOT_NOT_OBJECT
  MISSING_FIELD
  UNKNOWN_FIELD
  DUPLICATE_FIELD
  INVALID_FIELD_TYPE
  UNSUPPORTED_SCHEMA_VERSION
  INVALID_STATE_ID
  INVALID_DATA_ROOT_ID
  INVALID_ENVIRONMENT
  INVALID_CREATED_AT
  STATE_ID_MISMATCH
  DATA_ROOT_ID_MISMATCH
  ENVIRONMENT_MISMATCH

BindingFailure
  failure_classes: non-empty frozenset[BindingFailureClass]
  codes: non-empty tuple[BindingFailureCode, ...]
  locator: DataRootLocator

TestEnvironmentGuardFailureCode
  TEST_ENVIRONMENT_REQUIRED

TestEnvironmentGuardFailure
  code: TestEnvironmentGuardFailureCode
  locator: DataRootLocator

WriteTargetPathFailureCode
  INVALID_VERIFIED_ROOT
  EMPTY_PATH
  ABSOLUTE_PATH
  DRIVE_QUALIFIED_PATH
  UNC_PATH
  DEVICE_NAMESPACE_PATH
  PARENT_TRAVERSAL
  SELF_REFERENCE
  ALTERNATE_DATA_STREAM
  RESERVED_DEVICE_NAME
  TRAILING_DOT_OR_SPACE
  INVALID_CHARACTER

WriteTargetPathFailure
  code: WriteTargetPathFailureCode
  relative_path: string

ResolvedWriteTarget
  binding: VerifiedEnvironmentBinding
  relative_path: PureWindowsPath
  target_path: Path
```

L0 Marker validation用の型は`data_root_marker.py`側に置き、`BindingFailureCode`、`BindingFailureClass`、`BindingFailure`へ依存させない。最低限、次の定義をContractとする。

```python
class MarkerValidationErrorCode(str, Enum):
    MALFORMED_JSON = "MALFORMED_JSON"
    JSON_ROOT_NOT_OBJECT = "JSON_ROOT_NOT_OBJECT"
    MISSING_FIELD = "MISSING_FIELD"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    DUPLICATE_FIELD = "DUPLICATE_FIELD"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    UNSUPPORTED_SCHEMA_VERSION = "UNSUPPORTED_SCHEMA_VERSION"
    INVALID_STATE_ID = "INVALID_STATE_ID"
    INVALID_DATA_ROOT_ID = "INVALID_DATA_ROOT_ID"
    INVALID_ENVIRONMENT = "INVALID_ENVIRONMENT"
    INVALID_CREATED_AT = "INVALID_CREATED_AT"


@dataclass(frozen=True)
class MarkerValidationError:
    code: MarkerValidationErrorCode
    field_name: str | None = None


@dataclass(frozen=True)
class MarkerValidationFailure:
    errors: tuple[MarkerValidationError, ...]
```

`MarkerValidationFailure.errors`はnon-emptyとする。`MarkerValidationError`は機械可読なvalidation errorであり、`field_name`は該当fieldがある場合だけ設定する。JSON文書全体に対する`MALFORMED_JSON`および`JSON_ROOT_NOT_OBJECT`では`field_name = None`とする。fieldを特定できるSchema / Domain errorでは該当するJSON field名を設定する。

`data_root_marker.py`から`environment_binding.py`へのimportまたは循環依存を作らない。

`ExpectedEnvironmentBinding.state_id`と`ExpectedEnvironmentBinding.data_root_id`はUUID v4、`ExpectedEnvironmentBinding.environment`は`Environment`でなければならず、constructorでこのinvariantを検証する。`state_id != data_root_id`はinvariantにしない。

`ExpectedEnvironmentBinding`はRuntime側からinjectする。Data Root内のMarker、Data、path、drive letter、Volume GUID、Volume Label、その他のfilesystem情報からexpected bindingを導出してはならない。Gate Aではconfig / manifestの具体形式を定義しない。

`VerifiedEnvironmentBinding`は単純なbooleanの代替ではない。検証対象Locator、期待値、読込済みMarker、Marker bytesのSHA-256を保持する。`marker_content_hash`はexactly 64 charactersかつlowercase hexadecimal `[0-9a-f]`だけとし、`sha256:` prefixを付けない。SHA-256はIdentity判定に使用せず、検証Evidenceとして使用する。

`VerifiedEnvironmentBinding`の正規生成経路は`verify_environment_binding()`とし、successful verificationを表すtokenとして扱う。Python constructorを技術的に呼出不能にするprivate sentinel、factory token、hidden constructor、runtime caller inspection等は導入しない。

`LoadedDataRootMarker`は`@dataclass(frozen=True)`とし、load境界で一度だけ読み込んだ同一bytesから得た`marker`と`marker_content_hash`を保持する。`marker_content_hash`の形式は`VerifiedEnvironmentBinding`と同じ64-character lowercase hexadecimal SHA-256とし、`sha256:` prefixを付けない。

`TestEnvironmentGuardFailureCode`、`TestEnvironmentGuardFailure`、`WriteTargetPathFailureCode`、`WriteTargetPathFailure`、`ResolvedWriteTarget`は`environment_guard.py`側の`Enum`または`@dataclass(frozen=True)`として定義する。Contract-defined rejectionは例外を通常制御に使わず、明示的なfailure valueとして返す。

`TestEnvironmentGuardFailure`はexactly一つの`code`と対象`locator`を持つ。`WriteTargetPathFailure`はexactly一つの`code`とcallerが渡した未変更の`relative_path`文字列を持つ。`ResolvedWriteTarget`はfresh verificationで得た`binding`、正規化済みのrelative `PureWindowsPath`、およびそのbindingのroot配下にあるabsolute `target_path`を持つ。いずれも追加の任意diagnostic fieldをGate AのExact Oracleへ要求しない。

------------------------------------------------------------------------

# 5. Verification Contract

## 5.1 Primary comparison

次を規範的に`state_id`、`data_root_id`、`environment`の順で比較する。

```text
marker.state_id     == expected.state_id
marker.data_root_id == expected.data_root_id
marker.environment  == expected.environment
```

すべて一致した場合だけ`VerifiedEnvironmentBinding`を返す。一つでも不一致がある場合は`BindingFailure`を返す。

複数の不一致は最初の一件でshort-circuitせず、該当するfailure classの`frozenset`と、すべてのfailure codeのtupleを保持する。codeの規範的orderingは`STATE_ID_MISMATCH`、`DATA_ROOT_ID_MISMATCH`、`ENVIRONMENT_MISMATCH`とし、該当しないcodeは省略する。failure classにはorderingを定義せず、同一classを重複保持しない。

Schema validationに失敗したMarkerの一部フィールドを使ってIdentity比較を続行してはならない。

## 5.2 Verification lifetime

最低限、次の二つのboundaryでそれぞれ`data_root_marker.json`をloadし、検証する。

1. startup時
2. write-capable boundaryへ入る直前

write-capable boundaryはstartup時の検証結果だけを根拠に成功してはならない。`load_and_verify_environment_binding()`を新たに一回呼び、その呼出しが返した`VerifiedEnvironmentBinding`を当該boundaryのpath containmentへ渡す。新規呼出しが`BindingFailure`ならwrite-capable成功状態へ進まず、write side effectを発生させない。

`VerifiedEnvironmentBinding`は検証対象Locatorを保持する。同じ`state_id / data_root_id / environment / locator`に正当に拘束されたWriter instance同士をEnvironment Binding authorization上は区別しない。Python object identity、startup時と別instanceであること、Writer instance identityはauthorization条件にしない。

Gate Aでは具体的なproduction Writer lifecycle、OS device notification監視、filesystem metadataの読込前後比較、verificationから実writeまでの完全なTOCTOU防止を実装しない。正しいBinding再検証後の復帰を含む完全なCV-44はL3で扱う。

## 5.3 Read consistency

Markerはbytesとして読み、そのbytesのSHA-256を計算する。同じbytesをJSON parse / validationへ使用し、成功時の`VerifiedEnvironmentBinding.marker_content_hash`へ64-character lowercase hexadecimal SHA-256を保存する。Environment Binding domain上のhashには`sha256:` prefixを付けない。Test Strategy §18.1のartifact参照形式`sha256:<64 lowercase hex>`とは別の表現である。

hash一致だけでIdentityを成立させてはならない。

raw Marker bytesからhashを計算する責務は`data_root_marker_store.py`のload境界に置く。`verify_environment_binding()`はraw bytesを受け取らず、precomputed `marker_content_hash`を受け取り、成功時にその値をVerified tokenへ保持する。comparison failure時の`BindingFailure`に`marker_content_hash`を保持する要求は設けない。成功token内のhash形式は`VerifiedEnvironmentBinding`のconstructor invariantで保証する。

`load_data_root_marker()`はMarker fileを一度だけbytesとして読み込む。その同一bytesをSHA-256計算と`parse_data_root_marker()`の双方へ渡し、成功時に`LoadedDataRootMarker`を返す。hash用とparse用に別々のfilesystem readを行ってはならない。

------------------------------------------------------------------------

# 6. Failure Model

## 6.1 Failure class

```text
DATA_STORAGE_UNAVAILABLE
DATA_STORAGE_IDENTITY_MISMATCH
ENVIRONMENT_BINDING_MISMATCH
```

`BindingFailure.failure_classes`はnon-emptyな`frozenset[BindingFailureClass]`とし、immutableかつ同一classを重複保持しない。

## 6.2 Failure code

`BindingFailureCode`として最低限、次のcodeを定義する。

```text
DATA_ROOT_MISSING
DATA_ROOT_ACCESS_DENIED
DEVICE_UNAVAILABLE
MARKER_READ_FAILED
MARKER_MISSING
MALFORMED_JSON
JSON_ROOT_NOT_OBJECT
MISSING_FIELD
UNKNOWN_FIELD
DUPLICATE_FIELD
INVALID_FIELD_TYPE
UNSUPPORTED_SCHEMA_VERSION
INVALID_STATE_ID
INVALID_DATA_ROOT_ID
INVALID_ENVIRONMENT
INVALID_CREATED_AT
STATE_ID_MISMATCH
DATA_ROOT_ID_MISMATCH
ENVIRONMENT_MISMATCH
```

`BindingFailure.codes`はnon-emptyな`tuple[BindingFailureCode, ...]`とし、ordered immutable collectionとする。failure codeを包む中間objectは設けない。field name、expected value、actual value、messageは現Contractの`BindingFailure`に保持しない。

OS / filesystem errorの機密情報を含み得る文字列やMarker全文を、failure code以外の追加情報として無加工で保存しない。

## 6.3 Failure mapping

| Condition | Failure class | Required code |
|---|---|---|
| Data Root不存在 | `DATA_STORAGE_UNAVAILABLE` | `DATA_ROOT_MISSING` |
| Data Rootアクセス不能 / permission failure | `DATA_STORAGE_UNAVAILABLE` | `DATA_ROOT_ACCESS_DENIED` |
| device unavailable / disconnected | `DATA_STORAGE_UNAVAILABLE` | `DEVICE_UNAVAILABLE` |
| OS / filesystem I/O read failure | `DATA_STORAGE_UNAVAILABLE` | `MARKER_READ_FAILED` |
| Marker missing | `DATA_STORAGE_IDENTITY_MISMATCH` | `MARKER_MISSING` |
| malformed JSON | `DATA_STORAGE_IDENTITY_MISMATCH` | `MALFORMED_JSON` |
| JSON rootがobjectでない | `DATA_STORAGE_IDENTITY_MISMATCH` | `JSON_ROOT_NOT_OBJECT` |
| 必須field欠落 | `DATA_STORAGE_IDENTITY_MISMATCH` | `MISSING_FIELD` |
| unknown field | `DATA_STORAGE_IDENTITY_MISMATCH` | `UNKNOWN_FIELD` |
| duplicate field | `DATA_STORAGE_IDENTITY_MISMATCH` | `DUPLICATE_FIELD` |
| field type不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `INVALID_FIELD_TYPE` |
| schema version不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `UNSUPPORTED_SCHEMA_VERSION` |
| state UUID不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `INVALID_STATE_ID` |
| data-root UUID不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `INVALID_DATA_ROOT_ID` |
| environment値不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `INVALID_ENVIRONMENT` |
| timestamp不正 | `DATA_STORAGE_IDENTITY_MISMATCH` | `INVALID_CREATED_AT` |
| `state_id` mismatch | `ENVIRONMENT_BINDING_MISMATCH` | `STATE_ID_MISMATCH` |
| `environment` mismatch | `ENVIRONMENT_BINDING_MISMATCH` | `ENVIRONMENT_MISMATCH` |
| `data_root_id` mismatch | `DATA_STORAGE_IDENTITY_MISMATCH` | `DATA_ROOT_ID_MISMATCH` |

Filesystem failureは次のoperation stageで分類する。

| Stage | Operation |
|---|---|
| A | Data Rootへの到達とdirectory確認 |
| B | `data_root_marker.json`のopen / read |
| C | 同一directory temp fileのexclusive create / write / flush / fsync |
| D | temp fileのtarget名へのno-overwrite publish |
| E | publish済みtargetのreload / parse / domain equality確認 |

load時のStage A / B mappingを次に固定する。

| Observed condition | Failure class | Required code |
|---|---|---|
| Stage AでData Rootが存在しない | `DATA_STORAGE_UNAVAILABLE` | `DATA_ROOT_MISSING` |
| Stage AでData Rootは存在するがdirectoryではない | `DATA_STORAGE_UNAVAILABLE` | `MARKER_READ_FAILED` |
| Stage A / Bでアクセス拒否 | `DATA_STORAGE_UNAVAILABLE` | `DATA_ROOT_ACCESS_DENIED` |
| Stage A / Bで§6.4のdevice-unavailable WinErrorを観測 | `DATA_STORAGE_UNAVAILABLE` | `DEVICE_UNAVAILABLE` |
| Stage BでData Rootの存在を確認済みだがMarkerが存在しない | `DATA_STORAGE_IDENTITY_MISMATCH` | `MARKER_MISSING` |
| Stage A / Bの上記以外のOS / filesystem read failure | `DATA_STORAGE_UNAVAILABLE` | `MARKER_READ_FAILED` |

`MARKER_READ_FAILED`がOS / filesystem I/O原因の場合は`DATA_STORAGE_UNAVAILABLE`へ分類する。

`parse_data_root_marker()`はFilesystem failure classおよびBinding failure classを扱わない。malformed JSON、duplicate field、Schema validation、Domain validationだけを扱い、失敗を`MarkerValidationFailure`として明示的に返す。validation failureを例外による通常制御へ変換しない。

`MarkerValidationFailure`から`BindingFailure`への変換は、後段の`load_data_root_marker()`または`load_and_verify_environment_binding()`の責務とする。Marker内容のvalidation errorは後段で`DATA_STORAGE_IDENTITY_MISMATCH`へmappingし、各`MarkerValidationErrorCode`と同名の`BindingFailureCode`へ意味を保って変換する。このmappingのために`data_root_marker.py`から`environment_binding.py`を参照してはならない。

一つの`MarkerValidationFailure`に複数のerrorがある場合、変換後の`BindingFailure.codes`は元の`errors`の順序を保持し、省略、重複排除、最初の一件へのshort-circuitを行わない。`failure_classes`は`frozenset({DATA_STORAGE_IDENTITY_MISMATCH})`とする。

comparisonのcodeからfailure classへのmappingを次に固定する。

```text
STATE_ID_MISMATCH     → ENVIRONMENT_BINDING_MISMATCH
DATA_ROOT_ID_MISMATCH → DATA_STORAGE_IDENTITY_MISMATCH
ENVIRONMENT_MISMATCH  → ENVIRONMENT_BINDING_MISMATCH
```

`state_id`、`data_root_id`、`environment`がすべて不一致の場合、failure classは次の`frozenset`になる。

```text
frozenset({
  ENVIRONMENT_BINDING_MISMATCH,
  DATA_STORAGE_IDENTITY_MISMATCH
})
```

`codes`は次の3件を規範的orderingですべて保持する。

```text
(
  STATE_ID_MISMATCH,
  DATA_ROOT_ID_MISMATCH,
  ENVIRONMENT_MISMATCH,
)
```

例えば`state_id`と`environment`だけが不一致の場合は、`failure_classes = frozenset({ENVIRONMENT_BINDING_MISMATCH})`、`codes = (STATE_ID_MISMATCH, ENVIRONMENT_MISMATCH)`とする。`data_root_id`と`environment`だけが不一致の場合は、`codes = (DATA_ROOT_ID_MISMATCH, ENVIRONMENT_MISMATCH)`とする。

## 6.4 Windows WinError classification

Windows native実装では、アクセス拒否とdevice / path unavailableを次のclosed setで判定する。symbolic nameとdecimal valueはMicrosoftのSystem Error Codesを規範参照とする。

アクセス拒否集合:

| Symbol | Value |
|---|---:|
| `ERROR_ACCESS_DENIED` | 5 |
| `ERROR_NETWORK_ACCESS_DENIED` | 65 |

device / path unavailable集合:

| Symbol | Value |
|---|---:|
| `ERROR_INVALID_DRIVE` | 15 |
| `ERROR_BAD_UNIT` | 20 |
| `ERROR_NOT_READY` | 21 |
| `ERROR_BAD_NETPATH` | 53 |
| `ERROR_DEV_NOT_EXIST` | 55 |
| `ERROR_BAD_NET_NAME` | 67 |
| `ERROR_DEVICE_UNREACHABLE` | 321 |

判定には`OSError.winerror`の値を使う。アクセス拒否集合を先に判定し、次にdevice / path unavailable集合を判定する。`ERROR_FILE_NOT_FOUND` (2) と`ERROR_PATH_NOT_FOUND` (3) はdevice-unavailable集合に含めず、Stage A / Bの観測結果により`DATA_ROOT_MISSING`または`MARKER_MISSING`へ分類する。closed set外のread failureは`MARKER_READ_FAILED`とする。Windows以外のplatform mappingはGate A対象外であり、本節から推測しない。

規範参照:

- Microsoft Learn, *System Error Codes (0-499)*: <https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499->

------------------------------------------------------------------------

# 7. Marker Initialization Contract

Marker作成は通常startupから分離した、明示的なinitialization operationでのみ行う。

通常startupは次を行わない。

- Markerの新規作成
- 欠落Markerの補完
- 不正Markerの修復
- 既存Markerの上書き

## 7.1 Initialization error

Initialization errorは`BindingFailure`と分離し、例外ではなく明示的な戻り値である`MarkerInitializationError`系として扱う。これらは`Exception`を継承しないfrozen dataclass value objectとし、次を区別する。

```python
@dataclass(frozen=True)
class MarkerInitializationError:
    pass


@dataclass(frozen=True)
class DataRootInitializationUnavailable(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerAlreadyExists(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerAtomicWriteFailed(MarkerInitializationError):
    pass


@dataclass(frozen=True)
class MarkerReloadVerificationFailed(MarkerInitializationError):
    pass
```

通常想定されるinitialization failureは上記valueとして返す。programming errorまたは違反したPython-level preconditionまで`MarkerInitializationError`へ変換する要求、および内部cause chainingをpublic Contractとして保持する要求は設けない。

## 7.2 Atomic initialization

初期化はCallerから完成済みの`DataRootMarker`を受け取る。StoreはUUID、Environment、`created_at`を生成または補完しない。初期化は次の順序を満たす。

```text
明示的な単一管理Operation
  ↓
同一directoryにtemp fileを作成
  ↓
全bytesを書込
  ↓
flush
  ↓
fsync
  ↓
既存targetを上書きせずtarget名へ確定
  ↓
targetをreload
  ↓
Schema / Domain validation
  ↓
保存予定Markerとの一致確認
```

既存の`data_root_marker.json`がある場合は、内容が同一でも上書きしない。初期化失敗時のtemp fileを有効Markerとして扱わない。

並列initializationはGate Aではunsupportedであり、単一管理Operationであることをpreconditionとする。それでも既存targetを上書きしてはならない。

Windows nativeのStage Dは、同一directory / 同一volumeにexclusive createしたtemp fileのhandleに対し、`SetFileInformationByHandle(..., FileRenameInfo, ...)`と`FILE_RENAME_INFO.ReplaceIfExists = FALSE`を用いる最小Win32境界で実装する。Python標準libraryのrename関数へno-overwrite atomicityを推測して委ねない。copy、delete-then-rename、既存targetの置換へのfallbackを禁止する。

`CreateFileW`が成功してpublish用HANDLEを取得した後は、target pathのUTF-16表現への変換、`FILE_RENAME_INFO` bufferの構築、publish request表現の構築、および`SetFileInformationByHandle`の実行を含むHANDLE lifecycle全体を`finally`相当の保証で保護する。この範囲の処理結果にかかわらず`CloseHandle`を実行し、HANDLE leakを許可しない。

Contract-validなpathと内部引数を処理しているにもかかわらず、target pathのUTF-16表現への変換、`FILE_RENAME_INFO` bufferのallocation / construction、またはpublish request表現のconstructionでruntime failureが発生した場合は、Stage Dのexpected publish-preparation failureとして`MarkerAtomicWriteFailed`へmappingする。これはStage Dのpublish failureの一部であり、弱いpublish手段へのfallbackを許可しない。

一方、internal invariant violation、programmerが導入した`TypeError`、impossible internal state、またはWin32 / ctypes APIの誤用等、実装不備によるprogramming errorもしくはPython-level precondition violationは、このmappingの対象ではない。この境界はあらゆる`Exception`を捕捉して`MarkerAtomicWriteFailed`へ変換することを要求しない。

このContractでいうatomic publishは、完全にwrite / flush / fsync済みのtemp fileが、単一のfilesystem rename namespace operationによってtarget名に現れ、target名からpartial bytesが観測されないことを意味する。実装対象は、このsame-volume rename semanticsを提供するWindows filesystemに限定する。APIまたはfilesystemがこれを提供できない場合は`MarkerAtomicWriteFailed`とし、弱い手段へfallbackしない。

Win32 publish callはstore module内の一つのinternal adapter境界（例: `_publish_no_replace(temp_path, target_path)`）へ隔離し、unit testのfailure injection / patch boundaryとする。`ReplaceIfExists = FALSE`によるpublish失敗後にtargetが存在する場合は、pre-check後の競合を含め`MarkerAlreadyExists`へmappingする。targetが存在しないその他のpublish failureは`MarkerAtomicWriteFailed`とする。

規範参照:

- Microsoft Learn, `FILE_RENAME_INFO`: <https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info>
- Microsoft Open Specifications, `FileRenameInformationEx`: <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/4217551b-d2c0-42cb-9dc1-69a716cf6d0c>

## 7.3 Initialization failure mapping and cleanup

| Condition / stage | Exact result | Target side effect |
|---|---|---|
| Stage A開始前またはStage AでData Rootを利用不能 | `DataRootInitializationUnavailable` | targetを作成しない |
| Stage C開始前にtargetが既存 | `MarkerAlreadyExists` | 既存targetを変更しない |
| Stage Cのtemp create / write / flush / fsync失敗 | `MarkerAtomicWriteFailed` | targetを作成しない |
| Stage DでHANDLE取得後、Contract-valid inputに対するUTF-16変換、rename buffer、またはpublish request表現の構築がruntime failure | `MarkerAtomicWriteFailed` | targetを作成せず、取得済みHANDLEを閉じる |
| Stage Dのpublish失敗かつtarget不存在 | `MarkerAtomicWriteFailed` | targetを作成しない |
| Stage Dのpublish競合でtargetが存在 | `MarkerAlreadyExists` | 競合相手のtargetを変更しない |
| Stage Eのreload read / parse / domain equality確認失敗 | `MarkerReloadVerificationFailed` | publish済みtargetを自動削除・修復しない |

Stage D完了前の失敗では、final targetを作成してはならない。temp file cleanupはbest effortとし、cleanup失敗で主failure resultを置換しない。残存temp fileはMarkerとして扱わず、startup / loadは固定名`data_root_marker.json`以外を読まない。

Stage D完了後のStage E失敗では、final targetを自動削除、上書き、修復しない。failureを返し、operatorによる明示的な調査と是正を要求する。

Normal startupは、このpublish済みtargetについて通常のload + verificationが成功しない限り、Verified bindingとして使用してはならない。repair、delete、reinitializeは別の明示的management operationの責務とし、本Contractでは定義しない。

## 7.4 Reload verification

Stage Eはpublish済みtargetを`load_data_root_marker()`と同じread / parse contractでreloadする。成功にはreloadされたMarkerの全5 fieldが初期化入力とdomain valueとして等しいことを要求する。

- `schema_version`、`state_id`、`data_root_id`、`environment`は値の等価性で比較する。
- `created_at`はtimezone-aware datetimeのlogical instant equalityで比較する。timezone表記またはoffset表現の文字列一致は要求しない。
- reload bytesと`serialize_data_root_marker(marker)`のbyte-for-byte一致は要求しない。

全fieldが等しい場合だけreloadされた`DataRootMarker`を返す。不一致は`MarkerReloadVerificationFailed`とする。

------------------------------------------------------------------------

# 8. Public API / Module Boundary

production code実装時の最小module境界を次とする。

```text
src/argus/runtime/environment.py
  Environment

src/argus/runtime/data_root_marker.py
  DataRootMarker
  MarkerValidationErrorCode
  MarkerValidationError
  MarkerValidationFailure
  parse_data_root_marker()
  serialize_data_root_marker()
  Marker schema / domain validation
  deterministic serialization

src/argus/runtime/data_root_locator.py
  DataRootLocator

src/argus/runtime/environment_binding.py
  ExpectedEnvironmentBinding
  VerifiedEnvironmentBinding
  BindingFailureClass
  BindingFailureCode
  BindingFailure
  verify_environment_binding()

src/argus/runtime/data_root_marker_store.py
  LoadedDataRootMarker
  load_data_root_marker()
  load_and_verify_environment_binding()
  initialize_data_root_marker()
  MarkerInitializationError hierarchy

src/argus/runtime/environment_guard.py
  TestEnvironmentGuardFailureCode
  TestEnvironmentGuardFailure
  WriteTargetPathFailureCode
  WriteTargetPathFailure
  ResolvedWriteTarget
  verify_test_environment_startup()
  resolve_test_write_target()
```

module dependencyは次のDAGとする。

```text
environment.py ─> data_root_marker.py ─┐
       │                               ├─> environment_binding.py ─> data_root_marker_store.py
       └───────────────────────────────┤              ▲                 ▲
                                       │              │                 │
data_root_locator.py ──────────────────┴──────────────┘─────────────────┘
       │                                                              │
       └──────────────────────────────> environment_guard.py <─────────┘
```

より正確には、`data_root_marker_store.py`は`data_root_marker.py`、`data_root_locator.py`、`environment_binding.py`へ依存してよい。`environment_binding.py`から`data_root_marker_store.py`への依存、および両module間の双方向dependencyを禁止する。`DataRootLocator`は`data_root_locator.py`だけで定義し、store側で再定義しない。

最低限のpublic API contractは次とする。

```python
def parse_data_root_marker(
    data: bytes,
) -> DataRootMarker | MarkerValidationFailure:
    ...


def serialize_data_root_marker(
    marker: DataRootMarker,
) -> bytes:
    ...


def verify_environment_binding(
    locator: DataRootLocator,
    marker: DataRootMarker,
    marker_content_hash: str,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure:
    ...


@dataclass(frozen=True)
class LoadedDataRootMarker:
    marker: DataRootMarker
    marker_content_hash: str


def load_data_root_marker(
    locator: DataRootLocator,
) -> LoadedDataRootMarker | BindingFailure:
    ...


def load_and_verify_environment_binding(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure:
    ...


def initialize_data_root_marker(
    locator: DataRootLocator,
    marker: DataRootMarker,
) -> DataRootMarker | MarkerInitializationError:
    ...


def verify_test_environment_startup(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
) -> VerifiedEnvironmentBinding | BindingFailure | TestEnvironmentGuardFailure:
    ...


def resolve_test_write_target(
    locator: DataRootLocator,
    expected: ExpectedEnvironmentBinding,
    relative_path: str,
) -> (
    ResolvedWriteTarget
    | BindingFailure
    | TestEnvironmentGuardFailure
    | WriteTargetPathFailure
):
    ...
```

`parse_data_root_marker()`は入力bytesに対して、duplicate検出、JSON parse、Schema validation、Domain validationの順で処理する。成功時は`DataRootMarker`、validation失敗時はnon-emptyな`MarkerValidationFailure`を返す。invalid inputを補正・正規化して受理しない。Filesystem path、Locator、Filesystem exception、Binding expected valueは扱わない。

`serialize_data_root_marker()`は§3.3および§3.4に従い、UTF-8、BOMなし、LF、2-space indent、固定key order、final newlineを保証する。`created_at`はUTCへ正規化して`Z`表記にする。

`verify_environment_binding()`はfilesystem I/O、Marker JSON parse、Marker schema validation、hash計算、Expected bindingの推論を行わない。`state_id`、`data_root_id`、`environment`の順に比較し、全一致時は`VerifiedEnvironmentBinding`、一件以上の不一致時は全Mismatchを収集した`BindingFailure`を返す。

`load_data_root_marker()`は読み込んだ同一bytesからSHA-256を計算し、`parse_data_root_marker()`を呼ぶ。返された`MarkerValidationFailure`を本書§6.3に従って`DATA_STORAGE_IDENTITY_MISMATCH`の`BindingFailure`へmappingする。Filesystem failureの分類もこのFilesystem境界で行う。

`load_and_verify_environment_binding()`は`load_data_root_marker(locator)`を一度呼ぶ。`BindingFailure`ならその値をそのまま返す。`LoadedDataRootMarker`なら、その`marker`と`marker_content_hash`を`verify_environment_binding(locator, marker, marker_content_hash, expected)`へ渡し、その結果を返す。Store内でIdentity comparisonを複製してはならない。

`initialize_data_root_marker()`は§7のStage A〜Eを実行し、成功時はStage Eでreloadされた`DataRootMarker`、失敗時は対応する`MarkerInitializationError` valueを返す。通常のvalidation / initialization failureを例外として外へ漏らさない。

`verify_test_environment_startup()`は`expected.environment is Environment.TEST`でなければ、filesystemを読まず`TestEnvironmentGuardFailure(TEST_ENVIRONMENT_REQUIRED, locator)`を返す。TESTの場合だけ`load_and_verify_environment_binding(locator, expected)`を一回呼び、その`VerifiedEnvironmentBinding`または`BindingFailure`を変更せず返す。Marker作成、修復、fallbackを行わない。

`resolve_test_write_target()`は§8.1の順序でrelative pathを検証した後、`expected.environment is Environment.TEST`を要求し、`load_and_verify_environment_binding(locator, expected)`を新たに一回呼ぶ。成功時だけ、当該呼出しが返したbinding、正規化済み`PureWindowsPath`、および検証済みroot配下のtarget `Path`を持つ`ResolvedWriteTarget`を返す。startup時のresultを引数に取らず、Guard内でIdentity comparisonを複製しない。

`StartupAuthorization`、`WriteAuthorization`、`writer_id`、Writer-instance固有Capability Tokenを導入しない。`ResolvedWriteTarget`はpath containmentの成功結果であり、Writer-instance authorization tokenではない。

具体的なproduction Writer classとそのlifecycleはGate Aの本Contract実装範囲外である。Gate AはBinding verification、fail-closed guard boundary、path containment primitive、および後段write mechanismが従うContractを確立する。Data Root配下へwriteする各production Writer / Queue / Incident / Execution Fact / raw / normalized / archive / backupは、それぞれの実装Capabilityでwrite-capable boundaryとpath containmentへの拘束を検証する。Gate Aでは未実装の全write経路が実際にこのprimitiveを通ることをGREEN条件にしない。

read境界はwrite境界と分離する。Marker readはverificationに必要であり禁止しない。未検証またはverification失敗Rootのcanonical data/stateを動作入力に使用するかどうかは後段Capabilityで定義し、本write guardへ混在させない。

## 8.1 Windows lexical path containment

`resolve_test_write_target()`のpath containmentはWindows nativeの字句規則として決定論的に行う。単純なstring prefix比較をcontainment保証に使用しない。

validation順序とexact failure codeを次に固定する。最初に該当した一件を返し、複数codeを収集しない。

1. `relative_path == ""` → `EMPTY_PATH`
2. `\\\\?\\`または`\\\\.\\` prefix（separatorの`/`表記を`\\`相当として解釈したものを含む）→ `DEVICE_NAMESPACE_PATH`
3. UNC path → `UNC_PATH`
4. driveを持ちrootedなpath → `ABSOLUTE_PATH`
5. drive-qualified relative path（例: `C:x.json`）→ `DRIVE_QUALIFIED_PATH`
6. leading `/`または`\\`を持つrooted path → `ABSOLUTE_PATH`
7. componentが`..` → `PARENT_TRAVERSAL`
8. path全体またはいずれかのcomponentが`.` → `SELF_REFERENCE`
9. componentが空（連続separatorまたは末尾separatorによるもの）→ `EMPTY_PATH`
10. NULまたはWindows invalid character `< > " | ? *` → `INVALID_CHARACTER`
11. component内の`:` → `ALTERNATE_DATA_STREAM`
12. component末尾がdotまたはspace → `TRAILING_DOT_OR_SPACE`
13. componentの最初のdotより前をcase-insensitiveに比較したbasenameが`CON`、`PRN`、`AUX`、`NUL`、`COM1`〜`COM9`、`LPT1`〜`LPT9` → `RESERVED_DEVICE_NAME`

`/`と`\\`はどちらもseparatorとして受理し、mixed separatorも同じcomponent列へ正規化する。出力`relative_path`は`PureWindowsPath`で表し、`.`、`..`、空componentを正規化によって暗黙受理しない。

bindingの`locator.path`はWindows absolute pathでなければならず、満たさない場合は`INVALID_VERIFIED_ROOT`を返す。受理済みcomponentをrootへjoinし、Windows case-insensitive semanticsで`ntpath.commonpath((root, target)) == root`を確認する。不一致またはdifferent-drive errorは`PARENT_TRAVERSAL`とする。比較は`ntpath.normcase`と`ntpath.normpath`相当を使用し、string prefixだけで判定しない。

Gate Aの本primitiveはlexical containmentだけを保証する。symlink、junction、その他reparse point、8.3 short name、mount point、verification後のdevice replacement、filesystem metadata race、および実writeまでのTOCTOU完全防止は扱わない。これらは各production Writer / Runtime CapabilityおよびCV-44 / RV-34で扱う後段事項であり、Gate Aで安全が確認済みと表示しない。

------------------------------------------------------------------------

# 9. Test ID / Acceptance Criteria

Test IDはCapability内の安定IDであり、CV-44 / RV-34そのものとは区別する。

## 9.1 L0 Marker validation

| Test ID | Test | Acceptance Criteria |
|---|---|---|
| `EB-L0-001` | valid Marker | `parse_data_root_marker()`が5 fieldだけを持つschema version 1のbytesから`DataRootMarker`を返す |
| `EB-L0-002` | missing required field | default補完せず、`MISSING_FIELD`と該当`field_name`を持つ`MarkerValidationFailure`を返す |
| `EB-L0-003` | unknown field | unknown fieldを破棄せず、`UNKNOWN_FIELD`と該当`field_name`を持つ`MarkerValidationFailure`を返す |
| `EB-L0-004` | duplicate field | last-value-winsにせず、`DUPLICATE_FIELD`と該当`field_name`を持つ`MarkerValidationFailure`を返す |
| `EB-L0-005` | non-object JSON root | `JSON_ROOT_NOT_OBJECT`で拒否する |
| `EB-L0-006` | invalid field type | 暗黙変換せず`INVALID_FIELD_TYPE`で拒否する |
| `EB-L0-007` | unsupported schema version | version 1以外を`UNSUPPORTED_SCHEMA_VERSION`で拒否する |
| `EB-L0-008` | JSON boolean schema version | `true` / `false`をintegerとして受理せず、`INVALID_FIELD_TYPE`と`field_name = "schema_version"`を返す |
| `EB-L0-009` | canonical UUID v4 | lowercase + hyphen形式のUUID v4を受理する |
| `EB-L0-010` | non-v4 UUID | canonical表記でもv4以外を拒否する |
| `EB-L0-011` | non-canonical UUID | uppercase、brace、URN、hyphenなしを補正せず、対象IDに対応するerror codeと`field_name`を返す |
| `EB-L0-012` | invalid environment | TEST / PAPER / LIVE以外を拒否する |
| `EB-L0-013` | accepted RFC3339 | `Z`、`±HH:MM`、小数秒なし〜6桁を受理する |
| `EB-L0-014` | rejected timestamp | naive、offset秒、leap second、space separator、7桁以上小数秒を補正せず、`INVALID_CREATED_AT`と`field_name = "created_at"`を返す |
| `EB-L0-015` | deterministic serialization | `serialize_data_root_marker()`がUTF-8 BOMなし、LF、2-space indent、固定key order、final newlineのbytesを返す |
| `EB-L0-016` | UTC normalization | `serialize_data_root_marker()`が`created_at`をUTCへ正規化し`Z`表記のbytesを返す |

## 9.2 L0 Binding comparison

| Test ID | Test | Acceptance Criteria |
|---|---|---|
| `EB-L0-020` | all identities match | `VerifiedEnvironmentBinding`を返す |
| `EB-L0-021` | state mismatch | `frozenset({ENVIRONMENT_BINDING_MISMATCH})`と`(STATE_ID_MISMATCH,)`を返す |
| `EB-L0-022` | data-root mismatch | `frozenset({DATA_STORAGE_IDENTITY_MISMATCH})`と`(DATA_ROOT_ID_MISMATCH,)`を返す |
| `EB-L0-023` | environment mismatch | `frozenset({ENVIRONMENT_BINDING_MISMATCH})`と`(ENVIRONMENT_MISMATCH,)`を返す |
| `EB-L0-024` | multiple mismatches | 該当する`frozenset`の全classと、規範的orderingによるtupleの全codeを保持する |
| `EB-L0-025` | locator binding | Verified tokenが検証対象Locatorを保持する |
| `EB-L0-026` | content hash evidence | Verified tokenがprecomputedの64-character lowercase hexadecimal SHA-256を保持するがIdentity判定には使わない |

## 9.3 L1 Marker store / initialization

本節の全Testはrequirement `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE`へtraceし、Contractから期待結果が完全決定される`EXACT_CONTRACT_ORACLE-v1`を使用する。

| Test ID | Requirement | Input / injection | Exact expected result | Failure class / code | Required side effect | API |
|---|---|---|---|---|---|---|
| `EB-L1-001` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Data Root直下にvalid Marker | 同一bytesを一度読み、`LoadedDataRootMarker(marker, sha256(read_bytes).hexdigest())` | N/A | read-only | `load_data_root_marker` |
| `EB-L1-002` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage AでData Root不存在 | `BindingFailure` | `{DATA_STORAGE_UNAVAILABLE}` / `(DATA_ROOT_MISSING,)` | fileを作成しない | `load_data_root_marker` |
| `EB-L1-003` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Data Root directoryは存在、Marker不存在 | `BindingFailure` | `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(MARKER_MISSING,)` | Markerを作成しない | `load_data_root_marker` |
| `EB-L1-004` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage A / BでWinError 5または65 | `BindingFailure` | `{DATA_STORAGE_UNAVAILABLE}` / `(DATA_ROOT_ACCESS_DENIED,)` | writeしない | `load_data_root_marker` |
| `EB-L1-005` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage A / Bで§6.4のdevice-unavailable closed setの各WinError | `BindingFailure` | `{DATA_STORAGE_UNAVAILABLE}` / `(DEVICE_UNAVAILABLE,)` | writeしない | `load_data_root_marker` |
| `EB-L1-006` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage A / Bでclosed set外のread `OSError`、または既存の非directory locator | `BindingFailure` | `{DATA_STORAGE_UNAVAILABLE}` / `(MARKER_READ_FAILED,)` | writeしない | `load_data_root_marker` |
| `EB-L1-007` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Marker bytesがmalformed JSON | `BindingFailure` | `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(MALFORMED_JSON,)` | Markerを変更しない | `load_data_root_marker` |
| `EB-L1-008` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | parseが一件以上のSchema / Domain validation errorを順序付きで返す | `BindingFailure` | `{DATA_STORAGE_IDENTITY_MISMATCH}` / 元errorと同名codeを同じ順序ですべて保持 | Markerを変更しない | `load_data_root_marker` |
| `EB-L1-009` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Data Root、target不存在、valid input Marker、Stage A〜E成功 | reload Markerの5 fieldがinputとdomain equalityを満たす`DataRootMarker` | N/A | fixed targetを一つ作成 | `initialize_data_root_marker` |
| `EB-L1-010` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | targetが既存（同一bytesを含む） | `MarkerAlreadyExists` | N/A | 既存target bytesを変更しない | `initialize_data_root_marker` |
| `EB-L1-011` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage Cまたはtarget不存在のStage Dへfailure injection | `MarkerAtomicWriteFailed` | N/A | final targetを作成しない。temp cleanupはbest effort | `initialize_data_root_marker` |
| `EB-L1-012` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | Stage D成功後、Stage Eのread / parse / domain equality失敗 | `MarkerReloadVerificationFailed` | N/A | publish済みtargetを削除・修復しない | `initialize_data_root_marker` |
| `EB-L1-013` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Markerと全一致expected | `VerifiedEnvironmentBinding` | N/A | read-only、Markerを一度load | `load_and_verify_environment_binding` |
| `EB-L1-014` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Marker、`state_id`だけ不一致 | `BindingFailure` | `{ENVIRONMENT_BINDING_MISMATCH}` / `(STATE_ID_MISMATCH,)` | read-only | `load_and_verify_environment_binding` |
| `EB-L1-015` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Marker、`data_root_id`だけ不一致 | `BindingFailure` | `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(DATA_ROOT_ID_MISMATCH,)` | read-only | `load_and_verify_environment_binding` |
| `EB-L1-016` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Marker、`environment`だけ不一致 | `BindingFailure` | `{ENVIRONMENT_BINDING_MISMATCH}` / `(ENVIRONMENT_MISMATCH,)` | read-only | `load_and_verify_environment_binding` |
| `EB-L1-017` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Marker、3 identity fieldすべて不一致 | `BindingFailure` | `{ENVIRONMENT_BINDING_MISMATCH, DATA_STORAGE_IDENTITY_MISMATCH}` / `(STATE_ID_MISMATCH, DATA_ROOT_ID_MISMATCH, ENVIRONMENT_MISMATCH)` | read-only | `load_and_verify_environment_binding` |
| `EB-L1-018` | `ENVIRONMENT-BINDING-DATA-ROOT-MARKER-STORE` | valid Markerと全一致expected | tokenの`marker_content_hash == sha256(actual_read_bytes).hexdigest()` | N/A | read-only。serialize後bytesや再read bytesをhashしない | `load_and_verify_environment_binding` |

表中のclass集合は`frozenset`、code列はtupleを意味する。`EB-L1-004`と`EB-L1-005`は記載したclosed setをparameterizeして全値を検証する。`EB-L1-008`は少なくとも複数errorを含むcaseを持ち、全codeとorderingの保存を検証する。`EB-L1-011`のStage D publish競合でtargetが出現するcaseは例外として`MarkerAlreadyExists`を期待し、競合targetを変更しないことを検証する。

## 9.4 L1 TEST Environment Binding guard

本節の全Testはrequirement `ENVIRONMENT-BINDING-TEST-ENVIRONMENT-GUARD`へtraceし、`EXACT_CONTRACT_ORACLE-v1`を使用する。`EB-L1-020..027`はFrozen Test作成前のclarificationであり、IDを維持したまま次のOracleへ再構成する。

| Test ID | Requirement | Input / injection | Exact expected result | Failure class / code | Required side effect | API |
|---|---|---|---|---|---|---|
| `EB-L1-020` | `ENVIRONMENT-BINDING-TEST-ENVIRONMENT-GUARD` | valid TEST Marker、3 identity一致のexpected、valid Locator | `VerifiedEnvironmentBinding`。その`expected / marker / locator / marker_content_hash`は当該一回のload-and-verify結果と一致 | N/A | read-only。Markerを一回loadし、作成・修復・上書きしない | `verify_test_environment_startup` |
| `EB-L1-021` | 同上 | expectedとMarkerがともにPAPER、またはともにLIVE | `TestEnvironmentGuardFailure`、startup成功状態なし | N/A / `TEST_ENVIRONMENT_REQUIRED` | filesystemを読まず、write、fallback、Marker変更なし | `verify_test_environment_startup` |
| `EB-L1-022` | 同上 | expectedはTEST、valid Markerの`state_id`だけ不一致。startupおよびwrite-boundaryの両APIをparameterize | `BindingFailure`、成功状態または`ResolvedWriteTarget`なし | `{ENVIRONMENT_BINDING_MISMATCH}` / `(STATE_ID_MISMATCH,)` | read-only。対象Rootへの新規writeなし | 両Guard API |
| `EB-L1-023` | 同上 | expectedはTEST、valid Markerの`data_root_id`だけ不一致。startupおよびwrite-boundaryの両APIをparameterize | `BindingFailure`、成功状態または`ResolvedWriteTarget`なし | `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(DATA_ROOT_ID_MISMATCH,)` | read-only。対象Rootへの新規writeなし | 両Guard API |
| `EB-L1-024` | 同上 | TEST Data RootでMarker missing、またはmalformed JSON。startupおよびwrite-boundaryの両APIをparameterize | 元の`load_and_verify_environment_binding()`と同じ`BindingFailure`、成功状態なし | missing: `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(MARKER_MISSING,)`; malformed: 同class / `(MALFORMED_JSON,)` | Marker、canonical data/state、その他targetを新規作成せず変更しない | 両Guard API |
| `EB-L1-025` | 同上 | startup verification成功後、write-boundary呼出しの`load_and_verify_environment_binding()`を成功またはfailureへinject | write-boundaryごとに新規一回call。成功時はそのcallのbindingを持つ`ResolvedWriteTarget`。failure時は同じ`BindingFailure`を返し成功状態なし | injected failureのclass / codeを変更せず保持 | startup resultだけでは成功しない。failure時write side effectなし | `resolve_test_write_target` |
| `EB-L1-026` | 同上 | §8.1の各拒否classを代表するrelative path、およびvalid mixed-separator relative path | invalid入力は該当codeの`WriteTargetPathFailure`。valid入力はfresh bindingとroot配下targetを持つ`ResolvedWriteTarget` | §8.1のexact code。successはN/A | invalid時filesystem read/writeなし。success targetはverified root配下 | `resolve_test_write_target` |
| `EB-L1-027` | 同上 | startup / write-boundaryのsuccess、Binding failure、Guard failure、path failureをparameterizeし、initialization APIをcallするとTestが失敗するadapter injection | 各caseは上記Oracleどおりのvalueを返し、implicit initialization call countは0 | 各caseに対応するcode | Markerを作成・補完・修復・上書きせず、別Root / Environmentへfallbackしない | 両Guard API |

`EB-L1-021..024`は§9.3のMarker load / Binding comparison algorithm自体を再検証せず、Guardが既存failureを成功へ昇格させないこととside effect不在だけを追加Oracleとする。`EB-L1-025`の本質は新規verification callであり、Python object identityやWriter instance identityではない。`EB-L1-026`は旧writer-specific token requirementを置換する。旧「別Writer instanceへのtoken流用禁止」は廃止し、Windows lexical path containmentへtraceする。

## 9.5 Common fail-closed Acceptance Criteria

検証が成功しない場合、次をすべて満たす。

- `VerifiedEnvironmentBinding`を返さない
- startup成功状態へ進まない
- write-capable成功状態または`ResolvedWriteTarget`を生成しない
- 対象Data Rootへ新規writeしない
- Markerを作成、補完、修復、上書きしない
- 別Data Rootまたは別Environmentへ自動fallbackしない
- 新しい空Canonical Stateを作成しない
- mismatchをwarningだけに降格しない
- Human Correctionで迂回しない

Guardはfailureをwarningへ変換せず、Correction、implicit initialization、別Root、別Environment、または弱いpath判定へfallbackしない。

------------------------------------------------------------------------

# 10. CV / RV / Gate Mapping

- Gate A: 本書のL0 Marker validation、L0 Binding comparison、L1 Marker store、L1 TEST Binding guard、およびWindows lexical path containmentの代表Testを実行可能にし、TEST Environment BindingのObserved Evidenceを保存する。Gate Aは全production write経路の実装・拘束、physical filesystem containment、またはTOCTOU完全防止を保証しない。
- CV-44: 別Diskが同じdrive letterを取得した場合もMarker Identity mismatchでwriteを拒否し、正しいBindingの再検証後に復帰する。完全なCV-44はL3で扱う。
- RV-34: MVS成立後、TEST / PAPER / LIVEのcross-environment write拒否、および実装済み各write経路が共通guard/containment境界を迂回しないことをRegression Verificationとして実行する。

Gate AのPrimary verificationはMarker Identityに基づく。Volume GUID / Volume LabelはGate AのPASS条件にしない。

------------------------------------------------------------------------

# 11. Canonical Implementation / Verification Order

本Capabilityは新規L0 / L1かつCritical Pathであるため、次の順序を変更しない。

```text
本Contract確定
  ↓
Test Code
  ↓
Static Analysis of Test Code
  ↓
Baseline Freeze
  ↓
RED Check + Evidence保存
  ↓
Production Implementation
  ↓
Required Static Analysis
  ↓
GREEN Test
  ↓
Affected CV / RV
  ↓
Claude Code Review
  ↓
Finding disposition
  ↓
Gate判定
```
