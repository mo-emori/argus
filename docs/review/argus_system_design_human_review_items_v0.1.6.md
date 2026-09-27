# ARGUS Human System Design v0.1.6 Human Review事項

**対象HSD:** `docs/design/argus_system_design_v0.1.6.md`  
**Coverage Map:** `docs/review/argus_system_design_coverage_map_v0.1.6.md`  
**状態:** STOP Human Review

変換中に、SDDで未確定のまま保持するよう明示された事項を確認した。以下は欠落を推測で埋めず、HSD §10「継続検討事項」へ配置したCoverage Unitである。Human Reviewでは、未確定の維持が適切か、別のDesign Authority判断が成立済みでないかを確認する。

| Coverage ID | Human Review事項 | 現在の扱い |
|---|---|---|
| CU-0325 | Runtime Identityの物理filename、discovery、厳密型 | 後続Contractで確定する未確定事項として維持 |
| CU-0326 | 内蔵SSDに保持するrecent backup世代数N | TBDとして維持 |
| CU-0327 | point-in-time historical dataの十分性 | 未確定として維持 |
| CU-0328 | News / Web Provider | 将来Providerとして維持 |
| CU-0329 | Strategyごとのrequired latency | 運用設定として維持 |
| CU-0330 | 各Policy数値、Budget、通知、Retention等 | `UNCONFIGURED`として維持 |
| CU-0331 | SQLite / Parquetの選択とServer移行 | 将来Break候補として維持 |
| CU-0332 | Declared Reason Weightの正式較正方法 | 将来検討として維持 |
| CU-0333 | System Critical Override | 初期`UNCONFIGURED`として維持 |
| CU-0334 | Application Log保持期間 | 未確定として維持 |

Coverage Map上の`REVIEW`は10件である。Design Source / SDD間の新たな矛盾、参照不能な必須Authority Artifact、意味を変えずに配置できない追加事項は、今回の変換では検出していない。この記述はH1〜H10の受入PASSを意味しない。H1〜H10の最終判定はHumanが行う。

Human Review完了前にFreezeしない。

**STOP Human Review**
