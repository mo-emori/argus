from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

FORBIDDEN_TRANSLATOR_KEYS = {"source", "sdd", "section_context", "design_source", "coverage"}

TERMINOLOGY_RULES_V2 = (
    "Classify terms as machine-facing literals, human-facing technical concepts, or general prose vocabulary.",
    "Preserve every protected machine-facing literal exactly; do not require a Japanese gloss for it.",
    "At the first use of a human-facing technical concept, add a faithful Japanese explanation followed by the original term in parentheses when explanation is needed.",
    "After the first-use correspondence is established, the original technical term may be used alone.",
    "Translate general prose vocabulary into natural Japanese.",
    "If the technical meaning cannot be translated confidently, preserve the original term and add a Japanese explanation instead of generalizing it.",
    "Do not add a design condition, responsibility, causal relation, obligation, or prohibition through a terminology explanation.",
    "Priority: protected values, technical meaning boundaries, necessary first-use explanations, then natural Japanese prose.",
)


@dataclass(frozen=True)
class StructureLock:
    heading_hierarchy: bool = True
    paragraph_correspondence: bool = True
    table_structure: bool = True
    list_item_count: bool = True
    diagram_structure: bool = True
    cross_references: bool = True
    coverage_boundaries: bool = True


@dataclass(frozen=True)
class TranslationContract:
    section_id: str
    source_draft_digest: str
    source_language: str
    target_language: str
    protected_identifiers: tuple[str, ...]
    protected_literals: tuple[str, ...]
    protected_state_names: tuple[str, ...]
    protected_paths: tuple[str, ...]
    protected_numeric_values: tuple[str, ...]
    terminology_rules: tuple[str, ...]
    structure_lock: StructureLock
    producer_kind: str
    translator_session_id: str
    generation_timestamp: str
    provenance_version: str
    human_facing_technical_concepts: tuple[str, ...] = ()
    semantic_risk_terms: tuple[str, ...] = ()
    terminology_policy_version: str = "1"


@dataclass(frozen=True)
class TranslationOutput:
    section_id: str
    source_draft_digest: str
    translator_session_id: str
    producer_kind: str
    translation_contract_version: str
    generated_artifact_digest: str
    generation_timestamp: str
    provenance_version: str
    content: str


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_translator_input(source_draft: str, contract: TranslationContract) -> dict[str, Any]:
    if digest_text(source_draft) != contract.source_draft_digest:
        raise PermissionError("SOURCE_DRAFT_DIGEST_MISMATCH")
    if contract.terminology_policy_version == "2":
        findings = validate_terminology_policy(contract)
        if findings:
            raise PermissionError("INVALID_TERMINOLOGY_POLICY:" + ",".join(findings))
    return {"source_draft": source_draft, "translation_contract": asdict(contract)}


def validate_terminology_policy(contract: TranslationContract) -> list[str]:
    """Validate policy presence without deciding natural-language meaning in Python."""
    rules = "\n".join(contract.terminology_rules).casefold()
    required_concepts = {
        "protected": ("protected", "literal"),
        "first_use": ("first", "explanation", "original term"),
        "uncertain_meaning": ("cannot", "confident", "generaliz"),
        "no_new_design_meaning": ("do not add", "design"),
        "priority": ("priority", "technical meaning"),
    }
    return [
        f"TERMINOLOGY_POLICY_MISSING:{name}"
        for name, markers in required_concepts.items()
        if not all(marker in rules for marker in markers)
    ]


def validate_translator_input(envelope: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if set(envelope) != {"source_draft", "translation_contract"}:
        findings.append("TRANSLATOR_INPUT_NOT_CLOSED")
    pending: list[Any] = [envelope]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if FORBIDDEN_TRANSLATOR_KEYS.intersection(value):
                findings.append("FORBIDDEN_DESIGN_INPUT")
            pending.extend(value.values())
        elif isinstance(value, list | tuple):
            pending.extend(value)
    return sorted(set(findings))


def validate_translation_output(
    output: TranslationOutput,
    contract: TranslationContract,
    writer_session_id: str,
) -> list[str]:
    findings: list[str] = []
    if output.translator_session_id == writer_session_id:
        findings.append("WRITER_TRANSLATOR_SESSION_REUSE")
    if output.translator_session_id != contract.translator_session_id:
        findings.append("TRANSLATOR_SESSION_MISMATCH")
    if output.source_draft_digest != contract.source_draft_digest:
        findings.append("SOURCE_DRAFT_DIGEST_MISMATCH")
    if output.generated_artifact_digest != digest_text(output.content):
        findings.append("GENERATED_ARTIFACT_DIGEST_MISMATCH")
    if output.producer_kind != "LLM_TRANSLATOR" or contract.producer_kind != "LLM_TRANSLATOR":
        findings.append("INVALID_PRODUCER_KIND")
    try:
        timestamp = datetime.fromisoformat(output.generation_timestamp)
        if timestamp.tzinfo is None:
            findings.append("TRANSLATION_TIMESTAMP_NO_TIMEZONE")
    except ValueError:
        findings.append("TRANSLATION_TIMESTAMP_INVALID")
    return findings
