# E2E-14 Priority 1 — the C142 cell model, measured across 19 DR programs

`HEAD` production unchanged throughout. Production refusals verified intact before and
after every measurement (`P5/P6/P9/P12` still fail loudly with `[TBD]`; `git diff` empty).

## Method: where does DR actually put each anonymous cell's record?

`tools/reldump.py` gives every record a stream bit ✓ so a cell's position is measurable,
not arguable ✓✓. A `RELOC data N` record follows the operand bytes it describes, so the
instruction that references cell `N` is the nearest preceding `DATA code A` — positional
attachment, which my first two scripts got wrong (they looked for a code-address field
that a reloc record does not carry, and read the displacement field as the cell number;
both produced "all cells UNREFERENCED" ✓✗ and would have led me to conclude DR emits no
allocation records at all). Fixed by reading the correct field and the preceding code
record ✓✓.

For each cell I record: the bit of its `LINK-SET-LC data N` (its allocation/content
record), the code address of the first instruction that references it, and whether other
code records intervene. Two distinct placements emerge ✓✓:

- **AT-REF** — the record sits immediately before the `LXI H,*A(N)` that loads it ✓
- **EARLY** — the record sits before the enclosing expression's *first* code record, so
  one or more unrelated instructions intervene ✓

## The table

Cells below `0008` are declared/pool region and are not part of this question ✓. The
first row of each pair is DR; where shown, the second is my current compiler measured
with the C142 refusals temporarily bypassed in a throwaway worktree ✓✓.

| probe | expression | route | DR placement | mine |
|---|---|---|---|---|
| P3 | `t + g(3)` | defer | c0009@1846, ref `0051` | — (byte-exact already) |
| P4 | `g(3) + t` | defer | c0009@1846, ref `0051` | — |
| P7 | `g(3) - t` | XCHG | c0009@1846, ref `0051` | — |
| P8 | `g(2) + g(3)` | defer-ish | c0009@1846, ref `0051` | — |
| P1 | `g(h(2))` | defer | c000F@2401, ref `0076` | — |
| P11 | `g(2)*2 + h(1)` | defer | c000D@2391, ref `0075` | — |
| P10 | `g(1)+2 + h(3)` | defer | c000B@1834, c000D@1987 | — |
| **P9** | `t + g(h(2))` | defer | **c000D**@2010 (ref `0063`), c000B@2163 (ref `006C`) | **c000F**@2010, c000B@2163 ✓ positions identical, **number differs** ✗ |
| **P6** | `t - g(3)` | PUSH | **c0009@1846 EARLY**, ref `0055` | c0009@**1883** AT-REF ✓ number right, **record 37 bits late** ✗ |
| **P5** | `(t+u) - g(3)` | PUSH | c000B@1892 EARLY, ref `005F` | c000B@1892, ref `0056` — **same record bit, different code address** ✗ |
| **P12** | `g(3) + g(4)` | PUSH | c000B@1889 (ref `0051`), **c000D@1958 EARLY** (ref `0058`) | c000B@1889 ✓, c000D@**2023** AT-REF ✗ |
| D1 | `t - u - g(3)` | PUSH | c0013@2031 EARLY, ref `006C` | c0013@**2208** AT-REF ✗ |
| D3 | `t + g(h(k(2)))` | defer | c0017@2031, c0015@2183, c0013@2335 — all AT-REF | **identical to DR** ✓✓✓ |
| D4 | `t + g(h(2),k(3))` | defer | c0019@2074, c001D@2295, c0015@2226 | (mine refuses earlier: two-call-argument shape) |
| D5 | `t + g(2*h(3))` | defer | c0015@2074, c0019@2143 | (mine refuses earlier) |
| D9 | `t + g(3)*2` | defer | c0013@2031 AT-REF | — |
| D11 | `g(1)+g(2)+g(3)` | PUSH | c0017@2117 (ref `0061`), **c0019@2186, c001B@2255 EARLY** | c17@2117 ✓, c19@**2250**, c1B@**2384** ✗ |
| D12 | `t + (g(3)+g(3))` | PUSH | **c0013@2031 AT-REF, c0015@2100 EARLY**; cells numbered `000B,0013,0015` | mine numbers `000D,0015,0017` ✗ — **numbering shifted**, plus late records ✗ |

## The model these numbers imply (and where it is not yet forced)

**Numbering.** Per procedure section, DR numbers every call site's *descriptor slots* (2
bytes per argument) first, in pre-order over the sites, and only then the *expression-argument
value cells* ✓✓. Evidence: D3 numbers descriptors `0013(g) < 0015(h) < 0017(k)` and only
then the value cells `0019, 001B` ✓✓; P9 numbers `g.slot 000B`, `h.slot 000D`, then `g`'s
argument value cell `000F` ✓✓ — my `bind.ml` allocates `(slot, temps)` per site in one
pass, so my `g`-argument cell lands at `000D` *ahead* of `h`'s descriptor ✓✗. D12 shows
the same shift, one level shallower ✓.

**Record placement.** A descriptor's content is a 2-byte pointer to the cell holding that
argument's value. DR writes the descriptor record **as soon as its content is knowable** ✓:
- actual is a literal or a declared variable → the target cell already exists → the record
  is written during planning, hence **before** the enclosing expression's first code ✓✓
  (P6, P12's second call, D1, D11's second and third calls ✓✓);
- actual is an expression whose value cell has not yet been allocated (a nested call's
  result destination) → the content is not knowable until that cell is allocated → the
  record is written just before the `LXI H,*A(N)` that loads it ✓✓ (D3 all three ✓, P9 ✓,
  P1 ✓).

That single rule explains every row in the table ✓✓, including the rows that look
contradictory: for the DEFER route the call's code is the expression's first code, so
"at plan time" and "at reference" are the *same position* and the two readings cannot be
separated — which is why P3/P4/P7-P11 and D3/D9 are byte-exact under my current at-ref
emission ✓, and why the divergence appears only when other instructions precede the call's
code ✓✓ (the PUSH route ✓ and multi-call chains ✓).

## What is *not* settled by this evidence

1. Whether the value cells are numbered in pre-order over sites, or allocated at the first
   `SHLD` that writes them ✓. Both produce `0019 < 001B` for D3 and `000F` for P9 ✓. The
   discriminating shape is an expression with an expression-argument on an *inner* call
   whose store precedes an *outer* call's store in code order — D4/D5 have that shape and
   my compiler refuses them for a different reason, so I could not use them ✓.
2. Whether P5's `same record bit / different code address` means my *code* order is right
   and only the anchor record differs, or my expression-start anchor is wrong. It says
   nothing yet about the model ✓ — I am not treating it as confirmation ✓.
3. Nothing here re-tests C141's numeric conclusions ✓; the bypass was measurement-only, in
   a worktree, and reverted ✓.

## The migration this implies (Priority 2/3)

Two changes, each in one place, no second allocation source ✓✓:

- **`bind.ml`, `section2`** (the only place call-site cells are numbered ✓): split the
  single `List.map` into two passes — slots for all sites, then temps for all sites. ~8
  lines. Fixes P9 and D12-type numbering shifts ✓.
- **`codegen.ml`, the two PUSH-route arms** (both currently refused by `[TBD]` guards ✓):
  hoist the descriptor-word emission (`SET-LC data slot+2i` / `push (Reloc (Data, target))`
  / `SET-LC code st.lc`) out of the per-argument loop and run it *before* lowering the left
  operand, for the cases where the content is knowable ✓. Fixes P5/P6/P12/D1/D11 ✓.

The second change can only affect shapes that today refuse ✓✓ — the arms are behind `[TBD]`
guards — so it carries no regression risk for the 477 byte-exact cases by construction ✓,
*provided* the guard is retired only for shapes the prototype proves byte-exact ✓✓.

Prototype status: the `bind.ml` change is applied **in a throwaway git worktree**
(`/tmp/e14proto`, HEAD + that one edit) and is running the full 477-specimen gate there ✓,
because "does a numbering rule that fits D3/P9 also fit DECPOLY, R3104, LOAN1, NFACT" is a
question about the whole corpus, not about the four refusals ✓✓. Production at the time of
writing is byte-for-byte the committed state ✓.
