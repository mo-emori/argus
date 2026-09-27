from __future__ import annotations

import json
from pathlib import Path

import pytest
from major_chapter_orchestration import require_fresh_session, validate_writer_envelope
from renderer_guard import scan_active_scripts

ROOT = Path(__file__).parents[4]
SKILL = ROOT / ".codex/skills/argus-hsd-generation"


def test_active_scripts_remain_renderer_free() -> None:
    assert scan_active_scripts(SKILL / "scripts") == []


def test_chapter_three_contract_does_not_fix_output_shape() -> None:
    contract = json.loads((ROOT / "validation/reports/argus-p-0095-v1/chapter-contract.json").read_text("utf-8"))
    forbidden = {"fixed_subsection_count", "fixed_table_count", "fixed_diagram_count", "completed_prose"}
    assert not forbidden.intersection(contract)
    assert contract["included_child_sections"] == ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"]


def test_fresh_session_unavailable_stops() -> None:
    with pytest.raises(RuntimeError, match="FRESH_SESSION_UNAVAILABLE"):
        require_fresh_session(None, started=False)


def test_unrelated_chapter_context_fails() -> None:
    envelope = json.loads((ROOT / "validation/reports/argus-p-0095-v1/writer-input.json").read_text("utf-8"))
    envelope["context"]["sections"][0]["section_id"] = "4.1"
    with pytest.raises(PermissionError, match="unrelated chapter"):
        validate_writer_envelope(envelope, "3")


def test_full_sdd_field_fails_even_when_nested() -> None:
    envelope = json.loads((ROOT / "validation/reports/argus-p-0095-v1/writer-input.json").read_text("utf-8"))
    envelope["context"]["full_sdd"] = "must not reach Writer"
    with pytest.raises(PermissionError, match="forbidden Writer input"):
        validate_writer_envelope(envelope, "3")


def test_expected_values_are_pre_generation_artifacts() -> None:
    provenance = json.loads((ROOT / "validation/reports/argus-p-0095-v1/writer-session-provenance.json").read_text("utf-8"))
    assert provenance["expected_producer_kind"] == "LLM_WRITER"
    assert "content" not in provenance
    assert provenance["writer_input_digest"] == (ROOT / "validation/reports/argus-p-0095-v1/writer-input-digest.txt").read_text("utf-8").strip()
