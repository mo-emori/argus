from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class FindingSeverity(str, Enum):
    BLOCKER = "BLOCKER"
    REVIEW = "REVIEW"
    WARNING = "WARNING"


class SectionResult(str, Enum):
    PASS = "PASS"  # nosec B105
    ACCEPT_WITH_FINDINGS = "ACCEPT_WITH_FINDINGS"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class QualityFinding:
    code: str
    severity: FindingSeverity
    detail: str = ""


BLOCKER_CODES = {
    "PROHIBITION_REVERSAL",
    "PERMISSION_REVERSAL",
    "RESPONSIBILITY_REVERSAL",
    "CAUSAL_REVERSAL",
    "BEHAVIOR_CHANGING_NUMERIC_ALTERATION",
    "BEHAVIOR_CHANGING_STATE_ALTERATION",
    "BEHAVIOR_CHANGING_CONDITION_ALTERATION",
    "MAJOR_SAFETY_OMISSION",
    "MAJOR_PROCESS_OMISSION",
    "MAJOR_STATE_TRANSITION_OMISSION",
    "MAJOR_INVENTED_REQUIREMENT",
    "UNREADABLE_MOJIBAKE",
    "MEANING_CHANGING_PROTECTED_VALUE",
    "AUTHORITY_BINDING_FAILURE",
    "PROVENANCE_BINDING_FAILURE",
    "SESSION_BINDING_FAILURE",
    "UTF8_INTEGRITY_FAILURE",
    "TECHNICAL_GENERATION_FAILURE",
}

REVIEW_CODES = {
    "DESIGN_REFERENCE_OMISSION",
    "MINOR_COVERAGE_OMISSION",
    "MEANING_PRESERVING_LITERAL_NORMALIZATION",
    "METADATA_LEAKAGE",
    "TECHNICAL_TERM_VARIATION",
    "SUBSECTION_STRUCTURE",
    "DIAGRAM_SELECTION",
    "PARTIAL_EXPLANATION_COMPRESSION",
    "INSUFFICIENT_EXPLANATION",
    "MINOR_SEMANTIC_UNCERTAINTY",
    "INSPECTION_METADATA",
    "NON_NORMATIVE_ADDITION_SUSPECTED",
}

WARNING_CODES = {
    "JAPANESE_STIFFNESS",
    "ENGLISH_REMAINDER",
    "REDUNDANCY",
    "SENTENCE_SPLITTING",
    "NOTATION_VARIATION",
    "DIAGRAM_SHORTAGE",
    "CHAPTER_PILLAR_QUALITY",
    "CATALOGIZATION_CANDIDATE",
    "MINOR_READER_JOURNEY",
    "TERMINOLOGY_READABILITY",
}


def classify_finding(code: str) -> FindingSeverity:
    if code in BLOCKER_CODES:
        return FindingSeverity.BLOCKER
    if code in REVIEW_CODES:
        return FindingSeverity.REVIEW
    if code in WARNING_CODES:
        return FindingSeverity.WARNING
    raise ValueError(f"UNMAPPED_FINDING_SEVERITY:{code}")


def section_result(findings: Iterable[QualityFinding], *, technically_generated: bool = True) -> SectionResult:
    items = tuple(findings)
    if not technically_generated or any(item.severity is FindingSeverity.BLOCKER for item in items):
        return SectionResult.BLOCKED
    if any(item.severity is FindingSeverity.REVIEW for item in items):
        return SectionResult.ACCEPT_WITH_FINDINGS
    return SectionResult.PASS


def should_auto_repair(findings: Iterable[QualityFinding], repair_count: int) -> bool:
    if repair_count < 0 or repair_count > 1:
        raise ValueError("repair_count must be 0 or 1")
    return repair_count == 0 and any(item.severity is FindingSeverity.BLOCKER for item in findings)


def may_continue(result: SectionResult) -> bool:
    return result in {SectionResult.PASS, SectionResult.ACCEPT_WITH_FINDINGS}


def summarize_sections(results: Iterable[SectionResult]) -> dict[str, int]:
    items = tuple(results)
    return {status.value: sum(item is status for item in items) for status in SectionResult}


def candidate_kind(results: Iterable[SectionResult]) -> str:
    items = tuple(results)
    if not items:
        raise ValueError("candidate requires at least one section result")
    return "PARTIAL_HSD_CANDIDATE" if SectionResult.BLOCKED in items else "FULL_HSD_CANDIDATE"


def missing_sections_for_partial(section_results: dict[str, SectionResult]) -> tuple[str, ...]:
    return tuple(section_id for section_id, result in section_results.items() if result is SectionResult.BLOCKED)
