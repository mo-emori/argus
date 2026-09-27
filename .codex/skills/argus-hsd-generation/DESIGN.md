# ARGUS HSD Generation Skill Design v0.1

## 1. 目的と非目的

SDD から HSD を生成する前段を、検証可能な機械処理と Human 承認境界に分離する。現版はParser、Section Context Builder、Planning Validator、Planning Artifact、Human Approval Gateまでを実装し、HSD本文を生成しない。

## 2. Authority と入力

設計の一次 Authority は `docs/source/argus_design_source_v0.1.md`、直接構造入力は `docs/model/argus_structured_design_data_v0.1.md` とする。不一致は Design Source を優先し、Human Review finding として停止する。

## 3. 全体パイプライン

`SDD -> Parser -> Parser Self-Check -> Section Context Builder -> Context Set -> Planning Validator -> Planning Artifact -> STOP HUMAN REVIEW -> Human explicit approval -> Writer -> Mechanical Gate -> Section-local Repair -> Semantic Review -> Assembler -> Final Validator -> Coverage Map -> Human Review` とする。現版はSTOP HUMAN REVIEWまでを実行する。

## 4. SDD Parser

非空行を input unit とし、heading、label、table、list、fence、prose を決定論的に一分類する。分類不能、複数分類、section 未割当、重複割当は parse failure とする。単に節が存在しない状態と parse failure を区別する。

## 5. Parser Self-Coverage

`total = recognized + unrecognized + ambiguous + duplicate + unassigned` を検査する。成功には全 unit がちょうど一度認識され、後四分類がゼロであることが必要である。type 別件数を Evidence として出す。

## 6. Section Context

Context はsection_id、title、depth、premises、problems、purposes、design_reasons、processes、rules、prohibitions、exceptions、abnormal_handling、exact_values、states、semantic_candidates、actors_authorities、boundaries、relations、unresolved、cross_references、primary_owner、diagram_plan、source_locators、coverage_units、planning_statusを持つ。各SourceElementはcoverage ID、semantic kind、locator、原記述を保持する。semantic candidate は formal_state / status_value / identifier / technical_term / actor_component / unknown_candidate と CONFIRMED / REVIEW_REQUIRED / REJECTED を分離する。raw SDD、SDD path、全文fieldは持たない。

## 7. Planning Artifact

全39 Section Context、validation finding、artifact digest、旧Coverage Mapとの全件reconciliationを持つ。課題・目的・設計理由・前提の希薄性、semantic candidate noise、assignment confidence、baseline差分、coverage・owner・locator欠落、Coverage ID重複、duplicate primary owner、未解決参照、具体値不整合、schema違反をFAIL/WARNING/REVIEW_REQUIREDで可視化する。Parser失敗、配置失敗、SDD上の真の不在を区別し、真の不在だけがHumanのabsent_reason / approved_by / approval_refで例外化できる。旧UnitのMISSINGは承認をfail closedする。

## 8. Human Approval Gate

Human が `APPROVED`、承認者、時刻、planning digest を明示したときだけ WriterAuthorization を発行する。Codex、LLM、AI、auto は承認主体にできない。承認記録を本 Skill が自動作成しない。

## 9. Writer Interface と INV-01

WriterInput は Section Context、writing rules、approved references のみを受ける。raw SDD field、path、自由な source text を API に持たない。型と runtime 検査の両方で LLM input isolation を守る。

## 10. Coverage Ownership と INV-02

CoverageLedger は Python が unit を登録し、配置と判定を更新する。LLM-facing payload は immutable snapshot で更新 API を持たない。未知 ID、重複 unit、違法遷移は拒否する。

## 11. 日本語 Gate

日本語 Gate は見出し・本文・表・Mermaid label の Latin 偏重を機械検出する。正式用語として許可する具体値 token は Exact Value Catalog から取得し、別 allowlist を持たない。

## 12. Exact Value Gate

具体値はvalue_id、canonical、accepted、label、label_terms、source locator、coverage IDを一定義に保持する。Japanese GateとExact Value Gateは同一定義を使い、短い値の偶然一致をPASSにせず、label近接不明はREVIEWとする。

## 13. Semantic Review Interface

SemanticReviewPacket は機械 Gate 結果と承認済み Context を入力にする。reviewer は `FINDINGS` / `NO_FINDINGS` と finding 一覧だけを返し、coverage 更新、承認、PASS 判定を行わない。

## 14. PoC-0 回帰

既知失敗fixtureとOracleを固定し、PoC-0の8件、Expected finding 3件、MISSED 0、FALSE_POSITIVE 0、REVIEW 1を維持する。結果に合わせてOracleを変更しない。

## 15. 未実装範囲と停止条件

Section Writer、HSD assembly、final validator、repair loop、外部API、有料orchestration、完全なCV/RV、diagram生成は未実装である。Planning Artifact生成後は必ずSTOP Human Reviewする。

## 16. 責務境界

PythonはSDD構造、Parser self-check、Coverage ID、schema validation、機械候補抽出、Planning集計、機械Gate、承認状態、Coverage書込みを所有する。Codex/LLMは機械規則で確定不能な配置候補と将来の表現・意味指摘を扱う。Humanは配置、真の不在、Semantic Review、Governance変更を承認する。Pythonが意味理解を行えるとは仮定しない。

## 17. Section割当とCoverage

HSD骨格はHuman理解順序であり、SDD semantic typeの分類表ではない。明示的assignment policyで配置し、確定不能はREVIEW_REQUIREDとする。Coverage Unitはlabel配下の独立記述または表の意味行を原則とし、文字断片へ過剰分割しない。一つのprimary ownerとsecondary cross-referenceを区別し、Coverage stateはPythonだけが書く。

## 18. Term Governance

用語はalways_allowed、bilingual_only、forbiddenに分類する。baseline変更は理由、diff、Human承認者、approval referenceを持つ新revisionだけを許可する。通常RepairやAI自己承認でbaselineを緩和しない。

## 19. diagram_plan / Repair

PlanningはNEEDED / NOT_NEEDED / REVIEW、candidate type、reasonだけを持ち、図を生成しない。Repairは将来のSection単位処理、最大2回、diff保存とし、未収束はHUMAN_REVIEW_REQUIRED。baseline変更をRepairと扱わない。

## 20. 退化防止不変条件

INV-01 LLM Input Isolation、INV-02 Coverage Ownership、INV-03 Mechanical Gate Ownership、INV-04 Governance approval、INV-05 SKILL.md入口限定、INV-06 PoC-0 regression、INV-07 Planning Approvalをcode/testで固定する。

## 21. Section Writer PoC

`planning_v2.py::authorize_planning_artifact` は唯一のWriter authorization正本であり、Human approval、非AI approver、Planning hash、SDD hash、timezone付きtimestampを検証する。認可後、`writer_boundary.py` は対象Section Context、writing rules、approved references、Chapter Contract、許可されたcross-reference metadataだけをclosed envelopeとしてLLM Writerへ渡す。全文SDD、全文Design Source、他Section全文を含めない。PythonはHuman-facing plan・本文・図表を生成しない。出力はraw stringではなくprovenance付き `LLMWriterOutputArtifact` として検証し、session/chapter/contract/input/producer/timestamp/version不一致を拒否する。

## 22. 表現選択と全体Assembly

独立した対応関係を長い段落へ圧縮しない。2列以上の属性比較は表、一機構と説明の対応は箇条書き、処理順はflowまたは番号構造、状態遷移はstate/table/diagramを候補とする。ただしCoverage Unit単位の機械的列挙へ戻さず、因果、順序、例外を保つ。局所補正から全体展開する場合、対象Sectionで表現改善、意味保存、Mechanical Gate、Semantic Review、Coverage不変、受入済みSection不変を先にGateする。AssemblyはSection本文を大規模再生成せずPlanning skeleton順に結合し、全951 Coverage、cross-reference、exact value、formal state、日本語、過圧縮、catalog化、規範重複を横断検査する。Whole-HSD Reviewerはfindingだけを返し、本文修正、承認、Freezeを行わない。

## 23. Human-facing Composition Regression

Section Contextは本文schemaではなく材料箱とする。WriterはContext全体からHumanが理解すべき概念、順序、関係、図表、詳細配置を先にHuman Structure Planとして決め、本文・図表の後に柱書を作る。Coverage ID、assignment、parser分類、source locator、semantic dispositionを本文へ出さない。Human-facing Regression GateはPythonで確定できるcontext field見出し漏出、label-value dump、空heading/bullet、長大な単一level bullet catalog、template dump兆候を検出する。意味上の説明順序、因果、図表妥当性、catalog化は独立Semantic Reviewがfindingとして返す。既知不良fixtureの検出と受入済みSectionの非誤検出を一つの回帰条件とする。

## Session Architecture

HSD統制Sessionは全体TOC、章目的、読者の理解順序、章境界、cross-reference、重複回避、用語・粒度・図表方針、各Chapter Contract、完成後の全体整合Reviewを担当する。本文は量産しない。

大SectionごとにFresh LLM Writer Sessionを開始し、その配下の小Sectionを同一Sessionで扱う。次章には会話履歴や前章本文を渡さず、Artifact化された全体構成、対象Chapter Contract、Writer rules、承認済み参照、許可されたcross-reference metadataだけを渡す。Chapter Contractは説明責務と境界を定める契約であり、固定subsection数・table数・diagram数を含む本文Templateではない。詳細は `references/session-architecture.md` と `references/chapter-contract.schema.json` を正とする。

Fresh Sessionは現段階ではHuman-operated orchestration requirementであり、session IDの相違だけでfresh contextやprevious-context isolationを機械保証したとは扱わない。実LLM Writer harness接続時のsession creation provenanceとcontext isolation検証は次フェーズの未解決事項とする。

## Renderer migration

旧 `full_writer.py`、`drift_load_poc.py`、`multi_section_poc.py`、`repair_34.py`、`writer_poc.py` はproduction/active scriptsから除外し、過去Evidenceの検証専用として `tests/fixtures/legacy-renderers/` に隔離する。active Writerはこれらをimportまたはexecuteしない。

## 24. Multi-Section Composition PoC

局所修復の全体適用前に、説明・思想中心、Process中心、運用・異常処理中心からContextだけを使う決定論的scoreで各一Sectionを選ぶ。各Typeの上位候補、score、Coverage規模、semantic content、expected representation、representation riskを保存する。Type Aは自然なprose、Type Bは順序・分岐、Type Cは通常・異常・禁止・復旧境界を主眼とし、同じ表・図・subsection templateを強制しない。生成後は文字数、subsection、prose block、table、diagram、bullet、repair、Gate、Semantic findingを比較し、異なる内容が同じ外形へ収束していないことを検査する。

## 25. Translation Stage

Semantic Gate済みEnglish Semantic Draftは、Writerとは異なるFresh LLM Translator Sessionへclosed envelopeで渡す。Translator入力はsource draftとTranslation Contractだけであり、Source、SDD、Section Context、Coverageを含めない。Translatorは日本語化だけを担当し、設計判断、構造変更、追加、削除、要約、一般化を行わない。

Translation Contractは構造lockと保護対象を型付きで保持する。Translation provenanceはsource draft digest、translator session、producer、contract version、output digest、timezone付きtimestampを追跡する。Writer/Translator session一致、source/output digest不一致はfail closedとする。Translation Preservation Gateは構造、識別子、literal、path、数値、規範強度、未確定性を検査し、機械確定不能な追加意味の疑いを理由付きREVIEWとして独立Semantic Reviewへ渡す。Pythonは訳文を生成しない。

## 26. Independent Translation Semantic Review

Translation Preservation Gateが独立意味Reviewを要求した場合、orchestrationは結果なしで後続Gateへ進めない。ReviewerはWriter/Translatorと異なるFresh LLM Sessionとし、English Draft、Japanese Draft、Translation Contract、機械Gate結果だけを受け取る。Source、SDD、Context、Coverage、完成済み本文を入力しない。

PythonはReview schemaとdigest/session/producer/provenance binding、`PASS / REVIEW / FAIL` routingだけを担当する。`REVIEW`はSTOP Human Review、`MISSING / DISTORTED / INVENTED`はFAILとし、未解決findingを含むPASSを拒否する。subject-target、因果、条件、列挙対応等の自然言語意味判定はLLM Reviewerの責務でありPythonへ実装しない。
