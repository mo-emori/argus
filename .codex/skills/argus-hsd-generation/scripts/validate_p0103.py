from __future__ import annotations

import json
from pathlib import Path

from human_facing_gate import evaluate_human_facing
from translation_preservation_gate import evaluate_translation
from translation_stage import (
    StructureLock,
    TranslationContract,
    TranslationOutput,
    validate_translation_output,
)

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0103-v1"
SOURCE_REPORT = ROOT / "validation/reports/argus-p-0101-v1"

contract_data = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text(encoding="utf-8"))
contract_data["structure_lock"] = StructureLock(**contract_data["structure_lock"])
for key in (
    "protected_identifiers",
    "protected_literals",
    "protected_state_names",
    "protected_paths",
    "protected_numeric_values",
    "terminology_rules",
    "human_facing_technical_concepts",
    "semantic_risk_terms",
):
    contract_data[key] = tuple(contract_data[key])
contract = TranslationContract(**contract_data)
output = TranslationOutput(**json.loads((REPORT / "section-3.5.2-translation-output.json").read_text(encoding="utf-8")))
source = (SOURCE_REPORT / "section-3.5.2-en.md").read_text(encoding="utf-8")
target = (REPORT / "section-3.5.2-ja.md").read_text(encoding="utf-8")

provenance_findings = validate_translation_output(
    output,
    contract,
    "ARGUS-P-0101-v1:section:3.5.2:writer:01",
)
if output.content != target:
    provenance_findings.append("TRANSLATION_CONTENT_MISMATCH")
preservation = evaluate_translation(source, target, contract)
overall = "FAIL" if provenance_findings or preservation["status"] == "FAIL" else "PASS"
preservation_result = {"overall": overall, "provenance_findings": provenance_findings, **preservation}
(REPORT / "section-3.5.2-preservation-result.json").write_text(
    json.dumps(preservation_result, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
preservation_lines = [
    "# Section 3.5.2 Translation Preservation Gate",
    "",
    f"- Overall: `{overall}`",
    f"- Decision: `{preservation['decision']}`",
    f"- Independent semantic review required: `{str(preservation['independent_semantic_review_required']).lower()}`",
    f"- Provenance findings: {len(provenance_findings)}",
    "",
    "## Findings",
    "",
]
if preservation["findings"]:
    preservation_lines.extend(
        f"- `{item['status']}` `{item['code']}`: {item['detail']}" for item in preservation["findings"]
    )
else:
    preservation_lines.append("- None")
(REPORT / "section-3.5.2-translation-preservation-gate.md").write_text(
    "\n".join(preservation_lines) + "\n",
    encoding="utf-8",
)

protected = set(
    contract.protected_identifiers
    + contract.protected_literals
    + contract.protected_state_names
    + contract.protected_paths
)
human = evaluate_human_facing(
    target,
    protected,
    enforce_japanese=True,
    technical_concepts=set(contract.human_facing_technical_concepts),
)
human_lines = [
    "# Section 3.5.2 Human-facing Gate",
    "",
    f"- Status: `{human['status']}`",
    "",
    "## Metrics",
    "",
    f"- `{json.dumps(human['metrics'], ensure_ascii=False)}`",
    "",
    "## Findings",
    "",
]
if human["findings"]:
    human_lines.extend(f"- `{item['severity']}` `{item['code']}`: {item['detail']}" for item in human["findings"])
else:
    human_lines.append("- None")
(REPORT / "section-3.5.2-human-facing-gate.md").write_text(
    "\n".join(human_lines) + "\n",
    encoding="utf-8",
)

print(json.dumps({"preservation": preservation_result, "human_facing": human}, ensure_ascii=False, indent=2))
raise SystemExit(0 if overall == "PASS" and human["status"] == "PASS" else 1)
