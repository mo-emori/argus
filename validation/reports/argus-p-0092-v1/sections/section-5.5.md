## 5.5 Incidentと復旧

問題の検知、認知、解決、再通知をDurableな状態遷移として管理する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 状態の読み方

Proposalの失効や通知認知をIncident解決とみなすと、未解決問題が消失する。

### 遷移と関係

| 観点 | 設計上の内容 |
|---|---|
| problems | Proposalの失効や通知認知をIncident解決とみなすと、未解決問題が消失する。 |
| purposes | 問題の検知、認知、解決、再通知をDurableな状態遷移として管理する。 |
| processes | IncidentのOPEN、ACKNOWLEDGED、RESOLVED状態。 ／ ／ 未生成 ／ 問題検知 ／ incident_id、dedup_key、review情報を記録 ／ OPEN ／ 必要ならProposal / Alert生成 ／ Proposal TTLとは独立 ／ §24.1 ／ ／ ／ OPEN ／ 人が認知 ／ acknowledged_atを記録 ／ ACKNOWLEDGED ／ 再通知規則を再評価 ／ 認知を承認・注文・解決とみなさない ／ §24.1 ／ ／ ／ OPEN / ACKNOWLEDGED ／ 対応不要の証拠と解決理由が成立 ／ resolved理由を記録 ／ RESOLVED ／ 関連Proposalを再評価 ／ Proposal失効だけでは遷移しない ／ §24.1 ／ ／ ／ OPEN / ACKNOWLEDGED ／ next_review_at到来、未応答P0 ／ Relevanceと再通知上限を検査 ／ 同状態 ／ Alert再投入可能 ／ 間隔未設定を無限通知にしない ／ §24.1 ／ |
| 状態 | `ACKNOWLEDGED` ／ `OPEN` ／ `OPEN / ACKNOWLEDGED` ／ `RESOLVED` |

### 不整合時の扱い

問題の検知、認知、解決、再通知をDurableな状態遷移として管理する。 IncidentのOPEN、ACKNOWLEDGED、RESOLVED状態。 ／ 未生成 ／ 問題検知 ／ incident_id、dedup_key、review情報を記録 ／ OPEN ／ 必要ならProposal / Alert生成 ／ Proposal TTLとは独立 ／ §24.1 ／ ／ OPEN ／ 人が認知 ／ acknowledged_atを記録 ／ ACKNOWLEDGED ／ 再通知規則を再評価 ／ 認知を承認・注文・解決とみなさない ／ §24.1 ／ ／ OPEN / ACKNOWLEDGED ／ 対応不要の証拠と解決理由が成立 ／ resolved理由を記録 ／ RESOLVED ／ 関連Proposalを再評価 ／ Proposal失効だけでは遷移しない ／ §24.1 ／ ／ OPEN / ACKNOWLEDGED ／ next_review_at到来、未応答P0 ／ Relevanceと再通知上限を検査 ／ 同状態 ／ Alert再投入可能 ／ 間隔未設定を無限通知にしない ／ §24.1 ／
