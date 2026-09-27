from __future__ import annotations

import re
from dataclasses import dataclass

from contracts import ExactValue


@dataclass(frozen=True)
class GateFinding:
    gate: str
    code: str
    detail: str


@dataclass(frozen=True)
class GateReport:
    findings: tuple[GateFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


_LATIN = re.compile(r"\b[A-Za-z][A-Za-z0-9_./-]*\b")
_SENTENCE = re.compile(r"[^。\n]+。")


def accepted_tokens(exact_values: tuple[ExactValue, ...]) -> frozenset[str]:
    return frozenset(token for value in exact_values for token in value.accepted)


def japanese_gate(text: str, exact_values: tuple[ExactValue, ...], latin_limit: int = 200) -> GateReport:
    sanitized = text
    for token in accepted_tokens(exact_values):
        sanitized = sanitized.replace(token, "")
    count = len(_LATIN.findall(sanitized))
    findings = () if count <= latin_limit else (GateFinding("japanese", "LATIN_OVERUSE", str(count)),)
    return GateReport(findings)


def exact_value_gate(
    text: str, required_ids: tuple[str, ...], exact_values: tuple[ExactValue, ...]
) -> GateReport:
    catalog = {value.id: value for value in exact_values}
    findings: list[GateFinding] = []
    for value_id in required_ids:
        if value_id not in catalog:
            findings.append(GateFinding("exact-value", "UNKNOWN_EXACT_VALUE", value_id))
        elif not any(token in text for token in catalog[value_id].accepted):
            findings.append(GateFinding("exact-value", "MISSING_EXACT_VALUE", value_id))
    return GateReport(tuple(findings))


def long_sentence_gate(text: str, comma_limit: int = 3) -> GateReport:
    findings = tuple(
        GateFinding("long-sentence", "TOO_MANY_CLAUSES", sentence[:80])
        for sentence in _SENTENCE.findall(text)
        if sentence.count("、") >= comma_limit
    )
    return GateReport(findings)


def problem_purpose_gate(text: str) -> GateReport:
    findings: list[GateFinding] = []
    if "課題" not in text:
        findings.append(GateFinding("problem-purpose", "MISSING_PROBLEM", "課題"))
    if "目的" not in text:
        findings.append(GateFinding("problem-purpose", "MISSING_PURPOSE", "目的"))
    return GateReport(tuple(findings))
