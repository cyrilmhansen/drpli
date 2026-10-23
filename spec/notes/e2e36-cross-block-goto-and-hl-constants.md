# E2E-36 — cross-block GOTO, and what DR's HL register model actually is

Episode scope (from the task): (P1) probe what DR does with a `GOTO' whose label lives in another
block, (P2) implement it, (P3) get an execution witness for a nonlocal transfer, (P4) close the
residual difference the probes exposed, (P5) a machine-readable coverage inventory, (P6) a fresh
corpus sweep, (P7) a bounded differential probe generator.  P1-P4 are done and committed; P5-P7 are
not started.  Gate at the P2-P4 commit: **933 byte-exact / 0 fail, 124/124 negatives, 9/9
divergences as recorded, 16/16 runtime, exit 0** (was 891 / 122 / 12 / 15).

## P1 — the probe matrix, and the two things it settled

Seventeen sources (`artefacts/E36T2..T17.PLI`, `NETWORK` reused), compiled by DR with
`$L$D$C$S` into `golden/e36t/`.  Two questions were open from E2E-35 and both are answered by
which block ends up holding the cell:

- **Ownership, not proximity.** E36T13 (a reference from inside a nested `begin ... end;') and
  E36T14 (a grandchild naming main's label) both give main the pad and the saved-SP cell; the
  intermediate block gets neither.  E2E-34/P5's `on_facts` asked the question of the *referencing*
  block, which is why it worked for every same-block specimen and produced refusals for everything
  else [C233].
- **A procedure entry is not a label.** T9 (main's own nested proc), T10 (a name that is both),
  T15 (upward), T16 (sibling), T17 (itself) all get `NOT LABEL' from DR — five orientations, five
  identical diagnoses [C234].  That settled whether the scope chain should be able to resolve a
  procedure name: it must not, so procedure entries are filtered out of the owner block's label set
  and the resolver answers `Lbl_not_label'.

A third result was negative and useful: a plain `GOTO' inside the block that owns the label does
NOT make it pad-bearing (T11/T12, byte-exact with no cell), so the rule is not "mentioning a label
costs a pad".

## P2 — one survey, one chain, three bugs

`bind.ml` walks the block tree once (`survey`/`survey_all`/`facts_of`), resolving each label
reference against the blocks visible from where it is written and propagating unresolved references
upward so that a descendant's reference charges its owner.  `section2` consumes that plan for the
cell; `codegen.ml` consumes the same plan through `pl_top_on`/`pl_on` and resolves references by
walking `ls.chain`, a list of `(scope, own, procs, pads)` frames pushed by `lower_proc`.
`resolve_label` returns `Lbl_here`, `Lbl_here_fwd`, `Lbl_pad`, `Lbl_pad_fwd` or `Lbl_not_label`,
and the pad-vs-direct answers are what the E36T goldens show.

Three defects surfaced, all of them in the plumbing rather than the model, and all caught by the
[C202] disagreement assertion between Bind's demand and codegen's resolution:

1. `List.concat_map fst kid_unresolved` collected the wrong element of each child's pair, silently
   dropping every unresolved reference — so an outer label looked undefined.
2. The chain slot for the enclosing frame pushed `ls.on_pads`, which by then was the CHILD's empty
   list; it has to push the `saved_pads` captured before the [E2E-34/P1] swap [C235](a).
3. Forward slots were keyed by name, which lets an inner definition satisfy an outer reference in
   the [C228] shapes (E35X1/E35X4 define the same label name at two levels) [C235](b).

Result: 12 of 14 cross-block probes byte-exact on the first coherent build; the other two were P4's
problem, and one of them turned out to be a wrong-value defect that had nothing to do with
transfers.

## P3 — a nonlocal transfer, executed

`E36R1` (`artefacts/E36R1.PLI`, `golden/e36r/`): main declares an `on endfile(sysin) goto done;`
unit, accumulates `tot` at `loop:`, and its nested procedure does `n = n + 10; goto loop;`.  The
transfer is taken, so the run goes through main's recovery pad (`LHLD` saved-SP / `SPHL` /
`CALL ?RECOV`) rather than through the callee's return path, and the printed value is main's own
local accumulated across three arrivals at `loop` — one fall-through, two through the pad.
Expectation `tot=        13`, hand-derived (0+1, then n = 11, 12; tot = 1 + 12).  Both images print
it; runtime panel 16/16.  The row's own caveat is the [C137] one: mine's `.REL` is byte-identical
to DR's here, so the run validates the expectation and PLILIB, not the lowering — what it adds over
E35N1/E35N2 is that the transfer is CROSS-BLOCK and the value that survives it belongs to the block
whose frame the pad re-establishes.

## P4 — the HL constant model, and the kill that was in the wrong place

I planned this phase as "add an HL tracker like the DE one" and wrote ~200 lines of `hl_val` /
`hl_wait` / `hl_written` / `hl_reuse` against 15 probes.  The build failed on an anchor, and while
fixing the anchor I went and read the code the patch was supposed to extend: `st.last_imm` — "HL
still holds this constant? [G114 b=3 folded from a=5]" — **already is that model**, with the bump
arms, the `MVI L` arm, the +/-256 arms and the no-load arm.  The patch was never applied.  What was
actually wrong was four small things, each pinned by a probe:

- `kill` sites.  DR forgets HL at branch **targets** and at instructions that write HL; it does not
  forget at the **source** of an unconditional branch.  Mine killed in `Ast.Sgoto` (three sites,
  including the pad stub's `JMP`), which cost six byte-exact goldens: E35Y3, E35X5, E36T3, E36T4,
  E36T5, E36T8 all store a constant in the statement after a `goto' and DR bumps (`INX H / SHLD',
  4 bytes) where mine reloaded (`LXI H,nnnn / SHLD', 6 bytes).  The kill now sits at the IF joins
  (`E36H8` for a plain IF, `E36H35` for the conditional landing pad with an ELSE), at label
  definitions (`E36H29`: `n = 5; l1: n = 6;' reloads where the same pair with no label bumps), and
  at the GOTO join (`E36H32`, whose two incoming edges carry 5 and 1).  That is the same set of
  places [C220] established for DE, so it is one model with one kill rule rather than two.
- A null store published nothing, so `p = null; p = null;' (E36H11) and `p = null; n = 0;'
  (E36H12) reloaded; publishing `HL = 0' from `hl_zero` closed both, and closed E29X3 and E30L1,
  which had been pinned divergences for two episodes on exactly that load.
- The zero arm of the store ladder published `last_imm` BEFORE calling `hl_zero`.  Harmless while
  `hl_zero` ignored the field; once it consulted it, a program's very first zero store emitted no
  load at all (E29X3 went 3 bytes over, then 3 under).  Ask, then publish.
- The plain pointer-store route cleared `last_imm` AFTER lowering the value, i.e. after the loader
  had established it.  Moved to before, like the self-add and DEC arms next to it — with the
  `null()` shape exempted, because that is the one whose loader ends by publishing the constant it
  is about to store.

The ladder's arms, with the probes that fix them, are in [C237].  Two of them were surprises:
`MVI L` has no small-delta limit (H33 delta 5, H34 delta 14 both take it — so H8's reload is the
join kill and not a limit), and reuse is destination-independent (H30: `m = 5; n = 6;' bumps),
which is the same "it is the register, not the variable" fact the DE tracker's V-series established.

## P4 — two defects, one on each side

- **Mine.** `E36T4` declares `inner` inside `sub`.  The [E2E-28/P1] branch-over JMP was gated on
  `not st.in_proc`, so inside a procedure body no jump was emitted and no slot was resolved:
  `n = 4;' fell straight through into `inner'`s body.  Wrong value, three bytes, and the reason no
  earlier specimen caught it is that none had a procedure nested inside a procedure with the
  declaration at the end of the enclosing body [C238].  E36T14 is the same hole; both are
  byte-exact now and registered as specimens.
- **DR.** `E27S2` (`artefacts/ST2.PLI`) stores `addr(z)` into a record's POINTER member and DR
  writes `LXI D,*A / MOV M,E / INX H / MOV M,D` — the high half of the address at the lower byte,
  i.e. a byte-swapped pointer.  The call site's comment in my tree had described DR's order
  correctly for two episodes while the code emitted the opposite, which is why the row read as "one
  byte DR adds that I cannot find".  Reproduced as DR's, recorded as a DR defect [C236]; no runtime
  row claims it, because ST2 never dereferences `nx`.

## P6 — the historical corpus, re-swept with this build

`golden/first8080u/<NAME>/<NAME>.REL` paired with `artefacts/<NAME>.PLI`: **44 pairs, 15 byte-exact,
0 divergent, 29 refusals.**  The E2E-35/P3 baseline was 41 pairs / 15 / 0 / 26 [C230]; the pair count
grew because three more corpus sources are now in `artefacts/`, and the exact set is *identical*
(A, DECPOLY, DEMO, DFACT, DTEST, FDTEST, FFACT, FLTPOLY, FLTPOLY2, IFACT, LOAN1, NETWORK, REVERSE,
RFACT, TEST).  That is the check this commit needed: the survey rewrite and the HL kill set both sit
in code shared by every program, and the corpus contains no cross-block transfer at all, so the
correct result is "nothing moved" — a byte-exact count that stays put and a divergence count that
stays at zero.  The top refusal reasons are unchanged too (array element width, `BASED` on a
non-bare operand, `STATIC` on character, multi-dimensional arrays, `ON ERROR`, long FILE names).

## Harness caveat, because it changed how I read one number

The throwaway driver I used for the probe-by-probe diagnosis (`/tmp/e36/check.py`) invoked the
compiler with `--layout v7 --org 0x100 --rel OUT IN`; the CLI in this tree takes
`pli80c [-d] INPUT.PLI OUTPUT.REL` and rejects that form with a usage error and rc=2.  Its outputs
moved in response to each codegen edit, which is what a fresh compile looks like, and every
conclusion I drew from it was re-verified through `tools/e2e_gate.py --update-divergent` and the
committed panel (each closed divergence became a byte-exact specimen compiled by the gate itself).
So the substance survived; the lesson is the [C224] one again — an ad-hoc harness that nobody else
can re-run is not evidence, and the corpus sweep above was deliberately written against the gate's
own `compile_one` argv so it can be.

## Panel state and what is still open

- Promoted to specimens: E35X5, E35Y3, E35Y4 (refusals in E2E-35/P3), E36T2-T8, T11-T14, E35X1/X2/X4/Y1/Y2,
  24 `E36H` ladder probes, and out of the divergence panel: E29X3, E30L1, E27S2.
- Registered as negatives: E36T9/T10/T15/T16/T17 (`dr-refuses`, NOT LABEL) — 124/124.
- Divergence panel, 9 rows, unchanged in shape: E28N7, E30G1, E30L2, E30L3, E30L4, E32B3, E32C6,
  E33MC, PB4.  E30L2/L3/L4/G1 are still one HL reload over; the `null()` arm that closed
  E29X3/E30L1 did not reach them, so the remaining reload is in the traversal/based-member route
  and is NOT the same rule as the ones closed here — pinned rather than fitted, per [C179].
- `E36H13` does not parse here (`begin ... end;` as a statement, the [E34A9] shape) and it is not
  registered: DR's own answer for that source should be established before it becomes a row.
- Untouched: DECIMAL and NUMERIC backlog, P5 coverage inventory, P6 corpus sweep, P7 differential
  generator.
