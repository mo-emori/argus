# Section 3.5.2 Comparison with ARGUS-P-0098-v1

- 判定: `FINDINGS`
- 比較対象: P0101 の English / Japanese と、P0098 `section-3.5.md` 内の 3.5.2 subsection
- 判定方針: 差分を事実と本文根拠で記録し、総合的な「改善」または「改悪」は自動判定しない

## 比較結果

| 観点 | P0098 evidence | P0101 evidence | 比較所見 |
|---|---|---|---|
| 意味保存 | rotation、禁止6件、canonical artifact 代替禁止、削除安全性、保存優先度・有限保持、書込み失敗分離、Storage Fail Closed、環境分離、未確定7件を日本語 subsection 内に保持。禁止対象は `未redactのdebug dump` | 同じ意味を English / Japanese の両方で個別展開するが、Japanese は English の `unredacted debug dump` を `未編集のデバッグダンプ` とする | 共通の設計意味は原則保持されるが、redaction / masking に固有の禁止対象は P0101 Japanese で一般化されている。storage path と設計参照は P0101 で追加明示され、参照記号は修復済み |
| 英語過多 | 日本語本文で `Artifact`、`Daily rotation`、`retention`、`cleanup / deletion`、`Storage`、`redact`、`masking`、`partition / path`、`crash`、`Log durability` 等の一般説明語も英語表記 | Japanese は一般説明を `アーティファクト`、`日次ローテーション`、`保持期間`、`クリーンアップまたは削除`、`ストレージ障害`、`マスキング`、`パーティション方式またはパス方式`、`クラッシュ直前`、`ログの耐久性保証` とする。contract 上の protected identifiers は英字のまま | Japanese における非保護の英語表記は P0101 の方が少ない。P0101 English は英語 source draft であり、この「英語過多」比較の負例とは扱わない |
| 日本語自然性 | 簡潔だが、`別Artifact`、`投資Canonical処理`、`未redactのdebug dump`、`Log durability保証範囲` など日英混在が連続する | 一般概念を日本語化し、助詞と文を補っている。例: `正本となる投資処理`、`ログの耐久性保証の範囲` | P0101 は文章表面上の日本語連続性が高い。ただし `unredacted` を自然さだけで `未編集` とした箇所は、redaction の技術的意味を失っている |
| Formal Identifier | `Application Log`、`Canonical State`、`Event`、`Storage Fail Closed`、`TEST / PAPER / LIVE` 等を保持。storage path と `§2.6` / `§4` / `§28` は subsection にない | translation contract の protected identifiers 21件、protected literals 7件、protected path 1件を両言語で保持 | Fresh Translation repair により Japanese の `§2.6` / `§4` / `§28` を含む全29 protected value が正確に保存されている |
| 構造 | heading 1、bullet 4。主要規則は5段落、未確定事項のうち4件を末尾 list、残る3件を対応段落に配置 | 各言語とも heading 6、bullet 13。5つの主題 subheading、禁止6件の list、未確定7件の list | P0101 は規則群と未確定事項をより細かく独立表示する。P0098 は短い一続きの subsection として提示する |
| 未確定事項 | retention / cleanup、追加禁止 / masking、partition / path を各本文で、生成主体等・durability・最低限識別情報・format 等を4項目 list で保持 | 7件すべてを未確定 list に列挙し、前3件は関連本文でも未確定と再掲 | 両版とも未確定性を解決していない。P0101 は一覧の完全性を視覚的に確認しやすいが、関連本文との重複が増える |
| 情報量 | 対象 subsection は956 characters、heading 1、bullet 4。storage path と設計参照は記載なし | English は2867 characters、heading 6、bullet 13。Japanese は1637 characters、heading 6、bullet 13。`logs/application/YYYY-MM-DD/` と `§2.6` / `§4` / `§28` を追加明示 | P0101 は二言語化、明示的 subheading、個別 bullet、path・参照の追加により情報の明示量が多い。文字数増加だけでは品質改善とは判定しない |

## Findings

### C-01 P0101 Japanese の redaction 意味の一般化

P0098 の `未redactのdebug dump` と P0101 English の `an unredacted debug dump` は、いずれも redaction 未実施を禁止条件として特定する。P0101 Japanese の `未編集のデバッグダンプ` は編集一般の未実施を表し、秘密情報の除去・伏字化という redaction 固有の条件を特定しない。このため、英語量と引き換えに設計意味を一般化した比較上の退行である。

### C-02 比較上の非対称性

P0098 の許可比較範囲は日本語 subsection だけであり、P0101 は English と Japanese の対である。このため、二言語間の保存性は P0101 内では検証できるが、P0098 との English 品質の直接比較はできない。

## 非自動改善判定

P0101 には、一般説明語の日本語化、構造の細分化、未確定7件の一覧化、path・設計参照の明示、全 protected value の正確な保存という差分がある。同時に Japanese の redaction 意味の一般化と、再掲による文章量増加がある。以上は観測可能な差分として記録し、P0101 が P0098 より総合的に改善したかどうかの最終判断は Human に残す。
