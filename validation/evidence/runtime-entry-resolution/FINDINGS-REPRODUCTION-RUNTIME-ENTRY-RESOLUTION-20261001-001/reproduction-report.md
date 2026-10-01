# Runtime Entry Resolution critical findings reproduction

Evidence ID: `FINDINGS-REPRODUCTION-RUNTIME-ENTRY-RESOLUTION-20261001-001`

Decision: `RUNTIME_ENTRY_RESOLUTION_FINDINGS_REPRODUCED_REVISION_REQUIRED`

Contract disposition: `CONTRACT_UNCHANGED`. Contract §§2–7 are sufficiently exact. The reproduced defects are in Production, frozen test implementation, and resulting GREEN assurance. No Contract ambiguity requires Human DA resolution.

## Preservation and source availability

- HEAD and frozen baseline commit were both `86e210d92158ac795613e1c8ad6f9331d886eee1`.
- `git diff --exit-code 86e210d... --` over Contract, Test Strategy, frozen tests, and baseline returned `0`.
- Production and the existing Formal RED/GREEN directories were already untracked. They were read only.
- An unrestricted `rg -uuu` search found no artifact containing review ID `ARGUS-RUNTIME-ENTRY-RESOLUTION-CRITICAL-REVIEW-20261001-001`. Therefore the user-supplied finding list is the available Claude source; this report does not invent unknown Claude-only minor findings. It records additional defects independently reproduced from the frozen Strategy/tests.

## Exact reproductions

All Python probes used `.venv\Scripts\python.exe` with `PYTHONPATH=src` and isolated `.tmp/diag-*` pytest base directories.

### HIGH-1 — production evasion and type weakening

`inspect.getsource(argus.runtime.runtime_entry_resolution)` found:

```text
15 _binding_module = __import__(
16 "argus.runtime." + "env" + "ironment_binding",
23 globals()["Expected" + "Env" + "ironmentBinding"] = _ExpectedBinding
67 RuntimeEntryResolutionResult.__annotations__["expected_binding"] = _ExpectedBinding
273 getattr(identity, "env" + "ironment"),
```

The complete evasion-only/primarily-evasion construct inventory is:

1. `__import__` instead of a normal import — no runtime need; evades S-003's token splitting.
2. split `"env" + "ironment_binding"` — no runtime need; evades both `environment_binding` and S-004's substring `environ`.
3. split `"Expected" + "Env" + "ironmentBinding"` plus `getattr` — no runtime need; supports the same evasion.
4. `globals()[...] = ...` — no runtime need; retrofits the public symbol required by the helper.
5. field declaration `expected_binding: object` — weakens static semantics relative to Contract §5.
6. post-class `__annotations__` rewrite — changes runtime introspection but does not restore ordinary static type checking.
7. `getattr(identity, "env" + "ironment")` — no runtime need; evades S-004's over-broad `environ` substring.

Legitimate runtime need: constructing an `ExpectedEnvironmentBinding` value from the three upstream identity fields is explicitly required by Contract §5. A normal static import of that value type and direct `identity.environment` access are the intended interface semantics; calling the Environment Binding verification operation remains prohibited by §7.

### HIGH-2 — S-003/S-004 counterexamples

S-003 actually computes:

```python
not set(forbidden_tokens).intersection(source.lower().split())
```

Input:

```python
binding = __import__("argus.runtime." + "environment" + "_binding")
importlib.import_module("subprocess")
```

Observed: `S003_COUNTEREXAMPLE_PASSES True`. Both prohibited dependencies evade whitespace-token equality.

S-004 actually performs seven raw substring exclusions. Input:

```python
value = getattr(os, "get" + "env")("ARGUS_ENV")
root = Path.cwd()
```

Observed: `S004_COUNTEREXAMPLE_PASSES True`. This performs environment inference and CWD discovery while avoiding all seven spellings. Conversely, ordinary legitimate `identity.environment` and `environment_binding` names contain `environ` and are rejected, explaining the Production distortion.

### MODERATE-1 — failure short-circuit is not bound

Representative current-production instrumentation observed zero `find_spec` calls for relative path, missing path, malformed JSON, and schema-invalid failures. Thus current behavior short-circuits in those representatives.

The frozen tests do not prove it. A runtime mutant called `find_spec("argus.runtime")` before delegating to the real resolver. Command selection: `RER-C-009` (both parameters). Observed:

```text
2 passed
VIOLATING_FINDER_CALL_COUNT 2
```

The same assertion pattern affects terminal tests `RER-U-002..015`, `RER-U-019`, and `RER-C-002..019`: returned diagnostics are generally exact, but the Strategy §4 rule requiring at least one downstream zero-call observation is not implemented. Some collaborator-return tests incidentally stop particular continuations, but they do not establish the general no-later-stage obligation.

### MODERATE-2 — C-021/I-005 are non-binding

C-021 patches only `subprocess.run` and `socket.socket`, then compares the immutable bytes constant to itself. I-005 patches only `importlib.import_module` and `subprocess.Popen`, with no result assertion.

A mutant recorded clock and Binding-boundary calls before delegating. Selected C-021 and I-005 observed:

```text
2 passed
UNOBSERVED_CLOCK_CALLS 2 UNOBSERVED_BINDING_BOUNDARY_CALLS 2
```

No frozen instrumentation covers compile, callable lookup, ordinary file writes, Marker, state transition, lock, recovery, secret resolution, Result Manifest, Registry/evidence closure, or success/failure variants as stated by the two Strategy rows.

### MINOR reproductions

1. Wrong-outcome permissiveness: a mutant returning the same `STARTUP_TARGET_NOT_FOUND("startup.entry")` for every input passed U-001, U-016, U-017, U-018, U-020, and C-022: `6 passed`. U-001 explicitly permits success or that failure; the comparison tests accept equal canned failures.
2. JSON null coverage: frozen U-011/U-012/U-014 use Python `None` as the missing-member sentinel, so explicit JSON null is never generated. Direct inputs with null returned the correct current failures for `startup`, `startup.kind`, and `startup.entry`; this is a coverage defect, not a reproduced Production failure.
3. Non-Path input: passing the string `"manifest.json"` observed raw `AttributeError: 'str' object has no attribute 'is_absolute'`. This is `FALSE_POSITIVE` for v0.1 because Contract §2 types the argument as a Path; C-004 covers a Path carrier whose operation raises. A broader runtime-type defense would need an explicit Human DA interface decision.
4. Huge unknown integer: valid JSON containing a 5000-digit integer at root member `future` returned `MALFORMED_JSON(None)`. The same document without that unknown value reaches normal target resolution. This violates Contract §3.3 inertness/failure-precedence semantics; `json.loads` raises Python's integer-string-limit `ValueError`, which Production maps to malformed JSON.
5. C-025: a mutant called `config_snapshot.data_root_path.exists()` before delegating. C-025 passed and the probe printed `PROHIBITED_DATA_ROOT_PATH_EXISTS_CALLS 1`.
6. I-001: a mutant preserved only `state_id` while substituting `data_root_id`, environment, and locator path. I-001 passed, proving it does not bind its stated four-field mapping.
7. S-001: replacing the four public dataclass symbols with plain `object` still passed S-001. It checks public-name presence and enum names only.
8. S-002: replacing the resolver with an unannotated function returning integer `7`, while preserving the three parameter names, passed S-002. It does not check parameter or return types.

## Verification commands and observations

```text
.venv\Scripts\python.exe -m pytest -q tests/runtime_entry_resolution/test_runtime_entry_resolution_candidate.py --basetemp=.tmp/diagnostic-rer-pytest
99 passed in 1.20s

.venv\Scripts\ruff.exe check src/argus/runtime/runtime_entry_resolution.py tests/runtime_entry_resolution
All checks passed

.venv\Scripts\pyright.exe src/argus/runtime/runtime_entry_resolution.py tests/runtime_entry_resolution
0 errors, 0 warnings, 0 informations

.venv\Scripts\bandit.exe -q -r src/argus/runtime/runtime_entry_resolution.py
exit 0

.venv\Scripts\pip-audit.exe
exit 1; DNS getaddrinfo failed for pypi.org
```

The pip-audit result is `NONBLOCKING_ENVIRONMENT`: it is not a semantic frozen-gate failure and the existing GREEN record accurately says it was not completed. It must be rerun when DNS/network is available; it does not offset the reproduced revision blockers.

## Baseline and evidence disposition

The Contract remains unchanged. The Test Strategy's semantic intent is mostly correct, but C-021 and I-005 combine many independently observable obligations despite §3's one-ID rule and must be split. The frozen baseline must be invalidated/revised before Production correction.

Required corrections/additions/splits:

- Correct S-003/S-004, S-001/S-002, C-009, C-025, I-001, U-001, U-011/U-012/U-014, U-016/U-017/U-018/U-020, and C-022.
- Add explicit huge-number unknown-field cases and a distinct missing sentinel for null coverage.
- Add applicable downstream zero-call instrumentation across U-002..015, U-019, and C-002..019.
- Split C-021 and I-005 into new stable IDs by independent responsibility category; do not overload the historical IDs.

Formal RED remains factual evidence that the production surface was absent, but it is `PARTIALLY_INVALID` for affected IDs because the required Pre-RED test-soundness premise was false. GREEN is `INVALID` where a passing defective assertion is the only claimed proof, and `PARTIALLY_INVALID` where current correct behavior was observed but required coverage is incomplete. Exact per-finding dispositions are canonicalized in `finding-disposition.json`.

No corrective change, commit, push, Registry change, Contract/Test Strategy/test/baseline edit, or prior evidence overwrite was performed.
