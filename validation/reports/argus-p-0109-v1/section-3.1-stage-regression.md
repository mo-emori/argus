# Section 3.1 stage regression

Regression coverage verifies:

1. `17〜18` and `§49` survive strict UTF-8 decode and byte round-trip.
2. A fixture produced by decoding the UTF-8 bytes as CP932 is detected and recoverable for authority comparison, but is not automatically rewritten.
3. Invalid UTF-8 fails closed.
4. U+FFFD is reported.
5. The real 39 Context scan contains no candidate.

The authority value and stored Section Context are exactly equal. The initial P-0108 English draft remains unchanged and continues to show the Writer-level U+2013 substitution.
