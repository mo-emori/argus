from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from context_builder import build_section_contexts
from contracts import canonical_digest
from coverage_reconciliation import reconcile_coverage
from planning_schema import SectionContext
from sdd_parser import parse_sdd


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    section_id: str
    detail: str


@dataclass(frozen=True)
class PlanningApproval:
    artifact_id: str
    planning_hash: str
    approved_by: str
    approved_at: str
    status: str
    sdd_sha256: str


@dataclass(frozen=True)
class WriterPhaseAuthorization:
    artifact_id: str
    planning_hash: str
    approved_by: str
    approved_at: str
    sdd_sha256: str


def authorize_planning_artifact(
    artifact: dict[str, Any], approval: PlanningApproval, *, expected_sdd_sha256: str
) -> WriterPhaseAuthorization:
    if artifact.get("approval_status") != "PENDING":
        raise PermissionError("planning artifact state is invalid")
    if any(item.get("severity") == "FAIL" for item in artifact.get("findings", [])):
        raise PermissionError("planning artifact has blocking findings")
    if artifact.get("coverage_reconciliation", {}).get("missing", 0):
        raise PermissionError("coverage reconciliation contains MISSING units")
    if approval.status != "APPROVED":
        raise PermissionError("explicit human approval is required")
    if approval.artifact_id != artifact.get("artifact_id") or approval.planning_hash != artifact.get("planning_hash"):
        raise PermissionError("approval target is stale or mismatched")
    if not approval.approved_at or not approval.approved_by or not approval.sdd_sha256 or not expected_sdd_sha256:
        raise PermissionError("approval metadata is incomplete")
    actor = approval.approved_by.strip()
    rejected_actors = {"codex", "llm", "ai", "auto", "automation"}
    if not actor or actor.casefold() in rejected_actors:
        raise PermissionError("AI cannot approve planning")
    if approval.sdd_sha256 != expected_sdd_sha256 or artifact.get("source_sdd_sha256") != expected_sdd_sha256:
        raise PermissionError("SDD approval binding is stale or mismatched")
    try:
        approved_at = datetime.fromisoformat(approval.approved_at)
    except ValueError as exc:
        raise PermissionError("approved_at must be valid ISO-8601") from exc
    if approved_at.tzinfo is None:
        raise PermissionError("approved_at must include a timezone")
    return WriterPhaseAuthorization(
        approval.artifact_id, approval.planning_hash, actor, approval.approved_at, approval.sdd_sha256
    )


def validate_contexts(
    contexts: tuple[SectionContext, ...], parser_unrecognized: int = 0,
    reconciliation: dict[str, Any] | None = None,
) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    if parser_unrecognized:
        findings.append(Finding("FAIL", "PARSER_UNRECOGNIZED", "*", str(parser_unrecognized)))
    section_ids = {context.section_id for context in contexts}
    all_coverage: list[tuple[str, str]] = []
    for context in contexts:
        if not context.section_id or not context.title or context.depth not in {1, 2}:
            findings.append(Finding("FAIL", "SCHEMA_VIOLATION", context.section_id, "identity/depth"))
        if not context.problems and not _approved_absence(context, "problems"):
            findings.append(Finding("FAIL", "EMPTY_PROBLEMS", context.section_id, ""))
        if not context.purposes and not _approved_absence(context, "purposes"):
            findings.append(Finding("FAIL", "EMPTY_PURPOSES", context.section_id, ""))
        if not context.coverage_units:
            findings.append(Finding("FAIL", "EMPTY_COVERAGE", context.section_id, ""))
        if not context.primary_owner:
            findings.append(Finding("FAIL", "OWNER_UNKNOWN", context.section_id, ""))
        for ref in context.cross_references:
            if ref not in section_ids:
                findings.append(Finding("FAIL", "UNRESOLVED_CROSS_REFERENCE", context.section_id, ref))
        for assignment in context.coverage_units:
            all_coverage.append((assignment.coverage_id, context.section_id))
            if not assignment.source_locator:
                findings.append(Finding("FAIL", "SOURCE_LOCATOR_MISSING", context.section_id, assignment.coverage_id))
            if assignment.primary_owner != context.primary_owner:
                findings.append(Finding("FAIL", "DUPLICATE_PRIMARY_OWNER", context.section_id, assignment.coverage_id))
        for value in context.exact_values:
            try:
                value.__post_init__()
            except ValueError as exc:
                findings.append(Finding("FAIL", "EXACT_VALUE_INVALID", context.section_id, str(exc)))
    counts = Counter(coverage_id for coverage_id, _ in all_coverage)
    for coverage_id, count in counts.items():
        if count > 1:
            owners = sorted(section for item, section in all_coverage if item == coverage_id)
            findings.append(Finding("FAIL", "COVERAGE_ID_DUPLICATE", "*", f"{coverage_id}:{owners}"))
    reason_sections = sum(bool(context.design_reasons) for context in contexts)
    premise_sections = sum(bool(context.premises) for context in contexts)
    if reason_sections == 0:
        findings.append(Finding("REVIEW_REQUIRED", "DESIGN_REASONS_ZERO", "*", "no explicit design reason was extracted"))
    elif reason_sections < len(contexts) // 4:
        findings.append(Finding("WARNING", "DESIGN_REASONS_SPARSE", "*", f"{reason_sections}/{len(contexts)} sections"))
    if premise_sections < len(contexts) // 4:
        findings.append(Finding("WARNING", "PREMISES_SPARSE", "*", f"{premise_sections}/{len(contexts)} sections; only explicit premises are retained"))
    semantic = [item for context in contexts for item in context.semantic_candidates]
    noisy = [item for item in semantic if item.disposition.value != "CONFIRMED"]
    if noisy:
        findings.append(Finding("REVIEW_REQUIRED", "SEMANTIC_CANDIDATE_NOISE", "*", f"{len(noisy)}/{len(semantic)} rejected or review-required"))
    assignment_review = sum(
        item.assignment_status == "REVIEW_REQUIRED"
        for context in contexts for item in context.coverage_units
    )
    if assignment_review:
        findings.append(Finding("REVIEW_REQUIRED", "ASSIGNMENT_REVIEW_REQUIRED", "*", str(assignment_review)))
    if reconciliation:
        if reconciliation.get("delta"):
            findings.append(Finding("WARNING", "COVERAGE_BASELINE_DIFFERENCE", "*", str(reconciliation["delta"])))
        if reconciliation.get("missing"):
            findings.append(Finding("FAIL", "COVERAGE_RECONCILIATION_MISSING", "*", str(reconciliation["missing"])))
    return tuple(findings)


def _approved_absence(context: SectionContext, kind: str) -> bool:
    return any(
        item.semantic_kind == kind and item.absent_reason and item.approved_by and item.approval_ref
        for item in context.absence_approvals
    )


def build_artifact(sdd_text: str, source_sha256: str, baseline_text: str = "") -> dict[str, Any]:
    parsed = parse_sdd(sdd_text)
    contexts = build_section_contexts(parsed)
    reconciliation = reconcile_coverage(baseline_text, parsed, contexts) if baseline_text else {}
    findings = validate_contexts(contexts, parsed.coverage.unrecognized, reconciliation)
    status_counts = Counter(context.planning_status.value for context in contexts)
    diagram_counts = Counter(context.diagram_plan.need.value for context in contexts)
    body: dict[str, Any] = {
        "artifact_id": "ARGUS-HSD-PLANNING-v0.1",
        "source_sdd_sha256": source_sha256,
        "approval_status": "PENDING",
        "stop": "STOP Human Review",
        "sections": [context.to_dict() for context in contexts],
        "coverage_reconciliation": reconciliation,
        "findings": [asdict(finding) for finding in findings],
        "summary": {
            "section_contexts": len(contexts),
            "coverage_units": sum(len(context.coverage_units) for context in contexts),
            "assignment_status": dict(sorted(status_counts.items())),
            "planning_failures": sum(f.severity == "FAIL" for f in findings),
            "planning_warnings": sum(f.severity == "WARNING" for f in findings),
            "planning_reviews": sum(f.severity == "REVIEW_REQUIRED" for f in findings),
            "design_reason_sections": sum(bool(c.design_reasons) for c in contexts),
            "premise_sections": sum(bool(c.premises) for c in contexts),
            "semantic_candidates": sum(len(c.semantic_candidates) for c in contexts),
            "semantic_confirmed_states": sum(len(c.states) for c in contexts),
            "assignment_review_required": sum(item.assignment_status == "REVIEW_REQUIRED" for c in contexts for item in c.coverage_units),
            "problems_empty": [c.section_id for c in contexts if not c.problems],
            "purposes_empty": [c.section_id for c in contexts if not c.purposes],
            "owner_unknown": [c.section_id for c in contexts if not c.primary_owner],
            "duplicate_owner": [f.detail for f in findings if f.code == "DUPLICATE_PRIMARY_OWNER"],
            "unresolved_cross_reference": [f.detail for f in findings if f.code == "UNRESOLVED_CROSS_REFERENCE"],
            "diagram_plan": dict(sorted(diagram_counts.items())),
        },
    }
    body["planning_hash"] = canonical_digest(body)
    return body


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("usage: planning_v2.py <sdd.md> <output.json> [baseline-coverage-map.md]", file=sys.stderr)
        return 2
    sdd_path = Path(sys.argv[1])
    baseline_text = Path(sys.argv[3]).read_text("utf-8") if len(sys.argv) == 4 else ""
    artifact = build_artifact(sdd_path.read_text("utf-8"), hashlib.sha256(sdd_path.read_bytes()).hexdigest(), baseline_text)
    Path(sys.argv[2]).write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
