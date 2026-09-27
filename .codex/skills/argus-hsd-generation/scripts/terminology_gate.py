from __future__ import annotations

import re

GENERAL_ENGLISH = {
    "Data", "Event", "Universe", "Value", "Change", "Filter", "Status", "State",
    "Rule", "Purpose", "Problem", "Process", "Overview", "Summary",
}


def validate_terminology(content: str, formal_identifiers: set[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for identifier in sorted(formal_identifiers):
        if identifier not in content:
            findings.append({"code": "FORMAL_IDENTIFIER_MISSING_OR_TRANSLATED", "detail": identifier})
    visible = re.sub(r"`[^`]+`", "", content)
    for word in sorted(GENERAL_ENGLISH):
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(word)}(?![A-Za-z0-9_])", visible):
            findings.append({"code": "UNNECESSARY_GENERAL_ENGLISH", "detail": word})
    return findings
