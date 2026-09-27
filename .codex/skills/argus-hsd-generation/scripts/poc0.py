from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from contracts import load_exact_values
from gates import exact_value_gate, japanese_gate, long_sentence_gate, problem_purpose_gate


def run_poc0(hsd_text: str, exact_values_path: Path) -> dict[str, object]:
    values = load_exact_values(json.loads(exact_values_path.read_text(encoding="utf-8")))
    reports = {
        "japanese": japanese_gate(hsd_text, values, latin_limit=25),
        "exact_value": exact_value_gate(
            hsd_text, ("notification-normal-start", "paper-duration"), values
        ),
        "long_sentence": long_sentence_gate(hsd_text, comma_limit=3),
        "problem_purpose": problem_purpose_gate(hsd_text),
    }
    return {
        "detected": any(not report.passed for report in reports.values()),
        "reports": {name: [asdict(item) for item in report.findings] for name, report in reports.items()},
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: poc0.py <known-failed-hsd.md>", file=sys.stderr)
        return 2
    script_root = Path(__file__).resolve().parent.parent
    result = run_poc0(
        Path(sys.argv[1]).read_text(encoding="utf-8"),
        script_root / "references" / "exact_values.json",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
