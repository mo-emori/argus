# Section 3.5.2 Regression Review

## Final routing result

`FAIL`

The first translation preserved protected values and passed the mechanical and Human-facing gates, but independent Semantic Review found that `外部接続アダプター（Adapter）` narrowed the English `Adapter` concept. Formal routing returned `FAIL` for that blocking finding and for a reviewer-side Translation Contract digest binding mismatch. The one permitted full-section repair removed the wording-level narrowing by using non-narrowing Japanese loanword correspondences.

The repaired draft then changed protected references `§2.6`, `§4`, and `§28` into mojibake forms (`ﾂｧ2.6`, `ﾂｧ4`, `ﾂｧ28`). Translation Preservation therefore returned `MISSING / PROTECTED_VALUE_CHANGED`. The repair limit was exhausted, so no additional repair or string patch was allowed.

## Regression meanings

The repaired prose retains the following substantive meanings in readable form:

- Application Log remains separate from Canonical State, Fact, Event, and Audit Record.
- It must not replace canonical information, and deletion must not lose canonical design information.
- Daily rotation remains bound to `Asia/Tokyo`.
- Storage priority remains below Canonical State, Commit, and Audit, with a finite but unresolved retention period.
- An Application Log-only write failure remains isolated from canonical processing; shared storage danger still applies Storage Fail Closed.
- Six prohibited information categories remain present; `unredacted` now retains masking/redaction-specific meaning.
- TEST / PAPER / LIVE and Development / Runtime separation remain present.
- All seven unresolved implementation-choice bullets remain unresolved.

However, the protected cross-reference loss is a blocking regression. The final draft is not accepted.
