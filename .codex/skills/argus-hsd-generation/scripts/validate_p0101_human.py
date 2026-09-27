from __future__ import annotations

import json
from pathlib import Path

from human_facing_gate import evaluate_human_facing

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0101-v1"
contract = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text("utf-8"))
text = (REPORT / "section-3.5.2-ja.md").read_text("utf-8")
protected = set(contract["protected_identifiers"] + contract["protected_literals"] + contract["protected_paths"])
result = evaluate_human_facing(text, protected, enforce_japanese=True)
lines = [
    "# Section 3.5.2 Human-facing Gate", "", f"- Status: `{result['status']}`", "",
    "## Metrics", "", f"- `{json.dumps(result['metrics'], ensure_ascii=False)}`", "", "## Findings", "",
]
if result["findings"]:
    lines.extend(f"- `{item['severity']}` `{item['code']}`: {item['detail']}" for item in result["findings"])
else:
    lines.append("- None")
(REPORT / "section-3.5.2-human-facing-gate.md").write_text("\n".join(lines) + "\n", "utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)
