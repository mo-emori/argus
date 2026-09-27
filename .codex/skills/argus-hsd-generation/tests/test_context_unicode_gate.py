from __future__ import annotations

import json
from pathlib import Path

import pytest
from context_unicode_gate import cp932_misdecode_recovery, scan_context, strict_utf8_load


def test_authority_range_and_reference_survive_strict_utf8_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "context.json"
    path.write_text(json.dumps({"stage": "17〜18", "reference": "§49"}, ensure_ascii=False), "utf-8")
    raw, text = strict_utf8_load(path)
    assert raw == text.encode("utf-8")
    assert "17〜18" in text
    assert "§49" in text
    assert scan_context(path)["candidates"] == []


def test_cp932_misdecoded_fixture_is_detected_but_not_rewritten(tmp_path: Path) -> None:
    corrupted = b"\xc2\xa7".decode("cp932") + "49"
    assert cp932_misdecode_recovery(corrupted) == "§49"
    path = tmp_path / "context.json"
    path.write_text(json.dumps({"stage": corrupted}, ensure_ascii=False), "utf-8")
    report = scan_context(path)
    assert report["candidates"][0]["recovered_candidate"] == "§49"
    assert json.loads(path.read_text("utf-8"))["stage"] == corrupted


def test_invalid_utf8_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "context.json"
    path.write_bytes(b'{"value":"\x81"}')
    with pytest.raises(UnicodeDecodeError):
        strict_utf8_load(path)


def test_replacement_character_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "context.json"
    path.write_text(json.dumps({"value": "bad\ufffdvalue"}), "utf-8")
    report = scan_context(path)
    assert any(item["kind"] == "U+FFFD" for item in report["candidates"])
