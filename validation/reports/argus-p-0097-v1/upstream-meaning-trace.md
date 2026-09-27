# Upstream Meaning Trace

| Issue | Stage | Locator | Meaning present? | Representation | First loss? | Evidence |
|---|---|---|---|---|---|---|
| R-05 | Design Source | lines 366, 625, 629–633, 668, 2053 | Yes | SecretはOS保護領域から取得し、project通常ファイル、logs/evidence/reports/backupsへ出力せず、Backupへ平文で含めない | No | Source本文 |
| R-05 | SDD | lines 1103, 1141, 1288, 1655 | Yes | Secretの保存先、禁止対象、Application Log禁止、Backup平文禁止を表形式で保持 | No | SDD本文 |
| R-05 | Parser output | `SDD-L1103`ほか | Yes | table_rowとして全文保持 | No | `parse_sdd`結果 |
| R-05 | Section 3.4 Context | Planning Artifact | No | `SDD-L1103`がSection 0へ単独割当され、3.4 Contextにない | **Yes** | `SECTION_MAP["17.1"] == "0"` |
| R-05 | Coverage Contract / Writer Input / HSD | P-0096 | No | ContextにないためCoverage対象化されず、下流でも復元不能 | No（二次欠落） | P-0096 regression |
| SDD-L1158 | SDD | line 1158–1166 | Yes | 「未確定事項」ラベルと後続bulletに具体項目 | No | SDD本文 |
| SDD-L1158 | Parser output | line 1158–1166 | Yes | labelとlist_itemを別Unitとして保持 | No | `parse_sdd`結果 |
| SDD-L1158 | Section 3.5 Context | `SDD-L1158` | No | label本文だけを抽出して空文字とし、後続list_itemを無視 | **Yes** | `context_builder`のlabel/table限定処理 |
| SDD-L1293 | SDD | line 1293–1295 | Yes | 「規則」ラベルとBackup配置・監視規則 | No | SDD本文 |
| SDD-L1293 | Parser output | line 1293–1295 | Yes | labelとlist_itemを別Unitとして保持 | No | `parse_sdd`結果 |
| SDD-L1293 | Section 3.5 Context | `SDD-L1293` | No | label本文だけが空文字となり、後続規則を無視 | **Yes** | `context_builder`のlabel/table限定処理 |

Root Cause:

- R-05: Section 17.1「情報種別の分離規則」のPlanning割当がSection 0のみで、状態・データ責務の3.4へ届かない。
- SDD-L1158: Context Builderが空のラベル行をCoverage化し、後続list itemを取り込まない。
- SDD-L1293: 同じContext Builder欠陥。

