# ARGUS Runtime Bootstrap Orchestrator Contract v0.1

**Document Type:** Draft Contract  
**Version:** `0.1`  
**Status:** `DRAFT / IN_PROGRESS`  
**Capability:** `RUNTIME-BOOTSTRAP-ORCHESTRATOR`  
**Human Design Authority:** H1 / H2 approved on `2026-10-03`  
**Implementation State:** Contract only; Production, tests, Freeze, RED/GREEN and process entry point are not authorized by this document
**Correction Basis:** `ARGUS-BOOTSTRAP-CONTRACT-V01-REVIEW-RETRY-20261003-001` (`CHANGES_REQUIRED`); Human DA H1/H2 unchanged

## 1. Purpose and v0.1 scope

Runtime Bootstrap Orchestrator v0.1は、通常Runtime Loopより前のfoundation startupを、既存のCLOSED subsystem境界を再実装せずに順序付けるread-only orchestration Contractである。

v0.1のmandatory sequenceは次の4段階だけである。

1. Runtime Identity
2. Runtime Config
3. Runtime Entry Resolution
4. Environment Binding

全4段階が成功した場合だけfoundation startup successを返す。このsuccessは、target processの起動、通常Loop readiness、`RUNNING`への遷移、PAPER/LIVE運用開始承認、またはpersistent write authorityを意味しない。

## 2. Authority and traceability

設計判断はDesign Sourceを優先し、CLOSED Contractは各subsystemの詳細境界として参照する。P-0021および2件のexternal analysisは判断履歴とreduction evidenceであり、Design Sourceを上書きしない。

| Artifact | Role | SHA-256 |
|---|---|---|
| `docs/source/argus_design_source_v0.1.md` | canonical Design Source、§4.0 / §4.1 / §4.2 / §4.7 / §22 / §52.3 | `feff970e4dc59c599c7fc5e48c5f77b87e7806aa156e87f8dd26bdae36609681` |
| `docs/contracts/argus_runtime_foundation_bootstrap_contract_v0.1.md` | P-0021 draft / gap analysis | `4b4a86e069108983f7d434772b1fe668a3633e926846a552eddde9aa875e4ab6` |
| `docs/contracts/argus_runtime_identity_document_contract_v0.1.md` | CLOSED Runtime Identity behavior | `51439a20f16440dfcc3e98ca7bfe4e862df89a85c70036474bfcbc4c7e745e72` |
| `docs/contracts/argus_runtime_config_mechanism_contract_v0.1.md` | CLOSED Runtime Config behavior | `22410d63e662cc5b52019031fe3de0e9d88e6ee6c54078e8584ea9f9284d7b97` |
| `docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md` | CLOSED Runtime Entry Resolution behavior | `a058a08fa6ebe013462141481ff8ec1965e49c49894a5da357e186ae51bd5e08` |
| `docs/contracts/argus_environment_binding_contract_v0.1.md` | CLOSED Environment Binding behavior | `90171ac4a5a0c3940cd4198515f89655b674e7b3aa5a5b7dcb293f698317fa8a` |
| `ARGUS-BOOTSTRAP-DA-REDUCTION-20261003-001/review-manifest.json` | adopted DA reduction evidence | `14a508e22c8d8799b71b1d7495d5d973a597fed996bb5287d5cead3f11947e1c` |
| `ARGUS-BOOTSTRAP-DA-SECOND-OPINION-20261003-001/review-manifest.json` | adopted independent second-opinion evidence | `c3cdb138a48f41abdd7e0fe16fa42ac95c58c6534d139f361cbdbbb76ceab845` |

The verified repository HEAD for this draft is `38cf7609d3175c78b74ab5e20ec271559dcc1eb6`.

### 2.1 Final Human Design Authority decisions

**H1 — Runtime Identity file/read transport**

- standard Runtime Identity Document filename is exactly `runtime_identity.json`;
- Bootstrap transport failures are exactly `RUNTIME_IDENTITY_NOT_FOUND` and `RUNTIME_IDENTITY_NOT_READABLE`;
- Identity content and semantic failures preserve the existing typed Runtime Identity failures unchanged and are never collapsed into a generic identity/bootstrap failure.

**H2 — `CONFIG_REQUIRED`**

- Bootstrap-specific `CONFIG_REQUIRED` label/outcome is not introduced;
- existing upstream typed Config states and diagnostics pass through unchanged;
- no generic `BOOTSTRAP_FAILED` translation layer is introduced.

These decisions are also recorded in ADR-009. They do not reopen or alter a CLOSED upstream Contract.

## 3. Authority and non-authority boundary

### 3.1 Bootstrap owns

- receipt of the three explicit launch input paths;
- Runtime Identity transport read and its two transport failure codes;
- exact stage ordering and first-failure short-circuit;
- passing successful typed outputs to the next stage without duplicating validation;
- one environment-agnostic Environment Binding invocation;
- the minimal foundation success wrapper;
- returning typed non-success values without generic translation.

### 3.2 Bootstrap does not own in v0.1

- Runtime Identity JSON/schema/domain validation or serialization;
- Runtime Config path/schema/domain validation, snapshot creation or Data Root resolution;
- Artificial Manifest parsing, target selection or physical entry validation;
- Marker read/validation, Binding comparison or Binding failure classification;
- environment inference from any directory, path, drive, marker placement or runtime tree;
- secret resolution;
- target import, execution, process start or Runtime Loop transition;
- Result Manifest generation or interaction;
- startup-state, Incident, Alert, log, identity, marker or other persistent writes;
- retry, fallback, repair, migration, auto-creation or alternate-file discovery.

Exit/loop/degraded-mode policy belongs to the broader Orchestrator capability but is deferred beyond v0.1. It is not declared permanently outside Bootstrap authority.

## 4. Inputs and caller responsibility

The logical v0.1 input is:

```text
RuntimeBootstrapInputs
  identity_path: path value that is absolute under the execution platform semantics
                 and ends exactly in runtime_identity.json
  config_path: absolute path supplied to Runtime Config
  artificial_manifest_path: absolute path supplied to Runtime Entry Resolution
```

The caller is responsible for supplying all three paths explicitly and as absolute paths. `identity_path` must be a path value accepted by the execution platform's path interface; a non-path value is caller programmer misuse and raises `TypeError`, not a returned runtime outcome. The caller must establish any required Python import environment before the call. Bootstrap does not derive any path from a runtime root, change CWD, change `sys.path`, inspect environment variables to discover files, or search parent/child/nearest directories.

Caller responsibility does not imply that the caller determines filesystem success. Bootstrap and the owning subsystems retain the following validation/read responsibilities:

- Bootstrap lexically verifies that `identity_path` is absolute and its basename is case-sensitive exactly `runtime_identity.json`, then reads that exact path.
- Runtime Config exclusively applies its CLOSED path contract to `config_path`, including exactly `config.json`; Bootstrap passes the caller value unchanged and performs no pre-check.
- Runtime Entry Resolution exclusively applies its CLOSED path contract to `artificial_manifest_path`, including exactly `manifest.json`; Bootstrap passes the caller value unchanged and performs no pre-check.

For `identity_path`, the filename convention constrains the explicitly supplied path; it does not create a discovery rule. Bootstrap never substitutes an alternate filename or searches for `runtime_identity.json`.

For `identity_path`, "absolute" is determined lexically by the execution platform's path semantics. On Windows, drive-relative forms such as `C:x\runtime_identity.json` and rooted-without-drive forms such as `\x\runtime_identity.json` are not absolute for this Contract. A path value that is non-absolute, has a different basename, or whose lexical path operation cannot complete is `RUNTIME_IDENTITY_NOT_READABLE`. Absence reported while reading the exact valid path is `RUNTIME_IDENTITY_NOT_FOUND`. Any other open/read transport failure is `RUNTIME_IDENTITY_NOT_READABLE`. Path text, OS/localized message and raw exception detail are not part of the returned failure's equality semantics.

## 5. Ordered stages and contracts

Each stage is terminal on failure. A later stage must not be invoked after an earlier failure.

### 5.1 Stage 1 — Runtime Identity

**Preconditions**

- caller supplied `identity_path`;
- no earlier stage exists;
- Bootstrap has not performed a persistent write.

**Operation**

1. Apply only the lexical absolute-path and exact-basename rule in §4.
2. Read the exact file once as raw bytes; do not decode in Bootstrap.
3. On successful read, call the CLOSED Runtime Identity parse/validation operation once with those bytes.

**Postconditions**

- success: one validated immutable Runtime Identity value is available to Stage 3;
- exact-path absence: return `RUNTIME_IDENTITY_NOT_FOUND`;
- invalid path form or any non-absence read failure: return `RUNTIME_IDENTITY_NOT_READABLE`;
- content/schema/domain failure: return the existing `RuntimeIdentityValidationFailure` unchanged;
- no Config, Manifest, Marker or Data Root read has occurred.

Invalid UTF-8, BOM, malformed JSON and semantic defects are Identity content failures owned by the CLOSED Identity subsystem. They are not transport failures and Bootstrap must not decode, reclassify, aggregate or revalidate them.

### 5.2 Stage 2 — Runtime Config

**Preconditions**

- Stage 1 succeeded;
- caller supplied `config_path`;
- no persistent write has occurred.

**Operation**

- invoke the CLOSED Runtime Config L1 operation exactly once with `config_path` unchanged;
- do not pre-validate, normalize independently, read or re-parse the Config in Bootstrap.

**Postconditions**

- `CONFIGURED`: one immutable `RuntimeConfigSnapshot` is available to Stage 3;
- `UNCONFIGURED`, `INVALID` or `ERROR`: return the complete upstream typed `RuntimeConfigResult`, including diagnostics, unchanged;
- a programmer error defined by the CLOSED Config Contract is raised by that operation and propagates as the same exception; Bootstrap neither catches nor wraps it, and it is not a Bootstrap return value;
- no `CONFIG_REQUIRED` and no `BOOTSTRAP_FAILED` label is created;
- on either a returned Config non-success or a raised Config programmer error, Manifest and Marker have not been read and Stages 3 and 4 are not invoked.

### 5.3 Stage 3 — Runtime Entry Resolution

**Preconditions**

- Stages 1 and 2 succeeded;
- validated Runtime Identity and `CONFIGURED` snapshot are available;
- caller supplied `artificial_manifest_path`;
- no persistent write has occurred.

**Operation**

- invoke the CLOSED Runtime Entry Resolution operation exactly once with the validated Identity, Config snapshot and unchanged Artificial Manifest path;
- do not re-read or revalidate Identity/Config;
- do not re-read the Manifest, reselect a target, import the target or create fallback candidates.

**Postconditions**

- success: `startup_target`, `expected_binding` and `data_root_locator` are available;
- failure: return `RuntimeEntryResolutionFailure` unchanged;
- Environment Binding has not yet been invoked;
- target import/execution/process start has not occurred.

### 5.4 Stage 4 — Environment Binding

**Preconditions**

- Stages 1–3 succeeded;
- `expected_binding` and `data_root_locator` came from the successful Entry Resolution result;
- no persistent write has occurred.

**Operation**

- invoke the same CLOSED environment-agnostic `load_and_verify_environment_binding(data_root_locator, expected_binding)` API exactly once for TEST, PAPER and LIVE;
- pass both values unchanged;
- do not branch to a TEST-only business path;
- do not separately load, parse or compare the Marker;
- do not create, repair or replace the Marker.

Bootstrap does not call the CLOSED `verify_test_environment_startup()` guard. That API is a TEST-specific guard, while this operation must use one environment-agnostic path for TEST, PAPER and LIVE; introducing a TEST-only Bootstrap business path would violate Test Strategy §2.4. No environment-specific Bootstrap branch is permitted.

**Postconditions**

- success: receive the exact `VerifiedEnvironmentBinding` produced by the CLOSED API;
- failure: return the complete `BindingFailure` unchanged, preserving all failure classes, codes and locator;
- `DATA_STORAGE_UNAVAILABLE` is non-success and never produces foundation success;
- no retry, fallback, alternate Data Root or degraded-mode transition is performed.

## 6. Success type and semantics

The minimal immutable success value is logically:

```text
RuntimeBootstrapSuccess
  startup_target: ResolvedPythonModuleTarget
  binding: VerifiedEnvironmentBinding
```

Both fields are the exact values produced by the successful upstream stages. The success payload does not include Runtime Identity, Runtime Config snapshot, the full Entry Resolution result, host/run metadata or duplicate snapshots.

Success means only that, for this invocation, the foundation sequence completed and the Environment Binding was verified at Stage 4. It does not authorize target launch, normal-loop entry, PAPER/LIVE operation, or any persistent write.

## 7. Failure model, precedence and short-circuit

The Bootstrap-owned transport types are logically:

```text
RuntimeIdentityTransportFailureCode
  RUNTIME_IDENTITY_NOT_FOUND
  RUNTIME_IDENTITY_NOT_READABLE

RuntimeIdentityTransportFailure
  code: RuntimeIdentityTransportFailureCode
```

Both are closed and immutable. Failure equality is determined only by `code`; path text, OS/localized message, stack trace and raw exception detail are excluded. This two-member Identity transport code set is not a generic Bootstrap failure enum.

The complete observable v0.1 operation algebra is:

```text
run_runtime_bootstrap(inputs) ->
    RuntimeBootstrapSuccess
  | RuntimeIdentityTransportFailure
  | RuntimeIdentityValidationFailure
  | RuntimeConfigResult          # only UNCONFIGURED, INVALID or ERROR
  | RuntimeEntryResolutionFailure
  | BindingFailure

raises:
  TypeError                      # non-path identity_path caller misuse
  upstream Config programmer error unchanged
                                  # including the CLOSED L1 path-contract ValueError
```

This is a logical Contract signature, not a prescription of Python module, function, class or source-file shape. A `CONFIGURED` `RuntimeConfigResult` is an intermediate success and is never a final Bootstrap return. Upstream success values from Identity, Config and Entry Resolution are likewise intermediate; only `RuntimeBootstrapSuccess` is operation success.

Failure precedence is operational and derives only from stage order:

1. Identity transport or typed Identity content failure;
2. typed Config non-success, or propagation of an upstream programmer-error raise;
3. typed Entry Resolution failure;
4. typed Binding failure.

The first observed returned runtime failure is returned immediately. A programmer error is raised immediately. In either case Bootstrap does not execute later stages to collect more failures and defines no cross-subsystem semantic priority.

| Stage | Non-success returned by Bootstrap | Translation |
|---|---|---|
| Identity transport | `RUNTIME_IDENTITY_NOT_FOUND` or `RUNTIME_IDENTITY_NOT_READABLE` | none |
| Identity content/semantic | existing `RuntimeIdentityValidationFailure` | unchanged |
| Config | existing non-`CONFIGURED` `RuntimeConfigResult` and diagnostics | unchanged; no `CONFIG_REQUIRED` |
| Config programmer misuse | no return value; same upstream exception is raised | uncaught and unwrapped |
| Entry Resolution | existing `RuntimeEntryResolutionFailure` | unchanged |
| Environment Binding | existing `BindingFailure` | unchanged |

There is no generic Bootstrap failure enum/outcome, no `BOOTSTRAP_FAILED`, and no loss of subsystem diagnostic detail. A caller may identify the failing stage from the returned typed value; this Contract does not require an additional persistent record or generic wrapper.

### 7.1 Bootstrap v0.1 startup outcome

At the Bootstrap v0.1 boundary, **startup outcome** means the observable result of the logical operation in the algebra above: either the sole success type `RuntimeBootstrapSuccess`, or the first subsystem-owned/Bootstrap-transport typed runtime failure returned unchanged. The required mapping in Design Source line 388, Runtime Config §8 and Runtime Entry Resolution §6 is therefore an identity mapping into this operation result: subsystem failure identity, diagnostic ordering and meaning are preserved, with no generic relabelling layer.

Raised programmer errors are not startup outcomes and are not converted into returned runtime failures. `DATA_STORAGE_UNAVAILABLE` remains a `BindingFailure` non-success startup outcome; it never becomes `RuntimeBootstrapSuccess`. Mapping a returned failure onward into `RECOVERY_REQUIRED`, Incident/Alert persistence, exit code, retry, normal-loop or degraded-mode process action is broader Orchestrator policy deferred by §11, not a license to relabel the v0.1 result.

## 8. Observable side-effect boundary

Future tests must be able to observe the following behavior without depending on Python module/file/class shape:

- successful-stage calls occur strictly in §5 order and at most once each;
- after a failure, no later-stage read or call occurs;
- observable reads are limited to the explicit Identity file, the Config resources owned by Runtime Config, the Artificial Manifest/module metadata owned by Entry Resolution, and the Data Root Marker owned by Environment Binding;
- Identity raw bytes are read once and handed to Identity validation without Bootstrap decoding;
- the Config and Manifest path values are passed unchanged;
- Entry Resolution's locator and expected binding are passed unchanged to the environment-agnostic Binding API;
- no filesystem creation, modification, deletion or persistent append occurs;
- no network call, secret-store lookup, target import/execution, child-process start, retry, sleep/backoff, alternate-path search, CWD mutation or `sys.path` mutation occurs;
- inputs and successful upstream immutable values are not mutated.

In-memory construction of typed input, failure and success values is not a persistent side effect. Diagnostic logging policy is deferred; v0.1 does not require or authorize a persistent log write.

## 9. Binding evidence and write-authority boundary

`VerifiedEnvironmentBinding` is evidence of the successful Stage 4 verification. Its presence in `RuntimeBootstrapSuccess` is not a capability token for future writes.

A write-capable boundary must follow the CLOSED Environment Binding Contract and perform fresh binding verification for that boundary. It must not accept Bootstrap success, Python object identity, or the startup `VerifiedEnvironmentBinding` as sufficient write authority. Bootstrap does not create `StartupAuthorization`, `WriteAuthorization`, writer-instance identity or any equivalent authority object.

## 10. Idempotency and re-entry

v0.1 guarantees no persistent Bootstrap writes and no rollback obligation. It does not guarantee that repeated invocations produce equal results when filesystem contents, accessibility, import metadata or Marker state change between invocations.

Exact concurrency, simultaneous invocation, caching, memoization, re-entry coordination, lock ownership and time-of-check/time-of-use policy are deferred. No stronger idempotency or re-entry semantics are invented by this Contract.

## 11. Deferred beyond v0.1

The following remain open for later authoritative contracts or a later Orchestrator version:

- `SYSTEM.md` read and broader Design Source §4.2 startup sequence;
- host/network/adapter/model/run identity recording;
- Canonical State acquisition, schema/Commit/Policy/System/Code hash comparison and recovery;
- Runner lock, `INIT` / `RESUMING` / `RUNNING`, inbox/outbox/UNKNOWN Order/Projection recovery;
- `MIGRATION_REQUIRED`, `RECOVERY_REQUIRED` and `RUNNER_LOCK_RECOVERY_REQUIRED` orchestration;
- `user_status`, `human_capacity`, `execution_slot`, Job state and catch-up/Relevance Check;
- process/CLI entry point, exit-code policy, target launch and normal-loop transition;
- degraded-mode policy after `DATA_STORAGE_UNAVAILABLE`;
- mapping from the v0.1 startup outcome into `RECOVERY_REQUIRED`, process action and the broader Incident taxonomy;
- Incident/Alert/Application Log persistence and Result Manifest interaction, including the Design Source §22 obligation that Alert/Incident recording continues for `DATA_STORAGE_IDENTITY_MISMATCH` and `ENVIRONMENT_BINDING_MISMATCH` even when System Critical Override is disabled;
- broader Runtime absolute-path provisioning/launcher convention;
- concurrency, cache lifetime and re-entry coordination;
- any retry/fallback policy explicitly authorized by a future closed contract.

Secret resolution remains the responsibility of the subsystem that consumes the secret; it is not a deferred Bootstrap-owned lookup stage.

## 12. Upstream consistency disposition

This draft changes no CLOSED capability status, history, type, validation rule or failure taxonomy. It composes the four upstream areas without duplicating their validation logic.

Consistency review result after adopting `ARGUS-BOOTSTRAP-CONTRACT-V01-REVIEW-RETRY-20261003-001`: `NO_CONTRADICTION_FOUND_AFTER_CORRECTION`. Config programmer-error raises, the complete operation algebra, startup-outcome identity mapping, explicit Identity path semantics, all-environment Binding behavior and first-failure short-circuit are now explicit.

The stale P-0021 gap analysis is retained as historical design input. Where P-0021 left questions open, the canonical Design Source, subsequently CLOSED contracts, adopted analyses and H1/H2 decisions govern this Orchestrator draft. P-0021 is not silently edited or treated as co-equal authority.

## 13. Development disposition

- Capability Registry state: `IN_PROGRESS`.
- Contract status: corrected draft, ready for independent delta re-review.
- Production implementation: not started and not authorized here.
- Test Strategy, tests, Freeze, RED/GREEN, commit and push: not performed.
- Exact next job: independent Runtime Bootstrap Orchestrator Contract v0.1 delta re-review; only after an accepted review may Test Strategy drafting begin.
