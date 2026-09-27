from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ChildSectionResponsibility:
    section_id: str
    responsibility: str


@dataclass(frozen=True)
class ChapterContract:
    chapter_id: str
    title: str
    chapter_purpose: str
    reader_outcome: str
    included_child_sections: tuple[str, ...]
    child_section_responsibilities: tuple[ChildSectionResponsibility, ...]
    explanation_order: tuple[str, ...]
    adjacent_chapter_boundaries: tuple[str, ...]
    allowed_cross_references: tuple[str, ...]
    terminology_constraints: tuple[str, ...]
    representation_considerations: tuple[str, ...]
    unresolved_human_decisions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_chapter_contract(value: dict[str, Any]) -> list[str]:
    required = set(ChapterContract.__dataclass_fields__)
    findings = [f"missing:{name}" for name in sorted(required - value.keys())]
    findings.extend(f"unknown:{name}" for name in sorted(value.keys() - required))
    if "included_child_sections" in value and not value["included_child_sections"]:
        findings.append("empty:included_child_sections")
    forbidden = {"fixed_subsection_count", "fixed_table_count", "fixed_diagram_count"}
    if forbidden.intersection(value):
        findings.append("template-counts-forbidden")
    return findings


def session_id(chapter_id: str, run_id: str) -> str:
    if not chapter_id or not run_id:
        raise ValueError("chapter_id and run_id are required")
    return f"{run_id}:chapter:{chapter_id}"
