from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from context_builder import build_section_contexts
from governance import GovernanceBaseline, GovernanceChange, TermClass, TermRule, apply_change
from planning_schema import HSD_SECTIONS, CoverageAssignment, ExactValueContext
from planning_v2 import (
    PlanningApproval,
    authorize_planning_artifact,
    build_artifact,
    validate_contexts,
)
from sdd_parser import parse_sdd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]


def real_contexts():  # type: ignore[no-untyped-def]
    text = (REPO / "docs/model/argus_structured_design_data_v0.1.md").read_text("utf-8")
    return build_section_contexts(parse_sdd(text))


def test_poc0_regression_remains_green() -> None:
    report = json.loads((REPO / "validation/reports/argus-p-0085-v1/poc0/validation-report.json").read_text("utf-8"))
    assert report["poc0"] == "PASS"
    assert report["summary"]["missed_findings"] == 0


def test_parser_failure_blocks_planning_validator() -> None:
    findings = validate_contexts(real_contexts(), parser_unrecognized=1)
    assert "PARSER_UNRECOGNIZED" in {finding.code for finding in findings}


def test_all_contexts_match_schema_and_skeleton() -> None:
    contexts = real_contexts()
    assert len(contexts) == len(HSD_SECTIONS) == 39
    assert [(c.section_id, c.title) for c in contexts] == list(HSD_SECTIONS)
    assert all(c.depth in {1, 2} for c in contexts)


def test_coverage_id_duplicate_is_detected() -> None:
    contexts = list(real_contexts())
    donor = contexts[0].coverage_units[0]
    contexts[1] = replace(contexts[1], coverage_units=contexts[1].coverage_units + (donor,))
    assert "COVERAGE_ID_DUPLICATE" in {f.code for f in validate_contexts(tuple(contexts))}


def test_missing_source_locator_is_detected() -> None:
    contexts = list(real_contexts())
    unit = contexts[0].coverage_units[0]
    contexts[0] = replace(contexts[0], coverage_units=(replace(unit, source_locator=""),))
    assert "SOURCE_LOCATOR_MISSING" in {f.code for f in validate_contexts(tuple(contexts))}


@pytest.mark.parametrize(("field", "code"), [("problems", "EMPTY_PROBLEMS"), ("purposes", "EMPTY_PURPOSES"), ("coverage_units", "EMPTY_COVERAGE")])
def test_empty_required_collection_is_detected(field: str, code: str) -> None:
    context = replace(real_contexts()[0], **{field: ()})
    assert code in {f.code for f in validate_contexts((context,))}


def test_unknown_primary_owner_is_detected() -> None:
    context = replace(real_contexts()[0], primary_owner="")
    assert "OWNER_UNKNOWN" in {f.code for f in validate_contexts((context,))}


def test_duplicate_primary_owner_assignment_is_detected() -> None:
    context = real_contexts()[0]
    assignment = replace(context.coverage_units[0], primary_owner="other")
    changed = replace(context, coverage_units=(assignment,))
    assert "DUPLICATE_PRIMARY_OWNER" in {f.code for f in validate_contexts((changed,))}


def test_unresolved_cross_reference_is_detected() -> None:
    context = replace(real_contexts()[0], cross_references=("404",))
    assert "UNRESOLVED_CROSS_REFERENCE" in {f.code for f in validate_contexts((context,))}


def test_exact_value_contract() -> None:
    with pytest.raises(ValueError):
        ExactValueContext("x", "17:30", ("17時30分",), "通知", ("通知",), "SDD §8.7", "C-1")


def test_exact_value_definition_is_available_to_japanese_gate() -> None:
    value = ExactValueContext("x", "17:30", ("17:30", "17時30分"), "通知", ("通知",), "SDD §8.7", "C-1")
    assert "17時30分" in value.accepted


def test_governance_change_requires_human_approval() -> None:
    baseline = GovernanceBaseline("1", (TermRule("API", TermClass.ALWAYS_ALLOWED),))
    change = GovernanceChange("1", "2", "", (TermRule("Data", TermClass.FORBIDDEN),), "", "")
    with pytest.raises(PermissionError):
        apply_change(baseline, change)


def test_real_sdd_generates_planning_artifact() -> None:
    path = REPO / "docs/model/argus_structured_design_data_v0.1.md"
    artifact = build_artifact(path.read_text("utf-8"), "sha")
    assert artifact["approval_status"] == "PENDING"
    assert artifact["stop"] == "STOP Human Review"
    assert artifact["summary"]["section_contexts"] == 39


def test_v2_approval_rejects_absent_and_stale_approval() -> None:
    path = REPO / "docs/model/argus_structured_design_data_v0.1.md"
    artifact = build_artifact(path.read_text("utf-8"), "sha")
    with pytest.raises(PermissionError):
        authorize_planning_artifact(artifact, PlanningApproval(artifact["artifact_id"], artifact["planning_hash"], "", "", "PENDING", "sha"), expected_sdd_sha256="sha")
    with pytest.raises(PermissionError):
        authorize_planning_artifact(artifact, PlanningApproval(artifact["artifact_id"], "stale", "Human", "2026-09-24T00:00:00+09:00", "APPROVED", "sha"), expected_sdd_sha256="sha")


def test_all_real_sections_have_machine_valid_identity() -> None:
    assert all(c.section_id and c.title and c.primary_owner for c in real_contexts())


def test_coverage_assignment_is_python_owned_and_single_section() -> None:
    assignments = [item for context in real_contexts() for item in context.coverage_units]
    assert all(isinstance(item, CoverageAssignment) for item in assignments)
    assert len({item.coverage_id for item in assignments}) == len(assignments)
