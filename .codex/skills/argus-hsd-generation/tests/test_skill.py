from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from contracts import CoverageStatus, SectionContext, load_exact_values
from coverage import CoverageEntry, CoverageLedger
from gates import accepted_tokens, exact_value_gate, japanese_gate
from planning import build_planning
from poc0 import run_poc0
from sdd_parser import parse_sdd

ROOT = Path(__file__).resolve().parents[1]


def context(**overrides: object) -> SectionContext:
    data: dict[str, object] = {
        "section_id": "1.1",
        "title": "目的",
        "problems": ("判断の丸投げを防ぐ",),
        "purposes": ("Human-in-the-loopを維持する",),
        "design_points": ("人が最終判断する",),
        "exact_value_ids": ("notification-normal-start",),
        "states": (),
        "actors_authorities": ("人: 最終判断",),
        "boundaries": ("ARGUSはBroker操作しない",),
        "relations": (),
        "cross_references": (),
        "primary_owner": "Human Interface",
        "diagram_plan": (),
        "source_locators": ("SDD §3.1",),
        "coverage_units": ("SDD-L0219",),
        "depth_target": "standard",
    }
    data.update(overrides)
    return SectionContext(**data)  # type: ignore[arg-type]


def values():  # type: ignore[no-untyped-def]
    return load_exact_values(json.loads((ROOT / "references/exact_values.json").read_text("utf-8")))


def test_parser_does_not_silently_drop_input() -> None:
    result = parse_sdd("# 節\n\n**課題：** 欠落を防ぐ。\nplain text\n")
    assert result.coverage.total_candidates == result.coverage.recognized == 3
    assert result.coverage.ok


def test_parser_accounts_for_fenced_content_and_closing_fence() -> None:
    result = parse_sdd("# 節\n```text\nraw line\n```\nafter fence\n")
    assert [unit.kind for unit in result.units] == ["heading", "fence", "code", "fence", "prose"]


def test_parser_report_counts_actual_sdd() -> None:
    path = ROOT.parents[2] / "docs/model/argus_structured_design_data_v0.1.md"
    result = parse_sdd(path.read_text("utf-8"))
    assert result.coverage.recognized > 1000
    assert sum(result.coverage.by_kind.values()) == result.coverage.recognized


@pytest.mark.parametrize(("field", "code"), [("problems", "EMPTY_PROBLEMS"), ("purposes", "EMPTY_PURPOSES")])
def test_planning_detects_empty_problem_or_purpose(field: str, code: str) -> None:
    plan = build_planning((context(**{field: ()}),))
    assert code in {finding.code for finding in plan.findings}


def test_exact_value_gate_accepts_approved_representation() -> None:
    assert exact_value_gate("通知は17時30分から。", ("notification-normal-start",), values()).passed


def test_japanese_and_exact_gates_share_catalog_definition() -> None:
    catalog = values()
    assert "17時30分" in accepted_tokens(catalog)
    assert exact_value_gate("17時30分", ("notification-normal-start",), catalog).passed
    assert japanese_gate("日本語の説明。17時30分", catalog, latin_limit=0).passed


def test_llm_snapshot_cannot_mutate_coverage() -> None:
    ledger = CoverageLedger((CoverageEntry("C-1", "SDD §1", "意味"),))
    snapshot = ledger.snapshot_for_llm()
    with pytest.raises(FrozenInstanceError):
        snapshot[0].status = CoverageStatus.PRESERVED  # type: ignore[misc]
    assert ledger.counts()["UNMAPPED"] == 1


def test_coverage_report_counts_python_updates() -> None:
    ledger = CoverageLedger((CoverageEntry("C-1", "SDD §1", "意味"),))
    ledger.update("C-1", CoverageStatus.PRESERVED, "HSD 1.1")
    assert ledger.counts()["PRESERVED"] == 1


def test_poc0_detects_known_failure() -> None:
    fixture = (ROOT / "tests/fixtures/poc0_known_failure.md").read_text("utf-8")
    report = run_poc0(fixture, ROOT / "references/exact_values.json")
    assert report["detected"] is True
    assert all(report["reports"][name] for name in ("japanese", "exact_value", "long_sentence", "problem_purpose"))
