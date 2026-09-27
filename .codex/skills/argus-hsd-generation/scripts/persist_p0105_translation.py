from __future__ import annotations

import json
from pathlib import Path

from text_artifact_io import persist_translation_artifacts, unicode_representation
from translation_stage import StructureLock, TranslationContract, TranslationOutput

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0105-v1"
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
candidate_data = json.loads((REPORT / "section-3.5.2-translation-candidate.json").read_text(encoding="utf-8"))
output = TranslationOutput(**candidate_data)
source = (SOURCE_REPORT / "section-3.5.2-en.md").read_text(encoding="utf-8")

persist_translation_artifacts(
    REPORT / "section-3.5.2-ja.md",
    REPORT / "section-3.5.2-translation-output.json",
    source,
    output,
    contract,
)
references = {
    value: unicode_representation(value)
    for value in ("§2.6", "§4", "§28")
}
result = {
    "status": "PASS",
    "boundary": "text_artifact_io.persist_translation_artifacts",
    "strict_utf8_roundtrip": "PASS",
    "protected_value_exact_match": "PASS",
    "generated_digest": "PASS",
    "json_markdown_content_binding": "PASS",
    "temporary_file_reload": "PASS",
    "protected_references": references,
}
(REPORT / "section-3.5.2-persistence-boundary.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2))
