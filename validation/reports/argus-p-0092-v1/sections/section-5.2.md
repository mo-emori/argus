## 5.2 Humanの対応状態

Human loadを制御しながら、Durableな判断・通知経路を維持する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 状態の読み方

人の処理能力、通知可能時間、Proposal validity、Incident解決状態を混同すると、通知過多または重大案件の消失が起き得る。 人の状態とSystem内部capacityを同一視すると、人の意思に反する自動遷移や処理量制御が起き得る。

### 遷移と関係

| 観点 | 設計上の内容 |
|---|---|
| problems | 人の処理能力、通知可能時間、Proposal validity、Incident解決状態を混同すると、通知過多または重大案件の消失が起き得る。 ／ 人の状態とSystem内部capacityを同一視すると、人の意思に反する自動遷移や処理量制御が起き得る。 |
| purposes | Human loadを制御しながら、Durableな判断・通知経路を維持する。 ／ Human入力のStatusから内部capacityを一方向に導出し、通知・処理量を制御する。 |
| processes | Status、Capacity、Queue、Incident、Alert、Notification。 ／ `FREE / NORMAL / BUSY`、`LARGE / MEDIUM / SMALL`、BUSY Lease。 ／ ／ FREE ／ LARGE ／ 新規BUY、ADD、SELL、Allocation、Break、通常Watch ／ 特記なし ／ ／ ／ NORMAL ／ MEDIUM ／ Position Watch、有力Candidate、BUY / SELL、重要ADD、重大Break ／ 低優先提案 ／ ／ ／ BUSY ／ SMALL ／ Position Watch、重大Risk、Thesis崩壊、重大SELL、配当Core監視 ／ 新規探索、通常Break、通常Candidate通知 ／ ／ 通知可否、通知時間帯、priority、Overrideは§8.5〜8.7のNotification Policyに従い、本節では再定義しない。BUSYという理由だけで通常通知を即時配送せず、BUSY専用の重大Risk Email通知を新設しない。 ／ §21〜23。 |
| rules |  |
| actors_authorities | Human |
| 状態 | `BUSY` ／ `FREE` ／ `FREE / NORMAL / BUSY` ／ `LARGE` ／ `LARGE / MEDIUM / SMALL` ／ `MEDIUM` ／ `NORMAL` ／ `SMALL` |

### 不整合時の扱い

Human loadを制御しながら、Durableな判断・通知経路を維持する。 Human入力のStatusから内部capacityを一方向に導出し、通知・処理量を制御する。 Status、Capacity、Queue、Incident、Alert、Notification。 `FREE / NORMAL / BUSY`、`LARGE / MEDIUM / SMALL`、BUSY Lease。 ／ FREE ／ LARGE ／ 新規BUY、ADD、SELL、Allocation、Break、通常Watch ／ 特記なし ／ ／ NORMAL ／ MEDIUM ／ Position Watch、有力Candidate、BUY / SELL、重要ADD、重大Break ／ 低優先提案 ／ ／ BUSY ／ SMALL ／ Position Watch、重大Risk、Thesis崩壊、重大SELL、配当Core監視 ／ 新規探索、通常Break、通常Candidate通知 ／ 通知可否、通知時間帯、priority、Overrideは§8.5〜8.7のNotification Policyに従い、本節では再定義しない。BUSYという理由だけで通常通知を即時配送せず、BUSY専用の重大Risk Email通知を新設しない。 §21〜23。  Human
