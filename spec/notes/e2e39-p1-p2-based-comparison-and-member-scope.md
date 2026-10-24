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

## For E2E-40, in order
1. Re-apply the member rows gated to non-BASED, non-view members, and re-run the negative panel
   FIRST — E27S12 is the gate, not an afterthought. Establish what E27S12 declares before widening.
2. DR's member operand-preservation rule (C254): `PUSH H/POP D` instead of `XCHG` when an operand is
   a structure member. One controlled pair exists (E39P1/E39S2); needs the relation × operand-position
   matrix before it generalizes.
3. Lazy QUALIFY at an unqualified use; qualified internal references (`cpb.nameadr`, MPMCALLB) are
   on the critical path and share this shape with the unqualified fix.
4. Nested internal structures: DR's S5 == S2 at DATA 4, my frame came out 6 — bind re-dispatches a
   head for a level-2 sibling after a level-3 member.
