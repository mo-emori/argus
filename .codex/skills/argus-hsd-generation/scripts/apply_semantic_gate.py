from __future__ import annotations

import argparse
import re
from pathlib import Path

DECISIONS = {"PRESERVED", "REFERENCED", "REVIEW", "MISSING", "DISTORTED", "INVENTED"}


def decision_map(review: str) -> dict[str, str]:
    decisions: dict[str, str] = {}
    for line in review.splitlines():
        match = re.match(r"^\|\s*(SDD-L\d+(?:-[a-z][a-z0-9]*)?)\s*\|\s*([A-Z]+)\s*\|", line)
        if match and match.group(2) in DECISIONS:
            decisions[match.group(1)] = match.group(2)
    return decisions


def apply_decisions(contract: str, decisions: dict[str, str]) -> str:
    output: list[str] = []
    seen: set[str] = set()
    for line in contract.splitlines():
        if not line.startswith("|"):
            output.append(line)
            continue
        cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
        cells = [cell.strip() for cell in cells]
        coverage_id = cells[0] if cells else ""
        if coverage_id in decisions and len(cells) == 9:
            cells[7] = decisions[coverage_id]
            cells[8] = "Independent Semantic Reviewerが本文根拠を個別照合済み。詳細はSection Semantic Gateを参照。"
            line = "| " + " | ".join(cells) + " |"
            seen.add(coverage_id)
        output.append(line)
    missing = set(decisions) - seen
    if missing:
        raise ValueError(f"review decisions not found in contract: {sorted(missing)}")
    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    decisions = decision_map(args.review.read_text("utf-8"))
    if not decisions or any(value in {"MISSING", "DISTORTED", "INVENTED"} for value in decisions.values()):
        raise PermissionError("semantic gate has an unclassified potentially blocking finding")
    updated = apply_decisions(args.contract.read_text("utf-8"), decisions)
    args.contract.write_text(updated, "utf-8")
    print(f"updated {len(decisions)} Coverage Units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
