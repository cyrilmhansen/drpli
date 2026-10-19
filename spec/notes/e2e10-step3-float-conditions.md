# E2E-10 step 3 — FLOAT conditions, GET, conjunctions; FLTPOLY and TEST accepted

Date: 2026-10-19.  Model: DR PL/I-80 v1.4 (`$L$C$D` listings) + `LINK` 1.31.
Acceptance rule unchanged: raw `.REL` bytes compared with `cmp`, no
normalisation.  Gate before this step: 241 byte-exact / 61 negatives.
Gate after this step: **284 byte-exact / 0 fail, negative panel 57/57 refused,
61 warnings (unchanged)**.  Corpus: **9/41 EXACT, 0 DIFFERS, 32 REFUSED**.

## 1. What this step set out to do

Step 2 left the two remaining historical float corpus programs open:

* `FLTPOLY` — blocked on GET of floats, float relations inside an
  `if`, the `&` conjunction over float operands, and `2 * y` inside the
  polynomial procedure.
* `TEST` — blocked on float relations over POINTER-FORMAL operands and on
  `max = x` (store from a formal into a local).

Both are now **byte-identical to DR** (`golden/first8080u/FLTPOLY`,
`golden/first8080u/TEST`).  FLTPOLY's newly captured `e2e13e` golden is
byte-identical to the `e2e13` golden captured at the start of E2E-10, which is
an independent re-confirmation of both the oracle and the source text.

## 2. Float relations in a condition (C104)

Every relation lowers to `?FC44M` on the two operand addresses, then ONE
conditional jump; DR picks the push order so that the tested sign is the one
the jump wants.  R3070-R3074, R3076, R3077 (each byte-identical):

| condition | first operand pushed | jump | why |
|---|---|---|---|
| `a > b` | b (the RIGHT side) | `JP` | `?FC44M` returns "DEHL" code; pushing right first makes A<0 mean greater |
| `a < b` | a | `JP` | mirror of the above |
| `a >= b` | a | `JM` | |
| `a <= b` | b | `JM` | |
| `a = b` | a | `JNZ` (skip) | `?FC44M` leaves `A = 0` when equal |
| `a <> b` | — | — | **DR itself rejects it** (R3075: PASS 1 clean, `1 ERROR(S) IN PASS 2`, no `.REL`).  DEC `<>` gets JZ [C085]; the float reader does not offer it.  Refused, not extrapolated. |

A comparison LITERAL (`a = 0`, `a > 2.5`) becomes a float POOL cell, never a
runtime conversion [R3076, R3077].  That is what made the prescan bug below so
nasty: the pool has to be sized before `base` is fixed.

## 3. Float operands in a conjunction (C105)

`FLTPOLY`'s `if x=0 & y=0 & z=0 then stop;` is three predicates AND-ed through
the PSW, in exactly the shape DECPOLY pinned for DEC [R2026]:

```
first operand : LXI H,x / PUSH H / LXI H,*S(zero) / POP D / ?FC44M / SUI 01 / SBB A
later operand : LXI H,y / PUSH PSW / PUSH H / LXI H,*S(zero) / POP D / ?FC44M / SUI 01 / SBB A
                ... POP B / ANA B after each later operand ...
final         : JP <skip>
```

The first ADDRESS LOAD of a later operand is hoisted above `PUSH PSW` so the
previous boolean byte survives in A; the combination is `POP B / ANA B`.
R3078 pins one more thing: when the operand is `>` rather than `=`, DR emits
the compare and then **nothing** — `?FC44M`'s raw signed-comparison byte *is*
the boolean (A<0 is "greater", and the conjunction's terminal `JP` tests the
sign of the AND).  So a `>` operand does NOT get `SUI 01 / SBB A`.  `<`, `>=`,
`<=` in a conjunction have no sample and refuse.

## 4. C103 corrected: POINTER FORMALS are address-mode, not a third kind

Step 2's suffix law classified operands as *cell* vs *computed* and explicitly
refused "mixing a plain cell with a pointer formal" as an unsampled exotic
shape (which is what R3005 seemed to show).  Ten new probes refute that:

```
R3082  2 * y   LXI H,*S(2) / PUSH H / LHLD Y / POP D / ?FM44M
R3083  y * 2   LHLD Y / PUSH H / LXI H,*S(2) / POP D / ?FM44M
R3084  y + 2   LHLD Y / PUSH H / LXI H,*S(2) / POP D / ?FA44M
R3086  x * y   LHLD X / PUSH H / LHLD Y / POP D / ?FM44M
R3091  2.5 * x LXI H,*S(2.5) / PUSH H / LHLD X / POP D / ?FM44M
R3087  (x*x + 2*y) + z   ... ?FA44S then LHLD Z / ?FA44L
R3089  z + x*y           x*y first, then LHLD Z / ?FA44L    (commuted, like R3051)
R3090  z / (x+y)         x+y first, then LHLD Z / ?FD44R    (order preserved)
```

The law is therefore **two-way after all, but the cut is in a different place
than step 2 drew it**: an operand is ADDRESS-MODE when DR can push a pointer to
its value cheaply — a plain cell (`LXI H,*S`) *or* a float pointer formal
(`LHLD ptr`) *or* a float literal pool cell — and COMPUTED when the value has
to be produced into the accumulator (`?QI15F` conversion, `?FN40` negation, an
arithmetic result).  Address-mode pairs always take `M` in written order, never
commuted (there is nothing to materialise).  The commute rule is unchanged
inside the computed half: DR exchanges a commutative op's operands only when
the right side is itself a binary result.  R3005 was never a mixed pair; the
"cell vs formal" distinction that step 2 built the mode type around does not
exist for suffix selection.  `fl_bin`'s and `fl_cmp_rel`'s mixed refusals are
deleted; `fmode` keeps `Fderef` because it chooses the *load instruction*, not
the suffix.

## 5. A deduplicating callee's declared formal cell occupies no storage (C106)

`TEST` and the R3079-R3096 family differed from DR only in the address of a
local declared *after* the formals of an internal procedure.  Six probes bracket
the size law by formal count, and the law is about DEDUP, not about the type:

```
float formals   DR local Q       charging model     1/2/3 fixed formals  DR Q   charging model
1               0014             0018  (+4)         1                      000C   000E  (+2)
2               0018             0020  (+8)         2                      0010   0012  (+4)
3               001C             0028  (+12)        3                      0014   0016  (+6)
```

with the 2-byte pointer cells themselves at DR's address in every case [R3095,
R3096, R3093, R3094, R3101, R3102].  So a formal dcl that dedups onto its pointer
cell adds nothing — for FLOAT and FIXED alike — and the correction in `bind.ml`
is keyed on `dedup`, exactly like the row's address.

The exception is the written RECURSIVE attribute, where dedup does not apply: the
declared cell IS the shadow value cell and DR allocates it (P401, NFACT, and
`R3104` = `p: procedure(x) returns(fixed) recursive; dcl (x,q) fixed;` are
byte-exact only with it charged).  One further fact came from the same shape: a
RECURSIVE callee with a FLOAT formal also COPIES the caller's value into that
declared cell at body entry [R3103: `LXI H,X A(0010) / PUSH H / LHLD X A(000E) /
XCHG / POP H / LXI B,0004 / CALL <copy>`].  R3103's DATA addresses all match mine
and only that prologue is missing, so that case refuses (N71) rather than shipping
a silent near-miss.

This was a pre-existing bind-level defect, invisible until a program put a local
after the formals; no accepted program had that shape, so the gate never caught it
(third declaration-kind layout surprise of the milestone series, cf. C086).

### 5a. The wrong turn I made here (kept because it is the instructive part)

I first concluded from FFACT alone that FIXED formals were charged, and only had
that refuted after sampling R3094/R3101/R3102 — FFACT declares `dcl i fixed;` with
NO variable after it, so it says nothing about the matter, and my C106 draft quoted
it (and quoted `fixed bin(31)`, which DR rejects outright as `NOT IMP` [C079], as
if it were in FFACT).  Then a shell loop that compared P401/NFACT against a golden
PATH THAT DOES NOT EXIST reported them as `differs`, which nearly made me keep the
type-discriminated rule and add a refusal for the fixed shape.  The real gate —
which resolves its own paths — had said 286/286 the entire time.  Two lessons:
check what a cited program actually contains before promoting it to evidence, and
never decide a layout question from an ad-hoc comparison loop whose paths are
guessed.

## 6. GET of a float (C107)

`get list(x,y,z)` reads each item through the DECIMAL scanner and then
converts: `?QCXOP` (clean the decimal) → `?QX8F4` (decimal → 4-byte float in
the accumulator) → `?FX44S` (store).  No `MVI A/B` width/scale operands appear,
unlike the DEC branch's `?QCDOP`/`?DSTOP` tail [R3065, R3066, R3004, R3100].
Consequence for the value model: a runtime-read float does NOT go through
C101's literal-conversion rounding law, so the two paths must not be assumed
equivalent.

## 7. Whole-literal float arithmetic now refuses loudly (R3044 correction)

R3044 (`d1 = 1.5 + 2.5`) was cited in the step-2 note as pinned evidence for
the "DR evaluates whole-literal float expressions in the DEC runtime"
observation, but the sweep line for it had never been checked: DR emits
`?DLDOP`/`?DADOP`/`?DMUOP`/`?QDCOP`/`?QCXOP`/`?QX8F4`, mine emitted `?FA44M`/
`?FM44M`.  I verified this is pre-existing, not a step-3 regression, by
building HEAD and re-running the probe (HEAD differs too).  That is worse than
an unimplemented feature: the two paths can compute *different values* (24-bit
float arithmetic vs DR's decimal arithmetic), so the compiler now refuses any
float arithmetic expression containing no identifier, with R3044 quoted in the
message.  Implementing the DEC-runtime route is the open half of this perimeter
member; it is not needed by any corpus program.

## 8. Process errors made in this step (all caught by a gate, none shipped)

1. **Prescan did not size float comparison cells.**  `prescan_cond` only knew
   DEC comparison literals, so `if a = 0` allocated its float zero cell at
   lowering time — after `base` was already fixed — and the zero cell and
   variable `a` both got address 0, silently shifting every later data address.
   Caught as two mismatched RELOC values on R3076/R3077, not as a crash.
2. **`conj_bin_zero` claims float operands.**  It matches any `ident = 0` whose
   operand is not DEC, and a float variable is not DEC, so FLTPOLY's second and
   third conjunction operands got the 2-byte FIXED-BINARY boolean form.  The
   float test now runs *before* that helper.  Caught only by byte diff, and
   only because I traced the diff down to a specific instruction pair.
3. **Invented a helper that did not exist** (`fl_addr_pre`) when writing the
   conjunction hoist.  The build caught it; the fix was a `?save_psw` argument
   on `fl_cmp_rel` rather than a second copy of the addressing ladder.
4. **Two malformed probe generations.**  My generator overwrote `R3091`
   (`2.5 * x`, a byte-exact golden) with a different program, and built
   `R3095`/`R3096` with `q` used but not declared — DR answered `NO DCL` and I
   spent oracle cycles on it.  Lesson recorded where it hurts: print the probe
   source text before batching it.
5. **A debug block written into a `let … in` chain** as a bare `(if …)`
   (syntax error), then a `let x = …` binding missing its `in`.  The
   measurement itself was worth it: `secs=mx@22+22` is what pointed at bind's
   per-section accounting instead of the float lowering.
6. **Warning count rose by one** (Warning 11, redundant `| _ ->` over the six
   `Ast.relop` constructors).  The warning-count check is a gate in its own
   right and caught it; back to 61.

## 9. Evidence and current state

* Float probes byte-identical: **111** distinct probe programs across
  `golden/e2e13*`; **0 DIFFERS**; 17 refused, each a named perimeter member.
* New DR goldens this step: R3065-R3066 (GET), R3070-R3079 (relations,
  conjunction, formal compare), R3080-R3091 (address-mode pairs, formal stores,
  literal × formal), R3093/R3095/R3096 (formal-storage size law), R3097-R3100
  (the four former negatives promoted to positives), FLTPOLY, TEST.
* Negative panel: N63/N64/N65/N66 retired as *proven supported*; their exact
  source text was compiled by DR and is now a byte-exact positive
  (R3097-R3100), so nothing was quietly deleted.
* `tools/floatmodel.py`: 45 assertions pass; pool validation **73/73
  float-literal cells byte-exact, 0 mismatch**, with 8 non-float cells and 4
  range-boundary cells excluded *by name and reason* rather than silently.
* Registering 41 probes plus FLTPOLY and TEST grew the gate from 241 to 284
  positives without touching the existing ones.

## 10. Remaining float perimeter (all fail-loud, none accepted silently)

1. Whole-literal float arithmetic → DR's DEC runtime path [R3044].
2. `<>` on floats — DR rejects it, so there is nothing to reproduce [R3075].
3. `Lt`/`Le`/`Ge` in a conjunction, and any non-`=` relation on the RIGHT side
   of a conjunction (the hoist placement has no sample) [R3078 partial].
4. Float pointer-formal mixed with a *computed* operand inside a `~save_psw`
   conjunction (only plain cells sampled).
5. Float→fixed/decimal stores [N61/R3002], `FLOAT BINARY(p)` with p ≠ 24
   [R3013/N62], float FILE I/O, float VARYING interaction.
6. Float literal at or below the 2^-129 boundary (encoding collides with DR's
   zero cell) — refused by the range check.
