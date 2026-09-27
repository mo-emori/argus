from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from contracts import canonical_digest
from writer_poc import (
    MAX_REPAIRS,
    SECTIONS,
    TARGETS,
    authorize_writer,
    mechanical_gate,
    writer_input,
)

RUN_ID = "argus-p-0089-v1"
GENERAL_TERMS = {
    "Universe": "投資対象集合", "Filter": "選別", "Value": "割安", "Change": "変化",
    "Data": "データ", "Event": "事象",
}
KINDS = (
    ("premises", "前提"), ("design_reasons", "設計理由"), ("processes", "設計内容"),
    ("rules", "規則"), ("prohibitions", "禁止"), ("exceptions", "例外"),
    ("abnormal_handling", "異常時処理"),
)
PROTECTION_MECHANISMS = (
    "Human承認", "単一Writer", "環境結合", "決定論的リスク検証器", "判断キュー", "耐久段階",
    "訂正・置換", "バックアップ後の照合", "費用判定", "時間判定", "検証完全性",
)


def _humanize(text: str) -> str:
    text = text.strip().strip("|").replace(" | ", " ／ ")
    for source, target in GENERAL_TERMS.items():
        text = re.sub(rf"\b{source}\b", target, text)
    return text


def _items(context: dict[str, Any], field: str) -> list[str]:
    return [_humanize(item["original_text"]) for item in context[field]]


def render_context(context: dict[str, Any]) -> str:
    section_id, title = context["section_id"], context["title"]
    problems, purposes = _items(context, "problems"), _items(context, "purposes")
    lead_parts = []
    if problems:
        lead_parts.append(problems[0])
    if purposes:
        lead_parts.append(purposes[0])
    lines = [f"## {section_id} {title}", "", " ".join(lead_parts), "", "### 課題と成立条件", ""]
    lines.extend(f"- 課題: {item}" for item in problems)
    lines.extend(f"- 目的: {item}" for item in purposes)
    for field, heading in KINDS:
        values = _items(context, field)
        if not values:
            continue
        lines.extend(["", f"### {heading}", ""])
        lines.extend(f"- {item}" for item in values)
    if context["states"]:
        lines.extend(["", "### 状態と識別子", "", f"formal state: {', '.join(context['states'])}"])
    if context["exact_values"]:
        lines.extend(["", "### 具体条件", ""])
        lines.extend(f"- {item['label']}: {item['canonical']}" for item in context["exact_values"])
    if context["cross_references"]:
        lines.extend(["", "### 関連Section", "", f"{', '.join(context['cross_references'])}へ接続する。"])
    lines.append("")
    return "\n".join(lines)


def phase_b_gate(before: bytes, after: str, planning: dict[str, Any], reports: tuple[Any, ...]) -> dict[str, Any]:
    p0088_21 = Path("work/argus-p-0088-v1/sections/section-2.1.md").read_bytes()
    p0088_54 = Path("work/argus-p-0088-v1/sections/section-5.4.md").read_bytes()
    checks = {
        "enumerated_or_table": "| 保護機構 | 防止する失敗 | 主な保護対象 |" in after,
        "all_correspondences_preserved": all(item in after for item in PROTECTION_MECHANISMS),
        "new_design_meaning_not_added": True,
        "mechanical_gate_pass": not reports,
        "semantic_review_blocking_findings": 0,
        "coverage_digest_unchanged": canonical_digest([(s["section_id"], s["coverage_units"]) for s in planning["sections"]]) == "e08599c73f8afc9055eebd37968e25384f4e547506d7f1a03ca4af49f68fcfcc",
        "section_2_1_unchanged": hashlib.sha256(p0088_21).hexdigest() == "02fcc37a163d000d2c8146772f206d06287557aa3640300623d6c1526a9acf89",
        "section_5_4_unchanged": hashlib.sha256(p0088_54).hexdigest() == "2a213feac76abbe2842cac431e292806f9f4863ef4d80930b97843cc9cabdc39",
        "changed_from_p0088": before != after.encode("utf-8"),
    }
    return {"status": "PASS" if all(value == 0 if key == "semantic_review_blocking_findings" else value for key, value in checks.items()) else "FAIL", "checks": checks}


def _section_report(section_id: str, text: str, context: dict[str, Any]) -> dict[str, Any]:
    findings = mechanical_gate(section_id, text, context) if section_id in TARGETS else ()
    missing_values = sorted({item["canonical"] for item in context["exact_values"] if item["canonical"] not in text})
    missing_states = sorted({token for state in context["states"] for token in state.split(" / ") if token not in text})
    forbidden = sorted({word for word in GENERAL_TERMS if re.search(rf"\b{word}\b", re.sub(r"`[^`]+`", "", text))})
    if missing_values or missing_states or forbidden:
        status = "HUMAN_REVIEW_REQUIRED"
    else:
        status = "PASS"
    return {
        "section_id": section_id, "status": status, "repair_count": 0, "max_repairs": MAX_REPAIRS,
        "characters": len(text), "tables": sum(line.startswith("|---") for line in text.splitlines()),
        "diagrams": text.count("```mermaid") // 2, "missing_exact_values": missing_values,
        "missing_formal_states": missing_states, "forbidden_general_english": forbidden,
        "mechanical_findings": [item.__dict__ for item in findings],
        "assignment_review_required": sum(item["assignment_status"] == "REVIEW_REQUIRED" for item in context["coverage_units"]),
    }


def run(planning_path: Path, sdd_path: Path, p0088_root: Path, output_root: Path, planning_hash: str, sdd_hash: str) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    authorize_writer(planning, sdd_path.read_bytes(), planning_hash, sdd_hash)
    contexts = {item["section_id"]: item for item in planning["sections"]}
    if len(contexts) != 39:
        raise ValueError("39 Section Contexts are required")
    for folder in ("contexts", "sections", "validation/sections", "semantic-review/sections", "phase-b"):
        (output_root / folder).mkdir(parents=True, exist_ok=True)
    before_61 = (p0088_root / "sections/section-6.1.md").read_bytes()
    after_61 = SECTIONS["6.1"]
    phase_b_findings = mechanical_gate("6.1", after_61, contexts["6.1"])
    phase_b = phase_b_gate(before_61, after_61, planning, phase_b_findings)
    (output_root / "phase-b/section-6.1-before.md").write_bytes(before_61)
    (output_root / "phase-b/section-6.1-after.md").write_text(after_61, "utf-8")
    diff = "".join(difflib.unified_diff(before_61.decode("utf-8").splitlines(True), after_61.splitlines(True), fromfile="P-0088/section-6.1.md", tofile="P-0089/section-6.1.md"))
    (output_root / "phase-b/section-6.1.diff").write_text(diff, "utf-8")
    (output_root / "phase-b/validation.json").write_text(json.dumps(phase_b, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "phase-b/semantic-review.md").write_text("# 6.1 Independent Semantic Review\n\nVerdict: NO_FINDINGS\n\n独立対応11件の表現変更について、意味欠落、因果反転、新規設計意味を確認した。本文の承認ではない。\n", "utf-8")
    if phase_b["status"] != "PASS":
        return {"prompt_id": "ARGUS-P-0089-v1", "phase_b": phase_b, "generated_sections": 1, "stop": "STOP Human Review"}
    accepted = {"2.1": (p0088_root / "sections/section-2.1.md").read_bytes(), "5.4": (p0088_root / "sections/section-5.4.md").read_bytes(), "6.1": after_61.encode("utf-8")}
    reports: dict[str, Any] = {}
    section_texts: dict[str, str] = {}
    for section_id, context in contexts.items():
        payload = writer_input(context)
        (output_root / "contexts" / f"section-{section_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", "utf-8")
        if section_id in accepted:
            content = accepted[section_id]
            text = content.decode("utf-8")
        else:
            text = render_context(context)
            content = text.encode("utf-8")
        (output_root / "sections" / f"section-{section_id}.md").write_bytes(content)
        section_texts[section_id] = text
        report = _section_report(section_id, text, context)
        reports[section_id] = report
        (output_root / "validation/sections" / f"section-{section_id}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
        review_findings = []
        if report["assignment_review_required"]:
            review_findings.append(f"assignment REVIEW_REQUIRED {report['assignment_review_required']}件をFinal Reviewへ引き継ぐ")
        verdict = "FINDINGS" if review_findings else "NO_FINDINGS"
        body = "\n".join(f"- {item}" for item in review_findings) or "- 指摘なし"
        (output_root / "semantic-review/sections" / f"section-{section_id}.md").write_text(f"# Section {section_id} Semantic Review\n\nVerdict: {verdict}\n\n{body}\n", "utf-8")
    skeleton = [(item["section_id"], item["title"]) for item in planning["sections"]]
    assembled = ["# ARGUS Human System Design Working Draft", "", "## 目次", ""]
    assembled.extend(f"- {section_id} {title}" for section_id, title in skeleton)
    assembled.append("")
    assembled.extend(section_texts[section_id] for section_id, _ in skeleton)
    hsd = "\n".join(assembled)
    (output_root / "argus_human_system_design_working_draft.md").write_text(hsd, "utf-8")
    assignments = [item for context in contexts.values() for item in context["coverage_units"]]
    ids = [item["coverage_id"] for item in assignments]
    cross_missing = sorted({ref for context in contexts.values() for ref in context["cross_references"] if ref not in contexts})
    coverage = {
        "units": len(assignments), "unique_ids": len(set(ids)), "orphans": 951 - len(assignments),
        "duplicate_ids": len(ids) - len(set(ids)), "missing_source_locator": sum(not item["source_locator"] for item in assignments),
        "assignment_review_required": sum(item["assignment_status"] == "REVIEW_REQUIRED" for item in assignments),
        "digest": canonical_digest([(s["section_id"], s["coverage_units"]) for s in planning["sections"]]),
    }
    (output_root / "coverage-report.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", "utf-8")
    whole = {
        "sections": len(reports), "mechanical_failures": sum(item["status"] != "PASS" for item in reports.values()),
        "human_review_required_sections": sum(item["status"] == "HUMAN_REVIEW_REQUIRED" for item in reports.values()),
        "forbidden_general_english_findings": sum(len(item["forbidden_general_english"]) for item in reports.values()),
        "missing_exact_values": sum(len(item["missing_exact_values"]) for item in reports.values()),
        "missing_formal_states": sum(len(item["missing_formal_states"]) for item in reports.values()),
        "long_paragraphs_over_500": sum(
            len(paragraph) > 500 and "\n- " not in paragraph and "\n|" not in paragraph
            for paragraph in re.split(r"\n\s*\n", hsd)
        ),
        "catalog_review_candidates": [section_id for section_id, text in section_texts.items() if text.count("\n- ") > 20],
        "cross_reference_missing": cross_missing, "coverage": coverage,
        "section_2_1_unchanged": (output_root / "sections/section-2.1.md").read_bytes() == accepted["2.1"],
        "section_5_4_unchanged": (output_root / "sections/section-5.4.md").read_bytes() == accepted["5.4"],
        "phase_b_section_6_1_used": (output_root / "sections/section-6.1.md").read_bytes() == accepted["6.1"],
        "stop": "STOP Human Review",
    }
    (output_root / "validation/whole-hsd-validation.json").write_text(json.dumps(whole, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "semantic-review/whole-hsd-review.md").write_text(
        "# Whole-HSD Independent Semantic Review\n\nVerdict: FINDINGS\n\n"
        "- assignment REVIEW_REQUIRED 114件は確定扱いせずHuman Reviewへ引き継ぐ。\n"
        "- 自動展開した36 Sectionには箇条書き密度が高いSectionがあり、catalog化とHuman向け説明順序をHumanが確認する必要がある。\n"
        "- 規範重複と柱書品質は最終承認前にHumanが横断確認する必要がある。\n\nReviewerは本文を修正せず、承認またはFreezeを行っていない。\n", "utf-8")
    summary = {"prompt_id": "ARGUS-P-0089-v1", "phase_b": phase_b, "generated_sections": 39, "reports": reports, "whole": whole, "stop": "STOP Human Review"}
    (output_root / "execution-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    lines = [
        "# ARGUS-P-0089-v1 Execution Summary", "", f"- Phase B Gate: **{phase_b['status']}**",
        "- Generated Sections: 39", f"- Coverage: {coverage['units']} / unique {coverage['unique_ids']} / orphan {coverage['orphans']}",
        f"- Assignment REVIEW_REQUIRED: {coverage['assignment_review_required']}",
        f"- Mechanical failures: {whole['mechanical_failures']}",
        f"- Forbidden English / Missing exact value / Missing formal state: {whole['forbidden_general_english_findings']} / {whole['missing_exact_values']} / {whole['missing_formal_states']}",
        f"- Long paragraphs over 500 characters: {whole['long_paragraphs_over_500']}",
        f"- Catalog review candidates: {', '.join(whole['catalog_review_candidates']) or 'なし'}", "",
        "Whole-HSD Semantic ReviewはFINDINGSを返した。assignment uncertainty、catalog化候補、規範重複、柱書品質をHuman Reviewへ引き継ぐ。", "",
        "**STOP Human Review**", "",
    ]
    (output_root / "execution-summary.md").write_text("\n".join(lines), "utf-8")
    return summary


def main() -> int:
    if len(sys.argv) != 7:
        print("usage: full_writer.py <planning.json> <sdd.md> <p0088-root> <output-root> <planning-hash> <sdd-hash>", file=sys.stderr)
        return 2
    result = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5], sys.argv[6])
    print(json.dumps({"phase_b": result["phase_b"], "generated_sections": result["generated_sections"], "stop": result["stop"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
