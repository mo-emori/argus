# ARGUS Runtime Entry Resolution Contract v0.1

**Status:** `RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY`  
**Capability:** `RUNTIME-ENTRY-RESOLUTION`  
**Registry status:** `IN_PROGRESS`  
**Scope:** Design/specification only. Test Strategy、baseline、tests、Pre-RED、RED、Production、Freeze は未着手であり、本書では作成しない。

## 1. Authority and final Human Design Authority decision

Design Source を正本とし、派生文書は View としてのみ参照する。本 Contract は 2026-10-01 の Human Design Authority（Human DA）決定を規範化する。

1. 起動責務順は `Runtime Identity -> Runtime Config -> Runtime Entry Resolution -> Runtime Bootstrap Orchestrator` とする。
2. Artificial `manifest.json` は v0.1 でも保持し、将来の Web / GDE / runtime 拡張点とする。ただし v0.1 は現在の起動解決に必要な最小 schema だけを持つ。
3. Entry Resolution は Artificial Manifest の read、duplicate-aware JSON parse、schema/version validation、entry resolution、physical validation を所有する。Result Manifest は別物であり対象外である。
4. v0.1 の起動対象は repository に実在する Python package module `argus.runtime` だけである。実在しない executable、script、callable、plugin、command、launcher model を先取りしない。
5. Entry Resolution は target を import、execute、probe、または process start しない。Environment Binding の実行も後段 Orchestrator の責務である。
6. success は unchecked string ではなく、物理検証済み target と CLOSED upstream interface から構成した Binding inputs を持つ typed immutable result である。
7. Registry は `IN_PROGRESS` を維持する。本 Contract の確定は Capability の CLOSE、Test Strategy 作成、実装許可を意味しない。

### 1.1 Source and repository basis

| Authority / fact | Contract consequence |
|---|---|
| Design Source §4.0 | 四つの責務順、directory から environment を推論しないこと、subsystem-local typed failure、Orchestrator による Binding 呼出しを維持する。 |
| Design Source §4.1 | Development / Runtime の物理分離を維持する。Entry Resolution は配置から identity/environment を推論しない。 |
| Design Source §4.2 | 固定 Manifest を読み、権威を確定できなければ fail closed とする。 |
| Design Source §52.3 | canonical filename は `manifest.json`、Runtime layout には `app/` がある。広い Bootstrap metadata は本 Contract へ取り込まない。 |
| CLOSED Runtime Identity / Runtime Config contracts | Binding inputs は Manifest field に重複させず、validated identity と successful config snapshot から構成する。 |
| `pyproject.toml`, `src/argus/runtime/__init__.py` | project は Python 3.11+ の `src` package layout であり、現時点に console script、`__main__.py`、launcher script、executable はない。最小の実在 target は package module `argus.runtime` である。 |

## 2. Typed input and ownership boundary

```text
resolve_runtime_entry(
  identity: RuntimeIdentity,
  config_snapshot: RuntimeConfigSnapshot,
  artificial_manifest_path: AbsolutePathToManifestJson,
) -> RuntimeEntryResolutionResult | RuntimeEntryResolutionFailure
```

- `identity` は CLOSED Runtime Identity Contract により validation 済みの immutable value である。Entry Resolution は再読込・再parse・再validationしない。
- `config_snapshot` は CLOSED Runtime Config Contract の `CONFIGURED` immutable L1 snapshot である。Entry Resolution は Config を再読込・再解決しない。
- caller は一つの absolute `manifest.json` path を渡す。CWD、executable location、repository、Runtime/Data Root tree、environment variable、directory name、nearest-file search から Manifest を発見しない。
- `config_path` の供給は本 Contract の scope 外である。

## 3. Normative Manifest v0.1 schema

### 3.1 Canonical JSON shape

```json
{
  "schema_version": "0.1",
  "startup": {
    "kind": "python_module",
    "entry": "argus.runtime"
  }
}
```

| JSON path | Required | Type | v0.1 accepted value |
|---|---:|---|---|
| `schema_version` | yes | string | exactly `"0.1"` |
| `startup` | yes | object | one object |
| `startup.kind` | yes | string | exactly `"python_module"` |
| `startup.entry` | yes | string | exactly `"argus.runtime"` |

`startup.kind` は file path や executable と混同せず type-specific validation を決定するための closed discriminator である。v0.1 で許可する kind は一つだけであり、複数 kind が存在するように扱ってはならない。

Manifest に runtime root、absolute path、Binding identity、Data Root、Web/GDE capability、deployment metadata、secret reference、command、arguments、callable name、fallback、複数 candidate を置かない。これらは v0.1 required meaning ではない。

### 3.2 JSON and duplicate rules

- input は UTF-8 JSON text とし、先頭 UTF-8 BOM は受理しない。
- JSON root は object でなければならない。
- object の同一階層に同名 member が二回以上現れた場合、値が同一でも `DUPLICATE_FIELD` とする。root、`startup`、未知 object のすべてへ適用する。
- JSON number coercion、string conversion、default insertion、case folding、Unicode normalization、whitespace trimmingを行わない。

### 3.3 Unknown-field and compatibility policy

- required member とその meaning は上表で closed である。
- duplicate check 後、root または `startup` にある未知 member は v0.1 reader が無視し、result へ保持・転送しない。未知 member の内容は startup selection、resolution、Binding inputs、failure precedence に影響してはならない。
- この ignore rule により、既存 required member の意味・型・値を変えず、既存 v0.1 document が引き続き有効で、旧 reader が安全に無視できる optional member の追加だけは `schema_version = "0.1"` のまま許可できる。
- required member の追加、削除、rename、型変更、accepted-value meaning の変更、`startup` shape の変更、未知 field が動作を変える拡張、または新しい `startup.kind` の追加には新しい schema version が必要である。
- v0.1 Contract は optional member を一つも定義しない。ignore rule は将来 section を今ここで設計するものではない。

### 3.4 Version and normalization rules

- `schema_version` は semantic-version range ではなく exact protocol token `"0.1"` である。他の string、number、null、missing は受理しない。
- `startup.kind` と `startup.entry` は exact ASCII token として比較する。case folding、Unicode normalization、trim、dot/slash conversion、relative-name completion、alias、fallback を適用しない。
- `startup.entry` は filesystem path ではない。`argus/runtime`、`argus.runtime:main`、`.argus.runtime`、`argus.runtime.__main__` は無効である。

## 4. Deterministic resolution and physical validation

一回の invocation は次の順で short-circuit する。

1. `artificial_manifest_path` が absolute で、basename が case-sensitive に exactly `manifest.json` であることを lexical に確認する。
2. path が存在する regular file であることを確認し、bytes を一回の load invocation として読む。
3. UTF-8 decode と duplicate-aware JSON parse を行う。
4. §3 の root、required member、type、version、closed value を validation する。
5. current Python runtime の side-effect-free finder interface で、module code や parent package code を importせず `argus.runtime` の module specification を解決する。finder/search path は caller が起動用 Python environment として確定済みのものを使用し、Entry Resolution が CWD や repository path を追加しない。
6. specification が package を表し、単一の concrete origin を持つことを確認する。namespace package、built-in、frozen module、origin 不明、複数 location だけの結果は拒否する。
7. origin を absolute normalized filesystem path とし、basename が exactly `__init__.py`、path が存在する readable regular file であることを確認する。
8. `ResolvedPythonModuleTarget` と Binding inputs を immutable result として構成する。

### 4.1 Valid resolved target

v0.1 で valid target となる必要十分条件は次のとおりである。

- Manifest の `startup.kind` / `startup.entry` が exact allowed values である。
- Python import resolution が `argus.runtime` の concrete regular package を一意に解決する。
- resolved origin が existing readable regular `__init__.py` である。readable とは binary read として open/close が成功することであり、内容の import、compile、実行は含まない。

physical validation は source bytes の compile、module import、callable/`main` 探索、`python -m` 可否、process execution、exit code、runtime root containment、symlink/junction/reparse policy、code hash、signature、deployment version を検証しない。それらを成功条件に追加するには、所有 Capability と新しい Contract decision が必要である。

この境界は「現に解決可能な package target」と「後段でそれをどう起動・統合するか」を分離する。Entry Resolution success は process start success または normal Runtime Loop readiness を意味しない。

## 5. Typed success result

```text
ResolvedPythonModuleTarget
  kind: Literal["python_module"]
  module_name: Literal["argus.runtime"]
  origin_path: AbsoluteNormalizedPathToExistingReadableRegularInitPy

RuntimeEntryResolutionResult
  startup_target: ResolvedPythonModuleTarget
  expected_binding: ExpectedEnvironmentBinding
  data_root_locator: DataRootLocator
```

Binding inputs は Manifest fields ではなく CLOSED upstream values からだけ構成する。

```text
expected_binding = ExpectedEnvironmentBinding(
  state_id=identity.state_id,
  data_root_id=identity.data_root_id,
  environment=identity.environment,
)

data_root_locator = DataRootLocator(path=config_snapshot.data_root_path)
```

Entry Resolution は `data_root_path` を再canonicalizeせず、existence、Marker、identity、read/write availability を検証しない。Manifest path/hash、Config/Identity provenance、`config_path`、timestamp、host、run ID、deployment metadata は v0.1 result field ではない。

Orchestrator はこの result を消費して後続順序と Environment Binding API 呼出しを所有する。Manifest の再読込、target の再選択、別 target への fallback、Entry Resolution physical validation の再実装を行わない。

## 6. Capability-local failure model

```text
RuntimeEntryResolutionFailureCode
  MANIFEST_PATH_INVALID
  MANIFEST_NOT_FOUND
  MANIFEST_READ_ERROR
  MALFORMED_JSON
  DUPLICATE_FIELD
  MANIFEST_SCHEMA_INVALID
  UNSUPPORTED_SCHEMA_VERSION
  STARTUP_TARGET_NOT_FOUND
  STARTUP_TARGET_INVALID

RuntimeEntryResolutionDiagnostic
  code: RuntimeEntryResolutionFailureCode
  field_name: string | None

RuntimeEntryResolutionFailure
  diagnostic: RuntimeEntryResolutionDiagnostic
```

| Condition | Code | `field_name` |
|---|---|---|
| non-absolute path、basename mismatch、path operation が lexical check を完了不能 | `MANIFEST_PATH_INVALID` | none |
| manifest path が存在しない | `MANIFEST_NOT_FOUND` | none |
| non-regular file、permission/I/O failure、UTF-8 decode failure | `MANIFEST_READ_ERROR` | none |
| JSON syntax/decoder failure | `MALFORMED_JSON` | none |
| duplicate JSON member | `DUPLICATE_FIELD` | duplicate member の decoded name |
| root/required/type/kind/entry shape/value violation。ただし version mismatch を除く | `MANIFEST_SCHEMA_INVALID` | 特定可能なら canonical field path、otherwise none |
| `schema_version` が string だが exact `"0.1"` でない | `UNSUPPORTED_SCHEMA_VERSION` | `schema_version` |
| import specification が見つからない、または origin path が存在しない | `STARTUP_TARGET_NOT_FOUND` | `startup.entry` |
| import resolution error、ambiguous/non-concrete spec、wrong physical type/name、unreadable origin、physical inspection failure | `STARTUP_TARGET_INVALID` | `startup.entry` |

最初に失敗した stage の一つの diagnostic を返し、後続 stage は実行しない。同一 schema stage で複数違反を検出した場合は canonical field order `schema_version`, `startup`, `startup.kind`, `startup.entry` の最初を返す。OS message、localized text、stack trace、raw exception、path text は public equality semantics に含めない。

Identity failure は Identity、Config failure は Config、Environment Binding failure は Binding に残す。Entry Resolution の failure を全 subsystem 共通 enum へ統合しない。Orchestrator が上位 startup outcome へ写像する。

## 7. Side-effect and non-responsibility boundary

Entry Resolution は Manifest/target を作成・修復・変更せず、network、clock、process start、module import、Environment Binding call、Marker read、state transition、persistent write、lock、recovery、secret resolution を行わない。

次も行わない。

- Runtime Identity / Runtime Config の再読込・再parse・再validation
- path、drive letter、directory layout、module location から environment/identity を推論
- alternate Manifest/target、relative anchoring、CWD/repository fallback
- Web/GDE/runtime capabilities、deployment metadata、support metadata の先行設計
- Result Manifest、Registry closure、evidence closure の生成

## 8. Resolved DA markers and testability

| Prior marker | Final disposition |
|---|---|
| Manifest owner / locator-vs-bytes | `RESOLVED_BY_HUMAN_DA` — Entry Resolution receives the path and owns read/parse/validation. |
| no physical check vs existence-only | `RESOLVED_BY_HUMAN_DA` — concrete Python package origin is mandatory. |
| single path vs runtime-root/entry pair | `RESOLVED_BY_HUMAN_DA` — v0.1 entry is a fixed Python module name; no root/entry composite is introduced. |
| generic readability/executability bundle | `RESOLVED_BY_HUMAN_DA` — package-origin checks are exact; execution checks remain later. |
| supported kind and discriminator | `RESOLVED_BY_HUMAN_DA` — one closed `python_module` kind. |
| schema/version/unknown/duplicate policy | `RESOLVED_BY_HUMAN_DA` — §§3 and 6 are normative. |
| Config `config_path` supplier | `OUT_OF_SCOPE` — upstream/launch concern; not an Entry Resolution blocker. |
| `RER-FINAL-DETAIL-001` | `RESOLVED_BY_HUMAN_DA` — exact schema, target kind/value, physical oracle, result and failures are fixed by this Contract. |

The Contract is internally testable without production implementation:

- bytes fixtures can cover JSON/duplicate/schema/version/unknown-field behavior;
- injected or isolated import resolution can cover missing, non-concrete, wrong-type, unreadable and valid package origins without importing/executing the target;
- typed result construction can verify exact Identity/Config-to-Binding mapping;
- operation ordering and fail-closed short-circuit can be observed without Environment Binding or process execution.

No unresolved DA marker remains for Runtime Entry Resolution v0.1. A later decision to add another kind, launcher semantics, runtime-root containment, or deployment metadata is a new version/change request, not a stale blocker in this Contract.

## 9. Disposition

The minimal Manifest v0.1 schema, physical target oracle, typed result, compatibility policy, and subsystem-local failure boundary are normative and ready to be used as input to a separate Test Strategy job.

`RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY`

Registry remains `IN_PROGRESS`. No Test Strategy, baseline, tests, Pre-RED, RED, Production, Freeze, commit, or push is authorized or performed by this Contract finalization.
