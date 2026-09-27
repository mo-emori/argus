# Context encoding boundary

`context_unicode_gate.py` establishes a machine-owned boundary before Writer handoff:

- decode bytes with strict UTF-8;
- require byte-for-byte UTF-8 round-trip;
- traverse every JSON string without rewriting it;
- report U+FFFD;
- detect values that can be losslessly recovered by reversing a UTF-8-as-CP932 misdecode;
- require authority comparison before classification or repair.

The detector never substitutes characters and contains no stage-specific replacement. Correct Japanese, `§`, and U+301C pass unchanged. Invalid bytes fail closed. A detected recovery candidate is Evidence only; it is not an automatic fix.
