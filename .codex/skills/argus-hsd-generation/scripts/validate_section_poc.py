from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from human_facing_gate import evaluate_human_facing
from renderer_guard import scan_active_scripts
from section_writer_pipeline import SectionWriterOutputArtifact, validate_output

GENERAL_ENGLISH = ("Universe", "Filter", "Value", "Change", "Data", "Event")
FORBIDDEN_METADATA = ("Coverage ID", "SDD line", "semantic_kind", "source_locator", "assignment_status")


def validate_section(root: Path, section_id: str, report_dir: Path | None = None) -> dict[str, object]:
    report = report_dir or root / "validation/reports/argus-p-0096-v1"
    provenance = json.loads((report / f"section-{section_id}-provenance.json").read_text("utf-8"))
    artifact = SectionWriterOutputArtifact(
        **json.loads((report / f"section-{section_id}-writer-output.json").read_text("utf-8"))
    )
    expected = {
        "writer_session_id": provenance["writer_session_id"],
        "section_id": provenance["section_id"],
        "chapter_contract_digest": provenance["chapter_contract_digest"],
        "human_structure_plan_digest": provenance["human_structure_plan_digest"],
        "coverage_contract_digest": provenance["coverage_contract_digest"],
        "writer_input_digest": provenance["writer_input_digest"],
        "provenance_version": provenance["expected_provenance_version"],
    }
    content = validate_output(artifact, expected)
    if content != (report / f"section-{section_id}.md").read_text("utf-8"):
        raise ValueError("writer artifact content mismatch")
    findings: list[dict[str, str]] = []
    visible = re.sub(r"`[^`]+`", "", content)
    for word in GENERAL_ENGLISH:
        if re.search(rf"(?<![A-Za-z0-9_]){word}(?![A-Za-z0-9_])", visible):
            findings.append({"code": "FORBIDDEN_GENERAL_ENGLISH", "detail": word})
    for value in FORBIDDEN_METADATA:
        if value in content:
            findings.append({"code": "METADATA_LEAK", "detail": value})
    if re.search(r"^#{2,6}\s+[^\n]+\n\s*(?=#{2,6}\s|\Z)", content, re.MULTILINE):
        findings.append({"code": "EMPTY_HEADING", "detail": "empty heading"})
    renderer = [item.__dict__ for item in scan_active_scripts(root / ".codex/skills/argus-hsd-generation/scripts")]
    findings.extend({"code": "RENDERER_GUARD", "detail": item["path"]} for item in renderer)
    mechanical = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    human = evaluate_human_facing(content)
    (report / f"section-{section_id}-mechanical-gate.json").write_text(
        json.dumps(mechanical, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    (report / f"section-{section_id}-human-facing-gate.json").write_text(
        json.dumps(human, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    return {"provenance": "PASS", "mechanical": mechanical, "human_facing": human, "renderer_findings": len(renderer)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("section_id", choices=("3.4", "3.5"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    try:
        report_dir = args.report_dir.resolve() if args.report_dir else None
        print(json.dumps(validate_section(args.root.resolve(), args.section_id, report_dir), ensure_ascii=False, indent=2))
    except (ValueError, TypeError, PermissionError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
