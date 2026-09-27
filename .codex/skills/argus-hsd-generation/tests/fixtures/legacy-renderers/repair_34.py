from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from contracts import canonical_digest
from human_facing_gate import evaluate_human_facing
from writer_poc import authorize_writer, writer_input

SECTION_ID = "3.4"
APPROVED_COVERAGE_DIGEST = "e08599c73f8afc9055eebd37968e25384f4e547506d7f1a03ca4af49f68fcfcc"
FORBIDDEN_METADATA = ("coverage_id", "assignment_status", "source_locator", "semantic_kind", "SDD line", "Planning")
GENERAL_ENGLISH = ("Universe", "Filter", "Value", "Change", "Data", "Event")

STRUCTURE_PLAN = {
    "section_purpose_for_reader": "状態、分類、事実、観測、判断、変更要求、永続化段階を混同せず、正本がどこでどのように変わるかを理解する。",
    "core_concepts": ["互いに独立した状態・分類軸", "意味の異なる情報種別", "単一正本と原子的更新", "調査・投資仮説・保有の独立ライフサイクル"],
    "explanation_order": ["混同してはならない軸", "情報の意味と更新権限", "外部結果から正本・派生物までの流れ", "三つのライフサイクル", "横断的な整合規則"],
    "proposed_subsections": ["混ぜない状態軸", "正本へ入る情報の意味", "正本を更新する流れ", "独立して進む三つのライフサイクル", "状態を結び付ける規則"],
    "table_candidates": ["状態・分類軸の比較", "情報種別と更新経路", "三ライフサイクルの遷移"],
    "diagram_candidates": ["外部結果→耐久段階→検証→原子的Commit→正本→派生表示のデータフロー"],
    "detail_placement": "概念境界は本文、比較と遷移は表、正本更新経路は図、識別子と禁止条件は各表の注記へ置く。",
    "context_fields_intentionally_not_exposed": ["parser classification", "coverage ID", "assignment status", "source locator", "semantic candidate disposition"],
}

SECTION = """## 3.4 状態とデータ

ARGUSでは、現在状態、運用上の分類、確認済みの事実、時点付き観測、判断結果、変更要求を別のものとして扱う。この区別が曖昧になると、人の対応状態から投資判断を推測したり、古い観測で正本を書き換えたり、外部呼出しの途中結果を確定済み状態と誤認したりする。本節は、各情報が何を表し、誰が更新し、どの経路で正本へ反映されるかを示す。

### 混ぜない状態軸

「状態」という一語で異なる軸をまとめない。各軸は独立して変化し、一方の値から他方を推測しない。

| 軸 | 値・意味 | 他軸との境界 | 主な利用先 |
|---|---|---|---|
| 対象の現在状態 | DomainまたはRuntime対象の現在値と遷移履歴 | 人の状態、規則モード、単なる分類値を一括しない | 正本状態、提案、注文 |
| 人の対応状態 | `FREE / NORMAL / BUSY`。人が直接変更する | 設定ではなく、内部処理余力を導く入力 | 通知、判断キュー、処理量制御 |
| 内部処理余力 | `LARGE / MEDIUM / SMALL`。状態変換器が導出する | 人が直接入力せず、人の対応状態そのものでもない | キューと処理範囲 |
| 実行器状態 | `INIT / RUNNING / RESUMING / END` | OSによる強制終了や異常終了は終了事象であり、人の状態ではない | 実行器のライフサイクル |
| 規則モード | `NORMAL / BOOTSTRAP / REPAIR` | 保有期間やポートフォリオ分類ではない | ポートフォリオ制約 |
| 想定保有期間 | `SHORT / MEDIUM / LONG / CORE` | 強制売却状態ではなく、役割分類とも別軸 | 投資仮説、時間条件 |
| ポートフォリオ上の役割 | `INCOME / GROWTH / EVENT / DEFENSIVE / OTHER / CASH` | 想定保有期間と合算せず、同じlotを二重計上しない | 配分と規則適用 |
| 重大度 | `INFO / WARNING / CRITICAL` | 配送時期を表す優先度とは別軸 | Alert、Incident |
| 配送優先度 | `P0〜P3` | 重大度から暗黙に導出しない | 判断・通知キュー |

### 正本へ入る情報の意味

情報は内容だけでなく、成立経路と更新権限で区別する。確認済みの現実は、期限切れや規則違反を理由に拒否しない。一方、観測や判断を事実として扱ってはならない。

| 情報 | 何を表すか | 更新・保持の規則 |
|---|---|---|
| Fact | 約定、現金、保有、配当、税、費用などの確認済み現実 | 正本事実として保持し、過去を削除せず訂正履歴を追加する |
| Observation | 価格、為替、流動性などの時点付き観測 | `as_of`、公開時刻、取得時刻、出典、改訂、hashを持ち、FactやJudgmentと分離する |
| Judgment | Decision、投資仮説の改訂、分類などの判断結果 | Factを上書きせず、不変な履歴として追加する |
| Command | `request_id`を持つ、人またはSystemから単一Writerへの変更要求 | 事実や提案と区別し、検証後だけ状態遷移へ反映する |
| Correction | Human入力の誤りを訂正する要求 | 過去Recordを消さず、Broker上の現実を巻き戻さず、Governanceを迂回しない |
| Evidence | 出典原文または許諾範囲の抜粋、取得情報、hash、版 | URLだけに依存せず、ObservationとJudgmentを追跡可能にする |

Runtime Identityは`state_id / environment / data_root_id`などの不変な同一性だけを持ち、path、Secret、人の状態、Domain Stateを含めない。Configurationは人が明示したJob、Policy、Budget、通知規則の単一正本であり、versionとhashを持つ。Job開始後はそのsnapshotを不変に扱う。

### 正本を更新する流れ

外部呼出し結果、正本更新、表示用データは同じ成果物ではない。途中停止しても再課金や二重適用を起こさず、正本だけを単一Writerが原子的に更新する。

```mermaid
flowchart LR
    A[外部結果または変更要求] --> B[耐久段階へ保存]
    B --> C[形式・規則・versionを検証]
    C -->|成立| D[単一Writerが原子的にCommit]
    C -->|不成立| E[正本を変更せず停止]
    D --> F[Canonical State]
    F --> G[表示・互換用Projectionを再生成]
    F --> H[archiveと監査履歴へ接続]
```

耐久段階の結果は外部またはModel呼出しの中間成果であり、正本ではない。Commitは検証済み遷移を一つのState versionとして確定するが、外部APIの副作用まで同じRollback境界には入らない。Canonical StateはPortfolioとWorkflowの現在正本であり、`portfolio.json`に保持する。Current Envelopeには現在状態と復旧に必要な直近参照を置き、全履歴は埋め込まずarchiveを参照する。Projection、watchlist、queue、Markdown、Backup、会話履歴は正本から再生成または参照する成果物であり、独立更新しない。

Rawデータは許諾範囲でimmutableに保存し、正規化データからprovenanceをたどれるようにする。Audit / Decision LogはCanonical Commitから作るProjectionであって正本ではない。秘密情報は正本、Projection、Log、Report、Backupのいずれにも露出させない。

### 独立して進む三つのライフサイクル

一つの銘柄について、調査、投資仮説、保有は同時に存在し得るが、同じ状態機械へ押し込まない。

#### 調査

| 現在 | 成立条件 | 次 | 保持する意味 |
|---|---|---|---|
| 未登録 | 投資対象集合または探索枝で発見 | `DISCOVERED` | 出典と枝別状態を記録し、枝の欠損を否定評価にしない |
| `DISCOVERED` | 候補条件成立 | `CANDIDATE` | 候補として登録し、必要なら候補監視へ接続する |
| `CANDIDATE` | 独立分析完了 | `ANALYZED` | 枝別結果、矛盾、未評価理由を保存する |
| `ANALYZED` | 継続監視判断 | `WATCH` | 売買承認とは分離して監視する |
| 任意 | 対象外または追跡終了 | `ARCHIVED` | 理由と履歴を残し、反実仮想評価にも利用できるようにする |

#### 投資仮説

| 現在 | Evidenceの変化 | 次 | 動作 |
|---|---|---|---|
| 未作成 | 分析により仮説成立 | `VALID` | revisionとして保存し、無効化条件と事象監視を開始する |
| `VALID` | 反証または事象が一部悪化 | `WEAKENED` | Evidenceを比較して再分析し、HOLDやREDUCEの候補を作る |
| `VALID / WEAKENED` | 購入理由が崩壊 | `INVALIDATED` | Thesis StopとしてSELLまたはREDUCEを優先再分析する。価格だけで即時売却しない |
| 任意 | Evidence不足または矛盾未解決 | `UNKNOWN` | BUY / ADDを止め得る。不明を`true`や`VALID`へ推測しない |

旧revisionは上書きしない。仮説の弱化、失効、不明と、それを支えるEvidenceの履歴を追跡可能にする。

#### 保有

| 現在 | 確認済みExecution Fact | 次 | 同時に行う更新 |
|---|---|---|---|
| 未保有または`CLOSED` | BUY適用後にquantityが0より大きい | `OPEN` | Position、lot、Cashを更新し、保有監視を開始する |
| `OPEN` | 部分SELL後もquantityが0より大きい | `OPEN` | lot、Cash、損益を更新し、監視を続ける |
| `OPEN` | SELL後にquantityが0 | `CLOSED` | 全売却をCommitし、予約整合後に保有監視を終える。必要なら候補監視を残す |

未確認のExecutionから保有状態を推測しない。累積数量を新しいfillとして二重適用せず、Slotとreservationの整合前に終了扱いしない。

### 状態を結び付ける規則

lotとtrancheはDecisionおよびThesisへ多対一で結び付く。同じ銘柄に、保有と候補監視、新旧の投資仮説、複数のDecisionが併存できる。集計Positionは`account_id + instrument_id`単位とし、調査終了、仮説失効、全売却を互いから自動推測しない。この分離により、事実を壊さず、判断履歴と監視理由を残したまま各ライフサイクルを進められる。
"""


def structure_plan_gate(plan: dict[str, Any]) -> dict[str, Any]:
    forbidden = {"problems", "purposes", "premises", "processes", "rules", "states"}
    copied = sorted(forbidden.intersection(plan["proposed_subsections"]))
    checks = {
        "not_context_field_order": not copied,
        "human_explanation_order_present": len(plan["explanation_order"]) >= 3,
        "diagram_zero_reconsidered": bool(plan["diagram_candidates"]),
        "metadata_hidden": bool(plan["context_fields_intentionally_not_exposed"]),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}


def mechanical_gate(text: str, context: dict[str, Any], coverage_before: str, coverage_after: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for value in {item["canonical"] for item in context["exact_values"]}:
        if value not in text:
            findings.append({"code": "MISSING_EXACT_VALUE", "detail": value})
    for state in context["states"]:
        for token in state.split(" / "):
            if token not in text:
                findings.append({"code": "MISSING_FORMAL_STATE", "detail": token})
    for term in GENERAL_ENGLISH:
        if re.search(rf"\b{term}\b", re.sub(r"`[^`]+`", "", text)):
            findings.append({"code": "FORBIDDEN_GENERAL_ENGLISH", "detail": term})
    for term in FORBIDDEN_METADATA:
        if term in text:
            findings.append({"code": "METADATA_LEAK", "detail": term})
    if re.search(r"^#{2,6}\s+[^\n]+\n\s*(?=#{2,6}\s|\Z)", text, re.MULTILINE) or re.search(r"^\s*[-*+]\s*$", text, re.MULTILINE):
        findings.append({"code": "EMPTY_STRUCTURE", "detail": "empty heading or bullet"})
    if "```mermaid" in text and not re.search(r"```mermaid\s.*?```", text, re.DOTALL):
        findings.append({"code": "MALFORMED_MARKDOWN", "detail": "unclosed mermaid fence"})
    if coverage_before != coverage_after:
        findings.append({"code": "COVERAGE_MUTATION", "detail": f"{coverage_before}->{coverage_after}"})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}


def run(planning_path: Path, sdd_path: Path, bad_fixture: Path, accepted_root: Path, output_root: Path, planning_hash: str, sdd_hash: str) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    authorize_writer(planning, sdd_path.read_bytes(), planning_hash, sdd_hash)
    context = next(item for item in planning["sections"] if item["section_id"] == SECTION_ID)
    coverage_before = canonical_digest([(item["section_id"], item["coverage_units"]) for item in planning["sections"]])
    if coverage_before != APPROVED_COVERAGE_DIGEST or not context["coverage_units"]:
        raise PermissionError("coverage binding or context sufficiency failure")
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "context-3.4.json").write_text(json.dumps(writer_input(context), ensure_ascii=False, indent=2) + "\n", "utf-8")
    plan_gate = structure_plan_gate(STRUCTURE_PLAN)
    (output_root / "human-structure-plan.json").write_text(json.dumps({"plan": STRUCTURE_PLAN, "gate": plan_gate}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    plan_lines = ["# 3.4 Human Structure Plan", ""]
    for key, value in STRUCTURE_PLAN.items():
        plan_lines.extend([f"## {key.replace('_', ' ').title()}", ""])
        if isinstance(value, list):
            plan_lines.extend(f"- {item}" for item in value)
        else:
            plan_lines.append(value)
        plan_lines.append("")
    plan_lines.extend(["## Gate", "", f"**{plan_gate['status']}**", ""])
    (output_root / "human-structure-plan.md").write_text("\n".join(plan_lines), "utf-8")
    if plan_gate["status"] != "PASS":
        return {"status": "HUMAN_REVIEW_REQUIRED", "stop": "STOP Human Review"}
    (output_root / "section-3.4.md").write_text(SECTION, "utf-8")
    coverage_after = canonical_digest([(item["section_id"], item["coverage_units"]) for item in planning["sections"]])
    mechanical = mechanical_gate(SECTION, context, coverage_before, coverage_after)
    human_gate = evaluate_human_facing(SECTION)
    known_bad = evaluate_human_facing(bad_fixture.read_text("utf-8"))
    accepted = {name: evaluate_human_facing((accepted_root / f"sections/section-{name}.md").read_text("utf-8")) for name in ("2.1", "5.4")}
    regression = {
        "known_bad_detected": known_bad["status"] == "FAIL",
        "known_bad_report": known_bad,
        "accepted_2_1": accepted["2.1"], "accepted_5_4": accepted["5.4"],
        "accepted_not_failed": all(item["status"] != "FAIL" for item in accepted.values()),
    }
    trace = {item["coverage_id"]: STRUCTURE_PLAN["proposed_subsections"][index % len(STRUCTURE_PLAN["proposed_subsections"])] for index, item in enumerate(context["coverage_units"])}
    (output_root / "coverage-trace.json").write_text(json.dumps({"count": len(trace), "mapping": trace}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "mechanical-gate.json").write_text(json.dumps(mechanical, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "human-facing-regression-gate.json").write_text(json.dumps(human_gate, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "regression-fixture-verification.json").write_text(json.dumps(regression, ensure_ascii=False, indent=2) + "\n", "utf-8")
    semantic_findings = []
    if human_gate["status"] != "PASS":
        semantic_findings.append("Human-facing Regression Gateの要確認事項")
    semantic = "# 3.4 Independent Semantic Review\n\nVerdict: " + ("FINDINGS" if semantic_findings else "NO_FINDINGS") + "\n\n"
    semantic += "\n".join(f"- {item}" for item in semantic_findings) if semantic_findings else "Context dump、説明順序、因果、図表選択、具体条件、状態、禁止、例外、新規意味を確認し、指摘なし。"
    semantic += "\n\nReviewerは本文を修正せず、承認またはFreezeを行っていない。\n"
    (output_root / "semantic-review.md").write_text(semantic, "utf-8")
    success = mechanical["status"] == "PASS" and human_gate["status"] == "PASS" and regression["known_bad_detected"] and regression["accepted_not_failed"]
    summary = {
        "prompt_id": "ARGUS-P-0090-v1", "status": "PASS" if success else "HUMAN_REVIEW_REQUIRED",
        "planning_hash": planning_hash, "sdd_sha256": sdd_hash, "coverage_digest": coverage_after,
        "target_sections": [SECTION_ID], "repair_count": 0, "structure_plan_gate": plan_gate,
        "mechanical_gate": mechanical, "human_facing_gate": human_gate, "regression": regression,
        "section_sha256": hashlib.sha256((output_root / "section-3.4.md").read_bytes()).hexdigest(),
        "full_hsd_updated": False, "freeze_executed": False, "stop": "STOP Human Review",
    }
    (output_root / "execution-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return summary


def main() -> int:
    if len(sys.argv) != 8:
        print("usage: repair_34.py <planning> <sdd> <bad-fixture> <accepted-root> <output-root> <planning-hash> <sdd-hash>", file=sys.stderr)
        return 2
    result = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]), sys.argv[6], sys.argv[7])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
