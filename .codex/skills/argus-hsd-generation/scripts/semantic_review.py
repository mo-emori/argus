from __future__ import annotations

from dataclasses import dataclass

from contracts import ReviewVerdict, SectionContext
from gates import GateReport


@dataclass(frozen=True)
class SemanticReviewPacket:
    context: SectionContext
    rendered_section: str
    mechanical_reports: tuple[GateReport, ...]

    def __post_init__(self) -> None:
        if any(not report.passed for report in self.mechanical_reports):
            raise ValueError("semantic review cannot bypass failed mechanical gates")


@dataclass(frozen=True)
class SemanticReviewResult:
    verdict: ReviewVerdict
    findings: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.verdict is ReviewVerdict.FINDINGS and not self.findings:
            raise ValueError("FINDINGS requires at least one finding")
        if self.verdict is ReviewVerdict.NO_FINDINGS and self.findings:
            raise ValueError("NO_FINDINGS cannot contain findings")

