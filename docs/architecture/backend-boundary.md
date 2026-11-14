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

### 7-5. E2E-54/P1-m0 LANDED — first native MIR AOT path (CLOSED 2026-11-09)

The first experimental NATIVE backend path exists, entirely inside the `pli80_hir` seam and
with ZERO historical bytes (`pli80c.exe` `172595d5…` held at every step; FULL gate frozen
1328/1328-190/190-9/9-149 rows 0/0-16/0/25/0-prose 5 ALL HIT; ledger C380; zero oracle).
`ocaml/hir/mir_backend.ml` lowers the typed `Hir.program` (NEVER the dump text; no second
parse; no `Semantic_env`/`Hir_build` bypass) to deterministic MIR text under an explicit
native subset: one zero-argument integer-returning procedure, straight-line `Assign`/`Return`
over `FIXED BINARY(p,0)` locals, with EVERY unsupported construct refusing BY NAME through
the appended codes `HIR-E18/E19/E20` — a refusal is total (rc 2, zero stdout, no artifact,
the emitter is never reached). Numeric safety is an exact-interval proof inside
`W(p)=±(2^(p-1)-1)`; the MIR `i64` carrier is a REPRESENTATION choice, never a DR claim,
and profile-UNKNOWN overflow/conversion behaviour is HONOURED by refusing. MIR-specific
types, opcodes, register names and ABI live ONLY in the backend — HIR and `Semantic_env`
remain backend- and libc-independent. Host-side, `tools/mir_aot/mir2o.c` runs the pinned
laboratory's complete object-mode generation sequence (out-of-tree `libmir.a`, lab
`ccc92c5c…`/madc `f541a7a5…`, pins re-verified clean; `MIR_object_load` NOT used) and
`tools/mir_aot_test.py` proves the whole chain END-TO-END: the genuine emitted `.o` is an
`ET_REL` x86-64 object exporting `T pli80_<name>` which LINKS and EXECUTES with the
independently hand-computed results 42/45/10, verified in two fresh processes per fixture
and guarded by two corruption controls that both fail natively. The runtime executable
needs no libmir/MADC/OCaml (`ldd`: libc/vdso/loader only).

**Roadmap (operator amendment §RD-COSMO, 2026-11-09, recorded VERBATIM in PLAN.md):**
Cosmopolitan Libc is the PREFERRED standard C runtime for future DRPLi/MIR native
executables; short-term target Linux x86-64 **static ELF** (APE not required unless
trivial); principle: Cosmopolitan-first native runtime, backend-independent HIR, no
mandatory glibc runtime dependency. The gcc/glibc linkage of P1-m0 is a DIAGNOSTIC
REFERENCE, not the deployment target; the static-link requirement concerns the GENERATED
executable — the build-time MIR emitter may still depend on host libraries. PROPOSED
stages, NONE authorized by this close (each needs its own PROTOCOL #1 pre-registration
and explicit operator authorization):

- **P1-mC — Cosmopolitan static-link feasibility**: reuse the GENUINE MIR-produced `.o`;
pin a Cosmopolitan/cosmocc toolchain version; investigate `x86_64-unknown-cosmo-cc` with
`-moptlinux`; build a small native C test driver with Cosmopolitan; attempt static linking
with the MIR-generated object; verify ABI compatibility, relocations, native execution and
the expected result, and the ABSENCE of `PT_INTERP`/`DT_NEEDED`; keep GCC/glibc linking as
the diagnostic reference; NEVER substitute generated C for MIR-generated machine code.
- **P1-m1 — Minimal PL/I console runtime**: small C adapters for integer/string input and
output linked against Cosmopolitan; PL/I I/O semantics explicitly DISTINGUISHED from the
underlying libc functions; test EOF, input errors, buffer bounds and deterministic output;
NOT a wholesale PLILIB reimplementation.
- **Future — portable native formats**: ARM64 native output first; APE only after the
static ELF integration works; HIR and MIR lowering stay independent of the selected libc
and of the final executable format.

Panel: RESULTS §P1-m0.


## 7-6 E2E-54/P1-mC — Cosmopolitan static-link feasibility (CLOSED 2026-11-09)

The native MIR objects of §7-5 are **libc-agnostic**: the SAME `mir2o` object bytes
(`M01 78656e6c…`, `M02 3822f777…`, `M03 02c15b1b…`, hashed BEFORE linking) link under
gcc/glibc AND under a pinned official **Cosmopolitan 4.0.2** (`cosmocc-4.0.2.zip`,
sha256 `85b8c37a…3f44`, GCC 14.1.0) into **plain static Linux x86-64 ELF** — no
`PT_INTERP`, no dynamic section, no `DT_NEEDED`, `nm T pli80_<n>`, MIR-originating code
disassembled, and **42 / 45 / 10 EXECUTED** in two fresh processes per fixture; both
non-vacuity controls fail natively on the Cosmopolitan path (C-a executes 13, C-b 42≠43).
Only the LINK COMMAND changed: the driver `tools/mir_aot/native_check.c`, the emitter
`mir2o.c`, the MIR backend and every `ocaml/` byte are untouched (`git diff --exit-code --
ocaml/lib ocaml/bin ocaml/hir hir/` rc 0); the recipe lives in
`tools/mir_aot/cosmo_link.sh` (raw `x86_64-linux-cosmo-gcc` + the wrapper's own
BUILDLOG-derived flags + `lib/optlinux/{ape-no-modify-self.o,crt.o}` + `-lcosmo` +
`ape.lds`) and is driven through the distribution's native ELF loader `bin/ape-x86_64.elf`
because this host's `binfmt_misc DOSWin` claims the toolchain's MZ-magic APE programs with
wine (wrapper path >90 s vs loader path ~1 s, **byte-identical output**). There is NO APE
step: no `fixupobj`/`objcopy`/`zipcopy`, no launcher, and `-mtinylinux` does not exist in
the pinned release (measured `-mtiny` instead: 216 544 B static ELF, also executes).
`§P1-m0`'s gcc/glibc link STAYS as the diagnostic reference (27 checks rc 0). Historical
gate FROZEN ALL HIT (1328/1328, 190/190, 9/9, 149 rows 0/0, census 16/0/25/0, prose 5);
ZERO oracle; the ledger stays **C380** — native-linking feasibility is DRPLi engineering
evidence, never a DR behaviour claim. Next stage remains **PROPOSED ONLY**: P1-m1 minimal
PL/I console I/O over Cosmopolitan (own PROTOCOL #1 pre-registration + operator
authorization required). Panel: RESULTS §P1-mC.

## 7-7 E2E-54/P1-m1 — Minimal console I/O over the native MIR path (CLOSED 2026-11-10)

The native MIR path now **executes console I/O end-to-end**: `PUT LIST` of a
`FIXED BIN(p,0)` expression and of a printable literal (codes 32..126), and `GET
LIST` of a declared binary scalar, on the default streams. The HIR seam grows
ADDITIVELY (`put_source`/`Put`/`Get` reusing the existing `designator` and
`resolve`; new refusals `HIR-E21`/`HIR-E22` appended to `diagnostic.ml`); the
backend emits used-only console protos before ONE canonical import line plus
`string` items keyed by first distinct literal use, an `Lfail:` fail-fast tail,
and the **WINDOW LAW** post-GET (`env sid := W(p)` — a GET proves exactly the
declared window, nothing wider). The `mir2o` host-import gap (the madc fork
cannot express WEAK imports from MIR text) is closed by a justified ADDITIVE
block in OUR `tools/mir_aot/mir2o.c` (`MIR_load_external` per import item before
`MIR_link`), proven byte-invisible to I/O-free modules: the frozen §P1-m0 object
hashes `78656e6c…`/`3822f777…`/`02c15b1b…` still hold and the no-IO MIR bytes are
untouched (T9 first-hand). The runtime is two small committed C adapters
(`tools/mir_aot/{pli_console.c,console_check.c}`; statuses OK0/EOF1/BAD2/RANGE3/
IOERR4; the backend — not the runtime — closes every PUT with the newline).
Console programs link (Cosmopolitan `tiny`) into plain static x86-64 ELF and
were **judged by EXECUTED BYTES** against independently hand-computed
expectations (§P1-m1.7): `42\n`, `123\n`, `-42\n`, BAD rc 2 / EOF rc 1 / RANGE
rc 3 with EMPTY stdout, and the 33-byte `DR PL/I-80 hello from Cosmo!!\n42\n`;
all three non-vacuity controls (wrong arithmetic, ignored status, EOF-as-success)
failed loudly. The historical compiler (`ocaml/lib`, `ocaml/bin`) and every H
pin stay byte-clean; FULL gate FROZEN ALL HIT; `hir_test` 220 ok with the 11
frozen numbers UNMOVED. PL/I condition designators, `PUT EDIT`, file streams,
character variables and production adoption remain **PROPOSED ONLY** (each needs
its own PROTOCOL #1 pre-registration + operator authorization); console
semantics are DRPLi engineering evidence, never DR claims — the ledger stays
**C380**. Panel: RESULTS §P1-m1.

## 7-8 E2E-54/P1-mD — Native DWARF source debugging of MIR AOT objects (CLOSED 2026-11-11)

The native MIR path is now **source-level debuggable**: `pli80mir -g` writes,
alongside the byte-frozen `.mir`, a line-oriented **sidecar debug map**
(`OUT.mir.p1md` by default; `mir_backend.ml` ADDITIVELY carries the HIR
`st_line`/`ex_line` already in scope on every emit and the `v<sid>`→`sorig`
law — the assembly drops the line, so the default `.mir` bytes move NOWHERE),
and `mir2o --debug-map MAP` folds it into a genuine MIR-produced object. The
map is machine-validated **before any annotation** (magic, sha256 of the exact
`.mir` bytes, func resolution, per-func insn COUNT, per-index OPCODE name,
duplicates, var existence, absolute `file` path); every mismatch is a loud rc 8
with the exact named delta and NO object (rc 7 map-read). The sha256 is
re-implemented in C inside `mir2o.c` and in OCaml in `ocaml/hir/sha256.ml`
(decimal tables); both were cross-checked against Python `hashlib` — the debug
leg itself caught a hex-transcription bug in the hand-copied C `K[56]`
(**a hand-copied constant table is not an oracle**). The cosmo blocker (hop-2:
`ape.lds` folds `.eh_frame` into `.data`) is closed by the PUBLIC read-back
route: `MIR_gen_object_emit` capture → IN-C structural ELF drop of
`.eh_frame`/`.rela.eh_frame` (pure ELF bookkeeping, sh_link/sh_info/st_shndx
re-indexed) → `MIR_object_create`+`MIR_object_read` → fresh debug builder →
`MIR_object_set_debug` BEFORE emit — the builder then writes a NAMED
`.debug_frame`, which every ape.lds keeps. The debug object (M05, sha
`cb263c2c…`, pinned BEFORE linking) links via the pinned Cosmopolitan recipe
and a full gdb 18.1 battery is GREEN: `break M05.pli:4`, hit at `pli80_iorw`,
`print n` = `$1 = 77` (scalar auto homes only), `stepi` on line 4, `info line`
= the exact line-map bounds `+97..+139`, `bt` `#0 pli80_iorw … M05.pli:4 / #1
main`, continue exit 0; controls D-C1/D-C2/D-C3 all fail loudly. The default
(non-`-g`, non-`--debug-map`) paths call NOTHING new — CT2 objects, all MIR/HIR
pins, `hir_test` (220 ok, 11 numbers UNMOVED) and the FULL gate (1328/1328 …
prose 5) stayed FROZEN ALL HIT; the debug `.o` route even reproduces the hop-3
objcopy probe byte-for-byte. Scope ends at single-file, one-function, scalar
non-param auto variables; parameters, aggregates, multi-home/multi-CU, APE and
production adoption are **PROPOSED ONLY** (each needs its own PROTOCOL #1
pre-registration + operator authorization). Zero oracle: this is toolchain
engineering evidence, never a DR claim — the ledger stays **C380**. Panel:
RESULTS §P1-mD.

## 7-9 E2E-54/P1-m2 — Native control flow in the MIR backend (CLOSED 2026-11-12)

The native MIR path now lowers **PL/I `IF/ELSE` and bounded `DO WHILE`**. All
of it lives in `ocaml/hir/mir_backend.ml` (the only compiler file touched in
the whole slice): `Hir.If` emits the §P1-m2.2 shapes (both-arm `b<cc>/jmp` form
and the no-ELSE inverted-guard form) with globally-unique dense labels from a
dedicated `cf_n` counter; each arm lowers in a COPY of the value env and the
`Ljoin` merge is **drop-not-inherit plus sound interval hull** — a variable
assigned on only one path is `None` afterwards, so any later read refuses by
name (CFN1); the window law is never bypassed inside arms. `Hir.While` emits the
PROVEN header/backedge shape with the guard re-evaluated every iteration and the
mandatory `jmp Lh<k>`, accepted ONLY through the exact-integer counted-loop
proof (constant IV init, single monotonic literal step, guard-direction match,
exact exit value `iv0 + c·ceil(...)` inside the declared window; zero-iteration
path exact; every other body-written sid dropped at the header; nested loops
and any other IV write refuse BY NAME). The scientific law of the slice:
**an unprovable loop is never accepted to make a fixture pass** — the six
negative fixtures each pin the named refusal. Non-vacuity is executed, not
argued: flipping `blt`→`bge` or deleting the backedge in disposable MIR copies
makes the NATIVE program execute the predicted wrong bytes (C-M2a prints `1\n`
where `-1\n` is the hand-derived expectation; C-M2b runs exactly one iteration),
observed failing loudly inside the committed runner `tools/mir_aot_cf_test.py`
(83 measured checks; every §P1-m2.5 leg executed byte-exactly on cosmo tiny
static links, plus glibc legs for the no-console fixtures). The §P1-mD sidecar
contract needed no new record type — CF insns ride `st_line` and label rows
record opcode `label` (a defect caught by `mir2o`'s own opcode validation);
gdb breaks on the IF line read both arms' variables and a three-hit breakpoint
on the loop body reads the induction variable 0, 1, 2 on the real machine. The
brief's §2-vs-§9 contradiction was resolved IN ADVANCE in §P1-m2.8 (N1 wording
truth, N2 straight into a positive with value 2, N7 re-pin, 27→32): those four
are the ONLY pre-existing artifacts that moved; every other pin, the CT2
objects, `hir_test` (220 ok, 11 numbers UNMOVED), the console (43) and debug
(23) suites and the FULL gate (1328/1328 … prose 5) stayed FROZEN ALL HIT.
Scope stops at one function, scalar autos, no early/nested RETURN, no
parameters/aggregates/arrays/FILE streams/`ON` conditions, no general fixpoint;
everything beyond is **PROPOSED ONLY**. Zero oracle throughout — ledger stays
**C380**. Panel: RESULTS §P1-m2.

## 7-10 E2E-54/P1-m3 — Native procedure calls in the MIR backend (CLOSED 2026-11-13)

The native MIR path now lowers **calls between procedures** — by-value, by-reference (with real
aliasing) and value-position `Call_e` — in one MIR module per program. All of it still lives in
`ocaml/hir/mir_backend.ml`, the only compiler file touched in the whole slice (18 hops, four
operator amendments, three separately gated milestones). The blanket one-procedure E20 refusal was
replaced by a **selection/validation pass** (entry = `procs` head, `--export` must fold-equal the
entry, entry stays zero-parameter value-returning, cycles refused by DFS, unreached siblings
DROPPED, nested procedures refused, `-g` + multi-proc refused) and a **discovery-order
per-procedure engine** assembled callee-first in post-order with the entry LAST and the ONE
`export` — the callee-first ORDER is a pinned-parser law, not a style choice: the swapped copy
makes `mir2o` fail with `ln 16: undeclared name` (C-M3a, observed loudly). The ABI is the
**HOME-PASS**: every callee formal is accessed through `i64:(v<sid>)`; a bare-name (`A_reference`)
actual passes the caller's entry-hoisted `alloca h<sid>, 8` HOME so the callee's writes are
visible to the caller — executed, not argued, on the differential CALL06B (`2\n7\n`: a value call
and a reference call on the same variable in the same program) — while a by-value actual passes
an entry-hoisted **per-slot** `hv<k>` cell rewritten before every call and never read back, which
is what makes ONE callee legal at mixed-mode sites (CALL10). After each call the designated sids
widen **monotonically** to the declared window (`W(declared)`); nothing is ever narrowed to a
`Some` a call could invalidate (I2/I4), and a by-ref actual whose designation is not definitely
initialized refuses `E19` by name. `Call_e` is admitted ONLY as the whole RHS of an assignment or
the whole `Return` expression, all actuals `A_value`, with the result in a caller-local register
carrying the callee's interval `W(ret-p)` — **no interprocedural value analysis is performed or
claimed anywhere in this slice** (I3), and that honesty is exactly what made the originally
pre-registered `+ literal`-on-a-formal fixtures `E19` (hop 10) and `CALL07/CALL08` unprovable
(hop 15): both were STOP-AND-ATTRIBUTED and resolved by OPERATOR amendments to the PLAN, never by
weakening the window law. The scientific law of the slice is the §P1-m2 one carried forward:
**an unprovable program is never accepted to make a fixture pass** — the eight surviving negatives
pin named refusals, and the three non-vacuity controls are executed in the committed runner
`tools/mir_aot_call_test.py` (86 measured checks; all three observed failing loudly INSIDE, each
producing a valid, linkable, EXECUTING artifact where the law says it must not). Two pre-existing
negative pairs were retired — the ONLY artifacts that moved, both operator-authorized with
named provenance (`CALLN10` → positive at m3b, `CALLN1` → positive at m3c), and `git`'s
rename-rendering of both was disclosed and verified against the tree. Every other pin — all of
`hir/mir-expected/*`, `hir/mir-cf-expected/*`, the debug sidecar and `.o` shas, `hir_test`
(220 ok, 11 numbers UNMOVED), the AOT suites (32/25/43/23/83), the FULL gate (1328/1328 … prose
5) — stayed FROZEN ALL HIT through all three milestones and the close. Scope stops at entry-level
procedures, scalar autos, `D_var` designations, no early/nested `RETURN`, no aggregates/arrays/
`D_elem` (end-to-end unreachable: an array `dcl` dies at the PARSER), no FILE streams, no
`PUT EDIT`, no multi-proc DWARF; everything beyond is **PROPOSED ONLY** — interprocedural
narrowing being the obvious next candidate, and each needing its own PROTOCOL #1
pre-registration plus operator authorization. Zero oracle throughout — this is backend
engineering evidence, never a DR claim; the ledger stays **203 headers ending C380**. Panel:
RESULTS §P1-m3.

## 7-11 E2E-54/P2-DIFF-1 — Cross-backend differential validation (CLOSED 2026-11-13)

The two backends that share this front end — the historical 8080 `codegen.ml`/`rel80.ml` path and
the native `hir/mir_backend.ml` path — were compared for the first time **behaviorally**, on
identical committed source bytes, through the runner `tools/dual_backend_test.py`. Four programs
(a bounded counted `do while`, a three-deep call chain whose only output is in the DEEPEST
procedure, a by-reference aliasing differential, and a value-returning call whose result the
caller prints) produced the **same complete ordered console integer vector on both lanes** as the
hand-derived expectation, in two fresh executions per lane, and the comparator's three
mutation controls (change / delete / permute) plus the empty-expectation attack all rejected
against the real observations.

Two architectural facts this slice establishes, and both are worth keeping in mind for any later
work on the boundary:

1. **The boundary is only where the target ABI starts** — *AMENDED 2026-11-13 at the P2-DIFF-2
   close (PLAN §P2-DIFF-2.5): the sentence below, as originally published, is FALSE and is kept
   here only as the quoted original.* The two lanes share the parser, the
   binder and the HIR, and they differ in nothing that is observable through the *program's own*
   console output; the divergence is entirely in the 8080 instruction/`REL`-record/`?STOPX`
   chain versus the `mir2o`/`i64`/C-driver chain. The differential is therefore a real
   **end-to-end** check of the shared front end + HIR, not of the backends' internals.
   **The corrected statement (verified against the code and §0 of this document):** the two
   lanes share the **parser and the binder** — `Pli80.Parser.parse_source` and the
   `Bind`-driven semantic layer — but they do **not** share the HIR. The 8080 production
   pipeline is `bin/pli80c.ml` → `Parser.parse_source` → `Pli80.Codegen.rows_of` (which calls
   `Bind.bind_program`/`Bind.bind_rows`) → `Codegen.emit_program` → `Rel80.encode`; `pli80c`
   **never constructs a `Hir.program`** — `grep -rn "Hir_build|Hir\.program"` over
   `ocaml/lib` + `ocaml/bin` is EMPTY. The native pipeline is `ocaml/hir/pli80mir.ml` →
   `Parser.parse_source` → `Pli80_hir.Hir_build.build` → `Mir_backend` (the HIR is consumed by
   the **native** MIR backend only). The agreement therefore exercises the shared
   lexer/parser/bind layer and the two *different* lowering paths, and the divergence begins at
   the lowering, not at the ABI.
2. **The two entry mechanisms are independent and that sets the limit of the claim.** The native
   lane needs a `--export`-fold-matching zero-argument value-returning entry and a C driver that
   prints the result to **stderr**; the 8080 lane takes the outermost procedure as `MAIN` and its
   exit convention is CP/M's process status, **not** a PL/I return value. The only common
   observable is the program's own console output, so `driver-return` is excluded from the
   comparison and any case whose sole output is a returned value (D01 `M02`) is
   **NOT-COMPARABLE**, not a failed test. The pilot accordingly says nothing about return
   values, call mechanisms, or full PL/I equivalence.

This is NOT a DR oracle comparison: the historical LINK-80/PLILIB are the linker and runtime, but
the object code on that lane is produced by the reproduction compiler, and `PLI.COM` was never
executed. The evidence is integration evidence — `spec/lab-evidence/e2e54/RESULTS.md` §P2-DIFF-1;
the ledger stays **203 headers ending C380**.

## 7-12 E2E-54/P2-DIFF-2 — Hardened differential runner, integrated programs, and the `Mir_numeric` audit (Stages A+B CLOSED 2026-11-13; Stage C tracked separately)

Two PL/I programs that are **integrated** rather than single-feature — nested `IF`/`ELSE` rule
selection with `+`/`-`/`*`, a void `Call_s` carrying BOTH a by-reference home and a by-value copy,
three `Call_e` results, a counted `DO WHILE` with callee-modified aliasing and per-iteration
output — now run on BOTH backends from the SAME committed bytes (`hir/dif-fixtures/DIF01.pli`,
`DIF02.pli`; pins `hir/dif-expected/*.mir`) and agree with hand-derived expectations written
**before the sources existed**. The runner `tools/dual_backend_test.py` is the artifact of record:
it validates BOTH executions of EACH lane, enforces the pre-registered native process-status law
`rc == 0` (the PL/I return value is a different field and is EXCLUDED from the comparison), and
classifies `infrastructure_failure` separately from `semantic_divergence` — the two things a
verdict must never conflate. The adversarial suite `tools/test_dual_backend.py` (29 checks, no
subprocess, lane functions injected) exists to prove the runner is not vacuous: the three
pre-registered defects were demonstrated by running the suite against the UNMODIFIED runner first
(rc 1, 4 FAIL + 3 missing API groups), and 22/22 comparator controls plus the `MIR2O-FUNC-COUNT`
mutation controls (both executions blocked, the block NAMED) reject on the live path.

Three things this slice adds to the boundary picture:

1. **The shared layer is the parser + binder, not the HIR** — see the §7-11 amendment above. The
   differential therefore validates the shared front end against the two *different* lowerings;
   it says nothing about a shared IR, because there is none.
2. **The numeric domain is the real capability boundary.** The measured intersection that binds
   any program written for this lane pair is: literals inside the MIR window `W(15) = ±16383` (the `32767` this note first quoted is the 8080 `bin15_fits` literal-IMMEDIATE ceiling, a different quantity — corrected by measurement at the Stage-C close, RESULTS §P2-DIFF-2.7); a multiplication
   needs at least one tight-interval operand (a `var*var` with both sides wide REFUSES);
   `pli80c` refuses literal+literal `fixed bin` ADD while literal MINUS literal folds; a `Call_e`
   result widens to `W(15)` and must be re-copied before multiplication; every body-written
   variable is dropped at a loop exit (output must be INSIDE the loop); a bare-name or literal
   actual is BY REFERENCE. These are the same ±(2^(p-1)-1) window laws the native backend
   implements — the interval algebra that enforces them is the subject of the Stage-C extraction
   (RESULTS §P2-DIFF-2.7).
3. **The 8080 console field law is the only cross-lane observable.** The CP/M region is
   right-justified (first field 9 wide, the rest 10, one `CR LF` at the end); the native lane
   prints plain decimal lines. The comparator normalizes to an ordered signed-decimal vector and
   keeps the raw bytes, the transcript and the extracted region separately — cross-lane raw byte
   equality is never required or claimed.

Zero oracle throughout: `PLI.COM` never ran; the 8080 lane's COMPILER is this reproduction, the
LINK-80/PLILIB are Digital Research's linker and runtime. No compiler, golden, pin or claims byte
moved — the historical compiler stays `172595d5…aca281` and the ledger stays **203 headers ending
C380**. Panel: RESULTS §P2-DIFF-2.

## 7-13 E2E-54/P2-DIFF-2 Stage C — the `Mir_numeric` extraction (CLOSED 2026-11-13)

The pure numeric-domain algebra of the native MIR backend moved OUT of `mir_backend.ml` into
`ocaml/hir/mir_numeric.ml`: the declared-precision window, containment, interval display, the
canonical-decimal literal test, the exact `+ - *`/negation endpoint algebra and the control-flow
join hull — nine top-level `let`s plus the `iv` type. The module **imports nothing at all** (not
even `Hir`): the precision is passed as an `int`, the `FIXED BINARY(p,0)` type is never named
there. The backend keeps every diagnostic string, the `win`/`prove` wrappers, the operator
dispatch, the refusal ORDER and the emission, and reaches the algebra through four delegating
`let`s — so the 1900-line body is untouched. The one measured deviation from the original
candidate list: `join_env` could NOT move as a whole, because the environment map is a GENERATIVE
`Map.Make` instance and a second instance would be a distinct type (verified with `ocamlopt`);
only its pure `Some`/`Some` hull moved, as `iv_hull`.

This is a MOVEMENT, not a rule: no numeric acceptance condition was added, widened or narrowed.
The equivalence is proven by the whole frozen panel §P2-DIFF-2.6 (every log `cmp`-identical to
the campaign baseline; `pli80c.exe` `172595d5…aca281`), by re-measuring **all 32 committed
`.mir` pins** from the committed fixtures with the post-extraction compiler (twice each, `stdout
== pin == -o file`), and by a NEW independent driver `mirnumtest.exe` (41563 live checks, four
corrupt controls whose exact stderr bytes are pinned) whose laws are judged by hand-derived
tables plus a second, independently written reference formulation. The driver is driven by the
additive panel tool `tools/mir_numeric_test.py` (41 checks) — the checks were deliberately NOT
added to `tools/hir_test.py`, whose 220-ok count is a frozen panel constant. One honest exception
in the panel: the hir F8 purity check embeds the `ocaml/hir/*.ml` FILE COUNT in its own log line,
so adding two files moves that line (`11 → 13`); the conflict between "byte-identical log" and
"the extraction lives in `ocaml/hir/`" is resolved by DISCLOSING the one-line diff, not by hiding
the new unit in a subdirectory to evade the audit. A PRE-EXISTING latent defect was found and
left alone (invariant 3): `decimal_int` raises on the empty literal text — unreachable from the
compiler (no HIR literal is empty) and byte-for-byte the code the backend held before the
movement; a fix needs its own pre-registration. Commits `f1f3c1ab` + `97c0fa29`; findings, the
four falsifications of the driver's own hand-derived tables, and the `±16383` correction of the
§7-12 capability clause are in RESULTS §P2-DIFF-2.7.

## 7-15 E2E-54/P2-DIFF-4 — call-site interval specialization (CLOSED 2026-11-14)

The return-value summary of §7-14 is now specialized AT THE CALL SITE: `lower_call_e` keeps the
per-actual interval `(cell, iv)` already produced by `lower`, and `Mir_return_summary.
summary_of_actuals` re-evaluates the callee body with the ACTUAL intervals as formal seeds,
subject to the §P2-DIFF-4.2 obligations (arity/order equality, non-empty, `Formal` storage,
`bin_p`, containment in `W(p)`); ANY violation returns `Unknown` and the fallback is the
three-level chain specialized → context-independent → `window cq`, each `Known` guarded by the
existing `in_window full` re-check. The module is ONE shared `eval_body` — no duplicated
traversal; the context-independent semantics of `summary_of` are preserved byte-for-byte
(verified: the 34 pre-existing pins byte-equal, the panel logs `cmp`-identical). The
MONOTONICITY lemma (narrowing a seed can only narrow the result, never turn `Known` into
`Unknown`) gives `specialized ⊆ context-independent` automatically. The admitted capability
grew: a `min`-shaped callee (`if x > k then c = k; else c = x;`) whose context-independent
summary is the full window now admits a narrow actual at a call site (DIF05/DIF06, the
`mul`-window refusals GONE, both lanes BOTH-PASS). The emission law is unchanged — the summary
is a PROOF, never a code-motion; the ABI, the ordering, and the `hv` allocation are untouched.
The 7-14 numbering gap is a DOCUMENTATION GAP (P2-DIFF-3 closed without an arch section), kept
as-is, not renumbered. Commits `d1885505`/`2d78f47b` (module + integration), `32efdff6`/
`001822bb` (the driver), `42dc3086` (the differential cases); full record RESULTS §P2-DIFF-4.
