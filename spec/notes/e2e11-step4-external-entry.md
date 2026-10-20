# E2E-11 step 4 — external ENTRY, and the first corpus program closed by it

Date: 2026-08-03 (session 14). Builds on step 3e (`1fac1ee`), which established the
RMAC path and linked/ran DR's own DTEST/FDTEST. **DTEST and FDTEST are now ACCEPTED:
corpus 10/41 -> 12/41.** Gate **390/390 raw byte-exact**, negatives **65/65**.

## 1. What external ENTRY costs, and what it buys

It buys the first two programs closed by a feature this session, and it buys them at
every level of acceptance, not just compile:

| check | DTEST | FDTEST |
|---|---|---|
| `.REL` raw bytes vs DR | 384/384 identical | 384/384 identical |
| linked `.COM` vs DR (RMAC DIV2/FDIV2) | 7808 bytes identical | 7808 bytes identical |
| executed output vs DR's run | 5063 bytes identical | 5085 bytes identical |
| independent numeric check | 135/135 values | 135/135 values |
| exit | rc=0 | rc=0 |

`100 / 2 ** i` holds to 7 significant digits for i = 0..127 and then through the
index cell's signed wrap (-128..-121): `100 / 2 ** -128 = 3.4028235E+38`, the maximum
single-precision value. The wrap was not chosen — it emerged from DR's 1-byte index
cell — and the numbers came out right anyway, which is what makes the run evidence
rather than decoration.

Both programs end the same way, with DR's own runtime diagnostic:

```
100 / 2 **    -121 =                     <- FDTEST, record cut mid-line
UNDERFLOW (128), Underflow in Divide by Two
Traceback: 0179 0143
```

`Underflow in Divide by Two` is FDIV2's own message — the MAC-80 module declares
`extrn ?signal` and signals the condition; the `Traceback:` line is DR's RTL reporting
PC and SP. The last PUT record is therefore **incomplete** (label printed, no value),
so a console comparison has to compare whole records and note the truncation, which
is what the harness does here: 135 complete records verified, one partial record
present in both runs identically.

## 2. The external ENTRY lowering (C133)

`declare <name> entry(<formals>) external [returns(<type>)];` compiled in the caller
emits, at the call site:

```
LXI H,* A(desc) ; CALL * L(ext-symbol) ; LINK-CHAIN-EXT code <addr> <SYMBOL>
```

and nothing else. Three negative-space findings, each pinned by a probe I ran
*because* my first guess was wrong:

- **No `LINK-DEF-EXT`.** E29A vs E29E: the same `call ext(i)` with
  `declare ext entry(fixed) external` emits 1 record (CHAIN-EXT); adding a second
  program `E29E.PLI` that *defines* `ext` as an ENTRY emits 4 records
  (DEF-EXT/EXT-NAME/EXT-ADDR/END-EXT) — from the defining program, not the caller.
  An external ENTRY is a reference with no definition request.
- **Inline reloc on the CALL is rejected.** E29B (inline RELOC, addr 0) produced the
  identical size to the clean file, and the linked run **failed** with a traceback —
  a CALL to address 0. `reloc st (Code addr) 0` emits a record, so "zero inline
  reloc" and "no inline reloc" are not the same file.
- **CHAIN-ADDR on the symbol is rejected.** E29D: 0 bits consumed, `NOT IMP`.
  A `LINK-CHAIN-EXT` carries only the name and a code address, no `ADDRESS` field;
  its `LINK-CHAIN-ADDR` sibling carries the address and no name. That asymmetry is
  why the record type exists.

So the CALL site gets an EXT-class chain fixup and that is the entire mechanism.
FDTEST additionally needs `fl_proc_ret` to consult the external table, so an
expression-position external call returning FLOAT lands its result on the float
stack and prints correctly.

## 3. The two DTEST shapes nobody could have guessed

DTEST's `dcl i fixed(7)` is a **1-byte cell**, and neither the initialization nor the
increment uses the general-purpose path:

```
do i = 0 by 1:      XRA A ; STA i            <- 2 bytes, not MVI A,00 / STA (3)
loop tail:          LXI H, i ; INR M ; JMP t <- 6 bytes, not LHLD/INX H/SHLD (9)
```

`INR M` increments **in memory**. If I had kept the 3-cell ladder, the loop would have
modified a copy, `i` would never change, and the program would print `100 / 2 ** 0`
forever — while the PUT items would still have printed *correct values*, so no output
comparison would have caught it and only the byte compare would have.

The zero forms are one rule seen three ways: DO initialization (DTEST), plain
assignment (E29A/E29D), and — for a FLOAT target — an explicit 24-bit zero cell
(FLTPOLY2's `u = 0.0`). Each shape was pinned separately before being generalized, and
`MVI A,lo` remains for non-zero constants because N306/N308 pin that.

## 4. Pool accounting for call arguments (C134)

This is where the real damage was, and it went through two wrong fixes.

`base = statics_total + pool_total` is computed **from the prescan**, before lowering
allocates anything. So every pool cell must be *demanded* by a prescan walker, and
literal call arguments are demanded by two different walkers depending on position:

- assignment with a float target -> `pdec_fl_expr` (which already had an Esuffix arm,
  which is why **R3062 was always exact**);
- **every other expression position** -> `prescan_expr`, which had **no Esuffix arm at
  all** — so FDTEST's `fdiv2(i, 100)` inside a PUT item demanded nothing, the base
  came out 2 bytes short, and the first automatic (`i`) landed **on top of the float
  constant**: FDTEST references 100.0 at 000b-000e and `i` at 000d. `STA I` would have
  overwritten the constant's middle byte, and every address in a dump still looked
  plausible. Symptom: `DEF-DATA-SIZE` mine 0016 vs DR 0018.

My first fix counted float literal args in `const_cells` instead. That made FDTEST
byte-exact and **broke R3062** (0018 vs DR's 0014 — double count). Reverting that
and adding the missing `prescan_expr` Esuffix arm made both exact — but a third half
rule remained: `formal_float_at`, used by `const_cells` to decide "is this argument
position float?", resolved callees through `pl_ptrs` only, so for an external entry it
answered *no* and `const_cells` added its 2-byte FIXED cell on top of the 4-byte float
cell the prescan had just demanded: FDTEST 001A vs DR 0018. Pointing all three
consumers at one accessor `callee_formal_rt_l` finished it.

**Three functions, one question.** "Is argument i of this callee FLOAT?" was answered
three times, each time correctly for the case that function had been written for, and
each time wrongly for the new case. This is the C129 pattern in its purest form, and
it is the strongest single piece of evidence for the architecture work: I did not hit
a hard case; I added a callee type, and the codebase had three independent answers to
what a callee's formal type is.

Method note worth keeping: a double-count and a missing-count produce the *same*
symptom class (DEF-DATA-SIZE disagreeing by a small amount), so the size difference
alone does not tell you which. The discriminator is which *previously exact* specimen
you break when you add: R3062 broke on adding, so those bytes were already counted
somewhere, which means "missing" was the wrong story and "two owners" was the right one.

## 5. Negative panel

`N84_EXTERNAL_ENTRY_CALL` retired — **eighth instance** of "negative whose subject DR
compiles" (it was my perimeter refusal; DR compiles E24G). E24G promoted to a positive
specimen, joined by DTEST, FDTEST, E29A, E29D. Panel 66 -> 65.

Three probes now **refuse**, and that is the honest outcome — each is a case where my
compiler would have emitted a *shorter, plausible* file:

| probe | shape | DR's behavior (pinned in the probe's golden) |
|---|---|---|
| E29B/E29E | `i = ff(i, 101.5)` — FLOAT result into FIXED | `CALL FF ; CALL ?QFI15 ; STA I` — converts first. My old path took `MOV A,L` of a mantissa byte and still produced a number. |
| E29C | 1-byte actual against `entry(fixed)` (2-byte) formal | `LDA J ; <sign-extend> ; SHLD *A(0006)` — widens through an anonymous cell. Mine passed `&j` directly, so the callee would read past it. |

## 6. What this does not settle

- **Named sequential FILE I/O** is still the biggest remaining common construct
  (7 programs, 0 accepted) and is unaffected by any of this.
- External ENTRY with a FLOAT actual that is a variable, or a general expression
  argument, still refuses (C126 applies).
- `fixed(7)` vs `fixed` width mismatch inside a call refuses (E29C).
- FLOAT -> FIXED conversion refuses (E29B/E29E).
- DIV2/FDIV2 are linked from RMAC-assembled originals; my compiler cannot yet *produce*
  MAC-80, so those two programs' acceptance depends on the external module being
  available. That is a toolchain fact about the specimen, not about my lowering.
