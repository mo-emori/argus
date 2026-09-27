from __future__ import annotations

import json
from pathlib import Path

from translation_semantic_review import make_review_input

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0103-v1"
SOURCE_REPORT = ROOT / "validation/reports/argus-p-0101-v1"

english = (SOURCE_REPORT / "section-3.5.2-en.md").read_text(encoding="utf-8")
japanese = (REPORT / "section-3.5.2-ja.md").read_text(encoding="utf-8")
contract = json.loads((REPORT / "section-3.5.2-translation-contract.json").read_text(encoding="utf-8"))
gate = json.loads((REPORT / "section-3.5.2-preservation-result.json").read_text(encoding="utf-8"))
gate["independent_semantic_review_required"] = True
gate["post_gate_semantic_trigger"] = {
    "status": "REVIEW",
    "code": "TECHNICAL_FIRST_USE_EXPLANATION_MEANING_VALIDITY",
    "detail": "Confirm that Japanese first-use explanations do not narrow or add meaning, especially Adapter.",
}
packet = make_review_input(english, japanese, contract, gate)
(REPORT / "section-3.5.2-semantic-review-input.json").write_text(
    json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("semantic review input: PASS")
