# ARGUS-P-0114-v1 Cleanup Summary

- Final HSD: `docs/design/argus_system_design_v0.1.md`
- SHA-256: `980c90feadd6f0e868028a8d86adee74d1d42470b05285315de95557369aa014`
- P0113 Full Candidateとの一致: PASS（既知hash一致）
- HSD本文の再生成・改善: なし

## oldへ移動

- `docs/design/argus_system_design_v0.1.md` の旧内容、および `v0.1.1`〜`v0.1.6`: `docs/old/design/`
- `docs/model/argus_structured_design_model_v0.1.1`〜`v0.1.3`: `docs/old/model/`
- 旧Structured Design Model Prompt 7件と旧System Design Prompt 7件: `docs/old/prompts/`

現行Promptとして `argus_structured_design_model_prompt_v0.2.md` と `argus_structured_design_model_transformation_prompt_v0.1.6.md` を保持した。

## 削除

- 参照不要なHSD生成・PoC report 21ディレクトリ
- `work/argus-p-0088-v1`〜`argus-p-0091-v1`
- `docs/model/work/`
- `docs/design/argus_system_design_v0.1.6_planning.md`

## 参照により保持

現行Skill scripts/testsから直接参照される `validation/reports` 12ディレクトリを保持した: P-0085、P-0087、P-0092、P-0095〜P-0098、P-0101、P-0103、P-0105、P-0109、P-0110。

削除した `work/` 回帰入力へのactive test参照を検出したため、同じ Human-facing Gate の受入済み回帰目的を維持したまま、保持対象report内の受入済みSection artifactへ参照を付け替えた。また、PoC-0既知不良fixtureの参照先を移動後の `docs/old/design/` へ更新した。Skill testは183件PASS。

## 保護・未解決事項

- Design Source、Structured Design Data、現行Structured Design Model、contracts、development管理文書、src、tests、現行Skill、baselines、evidence、metricsを保持。
- execution ledger: `validation/metrics/codex-execution-ledger.json` 1ファイルのみ。
- broken live reference: 0。
- unresolved cleanup item: なし。
- Freeze / Capability Closure: 実施なし。
