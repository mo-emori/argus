from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from translation_semantic_review import digest_json
from translation_stage import (
    StructureLock,
    TranslationContract,
    make_translator_input,
    validate_translator_input,
)

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0103-v1"
SOURCE_REPORT = ROOT / "validation/reports/argus-p-0101-v1"

for source_name, target_name in (
    ("section-3.5.2-ja.md", "section-3.5.2-ja-initial-failed.md"),
    ("section-3.5.2-translation-output.json", "section-3.5.2-translation-output-initial-failed.json"),
    ("section-3.5.2-translation-contract.json", "section-3.5.2-translation-contract-initial.json"),
    ("section-3.5.2-translation-input.json", "section-3.5.2-translation-input-initial.json"),
    ("section-3.5.2-semantic-review.json", "section-3.5.2-semantic-review-initial-failed.json"),
):
    shutil.copyfile(REPORT / source_name, REPORT / target_name)

data = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text(encoding="utf-8"))
data["structure_lock"] = StructureLock(**data["structure_lock"])
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
    data[key] = tuple(data[key])
data["translator_session_id"] = "ARGUS-P-0103-v1:section:3.5.2:translator:02"
data["generation_timestamp"] = datetime.now(timezone(timedelta(hours=9))).isoformat()
data["provenance_version"] = "2-repair-1"
data["terminology_rules"] += (
    "Repair constraint: do not narrow Runtime, Job, Adapter, or Error through a first-use explanation; prefer a faithful Japanese loanword correspondence with the original term when a more specific explanation would add meaning.",
)
data["semantic_risk_terms"] = ("unredacted", "Runtime", "Job", "Adapter", "Error")
contract = TranslationContract(**data)
source = (SOURCE_REPORT / "section-3.5.2-en.md").read_text(encoding="utf-8")
envelope = make_translator_input(source, contract)
findings = validate_translator_input(envelope)
if findings:
    raise PermissionError(findings)

(REPORT / "section-3.5.2-translation-contract.json").write_text(
    json.dumps(asdict(contract), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(REPORT / "section-3.5.2-translation-input.json").write_text(
    json.dumps(envelope, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
provenance = {
    "writer_session_id": "ARGUS-P-0101-v1:section:3.5.2:writer:01",
    "translator_session_id": contract.translator_session_id,
    "source_draft_digest": contract.source_draft_digest,
    "translation_contract_digest": digest_json(asdict(contract)),
    "translation_contract_version": contract.provenance_version,
    "terminology_policy_version": contract.terminology_policy_version,
    "producer_kind": contract.producer_kind,
    "repair_count": 1,
    "initial_failed_artifacts": [
        "section-3.5.2-ja-initial-failed.md",
        "section-3.5.2-translation-output-initial-failed.json",
        "section-3.5.2-translation-contract-initial.json",
        "section-3.5.2-translation-input-initial.json",
        "section-3.5.2-semantic-review-initial-failed.json",
    ],
}
(REPORT / "section-3.5.2-translation-provenance.json").write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(provenance, ensure_ascii=False, indent=2))
