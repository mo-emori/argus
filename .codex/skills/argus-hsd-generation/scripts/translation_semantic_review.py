from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Literal

from hsd_quality_policy import FindingSeverity, QualityFinding, SectionResult, section_result

FindingStatus = Literal["PRESERVED", "REVIEW", "MISSING", "DISTORTED", "INVENTED"]
ReviewResult = Literal["PASS", "REVIEW", "FAIL"]
RouteDecision = Literal["NEXT_GATE", "FAIL"]

FORBIDDEN_REVIEW_KEYS = {"source", "sdd", "section_context", "design_source", "coverage", "accepted_prose"}


@dataclass(frozen=True)
class TranslationSemanticFinding:
    status: FindingStatus
    subject: str
    detail: str
    severity: FindingSeverity | None = None


@dataclass(frozen=True)
class TranslationSemanticReview:
    section_id: str
    english_draft_digest: str
    japanese_draft_digest: str
    translation_contract_digest: str
    translation_contract_version: str
    reviewer_session_id: str
    producer_kind: str
    review_timestamp: str
    review_result: ReviewResult
    findings: tuple[TranslationSemanticFinding, ...]
    provenance_version: str


def digest_json(value: Any) -> str:
    import json

    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def make_review_input(
    english_draft: str,
    japanese_draft: str,
    translation_contract: dict[str, Any],
    preservation_gate_result: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "english_semantic_draft": english_draft,
        "japanese_draft": japanese_draft,
        "translation_contract": translation_contract,
        "translation_preservation_gate_result": preservation_gate_result,
    }
    findings = validate_review_input(packet)
    if findings:
        raise PermissionError(",".join(findings))
    return packet


def validate_review_input(packet: dict[str, Any]) -> list[str]:
    allowed = {
        "english_semantic_draft", "japanese_draft", "translation_contract",
        "translation_preservation_gate_result",
    }
    findings: list[str] = []
    if set(packet) != allowed:
        findings.append("REVIEW_INPUT_NOT_CLOSED")
    pending: list[Any] = [packet]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if FORBIDDEN_REVIEW_KEYS.intersection(value):
                findings.append("FORBIDDEN_DESIGN_INPUT")
            pending.extend(value.values())
        elif isinstance(value, list | tuple):
            pending.extend(value)
    return sorted(set(findings))


def route_translation_review(
    preservation_gate_result: dict[str, Any],
    review: TranslationSemanticReview | None,
    *,
    section_id: str,
    english_draft_digest: str,
    japanese_draft_digest: str,
    translation_contract_digest: str,
    translation_contract_version: str,
    writer_session_id: str,
    translator_session_id: str,
) -> dict[str, object]:
    required = preservation_gate_result.get("independent_semantic_review_required") is True
    if not required:
        return {"decision": "NEXT_GATE", "findings": [], "semantic_review_required": False}
    if review is None:
        return {"decision": "FAIL", "findings": ["SEMANTIC_REVIEW_REQUIRED_MISSING"], "semantic_review_required": True}

    findings: list[str] = []
    expected = {
        "section_id": section_id,
        "english_draft_digest": english_draft_digest,
        "japanese_draft_digest": japanese_draft_digest,
        "translation_contract_digest": translation_contract_digest,
        "translation_contract_version": translation_contract_version,
    }
    for field, value in expected.items():
        if getattr(review, field) != value:
            findings.append(f"BINDING_MISMATCH:{field}")
    if review.reviewer_session_id in {writer_session_id, translator_session_id}:
        findings.append("REVIEWER_SESSION_NOT_INDEPENDENT")
    if review.producer_kind != "LLM_TRANSLATION_SEMANTIC_REVIEWER":
        findings.append("REVIEWER_PRODUCER_KIND_MISMATCH")
    try:
        timestamp = datetime.fromisoformat(review.review_timestamp)
        if timestamp.tzinfo is None:
            findings.append("REVIEW_TIMESTAMP_NO_TIMEZONE")
    except ValueError:
        findings.append("REVIEW_TIMESTAMP_INVALID")

    quality_findings = tuple(
        QualityFinding(
            code=item.status,
            severity=item.severity or (
                FindingSeverity.REVIEW if item.status == "REVIEW" else
                FindingSeverity.BLOCKER if item.status in {"MISSING", "DISTORTED", "INVENTED"} else
                FindingSeverity.WARNING
            ),
            detail=item.detail,
        )
        for item in review.findings
        if item.status != "PRESERVED"
    )
    result = section_result(quality_findings)
    if review.review_result == "PASS" and result is not SectionResult.PASS:
        findings.append("ILLEGAL_PASS_WITH_FINDINGS")
    if result is SectionResult.BLOCKED:
        findings.append("SEMANTIC_FINDING_BLOCKING")

    if findings:
        return {"decision": "FAIL", "findings": sorted(set(findings)), "semantic_review_required": True}
    return {
        "decision": "NEXT_GATE",
        "findings": [],
        "semantic_review_required": True,
        "section_result": result.value,
        "review": asdict(review),
    }
