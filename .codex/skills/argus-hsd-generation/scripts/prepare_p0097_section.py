from __future__ import annotations

import argparse
import json
from pathlib import Path

from section_writer_pipeline import (
    digest,
    make_writer_input,
    validate_coverage_contract,
    validate_distinct_sessions,
    validate_handoff,
)

SESSIONS = {
    "3.4": "ARGUS-P-0097-v1:section:3.4:writer:01",
    "3.5": "ARGUS-P-0097-v1:section:3.5:writer:01",
}


def prepare_section(
    root: Path,
    section_id: str,
    handoff_path: Path | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    source_report = root / "validation/reports/argus-p-0096-v1"
    report = root / "validation/reports/argus-p-0097-v1"
    repaired = json.loads((report / "repaired-section-contexts.json").read_text("utf-8"))
    context = next(item for item in repaired["sections"] if item["section_id"] == section_id)
    chapter_contract = json.loads((source_report / "chapter-contract.json").read_text("utf-8"))
    structure_plan = (source_report / "human-structure-plan.md").read_text("utf-8")
    coverage_path = report / f"section-{section_id}-coverage-contract.md"
    coverage_contract = coverage_path.read_text("utf-8")
    findings = validate_coverage_contract(coverage_contract)
    if findings:
        raise PermissionError(f"invalid Coverage Contract: {findings}")

    handoff = None
    if handoff_path is not None:
        handoff = json.loads(handoff_path.read_text("utf-8"))
        source_material = (report / "section-3.4.md").read_text("utf-8") + structure_plan
        handoff_findings = validate_handoff(handoff, "3.4", source_material)
        blocking = [item for item in handoff_findings if item != "HANDOFF_NEW_MEANING_REVIEW"]
        if blocking:
            raise PermissionError(f"invalid handoff: {blocking}")

    terminology_policy = (report / "terminology-policy.md").read_text("utf-8")
    writing_rules = [
        "Human-facing本文は日本語で書き、Contextの意味を上位概念へ一般化して欠落させない。",
        "Coverage Contractの各行を個別に満たし、主体、対象、条件、禁止、例外、失敗時挙動を保存する。",
        "複数の独立関係を、複数未満の曖昧な対応関係へ縮約しない。",
        "固定値、状態、条件、Authority、禁止、不変条件、例外、失敗・復旧挙動を個別に保存する。",
        "Coverage ID、SDD位置、Context field名、判定metadataをHuman-facing本文へ露出しない。",
        "Source/Contextにない意味を補完せず、不足時はCONTEXT_INSUFFICIENTを返す。",
        "図表と小節数は固定せず、意味構造から選ぶ。",
        "次のTerminology Policyを遵守する:\n" + terminology_policy,
    ]
    envelope = make_writer_input(
        chapter_contract,
        structure_plan,
        context,
        coverage_contract,
        writing_rules,
        [
            {"section_id": value, "scope": "within Major Chapter 3"}
            for value in ("3.4", "3.5")
            if value != section_id
        ],
        handoff,
    )
    if section_id == "3.5":
        validate_distinct_sessions(SESSIONS["3.4"], SESSIONS["3.5"])

    digests = {
        "chapter_contract_digest": digest(chapter_contract),
        "human_structure_plan_digest": digest(structure_plan),
        "coverage_contract_digest": digest(coverage_contract),
        "writer_input_digest": digest(envelope),
    }
    input_path = report / f"section-{section_id}-writer-input.json"
    input_path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", "utf-8")
    effective_session_id = session_id or SESSIONS[section_id]
    provenance = {
        "writer_session_id": effective_session_id,
        "section_id": section_id,
        **digests,
        "expected_producer_kind": "LLM_WRITER",
        "expected_provenance_version": "2",
        "session_start_method": "fresh delegated LLM session with no conversation-history fork",
        "input_artifact": str(input_path.relative_to(root)).replace("\\", "/"),
        "previous_completed_prose_supplied": False,
        "full_source_supplied": False,
    }
    (report / f"section-{section_id}-provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    return {"writer_session_id": effective_session_id, **digests}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("section_id", choices=sorted(SESSIONS))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--handoff", type=Path)
    parser.add_argument("--session-id")
    args = parser.parse_args()
    result = prepare_section(args.root.resolve(), args.section_id, args.handoff, args.session_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
