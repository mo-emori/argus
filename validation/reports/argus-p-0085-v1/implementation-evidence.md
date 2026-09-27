# ARGUS-P-0085-v1 Implementation Evidence

## 1. Skill root と tree

Skill root は `.codex/skills/argus-hsd-generation/` である。開始時点では IDE 表示にあった `.codex/skills/argus-hsd-generator/SKILL.md` は filesystem 上に存在しなかったため、Prompt 指定の名称で新規作成した。

```text
argus-hsd-generation/
├── SKILL.md
├── DESIGN.md
├── references/
│   ├── contracts.md
│   ├── exact_values.json
│   └── planning_artifact.example.json
├── scripts/
│   ├── contracts.py
│   ├── coverage.py
│   ├── gates.py
│   ├── planning.py
│   ├── poc0.py
│   ├── sdd_parser.py
│   └── semantic_review.py
└── tests/
    ├── conftest.py
    ├── fixtures/
    │   ├── poc0_known_failure.json
    │   └── poc0_known_failure.md
    └── test_skill.py
```

## 2. DESIGN.md の章

目的と非目的、Authority、全体パイプライン、SDD Parser、Parser Self-Coverage、Section Context、Planning Artifact、Human Approval Gate、Writer Interface / INV-01、Coverage Ownership / INV-02、日本語 Gate、Exact Value Gate、Semantic Review Interface、PoC-0 回帰、未実装範囲と停止条件の15章を定義した。

## 3. DA-0007 finding 対応

| Finding | 実装 |
|---|---|
| S-01 | 全非空行の単一分類と self-coverage、異常時 fail closed |
| S-02 | Section Context、Planning Artifact、digest 拘束 Human Approval Gate |
| S-03 | 既知失敗 fixture に対する PoC-0 回帰 |
| S-04 | canonical / accepted / label / locator を持つ共有 Exact Value 定義 |
| S-06〜S-08 | Context に authority、boundary、cross reference、owner、diagram plan、depth を保持 |
| S-09 | `FINDINGS / NO_FINDINGS` の独立 Semantic Review interface |
| S-11 | 課題・目的空欄を Planning error として検出 |
| S-15 | SKILL.md は実行境界に絞り、詳細を DESIGN / references へ分離 |

## 4. PoC-0 対象と選定理由

DA-0007 は draft3 について Latin 1114、読点3個以上78文、5個以上36文、具体値が実質 `一か月` のみと記録する。一方、repo に現存する `docs/design/argus_system_design_v0.1.6.md` の再計測値は Latin 1356、読点3個以上97文、5個以上44文であり、同一 snapshot と確認できなかった。git history にも draft3 artifact は存在しない。

このため既存 HSD を誤って draft3 と断定せず、DA-0007 の既知失敗特性を最小再現した `tests/fixtures/poc0_known_failure.md` と provenance metadata を回帰 fixture とした。PoC-0 は Latin overuse 46、具体値2件欠落、長文1件、課題・目的2件欠落を検出した。

## 5. Parser self-coverage

実 SDD `docs/model/argus_structured_design_data_v0.1.md` を解析した結果は次のとおりである。

| 指標 | 件数 |
|---|---:|
| total candidates | 1284 |
| recognized | 1284 |
| unrecognized | 0 |
| ambiguous | 0 |
| duplicate assignments | 0 |
| unassigned | 0 |
| heading / label / list / table row / separator | 104 / 408 / 73 / 621 / 78 |

## 6. Planning sample と Human gate

`references/planning_artifact.example.json` に課題、目的、設計事項、具体値ID、Actor/Authority、Boundary、関係、owner、locator、coverage、depth を持つ1節の例を置いた。承認状態は意図的に `PENDING` であり、自動承認していない。

Gate は Planning error、非APPROVED、空承認者、AI系承認者、digest不一致、不正日時を拒否する。Human承認済み digest と一致した場合だけ WriterAuthorization を返す。

## 7. Invariant test

- INV-01: WriterInput の field を closed set にし、`raw_sdd`, `sdd_path`, `source_text`, `raw_source` を runtime でも拒否する。
- INV-02: frozen CoverageEntry の tuple snapshot だけを LLM-facing interface に公開し、更新は Python CoverageLedger のみが行う。

## 8. Gate と Semantic Review

日本語 Gate と Exact Value Gate は同じ `ExactValue` tuple から accepted token を得る。Semantic Review は機械 Gate failure を迂回できず、`PASS` を持たない closed verdict を使用する。

## 9. 試験結果

| Verification | 結果 |
|---|---|
| skill quick_validate | PASS |
| Skill pytest | 12 passed |
| repo pytest | 215 passed、pytest cache 作成権限 warning 1件 |
| ruff (`src tests skill`) | PASS |
| pyright strict (skill) | 0 errors |
| bandit (`src` + skill scripts) | PASS |
| pip-audit | No known vulnerabilities found |
| repo全体 pyright | FAIL: 既存 component test の private usage / unknown lambda type 7件 |

repo全体 pyright の7件は `tests/component/test_data_root_marker_store_contract.py` にあり、本変更対象外である。隠さず既存 finding として残す。

## 10. Artifact hash

以下は ARGUS-P-0085-v1 初回完了時点のbaseline hashである。後続の添付指示によるPoC-0実装で `SKILL.md`、`sdd_parser.py` 等が更新されたため、現在値として使用してはならない。PoC-0の現行成果物は `poc0/regression-summary.md` と各reportを参照する。

| Artifact | SHA-256 |
|---|---|
| `SKILL.md` | `7bf01d569e04cb6a5e84bbdbb534bb0b26e49624cb91d40818a5e3b94988c24b` |
| `DESIGN.md` | `46b85acd3802481a69bc1c1d545531fec59930f25fa6a51135f7b4b12dea0d00` |
| `references/contracts.md` | `6afbe7ad5ed791196961e6a8657a2c90ca67fd5e4e0292c57cfed734143c5e67` |
| `references/exact_values.json` | `8973a2272ec55475d90db316dbf65c07110917279c4a8f57221044302ef96104` |
| `references/planning_artifact.example.json` | `82caf253342366fa85a620110eb85fdbd14390df66269e2c754e9f91b11d4c5a` |
| `scripts/contracts.py` | `cbfe40830b442708d495c16d64edd56b49626f4d4355852e5d51899c664982ae` |
| `scripts/coverage.py` | `b23ff25831a397c783a03d2fafbb513e14212a986c954a0a8334e8a189237888` |
| `scripts/gates.py` | `b756f19c18f757da8046795701339e94ba5a4c2b6ff98a9fcbb9903c2dc84d35` |
| `scripts/planning.py` | `738801b0378cfaa5a9df495d01da909072a2cc23a6d34437857b47fc706ab35c` |
| `scripts/poc0.py` | `e1d692aaa5e1161de51c95bc240aa37286e9fad504c7319e05c6aa2e09290ff6` |
| `scripts/sdd_parser.py` | `fdea077a1ff2be6d5615c1b74ca82874df759c36223129d8f18547595c5002aa` |
| `scripts/semantic_review.py` | `a5bcabcd4257d7c8b022f4df531d25ed3633a8c894898c78ffc9532c6af11220` |
| `tests/conftest.py` | `c8067f7fbd82f71e877be2fc69a5676fe0a050a20e03c290610406528fd8db2d` |
| `tests/fixtures/poc0_known_failure.json` | `89a74f8dab78544b37da8b4a497f75a940675acbcbd7c5282b0f615d3704c5df` |
| `tests/fixtures/poc0_known_failure.md` | `6e67b2eea01f79107aae763bee272b4cc6431ac6a4536afc7ff5871b899d9039` |
| `tests/test_skill.py` | `64c8cec2b07256de21f6bf03528471bfc63dab400604a12474668a56a3a282ed` |

## 11. 未実装と停止

Section Writer、HSD assembly、final validator、repair loop、外部 API、有料 orchestration、完全な CV/RV、allowed terms governance、diagram optimization は未実装である。HSD は生成せず、Writer も起動していない。Human Approval は `PENDING` のままである。

## 12. Review handoff

独立 review では parser の分類境界、approval digest の canonicalization、fixture provenance、Gate threshold の妥当性、INV-01/02 の interface leakage を重点確認する。Semantic reviewer は finding を返すだけで、承認・coverage・機械 Gate を更新しない。
