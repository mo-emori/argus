# Proposed Runtime Identity Corrective Test Strategy Amendment

The revised candidate keeps `tests/unit/test_runtime_identity_contract.py` and adds `tests/unit/test_runtime_identity_critical_path_corrections.py` as supplemental bindings to existing canonical IDs. Duplicate IDs mean additional concrete cases, not new requirements or replacement of original bindings.

| Finding | ID | Supplemental function | Delta class |
|---|---|---|---|
| F1 | `RI-L0-015` | `test_ri_l0_015_valid_rfc3339_boundaries_remain_accepted` | `ADDITIVE` |
| F1 | `RI-L0-016` | `test_ri_l0_016_invalid_rfc3339_boundaries_are_rejected_without_repair` | `TIGHTENING` |
| F2 | `RI-L0-002` | `test_ri_l0_002_pathologically_deep_json_is_a_typed_malformed_failure` | `ADDITIVE` |
| F3 | `RI-L0-024` | `test_ri_l0_024_serializer_supports_representable_datetime_range_edges` | `ADDITIVE` |
| F3 | `RI-L0-026` | `test_ri_l0_026_serializer_maps_unrepresentable_utc_edges_to_value_error` | `TIGHTENING` |
| F4 | `RI-L0-020` | `test_ri_l0_020_returns_first_defect_detected_by_validation_pipeline` | `RESTATEMENT` |

Revised Pre-RED must statically verify both test files, confirm the union remains exactly `RI-L0-001..028`, confirm supplemental bindings are exactly `{002,015,016,020,024,026}`, and mechanically establish unchanged bindings/oracles for all other IDs. It must hash the canonical ADR, Contract amendment, this strategy amendment, both test files, invalidation record, and static configuration as revised inputs.

No RED or GREEN is run by this specification job. Existing corrective observations are context only and must not be promoted to Revision RED. Gate order: revised Pre-RED → revised Freeze → Human commit checkpoint → Revision RED.
