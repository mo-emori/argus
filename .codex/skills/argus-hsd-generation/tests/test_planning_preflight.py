from __future__ import annotations

from planning_preflight import evaluate_approved_planning, evaluate_context


def planning() -> dict[str, object]:
    return {
        "artifact_id": "p",
        "planning_hash": "hash",
        "source_sdd_sha256": "sdd",
        "findings": [{"severity": "REVIEW_REQUIRED", "code": "INSPECTION"}],
        "coverage_reconciliation": {"missing": 0},
    }


def approval() -> dict[str, str]:
    return {
        "artifact_id": "p",
        "planning_hash": "hash",
        "sdd_sha256": "sdd",
        "status": "APPROVED",
        "approved_by": "Human",
    }


def test_human_bound_approval_makes_retained_review_markers_nonblocking() -> None:
    result = evaluate_approved_planning(planning(), approval(), expected_sdd_sha256="sdd")
    assert result["writer_preflight"] == "PASS"
    assert result["retained_review_markers"]
    assert result["planning_content_mutated"] is False


def test_ai_or_hash_mismatch_remains_fail_closed() -> None:
    bad = approval() | {"approved_by": "Codex", "planning_hash": "stale"}
    result = evaluate_approved_planning(planning(), bad, expected_sdd_sha256="sdd")
    assert result["writer_preflight"] == "FAIL"
    assert "approval actor is not Human" in result["errors"]
    assert "planning hash mismatch" in result["errors"]


def test_context_keeps_markers_but_is_effectively_ready() -> None:
    context = {
        "context": {
            "section_id": "1.2",
            "planning_status": "REVIEW_REQUIRED",
            "unresolved": [],
            "semantic_candidates": [{"disposition": "REVIEW_REQUIRED"}],
            "coverage_units": [{"assignment_status": "REVIEW_REQUIRED"}],
        }
    }
    result = evaluate_context(context, evaluate_approved_planning(planning(), approval(), expected_sdd_sha256="sdd"))
    assert result["effective_planning_status"] == "READY"
    assert result["retained_semantic_review_markers"] == 1
    assert result["retained_assignment_review_markers"] == 1


def test_section_specific_unresolved_item_stays_blocking() -> None:
    context = {"section_id": "x", "planning_status": "REVIEW_REQUIRED", "unresolved": ["parse failure"]}
    result = evaluate_context(context, evaluate_approved_planning(planning(), approval(), expected_sdd_sha256="sdd"))
    assert result["writer_preflight"] == "FAIL"
    assert result["effective_planning_status"] == "REVIEW_REQUIRED"
