from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CompositionFinding:
    severity: str
    code: str
    detail: str


_CONTEXT_HEADINGS = {"課題と成立条件", "前提", "設計内容", "状態と識別子", "規則", "異常時処理"}
_LABEL = re.compile(r"^\s*-\s*(?:課題|目的|前提|規則|禁止|例外|異常時処理)\s*:", re.MULTILINE)
_EMPTY_HEADING = re.compile(r"^#{2,6}\s+[^\n]+\n\s*(?=#{2,6}\s|\Z)", re.MULTILINE)
_EMPTY_BULLET = re.compile(r"^\s*[-*+]\s*$", re.MULTILINE)
_CONTEXT_FIELDS = {
    "premises", "problems", "purposes", "design_reasons", "processes", "rules",
    "prohibitions", "exceptions", "abnormal_handling", "actors_authorities",
    "boundaries", "relations", "states", "exact_values",
}
_WRITER_META = (
    "本節では、個々の条件を列挙するのではなく",
    "context field order",
    "Human Structure Plan before writing",
)
_WRITER_META_PATTERNS = (
    re.compile(r"(?:writer|generation|context).{0,30}(?:instruction|procedure|field|array|processing)", re.IGNORECASE),
    re.compile(r"(?:生成手順|執筆指示|入力コンテキスト|コンテキスト(?:配列|フィールド|処理))"),
)
_GENERIC_MERMAID = (
    "A[入力を受け取る] --> B[条件を検証する]",
    "C -->|はい| D[結果を確定する]",
    "C -->|いいえ| E[安全に停止する]",
)


def evaluate_human_facing(
    text: str,
    protected_identifiers: set[str] | None = None,
    *,
    enforce_japanese: bool = False,
    technical_concepts: set[str] | None = None,
) -> dict[str, object]:
    findings: list[CompositionFinding] = []
    headings = re.findall(r"^#{2,6}\s+(.+)$", text, re.MULTILINE)
    leaked = [heading for heading in headings if heading in _CONTEXT_HEADINGS]
    if len(leaked) >= 2:
        findings.append(CompositionFinding("FAIL", "CONTEXT_FIELD_HEADINGS", ", ".join(leaked)))
    label_count = len(_LABEL.findall(text))
    if label_count >= 4:
        findings.append(CompositionFinding("FAIL", "LABEL_VALUE_DUMP", str(label_count)))
    if _EMPTY_HEADING.search(text) or _EMPTY_BULLET.search(text):
        findings.append(CompositionFinding("FAIL", "EMPTY_STRUCTURE", "empty heading or bullet"))
    bullets = len(re.findall(r"^\s*-\s+", text, re.MULTILINE))
    tables = len(re.findall(r"^\|(?:\s*:?-+:?\s*\|)+$", text, re.MULTILINE))
    diagrams = text.count("```mermaid")
    if len(text) > 3000 and bullets >= 20 and tables + diagrams == 0:
        findings.append(CompositionFinding("FAIL", "SINGLE_LEVEL_BULLET_CATALOG", f"bullets={bullets}"))
    if bullets >= 30 and tables + diagrams < 2:
        findings.append(CompositionFinding("REVIEW_REQUIRED", "TEMPLATE_DUMP_SUSPECTED", f"bullets={bullets}, visual={tables + diagrams}"))
    if len(headings) <= 2 and len(text) > 5000:
        findings.append(CompositionFinding("REVIEW_REQUIRED", "INSUFFICIENT_EXPLANATION_STRUCTURE", str(len(headings))))
    exposed = sorted(
        field for field in _CONTEXT_FIELDS
        if re.search(rf"(?:^#{2,6}\s+{re.escape(field)}\s*$|^\|\s*{re.escape(field)}\s*\|)", text, re.MULTILINE)
    )
    if exposed:
        findings.append(CompositionFinding("FAIL", "CONTEXT_FIELD_EXPOSURE", ", ".join(exposed)))
    meta = [phrase for phrase in _WRITER_META if phrase.casefold() in text.casefold()]
    generic_meta = [pattern.pattern for pattern in _WRITER_META_PATTERNS if pattern.search(text)]
    if meta or generic_meta:
        findings.append(CompositionFinding("FAIL", "WRITER_META_PROSE", ", ".join(meta + generic_meta)))
    if sum(pattern in text for pattern in _GENERIC_MERMAID) >= 2:
        findings.append(CompositionFinding("FAIL", "FIXED_GENERIC_MERMAID", "generic input/check/result/stop flow"))
    visible = re.sub(r"`[^`]+`", "", text)
    for identifier in sorted(protected_identifiers or set(), key=len, reverse=True):
        visible = visible.replace(identifier, "")
    unexplained: list[str] = []
    explained: list[str] = []
    protected = protected_identifiers or set()
    for concept in sorted((technical_concepts or set()) - protected):
        match = re.search(rf"(?<![A-Za-z0-9_]){re.escape(concept)}(?![A-Za-z0-9_])", visible)
        if not match:
            continue
        prefix = visible[max(0, match.start() - 80):match.start()]
        has_first_use_explanation = bool(re.search(r"[一-龯ぁ-んァ-ヶ][^。\n]{0,60}[（(]\s*$", prefix))
        if has_first_use_explanation:
            explained.append(concept)
        else:
            unexplained.append(concept)
    english_scan = visible
    for concept in explained:
        english_scan = re.sub(
            rf"(?<![A-Za-z0-9_]){re.escape(concept)}(?![A-Za-z0-9_])",
            "",
            english_scan,
        )
    english_runs = re.findall(r"\b[A-Za-z][A-Za-z0-9_-]*(?:\s*(?:の|を|が|に|へ|と|で|や|・|/|,)?\s*[A-Za-z][A-Za-z0-9_-]*){3,}", english_scan)
    if enforce_japanese and english_runs:
        findings.append(CompositionFinding("FAIL", "UNNECESSARY_ENGLISH_TECHNICAL_RUN", english_runs[0][:120]))
    if enforce_japanese and len(unexplained) >= 2:
        findings.append(CompositionFinding(
            "FAIL",
            "UNEXPLAINED_TECHNICAL_CONCEPT_SEQUENCE",
            ", ".join(unexplained),
        ))
    return {
        "status": "FAIL" if any(item.severity == "FAIL" for item in findings) else "REVIEW_REQUIRED" if findings else "PASS",
        "metrics": {"characters": len(text), "subsections": len(headings), "bullets": bullets, "tables": tables, "diagrams": diagrams},
        "findings": [asdict(item) for item in findings],
    }


def evaluate_corpus(texts: list[str]) -> dict[str, object]:
    """Detect template provenance without requiring gratuitous section differences."""
    signatures: dict[tuple[str, ...], int] = {}
    for text in texts:
        signature = tuple(re.findall(r"^###\s+(.+)$", text, re.MULTILINE))
        signatures[signature] = signatures.get(signature, 0) + 1
    largest = max(signatures.values(), default=0)
    mermaid_signatures: dict[str, int] = {}
    for text in texts:
        for block in re.findall(r"```mermaid\s*(.*?)```", text, re.DOTALL):
            normalized = re.sub(r"\s+", " ", block).strip()
            mermaid_signatures[normalized] = mermaid_signatures.get(normalized, 0) + 1
    largest_mermaid = max(mermaid_signatures.values(), default=0)
    suspicious = len(texts) >= 10 and largest >= max(8, int(len(texts) * 0.8))
    generic_flow_convergence = len(texts) >= 5 and largest_mermaid >= max(4, int(len(texts) * 0.6))
    findings = []
    if suspicious:
        findings.append({"code": "MASS_TEMPLATE_CONVERGENCE", "detail": f"largest_signature={largest}/{len(texts)}"})
    if generic_flow_convergence:
        findings.append({"code": "GENERIC_MERMAID_CONVERGENCE", "detail": f"largest_mermaid={largest_mermaid}/{len(texts)}"})
    return {
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
    }
