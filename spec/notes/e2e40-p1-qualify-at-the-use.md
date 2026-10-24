# E2E-40 P1 — DR raises QUALIFY at the use, and the candidate set is the visible one

Baseline `0df3900` verified first: build clean, `e2e_gate.py --runtime` exit 0 at
939 byte-exact / 0 fail, 123 negatives, 12 divergences, 18/18 runtime, 84 coverage rows.

## What E2E-39 left

C255 said "QUALIFY is real but must fire at the **USE**, not at a declaration", because the
declaration-time version over-refused MPMCALLB. E39X1 was carried as a live wrong-acceptance:
my binder picked a first binding and compiled a program DR produces no object for.

## DR's verdicts (5 probes, tag e40a + 1 existing golden)

| probe | shape | DR |
|---|---|---|
| E39X1 | `1 g, 2 a fixed` + `1 k, 2 a fixed`, unqualified `a = 3; put list(a)` | PASS 1 **clean**; `QUALIFY ?` under BOTH uses; `2 ERROR(S) IN PASS 2`; **no `.REL`** |
| E40Q1 | same declarations, all references **qualified** `g.a`/`k.a` | **compiled**, CODE 0036 / DATA 0008 |
| E40Q2 | two structures, **disjoint** member names, all unqualified | **compiled**, CODE 0036 / DATA 0008 — same sizes as E40Q1 |
| E40X3 | internal `1 g, 2 a fixed` + **BASED view** `1 k based(p), 2 a fixed`, unqualified `a = 3` | `QUALIFY ?` at the use, 2 errors PASS 2, **no `.REL`** |
| E40N1 | member `a` of an **enclosing** structure, referenced unqualified from a nested procedure | **compiled**, CODE 004C / DATA 0006 |
| E40Q4 | MPMCALLB's shape: `1 cpb, 2 nameadr pointer, 2 paramadr pointer`, `cpb.nameadr = addr(t)`, `cpb.paramadr = cpb.nameadr` | **compiled**, CODE 003E / DATA 0008 |

Three things follow. Ambiguity is a property of a *use*, one error per use, raised in pass 2 — so
no declaration-time filter can be the mechanism. The candidate set is over member **names** as an
unqualified reference can see them, not over cell-owning declarations, because a BASED view's
member counts (E40X3) while owning no storage. And the visible set spans enclosing frames, because
DR resolves an outer member from inside a nested procedure (E40N1).

E40Q1 vs E40Q2 also extends C253: qualified and unqualified spellings of the same layout are
identical in **code size as well as DATA** (0036/0008 both), so qualification leaves no trace in
either area.

## Implementation

`bind.ml`: `check_qualified_uses`, called from `layout` — the per-frame authority every frame
goes through (`bind_rows -> layout`, and the dump path calls it too), so each frame is checked
exactly once. It builds a candidate table from `RTimem` **and** `RTbmem` rows, walks the frame's
statements for bare `Ast.Eident` occurrences (`Sdcl` skipped, `Sproc` not descended into — that
frame is checked by its own `layout` call), and refuses the first ambiguous use quoting DR's own
diagnostic. `pl_kids` was relocated earlier in the file rather than duplicated. `is_cell` was
hoisted to `is_cell_rt` so DUPLIC and QUALIFY agree on what a cell-owning name is.

Controls, measured: E39X1 refuses (QUALIFY), E40X3 refuses (QUALIFY — previously it refused with a
bogus "conflicting kinds" from codegen), E39X2 refuses (DUPLIC, unchanged), E40Q1/E40Q4 get past
bind untouched and stop later at the unresolved qualified reference (P2's job), E40Q2/E40N1/E39S2/
ST12 compile, MPMCALLB passes bind and stops at `STATIC on CHAR(27)` — no false ambiguity anywhere.

Gate: **939 byte-exact / 0 fail, negatives 123 → 125, divergences 12 → 14, coverage 84 → 85 rows
0 errors.** The two new divergences (E40Q2, E40N1) both have DATA agreeing with DR and differ only
in code shape — C254 again; E40N1 is the first row in that file whose code is *shorter* than DR's
(73 vs 76).

## Two process findings

1. **The E39X1/E39X2 negative rows never existed.** This episode's inherited summary said E2E-39
   added them and the panel read 124; `git show` finds `E39X` in *none* of the commits. The count
   arithmetic was actually consistent (124 − E27S12 retired = 123), which is why "123/123 passed"
   never looked suspicious. A patch printing `gate rows added` is not evidence the content is in
   the file — the file has to be read back. PERIMETER's own wording was correct throughout (it
   said E39X1 compiles here and must not be trusted); the overstatement was only in the session
   summary. The rows are registered for real now, anchored to DR's transcripts.
2. **My own regex rewrite ate part of my own comment.** `re.search(r"Scope is the frame:[^*]*", ...)`
   ran past the intended sentence into the next paragraph, and the file was written with that text
   lost. Caught only because a follow-up patch asserted on the vanished anchor. Narrow anchors and
   exact replacements beat `[^*]*` spans.

## Limits this increment leaves open (all in PERIMETER / the new coverage row)

* Qualified references to internal members do not resolve yet, so the remedy DR names for an
  ambiguous program is unavailable — E39X1 cannot be made to compile either way. (P2.)
* An ambiguity declared in an *enclosing* frame and used inside a nested procedure is missed:
  `outer_rows` exists but no caller threads it, because `bind_rows` has no ancestor knowledge and
  threading it means changing `section2`'s signature. E39S4, the probe meant to measure this, was
  written malformed (`end b9e;  s: procedure;`) and says nothing.
* Ambiguous names inside `INITIAL`/`DIMS`/`ATTRS` are not treated as uses — unprobed shape.
