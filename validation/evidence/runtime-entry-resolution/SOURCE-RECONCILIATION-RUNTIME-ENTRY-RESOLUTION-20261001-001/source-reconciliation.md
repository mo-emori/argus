# Runtime Entry Resolution canonical design evidence

Evidence ID: `SOURCE-RECONCILIATION-RUNTIME-ENTRY-RESOLUTION-20261001-001`  
Date: `2026-10-01`  
Outcome: `RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY`  
Registry disposition: `IN_PROGRESS`

## Scope and exclusions

Human DA の final Manifest direction を Design Source、派生 View、CLOSED Runtime Identity / Runtime Config contracts、および repository の Python package layout と照合した。Design/specification と canonical evidence だけを更新し、Test Strategy、baseline、tests、Pre-RED、RED、Production、Freeze、commit、push は行っていない。

## Final Human DA decision

1. Artificial `manifest.json` は将来拡張点として保持するが、v0.1 は現在の Runtime Entry Resolution に必要な最小 schema だけを持つ。
2. v0.1 schema は required `schema_version`, `startup.kind`, `startup.entry` だけを定義する。
3. repository に console script、`__main__.py`、launcher script、executable はなく、実在する最小 package boundary は `src/argus/runtime/__init__.py` である。
4. v0.1 target は closed single kind `python_module`、fixed entry `argus.runtime` とする。future launcher/plugin kinds は導入しない。
5. physical validation は import を実行せず Python module specification を解決し、concrete package origin が existing readable regular `__init__.py` であることを確認する。
6. success result は resolved module target、Identity 由来の `ExpectedEnvironmentBinding`、Config snapshot 由来の `DataRootLocator` を持つ。
7. actual import/execution、Environment Binding、Marker、process start、runtime loop readiness は後段責務である。

## Exact normative schema

```json
{
  "schema_version": "0.1",
  "startup": {
    "kind": "python_module",
    "entry": "argus.runtime"
  }
}
```

- required values are exact, case-sensitive ASCII tokens;
- UTF-8 BOM、duplicate members、coercion、trim、normalization、alias、fallback are rejected;
- unknown members are duplicate-checked then ignored and do not affect resolution or result;
- only ignorable optional additions that preserve all existing required meaning may retain schema version `0.1`;
- required shape/meaning changes or a new kind require a new schema version.

## Source reconciliation

| Source | Verified consequence |
|---|---|
| Design Source §4.0 | Ordered responsibilities, no directory-derived environment, subsystem-local failures, later Orchestrator Binding call. |
| Design Source §4.1 | Development/Runtime separation remains; Entry Resolution does not infer identity from placement. |
| Design Source §4.2 | Fixed Manifest is read and unresolved authority fails closed. |
| Design Source §52.3 | `manifest.json` is canonical filename; broader Runtime layout does not require broader v0.1 fields. |
| Runtime Identity Contract | validated immutable `state_id`, `data_root_id`, `environment` supply expected binding. |
| Runtime Config Contract | successful immutable snapshot supplies lexical absolute `data_root_path`. |
| `pyproject.toml` and `src/argus/runtime/__init__.py` | Python 3.11+ src layout and real `argus.runtime` package exist; no executable/script/console entry is established. |

No conflict with Design Source was found. The Manifest describes deployment/startup selection and does not place code path in Runtime Identity or duplicate mutable Data Root locator into Identity.

## Result and failure boundary

`RuntimeEntryResolutionResult` contains only:

- `ResolvedPythonModuleTarget(kind="python_module", module_name="argus.runtime", origin_path=<validated absolute __init__.py>)`;
- `ExpectedEnvironmentBinding(identity.state_id, identity.data_root_id, identity.environment)`;
- `DataRootLocator(config_snapshot.data_root_path)`.

Capability-local failure reasons are limited to manifest path/not-found/read, malformed JSON, duplicate field, schema invalid, unsupported schema version, startup target not found, and startup target invalid. Resolution short-circuits on the first stage failure and does not expose raw OS exception text as equality semantics.

## Residual disposition and readiness

`RER-FINAL-DETAIL-001` is resolved. All earlier unresolved DA markers were either resolved by the final Human DA decision or confirmed out of scope. No genuine blocker remains.

The Contract now supplies deterministic oracles for JSON/schema/version/compatibility behavior, fixed target selection, physical package validation, typed mapping, failure locality, ordering, and non-responsibilities. It is therefore ready for a separate Test Strategy job.

Registry remains `IN_PROGRESS`; readiness does not CLOSE the Capability and does not authorize Test Strategy or implementation in this job.

Final: `RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY`
