# Section 3.5 Local Structure Review

## 判定

P-0097本文は意味を完全保存しているが、3.5.1のAuthority一覧後にApplication Logの詳細が連続し、親一覧と独立Artifact仕様の説明粒度が混在している。3.5.2もBackupの構成・媒体・鮮度と、Restore / Reconciliationの手順を同じ説明単位に置いているため、読者が平常時の保全と障害後の復旧を切り替えにくい。

## 採用する最小構成

1. `3.5.1 保存対象とAuthority`
   - 保存対象一覧とAuthority表だけを中心に置く。
2. `3.5.2 Application Log`
   - Canonical / Auditとの境界、rotation / retention、書込み失敗、記録禁止、環境分離、未確定事項を一つの独立説明単位にする。
3. `3.5.3 Backup`
   - Canonical commitとの結合、snapshot、媒体責務、N世代未確定、鮮度監視、Secret平文禁止を扱う。
4. `3.5.4 Restore / Reconciliation`
   - Restoreから照合、Correction / missing Fact、確認済み差分Commit、通常運用復帰条件までを手順として扱う。
5. `3.5.5 Data Root、容量監視および保存形式`
   - P-0097の旧3.5.3本文を意味・順序・表内容とも変更せず、前段の分割に伴う番号だけを変更する。

## 不変条件

- 内容短縮を目的とせず、P-0097の66 Coverage Unitをすべて維持する。
- Application Log、Backup、Restore / Reconciliationを統合・一般化しない。
- Section 3.4とFull HSDは変更しない。
- Source / SDD / Context / Coverage Contract、Writer Architecture、Coverage Architectureを変更しない。
- 新しい理由、因果、状態、固定値を追加しない。
- Formal Identifier、禁止、不変条件、未確定事項、R-05、R-06を維持する。

