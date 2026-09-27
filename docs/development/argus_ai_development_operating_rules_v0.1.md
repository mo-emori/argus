# argus AI Development Operating Rules v0.1

**Document Type:** AI-assisted Development Governance  
**Version:** `0.1`  
**Status:** `ACTIVE`  
**Canonical Location:** `docs/development/argus_ai_development_operating_rules_v0.1.md`

## 1. Purpose and authority

本書は、argusにおけるChatGPT、Human、Codex、Claude Code間の開発権限、handoff、およびPrompt Registry運用のCanonical Sourceである。

設計判断は、次のauthority modelに従う。

> Design Authority decision, based on ChatGPT design discussion and Human final approval.

### 1.1 Design Authority

`Design Authority = ChatGPT + Human`

ChatGPTは次を担当する。

- design synthesis
- Contract design
- finding analysis
- change planning
- cross-artifact consistency analysis
- Prompt作成

HumanはFinal Approval Authorityであり、次を担当する。

- Design Authorityの最終承認
- rule activation / supersessionの最終承認
- paid service等、Human approvalが要求される判断

### 1.2 Codex

Codexの役割は`Test Implementation + Production Implementation + Evidence Generation`である。CodexはDesign Authorityではない。新たなDesign判断、Contract clarification、またはCanonical Sourceの曖昧さが必要になった場合、推測して進めず停止し、Design Authorityへ返す。

### 1.3 Claude Code

Claude Codeの役割は`Independent Review / Audit Actor`である。Claude Codeはreview対象のProduction、Frozen Test、Contract、Test Strategyを修正せず、Finding dispositionおよびCapability closeを決定しない。FindingはDesign Authorityへ返す。

## 2. Canonical Source model

### 2.1 argus repository

次のCanonical Sourceはargus repositoryに置く。

- Design
- Contract
- Test Strategy
- Frozen Test
- Baseline
- Production
- Run
- Evidence
- Review Input Manifest
- Review artifact
- Finding disposition
- Development Operating Rules

### 2.2 Notion Prompt Registry

Notion Prompt Registryは次のためのhandoff / execution registryである。

- execution instruction
- AI-to-AI handoff
- execution status
- result summary / index
- output reference

NotionのPrompt本文またはResult Summaryはrepo artifactの代替ではない。Prompt内にrepo情報が複製されている場合も、指定されたrepo artifactとその実測hashを正本として検証する。

### 2.3 Conversation

ChatGPT、Codex、Claude Codeのconversation memoryはCanonical Sourceではない。後続工程に必要な状態、判断、Evidence、およびprovenanceは適切なartifactへ外出しする。

## 3. Prompt Registry model

Prompt Registry rowは基本的に次のpropertyを持つ。

- Prompt ID
- Project
- Capability
- Target
- Type
- Status
- Version
- Created By
- Approved By
- Execution Status
- Result
- Executed By
- Result Summary
- Output Ref
- Executed At

### 3.1 Status

`Status`はinstruction validityを表し、次の値を使用する。

- `DRAFT`
- `APPROVED`
- `SUPERSEDED`

### 3.2 Execution Status

`Execution Status`はexecution stateを表し、次の値を使用する。

- `NOT_RUN`
- `COMPLETED`
- `BLOCKED`
- `FAILED`

`Status`と`Execution Status`を混同しない。例えば`Status=APPROVED`かつ`Execution Status=COMPLETED`は正常な状態である。

## 4. Prompt immutability

一度`APPROVED`になったPrompt本文は実行後に書き換えない。指示変更が必要な場合は、新Versionまたは新Prompt IDを作成する。過去Promptはexecution historyとして保持し、Prompt IDをimmutableかつversionedなidentifierとして扱う。

## 5. Target actor routing

ActorはPrompt取得後、実行前に必ず次を確認する。

- `Target = current actor`
- `Status = APPROVED`
- `Approved By = Human`

条件不成立時はfail closedとする。

### 5.1 Target mismatch

`Target != current actor`の場合、非Target Actorは次を厳守する。

- Promptを実行しない
- 対象PromptのResult系propertyを変更しない
- `Execution Status`を`BLOCKED`へ変更しない
- `Result`へ`TARGET_MISMATCH`を書かない
- `Executed By`、`Result Summary`、`Output Ref`、`Executed At`を変更しない
- read-onlyで停止する

Target mismatchは対象Prompt自身のexecution failureではない。非Target Actorはローカル出力として`TARGET_MISMATCH`を報告してよいが、対象Prompt rowのexecution stateを汚染してはならない。

## 6. Result write authority

次のResult系propertyを更新できるのは、原則として対象PromptのTarget Actorだけである。

- Execution Status
- Result
- Executed By
- Result Summary
- Output Ref
- Executed At

例外はDesign Authorityによる明示的な管理・訂正操作である。この例外は誤Actor書込み等のRegistry operational correctionに限定でき、Prompt本文またはapproval metadataを暗黙に変更してはならない。

## 7. Actor-specific Registry rules

### 7.1 Codex

Codexは実行前にPrompt IDを取得し、`Target=Codex`、`Status=APPROVED`、`Approved By=Human`、およびrepo側Canonical artifact/hashを確認する。次の場合は停止する。

- approval不足
- immutable artifact mismatch
- Canonical Source ambiguity
- 新たなDesign judgmentが必要
- Contract clarificationが必要

CodexはPrompt本文または過去Versionを書き換えない。

### 7.2 Claude Code

Claude Codeは実行前にPrompt IDを取得し、`Target=Claude Code`、`Status=APPROVED`、`Approved By=Human`、repo側Canonical artifact/hash、およびReview Input Manifest boundaryを確認する。Claude Codeはread-only reviewを原則とし、Findingを発見しても修正またはDispositionせず、Design Authorityへ返す。

## 8. Review isolation

Critical Path Reviewは次を満たす。

- Review Input Manifestでreview boundaryをfreezeする
- reviewerはManifest外の変更を暗黙に追加しない
- Test PASSをContract complianceの証明として扱わない
- ContractとProductionを独立比較する
- Frozen Test coverageを別対象として監査する
- GREEN / static analysis Evidenceを補助証拠として扱う

Review Findingのflowは次とする。

```text
Review
→ Design Authority
→ Finding disposition
→ remediation / risk accept / clarification
```

reviewer自身はDispositionを確定しない。

## 9. Fail closed

不明点を推測して実行継続しない。少なくとも次の場合は停止し、理由を明示する。

- Target mismatch
- approval不足
- immutable artifact/hash mismatch
- Canonical Source ambiguity
- Design判断を要するContract ambiguity
- Review Input Manifest mismatch
- required Evidence不足

Target mismatchでは対象Prompt rowを書き換えない。

## 10. Manual fallback

Notion、MCP、またはactor integrationが利用不能でも、repoのCanonical artifactを失わない設計とする。次のようなmanual fallbackを常に許容する。

- HumanがPrompt IDをactorへ渡す
- Humanがrepo path/hashを渡す
- Review artifactを手動handoffする

自動化不能を理由にCanonical Sourceをconversation memoryへ移さない。

## 11. Rule change model

Development Operating RulesのCanonical Sourceは本repo文書である。ルール変更は次のflowに従う。

```text
Design Authority discussion
→ Human approval
→ repo rule documentの新versionまたは承認済みupdate
→ activation / handoff instruction
```

Rule変更指示をPrompt Registry経由で配布してよい。ただしPrompt Registry内のRULE系rowはCanonical Rule本文ではなく、`Rule Change / Activation / Adoption Instruction`として扱う。将来NotionにRule Registryを作る場合も、その役割はActive Rule Indexとし、repo文書をCanonical Sourceとする。

## 12. Rule versioning

本書のVersionは`0.1`、Statusは`ACTIVE`である。意味的なルール変更ではversionを更新し、旧versionを履歴として保持する。単なる誤字等の扱いは必要に応じて別途決定し、現時点で独自の上書きルールを追加しない。

## 13. AI Integration Requirementsとの対応

本書は次のAI Integration backlog requirementに対応する。各domain requirementの詳細はそのCanonical artifactを正本とし、本書ではauthority、handoff、およびoperational boundaryとの対応だけを示す。

| Requirement | 対応する本書の関心事 |
|---|---|
| `REQ-AI-001 Shared Development Context` | repo artifactによる共有context |
| `REQ-AI-002 MCP Compatibility` | MCPを利用可能なhandoff手段として扱う |
| `REQ-AI-003 Single Canonical Project State` | repoをCanonical Sourceとする |
| `REQ-AI-004 Role-Based Tool Exposure` | Actorごとの役割とwrite authority |
| `REQ-AI-005 Authority Separation` | Design / Implementation / Reviewの分離 |
| `REQ-AI-006 Human Final Approval` | HumanをFinal Approval Authorityとする |
| `REQ-AI-007 AI-to-AI Handoff` | Prompt Registryとartifact referenceによるhandoff |
| `REQ-AI-008 Review Isolation` | Review Input Manifest boundary |
| `REQ-AI-009 Provenance` | Run / Evidence / Review artifactへの外出し |
| `REQ-AI-010 MCP Tool Audit` | MCP操作をactor authority内に制限する |
| `REQ-AI-011 Least Privilege` | Target Actorだけが実行・Result更新する |
| `REQ-AI-012 Fail Closed` | ambiguity / mismatch時の停止 |
| `REQ-AI-013 Manual Fallback` | integration利用不能時の手動handoff |
| `REQ-AI-014 Provider Independence` | Canonical Sourceを特定AI providerへ依存させない |
| `REQ-AI-015 Automated Handoff Future` | 将来自動化を許容しつつ現状を過大表示しない |
| `REQ-AI-016 Prompt Registry / Manual Handoff` | Registryをinstruction/indexとして利用する |

### 13.1 REQ-AI-017 Execution Status Monitoring

`REQ-AI-017 Execution Status Monitoring`を将来要求候補として記録する。目的はPrompt Registryの`Execution Status`をpolling、event、またはwebhookで監視し、`COMPLETED / BLOCKED / FAILED`等を次工程へ接続可能にすることである。

段階は次を想定する。

1. manual status handoff
2. polling
3. event / webhook-driven orchestration

現時点のStatusは`FUTURE_REQUIREMENT / NOT_IMPLEMENTED`であり、実装済みと扱わない。

## 14. Current known operational incident

初期運用で、Claude CodeをTargetとする`ARGUS-P-0003-v1`をCodexが取得した。CodexはTarget mismatchを正しく検出してPromptを実行しなかったが、対象Prompt rowへ`BLOCKED / TARGET_MISMATCH`を書き戻した。その後、Design Authorityがoperational correctionとしてP-0003を`NOT_RUN`へ復元した。

この事例から、Promptを読むauthorityとexecution/resultを書き込むauthorityを分離し、Target mismatch時に非Target Actorが対象Prompt rowを書き換えない規則を明文化した。

## 15. Development flow

argusの基本flowは次とする。

```text
Contract
→ Test
→ Implementation
→ Static Analysis
→ GREEN
→ CV / RV
→ Critical Path Review
→ Finding Disposition
→ Remediation / Close
```

Review feedbackは対象に応じて戻す。

- Implementation defect → Implementation
- Test defect / coverage gap → Test
- Spec ambiguity → Contract

TestとImplementation間のfeedbackはあり得るが、default directionは`Test → Implementation`である。

## 16. Scope boundary

本書はAI-assisted development governanceを定義し、次のdomain/runtime policy自体を再定義しない。

- investment decision policy
- portfolio / risk policy
- Environment Binding Contract
- Test Strategy
- Budget / Paid Service Governance
- runtime operational semantics

これらは各Canonical artifactを参照する。

## 17. Operational checklist

Promptを扱うActorは最低限次を確認する。

```text
Prompt ID取得
→ Target / Status / Approved By確認
→ repo Canonical artifact/hash確認
→ actor authority内で実行
→ Target ActorだけがResult系property更新
→ repo output path/hashをRegistryへ索引として記録
```

ReviewではさらにReview Input Manifest boundaryを確認する。新たなDesign判断が必要な場合はDesign Authorityへ返す。
