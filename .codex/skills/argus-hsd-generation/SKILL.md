---
name: argus-hsd-generation
description: ARGUS の Structured Design Data から Human System Design を生成する工程を、安全な Python 管理の coverage、Human 承認済み Planning Artifact、機械 Gate、独立 Semantic Review に分離して実行するときに使用する。HSD の生成・再生成、SDD parser、Section Context、Planning Gate、PoC-0 回帰に適用する。
---

# ARGUS HSD Generation

この Skill は HSD 生成工程の境界を定義する。現版は基盤だけを実装し、Section Writer、HSD 組立、Repair、外部 API 呼出しは実行しない。

HSD は `NONCANONICAL_HUMAN_READABLE_PROJECTION` であり、Design Source / SDD に代わる machine authority ではない。Design Source / SDD の厳格品質、Section Context / Coverage の搬送 integrity、provenance / session binding / UTF-8 artifact integrity は fail-closed のまま維持する。

## HSD quality severity

- `BLOCKER`: 禁止・許可・責務・因果の反転、挙動を変える数値・状態・条件変更、主要安全条件・process・state transition の丸ごと欠落、主要設計の発明、読解不能な文字化け、意味を変える protected value 破損、authority / provenance / session binding 破壊、技術的生成不能。Section は `BLOCKED` とする。
- `REVIEW`: design reference 単独欠落、minor Coverage omission、意味と順序を保つ literal 表記差、通常の metadata leakage、technical term 揺れ、subsection・図表選択、一部圧縮・説明不足、軽微な semantic uncertainty。Section は `ACCEPT_WITH_FINDINGS` とし、pipeline を継続する。
- `WARNING`: 日本語の硬さ、英語残存、冗長、文分割、軽微な表記・reader journey、図表・柱書品質、catalog 化候補。Section の `PASS` を妨げず、自動 Repair しない。

Section result は `PASS`（BLOCKER=0、REVIEW=0）、`ACCEPT_WITH_FINDINGS`（BLOCKER=0、REVIEW>=1）、`BLOCKED`（BLOCKER>=1または技術的生成不能）とする。自動 Repair は BLOCKER に対して Section ごとに最大1回だけ行い、REVIEW / WARNING だけでは行わない。`ACCEPT_WITH_FINDINGS` は Translation、次Section、Assemblyへ進める。BLOCKED Section があっても無関係Sectionを可能な限り継続し、生成済みSectionから Partial Candidate を作る場合は blocked / missing Section を明示する。Whole-document Review は candidate 生成後に実施し、REVIEW / WARNING を Finding backlog として保持する。

## 必須フロー

1. `scripts/sdd_parser.py` で SDD を解析し、self-coverage report を確認する。
2. 未認識、曖昧分類、重複割当、未割当が一件でもあれば停止する。
3. `scripts/context_builder.py` と `scripts/planning_v2.py` で全39 Section ContextとPlanning Artifactを作る。
4. 課題、目的、設計理由、前提、具体値、semantic candidate、coverage、assignment confidence、primary owner、cross reference の欠落・要確認を確認する。
5. 直近 Coverage Map がある場合は全旧 Unit を `SAME / SPLIT / MERGED / EXCLUDED_NON_DESIGN / MISSING / DEFINITION_CHANGED / REVIEW_REQUIRED` のいずれかへ照合し、`MISSING` が一件でもあれば承認を拒否する。
6. Human が Planning Artifact の digest を明示承認するまで Writer phase を開始しない。
7. Writer へ渡せるのは Section Context と writing rules と承認済み参照だけである。
8. SDD 全文、SDD path、raw source を Writer / LLM へ直接渡さない。
9. Coverage ledger の生成・更新・集計・判定は Python だけが所有する。LLM 出力で更新しない。
10. 日本語 Gate と Exact Value Gate は `references/exact_values.json` の同一定義を使う。
11. Semantic Review は機械 Gate と分離し、`FINDINGS` または `NO_FINDINGS` だけを返す。`PASS` を返さない。各 Finding は `BLOCKER / REVIEW / WARNING` に分類し、未分類 Finding を機械的に降格しない。
12. Planning Artifact生成後は必ず `STOP Human Review`。承認済みhashなしにWriterへ進まない。
13. Term/Exact baseline変更は通常Repairから分離し、理由・diff・Human approval referenceを要求する。
14. Writer authorizationの正本は `scripts/planning_v2.py::authorize_planning_artifact` だけとする。Human approval、approver、planning hash、SDD hash、timezone付きtimestampをFail Closedで検証してから、`scripts/writer_boundary.py` のclosed envelopeをLLM Writer Sessionへ渡す。PythonはHuman-facing本文を生成しない。
15. Writer入力は対象Section Context、writing rules、承認済み用語・参照規則の3種に限定する。Coverageは読み取り専用とし、前後digestを照合する。
16. Mechanical Gate後のSemantic Reviewは `FINDINGS` / `NO_FINDINGS` のみを返し、本文修正・PASS・承認・Freezeを行わない。
17. 独立した対応関係を長い連続段落へ圧縮しない。複数の機構と防止事項・保護対象、条件と動作、状態と遷移は、因果を失わない範囲で表または箇条書きを優先する。
18. 局所Writer rule補正後に全体展開する場合は、指定Sectionだけで補正効果と不変条件を先にGateし、失敗時は展開せず停止する。
19. Assemblyは承認済みSection本文を再生成せず、Planning skeleton順に連結し、Coverage・cross-reference・具体値・状態・日本語・過圧縮を横断検査する。
20. Section ContextはWriterの材料箱であり、field名・配列順・category順を本文テンプレートへ写像しない。本文前にHuman Structure Planを作り、Humanの理解順、図表候補、詳細配置、隠すmetadataを検査する。
21. Human-facing Regression Gateはcontext field見出しの大量展開、label-value連続、空構造、単一level bullet catalog、template dump兆候を検出する。意味品質はSemantic Reviewへ残す。
22. 既知不良Sectionをregression fixtureとして固定し、受入済みSectionを新Gateが誤ってFAILにしないことを同時に確認する。
23. 複数Section PoCでは、Contextから再現可能な採点規則で異なる性質のSectionを選び、候補・根拠・規模・表現候補・riskを保存する。
24. Type別にprose / table / diagramの役割を変え、同一subsection template、均一な表数、局所成功形式の無条件コピーを横断比較で検出する。
25. HSD統制Sessionは全体TOC、読者の理解順序、章境界、cross-reference、重複回避、用語・粒度・図表方針、Chapter Contract、全体整合Reviewを担当し、Section本文を量産しない。
26. Writer Sessionは大Section単位のFresh Sessionとする。同じ大Sectionの子Sectionは同一Sessionで扱い、次の大Sectionへ会話履歴や前章本文を持ち越さない。
27. Session間で渡せるのは、承認済み全体構成、対象Chapter Contract、Writer rules、承認済み用語・参照規則、明示許可されたcross-reference metadataだけである。
28. Human Structure Plan、説明順、subsection、prose、table、diagram、柱書はLLM Writerがsemantic needから作る。固定数・固定TemplateをPythonで決めない。
29. Context不足時は `CONTEXT_INSUFFICIENT` として停止し、Python Rendererまたは推測で補完しない。
30. Session Architectureの詳細は [references/session-architecture.md](references/session-architecture.md)、Chapter Contractの機械schemaは [references/chapter-contract.schema.json](references/chapter-contract.schema.json) を参照する。
31. LLM Writer出力はraw stringではなく `LLMWriterOutputArtifact` とし、session/chapter/Chapter Contract/Writer input/producer/timestamp/versionのprovenance一致を検査する。これは宣言provenanceの境界であり、実LLM生成の暗号学的証明ではない。
32. Fresh Sessionは現段階ではHuman-operated orchestration requirementである。session IDだけでprevious-context isolationを保証したと主張しない。

## 安全境界

- Gate の判定を LLM に委ねない。
- Human 承認を自動生成または自己付与しない。
- 外部 API、MCP、有料サービス、課金 fallback を直接呼ばない。
- Design Source と SDD の矛盾を推測で解消しない。
- PoC-0 が既知失敗 HSD を検出できない場合、生成工程へ進まない。
- `PENDING`、digest 不一致、空の承認者、AI/自動承認主体は fail closed とする。

## 現版の使い方

```powershell
python .codex/skills/argus-hsd-generation/scripts/sdd_parser.py docs/model/argus_structured_design_data_v0.1.md
python .codex/skills/argus-hsd-generation/scripts/poc0.py .codex/skills/argus-hsd-generation/tests/fixtures/poc0_known_failure.md
python .codex/skills/argus-hsd-generation/scripts/planning_v2.py docs/model/argus_structured_design_data_v0.1.md validation/planning-artifact.json docs/review/argus_system_design_coverage_map_v0.1.6.md
pytest .codex/skills/argus-hsd-generation/tests
```

実装契約と未実装範囲は [DESIGN.md](DESIGN.md)、型と Gate の定義は [references/contracts.md](references/contracts.md) を参照する。既知失敗HSDの回帰を行う場合は、入力を変更する前に [PoC-0 Test Specification](references/poc0-test-spec.md) を読む。
