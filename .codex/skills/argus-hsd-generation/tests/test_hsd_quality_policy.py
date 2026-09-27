from __future__ import annotations

import pytest
from hsd_quality_policy import (
    QualityFinding,
    SectionResult,
    candidate_kind,
    classify_finding,
    may_continue,
    missing_sections_for_partial,
    section_result,
    should_auto_repair,
    summarize_sections,
)


def finding(code: str) -> QualityFinding:
    return QualityFinding(code, classify_finding(code))


@pytest.mark.parametrize("code", [
    "METADATA_LEAKAGE", "DESIGN_REFERENCE_OMISSION", "MINOR_COVERAGE_OMISSION",
    "MEANING_PRESERVING_LITERAL_NORMALIZATION",
])
def test_review_findings_accept_and_continue(code: str) -> None:
    result = section_result([finding(code)])
    assert result is SectionResult.ACCEPT_WITH_FINDINGS
    assert may_continue(result)
    assert not should_auto_repair([finding(code)], 0)


@pytest.mark.parametrize("code", [
    "PROHIBITION_REVERSAL", "BEHAVIOR_CHANGING_NUMERIC_ALTERATION",
    "MAJOR_INVENTED_REQUIREMENT", "MAJOR_SAFETY_OMISSION",
])
def test_major_meaning_damage_blocks_and_gets_one_repair(code: str) -> None:
    item = finding(code)
    assert section_result([item]) is SectionResult.BLOCKED
    assert should_auto_repair([item], 0)
    assert not should_auto_repair([item], 1)


def test_readability_is_warning_and_does_not_repair() -> None:
    item = finding("TERMINOLOGY_READABILITY")
    assert section_result([item]) is SectionResult.PASS
    assert not should_auto_repair([item], 0)


def test_review_does_not_stop_multi_section_or_assembly() -> None:
    results = [SectionResult.ACCEPT_WITH_FINDINGS, SectionResult.PASS]
    assert all(may_continue(result) for result in results)
    assert summarize_sections(results) == {"PASS": 1, "ACCEPT_WITH_FINDINGS": 1, "BLOCKED": 0}
    assert candidate_kind(results) == "FULL_HSD_CANDIDATE"


def test_blocked_section_does_not_hide_partial_candidate_gaps() -> None:
    results = {"1.2": SectionResult.BLOCKED, "3.1": SectionResult.PASS}
    assert candidate_kind(results.values()) == "PARTIAL_HSD_CANDIDATE"
    assert missing_sections_for_partial(results) == ("1.2",)


@pytest.mark.parametrize("code", [
    "PROVENANCE_BINDING_FAILURE", "SESSION_BINDING_FAILURE", "UTF8_INTEGRITY_FAILURE",
])
def test_integrity_failures_remain_blockers(code: str) -> None:
    assert section_result([finding(code)]) is SectionResult.BLOCKED


def test_unknown_finding_cannot_be_mechanically_downgraded() -> None:
    with pytest.raises(ValueError, match="UNMAPPED_FINDING_SEVERITY"):
        classify_finding("NEW_UNREVIEWED_CODE")
