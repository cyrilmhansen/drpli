# E2E-22 — variable-index arrays, element arguments, and the integration programs

Gate at completion: **582/582 byte-exact, 101/101 negatives refused, divergence panel 4/4,
inventory 582 rows reconciled, exit 0.** Corpus sweep re-run after the DO-bound change (see §5).
Baseline was `ab15141` (E2E-21 P0, 568/568/106/3/674). Fourteen programs joined the byte-exact
panel and one joined the divergence panel; nothing that was accepted before changed.

---

## 1. Priority 1 — the address ladder, and C159's operand was wrong

E2E-21 measured a ladder and recorded its operand as `base + (lb-1)*(-2)`. Three goldens with
three different lower bounds settle it, by reading the DATA relocation addend that DR attaches to
the ladder's first instruction:

| probe | declaration | lb | addend | `base - lb*esz` | `(lb-1)*(-esz)` |
|-------|-------------|----|--------|-----------------|-----------------|
| VB1   | `a(0:3)`    | 0  | 0x0000 | base + 0  ✓     | base + 2  ✗     |
| AB2   | `a(5)`      | 1  | 0xFFFE | base - 2  ✓     | base + 0  ✗     |
| VB2   | `a(2:6)`    | 2  | 0xFFFC | base - 4  ✓     | base - 2  ✗     |

VB1 and VB2 exist only to make this table have three rows. The rule is
**operand = array base - lower_bound * element_size**. C159's wording is corrected in place by
C172, and the stale sentence inside the gate's `_ARR` note — which is embedded in inventory rows
for several still-open negatives — was rewritten, because a note that says "my parser has no
array declaration form and bind has no array sizing" is simply false now and would mislead the
next reader about what an open row means.

### Two forms, and why the choice is forced

```
bias = 0   (lb = 0, VB1):   LHLD idx [; INX H] ; DAD H ; LXI D,<base>  ; DAD D      (7 bytes, no stack)
bias <> 0  (AB2 VB2 AB8 AB10):
                            LXI H,<biased> ; PUSH H ; LHLD idx [; INX H] ; DAD H ; POP D ; DAD D  (13 bytes)
```

`LHLD idx` destroys HL. When the biased operand differs from the plain base, that base value has
to survive the load, and DR parks it on the runtime stack — the C141 discipline (never preserve
across a destroying operation in a register) applied to an address rather than to a value. When
the bias is zero there is nothing to preserve, so DR reorders: compute `2*idx` first, then add the
base in from DE. The difference is not stylistic, and it is not an optimization choice I could
have guessed — it is two different instruction sequences, both measured.

The doubling is `DAD H` on the **index**, and the second copy comes from the parked value, so the
ladder's own `PUSH H / POP D` pair nests inside a caller's parking pair. That composition is what
AB8 and AB10 show for a computed store (§3), and it works without any special case: the ladder is
just another HL producer.

### Index expressions

`a(i+1)` (AB8) emits `LHLD i / INX H / DAD H`. The `+1` is applied to the **index value before the
doubling**, so it moves exactly one element; applied to the address it would move two. Only `+1`
is DR-measured. `i+k`, `i-1`, `i*2`, and an element as an index all keep refusing with a message
that names what is unmeasured, rather than extrapolating `INX H` repetition — the E2E-13 rule.

### Representation

`resolve_suffix` gained a third case, `Suf_element_dyn of dyn_ref` (base, bias, index expression,
index adjustment). It is still an **array reference**, not a call: making it a `Suf_call` variant
was the misdiagnosis behind C165, and the discriminated type plus guarded match cases is what
keeps that from recurring. No new storage rule and no new sizing authority — the ladder emits
ordinary 2-byte DATA relocations, and `bind.layout` remains the only place array extents are
decided [C164/C167].

---

## 2. Priority 2 — reads, stores, and where the value actually lands

The read tail is `MOV E,M / INX H / MOV D,M`, i.e. the value arrives in **DE, not HL**. What
settles the register contract is the DR continuation, not the tail:

* AB2 `b = a(i)` continues `XCHG / SHLD b`
* AB8/AB10 `put skip list(a(i+1))` continues `XCHG / MVI A,09 / <numeric PUT tail>`

So DR normalizes to HL with `XCHG` in every measured case. Emitting that `XCHG` inside the read
preserves `lower_hl`'s HL invariant, and every existing consumer — scalar store, PUT item,
arithmetic — worked unchanged with no routing edits. That is the cheapest possible confirmation
that the contract was read correctly: nothing downstream had to move.

Store tails, both measured:

```
literal value   (AB2 VB1 VB2) : <ladder> ; MVI M,lo ; INX H ; MVI M,hi
computed value  (AB8 AB10)    : lower_hl(rhs) ; PUSH H ; <ladder> ; POP D ; MOV M,E ; INX H ; MOV M,D
```

The computed form parks the value **before** running the ladder, so two stack slots are live at
once and the outer `POP D` recovers the value into DE immediately before storing. This is E2E-20's
byte-order lesson still in force: `0x73` is `MOV M,E` (low byte) and `0x72` is `MOV M,D` — my
first cut of this tail omitted the second `MVI M` opcode for the literal form and emitted the
high byte bare, which disassembled as `INX H / NOP`. It cost exactly one byte of diagnosis.

Not measured, therefore refused: a computed store whose bias is 0 (both measured computed stores
carry nonzero bias, so whether DR still nests a parking pair when the ladder itself parks nothing
is unknown), and a variable-index self-update like `a(i) = a(i) + 5` (AC4's form-4 rule is
constant-index only).

Slice coverage as specified: literal store ✓ (AB2 VB1 VB2), element read into scalar ✓ (AB2),
PUT LIST item ✓ (AB8 AB10), computed-value store ✓ (AB8 AB10), index expression `a(i+1)` ✓ (AB8).

---

## 3. Priority 3 — element as actual: there is no array calling convention

DR hands the callee the element's **address** through the ordinary pointer-formal descriptor
[C130]:

```
AB7      call p(a(4))            : LXI H,<a+6> ; SHLD <desc cell> ; LXI H,<desc> ; CALL p
PASSARAY call inner(argument(I)) : <ladder>    ; SHLD <desc cell> ; CALL inner
```

The variable form composes for free, because the ladder already leaves the address in HL. Both
take the **dynamic** descriptor route — runtime `SHLD`, bare `RELOC`, no `SET-LC` wrapping — which
is the route E27B established for a forwarded pointer formal. It is worth stating explicitly that
this is slightly surprising: a constant-index element address *is* statically known, and a plain
scalar-variable actual gets a static descriptor word, yet DR still writes the element's address at
runtime. Byte parity is the only reason I would have noticed if I had "simplified" it.

**bind**, not codegen, carries the other half: `cs_temps` classifies an argument as needing an
anonymous value cell, and an element actual must be treated as simple. DR allocates none for AB7
or PASSARAY. Had I patched only codegen, the descriptor store would have been right and the data
area one cell too large, with every later anonymous-cell number shifted — i.e. I would have
broken the C145 numbering that four accepted specimens depend on. Width is checked against the
formal and refuses on mismatch, because DR's widening route for a narrow actual copies through an
anonymous cell [E29C] and that is unmeasured for elements.

Checkpoint C (can the callee mutate the original element?) is answered **yes**, by EA2: it passes
`a(4)` and `a(i)` to a procedure whose body is `x = x + 100`. My `.REL` is byte-exact against DR
(DR reports NO ERROR(S) in both passes), and both linked `.COM`s print `106 100` — a(4) went
6→106 and a(2) went 0→100. Mutation through both a constant and a runtime index, verified by
execution rather than by inference.

EA2 had to be written in AB22's proven arrangement (`stop;` **before** the appended procedure).
AB7 itself is AB14's shape — a main-block statement after an appended procedure — whose DR layout
is still unproven, so AB7 and a new probe EA1 (AB7's shape with the array work added) stay
negatives with that marker. They no longer stop on arrays at all, and their notes say so.

---

## 4. Priority 4 — the last mile was `put skip(one)`, and behind it a real miscompile

Both PLI-2000 integration programs stopped on one line shape: `put skip(one) list('...')`. Four
probes isolated it in one batch:

| probe | form | before | after |
|-------|------|--------|-------|
| SK1 | `put skip list('abc')` | byte-exact | byte-exact |
| SK2 | `put skip(2) list(x)`  | byte-exact | byte-exact |
| SK3 | `put skip(one) list(x)` | **refused** | byte-exact |
| SK4 | `put skip(one) list('abc')` | **refused** | byte-exact |

So neither the character-literal item nor the parenthesized literal count was missing — only the
runtime count. DR's form is `LHLD one / MOV A,L / CALL ?SKPOP`: it keeps only the **low byte** of
the expression value, the same 8-bit quantity the `MVI A,n` immediate carries, with no range check
and no widening [C174]. Only a bare variable is measured, so anything else refuses — the value
lives in A between the load and `?SKPOP`, and any intervening call destroys it, which is C141's
hazard in a new place.

Independent corroboration, and the kind you cannot arrange on purpose: **N4_SKIPVAR**, an E2E-8-era
inline negative with its own older golden (`golden/negpanel1/NG36`), became byte-identical under
this rule. Two DR goldens built through different batches agreeing on one instruction sequence
retires a negative the only legitimate way [C154].

Then PASSARAY and ARRAY compiled — and were **wrong**. Linked with LINK 1.31 and run under cpmsim,
against DR's own `.COM`s:

* PASSARAY: mine **69900 lines**, DR **75**
* ARRAY: mine **139580 lines**, DR **75**

Both `rc=0`. Both "compiled". The cause was a single missing 4-byte tail: DR reads a pointer
formal in a DO bound position by dereferencing it (`DO1: do j = 1 to x`, `DO2: do j = x to 5`),
and I used the pointer's *content* — an address — as the bound. Same cells on both sides of the
relocation stream, so this was not a layout disagreement; mine stored the address where DR stored
`MOV E,M / INX H / MOV D,M / XCHG` first [C173].

Two things about this deserve to be kept as method, not just as a fix:

1. It predates E2E-22 entirely. Nothing in the array work caused it; the array work is what made
   a program reachable that exercises it. A latent defect in `lower_doto` had been invisible for
   eleven episodes because no accepted specimen put a formal in a bound position — the panel
   counted refusals and bytes, and this shape was neither.
2. Byte parity would not have caught it either, had DR's bytes also been matchable by luck. The
   only reason it surfaced is that Priority 4 asked for **executed output**, not for a `.REL`.
   That is C137 ("do not accept on REL parity alone") earning its keep for the fourth time.

The fix is conditional on `st.deref`, so every non-formal bound (NFACT, RFACT, IFACT, the whole
R10xx bank) emits exactly what it emitted before — and the corpus sweep was re-run afterwards to
confirm no accepted program shifted. DO1 prints `1 2 3`, DO2 prints `3 4 5`, both identical to DR.

---

## 5. Panel state and what it means

* **Promoted from negative to specimen** [C154]: AB2, AB8, AB10 (variable-index store/read),
  PASSARAY (integration, byte-exact + runtime-identical), N4_SKIPVAR (runtime SKIP count).
* **New specimens**: VB1, VB2 (the two ladder forms and the bias operand), EA2 (element-as-actual
  mutation), SK1–SK4 (PUT SKIP forms), DO1, DO2 (pointer-formal DO bounds).
* **New negative**: EA1 (AB7's shape; stops on the unproven append layout).
* **Re-marked, not deleted**: AB7 → append layout; ARRAY → out of the negative panel entirely.
  The old pinned reason "runtime-variable array subscript" is now a rule that works, and leaving
  it pinned would have asserted a gap that no longer exists.
* **DIVERGENT panel** [C168/C171]: ARRAY added, shape measured rather than guessed — mine 181 code
  bytes vs DR 180, DATA area 62 = 62 (so layout and array sizing agree), 438 of 640 bytes differ,
  runtime output line-for-line identical to DR's (1121 bytes). Cause is the C168 peephole family:
  DR writes `XRA A / MOV M,A` for a zero store where I write `MVI M,00`. Priority 5 excludes C168
  optimization, so ARRAY is recorded as divergent — a specimen row would claim byte-exactness it
  does not have, and a refusal row would hide that it compiles. Its gate row will fail the day it
  becomes exact, which is the point [C171].
* Untouched: C161 mixed DEC/BIN, C146 record placement, ARCH-1 (`ocaml/proto/` md5 unchanged),
  the C155/C162 demand/layout invariant (the ladder and the descriptor route add no pool cells;
  `emit_skip_count` and `do_bound_deref` emit code only).

Registration discipline slipped once in this episode and the gate caught it: my own edit script
used `str.replace` with a pattern that did not match, so EA1 sat in the marker list but was never
added to `REJECTS` — a panel entry that quietly disappears. The replacements are now
anchor-asserted, and the `REJECTS`/`NEG_META` symmetry guard did the rest [C163/C158].

---

## 6. What is still open

1. **C168 peephole family** — cross-statement constant reuse (`INX H` chains, `MVI L,k`,
   `XRA A/MOV M,A` for zero stores). Promotes AB19, AB21, RT1, and ARRAY from divergent to exact.
   One project, explicitly not started here.
2. **AB7 / EA1 / AB14 append layout** — a main-block statement after an appended procedure. Needs
   DR's ordering proven, not assumed [C146-class].
3. **AB13 multi-dimensional indexing**, **AB5/AB15 STATIC arrays**, **AB11's condition form**.
4. **Named FILE I/O** (`?OIOOP`/`?SIOOP`) — PUT/GET with a FILE clause or ON options (PU1, KEYFILE,
   CREATE) and the `PUT LIST` file-stream route.
5. **C161 mixed DEC/BIN** — needs the inbound expected-context argument to `lower_hl`.
