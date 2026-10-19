# golden/e2e13 -- E2E-10 ASSESSMENT evidence (FLOAT), oracle-only, no gate positives

Produced by `oracle/batch.py --switches '$L$C$D'` (source listing + code trace +
disk print) so every `.PRN` carries DR's instruction-level lowering.  Nothing in
this directory is registered as an e2e gate positive: the assessment deliberately
made **no compiler change**, so `float` declarations still fail loud in my build
(`codegen: declared variable kind not in supported subset [TBD]: FLOAT
BINARY(24,0)`).

| specimen | source | what it pins |
|---|---|---|
| FLTPOLY | corpus program re-run (mirrors DECPOLY) | float GET tail (`?QCXOP/?QX8F4/?FX44S`), float compare + `&` machinery identical to DEC, **multi-arg descriptor ABI byte-identical (`MVI C,06` block copy into 2-byte pointer cells)**, `JMP ?FPRET` |
| FFACT | corpus program re-run | `?QI15F` fixed->float, `?FM44S`, `?QFCSS` (width 14), recursive float return |
| R3001 | `e13src/R3001.PLI` | float cell = 4 bytes; `float` == `float binary(24)`; float literal = 4-byte pool cell (encoding samples) |
| R3002 | `e13src/R3002.PLI` | `?QI15F` / `?QFI15` conversions, `?QFCMS` PUT form |
| R3003 | `e13src/R3003.PLI` | `?FA44M ?FS44M ?FM44M ?FD44M` (M operand mode) + `?FX44S` store |
| R3004 | `e13src/R3004.PLI` | float GET LIST of two vars, `?FC44M` compare for `>` and `=` |
| R3005 | `e13src/R3005.PLI` | arity-1 float formal (pointer cell) + float return |
| R3006 | `e13src/R3006.PLI` | fraction byte ORDER: 1+2\*\*-16 and 1+2\*\*-23 both land in byte 0 |
| R3007 | `e13src/R3007.PLI` | sign bit in byte 2 bit 7; `0`, `0.0`, `-0.0` share one all-zero cell (no negative zero) |
| R3008 | `e13src/R3008.PLI` | E-notation literals, exponent byte 62 (1E-20), 127.5 |
| R3009 | `e13src/R3009.PLI` | normalization at powers of two (0.5 -> exp 128) |
| R3010 | `e13src/R3010.PLI` | 2\*\*24 capacity boundary + the first tie sample (16777217 -> up) |
| R3011 | `e13src/R3011.PLI` | non-exact decimals 0.1 / 0.2 / 1.1 / 3.14159 / 12345.678 |
| R3012 | `e13src/R3012.PLI` | 14-digit near-half-ulp literals (NOT true ties -- see the step-1 note) |
| R3013 | `e13src/R3013.PLI` | `float binary(14)` cell is also 4 bytes; literal cell shared |
| R3014 | `e13src/R3014.PLI` | quarter-ulp and negative-near-tie cases |
| R3015 | `e13src/R3015.PLI` | **no .REL**: `1E-45` rejected in pass 2 with `CONVERT` (while 1E38/1E-38 compile) |
| R3016 | `e13src/R3016.PLI` | **no .REL**: `1E39` rejected (`CONVERT`) |
| R3017 | `e13src/R3017.PLI` | **no .REL**: `1E-60` rejected (`CONVERT`) |
| R3018 | `e13src/R3018.PLI` | sign together with set fraction bits: -1.75, -127.5, -0.1, -3E7, -0.5 |
| R3019 | `e13src/R3019.PLI` | legal range extremes: 1E38 (byte 255), 1E-38 (byte 2), 1E-37 |
| R3020 | `e13src/R3020.PLI` | **EXACT integer ties** +-16777217, +-16777219, 50331649 -> ties away from zero |
| R3021 | `e13src/R3021.PLI` | DR reads >=16 significant decimal digits |
| R3022 | `e13src/R3022.PLI` | 3E-39 -> exponent byte 1 |
| R3023 | `e13src/R3023.PLI` | 2E-39 -> exponent byte 0 is a legal NORMAL characteristic |
| R3024 | `e13src/R3024.PLI` | 1.6E38 accepted (byte 255) |
| R3025 | `e13src/R3025.PLI` | **no .REL**: 1.8E38 rejected -> upper bound is 2\*\*127 |

`tools/floatmodel.py` validates itself against the cells in this directory:

    floatmodel selftest: 43 assertions passed
    pool validation: 60/60 float-literal cells reproduced byte-exactly, 0 mismatch,
                     3 non-float pool cells excluded

The 3 excluded cells are STRING literals sharing DR's literal pool (FLTPOLY's
`'    '` and `'Type'`); the validator classifies them rather than counting them.

Related link/run evidence lives in `golden/e2estagedr3`, `golden/e2elinkfloat`
and `golden/e2erunfloat`, which are UNTRACKED scratch directories by project
convention (`golden/e2elink*/`, `golden/e2erun*/`, `golden/e2estage*/` are
gitignored; the semantic content is transcribed into the notes instead).  They
were produced by `oracle/linkrun.py link --tag e2estagedr3 --out e2elinkfloat
--names FLTPOLY FFACT TEST` and the matching `run`, and they showed:

* DR's FLTPOLY/FFACT/TEST `.REL` all link to `.COM` against stock PLILIB
  (`COM=True` x3) -> all 13 new routine names resolve in the library, so FLOAT
  requires no runtime implementation by me;
* DR's own FFACT transcript is 1,415 bytes, never terminates, and prints
  E-notation with seven fraction digits (`  2.4000000E+01` for 4!), each value
  correct against `math.factorial`.

Re-run those two commands to regenerate the evidence; nothing in them is needed
for the gate.
