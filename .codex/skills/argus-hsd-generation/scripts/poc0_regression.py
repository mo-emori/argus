from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from poc0_gates import GateOutcome, evaluate_case
from sdd_parser import parse_sdd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _header_hash(hsd: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\* `([0-9a-f]{{64}})`", hsd)
    if not match:
        raise ValueError(f"missing HSD header hash: {label}")
    return match.group(1)


def verify_inputs(repo: Path, metadata: dict[str, Any]) -> dict[str, object]:
    paths = {key: repo / str(metadata[key]) for key in ("source_path", "sdd_path", "design_source_path")}
    actual = {key: sha256(path) for key, path in paths.items()}
    expected = {
        "source_path": str(metadata["sha256"]),
        "sdd_path": str(metadata["sdd_sha256"]),
        "design_source_path": str(metadata["design_source_sha256"]),
    }
    hsd = paths["source_path"].read_text(encoding="utf-8")
    header = {
        "sdd_path": _header_hash(hsd, "SDD SHA-256"),
        "design_source_path": _header_hash(hsd, "Design Source SHA-256"),
    }
    mismatches = [key for key in actual if actual[key] != expected[key]]
    mismatches.extend(key for key in header if header[key] != actual[key])
    return {"actual": actual, "expected": expected, "header": header, "mismatches": sorted(set(mismatches)), "passed": not mismatches}


def classify(expected: str, actual: GateOutcome) -> str:
    if expected == "FAIL":
        return "DETECTED" if actual is GateOutcome.FAIL else ("REVIEW" if actual is GateOutcome.REVIEW else "MISSED")
    if expected == "PASS":
        return "CONFIRMED" if actual is GateOutcome.PASS else ("REVIEW" if actual is GateOutcome.REVIEW else "FALSE_POSITIVE")
    return "REVIEW"


def run(repo: Path, skill_root: Path) -> dict[str, object]:
    metadata = json.loads((skill_root / "tests/fixtures/failure_fixture_v0.1.4.json").read_text("utf-8"))
    verification = verify_inputs(repo, metadata)
    if not verification["passed"]:
        return {"input_verification": verification, "poc0": "FAIL_CLOSED", "reason": "INPUT_SHA_MISMATCH"}
    oracle = json.loads((skill_root / "tests/oracle/poc0_oracle_v0.1.json").read_text("utf-8"))
    hsd = (repo / metadata["source_path"]).read_text("utf-8")
    sdd = (repo / metadata["sdd_path"]).read_text("utf-8")
    parser = parse_sdd(sdd)
    rows: list[dict[str, object]] = []
    for case in oracle["cases"]:
        result = evaluate_case(hsd, sdd, case)
        regression = classify(str(case["expected"]), result.outcome)
        rows.append({
            "id": case["id"], "gate": case["gate"], "expected": case["expected"],
            "actual": result.outcome.value, "regression": regression,
            "critical": case["critical"], "code": result.code, "detail": result.detail,
        })
    counts = Counter(str(row["regression"]) for row in rows)
    expected_findings = sum(row["expected"] == "FAIL" for row in rows)
    detected = counts["DETECTED"]
    critical_missed = [row["id"] for row in rows if row["critical"] and row["regression"] == "MISSED"]
    summary = {
        "expected_findings": expected_findings,
        "detected_findings": detected,
        "missed_findings": counts["MISSED"],
        "false_positives": counts["FALSE_POSITIVE"],
        "review_required": counts["REVIEW"],
        "detection_rate": detected / expected_findings if expected_findings else 1.0,
        "critical_missed": critical_missed,
    }
    poc_pass = not critical_missed and counts["MISSED"] == 0 and counts["FALSE_POSITIVE"] == 0
    return {
        "input_verification": verification,
        "parser_coverage": parser.coverage.__dict__,
        "oracle_cases": len(oracle["cases"]),
        "results": rows,
        "summary": summary,
        "poc0": "PASS" if poc_pass else "FAIL",
        "stop": "STOP Human Review",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: poc0_regression.py <repo-root>", file=sys.stderr)
        return 2
    repo = Path(sys.argv[1]).resolve()
    result = run(repo, Path(__file__).resolve().parent.parent)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result.get("poc0") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
