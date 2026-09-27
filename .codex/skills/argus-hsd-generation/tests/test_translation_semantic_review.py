from __future__ import annotations

from dataclasses import replace

import pytest
from hsd_quality_policy import FindingSeverity
from translation_semantic_review import (
    TranslationSemanticFinding,
    TranslationSemanticReview,
    make_review_input,
    route_translation_review,
)

BASE = {
    "section_id": "3.5.2", "english_draft_digest": "e" * 64, "japanese_draft_digest": "j" * 64,
    "translation_contract_digest": "c" * 64, "translation_contract_version": "1",
    "writer_session_id": "writer", "translator_session_id": "translator",
}


def review(result: str = "PASS", status: str = "PRESERVED") -> TranslationSemanticReview:
    return TranslationSemanticReview(
        "3.5.2", "e" * 64, "j" * 64, "c" * 64, "1", "reviewer",
        "LLM_TRANSLATION_SEMANTIC_REVIEWER", "2026-09-25T00:00:00+09:00", result,  # type: ignore[arg-type]
        (TranslationSemanticFinding(status, "subject-target", "checked"),), "1",  # type: ignore[arg-type]
    )


def route(item: TranslationSemanticReview | None, required: bool = True) -> dict[str, object]:
    return route_translation_review({"independent_semantic_review_required": required}, item, **BASE)


def test_required_without_result_fails() -> None:
    assert route(None)["decision"] == "FAIL"


def test_required_pass_advances() -> None:
    assert route(review())["decision"] == "NEXT_GATE"


def test_required_review_advances_with_findings() -> None:
    result = route(review("REVIEW", "REVIEW"))
    assert result["decision"] == "NEXT_GATE"
    assert result["section_result"] == "ACCEPT_WITH_FINDINGS"


def test_required_fail_fails() -> None:
    assert route(review("FAIL", "MISSING"))["decision"] == "FAIL"


@pytest.mark.parametrize("session", ["translator", "writer"])
def test_reviewer_session_must_be_independent(session: str) -> None:
    assert route(replace(review(), reviewer_session_id=session))["decision"] == "FAIL"


@pytest.mark.parametrize("field,value", [
    ("english_draft_digest", "x" * 64), ("japanese_draft_digest", "x" * 64),
    ("translation_contract_digest", "x" * 64), ("translation_contract_version", "2"),
])
def test_binding_mismatch_fails(field: str, value: str) -> None:
    assert route(replace(review(), **{field: value}))["decision"] == "FAIL"


def test_producer_kind_mismatch_fails() -> None:
    assert route(replace(review(), producer_kind="LLM_TRANSLATOR"))["decision"] == "FAIL"


@pytest.mark.parametrize("status", ["MISSING", "DISTORTED", "INVENTED"])
def test_blocking_finding_fails(status: str) -> None:
    assert route(review("FAIL", status))["decision"] == "FAIL"


def test_minor_missing_can_be_explicitly_review_severity() -> None:
    item = review("REVIEW", "MISSING")
    item = replace(item, findings=(replace(item.findings[0], severity=FindingSeverity.REVIEW),))
    result = route(item)
    assert result["decision"] == "NEXT_GATE"
    assert result["section_result"] == "ACCEPT_WITH_FINDINGS"


def test_review_finding_cannot_auto_pass() -> None:
    assert route(review("PASS", "REVIEW"))["decision"] == "FAIL"


def test_review_not_required_advances_without_llm_review() -> None:
    assert route(None, required=False)["decision"] == "NEXT_GATE"


def test_reviewer_input_rejects_design_sources() -> None:
    with pytest.raises(PermissionError, match="FORBIDDEN_DESIGN_INPUT"):
        make_review_input("English", "日本語", {"section_context": {}}, {"status": "FAIL"})
