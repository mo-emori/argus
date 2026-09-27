# Section 3.4 Semantic Gate

## 総合判定

**PASS**

Coverage Contract 94件を `section-3.4.md` と個別照合した。全94件が意味、保存必須要素、Formal Identifier、参照、否定・例外・失敗時動作および規範強度を保存している。限定修正後の `SDD-L1094` は、契約の列挙 `Runtime Identity`、`Configuration`、`User / Domain / Runtime State`、`Secret` を情報種別節の導入文でそのまま明示し、後続表の個別行とも対応する。全件合格条件を満たす。

判定語は `PRESERVED`（本文内で意味を直接保存）、`REFERENCED`（明示的な相互参照から復元）、`MISSING`（復元不能）、`DISTORTED`（存在するが意味・識別子・規範強度が変化）、`INVENTED`（契約にない意味を追加）である。本レビューでは固定template照合を用いていない。

## Coverage ID別判定

| Coverage ID | 判定 | 本文根拠・照合所見 |
|---|---|---|
| SDD-L0066 | PRESERVED | 「状態軸と分類軸」導入文が全混同対象と誤遷移の因果を保持。 |
| SDD-L0086 | PRESERVED | 「データ種別と変更要求」導入文が4対象の混同と事実拒否・履歴破壊を保持。 |
| SDD-L0139 | PRESERVED | 「永続化段階とArtifact Authority」導入文が3種Artifactの混同と再実行・正本性誤認を保持。 |
| SDD-L0361 | PRESERVED | 「Canonical Dataと派生データの更新」導入文が4対象、並行更新、途中停止、正本破損を保持。 |
| SDD-L0369 | PRESERVED | 同導入文がIdentityからProjectionまでの全9対象と正本性喪失を保持。 |
| SDD-L1090 | PRESERVED | 「情報種別ごとの正本、更新主体、失敗動作」導入文が原因と権限・復旧条件の曖昧化を保持。 |
| SDD-L1730 | PRESERVED | Research lifecycle導入文が全5段階の混同と履歴・欠損理由喪失を保持。 |
| SDD-L1746 | PRESERVED | Thesis revision導入文が上書き・二値化と弱化・失効・不明・Evidence履歴の識別不能を保持。 |
| SDD-L1761 | PRESERVED | Holding lifecycle導入文がProposal/Orderからの推測と部分約定・監視終了の誤りを保持。 |
| SDD-L0068 | PRESERVED | 状態概念と独立分類軸を「区別」と明記。 |
| SDD-L0088 | PRESERVED | データと操作要求の意味・更新経路を「分離」と明記。 |
| SDD-L0141 | PRESERVED | 永続化段階とArtifact Authorityを「区別」と明記。 |
| SDD-L0363 | PRESERVED | 冒頭および更新節で単一正本、再現可能、原子的更新を明記。 |
| SDD-L0371 | PRESERVED | 冒頭および更新節で生成元、利用先、保持条件、更新Authorityの区別を明記。 |
| SDD-L1092 | PRESERVED | 情報種別ごとに正本、更新主体、包含範囲、禁止対象、失敗時動作を固定すると明記。 |
| SDD-L1732 | PRESERVED | Research lifecycleを独立した状態機械と明記。 |
| SDD-L1748 | PRESERVED | Thesis revisionとEvidence変化を状態遷移として保持すると明記。 |
| SDD-L1763 | PRESERVED | Holdingを確認済みExecution Factと数量に基づき遷移させると明記。 |
| SDD-L0070 | PRESERVED | 状態軸表にState、User Status、human_capacity、Runner State、Policy Mode、Holding Horizon、Role Bucket、severity、priorityの全9対象あり。 |
| SDD-L0074 | PRESERVED | State行に現在値・遷移履歴、混同禁止、利用先、§4〜5・§13を保持。 |
| SDD-L0075 | PRESERVED | User Status行に値域、人の直接操作、Configuration否定、human_capacity入力、利用先、参照を保持。 |
| SDD-L0076 | PRESERVED | human_capacity行に値域、Status Mapper、入力値/Status否定、利用先、参照を保持。 |
| SDD-L0077 | PRESERVED | Runner State行に全状態、OS kill/crashの終了事象性、User Statusとの分離、利用先、参照を保持。 |
| SDD-L0078 | PRESERVED | Policy Mode行に全状態、Holding Horizon/Role Bucket否定、利用先、§15Bを保持。 |
| SDD-L0079 | PRESERVED | Holding Horizon行に全値、時間軸、強制SELL否定、Role Bucketとの別軸、利用先、§16を保持。 |
| SDD-L0080 | PRESERVED | Role Bucket行に全値、二重計上禁止、Holding Horizonとの別軸、利用先、参照を保持。 |
| SDD-L0081 | PRESERVED | severity行に全値、priorityとの別軸、利用先、§24.0を保持。 |
| SDD-L0082 | PRESERVED | priority行にP0〜P3、severityからの暗黙導出禁止、利用先、§24.0を保持。 |
| SDD-L0090 | PRESERVED | 導入文と表にFact、Observation、Judgment、Command、Correction、Evidenceの全6対象あり。 |
| SDD-L0094 | PRESERVED | Fact行に区分、確認済み現実の例、拒否禁止、Canonical Facts、§12〜13を保持。 |
| SDD-L0095 | PRESERVED | Observation行に時点付き例、Fact/Judgmentとの分離、as_of provenance、利用先、参照を保持。 |
| SDD-L0096 | PRESERVED | Judgment行に判断結果、行為との区別、Fact上書き禁止、履歴追加、利用先、参照を保持。 |
| SDD-L0097 | PRESERVED | Command行にrequest_id、主体とWriter、Fact/Proposalとの区別、利用先、参照を保持。 |
| SDD-L0098 | PRESERVED | Correction行にHuman入力、削除禁止と履歴追加、Broker現実Rollback否定、Governance非迂回、利用先、参照を保持。 |
| SDD-L0099 | PRESERVED | Evidence行に原文/許諾抜粋、取得情報、hash、vintage、URLのみの固定否定、Observation根拠、利用先、参照を保持。 |
| SDD-L0143 | PRESERVED | 永続化表に列挙8対象がすべて独立行として存在。 |
| SDD-L0147 | PRESERVED | Durable Stage Result行に位置付け、Commit前永続化、Canonical State否定、再開・再課金防止、利用先、参照を保持。 |
| SDD-L0148 | PRESERVED | Commit行にTransaction結果、原子的State version、外部API副作用のRollback境界外、Single Writer、参照を保持。 |
| SDD-L0149 | PRESERVED | Canonical State行に現在正本、4種の正本化禁止、portfolio.json、参照を保持。 |
| SDD-L0150 | PRESERVED | Current Envelope行に現在状態・直近参照、無期限埋込み禁止、archive参照、state/archive、§13.4を保持。 |
| SDD-L0151 | PRESERVED | Projection行に再生成可能な派生物、独立更新禁止、全利用先、参照を保持。 |
| SDD-L0152 | PRESERVED | Artifact行に成果物例、Artifact単位のAuthority/正本性、Repository/Runtime、参照を保持。 |
| SDD-L0153 | PRESERVED | Configuration行に人が明示する単一正本、4対象との分離、config.json、§4.0を保持。 |
| SDD-L0154 | PRESERVED | Runtime Identity行にlogical instance、不変識別子、Deployment/Run Identity・path・設定値との分離、利用先、参照を保持。 |
| SDD-L0365 | PRESERVED | 永続化表直後の本文にCanonical Envelope、inbox、archive、Stage、Projectionの全対象と役割分離あり。 |
| SDD-L0373 | PRESERVED | 更新節で対象をRuntimeからAuditまでのCanonical Dataおよび派生データと明記。 |
| SDD-L0377 | PRESERVED | Runtime Identity行に性質、生成元、利用先、3識別子、path/Secret/Status/Domain State禁止、§4.0を保持。 |
| SDD-L0378 | PRESERVED | Configuration行に生成元、利用先、config.json単一正本、version/hash、immutable snapshot、§4.0を保持。 |
| SDD-L0379 | PRESERVED | User Status行にStatusChangeCommand、利用先、user_status.json、status_version、直接編集禁止、参照を保持。 |
| SDD-L0380 | PRESERVED | Facts行に全生成元、利用先、拒否・破壊・過去上書き禁止、参照を保持。 |
| SDD-L0381 | PRESERVED | Observations行にProvider Adapter、利用先、全provenance項目、参照を保持。 |
| SDD-L0382 | PRESERVED | Judgments行にAgent/人、利用先、immutable Decision、Thesis revision、Human Decision、参照を保持。 |
| SDD-L0383 | PRESERVED | Workflow行に全生成元、実行制御、独立状態保持、参照を保持。 |
| SDD-L0384 | PRESERVED | Raw Data行に外部原本、Provider Adapter、利用先、許諾範囲、immutable保存、参照を保持。 |
| SDD-L0385 | PRESERVED | Normalized Data行にProvider非依存、生成元、利用先、Raw追跡可能性、参照を保持。 |
| SDD-L0386 | PRESERVED | Durable Stage行に生成元、Validate/Commit再開、再課金・重複適用防止、Canonical Factとの区別、参照を保持。 |
| SDD-L0387 | PRESERVED | Audit / Decision Log行にCanonical Commit由来Projection、利用主体、Markdown正本否定、参照を保持。 |
| SDD-L1094 | PRESERVED | 情報種別節の導入文が `Runtime Identity`、`Configuration`、`User / Domain / Runtime State`、`Secret` を契約どおり列挙し、後続表が各情報種別の内容を個別化している。 |
| SDD-L1098 | PRESERVED | Runtime Identity行に物理形式、更新主体、全格納候補、全禁止対象、通常起動禁止、§4.0を保持。 |
| SDD-L1099 | PRESERVED | Configuration行にconfig.json、Config Writer、全格納内容、3禁止対象、CONFIG_REQUIRED等、§4.0を保持。 |
| SDD-L1100 | PRESERVED | User Status行にuser_status.json、Status Writer、全格納内容、3禁止対象、競合時破棄、参照を保持。 |
| SDD-L1101 | PRESERVED | Domain State行にportfolio.json Envelope、Writer、全格納内容、禁止対象、RECOVERY_REQUIRED、参照を保持。 |
| SDD-L1102 | PRESERVED | Runtime State行に物理位置、Runner/Writer、全格納内容、禁止対象、latest Stateからの再構成、§4.0を保持。 |
| SDD-L1103-a | PRESERVED | Secret行の物理形式がEnvironment Variable / OS-protected storeであり、二つの保存元を個別復元可能。 |
| SDD-L1103-b | PRESERVED | Secret行の更新主体が「使用Subsystem」であり、利用主体を個別復元可能。 |
| SDD-L1103-c0 | PRESERVED | Secret行の格納内容が「API key等のSecret値」であり、API keyが値の例であることを復元可能。 |
| SDD-L1103-c1 | PRESERVED | Secret行の「格納しない内容」にprojectを明示。 |
| SDD-L1103-c2 | PRESERVED | Secret行の「格納しない内容」にconfigを明示。 |
| SDD-L1103-c3 | PRESERVED | Secret行の「格納しない内容」にlogを明示。 |
| SDD-L1103-c4 | PRESERVED | Secret行の「格納しない内容」にevidenceを明示。 |
| SDD-L1103-c5 | PRESERVED | Secret行の「格納しない内容」にreportを明示。 |
| SDD-L1103-c6 | PRESERVED | Secret行の「格納しない内容」にbackupを明示。 |
| SDD-L1103-d | PRESERVED | Secret行が漏出の「疑い」を条件にAdapter停止とSECURITY_INCIDENTをともに要求し、fail-closed強度を保持。 |
| SDD-L1103-e | PRESERVED | Secret行の設計参照に§4.4と§46Eをともに明示。 |
| SDD-L1734 | PRESERVED | Research導入文にDISCOVERED、CANDIDATE、ANALYZED、WATCH、ARCHIVEDの全状態あり。 |
| SDD-L1738 | PRESERVED | 未登録行に探索条件、source/枝別状態、DISCOVERED、利用先、欠損の否定評価禁止、§5〜7を保持。 |
| SDD-L1739 | PRESERVED | DISCOVERED行に条件、登録、CANDIDATE、利用先、DATA_INSUFFICIENTの0点化禁止、§5〜7を保持。 |
| SDD-L1740 | PRESERVED | CANDIDATE行に条件、branch結果/矛盾、ANALYZED、Report/Proposal、未評価理由保存、参照を保持。 |
| SDD-L1741 | PRESERVED | ANALYZED行に条件、Watch登録、WATCH、Candidate Watch、売買承認否定、参照を保持。 |
| SDD-L1742 | PRESERVED | 任意行に対象外/追跡終了、理由、ARCHIVED、Counterfactual sample、履歴削除禁止、参照を保持。 |
| SDD-L1750 | PRESERVED | Thesis導入文にVALID、WEAKENED、INVALIDATED、UNKNOWNの全状態あり。 |
| SDD-L1754 | PRESERVED | 未作成行に成立条件、revision保存、VALID、監視開始、旧revision上書き禁止、参照を保持。 |
| SDD-L1755 | PRESERVED | VALID行に一部悪化条件、Evidence比較/再分析、WEAKENED、候補、UNKNOWN検討、参照を保持。 |
| SDD-L1756 | PRESERVED | VALID/WEAKENED行に理由崩壊、Thesis Stop、INVALIDATED、最優先再分析、Price即SELL禁止、参照を保持。 |
| SDD-L1757 | PRESERVED | 任意行にEvidence不足/矛盾未解決、不明明示、UNKNOWN、BUY/ADD停止可能性、推測禁止、参照を保持。 |
| SDD-L1765 | PRESERVED | Holding導入文に未保有/CLOSED、OPEN、partial SELL、全売却の全対象あり。 |
| SDD-L1769 | PRESERVED | 未保有/CLOSED行に確認済みBUY Factと数量条件、全更新、OPEN、Watch開始、未確認遷移禁止、参照を保持。 |
| SDD-L1770 | PRESERVED | OPEN行にPartial SELLと数量条件、全更新、OPEN維持、Watch継続、cumulative quantity誤用禁止、参照を保持。 |
| SDD-L1771 | PRESERVED | OPEN行にSELLと数量条件、Commit、CLOSED、監視移行、Slot/reservation整合前終了禁止、参照を保持。 |
| SDD-L1773-a | PRESERVED | 後続本文がlot / trancheとDecision/Thesisの多対一関係を明記。 |
| SDD-L1773-b | PRESERVED | 後続本文が同一銘柄で保有、Candidate、新旧Thesisの併存可能性を明記。 |
| SDD-L1773-c | PRESERVED | 後続本文が同一銘柄で複数Decisionの併存可能性を明記。 |
| SDD-L1775 | PRESERVED | 集計Positionをaccount_idとinstrument_idの複合単位と明記。 |
| SDD-L1777 | PRESERVED | Holding lifecycleと履歴関係の基礎参照を§5と明記。 |

## R-05重点確認

`SDD-L1103-a`〜`e`は、単一のSecret行から固定文面ではなく列意味として個別に復元できる。Secret値の例 `API key`、保存元2種、利用主体、project/config/log/evidence/report/backupの6禁止対象、漏出疑い時のAdapter停止、`SECURITY_INCIDENT`、§4.4、§46Eはいずれも欠落・弱化・置換がない。

## 影響再確認

限定修正の影響確認対象 `SDD-L0066`、`SDD-L0075`、`SDD-L0369`、`SDD-L0379`、`SDD-L1100` は、いずれも従前の意味とFormal Identifierを維持している。`User Status` の定義、値域、更新主体、保存先、競合時動作は変更されておらず、追加された列挙 `User / Domain / Runtime State` による概念統合や規範強度の変化もない。追加修正指示はない。
