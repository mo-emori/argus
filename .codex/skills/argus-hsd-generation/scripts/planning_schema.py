from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class PlanningStatus(str, Enum):
    READY = "READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class DiagramNeed(str, Enum):
    NEEDED = "NEEDED"
    NOT_NEEDED = "NOT_NEEDED"
    REVIEW = "REVIEW"


class CandidateDisposition(str, Enum):
    CONFIRMED = "CONFIRMED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class SourceElement:
    coverage_id: str
    semantic_kind: str
    source_locator: str
    original_text: str


@dataclass(frozen=True)
class ExactValueContext:
    value_id: str
    canonical: str
    accepted: tuple[str, ...]
    label: str
    label_terms: tuple[str, ...]
    source_locator: str
    coverage_id: str

    def __post_init__(self) -> None:
        if not all((self.value_id, self.canonical, self.label, self.source_locator, self.coverage_id)):
            raise ValueError("exact value fields must be non-empty")
        if self.canonical not in self.accepted:
            raise ValueError("canonical must be accepted")


@dataclass(frozen=True)
class CoverageAssignment:
    coverage_id: str
    source_locator: str
    assigned_section: str
    primary_owner: str
    assignment_status: str
    confidence_reason: str


@dataclass(frozen=True)
class SemanticCandidate:
    value: str
    candidate_type: str
    disposition: CandidateDisposition
    reason: str
    source_locator: str


@dataclass(frozen=True)
class DiagramPlan:
    need: DiagramNeed
    candidate_type: str
    reason: str


@dataclass(frozen=True)
class AbsenceApproval:
    semantic_kind: str
    absent_reason: str
    approved_by: str
    approval_ref: str


@dataclass(frozen=True)
class SectionContext:
    section_id: str
    title: str
    depth: int
    premises: tuple[SourceElement, ...]
    problems: tuple[SourceElement, ...]
    purposes: tuple[SourceElement, ...]
    design_reasons: tuple[SourceElement, ...]
    processes: tuple[SourceElement, ...]
    rules: tuple[SourceElement, ...]
    prohibitions: tuple[SourceElement, ...]
    exceptions: tuple[SourceElement, ...]
    abnormal_handling: tuple[SourceElement, ...]
    exact_values: tuple[ExactValueContext, ...]
    states: tuple[str, ...]
    semantic_candidates: tuple[SemanticCandidate, ...]
    actors_authorities: tuple[str, ...]
    boundaries: tuple[str, ...]
    relations: tuple[str, ...]
    unresolved: tuple[str, ...]
    cross_references: tuple[str, ...]
    primary_owner: str
    diagram_plan: DiagramPlan
    source_locators: tuple[str, ...]
    coverage_units: tuple[CoverageAssignment, ...]
    planning_status: PlanningStatus
    absence_approvals: tuple[AbsenceApproval, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


HSD_SECTIONS: tuple[tuple[str, str], ...] = (
    ("0", "設計環境"), ("1.1", "システムの目的"), ("1.2", "全体構成"),
    ("1.3", "HumanとARGUSの役割分担"), ("1.4", "全体処理"),
    ("2.1", "候補探索"), ("2.2", "分析・反証・判断材料"),
    ("2.3", "資金配分とリスク検証"), ("2.4", "Humanの判断"),
    ("2.5", "売買と売買結果"), ("2.6", "ポートフォリオ管理"),
    ("2.7", "監視と再評価"), ("3.1", "起動"), ("3.2", "継続実行"),
    ("3.3", "中断・再開"), ("3.4", "状態とデータ"),
    ("3.5", "保存・バックアップ・復旧"), ("3.6", "Deployment"),
    ("4.1", "外部サービスとの境界"), ("4.2", "Provider"),
    ("4.3", "費用・利用量"), ("4.4", "外部障害"),
    ("5.1", "CLI / Human Interface"), ("5.2", "Humanの対応状態"),
    ("5.3", "判断待ち"), ("5.4", "通知"), ("5.5", "Incidentと復旧"),
    ("6.1", "Fail Closed"), ("6.2", "TEST / PAPER / LIVE"),
    ("6.3", "正本状態の保護"), ("6.4", "投資リスク"),
    ("6.5", "Secret・データ保護"), ("7.1", "検証"),
    ("7.2", "Historical / PAPER / LIVE"), ("7.3", "判断結果の評価"),
    ("7.4", "変更管理"), ("8", "機能一覧"),
    ("9", "用語・詳細仕様への参照"), ("10", "継続検討事項"),
)
