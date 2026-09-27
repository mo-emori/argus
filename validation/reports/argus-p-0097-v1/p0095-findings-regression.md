# P0095 Findings Regression Review

## 総合判定

**PASS**

P0095の`major-chapter-3.md`およびP0096の回帰レビューで定義されたR-01〜R-06を、assembled本文に対して意味単位で再評価した。R-01〜R-06はすべてPASSであり、既知findingの回帰はない。固定templateとの文面一致は判定条件にしていない。

## Regression matrix

| ID | 判定 | assembled本文の証拠 | 回帰評価 |
|---|---|---|---|
| R-01 User Status | **PASS** | 3.4の状態軸表は`FREE / NORMAL / BUSY`を人が直接操作する値として定義し、`human_capacity`の入力であってConfigurationではないと分離する。更新表は`StatusChangeCommand`、`user_status.json`、`status_version`、直接編集禁止、version競合時の旧変更破棄を保持する。 | P0095の人操作、内部capacity入力、独立保存・更新境界を維持し、弱化していない。 |
| R-02 Workflow | **PASS** | 3.4の更新表はQueue / Approval / Order / Reservation / Watchを生成元、実行制御を利用先とし、Proposal / Order / Incident等を独立状態として保持する。 | 一つの状態への統合や履歴縮約はなく、P0095のWorkflow境界を維持する。 |
| R-03 Configuration | **PASS** | 3.4は`config.json`を人が明示する動作規則の単一正本とし、version/hashとJob開始時immutable snapshotを要求する。格納内容にruntime、model、budget、notification、portfolio / risk policy、strategy等を列挙し、Secret値、User Status、Domain Stateを除外する。 | P0095の単一正本、利用範囲、snapshot不変性および情報分離を維持する。 |
| R-04 Runtime Identity | **PASS** | 3.4は`state_id / environment / data_root_id`等の不変Identityを保持し、path、drive letter、Budget、Secret、Status、Domain / Runtime State、plan tier、code pathを禁止する。解決不能時は通常起動しない。 | P0095のIdentity境界を維持し、禁止対象とfail-closed動作を具体化している。 |
| R-05 Secret非露出境界 | **PASS** | 3.4のSecret行は取得元をEnvironment Variable / OS-protected store、利用主体を使用Subsystemとし、Secret値をproject、config、log、evidence、report、backupへ格納しない。漏出の疑いでAdapter停止と`SECURITY_INCIDENT`を要求する。3.5はApplication LogへのSecret / Credential / Token / API key / Authorization header / 未redact debug dumpを禁止し、Backup snapshotへの平文Secretを禁止する。 | project通常ファイルと、log・evidence・report・backupを横断する非露出境界、Application / Audit系Artifactの分離、Backup平文禁止、漏出疑い時fail-closedをすべて復元できる。P0096で欠けていた横断境界は回復している。 |
| R-06 3.5 Artifact固有条件 | **PASS** | 3.5は保存対象10群、Authority表、Application Logの未確定事項、Backup媒体責務、`last_local_backup_at` / `last_external_backup_at`、Restore / Reconciliation手順、Data Rootと容量・形式条件を具体化する。旧空要素に続く実意味であるApplication Log未確定事項とBackup配置・監視規則も本文に存在する。 | 3.5はもはやcontext-insufficientではない。非空意味を推測補完せず、SDD-L1159〜L1165相当およびSDD-L1294〜L1295相当を含む全66 Coverage意味が残る。 |

## R-05重点確認

Secret境界は単なるConfiguration / Runtime Identity分離に留まらない。3.4で通常project保存とconfig、log、evidence、report、backupへの格納を横断禁止し、3.5でApplication Logの具体的な秘密情報種別と未redact dumpを禁止し、Backupでは平文格納を禁止する。さらに漏出の「疑い」の段階でAdapter停止と`SECURITY_INCIDENT`を要求するため、非露出と事故時のfail-closedの双方が復元可能である。

## R-06重点確認

P0096で`NOT_RUN — CONTEXT_INSUFFICIENT`となった二つの領域は解消している。

- Application Log: 生成主体、Writer責務、書込み経路、retention期間、cleanup / deletion、crash直前durability、最低限識別情報、partition / path、追加masking範囲、filename / format / schema / libraryを未確定のまま列挙する。
- Backup: 内蔵SSDの直近N世代、外付けHDDの長期Backup、N未確定、`last_local_backup_at`と`last_external_backup_at`の個別監視を保持する。

加えて、3.5 semantic gateが対象とした66件は本文から復元でき、空ラベルそのものを意味要素として誤評価していない。Artifact固有の生成元、利用先、保持条件、禁止、復旧条件、Formal Identifierおよび設計参照に欠落はない。

## 結論

- PASS: R-01、R-02、R-03、R-04、R-05、R-06
- FAIL / NOT_RUN: なし

既知findingの回帰は検出しなかったため、Regression reviewはPASSとする。初回Assembly reviewで検出されたhash証跡の算出不一致は、実ファイルbytes基準へ修正され、再検証で解消済みである。
