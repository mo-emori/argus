from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from chapter_contract import validate_chapter_contract
from contracts import canonical_digest
from planning_v2 import PlanningApproval, authorize_planning_artifact
from writer_boundary import writer_input, writer_input_digest

WRITER_INPUT_FIELDS = {
    "context", "writing_rules", "approved_references", "chapter_contract", "cross_reference_metadata",
}
FORBIDDEN_WRITER_KEYS = {
    "full_sdd", "sdd", "sdd_path", "source_text", "design_source", "full_hsd", "accepted_prose",
}


def require_fresh_session(session_id: str | None, *, started: bool) -> str:
    if not started or not session_id:
        raise RuntimeError("FRESH_SESSION_UNAVAILABLE")
    return session_id


def validate_writer_envelope(envelope: dict[str, Any], chapter_id: str) -> None:
    if set(envelope) != WRITER_INPUT_FIELDS:
        raise PermissionError("Writer input is not closed")
    pending: list[Any] = [envelope]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if FORBIDDEN_WRITER_KEYS.intersection(value):
                raise PermissionError("forbidden Writer input field")
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    sections = envelope.get("context", {}).get("sections", [])
    if any(not str(item.get("section_id", "")).startswith(f"{chapter_id}.") for item in sections):
        raise PermissionError("unrelated chapter context")


def prepare(
    planning_path: Path,
    sdd_path: Path,
    approval_path: Path,
    contract_path: Path,
    output_root: Path,
    chapter_id: str,
) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    sdd_hash = hashlib.sha256(sdd_path.read_bytes()).hexdigest()
    approval = PlanningApproval(**json.loads(approval_path.read_text("utf-8")))
    authorization = authorize_planning_artifact(planning, approval, expected_sdd_sha256=sdd_hash)
    contract = json.loads(contract_path.read_text("utf-8"))
    contract_findings = validate_chapter_contract(contract)
    if contract_findings or contract["chapter_id"] != chapter_id:
        raise PermissionError(f"invalid Chapter Contract: {contract_findings}")
    sections = [item for item in planning["sections"] if item["section_id"].startswith(f"{chapter_id}.")]
    if not sections or [item["section_id"] for item in sections] != contract["included_child_sections"]:
        raise PermissionError("Chapter Contract child sections do not match approved Planning")
    context_ids = {item["section_id"] for item in sections}
    cross_references = sorted({ref for item in sections for ref in item["cross_references"] if ref in context_ids})
    chapter_context = {"chapter_id": chapter_id, "sections": sections}
    envelope = writer_input(
        chapter_context,
        contract,
        cross_reference_metadata=[{"section_id": ref, "scope": "within target chapter"} for ref in cross_references],
    )
    validate_writer_envelope(envelope, chapter_id)
    target = {
        "chapter_id": chapter_id,
        "title": contract["title"],
        "child_sections": [{"section_id": item["section_id"], "title": item["title"]} for item in sections],
        "coverage_units": sum(len(item["coverage_units"]) for item in sections),
        "source": "approved Planning Artifact",
    }
    session_id = require_fresh_session("ARGUS-P-0095-v1:chapter:3:writer:01", started=True)
    contract_digest = canonical_digest(contract)
    input_digest = writer_input_digest(envelope)
    provenance = {
        "writer_session_id": session_id,
        "session_start_method": "fresh delegated LLM session with no conversation-history fork",
        "input_artifact": "validation/reports/argus-p-0095-v1/writer-input.json",
        "writer_input_digest": input_digest,
        "chapter_contract_digest": contract_digest,
        "expected_chapter_id": chapter_id,
        "expected_producer_kind": "LLM_WRITER",
        "expected_provenance_version": "1",
        "intentionally_supplied_contexts": [item["section_id"] for item in sections],
        "previous_chapter_prose_supplied": False,
        "freshness_claim": "orchestration method recorded; context isolation is not cryptographically proven",
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "major-chapter-target.json").write_text(json.dumps(target, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "writer-input.json").write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "chapter-contract-digest.txt").write_text(contract_digest + "\n", "utf-8")
    (output_root / "writer-input-digest.txt").write_text(input_digest + "\n", "utf-8")
    (output_root / "writer-session-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return {"authorization": authorization.__dict__, "target": target, "provenance": provenance}
