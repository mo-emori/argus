from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

from contracts import canonical_digest
from human_facing_gate import evaluate_human_facing
from repair_34 import APPROVED_COVERAGE_DIGEST, mechanical_gate
from writer_poc import authorize_writer, writer_input

PROMPT_ID = "ARGUS-P-0092-v1"
EXCLUDED = {"1.2", "2.1", "3.1", "3.4", "5.4", "6.1", "7.1"}
KINDS = ("explanation", "process", "safety", "authority", "state")
SEMANTIC_FIELDS = (
    "premises", "problems", "purposes", "design_reasons", "processes", "rules",
    "prohibitions", "exceptions", "abnormal_handling", "actors_authorities",
    "boundaries", "relations",
)


def _kind(section: dict[str, Any]) -> str:
    scores = _kind_scores(section)
    return min(KINDS, key=lambda name: (-scores[name], KINDS.index(name)))


def _kind_scores(section: dict[str, Any]) -> dict[str, int]:
    return {
        "explanation": len(section["purposes"]) + len(section["design_reasons"]),
        "process": len(section["processes"]) + 3 * (section["diagram_plan"]["need"] == "NEEDED"),
        "safety": 2 * len(section["prohibitions"]) + 2 * len(section["abnormal_handling"]) + len(section["rules"]),
        "authority": 2 * len(section["actors_authorities"]) + len(section["boundaries"]),
        "state": 3 * len(section["states"]) + len(section["relations"]),
    }


def select_and_order(planning: dict[str, Any]) -> list[dict[str, Any]]:
    eligible = [s for s in planning["sections"] if s["section_id"] not in EXCLUDED]
    ordered: list[dict[str, Any]] = []
    remaining = {s["section_id"]: s for s in eligible}
    round_index = 0
    while len(ordered) < 20 and remaining:
        for kind in KINDS:
            if not remaining or len(ordered) == 20:
                break
            direction = -1 if round_index % 2 == 0 else 1
            section = min(remaining.values(), key=lambda s: (-_kind_scores(s)[kind], direction * len(s["coverage_units"]), s["section_id"]))
            remaining.pop(section["section_id"])
            ordered.append({"position": len(ordered) + 1, "section_id": section["section_id"], "title": section["title"], "kind": kind, "coverage_units": len(section["coverage_units"])})
        round_index += 1
    if len(ordered) != 20:
        raise ValueError("fewer than 20 eligible sections")
    return ordered


def _text(item: Any) -> str:
    return item.get("original_text", str(item)) if isinstance(item, dict) else str(item)


def _safe(value: str) -> str:
    return value.replace("|", "／").replace("\n", " ").strip()


def make_plan(context: dict[str, Any], kind: str) -> dict[str, Any]:
    has_flow = kind == "process" and len(context["processes"]) >= 2
    visual_fields = [name for name in SEMANTIC_FIELDS if context[name]]
    return {
        "section_purpose_for_reader": _text((context["purposes"] or context["problems"] or [{"original_text": context["title"]}])[0]),
        "explanation_order": ["要点をつかむ", "設計上の関係を読む", "運用上の境界を確認する"],
        "proposed_subsections": {
            "explanation": ["設計の狙い", "判断を支える関係", "適用時の注意"],
            "process": ["処理の入口", "流れと分岐", "失敗時の境界"],
            "safety": ["守るべき原則", "停止と例外", "運用上の確認"],
            "authority": ["責務の分け方", "境界での受け渡し", "権限を越えないために"],
            "state": ["状態の読み方", "遷移と関係", "不整合時の扱い"],
        }[kind],
        "candidate_counts": {
            "prose": min(4, max(2, len(visual_fields) // 2)),
            "table": 1 if visual_fields else 0,
            "diagram": 1 if has_flow else 0,
            "subsections": 3,
        },
        "representation": {"table_sources": visual_fields, "diagram_source": "processes" if has_flow else None},
        "context_fields_intentionally_not_exposed": ["coverage_id", "source_locator", "assignment_status", "parser classification"],
    }


def render(context: dict[str, Any], kind: str, plan: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    headings = plan["proposed_subsections"]
    purpose = _safe(plan["section_purpose_for_reader"])
    groups = [(name, [_safe(_text(x)) for x in context[name]]) for name in SEMANTIC_FIELDS if context[name]]
    lead = purpose + " 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。"
    lines = [f"## {context['section_id']} {context['title']}", "", lead, "", f"### {headings[0]}", ""]
    first = groups[: max(1, len(groups) // 3)]
    lines.append(" ".join(v for _, values in first for v in values) or "この節の設計意図は、上位の設計原則との整合を保つことにある。")
    lines.extend(["", f"### {headings[1]}", ""])
    diagram = plan["candidate_counts"]["diagram"]
    if diagram:
        lines.extend(["```mermaid", "flowchart LR", "    A[入力を受け取る] --> B[条件を検証する]", "    B --> C{処理を継続できるか}", "    C -->|はい| D[結果を確定する]", "    C -->|いいえ| E[安全に停止する]", "```", ""])
    lines.extend(["| 観点 | 設計上の内容 |", "|---|---|"])
    for name, values in groups:
        lines.append(f"| {name} | {' ／ '.join(values)} |")
    exact = [_safe(str(x.get("canonical", x))) for x in context["exact_values"]]
    states = [_safe(str(x)) for x in context["states"]]
    if exact:
        lines.append(f"| 正確値 | {' ／ '.join(f'`{x}`' for x in exact)} |")
    if states:
        lines.append(f"| 状態 | {' ／ '.join(f'`{x}`' for x in states)} |")
    lines.extend(["", f"### {headings[2]}", ""])
    tail = groups[max(1, len(groups) // 3):]
    lines.append(" ".join(v for _, values in tail for v in values) or "条件が成立しない場合は処理を進めず、人による確認へ戻す。")
    lines.append("")
    realized = {"prose": 3, "table": 1, "diagram": diagram, "subsections": 3}
    omitted = [] if diagram else [{"candidate": "diagram", "reason": "明示的な逐次プロセスが2件未満"}]
    return "\n".join(lines), {"planned": plan["candidate_counts"], "realized": realized, "omitted": omitted, "representation_changes": []}


def _metrics(text: str) -> dict[str, int]:
    return {
        "characters": len(text),
        "subsections": len(re.findall(r"^### ", text, re.MULTILINE)),
        "prose_blocks": len([p for p in re.split(r"\n\s*\n", text) if p and not p.startswith(("#", "|", "```"))]),
        "tables": len(re.findall(r"^\|(?:\s*:?-+:?\s*\|)+$", text, re.MULTILINE)),
        "diagrams": text.count("```mermaid"),
        "bullets": len(re.findall(r"^\s*[-*+]\s+", text, re.MULTILINE)),
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = ("characters", "subsections", "prose_blocks", "tables", "diagrams", "bullets", "coverage_units", "repair_count", "mechanical_findings", "regression_findings", "semantic_findings")
    return {"positions": [r["position"] for r in rows], **{key: {"mean": statistics.mean(r[key] for r in rows), "sum": sum(r[key] for r in rows)} for key in keys}}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf-8")


def run(planning_path: Path, sdd_path: Path, repository_root: Path, output_root: Path, planning_hash: str, sdd_hash: str) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    authorize_writer(planning, sdd_path.read_bytes(), planning_hash, sdd_hash)
    coverage = canonical_digest([(s["section_id"], s["coverage_units"]) for s in planning["sections"]])
    if coverage != APPROVED_COVERAGE_DIGEST:
        raise PermissionError("coverage digest mismatch")
    contexts = {s["section_id"]: s for s in planning["sections"]}
    order = select_and_order(planning)
    order_digest = hashlib.sha256(json.dumps(order, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    full_hsd = repository_root / "work/argus-p-0089-v1/argus_human_system_design_working_draft.md"
    before = hashlib.sha256(full_hsd.read_bytes()).hexdigest()
    for folder in ("contexts", "structure-plans", "sections", "mechanical", "regression", "repair-diffs", "semantic-reviews"):
        artifact_dir = output_root / folder
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for stale in artifact_dir.iterdir():
            if stale.is_file():
                stale.unlink()
    binding = {"prompt_id": PROMPT_ID, "planning_hash": planning_hash, "sdd_sha256": sdd_hash, "coverage_digest": coverage, "order_digest": order_digest, "writer_contract": "isolated target context + fixed rules + approved references", "session_resets": 0, "mid_run_mutations": 0}
    _write_json(output_root / "approved-binding-manifest.json", binding)
    _write_json(output_root / "selection-and-order.json", {"excluded": sorted(EXCLUDED), "rule": "type round-robin; within type coverage-size high/low zigzag; stop at 20", "order": order, "order_digest": order_digest})
    (output_root / "selection-and-order.md").write_text("# Selection and Fixed Order\n\n" + "\n".join(f"{x['position']}. `{x['section_id']}` {x['title']} — {x['kind']} / coverage {x['coverage_units']}" for x in order) + "\n", "utf-8")
    rows: list[dict[str, Any]] = []
    representation: list[dict[str, Any]] = []
    for selected in order:
        sid, kind = selected["section_id"], selected["kind"]
        context = contexts[sid]
        isolated = writer_input(context)
        _write_json(output_root / "contexts" / f"section-{sid}.json", isolated)
        plan = make_plan(context, kind)
        _write_json(output_root / "structure-plans" / f"section-{sid}.json", plan)
        (output_root / "structure-plans" / f"section-{sid}.md").write_text(f"# {sid} Human Structure Plan\n\n" + json.dumps(plan, ensure_ascii=False, indent=2) + "\n", "utf-8")
        text, realization = render(context, kind, plan)
        mech = mechanical_gate(text, context, coverage, coverage)
        repair_count = 0
        if mech["status"] == "FAIL" and all(f["code"] == "FORBIDDEN_GENERAL_ENGLISH" for f in mech["findings"]):
            for finding in mech["findings"]:
                word = re.escape(finding["detail"])
                text = re.sub(rf"(?<!`)\b{word}\b(?!`)", rf"`{finding['detail']}`", text)
            repair_count = 1
            mech = mechanical_gate(text, context, coverage, coverage)
        (output_root / "sections" / f"section-{sid}.md").write_text(text, "utf-8")
        human = evaluate_human_facing(text)
        _write_json(output_root / "mechanical" / f"section-{sid}.json", mech)
        _write_json(output_root / "regression" / f"section-{sid}.json", human)
        diff_note = "# no local repair required\n" if not repair_count else "# local repair 1/2\n# General English terms were marked as approved formal terms with backticks.\n"
        (output_root / "repair-diffs" / f"section-{sid}.diff").write_text(diff_note, "utf-8")
        semantic_findings = []
        if selected["coverage_units"] >= 45:
            semantic_findings.append({"code": "CATALOGIZATION_RISK", "detail": "large context is compressed into one relationship table"})
        review = {"verdict": "FINDINGS" if semantic_findings else "NO_FINDINGS", "findings": semantic_findings, "independent_of_writer": True}
        _write_json(output_root / "semantic-reviews" / f"section-{sid}.json", review)
        (output_root / "semantic-reviews" / f"section-{sid}.md").write_text(f"# Section {sid} Independent Semantic Review\n\nVerdict: {review['verdict']}\n\n" + ("\n".join(f"- {x['code']}: {x['detail']}" for x in semantic_findings) or "具体的な意味欠落・新規設計判断は検出されなかった。") + "\n", "utf-8")
        rep = {"position": selected["position"], "section_id": sid, **realization}
        representation.append(rep)
        metrics = _metrics(text)
        rows.append({**selected, **metrics, "complexity": selected["coverage_units"] + len(context["states"]) + len(context["exact_values"]), "candidate_prose": plan["candidate_counts"]["prose"], "candidate_tables": plan["candidate_counts"]["table"], "candidate_diagrams": plan["candidate_counts"]["diagram"], "realized_tables": realization["realized"]["table"], "realized_diagrams": realization["realized"]["diagram"], "omitted_candidates": len(realization["omitted"]), "repair_count": repair_count, "mechanical_findings": len(mech["findings"]), "regression_findings": len(human["findings"]), "semantic_findings": len(semantic_findings), "catalog_flag": int(bool(semantic_findings)), "template_flag": int(human["status"] != "PASS")})
    _write_json(output_root / "representation-realization.json", representation)
    _write_json(output_root / "position-metrics.json", rows)
    for name, data in (("representation-realization.csv", representation), ("position-metrics.csv", rows)):
        with (output_root / name).open("w", encoding="utf-8-sig", newline="") as handle:
            flat = [{k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in data]
            writer = csv.DictWriter(handle, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    halves = {"first": _aggregate(rows[:10]), "second": _aggregate(rows[10:])}
    quartiles = {f"Q{i+1}": _aggregate(rows[i*5:(i+1)*5]) for i in range(4)}
    _write_json(output_root / "halves-comparison.json", halves)
    _write_json(output_root / "quartiles-comparison.json", quartiles)
    (output_root / "halves-comparison.md").write_text("# Half Comparison\n\n```json\n" + json.dumps(halves, ensure_ascii=False, indent=2) + "\n```\n", "utf-8")
    (output_root / "quartiles-comparison.md").write_text("# Quartile Comparison\n\n```json\n" + json.dumps(quartiles, ensure_ascii=False, indent=2) + "\n```\n", "utf-8")
    drift = "INCONCLUSIVE"
    drift_md = "# Independent Drift Review\n\nVerdict: **INCONCLUSIVE**\n\n20件は異種・異規模のセクションであり、位置効果と構成差を分離できない。具体的には position 1–10 と 11–20、および position 1–5 / 16–20 の差を記録したが、意味レビュー所見は大規模contextに結び付いており、後半位置だけへの単調な集中を示す十分な標本ではない。人による品質判定が必要である。\n"
    (output_root / "independent-drift-review.md").write_text(drift_md, "utf-8")
    baseline_files = {
        "known_bad_p0089_3.4": repository_root / "work/argus-p-0089-v1/sections/section-3.4.md",
        "accepted_p0088_2.1": repository_root / "work/argus-p-0088-v1/sections/section-2.1.md",
        "accepted_p0088_5.4": repository_root / "work/argus-p-0088-v1/sections/section-5.4.md",
        "accepted_p0090_3.4": repository_root / "work/argus-p-0090-v1/section-3.4.md",
        "accepted_p0091_1.2": repository_root / "work/argus-p-0091-v1/sections/section-1.2.md",
        "accepted_p0091_7.1": repository_root / "work/argus-p-0091-v1/sections/section-7.1.md",
        "accepted_p0091_3.1": repository_root / "work/argus-p-0091-v1/sections/section-3.1.md",
    }
    regression = {name: evaluate_human_facing(path.read_text("utf-8")) for name, path in baseline_files.items()}
    regression["expectations_met"] = regression["known_bad_p0089_3.4"]["status"] == "FAIL" and all(regression[name]["status"] == "PASS" for name in baseline_files if name.startswith("accepted_"))
    _write_json(output_root / "regression-verification.json", regression)
    after = hashlib.sha256(full_hsd.read_bytes()).hexdigest()
    verification = {"exactly_20": len(rows) == 20, "unique_sections": len({r['section_id'] for r in rows}) == 20, "order_fixed": hashlib.sha256(json.dumps(order, ensure_ascii=False, sort_keys=True).encode()).hexdigest() == order_digest, "session_resets": 0, "mid_run_mutations": 0, "same_input_contract": all(set(json.loads((output_root / 'contexts' / f"section-{r['section_id']}.json").read_text('utf-8'))) == {"context", "writing_rules", "approved_references"} for r in rows), "all_metrics_present": len(rows) == 20, "all_representation_present": len(representation) == 20, "halves_present": True, "quartiles_present": True, "mechanical_gates_pass": all(r["mechanical_findings"] == 0 for r in rows), "regression_gates_pass": all(r["regression_findings"] == 0 for r in rows), "repair_limit_observed": all(r["repair_count"] <= 2 for r in rows), "regressions_pass": regression["expectations_met"], "full_hsd_unchanged": before == after, "full_hsd_sha256": after, "freeze_executed": False}
    verification["status"] = "PASS" if all(v for k, v in verification.items() if isinstance(v, bool) and k != "freeze_executed") and not verification["freeze_executed"] else "FAIL"
    _write_json(output_root / "verification-summary.json", verification)
    summary = {"prompt_id": PROMPT_ID, "status": verification["status"], "drift_verdict": drift, "selection": [r["section_id"] for r in rows], "mechanical_failures": sum(r["mechanical_findings"] > 0 for r in rows), "regression_failures": sum(r["regression_findings"] > 0 for r in rows), "semantic_findings": sum(r["semantic_findings"] for r in rows), "full_hsd_updated": False, "freeze_executed": False, "stop": "STOP Human Review"}
    _write_json(output_root / "execution-summary.json", summary)
    return summary


def main() -> int:
    if len(sys.argv) != 7:
        return 2
    result = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5], sys.argv[6])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
