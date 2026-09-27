# Section 3.5 Semantic Gate

## 総合判定

**PASS**

- 対象: Coverage Contract全66行
- 結果: PRESERVED 66、REFERENCED 0、MISSING 0、DISTORTED 0、INVENTED 0
- 判定理由: 全66件について、主体、対象、条件、否定、例外、失敗時挙動、保存必須要素、Formal Identifier、設計参照および規範強度を本文から一意に復元できる。
- レビュー方法: 固定templateとの一致ではなく、各Coverage行について主体、対象、条件、否定、例外、失敗時挙動、保存必須要素、Formal Identifierおよび規範強度を本文から復元できるかを意味単位で照合した。

## Coverage別判定

| Coverage ID | 判定 | 本文根拠と照合結果 |
|---|---|---|
| SDD-L1126 | PRESERVED | 3行目。正本性・派生性の曖昧さを原因、Projection / Backupの独立更新と正本との差異を結果として保持。 |
| SDD-L1280 | PRESERVED | 40行目。古いsnapshot、Broker実約定・Cash、差異を消す危険の因果を保持。 |
| SDD-L1858 | PRESERVED | 62行目。容量目安・警告候補・保存形式の確定値化を禁止し、不適切な固定を具体化。 |
| SDD-L1128 | PRESERVED | 3行目。各Artifactの生成元、利用先、保持条件、不変条件をすべて明示。 |
| SDD-L1282 | PRESERVED | 46行目。Restore後のReconciliationと確認済み差分の`Event`再Commitを「必須」として保持。 |
| SDD-L1860 | PRESERVED | 3行目および52〜62行目。既定値、候補値、監視量、形式、将来移行条件の区別を復元可能。 |
| SDD-L1130 | PRESERVED | 7行目。`SYSTEM.md`、Canonical State、Projection、`inbox/`、`evidence/`、`logs/`、`reports/`、`validation/`、`archive/`、`stage/`を列挙。 |
| SDD-L1134 | PRESERVED | 11行目。名称、種別、生成元、利用先、内容および参照`§4`を保持。 |
| SDD-L1135 | PRESERVED | 12行目。`portfolio.json`からAtomic Commitまでの関係と参照`§4、§13`を保持。 |
| SDD-L1136 | PRESERVED | 13行目。3 Projection、再生成、利用先、独立更新禁止および参照`§4`を保持。 |
| SDD-L1137 | PRESERVED | 14行目。`performance.json`、派生結果、評価処理、Report、計算条件・参照Commit、参照`§4、§36`を保持。 |
| SDD-L1138 | PRESERVED | 15行目。`inbox/`、Durable入力、Fact ingress、Parser / Writer、原文保持条件、参照`§4、§12`を保持。 |
| SDD-L1139 | PRESERVED | 16行目。`evidence/`の全意味要素と参照`§4、§29`を保持。 |
| SDD-L1140 | PRESERVED | 17行目。Audit Projection、生成元、利用者、両ID、代替禁止および参照`§4、§28〜30`を保持。 |
| SDD-L1141 | PRESERVED | 18行目および28〜30行目。規則群と参照`§2.6、§4、§28`を保持。 |
| SDD-L1142 | PRESERVED | 19行目。対象、種別、生成元、利用者、正本禁止および参照`§4、§9〜10`を保持。 |
| SDD-L1143 | PRESERVED | 20行目。検証Artifactの全意味要素と参照`§4、§46B`を保持。 |
| SDD-L1144 | PRESERVED | 21行目。append-only Fact履歴、生成元、利用先、hash / range / high-water mark、参照`§13.4`を保持。 |
| SDD-L1145 | PRESERVED | 22行目。観測履歴、生成元、利用先、revision / vintage、参照`§13.4、§39`を保持。 |
| SDD-L1146 | PRESERVED | 23行目。監査履歴、Commit、Review、削除禁止および参照`§13.4`を保持。 |
| SDD-L1147 | PRESERVED | 24行目。Durable Stageの全意味要素と参照`§2.5、§13.4`を保持。 |
| SDD-L1149 | PRESERVED | 26行目。用途と、Canonical State / Fact / `Event` / Audit Recordとは別Artifactである関係を保持。 |
| SDD-L1152-a | PRESERVED | 28行目。`Asia/Tokyo`の日付境界とDaily rotationを同時に保持。 |
| SDD-L1152-b | PRESERVED | 28行目。日付単位で管理可能と明示。 |
| SDD-L1153-a | PRESERVED | 30行目。Secretの記録禁止を保持。 |
| SDD-L1153-b | PRESERVED | 30行目。Credentialの記録禁止を保持。 |
| SDD-L1153-c | PRESERVED | 30行目。Tokenの記録禁止を保持。 |
| SDD-L1153-d | PRESERVED | 30行目。API keyの記録禁止を保持。 |
| SDD-L1153-e | PRESERVED | 30行目。Authorization headerの記録禁止を保持。 |
| SDD-L1153-f | PRESERVED | 30行目。未redactのdebug dumpの記録禁止を保持。 |
| SDD-L1154-a | PRESERVED | 26行目。Application LogによるCanonical State / Fact / `Event` / Audit Recordの代替を禁止。 |
| SDD-L1154-b | PRESERVED | 26行目。Log削除時にも投資判断、状態、履歴等のCanonical設計情報を失わない構造を要求。 |
| SDD-L1155-a | PRESERVED | 28行目。Canonical State、Commit、Auditより低い保存優先度を保持。 |
| SDD-L1155-b | PRESERVED | 28行目。具体期間は未確定のまま有限保持上限を要求。 |
| SDD-L1155-c | PRESERVED | 28行目。Log単独書込み失敗をCanonical Commit / 投資Canonical処理へ波及させない。 |
| SDD-L1155-d | PRESERVED | 28行目。単独書込み失敗を可能な範囲で観測可能にする。 |
| SDD-L1155-e | PRESERVED | 28行目。同一Storage障害がCanonical安全性を損なう条件でStorage Fail Closedを適用。 |
| SDD-L1156-a | PRESERVED | 30行目。TEST / PAPER / LIVEのRuntime Identity分離を保持。 |
| SDD-L1156-b | PRESERVED | 30行目。Development / Runtimeの物理分離を保持。 |
| SDD-L1156-c | PRESERVED | 30行目。分離されたApplication Logの相互混在を禁止。 |
| SDD-L1159 | PRESERVED | 32行目。生成主体、Writer責務、書込み経路を未確定事項として保持。旧空要素SDD-L1158ではなく、この実意味行が保存されている。 |
| SDD-L1160 | PRESERVED | 32行目。retention具体期間とcleanup / deletion実行方法を未確定として保持。 |
| SDD-L1161 | PRESERVED | 32行目。crash直前のLog durability保証範囲を未確定として保持。 |
| SDD-L1162 | PRESERVED | 32行目。Runtime / Job / Adapter / Errorごとの最低限識別情報を未確定として保持。 |
| SDD-L1163 | PRESERVED | 32行目。両分離軸の具体的partition / path方式を未確定として保持。 |
| SDD-L1164 | PRESERVED | 32行目。追加の禁止・masking情報範囲を未確定として保持。 |
| SDD-L1165 | PRESERVED | 32行目。filename、file format、schema、logging libraryを未確定として保持。 |
| SDD-L1284 | PRESERVED | 40行目。Backup snapshot、Restore、Broker照合、Correction / missing Fact、通常運用復帰を一連の手順として列挙。 |
| SDD-L1288 | PRESERVED | 36行目。ARGUS / Backup Job、Canonical commit、4種のsnapshot識別情報、成功分離、recent / long-term、Secret平文禁止、freshness監視を保持。 |
| SDD-L1289 | PRESERVED | 42行目。人、Recovery Service、対象snapshot配置、`RESTORE_RECOVERY`、復旧State、実約定を消したままの再開禁止、Reconciliationを保持。 |
| SDD-L1290 | PRESERVED | 43行目。ARGUS、実装主体未確定、Broker / execution / cash / position照合、`RECONCILIATION_REQUIRED`、差分、推測禁止、Correction / missing Factを保持。 |
| SDD-L1291 | PRESERVED | 44行目。主体`ARGUS`とWriter、確認済み差分、`Event` Commit、Reconciliation Complete、整合State、Formal Identifier `BUY/ADD`、停止継続および通常運用条件を保持。 |
| SDD-L1294-a | PRESERVED | 38行目。内蔵SSD、直近N世代、復旧snapshotを保持し、Nを未確定として固定値化を禁止。旧空要素SDD-L1293ではなく、この実意味行が保存されている。 |
| SDD-L1294-b | PRESERVED | 38行目。外付けHDDの長期Backup責務を保持。 |
| SDD-L1295-a | PRESERVED | 38行目。Formal Identifier `last_local_backup_at`と監視を保持。 |
| SDD-L1295-b | PRESERVED | 38行目。`last_external_backup_at`を原表記で保持し、localとは別々の監視と明示。 |
| SDD-L1297 | PRESERVED | 40行目。保存必須の設計元参照`§4.5、§4.7`をBackup、Restore、Reconciliationの接続根拠として保持。 |
| SDD-L1862 | PRESERVED | 50〜60行目。Data Root、2TB、1.8TB、usage / growth、Raw、JSONL、JSON、SQLite / Parquetをすべて復元可能。 |
| SDD-L1866 | PRESERVED | 50行目および54行目。Data Root、正確なpath、初期保存先、drive letter非依存、marker照合必須、参照`§4.1、§4.7`を保持。 |
| SDD-L1867 | PRESERVED | 55行目と63行目。最大約2TB、目安、見積値・予約領域ではないこと、参照`§4.1`を保持。 |
| SDD-L1868 | PRESERVED | 56行目。約1.8TB、候補値、実測後CV設定、参照`§4.7`を保持。 |
| SDD-L1869 | PRESERVED | 57行目。4監視量、Adapter暴走・Log loop検知目的、参照`§4.1`を保持。 |
| SDD-L1870 | PRESERVED | 58行目。Raw、Response / ZIP / XBRL / PDF、原本または許諾形式、immutable保持、参照`§4.7`を保持。 |
| SDD-L1871 | PRESERVED | 59行目。Normalized time series、JSONL初期標準候補、Provider非依存schema、provenance、参照`§4.7、§37A`を保持。 |
| SDD-L1872 | PRESERVED | 60行目。Small metadata、JSON許容、小容量単発Record、参照`§4.7`を保持。 |
| SDD-L1873 | PRESERVED | 61行目。将来形式、SQLite / Parquet候補、容量・検索性能bottleneck時の移行判断、参照`§4.7`を保持。 |

## 特記事項

### 旧空要素と実意味行

- 旧空要素SDD-L1158およびSDD-L1293はCoverage Contractの対象ではなく、欠落判定の対象にしていない。
- SDD-L1159〜SDD-L1165の未確定事項は、32行目で未確定という規範強度を弱めず保存されている。
- SDD-L1294-a / bおよびSDD-L1295-a / bは、38行目で媒体責務、未確定のN、二つのFormal Identifier、別々の監視を欠落なく保存している。

### R-06相当の3.5欠落回帰

3.5固有の欠落回帰は検出しなかった。SDD-L1297の`§4.5、§4.7`、表由来Coverage 22行の設計参照、SDD-L1291の主体`ARGUS`とFormal Identifier `BUY/ADD`はすべて復元された。旧空要素SDD-L1158 / SDD-L1293を誤って契約対象へ含めず、その直後の実意味行SDD-L1159〜およびSDD-L1294〜を欠落なく保存している。

### 発明検査

契約外の新しい状態、Authority、固定閾値、固定保持期間、有料サービスまたは失敗時挙動の発明は検出しなかった。`N`、retention期間、Application Log実装主体、Reconciliation実装主体は未確定のまま維持されている。
