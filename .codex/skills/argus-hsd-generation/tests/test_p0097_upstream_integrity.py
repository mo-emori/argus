from __future__ import annotations

from pathlib import Path

from context_builder import build_section_contexts
from sdd_parser import parse_sdd
from terminology_gate import validate_terminology

ROOT = Path(__file__).parents[4]


def _contexts():
    text = (ROOT / "docs/model/argus_structured_design_data_v0.1.md").read_text("utf-8")
    return {item.section_id: item for item in build_section_contexts(parse_sdd(text))}


def test_label_only_units_are_not_empty_context_meanings() -> None:
    section = _contexts()["3.5"]
    elements = [item for name in ("processes", "rules") for item in getattr(section, name)]
    by_id = {item.coverage_id: item.original_text for item in elements}
    assert "SDD-L1158" not in by_id
    assert "SDD-L1293" not in by_id
    assert by_id["SDD-L1159"]
    assert by_id["SDD-L1294"]


def test_r05_secret_boundary_reaches_section_34_context() -> None:
    section = _contexts()["3.4"]
    elements = [item for item in section.processes if item.coverage_id == "SDD-L1103"]
    assert len(elements) == 1
    for token in ("project", "config", "log", "evidence", "report", "backup"):
        assert token in elements[0].original_text


def test_formal_identifier_translation_fails() -> None:
    findings = validate_terminology("状態変更命令を送る。", {"StatusChangeCommand"})
    assert any(item["code"] == "FORMAL_IDENTIFIER_MISSING_OR_TRANSLATED" for item in findings)


def test_unnecessary_general_english_is_detected_without_code_false_positive() -> None:
    assert any(item["detail"] == "Data" for item in validate_terminology("Dataを保存する。", set()))
    assert not validate_terminology("`Data`を識別子として保存する。", set())


def test_japanese_rewrite_must_keep_coverage_identifier() -> None:
    findings = validate_terminology("利用者状態を更新する。", {"user_status.json"})
    assert findings == [{"code": "FORMAL_IDENTIFIER_MISSING_OR_TRANSLATED", "detail": "user_status.json"}]
