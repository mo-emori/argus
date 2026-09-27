# Regression Comparison

同一の Human-facing Gate を既存 accepted / known-bad artifact に再適用した。

| Artifact | 期待 | 結果 | 主要指標 |
|---|---:|---:|---|
| P-0090 section 3.4 | PASS | PASS | 4,118字、9小節、5表、1図 |
| P-0088 section 2.1 | PASS | PASS | 733字、2小節、1表 |
| P-0088 section 5.4 | PASS | PASS | 1,316字、3小節、3表 |
| P-0091 section 1.2 | PASS | PASS | 1,967字、5小節、1表 |
| P-0091 section 7.1 | PASS | PASS | 2,837字、6小節、2表、1図 |
| P-0091 section 3.1 | PASS | PASS | 2,030字、5小節、2表、1図 |
| P-0092 known-bad section 0 | FAIL | FAIL | context field exposure / writer meta prose |
| P-0092 known-bad section 9 | FAIL | FAIL | context field exposure / writer meta prose |

P-0095 Major Chapter 3 は 10,391字、6 child section、8表、2図で PASS。既存 accepted artifact を拒否せず、known-bad artifact を誤受入しないため、gate regression は PASS とする。

