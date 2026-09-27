from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from chapter_contract import validate_chapter_contract
from human_facing_gate import evaluate_corpus, evaluate_human_facing
from planning_v2 import PlanningApproval, authorize_planning_artifact
from renderer_guard import scan_active_scripts, scan_script
from writer_boundary import (
    LLM_PRODUCER,
    PROVENANCE_VERSION,
    WRITER_INPUT_FIELDS,
    LLMWriterOutputArtifact,
    validate_llm_output,
    writer_input,
    writer_input_digest,
)

ROOT = Path(__file__).parents[4]
SKILL = ROOT / ".codex/skills/argus-hsd-generation"


def contract() -> dict[str, object]:
    return {
        "chapter_id": "2", "title": "投資機能", "chapter_purpose": "判断を支える",
        "reader_outcome": "責務を説明できる", "included_child_sections": ["2.1"],
        "child_section_responsibilities": [{"section_id": "2.1", "responsibility": "候補探索"}],
        "explanation_order": ["探索", "評価"], "adjacent_chapter_boundaries": ["実行基盤は3章"],
        "allowed_cross_references": ["3.1"], "terminology_constraints": ["Human"],
        "representation_considerations": ["意味に応じて選択"], "unresolved_human_decisions": [],
    }


def test_writer_input_is_closed_and_preserves_contract() -> None:
    value = writer_input({"section_id": "2.1"}, contract(), cross_reference_metadata=[{"section_id": "3.1"}])
    assert set(value) == WRITER_INPUT_FIELDS
    assert value["chapter_contract"] == contract()
    assert "full_sdd" not in value and "other_section_text" not in value


def valid_output(**overrides: str) -> LLMWriterOutputArtifact:
    values = {
        "content": "Human-facing output", "writer_session_id": "run:chapter:2",
        "chapter_id": "2", "chapter_contract_digest": "contract-digest",
        "writer_input_digest": "input-digest", "producer_kind": LLM_PRODUCER,
        "generated_at": "2026-09-24T16:00:00+09:00", "provenance_version": PROVENANCE_VERSION,
    }
    values.update(overrides)
    return LLMWriterOutputArtifact(**values)


def accept_output(output: LLMWriterOutputArtifact) -> str:
    return validate_llm_output(
        output, expected_session_id="run:chapter:2", expected_chapter_id="2",
        expected_chapter_contract_digest="contract-digest", expected_writer_input_digest="input-digest",
    )


def test_valid_llm_output_artifact_passes() -> None:
    assert accept_output(valid_output()) == "Human-facing output"


@pytest.mark.parametrize(
    "change",
    [
        {"content": ""}, {"writer_session_id": ""}, {"writer_session_id": "wrong"},
        {"chapter_id": "3"}, {"chapter_contract_digest": "wrong"},
        {"writer_input_digest": "wrong"}, {"producer_kind": "PYTHON"},
        {"generated_at": "not-a-date"}, {"generated_at": "2026-09-24T16:00:00"},
        {"provenance_version": "99"},
    ],
)
def test_invalid_llm_output_provenance_fails(change: dict[str, str]) -> None:
    with pytest.raises((TypeError, ValueError)):
        accept_output(valid_output(**change))


def test_raw_string_is_not_writer_output() -> None:
    with pytest.raises(TypeError, match="raw strings"):
        accept_output("body")  # type: ignore[arg-type]


def test_chapter_contract_has_no_template_counts() -> None:
    assert validate_chapter_contract(contract()) == []
    bad = {**contract(), "fixed_table_count": 1}
    assert "template-counts-forbidden" in validate_chapter_contract(bad)


def test_active_writer_path_contains_no_renderer_or_fixed_body() -> None:
    assert scan_active_scripts(SKILL / "scripts") == []


def test_known_legacy_renderer_fails_guard() -> None:
    fixture = SKILL / "tests/fixtures/legacy-renderers/full_writer.py"
    assert scan_script(fixture)


def test_p0092_section_zero_is_known_bad() -> None:
    fixture = json.loads((SKILL / "tests/fixtures/p0092-known-bad.json").read_text("utf-8"))
    bad = (ROOT / fixture["path"]).read_text("utf-8")
    report = evaluate_human_facing(bad)
    assert report["status"] == "FAIL"
    assert {item["code"] for item in report["findings"]} & {"CONTEXT_FIELD_EXPOSURE", "WRITER_META_PROSE"}


def test_accepted_outputs_have_no_false_positive() -> None:
    paths = [
        ROOT / "validation/reports/argus-p-0110-v1/multi-section-poc/sections/section-1.2/writer-output.md",
        ROOT / "validation/reports/argus-p-0110-v1/multi-section-poc/sections/section-3.1/writer-output.md",
        ROOT / "validation/reports/argus-p-0096-v1/section-3.4.md",
        ROOT / "validation/reports/argus-p-0097-v1/section-3.5.md",
        ROOT / "validation/reports/argus-p-0098-v1/section-3.5.md",
        ROOT / "validation/reports/argus-p-0101-v1/section-3.5.2-en.md",
    ]
    assert all(evaluate_human_facing(path.read_text("utf-8"))["status"] == "PASS" for path in paths)


def test_corpus_gate_detects_mass_template_not_normal_similarity() -> None:
    repeated = ["## X\n\n### 同じ構成\n\n本文\n\n### 同じ終端\n\n本文\n"] * 10
    assert evaluate_corpus(repeated)["status"] == "FAIL"
    assert evaluate_corpus(repeated[:2])["status"] == "PASS"


def test_generalized_meta_prose_and_mermaid_convergence() -> None:
    meta = "この入力コンテキストフィールドを順番に処理して本文を生成する。"
    assert {item["code"] for item in evaluate_human_facing(meta)["findings"]} == {"WRITER_META_PROSE"}
    flow = "## X\n\n### 個別\n\n本文\n\n```mermaid\nflowchart LR\nA[開始] --> B[判定]\nB --> C[完了]\n```\n"
    findings = evaluate_corpus([flow] * 5)["findings"]
    assert "GENERIC_MERMAID_CONVERGENCE" in {item["code"] for item in findings}


def test_schema_artifact_is_closed() -> None:
    schema = json.loads((SKILL / "references/chapter-contract.schema.json").read_text("utf-8"))
    assert schema["additionalProperties"] is False


def test_writer_input_digest_requires_canonical_envelope() -> None:
    value = writer_input({"section_id": "2.1"}, contract())
    assert writer_input_digest(value)
    with pytest.raises(ValueError):
        writer_input_digest({**value, "full_sdd": "forbidden"})


def planning_artifact() -> dict[str, object]:
    return json.loads((ROOT / "validation/reports/argus-p-0087-v1/planning-artifact.json").read_text("utf-8"))


def approval(artifact: dict[str, object], **overrides: str) -> PlanningApproval:
    values = {
        "artifact_id": str(artifact["artifact_id"]), "planning_hash": str(artifact["planning_hash"]),
        "approved_by": "Human", "approved_at": "2026-09-24T16:00:00+09:00",
        "status": "APPROVED", "sdd_sha256": str(artifact["source_sdd_sha256"]),
    }
    values.update(overrides)
    return PlanningApproval(**values)


def test_canonical_authorization_accepts_bound_human_approval() -> None:
    artifact = planning_artifact()
    result = authorize_planning_artifact(artifact, approval(artifact), expected_sdd_sha256=str(artifact["source_sdd_sha256"]))
    assert result.approved_by == "Human"


@pytest.mark.parametrize(
    "approval_change,artifact_change,expected_sdd",
    [
        ({"status": "PENDING"}, {}, None), ({"status": "REJECTED"}, {}, None),
        ({"approved_by": "AI"}, {}, None), ({"planning_hash": "wrong"}, {}, None),
        ({"sdd_sha256": "wrong"}, {}, None), ({"approved_at": "bad"}, {}, None),
        ({"approved_at": ""}, {}, None), ({"approved_at": "2026-09-24T16:00:00"}, {}, None),
        ({"artifact_id": ""}, {}, None), ({}, {"source_sdd_sha256": "wrong"}, None),
        ({}, {}, "wrong"),
    ],
)
def test_canonical_authorization_fails_closed(
    approval_change: dict[str, str], artifact_change: dict[str, str], expected_sdd: str | None,
) -> None:
    artifact = planning_artifact()
    changed = deepcopy(artifact)
    changed.update(artifact_change)
    expected = expected_sdd or str(artifact["source_sdd_sha256"])
    with pytest.raises(PermissionError):
        authorize_planning_artifact(changed, approval(artifact, **approval_change), expected_sdd_sha256=expected)
