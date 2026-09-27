from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from translation_semantic_review import digest_json
from translation_stage import StructureLock, TranslationContract, make_translator_input

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0101-v1"
source = (REPORT / "section-3.5.2-en.md").read_text("utf-8")

(REPORT / "section-3.5.2-ja-initial-failed.md").write_text((REPORT / "section-3.5.2-ja.md").read_text("utf-8"), "utf-8")
(REPORT / "section-3.5.2-translation-output-initial-failed.json").write_text(
    (REPORT / "section-3.5.2-translation-output.json").read_text("utf-8"), "utf-8"
)
(REPORT / "section-3.5.2-translation-contract-initial.json").write_text(
    (REPORT / "section-3.5.2-translation-contract.json").read_text("utf-8"), "utf-8"
)

data = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text("utf-8"))
data["protected_literals"] = [*data["protected_literals"], "§2.6", "§4", "§28"]
data["translator_session_id"] = "ARGUS-P-0101-v1:section:3.5.2:translator:02"
data["provenance_version"] = "1-repair-1"
data["structure_lock"] = StructureLock(**data["structure_lock"])
for key in ("protected_identifiers", "protected_literals", "protected_state_names", "protected_paths", "protected_numeric_values", "terminology_rules"):
    data[key] = tuple(data[key])
contract = TranslationContract(**data)
envelope = make_translator_input(source, contract)
(REPORT / "section-3.5.2-translation-contract.json").write_text(json.dumps(asdict(contract), ensure_ascii=False, indent=2) + "\n", "utf-8")
(REPORT / "section-3.5.2-translation-input.json").write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", "utf-8")
provenance = json.loads((REPORT / "section-3.5.2-translation-provenance.json").read_text("utf-8"))
provenance.update({
    "translator_session_id": contract.translator_session_id,
    "translation_contract_digest": digest_json(asdict(contract)),
    "translation_contract_version": contract.provenance_version,
    "repair_count": 1,
    "initial_failed_artifacts": [
        "section-3.5.2-ja-initial-failed.md",
        "section-3.5.2-translation-output-initial-failed.json",
        "section-3.5.2-translation-contract-initial.json"
    ]
})
(REPORT / "section-3.5.2-translation-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8")
print(json.dumps(provenance, ensure_ascii=False, indent=2))
