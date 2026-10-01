"""Build and machine-check the unfrozen Runtime Entry Resolution v0.2 metadata."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
TEST = Path("tests/runtime_entry_resolution/test_runtime_entry_resolution_candidate.py")
HELPER = Path("tests/runtime_entry_resolution/_candidate.py")
SEMANTIC = Path("tests/runtime_entry_resolution/_semantic_boundaries.py")
MUTANTS = Path("tests/runtime_entry_resolution/test_semantic_mutant_diagnostics.py")
CONTRACT = Path("docs/contracts/argus_runtime_entry_resolution_contract_v0.1.md")
STRATEGY = Path("docs/test/argus_runtime_entry_resolution_test_strategy_v0.1.md")
PRODUCTION = Path("src/argus/runtime/runtime_entry_resolution.py")
OLD_METADATA = Path("validation/evidence/runtime-entry-resolution/PRE-RED-COMPLETION-RUNTIME-ENTRY-RESOLUTION-20261001-001/test-observation-bindings.json")
OUTPUT = Path("validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.2.candidate.json")


def digest(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def ids() -> list[str]:
    return [
        *(f"RER-U-{number:03d}" for number in range(1, 23)),
        *(f"RER-C-{number:03d}" for number in range(1, 35)),
        *(f"RER-I-{number:03d}" for number in range(1, 9)),
        *(f"RER-S-{number:03d}" for number in range(1, 9)),
    ]


def test_functions() -> dict[str, str]:
    tree = ast.parse((ROOT / TEST).read_text(encoding="utf-8"))
    found: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_rer_"):
            test_id = "-".join(node.name.split("_")[1:4]).upper()
            if test_id in found:
                raise ValueError(f"duplicate test binding: {test_id}")
            found[test_id] = node.name
    return found


def main() -> None:
    canonical = ids()
    functions = test_functions()
    if set(functions) != set(canonical) or len(functions) != 72:
        raise ValueError("canonical ID/test alignment failed")
    old = cast(dict[str, Any], json.loads((ROOT / OLD_METADATA).read_text(encoding="utf-8")))
    old_by_id = {record["test_id"]: record for record in old["records"]}
    pass_permitted = {"RER-I-006", "RER-S-005", "RER-S-006", "RER-S-008"}
    new_clauses = {
        "RER-U-021": "§§3.2-3.3", "RER-U-022": "§§3.3, 6",
        **{f"RER-C-{number:03d}": "§§4, 6" for number in range(26, 33)},
        "RER-C-033": "§§4.1, 7", "RER-C-034": "§7",
        "RER-I-007": "§§5, 7", "RER-I-008": "§§2, 7",
        "RER-S-007": "§§2, 5, 7", "RER-S-008": "§9",
    }
    records: list[dict[str, Any]] = []
    for test_id in canonical:
        previous = old_by_id.get(test_id, {})
        previous_expected = previous.get("expected_observation", {})
        classification = "PASS_PERMITTED" if test_id in pass_permitted else "RED_REQUIRED"
        records.append({
            "test_id": test_id,
            "contract_clause": previous.get("contract_clause", new_clauses.get(test_id, "Corrective Strategy §16 binding to unchanged Contract")),
            "test_binding": {"path": TEST.as_posix(), "function": functions[test_id]},
            "non_vacuity_condition": previous.get("non_vacuity_binding", {}).get("required_consumption", "The named concrete test must reach its recorded public/runtime/static boundary and consume the exact sentinel observation; skip, xfail, canned results, and source-spelling assertions are prohibited."),
            "expected_pre_correction_revision_observation": previous_expected.get("pre_implementation", {"outcome": classification, "observation": "Corrective candidate observation per Test Strategy §16; semantic/static IDs bind the defective production surface and inherited/lifecycle IDs retain their explicit permitted observation."}),
            "later_green_observation": previous_expected.get("later_green", {"outcome": "PASS", "observation": "Exact corrected Contract behavior and non-vacuity oracle pass after a separately authorized Production correction."}),
            "classification": classification,
            "concrete_test_refs": [f"{TEST.as_posix()}::{functions[test_id]}"],
            "historical_invalidation_refs": ["validation/baselines/runtime-entry-resolution/RUNTIME-ENTRY-RESOLUTION-v0.1.baseline.json", "validation/evidence/runtime-entry-resolution/CORRECTIVE-TEST-REVISION-RUNTIME-ENTRY-RESOLUTION-20261001-001/corrective-test-revision.json"],
            "authoritative_refs": [CONTRACT.as_posix(), STRATEGY.as_posix()],
            "freeze_lifecycle": {"freeze_status": "NOT_FROZEN", "freeze_evidence_id": None, "human_approval_ref": None, "revision_red_evidence_id": None, "green_evidence_id": None},
        })
    hashes = {path.as_posix(): digest(path) for path in (CONTRACT, STRATEGY, TEST, HELPER, SEMANTIC, MUTANTS, PRODUCTION)}
    candidate: dict[str, Any] = {
        "record_type": "CORRECTED_PRE_RED_BASELINE_CANDIDATE",
        "metadata_version": 2,
        "candidate_id": "RUNTIME-ENTRY-RESOLUTION-v0.2-candidate",
        "status": "UNFROZEN_CORRECTED_PRE_RED_CANDIDATE",
        "registry_status": "IN_PROGRESS",
        "contract_semantics": "UNCHANGED",
        "canonical_test_id_count": 72,
        "canonical_concrete_case_count": 118,
        "diagnostic_mutant_case_count": 13,
        "total_collection_case_count": 131,
        "case_count_change_reason": "Thirteen non-canonical diagnostic cases exercise twelve forbidden semantic mutants and one legitimate typed implementation; the 72 canonical IDs and their 118 concrete cases are unchanged.",
        "hashes": hashes,
        "authoritative_references": [CONTRACT.as_posix(), STRATEGY.as_posix(), "docs/source/argus_design_source_v0.1.md", "docs/test/argus_test_strategy_v0.1.3.md"],
        "historical_evidence_preserved": True,
        "freeze_authorized": False,
        "formal_revision_red_authorized": False,
        "records": records,
        "machine_check": {"record_count": len(records), "unique_id_count": len({record["test_id"] for record in records}), "missing": [], "duplicates": [], "unexpected": [], "test_binding_alignment": "PASS"},
        "next_step": "Retry corrected Pre-RED static/non-vacuity/mutant validation only; require separate Human authorization before Freeze or Formal Revision RED.",
    }
    (ROOT / OUTPUT).write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(candidate["machine_check"], sort_keys=True))


if __name__ == "__main__":
    main()
