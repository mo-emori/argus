from __future__ import annotations

import json
from pathlib import Path

from translation_semantic_review import (
    TranslationSemanticFinding,
    TranslationSemanticReview,
    route_translation_review,
)

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0105-v1"

review_data = json.loads((REPORT / "section-3.5.2-semantic-review.json").read_text(encoding="utf-8"))
review_data["findings"] = tuple(TranslationSemanticFinding(**item) for item in review_data["findings"])
review = TranslationSemanticReview(**review_data)
preservation = json.loads((REPORT / "section-3.5.2-preservation-result.json").read_text(encoding="utf-8"))
provenance = json.loads((REPORT / "section-3.5.2-translation-provenance.json").read_text(encoding="utf-8"))
result = route_translation_review(
    preservation,
    review,
    section_id="3.5.2",
    english_draft_digest=provenance["source_draft_digest"],
    japanese_draft_digest=review.japanese_draft_digest,
    translation_contract_digest=provenance["translation_contract_digest"],
    translation_contract_version=provenance["translation_contract_version"],
    writer_session_id=provenance["writer_session_id"],
    translator_session_id=provenance["translator_session_id"],
)
(REPORT / "section-3.5.2-semantic-review-routing.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["decision"] == "NEXT_GATE" else 1)
