# Argus Capability Registry

## 1. 目的と権限

本Registryは、ArgusのCapability lifecycle stateを記録するrepository上のCanonical Sourceである。Notion、conversation、Development Progress Mapは本書を索引・要約できるが、Capability stateを決定しない。

ここで参照する事実については、CanonicalなImplementation、Test、Baseline、Run、Evidence、Review、Approval artifactが引き続き正本である。本Registryとそれらが矛盾する場合はtransitionを停止し、該当するDesign AuthorityおよびHuman approval processを通じて整合させる。

## 2. Capability state

有効なstateは次の4つに限定する。

- `NOT_STARTED`: 承認されたCapability implementation cycleが開始されていない。
- `IN_PROGRESS`: 承認されたlifecycleが進行中だが、CapabilityはすべてのCLOSE条件を満たしていない。
- `BLOCKED`: 記録されたblockerが解消されるまで、安全または権限上の理由により作業を進められない。
- `CLOSED`: すべてのCLOSE条件を満たし、Human final approvalが記録されている。

許可するtransition:

- `NOT_STARTED -> IN_PROGRESS`
- `IN_PROGRESS -> BLOCKED`
- `BLOCKED -> IN_PROGRESS`
- `IN_PROGRESS -> CLOSED`

`CLOSED` Capabilityのreopenは本versionでは未定義である。reopen transitionを推測してはならない。

## 3. CLOSE条件

Capabilityは、適用される次の条件をすべて満たした場合にのみ`CLOSED`へtransitionできる。

1. Production implementationが完了している。
2. Frozen capability testがGREENである。
3. 必須regression testがGREENである。
4. 必須static analysisがPASSである。
5. 適用対象の場合、Critical Path Reviewが完了している。
6. Review適用対象の場合、Canonical review artifactが存在する。
7. すべてのFindingに承認されたdispositionがある。
8. 未解決のCLOSE blockerがない。
9. 必要な場合、Design Authority judgmentが記録されている。
10. Human final approvalが記録されている。

`CLOSED`は、CV PASS、RV PASS、または当該subsystem全体の完了を意味しない。CVとRVは、それぞれ独立して記録された意味とstateを維持する。

## 4. 現在状態

| Capability ID | State | Current Gate / Note | Final or Current Run | Review Reference | CV / RV | Updated At | Approval |
|---|---|---|---|---|---|---|---|
| `EB-L0-MARKER-JSON` | `CLOSED` | Frozen GREEN、Finding disposition完了 | `validation/runs/eb-l0-marker-json/RUN-EB-L0-MARKER-JSON-GREEN-20260916T121757244856Z.run.json` (`sha256:8c09b983e0b7ca3792abe60df8fc0f0d03f149f1bf4a7860f07c02596073b91a`) | `validation/evidence/eb-l0-marker-json/CLAUDE-REVIEW-20260916T121229817000Z/claude-review-record.json` (`sha256:d518a8998d6971881abf80ce1d4572307d24fc07bdb341a0d96a1ebbcdb5b1a6`) | Canonical Run/Review artifactを参照 | `2026-09-19T17:42:45.165598Z` | CanonicalなCLOSED Evidenceに基づく遡及的な初期登録 |
| `EB-L0-MARKER-JSON-REMAINDER` | `CLOSED` | Regression/Contract coverage GREEN、Review `NO_FINDING` | `validation/runs/eb-l0-marker-json-remainder/RUN-EB-L0-MARKER-JSON-REMAINDER-GREEN-20260916T123518536352Z.run.json` (`sha256:5c3da4dd54276d2047160864701fd0ab47f7ba24c9babe2b118084cb75c56000`) | `validation/evidence/eb-l0-marker-json-remainder/CLAUDE-REVIEW-20260916T125001559000Z/claude-review-record.json` (`sha256:beb11c22812606385b8fbe20014221e4be66227e9b087246135b6caf11845e4d`) | Canonical Run/Review artifactを参照 | `2026-09-19T17:42:45.165598Z` | CanonicalなCLOSED Evidenceに基づく遡及的な初期登録 |
| `EB-L0-ENVIRONMENT-BINDING-COMPARISON` | `CLOSED` | GREEN、Canonical review provenance完備 | `validation/runs/eb-l0-environment-binding-comparison/RUN-EB-L0-ENVIRONMENT-BINDING-COMPARISON-GREEN-20260916T141624467677Z.run.json` (`sha256:cb0c01dec2d5f711c7b8b444a0506e90d39db700de390ef25a8c214462174a15`) | `validation/evidence/eb-l0-environment-binding-comparison/CLAUDE-REVIEW-20260917-DATE-ONLY-f983e36d/claude-review-provenance-supplement.json` (`sha256:d139aae182e076aaefd228cfee4aaa9d37ce230ee85310e36771aad1da47f6cf`) | Canonical Run/Review artifactを参照 | `2026-09-19T17:42:45.165598Z` | CanonicalなCLOSED Evidenceに基づく遡及的な初期登録 |
| `EB-L1-DATA-ROOT-MARKER-STORE` | `CLOSED` | Critical Path Review `NO_FINDING`、全Finding disposition完了、CLOSE blockerなし | `validation/runs/eb-l1-data-root-marker-store/RUN-EB-L1-DATA-ROOT-MARKER-STORE-GREEN-REMEDIATION-20260919T065317276800Z.run.json` (`sha256:fba3a5ef5d2690d0ba31f2ad2dda3810e8b0fef1676caa0d7e45c28fc295e94a`) | `validation/evidence/eb-l1-data-root-marker-store/CLAUDE-REVIEW-20260919T173431371528Z/claude-review-record.json` (`sha256:a3e7f6789ed0bd5001483caeaf5f59d8230168e4bc1a430c820b6491979d5074`)、provenance supplement `sha256:0d1c4c42b363e734c853bf7248c7c3da3316dde8536317465260aeefdeeaaf71` | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | `2026-09-19T17:42:45.165598Z` | `ARGUS-P-0007-v1`によるHuman approval |
| `EB-L1-TEST-ENVIRONMENT-GUARD` | `CLOSED` | GREEN完了、Critical Path Review `NO_FINDING`、Finding 0、CLOSE blockerなし | GREEN Run `validation/runs/eb-l1-test-environment-guard/RUN-EB-L1-TEST-ENVIRONMENT-GUARD-GREEN-20260920T063252867000Z.run.json` (`sha256:3796c74d6e9ecfbdabf0ea3726eae2779575540665115813de37c6c5aa591bab`) | `validation/evidence/eb-l1-test-environment-guard/CLAUDE-REVIEW-20260920T072749103158Z/claude-review-record.json` (`sha256:06e6bfc4c4dc63d0c42e5195a41eff17a51d2e11f45a6c0c52dab82889e8fcbc`) | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | `2026-09-20T07:47:13.151205Z` | Design Authority decision + `ARGUS-P-0019-v1` Human approval |
| `RUNTIME-IDENTITY-DOCUMENT` | `IN_PROGRESS` | Exact Contract `ACCEPTED FOR TEST DESIGN`。`RI-L0-001..028`確定、次工程はTest Code。Baseline/RED/Production未着手 | N/A | `ARGUS-DA-0003` / `ARGUS-P-0022-v1` / `ARGUS-P-0023-v1` | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | `2026-09-20T12:09:55.4677120Z` | `ARGUS-P-0023-v1` (`Approved By: Human`) |

### 4.1 EB-L1-TEST-ENVIRONMENT-GUARD CLOSE record

- Decision: `EB-L1-TEST-ENVIRONMENT-GUARD = CLOSED`
- Authority: Design Authority decision, based on ChatGPT design discussion and Human final approval
- Human approval: `ARGUS-P-0019-v1` (`Approved By: Human`)
- Contract: `docs/contracts/argus_environment_binding_contract_v0.1.md` (`sha256:90171ac4a5a0c3940cd4198515f89655b674e7b3aa5a5b7dcb293f698317fa8a`)
- Frozen Test: `tests/component/test_test_environment_guard_contract.py` (`sha256:a7fb71fb79a7cd8a4eed6be0e3beb7cf1c6728e136ef3cbc9caa4fb4692659ea`)
- Frozen Baseline: `validation/baselines/eb-l1-test-environment-guard/EB-L1-TEST-ENVIRONMENT-GUARD-v0.1.baseline.json` (`sha256:4d670ef4da00dc449b3ffef72c3eff3b521bef2603b014dbab881e66de2b2b0c`)
- `validation_baseline_hash`: `sha256:edee7a51c7406d412b7e844d2a2456f655282dc54ceda5ef5f91966308dca800`
- Formal RED Run: `RUN-EB-L1-TEST-ENVIRONMENT-GUARD-RED-20260920T053610824318Z` (`sha256:2566effbd2c049b9d9efeb617a09fa3d606b52bd550be7145f399f492c938a5e`)
- Production: `src/argus/runtime/environment_guard.py` (`sha256:ad3ffc07402d2b305ff200b8b4a7814f0e62f1ab510e3f4aeaff1f73f004954a`)
- Canonical GREEN Run: `RUN-EB-L1-TEST-ENVIRONMENT-GUARD-GREEN-20260920T063252867000Z` (`sha256:3796c74d6e9ecfbdabf0ea3726eae2779575540665115813de37c6c5aa591bab`)
- Critical Path Review: `validation/evidence/eb-l1-test-environment-guard/CLAUDE-REVIEW-20260920T072749103158Z/claude-review-record.json` (`sha256:06e6bfc4c4dc63d0c42e5195a41eff17a51d2e11f45a6c0c52dab82889e8fcbc`)
- Review result: `NO_FINDING`; Finding count: `0`
- Close timestamp: `2026-09-20T07:47:13.151205Z`
- Nonblocking backlog: `ARGUS-IMP-0008`, `ARGUS-IMP-0009`, `ARGUS-IMP-0010`; TBD-24 remains unresolved
- Capability CLOSE does not promote `CV-44` or `RV-34`: `CV-44 = PARTIAL`, `RV-34 = NOT_RUN`

`EB-L1-DATA-ROOT-MARKER-STORE`の`FINDING-03`は、backlog status `BACKLOG_ONLY_NOT_STARTED`を伴う`RISK_ACCEPT`のままである。これは`CV-44`または`RV-34`を昇格させず、関連する改善が実装済みであることも意味しない。

## 5. Transition History

本節はappend-orientedである。後の判断を表現するために既存transitionを書き換えず、新しい承認済みtransitionを追記する。

| Timestamp | Capability ID | From | To | Reason | Evidence | Authority | Human Approval |
|---|---|---|---|---|---|---|---|
| `2026-09-19T17:42:45.165598Z` | `EB-L0-MARKER-JSON` | `IN_PROGRESS` | `CLOSED` | 既存のCanonicalなCLOSED Evidenceから遡及的にRegistryへ初期登録。実際のCLOSEは本Registry作成前 | 現在状態で参照したFinal GREEN RunおよびReview record | 既存のCanonical close artifact | Canonical artifactに記録された既存close approval |
| `2026-09-19T17:42:45.165598Z` | `EB-L0-MARKER-JSON-REMAINDER` | `IN_PROGRESS` | `CLOSED` | 既存のCanonicalなCLOSED Evidenceから遡及的にRegistryへ初期登録。実際のCLOSEは本Registry作成前 | 現在状態で参照したFinal GREEN RunおよびReview record | 既存のCanonical close artifact | Canonical artifactに記録された既存close approval |
| `2026-09-19T17:42:45.165598Z` | `EB-L0-ENVIRONMENT-BINDING-COMPARISON` | `IN_PROGRESS` | `CLOSED` | 既存のCanonicalなCLOSED Evidenceから遡及的にRegistryへ初期登録。実際のCLOSEは本Registry作成前 | 現在状態で参照したFinal GREEN RunおよびReview provenance | 既存のCanonical close artifact | Canonical artifactに記録された既存close approval |
| `2026-09-19T17:42:45.165598Z` | `EB-L1-DATA-ROOT-MARKER-STORE` | `IN_PROGRESS` | `CLOSED` | GREEN remediation検証済み、Critical Path Reviewを`NO_FINDING`としてCanonical化済み、Finding disposition完了、HumanがCLOSEを承認 | Production `src/argus/runtime/data_root_marker_store.py` (`sha256:061441840efc089607e5275bb7ed94681cc0ddc3f81b01fa72c72667821427bb`)、Frozen Test `tests/component/test_data_root_marker_store_contract_v03.py` (`sha256:ca27771d111263190dfc28b0b9e633be82ca105ad8bdcf64743668a2c5d608a7`)、Baseline `validation/baselines/eb-l1-data-root-marker-store/EB-L1-DATA-ROOT-MARKER-STORE-v0.3.baseline.json` (`sha256:667159ef4c7ba3f7520ddfb02724f2ae367d592388dc72438a1d42ada30e83cb`)、上記GREEN RunおよびReview artifact、Review Input Manifest `sha256:4b1dab880ee83b30d639f873cc33803efc66edb5a2a3d1980241b42c10a9a19d` | 承認済みPromptに示されたDesign Authority judgment。Codexは機械的なRegistry更新を実施 | `ARGUS-P-0007-v1` (`Approved By: Human`) |
| `2026-09-19T18:06:26.9540321Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `NOT_STARTED` | `IN_PROGRESS` | EB-L1-020..027の正式なTest / Oracle / Baseline / RED準備を開始 | Environment Binding Contract `sha256:027a826cc21ea4d2b05622fa767f1c748d87a2bec1a752a3b71eab5a73c7212c`、Test Strategy `sha256:290d25aec71f6c3a89b1183873894235c7179d14298dc9ec5533213c3730778c` | `ARGUS-P-0009-v1`によるHuman-approved transition | `ARGUS-P-0009-v1` (`Approved By: Human`) |
| `2026-09-19T18:06:26.9540321Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `IN_PROGRESS` | `BLOCKED` | EB-L1-020..027のbehavior概要とfail-closed条件は定義済みだが、Frozen Testが直接使用するstartup guard / Writer guardのpublic API、result model、Writer instanceへのtoken拘束interfaceが未定義。Test側で仕様を推測できない | Contract §5.2、§8、§9.4、§9.5。Productionにはguard symbolなし。Frozen Test、Baseline、RED Evidenceは未作成 | Canonical Source ambiguityのためCodexがfail-closed。Design Authority clarificationが必要 | 開始承認は`ARGUS-P-0009-v1`。CLOSE authorityなし |
| `2026-09-20T05:07:57.8730377Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `BLOCKED` | `IN_PROGRESS` | Design Authority決定によりAuthorization frameworkとWriter-instance拘束を採用せず、fresh write-boundary verificationとWindows lexical path containmentへContractを再構成。EB-L1-020..027をExact Oracle化可能 | Environment Binding Contract `sha256:c37471bfc8b955a28be45088d234a48fc13937f5bed77a09f055d65857d77426`。Frozen Test、Baseline、RED Evidence、Productionは未変更 | `ARGUS-P-0012-v1`によるHuman-approved clarification and resume | `ARGUS-P-0012-v1` (`Approved By: Human`) |
| `2026-09-20T06:16:27.304000Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `IN_PROGRESS` | `BLOCKED` | P-0015でProduction/Frozen Test/Regressionとaffected static analysisは成功したが、repo-wide Pyrightがsuperseded immutable Store Testの既知7 diagnosticsを検出。P-0016でAffected GateとRepository Healthを分離し、7件をknown debtへ分類したが、別PromptのGREEN再検証前のためBLOCKEDを維持 | P-0015 verification attempt `validation/evidence/eb-l1-test-environment-guard/RUN-EB-L1-TEST-ENVIRONMENT-GUARD-GREEN-20260920T055856057133Z/green-verification-attempt.json` (`sha256:38d85be3678014618eb6600631a034cdfc0aee46bbd116ae458e3d3ff194b51d`)、Test Strategy §24.1.2、Backlog `ARGUS-IMP-0008` | `ARGUS-P-0016-v1`によるHuman-approved governance correction | `ARGUS-P-0016-v1` (`Approved By: Human`) |
| `2026-09-20T06:34:37.847989Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `BLOCKED` | `IN_PROGRESS` | P-0016後のStatic Analysis governanceで新規GREEN再検証が成立。Current Gateは全PASS、Repository Healthの既知7 diagnosticsは件数・severity・rule・scope非悪化 | GREEN Run `validation/runs/eb-l1-test-environment-guard/RUN-EB-L1-TEST-ENVIRONMENT-GUARD-GREEN-20260920T063252867000Z.run.json`、known debt `ARGUS-IMP-0008` | `ARGUS-P-0017-v1`によるHuman-approved GREEN re-verification | `ARGUS-P-0017-v1` (`Approved By: Human`) |
| `2026-09-20T07:47:13.151205Z` | `EB-L1-TEST-ENVIRONMENT-GUARD` | `IN_PROGRESS` | `CLOSED` | Contract、Frozen Test/Baseline、Formal RED、Production、Canonical GREENを確認し、Critical Path Review `NO_FINDING`・Finding 0、未解決CLOSE blockerなし | §4.1 CLOSE record、Canonical GREEN Run、Claude review record | Design Authority decision, based on ChatGPT design discussion and Human final approval | `ARGUS-P-0019-v1` (`Approved By: Human`) |
| `2026-09-20T11:54:57.5246999Z` | `RUNTIME-IDENTITY-DOCUMENT` | `NOT_STARTED` | `IN_PROGRESS` | DA-0003の承認済み判断により、Runtime Foundationを4段階へ整理し、最小L0 CapabilityのContract designを開始。Exact Oracleは未確定 | `docs/contracts/argus_runtime_identity_document_contract_v0.1.md`、`ARGUS-DA-0003` | Design Authority decision canonicalized by `ARGUS-P-0022-v1` | `ARGUS-P-0022-v1` (`Approved By: Human`) |
