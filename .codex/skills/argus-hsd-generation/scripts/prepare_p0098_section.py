from __future__ import annotations

import json
from pathlib import Path

from section_writer_pipeline import digest, validate_writer_input

ROOT = Path(__file__).resolve().parents[4]
P97 = ROOT / "validation/reports/argus-p-0097-v1"
P98 = ROOT / "validation/reports/argus-p-0098-v1"

source = json.loads((P97 / "section-3.5-writer-input.json").read_text("utf-8"))
source["human_structure_plan"] = (P98 / "section-3.5-structure-review.md").read_text("utf-8")
source["section_coverage_contract"] = (P97 / "section-3.5-coverage-contract.md").read_text("utf-8")
source["writing_rules"].extend(
    [
        "P-0097完成本文をtemplateとして使わず、局所structure planに従ってSection 3.5を再生成する。",
        "3.5.3の既存意味・順序・表内容は変えず、前段分割に伴う見出し番号のみ変更する。",
        "Section 3.5の66 Coverage Unitを減らさず、新しい設計意味を追加しない。",
    ]
)
findings = validate_writer_input(source, "3.5")
if findings:
    raise PermissionError(findings)

P98.mkdir(parents=True, exist_ok=True)
input_path = P98 / "section-3.5-writer-input.json"
input_path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", "utf-8")
provenance = {
    "writer_session_id": "ARGUS-P-0098-v1:section:3.5:writer:01",
    "section_id": "3.5",
    "chapter_contract_digest": digest(source["chapter_contract"]),
    "human_structure_plan_digest": digest(source["human_structure_plan"]),
    "coverage_contract_digest": digest(source["section_coverage_contract"]),
    "writer_input_digest": digest(source),
    "expected_producer_kind": "LLM_WRITER",
    "expected_provenance_version": "2",
    "session_start_method": "fresh delegated LLM session with no conversation-history fork",
    "input_artifact": "validation/reports/argus-p-0098-v1/section-3.5-writer-input.json",
    "previous_completed_prose_supplied": False,
    "full_source_supplied": False,
}
(P98 / "section-3.5-provenance.json").write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8"
)
print(json.dumps(provenance, ensure_ascii=False, indent=2))
