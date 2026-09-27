## 4.3 費用・利用量

有料Serviceの有効化とModel Callを事前承認・Budget reservation・Hard Gateで統制する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 守るべき原則

Model API費用は観測指標だけでなく実行前Hard Gateとして扱い、有料Service全般をHuman Approval下に置く。 課金条件・上限・Fallbackが暗黙だと、Human承認なしの費用Commitment拡大が起き得る。

### 停止と例外

| 観点 | 設計上の内容 |
|---|---|
| premises | Model API費用は観測指標だけでなく実行前Hard Gateとして扱い、有料Service全般をHuman Approval下に置く。 |
| problems | 課金条件・上限・Fallbackが暗黙だと、Human承認なしの費用Commitment拡大が起き得る。 |
| purposes | 有料Serviceの有効化とModel Callを事前承認・Budget reservation・Hard Gateで統制する。 |
| processes | Paid Service Governance、Budget Policy、Model Call、Budget reservation。 ／  ／ ／ paidかつ有効なのにhuman_approval_refがない ／ Configuration Validation Error ／ 有料Serviceを開始しない ／ ／ ／ Pricing不明・上限見積不能 ／ `COST_ESTIMATE_UNAVAILABLE` ／ 対象Model Callを開始しない ／ ／ ／ いずれかのBudget階層を超過 ／ `BUDGET_EXCEEDED` ／ 対象Callを開始せず、新規探索・候補分析・通常Breakを停止する ／ ／ per-call / per-job、per-run、daily、monthlyの全階層を実行前Hard Gateとし、estimated_max_costをreserveして実usageで精算する。 ／ 使用率閾値の候補は70% NOTICE、85% WARNING、95% CRITICAL、100% BUDGET_EXCEEDED。 ／ §24.3、§37A〜37B。 |
| rules |  |
| prohibitions |  |
| actors_authorities | Human |
| 正確値 | `70%` ／ `85%` ／ `95%` ／ `100%` |

### 運用上の確認

有料Serviceの有効化とModel Callを事前承認・Budget reservation・Hard Gateで統制する。 Paid Service Governance、Budget Policy、Model Call、Budget reservation。  ／ paidかつ有効なのにhuman_approval_refがない ／ Configuration Validation Error ／ 有料Serviceを開始しない ／ ／ Pricing不明・上限見積不能 ／ `COST_ESTIMATE_UNAVAILABLE` ／ 対象Model Callを開始しない ／ ／ いずれかのBudget階層を超過 ／ `BUDGET_EXCEEDED` ／ 対象Callを開始せず、新規探索・候補分析・通常Breakを停止する ／ per-call / per-job、per-run、daily、monthlyの全階層を実行前Hard Gateとし、estimated_max_costをreserveして実usageで精算する。 使用率閾値の候補は70% NOTICE、85% WARNING、95% CRITICAL、100% BUDGET_EXCEEDED。 §24.3、§37A〜37B。   Human
