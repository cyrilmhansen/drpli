# E2E-7A slice 3 — FIXED DECIMAL ROUND (`?DROUN`)

Evidence base: 13 new DR specimens R801-R813 (`$L$D$C$S`, `golden/e2e9/`),
compiled before any implementation was written, plus the already-banked
LOAN1 `$C` trace (`?DROUN` at 0162) and the slice-2 divide specimens that
share the stack.

## 0. Count reconciliation

| bucket | count | names |
|---|---|---|
| probes generated + DR-compiled | **13** | R801-R813 |
| registered BYTE-EXACT positive specimens | **8** | R801, R802, R803, R804, R806, R807, R811, R813 |
| refused by design (DR goldens kept as evidence) | **5** | R805, R808, R809, R810, R812 |
| of those, DR produces **no `.REL` at all** | **1** | R808 — DR rejects `y = round(a);` itself (`SYNTAX ?`, 1 error in pass 2) |
| new negative-panel members | **8** | N36-N43 (5 matching the refused probes + 3 shapes with no sample at all) |
| gate totals | **143 / 143** positive, **38 / 38** negative | was 135 / 30 at `a46c386` |

R813 is LOAN1's own statement, `P = P + round(i * P / 1200, 2)`, with LOAN1's
own declarations (dec(11,2), dec(4,2), literal 1200) isolated into a
standalone program. Its instruction stream is **identical to LOAN1's** at
0142-017F, and it prints `505.83` — LOAN1's month-1 balance.

## 1. The `?DROUN` convention (all bytes directly observed)

```
MVI  A,k
CALL ?DROUN          k = (scale of the entry on top) - n
```

* **One argument, in A. It is NOT the requested scale `n`.** For
  `y dec(9,2) = round(a dec(9,3), 2)` DR emits `MVI A,01` — the number of
  fractional digits to drop, `s - n = 3 - 2`. Samples: 3→2 gives 01
  [R801/R802/R803/R811], 6→2 gives 04 [R804/R807], 4→2 gives 02 [LOAN1/R813],
  3→0 gives 03 [R806], 3→3 gives 00 [R811 inner].
* **`k = 0` is still emitted.** Unlike the divide pre-shift, which vanishes
  at N=0 [L3], `MVI A,00; CALL ?DROUN` appears for the inner round of
  R811. So "no digits to drop" is a call, not an omission.
* **The entry KEEPS its scale.** After `?DROUN` the top is still at `s`,
  with the digits below `n` rounded off. Proof, three independent ways:
  - R801: store into dec(9,2) still needs `MVI A,01; CALL ?QDDSR` — if DROUN
    had set s=2 the shift would be 0 and would not be emitted at all.
  - R804/R807: quotient at s=6, `DROUN 4`, then the SAME `QDDSR 4` the
    shift-only case needed.
  - R807/LOAN1/R813: the enclosing `+` emits `QDDSL` to lift the *other*
    operand up to the rounded entry's original scale (4 in LOAN1's case, 6 in
    R807's) — an alignment that only makes sense if DROUN left s alone.
  So ROUND introduces **no new shift machinery**: L1 (align the shorter
  operand up) and L5 (consumer fixes the scale) apply verbatim, computed from
  the operand's pre-round scale.
* **Push order.** `X + round(<compound>, n)` pushes the ROUND subtree first
  [LOAN1 0142-0162 before P at 0165; R807 0036-0050 before P at 0053], which
  is exactly law L7 (right-first iff right compound and left simple) once a
  round node with a compound argument counts as compound. A simple-argument
  round on either side of `+`/`-` has **no** sample, so it refuses [N41].
* **The digit count is a static immediate.** With a variable `n` DR computes
  it at run time: `LHLD N; MOV A,L; SUI 04; CMA; CALL ?DROUN` = `3 - n` for
  s=3 [R812] — same law, six extra bytes, not implemented (LOAN1 uses a
  literal) [N39].

## 2. Numerical semantics — settled by DR's own runtime, not assumed

Console values from DR's linked programs (`golden/e2e9run/`), then re-checked
against Python `Decimal` with explicit rounding modes:

| expression | DR printed | HALF-UP | HALF-EVEN | TRUNCATE |
|---|---|---|---|---|
| `round(2.125, 2)` | **2.13** | 2.13 | 2.12 ✗ | 2.12 ✗ |
| `round(2.135, 2)` | **2.14** | 2.14 | 2.14 | 2.13 ✗ |
| `round(2.145, 2)` | **2.15** | 2.15 | 2.14 ✗ | 2.14 ✗ |
| `round(2.155, 2)` | **2.16** | 2.16 | 2.16 | 2.15 ✗ |
| `round(-2.125, 2)` | **-2.13** | -2.13 | -2.12 ✗ | -2.12 ✗ |
| `round(2.5, 0)` | **3** | 3 | 2 ✗ | 2 ✗ |

**The tie rule is HALF-UP, AWAY FROM ZERO.** 2.125 and 2.145 kill banker's
rounding (which would give 2.12 and 2.14), and -2.125 → -2.13 rules out any
toward-+infinity variant. This closes the question C084/C086 explicitly left
open: division truncates [L9] and never produces a tie, so `?DROUN` is the
only place DR rounds, and it needed its own specimens.

`round` acts on the value **on the stack, before the store truncates it**
[criterion: original value vs truncated intermediate]:

```
x = two / three;             -> DR prints   0.66   (store truncates)
y = round(two / three, 2);   -> DR prints   0.67   (round sees 0.666666)
```

and R807 confirms the composition (`100 + round(7/3,2)` → `102.33`, not
`102.32` which a truncated-then-added path would give).

## 3. What my compiler emits, and what DR's runtime does

Byte generation (mine) and arithmetic (DR's PLILIB) stay separate criteria:

* mine: push the argument exactly as any DEC operand, then `MVI A, s-n`,
  `CALL ?DROUN`, then the ordinary L5 consumer fix (QDDSL/QDDSR) or nothing
  in an operand position; the descriptor keeps `(p, s)` of the argument.
* the value is computed by DR's `?DROUN` at run time. That is why the
  linked-`.COM` + console arms matter here: they are the only way to show my
  program's arithmetic agrees, and all 8 positives came back **console
  byte-equal** (`2.13`, `2.13 2.14 2.15 2.16`, `-2.125 -2.13`,
  `0.66 0.67`, `2.500 3`, `102.33`, `2.13`, `505.83`).

## 4. Defect caught by the probe set before it could ever ship

My first implementation of R813 compiled, but its `.REL` **differed from DR's
in 11 bytes**: the prescan function that sizes the DEC literal pool
(`pdec_operand_bytes`) had no ROUND case, so the 1200 cell inside
`round(i*P/1200, 2)` was never counted, the pool came out 3 bytes short, and
every AUTO base after it shifted. Layout-wrong output that still "compiled
fine" is the classic fail-silent shape — it was caught by raw byte
comparison against a fresh DR golden, before registration and before any
commit, by generating the LOAN1-shaped probe *first*. The fix is the ROUND
case in the prescan [codegen.ml]; the digit-count argument `n` deliberately
contributes nothing there, because it becomes an immediate byte and never a
pool cell.

## 5. Fail-loud perimeter after slice 3 (each is a tested negative)

| negative | shape | why unpinned |
|---|---|---|
| N36_ROUND_ONEARG | `y = round(a)` | DR rejects it (`SYNTAX ?`, no .REL) [R808] |
| N37_ROUND_LITERAL | `round(2.125, 2)` | a literal argument takes own-digits AND own-scale (A=04 for 2.125) [R809] — a third literal role, one sample, not needed |
| N38_ROUND_INTARG | `round(i, 2)`, i FIXED BIN | DR uses a separate route `?IROUN` + `?QI15D` and emits no `?DROUN` at all [R810] |
| N39_ROUND_DYNSCALE | `round(a, n)` | runtime-computed k [R812]; template known (6 bytes) but LOAN1 never asks |
| N40_ROUND_SCALE_ABOVE | n > s | DR emits the WRAPPED byte `s-n` = 0xFE [R805]; value unchanged in that one sample, rule not pinned |
| N41_ROUND_SIMPLE_INADD | `p + round(a, 2)` | push order for a simple-argument round in an operand position has no sample |
| N42_ROUND_INMUL | `p * round(a, 2)` | round in a multiplicative position is unsampled |
| N43_ROUND_AS_DIVIDEND | `round(a,2) / b` | a rounded entry's PRECISION is not observable (same family as the quotient-precision gap [L4]) |
| (in code, no probe) | `round(...)` inside a relation | the compare path only accepts the C085/C086 operand shapes |

## 6. Verification performed

* `.REL` byte-identity: 8/8 new positives (gate 143/143, 0 fail).
* Linked `.COM` byte-identity vs DR's: 8/8 IDENTICAL.
* RAW console byte-equality vs DR's: 8/8 BYTE-EQUAL; every probe ends with
  `stop;`, so each transcript is COMPLETE — no bounded prefix, no timeout
  truncation.
* Independent Python model (`tools/decmodel.py`, extended with the DROUN
  schedule + half-up-away-from-zero arithmetic): corpus-wide **57 SCHED MATCH
  / 0 DIFFER**, **29 VALUE-MATCH / 0 VALUE-DIFF**, and 9 named model-side
  refusals (R506/R509/R709/R725 DEC calls; R805/R808/R809/R810/R812 the
  slice-3 perimeter — the model refuses them for the same reasons as the
  compiler, so the perimeter is cross-checked too, not just the happy path).
  All 8 positives match value-for-value against DR's printed fields, R813
  included (`505.83`).
* The model's `DROUN` token initially failed to appear for DR: `dr_tokens()`
  did not include DROUN/IROUND in its CALL alternation. Harness bug, fixed;
  without the fix, eight "DIFFER" results would have been read as law
  disagreements.
* Older DEC specimens: their `.REL` is unchanged byte-for-byte inside the
  143/143 gate, which is what pins them (identical program bytes cannot
  behave differently once linked). As a belt-and-braces check anyway, a
  12-specimen sample spanning the law families was re-run through the link
  arm: **R505, R509, R511, R512, R608, R609, R704, R705, R712, R716, R721,
  R723 -> 24/24 verdicts clean** (12 `.COM` IDENTICAL + 12 console
  BYTE-EQUAL, 0 failures, 0 omissions).
* LOAN1: unchanged first blocker (`get list(P)`), because GET is not decimal
  work. R813 shows LOAN1's round line is now byte-exact in isolation.

## 7. Not claimed

One-argument ROUND, dynamic digit counts, n > s, literal arguments, integer
arguments (`?IROUN` is an entirely separate route whose semantics I have not
probed), round in a multiplicative or comparison position, the precision
carried by a rounded entry, ROUND of a DEC function-call result (DEC calls
themselves still refuse [N33/C086]), ROUND inside PUT EDIT pictures, and
LOAN1 acceptance. The half-up rule is established from six printed values,
not from a proof; nothing is claimed about values whose tie falls below the
represented scale.
