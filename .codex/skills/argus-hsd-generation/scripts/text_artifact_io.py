from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from translation_stage import TranslationContract, TranslationOutput, digest_text


def unicode_representation(value: str) -> dict[str, Any]:
    return {
        "text": value,
        "code_points": [f"U+{ord(character):04X}" for character in value],
        "utf8_hex": value.encode("utf-8").hex(),
    }


def validate_utf8_roundtrip(text: str) -> list[str]:
    encoded = text.encode("utf-8", errors="strict")
    decoded = encoded.decode("utf-8", errors="strict")
    return [] if decoded == text else ["UTF8_ROUNDTRIP_MISMATCH"]


def validate_protected_values_before_persistence(
    source_draft: str,
    translated_text: str,
    contract: TranslationContract,
) -> list[str]:
    protected = (
        contract.protected_identifiers
        + contract.protected_literals
        + contract.protected_state_names
        + contract.protected_paths
        + contract.protected_numeric_values
    )
    return [
        f"PROTECTED_VALUE_CHANGED:{value}"
        for value in protected
        if value in source_draft and value not in translated_text
    ]


def persist_translation_artifacts(
    markdown_path: Path,
    output_path: Path,
    source_draft: str,
    output: TranslationOutput,
    contract: TranslationContract,
) -> None:
    """Validate Unicode/protected invariants, then persist explicit UTF-8 artifacts.

    This function never repairs text and contains no character-specific replacement.
    """
    findings = validate_utf8_roundtrip(output.content)
    findings.extend(validate_protected_values_before_persistence(source_draft, output.content, contract))
    if output.generated_artifact_digest != digest_text(output.content):
        findings.append("GENERATED_ARTIFACT_DIGEST_MISMATCH")
    if findings:
        raise ValueError(",".join(findings))

    markdown_bytes = output.content.encode("utf-8", errors="strict")
    output_json = json.dumps(asdict(output), ensure_ascii=False, indent=2) + "\n"
    output_bytes = output_json.encode("utf-8", errors="strict")
    reloaded = json.loads(output_bytes.decode("utf-8", errors="strict"))
    if reloaded["content"] != output.content:
        raise ValueError("SERIALIZED_CONTENT_MISMATCH")

    markdown_tmp = markdown_path.with_name(markdown_path.name + ".tmp")
    output_tmp = output_path.with_name(output_path.name + ".tmp")
    try:
        markdown_tmp.write_bytes(markdown_bytes)
        output_tmp.write_bytes(output_bytes)
        if markdown_tmp.read_bytes().decode("utf-8", errors="strict") != output.content:
            raise ValueError("MARKDOWN_RELOAD_MISMATCH")
        persisted = json.loads(output_tmp.read_bytes().decode("utf-8", errors="strict"))
        if persisted["content"] != output.content:
            raise ValueError("OUTPUT_RELOAD_MISMATCH")
        os.replace(markdown_tmp, markdown_path)
        os.replace(output_tmp, output_path)
    finally:
        markdown_tmp.unlink(missing_ok=True)
        output_tmp.unlink(missing_ok=True)
