## 3.3 中断・再開

Runtimeの通常系と異常終了後の起動時復旧を簡潔な状態機械として固定する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 状態の読み方

初期化、通常実行、異常終了後の復旧、正常終了を混同すると、不明な正本での再開やCrashの状態化が起き得る。 Schedule時刻と経過時間を同じClockで扱うと、Sleepや時計変更後のDue判定を誤り得る。

### 遷移と関係

| 観点 | 設計上の内容 |
|---|---|
| problems | 初期化、通常実行、異常終了後の復旧、正常終了を混同すると、不明な正本での再開やCrashの状態化が起き得る。 ／ Schedule時刻と経過時間を同じClockで扱うと、Sleepや時計変更後のDue判定を誤り得る。 |
| purposes | Runtimeの通常系と異常終了後の起動時復旧を簡潔な状態機械として固定する。 ／ Wall Clockとmonotonic clockの用途を分離し、復帰後Catch-upを成立させる。 |
| processes | Runnerの`INIT / RUNNING / RESUMING / END`状態。 ／ ／ INIT ／ Identity・Binding・Schema・Lock検証成功、前回正常終了 ／ Runner lock取得、通常実行準備 ／ RUNNING ／ 正本不明等はFail Closedで起動失敗 ／ §4.2、§4.3 ／ ／ ／ INIT ／ 前回の正常終了を確認できない ／ 復旧対象を特定 ／ RESUMING ／ OS kill / crash自体は状態にしない ／ §4.2、§4.3 ／ ／ ／ RESUMING ／ lock、inbox、outbox、Stage、Commitの復旧・照合成功 ／ Due / Gap / Queueを再評価 ／ RUNNING ／ 復旧不能時はIncident化して起動失敗 ／ §4.2、§4.3、§13.2 ／ ／ ／ RUNNING ／ Exit要求 ／ 新規Job受付停止、実行中処理を安全点またはDurable Stageへ退避、flush、lock解放 ／ END ／ Crash時はENDへ遷移せず、次回INITで検出 ／ §4.3 ／ ／ Schedule、timeout、retry、clock discontinuity、last_success、cursor。 ／ ／ Schedule、Due、Market calendar ／ timezone付きWall Clock、`Asia/Tokyo` ／ Sleep中の予定時刻通過を復帰後に検出する ／ ／ ／ wait、timeout、retry interval ／ monotonic clock ／ OS時計変更の影響を避ける ／ ／ ／ 時計・timezoneの大幅変更 ／ Wall Clock観測 ／ `CLOCK_DISCONTINUITY`を記録しDue Jobを再評価する ／ ／ ／ 停止期間の復帰 ／ `last_success` / cursor / inbox ／ RUN / REANALYZE / EXPIRE / MERGE / DROPをFreshnessとTTLにより決める ／ ／ §2.4、§2.6、§26、§42A。 |
| 状態 | `END` ／ `INIT` ／ `INIT / RUNNING / RESUMING / END` ／ `RESUMING` ／ `RUNNING` |

### 不整合時の扱い

Runtimeの通常系と異常終了後の起動時復旧を簡潔な状態機械として固定する。 Wall Clockとmonotonic clockの用途を分離し、復帰後Catch-upを成立させる。 Runnerの`INIT / RUNNING / RESUMING / END`状態。 ／ INIT ／ Identity・Binding・Schema・Lock検証成功、前回正常終了 ／ Runner lock取得、通常実行準備 ／ RUNNING ／ 正本不明等はFail Closedで起動失敗 ／ §4.2、§4.3 ／ ／ INIT ／ 前回の正常終了を確認できない ／ 復旧対象を特定 ／ RESUMING ／ OS kill / crash自体は状態にしない ／ §4.2、§4.3 ／ ／ RESUMING ／ lock、inbox、outbox、Stage、Commitの復旧・照合成功 ／ Due / Gap / Queueを再評価 ／ RUNNING ／ 復旧不能時はIncident化して起動失敗 ／ §4.2、§4.3、§13.2 ／ ／ RUNNING ／ Exit要求 ／ 新規Job受付停止、実行中処理を安全点またはDurable Stageへ退避、flush、lock解放 ／ END ／ Crash時はENDへ遷移せず、次回INITで検出 ／ §4.3 ／ Schedule、timeout、retry、clock discontinuity、last_success、cursor。 ／ Schedule、Due、Market calendar ／ timezone付きWall Clock、`Asia/Tokyo` ／ Sleep中の予定時刻通過を復帰後に検出する ／ ／ wait、timeout、retry interval ／ monotonic clock ／ OS時計変更の影響を避ける ／ ／ 時計・timezoneの大幅変更 ／ Wall Clock観測 ／ `CLOCK_DISCONTINUITY`を記録しDue Jobを再評価する ／ ／ 停止期間の復帰 ／ `last_success` / cursor / inbox ／ RUN / REANALYZE / EXPIRE / MERGE / DROPをFreshnessとTTLにより決める ／ §2.4、§2.6、§26、§42A。
