# Argus Development Progress Map

## 1. 目的と権限

本書は、人間が読みやすいderived progress viewであり、Capability lifecycle stateのCanonical Sourceではない。Canonical stateは、参照先のrepository上のContract、Test、Baseline、Run、Evidence、Review、Approval artifactに裏付けられた`docs/development/argus_capability_registry.md`にある。

本MapとCanonical artifactが矛盾する場合は`Canonical Source wins`とし、本Mapを機械的に修正する。

CodexとClaude Codeは、Canonical artifactから機械的に確認できるObservationおよびDerived State、current step、completed step、missing artifact、blocking reason、next mechanically implied stepのみを更新できる。本Mapを通じてDesign judgment、Capability CLOSE、Finding disposition、Contractまたはlifecycle ruleの変更、Authority変更、CV/RVの意味的昇格を行ってはならない。

## 2. Lifecycle Map

```text
Contract
  ↓
Test / Oracle
  ↓
Baseline Freeze
  ↓
RED
  ↓
Implementation
  ↓
Static Analysis
  ↓
GREEN + Regression
  ↓
CV / RV as required
  ↓
Critical Path Review
  ↓
Canonical Review Artifact
  ↓
Finding Disposition
  └─ remediation required → GREEN / Regression → re-review
  ↓
Human CLOSE Approval
  ↓
CLOSED
```

各stageはCapabilityのCanonical ContractおよびTest Strategyに従って適用する。意味のないREDに対する承認済みexceptionなどが記録されていても、無関係なgateの省略を許可するものではない。

## 3. 凡例

- `✓` = `COMPLETE`
- `→` = `CURRENT / NEXT`
- `-` = `NOT_STARTED / WAITING`
- `×` = `FAILED / MISSING / BLOCKED`
- `!` = `ATTENTION`
- `N/A` = `NOT_APPLICABLE`

`-`と`N/A`は異なる。`-`は未着手または待機中、`N/A`は当該工程が適用対象外であることを示す。本Mapのみから正式なPASS/FAILを判定してはならない。

## 4. 現在のCapability概要

| Capability | Contract / Test | Baseline / RED | Implementation | Static / GREEN / Regression | CV / RV | Review / Disposition / Approval | State |
|---|---|---|---|---|---|---|---|
| `EB-L0-MARKER-JSON` | ✓ | ✓ | ✓ | ✓ | Canonical artifactを参照 | ✓ | `CLOSED` |
| `EB-L0-MARKER-JSON-REMAINDER` | ✓ | ✓（承認済みRED exception） | ✓ 既存behavior | ✓ | Canonical artifactを参照 | ✓ `NO_FINDING` | `CLOSED` |
| `EB-L0-ENVIRONMENT-BINDING-COMPARISON` | ✓ | ✓ | ✓ | ✓ | Canonical artifactを参照 | ✓ | `CLOSED` |
| `EB-L1-DATA-ROOT-MARKER-STORE` | ✓ | ✓ | ✓ | ✓ | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | ✓ Review `NO_FINDING`、Finding disposition完了、Human close approval `ARGUS-P-0007-v1` | `CLOSED` |
| `EB-L1-TEST-ENVIRONMENT-GUARD` | ✓ Contract / Frozen Test | ✓ Baseline / RED | ✓ Production | ✓ Canonical GREEN。Affected checks、Frozen 68件、Regression 215件PASS | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | ✓ Critical Path Review `NO_FINDING`、Finding 0、Human CLOSE approval | `CLOSED` |
| `RUNTIME-IDENTITY-DOCUMENT` | ✓ Exact Contract / → Test Code | - | - | - | `CV-44: PARTIAL`、`RV-34: NOT_RUN` | - | `IN_PROGRESS` |

現在地:

```text
Environment Binding

EB-L0-MARKER-JSON
    ✓ CLOSED

EB-L0-MARKER-JSON-REMAINDER
    ✓ CLOSED

EB-L0-ENVIRONMENT-BINDING-COMPARISON
    ✓ CLOSED

EB-L1-DATA-ROOT-MARKER-STORE
    ✓ CLOSED

EB-L1-TEST-ENVIRONMENT-GUARD
    ✓ CLOSED
    ✓ Contract clarification
    ✓ Frozen Test / Baseline / RED / Production
    ✓ Static Analysis governance correction
    ✓ GREEN再検証
    ✓ Claude Code Critical Path Review: NO_FINDING
    ✓ Human CLOSE approval: ARGUS-P-0019-v1
```

`EB-L1-TEST-ENVIRONMENT-GUARD`はP-0017でCanonical GREENを確定し、P-0018の独立Critical Path Reviewで`NO_FINDING`・Finding 0となった。`ARGUS-P-0019-v1`のDesign Authority decisionとHuman final approvalにより`CLOSED`へ遷移した。Repository Health debtとReview observationは`ARGUS-IMP-0008`、`ARGUS-IMP-0009`、`ARGUS-IMP-0010`で非blockerとして継続追跡する。Capability CLOSEはCV/RVの完了を意味せず、`CV-44 = PARTIAL`、`RV-34 = NOT_RUN`を維持する。

次のCapabilityは`ARGUS-DA-0003` / `ARGUS-P-0022-v1`により`RUNTIME-IDENTITY-DOCUMENT`へ確定した。`ARGUS-P-0023-v1`でL0 `bytes -> RuntimeIdentity | typed validation failure`のExact Contractと`RI-L0-001..028`を確定した。Test Code、Baseline、RED、Productionは未着手である。Runtime Foundationは`RUNTIME-IDENTITY-DOCUMENT`、`RUNTIME-CONFIG-MECHANISM`、`RUNTIME-ENTRY-RESOLUTION`、`RUNTIME-BOOTSTRAP-ORCHESTRATOR`の4段階とするが、後続3 Capabilityの詳細仕様は未確定である。

## 5. EB-L1 Data Root Marker Store完了詳細

- ✓ Production: `src/argus/runtime/data_root_marker_store.py` (`sha256:061441840efc089607e5275bb7ed94681cc0ddc3f81b01fa72c72667821427bb`)
- ✓ Frozen Test: `tests/component/test_data_root_marker_store_contract_v03.py` (`sha256:ca27771d111263190dfc28b0b9e633be82ca105ad8bdcf64743668a2c5d608a7`)
- ✓ Baseline: `validation/baselines/eb-l1-data-root-marker-store/EB-L1-DATA-ROOT-MARKER-STORE-v0.3.baseline.json` (`sha256:667159ef4c7ba3f7520ddfb02724f2ae367d592388dc72438a1d42ada30e83cb`)
- ✓ Final GREEN remediation run: `validation/runs/eb-l1-data-root-marker-store/RUN-EB-L1-DATA-ROOT-MARKER-STORE-GREEN-REMEDIATION-20260919T065317276800Z.run.json` (`sha256:fba3a5ef5d2690d0ba31f2ad2dda3810e8b0fef1676caa0d7e45c28fc295e94a`)
- ✓ Review Input Manifest: `validation/evidence/eb-l1-data-root-marker-store/CLAUDE-REVIEW-INPUT-EB-L1-DATA-ROOT-MARKER-STORE-REMEDIATION-20260919T065502999018Z/review-input-manifest.json` (`sha256:4b1dab880ee83b30d639f873cc33803efc66edb5a2a3d1980241b42c10a9a19d`)
- ✓ Canonical Review: `validation/evidence/eb-l1-data-root-marker-store/CLAUDE-REVIEW-20260919T173431371528Z/claude-review-record.json` (`sha256:a3e7f6789ed0bd5001483caeaf5f59d8230168e4bc1a430c820b6491979d5074`)
- ✓ Review provenance supplement: `validation/evidence/eb-l1-data-root-marker-store/CLAUDE-REVIEW-20260919T173431371528Z/claude-review-provenance-supplement.json` (`sha256:0d1c4c42b363e734c853bf7248c7c3da3316dde8536317465260aeefdeeaaf71`)
- ✓ `FINDING-01`: Canonical review artifactに記録されたとおり解消済み。
- ✓ `FINDING-02`: Canonical review artifactに記録されたcoverage extensionにより解消済み。
- ✓ `FINDING-03`: `RISK_ACCEPT`。改善は`BACKLOG_ONLY_NOT_STARTED`であり、Improvement Backlogで`OPEN`のまま。
- ✓ Human close approval: `ARGUS-P-0007-v1`。

工程欠落の履歴:

```text
Claude Review
    ↓
NO_FINDING
    ↓
Notion Result
    ↓
Canonical Review Artifact
    × MISSING
    ↓
P-0005 fail-closed
    ↓
P-0006 canonicalization
    ✓ COMPLETE
    ↓
P-0007 CLOSE
    ✓ COMPLETE
```

P-0005はCanonical Review Artifactの不足を検出し、Capabilityをfail-closedで停止した。P-0006がReview provenanceをCanonical化し、その後P-0007が`CV-44: PARTIAL`、`RV-34: NOT_RUN`、`FINDING-03`の意味を変更せずRegistryの`CLOSED` transitionを承認した。

## 6. 現在工程と次の工程

`→ RUNTIME-IDENTITY-DOCUMENT Test Code`

Exact Contractは`ACCEPTED FOR TEST DESIGN`であり、public API、error model、serialization、Acceptance Criteria、Test IDを確定済みである。次工程は`RI-L0-001..028`のTest Code作成とPre-RED Static Analysisである。Baseline Freeze、RED、Production implementationへはまだ進まない。CV-44は`PARTIAL`、RV-34は`NOT_RUN`を維持する。

## 7. 更新規律

- 本Mapの更新前にCapability Registryと参照先のCanonical artifactを確認する。
- Repository artifactから機械的に確認できる事実のみを更新する。
- CV/RV値を正確に維持し、PASSまたは完了を推測しない。
- 未着手または待機中は`-`、適用対象外は`N/A`、不足・失敗・blockは`×`、注意事項は`!`として記録し、完了として扱わない。
- Immediate issueとBacklogの判断基準およびCanonical authorityが要求しない限り、Backlog entryをblockerへ変更しない。
- Lifecycle historyを読みやすい別の物語へ置き換えず、実際のsequenceを追跡できるreferenceを維持する。
