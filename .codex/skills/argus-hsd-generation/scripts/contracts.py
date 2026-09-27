from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha256


class CoverageStatus(str, Enum):
    UNMAPPED = "UNMAPPED"
    PRESERVED = "PRESERVED"
    REFERENCED = "REFERENCED"
    REVIEW = "REVIEW"


class ReviewVerdict(str, Enum):
    FINDINGS = "FINDINGS"
    NO_FINDINGS = "NO_FINDINGS"


@dataclass(frozen=True)
class ExactValue:
    id: str
    canonical: str
    accepted: tuple[str, ...]
    label: str
    source_locator: str

    def __post_init__(self) -> None:
        if not self.id or not self.canonical or not self.label or not self.source_locator:
            raise ValueError("exact value fields must be non-empty")
        if self.canonical not in self.accepted:
            raise ValueError("canonical value must be accepted")


@dataclass(frozen=True)
class SectionContext:
    section_id: str
    title: str
    problems: tuple[str, ...]
    purposes: tuple[str, ...]
    design_points: tuple[str, ...]
    exact_value_ids: tuple[str, ...]
    states: tuple[str, ...]
    actors_authorities: tuple[str, ...]
    boundaries: tuple[str, ...]
    relations: tuple[str, ...]
    cross_references: tuple[str, ...]
    primary_owner: str
    diagram_plan: tuple[str, ...]
    source_locators: tuple[str, ...]
    coverage_units: tuple[str, ...]
    depth_target: str


def canonical_digest(value: object) -> str:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)  # type: ignore[arg-type]
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def load_exact_values(data: Sequence[Mapping[str, object]]) -> tuple[ExactValue, ...]:
    return tuple(
        ExactValue(
            id=str(item["id"]),
            canonical=str(item["canonical"]),
            accepted=tuple(str(v) for v in item["accepted"]),  # type: ignore[union-attr]
            label=str(item["label"]),
            source_locator=str(item["source_locator"]),
        )
        for item in data
    )
