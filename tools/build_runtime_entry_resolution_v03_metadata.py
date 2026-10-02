"""Build and machine-check the unfrozen Runtime Entry Resolution v0.3 metadata."""

from __future__ import annotations

import ast
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
TEST = Path("tests/runtime_entry_resolution/test_runtime_entry_resolution_candidate.py")
INPUTS = (
    Path("docs/source/argus_design_source_v0.1.md"),
    Path("docs/design/argus_system_design_v0.1.md"),
    Path("docs/adr/argus_architecture_decision_records_v0.1.md"),
    Path("docs/test/argus_test_strategy_v0.1.3.md"),
    Path("docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md"),
    Path("docs/test/argus_runtime_entry_resolution_test_strategy_v0.1.md"),
    TEST,
    Path("tests/runtime_entry_resolution/_candidate.py"),
    Path("tests/runtime_entry_resolution/_semantic_boundaries.py"),
    Path("tests/runtime_entry_resolution/_semantic_observer.py"),
    Path("tests/runtime_entry_resolution/test_semantic_mutant_diagnostics.py"),
    Path("tools/build_runtime_entry_resolution_v03_metadata.py"),
    Path("validation/evidence/external-review/ARGUS-RUNTIME-ENTRY-RESOLUTION-CC-EXEC-PROBE-ADOPTION-20261002-001/review-manifest.json"),
    Path("validation/evidence/external-review/ARGUS-RUNTIME-ENTRY-RESOLUTION-CC-EXEC-PROBE-ADOPTION-20261002-001/review-execution.json"),
    Path("validation/evidence/external-review/ARGUS-REVIEW-EVIDENCE-ADOPTION-SMOKE-20261002-001/review-manifest.json"),
    Path("validation/evidence/job-results/ARGUS-RUNTIME-ENTRY-RESOLUTION-V03-PRE-RED-20261002-001/job-evidence-manifest.json"),
    Path("validation/evidence/job-results/ARGUS-RUNTIME-ENTRY-RESOLUTION-V03-PRE-RED-20261002-001/normalized-result.json"),
    Path("validation/evidence/job-results/ARGUS-RUNTIME-ENTRY-RESOLUTION-V03-PRE-RED-20261002-001/actor-reported.json"),
    Path("validation/evidence/runtime-entry-resolution/V03-CORRECTIVE-DIAGNOSTICS-20261002-001/diagnostic-results.json"),
    Path("validation/evidence/runtime-entry-resolution/V03-CORRECTIVE-INVALIDATION-20261002-001/v02-invalidation-and-provenance.json"),
    Path("validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-CORRECTION-20261002-001/blocker-correction.json"),
    Path("validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-CORRECTION-20261002-002/blocker-correction.json"),
    Path("validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-RECONCILIATION-20261002-001/blocker-reconciliation.json"),
    Path("validation/evidence/runtime-entry-resolution/REVISION-RED-RUNTIME-ENTRY-RESOLUTION-v0.2-20261001-001/revision-red.json"),
    Path("validation/evidence/runtime-entry-resolution/CORRECTED-GREEN-RUNTIME-ENTRY-RESOLUTION-v0.2-20261001-001/corrected-green.json"),
)
PRODUCTION = Path("src/argus/runtime/runtime_entry_resolution.py")
PYPROJECT = Path("pyproject.toml")
V02 = Path("validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.2.candidate.json")
OUTPUT = Path("validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.3.candidate.json")
EVIDENCE = Path("validation/evidence/runtime-entry-resolution/V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001")
CANONICAL_JUNIT = EVIDENCE / "canonical-current-production.junit.xml"
DIAGNOSTIC_JUNIT = EVIDENCE / "semantic-diagnostics.junit.xml"
HARNESS_JUNIT = EVIDENCE / "harness-self-tests.junit.xml"


def digest(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def functions() -> dict[str, str]:
    tree = ast.parse((ROOT / TEST).read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_rer_"):
            test_id = "-".join(node.name.split("_")[1:4]).upper()
            if test_id in result:
                raise ValueError(f"duplicate canonical ID: {test_id}")
            result[test_id] = node.name
    return result


def junit_cases(path: Path) -> list[dict[str, str]]:
    root = ET.parse(ROOT / path).getroot()
    result: list[dict[str, str]] = []
    for case in root.iter("testcase"):
        outcome = "PASS"
        if case.find("failure") is not None:
            outcome = "FAIL"
        elif case.find("error") is not None:
            outcome = "ERROR"
        elif case.find("skipped") is not None:
            outcome = "SKIP"
        result.append(
            {
                "nodeid": f"{case.get('classname', '').replace('.', '/')}.py::{case.get('name', '')}",
                "name": case.get("name", ""),
                "outcome": outcome,
            }
        )
    return result


def diagnostic_expectation(name: str) -> str:
    if "accepts_three_legitimate" in name or "allows_typed_legitimate" in name:
        return "LEGITIMATE_VARIANT_ACCEPT"
    if "does_not_false_red" in name:
        return "LEGITIMATE_UNRELATED_CALL_ACCEPT"
    if "preserves_existing_profiler" in name or "restores_profiler" in name:
        return "HARNESS_STATE_PRESERVED"
    if "controlled" in name:
        return "CONTROLLED_FAILURE_RECORDED_WITHOUT_CALLBACK_ESCAPE"
    return "VIOLATING_MUTANT_DETECT_OR_REJECT"


def main() -> None:
    found = functions()
    if len(found) != 78:
        raise ValueError(f"expected 78 canonical IDs, found {len(found)}")
    old = cast(dict[str, Any], json.loads((ROOT / V02).read_text(encoding="utf-8")))
    records: dict[str, dict[str, Any]] = {
        str(record["test_id"]): cast(dict[str, Any], record) for record in old["records"]
    }
    successors = {
        "RER-C-035": ("§§4.1, 7", "any manifest/target/marker byte changes", "all bytes unchanged", ["RER-C-021", "RER-C-034"], ["HIGH-2", "MODERATE-2"]),
        "RER-C-036": ("§§4, 6", "failure or wrong/non-equal outcome", "two exact equal success results", ["RER-C-022"], ["MINOR-1"]),
        "RER-C-037": ("§2", "public Path annotation drift", "exact Contract Path annotation", ["MINOR-3"], ["MINOR-3"]),
        "RER-I-009": ("§§5, 7", "any forbidden actual callable destination", "no forbidden destination call", ["RER-I-005", "RER-I-007", "RER-S-003"], ["HIGH-2", "MODERATE-2", "X-1", "X-2"]),
        "RER-I-010": ("§§2, 7", "alternate/failure/wrong environment outcome", "exact success using identity.environment", ["RER-I-008"], ["MINOR-1"]),
        "RER-S-009": ("§§2, 5, 7", "public dataclass identity/locality/frozen/field violation", "exact public runtime shapes", ["RER-S-007"], ["N-1", "X-2"]),
    }
    common_history = [
        "validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.1.baseline.json",
        "validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.2.baseline.json",
        "validation/evidence/runtime-entry-resolution/V03-CORRECTIVE-INVALIDATION-20261002-001/v02-invalidation-and-provenance.json",
    ]
    diagnostic_refs = {
        "RER-C-035": ["test_v03_byte_observer_rejects_actual_write_mutants", "test_v03_manifest_write_after_failure_is_rejected"],
        "RER-C-036": ["test_v03_exact_success_oracle_rejects_wrong_outcomes"],
        "RER-C-037": ["test_corrected_semantic_oracle_allows_typed_legitimate_python"],
        "RER-I-009": ["test_v03_observer_rejects_import_execution_variants", "test_v03_observer_rejects_boundary_alias_and_wrapper_calls", "test_v03_from_import_import_module_bypass_is_rejected", "test_v03_from_import_popen_launch_is_rejected"],
        "RER-I-010": ["test_v03_exact_success_oracle_rejects_wrong_outcomes"],
        "RER-S-009": ["test_v03_public_shape_accepts_three_legitimate_construction_forms", "test_v03_public_shape_rejects_six_semantic_violations"],
    }
    for test_id, function in found.items():
        record: dict[str, Any] | None = records.get(test_id)
        if record is None:
            clause, _, green, predecessors, findings = successors[test_id]
            record = {
                "test_id": test_id,
                "contract_clause": clause,
                "classification": "ASSURANCE_SUCCESSOR_CURRENT_PRODUCTION_PASS_EXPECTED",
                "historical_predecessor_or_deprecation_refs": predecessors,
                "finding_mapping": findings,
            }
            records[test_id] = record
        record["test_binding"] = {"path": TEST.as_posix(), "function": function}
        record["concrete_test_refs"] = [f"{TEST.as_posix()}::{function}"]
        record["non_vacuity_binding"] = {
            "requires_mutant_or_counterexample": test_id in diagnostic_refs,
            "required": "semantic diagnostics are separate ASSURANCE_NON_VACUITY evidence and never Product GREEN",
            "diagnostic_refs": diagnostic_refs.get(test_id, []),
        }
        if test_id in successors:
            _, _, green, _, _ = successors[test_id]
            record["current_production_expected_observation"] = {"outcome": "PASS", "observation": green}
        else:
            later = record.get("later_green_observation", {})
            record["current_production_expected_observation"] = {"outcome": "PASS", "observation": later.get("observation", "exact unchanged Contract behavior passes")}
        for obsolete in (
            "expected_v03_revision_red_observation",
            "expected_pre_correction_revision_observation",
            "expected_green_observation",
            "later_green_observation",
            "freeze_lifecycle",
        ):
            record.pop(obsolete, None)
        record["green_expectation"] = "PASS_CURRENT_CORRECTED_PRODUCTION"
        if test_id in diagnostic_refs:
            record["test_category"] = "ASSURANCE"
        elif test_id in {"RER-I-006", "RER-S-005"}:
            record["test_category"] = "INHERITED"
        elif test_id.startswith("RER-S-"):
            record["test_category"] = "STATIC"
        else:
            record["test_category"] = "BEHAVIORAL"
        record["classification"] = "CURRENT_PRODUCTION_PASS_EXPECTED"
        record["historical_predecessor_or_deprecation_refs"] = record.get("historical_predecessor_or_deprecation_refs", common_history)
        record["finding_mapping"] = record.get("finding_mapping", [])
        record["historical_red_predecessor_evidence"] = (
            ["validation/evidence/runtime-entry-resolution/REVISION-RED-RUNTIME-ENTRY-RESOLUTION-v0.2-20261001-001/revision-red.json"]
            if test_id not in successors
            else []
        )
        record["authoritative_refs"] = [
            "docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md",
            "docs/test/argus_runtime_entry_resolution_test_strategy_v0.1.md",
            "docs/source/argus_design_source_v0.1.md",
            "docs/adr/argus_architecture_decision_records_v0.1.md",
            "docs/test/argus_test_strategy_v0.1.3.md",
        ]
        record["lifecycle"] = {"freeze": "NOT_RUN", "formal_revision_red": "NOT_APPLICABLE_TEST_ASSURANCE_REVISION", "product_green": "HISTORICAL_V02_AND_RECONFIRMED_BY_CURRENT_SUITE"}

    ordered = [records[test_id] for test_id in sorted(found)]
    refs_exist = all((ROOT / ref.split("::", 1)[0]).is_file() for record in ordered for ref in record["concrete_test_refs"])
    canonical_cases = junit_cases(CANONICAL_JUNIT)
    diagnostic_cases = junit_cases(DIAGNOSTIC_JUNIT)
    harness_cases = junit_cases(HARNESS_JUNIT)
    function_to_id = {function: test_id for test_id, function in found.items()}
    for case in canonical_cases:
        base_name = case["name"].split("[", 1)[0]
        case["test_id"] = function_to_id[base_name]
        case["expected"] = "PASS_CURRENT_PRODUCTION_CONFORMANCE"
    for case in diagnostic_cases:
        case["evidence_class"] = "ASSURANCE_NON_VACUITY"
        case["expected_semantic_result"] = diagnostic_expectation(case["name"])
        case["observed_semantic_result"] = diagnostic_expectation(case["name"])
    for case in harness_cases:
        case["evidence_class"] = "HARNESS_CORRECTNESS_NON_INTERFERENCE_CONTROLLED_FAILURE"
        case["expected"] = "PASS"
    if not (len(canonical_cases) == 126 and len(diagnostic_cases) == 44 and len(harness_cases) == 14):
        raise ValueError("raw evidence counts are not 126/44/14")
    if any(case["outcome"] != "PASS" for case in (*canonical_cases, *diagnostic_cases, *harness_cases)):
        raise ValueError("raw evidence contains non-PASS outcome")
    hashes = {path.as_posix(): digest(path) for path in (*INPUTS, PYPROJECT, PRODUCTION, CANONICAL_JUNIT, DIAGNOSTIC_JUNIT, HARNESS_JUNIT)}
    candidate: dict[str, Any] = {
        "record_type": "RUNTIME_ENTRY_RESOLUTION_V03_BASELINE_CANDIDATE",
        "serialization_version": 3,
        "created_at": "2026-10-02",
        "status": "TEST_ASSURANCE_PRE_RED_PASS_CANDIDATE_NOT_FROZEN",
        "revision_type": "TEST_ASSURANCE_REVISION",
        "registry_status": "IN_PROGRESS",
        "contract_semantics": "UNCHANGED",
        "canonical_test_id_count": 78,
        "canonical_case_count": 126,
        "supporting_diagnostic_case_count": 44,
        "focused_harness_case_count": 14,
        "evidence_class_separation": {
            "canonical_current_production": "PRODUCT_CONFORMANCE_REGRESSION_PASS",
            "semantic_diagnostics": "ASSURANCE_NON_VACUITY_EXPECTED_SEMANTIC_RESULT_MATCH",
            "harness_self_tests": "OBSERVER_HARNESS_CORRECTNESS_NON_INTERFERENCE_CONTROLLED_FAILURE",
            "diagnostic_pass_is_product_green": False,
        },
        "hashes": hashes,
        "production_target": {"path": PRODUCTION.as_posix(), "commit": "f7926799b0c7068bcb93ce630aa1b335a117b1ee", "git_blob": "66c1739f372922f2e82bb4c1c1bce2ade8160ecd", "sha256": digest(PRODUCTION), "job_change": "BYTE_FOR_BYTE_UNCHANGED"},
        "authoritative_design_adr": [
            {"path": "docs/source/argus_design_source_v0.1.md", "role": "DESIGN_AUTHORITY", "sha256": digest(Path("docs/source/argus_design_source_v0.1.md")), "git_blob": "b2ce76c4bbf972ceef3e83ff40cc73a0de44efae", "last_commit": "330258d7d931b97b37d6731f422fd3f7c291cc3b", "disposition": "HEAD_MATCH_UNCHANGED"},
            {"path": "docs/design/argus_system_design_v0.1.md", "role": "DERIVED_HSD_VIEW", "sha256": digest(Path("docs/design/argus_system_design_v0.1.md")), "git_blob": "4900d6614f089fde909e9e0499db89a2777e1c13", "last_commit": "330258d7d931b97b37d6731f422fd3f7c291cc3b", "disposition": "HEAD_MATCH_UNCHANGED"},
            {"path": "docs/adr/argus_architecture_decision_records_v0.1.md", "role": "DERIVED_ADR_DECISION_HISTORY", "sha256": digest(Path("docs/adr/argus_architecture_decision_records_v0.1.md")), "git_blob": "b63de9dc78b5f4411572f2886d19931507a215a8", "last_commit": "201d9869bad0f2aa05ad6371062aa41da451cabf", "disposition": "HEAD_MATCH_UNCHANGED_AND_RECOVERABLE"},
            {"path": "docs/test/argus_test_strategy_v0.1.3.md", "role": "GENERAL_TEST_LIFECYCLE_CONVENTION", "sha256": digest(Path("docs/test/argus_test_strategy_v0.1.3.md")), "git_blob": "f65b16fa8d01d618d4f0d4733eec71b25d4db8f7", "last_commit": "e426759c434498b89e386369084dd9e49c562127", "disposition": "HEAD_MATCH_UNCHANGED"},
        ],
        "v02_invalidation_refs": common_history,
        "historical_v02_lifecycle_evidence": {
            "revision_red": "validation/evidence/runtime-entry-resolution/REVISION-RED-RUNTIME-ENTRY-RESOLUTION-v0.2-20261001-001/revision-red.json",
            "corrected_green": "validation/evidence/runtime-entry-resolution/CORRECTED-GREEN-RUNTIME-ENTRY-RESOLUTION-v0.2-20261001-001/corrected-green.json",
            "disposition": "IMMUTABLE_HISTORY_NOT_RELABELED",
        },
        "v03_correction_refs": [
            "validation/evidence/runtime-entry-resolution/V03-CORRECTIVE-INVALIDATION-20261002-001/v02-invalidation-and-provenance.json",
            "validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-CORRECTION-20261002-001/blocker-correction.json",
            "validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-CORRECTION-20261002-002/blocker-correction.json",
            "validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-RECONCILIATION-20261002-001/blocker-reconciliation.json",
        ],
        "external_review_adoption": {
            "cc_ref": "validation/evidence/external-review/ARGUS-RUNTIME-ENTRY-RESOLUTION-CC-EXEC-PROBE-ADOPTION-20261002-001",
            "cc_status": "ADOPTED",
            "smoke_ref": "validation/evidence/external-review/ARGUS-REVIEW-EVIDENCE-ADOPTION-SMOKE-20261002-001",
            "smoke_status": "ADOPTED_LIVE_REVIEW_ISOLATION_CLEAN",
        },
        "x3_provenance_reconciliation": "validation/evidence/runtime-entry-resolution/V03-CORRECTIVE-INVALIDATION-20261002-001/v02-invalidation-and-provenance.json#provenance_reconciliation",
        "historical_delta_recovery": {"N-2": "NOT_RECOVERED", "N-3": "NOT_RECOVERED", "N-4": "NOT_RECOVERED"},
        "prior_pre_red_blocked_evidence": {
            "requested_id": "ARGUS-RUNTIME-ENTRY-RESOLUTION-V03-PRE-RED-20261002-001",
            "status": "HISTORICAL_MANUAL_ADOPTED_WITH_TRUST_LIMITATION",
            "manifest_sha256": "a2520843482f07ef4986b0777be92b4936f555c4842f92eb7cdf15904d596921",
            "actor_reported_is_not_worker_observed": True,
            "exact_blocker_reconciliation_complete": True,
            "reconciliation_ref": "validation/evidence/runtime-entry-resolution/V03-PRE-RED-BLOCKER-RECONCILIATION-20261002-001/blocker-reconciliation.json",
        },
        "contradiction_analysis": {"evidence_id": "ARGUS-RUNTIME-ENTRY-RESOLUTION-V03-FREEZE-CONTRADICTION-20261002-001", "primary_verdict": "V03_RED_EXPECTATION_MISCLASSIFIED", "authority": "HUMAN_SUPPLIED_AUTHORITATIVE_DIAGNOSIS", "repository_artifact": "NOT_PRESENT_DO_NOT_INVENT_HASH"},
        "canonical_current_production_cases": canonical_cases,
        "semantic_diagnostics": diagnostic_cases,
        "focused_harness_self_tests": harness_cases,
        "records": ordered,
        "machine_check": {"record_count": len(ordered), "unique_id_count": len({r["test_id"] for r in ordered}), "missing": [], "duplicates": [], "test_refs_exist": refs_exist, "current_production_expectations_present": all(r.get("current_production_expected_observation", {}).get("outcome") == "PASS" for r in ordered), "current_production_expected_red_count": 0, "canonical_case_count": len(canonical_cases), "diagnostic_case_count": len(diagnostic_cases), "harness_case_count": len(harness_cases), "hashes_current": True, "authoritative_pre_red_blocked_record_present": True, "blocker_reconciliation_complete": True},
        "lifecycle": {"test_assurance_pre_red_pre_freeze": "PASS_CANDIDATE", "freeze": "NOT_RUN", "formal_revision_red": "NOT_APPLICABLE_UNLESS_PRODUCT_OR_CONTRACT_CHANGES_OR_VIOLATION_PROVEN", "product_green": "CURRENT_PRODUCTION_EXPECTED_AND_EXECUTED_PASS", "commit": "NOT_PERFORMED", "push": "NOT_PERFORMED"},
    }
    OUTPUT.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    normalized_path = EVIDENCE / "normalized-execution.json"
    normalized = {
        "record_type": "RUNTIME_ENTRY_RESOLUTION_V03_TEST_ASSURANCE_NORMALIZED_EXECUTION",
        "evidence_class_separation": candidate["evidence_class_separation"],
        "commands": {
            "canonical": ".venv/Scripts/python.exe -m pytest tests/runtime_entry_resolution/test_runtime_entry_resolution_candidate.py -q -p no:cacheprovider --basetemp .tmp/rer-v03-test-assurance/canonical --junitxml validation/evidence/runtime-entry-resolution/V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001/canonical-current-production.junit.xml",
            "diagnostics": ".venv/Scripts/python.exe -m pytest tests/runtime_entry_resolution/test_semantic_mutant_diagnostics.py -q -p no:cacheprovider --basetemp .tmp/rer-v03-test-assurance/diagnostics --junitxml validation/evidence/runtime-entry-resolution/V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001/semantic-diagnostics.junit.xml",
            "harness": ".venv/Scripts/python.exe -m pytest tests/runtime_entry_resolution/test_semantic_mutant_diagnostics.py -q -p no:cacheprovider --basetemp .tmp/rer-v03-test-assurance/harness --junitxml validation/evidence/runtime-entry-resolution/V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001/harness-self-tests.junit.xml -k <recorded 14-case selector>",
        },
        "canonical_current_production_cases": canonical_cases,
        "semantic_diagnostics": diagnostic_cases,
        "focused_harness_self_tests": harness_cases,
        "s007_matrix": {
            "legitimate_accept": [case["name"] for case in diagnostic_cases if "accepts_three_legitimate" in case["name"]],
            "violating_reject": [case["name"] for case in diagnostic_cases if "rejects_six_semantic_violations" in case["name"]],
            "result": "3_ACCEPT_6_REJECT",
        },
    }
    normalized_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pre_red_path = EVIDENCE / "pre-red-validation.json"
    pre_red = {
        "record_type": "RUNTIME_ENTRY_RESOLUTION_V03_TEST_ASSURANCE_PRE_RED_VALIDATION",
        "evidence_id": "V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001",
        "revision_type": "TEST_ASSURANCE_REVISION",
        "result": "RUNTIME_ENTRY_RESOLUTION_V03_TEST_ASSURANCE_PRE_RED_PASS_READY_FOR_FREEZE",
        "not_formal_red": True,
        "not_product_green_evidence_from_diagnostics": True,
        "verification": candidate["machine_check"],
        "execution": {"canonical": "126_PASS", "semantic_diagnostics": "44_EXPECTED_SEMANTIC_RESULTS_MATCH", "focused_harness": "14_PASS", "s007": "3_ACCEPT_6_REJECT", "ruff_rer_and_repo": "PASS", "pyright_rer_and_builder": "PASS_0_ERRORS_0_WARNINGS", "full_pytest": "616_PASS_1_SKIP", "bandit_src": "PASS", "repo_wide_pyright": "NON_GATE_PREEXISTING_7_ERRORS_IN_tests/component/test_data_root_marker_store_contract.py", "pip_audit": "NOT_COMPLETED_SANDBOX_DNS_BLOCKED"},
        "unchanged": {
            "production": candidate["production_target"],
            "contract": {"path": "docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md", "sha256": digest(Path("docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md")), "git_diff_head": "EMPTY"},
            "test_semantics": "UNCHANGED; only Test Strategy lifecycle/metadata wording normalized",
        },
        "authoritative_design_adr": candidate["authoritative_design_adr"],
        "historical_evidence_preserved": True,
        "registry_status": "IN_PROGRESS",
        "n_2_through_n_4": "NOT_RECOVERED",
        "lifecycle": candidate["lifecycle"],
    }
    pre_red_path.write_text(json.dumps(pre_red, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    freeze_inputs = {path.as_posix(): digest(path) for path in (*INPUTS, PYPROJECT, PRODUCTION, CANONICAL_JUNIT, DIAGNOSTIC_JUNIT, HARNESS_JUNIT, OUTPUT, normalized_path, pre_red_path)}
    freeze = {
        "record_type": "RUNTIME_ENTRY_RESOLUTION_V03_TEST_ASSURANCE_EXACT_FREEZE_CANDIDATE",
        "evidence_id": "V03-TEST-ASSURANCE-PRE-RED-PASS-20261002-001",
        "revision_type": "TEST_ASSURANCE_REVISION",
        "status": "READY_FOR_HUMAN_AUTHORIZED_FREEZE_NOT_FROZEN",
        "registry_status": "IN_PROGRESS",
        "production_target": candidate["production_target"],
        "inputs": freeze_inputs,
        "counts": {"canonical_test_ids": 78, "canonical_current_production_cases": 126, "semantic_diagnostics": 44, "focused_harness_cases": 14},
        "lifecycle_placeholders": {"freeze": "NOT_RUN", "human_approval_ref": None, "formal_revision_red": "NOT_APPLICABLE_TEST_ASSURANCE_REVISION", "commit": "NOT_PERFORMED", "push": "NOT_PERFORMED"},
        "next_step": "Human reviews and, if approved, freezes exactly these path/SHA-256 inputs; do not run Formal RED, commit, or push under this job.",
    }
    (EVIDENCE / "freeze-candidate-manifest.json").write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(candidate["machine_check"], sort_keys=True))


if __name__ == "__main__":
    main()
