# P-0101 / P-0103 Comparison

| Viewpoint | P-0105 observation |
|---|---|
| Meaning preservation | Independent Semantic Review returned PASS with PRESERVED-only findings. |
| Explanation | Runtime / Job / Adapter / Error receive Japanese loanword correspondences without narrowing their scope. |
| Japanese naturalness | The opening is readable Japanese rather than a bare sequence of English concepts. |
| Technical precision | `unredacted` is described as lacking masking or concealment, avoiding P-0101's generic `未編集`. |
| Protected values | `§2.6 / §4 / §28`, TEST / PAPER / LIVE, `Asia/Tokyo`, and `logs/application/YYYY-MM-DD/` are exact. |
| Mojibake | P-0103's `ﾂｧ` corruption is absent; `§` remains U+00A7 with UTF-8 `c2 a7`. |
| Redundancy | First-use explanations are localized; later occurrences retain concise original terminology. |
| Unresolved matters | Seven unresolved choices remain independently listed and unresolved. |
| Information volume | Six prohibited categories, seven unresolved choices, failure behavior, and environment separation remain present. |

P-0103 remains an unchanged FAIL artifact and was used only after all P-0105 gates for observation, not as Translator or Reviewer input.
