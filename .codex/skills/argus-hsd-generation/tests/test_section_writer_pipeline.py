from __future__ import annotations

from pathlib import Path

from section_writer_pipeline import (
    SectionWriterOutputArtifact,
    parse_coverage_contract,
    semantic_gate_allows_progress,
    validate_coverage_contract,
    validate_distinct_sessions,
    validate_handoff,
    validate_output,
    validate_writer_input,
)


def coverage(status: str = "PRESERVED", meaning: str = "意味", required: str = "condition") -> str:
    return (
        "| Coverage ID | SDD位置 | 設計意味 | 保存必須要素 | 関係対象 | 許容表現 | HSD配置先 | 判定 | 備考 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"| C-1 | L1 | {meaning} | {required} | 対象 | 本文 | 3.4 | {status} | 根拠あり |\n"
    )


def test_coverage_meaning_empty_fails() -> None:
    assert any("設計意味" in item for item in validate_coverage_contract(coverage(meaning="—")))


def test_coverage_required_elements_empty_fails() -> None:
    assert any("保存必須要素" in item for item in validate_coverage_contract(coverage(required="—")))


def test_possible_illegal_merge_is_flagged() -> None:
    assert any("ILLEGAL_MERGE" in item for item in validate_coverage_contract(coverage(meaning="複数の独立意味")))


def test_other_section_or_completed_prose_in_writer_input_fails() -> None:
    envelope = {"section_context": {"section_id": "3.5"}, "completed_prose": "本文"}
    findings = validate_writer_input(envelope, "3.4")
    assert "WRITER_INPUT_NOT_CLOSED" in findings
    assert "FORBIDDEN_COMPLETED_OR_FULL_SOURCE_INPUT" in findings
    assert "WRONG_SECTION_CONTEXT" in findings


def test_handoff_completed_prose_fails() -> None:
    handoff = {
        "section_id": "3.4", "concepts_already_explained": ["completed_prose"], "terms_fixed": [],
        "boundaries_established": [], "cross_references_available": [], "unresolved_items": [],
        "next_section_notes": [],
    }
    assert "HANDOFF_CONTAINS_COMPLETED_PROSE" in validate_handoff(handoff, "3.4", "")


def test_handoff_new_design_meaning_is_review() -> None:
    handoff = {
        "section_id": "3.4", "concepts_already_explained": ["新規意味"], "terms_fixed": [],
        "boundaries_established": [], "cross_references_available": [], "unresolved_items": [],
        "next_section_notes": [],
    }
    assert "HANDOFF_NEW_MEANING_REVIEW" in validate_handoff(handoff, "3.4", "既存意味")


def test_same_writer_session_fails() -> None:
    import pytest

    with pytest.raises(PermissionError, match="SESSION_REUSE"):
        validate_distinct_sessions("same", "same")


def test_semantic_failure_blocks_progress() -> None:
    for status in ("MISSING", "DISTORTED", "INVENTED"):
        assert not semantic_gate_allows_progress(parse_coverage_contract(coverage(status=status)))


def test_review_with_finding_note_allows_progress() -> None:
    assert semantic_gate_allows_progress(parse_coverage_contract(coverage(status="REVIEW")))


def test_preserved_contract_passes_progress_gate() -> None:
    assert semantic_gate_allows_progress(parse_coverage_contract(coverage()))


def test_coverage_and_structure_digest_mismatch_fail() -> None:
    import pytest

    artifact = SectionWriterOutputArtifact(
        writer_session_id="session", section_id="3.4", chapter_contract_digest="chapter",
        human_structure_plan_digest="wrong-plan", coverage_contract_digest="wrong-coverage",
        writer_input_digest="input", producer_kind="LLM_WRITER",
        generated_at="2026-09-24T20:00:00+09:00", provenance_version="2", content="本文",
    )
    expected = {
        "writer_session_id": "session", "section_id": "3.4", "chapter_contract_digest": "chapter",
        "human_structure_plan_digest": "plan", "coverage_contract_digest": "coverage",
        "writer_input_digest": "input", "provenance_version": "2",
    }
    with pytest.raises(PermissionError, match="human_structure_plan_digest"):
        validate_output(artifact, expected)


def test_p0096_r01_to_r04_regressions_are_present() -> None:
    root = Path(__file__).parents[4]
    draft = (root / "validation/reports/argus-p-0096-v1/section-3.4.md").read_text("utf-8")
    for token in (
        "StatusChangeCommand", "user_status.json", "status_version", "Proposal", "Order", "Incident",
        "config.json", "version", "hash", "Runtime Identity", "Secret", "Domain State",
    ):
        assert token in draft


def test_p0096_r05_failure_and_r06_stop_are_not_hidden() -> None:
    root = Path(__file__).parents[4]
    regression = (root / "validation/reports/argus-p-0096-v1/p0095-findings-regression.md").read_text("utf-8")
    stop = (root / "validation/reports/argus-p-0096-v1/section-3.5-context-insufficient.md").read_text("utf-8")
    assert "R-05" in regression and "FAIL" in regression
    assert "R-06" in regression and "NOT_RUN" in regression
    assert "CONTEXT_INSUFFICIENT" in stop
