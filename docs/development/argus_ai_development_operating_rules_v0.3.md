# ARGUS Development Operating Rules v0.3

**Document Type:** AI-assisted Development Governance
**Version:** `0.3`
**Status:** `ACTIVE`
**Canonical Location:** `docs/development/argus_ai_development_operating_rules_v0.3.md`
**Activation Date:** 2026-09-28
**Supersedes:** `v0.1`, `v0.2`

## 1. Purpose and authority

本書は、ARGUSのAI-assisted developmentにおけるauthority、instruction、execution、evidence、review、およびclosureの運用規則を定義するCanonical Sourceである。RepositoryのDesign Sourceが定義するsystem designを変更せず、開発作業の統制境界を定める。

### 1.1 Authority model

- **ChatGPT:** Design Authority participant、Agent Orchestrator、およびRegistry lifecycle recorder。design synthesis、contract/change planning、actor routing、evidence照合、Registry lifecycle記録を行う。単独でHuman approvalを代替しない。
- **Human:** Final Approval Authority。design、rule activation/supersession、必要なfinding disposition、paid service等の最終判断を行う。
- **Codex:** implementation、test、およびevidence actor。Design Authorityではなく、未承認のdesign判断またはcontract clarificationを行わない。
- **Claude Code:** read-only independent review/audit actor。対象artifactを修正せず、finding dispositionまたはclosureを決定しない。

### 1.2 Closure authority

ChatGPTはActorのself-reportだけを根拠にexecutionまたはartifactをcloseしてはならない。closureは、externally generated Result Manifest、Git evidence、およびrequired artifactを照合できる場合に限る。Human approvalが必要な状態はHuman承認前にcloseしない。

## 2. System-of-record and service roles

### 2.1 Local Repo / Git

Local Repo / Gitは、Design、Contract、Test Strategy、Frozen Test、Baseline、Production、Run定義、review artifact、finding disposition、および本RulesのSource of Truthである。

### 2.2 Notion

Notionは`Instruction / Registry / Human-facing Context`であり、Command Busではない。Prompt Registryはinstruction identity、approval、execution lifecycle、result indexを保持するが、repo artifactまたはexecution evidenceそのものを代替しない。

### 2.3 Slack

Slackは`Command / Result Bus`である。配送されたmessageはCanonical Sourceではなく、欠落、重複、再送を前提に、Prompt ID、Job ID、およびhashで照合する。

### 2.4 Local Worker

Local Workerは`Execution Bridge`である。Slackからgoverned commandを受け、検証後に対象Actorを起動し、Result Manifestを生成・返送する。Business/design authorityを持たない。Local WorkerはNotionを直接read/writeしてはならない。Registryのread/writeとlifecycle recordingはChatGPTが担う。

### 2.5 Google Drive

Google Driveは`Artifact Store / Delivery`であり、Source of Truthではない。通常の成果物配送または明示されたartifact保管に使用できるが、repo/Gitのcanonical stateを上書きしない。

### 2.6 Local Execution Log

Local Execution Logは一次execution evidenceであり、repo-externalかつgit-excludedとする。default pathは **`C:\dev\chatgpt-agent\logs\<job_id>\`** であり、repo-relative pathではない。詳細は§19.1を参照する。Local Execution Logは通常のGoogle Drive Artifactに含めない。明示的なreviewまたはincident handoffが必要な場合だけ、秘匿情報を除去した限定artifactを別途生成する。

### 2.7 Conversation memory

Conversation memoryとActor self-reportはCanonical Sourceでも一次execution evidenceでもない。後続工程に必要なinstruction、decision、state、evidence、およびprovenanceは所定のsystem of recordへ外出しする。

## 3. Prompt Registry model

現行モデルでは、**1 Registry row = 1 execution record** とする。retryは同じrowの再実行ではなく、新しいPrompt Registry rowと未使用のJob IDを作成する。

各rowは少なくとも次のpropertyを持つ。

- Prompt ID
- Job ID
- Project
- Capability
- Target
- Type
- Status
- Version
- Created By
- Approved By
- **Prompt SHA-256**
- **Baseline Commit**
- Execution Status
- Artifact Status
- Result
- Executed By
- Result Summary
- Output Ref
- Executed At
- Result Manifest Ref
- Result Manifest SHA-256
- Required Artifacts
- Produced Artifacts
- **Rejected Artifacts**
- Review / Finding Ref
- Supersedes / Retry Of

Propertyの意味、source field、および更新主体は§20のCanonical Result Manifest → Registry mappingに従う。§20にない推測変換を行ってはならない。

### 3.1 Instruction Status

`Status`はinstruction validityを表し、`DRAFT / APPROVED / SUPERSEDED`を使用する。`APPROVED`にはHuman approvalを必要とする。

### 3.2 Execution Status

`Execution Status`はcommand executionの状態を表し、少なくとも`NOT_RUN / RUNNING / COMPLETED / BLOCKED / FAILED`を使用する。

### 3.3 Artifact Status

`Artifact Status`はrequired artifactの検証状態を表し、少なくとも`NOT_ASSESSED / COMPLETE / PARTIAL / REJECTED / MISSING`を使用する。Execution StatusとArtifact Statusは独立したfailure domainである。processの正常終了はartifact completenessを意味せず、artifactの存在はexecution successを意味しない。

## 4. Execution identity and immutability

- Prompt IDは`Instruction Identity`である。
- Job IDは`Execution Identity`である。
- `job_id`は一度割り当てたら、成功、失敗、取消、timeoutの別を問わず再利用しない。
- `APPROVED`後のPrompt本文、Prompt SHA-256、approval metadata、およびBaseline Commitはimmutableとする。
- instruction変更またはretryには新しいrow、新しいJob ID、および必要に応じ新しいPrompt versionを作る。
- historical rowとrejected artifact referenceは監査履歴として保持する。

## 5. Approval and target routing gate

ChatGPTはdispatch前、WorkerはActor invocation前に、Project、Target、`Status=APPROVED`、Human approval、Prompt ID、未使用Job ID、Baseline Commit、§7のPrompt SHA-256 chain、required input、およびactor authorityをfail-closedで検証する。不成立時はActorを起動せず、対象rowを非Target Actorのself-reportで変更しない。

## 6. Protocol v1 JOB envelope

Governed ARGUS Agent executionの`JOB` messageは少なくとも次を含む。

```text
protocol_version = 1
project = ARGUS
prompt_id = <instruction identity>
job_id = <unique execution identity>
target = <Codex | Claude Code | other approved actor>
prompt_sha256 = <64 lowercase hexadecimal characters>
baseline_commit = <Git commit SHA>
```

ARGUSでは`prompt_sha256`は**MUST**である。欠落、形式不正、またはRegistry値との不一致を許容してはならない。非ARGUS互換運用を別scopeで定義してもよいが、その互換規則によってARGUSのMUSTまたはfail-closed behaviorを弱めてはならない。

## 7. Governed prompt hash chain

Governed ARGUS Agent executionでは、次の値が同一でなければならない。

```text
Prompt Registry Prompt SHA-256
= Protocol v1 JOB prompt_sha256
= Local Workerが正規Prompt bytesから計算・検証したSHA-256
= Result Manifest prompt_sha256
```

Prompt RegistryへのPrompt SHA-256保存は**MUST**である。ChatGPTはdispatch前にRegistry値を確認し、WorkerはActor invocation前に実測値を確認し、ChatGPTはclosure前にResult Manifest値を再照合する。hashの欠落、非64桁lowercase hexadecimal、またはいずれかの不一致は、**Actor invocation前にfail closed**とする。Actorが既に起動されたことが判明した場合、executionを正常完了扱いにせずincidentとして扱う。Hash対象bytesのcanonicalizationが一意に決まらない場合も推測せず停止する。

## 8. Actor boundaries

### 8.1 Codex

Codexは承認済みboundary内でimplementation、test、およびevidence生成を行う。Canonical Sourceの曖昧さ、新たなdesign judgment、contract clarification、approval不足を検知した場合は停止してChatGPTへ返す。CodexはClaude Codeを直接launchしてはならない。

```text
Codex → Result / Evidence → ChatGPT → optional Human → Claude Code
```

### 8.2 Claude Code

Claude Codeはindependent review/auditをread-onlyで行う。review対象のProduction、Frozen Test、Contract、Test Strategy、evidenceを変更せず、findingをChatGPTへ返す。

### 8.3 ChatGPT and Human

ChatGPTはactor routing、Registry lifecycle recording、cross-artifact verificationを担う。HumanはFinal Approval Authorityを維持する。ChatGPTもHuman approvalを自己生成してはならない。

## 9. Registry access boundary

通常のLocal Agent operationでは、Codex、Claude Code、およびLocal WorkerはPrompt Registryを直接read/writeしてはならない。ChatGPTがRegistryから承認済みinstructionを取得・検証し、Slack経由でJOBをdispatchし、Result Manifestとartifact evidenceに基づいてRegistryを更新する。manual fallbackでもHumanまたはChatGPTが同等のverified envelopeを渡し、ActorへRegistry credentialを付与しない。

## 10. Command and result transport

Slackはat-least-once deliveryや順序入替を想定する。WorkerはJob IDでduplicateを検出し、同じJob IDを別executionへ再利用しない。transport acknowledgement、Actor process exit、およびgovernance closureを同一視しない。ResultはResult Manifestを中心に返し、大きなartifactはrepo path/Git objectまたは承認済みArtifact Store referenceで参照する。

## 11. Result write authority and lifecycle recording

ActorはLocal Execution Logおよび自身に許可されたworkspace artifactを生成できるが、Prompt Registryを更新しない。ChatGPTはResult Manifest、Git evidence、required artifactを検証した後にRegistry lifecycleを記録する。Registry correctionはprovenanceを残す明示的な管理操作に限り、Prompt本文、hash、approval metadata、Job ID、Baseline Commitを暗黙に変更してはならない。

## 12. Review isolation

Critical Path ReviewはReview Input Manifestでboundaryをfreezeする。reviewerはManifest外変更を暗黙に追加せず、Test PASSをContract complianceの十分条件とせず、Contract、Production、Frozen Test coverage、Result Manifest、およびGit evidenceを独立に比較する。reviewer自身はfinding dispositionを確定しない。

```text
Review → ChatGPT → optional Human disposition
       → remediation / risk acceptance / clarification / close
```

## 13. Artifact acceptance and rejection

Required artifactは、存在、path、digest、producer、Job ID、Prompt ID、Baseline Commit、および必要なschemaを検証する。検証不能または境界外artifactは`Rejected Artifacts`へ理由とともに記録し、accepted artifactとして扱わない。Rejected artifactを削除して履歴を消してはならず、再生成は新Job IDで行う。

## 14. Closure gate

ChatGPTはverified Result Manifest、identity/hash/baseline一致、Git evidenceまたはno-change evidence、required artifactsと個別Artifact Status、required validation results、未解決finding/rejected artifact/blocked condition、および必要なHuman approvalが揃うまでclosureしない。Actor self-report、process exit code、Slack message、またはtest summary単独ではclosure evidenceにならない。

## 15. Fail-closed conditions

少なくとも、target/approval/identity/baselineの欠落・不一致、Prompt hashの欠落・形式不正・不一致、Job ID再利用、Canonical Source ambiguity、未承認design judgment、Review Input Manifest mismatch、required evidence不足、TEST/PAPER/LIVE境界違反、禁止されたRegistry access、authority外write、有料service追加要求では停止する。

## 16. Manual fallback

Notion、Slack、Worker、connectorの一部が利用不能でもrepo/GitのCanonical Sourceをconversation memoryへ移さない。HumanまたはChatGPTは、Prompt ID、unique Job ID、approved prompt bytes/hash、Target、Baseline Commitを含むclosed envelopeを手動で渡せる。fallback executionも同じhash chain、Result Manifest、evidence、Registry lifecycle rulesに従う。

## 17. Development and review flow

```text
Design discussion → Human approval → Prompt Registry record
→ ChatGPT verification/dispatch → Worker pre-invocation gate
→ Actor execution → Result Manifest + Local Execution Log + Git/artifacts
→ ChatGPT verification → optional independent review / Human decision
→ separate Execution Status and Artifact Status recording → close
```

実装flowの基本順序は`Contract → Test → Implementation → Static Analysis → GREEN → CV/RV → Critical Path Review → Finding Disposition → Remediation/Close`とする。

## 18. Retry, recovery, and duplicate handling

retryは常に新しいRegistry rowと新しいJob IDを作成し、`Retry Of`で先行executionを参照する。先行rowの結果を上書きしない。duplicate JOBはActorを再起動せず、既存Job IDのlogとresult stateを照合してChatGPTへ返す。partial execution、timeout、transport failure、artifact rejectionはExecution StatusとArtifact Statusへ独立して反映する。

## 19. Evidence storage

### 19.1 Local Execution Log layout

Default rootはrepo外の`C:\dev\chatgpt-agent\logs\<job_id>\`とする。最低限、受信JOB envelope、preflight検証結果、Actor invocation metadata、stdout/stderrまたは同等記録、exit information、Result Manifest、artifact digest/indexを追跡可能にする。credential、token、不要なsecretを記録しない。このdirectoryはARGUS repoにcopy/commitせず、通常のDrive Artifactにも送らない。必要な証拠は最小化・redactした派生artifactとして明示的に作る。

### 19.2 Git and artifact evidence

変更を伴うexecutionではBaseline Commit、resulting commitまたはworking-tree diff evidence、changed paths、validation結果を記録する。既存のunrelated changeをActor成果としてclaimしない。no-change executionではその旨と検証根拠をManifestへ記録する。

## 20. Canonical Result Manifest → Registry mapping

Result ManifestはActor self-reportではなくLocal Workerがexecution境界で生成・確定する。Actor出力はManifestへのinputになり得るが、ActorがManifestのverified fieldsを自己承認しない。

| Result Manifest field | Registry property | Rule |
|---|---|---|
| `prompt_id` | Prompt ID | exact match |
| `job_id` | Job ID | exact match; never reused |
| `target` / `executed_by` | Target / Executed By | approved targetと実Actorを別々に記録 |
| `prompt_sha256` | Prompt SHA-256 | §7のchainとexact match |
| `baseline_commit` | Baseline Commit | approved baselineとexact match |
| `execution_status` | Execution Status | artifact statusから独立して記録 |
| `artifact_status` | Artifact Status | execution statusから独立して記録 |
| `result_code` | Result | controlled valueを転記 |
| `summary` | Result Summary | evidenceを過大表示しない要約 |
| `finished_at` | Executed At | Worker観測時刻を使用 |
| `manifest_ref` / `manifest_sha256` | Result Manifest Ref / SHA-256 | immutable evidence reference |
| `produced_artifacts[]` | Produced Artifacts / Output Ref | path/refとdigestを保持 |
| `rejected_artifacts[]` | Rejected Artifacts | reasonを保持しaccepted outputへ混入させない |
| `required_artifacts[]` | Required Artifacts | completeness判定の母集団 |
| `validation[]` | Result Summary / linked evidence | raw evidence refを保持 |

mapping対象fieldが欠落、malformed、またはRegistryのimmutable fieldと不一致なら、ChatGPTはclosureせず`BLOCKED`または`FAILED`の適切な状態とartifact findingを記録する。値を推測して補完しない。

## 21. Historical versions and rule change model

本書v0.3のactivationにより、**v0.1とv0.2はいずれもhistorical version**となり、active ruleとして使用しない。両versionは監査・lineageのため削除または上書きせずhistoryとして保持する。Repositoryに存在しないhistorical artifactを推測で再作成してはならず、所在不明は明示する。旧文書のheaderに残る当時の`ACTIVE`表記はhistorical metadataであり、現在のactivation stateを示さない。

rule changeは`design discussion → Human approval → new version artifact → activation instruction`の順とする。Prompt Registry内のRULE rowはactivation/adoption instructionであり、Canonical Rule本文ではない。

## 22. Current normal Local Agent rule

現在の通常Local Agent operationでは、次を必須境界とする。

- Codex、Claude Code、Local WorkerはPrompt Registryを直接read/writeしない。
- ChatGPTがPrompt Registry lifecycle recorderとしてinstructionを取得・検証し、result evidenceを照合して更新する。
- NotionをCommand Busとして使用しない。SlackをCommand / Result Busとして使用する。
- WorkerはActor invocation前にapproval、target、identity、baseline、およびprompt hashをfail-closedで検証する。
- Actorはauthority内のrepo/artifact作業だけを行う。

この規則は、非Target Actorによるmismatch writeだけを禁止する旧規則より強い。通常運用におけるActor/WorkerのPrompt Registry直接readも直接writeも禁止する。

## 23. Historical target-mismatch incident

初期運用で、Claude CodeをTargetとする`ARGUS-P-0003-v1`をCodexが取得した。CodexはTarget mismatchを検出してPromptを実行しなかったが、対象Prompt rowへ`BLOCKED / TARGET_MISMATCH`を書き戻した。その後、Design Authorityがoperational correctionとして`NOT_RUN`へ復元した。

この事例は、Promptを読むauthorityとexecution/resultを書くauthorityを分離し、非Target Actorが対象rowを変更してはならないことを示した。ただし、これは現在の規則の一部にすぎない。**現在の通常Local Agent operationでは§22のより強い規則が適用され、Codex、Claude Code、およびLocal WorkerによるPrompt Registryの直接read/write自体を禁止する。**

## 24. Scope boundary and operational checklist

本書はAI-assisted development governanceを定義し、investment policy、portfolio/risk policy、Environment Binding Contract、Test Strategy、runtime semanticsを再定義しない。自動Broker発注、有料service追加、TEST/PAPER/LIVE混在を許可しない。

```text
Human-approved instruction
→ Registry Prompt SHA-256 / Baseline Commit確認
→ unique Job ID発行
→ Protocol v1 JOB dispatch
→ Worker hash/preflight gate
→ Actor execution
→ Worker Result Manifest + Local Execution Log
→ ChatGPT Manifest/Git/artifact verification
→ independent Execution Status / Artifact Status recording
→ optional review / required Human approval
→ auditable closure
```
