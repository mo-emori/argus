# Section 3.5.2 Post-gate Regression Review

- 判定: `FINDINGS`
- 対象: `section-3.5.2-en.md`、`section-3.5.2-ja.md`
- 評価基準: writer input の Section 3.5.2 Coverage Contract、translation contract、Translation Preservation Gate、Human-facing Gate
- Gate evidence: Translation Preservation Gate は `PASS` / `PRESERVED` / findings 0、Human-facing Gate は `PASS` / findings 0

## Findings

### R-01 `unredacted` の禁止意味が日本語版で一般化されている

English の禁止対象 `an unredacted debug dump` に対し、Japanese は `未編集のデバッグダンプ` としている。redaction は秘密情報等を除去・伏字化する処理であり、一般的な「編集」と同義ではない。writer input の SDD-L1153-f が要求する「未redactのdebug dump」の禁止対象を広く曖昧な表現へ置き換えており、translation contract の「Do not ... generalize design meaning」に反する。禁止項目の個数と禁止の規範強度は保持されるが、禁止対象の性質が正確には保存されていない。

この所見は、先行する2つの Gate がいずれも findings 0 であるという事実を変更せず、post-gate review で追加検出された差分として記録する。

## Regression Meaning evidence

`NO_FINDINGS` は English と Japanese の双方で、対象、条件、規範強度、失敗動作、未確定性が独立に確認できたことを示す。SDD-L1153-f だけは、Japanese の禁止対象の意味一般化により `FINDINGS` である。

| Coverage | 確認対象 | English evidence | Japanese evidence | 判定 |
|---|---|---|---|---|
| SDD-L1141 | path、種別、生成主体未確定、用途、rotation、低優先・有限保持、単独失敗分離、禁止情報、参照 | 冒頭、rotation、禁止情報、write-failure の各記述に分解して保持。`logs/application/YYYY-MM-DD/` と `§2.6` / `§4` / `§28` を明記 | 同じ意味要素、path、`§2.6` / `§4` / `§28` を保持 | `NO_FINDINGS` |
| SDD-L1149 | 運用・障害解析用記録、4 Artifact との分離 | 冒頭第1段落 | 冒頭第1段落 | `NO_FINDINGS` |
| SDD-L1152-a | `Asia/Tokyo` 日付境界の daily rotation | Rotation 第1文 | ローテーション第1文 | `NO_FINDINGS` |
| SDD-L1152-b | 日付単位で管理可能 | Rotation 第2文 | ローテーション第2文 | `NO_FINDINGS` |
| SDD-L1153-a | Secret 記録禁止 | 禁止リストの独立項目 | 禁止リストの独立項目 | `NO_FINDINGS` |
| SDD-L1153-b | Credential 記録禁止 | 禁止リストの独立項目 | 禁止リストの独立項目 | `NO_FINDINGS` |
| SDD-L1153-c | Token 記録禁止 | 禁止リストの独立項目 | 禁止リストの独立項目 | `NO_FINDINGS` |
| SDD-L1153-d | API key 記録禁止 | 禁止リストの独立項目 | 禁止リストの独立項目 | `NO_FINDINGS` |
| SDD-L1153-e | Authorization header 記録禁止 | 禁止リストの独立項目 | 禁止リストの独立項目 | `NO_FINDINGS` |
| SDD-L1153-f | 未 redacted debug dump 記録禁止 | `an unredacted debug dump` | `未編集のデバッグダンプ` は redaction / masking の意味を特定しない | `FINDINGS` |
| SDD-L1154-a | Canonical State / Fact / Event / Audit Record の代替禁止 | 冒頭第2段落第1文 | 冒頭第2段落第1文 | `NO_FINDINGS` |
| SDD-L1154-b | 削除時も投資判断・状態・履歴等を喪失しない | 冒頭第2段落第2文 | 冒頭第2段落第2文 | `NO_FINDINGS` |
| SDD-L1155-a | Canonical State / Commit / Audit より低い保存優先度 | 冒頭第2段落第3文 | 冒頭第2段落第3文 | `NO_FINDINGS` |
| SDD-L1155-b | 有限の保持上限 | `finite retention limit` | `有限の保持期限` | `NO_FINDINGS` |
| SDD-L1155-c | Application Log 単独書込み失敗を Canonical 処理へ波及させない | Write-failure 第1文 | 書き込み失敗第1文 | `NO_FINDINGS` |
| SDD-L1155-d | 単独書込み失敗を可能な範囲で観測可能にする | `to the extent possible` を保持 | `可能な範囲で` を保持 | `NO_FINDINGS` |
| SDD-L1155-e | 同一 storage 障害が canonical safety を損なう場合の Storage Fail Closed | Write-failure 第2段落 | 書き込み失敗第2段落 | `NO_FINDINGS` |
| SDD-L1156-a | TEST / PAPER / LIVE の Runtime Identity 分離 | Environment 第1文 | 環境の分離第1文 | `NO_FINDINGS` |
| SDD-L1156-b | Development / Runtime の物理分離 | Environment 第2文 | 環境の分離第2文 | `NO_FINDINGS` |
| SDD-L1156-c | 分離環境・domain の Log 混在禁止 | Environment 第3文 | 環境の分離第3文 | `NO_FINDINGS` |
| SDD-L1159 | 生成主体、Writer 責務、書込経路は未確定 | unresolved list 1 | 未解決 list 1 | `NO_FINDINGS` |
| SDD-L1160 | retention 期間、cleanup / deletion 方法は未確定 | unresolved list 2 | 未解決 list 2 | `NO_FINDINGS` |
| SDD-L1161 | crash 直前の Log durability 保証範囲は未確定 | unresolved list 3 | 未解決 list 3 | `NO_FINDINGS` |
| SDD-L1162 | Runtime / Job / Adapter / Error の最低限識別情報は未確定 | unresolved list 4 | 未解決 list 4 | `NO_FINDINGS` |
| SDD-L1163 | 環境・domain 分離の partition / path は未確定 | Environment 末尾および unresolved list 5 | 環境の分離末尾および未解決 list 5 | `NO_FINDINGS` |
| SDD-L1164 | 既知項目以外の禁止・masking 範囲は未確定 | 禁止情報末尾および unresolved list 6 | 記録禁止末尾および未解決 list 6 | `NO_FINDINGS` |
| SDD-L1165 | filename / format / schema / logging library は未確定 | unresolved list 7 | 未解決 list 7 | `NO_FINDINGS` |

## Formal Identifiers

translation contract の protected identifiers 21件、protected literals 7件、protected path 1件、計29件は、English と Japanese の双方に同一文字列で存在する。`Application Log`、`Canonical State`、`Canonical Commit`、`Storage Fail Closed`、`Runtime Identity`、`TEST` / `PAPER` / `LIVE`、`Asia/Tokyo`、`§2.6` / `§4` / `§28`、`logs/application/YYYY-MM-DD/` を含め、省略・翻訳・置換はない。protected state names と protected numeric values は空である。

Fresh Translation repair 前に破損していた設計参照記号は修復され、`§2.6` / `§4` / `§28` は protected literals として両言語で正確に保存されている。

## 未確定性、非圧縮、非一般化

- 未確定事項7件は English / Japanese とも7個の独立 list item として保持され、固定要件へ解決されていない。
- 保持期間、追加禁止・masking 範囲、partition / path は、適用箇所の本文でも未確定と明記されている。
- 禁止情報6件は個別 item として非圧縮である。ただし、そのうち `unredacted debug dump` は Japanese で `未編集のデバッグダンプ` に一般化されており、R-01 の対象である。
- 失敗分離の通常条件と Storage Fail Closed 条件は別段落、3種類の環境分離要件は個別文として保持されている。これらに意味の圧縮・一般化は確認されない。
- English と Japanese はともに5つの同対応 subheading、13 bullet を持ち、paragraph correspondence と list item count は一致する。
- Coverage ID、SDD location、parser field、assignment metadata は Human-facing 本文に露出していない。
