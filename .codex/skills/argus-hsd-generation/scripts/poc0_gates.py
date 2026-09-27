from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


class GateOutcome(str, Enum):
    # This is a regression verdict, not a credential.
    PASS = "PASS"  # nosec B105
    FAIL = "FAIL"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class PocGateResult:
    case_id: str
    gate: str
    outcome: GateOutcome
    code: str
    detail: str


def markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    tail = text[start + len(heading) :]
    marker = "\n" + "#" * level + " "
    end = tail.find(marker)
    return text[start:] if end < 0 else text[start : start + len(heading) + end]


def gate_jp(hsd: str, case: Mapping[str, Any]) -> PocGateResult:
    section = markdown_section(hsd, str(case["scope_heading"]))
    tokens = tuple(str(v) for v in case.get("tokens", (case.get("token"),)) if v)
    classification = str(case["classification"])
    present = [token for token in tokens if token in section]
    if not section:
        return PocGateResult(str(case["id"]), "JP", GateOutcome.REVIEW, "SCOPE_NOT_FOUND", "")
    if not present:
        return PocGateResult(str(case["id"]), "JP", GateOutcome.PASS, "TOKEN_ABSENT", "")
    if classification == "UNCONDITIONAL":
        return PocGateResult(str(case["id"]), "JP", GateOutcome.PASS, "UNCONDITIONAL", ",".join(present))
    if classification == "PROHIBITED":
        return PocGateResult(str(case["id"]), "JP", GateOutcome.FAIL, "PROHIBITED_LATIN", ",".join(present))
    if classification == "CONDITIONAL":
        context = tuple(str(v) for v in case.get("required_context", ()))
        outcome = GateOutcome.PASS if context and any(value in section for value in context) else GateOutcome.REVIEW
        code = "CONTEXT_PRESENT" if outcome is GateOutcome.PASS else "CONDITIONAL_CONTEXT_UNCLEAR"
        return PocGateResult(str(case["id"]), "JP", outcome, code, ",".join(present))
    return PocGateResult(str(case["id"]), "JP", GateOutcome.REVIEW, "UNCLASSIFIED_LATIN", ",".join(present))


def gate_value(hsd: str, case: Mapping[str, Any], proximity: int = 120) -> PocGateResult:
    section = markdown_section(hsd, str(case["scope_heading"]))
    accepted = tuple(str(v) for v in case["accepted"])
    positions = [(token, section.find(token)) for token in accepted if token in section]
    if not positions:
        return PocGateResult(str(case["id"]), "VALUE", GateOutcome.FAIL, "VALUE_MISSING", str(case["canonical"]))
    label_terms = tuple(str(v) for v in case.get("label_terms", ()))
    for token, position in positions:
        window = section[max(0, position - proximity) : position + len(token) + proximity]
        if any(label in window for label in label_terms):
            return PocGateResult(str(case["id"]), "VALUE", GateOutcome.PASS, "VALUE_WITH_LABEL", token)
    return PocGateResult(str(case["id"]), "VALUE", GateOutcome.REVIEW, "VALUE_CONTEXT_AMBIGUOUS", positions[0][0])


def gate_state(hsd: str, case: Mapping[str, Any]) -> PocGateResult:
    section = markdown_section(hsd, str(case["scope_heading"]))
    missing = [str(value) for value in case["identifiers"] if str(value) not in section]
    outcome = GateOutcome.FAIL if missing else GateOutcome.PASS
    code = "STATE_MISSING" if missing else "STATE_SET_PRESERVED"
    return PocGateResult(str(case["id"]), "STATE", outcome, code, ",".join(missing))


def gate_struct(hsd: str, sdd: str, case: Mapping[str, Any]) -> PocGateResult:
    hsd_section = markdown_section(hsd, str(case["scope_heading"]))
    sdd_section = markdown_section(sdd, str(case["sdd_heading"]))
    missing = [label for label in case["required_sdd_labels"] if f"**{label}：**" not in sdd_section]
    if missing:
        return PocGateResult(str(case["id"]), "STRUCT", GateOutcome.FAIL, "SDD_LABEL_MISSING", ",".join(missing))
    if not hsd_section:
        return PocGateResult(str(case["id"]), "STRUCT", GateOutcome.FAIL, "HSD_SCOPE_MISSING", "")
    return PocGateResult(
        str(case["id"]),
        "STRUCT",
        GateOutcome.REVIEW,
        "SEMANTIC_REVIEW_REQUIRED",
        "課題・目的の意味対応は機械判定しない",
    )


def evaluate_case(hsd: str, sdd: str, case: Mapping[str, Any]) -> PocGateResult:
    gate = str(case["gate"])
    if gate == "JP":
        return gate_jp(hsd, case)
    if gate == "VALUE":
        return gate_value(hsd, case)
    if gate == "STATE":
        return gate_state(hsd, case)
    if gate == "STRUCT":
        return gate_struct(hsd, sdd, case)
    return PocGateResult(str(case["id"]), gate, GateOutcome.REVIEW, "UNKNOWN_GATE", gate)
