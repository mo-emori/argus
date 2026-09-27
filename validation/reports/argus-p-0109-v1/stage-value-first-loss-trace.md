# Stage value first-loss trace

Authority value: `17〜18` (`17`, U+301C WAVE DASH, `18`; UTF-8 `31 37 e3 80 9c 31 38`).

| Boundary | Locator/artifact | Observed value | Status |
|---|---|---|---|
| Design Source | lines 3524–3525 | separate stages `17. Realtime Paper Test` and `18. Live Readiness Review` | PRESERVED authority semantics |
| Structured Design Data | line 1562 / `SDD-L1562` | `17〜18` | PRESERVED |
| Parser normalized unit | `SDD-L1562` | `17〜18`, U+301C, UTF-8 `e3 80 9c` | PRESERVED |
| P-0087 Planning | section 3.1 unit | `17〜18` | PRESERVED |
| P-0091 Section Context / Writer input | line 179 | `17〜18` | PRESERVED |
| P-0108 initial English Writer output | stage table | `17–18`, U+2013 EN DASH | **FIRST SEMANTIC LOSS** |
| P-0108 reviewer Evidence | finding description | `17窶・8` | **DISPLAY/READ MISDECODE**, not stored Context content |

No Source→Context encoding corruption exists. The first content change is Writer normalization from the protected U+301C literal to U+2013. Separately, the reviewer observation path rendered the correct UTF-8 bytes as CP932-style mojibake and incorrectly attributed that display corruption to the Context.

The P-0108 repair file contains `17〜18` and `§49`, but P-0109 does not validate or promote it because its Fresh Session ended without completed provenance.
