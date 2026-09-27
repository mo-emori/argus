from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _short(items: list[dict[str, Any]], limit: int = 2) -> str:
    values = [str(item["original_text"]).replace("|", "\\|")[:100] for item in items[:limit]]
    return " / ".join(values) if values else "—"


def render(artifact: dict[str, Any]) -> str:
    summary = artifact["summary"]
    lines = [
        "# ARGUS HSD Planning Artifact v0.1",
        "",
        f"- Artifact ID: `{artifact['artifact_id']}`",
        f"- Planning hash: `{artifact['planning_hash']}`",
        f"- SDD SHA-256: `{artifact['source_sdd_sha256']}`",
        f"- Approval: **{artifact['approval_status']}**",
        f"- Stop: **{artifact['stop']}**",
        "",
        "## Summary",
        "",
        f"- Section Context: {summary['section_contexts']}",
        f"- Coverage Unit: {summary['coverage_units']}",
        f"- Planning FAIL / WARNING / REVIEW_REQUIRED: {summary['planning_failures']} / {summary['planning_warnings']} / {summary['planning_reviews']}",
        f"- Design reason sections / Premise sections: {summary['design_reason_sections']} / {summary['premise_sections']}",
        f"- Semantic candidates / Confirmed states: {summary['semantic_candidates']} / {summary['semantic_confirmed_states']}",
        f"- Assignment REVIEW_REQUIRED: {summary['assignment_review_required']}",
        f"- Diagram NEEDED / REVIEW / NOT_NEEDED: {summary['diagram_plan'].get('NEEDED', 0)} / {summary['diagram_plan'].get('REVIEW', 0)} / {summary['diagram_plan'].get('NOT_NEEDED', 0)}",
        "",
        "## Section Overview",
        "",
        "| ID | Section | P | Problem | Purpose | Reason | Exact | State | Candidate | Actor | Boundary | Coverage | Assignment Review | Owner | Diagram | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for section in artifact["sections"]:
        lines.append(
            f"| {section['section_id']} | {section['title']} | {len(section['premises'])} | "
            f"{len(section['problems'])} | {len(section['purposes'])} | {len(section['design_reasons'])} | "
            f"{len(section['exact_values'])} | {len(section['states'])} | {len(section['semantic_candidates'])} | {len(section['actors_authorities'])} | "
            f"{len(section['boundaries'])} | {len(section['coverage_units'])} | {sum(item['assignment_status'] == 'REVIEW_REQUIRED' for item in section['coverage_units'])} | {section['primary_owner']} | "
            f"{section['diagram_plan']['need']} | {section['planning_status']} |"
        )
    lines.extend(["", "## Section Details", ""])
    for section in artifact["sections"]:
        exact = ", ".join(item["canonical"] for item in section["exact_values"][:12]) or "—"
        locators = ", ".join(section["source_locators"][:12]) or "—"
        unresolved = ", ".join(section["unresolved"]) or "—"
        coverage = ", ".join(item["coverage_id"] for item in section["coverage_units"][:12]) or "—"
        lines.extend([
            f"### {section['section_id']} {section['title']}", "",
            f"- Problem: {_short(section['problems'])}",
            f"- Purpose: {_short(section['purposes'])}",
            f"- Exact values: {exact}",
            f"- Assignment review: {sum(item['assignment_status'] == 'REVIEW_REQUIRED' for item in section['coverage_units'])}",
            f"- Semantic review: {sum(item['disposition'] == 'REVIEW_REQUIRED' for item in section['semantic_candidates'])} review / {sum(item['disposition'] == 'REJECTED' for item in section['semantic_candidates'])} rejected",
            f"- Major coverage: {coverage}",
            f"- Source locators: {locators}",
            f"- Cross references: {', '.join(section['cross_references']) or '—'}",
            f"- Unresolved: {unresolved}",
            f"- Diagram: {section['diagram_plan']['need']} / {section['diagram_plan']['candidate_type']} / {section['diagram_plan']['reason']}",
            "",
        ])
    reconciliation = artifact.get("coverage_reconciliation", {})
    if reconciliation:
        lines.extend([
            "## Coverage Reconciliation", "",
            f"- Baseline / Current / Delta: {reconciliation['baseline_units']} / {reconciliation['current_units']} / {reconciliation['delta']}",
            f"- Dispositions: {reconciliation['dispositions']}",
            f"- MISSING: {reconciliation['missing']}", "",
        ])
    lines.extend(["## Human Review", "", "配置、assignment confidence、semantic candidate、coverage reconciliation、primary owner、cross reference、diagram planを確認し、承認する場合は別のmachine-readable approval artifactでplanning hashを指定する。本Artifact自身はPENDINGであり、Codexは承認しない。", "", "**STOP Human Review**", ""])
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_planning.py <planning.json> <planning.md>", file=sys.stderr)
        return 2
    artifact = json.loads(Path(sys.argv[1]).read_text("utf-8"))
    Path(sys.argv[2]).write_text(render(artifact), "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
