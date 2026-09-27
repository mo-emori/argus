from __future__ import annotations

import pytest
from human_facing_gate import evaluate_human_facing
from translation_preservation_gate import evaluate_translation
from translation_stage import (
    StructureLock,
    TranslationContract,
    TranslationOutput,
    digest_text,
    make_translator_input,
    validate_translation_output,
    validate_translator_input,
)


def contract(source: str) -> TranslationContract:
    return TranslationContract(
        section_id="3.5.2", source_draft_digest=digest_text(source), source_language="en", target_language="ja",
        protected_identifiers=("Canonical State",), protected_literals=("BUY/ADD",),
        protected_state_names=("RECONCILIATION_REQUIRED",), protected_paths=("L:\\data",),
        protected_numeric_values=("1.8TB",), terminology_rules=("一般説明は日本語",),
        structure_lock=StructureLock(), producer_kind="LLM_TRANSLATOR", translator_session_id="translator-1",
        generation_timestamp="2026-09-25T00:00:00+09:00", provenance_version="1",
    )


@pytest.mark.parametrize("old,new", [
    ("Canonical State", "正本状態"), ("L:\\data", "D:\\data"),
    ("RECONCILIATION_REQUIRED", "RECONCILED"), ("1.8TB", "2TB"),
])
def test_protected_value_change_fails(old: str, new: str) -> None:
    source = f"## A\n{old}."
    assert evaluate_translation(source, source.replace(old, new), contract(source))["status"] == "FAIL"


def test_normative_weakening_fails() -> None:
    source = "## A\nThe operation must not continue."
    assert evaluate_translation(source, "## A\n操作を継続できる。", contract(source))["status"] == "FAIL"


def test_unresolved_resolution_fails() -> None:
    source = "## A\nRetention is TBD."
    assert evaluate_translation(source, "## A\n保持期間は30日である。", contract(source))["status"] == "FAIL"


@pytest.mark.parametrize("source,target,code", [
    ("## A\n|a|b|\n|-|-|\n|1|2|", "## A\n|a|b|\n|-|-|", "TABLE_STRUCTURE_CHANGED"),
    ("## A\n- one\n- two", "## A\n- 一つ", "LIST_ITEM_COUNT_CHANGED"),
    ("## A\ntext", "### A\n文", "HEADING_HIERARCHY_CHANGED"),
])
def test_structure_change_fails(source: str, target: str, code: str) -> None:
    result = evaluate_translation(source, target, contract(source))
    assert result["status"] == "FAIL"
    assert code in {item["code"] for item in result["findings"]}


def test_possible_new_meaning_requires_review() -> None:
    source = "## A\nOne."
    result = evaluate_translation(source, "## A\n一。追加。さらに追加。", contract(source))
    assert result["status"] == "FAIL"
    assert result["independent_semantic_review_required"] is True


def test_source_digest_mismatch_fails() -> None:
    with pytest.raises(PermissionError, match="SOURCE_DRAFT_DIGEST_MISMATCH"):
        make_translator_input("changed", contract("original"))


def test_same_writer_translator_session_fails() -> None:
    source = "## A\nText."
    c = contract(source)
    output = TranslationOutput("3.5.2", c.source_draft_digest, "translator-1", "LLM_TRANSLATOR", "1", digest_text("訳。"), "2026-09-25T00:00:00+09:00", "1", "訳。")
    assert "WRITER_TRANSLATOR_SESSION_REUSE" in validate_translation_output(output, c, "translator-1")


def test_forbidden_design_input_fails() -> None:
    assert "FORBIDDEN_DESIGN_INPUT" in validate_translator_input({"source_draft": "x", "translation_contract": {}, "sdd": "x"})


def test_english_run_is_detected() -> None:
    assert evaluate_human_facing("これは Storage Backup Restore Process の説明である。", enforce_japanese=True)["status"] == "FAIL"


def test_protected_identifier_is_not_false_positive() -> None:
    result = evaluate_human_facing("`Canonical State`を保持する。", {"Canonical State"}, enforce_japanese=True)
    assert result["status"] == "PASS"
