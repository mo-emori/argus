from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_approved_planning(
    planning: dict[str, Any], approval: dict[str, Any], *, expected_sdd_sha256: str
) -> dict[str, Any]:
    """Return effective readiness without rewriting immutable planning findings.

    A Planning Artifact is generated in PENDING state.  Human authorization is a
    separately bound artifact so that the approved planning hash stays stable.
    REVIEW_REQUIRED inspection markers remain visible and are not converted into
    design decisions by this function.
    """
    errors: list[str] = []
    if approval.get("status") != "APPROVED":
        errors.append("approval status is not APPROVED")
    if approval.get("approved_by") != "Human":
        errors.append("approval actor is not Human")
    if approval.get("artifact_id") != planning.get("artifact_id"):
        errors.append("artifact id mismatch")
    if approval.get("planning_hash") != planning.get("planning_hash"):
        errors.append("planning hash mismatch")
    if approval.get("sdd_sha256") != expected_sdd_sha256:
        errors.append("approval SDD hash mismatch")
    if planning.get("source_sdd_sha256") != expected_sdd_sha256:
        errors.append("planning SDD hash mismatch")
    if any(item.get("severity") == "FAIL" for item in planning.get("findings", [])):
        errors.append("planning contains FAIL finding")
    if planning.get("coverage_reconciliation", {}).get("missing", 0):
        errors.append("coverage reconciliation contains MISSING")

    retained = [
        item for item in planning.get("findings", [])
        if item.get("severity") == "REVIEW_REQUIRED"
    ]
    return {
        "effective_approval_status": "APPROVED" if not errors else "BLOCKED",
        "writer_preflight": "PASS" if not errors else "FAIL",
        "errors": errors,
        "retained_review_markers": retained,
        "review_markers_are_inspection_metadata": True,
        "planning_content_mutated": False,
    }


def evaluate_context(
    context: dict[str, Any], planning_result: dict[str, Any]
) -> dict[str, Any]:
    body = context.get("context", context)
    semantic = sum(
        item.get("disposition") == "REVIEW_REQUIRED"
        for item in body.get("semantic_candidates", [])
    )
    assignments = sum(
        item.get("assignment_status") == "REVIEW_REQUIRED"
        for item in body.get("coverage_units", [])
    )
    unresolved = list(body.get("unresolved", []))
    blockers = list(planning_result.get("errors", []))
    if unresolved:
        blockers.append("section has unresolved parser items")
    return {
        "section_id": body.get("section_id"),
        "stored_planning_status": body.get("planning_status"),
        "effective_planning_status": "READY" if not blockers else "REVIEW_REQUIRED",
        "writer_preflight": "PASS" if not blockers else "FAIL",
        "section_specific_blockers": blockers,
        "retained_semantic_review_markers": semantic,
        "retained_assignment_review_markers": assignments,
        "context_content_mutated": False,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("planning", type=Path)
    parser.add_argument("approval", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("contexts", nargs="+", type=Path)
    args = parser.parse_args()

    planning = json.loads(args.planning.read_text("utf-8"))
    approval = json.loads(args.approval.read_text("utf-8"))
    result = {
        "planning": evaluate_approved_planning(
            planning, approval, expected_sdd_sha256=approval["sdd_sha256"]
        ),
        "contexts": [],
        "provenance": {
            "planning_path": str(args.planning).replace("\\", "/"),
            "planning_sha256": sha256_file(args.planning),
            "approval_path": str(args.approval).replace("\\", "/"),
            "approval_sha256": sha256_file(args.approval),
        },
    }
    result["contexts"] = [
        evaluate_context(json.loads(path.read_text("utf-8")), result["planning"])
        for path in args.contexts
    ]
    result["decision"] = (
        "PASS" if result["planning"]["writer_preflight"] == "PASS"
        and all(item["writer_preflight"] == "PASS" for item in result["contexts"])
        else "FAIL"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
