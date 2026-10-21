# E2E-20 — indexed-reference resolution; constant-subscript array reads and stores

Baseline `06f719b`→`06f737b` verified before starting: clean tree, fresh build, 546/546 byte-exact,
117/117 negatives, inventory in sync (663 rows), no missing goldens, 6 spot-checks re-run against
a freshly built binary (DECPOLY FFACT P9 U1 AR1 R3062 all exact).

---

## 1. Priority 1: what actually crashed (C165 corrected)

Reproduced `spec/patches/e19-array-read-attempt.patch` in a worktree (`/tmp/e20`), added one
probe *after* the suspect branch:

```
DBG READONLY nm=a arrays=1 [a] exts=false procs=false
DBG REACH-THROUGH into call setup for nm=a
Fatal error: exception Not_found
```

One resolution, not two. E2E-19's patch inserted

```ocaml
if is_array then begin <emit LHLD> end
else if not (mem_assoc nm st.procs || mem_assoc nm st.exts) then failwith "call to unknown"
let ext = List.assoc_opt nm st.exts in      (* <- runs unconditionally after the if *)
... List.assoc nm st.procs                  (* <- raises *)
```

into the body of lower_hl's existing `Ast.Eident h, args ->` arm. Both `if` branches have type
`unit`, so the `if` is a statement and the sequence **continues into the call machinery**. The
element emitted a correct `LHLD` and then the call route ran on it anyway.

Consequences:

* There was no "genuinely broader architectural dependency". The requirement was an early exit.
* The fix is a *guarded match case*, which makes fall-through structurally impossible instead of
  relying on care. Every array route in this milestone is written that way.
* Methodological: the trace named `lower_hl`, and the "PUT re-lowers the same Esuffix" story was
  accepted because it fitted C161's unrelated need for type context. A line number is not a
  causal explanation. One extra probe placed after the suspect branch settles it.

## 2. Priority 2: the resolution mechanism

Two additions, both in `codegen.ml`, no new IR:

* `hd_is_element arrays hd` / `suf_is_element st e` — a **total** predicate (never refuses, never
  lowers, never allocates) over `st.arrays`, which is `Bind.bind_arrays blk` for the block being
  emitted. Used by every consumer so classification cannot drift from resolution.
* `resolve_suffix st hd args : suffix_ref = Suf_element of int | Suf_call of string * expr list` —
  the single place that decides, returning the relocated element address or deferring to the call
  route. Unsupported shapes refuse *with their reason* inside resolution (variable subscript,
  multi-dimensional, non-literal bound).

Shadowing is by scope, not priority: `st.arrays` is the current block's list and is swapped per
callee (below), so AB1's `dcl a(5) fixed` inside `a: procedure options(main)` wins *in that block*
because the inner list is what is consulted. A name bound as a callable in the referencing block
is still a call. No global "arrays beat procedures" rule exists in this code.

### Nested-procedure scope

`lower_proc` saved/restored `st.vars` but not `st.arrays`, so a callee resolved subscripts against
its caller's block. Now `st.arrays <- pl.pl_arrays @ saveda` on entry and restored on exit, from
the same `proc_layout` record that supplies `pl_rows`. AB22 (array last inside `p`) crashed before
this and is byte-exact after; RT3 is the runtime witness — outer `w(3)` and inner `w(2)` share a
name, and the eight values only come out right if each block uses its own extents.

### Whole-array refusal (negative witness, class `dr-refuses`)

`b = a`, `a = 3`, `put skip list(a)` (GW1/GW2/GW3): DR parses all three (pass 1 clean) and rejects
in pass 2 with `TYPES NOT=`, emitting **no .REL** [golden/e2e230]. Before this milestone my
compiler *accepted* all three and loaded/stored the array's base cell as a scalar — a wrong-value
miscompile, the C139/C150/C162 class. The guard sits in `addr_of` and `vk_of`, the two points every
un-subscripted data reference flows through (rather than at ~10 sites). `vk_of` is guarded too
because prescan asks it for DEC/FLOAT demand; answering `Vint` would size the pool around a
reference DR rejects. `resolve_suffix` uses `addr_of_raw` for the base so subscripted references
are unaffected.

## 3. Priority 3: reads

`LHLD` + 2-byte `Data` reloc at `base + (sub - lb) * esz`, via the existing relocation machinery —
no new record format. Byte-identical in both contexts DR was measured in:

| probe | context | DR form |
|---|---|---|
| RD1 | `put skip list(a(3))` | `LHLD A(0000)+0004 / MVI A,09 / ?QICOP / ?PNVOP / ?QIOOP` |
| RD2 | `a(0:3)`, `put skip list(a(2))` | non-default lower bound |
| RD3 | `b = a(1); c = a(5)` | first and last element inside expressions |

Element-as-actual is *guarded off*: DR puts the element's **address** in the call descriptor
(AB7), which is a different lowering; without the guard the existing argument path would have
lowered it as a value — right-ish semantics, wrong bytes.

## 4. Priority 4: the four store forms (plus the routing fixes that made them exact)

| # | condition | DR sequence | probes |
|---|---|---|---|
| 1 | offset 0, any value | `<value route> ; SHLD base` | AB1 AB16 AC5 AB12 |
| 2 | offset ≠ 0, literal | `LXI H,base+off ; MVI M,lo ; INX H ; MVI M,hi` | AB3 AB9 AB18 AB22 |
| 3 | offset ≠ 0, computed | `PUSH H ; LXI H ; POP D ; MOV M,E ; INX H ; MOV M,D` | AC1 AC2 AC3 RT4 |
| 4 | same element both sides, literal bias | `LHLD ; <bias> ; SHLD` | AB12 AC4 |

Form 4 is tested **before** form 3: AC4 (`a(2) = a(2)+5`) needs no parking, which is what
disproved the literal-versus-computed model as the sole discriminator. `hl_bias` supplies the
route-dependent threshold (k≤3 → `INX H`, else `LXI B,k / DAD B`), matching AB12's k=1 and AC4's
k=5 without new code.

Bug caught by bytes, not by reading: 0x72 is `MOV M,D`, 0x73 is `MOV M,E`. My first draft had the
comments inverted and therefore emitted the halves swapped; AC1/AC2 showed it as a difference.

Three routing defects had to be fixed before the measured forms could be reached — all the same
misclassification (see C169): `expr_contains_call` (AB9 multiply route, control AB23), the ADD
arm's "call on the right" guard (AB6, AC3 — and DR really does *park* for a subscripted operand,
re-confirming C150's syntactic rule), and `num_width` (RD1/RD2).

## 5. C167: the sizing bug AB16 exposed

AB16 differed from DR by **exactly one byte** (index 18, 0x40 vs 0xC0). The decoded records show
why: `LINK-DEF-DATA-SIZE abs 0002` vs DR `abs 0006`. `section2`'s span used `rt_bytes`, which
returns the element size for an array; offsets themselves were packed correctly, so an array that
was *last or middle* in its declaration lost its extent from the module total, and an array
declared *first* looked fine because a later row pushed the `max` past it. AR1–AR5 are all
array-first — E2E-19 tested five layouts and every one was insensitive to the defect.

DR pinned the rule before I fixed it: AB18 (scalar then array) and AB19 (array in the middle)
both report `DATA AREA = 0008`. **A rule verified only in the orientation that conceals its bug is
not verified.**

## 6. C168: what I deliberately did not register

AB19, AB21 and RT1 compile in both compilers and differ only because DR reuses constant registers
across statement boundaries — `INX H` chains (AB19), `MVI L,k` when H is already right (AB21),
`DCX H` plus two fewer DATA bytes (RT1). They are registered as neither specimen nor refusal:
they do not refuse (a negative would claim a `[TBD]` that never happens) and they are not exact.
AB21 and RT1 use distinct high bytes to try to avoid the peephole; AB21 still hit `MVI L`, so the
reuse is broader than "same H". RT2/RT3/RT4 avoid it and are byte-exact.

## 7. Priority 5: runtime and memory-layout evidence

All three programs are byte-identical to DR, linked with LINK 1.31, and run to output **identical
to DR's own `.COM`** (`golden/e20mine_r` vs `golden/e229_r`) and to values computed by hand first:

* RT2 `dcl a(0:3) fixed, t fixed` → `1027 1283 1539 1795 5` — explicit lower bound respected, the
  scalar after the array untouched, four element writes and five reads agree.
* RT3 outer `w(3)` / inner `w(2)` (same name, different extents) with a call between the PUTs →
  `1031 1287 13` then `259 515 771 9` — per-block resolution, and the call still works.
* RT4 `a(2)=b` (form 3), `a(2)=a(2)+5` (form 4), `a(4)=b+1` (form 3), `c=a(2)+a(4)` (park route)
  → `22 18 40`.

Reads alone could not have been witnessed numerically: reading an element that was never written
returns uninitialized storage, where mine would print 0 and DR garbage. That is why the landing
order in the notes is read-first but the *promotion* of RD1–RD3 rests on byte parity, and why the
runtime section belongs to the store commit.

## 8. Boundaries kept (Priority 6)

Refusing, with reason pinned in the panel: variable subscripts [AB2 AB8 AB10 ARRAY PASSARAY],
multi-dimensional/assumed-size [AB13], STATIC arrays [AB5 AB15], element-as-actual [AB7],
element test in a condition [AB11], whole-array [GW1 GW2 GW3]. The binder still refuses
non-2-byte elements and non-constant bounds. C161 mixed DEC/BIN untouched; CB1–CB5/CB7/CB10 still
refuse for the same reason as before. C146 and ARCH-1 untouched; `ocaml/proto/` unmodified.

Marker maintenance: AB2/AB7/AB8/AB10/AB11/AB14/ARRAY/PASSARAY all changed refusal *reason* as
routes moved. Markers were re-pinned to the new reason (via `pop()` then reassignment, because
`NoOverwriteDict` refuses in-place substitution by design [C163]). The first final gate run caught
me forgetting AB14 — the panel exists to notice exactly that.

## 9. Gate numbers (this milestone)

* Specimens: 546 → **568** (+22: RD1–3, AB1 AB3 AB4 AB6 AB9 AB12 AB16 AB17 AB18 AB22 AB23,
  AC1–AC5, RT2 RT3 RT4), all byte-exact on raw bytes.
* Negatives: 117 → **104** (13 promoted away, 3 `dr-refuses` added).
* Inventory: 663 → **672** rows, reviewed line by line; no unnameable removals.
* Historical corpus sweep: unchanged (13 EXACT / 0 DIFFERS / 28 REFUSED) — re-run as part of the
  final verification below.

## 10. E2E-21 recommendation

1. **Variable subscripts** — the last big array gap and the one with the most corpus payoff
   (ARRAY.PL1, PASSARAY.PL1, AB2/AB8/AB10 all stall on it). DR's ladder is characterized in C159:
   `LXI H,(lb-1)*sz / PUSH H / LHLD i / DAD H / POP D / DAD D`, with the pre-biased relocation
   carrying `(lb-1)*sz`. The index cell must be resolved as a variable reference, and the ladder's
   `PUSH H` interacts with C141's no-parking rule, so start by pinning the reloc arithmetic in one
   probe (AB2) before touching PUT/condition contexts.
2. **Element-as-actual** — AB7's golden shows `LXI H,base+off / SHLD descriptor / LXI H,desc /
   CALL p`, i.e. the existing pointer-formal descriptor route (C130) reached from a new operand
   shape. This is the mechanism that finally exercises `resolve_suffix` returning something other
   than an address or a call, so it may want a third `suffix_ref` case (`Suf_element_ptr`) rather
   than a new code path.
3. **Then the peephole family (C168) as one project** — constant-register reuse across statements
   and `* 0` elision (C156) are the same DR optimizer. Implementing it would make AB19/AB21/RT1
   byte-exact specimens from existing goldens, and is worth doing before chasing more singletons.
4. Mixed DEC/BIN (C161) via an inbound expected-context argument on `lower_hl` — the resolution
   work here is the model for carrying the answer, but the change is independent and larger.

## 11. Pre-existing defect found, not fixed (deliberately)

The corpus sweep shows `REVERSE.PLI` ending in a **bare** `Pattern matching failed` at
`bind.ml` line 1054 instead of a `[TBD]` refusal. That is not E2E-20's doing: the same program on
the E2E-10 base tree (`521cacb`) refuses cleanly with `declared variable kind not in supported
subset`, so it now simply gets further and lands in the statement walker `w`, whose `match`
omits `Ast.Salloc _ | Ast.Sfree _` -- and the compiler itself flags this at build time as
Warning 8 (`Here is an example of a case that is not matched: (Salloc _|Sfree _)`). It is masked
in the sweep because REFUSED is defined as rc != 0, which is exactly why the negative panel
greps for `[TBD]` rather than trusting exit codes.

Two-arm fix in `bind.ml`'s walker (`| Ast.Salloc {…} -> …` and `Sfree`, threading their operand
expressions through `w` like the other arms). I did NOT apply it: it is unrelated to arrays, and
editing production code after the final gate would mean a byte-identity claim made against a
binary that had not been re-gated. Recorded for E2E-21 as a small, precisely located item
(`grep -n "Warning 8" ` after a build will name any other partial match of this shape).
