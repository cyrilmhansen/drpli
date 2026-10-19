# golden/e2e12c -- DR code-trace goldens for the FIXED BINARY peephole discovery (C099)

Compiled with `oracle/batch.py --switches '$L$C$D'` (source listing + code trace
+ disk print), so each `.PRN` carries DR's instruction-by-instruction lowering.

| specimen | purpose | status against my build |
|---|---|---|
| R2043 | multi-clause `%replace` (comments between clauses), used in `+` | DIFFERS -- cause is fixed-bin `lit + lit` (C099 rule 1), NOT `%replace` |
| R2045 | control for R2043: same program, literals written inline | DIFFERS identically to R2043; R2043/R2045 code traces are IDENTICAL, which proves `%replace` is textual (C097) |
| R2046 | multi-clause `%replace` in shapes my build supports | DIFFERS -- `n * 2` is `DAD H` in DR (C099 rule 4) |
| P044 | fixed-bin literal/identity arithmetic battery | DIFFERS -- source of rules 1, 3, 5 |

None of these is a gate positive.  Their role is to pin the four peepholes as
tested refusals (N56-N60) instead of silent divergence.  Sources live in
`probes/`.
