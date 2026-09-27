# EB-L1-TEST-ENVIRONMENT-GUARD Oracle Mapping

Canonical contract: `docs/design/argus_environment_binding_contract_v0.1.md#9.4`
Requirement: `ENVIRONMENT-BINDING-TEST-ENVIRONMENT-GUARD`
Oracle: `EXACT_CONTRACT_ORACLE-v1`
Test level: L1

| Test ID | Input / requirement | Exact expected result | Failure class / code | Required side effect | API | §9.3 dependency | RED |
|---|---|---|---|---|---|---|---|
| EB-L1-020 | valid TEST Marker, matching state/data-root/environment, valid locator | `VerifiedEnvironmentBinding` carrying the load-and-verify result | N/A | read-only; one marker load; no create/repair/overwrite | `verify_test_environment_startup` | uses existing load and comparison behavior without duplicating its internals | required |
| EB-L1-021 | expected and Marker are PAPER, or both LIVE | `TestEnvironmentGuardFailure(TEST_ENVIRONMENT_REQUIRED)` | N/A / `TEST_ENVIRONMENT_REQUIRED` | no filesystem read/write, fallback, or marker change | `verify_test_environment_startup` | guard-only rejection before existing load logic | required |
| EB-L1-022 | TEST expected; valid Marker with only `state_id` mismatched; both boundaries | unchanged `BindingFailure`; no success state / resolved target | `{ENVIRONMENT_BINDING_MISMATCH}` / `(STATE_ID_MISMATCH,)` | read-only; no new root write | both guard APIs | delegates comparison to existing §9.3 API | required |
| EB-L1-023 | TEST expected; valid Marker with only `data_root_id` mismatched; both boundaries | unchanged `BindingFailure`; no success state / resolved target | `{DATA_STORAGE_IDENTITY_MISMATCH}` / `(DATA_ROOT_ID_MISMATCH,)` | read-only; no new root write | both guard APIs | delegates comparison to existing §9.3 API | required |
| EB-L1-024 | TEST root with missing Marker or malformed JSON; both boundaries | unchanged load-and-verify `BindingFailure`; no success state | missing: identity mismatch / `MARKER_MISSING`; malformed: identity mismatch / `MALFORMED_JSON` | no marker, canonical data/state, or target creation/change | both guard APIs | delegates load/parse mapping to existing §9.3 API | required |
| EB-L1-025 | startup success, then injected success or failure at write boundary | exactly one fresh load-and-verify call per write boundary; fresh binding in success result or same failure value | injected failure preserved | startup result alone cannot authorize; failure has no write side effect | `resolve_test_write_target` | relies on existing load-and-verify as injected boundary | required |
| EB-L1-026 | every §8.1 rejection class plus valid mixed separators | exact `WriteTargetPathFailure`, or fresh-bound `ResolvedWriteTarget` under root | exact §8.1 path code; success N/A | invalid path performs no filesystem read/write | `resolve_test_write_target` | binding is reached only after lexical validation | required |
| EB-L1-027 | startup/write success, binding failure, guard failure, and path failure with initialization fail injection | each preceding exact value; initialization call count zero | code of each selected outcome | no create/complete/repair/overwrite or fallback | both guard APIs | verifies guard composition, not store initialization behavior | required |

No Contract ambiguity, missing API, or additional path semantics were introduced. Physical containment, reparse points, 8.3 aliases, device replacement, complete TOCTOU prevention, and production Writer lifecycle remain outside this Frozen Test candidate.

