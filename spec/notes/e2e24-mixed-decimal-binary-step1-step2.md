# E2E-24 step 1 / step 1b / step 2 — DR's out-of-range FIXED literal, and the decimal route at the store

Baseline HEAD: `d528144`. Gate at start: 607 byte-exact / 101 negatives / 3 divergences.
Gate at end:   **633 byte-exact / 107 negatives / 22 divergences / exit 0.**

Scope actually reached: Priority 1 (characterise DR), Priority 1b (cell layout), Priority 2 at the
**store** AND at **both ADD operand orientations** (including self-add).  Priorities 3, 5 and 6 are
NOT done: SUB, array-element stores, PUT items, call arguments and conditions stay unrouted and are
pinned as wrong-value rows rather than guessed at.

---

## 1. What DR does with a FIXED literal that does not fit bin(15) — Priority 1

Probe families: **ML1–ML15** (`golden/e2e244`, `e2e245`) — value/threshold sweep;
**MN1–MN8** (`e2e245`) — negative and mixed-sign forms.

The rule is **value-based, not text-based** (`fixed bin(31)` is `NOT IMP` in DR's own listing, so
there is no wider immediate form to fall back to):

| probe | literal | DR's route |
|---|---|---|
| ML9 | 32767 | `LXI H,<imm>` — immediate |
| ML10 | 32768 | `LXI H,<cell> / MVI A,p / CALL ?DLDOP / CALL ?QDI15` |
| ML1 | 1234567890 | decimal cell, p=10, 6 bytes |
| ML2 | 0123456789 | decimal cell — same *structure* as ML1, different cell bytes |

**The boundary is 32767 / 32768 exactly.** Leading zeros are insignificant to the value and
decisive for the cell (§2).

### The part that changes what "correct" means

At run time DR does **not** quietly keep a truncated value. Every overflow case aborts:

```
ERROR (1), Conversion
Traceback: 0612 0144 3620 3535 3533
```

So HEAD was not merely byte-divergent on these programs, it was **silently wrong**: ML1-class code
printed `723` where DR raises a conversion error. Reproducing the *bytes* of the decimal route is
therefore not a cosmetic exercise — it is what makes the program fail the same way DR fails.
See §5 for the executed evidence.

---

## 2. Cell layout and dedup — Priority 1b

Probes: **LP1–LP16** (`golden/e2e246`), **LQ1–LQ9, LQA** (`golden/e2e247`).

* Size: `dec_pool_bytes p = ceil((p+1)/2)` — p digits plus one sign nibble.
* Nibble order: **least-significant digit first**; the **final nibble is the sign** (0 = positive,
  9 = negative). Negatives are stored as ten's complement in p digits.
  Verified against LP1's cell for 32768: `68 27 03` = nibbles 8,6,7,2,3,sign0 ✓.
* **p is the digit count of the literal TEXT, leading zeros included**: `0000032768` is p=10 and
  takes a 6-byte cell; `32768` is p=5 and takes 3 (LP15 vs LP2, same value).
* **Dedup is on the byte IMAGE, not on (precision, value):**
  * LP1 `y = 32768; y2 = 32768` → **one** cell.
  * LQ6 `032768` (p=6) then `0032768` (p=7) → different precisions, **identical 4-byte image** →
    **one** cell. A `(p, value)` key would have made two.
  * LQA → a `fixed dec(5)` store and an integer store of the same literal **share one** cell, so
    the dedup table crosses declaration kinds.
* The route is **context-free** in DR: it appears identically in assignments, ADD/SUB operands
  (with C150's XCHG / PUSH-H-POP-D parking: LP4 puts the literal on the left and parks with XCHG;
  LP5/LP9 put it on the right and park with `PUSH H` … `POP D`), conditions, call arguments
  (LP16), array-element stores (LP12) and multiply (LP13, reproducing MB31's documented form).

---

## 3. Implementation (store position only)

One route, decided in one place, in `ocaml/lib/codegen.ml`:

* `bin15_fits v` = `-32768 <= v <= 32767` — the threshold of §1.
* `lit_dec_p text` — digit count of the text (§2).
* `lit_dec_to_hl st text v` — allocate/dedup the cell through `st.dec_cells` keyed on the byte
  image, then emit `LXI H,*cell / MVI A,p / ?DLDOP / ?QDI15`, and set `st.last_imm <- None`.
* `int_lit_to_hl st text` — the dispatcher: in range → `hl_const` (C177's ladder, untouched);
  out of range → `lit_dec_to_hl`.
* `bcd_pack_scaled` was **moved above every user** so prescan demand and lowering layout call the
  *same* encoder. Demand and layout must not be two rules that happen to agree today [C155/C162].
* `pdec_dec_cell`'s prescan dedup key changed from `(p, sc, scaled-magnitude)` to the encoder's
  byte image — the same key the lowering's `st.dec_cells` already uses. This is what makes
  **LQA** work, and it also removes a latent mismatch: prescan was counting cells the image-keyed
  layout was going to merge.
* `pdec_int_lit_cell` makes the demand for an out-of-range literal **at the store**, inside HEAD's
  own C162 arm (`dec_rhs_in_int_target`), which previously said "a bare literal under an integer
  target allocates nothing at lowering". That sentence was true of HEAD and false of this build, so
  the demand belongs exactly there.

**Deliberately NOT routed:** ADD/SUB constants, PUT items, call arguments, array-element stores,
and anything reaching `lower_hl`'s `Enumber` arm. Each is a DIVERGENT row with its measured bytes.

`st.last_imm <- None` after `?QDI15` is measured, not cautious: LP1 stores 32768 twice and DR
re-emits the whole route for the second store instead of reusing HL, so C177's constant-reuse facts
do **not** survive a conversion.

---

## 4. Four mistakes made during this step (all fixed before commit)

1. **Two copies of one demand arm.** A patch script was run twice; each run inserted a
   `prescan_expr` `Enumber` arm. `prescan_expr` *recurses into operands*, so `y = x + 32768`
   demanded a cell twice while its lowering (the C150 constant-operand path, which allocates
   nothing) produced none: prescan 6 bytes vs layout 0, and ML1/ML2/ML5/ML8/LQ5 — programs that had
   *built* at HEAD — started failing the pool invariant. Two identical arms and a doubled demand
   were only found by reading the diff, not by reasoning about it.
2. **Demand placed in the wrong walker.** Even one copy over-counted, for the same reason. The
   demand has to be made at the AST position whose *lowering* allocates — the store — and HEAD
   already had exactly that position written out (`dec_rhs_in_int_target`) saying it allocated
   nothing.
3. **A "threshold sweep" that measured nothing.** A script built variants with
   `str.replace("  y = x + 1234567890;\r\n  put skip list(y);\r\n", …)` after opening the file in
   **text mode** (newlines translated), so the pattern never matched and every generated file was a
   copy of ML1. All nine "thresholds" reported the same numbers — which should have been the tell.
   Rewritten with `newline=''` and explicit CRLF, the sweep became meaningful: `y = 32768` and
   `y = 1234567890` are fine as stores; `y = x + 32768` is the broken shape.
4. **A test loop that reused a shell variable**, which silently compiled the previous probe's source
   against the current probe's golden and reported "12 regressions" that did not exist. The gate's
   own 607/607 was the contradiction that sent me back to the loop.

Also worth recording: **LP12's element store was byte-exact at one point and was then reverted.**
Routing it needs the prescan to know an array's *element* kind, and `pdec_ctx` carries scalar kinds
only — so the demand could not be made, and the program went from building to failing the pool
invariant. Restoring HEAD's behaviour for that position (it builds, prints a truncated value, and is
pinned in DIVERGENT.txt) beat keeping one more exact probe. **A change that makes previously-building
programs fail an internal consistency check is not an acceptable trade** [C179].

---

## 5. Evidence

**Byte-exact (37 promoted specimens):** LP1 LP2 LP4 LP5 LP6 LP14 LP15, LQ1 LQ3 LQ6 LQ7 LQ8 LQ9 LQA,
ML1–ML5 ML9–ML15, MN1–MN8, and **ZK8 ZK10 ZK11** — the three programs E2E-23 pinned as divergences.
They were never waiting on a register optimiser; they were waiting on this literal route. Their
divergence rows are deleted and they are specimens now.

**Regression check, not assumed:** the whole 45-probe set was compiled with the HEAD binary and with
this build. The build/refuse/crash classification is **identical for every probe** — the only
differences are bytes. Refusals that remain (LP3, LP7, LP10, LP13, ML6, ML7) are all pre-designed
`[TBD]` guards, none is a pool-invariant failure; each carries NEG_META evidence naming DR's own
golden.

**Executed (8 witnesses, mine's `.COM` vs DR's `.COM`, LINK 1.31, cpmsim):**

| program | output (both sides, byte-identical) |
|---|---|
| ML3 | `ERROR (1), Conversion` + `Traceback: 2066 0002 0612 1176 3635 3837 3039` |
| ML4 | `ERROR (1), Conversion` + identical traceback |
| **ML1** (`y = x + 1234567890`, the case that motivated the step) | `ERROR (1), Conversion` + `Traceback: 2070 0002 0612 1182 3635 3837 3039 0001` — **at HEAD this program printed `723`** |
| LP5, LP14 | `ERROR (1), Conversion` + identical traceback each |
| ML15 | `      124` |
| ZK8, ZK10, ZK11, LP15, LQA | `ERROR (1), Conversion` + identical traceback each |

11 executed witnesses in total.  Staged `.REL`s were `cmp`'d against DR's goldens before linking.

The staged `.REL` used for linking was re-`cmp`'d against DR's golden first — runtime evidence has
to come from the same artifact the byte check used. ML3/ML4/ML15 etc. are in
`golden/e2e250m`, `e2e255m`; transcripts in `e2e251m…e2e266d`.

**Divergence panel:** 22 rows, shapes measured with the gate's own `_rel_stats`, causes split into
two families and each row quotes its own statement — (A) out-of-range literal in a non-store
position, which **prints a wrong value where DR aborts**, and (B) negative literals, where DR folds
`-32768` to `LXI H,FFFB` and mine calls a negate routine: a **pre-existing** gap that HEAD
classifies identically, not damage from this step.

---

## 6. Open items

1. **Operand positions** (ADD/SUB constants, PUT items, call arguments, element stores): the route
   is measured (LP4/LP5/LP9 give the parking), what is missing is a demand path that can see those
   positions *and* the C150 constant-operand lowering agreeing with it. This is the
   expected-context work, and it is where a wrong value still lives.
2. **Negative literals** (MNEG/MNEGV/LQ2/LQ4/ML13): DR folds, mine negates. Independent of this step.
3. **`pdec_dec_cell`'s image key is now load-bearing for LQA** — but the const-const DEC chain
   (`pool_alloc` with no dedup) and `pdec_dec_cell` (dedup) still disagree in principle about shared
   images; LP3/LP10-style shapes refuse for unrelated designed reasons, so this has not bitten.
4. **CB1–CB5, CB7** (mixed DEC/BIN ADD/SUB/MUL under explicit declarations) are still refused:
   Priority 3, untouched. CB9/CB6 stay byte-exact ✓.
5. **CONV.PL1 / DECY.PL1** integration: both still refuse (C161 non-decimal-operand guard) —
   Priority 6 depends on Priority 3.
