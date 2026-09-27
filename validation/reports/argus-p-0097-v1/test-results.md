# ARGUS-P-0097-v1 Verification Results

## Result

- Repository pytest: PASS, 215 tests
- HSD generation skill pytest: PASS, 106 tests
- Ruff: PASS
- Pyright (P-0097 changed scripts): PASS, 0 errors
- Bandit: PASS
- pip-audit: PASS, no known vulnerabilities

## Notes

- pytest reported one cache warning because the existing `.pytest_cache` path could not be created/accessed. Test execution itself passed.
- Ruff reported access-denied warnings while traversing existing cache entries, but completed with `All checks passed` and exit code 0.
- Repository-wide Pyright was also run and reported seven pre-existing errors in `tests/component/test_data_root_marker_store_contract.py` concerning private member use and unknown lambda parameter types. P-0097 changed scripts pass Pyright with zero errors.
- The first pip-audit attempt was blocked by sandbox network access. It was rerun with approved network access and passed.

## Gate Results

- Section 3.4 provenance: PASS
- Section 3.4 mechanical: PASS
- Section 3.4 human-facing: PASS
- Section 3.4 semantic: PASS, 94/94 PRESERVED
- Section 3.5 provenance: PASS
- Section 3.5 mechanical: PASS
- Section 3.5 human-facing: PASS
- Section 3.5 semantic: PASS, 66/66 PRESERVED
- Context-to-Coverage completeness: PASS, 133 Context meanings mapped to 160 Coverage Units
- Assembly semantic review: PASS
- R-01 through R-06 regression: PASS

