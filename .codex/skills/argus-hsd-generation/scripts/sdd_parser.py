from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParsedUnit:
    unit_id: str
    line_number: int
    section: str
    kind: str
    text: str
    source_locators: tuple[str, ...] = ()
    exact_value_candidates: tuple[str, ...] = ()
    state_identifier_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class CoverageReport:
    total_lines: int
    total_candidates: int
    recognized_regions: int
    recognized: int
    unrecognized: int
    ambiguous: int
    duplicate_assignments: int
    unassigned: int
    unrecognized_locations: tuple[str, ...]
    by_kind: dict[str, int]
    labels: dict[str, int]
    tables: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return (
            self.total_candidates == self.recognized
            and self.unrecognized == 0
            and self.ambiguous == 0
            and self.duplicate_assignments == 0
            and self.unassigned == 0
        )


@dataclass(frozen=True)
class ParseResult:
    units: tuple[ParsedUnit, ...]
    coverage: CoverageReport


_LABEL = re.compile(r"^\*\*[^*]+[：:]\*\*")
_TABLE_SEPARATOR = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+$")
_SOURCE_LOCATOR = re.compile(r"§\d+(?:\.\d+)?(?:[A-Z])?(?:[〜～-]§?\d+(?:\.\d+)?)?")
_EXACT_VALUE = re.compile(
    r"(?<![A-Za-z0-9_])(?:\d+(?:\.\d+)?(?:%|時|分|秒|日|週|か月|ヶ月|箇月|年|件|回|GB|TB)|\d{1,2}:\d{2})(?![A-Za-z0-9_])"
)
_STATE_IDENTIFIER = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]*(?: / [A-Z][A-Z0-9_]*)*(?![A-Za-z0-9_])")


def _matching_kinds(line: str, in_fence: bool) -> list[str]:
    if line.startswith("```"):
        return ["fence"]
    if in_fence:
        return ["code"]
    matches: list[str] = []
    if line.startswith("#") and re.match(r"^#{1,6}\s+\S", line):
        matches.append("heading")
    if _LABEL.match(line):
        matches.append("label")
    if line.startswith("|") and line.endswith("|"):
        matches.append("table_separator" if _TABLE_SEPARATOR.match(line) else "table_row")
    if re.match(r"^\s*(?:[-*+] |\d+[.)] )", line):
        matches.append("list_item")
    if line.strip() in {"---", "***", "___"}:
        matches.append("separator")
    if not matches:
        matches.append("prose")
    return matches


def parse_sdd(text: str) -> ParseResult:
    units: list[ParsedUnit] = []
    current_section = "document"
    unrecognized = ambiguous = duplicate = unassigned = 0
    in_fence = False
    labels: Counter[str] = Counter()
    tables: list[str] = []
    current_table = ""
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        kinds = _matching_kinds(line, in_fence)
        if len(kinds) != 1:
            ambiguous += 1
            continue
        kind = kinds[0]
        if not kind:
            unrecognized += 1
            continue
        if kind == "heading":
            current_section = re.sub(r"^#+\s+", "", line)
            current_table = ""
        if not current_section:
            unassigned += 1
            continue
        unit_id = f"SDD-L{line_number:04d}"
        if any(unit.unit_id == unit_id for unit in units):
            duplicate += 1
            continue
        label_match = _LABEL.match(line)
        if label_match:
            label = re.sub(r"^\*\*|[：:]\*\*$", "", label_match.group(0))
            labels[label] += 1
        if kind == "table_row" and not current_table:
            current_table = f"{current_section} (line {line_number})"
            tables.append(current_table)
        if kind not in {"table_row", "table_separator"}:
            current_table = ""
        units.append(
            ParsedUnit(
                unit_id,
                line_number,
                current_section,
                kind,
                line,
                tuple(_SOURCE_LOCATOR.findall(line)),
                tuple(_EXACT_VALUE.findall(line)),
                tuple(_STATE_IDENTIFIER.findall(line)),
            )
        )
        if kind == "fence":
            in_fence = not in_fence
    by_kind = dict(sorted(Counter(unit.kind for unit in units).items()))
    report = CoverageReport(
        total_lines=len(text.splitlines()),
        total_candidates=len(units) + unrecognized + ambiguous + duplicate + unassigned,
        recognized_regions=len(units),
        recognized=len(units),
        unrecognized=unrecognized,
        ambiguous=ambiguous,
        duplicate_assignments=duplicate,
        unassigned=unassigned,
        unrecognized_locations=(),
        by_kind=by_kind,
        labels=dict(sorted(labels.items())),
        tables=tuple(tables),
    )
    if not report.ok:
        raise ValueError(f"SDD parser self-coverage failed: {report}")
    return ParseResult(tuple(units), report)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: sdd_parser.py <sdd.md>", file=sys.stderr)
        return 2
    result = parse_sdd(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(result.coverage.__dict__, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
