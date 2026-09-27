from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from planning_v2 import PlanningApproval, authorize_planning_artifact
from section_writer_pipeline import (
    digest,
    make_writer_input,
    validate_coverage_contract,
    validate_distinct_sessions,
    validate_handoff,
)

SESSIONS = {
    "3.4": "ARGUS-P-0096-v1:section:3.4:writer:01",
    "3.5": "ARGUS-P-0096-v1:section:3.5:writer:01",
}


def prepare_section(
    root: Path,
    section_id: str,
    handoff_path: Path | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    report = root / "validation/reports/argus-p-0096-v1"
    planning_path = root / "validation/reports/argus-p-0087-v1/planning-artifact.json"
    sdd_path = root / "docs/model/argus_structured_design_data_v0.1.md"
    approval_path = root / "validation/reports/argus-p-0095-v1/planning-approval.json"
    planning = json.loads(planning_path.read_text("utf-8"))
    approval = PlanningApproval(**json.loads(approval_path.read_text("utf-8")))
    sdd_sha = hashlib.sha256(sdd_path.read_bytes()).hexdigest()
    authorize_planning_artifact(planning, approval, expected_sdd_sha256=sdd_sha)

    context = next(item for item in planning["sections"] if item["section_id"] == section_id)
    chapter_contract = json.loads((report / "chapter-contract.json").read_text("utf-8"))
    structure_plan = (report / "human-structure-plan.md").read_text("utf-8")
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

    writing_rules = [
        "Human向け日本語で、Context field順ではなく意味上の理解順に組み換える。",
        "Coverage Contractの各独立Unitを上位概念への一般化だけで充足したとみなさない。",
        "N個の独立対応関係をN個未満の曖昧な対応関係へ縮約しない。",
        "固定値、状態、条件、Authority、禁止、不変条件、例外、失敗・復旧挙動を個別に保存する。",
        "表形式のCoverage Unitは、定義・区分・意味・禁止/境界・利用先・参照先の各対応を落とさず保存する。",
        "Coverage Contractの各行を生成後に照合し、説明済みの上位概念があっても個別Unitを省略しない。",
        "Coverage ID、SDD位置、Context field名、判定metadataをHuman-facing本文へ露出しない。",
        "Source/Contextにない意味を補完せず、Context不足ならCONTEXT_INSUFFICIENTを返す。",
        "図表と小節数は固定せず意味構造から選ぶ。",
    ]
    envelope = make_writer_input(
        chapter_contract,
        structure_plan,
        context,
        coverage_contract,
        writing_rules,
        [{"section_id": value, "scope": "within Major Chapter 3"} for value in ("3.4", "3.5") if value != section_id],
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
