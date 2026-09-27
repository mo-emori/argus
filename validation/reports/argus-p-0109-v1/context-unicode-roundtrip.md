# Context Unicode round-trip

Section 3.1 Context decoded strictly as UTF-8 and re-encoded to identical bytes.

- Context SHA-256: `9e25d939e89ed7fe06257604d4ed98fa9a7d7eb5c0f2ced274d4e9511236138d`
- Stage value: `17〜18`
- Stage code points: U+0031 U+0037 U+301C U+0031 U+0038
- Stage UTF-8: `31 37 e3 80 9c 31 38`
- Reference: `§49`
- Reference code points: U+00A7 U+0034 U+0039
- Reference UTF-8: `c2 a7 34 39`
- Strict decode: PASS
- Byte round-trip: PASS
- Source/normalized binding: PASS

There is no justification for changing the Context artifact.
