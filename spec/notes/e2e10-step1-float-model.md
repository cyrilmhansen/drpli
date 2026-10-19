# E2E-10 STEP 1 — FLOAT BINARY(24) value-model characterization (no compiler change)

Date: 2026-10-20.  Baseline commit: `29fe3fb` (assessment) on top of `07ff3ce`
(DECPOLY, 6/41).  Scope, as approved: **characterize the representation only**.
`ocaml/` was not touched; `tools/` gained exactly one file, `floatmodel.py`
(model + self-tests + pool validator).  Laws are banked as **C100** (format) and
**C101** (literal conversion, rounding, pool rules); this file records coverage
and what is still open.

## 1. Probe coverage (exact)

Sources `e13src/R30xx.PLI` (25 files, new provenance tree; nothing duplicated
from `e12src/`/`e12b/`).  DR runs: `oracle/batch.py --tag e2e13 --switches
'$L$C$D'`, so every `.PRN` carries the source listing **and** the instruction
trace.  23 specimens produced `.REL`; 4 were rejected in pass 2 and are
themselves the boundary evidence.

| specimen | what it pins | outcome |
|---|---|---|
| FLTPOLY (corpus re-run) | float mirror of DECPOLY: GET tail, compare, `&`, descriptor ABI, `?FPRET` | REL + trace |
| FFACT (corpus re-run) | `?QI15F`, `?FM44S`, `?QFCSS`, recursive float return, DO REPEAT | REL + trace |
| R3001 | cell = 4 bytes; `float` == `float binary(24)`; literal pool cells precede variables | REL |
| R3002 | `?QI15F` / `?QFI15` conversions, `?QFCMS` PUT form | REL |
| R3003 | `?FA44M ?FS44M ?FM44M ?FD44M`, `?FX44S` store | REL |
| R3004 | float GET LIST ×2, `?FC44M` for `>` and `=` | REL |
| R3005 | arity-1 float formal (2-byte pointer cell) + float return | REL |
| R3006 | **fraction byte ordering**: 1+2\*\*-16 → `80 00 00 81`, 1+2\*\*-23 → `01 00 00 81` | REL |
| R3007 | **sign/zero**: `-1.5` → `00 00 c0 81`; `0`, `0.0`, `-0.0` share one `00 00 00 00` cell (no negative zero) | REL |
| R3008 | E-notation (`3E7`, `1E-20`), exponent byte 62 for 1E-20, `127.5` | REL |
| R3009 | normalization at powers of two (`0.5` → exp 128, `0.25` → 127, `0.9375` → `00 00 70 80`) | REL |
| R3010 | mantissa capacity 2\*\*24-1/2\*\*24/**2\*\*24+1 (tie → up)**; dedup with 2\*\*24+2 | REL |
| R3011 | non-exact decimals: `0.1` `0.2` `1.1` `3.14159` `12345.678` (nearest) | REL |
| R3012 | 14-digit literals near a half-ulp — **not** true ties (see §3) | REL |
| R3013 | `float binary(14)` also gets a 4-byte cell; shares the `1.5` literal cell | REL |
| R3014 | quarter-ulp and near-tie cases (`33554433` → down = nearest) | REL |
| R3015 | `1E38` and `1E-38` compile, `1E-45` → pass-2 `CONVERT` | no REL (evidence) |
| R3016 | `1E39` → `CONVERT` | no REL (evidence) |
| R3017 | `1E-60` → `CONVERT` | no REL (evidence) |
| R3018 | sign with top fraction bits set: `-1.75` → `00 00 e0 81`, `-127.5` → `00 00 ff 87`, `-0.1`, `-3E7`, `-0.5` | REL |
| R3019 | range extremes that are legal: `1E38` (byte 255), `1E-38` (byte 2), `1E-37` | REL |
| R3020 | **exact integer ties, including negative**: ±16777217, ±16777219, 50331649 | REL |
| R3021 | DR reads ≥16 significant digits (`1.0000000596046448` → up vs `…64` → down) | REL |
| R3022 | `3E-39` → exponent byte 1 | REL |
| R3023 | `2E-39` → exponent byte **0** is a legal normal characteristic | REL |
| R3024 | `1.6E38` → byte 255 accepted | REL |
| R3025 | `1.8E38` → `CONVERT` (upper boundary is 2\*\*127) | no REL (evidence) |

## 2. Result — the representation is fully characterized for literals

`tools/floatmodel.py` (pure Python, `Fraction`/`Decimal`, exact arithmetic):

    floatmodel selftest: 43 assertions passed
    pool validation: 60/60 float-literal cells reproduced byte-exactly,
                     0 mismatch, 3 non-float pool cells excluded

The three excluded cells are STRING literals sharing DR's literal pool
(`20 20 20 20` = `'    '`, `54 79 70 65` = `'Type'`) — the validator classifies
them explicitly instead of counting them as float tests.  Self-tests include the
non-exact decimal constants (`0.1`, `0.2`, `1.1`, `3.14159`, `12345.678`), the
precision-boundary integers (2\*\*24-1 … 2\*\*24+3), all four exact ties, sign
forms, zero/`-0.0`, and the four out-of-range literals (which must *raise*).

Format (see C100): little-endian 23-bit fraction in bytes 0..2 with an implied
leading one, sign in byte 2 bit 7, characteristic in byte 3 with bias 129;
zero = all bytes zero; range |v| ∈ [2\*\*-129, 2\*\*127); no subnormals; no
negative zero.  Rounding = nearest, **ties away from zero** (C101), which agrees
independently with the DECIMAL tie law C087.

## 3. Two of my own errors, caught during step 1

1. I first read the sign as living in the exponent byte, because I mislabelled
   which byte was the fraction's top byte: `3E7` is stored `c0 e1 64 99` and I
   took `c0` to be the top byte.  DR prints bytes in address order — byte 0 is
   the *low* fraction byte.  With that corrected, `-1.5` → `00 00 c0 81` and
   `-1.75` → `00 00 e0 81` put the sign unambiguously in byte 2 bit 7.
2. I nearly reported "DR's 1E-37 literal is wrong" (my hand arithmetic gave
   1.25e-37 from `ea 1c 08 06`).  Recomputing with the model gave exactly
   1.000000e-37: my mental value of 2\*\*-123 was wrong.  Given the DECPOLY
   retraction, I recorded this one as a self-check rather than a defect claim —
   the rule now is that a DR-defect assertion needs the model's arithmetic, not
   mine, and a quoted source line.
   Related: my first "tie" probes (R3012) were not ties at all — a 14-digit
   decimal cannot land exactly on a half-ulp of a binary32-style number.  R3020
   used exact integer ties instead, which is what settled the tie direction.

## 4. What step 2 (assignment/store subset) still needs

Nothing about the representation blocks it.  Open items are lowering, not
encoding, and are listed verbatim in C101's UNRESOLVED block: the
`?FA44M/?FA44S/?FA44L` operand-mode rule, `float binary(14)` computed precision,
runtime tie behaviour of the PLILIB routines (irrelevant to `.REL` identity,
relevant to console equality only through the shared library), and whether DR
ever produces a subnormal at runtime.

Planned order, unchanged: assignment/store subset → FFACT → FLTPOLY → TEST.

## 5. Acceptance state of the build during step 1

`float` declarations still fail loud in codegen, unchanged from before step 1:
`codegen: declared variable kind not in supported subset [TBD]: FLOAT
BINARY(24,0)`.  No probe from this step is registered as an e2e positive (the
compiler cannot compile them yet), so the gate stays exactly where slice 6 left
it: 211 byte-exact / 211, negative panel 51/51, corpus 6 EXACT / 0 DIFFERS /
35 REFUSED.
