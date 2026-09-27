from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def strict_utf8_load(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    if text.encode("utf-8", errors="strict") != raw:
        raise UnicodeError("UTF-8 round-trip mismatch")
    return raw, text


def cp932_misdecode_recovery(value: str) -> str | None:
    """Return a plausible original when UTF-8 bytes were decoded as CP932.

    This is detection only.  Callers must compare the candidate with authority;
    this function never rewrites an artifact.
    """
    try:
        recovered = value.encode("cp932", errors="strict").decode("utf-8", errors="strict")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return recovered if recovered != value else None


def iter_strings(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def scan_context(path: Path) -> dict[str, Any]:
    raw, text = strict_utf8_load(path)
    payload = json.loads(text)
    candidates: list[dict[str, str]] = []
    for location, value in iter_strings(payload):
        if "\ufffd" in value:
            candidates.append({"location": location, "value": value, "kind": "U+FFFD"})
        recovered = cp932_misdecode_recovery(value)
        if recovered is not None:
            candidates.append({
                "location": location,
                "value": value,
                "kind": "CP932_MISDECODE_CANDIDATE",
                "recovered_candidate": recovered,
            })
    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "strict_utf8": "PASS",
        "utf8_roundtrip": "PASS",
        "candidates": candidates,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("contexts", nargs="+", type=Path)
    args = parser.parse_args()
    scans = [scan_context(path) for path in args.contexts]
    report = {
        "contexts_scanned": len(scans),
        "strict_utf8_pass": sum(item["strict_utf8"] == "PASS" for item in scans),
        "candidate_count": sum(len(item["candidates"]) for item in scans),
        "classification_policy": "Candidates require authority comparison; this scanner never rewrites content.",
        "contexts": scans,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
