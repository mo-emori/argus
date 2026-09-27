from __future__ import annotations

import json
import re
from pathlib import Path

from section_writer_pipeline import digest, make_writer_input

ROOT = Path(__file__).resolve().parents[4]
P97 = ROOT / "validation/reports/argus-p-0097-v1"
P96 = ROOT / "validation/reports/argus-p-0096-v1"
OUT = ROOT / "validation/reports/argus-p-0101-v1"
BASE_IDS = {"SDD-L1141", "SDD-L1149", *(f"SDD-L{line}" for line in range(1152, 1166))}
COLLECTIONS = (
    "premises", "problems", "purposes", "design_reasons", "processes", "rules",
    "prohibitions", "exceptions", "abnormal_handling",
)


def base_id(value: str) -> str:
    return re.sub(r"-[a-z][a-z0-9]*$", "", value)


payload = json.loads((P97 / "repaired-section-contexts.json").read_text("utf-8"))
full_context = next(item for item in payload["sections"] if item["section_id"] == "3.5")
context = {key: value for key, value in full_context.items() if key not in COLLECTIONS}
for collection in COLLECTIONS:
    context[collection] = [item for item in full_context.get(collection, []) if item["coverage_id"] in BASE_IDS]
context["section_id"] = "3.5.2"
context["title"] = "Application Log"

contract_lines = (P97 / "section-3.5-coverage-contract.md").read_text("utf-8").splitlines()
selected = []
for line in contract_lines:
    if not line.startswith("|") or line.startswith(("| Coverage ID", "|---")):
        continue
    coverage_id = line.split("|", 2)[1].strip()
    if base_id(coverage_id) in BASE_IDS:
        selected.append(line)
contract = "\n".join([
    "# Section 3.5.2 Application Log Coverage Contract", "",
    "| Coverage ID | SDD位置 | 設計意味 | 保存必須要素 | 関係対象 | 許容表現 | HSD配置先 | 判定 | 備考 |",
    "|---|---|---|---|---|---|---|---|---|", *selected, "",
])

chapter = json.loads((P96 / "chapter-contract.json").read_text("utf-8"))
structure = """# English Semantic Draft Structure

Explain Application Log as an independent Human-facing unit. Establish its boundary from Canonical State, Fact, Event, and Audit Record; then cover rotation and retention, isolated write failure, forbidden sensitive content, environment separation, and unresolved implementation choices. Preserve every condition and unknown without summarizing or resolving it. Choose prose, tables, or lists according to semantic need; do not expose Coverage metadata.
"""
rules = [
    "Write the Human-facing semantic draft in clear technical English.",
    "Preserve every Coverage meaning, subject, target, condition, prohibition, failure behavior, and unresolved item independently.",
    "Keep Formal Identifiers, paths, state names, enum literals, and API fields unchanged.",
    "Do not add, delete, summarize, generalize, translate into Japanese, or resolve TBD items.",
    "Do not expose Coverage IDs, SDD locations, parser fields, or assignment metadata.",
    "Return CONTEXT_INSUFFICIENT instead of inventing missing design meaning.",
]
envelope = make_writer_input(chapter, structure, context, contract, rules, [{"section_id": "3.5", "scope": "parent section only"}])
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "section-3.5.2-writer-input.json").write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", "utf-8")
provenance = {
    "writer_session_id": "ARGUS-P-0101-v1:section:3.5.2:writer:01",
    "section_id": "3.5.2",
    "chapter_contract_digest": digest(chapter),
    "human_structure_plan_digest": digest(structure),
    "coverage_contract_digest": digest(contract),
    "writer_input_digest": digest(envelope),
    "expected_producer_kind": "LLM_WRITER",
    "expected_provenance_version": "2",
    "previous_completed_prose_supplied": False,
    "full_source_supplied": False,
}
(OUT / "section-3.5.2-writer-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8")
print(json.dumps({**provenance, "coverage_units": len(selected)}, ensure_ascii=False, indent=2))
