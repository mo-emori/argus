from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from planning_schema import SectionContext
from sdd_parser import ParseResult


@dataclass(frozen=True)
class ReconciliationEntry:
    baseline_coverage_id: str
    baseline_locator: str
    current_coverage_ids: tuple[str, ...]
    current_locators: tuple[str, ...]
    disposition: str
    reason: str


_ROW = re.compile(r"^\|\s*(HSD-COV-\d+)\s*\|\s*([^|]+)\|")
_LINE = re.compile(r"line\s+(\d+)", re.IGNORECASE)


def parse_baseline(text: str) -> tuple[tuple[str, str, int | None], ...]:
    rows: list[tuple[str, str, int | None]] = []
    for raw in text.splitlines():
        match = _ROW.match(raw)
        if not match:
            continue
        locator = match.group(2).strip()
        line_match = _LINE.search(locator)
        rows.append((match.group(1), locator, int(line_match.group(1)) if line_match else None))
    return tuple(rows)


def reconcile_coverage(
    baseline_text: str, parsed: ParseResult, contexts: tuple[SectionContext, ...]
) -> dict[str, Any]:
    assignments = [item for context in contexts for item in context.coverage_units]
    by_line: dict[int, list[Any]] = {}
    for item in assignments:
        line_match = re.search(r"(\d+)$", item.source_locator)
        if line_match:
            by_line.setdefault(int(line_match.group(1)), []).append(item)
    parsed_by_line = {item.line_number: item for item in parsed.units}
    coverage_lines = sorted(by_line)
    entries: list[ReconciliationEntry] = []
    for coverage_id, locator, line_number in parse_baseline(baseline_text):
        exact = by_line.get(line_number or -1, [])
        if exact:
            disposition = "SAME" if len(exact) == 1 else "SPLIT"
            reason = "same SDD source line" if len(exact) == 1 else "one baseline unit maps to multiple current assignments"
            targets = exact
        elif line_number is not None and parsed_by_line.get(line_number) and parsed_by_line[line_number].kind == "list_item":
            preceding = [line for line in coverage_lines if line < line_number]
            nearest = preceding[-1] if preceding else None
            targets = by_line.get(nearest or -1, [])
            disposition = "MERGED" if targets else "MISSING"
            reason = "independent bullet is grouped into its enclosing labeled/table design unit" if targets else "no enclosing current design unit"
        elif line_number is not None and parsed_by_line.get(line_number) and parsed_by_line[line_number].kind in {"heading", "table_separator", "separator"}:
            targets = []
            disposition = "EXCLUDED_NON_DESIGN"
            reason = "structural Markdown is outside the current design-unit definition"
        else:
            targets = []
            disposition = "MISSING"
            reason = "baseline unit has no traceable current assignment"
        entries.append(ReconciliationEntry(
            coverage_id,
            locator,
            tuple(item.coverage_id for item in targets),
            tuple(item.source_locator for item in targets),
            disposition,
            reason,
        ))
    counts = Counter(entry.disposition for entry in entries)
    baseline_count = len(entries)
    current_count = len(assignments)
    matched_current = {coverage_id for entry in entries for coverage_id in entry.current_coverage_ids}
    current_only = sorted(item.coverage_id for item in assignments if item.coverage_id not in matched_current)
    return {
        "baseline_definition": "P-0085 Coverage Map: table rows, explicit labeled design items, and independent bulleted rules; Markdown structure excluded",
        "current_definition": "P-0086 parser: table data rows and explicit labeled design items; independent bullets remain grouped under enclosing units",
        "baseline_units": baseline_count,
        "current_units": current_count,
        "delta": current_count - baseline_count,
        "dispositions": dict(sorted(counts.items())),
        "missing": counts.get("MISSING", 0),
        "current_only_count": len(current_only),
        "current_only_coverage_ids": current_only,
        "entries": [asdict(entry) for entry in entries],
    }
