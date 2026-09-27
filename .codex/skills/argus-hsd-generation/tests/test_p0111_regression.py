from __future__ import annotations

import json
from pathlib import Path

from hsd_quality_policy import QualityFinding, SectionResult, classify_finding, section_result

ROOT = Path(__file__).resolve().parents[4]


def test_p0110_metadata_leakage_is_review_not_blocker() -> None:
    path = ROOT / "validation/reports/argus-p-0110-v1/multi-section-poc/sections/section-1.2/english-semantic-review-repair-1.json"
    review = json.loads(path.read_text("utf-8"))
    assert review["findings"][0]["category"] == "metadata_leak"
    item = QualityFinding("METADATA_LEAKAGE", classify_finding("METADATA_LEAKAGE"))
    assert section_result([item]) is SectionResult.ACCEPT_WITH_FINDINGS


def test_p0109_literal_normalization_and_reference_omission_are_review() -> None:
    evidence = json.loads((ROOT / "validation/reports/argus-p-0109-v1/execution-summary.json").read_text("utf-8"))
    assert evidence["authority_stage_value"] == "17〜18"
    assert "17–18" in evidence["first_loss"]
    assert evidence["section_49_classification"] == "WRITER_OMISSION"
    items = [
        QualityFinding(code, classify_finding(code))
        for code in ("MEANING_PRESERVING_LITERAL_NORMALIZATION", "DESIGN_REFERENCE_OMISSION")
    ]
    assert section_result(items) is SectionResult.ACCEPT_WITH_FINDINGS


def test_value_or_order_corruption_remains_blocker() -> None:
    item = QualityFinding(
        "BEHAVIOR_CHANGING_NUMERIC_ALTERATION",
        classify_finding("BEHAVIOR_CHANGING_NUMERIC_ALTERATION"),
    )
    assert section_result([item]) is SectionResult.BLOCKED


def test_p0105_translation_findings_remain_non_blocking_when_preserved() -> None:
    path = ROOT / "validation/reports/argus-p-0105-v1/section-3.5.2-semantic-review.json"
    review = json.loads(path.read_text("utf-8"))
    assert review["review_result"] == "PASS"
    assert {item["status"] for item in review["findings"]} == {"PRESERVED"}
    assert section_result([]) is SectionResult.PASS
