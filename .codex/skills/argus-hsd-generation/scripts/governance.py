from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TermClass(str, Enum):
    ALWAYS_ALLOWED = "always_allowed"
    BILINGUAL_ONLY = "bilingual_only"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class TermRule:
    term: str
    classification: TermClass
    japanese: str = ""


@dataclass(frozen=True)
class GovernanceBaseline:
    revision: str
    rules: tuple[TermRule, ...]


@dataclass(frozen=True)
class GovernanceChange:
    base_revision: str
    new_revision: str
    reason: str
    diff: tuple[TermRule, ...]
    approved_by: str
    approval_ref: str


def apply_change(baseline: GovernanceBaseline, change: GovernanceChange) -> GovernanceBaseline:
    if change.base_revision != baseline.revision:
        raise PermissionError("governance baseline revision mismatch")
    if not change.reason or not change.diff or not change.approved_by or not change.approval_ref:
        raise PermissionError("human-approved governance change is required")
    if change.approved_by.casefold() in {"codex", "llm", "ai", "auto", "automation"}:
        raise PermissionError("AI cannot approve governance changes")
    merged = {rule.term: rule for rule in baseline.rules}
    merged.update({rule.term: rule for rule in change.diff})
    return GovernanceBaseline(change.new_revision, tuple(merged[key] for key in sorted(merged)))

