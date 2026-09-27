"""Mechanical boundary for an external LLM writer.

This module deliberately does not generate a Human-facing plan or section body.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from contracts import canonical_digest

WRITER_INPUT_FIELDS = frozenset(
    {"context", "writing_rules", "approved_references", "chapter_contract", "cross_reference_metadata"}
)


PROVENANCE_VERSION = "1"
LLM_PRODUCER = "LLM_WRITER"


@dataclass(frozen=True)
class LLMWriterOutputArtifact:
    content: str
    writer_session_id: str
    chapter_id: str
    chapter_contract_digest: str
    writer_input_digest: str
    producer_kind: str
    generated_at: str
    provenance_version: str


def writer_input(
    context: dict[str, Any],
    chapter_contract: dict[str, Any],
    *,
    cross_reference_metadata: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "context": deepcopy(context),
        "writing_rules": [
            "Write Human-facing Japanese from semantic need, not Context field order.",
            "Create a Human Structure Plan before writing the section body.",
            "Do not infer missing design meaning; return CONTEXT_INSUFFICIENT.",
            "Do not expose coverage IDs, source locators, parser categories, or assignment metadata.",
            "Choose prose, tables, and diagrams by meaning; no fixed counts or templates.",
        ],
        "approved_references": ["term_governance.json", "exact_values.json"],
        "chapter_contract": deepcopy(chapter_contract),
        "cross_reference_metadata": deepcopy(cross_reference_metadata or []),
    }


def validate_llm_output(
    artifact: LLMWriterOutputArtifact,
    *,
    expected_session_id: str,
    expected_chapter_id: str,
    expected_chapter_contract_digest: str,
    expected_writer_input_digest: str,
) -> str:
    if not isinstance(artifact, LLMWriterOutputArtifact):
        raise TypeError("LLMWriterOutputArtifact is required; raw strings are forbidden")
    required = asdict(artifact)
    if any(not isinstance(value, str) or not value.strip() for value in required.values()):
        raise ValueError("all provenance fields and content are required")
    checks = {
        "writer session": artifact.writer_session_id == expected_session_id,
        "chapter": artifact.chapter_id == expected_chapter_id,
        "Chapter Contract": artifact.chapter_contract_digest == expected_chapter_contract_digest,
        "Writer input": artifact.writer_input_digest == expected_writer_input_digest,
        "producer": artifact.producer_kind == LLM_PRODUCER,
        "provenance version": artifact.provenance_version == PROVENANCE_VERSION,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"provenance mismatch: {', '.join(failed)}")
    try:
        generated_at = datetime.fromisoformat(artifact.generated_at)
    except ValueError as exc:
        raise ValueError("generated_at must be valid ISO-8601") from exc
    if generated_at.tzinfo is None:
        raise ValueError("generated_at must include a timezone")
    return artifact.content


def writer_input_digest(value: dict[str, Any]) -> str:
    if set(value) != WRITER_INPUT_FIELDS:
        raise ValueError("Writer input envelope is not canonical")
    return canonical_digest(value)
