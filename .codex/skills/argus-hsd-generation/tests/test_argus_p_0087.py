from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from context_builder import build_section_contexts
from planning_v2 import PlanningApproval, authorize_planning_artifact, build_artifact
from render_planning import render
from sdd_parser import parse_sdd

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
SDD = REPO / "docs/model/argus_structured_design_data_v0.1.md"
BASELINE = REPO / "docs/review/argus_system_design_coverage_map_v0.1.6.md"


def artifact() -> dict[str, object]:
    text = SDD.read_text("utf-8")
    return build_artifact(text, hashlib.sha256(text.encode()).hexdigest(), BASELINE.read_text("utf-8"))


def test_api_os_sha_are_not_states() -> None:
    parsed = parse_sdd("## 3.1 x\n**課題：** API OS SHA FOOBAR INIT RUNNING RESUMING END\n**目的：** x\n")
    context = next(item for item in build_section_contexts(parsed) if item.coverage_units)
    assert {"API", "OS", "SHA"}.isdisjoint(context.states)
    assert {"INIT", "RUNNING", "RESUMING", "END"}.issubset(context.states)


def test_unknown_candidate_is_review_required() -> None:
    parsed = parse_sdd("## 3.1 x\n**課題：** FOOBAR\n**目的：** x\n")
    context = next(item for item in build_section_contexts(parsed) if item.coverage_units)
    candidate = next(item for item in context.semantic_candidates if item.value == "FOOBAR")
    assert candidate.candidate_type == "unknown_candidate"
    assert candidate.disposition.value == "REVIEW_REQUIRED"


def test_reason_and_premise_signals_are_present() -> None:
    result = artifact()
    summary = result["summary"]
    codes = {item["code"] for item in result["findings"]}
    assert summary["design_reason_sections"] > 0
    assert summary["premise_sections"] > 0
    assert {"DESIGN_REASONS_SPARSE", "PREMISES_SPARSE"}.issubset(codes)


def test_all_legacy_coverage_units_are_reconciled() -> None:
    reconciliation = artifact()["coverage_reconciliation"]
    assert reconciliation["baseline_units"] == 1000
    assert len(reconciliation["entries"]) == 1000
    assert reconciliation["missing"] == 0


def test_missing_reconciliation_blocks_approval() -> None:
    result = artifact()
    result["coverage_reconciliation"]["missing"] = 1
    result["findings"] = []
    approval = PlanningApproval(result["artifact_id"], result["planning_hash"], "Human", "2026-09-24T00:00:00+09:00", "APPROVED", result["source_sdd_sha256"])
    with pytest.raises(PermissionError, match="MISSING"):
        authorize_planning_artifact(result, approval, expected_sdd_sha256=result["source_sdd_sha256"])


def test_assignment_review_is_visible_in_json_and_markdown() -> None:
    result = artifact()
    assert result["summary"]["assignment_review_required"] > 0
    assert "Assignment REVIEW_REQUIRED" in render(result)


def test_poc0_and_invariants_regression_evidence_remains_green() -> None:
    report = json.loads((REPO / "validation/reports/argus-p-0085-v1/poc0/validation-report.json").read_text("utf-8"))
    assert report["poc0"] == "PASS"
    design = (ROOT / "DESIGN.md").read_text("utf-8")
    assert all(f"INV-{number:02d}" in design for number in range(1, 8))


def test_deterministic_regeneration() -> None:
    assert json.dumps(artifact(), ensure_ascii=False, sort_keys=True) == json.dumps(artifact(), ensure_ascii=False, sort_keys=True)
