from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from translation_semantic_review import digest_json
from translation_stage import (
    TERMINOLOGY_RULES_V2,
    StructureLock,
    TranslationContract,
    digest_text,
    make_translator_input,
    validate_translator_input,
)

ROOT = Path(__file__).resolve().parents[4]
SOURCE_REPORT = ROOT / "validation/reports/argus-p-0101-v1"
REPORT = ROOT / "validation/reports/argus-p-0105-v1"
REPORT.mkdir(parents=True, exist_ok=True)

source = (SOURCE_REPORT / "section-3.5.2-en.md").read_text(encoding="utf-8")
contract = TranslationContract(
    section_id="3.5.2",
    source_draft_digest=digest_text(source),
    source_language="en",
    target_language="ja",
    protected_identifiers=(
        "Application Log",
        "Canonical State",
        "Fact",
        "Event",
        "Audit Record",
        "Writer",
        "Canonical Commit",
        "Commit",
        "Audit",
        "Storage Fail Closed",
        "Runtime Identity",
        "Secret",
        "Credential",
        "Token",
        "API key",
        "Authorization header",
        "Development",
    ),
    protected_literals=("TEST", "PAPER", "LIVE", "Asia/Tokyo", "§2.6", "§4", "§28"),
    protected_state_names=(),
    protected_paths=("logs/application/YYYY-MM-DD/",),
    protected_numeric_values=(),
    terminology_rules=TERMINOLOGY_RULES_V2
    + (
        "Do not narrow Runtime, Job, Adapter, or Error through first-use wording; if a precise explanation would add specificity, retain a faithful Japanese loanword correspondence and the original term.",
        "Preserve the redaction or masking-specific meaning of unredacted; do not generalize it to unedited.",
    ),
    structure_lock=StructureLock(),
    producer_kind="LLM_TRANSLATOR",
    translator_session_id="ARGUS-P-0105-v1:section:3.5.2:translator:01",
    generation_timestamp=datetime.now(timezone(timedelta(hours=9))).isoformat(),
    provenance_version="3",
    human_facing_technical_concepts=("Runtime", "Job", "Adapter", "Error", "unredacted"),
    semantic_risk_terms=("unredacted", "Runtime", "Job", "Adapter", "Error"),
    terminology_policy_version="2",
)
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
    "persistence_boundary": "text_artifact_io.persist_translation_artifacts",
    "producer_kind": contract.producer_kind,
    "repair_count": 0,
}
(REPORT / "section-3.5.2-translation-provenance.json").write_text(
    json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(provenance, ensure_ascii=False, indent=2))
