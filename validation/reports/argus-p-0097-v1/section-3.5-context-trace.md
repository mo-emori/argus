# Section 3.5 Context Trace

| Coverage ID | 分類 | Root Cause | Source/SDD状態 | 修正方針 |
|---|---|---|---|---|
| SDD-L1158 | C | Parser outputにはラベルと後続list itemがあるがContext Builderが空ラベルだけを採用 | 具体的な未確定事項はSDD lines 1159–1166に存在 | ラベル配下のlist itemを独立SourceElementとして取り込む |
| SDD-L1293 | C | Parser outputにはラベルと後続list itemがあるがContext Builderが空ラベルだけを採用 | Backup配置・監視規則はSDD lines 1294–1295に存在 | 同上 |

周辺情報からの推測ではなく、Parserが保持している原文をContextへ伝播する修正である。

