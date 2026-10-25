# E2E-40/P6 — nested internal structure layout: a subgroup reserves nothing, and a code-byte match proves nothing about addresses

## The question

`E39S5` (`declare 1 g, 2 h, 3 a fixed, 2 b fixed;`) came out of P4 with its CODE recorded as
byte-identical to DR's and a 2-byte DATA excess (mine 6, DR 4) attributed, per [C255], to "bind's
head re-dispatch" — a level-2 sibling after a level-3 member supposedly reopening a head. The task
was to find where the excess actually originates, consider at least two explanations, and implement
only a demonstrated general rule.

## The measurement that reframed it

Both compilers' `.REL` files were opened with `tools/reldump.py`, not compared as blobs:

| | DR | mine (pre-fix) |
|---|---|---|
| `a` store | `RELOC data 0x0` | `RELOC data 0x2` |
| `b` store | `RELOC data 0x2` | `RELOC data 0x4` |
| LINK-DEF-DATA-SIZE | 0x04 | 0x06 |

**The code payload is identical because it never contains a member address.** `LXI H,<DATA+off>`
records the segment; the offset is carried by the LINK-CHAIN-DATA / RELOC item. Two of the five
differing file bytes (`0x2F`, `0x38`) *were* those offsets, so P4's "5 differing bytes, all of them
record-length fields" misdescribed its own evidence. [C261]'s conclusion — code closed, only extent
left — was therefore not just incomplete: the two things were the same defect, and it is an addressing
defect, not a size defect. `pli80bind` showed it directly:

    c 0000 .H FIXED BINARY(15,0) MEMBER     <- a GROUP, charged a 2-byte cell as a scalar
    c 0002 .A FIXED BINARY(15,0) MEMBER     <- DR: 0x0000
    c 0004 .B FIXED BINARY(15,0) MEMBER     <- DR: 0x0002

## Root cause

The layout walk classifies an item by `starts_head = lvl <= hl`, where `hl` is the *open head's*
level. In `1 g, 2 h, 3 a fixed, 2 b fixed` the open head stays at level 1 for the whole declaration
(2 <= 1 is false, 3 <= 1 is false, 2 <= 1 is false), so `h`, `a` and `b` are all members. `h` *has a
child*, but nothing in the member branch knows that: a typeless item resolves to the default type
`RTbin 15`, `bytes_of` gives 2, and the group consumes a cell no one declared. Every later member is
pushed up by exactly that 2. **The head path already had the right rule** ("TYPELESS group heads
occupy nothing [EX employee, record, grp]") — it simply did not extend to heads at level >= 2. So the
fix is not a new mechanism; it is the existing invariant, applied once more.

[C255]'s diagnosis is withdrawn: no head re-dispatch occurs, and the nested shape did *not* refuse —
it compiled to a frame 2 bytes too big.

## Evidence, five programs, one authenticated

| program | declaration | DR DATA | DR member offsets |
|---|---|---|---|
| E39S5 | `1 g, 2 h, 3 a fixed, 2 b fixed` | 0004 | 0x0, 0x2 |
| **E40S1** (new) | `1 g, 2 h, 3 a fixed` — group LAST | 0002 | 0x0 |
| **E40S2** (new) | `1 g, 2 h, 3 a fixed, 3 c fixed, 2 b fixed` | 0006 | 0x0, 0x2, 0x4 |
| **E40S3** (new) | `1 g, 2 h, 3 i, 4 a fixed, 2 b fixed` — level 4 | 0004 | 0x0, 0x2 |
| **E40S4** (new) | `1 g, 2 a fixed, 2 h, 3 c fixed, 2 b fixed` — leaf first | 0006 | 0x0, 0x2, 0x4 |
| **ENTER** (authentic historical) | `1 employee static, 2 name CHAR(30) VARYING, 2 address, 3 street/city/state/zip, 2 age, 2 wage, 2 hours` | 00BE | name 0x0, address 0x1F, street 0x1F, age 0x59, wage 0x5B, hours 0x5E, `default` 0x61 |

Each probe varies one dimension, chosen *before* DR was run, with the competing predictions written
down first: mine (group charges 2) = 4/8/8/8, the overlay rule = 2/6/4/6, children-placed-after-the-
group = up to 12. All four landed on the overlay rule.

E40S1 isolates the phantom cell from any level-3→level-2 transition artifact (there is no sibling).
E40S2's two children refute "a group advances by a fixed 2 bytes". E40S3 shows the predicate is "has
children", not "level = 3". E40S4 shows the group is entered at the running offset and its child
OVERLAYS it — which is the same thing ENTER shows with `address` at 0x1F, the base from which
`address = default` copies 58 bytes.

**ENTER is the decisive witness** because it needs no knowledge of my probe designs and no knowledge
of VARYING/DECIMAL widths: it is a *difference* test on an authenticated DR object. Its fixups say
age/wage/hours = 89/91/94 and the following structure `default` = 97; my binder said 91/93/96/99.
Every member after the subgroup exactly 2 high — one phantom cell, and the frame 2 too large.
Recomputing with groups charging nothing reproduces all seven of DR's offsets, and the member sizes
fall out of the differences (VARYING(30) = 31, DEC(3) = 2, DEC(5,2) = 3, DEC(5,1) = 3, employee = 97
= 0x61 = DR's own `default` base).

## Implementation

One predicate plus one branch, in `ocaml/lib/bind.ml`, inside `layout`:

* `group_counts` — precomputed from the very record list the walk iterates (`items`), skipping
  `dpre`-prefixed items for exactly the reason the walk skips them: they are never laid out, so they
  cannot be children. Membership is tested by **physical equality**, not by name, because a member
  name is not unique (`address` can be declared twice) and a name-keyed table would misclassify.
* In the internal-member branch: `Some n` → the item's offset is the running offset and **no**
  advance happens (auto *or* static); the storage row is not emitted, so codegen cannot see a group as
  a 2-byte scalar.

The DATA extent, the fixups and the `.REL` size field all follow from `off`, which has exactly one
authority — no second source of truth, no probe-name special case, no "minus 2" anywhere.

## Result

`946 → 949` byte-exact. E39S5, E40S1, E40S3 are 256/256 identical to DR and registered. Negatives
125/125, divergence panel 12/12 (E39S5's row deleted because the panel *fails* a row that turns out
identical — that failure was the promotion signal; E40S2/E40S4 added, measured by
`--update-divergent`, not typed by hand), runtime 22/22, coverage 85 rows 0 errors, gate exit 0.

E39S5 also links and runs: `.COM` **IDENTICAL** to DR's (6912 bytes), console **BYTE-EQUAL**
(`      16`, 10 raw bytes, DR's authenticated transcript), and 7+9=16 is independently expected.

**But the run is not evidence about the layout, and saying so matters.** The pre-fix frame was
*self-consistent*: the store and the load both used the shifted `DATA+0x2/0x4`, so it printed 16 too.
Execution cannot discriminate this defect class; only the fixup offsets and ENTER's seven member
addresses can. E40S2/E40S4 runtime rows are the more informative ones (their images differ from DR's,
so they test my lowering), and they still cannot see the offset question.

## E40S2 / E40S4: layout closed, code 1 instruction short

Both measure code 67 vs DR 68, DATA **6/6 agrees**, members at 0/2/4 = DR's. The first differing
instruction is `XCHG` where DR uses `PUSH H`, in the second ADD of a three-member sum (`a + b + c`) —
left operand already a computed value in HL, right operand a member. So **[C261]'s "both operands are
members" predicate is too narrow**, and this is the same residual E39S7 pins from a different
direction. I did not touch it: it belongs to the P4 rule, needs its own evidence matrix, and this
slice was scoped to layout. They are registered as DIVERGENT rows with the reason in the row.

## Two tool truths (C265)

`tools/corpus_census.py --verify` compares per-program `dr_verdict, sha_ok, mine, mine_bytes,
differing_bytes` — **not `msg`** — and only `--check` writes the committed snapshot. So the panel is
structurally blind to a blocker moving, which is why [C263]'s transition was found by hand and why my
first automated check of *this* transition printed "0 programs changed": it compared a stale snapshot
against a file no gate run had rewritten. Fixed by adding `msg` to the compared fields — measured
first: 41 of 44 messages already matched, and the 3 that drifted are exactly this change — then
refreshing with `--check` against HEAD's snapshot, which also proved the counts identical.

## Blocker transitions, per program

ENTER and UPDATE: `STATIC on ... MEMBER OF EMPLOYEE@31` → back to `statement kind not in supported
subset (line 37 / line 31)` — the keyed `open file(emp) ... environment(f(128),b(8000))`. REPORT:
`EMPLOYEE@31` → `STATIC on CHAR(15)`. **This retracts [C263]'s interpretation**: P4 did not unblock a
statement class in ENTER/UPDATE; it inserted a *spurious* refusal ahead of the real one, and the real
one was there all along. MPMCALLB / FSCAN / LOAN2 never moved. Also corrected: C263 listed MPMCALLB
among the programs whose message changed, which is false — its blocker has been
`STATIC on CHAR(27)` throughout.

Net: the nested-structure class no longer contributes a refusal anywhere, and ENTER/UPDATE/REPORT
stand where they stood at P3 — ENTER/UPDATE on keyed FILE support, REPORT on static character cells.

## Not claimed

Nested structures are **not** "supported". Still unmeasured or unsupported: the `$S` dump *spelling*
of a subgroup (`STRUCTURE LEVEL n, MEMBERS k` at level >= 2 is an analogue of the head line, chosen
not observed — golden/bind1's six DR dumps contain only LEVEL 1 structures with leaf members);
whether `MEMBERS k` counts direct or subtree members; bare GROUP-name references
(`address = default`), which now refuse instead of resolving to the phantom cell (a refusal is better
than a wrong-width copy, but DR's behaviour for that shape has no sample); arrays inside level-numbered
structures; subgroups inside BASED views (the head path is untouched); CHAR/BIT/DEC/VARYING members
[C228]; STATIC INITIAL on a member; level ordering inside one item list is assumed well-formed nesting.
