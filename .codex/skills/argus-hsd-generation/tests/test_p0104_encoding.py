from __future__ import annotations

import json
from pathlib import Path

import pytest
from text_artifact_io import (
    persist_translation_artifacts,
    unicode_representation,
    validate_protected_values_before_persistence,
    validate_utf8_roundtrip,
)
from translation_preservation_gate import evaluate_translation
from translation_stage import StructureLock, TranslationContract, TranslationOutput, digest_text

REFERENCES = ("§2.6", "§4", "§28")


def contract(source: str, *, repair: bool = False) -> TranslationContract:
    version = "2-repair-1" if repair else "2"
    return TranslationContract(
        section_id="3.5.2",
        source_draft_digest=digest_text(source),
        source_language="en",
        target_language="ja",
        protected_identifiers=("Canonical State",),
        protected_literals=REFERENCES + ("TEST", "PAPER", "LIVE", "Asia/Tokyo"),
        protected_state_names=(),
        protected_paths=("logs/application/YYYY-MM-DD/",),
        protected_numeric_values=(),
        terminology_rules=("test-only complete policy",),
        structure_lock=StructureLock(),
        producer_kind="LLM_TRANSLATOR",
        translator_session_id="translator-repair" if repair else "translator",
        generation_timestamp="2026-09-25T14:00:00+09:00",
        provenance_version=version,
    )


def output(text: str, *, repair: bool = False) -> TranslationOutput:
    version = "2-repair-1" if repair else "2"
    return TranslationOutput(
        section_id="3.5.2",
        source_draft_digest=digest_text(SOURCE),
        translator_session_id="translator-repair" if repair else "translator",
        producer_kind="LLM_TRANSLATOR",
        translation_contract_version=version,
        generated_artifact_digest=digest_text(text),
        generation_timestamp="2026-09-25T14:00:01+09:00",
        provenance_version=version,
        content=text,
    )


SOURCE = "## A\nReferences: §2.6 / §4 / §28. TEST / PAPER / LIVE. Asia/Tokyo. logs/application/YYYY-MM-DD/."
TARGET = "## A\n参照: §2.6 / §4 / §28。TEST / PAPER / LIVE。Asia/Tokyo。logs/application/YYYY-MM-DD/。"


@pytest.mark.parametrize("repair", [False, True])
def test_protected_reference_roundtrip_through_persistence(tmp_path: Path, repair: bool) -> None:
    markdown = tmp_path / "section.md"
    artifact = tmp_path / "output.json"
    persist_translation_artifacts(markdown, artifact, SOURCE, output(TARGET, repair=repair), contract(SOURCE, repair=repair))
    assert markdown.read_text(encoding="utf-8") == TARGET
    assert json.loads(artifact.read_text(encoding="utf-8"))["content"] == TARGET
    assert evaluate_translation(SOURCE, TARGET, contract(SOURCE, repair=repair))["status"] == "PASS"


def test_section_sign_is_u00a7_and_utf8_c2a7() -> None:
    representation = unicode_representation("§")
    assert representation["code_points"] == ["U+00A7"]
    assert representation["utf8_hex"] == "c2a7"


def test_mojibake_is_rejected_before_persistence(tmp_path: Path) -> None:
    corrupt = TARGET.replace("§", "ﾂｧ")
    with pytest.raises(ValueError, match="PROTECTED_VALUE_CHANGED"):
        persist_translation_artifacts(
            tmp_path / "section.md",
            tmp_path / "output.json",
            SOURCE,
            output(corrupt, repair=True),
            contract(SOURCE, repair=True),
        )
    assert not (tmp_path / "section.md").exists()
    assert not (tmp_path / "output.json").exists()
    assert evaluate_translation(SOURCE, corrupt, contract(SOURCE, repair=True))["status"] == "FAIL"


def test_unrelated_protected_values_are_unchanged() -> None:
    assert validate_protected_values_before_persistence(SOURCE, TARGET, contract(SOURCE)) == []


def test_japanese_utf8_roundtrip_is_lossless() -> None:
    assert validate_utf8_roundtrip("一般的な日本語本文。節記号§と技術用語を含む。") == []
