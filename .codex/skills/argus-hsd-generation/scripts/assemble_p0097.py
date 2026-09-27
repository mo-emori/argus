from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    report = args.root.resolve() / "validation/reports/argus-p-0097-v1"
    section_34 = (report / "section-3.4.md").read_text("utf-8").rstrip()
    section_35 = (report / "section-3.5.md").read_text("utf-8").rstrip()
    assembled = section_34 + "\n\n" + section_35 + "\n"
    output = report / "section-3.4-3.5-assembled.md"
    output.write_text(assembled, "utf-8")
    evidence = {
        "artifact": str(output),
        "section_3_4_sha256": sha256_file(report / "section-3.4.md"),
        "section_3_5_sha256": sha256_file(report / "section-3.5.md"),
        "assembled_sha256": sha256_file(output),
        "method": "exact ordered concatenation with one blank line; no prose rewriting",
    }
    (report / "assembly-evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
