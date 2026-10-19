# E2E-10 step 2 — FLOAT BINARY(24) lowering: assignment, arithmetic, calls; FFACT accepted

Continues `e2e10-step1-float-model.md` (value model, C100/C101).  Step 2 is the
first step of this milestone that changes the compiler.

Status: **corpus 7/41 EXACT (FFACT added), 0 DIFFERS**.
Gates: e2e **241/241 byte-exact** (was 211; +30 float specimens), negative panel
**61/61 refused** (was 51; +10), parse 532 ok / 0 FAIL, bind 45 exact / 0 FAIL,
ir 0 FAIL, rel round-trip 661/661.
Float probe set: 33 EXACT / 0 DIFFERS / 7 REFUSED (each refusal a named
perimeter member with its own tested negative).

## 1. What is now lowered

* `dcl x float;` / `float binary(24)` — 4-byte cell, pool-first layout (C100/C101).
  `float binary(p)` with p <> 24 refuses.
* Literal → variable store, cell → variable store, computed → variable store:
  `?FX44M` for cell-to-cell, `?FX44S` to pop the accumulator into a cell
  [R3001-R3034].
* Fixed operand inside a float expression: evaluate to HL, `?QI15F`
  [R3036]; decimal and character operands refuse.
* `+ - * /` on floats through `?FA44? / ?FS44? / ?FM44? / ?FD44?` with the
  operand-mode suffix law of C103 (see below).
* Unary minus: `?FN40M` (cell/formal operand), `?FN40S` (accumulator operand)
  [R3035, R3046]; negative *literals* fold into the pool cell (C101).
* Float function call as an operand: `JMP ?FPRET` exit, `?RSBLK` when
  recursive, `?FL40M` to push a bare cell for `return (literal)`
  [FFACT, R3038].
* Float arguments to float formals through the descriptor block already built
  for DEC formals [R3061, R3062, R3063]: caller emits one
  `LXI H,*A(slot)` + `CALL`; the slot cell holds the address of the argument's
  4-byte cell, so a *literal* float argument passes the address of its pool
  cell.  Callee prologue loads `[HL]` into the formal's pointer cell, and uses
  inside the callee are `LHLD` derefs (`Fderef`).
* `PUT` of a float variable / accumulator value: `MVI A,0E` + `?QFCMS` /
  `?QFCSS`; the width byte 14 is constant regardless of the value.

## 2. The operand-mode suffix law (C103)

The step-1 guess — a two-way cell-vs-stack rule — is **refuted**.  `L` and `R`
say which *side* the accumulator is on (L = acc OP HL, R = HL OP acc), and
three kinds of accumulator value behave differently: binary-op result,
`?QI15F` conversion, negation.  Full table in `spec/CLAIMS.md` C103.  R3046 is
the decisive specimen (`-a * b` -> `?FM44L`, `a * -b` -> `?FM44R`,
`-(a) * -(b)` -> `?FM44S` in one program).

## 3. Refused, with a tested negative each (nothing silent)

| shape | why | negative |
|---|---|---|
| float value → fixed/dec variable store | `?FL40M`/`?QFI15` has no standalone DR sample | N61 |
| `float binary(14)` | storage is 4 bytes (R3013) but computed precision is uncharacterized | N62 |
| float compare in a condition | DR uses `?FC44M` + JP/JM/JZ, and R3037/R3045 pair `>` with the ELSE branch, implying `>=`; flag convention needs a runtime probe | N63, N64 |
| mixing a plain cell with a pointer formal in one op | R3030-R3033 pin cell+cell, R3038 pins formal+formal; the mix has no sample | N65 |
| `GET LIST` of a float | observed on DR [R3004], not yet implemented — this is step 3 | N66 |
| negating a `?QI15F` conversion result | `?FN40S` is sampled only on arithmetic and `?FN40M` results | N67 |
| non-float call used as a float operand | no DR sample | N68, N70 |
| fixed argument against a float formal | DR's route is understood — `?QI15F` then `?FX44S` into an anonymous temp cell, descriptor pointing at the temp [R3064] — but unimplemented | N69 |

## 4. Errors I made in this step, recorded so they are not repeated

1. **Silent no-match replacements.** Two `str.replace()` calls in my own patch
   scripts matched nothing and I did not assert: (a) the `type fmode` line
   (multi-line with trailing comments, not the single line I searched for),
   (b) the `Vint -> Fconv` arm (a comment intervenes).  The build caught (a),
   the negative panel caught (b) days later as "compiled silently".  This is
   the rule I already wrote for harness edits — *assert every replace* — and it
   applies to compiler patches exactly the same way.
2. **Unparenthesized `match` inside an arm body.** `fl_push`'s `Eprefix` arm
   contained a bare `match`, which swallowed every following `|` arm: the outer
   match silently kept only 3 arms, so any `Ebinary` raised
   `Match_failure` that looked like it came from a different line.  Fixed by
   parenthesizing the arm (the DECPOLY-era note about `if`/then-branch
   absorption is the same family of trap).
3. **Probe source ordering.** Three probes placed the nested `procedure` before
   the main block's trailing statements and were refused by my own
   "main-block statement after an appended procedure" perimeter rule; the
   refusal was mine, not a DR discovery.  FFACT-order (statements, `stop`,
   then procedures) is the correct specimen shape.
4. **`const_cells` double-charging a float literal argument.** The call-argument
   prescan added a flat 2 bytes per numeric argument.  With a FLOAT formal the
   4-byte pool cell is *also* demanded by `pdec_fl_expr`, so the literal was
   counted twice and every variable address shifted by 2 — visible only as a
   uniform reloc-value offset.  Now formal-type aware.
5. **A wrong oracle, caught before I blamed DR.** I first validated FFACT's
   printed factorials against correctly-rounded exact `n!`, got 14
   mismatches, and started writing about DR's arithmetic.  The right oracle is
   the float *accumulation* the program performs; under it the residue is 14
   last-digit differences attributable to PLILIB's own binary->decimal /
   multiply rounding, which byte identity of the linked `.COM` makes irrelevant
   to acceptance.  Same lesson as the DECPOLY retraction: an accusation against
   DR needs the arithmetic done in the same breath.

## 5. Next

1. **GET of a float** (step 3): unblocks FLTPOLY and, with it, the corpus
   8/41; R3004/R3006/R3010/R3011 already characterize the value model the
   converted input must land in.
2. **FLTPOLY** — DECPOLY's structural twin for float (GET, compare, `&`,
   descriptor ABI, `?FPRET`).  Needs float compare in conditions, which is
   currently a refusal: the flag/register convention requires a runtime probe,
   not another static listing read.
3. **TEST** — the remaining float corpus program.
4. Fixed argument against a float formal (R3064 route) when a corpus program
   needs it.
