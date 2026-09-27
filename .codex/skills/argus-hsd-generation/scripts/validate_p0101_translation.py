from __future__ import annotations

import json
from pathlib import Path

from translation_preservation_gate import evaluate_translation
from translation_stage import (
    StructureLock,
    TranslationContract,
    TranslationOutput,
    validate_translation_output,
)

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0101-v1"
contract_data = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text("utf-8"))
contract_data["structure_lock"] = StructureLock(**contract_data["structure_lock"])
for key in (
    "protected_identifiers", "protected_literals", "protected_state_names", "protected_paths",
    "protected_numeric_values", "terminology_rules",
):
    contract_data[key] = tuple(contract_data[key])
contract = TranslationContract(**contract_data)
output = TranslationOutput(**json.loads((REPORT / "section-3.5.2-translation-output.json").read_text("utf-8")))
source = (REPORT / "section-3.5.2-en.md").read_text("utf-8")
target = (REPORT / "section-3.5.2-ja.md").read_text("utf-8")
provenance_findings = validate_translation_output(output, contract, "ARGUS-P-0101-v1:section:3.5.2:writer:01")
if output.content != target:
    provenance_findings.append("TRANSLATION_CONTENT_MISMATCH")
gate = evaluate_translation(source, target, contract)
status = "FAIL" if provenance_findings or gate["status"] == "FAIL" else "PASS"
result = {"status": status, "provenance_findings": provenance_findings, **gate}
lines = [
    "# Section 3.5.2 Translation Preservation Gate", "", f"- Overall: `{status}`",
    f"- Decision: `{gate['decision']}`", f"- Independent semantic review required: `{str(gate['independent_semantic_review_required']).lower()}`",
    f"- Provenance findings: {len(provenance_findings)}", "", "## Findings", "",
]
if gate["findings"]:
    lines.extend(f"- `{item['status']}` `{item['code']}`: {item['detail']}" for item in gate["findings"])
else:
    lines.append("- None")
(REPORT / "section-3.5.2-translation-preservation-gate.md").write_text("\n".join(lines) + "\n", "utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(1 if status == "FAIL" and not gate["independent_semantic_review_required"] else 0)
