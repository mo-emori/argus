# ARGUS Runtime Entry Resolution Test Strategy v0.1

**System:** `argus`  
**Document Type:** Capability Test Strategy / Verification Design  
**Status:** `TEST_CANDIDATE_READY_FOR_PRE_RED_RETRY`  
**Capability:** `RUNTIME-ENTRY-RESOLUTION`  
**Authoritative Contract:** `docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md`  
**Contract status:** `RUNTIME_ENTRY_RESOLUTION_CONTRACT_READY_FOR_TEST_STRATEGY`  
**Registry status:** `IN_PROGRESS`  
**Date:** 2026-10-01

## 1. Purpose, authority, and job boundary

This document derives the future verification baseline from the finalized Runtime Entry Resolution Contract. The Contract is the sole behavioral oracle. The Design Source remains the design authority; the general Test Strategy and the Runtime Config/Runtime Identity lifecycle records supply verification process conventions only. Existing implementation, test convenience, and adjacent-capability behavior do not add meaning.

The strategy was initially derived before test code existed. The current correction adds the complete executable test candidate and corrects only lifecycle classification. It does not create production code, an accepted Pre-RED result, a baseline, a freeze, Formal RED, GREEN, Registry transition, commit, or push. Contract review found no direct internal contradiction and no unresolved Design Authority marker.

## 2. Test levels and binding convention

| Level | Boundary | Allowed observation |
|---|---|---|
| Unit (`RER-U`) | bytes decode, duplicate-aware JSON parsing, schema/value validation, immutable value construction with controlled collaborators | typed diagnostic/result values, exact fields, ordering, purity |
| Component (`RER-C`) | one explicit Manifest path through load and physical Python-package resolution | filesystem/finder calls at public dependency boundaries, typed result/failure, short-circuit behavior |
| Integration (`RER-I`) | Entry Resolution composed with already-validated Runtime Identity and configured Runtime Config values | ownership/order boundaries and exact upstream-to-result mapping; no upstream semantic revalidation |
| Static (`RER-S`) | future public API, types, imports, source/test inventory, and prohibited dependencies | closed shape, Test-ID binding, absence of forbidden responsibility coupling |

Future test/implementation coordination should use a subsystem-local public module such as `argus.runtime.runtime_entry_resolution`, with the Contract's `resolve_runtime_entry(identity, config_snapshot, artificial_manifest_path)` operation and named immutable value/failure types. The exact Python symbol spelling is a Test Binding, not new Contract semantics; Pre-RED must freeze the chosen public binding before Formal RED. Tests assert only public values and externally observable dependency calls, not private helper names or an internal call graph.

## 3. Stable Test-ID and granularity rules

- Canonical inventory is exactly `RER-U-001..020`, `RER-C-001..025`, `RER-I-001..006`, and `RER-S-001..006` (57 IDs).
- One ID denotes one independently observable obligation. An ID is never reused, reassigned, or broadened to absorb a later correction.
- Parameterized cases may share an ID only when they are boundary representatives of the same oracle. Every case has a stable case label in test metadata/reporting.
- A test function or explicit metadata must expose exactly one primary Test ID. One function may not claim unrelated IDs merely because a common fixture reaches them.
- A later correction receives a new ID and a governed revision classification. It does not overwrite a historical binding. This rule directly prevents recurrence of the Runtime Identity Test-ID correction incident.
- Every ID below is baseline-freeze eligible (`BF=YES`) and is invoked in Formal RED (`FR=YES`) once executable test code, Pre-RED, and Human-authorized Freeze exist. `FR=YES` means inclusion in the run, not that every ID must fail. Implementation-dependent behavioral IDs are `RED_REQUIRED`; inherited regression and lifecycle/static-inventory IDs are `PASS_PERMITTED`. Eligibility and classification are not evidence that those lifecycle stages have occurred.
- `RER-I-006`, `RER-S-005`, and `RER-S-006` are `PASS_PERMITTED`: they verify inherited CLOSED upstream behavior/references, the frozen candidate inventory, and authorized scope/lifecycle state. Their legitimate PASS before Entry Resolution production exists does not invalidate Formal RED. `RER-S-001..004` remain `RED_REQUIRED` because they inspect the absent/incomplete Entry Resolution production surface. All `RER-U-*`, `RER-C-*`, and `RER-I-001..005` remain `RED_REQUIRED` because their oracles depend on Entry Resolution behavior.

## 4. Common exact oracles and non-vacuity

On failure, the public value is exactly one `RuntimeEntryResolutionFailure` containing one subsystem-local `RuntimeEntryResolutionDiagnostic(code, field_name)`. No success payload is present. OS/localized text, raw exception, stack trace, and path text are not equality fields. The first failing stage terminates processing; within schema validation the first defect follows `schema_version`, `startup`, `startup.kind`, `startup.entry`.

On success, the result is immutable and has exactly `startup_target`, `expected_binding`, and `data_root_locator`; the target is immutable and has exactly `kind`, `module_name`, and `origin_path`. Tests must compare complete public shapes, not truthiness or a subset.

Every executable behavioral test must prove Entry Resolution was exercised by all of the following applicable bindings:

1. invoke the frozen public Entry Resolution operation, not a fixture-only parser or a reimplemented oracle;
2. assert the complete typed success or failure value and the primary Test ID;
3. use a sentinel Manifest path/bytes/finder outcome that differs from defaults, so an unconditional canned result cannot pass;
4. for terminal failures, assert at least one prohibited downstream public dependency boundary has zero calls;
5. for success, assert Manifest read and finder/physical validation were actually consumed exactly as required;
6. prohibit mocks that return the expected public result directly and prohibit assertions satisfied only by import/collection failure;
7. require mutation controls at Pre-RED: changing the relevant fixture token or collaborator outcome must change/fail the observation for each requirement family.

Production-surface static tests (`RER-S-001..004`) must inspect the frozen production surface or source inventory and fail when it is absent. A no-file/no-symbol condition for those IDs is RED, never a vacuous PASS. Lifecycle/static-inventory checks (`RER-S-005..006`) inspect canonical artifacts and may PASS before production exists. `skip`, `xfail`, `Any`, `getattr`, ignore comments, broad exception swallowing, or configuration exclusion may not conceal an absent binding or unexercised path.

## 5. Unit requirements

| Test ID | Contract | Setup / input | Expected observation | BF | FR |
|---|---|---|---|---:|---:|
| `RER-U-001` | §3.1, §3.2 | canonical UTF-8 bytes | parse/schema stage accepts the exact four required values and proceeds to target resolution | YES | YES |
| `RER-U-002` | §3.2, §6 | leading UTF-8 BOM | exactly `MANIFEST_READ_ERROR(None)`; no JSON/schema/finder call | YES | YES |
| `RER-U-003` | §3.2, §6 | truncated/trailing-token JSON and bounded deeply nested decoder input | exactly `MALFORMED_JSON(None)`; decoder/recursion exception does not escape | YES | YES |
| `RER-U-004` | §3.2, §6 | duplicate root member, including equal values and escaped-equivalent decoded names | exactly `DUPLICATE_FIELD(decoded_name)`; no last-value-wins or schema stage | YES | YES |
| `RER-U-005` | §3.2, §6 | duplicate member inside `startup` | exactly `DUPLICATE_FIELD(decoded_name)`; no target resolution | YES | YES |
| `RER-U-006` | §3.2-3.3, §6 | duplicate member inside an otherwise unknown nested object | duplicate is still detected and returned before unknown-field ignore | YES | YES |
| `RER-U-007` | §3.2, §6 | array, string, number, boolean, or null root | exactly `MANIFEST_SCHEMA_INVALID(None)` | YES | YES |
| `RER-U-008` | §3.1, §6 | missing `schema_version` | exactly `MANIFEST_SCHEMA_INVALID("schema_version")` | YES | YES |
| `RER-U-009` | §3.1, §3.4, §6 | number, null, boolean, array, or object `schema_version` | exactly `MANIFEST_SCHEMA_INVALID("schema_version")`; no coercion | YES | YES |
| `RER-U-010` | §3.4, §6 | string versions `"0.0"`, `"0.1.0"`, `"1"`, empty, whitespace/case variants | exactly `UNSUPPORTED_SCHEMA_VERSION("schema_version")` | YES | YES |
| `RER-U-011` | §3.1, §6 | missing `startup` and non-object `startup` cases | exactly `MANIFEST_SCHEMA_INVALID("startup")` | YES | YES |
| `RER-U-012` | §3.1, §6 | missing or non-string `startup.kind` | exactly `MANIFEST_SCHEMA_INVALID("startup.kind")` | YES | YES |
| `RER-U-013` | §3.1, §3.4, §6 | `startup.kind` case/space/Unicode variants and other kinds | exactly `MANIFEST_SCHEMA_INVALID("startup.kind")`; no trim/case/normalization/fallback | YES | YES |
| `RER-U-014` | §3.1, §6 | missing or non-string `startup.entry` | exactly `MANIFEST_SCHEMA_INVALID("startup.entry")` | YES | YES |
| `RER-U-015` | §3.4, §6 | `argus/runtime`, `argus.runtime:main`, `.argus.runtime`, `argus.runtime.__main__`, case/space/Unicode variants | exactly `MANIFEST_SCHEMA_INVALID("startup.entry")`; no completion/conversion/alias | YES | YES |
| `RER-U-016` | §3.3 | unique unknown root members with scalar/object/array content | ignored; not retained or forwarded and canonical required meaning is unchanged | YES | YES |
| `RER-U-017` | §3.3 | unique unknown members inside `startup` | ignored; target selection remains exactly `python_module` / `argus.runtime` | YES | YES |
| `RER-U-018` | §3.3-3.4 | unknown fields attempt to supply path, binding, command, fallback, or alternate candidates | values cannot change target, Binding inputs, or failure precedence | YES | YES |
| `RER-U-019` | §4, §6 | multiple simultaneous schema defects | exactly the first canonical-field-order diagnostic; later schema checks/finder are not observed | YES | YES |
| `RER-U-020` | §3.2-3.4 | legal JSON whitespace/key order positive controls plus near-miss tokens | whitespace/key order do not alter meaning; no default, numeric/string coercion, trim, case fold, or Unicode normalization occurs | YES | YES |

## 6. Component requirements

| Test ID | Contract | Setup / input | Expected observation | BF | FR |
|---|---|---|---|---:|---:|
| `RER-C-001` | §2, §4 | absolute path whose case-sensitive basename is `manifest.json`, readable regular file, valid bytes | exactly that file is loaded once; no discovery or alternate Manifest access | YES | YES |
| `RER-C-002` | §2, §4, §6 | relative `manifest.json` path | exactly `MANIFEST_PATH_INVALID(None)`; filesystem/finder calls are zero | YES | YES |
| `RER-C-003` | §2, §4, §6 | absolute path with `Manifest.json`, other basename, or trailing child | exactly `MANIFEST_PATH_INVALID(None)` before existence/read | YES | YES |
| `RER-C-004` | §4, §6 | public path carrier whose lexical absolute/basename operation fails | exactly `MANIFEST_PATH_INVALID(None)`; raw exception does not escape | YES | YES |
| `RER-C-005` | §4, §6 | valid lexical path that is genuinely absent | exactly `MANIFEST_NOT_FOUND(None)`; no read/parse/finder | YES | YES |
| `RER-C-006` | §4, §6 | path exists but is not a regular file | exactly `MANIFEST_READ_ERROR(None)`; no parse/finder | YES | YES |
| `RER-C-007` | §4, §6 | regular file whose read raises permission or generic I/O error | exactly `MANIFEST_READ_ERROR(None)`; raw exception/path text absent from equality | YES | YES |
| `RER-C-008` | §3.2, §4, §6 | regular file containing invalid UTF-8 | exactly `MANIFEST_READ_ERROR(None)`; no JSON/schema/finder | YES | YES |
| `RER-C-009` | §4, §6 | representative failure at each ordered stage | one diagnostic from earliest failing stage and zero later-stage calls | YES | YES |
| `RER-C-010` | §4 | valid schema with controlled side-effect-free finder | finder receives exactly `argus.runtime`; no CWD/repository/search-path insertion and no import | YES | YES |
| `RER-C-011` | §4, §6 | finder returns no specification | exactly `STARTUP_TARGET_NOT_FOUND("startup.entry")` | YES | YES |
| `RER-C-012` | §4, §6 | finder raises resolution/inspection error | exactly `STARTUP_TARGET_INVALID("startup.entry")`; exception does not escape | YES | YES |
| `RER-C-013` | §4-4.1, §6 | built-in, frozen, origin-unknown, namespace-only, or otherwise non-concrete spec cases | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-014` | §4-4.1, §6 | spec represents a non-package module | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-015` | §4, §6 | spec exposes multiple locations without a single concrete origin | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-016` | §4, §6 | concrete-looking spec whose origin path is absent | exactly `STARTUP_TARGET_NOT_FOUND("startup.entry")` | YES | YES |
| `RER-C-017` | §4-4.1, §6 | existing origin whose basename is not exactly `__init__.py` | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-018` | §4-4.1, §6 | origin exists but is a directory or another non-regular type | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-019` | §4-4.1, §6 | regular `__init__.py` whose binary open/readability check fails | exactly `STARTUP_TARGET_INVALID("startup.entry")` | YES | YES |
| `RER-C-020` | §4-5 | valid concrete package spec and readable regular `__init__.py` | target has exact literals and absolute normalized origin; open/close succeeds without import/compile/execute | YES | YES |
| `RER-C-021` | §4, §7 | valid and invalid controlled cases with spies for import, compile, callable lookup, process, network, clock, writes, Marker, Binding | all prohibited calls are zero; Manifest/target bytes remain unchanged | YES | YES |
| `RER-C-022` | §4-5 | repeat same explicit path, bytes, finder result, and filesystem observations under different CWD/environment/directory contents | equal typed result/failure; no discovery, randomness, or directory inference | YES | YES |
| `RER-C-023` | §5 | successful invocation | exact immutable result/target field set; no Manifest path/hash, provenance, config path, timestamp, host, run/deployment fields | YES | YES |
| `RER-C-024` | §5 | identity/config sentinels plus valid target | exact `ExpectedEnvironmentBinding(state_id, data_root_id, environment)` and `DataRootLocator(path=data_root_path)`; no Manifest-derived substitutes | YES | YES |
| `RER-C-025` | §5, §7 | config snapshot with sentinel `data_root_path` whose target is absent/inaccessible and path operations are fail-on-call | locator preserves the supplied value; no recanonicalize/existence/Marker/identity/read-write check | YES | YES |

## 7. Integration and static boundary requirements

| Test ID | Contract | Setup / input | Expected observation | BF | FR |
|---|---|---|---|---:|---:|
| `RER-I-001` | §1-2, §5 | real public Runtime Identity value and configured Runtime Config snapshot with distinct sentinels | Entry Resolution consumes them as immutable inputs and maps only the specified four upstream fields | YES | YES |
| `RER-I-002` | §2, §7 | upstream loader/parser/validator APIs instrumented fail-on-call | no Runtime Identity or Runtime Config reread, reparse, revalidation, or re-resolution | YES | YES |
| `RER-I-003` | §2, §5, §7 | no `config_path` argument; config loader and discovery boundaries fail-on-call | Entry Resolution neither accepts/supplies `config_path` nor reruns Config responsibilities | YES | YES |
| `RER-I-004` | §1-2, §7 | paths, drive/directory/module locations deliberately imply a different environment than identity | output environment is exactly `identity.environment`; no directory-based environment/identity inference | YES | YES |
| `RER-I-005` | §1, §4.1, §5, §7 | success and failure with Orchestrator/Binding/execution/Result Manifest boundaries fail-on-call | no Environment Binding, target import/execution/process start, Result Manifest, Registry/evidence closure, or later readiness semantics | YES | YES |
| `RER-I-006` | §1-2, §5-7 | run frozen CLOSED Runtime Identity and Runtime Config affected regression selections beside RER tests | their public semantics/evidence remain inherited; no changed upstream schema, failure enum, ordering, or ownership is required for RER | YES | YES |
| `RER-S-001` | §5-6 | inspect frozen public type surface | success/target/failure/diagnostic are subsystem-local immutable typed shapes with exactly the Contract fields and closed code set | YES | YES |
| `RER-S-002` | §2, §5 | inspect public resolver signature/types | requires validated identity, configured snapshot, one Manifest path; has no `config_path`, runtime root, bytes bypass, command, or alternate target input | YES | YES |
| `RER-S-003` | §7 | inspect production imports/references and test spies | no production dependency enabling module import/execution, Environment Binding call, Result Manifest, process/network/clock/Marker/state/write/lock/recovery/secret responsibilities | YES | YES |
| `RER-S-004` | §2, §4, §7 | inspect source and tests for discovery/inference mechanisms | no CWD/repository/env/directory search, relative anchoring, search-path mutation, environment inference, fallback, or repair | YES | YES |
| `RER-S-005` | §§1-9 | AST/metadata inventory of future tests | union is exactly all 57 IDs, each primary binding occurs once, no missing/unexpected/reused ID, and traceability is bidirectional | YES | YES |
| `RER-S-006` | §1, §7, §9 | repository diff/scope inventory | no Contract edit, upstream Contract/test semantic edit, production/test implementation outside the authorized future job, Registry close, or Result Manifest work is smuggled into the baseline | YES | YES |

## 8. Contract-to-test traceability and coverage

| Contract obligation group | Test IDs | Coverage statement |
|---|---|---|
| §1 authority, order, ownership | `RER-I-001..006`, `RER-S-003..004` | Entry Resolution's owned work and later/upstream boundaries remain separated |
| §2 explicit input boundary | `RER-C-001..004`, `RER-I-001..004`, `RER-S-002`, `RER-S-004` | one absolute canonical Manifest path; no discovery, config path, or upstream rerun |
| §3.1 required schema | `RER-U-001`, `RER-U-008..015` | every required field, type, and closed value has positive/negative coverage |
| §3.2 strict JSON/duplicates | `RER-U-002..007`, `RER-U-020`, `RER-C-008` | UTF-8/BOM, malformed/deep, decoded-name duplicate at all object locations, object root |
| §3.3 compatibility/unknown fields | `RER-U-006`, `RER-U-016..018`, `RER-C-024` | duplicate-first and inert ignore policy without retention/behavior changes |
| §3.4 version/normalization | `RER-U-009..010`, `RER-U-013`, `RER-U-015`, `RER-U-020` | exact version and token comparisons; no repair/coercion/normalization |
| §4 deterministic ordered resolution | `RER-C-001..022` | load once, parse order, finder, package/origin/readability oracle, determinism |
| §5 typed result/Binding inputs | `RER-C-020`, `RER-C-023..025`, `RER-I-001`, `RER-S-001..002` | exact immutable result and allowed upstream composition only |
| §6 local typed failures | `RER-U-002..015`, `RER-U-019`, `RER-C-002..019`, `RER-S-001` | all nine codes, field names, first-stage/field precedence, no raw exception leakage |
| §7 side effects/non-responsibilities | `RER-C-021..022`, `RER-C-025`, `RER-I-002..006`, `RER-S-002..004` | no inference, upstream rerun, execution, Binding, Result Manifest, or stateful side effects |
| §8 resolved testability markers | `RER-U-001..020`, `RER-C-010..025` | bytes, isolated finder, physical origin, mapping, and ordering are observable |
| §9 lifecycle disposition | §9-§15 and `RER-S-005..006` | Strategy only; downstream lifecycle remains gated and Registry stays `IN_PROGRESS` |

All normative behavior has at least one independently observable primary ID. Failure-code coverage is exact: path invalid (`C-002..004`), not found (`C-005`), read (`U-002`, `C-006..008`), malformed (`U-003`), duplicate (`U-004..006`), schema (`U-007..009`, `U-011..015`), version (`U-010`), target not found (`C-011`, `C-016`), and target invalid (`C-012..015`, `C-017..019`).

## 9. Pre-RED static checks

A future Pre-RED job must produce `PRE_RED_PASS_BASELINE_FREEZE_READY` only when all checks pass:

1. test files and helpers decode as UTF-8 and compile/parse; test collection structure is valid without executing behavioral tests;
2. AST/metadata inventory proves exactly 57 primary IDs and the four contiguous ranges in §3, with one primary binding per ID and no reuse;
3. every table row contains Contract clause, level, setup/input, complete observation, `BF`, and `FR`; future code maps bidirectionally to the row;
4. non-vacuity rules in §4 are mechanically checked, including sentinel consumption, public resolver invocation, terminal zero-call assertions, and prohibited direct-result mocks;
5. Ruff and Pyright run on the candidate tests/helpers; test-owned lint/type/config/import defects are zero;
6. absent intended production module/symbol diagnostics are isolated as `EXPECTED_STATIC_RED`, with root count and mechanically derived unknown-type count; this is not PASS;
7. syntax, wrong import path, missing dependency, malformed fixture, unrelated diagnostics, suppression, collection failure, or configuration exclusion blocks Pre-RED;
8. traceability confirms all Contract groups in §8 and all nine failure codes; unknown-field cases prove duplicate-first behavior;
9. scope inventory proves Contract and CLOSED Runtime Identity/Config semantics were not edited and no production/baseline/Registry work occurred;
10. paths and SHA-256 values for every baseline input in §10, Git HEAD/worktree state, tool/config versions, commands, and raw outputs are recorded.

Pre-RED is static validation only. It does not run the future behavioral suite against production and does not freeze anything.

## 10. Future baseline inputs and Freeze rules

The Human-authorized baseline must freeze by path plus SHA-256:

1. finalized Runtime Entry Resolution Contract;
2. approved revision of this Test Strategy;
3. complete future test files, fixtures, helpers, and Test-ID metadata;
4. accepted `PRE_RED_PASS_BASELINE_FREEZE_READY` evidence and raw static outputs;
5. `pyproject.toml` and every effective test/lint/type/static configuration file;
6. exact 57-ID inventory, bidirectional traceability report, non-vacuity report, and mutation-control report;
7. CLOSED Runtime Identity and Runtime Config Contract/test references and the selected inherited regression inventory/hashes;
8. Git HEAD, working-tree status, tracked diff hash, and hashes of untracked capability inputs;
9. reserved Formal RED run ID, expected absent-production root cause and production symbol-presence state;
10. Human approval reference, timestamp, baseline ID/version, and freeze rule.

Freeze rule: the Contract, approved Test Strategy, tests, fixtures, helpers, ID bindings, and effective configuration must not be changed merely to make production pass. Any change requires rationale, impact classification, Human approval, new hashes, repeated Pre-RED, a new freeze, and Revision RED where applicable. Historical IDs and evidence remain immutable; removal is tombstoned, not reassigned. This document supplies the future input list only and does not compute a candidate baseline or freeze it.

## 11. Formal RED requirement

Formal RED is mandatory, non-waivable, and may run only after accepted Pre-RED and Human-authorized Freeze. All frozen RER tests are invoked. Accepted RED requires every `RED_REQUIRED` ID to fail solely because the frozen Entry Resolution production surface is intentionally absent/incomplete, with test collection and test-owned static validity already established. Every `PASS_PERMITTED` ID must PASS and may not be counted as a RED failure. The run records per-ID classification and outcome, failing IDs, phase, root cause, hashes, command/tool versions, exit status, and raw output references.

Unexpected PASS by a `RED_REQUIRED` ID; any failure by a `PASS_PERMITTED` ID; wrong-reason failure; unrelated regression/environment failure; syntax/fixture/config/dependency/permission error; hash drift; skip/xfail; test weakening; or mixed expected/unexpected failure yields `FORMAL_RED_BLOCKED`, not accepted RED. Import/collection failure is acceptable only if it exactly matches the frozen absent public module/symbol root cause and does not prevent the evidence system from identifying the complete intended frozen inventory. Accepted outcome is exactly `FORMAL_RED_ACCEPTED`.

## 12. GREEN, regression, and static closure gates

After accepted Formal RED, a separate authorized implementation job may seek GREEN. Closure requires:

- all 57 frozen IDs PASS with no skip/xfail/unexpected warning and hashes matching the baseline;
- expected static RED is gone without suppression or configuration weakening;
- scoped and repository-required `pytest`, `ruff`, `pyright`, `bandit`, and `pip-audit` results are recorded; failures are reported and current-change attribution is explicit;
- affected CLOSED Runtime Identity/Config regression selections pass unchanged, with prior evidence inherited rather than relabeled as new RER evidence;
- no Contract-external feature, fallback, environment inference, upstream semantic change, Result Manifest, Binding call, import/execution, or Registry closure was introduced;
- evidence records commands, tool versions, effective configuration hashes, exit status, raw-output hashes, test counts/IDs, code/worktree identity, and deviations.

GREEN automation does not close the capability. Registry remains `IN_PROGRESS` until independent review and the separately authorized closure transition complete.

## 13. Independent semantic review gate

An implementation author-independent reviewer must receive the Contract, approved/frozen strategy, frozen tests, full changed files/diff, Pre-RED/Freeze/RED/GREEN evidence, static/regression outputs, input manifest hash, and code/worktree identity. Review must check:

- every normative obligation and failure mapping against the Contract, especially duplicate-first unknown objects and version/type distinction;
- Test-ID granularity, one-primary-binding rule, non-vacuity, and absence of historical ID reuse;
- finder side-effect freedom, concrete package/origin/readability oracle, and no import/compile/execute expansion;
- exact result composition and no Manifest/config-path/provenance or directory-derived binding data;
- no upstream revalidation, Environment Binding, Orchestrator, Result Manifest, Registry, or later execution responsibility leakage;
- no test weakening, invented fault semantics, private-implementation overbinding, or silent baseline drift.

The reviewer returns `NO_FINDINGS` or evidence-backed findings with severity, Contract/Test-ID references, and disposition. Unresolved critical or major semantic findings block closure. Automated GREEN does not override review findings, and review does not replace deterministic test/static evidence.

## 14. Revision lifecycle

Any Contract change first returns to Design Authority and invalidates affected strategy/baseline inputs. Strategy-only clarification receives a new document revision and impact analysis. Test correction or new obligation receives new Test IDs; existing meanings/bindings remain preserved. Each revision follows: proposal and traceability impact → Human approval → revised Pre-RED → revised Freeze → Human commit checkpoint → mandatory Revision RED for changed/new security or fail-closed obligations → corrective GREEN/regression/static checks → independent review. Prior observations are not retroactively promoted to Revision RED.

Changes to schema versions, accepted kinds, launcher semantics, runtime-root containment, symlink policy, deployment metadata, or optional-field behavior are new Contract decisions, not test-strategy repair. No revision may silently reopen CLOSED Runtime Identity or Runtime Config semantics.

## 15. Strategy disposition and exact next step

This strategy is complete with 57 stable IDs, full Contract traceability, corrected Formal RED classification, and a complete executable candidate. The exact next lifecycle step is: **retry Pre-RED static validation against this strategy and candidate; do not execute behavioral RED and do not freeze until Pre-RED returns `PRE_RED_PASS_BASELINE_FREEZE_READY` and Human separately authorizes Freeze.**

`RUNTIME_ENTRY_RESOLUTION_TEST_CANDIDATE_READY_FOR_PRE_RED_RETRY`
