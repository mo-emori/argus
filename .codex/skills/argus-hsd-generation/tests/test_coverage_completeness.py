from __future__ import annotations

from coverage_completeness import validate_context_to_contract


def contract(meaning: str, required: str, status: str = "PRESERVED") -> str:
    return (
        "| Coverage ID | SDD位置 | 設計意味 | 保存必須要素 | 関係対象 | 許容表現 | HSD配置先 | 判定 | 備考 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"| C-1 | L1 | {meaning} | {required} | 対象 | 本文 | 3.4 | {status} | 理由 |\n"
    )


def context(text: str) -> dict[str, object]:
    return {"rules": [{"coverage_id": "C-1", "original_text": text}]}


def test_r05_context_meaning_missing_from_contract_fails() -> None:
    result = validate_context_to_contract(
        context("Secretをproject、config、log、evidence、report、backupへ保存しない"),
        contract("Secretを保存しない", "prohibition"),
    )
    assert result["status"] == "FAIL"
    assert any(item["code"] == "COVERAGE_TARGETS_SHRUNK" for item in result["findings"])


def test_partial_targets_fail() -> None:
    result = validate_context_to_contract(context("Application Log / Audit Log / Report / Backup"), contract("Log", "Log"))
    assert result["status"] == "FAIL"


def test_multiple_meanings_merged_to_vague_unit_fails() -> None:
    result = validate_context_to_contract(context("Alpha、Beta、Gamma、Delta"), contract("対象群", "関係を保存"))
    assert any(item["code"] == "INDEPENDENT_MEANINGS_AMBIGUOUSLY_MERGED" for item in result["findings"])


def test_empty_original_text_is_not_autofilled() -> None:
    result = validate_context_to_contract(context(""), contract("周辺から補完", "推測"))
    assert any(item["code"] == "CONTEXT_MEANING_EMPTY" for item in result["findings"])


def test_all_review_does_not_pass() -> None:
    result = validate_context_to_contract(context("Secret backup"), contract("Secret backup", "Secret backup", "REVIEW"))
    assert any(item["code"] == "ALL_REVIEW_CANNOT_PASS" for item in result["findings"])
