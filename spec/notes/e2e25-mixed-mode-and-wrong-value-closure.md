# E2E-25 -- closing the wrong-value panel, then C161

Milestone brief: (P0) close the remaining wrong-value divergences LP8/LQ2/LQ4 (negative literals) and
LP11/LP12/LP16 (unsupported positions); (P1) implement C161 mixed DEC/BIN; (P3) prove CB9/CB6/C162W
protections still byte-exact; (P4) re-test CONV/DECY integration; (P5) characterize INT->DEC, and
register only what is actually tested.

Gate at every commit: `dune build` clean, then the full gate.  Start of milestone **647 byte-exact /
112 negatives / 3 divergences**.  End: **667 byte-exact / 117 negatives / 0 divergences**, exit 0.
Commits `d7702d8` (P0-1) -> `94c6b6e` (P0-2) -> `11d4a61` (P0-3) -> `f5ec37d` (P1+P4) -> this.

## P0-1  the negative literal is a signed decimal cell (C180)

DR's cells, measured not assumed: LP8 `-32768` -> `32 72 96` (10^5 - 32768 = 67232, LSD-first, sign
nibble 9); LQ2 `-65535` -> `65 44 93`.  The instruction stream carries no `?IN20N`: the minus is folded
in at compile time.  Mine loaded the magnitude and negated at run time, which COMPLETED where DR aborts
with `ERROR (1), Conversion` -- one of the three divergences, and the reason LP8/LQ2/LQ4 closed together
rather than one per probe.

Runtime re-verified against DR for all three after re-baselining their goldens (the old `m*.REL` files
were mine, which is exactly what C137 forbids).  Each shows `LINK-ERRORS: none`, `.COM IDENTICAL`,
console byte-equal, and the DR traceback at the same PC:

    LP8  8061  0013 004A 0020 0039   LQ2 8061 0013 004A 0024   LQ4 8061 0013 004A 0025

The "cosmetic" traceback difference (3 cells vs 4) was a code-size artefact of MY truncation and
disappeared once both sides aborted at the same instruction -- a reminder that a difference nobody can
explain is usually evidence about something else (C140).

## P0-2  one arm for the whole ADD/SUB literal matrix

Measured shape, identical for every literal once the sign is folded into the cell -- only the SIDE and
the OPERATOR matter:

    left  -> <route> / XCHG / <other operand> / (DAD D | ?IS22N)
    right -> <other operand> / PUSH H / <route> / POP D / (DAD D | ?IS22N)

Parentheses disappear (they arrive as `Econd`, unwrapped ONCE in the shared classifier) and the sign
disappears into the cell, so E2E-24's four arms collapse into one unified arm and the prescan asks the
same predicate.  Fifteen new probes (LR1-LR19, DR batch e2e292d/e2e293d) cover both operands of both
operators, both signs, with and without parentheses, leading zeros (`LR2 x + 0123456789` -> p=10,
6 bytes, inside an ADD), plus the positions the matrix does NOT cover.

Three defects in my own drafts, all caught by the pool invariant before any wrong byte shipped:

1. prescan demanded through the unwrapping classifier while lowering matched raw patterns, so
   `x + (-32768)` demanded 3 bytes and allocated 0 (LR18/LR19).  One function, asked by both walkers.
2. deleting the out-of-range branch from the E2E-24 ADD arms without narrowing their PATTERNS made
   `x + 0123456789` match a body that no longer converts -- 11 byte-exact specimens became pool
   refusals (LP10, LQ1, LQ8, LQ9, LR1, LR9, LR10, LR13, LR16, ML14, ML5).
3. `op = Ast.Add || <other-operand shape>` is true for ANY operator with an identifier partner, so
   `x * 32768` allocated a cell nobody demanded and died on the size check instead of its designed
   MB31 refusal (LR7).

## P0-3  every silent truncation became a refusal naming its position (C182)

A sweep of 15 probes found ELEVEN positions that truncate silently -- almost twice the six the
divergence panel named.  Before the guards: `if x > 32768` evaluated as `x + 32767` signed, so LP11
TOOK a branch DR never reached and assigned y=1; LP12 stored a wrapped 0x8000 into z(1); LP16 handed p
a truncated value; LR8 completed with wrong bytes; all with rc=0.

Now one choke point, `int_lit_checked`, refuses at each position with that position's name (condition /
DO-bound comparison constant, array element store in all four forms, element self-update,
procedure-call argument, function argument, direct HL load).  Fourteen negatives registered with
markers taken from the compiler's ACTUAL stderr; DIVERGENT.txt reduced to its header (0 rows) and the
three original divergences left the panel by being CLOSED, not moved: LP8/LQ2/LQ4 -> byte-exact +
executed specimens, LP11/LP12/LP16 -> refusals that name their position.

The instructive failure was LR8: narrowing the routing predicate pushed it out of the routed set and it
did NOT fall back to a designed refusal -- it kept building with wrong bytes, because the element
self-update form biases HL from its own copy of the constant.  A position is only closed when the site
that emits it refuses.

## P1 + P4  C161 implemented for ADD and SUB (C181)

`lower_assign`'s decimal-store arm now guards on `is_dec_expr st rhs && dec_pure st rhs`, so mixed trees
fall through to the integer route instead of being claimed and then refused.  In `lower_hl` a bare
FIXED DEC operand converts in place -- `LXI H,<var> / MVI A,p / ?DLDOP / ?QDI15`, p the SOURCE
precision -- and then takes DR's measured parking rule unchanged, because that rule protects the OTHER
operand and is not about which conversion ran.

Byte-exact against their own DR goldens and executed by the gate's `--link-run` with byte-equal console
output and independently computed values:

    CB1 -> 8    CB2 -> 8    CB3 -> -2    CB4 -> 2    CB5 -> 8    CB7 -> 12350
    CONV.PL1, DECY.PL1  byte-exact (the third-party programs that motivated C161 in the first place)
    NG14 (`i = i + d')  byte-exact -- note its source is negsrc/NG14.PLI, NOT a renamed copy: the
                        program name lands in the LINK header, so comparing `N29.PLI' against NG14
                        showed a spurious 120-byte divergence.

Protections re-verified in the same run (P3): CB6, CB9, DECPOLY, DFACT, C162W1..W8 and all other
specimens unchanged at 0 failures -- the change that once made CB9 double-convert is gone.

Refused on purpose: CB8 mixed MUL (DR parks the LEFT operand although XCHG would work; one sample is
not a rule), CB10 mixed result into a DEC target, DEC operands in DIV/EXP, DEC sub-expressions.

## P5  INT -> DEC characterized (Q8), not implemented

    IC5 `e = 7'           BYTE-EXACT + executed ('      7')   integer literal -> DEC works
    IC7 `e = decimal(b,5)' BYTE-EXACT + executed ('      5')  the sanctioned doorway works
    IC1 `e = b'           refused; DR converts HL with `CALL ?QI15D' (chain-ext code 0020)
    IC2 `e = d + b'       refused        IC3 `e = b + d'  refused (CB10's shape)
    IC4 `e = b - d'       refused        IC6 `e = b * 2'  refused
    (DR batch e2e309d, 7/7 ok; five registered as negatives with DR goldens, two as specimens)

Closing this wants converting AFTER the binary combine, and the decimal store route is pinned tightly by
DECPOLY/DFACT/C162W1..W8 -- all six goldens want to be in view at once.  Recorded as characterization,
not as a half-implementation.

## Not done this milestone

* `$X'DEC,BIN'` global mode: never tested, so not claimed.  All probes above use explicit declarations.
* Array-element DEC stores on the literal route (LP12/LR6/LR7/LR8): the element's type is not in the
  prescan context, and a `fixed dec(3)` element is 2 bytes like an integer, so demand and layout cannot
  yet be distinguished.  They refuse rather than guess (C182).
* Element self-update with a DEC element (form 4): same missing type context; the site refuses.
