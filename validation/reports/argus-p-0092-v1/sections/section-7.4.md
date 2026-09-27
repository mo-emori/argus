## 7.4 変更管理

Breakを影響範囲別に分類し、具体的diff・再承認・Version切替へ拘束する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 守るべき原則

RV-01〜35はMVS成立後のRegression Setである。 変更階層、承認対象、Rollback境界が曖昧だと、Objectiveの自己正当化や事実履歴の巻戻しが起き得る。 変更後に成立済みCapabilityを再確認しないと、局所修正がState・Funds・Approval等の不変条件を破り得る。 現行Baselineと過去の変更履歴を混同すると、旧要件を現行仕様として再導入し得る。

### 停止と例外

| 観点 | 設計上の内容 |
|---|---|
| premises | RV-01〜35はMVS成立後のRegression Setである。 |
| problems | 変更階層、承認対象、Rollback境界が曖昧だと、Objectiveの自己正当化や事実履歴の巻戻しが起き得る。 ／ 変更後に成立済みCapabilityを再確認しないと、局所修正がState・Funds・Approval等の不変条件を破り得る。 ／ 現行Baselineと過去の変更履歴を混同すると、旧要件を現行仕様として再導入し得る。 |
| purposes | Breakを影響範囲別に分類し、具体的diff・再承認・Version切替へ拘束する。 ／ 変更影響に応じたAffected / Core / Full回帰集合で不変条件を検証する。 ／ 現行仕様に必要なVersion管理規則だけを保持する。 |
| processes | B1〜B4、Break Proposal、Human Approval、Rollback、System Version。 ／ ／ B1 Parameter ／ threshold、period、score、frequency ／ Human Approval、diff、試験 ／ ／ ／ B2 Component ／ Agent、Skill、Scanner、Watch module ／ 同上 ／ ／ ／ B3 Architecture ／ Workflow、Agent graph、System structure ／ 同上 ／ ／ ／ B4 Objective ／ Objective、評価関数、Risk / Return / Income / Human Load ／ 旧Objectiveを凍結保持し、新旧を並行測定後に再度Human Approval ／ ／ すべてのBreak Proposalはchange_id、対象版、完全diff、変更後hash、理由、期待効果、影響Strategy、試験計画、rollbackを持つ。 ／ RollbackはCode / Policy / 将来処理を対象とし、実約定、Cash、監査履歴を過去snapshotで上書きしない。 ／ §32〜35。 ／ RV-01〜35。 ／ ／ RV-01〜02 ／ TTLとExecution、重複、部分約定、取消 ／ 確認済みFactを受領し、二重計上せず予約整合 ／ ／ ／ RV-03〜04 ／ 同版競合、中断位置 ／ 一方だけCommit、旧版か新版で復旧、Log再生成 ／ ／ ／ RV-05〜06 ／ Cash競合、条件変更 ／ A確保後B保留、古い承認を流用しない ／ ／ ／ RV-07〜08 ／ BOOTSTRAP / REPAIR / SELL ／ 進捗取引許可、段階縮小、空売り拒否 ／ ／ ／ RV-09〜10 ／ Binding、Validator迂回 ／ 空Portfolioを作らず、偽PASSを拒否 ／ ／ ／ RV-11〜16 ／ Cash保存則、通知、枝欠損、Time Gate、`Change`、MVS ／ Fact・State・評価・全売却復元の整合 ／ ／ ／ RV-17〜22 ／ Command冪等、Stage、Budget、Runner、Restore、翌朝再検証 ／ 二重取得・再課金・危険再開・承認流用なし ／ ／ ／ RV-23〜29 ／ BUSY、Status競合、pre-submit、Storage、Deploy、Budget段階 ／ 時刻境界、Human優先、安全縮退、自動増額なし ／ ／ ／ RV-30 ／ Decision Correction ／ 未発注ApprovalをSupersedeしreservation解放 ／ ／ ／ RV-31 ／ Fact Correction ／ 旧Factを消さずappendしCurrent State再計算 ／ ／ ／ RV-32 ／ System Critical Override ／ ENABLED即時、DISABLED Queue、storm抑止 ／ ／ ／ RV-33 ／ 長期Human不在 ／ PAUSE / STOP、再開後Catch-up / reconciliation ／ ／ ／ RV-34 ／ Environment分離 ／ state_id / marker mismatchでcross-write拒否 ／ ／ ／ RV-35 ／ Historical Provider ／ as_of_time以降Dataを返さない ／ ／ §46B Regression Verification Set。 ／ 現行Design BaselineおよびCode / Schema / Policy / `Data` / Design version。 ／ §49、§52、Final Freeze。 |
| rules | 承認後にdiffまたは基準版が変われば再承認する。 ／ 通常変更はAffected RVとCore RV、Release / Paper Gate / Runtime・Schema・Provider・Governance重要変更前はFull RVを実行する。 ／  |
| prohibitions | NOT_RUNをPASSにしない。 |
| actors_authorities | Human |
| boundaries | ／ RV-23〜29 ／ BUSY、Status競合、pre-submit、Storage、Deploy、Budget段階 ／ 時刻境界、Human優先、安全縮退、自動増額なし ／ |
| 状態 | `BUSY` |

### 運用上の確認

Breakを影響範囲別に分類し、具体的diff・再承認・Version切替へ拘束する。 変更影響に応じたAffected / Core / Full回帰集合で不変条件を検証する。 現行仕様に必要なVersion管理規則だけを保持する。 B1〜B4、Break Proposal、Human Approval、Rollback、System Version。 ／ B1 Parameter ／ threshold、period、score、frequency ／ Human Approval、diff、試験 ／ ／ B2 Component ／ Agent、Skill、Scanner、Watch module ／ 同上 ／ ／ B3 Architecture ／ Workflow、Agent graph、System structure ／ 同上 ／ ／ B4 Objective ／ Objective、評価関数、Risk / Return / Income / Human Load ／ 旧Objectiveを凍結保持し、新旧を並行測定後に再度Human Approval ／ すべてのBreak Proposalはchange_id、対象版、完全diff、変更後hash、理由、期待効果、影響Strategy、試験計画、rollbackを持つ。 RollbackはCode / Policy / 将来処理を対象とし、実約定、Cash、監査履歴を過去snapshotで上書きしない。 §32〜35。 RV-01〜35。 ／ RV-01〜02 ／ TTLとExecution、重複、部分約定、取消 ／ 確認済みFactを受領し、二重計上せず予約整合 ／ ／ RV-03〜04 ／ 同版競合、中断位置 ／ 一方だけCommit、旧版か新版で復旧、Log再生成 ／ ／ RV-05〜06 ／ Cash競合、条件変更 ／ A確保後B保留、古い承認を流用しない ／ ／ RV-07〜08 ／ BOOTSTRAP / REPAIR / SELL ／ 進捗取引許可、段階縮小、空売り拒否 ／ ／ RV-09〜10 ／ Binding、Validator迂回 ／ 空Portfolioを作らず、偽PASSを拒否 ／ ／ RV-11〜16 ／ Cash保存則、通知、枝欠損、Time Gate、`Change`、MVS ／ Fact・State・評価・全売却復元の整合 ／ ／ RV-17〜22 ／ Command冪等、Stage、Budget、Runner、Restore、翌朝再検証 ／ 二重取得・再課金・危険再開・承認流用なし ／ ／ RV-23〜29 ／ BUSY、Status競合、pre-submit、Storage、Deploy、Budget段階 ／ 時刻境界、Human優先、安全縮退、自動増額なし ／ ／ RV-30 ／ Decision Correction ／ 未発注ApprovalをSupersedeしreservation解放 ／ ／ RV-31 ／ Fact Correction ／ 旧Factを消さずappendしCurrent State再計算 ／ ／ RV-32 ／ System Critical Override ／ ENABLED即時、DISABLED Queue、storm抑止 ／ ／ RV-33 ／ 長期Human不在 ／ PAUSE / STOP、再開後Catch-up / reconciliation ／ ／ RV-34 ／ Environment分離 ／ state_id / marker mismatchでcross-write拒否 ／ ／ RV-35 ／ Historical Provider ／ as_of_time以降Dataを返さない ／ §46B Regression Verification Set。 現行Design BaselineおよびCode / Schema / Policy / `Data` / Design version。 §49、§52、Final Freeze。 承認後にdiffまたは基準版が変われば再承認する。 通常変更はAffected RVとCore RV、Release / Paper Gate / Runtime・Schema・Provider・Governance重要変更前はFull RVを実行する。  NOT_RUNをPASSにしない。 Human ／ RV-23〜29 ／ BUSY、Status競合、pre-submit、Storage、Deploy、Budget段階 ／ 時刻境界、Human優先、安全縮退、自動増額なし ／
