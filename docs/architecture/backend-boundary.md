# DRPLi architecture — the backend boundary (E2E-54/P0 audit)

Status: **FINAL — P0 CLOSED 2026-11-08; §7-1 added at P1-b CLOSE 2026-11-08** (audit pass
opened session `01a1bbbd`, E2E-54/P0; finalised at hop 4 close; see
`spec/lab-evidence/e2e54/RESULTS.md`). This document analyses
the CURRENT pipeline; it does not change it. All line anchors were
read from the tree at `b420fe01`/`c89a9df3` and are given as `module.ml:line`.

Scope discipline (brief §2): a **DR code-generation law** (measured oracle behaviour recorded in
`spec/CLAIMS.md`) is NOT a universally valid PL/I semantic rule. Where this file says
"semantic", it means *plausibly target-independent*, judged by inspection — not newly measured.
Zero oracle runs are part of P0.

## 0. The measured pipeline (as it actually is)

```text
bin/pli80c.ml
  → Parser.parse_source            (lexer.ml → parser.ml → Ast.block)
  → Codegen.rows_of blk            (codegen.ml:16535 — calls Bind.bind_program 2173 / Bind.bind_rows 1577)
  → Codegen.emit_program …         (codegen.ml:15804 — instruction selection, DR ABI, pool/statics layout)
  → Rel80.encode items             (rel80.ml:48 — LINK-80 bit-packed records)
  → 128-byte sector padding        (pli80c.ml)
```

`ir.ml` (324 lines) is a **separate diagnostic emitter for DR's historical `$V` IR** (validated by
`tools/ir_gate.py`, model `spec/notes/ir-opcodes.md`, claims C051/C052/C058). It is *not* a
backend-neutral IR and is deliberately left untouched (brief §2 warning, restated here).
`bin/pli80ir.ml`, `pli80bind.ml`, `pli80tree.ml`, `tokdump.ml`, `pli80deps.ml` are read-only
observation CLIs; the production path is only `pli80c.ml`.

## 1. Responsibility map (brief §2 list, with measured anchors)

### 1.1 Name resolution and lexical scopes — SPLIT, partly reusable

- Block declaration harvesting: `bind.ml:frame_decls:390`, `bind.ml:pl_kids:435` (level-numbered
  structure children), `bind.ml:block_kind` usage in `bind_program`.
- Per-block row tables (name → type → offset): `bind.ml:layout:620` (returns `rows`), exposed as
  `bind_rows:1577`, `bind_arrays:1588`, `bind_members:1592`, `bind_label_arrays:1600`, and per
  procedure as `proc_layout.pl_rows:1955` (body-visible rows), `pl_members:1961`.
- **Alias policy is DR-measured, not semantic**: bind registers a bare (unqualified) alias only
  for some member kinds (`RTbin 15 | RTptr`); other internal members land in `unaliased` and
  reach codegen only through `pl_members` so it can *name its refusal*
  (`codegen.ml:vinfo_imem:884`, `member_note:903`). Outer-scope shadowing/precedence rules follow
  DR listings, e.g. qualified-use checking `check_qualified_uses:535`, `unshadow_char_members:469`.
- Suffix/qualified *use* resolution lives in **codegen**, not bind:
  `codegen.ml:resolve_suffix:1033`, `qref_key:4550`, `imem_in_e:4570`, `imem_of_name:4585`.
- Call-target classification: `bind.ml:proc_entries:1742` (which names are procedures), and the
  DFS registry inside `bind_program` (`collect`, `reg`, `is_proc`).

Classification: *reusable after a small extraction* for scalar/qualified lookup (it is already
read-only data in `prog_layout`); the alias-registry policy and suffix resolution are
*DR-specific/unknown* until independently characterised.

### 1.2 Type interpretation — semantically reusable (best seam in the tree)

- `bind.ml:rt` (37) is a semantic type record: precision, scale, varying flag, pointer, label,
  struct shape. `rt_of_basic:129`, `resolve_type_raw:284`, `resolve_type:328`, `check_fixed_prec:119`
  (DR's bin/dec ≤ 15 ceiling — **a DR-measured limit [C-era evidence E1415..E1432], recorded in the
  code comment as DR behaviour, not adopted as language law**), `has_attr:195`,
  `apply_varying_attr:240`, `returns_attr:410`.
- `rty_str:78` already prints types in DR's own words — a deterministic type printer exists.
- The *physical* projection `bytes_of` (~bind.ml:148 region) and the pool-cell encodings in
  codegen (`bcd_pack:1394`, `mbf_encode:1750`, `dec_pool_bytes:1362`) are **storage format, not
  type** — they are exactly what the brief's §3 separation example (FIXED DECIMAL(9,2) vs packed
  decimal vs modern decimal) forbids inside HIR.

Classification: `rt` + interpretation = *semantically reusable*; sizes/encodings =
*historical DR-specific*.

### 1.3 Numeric conversions and expression typing — entangled, not independently characterised

- There is **no expression-type function in bind**. Result-type knowledge is distributed through
  codegen decisions: `dec_prec_of:2171`, `is_dec_expr:6394`, `dec_pt_of:6991`, `dec_cmp_pt:7015`,
  `num_width:12642`, `is_float_expr:7233`, the operand-classification in `e25_bin_routes:2194`
  and `e25_bin_routes_dec:2236`, `elide_fixed_zero:4369`. These functions choose *both* a type
  shape *and* an instruction route; the type component is not separable by inspection alone.

Classification: *unknown / not independently characterized* as a reusable unit. P0 does **not**
extract it. HIR expression typing for the P0 subset is computed by an explicitly documented
language-level rule (see §4) rather than by guessing DR's unmeasured internal typing; no DR
behaviour is claimed.

### 1.4 Addressable values and aliasing — DR-specific machinery over reusable facts

- Frame addressing: `addr_of_raw:931`, `addr_of:953`, `vk_of:958`, `dyn_ref`/`dyn_addr:1147`,
  `hl_bias:8014`, `member_step:624`, `store_based:10066`, `store_zero_pair:672`.
- Pointer/BASED view semantics: `RTbased`/`RTbmem`/`RTimem` in bind (1.2) carry *which* pointer
  views which type at which record offset — semantic in kind, but the offsets are DR layout
  numbers.
- Register/accumulator aliasing state (`a_zero:204` region, `de_val`, `last_imm`, `kill_de:702`)
  is pure 8080 instruction-selection state — never HIR material.

Classification: the *addressability fact* (is this name a variable, a constant, a label value) is
*reusable*; every address *computation* is *historical DR-specific*.

### 1.5 Procedure signatures and calls — signatures reusable, ABI not

- Signature facts already exist in bind output: `proc_layout.pl_ret:1953`, `pl_ptrs:1954`
  (formal → pointer cell — *the mapping* is semantic, *the 2-byte cell* is DR), `pl_rows`,
  `prog_layout.pl_exts:2011` (params, external_, returns, formal types), `pl_secs:1976`.
- Call-site discovery: `pl_expr_calls:2020`, `pl_stmt_calls:2052` (bind), `call_site:1650`.
- Formal-type lookup at lowering time already reads bind: `callee_formal_rt_l:3984` /
  `callee_formal_rt:4004` — the precedent that proves HIR can be a *consumer* of bind, not a
  rival resolver.
- Everything about *how* calls execute — descriptor cells, the pool, `?CALL` linkage, SVBLK,
  shadow cells (`pl_sp_cell`), `call_ext:660`, builtin names (`?SMCCM`, `?SLCTS`, `?QDDSL`,
  `?STOPX`, …) — is the DR runtime ABI.

Classification: *semantically reusable* (signatures/call graph) + *historical DR-specific* (ABI).

### 1.6 Control-flow semantics — facts reusable, lowering entirely DR

- bind survey gives target/label facts: `own_labels_stmts:1721`, `refs_stmts:1767` (with
  `ref_kind:1702` `Rk_on/Rk_plain/Rk_val`), `label_class_names:1826`, `survey_all:1933`,
  `on_facts:1706`, `facts_of:1938`.
- The lowering is 8080/DR through and through: recovery pads, epilogue/guard windows,
  `resolve_label:13838`, `label_def:13909`, `emit_pad:13896`, `fwd_ref:14033`,
  `lower_test_skip0:8991` (condition evaluation *is* branch-code generation), `do_bound_deref`.

Classification: the *classification of labels and gotos* is *reusable after a small extraction*;
evaluation-order/short-circuit behaviour of conditions is entangled with instruction emission
(*unknown* as an independent semantic unit — P0 takes explicit evaluation order from a
language-level reading, documented, not from a DR measurement).

### 1.7 Storage allocation and layout — historical DR-specific

- `bind.ml:layout:620` computes DR DATA-area offsets (`soff` static counter vs automatic packing,
  comment citing bind.ml:329-340 and [C114]); `proc_layout`/`prog_layout` fields
  (`pl_secs`, `pl_total`, `pl_top_cell`, `pl_sp_cell`) are LINK-80 area numbers.
- codegen re-derives its DATA-area order `[prealloc EDIT tables][statics][pool][automatics]`
  (`st.stat_addrs:172` region, `prealloc_fmt_tables:3302`, `pool_alloc:546`).

Classification: *historical DR-specific*. HIR must carry **no** offset — only the semantic fact
"declared static vs automatic" may survive (as `storage` on a symbol, see §4).

### 1.8 DR-specific runtime ABI — historical, entire layer

File control blocks (`file_cb_bytes:15718`, `load_file_cb:1339`), builtin entry points
(`call_ext:660` and every `?NAME` string), `?STOPX` epilogue, saved-SP cells (`emit_sp_save:13814`),
ON-unit registration prefixes (`on_reg_prefix:13769`), EDIT/PUT/GET chains
(`lower_put_items_gen:13194`, `?SIOOP/?QIOOP`). Classification: *historical DR-specific*; it is a
**backend**, and `Rel80.encode` + `tools/` LINK-80 behaviour (128-byte sector padding in
`pli80c.ml`) belong to the same layer.

### 1.9 Intel 8080 instruction selection — historical, entire layer

`op_*` opcode constants (595-1288), `lower_hl:4619` (the ~1400-line expression→HL emitter),
`lower_assign:10229`, `store_char:6072`, `cmp_*` families, register-state tracking,
`emit_triple:1261`. Classification: *historical DR-specific*.

### 1.10 LINK-80 relocation and record sequencing — historical, entire layer

`rel80.ml` (`rel_item:16`, `encode:48`, record-type constants 72-94): the bit-packed record
stream, CHAIN-ADDR/CHAIN-EXT semantics, segment model. Classification: *historical DR-specific*.

## 2. Where the responsibilities are tangled (the actual finding)

1. **bind = semantics + DR layout in one pass.** `layout` cannot answer "what is x's type" without
   also deciding x's DATA offset under DR's packing, and its *alias registry* policy (which bare
   names exist unqualified) is itself derived from DR listings. Extraction is possible but would
   shift golden offsets — **must not be refactored in P0** (brief §5: incremental + independently
   regression-tested; the regression budget is P1+).
2. **codegen = expression typing + instruction selection in one walk.** `lower_hl` knows the type
   rules only as guards on instruction shapes. Nothing here is safely extractable without parity
   work.
3. **The reusable semantic surface that already exists is read-only data**: `prog_layout` /
   `proc_layout` / `rt` / `ref_kind` / `on_facts` / the label-name sets. That is precisely what
   HIR construction consumes. The precedent for consuming it at lowering time is
   `callee_formal_rt` (codegen already does exactly this).
4. `ir.ml` models DR's `$V` stream — a *third* thing: neither bind data nor an IR contract. Left
   alone.

## 3. P0 decision: the seam that costs zero historical risk

The adapter `Hir_build` consumes `(Ast.block × Bind.prog_layout)` — the same pair `rows_of`
already consumes — and lowers only the P0 subset. Rules:

- Every identifier resolves through a bind `pl_rows`/`pl_exts`/`pl_procs` entry — never through a
  re-implementation of lookup (brief §5; falsifier F6).
- Every HIR type is a pure function of a `Bind.rt` mapped into `Hir.ty` — precision/scale/varying
  carried, **byte sizes and offsets dropped at the boundary** (falsifier F8).
- Anything outside the subset → `Diagnostic` (stable code + line), nonzero rc, no partial dump
  (falsifier F9). Silent generic nodes are forbidden by design: the statement grammar in `Hir` is
  closed over the subset, so there is *no constructor* to silently misuse.

## 4. Expression typing: explicit language-level rule (documented assumption, NOT a DR claim)

For the P0 arithmetic subset (`FIXED BINARY`, `+ - *`), HIR result types use the classical PL/I
language rule: `FIXED BINARY(p1,0) op FIXED BINARY(p2,0)` yields `FIXED BINARY(max(p1,p2)+1,0)`
for `+`/`-`, and `FIXED BINARY(p1+p2,0)` for `*` (sum of precisions). Adopted-in-code amendment
(hop 2, recorded in RESULTS §3.3): a rule result above the profile's FIXED ceiling is **CLAMPED**
to that ceiling and the node's `typing` string names both the language rule and the clamp —
refusing instead made the pre-registered §P0.6 fixtures unlowerable.

PRECISION (recorded honestly): DRPLi's oracle evidence pins DR *object bytes* for bin(15)
arithmetic but has never measured DR's *internal result precision* for these expressions
(no `$V` dump witness pins max+1 vs max for addition in this repository). P0 therefore types P0
binary nodes with the **language-level rule marked `Language_level` in the HIR node** (the rule's
provenance travels with the node), and `Target.profile` records the DR profile's numeric-typing
field as `Unknown — unmeasured; needs a preregistered oracle experiment`. Nothing in P0 asserts
this is what DR computes. Multiplication overflow precision beyond DR's measured 15-digit FIXED
ceiling (`bind.ml:dr_max_fixed_prec:119`, itself DR-measured) is CLAMPED to the ceiling by the
profile (see amendment above); a future pre-registered `$V`-stream experiment may replace the
language rule and the clamp with measured behaviour — only the profile field and the rule string
would change.

## 5. What the future MIR backend will need from this layer (brief §10.5)

(Study only; the external lab `cyrilmhansen/mir-madc-aot-lab` was checked for local accessibility
without network at P0 close — **not reachable**, recorded as `[TBD — lab not reachable]` in
RESULTS §5. P0 adds no MIR/MADC dependency.)

- Typed values with semantic precision/scale, not cells: `Hir.ty` (no `bytes_of`, no pool address).
- Stable symbol identity across functions: `sid` + scope tree.
- Call/return signature facts: `Hir.proc.params` (formal sids in declaring order) +
  `Hir.proc.ret` (`ty option`) and `SYM` types per formal — *not* the 2-byte
  pointer cells; MIR chooses its own ABI.
- Explicit conversion nodes so the backend decides representation conversions itself.
- Deterministic, position-annotated IR so the backend can emit DWARF-free debug annotations later.
- A `Target.profile` it can extend (default int precision etc.) with UNKNOWN fields honoured as
  compile-time refusals, not defaults.

## 6. Safety list (what must NOT be refactored yet)

- `bind.ml:layout` alias-registry policy and offset arithmetic — any change moves goldens.
- `codegen.ml` lowering — it is the byte-exact oracle reproduction itself.
- `rel80.ml` and the sector padding in `pli80c.ml` — LINK-80 evidence surface.
- `ir.ml` `$V` emitter — separate scientific instrument.
- The refusal surfaces (`[TBD]` failwiths, histogram-pinned sites) — census/gate property.

## 7. Candidate safe extractions for a later phase (PROPOSED, unranked, none executed in P0)

1. A read-only `Semantic_env` view module exposing bind's name→`rt` facts *without* offsets
   (pure projection over `prog_layout`, zero bind edits).
2. `bytes_of`-style physical projection moved beside `Rel80` producers as a *layout* module —
   behaviour-preserving, needs a full gate.
3. Extracting expression typing out of `lower_hl` guards — large, needs its own campaign.
4. Replacing `Hir_build`'s subset refusals one at a time as oracle evidence for each construct
   shape arrives.

### 7-1. E2E-54/P1-b LANDED — item 1 executed (CLOSED 2026-11-08)

Item 1 is now real: **`ocaml/hir/semantic_env.ml`** (476 L) — a read-only, typed
projection over `(Ast.block × Bind.prog_layout)`, transitional by design (lives in
`pli80_hir`; the historical pipeline never references it; `pli80c.exe` never links it —
S1 `172595d5…` held through every step and on a fresh build dir). Measured end state
(RESULTS §P1-b): `Hir_build`'s ONLY remaining Bind references are the module alias
(`hir_build.ml:41`) and the single `Bind.bind_program` call (`:557`), pinned by name in
`tools/hir_test.py` (F10); the six table-reconstruction sites (§P1-b.1 audit 4/6/11/14/15/16)
are owned by the env; **no offset, cell size, section size, pool address or relocation
crosses the seam** (excluded by contract §P1-b.2, grepped by S8); the public interface
references **no `Hir` type** — the subset gate `ty_of_rt` stays in the consumer and quotes
bind's own `epr`/`sret_pr` renderings VERBATIM, so every diagnostic is byte-identical
across the seam (S10) and H01–H05 dumps are byte-frozen (S2). Semantic authority is judged
against the LIVE env by `ocaml/hir/semtest.exe` (7 invariants + `--corrupt` non-vacuity
control), never against dump text. Honest audit result, re-confirmed at close: class [D]
(duplicate resolution) was **NONE** — P1-b removed table-reconstruction machinery and made
it testable, it did not delete a second binder. The six facts Bind still does not expose
(§P1-b.6 / RESULTS §P1-b.4) remain documented gaps; per-`BEGIN` scoping is the one that
BLOCKS the corresponding P1-a construct. Items 2–4 stay PROPOSED, untouched. **P1-a is NOT
authorized.**

### 7-2. E2E-54/P1-a1 LANDED — arrays and addressable references (CLOSED 2026-11-09)

Item: **addressability** (§1.4 "Addressable values and aliasing") gains its first
HIR-side representation. Measured outcome: the HIR now expresses one-dimensional
arrays **semantically only** — `Array1{elem;lo;hi}` carries the element type and the
DECLARED index bounds; `Elem_read` (load) and `Elem_ref`/`T_elem` (designation) are
distinct constructors so read and designate cannot collapse; assignment targets are the
typed `target = T_var | T_elem`, not value expressions. Every physical array fact
(element width, placement, stride) STOPS at the `Semantic_env` boundary: bind's
`bind_arrays` channel is read by exactly two modules — the projection and the test
binary — and the width is dropped at first touch (T5/T6 greps, enforced by
`tools/hir_test.py`). Out-of-subset array uses (whole-array, subscript-on-scalar,
wrong dims, out-of-band elements, dims-without-record) refuse loudly on stable codes
HIR-E02/E03/E12/E13/E14 with ZERO output; DR's runtime bounds and intermediate-typing
behaviour remain UNMEASURED `[TBD]` — the E12 constant range-check is an HIR subset
rule, never a language claim. Descriptor/actual array passing is out of scope (future
slice). Full panel: RESULTS §P1-a1.

### 7-3. E2E-54/P1-a2 LANDED — procedure arguments and indirect references (CLOSED 2026-11-10)

Item: §1.5 "Procedure signatures and calls" gains its first HIR-side ARGUMENT
representation. Measured outcome: the HIR now distinguishes argument forms **by
construction** — `actual_form = A_value of expr | A_reference of designator`, so a
by-value actual cannot masquerade as a reference; `designator = D_var{sid} |
D_elem{base;subs}` (the P1-a1 assign-target `target` renamed and SHARED with argument
references, dump bytes unchanged). Passing semantics enter HIR only as a SYMBOLIC
classification projected by `Semantic_env` (`passing_mode`: own-cell / value-cell /
immediate / copy-in / unknown): every physical parameter-passing fact — descriptor slot,
value-cell placement, DEC temp (`cs_slot` is not even READ outside `bind.ml`) — STOPS at
the seam, enforced by the extended RAW T5 greps (`pl_calls|cs_temps|cs_copies|cs_dec|
bind_arrays` read ONLY by the projection and the test binary). Call lowering is
EVIDENCE-DRIVEN: `call_evidence` matches bind's recorded site by callee key plus PHYSICAL
`(==)` identity of the argument nodes (the matching law CONFIRMED first-hand at
expression and statement sites — hop 6/7), and typed absence refuses loudly on new
stable code HIR-E16; it NEVER guesses a position. Whole-array actuals refuse E15,
argument type mismatch E17 (DR behaviour `[TBD]`). Statement calls with arguments are now
lowered to `Call_s` (previously refused E04) — the slice's only sanctioned behaviour
expansion besides the E13→E15 handover. Language-level argument EVALUATION ORDER remains
[unmeasured] [TBD]: the dump's `args left-to-right` is the §P1-a2.2 adjudication, backed
as DR EMISSION order only [C093]. Semantic authority is judged LIVE by semtest I11–I13
sharing their comparison functions with four new non-vacuous corrupt controls (seven
modes total, 11 positives × 7 = 77 control runs, each rc 1 ZERO stdout). The alias-pair
and nested-actual fixtures pin HIR REPRESENTATION only, never runtime behaviour. Full
panel: RESULTS §P1-a2.

### 7-4. E2E-54/P1-h LANDED — BEGIN/DO discovery hygiene (CLOSED 2026-11-10)

The pre-existing HIR procedure-discovery hang (§P1-b.5 note 3) was REPAIRED, zero-oracle, in
ONE file: `Semantic_env`'s discovery walk is now the structural visitor
`discover_stmts st plan ctx ss`, which SEPARATES the statement subtree being traversed from
the enclosing procedure's semantic owner. A non-`Bproc` nested block (BEGIN/DO) is descended
for its OWN statements under the SAME `ctx` — bind has no per-BEGIN scoping (`frame_decls`
stops at `Sproc`, `bind.ml:390-408`) and its `collect` descends every `Sproc` child while
registering only `Bproc`s (`bind.ml:2204-2231`), so mirroring it exactly invents no scope,
pid, signature or ownership. Termination is structural. Shapes that previously hung (rc 124)
or BOGUS-refused with `duplicate internal procedure name` now dump rc 0 with the BEGIN's
statements inlined EXACTLY ONCE (H22–H28 measured; H28 is the regression witness). A `dcl`
inside a BEGIN still refuses on the LIVE typed channel `HIR-E03 … produced no bind row in
this block` (H29 pins it; the `bdecls <> []` E11 guards are DEAD for parser ASTs and were
kept, not removed). DO groups still refuse E05 by name; the conditional-position nested-proc
asymmetry (M-6) is PRE-EXISTING, untouched and carried as an unknown. No diagnostic, HIR
node, lowering rule or `ocaml/lib`/`ocaml/bin` byte changed; zero drift MEASURED (H01–H21
frozen; gate 1328/1328-190/190-9/9-149 rows 0/0-16/0/25/0-prose 5 ALL HIT; all 11 semtest OK
numbers unmoved). `semtest.ml` gained the §P1-a2.6 shared-comparison extraction of I6 plus
two non-vacuous controls (`--corrupt-owner`, `--corrupt-discovery`) — live + NINE corrupt
modes on 18 positives. Panel: RESULTS §P1-h.
