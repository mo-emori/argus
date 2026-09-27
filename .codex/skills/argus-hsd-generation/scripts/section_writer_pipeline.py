from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from contracts import canonical_digest

COVERAGE_COLUMNS = (
    "Coverage ID", "SDD位置", "設計意味", "保存必須要素", "関係対象",
    "許容表現", "HSD配置先", "判定", "備考",
)
HANDOFF_FIELDS = {
    "section_id", "concepts_already_explained", "terms_fixed", "boundaries_established",
    "cross_references_available", "unresolved_items", "next_section_notes",
}
FORBIDDEN_INPUT_KEYS = {
    "completed_prose", "previous_section_prose", "full_sdd", "design_source", "full_hsd",
    "accepted_prose", "p0095_draft",
}
SEMANTIC_STATUSES = {"PRESERVED", "REFERENCED", "REVIEW", "MISSING", "DISTORTED", "INVENTED"}


@dataclass(frozen=True)
class SectionWriterOutputArtifact:
    writer_session_id: str
    section_id: str
    chapter_contract_digest: str
    human_structure_plan_digest: str
    coverage_contract_digest: str
    writer_input_digest: str
    producer_kind: str
    generated_at: str
    provenance_version: str
    content: str


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_coverage_contract(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [
            cell.strip().replace(r"\|", "|")
            for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
        if cells == list(COVERAGE_COLUMNS) or all(re.fullmatch(r"-+", cell) for cell in cells):
            continue
        if len(cells) == len(COVERAGE_COLUMNS):
            rows.append(dict(zip(COVERAGE_COLUMNS, cells, strict=True)))
    return rows


def validate_coverage_contract(markdown: str) -> list[str]:
    rows = parse_coverage_contract(markdown)
    findings: list[str] = []
    if not rows:
        return ["COVERAGE_EMPTY"]
    ids: set[str] = set()
    for row in rows:
        coverage_id = row["Coverage ID"]
        if coverage_id in ids:
            findings.append(f"COVERAGE_ID_DUPLICATE:{coverage_id}")
        ids.add(coverage_id)
        for column in ("Coverage ID", "SDD位置", "設計意味", "保存必須要素", "関係対象", "許容表現", "HSD配置先", "判定", "備考"):
            if not row[column] or row[column] in {"-", "—", "N/A"}:
                findings.append(f"COVERAGE_FIELD_EMPTY:{coverage_id}:{column}")
        if row["判定"] not in SEMANTIC_STATUSES:
            findings.append(f"COVERAGE_STATUS_INVALID:{coverage_id}")
        if "複数" in row["設計意味"] and not re.search(r"-[a-z][a-z0-9]*$", coverage_id):
            findings.append(f"COVERAGE_POSSIBLE_ILLEGAL_MERGE:{coverage_id}")
    return findings


def validate_writer_input(envelope: dict[str, Any], expected_section: str) -> list[str]:
    findings: list[str] = []
    allowed = {
        "chapter_contract", "human_structure_plan", "section_context", "section_coverage_contract",
        "writing_rules", "allowed_cross_reference_metadata", "section_handoff_metadata",
    }
    if not set(envelope).issubset(allowed):
        findings.append("WRITER_INPUT_NOT_CLOSED")
    pending: list[Any] = [envelope]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if FORBIDDEN_INPUT_KEYS.intersection(value):
                findings.append("FORBIDDEN_COMPLETED_OR_FULL_SOURCE_INPUT")
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    section = envelope.get("section_context", {})
    if section.get("section_id") != expected_section:
        findings.append("WRONG_SECTION_CONTEXT")
    handoff = envelope.get("section_handoff_metadata")
    if expected_section == "3.4" and handoff:
        findings.append("UNEXPECTED_HANDOFF_FOR_FIRST_SECTION")
    return findings


def validate_handoff(handoff: dict[str, Any], source_section: str, source_material: str) -> list[str]:
    findings: list[str] = []
    if set(handoff) != HANDOFF_FIELDS:
        findings.append("HANDOFF_NOT_CLOSED")
    if handoff.get("section_id") != source_section:
        findings.append("HANDOFF_WRONG_SECTION")
    serialized = json.dumps(handoff, ensure_ascii=False)
    if any(key in serialized for key in FORBIDDEN_INPUT_KEYS):
        findings.append("HANDOFF_CONTAINS_COMPLETED_PROSE")
    values = [str(item) for key, items in handoff.items() if key != "section_id" for item in (items if isinstance(items, list) else [items])]
    if any(value and value not in source_material for value in values):
        findings.append("HANDOFF_NEW_MEANING_REVIEW")
    return findings


def validate_distinct_sessions(first: str, second: str) -> None:
    if first == second:
        raise PermissionError("SECTION_WRITER_SESSION_REUSE")


def semantic_gate_allows_progress(rows: list[dict[str, str]]) -> bool:
    statuses = [row["判定"] for row in rows]
    if not statuses:
        return False
    if any(status in {"MISSING", "DISTORTED", "INVENTED"} for status in statuses):
        return False
    return all(status != "REVIEW" or bool(row["備考"].strip()) for row, status in zip(rows, statuses, strict=True))


def validate_output(artifact: SectionWriterOutputArtifact, expected: dict[str, str]) -> str:
    for field, value in expected.items():
        if str(getattr(artifact, field)) != value:
            raise PermissionError(f"PROVENANCE_MISMATCH:{field}")
    if artifact.producer_kind != "LLM_WRITER":
        raise PermissionError("NON_LLM_PRODUCER")
    if not artifact.content.strip():
        raise ValueError("EMPTY_WRITER_OUTPUT")
    generated_at = datetime.fromisoformat(artifact.generated_at)
    if generated_at.tzinfo is None:
        raise ValueError("generated_at must include timezone")
    return artifact.content


def make_writer_input(
    chapter_contract: dict[str, Any],
    structure_plan: str,
    section_context: dict[str, Any],
    coverage_contract: str,
    writing_rules: list[str],
    cross_references: list[dict[str, str]],
    handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "chapter_contract": chapter_contract,
        "human_structure_plan": structure_plan,
        "section_context": section_context,
        "section_coverage_contract": coverage_contract,
        "writing_rules": writing_rules,
        "allowed_cross_reference_metadata": cross_references,
    }
    if handoff is not None:
        envelope["section_handoff_metadata"] = handoff
    findings = validate_writer_input(envelope, section_context["section_id"])
    if findings:
        raise PermissionError(",".join(findings))
    return envelope


def artifact_dict(artifact: SectionWriterOutputArtifact) -> dict[str, Any]:
    return asdict(artifact)


def digest(value: Any) -> str:
    return canonical_digest(value)
