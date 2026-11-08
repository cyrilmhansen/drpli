# spec/lab-evidence/e2e54/PLAN.md — E2E-54 campaign plan

Campaign **E2E-54 — Backend-Neutral HIR Foundation**. Opened 2026-11-08 in session
`01a1bbbd-252e-74f7-97ac-0a4a0e4b6df6` (fresh chain, renewals 0/12 at session start).

Starting Git reference: `b420fe01c50b3bfd44a20fc63050ece2da485b02` (HEAD at session start;
verified first-hand). E2E-53 is CLOSED; nothing in this campaign reopens or modifies it.

**Baseline VERIFIED first-hand at session start (2026-11-08), not copied from the brief:**

- `git rev-parse HEAD` = `b420fe01c50b3bfd44a20fc63050ece2da485b02` ✓
- `dune build` rc = 0; `sha256sum _build/default/bin/pli80c.exe` =
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` ✓ (== armed fingerprint)
- Kept gate log `build/gate-e53p4-reg.log`: `e2e gate: 1328 byte-exact / 0 fail of 1328`,
  `negative panel clean (190/190 refused)`, `divergence panel 9/9`, `coverage_check: 149 rows,
  0 errors, 0 warnings`, census `{EXACT 16, DIFFERS 0, REFUSED 25, NO_ORACLE 3}`, prose 5 clean ✓
- `spec/INVENTORY.txt`: 1518 non-comment rows = 1328 specimen + 190 refusal ✓
- `spec/CLAIMS.md`: 203 `^## C` headers; ledger ENDS **C380** ✓
- Working-tree dirt: `HANDOFF.md`/`PROGRESS.md` carry the prior session's stale auto checkpoint
  block (g608, unattested; committed HEAD holds attested g606) and `handoff.config.json` carries
  the operator's edit (cap 12, workingContextWindow 145000) — **config NEVER staged**.

## §0 — Operator brief (authoritative authorization)

Received verbatim in the operator's E2E-54 launch message, 2026-11-08. Reproduced below with
**one mechanical transformation**: the brief's own `##`/`###` headings are demoted to `###`/`####`
so they nest under this section; no word, number, path or constraint is otherwise altered. This §0
is the authoritative scope statement for the campaign; if any later section of this PLAN appears
to conflict with it, §0 wins and this PLAN is the thing to correct.

> ### 0. Operator brief — authoritative authorization
>
> The operator authorizes **E2E-54/P0**, a new architectural campaign to prepare DRPLi for
> future alternative code generators, including MIR and potentially WebAssembly.
>
> This is a deliberately limited architecture-and-prototype phase.
>
> **The primary objective remains the byte-exact reproduction of Digital Research PL/I-80 v1.4.**
>
> E2E-53 is CLOSED. Do not reopen or modify its scientific results.
>
> Starting Git reference:
>
> `b420fe01c50b3bfd44a20fc63050ece2da485b02`
>
> Verified baseline:
>
> - Compiler fingerprint: `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`
> - Whole-file exact specimens: 1328/1328
> - Negative panel: 190/190
> - Divergence panel: 9/9
> - Coverage contracts: 149, SUPPORTED 99
> - Historical corpus: 16 EXACT / 25 REFUSED / 3 NO_ORACLE
> - Last scientific claim: C380
> - Last full gate: `build/gate-e53p4-reg.log`, RC 0
> - Handoff chain: 2/12 at the last verified checkpoint
>
> Verify these from the actual repository and logs; do not blindly assume they remain current.
>
> #### First action — preserve this authorization
>
> Read `AGENTS.md`, `PROTOCOL.md` and the active `PROGRESS.md` / `HANDOFF.md`.
>
> Create:
>
> `spec/lab-evidence/e2e54/PLAN.md`
>
> Insert this operator brief as its authoritative §0, preserving its meaning, scope and constraints.
>
> Then preregister the P0 audit, prototype, tests and falsification criteria in §P0.
>
> Commit the plan before modifying compiler sources.
>
> This removes the previous Handoff blocker: the E2E-54 authorization is now explicit.
>
> ### 1. Architectural objective
>
> Prepare a clean boundary between PL/I language semantics and physical code generation.
>
> The intended long-term architecture is:
>
> ```text
>                 PL/I source
>                      |
>                Lexer / Parser
>                      |
>                     AST
>                      |
>           Shared semantic analysis
>                      |
>                   Typed HIR
>                      |
>          +-----------+-----------+
>          |           |           |
>     Historical     MIR        Other
>     8080 backend   backend    backends
>          |           |           |
>        REL-80     native AOT   WASM/other
> ```
>
> **This diagram represents the long-term destination, not the required P0 implementation.**
>
> During P0, retain the existing historical pipeline unchanged:
>
> ```text
> Parser
>   → existing Bind/Codegen
>   → Rel80.encode
>   → byte-identical .REL
> ```
>
> Construct HIR through a separate opt-in path.
>
> Do not refactor the historical backend to consume HIR in this phase.
>
> ### 2. Audit existing architecture first
>
> Inspect the actual implementations:
>
> - `ocaml/lib/ast.ml`
> - `ocaml/lib/bind.ml`
> - `ocaml/lib/ir.ml`
> - `ocaml/lib/codegen.ml`
> - `ocaml/lib/rel80.ml`
> - `ocaml/bin/pli80c.ml`
>
> Map the responsibilities currently intertwined in Bind and Codegen:
>
> 1. Name resolution and lexical scopes.
> 2. Type interpretation.
> 3. Numeric conversions and expression typing.
> 4. Addressable values and aliasing.
> 5. Procedure signatures and calls.
> 6. Control-flow semantics.
> 7. Storage allocation and layout.
> 8. DR-specific runtime ABI.
> 9. Intel 8080 instruction selection.
> 10. LINK-80 relocation and record sequencing.
>
> Produce a concrete dependency map with actual functions, modules and call sites.
>
> Classify each responsibility as:
>
> - Semantically reusable.
> - Reusable after a small extraction.
> - Historical DR-specific.
> - Unknown or not independently characterized.
>
> Do not confuse a known DR code-generation law with a universally valid PL/I semantic rule.
>
> #### Existing IR warning
>
> `ocaml/lib/ir.ml` already exists, but models Digital Research's historical `$V` intermediate
> representation.
>
> It is **not** the new backend-neutral HIR.
>
> Do not rename, replace or repurpose it.
>
> Use a distinct module such as `Hir`.
>
> ### 3. Define a minimal HIR
>
> Create a typed, target-independent representation for a small, demonstrable PL/I subset.
>
> The HIR should carry:
>
> - Stable symbol identifiers.
> - Lexical scopes and source positions.
> - Procedure signatures.
> - Semantic types with precision and scale.
> - Typed constants.
> - Variable references and addressable expressions.
> - Explicit conversions.
> - Assignment and arithmetic operations.
> - Conditions and control flow.
> - Calls and returns.
> - Explicit side-effect and evaluation-order information.
>
> Avoid premature SSA.
>
> Do not impose MIR instruction semantics on the HIR.
>
> Do not represent unsupported language forms as silently accepted generic nodes.
>
> A typed diagnostic is preferable to guessed semantics.
>
> #### Semantic types versus physical representation
>
> Keep these concepts separate.
>
> Example:
>
> ```text
> Language type:
>     FIXED DECIMAL(9,2)
>
> Possible physical representations:
>     DR packed decimal
>     libmpdec / modern decimal
>     backend-specific storage
> ```
>
> The semantic type does not prescribe the storage format.
>
> Likewise, CHARACTER VARYING is a semantic string type, not intrinsically the historical
> length-byte-plus-capacity representation.
>
> The original DR layout remains authoritative only for historical object reproduction.
>
> ### 4. Target semantic profile
>
> Define a small explicit target-profile abstraction.
>
> It should eventually describe:
>
> - Default integer precision.
> - Numeric conversion and rounding rules.
> - Arithmetic overflow behavior.
> - Floating-point semantics.
> - Character encoding assumptions.
> - Target-specific semantic restrictions.
>
> Distinguish:
>
> **Known historical behavior:** supported by oracle evidence.
>
> **Language-level behavior:** supported by explicit language specification or established
> semantic rules.
>
> **Unknown behavior:** requires a decision or additional measurement.
>
> Never invent a historical rule merely to populate a profile field.
>
> Use explicit unknown or unsupported status where necessary.
>
> Physical ABI choices belong to the backend, not the semantic profile.
>
> Do not attempt to complete all target profiles during P0.
>
> ### 5. Reuse the existing semantic authority
>
> **Do not implement a second independent PL/I binder.**
>
> This requirement is fundamental.
>
> A standalone HIR parser that independently resolves names, checks scopes and invents types
> would create a second compiler requiring its own compatibility effort.
>
> Instead:
>
> 1. Identify semantic information already produced by Bind.
> 2. Determine what can safely be exposed through a read-only adapter.
> 3. Extract minimal reusable semantic helpers only when compatibility can be demonstrated.
> 4. Keep DR-specific frame offsets, storage rows and relocation assumptions out of HIR.
> 5. Record unresolved dependencies as migration tasks.
>
> If the current binder API is too tightly coupled to physical layout, a small adapter is
> acceptable for the P0 subset.
>
> It must not become a duplicate semantic implementation.
>
> Any proposed shared-binder refactor must be incremental and independently regression-tested.
>
> ### 6. Executable P0 prototype
>
> Implement a small, end-to-end HIR construction path.
>
> Suggested starting subset:
>
> - Scalar declarations.
> - FIXED BINARY literals and variables.
> - Addition, subtraction and multiplication.
> - Assignment.
> - IF/ELSE.
> - A simple loop.
> - Internal procedure calls and returns where semantic reuse permits.
>
> Choose a subset that genuinely exercises resolution, typing and control flow.
>
> Do not implement broad syntax support using placeholder semantics.
>
> A complete three-statement example is more valuable than hundreds of syntactic constructors
> with no semantic guarantees.
>
> #### Observable output
>
> Provide a deterministic textual HIR dump.
>
> Prefer a separate CLI such as `pli80hir` rather than altering the standard compiler invocation.
>
> The dump must expose stable identifiers, types, scopes and operations.
>
> Avoid nondeterministic addresses, hash-table iteration, process identifiers and timestamps.
>
> For unsupported constructs, produce deterministic diagnostics and a nonzero return code.
>
> #### Test corpus
>
> Create at least:
>
> 1. An arithmetic-assignment fixture.
> 2. A branch/loop fixture.
> 3. A fixture testing variable shadowing or nested lexical scope.
> 4. A procedure call/return fixture, if supportable through existing semantic information.
> 5. A negative fixture proving unsupported constructs do not silently lower.
>
> Use repository fixtures when suitable.
>
> Compare textual HIR dumps against committed expected results.
>
> Do not change the original source files or golden objects.
>
> ### 7. Backend interface
>
> Specify a minimal interface conceptually similar to:
>
> ```ocaml
> module type BACKEND = sig
>   type artifact
>
>   val compile :
>     profile:Target.profile ->
>     Hir.program ->
>     (artifact, Diagnostic.t list) result
> end
> ```
>
> Adapt the actual type definitions to the measured architecture.
>
> The interface should not assume ELF, REL-80, a specific register set, or MIR-specific IR nodes.
>
> It must leave room for:
>
> - Native AOT code generation.
> - Library/shared-object generation.
> - WASM output.
> - An interpreter or alternative backend.
>
> Do not build a plugin registry or implement these backends now.
>
> A documented interface with compile-time tests is sufficient for P0.
>
> ### 8. MIR integration study
>
> Use the existing independent repository:
>
> `cyrilmhansen/mir-madc-aot-lab`
>
> Consult its verified findings when accessible.
>
> The future expected path is:
>
> ```text
> Typed HIR
>    ↓
> MIR-specific lowering
>    ↓
> MIR modules and functions
>    ↓
> MIR/MADC AOT
>    ↓
> Native object / executable / shared library
> ```
>
> Identify expected integration points:
>
> - Scalar values and conversions.
> - Pointer/reference semantics.
> - Procedure signatures and calling conventions.
> - Global and local storage.
> - Runtime-library calls.
> - External symbol resolution.
> - AOT object generation.
>
> Distinguish compilation into an independently linkable native object from loading a persisted
> MIR object through MIR's own loader.
>
> Do not assume these routes have identical relocation behavior.
>
> **P0 does not implement MIR code generation.**
>
> Do not add MIR or MADC as a dependency.
>
> Do not modify the MIR/MADC laboratory.
>
> ### 9. Validation and falsifiers
>
> P0 must prove that the new HIR path is observational and non-invasive.
>
> Mandatory checks:
>
> **Historical preservation**
>
> - Default compiler CLI unchanged.
> - Compiler behavior unchanged.
> - Complete byte-tier gate RC 0.
> - No historical golden rewritten.
> - No inventory or census modification.
> - No new DR C-claim.
> - No COVERAGE promotion for HIR-only work.
>
> **HIR correctness**
>
> - Deterministic textual dumps.
> - Stable symbol identities.
> - Correct lexical resolution on the selected fixtures.
> - Explicit type and conversion representation.
> - Explicit rejection of unsupported constructs.
> - No 8080 relocations or DR memory offsets in portable HIR nodes.
>
> **Architectural separation**
>
> - Historical Codegen does not depend on HIR.
> - HIR does not depend on Rel80.
> - HIR does not depend on MIR.
> - The prototype does not introduce a second independent resolver/type checker.
> - Target-independent semantics and target-dependent layout are not conflated.
>
> If a requirement cannot be achieved without a substantial compiler refactor, document the
> blocker and reduce P0 scope rather than compromising historical parity.
>
> No new oracle calls are planned for P0. Any new DR behavior question remains UNMEASURED and
> belongs to a separately preregistered experiment.
>
> ### 10. Deliverables
>
> Produce:
>
> - `spec/lab-evidence/e2e54/PLAN.md`
> - `spec/lab-evidence/e2e54/RESULTS.md`
> - `docs/architecture/backend-boundary.md`
> - Minimal HIR module(s).
> - Deterministic HIR dump executable.
> - Focused HIR fixtures and expected outputs.
> - Minimal backend-interface definition or executable type-checking witness.
> - Test command(s) and direct results.
> - A staged migration roadmap.
>
> The architecture document must identify:
>
> 1. What may already be shared.
> 2. What is DR-specific.
> 3. What can be safely extracted next.
> 4. What must not be refactored yet.
> 5. What MIR needs from the future semantic layer.
>
> ### 11. Scope and autonomy
>
> P0 authorizes architecture analysis, a limited HIR prototype and its tests.
>
> It does **not** authorize:
>
> - A wholesale Codegen refactor.
> - Replacing the historical compiler pipeline.
> - Implementing MIR code generation.
> - Implementing a WASM backend.
> - PLILIB reimplementation.
> - Changing GOAL.md.
> - Rewriting previous scientific evidence.
> - Mass cleanup of Handoff documentation.
>
> Follow the repository's existing preservation and Handoff rules.
>
> Use explicit-path commits. Never stage `handoff.config.json`. Never push.
>
> Continue across safe Handoff renewals when available.
>
> At P0 completion, run the full compile-tier gate, close RESULTS, record the architectural
> decisions, finalize the checkpoint and report.
>
> **Do not automatically begin E2E-54/P1: the proposed migration roadmap requires operator review.**
>
> ### Success criterion
>
> A minimal, deterministic and tested backend-neutral HIR, reusing existing semantic knowledge
> where possible, with a documented backend contract and no regression whatsoever in historical
> `.REL` reproduction.
>
> The purpose is to make later MIR integration straightforward — without prematurely transforming
> DRPLi into a different compiler.
>
> **Operator authorization: E2E-54/P0 is approved. Preregister the campaign and proceed.**

## §P0 — Pre-registration (committed BEFORE any compiler-source modification)

**Type of work:** architecture analysis + isolated prototype + tests. **ZERO oracle calls** are
planned or authorized for P0. **ZERO bytes of `ocaml/lib/codegen.ml`, `ocaml/lib/rel80.ml`,
`ocaml/lib/bind.ml`, `ocaml/lib/ir.ml`, `ocaml/lib/lexer.ml`, `ocaml/lib/parser.ml`,
`ocaml/lib/ast.ml`, `ocaml/lib/token.ml`, `ocaml/lib/source.ml` and `ocaml/bin/pli80c.ml` are
modified in P0** — new modules are added alongside; the historical pipeline is not rewired.
No new claim goes into `spec/CLAIMS.md` (no oracle experiment runs; per PROTOCOL #1 a
non-measurement cannot create a claim). No COVERAGE row is touched. No golden, inventory,
census, probe source or `artefacts/` file is touched.

### P0.1 Work order (exact order)

1. **(this commit)** `PLAN.md` §0 + §P0 pre-registration.
2. **Architecture audit (read-only).** Produce the dependency map of brief §2 — the ten
   responsibilities, each mapped to concrete functions/modules/call sites with measured line
   anchors, classified `reusable` / `reusable-after-small-extraction` / `dr-specific` /
   `unknown`. Written into `docs/architecture/backend-boundary.md` (draft) — never into prose
   that restates claim-level DR behaviour as semantic law (PROTOCOL: a DR code-gen law is not a
   PL/I semantic rule).
3. **HIR surface design** (§P0.3 below) — types only, no lowering, committed.
4. **Adapter + lowering for the P0 subset** (§P0.4), reusing `Bind` output; deterministic
   dumper; `pli80hir` CLI (§P0.5).
5. **Fixtures + expected dumps + tests** (§P0.6, §P0.7).
6. **Validation + falsifiers** (§P0.8), full compile-tier gate.
7. **Close-out:** RESULTS.md, final architecture doc, migration roadmap (PROPOSED, operator
   review required — P1 is NOT started), durables + guard checkpoint.

### P0.2 New file set (explicit paths)

- `ocaml/lib/hir.ml` — HIR types + dumper (new).
- `ocaml/lib/diagnostic.ml` — typed diagnostics (new).
- `ocaml/lib/target.ml` — minimal target-profile abstraction (new).
- `ocaml/lib/backend.ml` — `module type BACKEND` + compile-time witness types (new).
- `ocaml/lib/hir_build.ml` — the read-only adapter: AST + `Bind.prog_layout` → HIR for the P0
  subset, loud refusal otherwise (new).
- `ocaml/bin/pli80hir.ml` — CLI dump tool (new); `ocaml/lib/dune`, `ocaml/bin/dune` gain the
  new units/executables (build-file change only, no historical unit altered).
- `hir/fixtures/*.pli` + `hir/expected/*.txt` — P0 fixture corpus and expected dumps (new
  directory; keeps `probes/` free for oracle specimens; ids `H01..` verified unused: no file or
  inventory row matches `H0`/`h0` in `probes/`, `spec/INVENTORY.txt`).
- `tools/hir_test.py` — fixture runner (new; compares dumps, checks determinism, rc, refusal
  contract). Committed only at step 5.

### P0.3 HIR design commitments (fixed before coding)

- Symbols: each declared entity gets a stable integer `sid` assigned by deterministic pre-order
  traversal of the bind plan; dumps print `sid`, lowered name, declaring scope id, source line.
- Scopes: `program`, one nested scope per procedure block, source position on every node.
- Types (`Hir.ty`): semantic only — `FIXED BINARY(p,s)` / `FIXED DECIMAL(p,s)` / `CHAR(n[,varying])`
  / `BIT(n)` / `LABEL` / pointer-of — carried as precision+scale, with **no** byte-size, frame
  offset, `bytes_of` value, DR pool position or relocation in any HIR node. `Bind.rt` is mapped
  to `Hir.ty` explicitly; `RTbased`/`RTstruct*`/`RTentry` shapes outside the subset are refused.
- Statements: `let` (scalar declaration), `assign`, `if`, loop (the measured shape: pre-test
  `DO WHILE` or the `DO i = a TO b` form actually implemented — decided in the audit, recorded
  here as: exactly one loop form in P0), `call` (internal procedure, argument list ordered =
  evaluation order), `return`, `stop`.
- Expressions: `const` (typed), `var` (resolves to `sid`; addressable flag explicit), arithmetic
  `+ - *` with the **result type computed by the same type-interpretation functions Bind already
  uses** (`rt_of_basic`/precision-scale arithmetic if reusable — otherwise the gap is recorded,
  NOT reinvented), explicit `convert` nodes where operand type ≠ target type.
- Evaluation order / side effects: expression nodes carry explicit ordering; call arguments
  evaluate left-to-right in the dump order.
- Unsupported forms: `Diagnostic` with a stable code (`HIR-E<nn>`) and source position; the CLI
  exits nonzero and prints NO partial HIR on any diagnostic. No "generic node" escape hatch.
- NO SSA, no MIR-shaped nodes, no continuation objects, no register mentions anywhere in the IR.
- `ir.ml` is untouched, unreferenced by HIR code, and never renamed.

### P0.4 Semantic-reuse rule (fundamental, brief §5)

`Hir_build` consumes exactly two things: the parsed `Ast.block` and
`Bind.bind_program : Ast.block -> Bind.prog_layout` (+ the existing exported helpers it calls —
e.g. `Bind.rty_str`, `Bind.resolve_type`, `Bind.pl_l`). It performs **no independent name
resolution, no independent scope walk, no independent type invention**: any identifier reaching
HIR must have been resolved through a Bind-produced structure (`pl_procs`, `pl_rows`,
`pl_exts`). Testable form of the rule (falsifier F6 below): `hir_build.ml` contains no
`List.assoc`-style re-resolution over raw `Ast` names that bypasses bind layout rows — the only
name→meaning channels are bind outputs. If a needed fact is absent from bind, P0 records a
migration task; it does not recompute it independently.

### P0.5 CLI contract

`pli80hir INPUT.PLI` → deterministic HIR dump on stdout, rc 0; on unsupported construct:
diagnostic(s) on stderr, rc 2, **no** stdout output. Usage error rc 2. The default compiler
invocation (`pli80c`) is byte-untouched — its source file is in the zero-edit set.

### P0.6 Fixtures (minimum five, brief §6)

1. `H01` arithmetic assignment: `dcl x,y fixed bin(15); x = y + 3*2;` — typed consts, explicit
   conversion witness if any.
2. `H02` branch + loop: IF/ELSE + the one P0 loop form.
3. `H03` shadowing: outer and inner `BEGIN`/procedure declaring the same name — distinct sids,
   correct scope attribution on every reference.
4. `H04` procedure call/return: internal proc with formals + `RETURN`/result usage **only if**
   the bind layout carries the needed signature facts (it does: `pl_ret`, `pl_rows`, formals);
   otherwise downgraded to the no-formal case and recorded.
5. `H05` negative: a construct outside the subset (e.g. array reference, PUT statement,
   FIXED DECIMAL arithmetic — whichever the audit shows is genuinely un-lowered) must refuse
   with the named diagnostic, rc 2, zero stdout.

Expected dumps committed under `hir/expected/` only after being produced, reviewed line by line
against the design commitments above, and committed together with the fixtures.

### P0.7 Test commands (the P0 regression command set)

- `cd ocaml && eval "$(opam env)" && dune build` — rc 0, ZERO `Error` lines.
- `python3 tools/hir_test.py` — all fixtures byte-match expected dumps; determinism (each dump
  produced twice, `cmp` equal); negatives rc 2 + zero stdout; grep assertions for the
  separation rules (F7–F9).
- `python3 tools/e2e_gate.py` — FULL compile-tier gate, rc 0.
- Direct fingerprint check: `sha256sum ocaml/_build/default/bin/pli80c.exe` unchanged (§P0.8 F1).

### P0.8 Falsification criteria (each is a STOP-and-fix gate, not a number to force)

- **F1 Historical binary invariance:** with only the new units added, `pli80c.exe` sha256 must
  remain `172595d5…` (OCaml/dune link only referenced units). If it MOVES, attribute first-hand
  (which module entered the link) before any conclusion; a moved binary whose REL outputs are
  nonetheless 1328/1328 is recorded as link-scope drift, NOT celebrated, and the arm is
  restructured (separate library dir) until invariance holds.
- **F2 Byte-tier gate rc 0** with counts EXACTLY 1328/1328, 190/190, 9/9, coverage 149 rows 0/0,
  census 16/0/25/0, prose 5. Any movement = historical regression = STOP, revert the new
  modules' build wiring, diagnose. (Prediction: zero movement — no panel member changed.)
- **F3 Goldens/inventory/census/claims/coverage untouched:** `git status --porcelain golden/
  spec/ probes/ artefacts/ manuals/ extracted/ references/ oracle/disks/` shows no modification
  (new `spec/lab-evidence/e2e54/` files are additions). `spec/CLAIMS.md` header count stays 203.
- **F4 Determinism:** running each fixture dump twice in one process and across two fresh
  processes yields identical bytes; no timestamps, pids, pointer values or hash-map iteration
  order appear (grep dump for `[0-9a-f]{6,}` address shapes and verify every hex-looking token
  is a documented value, not an address).
- **F5 Stable identities:** sids depend only on source order — reordering two independent
  declarations in a fixture renumbers deterministically and is shown by fixture diff, not a bug.
- **F6 No second binder:** the P0.4 rule holds; audit grep of `hir_build.ml` resolution paths.
- **F7 Separation (build graph):** `codegen.ml`, `rel80.ml`, `pli80c.ml` contain zero references
  to `Hir`/`Hir_build`/`Target`/`Diagnostic`/`Backend`; `dune build` keeps `pli80c.exe`
  self-contained as before (implied by F1).
- **F8 HIR purity:** `hir.ml`/`hir_build.ml` contain zero references to `Rel80`, `Codegen`,
  `Bind.bytes_of`/frame-offset values, 8080 mnemonics or register names; `Hir.ty` carries no
  byte-size field.
- **F9 Negative silence:** every unsupported fixture refuses loudly; NOTHING is emitted to
  stdout by a refusing run (silent partial lowering is the primary failure mode).

### P0.9 Target profile scope

`Target.profile` in P0 is deliberately minimal: named record with the brief-§4 fields; the
`dr-pli80-v1-4` profile is populated ONLY with fields already backed by existing claims/manual
evidence (every populated field cites its claim id or marks `[TBD]`); a `generic-32bit` profile
is sketched with language-level or explicitly UNKNOWN fields. No new measurements; no invented
historical rules.

### P0.10 MIR study scope

Read-only: consult `cyrilmhansen/mir-madc-aot-lab` findings **if accessible** in this
environment (check without network first; if inaccessible, record `[TBD — lab not reachable]`).
Deliverable: integration-point list in the architecture doc. NO dependency, NO code, NO
modification to the lab.

### P0.11 Expected outcomes (pre-registered, falsified-not-forced)

- All gate/panel numbers frozen (F2/F3). Refusal of every non-subset construct on the five
  fixtures. A passing `tools/hir_test.py`. RESULTS.md records every falsifier with its measured
  value, and every requirement NOT achieved is documented as a blocker with reduced scope, per
  brief §9. The migration roadmap is written as PROPOSED and the session stops before P1.

### Dashboard

| slice | status | gate log | notes |
|---|---|---|---|
| P0 | OPEN (pre-registered) | (owed: `build/gate-e54p0-reg.log`) | zero oracle |
