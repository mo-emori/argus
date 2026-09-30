# Proposed ADR-008 — Runtime Identity corrective boundary

Status: Human decision captured; canonical ADR publication blocked by workspace write boundary.

1. F1: Validate every `created_at` date/time/offset component lexically and by range before parser use. Invalid forms including hour `24`, minute `60`, second `60`, offset hour `24`, or offset minute `60` fail closed as existing `INVALID_CREATED_AT`; parser normalization must not repair them. Existing formats and ranges are not broadened.
2. F2: `parse_runtime_identity()` maps recursion/pathological JSON decoder failure to the existing typed result `MALFORMED_JSON` with `field_name=None`. `RecursionError` must not escape and no new public taxonomy is introduced.
3. F3: `serialize_runtime_identity()` emits canonical UTC RFC3339 for publicly constructible values whose UTC instant is representable in the supported datetime range. UTC `datetime.min` and `datetime.max` are required boundary cases. If UTC conversion of a publicly constructible value crosses that range, it raises `ValueError`, emits no bytes, and does not leak `OverflowError`. No behavior is promised for invariant-bypassed objects or arbitrary datetime internals.
4. F4: Validation is fail-closed. The first defect actually detected by the validation pipeline terminates validation and returns that defect's existing typed reason. Nested duplicates follow the same rule. Neither `DUPLICATE_FIELD` nor `MALFORMED_JSON` globally outranks the other; v0.1 defines no global error-priority taxonomy.

Consequences: the prior Runtime Identity baseline and its downstream evidence remain immutable history but are superseded for a revised baseline. The next sequence is revised Pre-RED, revised Freeze, Human commit checkpoint, then Revision RED. No production change, Registry transition, or Runtime Entry Resolution is authorized here.
