# E2E-39 P1–P2: the BASED comparison fix, then internal-structure member scope

Baseline `1047632` (E2E-38, verified: 935 byte-exact / 0 fail, 124 negatives, 12 divergences, 16
runtime witnesses, 83 coverage rows, gate 0). P1 is committed at `11dfb09`; P2's evidence is at
`ada03ca` with its implementation reverted.

## P1 — C246 fixed and pinned (committed)

Root cause was not where the diagnosis put it. `cmp_load_deref` gated the whole dereference ladder
on `st.deref`, a flag carrying "pointer FORMAL" — so a BASED name never reached it and
`is_expr_trivial` sent most BASED comparisons down a pointer-derived path. Now every BASED view
loads through `LHLD <pointer>` + member step + `MOV E,M / INX H / MOV D,M / XCHG`.

**The diagnosis itself was wrong in detail and is corrected by C252.** C246 said the wrong value sat
in `q > k` and that all three probes E37B1/B2/B3 showed it. Disassembly of the fixed build says the
defect was in `q = k` (Eq/Ne): the three probes differ from DR only at 0x3d/0x40/0x43, the relation
at those addresses is `q = k`, and every `>`/`<`/`>=`/`<=` address is 9 bytes of DR code where mine
is 6 — DR's two-sided widening, which is a separate unsampled shape. The three probes agreed only
because each one's `q = k` sits at one constant data address. Four byte-exact witnesses now pin both
sides: PB4 `k = 40` (branch taken), E37B1 `k = 1` (not), E37B2 `k = 3` (not), E37B3 `k = 4` (taken).

Panels: PB4/E37B1/B2/B3 moved DIVERGENT → SPECIMENS (935 → 939 byte-exact, 12 → 8 divergences),
runtime witnesses 16 → 18, both outputs independently true AND false, coverage 83 → 84
(`COND.BASED_VIEW_LITERAL`, S→A, DIVERGENT→EXACT, 2→4 runtime witnesses).

Harness note: the runtime tool compares whitespace-separated token sequences, so `1`, `01`, `0001`
are one value. An expected string must be DR's exact bytes; a first attempt normalizing PB4 to
`1 0 0` was caught by reading DR's own print file and reverted.

## P2 — member scope: finding, implementation, revert

DR (15 goldens, `golden/e39a`/`e39b`/`e39c`) settled the model:
- E39S1/S2/S5 **byte-identical** — qualified, unqualified and level-3 nesting compile to the same
  bytes, DATA 0004 [C253]. Resolution is the whole job.
- E39X2 → `DUPLIC` PASS 1, no .REL: a member name shares the flat namespace, so no shadowing rule
  exists to implement.
- E39X1 → `QUALIFY` PASS 2, no .REL: ambiguity is an error — but at the USE. MPMCALLB declares
  `2 link` twice in two structures and DR compiles it, with qualified uses [C255].
- E39P1 (ordinary variables) is DR CODE SIZE 0030 where E39S2 is 0036 at the same addresses:
  DR spills a member operand with `PUSH H/POP D` and a plain variable with `XCHG`, same register
  state on exit [C254]. This refuted my first reading of C253 and is the *only* thing separating my
  member programs from DR's.

Implementation: bind entered each internal member as a row carrying `(owner, absolute frame offset,
type)`, with `bytes_of = 0` in bind so the layout cannot double-count; codegen mapped the row to an
ordinary cell. It resolved E39S2/S3/S5, matched DR's DATA exactly (0004, 0006), reproduced DR's own
S2==P1 byte-identity, and my E39P1 was byte-exact against DR's (256/256).

Two traps, both measured rather than reasoned:
1. **Bind must size zero but codegen must size the member's bytes.** This compiler derives the DATA
   extent from `max(off + size)` over the variable table, so `size = 0` gave E39S2 data=2 where DR
   records 4 and E39S3 4 where 6 is right — overlapping cells. Caught by arithmetic on three
   samples before any promotion.
2. **A declaration-time ambiguity check over-fires.** It refused MPMCALLB, which DR compiles. The
   DUPLIC half survived the whole panel; the QUALIFY half must become lazy.

**Reverted.** With resolution on, negative-panel **E27S12 — a program DR refuses — compiled
silently**. A wrong-acceptance outranks a new capability, so `bind.ml`/`codegen.ml` are back at P1's
state; the tree is 939 byte-exact / 0 fail, 84 coverage rows 0 errors, gate 0.

## CORRECTION to the P2 section above (same session, later)

The revert described above was **wrong** and has been undone — see [C256]. E27S12's panel row was
`kind=refusal, class=my-gap`, i.e. a pin on *my* gap, and its own note said "DR COMPILES IT
(golden/e2e324d/ST12/ST12.REL)". DR's listing line 5 is `i2 = 5`, both passes clean, DATA AREA 0006:
the unqualified internal-member write is DR behaviour. `NEG-FAIL ... compiled silently` is therefore
the fix landing, not a wrong-acceptance. Implementation restored, row retired.

Restored state (commit `dd844be`): my DATA matches DR exactly on E39S2 (0004), E39S3 (0006) and
E27S12 (0006); E39P1 is byte-exact against DR; the member programs are divergences of *one* named
rule [C254] — DR's `PUSH H/POP D` for a member operand vs `XCHG` for a plain variable, same
addresses, same exit registers. Negatives 124→123, divergences 8→12, specimens +1 (939 exact),
coverage 84 rows 0 errors with three obsolete rows corrected, full gate including `--runtime` exit 0.

The genuinely wrong-acceptance that remains is E39X1 (ambiguous unqualified member): DR prints
QUALIFY and emits no .REL, mine first-binds and compiles. The declaration-time check that caught it
also refused MPMCALLB, which DR compiles, so it was removed rather than left to block authentic
programs. It needs a lazy use-site rule [C255].

## For E2E-40, in order
1. Done in this slice: rows restored, E27S12 retired against its authentic golden, negative panel
   re-run clean. Next scope item is the *lazy* QUALIFY rule (E39X1 wrong-acceptance) and the
   qualified internal spelling (`cpb.nameadr = addr (procname)`, MPMCALLB — on the critical path,
   same shape as E39S1).
2. DR's member operand-preservation rule (C254): `PUSH H/POP D` instead of `XCHG` when an operand is
   a structure member. One controlled pair exists (E39P1/E39S2); needs the relation × operand-position
   matrix before it generalizes.
3. Lazy QUALIFY at an unqualified use; qualified internal references (`cpb.nameadr`, MPMCALLB) are
   on the critical path and share this shape with the unqualified fix.
4. Nested internal structures: DR's S5 == S2 at DATA 4, my frame came out 6 — bind re-dispatches a
   head for a level-2 sibling after a level-3 member.
