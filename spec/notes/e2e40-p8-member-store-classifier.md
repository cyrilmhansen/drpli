# E2E-40/P8 — the two "unmeasured" member stores were being emitted anyway

Scope: the fall-through arms of the internal-member integer store in
`ocaml/lib/codegen.ml` (`lower_assign`, `Ast.Eident` branch).  Nothing else in
the store machinery moved.

## The defect class, not the defect

[E2E-40/P7] introduced `rhs_landed_in_hl` so a member store whose value came
down the general expression path would take DR's parked sequence
(`PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D`), and deliberately
left two shapes out because "DR has no sample of them":

* **case A** — self-update on a member (`a = a + 5`), which keeps the ladder and
  does not set the flag;
* **case B** — an integer literal outside `hl_const` range (`a = 65535`), which
  reaches HL through `lit_dec_to_hl` and does not set the flag either.

Both therefore fell through the tail match to `SHLD`.  That is the whole bug, and
the interesting part is that it is not a wrong-value bug or a layout bug — it is
**a decision made by declining to make one**.  Prose in `PERIMETER.md`, in a
`codegen.ml` comment, and in [C266]'s "Not claimed" paragraph all said the shape
was unpinned and "not evidence of anything", while the shipped build emitted a
specific pinned shape for it, byte after byte.  Three texts and one code path
disagreed, and the code path was the only one that ran.

## Measurements

Both were probed against DR with tag `e42p` (`golden/e42p/`), with
`PREDICTIONS.txt` written first, and both verdicts were read off DR's **linked,
disassembled image** (`tools/dis80.py --com golden/e42p/E42Pn.COM`) rather than
off a `.REL` listing — the operands in a `.REL` are relocation placeholders and
reading them as immediates is [C264]'s error.

| probe | statement | DR | mine before | mine now |
|---|---|---|---|---|
| E42P1 | `g.a=5; g.b=100; a = a + 5` | `LHLD 19F6 / LXI B,0005 / DAD B / SHLD 19F6`, console `10` | ladder + `SHLD` | unchanged, **256/256 identical** |
| E42P2 | `a = 65535` into the same member | conversion calls, then **parked** store | conversion + `SHLD` | parked, **384/384 identical** (code 0x5A, DATA 0x7) |

So case A was right for the wrong reason — the ladder survives on a member, which
is [C165]'s form-4-before-form-3 precedence (AC4 `a(2) = a(2)+5` says the same for
an array cell), not [C266]'s destination rule.  Case B was simply wrong: 168
differing bytes.  [C266]'s rule survives both; what was overreaching was the claim
that a literal is written in place.  The real discriminator inside a member store
is **whether HL holds the value at the tail**, and a literal that DR has to convert
does end up in HL like any other computed value.

Then E42P2 was run.  **DR's own object aborts**: `ERROR (1), Conversion`, traceback
`0612 10B0 3620 3535 3533` — a `FIXED BIN(15)` cell cannot hold 65535 and the range
check lives in DR's runtime library, not in the code DR emits.  My object, linked
from a byte-identical `.REL` against the same library, aborts with byte-identical
console text.  That is the strongest argument in the slice for the runtime panel
existing at all, and the reason E42P2 is registered as a runtime row whose expected
output is an error message instead of a number.

The gate's `--link-run` arm settles it independently of my transcription: for both probes it links
BOTH objects and compares the consoles.  E42P1 prints `10` on both sides; E42P2 prints
`ERROR (1), Conversion` on both -- and each `.COM` came out **IDENTICAL** to DR's, which is what two
byte-identical `.REL`s should give and says something the `.REL` check alone cannot: relocation
resolution and runtime-library binding round-trip cleanly for these shapes.

## Implementation

`member_store_class` (codegen.ml, above `lower_assign`) returns one of four values:

| class | condition | route | DR witness |
|---|---|---|---|
| `Ms_literal` | integer literal, `fits_int_lit` | `LXI H,<cell> / MVI M,lo / INX H / MVI M,hi` | E39S1, E39S2, E40S1..S4 |
| `Ms_ladder` | `cell +/- k`, k in −8..16, same DATA address as the destination | ladder then `SHLD <cell>` | **E42P1** (+5 only) |
| `Ms_general` | everything else, incl. literals 32768..65535 | parked store | E39S7, E41P1, E41P4, **E42P2** |
| `Ms_unsampled` | negated literal at a member; literal > 65535; same-cell bias outside −8..16 | **refusal, before any byte is emitted** | none |

The classification happens immediately after `elide_fixed_zero`, before the value
match, so an unlicensed shape cannot leak a single instruction.  `rhs_landed_in_hl`
is gone: the tail now reads the class, which removes a piece of mutable state whose
correctness depended on every value-producing arm remembering to set it.  Ordinary
(non-member) destinations are untouched — `mstore` is `None` for them and `SHLD`
remains their measured route for every RHS class in the corpus.

`Ms_ladder` compares DATA addresses, not spellings: after [C258] `a` and `g.a` are
two names for one row, so `a = g.a + 5` classifies as a ladder.  That equivalence is
inferred from E40Q1/E40Q2 compiling byte-identically, **not** probed at this shape;
it is recorded as an inference in [C267]'s "Not claimed".  The R1..RA reproductions live in
`spec/lab-evidence/e2e40-p8/` (not goldens, no DR oracle -- they show what MY build did).

## Refusals registered

Four `my-gap` negatives (`spec/INVENTORY.txt`, `tools/e2e_gate.py` `REJECTS`),
sources mirrored in `artefacts/E42N1..E42N4.PLI` so the same text can be shown to
DR later: `a = -5`, `a = -65535`, `a = a + 100`, `a = 100000`.  They are `my-gap`,
not `dr-refuses`: DR has never been shown a member store of any of these shapes, and
[C256] is exactly about not laundering my refusal into DR's verdict.  For `E42N2`
the nearest DR evidence is a runtime abort, which argues for refusing but does not
make the source illegal.

## Gates

Byte-exact 954 → **956** (E42P1, E42P2).  Negatives 125 → **129**.  Runtime rows
26 → **28**.  Link-run console comparison: E42P1 equal (10), E42P2 equal (the abort), both `.COM` identical to DR's.  INVENTORY +6 entries, 0 removals, diff read.  Divergences 11 → **11**.
Coverage and census unchanged in counts; census `--verify` (which now compares `msg`
[C265]) passes.

## What this leaves open

* The ladder at biases other than +5, and the ladder on a member under `-`.
* Negated literals and out-of-range magnitudes at a member — refused, unmeasured.
* POINTER/BASED members ([C228], E40Q4's 12-byte gap): this table is derived for
  cells with a fixed DATA address and says nothing about pointer-displaced ones.
* Whether a `FIXED BIN(15)` member store of a converted literal should also abort in
  *my* runtime when mine is used standalone — my object only aborts because the
  linked library is DR's.  That is an ARCH-level question, not a codegen one.
* ~~E40S2/E40S4 remain divergent on `XCHG` vs `PUSH H`~~ **[closed in P9: [C271] — the discriminator is the class of
  the operand DR loads next, not the class pair; both are byte-exact now]** — operand preservation, a
  different route, untouched here.
