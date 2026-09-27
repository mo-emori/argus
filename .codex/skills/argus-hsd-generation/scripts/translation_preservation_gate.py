from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from translation_stage import TranslationContract


@dataclass(frozen=True)
class TranslationFinding:
    status: str
    code: str
    detail: str


def _headings(text: str) -> list[tuple[int, str]]:
    return [(len(level), title.strip()) for level, title in re.findall(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)]


def _table_shapes(text: str) -> list[tuple[int, int]]:
    tables: list[tuple[int, int]] = []
    current: list[int] = []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            current.append(len(re.split(r"(?<!\\)\|", line.strip().strip("|"))))
        elif current:
            tables.append((len(current), max(current)))
            current = []
    return tables


def _list_count(text: str) -> int:
    return len(re.findall(r"^\s*(?:[-*+] |\d+\. )", text, re.MULTILINE))


def _normative(text: str) -> set[str]:
    terms = (
        "must",
        "must not",
        "do not",
        "required",
        "prohibited",
        "shall",
        "してはならない",
        "必須",
        "禁止",
        "しなければならない",
    )
    lowered = text.casefold()
    return {term for term in terms if term.casefold() in lowered}


def _unresolved(text: str) -> bool:
    return bool(re.search(r"\bTBD\b|unresolved|未確定|未解決", text, re.IGNORECASE))


def evaluate_translation(source: str, target: str, contract: TranslationContract) -> dict[str, object]:
    findings: list[TranslationFinding] = []
    if [level for level, _ in _headings(source)] != [level for level, _ in _headings(target)]:
        findings.append(TranslationFinding("DISTORTED", "HEADING_HIERARCHY_CHANGED", "heading levels/count differ"))
    if _table_shapes(source) != _table_shapes(target):
        findings.append(TranslationFinding("MISSING", "TABLE_STRUCTURE_CHANGED", "table row/column shape differs"))
    if _list_count(source) != _list_count(target):
        findings.append(TranslationFinding("MISSING", "LIST_ITEM_COUNT_CHANGED", "list item count differs"))
    protected = (
        contract.protected_identifiers
        + contract.protected_literals
        + contract.protected_state_names
        + contract.protected_paths
        + contract.protected_numeric_values
    )
    for value in protected:
        if value in source and value not in target:
            findings.append(TranslationFinding("MISSING", "PROTECTED_VALUE_CHANGED", value))
    if _normative(source) and not _normative(target):
        findings.append(TranslationFinding("DISTORTED", "NORMATIVE_STRENGTH_WEAKENED", "obligation/prohibition missing"))
    if not _normative(source) and _normative(target):
        findings.append(TranslationFinding(
            "REVIEW",
            "POSSIBLE_INVENTED_NORMATIVE_MEANING",
            "target adds an obligation or prohibition; semantic review required",
        ))
    if _unresolved(source) and not _unresolved(target):
        findings.append(TranslationFinding("DISTORTED", "UNRESOLVED_WAS_RESOLVED", "TBD/unresolved status removed"))
    for term in contract.semantic_risk_terms:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", source, re.IGNORECASE) and not re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", target, re.IGNORECASE
        ):
            findings.append(TranslationFinding(
                "REVIEW",
                "TECHNICAL_CONCEPT_TRANSLATION_REQUIRES_REVIEW",
                f"meaning validity requires semantic review: {term}",
            ))
    source_sentences = len(re.findall(r"[.!?。！？]", source))
    target_sentences = len(re.findall(r"[.!?。！？]", target))
    if target_sentences > source_sentences + 1:
        findings.append(TranslationFinding("REVIEW", "POSSIBLE_INVENTED_MEANING", "reason required: target adds sentence boundaries"))
    blocking = {"MISSING", "DISTORTED", "INVENTED", "REVIEW"}
    return {
        "status": "FAIL" if any(item.status in blocking for item in findings) else "PASS",
        "decision": "PRESERVED" if not findings else "REVIEW",
        "findings": [asdict(item) for item in findings],
        "independent_semantic_review_required": any(item.status == "REVIEW" for item in findings),
    }
