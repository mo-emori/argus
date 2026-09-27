from __future__ import annotations

import hashlib
import re
from collections import defaultdict

from planning_schema import (
    HSD_SECTIONS,
    CandidateDisposition,
    CoverageAssignment,
    DiagramNeed,
    DiagramPlan,
    ExactValueContext,
    PlanningStatus,
    SectionContext,
    SemanticCandidate,
    SourceElement,
)
from sdd_parser import ParseResult

SECTION_MAP: dict[str, str] = {
    "1": "0", "1.1": "0", "2": "9", "2.1": "1.3", "2.2": "3.4", "2.3": "3.4",
    "2.4": "2.4", "2.5": "6.1", "2.6": "3.4", "2.7": "1.4", "2.8": "2.2",
    "2.9": "7.1", "3": "1.2", "3.1": "1.1", "3.2": "1.4", "4": "1.3",
    "4.1": "6.5", "5": "3.2", "5.1": "3.3", "5.2": "3.2", "5.3": "3.3",
    "6": "3.4", "6.1": "3.4", "6.2": "6.3", "7": "2.1", "7.1": "2.1",
    "7.2": "2.3", "7.3": "6.4", "8": "5.2", "8.1": "5.2", "8.2": "5.3",
    "8.3": "5.5", "8.4": "5.4", "8.5": "5.4", "8.6": "5.4", "8.7": "5.4",
    "9": "2.4", "9.1": "2.4", "9.2": "2.5", "9.3": "2.5", "10": "2.6",
    "10.1": "2.6", "10.2": "2.6", "10.3": "2.6", "10.4": "2.6", "10.5": "2.6",
    "11": "2.7", "12": "4.1", "12.1": "4.1", "12.2": "4.3", "12.3": "4.2",
    "13": "7.3", "13.1": "7.3", "13.2": "7.3", "13.3": "7.4", "14": "7.1",
    "14.1": "7.1", "14.2": "7.2", "14.3": "0", "15": "10", "15.1": "10", "16": "6.1",
    "17": "0", "17.1": "3.4", "17.2": "3.1", "17.3": "3.5", "17.4": "3.6",
    "18": "5.1", "18.1": "5.1", "18.2": "5.1", "19": "4.4", "19.1": "4.4",
    "19.2": "3.5", "19.3": "6.1", "20": "3.2", "20.1": "3.2", "20.2": "2.7",
    "21": "7.1", "21.1": "7.1", "21.2": "7.4", "22": "7.2", "22.1": "7.2",
    "22.2": "6.2", "22.3": "7.2", "23": "3.6", "23.1": "3.1", "23.2": "3.6",
    "23.3": "7.4", "24": "6.1", "24.1": "1.2", "24.2": "6.1", "25": "9",
    "25.1": "9", "25.2": "7.1", "26": "8", "26.1": "3.4", "26.2": "3.4",
    "26.3": "3.4", "26.4": "8", "26.5": "8", "26.6": "2.6", "26.7": "4.2",
    "26.8": "3.5",
}

OWNER = {sid: title for sid, title in HSD_SECTIONS}
OWNER.update({
    "0": "Design Authority", "1.3": "Human / ARGUS", "2.1": "Selection",
    "2.2": "Analysis", "2.3": "Risk Validator", "2.4": "Human",
    "2.5": "Execution Ingress", "2.6": "Portfolio", "2.7": "Watch",
    "3.1": "Bootstrap", "3.2": "Runner", "3.3": "Runner Recovery",
    "3.4": "Canonical Writer", "3.5": "Storage Manager", "3.6": "Deployment",
    "4.1": "ExternalServiceGateway", "4.2": "Provider Adapter", "4.3": "Budget Gate",
    "4.4": "Failure Controller", "5.1": "Human Interface", "5.2": "Status Mapper",
    "5.3": "Decision Queue", "5.4": "Notification Router", "5.5": "Incident Manager",
    "6.1": "Safety Gate", "6.2": "Environment Binding", "6.3": "Canonical Writer",
    "6.4": "Risk Validator", "6.5": "Security Boundary", "7.1": "Verification",
})

_SECTION_NUMBER = re.compile(r"^(\d+(?:\.\d+)?)")
_LABEL_TEXT = re.compile(r"^\*\*([^*：:]+)[：:]\*\*\s*(.*)$")

_TECHNICAL_TERMS = {"API", "CLI", "CPU", "CSV", "DB", "GUI", "HTTP", "JSON", "OS", "SDK", "SHA", "SQL", "URL", "UUID"}
_ACTOR_COMPONENTS = {"ARGUS", "BROKER", "HUMAN", "LLM"}
_FORMAL_STATES = {
    "ACKNOWLEDGED", "BLOCKED", "BUSY", "CANCELLED", "COMPLETED", "END", "FAILED",
    "FREE", "INIT", "LARGE", "MEDIUM", "NORMAL", "OPEN", "PENDING", "READY",
    "RESOLVED", "RESUMING", "RUNNING", "SMALL", "STOPPED", "UNKNOWN",
}


def _classify_candidate(value: str, locator: str) -> SemanticCandidate:
    normalized = value.strip()
    parts = normalized.split(" / ")
    if all(part in _FORMAL_STATES for part in parts):
        return SemanticCandidate(normalized, "formal_state", CandidateDisposition.CONFIRMED, "closed state vocabulary", locator)
    if normalized in _TECHNICAL_TERMS or normalized.startswith("SHA"):
        return SemanticCandidate(normalized, "technical_term", CandidateDisposition.REJECTED, "technical token is not a state", locator)
    if normalized in _ACTOR_COMPONENTS:
        return SemanticCandidate(normalized, "actor_component", CandidateDisposition.REJECTED, "actor/component is not a state", locator)
    if "_" in normalized or any(character.isdigit() for character in normalized):
        return SemanticCandidate(normalized, "identifier", CandidateDisposition.REVIEW_REQUIRED, "identifier requires semantic review", locator)
    return SemanticCandidate(normalized, "unknown_candidate", CandidateDisposition.REVIEW_REQUIRED, "uppercase token requires semantic review", locator)


def _target(section: str) -> str | None:
    match = _SECTION_NUMBER.match(section)
    return SECTION_MAP.get(match.group(1)) if match else None


def _diagram(section_id: str, title: str) -> DiagramPlan:
    if any(word in title for word in ("全体処理", "継続実行", "中断", "売買", "監視")):
        return DiagramPlan(DiagramNeed.NEEDED, "flowchart", "処理順または分岐")
    if any(word in title for word in ("状態", "判断待ち")):
        return DiagramPlan(DiagramNeed.NEEDED, "stateDiagram", "状態遷移")
    if section_id in {"1.2", "1.3", "4.1", "6.3"}:
        return DiagramPlan(DiagramNeed.REVIEW, "component/sequence", "境界または責務比較")
    return DiagramPlan(DiagramNeed.NOT_NEEDED, "", "図による改善根拠を未検出")


def build_section_contexts(parsed: ParseResult) -> tuple[SectionContext, ...]:
    buckets: dict[str, dict[str, list[SourceElement]]] = {sid: defaultdict(list) for sid, _ in HSD_SECTIONS}
    coverage: dict[str, list[CoverageAssignment]] = {sid: [] for sid, _ in HSD_SECTIONS}
    exacts: dict[str, list[ExactValueContext]] = {sid: [] for sid, _ in HSD_SECTIONS}
    states: dict[str, set[str]] = {sid: set() for sid, _ in HSD_SECTIONS}
    candidates: dict[str, dict[tuple[str, str], SemanticCandidate]] = {sid: {} for sid, _ in HSD_SECTIONS}
    locators: dict[str, set[str]] = {sid: set() for sid, _ in HSD_SECTIONS}
    unresolved: dict[str, list[str]] = {sid: [] for sid, _ in HSD_SECTIONS}
    active_labels: dict[str, tuple[str, str]] = {}
    for index, unit in enumerate(parsed.units):
        sid = _target(unit.section)
        if sid is None:
            continue
        category, semantic, text = "processes", "table_row", unit.text
        if unit.kind == "label":
            match = _LABEL_TEXT.match(unit.text)
            if not match:
                unresolved[sid].append(f"label parse: {unit.unit_id}")
                continue
            semantic, text = match.groups()
            category = {
                "前提": "premises", "課題": "problems", "目的": "purposes",
                "設計理由": "design_reasons", "規則": "rules", "禁止": "prohibitions",
                "例外": "exceptions", "失敗時": "abnormal_handling", "復旧": "abnormal_handling",
                "異常時": "abnormal_handling",
            }.get(semantic, "processes")
            active_labels[unit.section] = (category, semantic)
            if not text.strip():
                continue
        elif unit.kind in {"list_item", "prose"} and unit.section in active_labels:
            category, semantic = active_labels[unit.section]
            text = re.sub(r"^\s*(?:[-*+] |\d+[.)] )", "", unit.text).strip()
            if not text:
                continue
        elif unit.kind == "table_row":
            if index + 1 < len(parsed.units) and parsed.units[index + 1].kind == "table_separator":
                continue
            section_code = _SECTION_NUMBER.match(unit.section)
            if section_code and section_code.group(1) in {"16", "24.1"}:
                category, semantic = "design_reasons", "explicit_reason_table"
            elif "前提" in unit.text:
                category, semantic = "premises", "explicit_premise_table"
        else:
            continue
        source = SourceElement(unit.unit_id, semantic, f"SDD line {unit.line_number}", text)
        buckets[sid][category].append(source)
        section_match = _SECTION_NUMBER.match(unit.section)
        broad_section = bool(section_match and "." not in section_match.group(1))
        assignment_status = "REVIEW_REQUIRED" if broad_section else "ASSIGNED"
        confidence_reason = "top-level cross-cutting source requires Human placement review" if broad_section else "explicit SDD subsection mapping"
        coverage[sid].append(CoverageAssignment(unit.unit_id, source.source_locator, sid, OWNER[sid], assignment_status, confidence_reason))
        locators[sid].add(source.source_locator)
        for raw_candidate in unit.state_identifier_candidates:
            candidate = _classify_candidate(raw_candidate, source.source_locator)
            candidates[sid][(candidate.value, candidate.source_locator)] = candidate
            if candidate.candidate_type == "formal_state" and candidate.disposition == CandidateDisposition.CONFIRMED:
                states[sid].add(candidate.value)
        for value in unit.exact_value_candidates:
            suffix = hashlib.sha256(f"{unit.unit_id}:{value}".encode()).hexdigest()[:10]
            exacts[sid].append(ExactValueContext(f"EV-{suffix}", value, (value,), semantic, (semantic,), source.source_locator, unit.unit_id))
    contexts: list[SectionContext] = []
    ids = {sid for sid, _ in HSD_SECTIONS}
    for sid, title in HSD_SECTIONS:
        data = buckets[sid]
        cross = tuple(ref for ref in _cross_refs(sid) if ref in ids)
        status = PlanningStatus.READY
        if (not data["problems"] or not data["purposes"] or not coverage[sid] or unresolved[sid]
                or any(item.assignment_status == "REVIEW_REQUIRED" for item in coverage[sid])
                or any(item.disposition == CandidateDisposition.REVIEW_REQUIRED for item in candidates[sid].values())):
            status = PlanningStatus.REVIEW_REQUIRED
        all_text = " ".join(item.original_text for items in data.values() for item in items)
        contexts.append(SectionContext(
            sid, title, 1 if "." not in sid else 2,
            tuple(data["premises"]), tuple(data["problems"]), tuple(data["purposes"]),
            tuple(data["design_reasons"]), tuple(data["processes"]), tuple(data["rules"]),
            tuple(data["prohibitions"]), tuple(data["exceptions"]), tuple(data["abnormal_handling"]),
            tuple(exacts[sid]), tuple(sorted(states[sid])), tuple(candidates[sid].values()),
            tuple(word for word in ("Human", "ARGUS", "Broker", "Agent / LLM") if word in all_text),
            tuple(item.original_text for item in data["processes"] if "境界" in item.original_text)[:10],
            tuple(item.original_text for item in data["processes"] if "関係" in item.original_text)[:10],
            tuple(unresolved[sid]), cross, OWNER[sid], _diagram(sid, title),
            tuple(sorted(locators[sid])), tuple(coverage[sid]), status,
        ))
    return tuple(contexts)


def _cross_refs(section_id: str) -> tuple[str, ...]:
    return {
        "2.1": ("2.2",), "2.2": ("2.3",), "2.3": ("2.4", "6.4"),
        "2.4": ("2.5",), "2.5": ("2.6",), "2.6": ("2.7",),
        "3.1": ("3.2",), "3.2": ("3.3",), "3.3": ("3.5",),
        "4.1": ("4.2", "4.3", "4.4"), "5.3": ("5.4",),
        "6.2": ("7.2",), "7.1": ("7.2",), "7.3": ("7.4",),
    }.get(section_id, ())
