# Section 3.5 Semantic Gate

## 総合判定

**NO_FINDINGS**

- 対象: Coverage Contract全66行
- 結果: PRESERVED 66、REFERENCED 0、MISSING 0、DISTORTED 0、INVENTED 0
- 判定理由: 全66件について、主体、対象、条件、否定、例外、失敗時挙動、保存必須要素、Formal Identifier、設計参照および規範強度をP-0098本文から一意に復元できる。
- レビュー方法: 固定templateとの文面一致ではなく、各Coverage行の設計意味と保存必須要素をP-0098本文に対して個別に照合した。構造変更そのものの適否は別紙`section-3.5-regression.md`で評価する。

## Coverage別判定

| Coverage ID | 判定 | P-0098本文根拠と照合結果 |
|---|---|---|
| SDD-L1126 | PRESERVED | 3行目。Runtime Artifactの正本性・派生性が不明であることを原因、Projection / Backupの独立更新を結果として保持。 |
| SDD-L1280 | PRESERVED | 3行目および60行目。古いsnapshot、Broker実約定・Cash、差異を消し得る危険の因果を保持。 |
| SDD-L1858 | PRESERVED | 3行目および86行目。容量目安・警告候補・保存形式の確定値化が不適切な閾値・形式を固定し得る因果を保持。 |
| SDD-L1128 | PRESERVED | 5行目および9〜26行目。Artifactごとの生成元、利用先、保持条件、不変条件を定義。 |
| SDD-L1282 | PRESERVED | 5行目および60行目。Restore後のReconciliationと確認済み差分の`Event`再Commitを「必ず」として保持。 |
| SDD-L1860 | PRESERVED | 5行目および73〜86行目。既定値、候補値、監視量、形式、将来移行条件の区別を復元可能。 |
| SDD-L1130 | PRESERVED | 9行目。`SYSTEM.md`、Canonical State、Projection、`inbox/`、`evidence/`、logs、`reports/`、`validation/`、archive、`stage/`を列挙。 |
| SDD-L1134 | PRESERVED | 13行目。`SYSTEM.md`、起動Artifact、配備工程、人・Runner、起動手順・正本・版・入口・復旧、参照`§4`を保持。 |
| SDD-L1135 | PRESERVED | 14行目。`portfolio.json`、Canonical State、Single Writer、全Domain処理、Atomic Commit単位、参照`§4、§13`を保持。 |
| SDD-L1136 | PRESERVED | 15行目。3 Projection、Canonical Stateからの再生成、UI・互換利用、独立更新禁止、参照`§4`を保持。 |
| SDD-L1137 | PRESERVED | 16行目。`performance.json`、派生結果、評価処理、Report、計算条件・参照Commit、参照`§4、§36`を保持。 |
| SDD-L1138 | PRESERVED | 17行目。`inbox/`、Durable入力、Fact ingress、Parser・Writer、適用完了までの受領原文保持、参照`§4、§12`を保持。 |
| SDD-L1139 | PRESERVED | 18行目。`evidence/`、根拠Artifact、Provider / acquisition、Analysis・Audit、source・時刻・hash・許諾範囲原文、参照`§4、§29`を保持。 |
| SDD-L1140 | PRESERVED | 19行目。Audit Projection、Commit records、人・別AI、両IDによる重複排除、Application Log代替禁止、参照`§4、§28〜30`を保持。 |
| SDD-L1141 | PRESERVED | 20行目および30〜38行目。Application Logの生成主体・Writer実装未確定、用途、rotation、優先度・有限保持、失敗分離、秘密情報禁止、設計参照を保持。 |
| SDD-L1142 | PRESERVED | 21行目。`reports/`、Human-facing Artifact、Analysis / Evaluation、人、正本禁止、参照`§4、§9〜10`を保持。 |
| SDD-L1143 | PRESERVED | 22行目。`validation/`、検証Artifact、Test process、Gate判断、計画・入力・期待・実測・Evidenceの分離、参照`§4、§46B`を保持。 |
| SDD-L1144 | PRESERVED | 23行目。`archive/events`、append-only Fact履歴、Compaction / Writer、Rebuild・Audit、hash / range / high-water mark、参照`§13.4`を保持。 |
| SDD-L1145 | PRESERVED | 24行目。`archive/observations`、append-only観測履歴、Acquisition / archive、Analysis・Replay、revision / vintage、参照`§13.4、§39`を保持。 |
| SDD-L1146 | PRESERVED | 25行目。`archive/audit`、append-only監査履歴、Commit、Review、過去Record削除禁止、参照`§13.4`を保持。 |
| SDD-L1147 | PRESERVED | 26行目。`stage/`、Durable Stage、External / Model call、Validate・Commit再開、request/input/output hashとusage、参照`§2.5、§13.4`を保持。 |
| SDD-L1149 | PRESERVED | 30行目。Runtime / Job / Adapter / Error等の用途と、Canonical State / Fact / `Event` / Audit Recordとは別Artifactである関係を保持。 |
| SDD-L1152-a | PRESERVED | 32行目。`Asia/Tokyo`の日付境界とDaily rotationを同時に保持。 |
| SDD-L1152-b | PRESERVED | 32行目。日付単位で管理可能と明示。 |
| SDD-L1153-a | PRESERVED | 36行目。SecretのApplication Log記録禁止を保持。 |
| SDD-L1153-b | PRESERVED | 36行目。CredentialのApplication Log記録禁止を保持。 |
| SDD-L1153-c | PRESERVED | 36行目。TokenのApplication Log記録禁止を保持。 |
| SDD-L1153-d | PRESERVED | 36行目。API keyのApplication Log記録禁止を保持。 |
| SDD-L1153-e | PRESERVED | 36行目。Authorization headerのApplication Log記録禁止を保持。 |
| SDD-L1153-f | PRESERVED | 36行目。未redactのdebug dumpのApplication Log記録禁止を保持。 |
| SDD-L1154-a | PRESERVED | 30行目。Application LogによるCanonical State / Fact / `Event` / Audit Recordの代替を禁止。 |
| SDD-L1154-b | PRESERVED | 30行目。Application Log削除時にも投資判断、状態、履歴等のCanonical設計情報を失わないことを要求。 |
| SDD-L1155-a | PRESERVED | 32行目。Canonical State、Commit、Auditより低い保存優先度を保持。 |
| SDD-L1155-b | PRESERVED | 32行目。具体期間は未確定のまま有限保持上限を要求。 |
| SDD-L1155-c | PRESERVED | 34行目。Application Log単独書込み失敗をCanonical Commit / 投資Canonical処理へ波及させない。 |
| SDD-L1155-d | PRESERVED | 34行目。単独書込み失敗を可能な範囲で観測可能にする。 |
| SDD-L1155-e | PRESERVED | 34行目。同一Storage障害がCanonical安全性を損なう条件でStorage Fail Closedを適用。 |
| SDD-L1156-a | PRESERVED | 38行目。TEST / PAPER / LIVEのRuntime Identity分離を保持。 |
| SDD-L1156-b | PRESERVED | 38行目。Development / Runtimeの物理分離を保持。 |
| SDD-L1156-c | PRESERVED | 38行目。分離されたApplication Logの相互混在を禁止。 |
| SDD-L1159 | PRESERVED | 40〜42行目。生成主体、Writer責務、書込経路を未確定事項として保持。 |
| SDD-L1160 | PRESERVED | 32行目。retention具体期間とcleanup / deletion実行方法を未確定として保持。 |
| SDD-L1161 | PRESERVED | 40行目および43行目。crash直前のLog durability保証範囲を未確定として保持。 |
| SDD-L1162 | PRESERVED | 40行目および44行目。Runtime / Job / Adapter / Errorごとの最低限識別情報を未確定として保持。 |
| SDD-L1163 | PRESERVED | 38行目。両分離軸の具体的partition / path方式を未確定として保持。 |
| SDD-L1164 | PRESERVED | 36行目。追加の禁止・masking情報範囲を未確定として保持。 |
| SDD-L1165 | PRESERVED | 40行目および45行目。filename、file format、schema、logging libraryを未確定として保持。 |
| SDD-L1284 | PRESERVED | 60行目。Backup snapshot、Restore、Broker照合、Correction / missing Fact、通常運用復帰を列挙。 |
| SDD-L1288 | PRESERVED | 49行目および64行目。ARGUS / Backup Job、Canonical commit、`commit_id`・`state_version`・hash・版参照、成功分離、recent / long-term、Secret平文禁止、freshness監視を保持。 |
| SDD-L1289 | PRESERVED | 65行目。人、Recovery Service、対象snapshot配置、`RESTORE_RECOVERY`、復旧State、実約定を消したままの再開禁止、Reconciliationを保持。 |
| SDD-L1290 | PRESERVED | 66行目。ARGUS、実行担当未確定、Broker / execution / cash / position照合、`RECONCILIATION_REQUIRED`、差分、推測禁止、Correction / missing Factを保持。 |
| SDD-L1291 | PRESERVED | 67行目。ARGUSとWriter、確認済み差分、`Event` Commit、Reconciliation Complete、整合State、Formal Identifier `BUY/ADD`、停止継続、通常運用条件を保持。 |
| SDD-L1294-a | PRESERVED | 53行目。内蔵SSD、直近N世代、復旧snapshotを保持し、NをTBDとして固定値化していない。 |
| SDD-L1294-b | PRESERVED | 54行目。外付けHDDの長期Backup責務を保持。 |
| SDD-L1295-a | PRESERVED | 56行目。Formal Identifier `last_local_backup_at`と監視を保持。 |
| SDD-L1295-b | PRESERVED | 56行目。`last_external_backup_at`を原表記で保持し、localとは別々の監視と明示。 |
| SDD-L1297 | PRESERVED | 69行目。設計元参照`§4.5`および`§4.7`を保持。 |
| SDD-L1862 | PRESERVED | 73〜86行目。`Data Root`、2TB、1.8TB、usage / growth、Raw、JSONL、JSON、SQLite / Parquetをすべて復元可能。 |
| SDD-L1866 | PRESERVED | 73行目および77行目。`Data Root`、正確なpath、初期物理保存先、drive letterだけでは受け入れない条件、marker照合必須、参照`§4.1、§4.7`を保持。 |
| SDD-L1867 | PRESERVED | 78行目。最大約2TB、目安、必要容量見積・予約領域ではないこと、参照`§4.1`を保持。 |
| SDD-L1868 | PRESERVED | 79行目。約1.8TB、候補値、Dataset実測後のCV設定、参照`§4.7`を保持。 |
| SDD-L1869 | PRESERVED | 80行目。4監視量、Adapter暴走・Log loop検知目的、参照`§4.1`を保持。 |
| SDD-L1870 | PRESERVED | 81行目。Raw、Response / ZIP / XBRL / PDF、原本または許諾形式、immutable保持、参照`§4.7`を保持。 |
| SDD-L1871 | PRESERVED | 82行目。Normalized time series、JSONL初期標準候補、Provider非依存schema、provenance、参照`§4.7、§37A`を保持。 |
| SDD-L1872 | PRESERVED | 83行目。Small metadata、JSON許容、小容量単発Record、参照`§4.7`を保持。 |
| SDD-L1873 | PRESERVED | 84行目。将来形式、SQLite / Parquet候補、容量・検索性能bottleneck時の移行判断、参照`§4.7`を保持。 |

## 特記事項

- 旧空要素SDD-L1158およびSDD-L1293はCoverage Contractの対象ではなく、欠落判定の対象にしていない。
- Application Logの実意味行SDD-L1159〜SDD-L1165は、未確定という規範強度を弱めず保存されている。
- BackupのSDD-L1294-a / bおよびSDD-L1295-a / bは、媒体責務、未確定のN、二つのFormal Identifier、別々の監視を保存している。
- P-0098新3.5.5は、P-0097旧3.5.3の見出し番号を3.5.5へ正規化すると文字単位で完全一致する。Data Root関連Coverageの意味・順序・表内容はそのまま保存されている。
- 契約外の新しい状態、Authority、固定閾値、固定保持期間、有料サービスまたは失敗時挙動は検出しなかった。`N`、retention期間、Application Log実装主体、Reconciliation実行担当は未確定のままである。
