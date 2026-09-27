from __future__ import annotations

from dataclasses import dataclass

from contracts import CoverageStatus


@dataclass(frozen=True)
class CoverageEntry:
    unit_id: str
    source_locator: str
    meaning: str
    status: CoverageStatus = CoverageStatus.UNMAPPED
    placement: str = ""


class CoverageLedger:
    def __init__(self, entries: tuple[CoverageEntry, ...]) -> None:
        if len({entry.unit_id for entry in entries}) != len(entries):
            raise ValueError("duplicate coverage unit")
        self._entries = {entry.unit_id: entry for entry in entries}

    def update(self, unit_id: str, status: CoverageStatus, placement: str) -> None:
        if unit_id not in self._entries:
            raise KeyError(unit_id)
        if status in {CoverageStatus.PRESERVED, CoverageStatus.REFERENCED} and not placement:
            raise ValueError("covered unit requires placement")
        current = self._entries[unit_id]
        self._entries[unit_id] = CoverageEntry(
            unit_id=current.unit_id,
            source_locator=current.source_locator,
            meaning=current.meaning,
            status=status,
            placement=placement,
        )

    def snapshot_for_llm(self) -> tuple[CoverageEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    def counts(self) -> dict[str, int]:
        return {
            status.value: sum(entry.status is status for entry in self._entries.values())
            for status in CoverageStatus
        }

