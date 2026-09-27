from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from human_facing_gate import evaluate_human_facing
from translation_preservation_gate import evaluate_translation
from translation_stage import (
    TERMINOLOGY_RULES_V2,
    StructureLock,
    TranslationContract,
    digest_text,
    make_translator_input,
    validate_terminology_policy,
)


def contract(source: str) -> TranslationContract:
    return TranslationContract(
        section_id="3.5.2",
        source_draft_digest=digest_text(source),
        source_language="en",
        target_language="ja",
        protected_identifiers=("Canonical State",),
        protected_literals=("TEST", "PAPER", "LIVE", "Asia/Tokyo"),
        protected_state_names=("RECONCILIATION_REQUIRED",),
        protected_paths=("logs/application/YYYY-MM-DD/",),
        protected_numeric_values=(),
        terminology_rules=TERMINOLOGY_RULES_V2,
        structure_lock=StructureLock(),
        producer_kind="LLM_TRANSLATOR",
        translator_session_id="translator-p0102",
        generation_timestamp="2026-09-25T13:00:00+09:00",
        provenance_version="2",
        human_facing_technical_concepts=("Runtime", "Job", "Adapter", "Error"),
        semantic_risk_terms=("unredacted",),
        terminology_policy_version="2",
    )


def test_terminology_policy_is_complete() -> None:
    assert validate_terminology_policy(contract("Text.")) == []


def test_unexplained_technical_concept_sequence_is_finding() -> None:
    result = evaluate_human_facing(
        "Runtime、Job、Adapter、Errorを確認する。",
        enforce_japanese=True,
        technical_concepts={"Runtime", "Job", "Adapter", "Error"},
    )
    assert "UNEXPLAINED_TECHNICAL_CONCEPT_SEQUENCE" in {item["code"] for item in result["findings"]}


def test_explained_first_use_has_no_technical_concept_finding() -> None:
    result = evaluate_human_facing(
        "実行環境（Runtime）、処理単位（Job）、接続部品（Adapter）、障害（Error）を確認する。",
        enforce_japanese=True,
        technical_concepts={"Runtime", "Job", "Adapter", "Error"},
    )
    assert "UNEXPLAINED_TECHNICAL_CONCEPT_SEQUENCE" not in {item["code"] for item in result["findings"]}


def test_protected_values_are_not_technical_concept_false_positives() -> None:
    protected = {"TEST", "PAPER", "LIVE", "Asia/Tokyo", "logs/application/YYYY-MM-DD/"}
    text = "TEST / PAPER / LIVEを分離し、Asia/Tokyoでlogs/application/YYYY-MM-DD/へ保存する。"
    assert evaluate_human_facing(
        text,
        protected,
        enforce_japanese=True,
        technical_concepts=protected,
    )["status"] == "PASS"


def test_overlapping_protected_identifier_is_removed_longest_first() -> None:
    result = evaluate_human_facing(
        "Canonical State、Fact、Event、Audit Record、および Audit を保持する。",
        {"Canonical State", "Fact", "Event", "Audit Record", "Audit"},
        enforce_japanese=True,
    )
    assert result["status"] == "PASS"


def test_unredacted_to_generic_unedited_requires_semantic_review() -> None:
    source = "## A\nDo not record an unredacted debug dump."
    result = evaluate_translation(source, "## A\n未編集のデバッグダンプを記録してはならない。", contract(source))
    assert result["status"] == "FAIL"
    assert result["independent_semantic_review_required"] is True


def test_original_term_with_japanese_explanation_is_allowed() -> None:
    source = "## A\nDo not record an unredacted debug dump."
    target = "## A\n秘匿化されていない（unredacted）デバッグダンプを記録してはならない。"
    result = evaluate_translation(source, target, contract(source))
    assert result["status"] == "PASS"


def test_missing_no_new_design_meaning_rule_fails_contract_validation() -> None:
    weak = replace(
        contract("Text."),
        terminology_rules=tuple(rule for rule in TERMINOLOGY_RULES_V2 if "Do not add" not in rule),
    )
    assert "TERMINOLOGY_POLICY_MISSING:no_new_design_meaning" in validate_terminology_policy(weak)


def test_v2_translator_envelope_rejects_incomplete_terminology_policy() -> None:
    source = "Text."
    weak = replace(contract(source), terminology_rules=("preserve protected literal",))
    try:
        make_translator_input(source, weak)
    except PermissionError as error:
        assert "INVALID_TERMINOLOGY_POLICY" in str(error)
    else:
        raise AssertionError("incomplete v2 terminology policy must fail closed")


def test_first_use_explanation_cannot_add_normative_meaning() -> None:
    source = "## A\nA runtime coordinates the operation."
    target = "## A\n操作を調整しなければならない実行環境（Runtime）である。"
    result = evaluate_translation(source, target, contract(source))
    assert result["status"] == "FAIL"
    assert result["independent_semantic_review_required"] is True
    assert "POSSIBLE_INVENTED_NORMATIVE_MEANING" in {item["code"] for item in result["findings"]}


def test_p0101_artifact_is_a_detected_regression_fixture() -> None:
    root = Path(__file__).resolve().parents[4]
    report = root / "validation" / "reports" / "argus-p-0101-v1"
    source = (report / "section-3.5.2-en.md").read_text(encoding="utf-8")
    target = (report / "section-3.5.2-ja.md").read_text(encoding="utf-8")
    concepts = {"Runtime", "Job", "Adapter", "Error"}
    human = evaluate_human_facing(
        target,
        enforce_japanese=True,
        technical_concepts=concepts,
    )
    preservation = evaluate_translation(source, target, contract(source))
    assert "UNEXPLAINED_TECHNICAL_CONCEPT_SEQUENCE" in {item["code"] for item in human["findings"]}
    assert "TECHNICAL_CONCEPT_TRANSLATION_REQUIRES_REVIEW" in {
        item["code"] for item in preservation["findings"]
    }
