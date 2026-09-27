from __future__ import annotations

from dataclasses import dataclass

from contracts import SectionContext, canonical_digest


@dataclass(frozen=True)
class PlanningFinding:
    section_id: str
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class PlanningArtifact:
    sections: tuple[SectionContext, ...]
    findings: tuple[PlanningFinding, ...]

    @property
    def digest(self) -> str:
        return canonical_digest(self)


def validate_planning(sections: tuple[SectionContext, ...]) -> tuple[PlanningFinding, ...]:
    findings: list[PlanningFinding] = []
    ids = {section.section_id for section in sections}
    for section in sections:
        checks = (
            (not section.problems, "ERROR", "EMPTY_PROBLEMS", "課題が空です"),
            (not section.purposes, "ERROR", "EMPTY_PURPOSES", "目的が空です"),
            (not section.exact_value_ids, "WARNING", "NO_EXACT_VALUES", "具体値がありません"),
            (not section.coverage_units, "ERROR", "NO_COVERAGE", "coverage unit がありません"),
            (not section.primary_owner, "ERROR", "NO_PRIMARY_OWNER", "primary owner がありません"),
        )
        for failed, severity, code, message in checks:
            if failed:
                findings.append(PlanningFinding(section.section_id, severity, code, message))
        for reference in section.cross_references:
            if reference not in ids:
                findings.append(
                    PlanningFinding(section.section_id, "ERROR", "UNRESOLVED_REFERENCE", reference)
                )
    return tuple(findings)


def build_planning(sections: tuple[SectionContext, ...]) -> PlanningArtifact:
    return PlanningArtifact(sections=sections, findings=validate_planning(sections))

