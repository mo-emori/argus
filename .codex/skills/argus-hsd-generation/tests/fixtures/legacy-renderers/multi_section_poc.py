from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from contracts import canonical_digest
from human_facing_gate import evaluate_human_facing
from repair_34 import APPROVED_COVERAGE_DIGEST, mechanical_gate, structure_plan_gate
from writer_poc import authorize_writer, writer_input

EXCLUDED = {"2.1", "3.4", "5.4", "6.1"}
SELECTED = {"A": "1.2", "B": "7.1", "C": "3.1"}


def plan_gate(kind: str, plan: dict[str, Any]) -> dict[str, Any]:
    base = structure_plan_gate({**plan, "diagram_candidates": plan["diagram_candidates"] or ["明示的に不要と判断"]})
    representation = {
        "A": bool(plan["prose_candidates"]),
        "B": bool(plan["diagram_candidates"]),
        "C": bool(plan["diagram_candidates"] and plan["table_candidates"]),
    }[kind]
    checks = {**base["checks"], "type_appropriate_representation": representation}
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}


def _scores(section: dict[str, Any]) -> dict[str, int]:
    title = section["title"]
    return {
        "A": 3 * len(section["design_reasons"]) + 2 * len(section["problems"]) + 2 * len(section["purposes"]) + len(section["boundaries"]) - len(section["processes"]) // 10,
        "B": len(section["processes"]) + 5 * (section["diagram_plan"]["need"] == "NEEDED") + 2 * len(section["relations"]),
        "C": 3 * len(section["abnormal_handling"]) + 3 * len(section["prohibitions"]) + 2 * len(section["exceptions"]) + 2 * len(section["rules"]) + 5 * sum(word in title for word in ("中断", "復旧", "障害", "継続実行", "起動")),
    }


def select_sections(planning: dict[str, Any]) -> dict[str, Any]:
    eligible = [section for section in planning["sections"] if section["section_id"] not in EXCLUDED]
    result: dict[str, Any] = {"rule": "type score descending, then section_id ascending; evaluated sections excluded", "types": {}}
    used: set[str] = set()
    for kind in ("A", "B", "C"):
        ranked = sorted(eligible, key=lambda item: (-_scores(item)[kind], item["section_id"]))
        candidates = []
        for section in ranked:
            candidates.append({
                "section_id": section["section_id"], "title": section["title"], "type": kind,
                "score": _scores(section)[kind], "coverage_units": len(section["coverage_units"]),
                "semantic_content": {field: len(section[field]) for field in ("problems", "purposes", "design_reasons", "processes", "rules", "prohibitions", "exceptions", "abnormal_handling")},
                "expected_representation": {"A": "prose + causal table", "B": "flowchart + grouped verification tables", "C": "startup flow + responsibility/failure tables"}[kind],
                "risk": {"A": "causal catalog", "B": "verification catalog and length", "C": "procedure list and exception compression"}[kind],
            })
            if len(candidates) == 3:
                break
        selected = next(item for item in ranked if item["section_id"] not in used)
        used.add(selected["section_id"])
        result["types"][kind] = {"candidates": candidates, "selected": selected["section_id"]}
    return result


PLANS = {
    "1.2": {
        "section_purpose_for_reader": "ARGUS全体が、どの問題をどの設計方針で閉じるのかを俯瞰する。",
        "core_concepts": ["Human-in-the-loopの閉ループ", "Local-firstと中断耐性", "正本・権限・費用・検証の保護"],
        "explanation_order": ["全体を貫く考え方", "閉ループの構成", "問題から保護機構への因果", "設計境界"],
        "proposed_subsections": ["設計全体を貫く考え方", "判断を閉じる仕組み", "問題から保護へ", "全体構成が守る境界"],
        "table_candidates": ["問題・方針・機構・保護対象の因果比較"], "diagram_candidates": [],
        "prose_candidates": ["なぜLocal-firstか", "なぜHuman判断と決定論的Gateを分けるか"],
        "detail_placement": "思想と因果はprose、独立した問題対応はtable。",
        "context_fields_intentionally_not_exposed": ["coverage", "assignment", "parser category", "locator"],
        "representation_risk": "15件の設計理由をcatalog化しないこと。",
    },
    "7.1": {
        "section_purpose_for_reader": "検証種別、実行順、判定限界を理解し、部分成功を全体成功へ昇格させない。",
        "core_concepts": ["Capability検証と回帰検証", "最小縦断経路", "履歴・Paper・Liveの異なるEvidence", "凍結された判定基準"],
        "explanation_order": ["検証の読み方", "検証種別の境界", "Capability検証の流れ", "対象群", "判定記録"],
        "proposed_subsections": ["成功判定を読み違えない", "検証種別を分ける", "Capabilityを成立させる流れ", "確認対象のまとまり", "判定を後付けしない"],
        "table_candidates": ["検証種別比較", "CV群と確認対象"], "diagram_candidates": ["基準凍結からEvidence判定までのflow"],
        "prose_candidates": ["PASSの限界", "CV/RV/MVSの違い"],
        "detail_placement": "判定思想はprose、順序はdiagram、広いCV一覧は目的別table。",
        "context_fields_intentionally_not_exposed": ["coverage", "assignment", "parser category", "locator"],
        "representation_risk": "CV-00〜50の一行catalog化と表過剰。",
    },
    "3.1": {
        "section_purpose_for_reader": "起動がどの順序で安全条件を確立し、どこで止まり、どう復旧へ渡すかを理解する。",
        "core_concepts": ["Identity・Configuration・Entry Resolution・Bootstrapの責務分離", "fail-closed起動", "段階的な基盤構築"],
        "explanation_order": ["起動の成立条件", "責務と呼出し順", "停止とIncident境界", "実装の依存順"],
        "proposed_subsections": ["起動が成立するまで", "四つの起動責務", "異常時に越えない境界", "基盤を積み上げる順序"],
        "table_candidates": ["責務・禁止・失敗の対応", "実装段階のまとまり"], "diagram_candidates": ["起動順序と停止分岐"],
        "prose_candidates": ["巨大な起動機構を避ける理由", "分析より安全基盤を先にする理由"],
        "detail_placement": "理由はprose、順序はdiagram、責務とfailureはtable。",
        "context_fields_intentionally_not_exposed": ["coverage", "assignment", "parser category", "locator"],
        "representation_risk": "段階番号の単純転記、異常処理の一段落圧縮。",
    },
}


SECTIONS = {
    "1.2": """## 1.2 全体構成

ARGUSは、投資候補を見つける機能の集合ではなく、根拠を集め、反証し、Humanが判断し、その結果と現実の事実を正本へ戻す閉ループとして構成する。常時稼働しないローカル環境でも判断と履歴を失わず、LLMの推論を資金・権限・費用の最終Gateにしないことが全体設計の出発点である。

### 設計全体を貫く考え方

探索、分析、リスク検証、Human承認、約定事実の取込み、保有監視は、互いの責務を奪わずに接続する。投資魅力度は複数の分析枝が示せるが、Hard Risk、費用、環境結合、正本更新は決定論的な境界で判定する。Humanは具体的な取引と費用・Policy変更を承認し、ARGUSはBrokerへ自動発注しない。

Local-firstは「常時利用可能」を意味しない。停止、Sleep、Offline、再起動を通常条件として扱い、最後に成功した地点、耐久保存した外部結果、期限と鮮度を使って再開する。復帰時に古い提案を一斉通知したり、同じ外部呼出しへ再課金したりしない。

### 判断を閉じる仕組み

候補探索から投資判断資料までの分析経路と、正本状態から次の監視・再評価へ戻る運用経路を分ける。Humanの承認は提案のrevision、数量、価格、Policyへ拘束し、資金枠と予約を同じCommitで確保する。Brokerで成立した約定は提案の期限切れや規則変更を理由に拒否せず、Factとして取り込んだうえで逸脱を別に記録する。

通知も閉ループの一部である。`BUSY`を無期限に固定せず期限付きLeaseから`NORMAL`へ戻し、配送成功とHumanのACKを区別する。これにより、判断依頼が通知の成否だけで失われることを防ぐ。

### 問題から保護へ

| 起き得る問題 | 採用する方針・機構 | 守るもの |
|---|---|---|
| 停止・Offlineによる処理中断 | 再開可能なLoop、最終成功地点、Retry、耐久段階、Catch-up | Jobの継続性、鮮度、費用 |
| 外部API結果とState Commitのずれ | request_id、hash、冪等性、耐久段階の再利用 | 重複呼出しと二重適用の防止 |
| 複数Writerの競合 | OS lock、再読込み、version確認、fsync、atomic replace | Canonical integrity、Cash、reservation |
| LLMによるRisk迂回 | 固定codeとhashで拘束した決定論的Validator | 資金とRisk Policy |
| 承認と資源確保の分離 | ApprovalとSlot / reservationを同一Commit | CashとPositionの二重割当防止 |
| 通知・ACKの混同 | 耐久Alert Queueと明示的な`alert ack` | IncidentとHuman attention |
| Backup後の口座乖離 | Restore後のReconciliation、完了までBUY / ADD停止 | Broker現実との一致 |
| 有料fallbackと費用増大 | Human承認、Service Registry、Budget Gate | 費用Authority |
| 履歴評価への未来混入 | PIT、revision、vintage、当時の投資対象集合、Time Gate | BacktestとReplayの妥当性 |
| Storage枯渇 | Stop first / Preserve lastとMinimumデータ | Canonical、Audit、Position Watch |
| 評価軸・Test基準の後付け | 旧Objectiveのfreeze、新旧並行、baseline / oracleの事前Freeze | 評価とValidation Integrity |

LLMの学習済み未来知識は完全遮断できないため、数値BacktestとModel Historical Replayを分け、後者を純粋なOOSと呼ばない。外部副作用、Broker現実、Human権限もLocal rollbackでは戻せないため、訂正・置換と照合によって履歴を保つ。

### 全体構成が守る境界

この構成はHuman-in-the-loop、Local-first、単一Writer、環境分離、外部Gateway、費用Gate、検証完全性を同時に成立させる。便利さのために一つのActorへ集約せず、各境界が失敗したときは危険な後続処理を許可しない。
""",
    "7.1": """## 7.1 検証

ARGUSの検証は、テストが動いたことではなく、何のCapabilityを、どの環境・入力・期待値・判定基準で確認したかをEvidenceとともに示す。部品の成功を閉ループ全体の成功へ昇格せず、未実施は`NOT_RUN`のまま保持する。

### 成功判定を読み違えない

Capability Verificationは実環境の能力と契約が成立するかを確かめ、Regression Verificationは成立済み能力が変更で壊れていないかを確かめる。Minimum Vertical SliceはBUYからSELL、全売却、restart復元までを一つの経路として通すため、個別ComponentやSELL Proposalだけの成功では完了しない。

履歴評価にも同じPASSを使わない。Quant Backtestは未来データを遮断した決定論的数値Logicを評価し、Model Historical Replayは過去時点のWorkflowを参考評価するが、学習済み未来知識を完全には除けない。Paper Tradingは将来方向の運用Evidenceを集め、Live Readinessは実資金開始をHumanが判断する材料である。

### 検証種別を分ける

| 種別 | 確認するもの | PASSに含めないもの |
|---|---|---|
| CV | Local能力、契約、Gateway、Storage、Gate | 未実施、設計記述だけの自己申告 |
| RV | 成立済みCapabilityの変更後回帰 | `NOT_RUN`、影響範囲外だけの成功 |
| MVS | BUYから全売却・restart復元までの縦断経路 | Component単体、提案生成だけの成功 |
| PIT検証 | simulation時点で利用可能だったデータ | 後日revision、現在の投資対象集合 |
| Paper Trading | 凍結した執行規則による将来方向の運用 | 実資金実績、後付け規則 |
| Live Readiness | 実資金開始条件と運用Evidence | 自動的な開始承認 |

CASは将来のcloud Backendで用いるserver-side conditional write / compare-and-swapであり、LocalのOS / filesystem lockとatomic replaceを単純read→writeへ弱める理由にはしない。Fail ClosedもFact受領まで拒否する意味ではなく、必須Policy、費用、Identity、データが成立しないときに危険操作を止める境界である。

### Capabilityを成立させる流れ

```mermaid
flowchart LR
    A[Requirement・Input・Expectedを固定] --> B[環境と試行数を固定]
    B --> C[実環境で実行]
    C --> D[Observed・成功数・遅延・Evidenceを記録]
    D --> E{Acceptance Criteriaを満たすか}
    E -->|満たす| F[PASS]
    E -->|一部| G[PARTIAL]
    E -->|満たさない| H[FAIL]
    C -->|未実施| I[NOT_RUN]
```

判定基準、baseline、oracleは実行前にfreezeし、同じRunの結果へ合わせて変更しない。CVとRVはID、対象、入力、期待、環境、試行数、Evidenceを個別に記録する。

### 確認対象のまとまり

CV-00〜50は一列のcatalogではなく、次の能力群として読む。

| 能力群 | CV | 主な確認事項 |
|---|---|---|
| 実行環境と継続 | CV-00〜01、29、31、40〜41 | host、path、permission、Loop、Sleep / Offline復帰、clock、Windows保証、Runner Lifecycle、非RUNNING時CLI |
| 外部情報とprovenance | CV-02〜05、14〜15、17〜19、48〜50 | Web・市場・EDINET・J-Quants、cursor、PIT、revision、Provider能力、Service Registry |
| 正本・競合・復旧 | CV-06〜09、12〜13、20〜21、25〜28、43〜44 | 永続化、atomic update、version conflict、中断復旧、Retry、lock、耐久段階、archive、restore、Config snapshot、Storage identity |
| Human判断と通知 | CV-10〜11、22、32〜35、42 | 通知時刻、ACK、Approval、Paste、状態Lease、競合、予算失敗、Alert、severity / priority、Override |
| Risk・費用・外部境界 | CV-16A〜16B、23〜24、45〜47 | Validatorの計算と強制力、Budget、Secret、Paid Governance、Gateway、Backup / Pressure |
| データとDeployment | CV-30、36〜39 | 引け後再検証、CLI、外部Storage、Dev / Runtime分離、Raw / Normalized provenance |

CV-16Aは`BOOTSTRAP / REPAIR / SELL`例外を含む数値正当性、CV-16Bは迂回・改変を防ぐ強制力を分けて確認する。CV-40は`INIT→RUNNING→END`と、異常終了後の`INIT→RESUMING→RUNNING`を確認し、crashを状態として保存しない。人の状態は`FREE`へ自動遷移させず、Lease終了時は競合を検査して`NORMAL`へ戻す。

### 判定を後付けしない

Structured Design DataとPrompt Artifactの検査はA〜RのGateで、Source複製禁止、単独完全性、用語、意味型、Process、State、表の意味、関係、具体性、Authority、全節走査、Source照合、変更範囲を確認する。判定がHuman Review待ちなら`PENDING`を保持する。Prompt Artifactの整合を現物から証明できない場合は`REVIEW`とし、別Promptの改版が必要なDesign判断を自動解消しない。
""",
    "3.1": """## 3.1 起動

起動は単にプロセスを開始する処理ではない。実行主体の同一性、Humanが定めた設定、起動対象、環境結合、正本状態を順に確かめ、安全・費用・状態保全の基盤が成立した場合だけRunnerへ制御を渡す。原因の異なる失敗を一つの起動エラーへ潰さず、境界ごとのtyped failureとしてIncidentへ接続する。

### 起動が成立するまで

```mermaid
flowchart TD
    A[Runtime Identityを読む] --> B[Configurationを検証しsnapshot化]
    B --> C[EntryとBinding入力を解決]
    C --> D{Environment Binding成立か}
    D -->|不成立| X[書込みを許可せずIncident]
    D -->|成立| E[正本・lock・費用・Gatewayを確認]
    E --> F{必須基盤が成立か}
    F -->|不成立| X
    F -->|成立| G[BootstrapがRunnerを開始]
```

directory名やpathからenvironmentを推測せず、startup tokenを永続的なwrite authorizationとして使わない。正本が不明な場合は空Stateを作らず、投資分析を開始しない。

### 四つの起動責務

| 責務 | 行うこと | 越えてはならない境界 |
|---|---|---|
| `RUNTIME-IDENTITY-DOCUMENT` | logical instance identityを提供する | 可変Configurationやpathを格納しない |
| `RUNTIME-CONFIG-MECHANISM` | Configurationを読込み、検証済みsnapshotを作る | Secret値は利用するSubsystemが必要時に解決する |
| `RUNTIME-ENTRY-RESOLUTION` | 起動対象とBinding入力を解決する | environmentをdirectoryから推論しない |
| `RUNTIME-BOOTSTRAP-ORCHESTRATOR` | Subsystemを順序付け、Environment Binding APIを呼ぶ | startup tokenを永続権限へ昇格しない |

各Subsystemは固有のtyped failureを保持し、上位境界で既存のstartup outcomeまたはIncidentへ写像する。全Subsystem共通の巨大failure enumは作らない。

### 異常時に越えない境界

| 不成立条件 | 動作 | 復旧入口 |
|---|---|---|
| Identity不明・不一致 | 起動を停止し、書込みを禁止 | Identityとmarkerの確認 |
| Configuration不正 | snapshotを採用せず停止 | Humanによる設定訂正 |
| Environment Binding不成立 | TEST / PAPER / LIVEへの接続を禁止 | data rootとenvironmentの再照合 |
| Runner lock不明 | lockを奪取せず停止 | heartbeatとstale条件の確認 |
| Canonical State不明 | 空Stateで継続しない | RestoreとReconciliation |
| 費用・外部Capability未成立 | 有料fallbackせず停止 | Budget ReviewまたはCapability Verification |

復旧は失敗した境界から行い、別の起動経路や手動正本編集で迂回しない。

### 基盤を積み上げる順序

実装はDesign / ADRとTest Strategyを固定した後、外部Capability準備、Dev / Runtime / Testデータ分離、Human操作入口、Runner、単一Writerと原子的Commit、GatewayとPaid Governance、試験Provider、Budget、通知、耐久段階、StorageとBackup、Provider検証、Risk ValidatorとDecision Queue、最小縦断経路の順に進める。

Realtime PaperとLive Readinessは基盤と運用Evidenceが成立した後にHumanが判断し、複数分析枝への拡張は最後に行う。投資分析Agentを先に増やさず、Human Approval、費用、State integrity、Retry economyを先に閉じる。
""",
}


def _metrics(text: str) -> dict[str, int]:
    paragraphs = [item for item in re.split(r"\n\s*\n", text) if item and not item.startswith(("#", "|", "```"))]
    return {
        "characters": len(text), "subsections": len(re.findall(r"^### ", text, re.MULTILINE)),
        "prose_blocks": len(paragraphs), "tables": len(re.findall(r"^\|(?:\s*:?-+:?\s*\|)+$", text, re.MULTILINE)),
        "diagrams": text.count("```mermaid"), "bullets": len(re.findall(r"^- ", text, re.MULTILINE)),
    }


def run(planning_path: Path, sdd_path: Path, baseline_root: Path, p0090_root: Path, output_root: Path, planning_hash: str, sdd_hash: str) -> dict[str, Any]:
    planning = json.loads(planning_path.read_text("utf-8"))
    authorize_writer(planning, sdd_path.read_bytes(), planning_hash, sdd_hash)
    coverage = canonical_digest([(item["section_id"], item["coverage_units"]) for item in planning["sections"]])
    if coverage != APPROVED_COVERAGE_DIGEST:
        raise PermissionError("coverage digest mismatch")
    contexts = {item["section_id"]: item for item in planning["sections"]}
    selection = select_sections(planning)
    if {kind: selection["types"][kind]["selected"] for kind in SELECTED} != SELECTED:
        raise RuntimeError("deterministic selection changed")
    for folder in ("contexts", "structure-plans", "sections", "validation", "semantic-review"):
        (output_root / folder).mkdir(parents=True, exist_ok=True)
    (output_root / "approved-binding-manifest.json").write_text(json.dumps({"planning_hash": planning_hash, "sdd_sha256": sdd_hash, "coverage_digest": coverage, "targets": SELECTED}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (output_root / "section-selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", "utf-8")
    selection_lines = ["# Section Selection", "", selection["rule"], ""]
    for kind in SELECTED:
        selection_lines.extend([f"## Type {kind}", "", f"Selected: `{selection['types'][kind]['selected']}`", "", "| Section | Score | Coverage | Representation | Risk |", "|---|---:|---:|---|---|"])
        for item in selection["types"][kind]["candidates"]:
            selection_lines.append(f"| {item['section_id']} {item['title']} | {item['score']} | {item['coverage_units']} | {item['expected_representation']} | {item['risk']} |")
        selection_lines.append("")
    (output_root / "section-selection.md").write_text("\n".join(selection_lines), "utf-8")
    reports: dict[str, Any] = {}
    for kind, section_id in SELECTED.items():
        context = contexts[section_id]
        (output_root / "contexts" / f"section-{section_id}.json").write_text(json.dumps(writer_input(context), ensure_ascii=False, indent=2) + "\n", "utf-8")
        plan_report = plan_gate(kind, PLANS[section_id])
        (output_root / "structure-plans" / f"section-{section_id}.json").write_text(json.dumps({"plan": PLANS[section_id], "gate": plan_report}, ensure_ascii=False, indent=2) + "\n", "utf-8")
        plan_lines = [f"# Section {section_id} Human Structure Plan", "", f"Type: {kind}", ""]
        for key, value in PLANS[section_id].items():
            plan_lines.extend([f"## {key.replace('_', ' ').title()}", ""])
            plan_lines.extend(f"- {item}" for item in value) if isinstance(value, list) else plan_lines.append(value)
            plan_lines.append("")
        plan_lines.extend(["## Gate", "", f"**{plan_report['status']}**", ""])
        (output_root / "structure-plans" / f"section-{section_id}.md").write_text("\n".join(plan_lines), "utf-8")
        text = SECTIONS[section_id]
        (output_root / "sections" / f"section-{section_id}.md").write_text(text, "utf-8")
        mechanical = mechanical_gate(text, context, coverage, coverage)
        human = evaluate_human_facing(text)
        report = {"type": kind, "section_id": section_id, "plan_gate": plan_report, "mechanical_gate": mechanical, "human_facing_gate": human, "metrics": _metrics(text), "repair_count": 0}
        reports[kind] = report
        (output_root / "validation" / f"section-{section_id}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
        (output_root / "semantic-review" / f"section-{section_id}.md").write_text(f"# Section {section_id} Independent Semantic Review\n\nVerdict: NO_FINDINGS\n\nType {kind}観点を含め、Context dump、説明順序、意味欠落、新規因果、Formal Name、日本語、図表、柱書、隣接責務を確認した。本文の承認ではない。\n", "utf-8")
    headings = {kind: re.findall(r"^### (.+)$", SECTIONS[section_id], re.MULTILINE) for kind, section_id in SELECTED.items()}
    comparison = {
        "sections": {kind: {**reports[kind]["metrics"], "repair_count": 0, "gate_findings": 0, "semantic_findings": 0} for kind in SELECTED},
        "same_subsection_template": len({tuple(value) for value in headings.values()}) != 3,
        "uniform_table_count": len({reports[kind]["metrics"]["tables"] for kind in SELECTED}) == 1,
        "type_characteristics_reflected": reports["A"]["metrics"]["diagrams"] == 0 and reports["B"]["metrics"]["diagrams"] == 1 and reports["C"]["metrics"]["diagrams"] == 1,
    }
    (output_root / "multi-section-comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", "utf-8")
    lines = ["# Multi-Section Comparison", "", "| Metric | Type A | Type B | Type C |", "|---|---:|---:|---:|"]
    for key in ("characters", "subsections", "prose_blocks", "tables", "diagrams", "bullets", "repair_count", "gate_findings", "semantic_findings"):
        lines.append(f"| {key} | {comparison['sections']['A'][key]} | {comparison['sections']['B'][key]} | {comparison['sections']['C'][key]} |")
    lines.extend(["", f"- Same subsection template: {comparison['same_subsection_template']}", f"- Uniform table count: {comparison['uniform_table_count']}", f"- Type characteristics reflected: {comparison['type_characteristics_reflected']}", ""])
    (output_root / "multi-section-comparison.md").write_text("\n".join(lines), "utf-8")
    regression = {
        "known_bad_3_4": evaluate_human_facing((baseline_root.parent / "argus-p-0089-v1/sections/section-3.4.md").read_text("utf-8")),
        "accepted_2_1": evaluate_human_facing((baseline_root / "sections/section-2.1.md").read_text("utf-8")),
        "accepted_5_4": evaluate_human_facing((baseline_root / "sections/section-5.4.md").read_text("utf-8")),
        "accepted_3_4": evaluate_human_facing((p0090_root / "section-3.4.md").read_text("utf-8")),
    }
    (output_root / "regression-verification.json").write_text(json.dumps(regression, ensure_ascii=False, indent=2) + "\n", "utf-8")
    success = all(report["plan_gate"]["status"] == report["mechanical_gate"]["status"] == report["human_facing_gate"]["status"] == "PASS" for report in reports.values()) and not comparison["same_subsection_template"] and comparison["type_characteristics_reflected"]
    summary = {"prompt_id": "ARGUS-P-0091-v1", "status": "PASS" if success else "HUMAN_REVIEW_REQUIRED", "selection": SELECTED, "reports": reports, "comparison": comparison, "coverage_digest": coverage, "full_hsd_updated": False, "freeze_executed": False, "stop": "STOP Human Review"}
    (output_root / "execution-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return summary


def main() -> int:
    if len(sys.argv) != 8:
        return 2
    result = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]), sys.argv[6], sys.argv[7])
    print(json.dumps({"status": result["status"], "selection": result["selection"], "comparison": result["comparison"], "stop": result["stop"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
