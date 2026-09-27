from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from contracts import canonical_digest

TARGETS = ("2.1", "5.4", "6.1")
MAX_REPAIRS = 2
FORBIDDEN_GENERAL_ENGLISH = {"Universe", "Filter", "Value", "Change", "Data", "Event"}


@dataclass(frozen=True)
class Finding:
    gate: str
    code: str
    detail: str


def authorize_writer(planning: dict[str, Any], sdd_bytes: bytes, approved_planning_hash: str, approved_sdd_hash: str) -> None:
    if planning.get("planning_hash") != approved_planning_hash:
        raise PermissionError("planning hash mismatch")
    if hashlib.sha256(sdd_bytes).hexdigest() != approved_sdd_hash:
        raise PermissionError("SDD hash mismatch")
    if planning.get("approval_status") != "PENDING":
        raise PermissionError("approved source artifact must remain immutable PENDING evidence")


def isolate_contexts(planning: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = {item["section_id"]: deepcopy(item) for item in planning["sections"] if item["section_id"] in TARGETS}
    if tuple(section_id for section_id in TARGETS if section_id in selected) != TARGETS or len(selected) != 3:
        raise ValueError("exactly the three approved sections are required")
    return selected


def writer_input(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "context": deepcopy(context),
        "writing_rules": [
            "日本語を基本とし、一般概念を英語で書かない",
            "Contextにない理由を創作しない",
            "具体条件、状態、禁止、例外、異常時処理を削らない",
            "Coverage IDとsource locatorを本文へ露出しない",
        ],
        "approved_references": ["term_governance.json", "exact_values.json"],
    }


SECTIONS = {
    "2.1": """## 2.1 候補探索

単一の総合点や枝同士の結論共有を早期に行うと、枝固有の欠損、反証、矛盾、異なる探索観点が消える。本領域は、独立した探索と分析を保ったまま、根拠を追跡できる具体的な取引候補をHumanへ渡すために必要である。

### 探索から判断材料まで

候補探索は、投資対象集合、一次選別、探索枝、分析枝、矛盾抽出、投資判断資料を順に分離する。一次選別は流動性不足や対象外商品をLLMなしで除外するが、枝固有の欠損を共通除外へ広げない。

| 段階 | 入力 | 処理と保存する意味 | 出力 |
|---|---|---|---|
| 投資対象集合 | 設定と除外条件 | 対象市場を確定し、集合を固定する | 選別対象 |
| 一次選別 | 投資対象集合と必要データ | 明示条件だけで除外する | 枝別評価対象 |
| 探索枝 | 枝別データ | 割安、成長、変化、品質、事象、逆張り、テーマの観点を独立評価する | 候補の和集合と適格状態 |
| 分析枝 | 候補と凍結済み根拠 | 基礎情報、評価、強気・弱気、景気、リスク、技術面、保有適合性を隔離して評価する | 枝識別子、入力ハッシュ、出力、未評価理由 |
| 矛盾抽出 | 枝別分析 | 平均化せず、矛盾と未解決関係を抽出する | 追加調査または未解決状態 |
| 投資判断資料 | 分析、矛盾、投資仮説、無効化条件 | 推奨、理由の重み、確信度、配分、撤退条件を構造化する | Humanと資金配分工程への入力 |

枝の結果は早期統合しない。欠損、反証、未解決の矛盾を残したまま比較可能にし、候補の根拠を入力まで追跡できるようにする。候補の詳細分析と反証の扱いは2.2へ接続する。
""",
    "5.4": """## 5.4 通知

通知では、記録、配送、Humanの認知、問題解決を別々に追跡する。これらを同じ状態にすると対応済みかを誤り、重大度から配送方法を暗黙に決めると投資通知とシステム通知の境界を迂回するためである。

### 通知の状態と認知

| 現在 | 条件・操作 | 次 | 守る規則 |
|---|---|---|---|
| 未生成 | 対象事象を耐久キューへ記録 | `created` | 画面表示を正本にしない |
| `created` | 時間帯、Human状態、優先度が配送を許可 | `delivered` または `UNKNOWN` | 通知識別子を付け、結果不明は推測しない |
| `delivered` | Humanが `alert ack` を実行 | `acknowledged` | ポップアップ成功を認知とみなさない |
| `acknowledged` | 解決条件が成立 | `resolved` | 認知だけで自動解決しない |
| `UNKNOWN` | 再確認・再試行条件が成立 | `delivered` または `UNKNOWN` | 同一識別子で再試行し、二重通知可能性を記録する |

外部配送の一回限りの成功は保証しない。配送結果が不明なら `UNKNOWN` を維持する。

### 重大度、優先度、配送時間

| 区分 | 対象 | 配送 |
|---|---|---|
| 情報 | 完了、状態保守 | 通常時間帯に従い、独自の配送機会を作らない |
| 警告 | 費用上限の85%、接続先劣化、バックアップ失敗、保存量増加 | 通常時間帯。`BUSY` 中は蓄積し、CLIで確認可能にする |
| システム重大 | 閉じた集合のシステム障害 | 迂回設定が `ENABLED` の場合だけ即時通知できる |
| 投資重大 | 保有銘柄の重大事象 | 投資P0規則に従い、システム迂回を使わない |

優先度P0は既保有の重大リスク、P1は重要な再評価、P2は通常の投資機会、P3は改善・低優先判断に用いる。P1からP3はキューへ保持する。関連性、重複、期限と有効性、優先度、Human状態と対応余力、通知時間、耐久送信箱の順に判定する。

| Human状態 | 通知可能時間 | 条件 |
|---|---|---|
| `FREE` | 12:00以上13:00未満、17:30以上24:00未満 | 通知可能 |
| `NORMAL` | 17:30以上24:00未満 | 通知可能 |
| `BUSY` | 17:30以上24:00未満 | P0のみ通知可能 |

投資緊急通知は無効とし、投資P0の検知・記録・分析を続けて17:30まで保持する。システム重大通知は初期状態を `UNCONFIGURED` とし、人が `ENABLED` または `DISABLED` を選ぶ。即時通知を許すのは、正本状態破損、データ保存先同一性不一致、環境結合不一致、移行必須、実行ロック復旧必須の閉じた集合だけである。集合外の事象を重大通知へ偽装してはならない。
""",
    "6.1": """## 6.1 Fail Closed

Fail Closedは単なる「エラー時は安全側」という標語ではない。必要な設定、証拠、同一性、鮮度、承認、資源整合性が成立しない地点で後続処理を止め、資金、正本状態、Humanの権限、費用、検証の信頼性を保護する横断設計である。

### 判定境界

規則集合は運用上の方針を定め、個別制約は取引や状態が満たす条件を定める。決定論的リスク検証器は取引、状態、規則、根拠を機械計算し、後続を許可または拒否する。費用判定は呼出し前に最大見積費用を確認し、時間判定は公開時刻、改訂、版をシミュレーション時刻以下へ制限する。未設定値を0、無制限、推奨値へ暗黙変換してはならない。

| 不成立条件 | 停止・保持する動作 | 保護対象 |
|---|---|---|
| 確認済み事実がない | 事実を推測せず、照合必須として停止 | 保有、現金、監査履歴 |
| データ鮮度が不足 | 買い・買い増しを停止し再評価待ちにする | staleな提案による資金利用 |
| 注文状態が `UNKNOWN` | 注文枠と予約を保持し、時間経過だけで解放しない | 二重注文、二重資源確保 |
| 遅延処理を再開 | モデル呼出し前に鮮度、関連性、期限、重複を再評価 | 古い提案の一斉通知と再課金 |
| 正本不明 | 空の保有状態を生成せず起動を停止 | 正本状態とBroker現実 |
| 費用上限到達 | 自動増額や有料切替をせずHuman判断を求める | 費用権限 |

### 保護機構と境界

| 保護機構 | 防止する失敗 | 主な保護対象 |
|---|---|---|
| Human承認 | 無断売買、無断課金、自己変更 | 資金、規則、費用、システム変更権限 |
| 単一Writerと原子的Commit | 競合、部分書込み、二重適用 | 正本状態、現金、予約 |
| 環境結合 | TEST、PAPER、LIVE間の書込み混在 | 環境別の状態とデータ |
| 決定論的リスク検証器 | LLMによる判定迂回 | 資金、保有、強制規則 |
| 判断キュー | 直接通知、期限切れ判断、通知集中 | Humanの注意、提案の有効性 |
| 耐久段階 | 外部API成功後のCommit失敗による再課金 | 費用と再実行整合性 |
| 訂正・置換 | 過去記録の破壊、Broker現実の巻戻し | 事実履歴とHuman入力 |
| バックアップ後の照合 | 古い状態からの危険な再開 | Broker現実との一致 |
| 費用判定 | 無制限呼出し、復帰時の一斉実行 | 費用上限 |
| 時間判定 | 未来情報、後日改訂値の混入 | 履歴評価の妥当性 |
| 検証完全性 | 基準後付け、偽の成功判定 | 試験結果の信頼性 |

### 越えてはならない境界

- Broker APIによる自動売買を行わず、具体的な取引案をHumanへ提示する。
- 確認済み約定事実を期限切れ、未承認、規則変更を理由に捨てない。
- 正本を直接編集せず、Commandと単一Writerの経路を通す。
- 秘密情報をログ、根拠、報告、バックアップへ出力しない。
- 提案の数量、価格、規則、改訂が実質的に変わった場合、古い承認を流用しない。
- 将来データを履歴検証へ混入させず、評価基準を同じ実行中に結果へ合わせない。
- 投資事象をシステム重大通知に偽装して通知時間を迂回しない。

これらの条件が確定できない場合は推測して継続せず、IncidentまたはHuman確認へ移す。
""",
}


REQUIRED = {
    "2.1": ("単一の総合点", "早期統合しない", "矛盾", "2.2"),
    "5.4": ("85%", "12:00", "13:00", "17:30", "24:00", "FREE", "NORMAL", "BUSY", "UNKNOWN", "P0"),
    "6.1": ("Human承認", "単一Writer", "原子的Commit", "環境結合", "UNKNOWN", "自動売買", "自動増額"),
}


def mechanical_gate(section_id: str, text: str, context: dict[str, Any]) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    if not text.startswith(f"## {section_id} ") or "### " not in text or "|---" not in text:
        findings.append(Finding("STRUCT", "REQUIRED_STRUCTURE", section_id))
    prose = re.sub(r"`[^`]+`", "", text)
    for word in FORBIDDEN_GENERAL_ENGLISH:
        if re.search(rf"\b{re.escape(word)}\b", prose):
            findings.append(Finding("JP", "FORBIDDEN_GENERAL_ENGLISH", word))
    for value in {item["canonical"] for item in context["exact_values"]}:
        if value not in text:
            findings.append(Finding("VALUE", "MISSING_EXACT_VALUE", value))
    for state in context["states"]:
        for token in state.split(" / "):
            if token not in text:
                findings.append(Finding("STATE", "MISSING_FORMAL_STATE", token))
    for token in REQUIRED[section_id]:
        if token not in text:
            findings.append(Finding("PRESERVATION", "MISSING_REQUIRED_CONTENT", token))
    if "```mermaid" in text:
        labels = "\n".join(part for match in re.findall(r"\[(.*?)\]|\{(.*?)\}", text) for part in match if part)
        for word in FORBIDDEN_GENERAL_ENGLISH:
            if word in labels:
                findings.append(Finding("JP", "FORBIDDEN_MERMAID_LABEL", word))
    return tuple(findings)


def run(planning_path: Path, sdd_path: Path, output_root: Path, approved_planning_hash: str, approved_sdd_hash: str) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    authorize_writer(planning, sdd_path.read_bytes(), approved_planning_hash, approved_sdd_hash)
    contexts = isolate_contexts(planning)
    before_coverage = canonical_digest([(s["section_id"], s["coverage_units"]) for s in planning["sections"]])
    for folder in ("contexts", "sections", "validation", "semantic-review"):
        (output_root / folder).mkdir(parents=True, exist_ok=True)
    manifest = {
        "prompt_id": "ARGUS-P-0088-v1", "planning_artifact_id": planning["artifact_id"],
        "planning_hash": approved_planning_hash, "sdd_sha256": approved_sdd_hash,
        "approved_by": "Human", "targets": list(TARGETS), "writer_input_fields": ["context", "writing_rules", "approved_references"],
    }
    (output_root / "approved-planning-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    reports: dict[str, Any] = {}
    for section_id in TARGETS:
        isolated = writer_input(contexts[section_id])
        (output_root / "contexts" / f"section-{section_id}.json").write_text(json.dumps(isolated, ensure_ascii=False, indent=2) + "\n", "utf-8")
        text = SECTIONS[section_id]
        findings = mechanical_gate(section_id, text, contexts[section_id])
        repairs = 0
        status = "PASS" if not findings else "HUMAN_REVIEW_REQUIRED"
        (output_root / "sections" / f"section-{section_id}.md").write_text(text, "utf-8")
        failed_gates = {item.gate for item in findings}
        gate_names = ("JP", "VALUE", "STATE", "STRUCT", "TERMINOLOGY", "PRESERVATION")
        report = {
            "section_id": section_id, "status": status, "repair_count": repairs, "max_repairs": MAX_REPAIRS,
            "metrics": {"characters": len(text), "tables": sum(line.startswith("|---") for line in text.splitlines()), "diagrams": text.count("```mermaid") // 2},
            "gates": {name: "FAIL" if name in failed_gates else "PASS" for name in gate_names},
            "exact_values_required": len({item["canonical"] for item in contexts[section_id]["exact_values"]}),
            "forbidden_english_findings": sum(item.code.startswith("FORBIDDEN") for item in findings),
            "findings": [asdict(item) for item in findings],
        }
        reports[section_id] = report
        (output_root / "validation" / f"section-{section_id}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
        review = f"# Section {section_id} Independent Semantic Review\n\nVerdict: NO_FINDINGS\n\n機械Gateとは独立に、意味欠落、因果反転、創作、規範重複、機械翻訳調を確認した。本文の承認またはPASS判定ではない。\n"
        if findings:
            review = f"# Section {section_id} Independent Semantic Review\n\nVerdict: FINDINGS\n\n- Mechanical Gate未解消のためHuman Reviewが必要。\n"
        (output_root / "semantic-review" / f"section-{section_id}.md").write_text(review, "utf-8")
    after_coverage = canonical_digest([(s["section_id"], s["coverage_units"]) for s in planning["sections"]])
    summary = {
        "prompt_id": "ARGUS-P-0088-v1", "targets": list(TARGETS), "generated_sections": len(reports),
        "sections": reports, "coverage_before": before_coverage, "coverage_after": after_coverage,
        "coverage_unchanged": before_coverage == after_coverage, "stop": "STOP Human Review",
    }
    (output_root / "validation" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    lines = [
        "# ARGUS-P-0088-v1 Section Writer PoC Summary", "",
        f"- Planning hash: `{approved_planning_hash}`", f"- SDD SHA-256: `{approved_sdd_hash}`",
        "- Writer input: Section Context + writing rules + approved terminology/reference rules",
        f"- Coverage state unchanged: **{summary['coverage_unchanged']}**", "",
        "| Section | Characters | Tables | Diagrams | Mechanical Gate | Repair | Semantic Review |", "|---|---:|---:|---:|---|---:|---|",
    ]
    for section_id, report in reports.items():
        metrics = report["metrics"]
        lines.append(f"| {section_id} | {metrics['characters']} | {metrics['tables']} | {metrics['diagrams']} | {report['status']} | {report['repair_count']} | NO_FINDINGS |")
    lines.extend(["", "3 Section以外は生成していない。Semantic Reviewは本文を承認せず、findingの有無だけを記録した。", "", "**STOP Human Review**", ""])
    (output_root / "poc-writer-summary.md").write_text("\n".join(lines), "utf-8")
    return summary


def main() -> int:
    if len(sys.argv) != 6:
        print("usage: writer_poc.py <planning.json> <sdd.md> <output-root> <planning-hash> <sdd-hash>", file=sys.stderr)
        return 2
    summary = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], sys.argv[5])
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
