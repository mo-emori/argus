from __future__ import annotations

import json
from pathlib import Path

from poc0_gates import GateOutcome, gate_jp, gate_state, gate_struct, gate_value
from poc0_regression import run, verify_inputs
from sdd_parser import parse_sdd

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


def metadata() -> dict[str, object]:
    return json.loads(
        (SKILL_ROOT / "tests/fixtures/failure_fixture_v0.1.4.json").read_text("utf-8")
    )


def oracle_cases() -> dict[str, dict[str, object]]:
    data = json.loads((SKILL_ROOT / "tests/oracle/poc0_oracle_v0.1.json").read_text("utf-8"))
    return {case["id"]: case for case in data["cases"]}


def test_input_hashes_and_hsd_header_match() -> None:
    assert verify_inputs(REPO_ROOT, metadata())["passed"] is True


def test_parser_coverage_contains_required_evidence() -> None:
    sdd = (REPO_ROOT / str(metadata()["sdd_path"])).read_text("utf-8")
    report = parse_sdd(sdd).coverage
    assert report.total_lines > report.recognized_regions > 1000
    assert report.unrecognized_locations == ()
    assert report.labels["課題"] > 0
    assert report.labels["目的"] > 0
    assert len(report.tables) > 0


def test_gate_jp_distinguishes_prohibited_and_conditional_terms() -> None:
    hsd = (REPO_ROOT / str(metadata()["source_path"])).read_text("utf-8")
    cases = oracle_cases()
    assert gate_jp(hsd, cases["JP-DATA-001"]).outcome is GateOutcome.FAIL
    assert gate_jp(hsd, cases["JP-UNIVERSE-001"]).outcome is GateOutcome.PASS
    assert gate_jp(hsd, cases["JP-BRANCHES-001"]).outcome is GateOutcome.PASS


def test_gate_value_checks_absence_and_label_proximity() -> None:
    hsd = (REPO_ROOT / str(metadata()["source_path"])).read_text("utf-8")
    cases = oracle_cases()
    assert gate_value(hsd, cases["VALUE-NOTIFY-1730"]).outcome is GateOutcome.FAIL
    assert gate_value(hsd, cases["VALUE-BUSY-1H"]).outcome is GateOutcome.FAIL
    assert gate_value(hsd, cases["VALUE-PAPER-1M"]).outcome is GateOutcome.PASS


def test_gate_state_is_limited_to_runner_section() -> None:
    hsd = (REPO_ROOT / str(metadata()["source_path"])).read_text("utf-8")
    assert gate_state(hsd, oracle_cases()["STATE-RUNNER-001"]).outcome is GateOutcome.PASS


def test_gate_struct_requires_semantic_review() -> None:
    hsd = (REPO_ROOT / str(metadata()["source_path"])).read_text("utf-8")
    sdd = (REPO_ROOT / str(metadata()["sdd_path"])).read_text("utf-8")
    result = gate_struct(hsd, sdd, oracle_cases()["STRUCT-EXPLORATION-001"])
    assert result.outcome is GateOutcome.REVIEW
    assert result.code == "SEMANTIC_REVIEW_REQUIRED"


def test_poc0_regression_detects_all_critical_expected_findings() -> None:
    result = run(REPO_ROOT, SKILL_ROOT)
    assert result["poc0"] == "PASS"
    summary = result["summary"]
    assert summary["missed_findings"] == 0
    assert summary["false_positives"] == 0
    assert summary["critical_missed"] == []
