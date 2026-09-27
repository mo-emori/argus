## 3.6 Deployment

Job開始時snapshotと変更適用境界を固定する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 状態の読み方

Job途中でConfigurationが変わると、同一Runの判断条件と費用上限を再現できない。 分析機能を安全基盤より先に実装したり、DeploymentでState / Config / Dataを上書きしたりすると、検証不能なRuntimeが成立し得る。 稼働中更新や部分置換は、State破損、Schema不整合、復旧不能を引き起こし得る。 Job開始時snapshotと変更適用境界を固定する。 Authority・Cost・State integrity・Recoveryを先行させ、停止・Backup・Schema確認を伴う配備順を固定する。 Runtime停止、Backup、Code置換、Schema確認を順序化して安全に配備する。

### 遷移と関係

| 観点 | 設計上の内容 |
|---|---|
| problems | Job途中でConfigurationが変わると、同一Runの判断条件と費用上限を再現できない。 ／ 分析機能を安全基盤より先に実装したり、DeploymentでState / Config / Dataを上書きしたりすると、検証不能なRuntimeが成立し得る。 ／ 稼働中更新や部分置換は、State破損、Schema不整合、復旧不能を引き起こし得る。 |
| purposes | Job開始時snapshotと変更適用境界を固定する。 ／ Authority・Cost・State integrity・Recoveryを先行させ、停止・Backup・Schema確認を伴う配備順を固定する。 ／ Runtime停止、Backup、Code置換、Schema確認を順序化して安全に配備する。 |
| processes | Config version/hash、運用中変更、Budget limit低下。 ／ ／ Job単位snapshot ／ 全Job ／ Job開始時 ／ 検証済みimmutable snapshotを取得し、Run / Stage / Decisionへversion/hashを記録 ／ 実行途中へ新Configを動的注入しない ／ Job開始を拒否またはCONFIG_REQUIRED ／ §4.0 ／ ／ ／ Config変更境界 ／ 運用中Job ／ 人がConfig変更 ／ 次Jobから有効化 ／ 実行中Jobの条件を暗黙変更しない ／ 旧snapshotで当該Job完了 ／ §4.0 ／ ／ ／ Limit低下 ／ Budget reservation ／ 新limitが既存reservation未満 ／ 既存予約を維持し新規reservation停止 ／ 既存予約を暗黙取消しない ／ `LIMIT_BELOW_EXISTING_RESERVATION`表示 ／ §4.0 ／ ／ v0.1.7着手順、手動Deployment、Version lineage。 ／ Dev code、Runtime code、Migration、Validation、Backup、Runtime process。 ／ ／ 1 ／ 人 ／ 未確定 ／ Dev code ／ 実装・試験 ／ Acceptance / CV判定 ／ 候補版 ／ FAILならDeployしない ／ Runtime停止 ／ ／ ／ 2 ／ 人 / ARGUS ／ Runner ／ RUNNING Runtime ／ Graceful Exit ／ END ／ lock解放 ／ crashなら次回起動時RESUMING ／ Backup ／ ／ ／ 3 ／ ARGUS ／ Backup Job ／ State / Config ／ Snapshot ／ 復旧可能性確認 ／ Backup ／ 失敗をCommit成功と混同しない ／ app置換 ／ ／ ／ 4 ／ 人 ／ Deployment mechanism（詳細未確定） ／ Runtime `app/` ／ Code置換 ／ State / Config / Data非上書き ／ 新app ／ 部分更新禁止 ／ Schema確認 ／ ／ ／ 5 ／ ARGUS ／ Migration / Validation component ／ Code要求Schema、State Schema ／ version照合、必要時Migration ／ MIGRATION_REQUIREDまたはvalid ／ Migration audit ／ 不一致ならRunner開始しない ／ Restart ／ ／ 自動download、self-replace、自動rollbackは初期必須ではない。 ／ §4.6。 |
| rules | SYSTEM_VERSION、CONFIG_SCHEMA_VERSION、STATE_SCHEMA_VERSIONを分離する。 |
| actors_authorities | ARGUS |
| boundaries | ／ Config変更境界 ／ 運用中Job ／ 人がConfig変更 ／ 次Jobから有効化 ／ 実行中Jobの条件を暗黙変更しない ／ 旧snapshotで当該Job完了 ／ §4.0 ／ |
| 状態 | `END` ／ `RESUMING` ／ `RUNNING` |

### 不整合時の扱い

Config version/hash、運用中変更、Budget limit低下。 ／ Job単位snapshot ／ 全Job ／ Job開始時 ／ 検証済みimmutable snapshotを取得し、Run / Stage / Decisionへversion/hashを記録 ／ 実行途中へ新Configを動的注入しない ／ Job開始を拒否またはCONFIG_REQUIRED ／ §4.0 ／ ／ Config変更境界 ／ 運用中Job ／ 人がConfig変更 ／ 次Jobから有効化 ／ 実行中Jobの条件を暗黙変更しない ／ 旧snapshotで当該Job完了 ／ §4.0 ／ ／ Limit低下 ／ Budget reservation ／ 新limitが既存reservation未満 ／ 既存予約を維持し新規reservation停止 ／ 既存予約を暗黙取消しない ／ `LIMIT_BELOW_EXISTING_RESERVATION`表示 ／ §4.0 ／ v0.1.7着手順、手動Deployment、Version lineage。 Dev code、Runtime code、Migration、Validation、Backup、Runtime process。 ／ 1 ／ 人 ／ 未確定 ／ Dev code ／ 実装・試験 ／ Acceptance / CV判定 ／ 候補版 ／ FAILならDeployしない ／ Runtime停止 ／ ／ 2 ／ 人 / ARGUS ／ Runner ／ RUNNING Runtime ／ Graceful Exit ／ END ／ lock解放 ／ crashなら次回起動時RESUMING ／ Backup ／ ／ 3 ／ ARGUS ／ Backup Job ／ State / Config ／ Snapshot ／ 復旧可能性確認 ／ Backup ／ 失敗をCommit成功と混同しない ／ app置換 ／ ／ 4 ／ 人 ／ Deployment mechanism（詳細未確定） ／ Runtime `app/` ／ Code置換 ／ State / Config / Data非上書き ／ 新app ／ 部分更新禁止 ／ Schema確認 ／ ／ 5 ／ ARGUS ／ Migration / Validation component ／ Code要求Schema、State Schema ／ version照合、必要時Migration ／ MIGRATION_REQUIREDまたはvalid ／ Migration audit ／ 不一致ならRunner開始しない ／ Restart ／ 自動download、self-replace、自動rollbackは初期必須ではない。 §4.6。 SYSTEM_VERSION、CONFIG_SCHEMA_VERSION、STATE_SCHEMA_VERSIONを分離する。 ARGUS ／ Config変更境界 ／ 運用中Job ／ 人がConfig変更 ／ 次Jobから有効化 ／ 実行中Jobの条件を暗黙変更しない ／ 旧snapshotで当該Job完了 ／ §4.0 ／
