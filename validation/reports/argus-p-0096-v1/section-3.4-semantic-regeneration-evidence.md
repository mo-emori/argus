# Section 3.4 Semantic Regeneration Evidence

- regeneration count: 1（上限）
- before writer session: `ARGUS-P-0096-v1:section:3.4:writer:01`
- after writer session: `ARGUS-P-0096-v1:section:3.4:writer:02`
- before draft SHA-256: `8992755b2eae5a01111ae5e1a2e97367b6744ea81919c14025d5d9b757e11032`
- before output artifact SHA-256: `77ca67de1b7897039195ae1992a0f3d83a50cba2d7c0719ae393766b6f3b89b4`
- failure: PRESERVED 63 / MISSING 1 / DISTORTED 46 / INVENTED 0
- classification: 47件すべて、Coverage Contractに存在する個別対応・参照先の復元であり、新規Design judgmentは不要
- method: 部分文字列patchではなく、Section Coverage ContractからSection全体をFresh Writer Sessionで再生成
- strengthened contract rule: 表形式Unitの定義・区分・意味・禁止/境界・利用先・参照先を個別に保存する
- re-gate: PASS（PRESERVED 110 / その他 0）
