## 2.5 売買と売買結果

Broker上の確定事実と整合するまでOrder状態と資源予約を保持する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 守るべき原則

未解決OrderのSlotやreservationをTTL・停止だけで解放すると、同じ資源を別Tradeへ二重割当し得る。 Brokerで成立した事実をProposalの有効性判定と混同すると、TTL失効やPolicy変更を理由に現実の約定を失い得る。 Broker上の確定事実と整合するまでOrder状態と資源予約を保持する。 事実受領とCompliance評価を分離し、PortfolioをBroker現実へ一致させる。

### 停止と例外

| 観点 | 設計上の内容 |
|---|---|
| problems | 未解決OrderのSlotやreservationをTTL・停止だけで解放すると、同じ資源を別Tradeへ二重割当し得る。 ／ Brokerで成立した事実をProposalの有効性判定と混同すると、TTL失効やPolicy変更を理由に現実の約定を失い得る。 |
| purposes | Broker上の確定事実と整合するまでOrder状態と資源予約を保持する。 ／ 事実受領とCompliance評価を分離し、PortfolioをBroker現実へ一致させる。 |
| processes | Order状態、execution_slot、BUY費用予約、SELL数量予約。 ／ ／ AWAITING_SUBMISSION ／ 承認後、Broker未操作 ／ execution_slotとBUY最大支払額＋費用余裕またはSELL数量を保持 ／ ／ ／ ORDER_OPEN ／ Brokerへ発注済み ／ Slot・残予約を保持 ／ ／ ／ PARTIALLY_FILLED ／ 一部約定 ／ FactごとにPosition / Cash / 残予約更新 ／ ／ ／ CANCEL_PENDING ／ 取消依頼、未確定 ／ 予約を解放しない ／ ／ ／ FILLED ／ 全約定 ／ 累計数量照合後に終了処理 ／ ／ ／ CANCELLED / REJECTED ／ Broker確定 ／ 全約定累計と取消数量を照合して残予約解放 ／ ／ ／ UNKNOWN ／ 状況不明 ／ TTLや停止だけでSlot / reservationを解放しない ／ ／ §5、§13.3、§25。 ／ Broker結果原文、Execution Fact、Compliance Record、Reconciliation状態。 ／ ／ 1 ／ ARGUS ／ Fact Ingress ／ RUNNING中のBroker結果原文 ／ receipt_id、received_at、content hash付きでinboxへDurable保存 ／ 受領済み原文 ／ Parse / Validate ／ 非RUNNING時は実行可能状態でないErrorとして拒否する。通知時間外でもRUNNING中なら受領応答を返す ／ ／ ／ 2 ／ ARGUS ／ Parser / Validator ／ inbox原文 ／ account、instrument、side、quantity、price、currency、executed_at / timezone、broker IDsを決定論的検査 ／ 確認済みFact候補または照合待ち ／ Fact Commit ／ 矛盾・方向不明は推測しない ／ ／ ／ 3 ／ ARGUS ／ Canonical Writer ／ 確認済みExecution ／ Fact Eventへ変換しSingle Writer Commit ／ Portfolio / Cash / Order更新 ／ Compliance評価 ／ 重複IDは冪等化する ／ ／ ／ 4 ／ ARGUS ／ 未確定 ／ Factと元Proposal / Approval ／ Compliance処理：TTL、承認内容、発注条件との差を評価 ／ Compliance Record ／ 表示 ／ 逸脱しても確認済みFactを拒否しない ／ ／ ／ 5 ／ ARGUS ／ Human Interface ／ receipt / commit / reconciliation状態 ／ 受領済み、適用済み、照合待ちを区別 ／ 状態表示 ／ 必要時Reconciliation ／ 同値だけで別約定を重複扱いしない ／ ／ §12。 |
| rules |  ／  |
| abnormal_handling | 矛盾・方向不明は`RECONCILIATION_REQUIRED`とし、推測適用しない。 |
| actors_authorities | Human ／ ARGUS ／ Broker |
| 状態 | `RUNNING` ／ `UNKNOWN` |

### 運用上の確認

Order状態、execution_slot、BUY費用予約、SELL数量予約。 ／ AWAITING_SUBMISSION ／ 承認後、Broker未操作 ／ execution_slotとBUY最大支払額＋費用余裕またはSELL数量を保持 ／ ／ ORDER_OPEN ／ Brokerへ発注済み ／ Slot・残予約を保持 ／ ／ PARTIALLY_FILLED ／ 一部約定 ／ FactごとにPosition / Cash / 残予約更新 ／ ／ CANCEL_PENDING ／ 取消依頼、未確定 ／ 予約を解放しない ／ ／ FILLED ／ 全約定 ／ 累計数量照合後に終了処理 ／ ／ CANCELLED / REJECTED ／ Broker確定 ／ 全約定累計と取消数量を照合して残予約解放 ／ ／ UNKNOWN ／ 状況不明 ／ TTLや停止だけでSlot / reservationを解放しない ／ §5、§13.3、§25。 Broker結果原文、Execution Fact、Compliance Record、Reconciliation状態。 ／ 1 ／ ARGUS ／ Fact Ingress ／ RUNNING中のBroker結果原文 ／ receipt_id、received_at、content hash付きでinboxへDurable保存 ／ 受領済み原文 ／ Parse / Validate ／ 非RUNNING時は実行可能状態でないErrorとして拒否する。通知時間外でもRUNNING中なら受領応答を返す ／ ／ 2 ／ ARGUS ／ Parser / Validator ／ inbox原文 ／ account、instrument、side、quantity、price、currency、executed_at / timezone、broker IDsを決定論的検査 ／ 確認済みFact候補または照合待ち ／ Fact Commit ／ 矛盾・方向不明は推測しない ／ ／ 3 ／ ARGUS ／ Canonical Writer ／ 確認済みExecution ／ Fact Eventへ変換しSingle Writer Commit ／ Portfolio / Cash / Order更新 ／ Compliance評価 ／ 重複IDは冪等化する ／ ／ 4 ／ ARGUS ／ 未確定 ／ Factと元Proposal / Approval ／ Compliance処理：TTL、承認内容、発注条件との差を評価 ／ Compliance Record ／ 表示 ／ 逸脱しても確認済みFactを拒否しない ／ ／ 5 ／ ARGUS ／ Human Interface ／ receipt / commit / reconciliation状態 ／ 受領済み、適用済み、照合待ちを区別 ／ 状態表示 ／ 必要時Reconciliation ／ 同値だけで別約定を重複扱いしない ／ §12。   矛盾・方向不明は`RECONCILIATION_REQUIRED`とし、推測適用しない。 Human ARGUS Broker
