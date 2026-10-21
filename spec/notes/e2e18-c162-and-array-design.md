# E2E-18 — C162 resolved, and the array implementation plan left ready to execute

Baseline HEAD cb175a7 (532/532, 110/110). Result: **541 byte-exact / 0 fail, 109/109 refusals,
corpus unchanged.** C162 is fixed; C163 is a process defect in my own tooling that the fix exposed.

## 1. C162 root cause, in one sentence

`prescan_stmt` decides how much DECIMAL pool to demand by looking at the **type of the assignment
target**, not at the decimal content of the expression, so `b = d + 2` (BIN target, DEC-typed rhs)
fell through to `prescan_expr` — which has no `Enumber` arm — and the operand literal's cell was
never sized while lowering allocated it.

The three existing branches are: Vdec target (bare literal → target-precision cell; complex →
`pdec_operand_bytes`), Vflt target (`pdec_fl_expr`), everything else (`prescan_expr`).  That third
bucket is where a decimal expression under a binary target lives, and it had no decimal handling at
all.  The fix adds exactly the call the Vdec branch already makes, for complex DEC-typed
expressions only:

```
| target not Vdec/Vflt, rhs unwrapped is not a bare Enumber/Eident
  -> if pdec_is_dec cx rhs then pdec_operand_bytes cx rhs else 0
```

Excluding bare literals/identifiers is not caution-for-its-own-sake: under a BIN target those
allocate nothing at lowering (`LXI H,immediate`, direct `LHLD`), and `prescan_expr` already owns the
literal cells for `**` and const-minus-const via its own arms — including them would double-count.

## 2. Why it is a rule and not a +2

Eight controls (e22src/W1..W8 → panel keys C162W1..C162W8) each byte-identical to DR, each linking
and running to the same value in both compilers, matching hand-computed expectations:

| probe | statements | pool cells DR | mine | runtime |
|---|---|---|---|---|
| W1 | `d=3; b=5;` | 1 (2B) | matches | 5 |
| W2 | `b=5; d=3; b=d+2;` | 2 (4B) | matches | 5 |
| W3 | `d=3; b=d+2;` | 2 (4B) | matches | 5 |
| W4 | `d=3; e=4; b=d+e;` | 0 cells, both operands direct | matches | 7 |
| W5 | `d=3; b=d*2;` | 2B + **1B** (mul uses the literal's OWN digit count) | matches | 6 |
| W6 | `d=3; b=2+d;` | 2B + 2B (commuted) | matches | 5 |
| W7 | `d=3; d=4; b=5;` | 2 cells (distinct content) | matches | 5 |
| W8 | `d=3; b=d;` | 1 cell (direct DEC→INT, CB6 route) | matches | 3 |

W5 is the discriminating one: its two cells are 2 and 1 bytes, because `*` sizes a literal from its
own digit count while `+`/`-` align it to the DEC partner (R608).  A flat "+2 per mixed statement"
would have made W5 exact by accident only if it had been 4, and it is 3.  The rule is
`pdec_operand_bytes`, which already encodes the alignment difference.

## 3. C163 — the substitution I nearly shipped

I named the new controls W1..W8.  `W1`..`W6` are already accepted E2E-15 stack specimens from
e15src.  Plain dict assignment replaced five of them; the panel total read 536 instead of 541.  Had
I not stopped to ask why 541 − 9 + 1 ≠ 536, the gate would have run green on a panel missing five
verified behaviours, and because I ran `--update-inventory` before reading its diff, the committed
inventory would have ratified it.

Two failure layers, both now closed mechanically:
* `SPECIMENS`/`REJECTS` are `NoOverwriteDict`: any re-registration raises at import time, whether it
  arrives via a literal, a loop assignment or `.update()`.  Retiring a specimen still works —
  `pop()` it deliberately first.
* Loop-driven registrations go through `add_spec()`, which routes into that guard.
* And the human rule: **read `git diff spec/INVENTORY.txt` before accepting a rewrite.**  A removal
  is fine only if you can name it.  Here the intended diff is exactly one removed row (CB9's
  refusal) and nine added rows.

`registration_audit()` could not catch this because it scans source TEXT for duplicate literal keys;
it has no way to see a later assignment to an existing name.  Runtime enforcement is the only shape
that works.

## 4. Arrays: what is known, what is planned, why it did not land

Established (C159) and confirmed again here against DR's own listings.  Landing scope for the next
milestone is *constant-subscript 1-D FIXED BINARY(15)*.

Already free: **the parser handles dimensions** — `ddims : dim list` with
`Dim_bound (lo_expr, Some hi_expr)` for `a(1:5)` and `Dim_bound (hi, None)` for `a(5)` (lower bound
defaults to 1).  AB1/AB3 prove the front end parses arrays today; only binding and lowering are
missing.

### 4.1 The blocker is a signature, not a rule

`bind.layout` returns `(auto_bytes, syms, statics, rows)` — a 4-tuple destructured at bind.ml:648,
bind.ml:847 and in the `proc_layout` builder.  `pl_rows : (string * rt * int) list` is read at
**7 sites in codegen.ml**.  Array metadata (lower bound, upper bound, element size) has to reach
codegen, and there are only two ways: widen the row tuple (touches 7 consumers, and every one of
them is on the 541-specimen path) or add a parallel field to `proc_layout` fed by a new component of
`layout`'s return (touches the tuple destructuring + one record constructor).  I chose the second,
implemented it, and hit the point where the change was spreading through `layout`'s callers with not
enough context left to verify 541 specimens afterwards.  Reverted rather than landed partially.
A partially-right array feature's failure mode is exactly C162: mis-sized data area, variables on
top of live storage.

### 4.2 Sizing rule (validated against DR by AB1)

`sz = bytes_of rt * (ub - lb + 1)`, and the automatic offset advances by that whole amount, so
following variables shift (AB1: `a(5)` occupies 0000–0009, `b` lands at 000A).  Refuse loudly, do
not size: multi-dim, assumed-size dims, non-constant bounds, and any element type whose
`bytes_of <> 2` (char/float/dec arrays are unmeasured).  Static arrays land below the pool like
every other static (AB5), but AB5 also carries the pre-existing STATIC-on-fixed-bin refusal, so
STATIC arrays stay refused and separately measured.

### 4.3 Lowering, three shapes, DR's exact bytes

Let `base` be the array's data address and `off = (sub - lb) * elem`.

* **Read** — `d op_lhld (0x2A); reloc Data (base + off)`.  DR prints this as `LHLD A A(0000)+0004`;
  in .REL it is a plain 2-byte data reloc at the target address, exactly like a scalar reference, so
  my existing `reloc` primitive emits it unchanged — no new record shape.
* **Store, off = 0** — the ordinary scalar store: lower the value into HL, then
  `d op_shld (0x22); reloc Data base`.  AB1 confirms DR uses the scalar form at offset 0.
* **Store, off > 0** — byte stores at a computed address:
  `d op_lxi_h (0x21); reloc Data (base + off); d op_mvi_m (0x36); d lo; d op_inx_h (0x23);
  d op_mvi_m; d hi` (little-endian).  AB3: `a(3) = 5` → `LXI H,A+0004 / MVI M,05 / INX H / MVI M,00`.
  **Only the literal-value form is pinned.**  The form for a computed value (variable/expression
  stored into a non-zero-offset element) is not yet extracted from a DR listing — it must be read
  out of AB9/AB12/AB14/AB16's goldens or newly probed before implementing; refuse it until then.

### 4.4 Disambiguation — the architectural requirement

`a(i)` parses as `Esuffix(Eident a, [i])`, which is exactly what a procedure call parses as.  The
decision MUST come from the bound declaration: if `a` is in the array table → array element; if `a`
is a bound procedure → call; if neither → today's "call to undeclared procedure" refusal.  No
textual heuristic, and specifically: do NOT let a name that is a procedure become an array element
by proximity, and do not let the new array arm shadow the call path for names bind does not know.
Scalar use of an array NAME (`b = a;`, `a = 3;`) must refuse as a general array-valued expression.

### 4.5 Refusals to keep while Step 2 is narrow

Runtime-variable subscripts (the `LXI H,A+(lb-1)*size / PUSH H / LHLD i / DAD H / POP D / DAD D`
ladder + the pre-biased reloc — Step 4), multidimensional indexing, element-as-actual
(descriptor holds the element ADDRESS), char/float/dec element types, whole-array expressions,
STATIC arrays, and non-literal stores at non-zero offset until that sequence is measured.

### 4.6 Validation plan (already set up, reusable)

AB1–AB17 goldens exist [golden/e2e216–e2e218].  For Step 3, build witnesses for first/middle/last
element, several distinct values, scalars declared before AND after the array, a non-1 lower bound
(AB3/AB4 `a(0:3)`, AB9 `a(1:5)`), and offset-zero vs non-zero stores; compare DR acceptance →
instruction selection → raw .REL → linked execution against hand-computed values, keeping every
runtime witness in bounds (DR emits no bounds check — that is a fact about DR, not permission).
Retire an AB refusal only when its own registered golden turns byte-exact.

## 7. Totals

Gate 532 → **541 byte-exact / 0 fail**, negative panel **109/109** (CB9 promoted refusal→specimen;
8 C162 controls added), inventory 541 rows in sync with exactly one intentional removal, corpus
13/41 EXACT / 0 DIFFERS unchanged.  `bind.ml`, `reloc`, `link`, `ocaml/proto/` untouched.
