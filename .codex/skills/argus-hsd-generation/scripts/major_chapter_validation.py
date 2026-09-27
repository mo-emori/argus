from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from contracts import canonical_digest
from human_facing_gate import evaluate_human_facing
from renderer_guard import scan_active_scripts
from writer_boundary import LLMWriterOutputArtifact, validate_llm_output

FORBIDDEN_METADATA = (
    "coverage_id", "source_locator", "assignment_status", "semantic_kind",
    "planning_status", "absence_approvals",
)
GENERAL_ENGLISH = ("Universe", "Filter", "Value", "Change", "Data", "Event")


def _original_text(item: Any) -> str:
    return item.get("original_text", "") if isinstance(item, dict) else str(item)


def validate_run(output_root: Path, scripts_root: Path) -> dict[str, Any]:
    envelope = json.loads((output_root / "writer-input.json").read_text("utf-8"))
    expected = json.loads((output_root / "writer-session-provenance.json").read_text("utf-8"))
    artifact_data = json.loads((output_root / "writer-output-artifact.json").read_text("utf-8"))
    artifact = LLMWriterOutputArtifact(**artifact_data)
    content = validate_llm_output(
        artifact,
        expected_session_id=expected["writer_session_id"],
        expected_chapter_id=expected["expected_chapter_id"],
        expected_chapter_contract_digest=expected["chapter_contract_digest"],
        expected_writer_input_digest=expected["writer_input_digest"],
    )
    if content != (output_root / "major-chapter-3.md").read_text("utf-8"):
        raise ValueError("output artifact content does not match draft artifact")
    contexts = envelope["context"]["sections"]
    findings: list[dict[str, str]] = []
    for context in contexts:
        for value in context["exact_values"]:
            canonical = str(value.get("canonical", ""))
            if canonical and canonical not in content:
                findings.append({"code": "MISSING_EXACT_VALUE", "detail": canonical})
        for state in context["states"]:
            for token in str(state).split(" / "):
                if token and token not in content:
                    findings.append({"code": "MISSING_FORMAL_STATE", "detail": token})
    visible = re.sub(r"`[^`]+`", "", content)
    for word in GENERAL_ENGLISH:
        if re.search(rf"(?<![A-Za-z0-9_]){word}(?![A-Za-z0-9_])", visible):
            findings.append({"code": "FORBIDDEN_GENERAL_ENGLISH", "detail": word})
    for field in FORBIDDEN_METADATA:
        if field in content:
            findings.append({"code": "METADATA_LEAK", "detail": field})
    if re.search(r"^#{2,6}\s+[^\n]+\n\s*(?=#{2,6}\s|\Z)", content, re.MULTILINE):
        findings.append({"code": "EMPTY_HEADING", "detail": "empty heading"})
    renderer_findings = [item.__dict__ for item in scan_active_scripts(scripts_root)]
    findings.extend({"code": "RENDERER_GUARD", "detail": item["path"]} for item in renderer_findings)
    mechanical = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    human = evaluate_human_facing(content)
    (output_root / "provenance-validation.json").write_text(
        json.dumps({"status": "PASS", "expected_source": "pre-generation orchestration artifact", "artifact": artifact_data}, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    (output_root / "mechanical-gate.json").write_text(json.dumps(mechanical, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "human-facing-gate.json").write_text(json.dumps(human, ensure_ascii=False, indent=2) + "\n", "utf-8")
    coverage_rows: list[dict[str, str]] = []
    for context in contexts:
        for unit in context["coverage_units"]:
            meaning = _original_text(unit)
            status = "PRESERVED" if meaning and meaning in content else "REVIEW"
            coverage_rows.append({
                "coverage_id": unit["coverage_id"], "source_locator": unit["source_locator"],
                "meaning": meaning, "placement": context["section_id"], "representation": "prose/table/diagram inspection",
                "status": status, "note": "exact textual preservation" if status == "PRESERVED" else "semantic preservation requires independent review",
            })
    lines = ["# Major Chapter 3 Coverage Inspection", "", "| Coverage ID | SDD位置 | 設計意味 | HSD配置先 | 表現 | Coverage判定 | 備考 |", "|---|---|---|---|---|---|---|"]
    for row in coverage_rows:
        cells = [str(row[key]).replace("|", "／").replace("\n", " ") for key in ("coverage_id", "source_locator", "meaning", "placement", "representation", "status", "note")]
        lines.append("| " + " | ".join(cells) + " |")
    (output_root / "coverage-map.md").write_text("\n".join(lines) + "\n", "utf-8")
    lines = [
        "# Major Chapter 3 Coverage Inspection",
        "",
        "| Coverage ID | SDD位置 | 設計意味 | HSD配置先 | 表現 | Coverage判定 | 備考 |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in coverage_rows:
        cells = [
            str(row[key]).replace("|", "／").replace("\n", " ")
            for key in ("coverage_id", "source_locator", "meaning", "placement", "representation", "status", "note")
        ]
        lines.append("| " + " | ".join(cells) + " |")
    (output_root / "coverage-map.md").write_text("\n".join(lines) + "\n", "utf-8")
    return {
        "provenance": "PASS", "mechanical": mechanical, "human_facing": human,
        "coverage": {name: sum(row["status"] == name for row in coverage_rows) for name in ("PRESERVED", "REFERENCED", "REVIEW")},
        "coverage_digest": canonical_digest([(item["section_id"], item["coverage_units"]) for item in contexts]),
        "renderer_findings": len(renderer_findings),
    }
