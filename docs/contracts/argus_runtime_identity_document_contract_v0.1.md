# argus Runtime Identity Document Contract v0.1

**Status:** `ACCEPTED FOR TEST DESIGN`  
**Capability:** `RUNTIME-IDENTITY-DOCUMENT`  
**Requirement ID:** `RUNTIME-IDENTITY-DOCUMENT-JSON`  
**Authority:** `ARGUS-DA-0003`, canonicalized by `ARGUS-P-0022-v1`, exact contract approved by `ARGUS-P-0023-v1`  
**Scope:** L0 `bytes -> RuntimeIdentity | RuntimeIdentityValidationFailure`

## 1. Purpose

Runtime Identity Documentは、argus processが参照するlogical instance identityを、Data Rootおよびmutable operational Configurationから独立して宣言する不変artifactである。本書はL0 parse / schema validation / domain validation / deterministic serializationのExact Contractであり、Frozen Testが仕様判断なしで実装できるOracleを定義する。

Runtime IdentityはConfiguration、User Status、Domain State、Runtime State、Secretのいずれでもなく、第6の可変Stateカテゴリでもない。通常運用で書き換える設定ではなく、logical instanceを識別する独立した不変artifactである。

## 2. Identity boundary

次のidentityを区別する。

| Category | Meaning | Runtime Identity Documentに含めるか |
|---|---|---|
| Runtime Identity | `state_id` / `environment` / `data_root_id`等のlogical instance identity | 含める |
| Deployment Identity | install path / code version / development・runtime tree | 含めない。Evidence側 |
| Run Identity | run_id / pid / host / start time | 含めない。Runtime State側 |

Runtime Identity Documentへdata root path / drive letter / Volume GUID / Volume Label、mutable operational configuration、Secret値・参照、User Status、Domain State、Runtime State、provider plan tier、code/install pathを含めない。

`data_root_id`はlogical identityである。data root pathはmutable operational locatorであり、後続`RUNTIME-CONFIG-MECHANISM`の責務とする。path、drive letter、Volume GUID、Volume LabelまたはData Root内Markerからexpected identityを導出しない。`environment`をdevelopment/runtime treeから推論しない。

## 3. RuntimeIdentity field contract

Documentは次の5 fieldだけを持つJSON objectとする。

```json
{
  "schema_version": 1,
  "state_id": "12345678-1234-4234-9234-123456789abc",
  "data_root_id": "87654321-4321-4321-8321-cba987654321",
  "environment": "TEST",
  "created_at": "2026-09-20T00:00:00Z"
}
```

| Field | JSON type | Domain type | Exact Contract |
|---|---|---|---|
| `schema_version` | integer | `int` | exactly `1`。JSON booleanはintegerとして扱わない |
| `state_id` | string | `UUID` | canonical lowercase hyphenated UUID v4 |
| `data_root_id` | string | `UUID` | canonical lowercase hyphenated UUID v4 |
| `environment` | string | `Environment` | closed set `TEST`, `PAPER`, `LIVE` |
| `created_at` | string | timezone-aware `datetime` | §3.2のRFC3339 |

`state_id`、`data_root_id`、`environment`がEnvironment Bindingのidentity comparison対象である。`created_at`はDocument作成時刻の必須metadataであり、Binding identity comparisonへ追加しない。`schema_version`は本Document自身のschema versionであり、System、Config、Stateのversionではない。

### 3.1 UUID

UUIDはASCII lowercase hexadecimalによる`xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`だけを受理する。variantはRFC 4122、versionは4とする。uppercase、brace、URN、hyphenなし、leading/trailing whitespace、non-v4 UUIDを拒否する。parse可能でも入力文字列が`str(parsed_uuid)`と一致しなければ拒否する。case変換、trim、hyphen追加等で補正しない。

### 3.2 RFC3339 timestamp

`created_at`はASCII decimal digit、`T` separator、必須timezone `Z`または`±HH:MM`、省略または1〜6桁の小数秒、実在する暦日時、second `00`〜`59`を要求する。

naive datetime、offset秒、leap second、space separator、7桁以上の小数秒、Unicode decimal digit、leading/trailing whitespaceを拒否する。入力値を補正してから受理しない。

serialization時はlogical instantをUTCへ正規化し`Z`で表記する。microsecondが0なら小数部を出力せず、0でなければ6桁を出力する。

## 4. JSON parse and schema contract

### 4.1 Input encoding and JSON grammar

- input typeは`bytes`
- encodingはstrict UTF-8、UTF-8 BOMは拒否
- root前後のRFC 8259 JSON whitespace（space、tab、CR、LF）は許可
- 単一root後のnon-whitespace trailing dataは拒否
- invalid UTF-8、malformed/truncated JSONは`MALFORMED_JSON`
- JSON標準外の`NaN`、`Infinity`、`-Infinity`は`MALFORMED_JSON`
- JSON escapeはdecodingの一部とし、decoded文字列へ同じdomain ruleを適用
- valid UTF-8 UnicodeはJSON syntaxとして許可するが、field名と値はclosed schema/domain ruleに従う

### 4.2 Object schema

- rootはobjectだけを許可
- §3の5 fieldをすべて必須化
- unknown fieldとduplicate keyを拒否
- duplicate判定はJSON escape解決後のkeyに対して行い、last-value-wins禁止
- `null`を含むfieldごとのwrong JSON typeを拒否
- string/number/boolean間のcoercion禁止
- JSON booleanをintegerとして扱わない
- default補完、修正、trim、case変換、timezone補完、UUID生成、unknown field破棄を行わない

### 4.3 Validation phases and deterministic error ordering

```text
bytes / duplicate detection / JSON parse
  -> root validation
  -> field-presence and unknown-field validation
  -> field-type validation
  -> domain validation
  -> RuntimeIdentity
```

1. duplicate key、malformed JSON、non-object rootはterminalであり、後続phaseを実行しない。
2. 最初に検出したduplicate keyだけを`DUPLICATE_FIELD`として返す。`field_name`はdecoded keyとする。
3. missing fieldはcanonical field orderで全件収集し、その後unknown fieldをinput encounter orderで全件収集する。1件以上あればtype/domain phaseへ進まない。
4. type errorはcanonical field orderで全件収集する。1件以上あればdomain phaseへ進まない。
5. domain errorはcanonical field orderで全件収集する。

canonical field orderは`schema_version`、`state_id`、`data_root_id`、`environment`、`created_at`とする。同一inputに対するerror tupleの内容と順序は決定論的でなければならない。

## 5. Contract types and error model

Production moduleは`src/argus/runtime/runtime_identity.py`とする。`Environment`だけを`environment.py`から使用し、Marker validation型を共有しない。

```python
@dataclass(frozen=True)
class RuntimeIdentity:
    schema_version: int
    state_id: UUID
    data_root_id: UUID
    environment: Environment
    created_at: datetime


class RuntimeIdentityValidationErrorCode(str, Enum):
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
class RuntimeIdentityValidationError:
    code: RuntimeIdentityValidationErrorCode
    field_name: str | None = None


@dataclass(frozen=True)
class RuntimeIdentityValidationFailure:
    errors: tuple[RuntimeIdentityValidationError, ...]
```

`errors`はnon-empty ordered tupleとし、empty constructionは`ValueError`とする。`field_name`はfieldを特定できる場合だけ設定する。`MALFORMED_JSON`と`JSON_ROOT_NOT_OBJECT`は`None`、その他は該当decoded field名とする。

successとfailureはmutually exclusiveである。code setはclosed setであり、承認済みContract changeなしに追加しない。parse/schema/domain failureを通常制御の例外として外へ漏らさない。

`RuntimeIdentity` constructorは`type(schema_version) is int`かつ`1`、両IDがUUID v4、`environment`が`Environment`、`created_at`がtimezone-awareかつ`utcoffset() is not None`というinvariantを検証する。違反は`ValueError`としinvalid instanceを生成しない。

## 6. Public API

```python
def parse_runtime_identity(
    data: bytes,
) -> RuntimeIdentity | RuntimeIdentityValidationFailure:
    ...


def serialize_runtime_identity(
    identity: RuntimeIdentity,
) -> bytes:
    ...
```

`parse_runtime_identity()`は§4に従うpure operationである。filesystem path、Locator、Marker、Expected Binding、filesystem exceptionを扱わず、I/Oや状態変更を行わない。入力bytesを変更しない。

`serialize_runtime_identity()`は§7のcanonical bytesを返すpure operationである。入力を変更しない。入力が`RuntimeIdentity`でなければ`TypeError`、field invariant違反なら`ValueError`を送出し、bytesを返さない。validation failure valueは入力として受理しない。

同じ入力に対する反復呼出しはvalueとbytesについて決定論的でなければならない。

## 7. Deterministic serialization

- UTF-8、BOMなし、LF only
- `ensure_ascii=false`相当。ただしcanonical field/valueはASCII表現
- 2-space indent
- key/value separatorは`: `
- item separatorは`,`直後にLFと次indent、trailing commaなし
- final newline exactly 1つ
- `allow_nan=false`相当
- unknown fieldなし
- key orderは§4.3のcanonical field order
- UUIDはcanonical lowercase hyphenated string
- environmentはuppercase enum value
- `created_at`はUTC `Z`。microsecond 0ならfractionなし、非0なら6桁

canonical exampleのexact bytesは次のとおり。

```text
{
  "schema_version": 1,
  "state_id": "12345678-1234-4234-9234-123456789abc",
  "data_root_id": "87654321-4321-4321-8321-cba987654321",
  "environment": "TEST",
  "created_at": "2026-09-20T00:00:00Z"
}

```

## 8. Module and dependency boundary

```text
environment.py -> runtime_identity.py
```

- `runtime_identity.py`からMarker/Binding/Store/Guard moduleへ依存しない
- Marker type、parser、error enum、failureをaliasまたは共有しない
- helper共通化は本Contractの要件ではなく、public type/error authorityを統合しない
- Data Root側の値からRuntime Identityまたはexpected bindingを生成しない

## 9. Exact Oracle

全Test IDは`RUNTIME-IDENTITY-DOCUMENT-JSON`へtraceし、`EXACT_CONTRACT_ORACLE-v1`を使用する。side effect `none`はprocess外部変更なし、入力変更なしを意味する。

| Test ID | Requirement | Input | Exact expected result | Failure class / code | Required side effect | API |
|---|---|---|---|---|---|---|
| `RI-L0-001` | valid canonical document | canonical 5-field bytes | domain typeへ変換された`RuntimeIdentity` | N/A | none | parse |
| `RI-L0-002` | malformed/encoding/non-standard JSON | invalid UTF-8、BOM、truncated、trailing data、`NaN` / `±Infinity` | exactly one error、`field_name=None` | failure / `MALFORMED_JSON` | none | parse |
| `RI-L0-003` | object root | array/string/number/boolean/null | exactly one error、`field_name=None` | failure / `JSON_ROOT_NOT_OBJECT` | none | parse |
| `RI-L0-004` | required fields | 各required fieldを1件ずつ欠落 | exactly one named error、defaultなし | failure / `MISSING_FIELD` | none | parse |
| `RI-L0-005` | unknown fields | 1件/複数のASCII・Unicode unknown key | 全errorをencounter orderで保持 | failure / `UNKNOWN_FIELD` | none | parse |
| `RI-L0-006` | duplicate keys | 各required keyのduplicate | first duplicateだけ、last-value-wins禁止 | failure / `DUPLICATE_FIELD` + decoded key | none | parse |
| `RI-L0-007` | exact field types | 各fieldへ不正なstring/integer/float/boolean/object/array/null | coercionなし、該当field error | failure / `INVALID_FIELD_TYPE` | none | parse |
| `RI-L0-008` | boolean is not integer | schema version `true` / `false` | exactly one schema error | failure / `INVALID_FIELD_TYPE` | none | parse |
| `RI-L0-009` | schema version | integer `0`, `2`, `-1` | exactly one schema error | failure / `UNSUPPORTED_SCHEMA_VERSION` | none | parse |
| `RI-L0-010` | canonical UUID v4 | valid v4を両IDへ設定 | success、domain UUID v4一致 | N/A | none | parse |
| `RI-L0-011` | invalid state UUID | uppercase/brace/URN/no-hyphen/whitespace/non-v4/invalid | 補正なし、exactly one named error | failure / `INVALID_STATE_ID` | none | parse |
| `RI-L0-012` | invalid data root UUID | RI-L0-011と同じinvalid set | 補正なし、exactly one named error | failure / `INVALID_DATA_ROOT_ID` | none | parse |
| `RI-L0-013` | environment closed set | `TEST`, `PAPER`, `LIVE` | 対応する`Environment`でsuccess | N/A | none | parse |
| `RI-L0-014` | invalid environment | case variation/unknown/empty/whitespace | exactly one named error | failure / `INVALID_ENVIRONMENT` | none | parse |
| `RI-L0-015` | accepted RFC3339 | `Z` / `±HH:MM`、fraction 0/1/6 digits | timezone-aware datetimeでsuccess | N/A | none | parse |
| `RI-L0-016` | rejected RFC3339 | naive/offset seconds/leap second/space/7+ fraction/Unicode digit/invalid calendar/whitespace | exactly one named error | failure / `INVALID_CREATED_AT` | none | parse |
| `RI-L0-017` | schema error ordering | 複数missing + 複数unknown | missing canonical order後unknown encounter order | failure / ordered schema errors | none | parse |
| `RI-L0-018` | type error ordering | 複数field wrong type | canonical order、domain phaseなし | failure / ordered `INVALID_FIELD_TYPE` | none | parse |
| `RI-L0-019` | domain error ordering | type-correctで全5 field domain-invalid | canonical orderで5 error | failure / schema-version, state, data-root, environment, created-at codes | none | parse |
| `RI-L0-020` | structural precedence | duplicate + 他error | first duplicateの1 errorだけ | failure / `DUPLICATE_FIELD` | none | parse |
| `RI-L0-021` | JSON whitespace | root前後にspace/tab/CR/LF | success、field value不変 | N/A | none | parse |
| `RI-L0-022` | no normalization | trim/case/timezone補完を要する値 | field固有error、補正受理なし | failure / field-specific code | none | parse |
| `RI-L0-023` | exact serialization | valid UTC identity、microsecond 0 | §7 exampleとbyte-for-byte一致 | N/A | none | serialize |
| `RI-L0-024` | UTC/fraction normalization | non-UTC、fraction 1/6 digits由来identity | UTC `Z`、fraction 0/6 digits | N/A | none | serialize |
| `RI-L0-025` | canonical round trip | accepted environment/RFC3339 variants | domain value equality、canonical bytes | N/A | none | both |
| `RI-L0-026` | invalid serializer input | wrong object / invariant違反instance | `TypeError` / `ValueError`、bytesなし | programmer misuse / exception | none | serialize |
| `RI-L0-027` | repeated determinism | 同一valid bytes / identityを反復 | parse value equality、bytes exact equality | N/A | none | both |
| `RI-L0-028` | pure/no side effect | valid/invalid代表case | filesystem/network/environment/global state変更なし、入力不変 | N/A | none | both |

Oracle row数は28。parameterized concrete case数はTest designで上記の列挙値を最小重複で展開し、各列挙値を少なくとも1回直接観測する。

## 10. Acceptance Criteria

次の条件はすべて成立している。

- field set、external/domain type、canonical representationがexact
- encoding/JSON/schema/domain ruleがexact
- error type、closed code set、field semantics、non-empty invariantがexact
- multi-error collection、ordering、phase precedenceがexact
- module、type、API signature、return/exception boundaryがexact
- deterministic serialization bytesがexact
- Exact Oracle `RI-L0-001`〜`RI-L0-028`がcomplete
- 未実装でもimport target `argus.runtime.runtime_identity`が一意
- Test側のDesign判断が不要
- 本Capability scopeのTBD / UNSPECIFIED / CONFLICTINGは0件

次工程はCanonical Verification OrderのTest Code作成である。Baseline Freeze、RED、Production implementationはTest CodeとPre-RED Static Analysis完了前に開始しない。

## 11. Deferred outside this capability

physical filename/discovery、filesystem I/O/initialization、Config schema/hash/locator、Secret解決、Expected Binding derivation、Binding API call/failure mapping、Runner lock順序、RuntimeContext/Bootstrap orchestration、Deployment Evidence、PAPER/LIVE provisioning、Migration/Restoreは後続Capabilityの責務であり、本Contractのambiguityではない。

## 12. Development state

- `RUNTIME-IDENTITY-DOCUMENT`: `IN_PROGRESS`
- Production / Test / Frozen Test / Baseline / Run / Evidence: 未変更
- Existing Environment Binding capabilities: `CLOSED`維持
- unresolved ambiguity count: `0`（本Capability scope）
- Frozen Test design readiness: `READY`
- `CV-44`: `PARTIAL`
- `RV-34`: `NOT_RUN`
