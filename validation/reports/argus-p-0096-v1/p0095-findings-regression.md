# P0095 Findings Regression Review

## 総合判定

**FAIL**

生成後の最終 `section-3.4.md` を、accepted比較対象 `work/argus-p-0090-v1/section-3.4.md` と照合した。R-01〜R-04はPASS、R-05はFAILであり、P0090に存在したSecret非露出の安全境界が部分的に回帰している。R-06はSection 3.5のContext不足が明示されているためNOT_RUNとし、内容を推測していない。

本レビューは回帰判定のみであり、本文の修正または承認を行わない。

## Regression matrix

| ID | 判定 | 現行Section 3.4の根拠 | P0090安全境界回帰 |
|---|---|---|---|
| R-01 User Status | PASS | 行63に生成・更新主体 `StatusChangeCommand`、保持先 `user_status.json`、`status_version`、直接編集を通常操作にしない禁止境界が同一行で明記されている。 | **なし。** P0090の「人が直接変更する」「内部処理余力を導く入力」より具体的な更新経路・保持識別子・直接編集禁止が保持されている。 |
| R-02 Workflow | PASS | 行67にWorkflowの生成元としてQueue / Approval / Order / Reservation / Watch、利用先として実行制御、保持条件としてProposal / Order / Incident等の独立状態を明記している。 | **なし。** Proposal、Order、Incidentを一つの状態へ統合せず、独立状態として保持する境界が復元可能。 |
| R-03 Configuration | PASS | 行62に利用先 `Job、Policy、Budget、通知等`、`config.json`を単一正本とする規則、`version/hash`、Job開始時のimmutable snapshotを明記している。行50も人が明示する動作規則の単一正本と記載する。 | **なし。** P0090のJob / Policy / Budget / 通知、単一正本、version / hash、開始後snapshot不変の安全境界を維持。 |
| R-04 Runtime Identity | PASS | 行61に `state_id / environment / data_root_id`を保持し、path / Secret / Status / Domain Stateを入れないと明記。行51にDeployment Identity / Run Identity / path / 設定値との分離を明記している。 | **なし。** P0090のSecret・人の状態・Domain State除外を保持し、他Identityとの分離も明示。 |
| R-05 Secret非露出境界 | FAIL | 行50・61はSecretをConfigurationおよびRuntime Identityから分離・除外するだけである。Canonical State、Projection、Application Log、Audit Log、Report、BackupへのSecret非露出を包括的に禁止していない。行46のBackupは「非正本」というAuthority境界だけで、Secret非露出やBackup平文禁止ではない。 | **あり。** P0090は「秘密情報は正本、Projection、Log、Report、Backupのいずれにも露出させない」と明示していたが、現行本文ではこの横断的禁止が消失。さらに要求されたApplication / Audit Logの明示的範囲とBackup平文禁止も復元不能。 |
| R-06 3.5 Artifact固有条件 | NOT_RUN | `section-3.5-context-insufficient.md` はSDD-L1158およびSDD-L1293の `original_text` 欠落により、要求・制約・責任主体・状態遷移・復旧条件を決定できず、3.5本文生成を中止すると明記している。 | **判定しない。** Context不足下でArtifact固有条件を推測すると新規意味を導入するため、回帰有無も評価不能。 |

## Finding detail

### R-05 — Blocking regression

P0090 accepted本文に存在したのは、Secretの格納主体を一つ分離するだけの規則ではなく、正本と派生・監査・保存Artifactを横断する非露出境界である。現行本文から確定できるのは次の二点に限られる。

- ConfigurationはSecretと分離する。
- Runtime IdentityにSecretを入れない。

これらから、Canonical State、Projection、Application Log、Audit Log、Report、BackupにSecretを露出してよいとはいえないが、露出禁止であるとも本文だけでは復元できない。また、Backupを非正本とする記述は、Backupへの平文Secret保存禁止を含意しない。したがってR-05をPASSへ推測拡張することはできず、FAILとする。

## R-06 execution status

**NOT_RUN — CONTEXT_INSUFFICIENT**

SDD-L1158とSDD-L1293の具体的意味が欠けているため、3.5のArtifact固有条件は評価していない。周辺Unit、P0090、または一般的な復旧設計からの補完も行っていない。

## Conclusion

- PASS: R-01, R-02, R-03, R-04
- FAIL: R-05
- NOT_RUN: R-06

R-05にP0090安全境界の回帰があるため、Regression reviewの総合判定はFAIL。
