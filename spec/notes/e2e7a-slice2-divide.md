# E2E-7A slice 2 — FIXED DECIMAL divide + the scale-shift law

## 0. Count reconciliation (nothing hidden)

| bucket | count | names |
|---|---|---|
| probes generated + DR-compiled (`$L$D$C$S`, `golden/e2e8/`) | **25** | R701-R725 |
| registered BYTE-EXACT positive specimens | **23** | R701-R708, R710-R724 |
| excluded from the positive panel (refused; kept as refusal evidence) | **2** | R709, R725 — both FIXED DECIMAL **formal parameter** (§5) |
| promoted to positive by this slice | **+1** | R512 (`c = a / 2`: old E2E-6 divide-refusal evidence — negative N26_DECDIV retired because its shape is now PROVEN) |
| new negative-panel members | **5** | N31, N32, N33, N34, N35 (inline sources, each with a marker specific enough to catch a change of refusal reason) |
| gate totals | **135 / 135** positive, **30 / 30** negative | was 111 / 26 at `3636eec` |

Law evidence also reuses already-banked traces: R505, R509, R511, R512,
R608, R609, DFACT, and LOAN1 (`$C` + `$S`). Every acceptance arm was run:
`.REL` byte-identity for all 23; linked `.COM` byte-identity against DR's;
RAW console byte-equality against DR's (all 23 terminate with `stop;`, so
each transcript is COMPLETE — no bounded-prefix or timeout truncation).

## 1. The stack model (corrected and unified)

A decimal-stack entry carries **(p = digits, s = scale)**, value `m / 10**s`:

| route | effect |
|---|---|
| `?DLDOP` (A = digits) | push a cell whose address is in HL |
| `?DSTOP` (A = digits) | pop into the cell at HL |
| `?QDDSL` (A = n) | **top**: `m *= 10**n`, `s += n` — value preserved |
| `?QDDSR` (A = n) | **top**: `m //= 10**n`, `s -= n` — value preserved, **TRUNCATES** |
| `?DADOP ?DSUOP ?DMUOP ?DDVOP ?DCMOP` | pop two (or compare two), push one / leave flags |

The two things that make the traces readable are:

* **`?QDDSL` / `?QDDSR` act on whatever is the TOP at that moment**, so
  their *position* in the sequence identifies which value is being
  shifted: between the two operand pushes = the first-pushed operand,
  after both pushes = the second-pushed one.
* The scale a value ends up at is decided by its **consumer**, not by the
  operation that produced it.

## 2. Law table (every row is directly observed, never extrapolated)

| # | law | evidence (specimens) |
|---|---|---|
| L1 | `+`/`-` align the **shorter** operand UP to `max(s_l, s_r)`; equal scales emit nothing; both directions proven for `-` | R705 (s 2←4, shift between pushes), R707 (s 4→2, shift after both pushes), R715 (both directions of `-`), R505 / LOAN1 `p = p - pmt` (equal), R608 (literal pre-aligned ⇒ no shift) |
| L2 | `*` performs **no** alignment; result scale = `s_l + s_r` | R711 `d = a*b` into dec(9,4) emits **no shift at all**; R719/R720 (product scale 4 into a dec(9,2) target ⇒ one `?QDDSR 2`) |
| L3 | `/` pre-shifts the **dividend** by `N = 15 - p_dividend`, and omits the whole pair when `N = 0` | R512/R701/R703/R708/R712/R713/R714/R717/R718 (p=9 ⇒ N=6), R710 (p=11 ⇒ N=4, so N is **not** a constant), R702 (dividend dec(9,2) against a dec(13,2) **target** still gets N=6 ⇒ N tracks the dividend), LOAN1 + R704 (dividend = 15-digit product ⇒ N=0 ⇒ no pair) |
| L4 | quotient scale = `s_l + N - s_r` when `N > 0`, else `s_l - s_r`; the quotient's **precision is unpinned** (no sample exposes it) | derived + 13 samples; refusal `N32_DIV_CHAINED` guards the unpinned consumption |
| L5 | the **consumer fixes the scale**: a store/return shifts DOWN with `?QDDSR` or UP with `?QDDSL`; an enclosing `+`/`-` aligns instead and adds no fix | R701 (down 4), R713 (down 2), R716 (**up** 2, into dec(13,8)), R711 add (**up** 2), R505 mul (down 2), R721/R722 (quotient carries scale 6 into the add, no fix) |
| L6 | result precision, observable **only** through the next division's `N`: `+`/`-` ⇒ `min(15, min(p_l,p_r)+1)`; `*` ⇒ `min(15, p_l+p_r+1)` | R714 (9,9 ⇒ 10 ⇒ N=5), R717 (9,6 ⇒ 7 ⇒ N=8), R718 sub (5,5 ⇒ 6 ⇒ N=9), R718 mul (5,5 ⇒ 11 ⇒ N=4), LOAN1/R704 (4+11+1 ⇒ 16 ⇒ cap 15 ⇒ N=0) |
| L7 | push order: the **right** operand goes first iff it is compound and the left is simple; otherwise left first (both-compound and both-simple included). `/` **always** pushes the dividend first, because its `N` pre-shift must act on the top | R719, R722, R704, DFACT vs R720, R724, R505, R705, R707; R712 forces the `/` exception |
| L8 | integer literals: store/return role ⇒ target `(p,s)`; additive/compare role ⇒ DEC **partner's** `(p,s)`; multiplicative role ⇒ **own digit count, scale 0** | C084 (store), R608/R507 (additive, compare), R509 `*2` A=01, R511 `*1234` A=04, R512/R703/R710 `/2`, `/8` A=01, LOAN1 `/1200` A=04 (3-byte cell) |
| L9 | division **truncates** (no rounding) | R706: `2/3` into dec(9,2) ⇒ **0.66** (half-up would be 0.67); `9/2` into dec(9,0) ⇒ **4**; `2/8` ⇒ 0.25; `2/3` into dec(11,4) ⇒ 0.6666 |

`+`/`-` alignment, consumer fix, and the divide pair are the same
mechanism seen from three angles: the stack entry's scale is adjusted to
what its consumer needs, using `?QDDSL` upward and `?QDDSR` downward.

## 3. Corrections to banked claims

* **C084: "ADD/SUB never carry a rescale" — incomplete.** It holds for
  equal-scale operands (R505, LOAN1 `p = p - pmt`), but unequal scales do
  get a pair (R705, R707, R715). The rule is L1+L5, not "no rescale".
* **C084: "the rescale after a multiply is `MVI A,target_scale`" — wrong
  shape, right answer by coincidence.** The emitted amount is
  `result_scale - target_scale` = `(s_l + s_r) - s_t`; R505 happened to
  have `s_l = s_r = s_t = 2` so the two formulas agreed. R711 (product
  scale 4 into dec(9,4)) emits **nothing**, which the old rule would have
  got wrong.
* **C084: DEC pool cells are not deduplicated** — corrected in slice 1
  (R614); no further change here.
* **Literal precision** was split correctly in slice 1 (additive aligns,
  multiplicative doesn't) and is now confirmed from both sides by L8.
* **C085's HL-constant reuse (D6) is a STRAIGHT-LINE peephole.** R723
  proves it: `if a > e then m = 1; else m = 0;` reloads `LXI H,0000` in
  the else branch instead of reusing HL through the `[G116] MOV L,H`
  trick. My unqualified rule fired across the branch boundary and was 2
  bytes short. The tracking state now dies with every jump emitted.

## 4. New fail-loud perimeter (each is a tested negative)

| negative | shape | why it is genuinely unpinned |
|---|---|---|
| `N31_DIV_LITERAL_NUMERATOR` | `c = 1200 / a` | every divide sample has a variable/call/computed dividend; a literal dividend's `(p,s)` (and hence `N`) is unobserved |
| `N32_DIV_CHAINED` | `c = a / b / 2` | L4: a quotient's **precision** is never exposed by any trace, so it cannot be used where `N = 15 - p` needs it |
| `N34_DEC_NEGSCALE_DIV` | `a dec(9,0) / b dec(9,8)` | quotient scale `< 0`. R712 proves `s_r > s_l` is fine while the result stays ≥ 0, so the refused region is exactly the negative one |
| `N35_DEC_STORE_SCALE_DRIFT` | `c dec(9,4) = a dec(9,2)` | a **direct** operand whose own scale differs from the store target: every pinned fix was on a *computed* value; LOAN1's `PMT = P` crosses precisions but not scales (covered by `?DSTOP`'s A) |
| `N33_DEC_FORMAL` | `procedure(x)` with `dcl x fixed dec(...)` | see §5 |
| (existing) | divide-with-scaled-literal, fractional additive literal, `decimal(x,p)` inside a relation | unchanged from C084/C085 |

## 5. DEFECT FOUND AND CLOSED (fail-silent → fail-loud)

R709/R725 (DEC function call as a divide operand) uncovered a **silent**
wrong-code path that predated this slice: DR passes a FIXED DECIMAL
**formal parameter by reference**. The formal gets a **2-byte** cell (not
`ceil((p+1)/2)`) holding the caller's address:

```
prologue:  MOV E,M / INX H / MOV D,M / XCHG / SHLD J     copy the pointer
read:      LHLD J ; MVI A,09 ; CALL ?DLDOP               HL = ADDRESS
```

My build gave the formal a full 5-byte BCD cell (mis-sizing AUTO storage)
and referenced it with `LXI H,J` — 1 byte of divergence plus a wrong
address semantic, and **it compiled without complaint**. That is a
fail-silent defect by the audit §9 standard. It now refuses:
`codegen: FIXED DECIMAL formal parameter j is unproven [TBD]`. The refusal
is banked in the negative panel as `N33_DEC_FORMAL`, which uses an INLINE
source of the same shape (the panel's convention); R709 and R725 are the
independent DR-compiled evidence for it and deliberately stay OUT of the
positive panel — my build emits no `.REL` for them at all. The
DEC-call-with-DEC-formal sub-model is its own slice; note that **DFACT,
R509 and R510 are unaffected** because
their formals are `FIXED BINARY` (`dcl i fixed`), which is the by-value
2-byte copy already proven byte-exact.

## 6. Gate state after slice 2

* e2e byte-parity **135 / 135** (was 111 at `3636eec`: +23 divide
  specimens, +1 promoted R512). R709/R725 are not registered (DEC formal ⇒
  refused); their DR goldens stay in `golden/e2e8` as the §5 evidence.
* negative panel **30 / 30** refused loudly (N26_DECDIV retired because
  `c = a / 2` is now proven; N31-N35 + N33 added).
* parse 437 ok / 6 parity-rejects / 0 FAIL of 443 · bind 47/47 ·
  rel round-trip 409/409 · ir 0 FAIL · safety 28/28.
* corpus sweep: 3 byte-exact / 0 divergent / 39 explicit-[TBD] refusals, plus
  2 loud-but-untagged failures (CALL parser "expected statement", LABELS
  "undeclared x"). Both re-tested against a clean build of `3636eec` and
  identical there, so they are pre-existing wording debt, not slice-2
  damage — and "0 crashes" is NOT claimed. The DEC rewrite did not move the
  corpus: still exactly DEMO / RFACT / DFACT byte-exact.
* `tools/decmodel.py` (new): the independent simulator — 49/49 schedule
  MATCH over every DEC probe it can parse, 0 DIFFER, and 4 named model-side
  parse refusals (R506 `decimal(i,15)`, R509 `f(3)`, R709/R725 DEC call with
  a DEC formal). Those 4 are limits of the MODEL, not of the compiler:
  R506/R509 are byte-exact positive specimens, R709/R725 refuse by design.

## 7. Verification actually performed (three independent directions)

1. **Byte parity**: 23 registered specimens (R701-R724 minus R709, which is
   refused for §5's reason) compile to `.REL` byte-identical to DR.
   Gate total 135/135 (23 new + R512 promoted; see §0).
2. **Link + run parity**: every one of those 23 was linked with DR's LINK-80
   + PLILIB.IRL and the linked `.COM` was **byte-identical** to the `.COM`
   built from DR's own golden `.REL`; and the RAW console region of the
   executed program was **byte-equal** to DR's. All 23 terminate with
   `stop;`, so every transcript is COMPLETE -- no bounded prefix, no timeout
   truncation was used anywhere in this slice. Examples of the compared
   bytes: `\r\n     -1.0000        -1.00\r` (R715),
   `\r\n      2.33333300\r` (R716), `\r\n        0.66         0.25
   0.33         0.6666\r` (R706).
3. **Independent numeric model** (`tools/decmodel.py`): a from-scratch
   Python simulator of the (p,s,m) stack that emits BOTH the predicted token
   schedule (compared against DR's own `$C` listing) and the predicted
   printed field (compared against DR's console bytes, with the PUT LIST
   separator of one blank between items). Result over the whole DEC corpus:
   **49 SCHED MATCH / 0 DIFFER / 4 model-side parse refusals** (R506, R509,
   R709, R725 — all DEC *call* forms), and **22 VALUE-MATCH / 0 VALUE-DIFF**
   on the specimens that print only decimals. The model does not read
   compiler output, so it cannot be satisfied by the same bug twice — but
   note it is weaker than the byte gate, not above it: where the two
   disagreed (R507, before I taught the model about puts sitting in IF
   arms) the *model* was the one that got fixed, because DR and my `.REL`
   already agreed byte-for-byte.

## 8. Two things the model check surfaced that byte-comparison alone missed

* **A quotient is computed at 15 working digits and then PADDED, not
  recomputed.** R716 (`c dec(13,8) = a dec(9,2) / b dec(9,2)`) prints
  **2.33333300**, not 2.33333333: DR divides at scale 6 (s_l + N - s_r =
  2+6-2) and the consumer fix shifts LEFT by 2 to reach the target scale 8,
  appending zeros. So a decimal divide never gives you more than 15 digits
  of accuracy regardless of the target scale. My compiler reproduces this
  exactly (byte-identical `.COM`, byte-equal console) because it models the
  shift rather than the arithmetic -- but the *semantics* only became
  visible once the Python model predicted a printed field and DR disagreed
  with naive "divide at target precision" intuition.
* **Truncation is confirmed in both directions of the shift** (L9), and the
  PUT LIST inter-item blank separator is re-confirmed for DECIMAL fields
  (R706 four items, R711/R715/R718/R724 two items) -- previously banked only
  for binary/character items.

## 9. Explicitly NOT claimed

* `round()` / `?DROUN`: untouched by this slice (deferred to slice 3), and
  its HALF-UP-vs-HALF-EVEN tie mode remains untested -- division never
  rounds, so it gives no evidence either way.
* Truncation DIRECTION for a NEGATIVE quotient (toward zero vs toward minus
  infinity): no specimen produces one. My model implements toward-zero, but
  the accepted behaviour here is DR's own PLILIB at runtime -- my `.COM` is
  byte-identical, so whatever DR's `?DDVOP`/`?QDDSR` do with signs is what
  my programs get; this is a documentation gap, not a code risk.
* Quotient PRECISION (`p` after `?DDVOP`) is unpinned; refused where needed
  [N32].
* Any of L1-L9 outside the operand shapes sampled: `*`/`/` with a scaled
  literal, DEC arrays, DEC in GET, decimal(x,p) inside a relation, compare
  needing the DEEPER operand shifted (refused in code, see
  `lower_test_skip`'s DEC arm), and DEC(>15) (DR's own NOT IMP at p=31).

* Cell size: `ceil((p+1)/2)` is DIRECTLY observed at p = 1,3,4,5,6,7,9,11,15
  (nine values). It is NOT verified at p = 2, 8, 10, 12, 13, 14 — those are
  law-predicted. This slice re-tests no cell size at all: its operands sit
  at p = 4, 5, 9, 11, 13, and p=13 appears only as a consumer-side target,
  so p=13's cell size still rests on the law rather than a fresh sample.

## 10. Old-DEC regression re-verification after the rewrite (why it matters)

The divide slice *replaced* `dec_push` rather than adding to it, and it also
made the comparison path align operands (L1/L5) and kill HL-constant
tracking at every jump. Both changes reach code that slice 1 had already
banked, so the whole previously-verified DEC set was re-run through the link
arm, not just re-compiled: **R501, R502, R503, R505-R515 and R601-R614 —
28 specimens — each came back with `.COM` byte-IDENTICAL to DR's and RAW
console byte-EQUAL** (2 arms × 28 = 56 verdicts, 0 failures, 0 omissions).
DFACT is the 29th member but is verified by the bounded-prefix protocol
instead of a whole-transcript compare, because its main tail never exits;
after the rewrite it still gives `.REL` parity, `.COM` identity (8192 B) and
**first 12 COMPLETE records byte-equal**, plus **16 factorial records that
match `math.factorial` independently** of DR.
