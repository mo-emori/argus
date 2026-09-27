from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from section_writer_pipeline import parse_coverage_contract

CONTEXT_COLLECTIONS = (
    "premises", "problems", "purposes", "design_reasons", "processes", "rules",
    "prohibitions", "exceptions", "abnormal_handling",
)
TOKEN_STOP = {
    "the", "and", "or", "to", "of", "in", "for", "with", "等", "TBD",
}


def _base_id(coverage_id: str) -> str:
    return re.sub(r"-[a-z][a-z0-9]*$", "", coverage_id)


def _meaningful_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z][A-Za-z0-9_./-]*", text))
    return {token for token in tokens if token.lower() not in TOKEN_STOP and len(token) > 1}


def validate_context_to_contract(context: dict[str, Any], contract_markdown: str) -> dict[str, Any]:
    rows = parse_coverage_contract(contract_markdown)
    by_base: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_base.setdefault(_base_id(row["Coverage ID"]), []).append(row)
    findings: list[dict[str, str]] = []
    checked = 0
    for collection in CONTEXT_COLLECTIONS:
        for item in context.get(collection, []):
            checked += 1
            coverage_id = item["coverage_id"]
            original = str(item.get("original_text", "")).strip()
            matches = by_base.get(coverage_id, [])
            if not original:
                findings.append({"code": "CONTEXT_MEANING_EMPTY", "coverage_id": coverage_id, "detail": collection})
                continue
            if not matches:
                findings.append({"code": "CONTEXT_MEANING_UNMAPPED", "coverage_id": coverage_id, "detail": collection})
                continue
            represented = " ".join(" ".join(row.values()) for row in matches)
            missing_tokens = sorted(_meaningful_tokens(original) - _meaningful_tokens(represented))
            if missing_tokens:
                findings.append({
                    "code": "COVERAGE_TARGETS_SHRUNK",
                    "coverage_id": coverage_id,
                    "detail": ", ".join(missing_tokens),
                })
            independent = [value.strip() for value in re.split(r"[、,]", original) if value.strip()]
            if len(independent) >= 4 and len(matches) == 1 and missing_tokens:
                findings.append({
                    "code": "INDEPENDENT_MEANINGS_AMBIGUOUSLY_MERGED",
                    "coverage_id": coverage_id,
                    "detail": f"{len(independent)} candidates in one Coverage Unit",
                })
    statuses = [row["判定"] for row in rows]
    if statuses and all(status == "REVIEW" for status in statuses):
        findings.append({"code": "ALL_REVIEW_CANNOT_PASS", "coverage_id": "*", "detail": "all rows are REVIEW"})
    return {
        "status": "PASS" if not findings else "FAIL",
        "context_meanings_checked": checked,
        "coverage_units_checked": len(rows),
        "findings": findings,
        "scope": "Section Context to Coverage Contract only; Source to SDD completeness is not claimed",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("context_json", type=Path)
    parser.add_argument("contract_markdown", type=Path)
    parser.add_argument("section_id")
    args = parser.parse_args()
    payload = json.loads(args.context_json.read_text("utf-8"))
    sections = payload.get("sections", [payload])
    context = next(item for item in sections if item["section_id"] == args.section_id)
    result = validate_context_to_contract(context, args.contract_markdown.read_text("utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    blocking = [item for item in result["findings"] if item["code"] != "ALL_REVIEW_CANNOT_PASS"]
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
