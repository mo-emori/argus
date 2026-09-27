from __future__ import annotations

import json
from pathlib import Path

from section_writer_pipeline import SectionWriterOutputArtifact, validate_output

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "validation/reports/argus-p-0101-v1"
provenance = json.loads((REPORT / "section-3.5.2-writer-provenance.json").read_text("utf-8"))
artifact = SectionWriterOutputArtifact(**json.loads((REPORT / "section-3.5.2-writer-output.json").read_text("utf-8")))
expected = {
    "writer_session_id": provenance["writer_session_id"], "section_id": provenance["section_id"],
    "chapter_contract_digest": provenance["chapter_contract_digest"],
    "human_structure_plan_digest": provenance["human_structure_plan_digest"],
    "coverage_contract_digest": provenance["coverage_contract_digest"],
    "writer_input_digest": provenance["writer_input_digest"], "provenance_version": provenance["expected_provenance_version"],
}
content = validate_output(artifact, expected)
if content != (REPORT / "section-3.5.2-en.md").read_text("utf-8"):
    raise ValueError("WRITER_CONTENT_MISMATCH")
print(json.dumps({"provenance": "PASS", "content_binding": "PASS"}, indent=2))
