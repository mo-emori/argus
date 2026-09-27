from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from translation_semantic_review import digest_json
from translation_stage import (
    StructureLock,
    TranslationContract,
    digest_text,
    make_translator_input,
    validate_translator_input,
)

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0101-v1"
source = (REPORT / "section-3.5.2-en.md").read_text("utf-8")
contract = TranslationContract(
    section_id="3.5.2",
    source_draft_digest=digest_text(source),
    source_language="en",
    target_language="ja",
    protected_identifiers=(
        "Application Log", "Canonical State", "Fact", "Event", "Audit Record", "Runtime", "Job",
        "Adapter", "Error", "Writer", "Canonical Commit", "Commit", "Audit", "Storage Fail Closed",
        "Runtime Identity", "Secret", "Credential", "Token", "API key", "Authorization header",
        "Development",
    ),
    protected_literals=("TEST", "PAPER", "LIVE", "Asia/Tokyo"),
    protected_state_names=(),
    protected_paths=("logs/application/YYYY-MM-DD/",),
    protected_numeric_values=(),
    terminology_rules=(
        "Use natural Japanese for general explanations and general technical concepts.",
        "Keep protected values exactly as written.",
        "Do not add, delete, summarize, generalize, or resolve design meaning.",
        "Preserve unresolved status, normative strength, subjects, targets, conditions, and failure behavior.",
    ),
    structure_lock=StructureLock(),
    producer_kind="LLM_TRANSLATOR",
    translator_session_id="ARGUS-P-0101-v1:section:3.5.2:translator:01",
    generation_timestamp=datetime.now(timezone(timedelta(hours=9))).isoformat(),
    provenance_version="1",
)
envelope = make_translator_input(source, contract)
findings = validate_translator_input(envelope)
if findings:
    raise PermissionError(findings)
(REPORT / "section-3.5.2-translation-contract.json").write_text(json.dumps(asdict(contract), ensure_ascii=False, indent=2) + "\n", "utf-8")
(REPORT / "section-3.5.2-translation-input.json").write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", "utf-8")
provenance = {
    "writer_session_id": "ARGUS-P-0101-v1:section:3.5.2:writer:01",
    "translator_session_id": contract.translator_session_id,
    "source_draft_digest": contract.source_draft_digest,
    "translation_contract_digest": digest_json(asdict(contract)),
    "translation_contract_version": contract.provenance_version,
    "producer_kind": contract.producer_kind,
    "repair_count": 0,
}
(REPORT / "section-3.5.2-translation-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", "utf-8")
print(json.dumps(provenance, ensure_ascii=False, indent=2))
