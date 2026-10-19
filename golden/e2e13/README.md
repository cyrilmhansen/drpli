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
