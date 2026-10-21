# C146 (descriptor record placement) — status after E2E-15/E2E-16, and the gate on attempting it

**No production work was done on C146 in E2E-16, by instruction.** `ocaml/proto/` (ARCH-1) is
unmodified, `bind.ml`/`reloc`/`link` are unmodified, and all six shapes that depend on it still
refuse loudly with the reason named: P5 `(t+u)+g(3)`, P6 `t-g(3)`, P12 `g(3)+g(4)`, D1, D11, D12.

## Clarified evidence (what the last two milestones actually changed)

1. **Instruction selection is NOT the problem.** With the C150 parking rule in place, my lowering
   matches DR sequence-for-sequence on all three refused probe families:
   - P6 `t - g(3)` -> `LHLD T / PUSH H / LXI H,*A / CALL G / POP D / CALL ?IS22N`
   - P12 `g(3) + g(4)` -> `LXI H,* / CALL G / PUSH H / LXI H,* / CALL G / POP D / DAD D`
   - P5 `t + u + g(3)` -> `LHLD T / XCHG / LHLD U / DAD D / PUSH H / LXI H,* / CALL G / POP D / DAD D`
   The E2E-14 report of a P5 code-address mismatch (mine 0056 vs DR 005F) was an artifact of my own
   measurement bypass, which replaced `add_left_needs_push` with `false` and rerouted the expression
   through the DEFER path [R1, retracted]. **A bypass that changes routing is a change of subject.**
2. **Record placement IS the whole divergence.** DR emits a call's descriptor record as soon as its
   content is knowable -- before the enclosing expression's first code record -- while I emit it at
   the point of use. P5: DR's `SET-LC(data,000B)` sits at bit 1892, ahead of code starting at 0056.
   Where the DEFER route happens to make both coincide (P1-P4, P7-P11, D3/D9 class) the output is
   already byte-exact; where a PUSH route intervenes it is not.

## The prerequisite, stated as a criterion

Any prototype must demonstrate, **in isolation and before touching production**:

* descriptor records can be emitted ahead of code records that have not been emitted yet, without
  a second ordering authority;
* the anonymous-cell NUMBERING (C145's two-phase rule in `bind.ml`) and the record PLACEMENT remain
  one consistent model -- E2E-14's lesson is that conflating them nearly shipped a stream-reordering
  mechanism to fix an address inversion;
* the record/chain/dedup ORDER that ARCH-0 identified as the riskiest property of the current design
  is preserved for all 531 accepted specimens, not merely "the gate passes";
* there is exactly one source of truth for emission order. If a capture/replay path needs its own
  queue separate from the existing threaded location counter, that is a second source of truth and
  the prototype has to show why they cannot diverge -- the demand/layout pair in C152 is what two
  sources of truth looked like when they diverged, and it took a byte-count mismatch in a probe to
  find it.

The existing `new`/`old` route choice (`add_left_needs_push`, `hl_bias*`) is what makes the timing
difference observable at all, so a prototype that only reorders records without keeping those routes
byte-exact has not reproduced the phenomenon.
