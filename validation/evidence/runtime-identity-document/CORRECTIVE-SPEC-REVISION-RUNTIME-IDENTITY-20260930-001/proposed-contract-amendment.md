# Proposed Runtime Identity Contract v0.1 Corrective Amendment

This amendment is limited to F1–F4. Every unmentioned v0.1 clause remains unchanged.

## F1 — `created_at`

Before datetime construction, the existing ASCII RFC3339 form must satisfy month `01..12`, hour `00..23`, minute/second `00..59`, offset hour `00..23`, offset minute `00..59`, and an actual calendar day. Parser normalization must not convert invalid schema input into valid identity data. Failure is exactly one `INVALID_CREATED_AT` for `created_at`, without repair or side effect.

## F2 — typed parse boundary

Pathological JSON decoder recursion returns exactly `RuntimeIdentityValidationFailure(errors=(RuntimeIdentityValidationError(MALFORMED_JSON, None),))`. `RecursionError` does not cross the public API.

## F3 — serializer edge boundary

UTC `datetime.min` and `datetime.max` serialize canonically and parse back to the same value. If a Contract-valid, publicly constructible aware datetime would cross outside that range during UTC conversion, serialization raises `ValueError` (message contains `canonical UTC range`), emits no bytes, and does not leak `OverflowError`.

## F4 — first detected defect

The first defect actually detected by the defined validation pipeline is terminal and returns its existing typed reason. A nested duplicate detected before a later outer malformed condition returns `DUPLICATE_FIELD` for the decoded key; malformed syntax detected before a later duplicate returns `MALFORMED_JSON`. This is pipeline detection order, not a global semantic precedence guarantee.

## Exact-oracle amendments

| Finding | Test ID | Exact oracle |
|---|---|---|
| F1 | `RI-L0-015` | `23:59:59Z`, offsets `±23:59`, and `+05:59` remain accepted. |
| F1 | `RI-L0-016` | `24:00`, minute `60`, offset minute `60`, and offset hour `24` return exactly one `INVALID_CREATED_AT("created_at")`. |
| F2 | `RI-L0-002` | Deep decoder recursion returns exactly one `MALFORMED_JSON(None)` and no exception. |
| F3 | `RI-L0-024` | UTC min/max serialize and round-trip exactly. |
| F3 | `RI-L0-026` | UTC-underflow/overflow conversion raises the specified `ValueError` only. |
| F4 | `RI-L0-020` | Return the first detected typed defect; nested behavior is identical; assert no global precedence. |
