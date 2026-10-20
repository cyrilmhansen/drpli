# ARCH-0 — architecture map and read-only review of `codegen.ml`

Date: 2026-08-03 (session 14). **Scope: read-only.** No production file was
modified for this review; every number below was produced by mechanical
extraction (`grep`/`awk`/a short Python region-analyzer) against the tree at
commit `4f8c3cc`, so a later session can re-derive them instead of trusting me.

Deliverables: §2 pipeline, §3 responsibilities, §4 state, §5 ordering hazards,
§6 duplicate traversals, §7 where DR's rules actually live, §8 the semantic /
compiler-decision / serialization split, §9 evaluation of the structured-IR
proposal, §10 smallest useful rule+evidence representation, §11 prototype
recommendation with a kill criterion, §12 what this review did *not* establish.

---

## 1. Size, in numbers that matter

| quantity | value |
|---|---|
| `codegen.ml` | 6,052 lines |
| `bind.ml` / `parser.ml` / `ir.ml` / `ast.ml` / `rel80.ml` | 1,194 / 1,209 / 324 / 169 / 94 |
| top-level definitions in `codegen.ml` | 169 `let` + 7 `and` |
| mutable fields in `cstate` | **33** (plus 2 in `lblstate`) |
| `failwith` sites (≈ `[TBD]` refusals) | **232** |
| raw byte-emission sites (`d st …`) | **484** |
| inline-reloc sites (`reloc st …`) | 94 |
| RTL calls by name (`call_ext`) | 89 |
| `st.lc` reads/writes | 59 |
| functions matching the walker-name pattern | ~40 |
| comment lines in `codegen.ml` | 416 (≈ 7%) |
| evidence IDs cited in the file (Cxxx/Nxx/Rxxxx/Exx/Pxxx forms) | 480 |
| claims in `spec/CLAIMS.md` | 56 (C001–C134) |
| golden directories | 260 |
| scripts in `tools/` | 20 |

Two of these dominate everything else: **484 byte-emission sites inside lowering
functions**, and **33 mutable fields on one record that lowering threads through
them**. Neither is a style problem; both are the mechanism by which ordering bugs
reach byte identity.

---

## 2. The pipeline as it actually runs

The front end is genuinely staged; the back end is one function with an implicit
phase order. `emit_program` (`codegen.ml:5433`, ~619 lines) executes, in sequence:

| step | line | what it establishes |
|---|---|---|
| 1. statics pre-seed | ~5478 | `[statics]` bytes and their pool offsets |
| 2. `check_stmt` sweep | ~5508–5531 | whole-AST validation (refusals before emission) |
| 3. **`Bind.bind_program blk`** | ~5531 | **the one clean phase boundary in the project** |
| 4. type-map / `pd_vars` build | ~5589–5620 | the prescan's view of variable types |
| 5. `prescan_pool` → `pool_total` | ~5620 | every pool cell *demanded*, never allocated |
| 6. `const_cells` (call-literal cells) | ~5533–5568 | second, separate demand pass |
| 7. `base = statics_total + pool_total`; `st` construction | ~5628 | **the data area is fixed here** |
| 8. `lower_stmt` over main body | ~5669–5694 | code emission, descriptor cells, forward chains |
| 9. tail-guard backpatch | ~5730–5748 | `JMP` operands rewritten to point at the epilogue |
| 10. REL header items (PROG-NAME/EXTDEF/DEF-PUBLIC, 6-char truncation) | ~5758+ | record construction |
| 11. `Rel80.encode` | `rel80.ml:48` | bits → bytes (the only real serialization layer) |

Steps 4–7 are the demand/allocate/basis sequence, and steps 5 and 6 are **two
independent demand passes feeding one total**. Step 8 is where cells are actually
created. Nothing in the type system or the code structure enforces that step 8's
allocations were all demanded in 5+6 — that is a discipline maintained by memory
and by the byte gate.

`Rel80.ml` deserves credit: it is a real encoder (bit writer, record types, 94
lines) and it is *not* where the coupling lives. The coupling is one level up:
`rel_item` values are constructed inline during lowering, interleaved with opcode
bytes, and their **append order is a semantic property of the output** (see §5).

## 3. Responsibilities and their current owners

| responsibility | today's owner | location | coupling |
|---|---|---|---|
| Semantic interpretation (types, storage class, STATIC/INITIAL, pointer-vs-value formals, RETURNS rules) | `bind.ml` **and** `codegen.ml`'s `vkind`/`vk_*` helpers | `bind.ml` (rt, prog_layout) + `codegen.ml:21` (`vkind`), `vk_of`, `addr_of` | **duplicated**: `vkind` re-encodes `Bind.rt` into a codegen-local type, and neither carries ENTRY until step 4 added `exts` beside it |
| DR code selection (which instruction sequence for which construct) | `lower_assign`, `lower_hl`, `lower_test_skip*`, `fl_*`, `ds_*`, `dec_*` | ~3,600 lines of `lower_*`/`fl_*`/`dec_*` | expressed as `match` arms + `when` guards; a selected shape is invisible outside the function that chose it |
| Data layout (statics/pool/automatics, dedup, elision) | `emit_program` steps 1/5/6/7 + `pool_alloc`, `fl_pool`, `elide_fixed_zero` | spread across the orchestrator and the demand passes | **implicit ordering** (§5.1) |
| Instruction generation (8080 bytes, opcode quirks) | `d st`, opcode constants (~40 `op_*`), and raw hex literals | 484 sites, e.g. `d st 0x32` for STA, `0xbe`/`0x9e` for CMP M/SBB M | mixed with item construction; many opcodes are inline hex with a comment, not named constants |
| REL item construction & serialization | `push`/`reloc`/`emit_triple` + `rel_item` constructors in `codegen.ml`; `Rel80.encode` | interleaved in lowering; encoder separate | append-order (§5.2) |

The five responsibilities are not separated by module boundaries; four of the five
share one record and one file, and the fifth (semantics) shares a *type* with a
local mirror.

## 4. State inventory (33 mutables), grouped

Reading the record at `codegen.ml:40–168`, the fields fall into six groups, and
the grouping is what tells you which phases are secretly present:

1. **Output accumulation** — `items`, `lc`. Ordering-sensitive by definition.
2. **Data-area layout** — `pool`, `pool_next`, `fl_cells`, `dec_cells`, `stat_addrs`,
   `stat_total`, `secs`, `floor`, `base`(computed), `fmtq`, `files`. This is a *layout
   phase* living inside the lowering record.
3. **Call/descriptor machinery** — `calls`, `procs`, `exts`, `entries`, `fcalls`,
   `deref`, `call_stmt`, `dec_ret`, `float_ret`. Note `fcalls` is **prepend-ordered**
   (head = latest) and `calls` is a prescan FIFO: two different orders over the same
   call sites.
4. **Expression-evaluation micro-state** — `last_imm` (HL still holds this constant?),
   `temps`, `lowered`, `guards`, `guard_slots`, `appended`, `stop_seen`,
   `after_forever`, `last_loop_edge`, `in_proc`, `in_rec`, `vars`, `items`.
   `last_imm` is DR's constant-reuse optimization (C126: a LABEL definition kills it)
   and it is a *state field* rather than a property of an emitted instruction —
   which is why a future reader has to know the whole lowering history to use it.
5. **Label/linkage bookkeeping** — `lblstate.labs`, `.fwd` (forward-label backpatch).
6. **Configuration** — `base`, layout fields copied in at construction.

Groups 2 and 3 are candidates for their own records with their own phase. Group 4 is
where most of the 33 fields sit, and it is mostly *facts about the code just emitted*
held as mutable global state instead of being recomputed from the emitted sequence.

## 5. Hidden dependencies and ordering constraints (each one has already cost a bug)

These are the load-bearing invariants. Any restructuring that hides them behind an
abstraction will silently break byte identity, so they are the review's most concrete
output.

**5.1 Demanded-before-based.** `base` is computed from `pool_total` before any
lowering allocates. A cell type created during lowering must be demanded by a
prescan walker or the automatic variables land on top of pool cells. This session's
C134 is a three-part version of it: `pdec_fl_expr` had the Esuffix arm (so R3062 was
always exact), `prescan_expr` did not (so FDTEST's PUT-item call demanded nothing,
base 2 bytes short, `i` at 000d inside the constant at 000b–000e), and `const_cells`
plus `formal_float_at` each held a half-rule that produced a *double* count when the
missing count was patched in the wrong place. The symptom in both directions was a
small `DEF-DATA-SIZE` disagreement. **An over/under-allocated pool does not
corrupt addresses in a way any decoded dump shows** — every address still looks
plausible; only a value read at run time is wrong.

**5.2 Item append order = REL record order.** RELOC and LINK items are appended as a
side effect of emitting bytes, so the record order in the file is the order lowering
happened to touch them. Concretely: forward-reference chains must attach to the
*immediately preceding* site (C123, corrected version), and `LINK-CHAIN-ADDR`'s
target word is the only thing that says which site a chain hangs from — a decoder
that hides that field (which `reldump.py` did) makes different files look identical.

**5.3 `fcalls` vs `calls` disagree by construction.** One list is prepended, the other
consumed FIFO. A restructuring that "unifies" them by sorting one changes chain order
and therefore bytes.

**5.4 Zero-elision and dedup are layout rules with type preconditions.**
`elide_fixed_zero` is gated on every identifier being `Vint` (C116/C119); float cell
dedup is by identical bytes in first-use order (C101); dedup'd formal cells occupy no
storage (C106). Each of these is a *pair* of facts — the layout effect and the
condition under which it applies — and today the condition lives in the layout code
and the effect lives in the address arithmetic, in different places.

**5.5 Two walkers must agree on every statement kind.** C129: the omission class
(three occurrences: `prescan_pool` missing `Son`, `check_stmt`, `edit_stmts`). The
project's current mitigation is a **checklist in a note** — which is documentation
standing in for a structural property.

**5.6 Statement-order-sensitive evaluation.** C130's semantic witness (E28B
`a*10+b` → 53) is only reproducible if lowering keeps source order in the demand
passes: first-use ordering of dedup'd cells (§5.4) is a *source-order* property, so
any pass that visits expressions in a different order (e.g. grouping literals by
value for efficiency) breaks byte identity while remaining semantically valid.

**Bottom line on hazards:** 5.1, 5.2, 5.5 and 5.6 are all "two places must agree,
nothing enforces it". 5.3 and 5.4 are "an accident of implementation that is now load
bearing". A redesign must preserve them *explicitly* — as named stages and typed
orders — not preserve them by luck.

## 6. Duplicate AST traversals

~40 functions walk the AST; the ones that must agree per C129's checklist are
`prescan_pool`, `prescan_stmt`, `prescan_expr`, `pdec_fl_expr`, `pdec_operand_bytes`,
`edit_stmts`, `count_required`, `prealloc_fmt_tables`, `check_stmt`, `lower_stmt`,
`lower_hl`, plus `tools/mk_neg_panel`-adjacent `pli80deps.ml` in `bin/`.

Observation that the checklist misses: they are not duplicates of each other by
accident. Each one answers a *different question* about the tree — demand bytes,
count format tables, validate supportability, classify PUT lists, resolve skip
control, lower — and they were written in different slices as different questions
came up. So "one traversal to rule them all" is the wrong fix (it would need to
return a tuple of six answers, i.e. recreate the six phases inside one function).
The right fix is to make the *question* explicit: each of these is a separate pass
with a name and a declared output. Today they are 6 passes in disguise, distinguished
only by which function calls them, which is exactly why adding a callee type or a
statement kind means finding all of them by grep.

C133/C134 sharpen this: "is argument i of this callee FLOAT?" was answered by three
functions (`formal_float_at`, `pdec_fl_expr`'s Esuffix arm, `const_cells`) that each
resolved the callee their own way. After the fix all three call one accessor. That
is a one-line-per-consumer change with a measurable outcome (gate went 385→390 with
two corpus programs added), and it is the pattern to generalize: not "one AST walk",
but **one place per question**.

## 7. Where DR's rules actually live

Three media, in descending volume:

1. **Control flow.** 232 `failwith` sites; ~12 of them inside `lower_assign`
   (285 lines, 10 arms). Each refusal is a rule ("DR widens a narrow actual through
   an anonymous cell; I do not, so refuse" = E29C) recorded at the point where the
   decision is made — which is why they are individually correct and collectively
   unqueryable. There is no way to ask the build "which shapes do you implement by
   memory-form addressing?" without reading 6,000 lines.
2. **Comments.** 416 lines, 480 evidence-ID citations. Dense and unusually good,
   and they *are* the rule documentation. But prose is not checkable: nothing
   verifies that a comment's claim still matches the code, and the C123 episode
   shows a comment can be confidently wrong while the bytes pass `cmp`.
3. **`spec/CLAIMS.md`.** 56 claims, each with specimens and code references — a
   rule store maintained by hand, disconnected from the code that implements it.

The genuinely declarative parts already exist and are small: the `op_*` constants,
the `ds_*` decimal-model tables, `Bind.bytes_of`, `TYPES` in `reldump.py`, and
`SPECIMENS`/`REJECTS`/`NEG_META` in the gate. Those last three are proof that
declarative rule tables work fine in this project — the negative panel's *verdicts*
became machine-generated in `4f8c3cc` and immediately exposed the 54/11 skew the
prose had hidden. That experiment is the argument for §10.

## 8. Semantic behavior vs compiler decision vs byte serialization

This distinction is the useful output of the review, because the three kinds of fact
are interleaved at the same three lines in most arms. Worked example — a store
through a pointer formal (C127/C131):

- **PL/I semantics** (what must be true): `q` designates the caller's object;
  assigning to it mutates the caller's variable. Same for DEC and FLOAT.
- **DR's implementation decision** (how it chose to do it): pass the *descriptor
  address* in HL; store DEC via `?DSTOP` and FLOAT via `?FX44M`; take the
  destination in a register, so the only difference from the ordinary route is
  `LXI H,*A` → `LHLD A` — **one opcode**.
- **Byte-level serialization** (what it costs to write down): the `LHLD` operand
  becomes a DATA reloc item; the chain order of any forward reference; the 6-char
  truncation of `DEF-PUBLIC`; opcode `0x2a`.

The three have different failure modes and different evidence classes. Semantic
errors show up as wrong *values* (only found by running: E28B/E28C/E28E are exactly
this). Implementation-decision errors show up as byte *differences* (the gate's
daily work). Serialization errors show up as *linking* differences, and are the
class that decoders hide (C123). Right now the code expresses all three in one
`match` arm, so a reader — including me at fix time — cannot tell which kind of
fact a branch encodes, and neither can any future test.

Second example, same shape: `do i = 0 by 1` on a `fixed(7)` index. Semantic: the
induction variable is an integer cell. Decision: `XRA A; STA i` then
`LXI H,i; INR M; JMP` — in-memory increment, not `LHLD/INX/SHLD`. Serialization:
`STA` is `0x32` with an inline DATA reloc, not `0x3c`. The DTEST note (§3) records
that the middle fact, if guessed wrong, still produced correct printed values —
so only a byte compare catches it, which is precisely why the three layers must
stay distinguishable in the source.

## 9. Evaluation of the structured-IR proposal

The proposal: `semantic IR → DR lowering → symbolic 8080 → REL encoder`.

**For it:**
- §5.1/§5.6 become typed stages instead of discipline. If "demand" is a phase whose
  output is a layout, and "lower" is a phase that consumes that layout, the base
  cannot be computed before the demands are all in, because the second phase has no
  other input. C134 becomes unrepresentable — that alone justifies the shape.
- One question, one answer (§6): callee formal types, cell sizes, and mode
  classification would live in the IR, not in four functions.
- It makes the 232 refusal sites queryable and lets the negative panel's 54 gaps be
  priced as IR-lowering work rather than located by grep.
- The 8080 layer would hold the *implementation decisions* (§8), which is where all
  my hard-won DR facts live (`XRA A` vs `MVI A,00`, `LHLD` vs `LXI H`, `INR M`
  vs `INX H`, memory-form `CMP M`/`SBB M` for `>0` through a pointer). Today those
  facts are scattered through lowering; they are the project's most valuable asset
  and the least navigable.

**Against it, honestly:**
- **It does not touch the riskiest property.** Byte identity depends on item append
  order, chain order, dedup first-use order, and DR's quirks (5.2/5.3/5.4/5.6). A
  new IR adds a stage that *can* preserve them but does not *help* preserve them;
  the help comes from keeping the REL-item layer explicit (which is orthogonal to
  having an IR).
- **Cost is high and the payoff is deferred.** ~3,600 lines of lowering encode
  56 claims validated by 260 goldens and 390 byte-exact specimens. A rewrite's first
  commits would be *below* the gate, and the gate is the project's only hard
  evidence. Losing byte-parity protection for weeks, mid-reconstruction, is the
  worst possible time.
- **The clean seam already exists.** `bind.ml` is a real phase with a narrow typed
  interface (`rt`, `call_site`, `proc_layout`, `prog_layout`) and it has absorbed
  every change I've needed (this session: `pl_exts` + a widened `is_proc`, one
  commit, zero churn downstream). The evidence says the project's failure mode is
  not "missing a phase boundary" but "phases 5–7 of `emit_program` are inside a
  function instead of being named" — a much smaller extraction.
- **`ir.ml` is a caution.** The existing 324-line `ir.ml` reconstructs DR's `$V`
  traces; it is not a production IR, and `tools/ir_gate.py` gates it separately. A
  second half-real IR alongside the first would recreate the C134 pattern (two
  owners of one question) at architectural scale.

**Recommendation (this is the answer to "should we restructure now?"): no
rewrite; do three extractions, in this order, each byte-gated to 390 the whole
way.**

1. **Extract the layout/demand phase** out of `emit_program` into a module
   (`layout.ml`-shaped) whose inputs are `bind.prog_layout` + the AST and whose
   output is `{ statics; pool; base; cells }`. Pure data, no emission. This is the
   fix for the bug class I hit today and it is mechanical, not semantic.
2. **Extract the instruction layer** (`inst.ml`): lowering emits `Inst.t` values —
   `Movem | Lxi of operand | InrM | Call of operand | …` — where `operand` carries
   its relocation class (`Imm | DirCode | DirData | ExtSym | ChainExt`). One
   function converts `Inst.t list` into `rel_item`s, and *that* function owns record
   order and the quirks (0x32-vs-STA, 6-char truncation). This puts §8's three fact
   kinds in three places and makes the DR-decision layer searchable by mnemonic.
3. **Unify callee-type resolution** (already done for three consumers by
   `callee_formal_rt_l`); extend to `vkind` so `bind.rt` is the single type
   description and codegen-local mirrors disappear. Cheapest of the three; do it
   whenever convenient.

Each step is a *move*, not a redesign: same decisions, same bytes, better places.
Nothing here requires a new front end, a new IR, or touching `parser.ml`/`bind.ml`'s
public types.

## 10. Smallest useful rule/evidence representation

Not a rule engine. One generated table, `spec/rules.tsv` (+ a checker), with a row
per *fact*, linking the three media of §7:

```
rule_id   kind            construct              condition                      emission/lowering            specimens                       status
C131      code-selection  assign-through-ptr     dest=DEC, src=reg              LHLD + ?DSTOP                E26J,E28E                       implemented
C131b     code-selection  assign-through-ptr     dest=FLOAT                     LHLD + ?FX44M                E26K,E28D                       implemented
C130      code-selection  ptr-formal-as-actual   forward                        LHLD/SHLD, no SET-LC         E27B,E28A                       implemented
C123      serialization   forward-call-chain     2+ sites at same target        CHAIN-ADDR chains to prior   E25F,E27A,E27C                  implemented
C134      layout          float-literal-arg      formal is FLOAT                4-byte MBF cell, dedup       R3062,FDTEST                    implemented
C108      dr-limit        FIXED p>15             any                            refuse (NOT IMP)             N72,N73                         dr-refuses
E29C      my-gap          narrow-actual call     formal wider than actual       refuse (DR: widen to temp)   negpanel1/NG31                  refused-gap
```

`kind` ∈ `semantic | code-selection | layout | serialization | dr-limit | my-gap`,
i.e. §8's taxonomy plus the panel's two categories — which makes "which of these
56 claims is a DR rule and which is my limitation?" a `grep` instead of a memory
task, and would have caught the 9 mislabeled negatives mechanically.

Derivation, to keep it honest and cheap: `rule_id`/`specimens` come from
`SPECIMENS`/`REJECTS`/`NEG_META` in the gate (already machine-readable), `status`
from the gate's own verdicts (already generated), `kind` from a one-word label added
to each `## Cxxx` header in `CLAIMS.md`, and `emission/lowering` from the existing
`Cxxx` citations in code (`grep -oE 'C[0-9]{3}' codegen.ml` yields 26 today — the
generator should *report* claims with zero code citations and specimens with no
claim, both of which are currently invisible). One Python script, ~150 lines, no
runtime dependency from the compiler.

What it buys, concretely: (a) coverage gaps become enumerable rather than
surprising; (b) `tools/blocker_audit.py`'s payoff ranking can join against `status`
so "what would implementing DR's DEC-formal widening buy?" is a query; (c) the
C123-style failure — a claim whose supporting artifact is about a different thing —
gets a place to record what each specimen actually pins.

## 11. Prototype: yes, but not of the IR

Building a semantic IR prototype would test a hypothesis I already hold
confidently (§9: it would help) and would not test the one I don't. The open
question is whether **separating instruction emission from REL item construction**
can reproduce DR's bytes at all, given that record order and quirks are
load-bearing (5.2/5.3/5.6).

So prototype only §9 step 2, on one narrow path, in a new module nothing else
uses:

- Scope: one construct family — FIXED BINARY store/load (`lower_assign`'s
  `Eident`/`Enumber` arms) plus its pointer-formal variant (C127/C131) and the
  1-byte zero forms (C133).
- Inputs: bind's layout + a hand-written IR for exactly these shapes (no parser,
  no general lowering).
- Pipeline: `shape → Inst.t list → rel_item list → Rel80.encode → bytes`.
- **Acceptance: byte-identical `.REL` against 3 existing goldens** — N306/N308
  (1-byte const store), E26J (DEC through pointer), E29A (external ENTRY + `XRA A
  ; STA`). Chosen because they span layout, reloc, and the opcode-quirk class.
- Kill criterion: if the `Inst → rel_item` conversion cannot be written *without*
  access to a location counter threaded through the emitter, the abstraction is
  wrong and the extraction in §9 step 2 should be abandoned — that specific
  dependency (`st.lc`, 59 sites) is the real risk, not the instruction semantics.
- Cost: ~300 lines in `ocaml/proto/`, one `dune` target, no production change. It
  answers the architectural question for a day's work instead of a season's.
- If it succeeds, §9 step 2 becomes a migration with a known endpoint, and step 1
  (layout extraction) can proceed independently since they don't share files.

## 12. What this review did not establish

- **Instruction-level redundancy**: I counted `d st` sites but did not cluster
  emitted sequences, so I cannot say how many distinct code shapes exist or how
  much duplication there is. `vtrace.py`/`ctrace.py`/`tools/` suggest where to
  start; a real number needs a pass over goldens, not over source.
- **Whether 260 goldens are all still load-bearing**, and which claims rest on a
  single specimen (a golden deleted by mistake would silently orphan a claim).
- **How `ir.ml` and `trace*.py` relate to DR's `$V` in detail** — relevant because
  `bind.ml`'s `RTentry` mirrors a DR symbol-table entry type, which hints DR ran
  semantic analysis before emission; testing that hint (by reading DR's listing
  structure, not my code) is a separate investigation with real architectural
  payoff.
- **Cost of §9 step 1 in practice.** The extraction looks mechanical because the
  demand passes are pure; I have not tried it, and `prescan_*`'s `pdec_ctx` mutates
  a dedup list, which means the "pure data" claim needs checking before the
  extraction is priced.
- Anything about `parser.ml` or `lexer.ml` structure (out of scope; both look
  conventional and neither has caused an ordering bug this session).
