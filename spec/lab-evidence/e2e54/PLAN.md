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
| P0 | **CLOSED 2026-11-08** (hop 4) | `build/gate-e54p0-reg.log` (rc 0, frozen counts) | zero oracle; RESULTS.md §1–§8; P1 NOT authorized |

---

## §P1-b — Pre-registration: Semantic Environment Projection (committed BEFORE any code change)

**Authorized by the operator 2026-11-08** (message reproduced VERBATIM as §P1-b.0 below).
Campaign slice **E2E-54/P1-b** — roadmap item 2 of RESULTS §6, promoted to an authorized
phase by that explicit operator decision. Type of work: **backend architecture, ZERO oracle
calls** (none planned or authorized). Starting reference:
`aaf295f0257659c4b3bd8d070bd14a306cc36780` (verified first-hand at session start:
`dune build` rc 0; `pli80c.exe` sha256 `172595d5…` == P0 baseline; `tools/hir_test.py`
rc 0 H01–H05; `ocaml/lib`+`ocaml/bin` byte-clean).

P1-a (subset extension), P2, any MIR backend, and any historical-compiler refactor are
explicitly NOT started or authorized by this slice.

### P1-b.0 Operator authorization (verbatim)

> ## DRPLi — E2E-54/P1-b: Semantic Environment Projection
>
> ### Operator authorization
>
> E2E-54/P0 is CLOSED. The operator authorizes **P1-b: a read-only Semantic_env projection over the existing binder**.
>
> Starting reference: `aaf295f0257659c4b3bd8d070bd14a306cc36780`.
>
> This is a ZERO-oracle, backend-architecture campaign.
>
> Do not start P1-a, P2, a MIR backend, or a historical compiler refactor.
>
> ### Objective
>
> Make semantic information produced by the existing Bind implementation available through one coherent, typed, backend-independent interface.
>
> Reduce the number of places where HIR construction must reconstruct symbol tables, lexical lookup, procedure relationships and type information.
>
> The new interface must remain a projection of existing semantic evidence, not a competing binder.
>
> ### Step 1 — Preregister and audit
>
> Read: `AGENTS.md`, `PROTOCOL.md`, `spec/lab-evidence/e2e54/PLAN.md` and `RESULTS.md`, `docs/architecture/backend-boundary.md`, `ocaml/hir/hir_build.ml`, Existing `Bind.prog_layout`, `proc_layout`, `bind_rows` and associated helpers.
>
> Preregister P1-b in `spec/lab-evidence/e2e54/PLAN.md` and commit before code changes.
>
> Identify every current lookup, mapping or reconstruction performed by `Hir_build`. Classify each as: (1) Direct projection of bind-produced data. (2) Necessary lexical organization using facts from AST and Bind. (3) Duplicate semantic resolution or typing. (4) Unknown or unsupported.
>
> Do not claim that Bind provides a fact which is actually reconstructed from syntax.
>
> ### Step 2 — Implement Semantic_env
>
> Prefer an isolated module: `ocaml/hir/semantic_env.ml`. This module is transitional: it is consumed by the independent HIR path, while the historical compiler remains unchanged.
>
> Provide a minimal typed interface for: stable symbol identity; declaration type and source position; symbol ownership and scope; scoped name lookup; procedure identity and signatures; formal parameter identity and type; parent/child procedure relationships.
>
> Build the projection deterministically from the parsed AST and the existing Bind result. Keep the original Bind layout authoritative. Exclude physical offsets, frame sizes, relocation records, data-pool addresses and 8080-specific storage details from the public semantic interface. Do not perform a second independent declaration analysis. Do not duplicate existing Bind type-interpretation functions. Where Bind does not expose sufficient information, return a typed unsupported/unknown result or document the missing capability. Do not silently infer it.
>
> ### Step 3 — Migrate Hir_build
>
> Make `Hir_build` consume `Semantic_env` for supported symbol and procedure lookups. Eliminate redundant local tables and lookup code only where equivalent behavior is demonstrated. Avoid moving code merely to rename it: the objective is a stable semantic contract, not a cosmetic refactor. Preserve deterministic symbol identifiers and dump ordering. Retain all existing HIR diagnostics unless an explicitly documented bug is corrected. Do not widen the supported PL/I language subset during P1-b.
>
> ### Step 4 — Semantic authority tests
>
> Test against the actual Bind-produced facts, not merely the text of existing HIR dumps. Include: declaration order and symbol identity; local versus enclosing-scope references; procedure/formal relationships; shadowed names; unresolved names; unsupported declaration types; Bind/AST inconsistencies or missing information. Re-run H01–H05 unchanged. Add targeted fixtures for newly exposed semantic-environment behavior where necessary, without promoting additional HIR language constructs. Assert that every successfully resolved HIR identifier can be traced to an existing bind-produced authority. A wrapper that internally reimplements the same independent name-resolution rules is not sufficient.
>
> ### Step 5 — Keep unmeasured typing explicit
>
> Audit the current FIXED arithmetic rule: addition/subtraction `max(p1,p2)+1`; multiplication `p1+p2`; profile ceiling and clamping. `Target.fixed_arithmetic_typing` currently does not contain a verified DR intermediate-typing rule. Preserve the distinction between: language-level proposed typing; prototype normalization; oracle-backed historical behavior. Do not promote the current arithmetic rule to verified DR semantics. Do not change arithmetic typing or expected HIR dumps merely to simplify the new API. If a structural issue is found, document it for a separate phase.
>
> ### Step 6 — Regression and separation gates
>
> Mandatory: `dune build` RC 0; `tools/hir_test.py` RC 0; all existing HIR outputs and diagnostics unchanged unless explicitly adjudicated; fresh historical binary SHA-256 equal to the P0 baseline `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`; full `tools/e2e_gate.py` RC 0; historical parity 1328/1328; negative panel 190/190; divergence panel 9/9; no change to golden objects, historical sources, claims, coverage, inventory or census. Do not introduce references from the historical compiler into the new HIR modules. Do not modify `ocaml/lib/` or `ocaml/bin/`. No oracle calls, no MIR dependency, no push.
>
> ### Step 7 — Close and report
>
> Deliver: a documented `Semantic_env` API; a migrated HIR construction path; explicit semantic-authority tests; a before/after dependency map; all measured test results; a list of semantic facts that Bind still does not expose; a proposed P1-a subset-extension order. Update `docs/architecture/backend-boundary.md`, `spec/lab-evidence/e2e54/RESULTS.md` and the durable Handoff documents. Commit scoped changes, verify the checkpoint, and close P1-b.
>
> **STOP after P1-b closure. Do not begin P1-a automatically.**
>
> Success means that HIR construction consumes a clearer, testable projection of the existing binder, with less duplicated semantic logic and no change to historical compilation.
>
> **Operator decision: E2E-54/P1-b is authorized. Preregister and proceed.**

### P1-b.1 Audit — every lookup / mapping / reconstruction in `Hir_build` at `aaf295f0`

Classified per the brief. Classes: **[P]** direct projection of bind-produced data;
**[O]** necessary lexical organization using facts from the AST and Bind (organization the
interface must own, NOT claimed as a Bind fact); **[D]** duplicate semantic resolution or
typing; **[U]** unknown / unsupported. Anchors are the file as committed at the starting
reference (780 lines).

| # | Site | Operation | Class |
|---|---|---|---|
| 1 | `build` | `Bind.bind_program blk` — THE single semantic-authority call | authority (not a reconstruction) |
| 2 | `build` | `Bind.top_is_proc blk` + `plan.pl_top` → main-block procedure identity; main name enters `procs_by_name` only when bind itself laid the top block out as a procedure | [P] |
| 3 | `check_top_authority` | consistency check: every `Bind.bind_rows blk` name must appear in `pl_top.pl_rows` (mirror of codegen `rows_of`; two bind views, no resolution) | [P] guard |
| 4 | `rows_of_block` | `Bind.bind_rows blk` → `(lower name, rt, auto)`; **the physical offset component is dropped at this first touch** | [P] |
| 5 | `register_block` `dup_free` | refuse if bind produced two rows with the same name for one block (guard over bind data; a defensive witness, no fixture reaches it — see §P1-b.4 H07 measurement) | [P] guard |
| 6 | `find_dcl` | name → (source spelling, declare-statement line) through `Bind.frame_decls` (bind's OWN flattener) keyed by `Bind.pl_l` | [P] (bind owns both the flattening and the key policy; the scan itself is trivial deterministic lookup) |
| 7 | `register_block` formal set | lowercased `binfo_formals` (from AST `bparams` via `Bind.pl_l` at the call site) — `storage = Formal` is derived from **AST parameter-list membership**; TYPE and row existence stay bind facts | [O] (also a redundant double `String.lowercase_ascii` over an already-`pl_l` list — removed in migration; behaviour identical) |
| 8 | sid / scope / pid allocation in `register_block` + `build` | pre-order ids; WITHIN a block the order is bind's row order (bind measurement, hop 1); the block-tree WALK order is AST nesting order | [O] (the identity scheme is the interface's contract; it must stay deterministic and is NOT claimed to be a Bind fact — Bind has no sid/scope/pid) |
| 9 | storage Auto vs Static | the `auto` flag of the bind row | [P] |
| 10 | `ty_of_rt` | `Bind.rt → Hir.ty` map; only `RTbin p → Fixed_bin(p,0)` accepted, everything else refused (the refusal is the HIR **subset gate**, the map is a projection) | [P] + subset gate stays in the consumer |
| 11 | `resolve` | name lookup walking the `bi_syms` parent chain | [O] over [P] data — the CHAIN shape is read from the AST (hop-1 measurement: bind's `pl_procs` registry is FLAT and carries NO parent pointer); every table it walks is bind rows |
| 12 | `register_children` | AST walk over `Sproc`/`Bproc` to discover the block-tree shape; each discovered proc is then looked up in `plan.pl_procs` by `pl_name` — a Bproc child WITHOUT a `pl_procs` entry is a hard refusal (second-authority guard), never an invented block | [O] (shape) + [P] (identity/signature) |
| 13 | `register_children` guards | anonymous procedure block (no `bname`); proc not in bind registry; duplicate internal proc name | guard [O]/[P] — all refuse loudly |
| 14 | `procs_by_name` | name→pid registry assembled from bind-registered procs (+ main when `top_is_proc`) | [O] organizing [P] facts |
| 15 | `lower_call` | callee identity via `procs_by_name`; arity checked against `List.length pl.Bind.pl_ptrs` (bind's formal pointer cells; names are `List.map pl_l bparams` in bind — measured `bind.ml:2557`, so formal NAMES+ORDER are bind-produced); recursion via `pl_rec`/`pl_attr_rec`; result type via `pl_ret` | [P] (fallback: a callee with no `proc_layout` would use AST `bparams` length — reachable only for pid 0 of a MAIN program, which is never in `procs_by_name`; defensive branch kept) |
| 16 | `params_of` (in `build`) | AST `bparams` → sids via the block's bind rows; an AST formal with NO bind row refuses `HIR-E03` "explicit formal dcl required in P0" (bind gives an undeclared formal no row — hop-1 measurement; the refusal is the interface honouring missing bind data, NOT inferring a signature) | [P] + typed missing-information refusal |
| 17 | `Sdcl` lowering guards | `dlevel/ddims/dinit/dattrs/dpre` subset refusals; then existence via the block's bind rows (`List.assoc_opt key bi.bi_syms`) | guards (subset) + [P] |
| 18 | `lower_lit` / `lower_arith_node` | literal typing + `+ - *` result-precision rules + profile-ceiling clamp | **NOT bind** — target-profile language rules (`Language_rule` provenance, RESULTS §3.3, arch doc §4); stay in the consumer; audited in §P1-b.5 |
| 19 | `bind_and_dump`-adjacent | none — the HIR path never calls `$S` dumping | — |

**Class [D] finding (honest audit):** NONE. P0 falsifier F6 already established that every
name→meaning channel reads bind-seeded structures; no second resolver and no duplicate typing
function exists in `Hir_build` to delete. What P1-b reduces is the **number of places that
reconstruct the tables themselves** (rows re-keying, the dcl channel, the parent-chain
lookup, the proc registry, the formal/return/arity/recursive lookups — sites 4, 6, 11, 14,
15, 16): one module owns them and is directly testable against bind. Moving code merely to
rename it is NOT progress; the migration must therefore (a) delete exactly the table-building
and lookup machinery listed above from `hir_build.ml`, (b) add capability the old private
tables did not have (procedure signature by pid, formal typed identities, entry signatures,
parent/child edges as data, a `not_declared`/`not_visible`-typed lookup that distinguishes
"unknown scope" from "not found"), and (c) prove equivalence by test (§P1-b.4).

**Explicit anti-overclaim list (bind facts vs AST-reconstructed):** the block-tree NESTING
shape (parent/child edges), which statement is the proc definition, the parameter-name list,
and the anonymous-block detection are read from the **AST**, because Bind exposes none of them
(`pl_procs` flat, no parent pointer — hop-1 measurement). Symbol identity numbering (sid/scope/
pid integers) is the interface's own deterministic contract. Everything named [P] above is a
bind-produced fact, read through a bind-exported function or field.

### P1-b.2 `Semantic_env` contract (new module `ocaml/hir/semantic_env.ml`)

A **read-only projection** over `(Ast.block × Bind.prog_layout)`, transitional (lives in
`pli80_hir`; the historical pipeline never references it; `pli80c.exe` never links it). It is
NOT a binder: `create` performs no name resolution of uses, no type interpretation of
declarations (that is bind's `resolve_type`), no storage computation.

Public surface (exact names fixed at pre-registration; additions only by amendment):

```ocaml
type stype =            (* faithful projection of Bind.rt; physical components DROPPED *)
  | SFixed_bin of int | SFixed_dec of int * int | SFloat of int
  | SChar of int * bool | SBit of int | SPointer | SLabel
  | SFile of { internal : bool }
  | SBased of string * stype                       (* view through a named pointer cell *)
  | SMember of { owner : string; based : bool; ty : stype }  (* record-relative position dropped *)
  | SStruct of { level : int; members : int }
  | SStructrec of { ptr : string }                 (* record byte extent dropped *)
  | SBuiltin
  | SEntry of { params : int; external_ : bool; ret : stype option
              ; ptypes : stype list }
val type_of_rt  : Bind.rt -> stype        (* total, deterministic projection; not interpretation *)
val pp_stype    : stype -> string
type storage = S_auto | S_static | S_formal
type symbol = { esid : int; ekey : string; eorig : string; escope : int
              ; ety : stype; epr : string; estorage : storage; eline : int }
              (* epr = Bind.rty_str of the source row, carried VERBATIM so type-naming
                 diagnostics quote bind's own words and stay byte-identical across the seam *)
type proc_sig = { sptrs : string list; sret : stype option; sret_pr : string option
                ; sptr_count : int; srec : bool; sattr_rec : bool }
                (* sptrs = formal names in bind's own order (pl_ptrs keys, bind.ml:2557) *)
type block_env = { epid : int; escope : int; eparent : int option
                 ; ename : string option; ekey : string option   (* lowered proc key when named *)
                 ; esyms : (string * symbol) list                (* bind row order *)
                 ; eformals : string list                        (* lowered AST bparams *)
                 ; esig : proc_sig option; east : Ast.block }
type entry_sig = { en_params : int; en_external : bool
                 ; en_ret : stype option; en_ptypes : stype list }
type t   (* main block, pre-order block list, procs_by_name, entry decls *)
exception Not_found of { scope : int }   (* typed unsupported: NOT a silent None *)
val create                : Ast.block -> Bind.prog_layout -> (t, Diagnostic.t list) result
val key_of                : Ast.name -> string            (* = Bind.pl_l, the one alias policy *)
val find_dcl              : t -> block_env -> string -> (Ast.dcl * int) option (* Bind.frame_decls channel *)
val block_line            : Ast.block -> int              (* moved here; hir_build keeps one call site *)
val blocks                : t -> block_env list           (* pid-ascending = pre-order *)
val main_block            : t -> block_env
val block_of_pid          : t -> int -> block_env
val block_of_scope        : t -> int -> block_env         (* raises Not_found — typed unknown *)
val scope_syms            : t -> int -> (string * symbol) list (* raises Not_found *)
val symbol                : t -> int -> symbol option     (* esid lookup across ALL blocks *)
val resolve               : t -> int -> string -> symbol option
                          (* NEAREST lexical binding; the chain is AST nesting over bind rows *)
val procedure             : t -> string -> int option     (* lowered key -> pid *)
val signature             : t -> int -> proc_sig option   (* pid -> bind facts; None = not bind-laid *)
val enclosing             : t -> int -> int option        (* pid -> enclosing proc pid (main = 0 None) *)
val entry_decls           : t -> (string * entry_sig) list
```

Excluded from the public surface by contract (brief Step 2; falsifier F8 extended to this
module): frame/DATA offsets, `bytes_of` values, section sizes (`pl_secs`), `pl_total`,
`pl_top_cell`, `pl_sp_cell`, relocation records, data-pool addresses, 8080 vocabulary. The
offset components of `bind_rows`/`pl_ptrs`/`pl_rows`/`RTbmem`/`RTimem`/`RTstructrec` are
dropped at the projection boundary.

The public interface references **no `Hir` type**: the env is backend-independent; `Hir_build`
remains the only module mapping `stype → Hir.ty` (the subset gate). `Hir.storage` and
`Semantic_env.storage` stay parallel-by-hand by design (P0 deviation-1 precedent).

Typed unsupported/unknown policy (brief Step 2): a lookup against a scope pid never returns a
silent `None` — an out-of-range scope raises `Not_found` (caller bug, loud); a name absent
from the whole visible chain returns `None` (bind registered no row: THE one authority says
it does not exist); an AST formal with no bind row stays a refusal *in the consumer* (P0
message preserved). Missing Bind capabilities are listed in §P1-b.6 and RESULTS (no silent
inference): per-BEGIN scoping, expression typing, qualified/suffix resolution, INITIAL
values, static/varying descriptor detail, ON-unit facts (bind HAS `pl_on` but the env does
not expose it in P1-b — documented exclusion, not an invention).

Determinism: pre-order walk identical to today (main pid 0 scope 0, then AST-nested Bproc
children in source order; rows in bind declaration order). sids/scopes/pids assigned exactly
as at `aaf295f0`, so every existing dump byte is preserved (falsifier S2).

### P1-b.3 Migration contract for `ocaml/hir/hir_build.ml`

- DELETE: `ctx` mutable tables (`next_sid/next_scope/next_pid/blocks/procs_by_name`),
  `rows_of_block`, `dup_free` (now in env), `find_dcl` (env channel), `block_line`,
  `register_block`, `register_children`, `resolve`, the `procs_by_name`/arity/return-type
  direct bind reads in `lower_call`/`Sprocedure_stmt`/`params_of`/`ret_of`.
- KEEP in `Hir_build`: `ty_of_rt : Semantic_env.stype -> (Hir.ty, string) error` (the HIR
  subset gate, message text unchanged — it quotes the carried bind `epr` rendering), the
  sid-ordered eager projection of env symbols into `Hir.sym` (preserves today's refusal
  ORDER within registration), the statement/expression lowering, the profile language-rule
  typing (§P1-b.5), `Hir_error` plumbing, and the CLI contract.
- The ONLY remaining `Bind` reference in `hir_build.ml` is `Bind.bind_program` (plus its
  module alias): every other bind read moves behind `Semantic_env` (falsifier S5).
- No HIR construct, diagnostic code, dump format, message text, refusal, or subset rule
  changes. H01–H05 dumps and pinned stderr are byte-frozen (falsifier S2).
- Known adjudicated drift (predicted, not forced): guards that ran DURING registration now
  run in `env.create` BEFORE any subset projection — for a program carrying BOTH a nested
  registry guard violation AND an outer-block out-of-subset type, the FIRST reported
  diagnostic may differ. Both outcomes remain loud, rc 2, zero stdout; no P0/P1 fixture
  combines two independent refusals (measured in §P1-b.4). Recorded here so a future
  adjudication cannot be retro-fitted silently.

### P1-b.4 Semantic-authority tests (brief Step 4)

New fixtures (format law: CRLF + bare `^Z`; ids verified unused — `hir/fixtures` holds only
H01..H05; no `H6`/`H06`/`H07` anywhere in `hir/`, `probes/`, `spec/INVENTORY.txt`):

- **H06** unsupported declaration type: `dcl c char(3);` in main → `HIR-E02` quoting bind's
  own rendering `CHAR(3)`, rc 2, zero stdout (pinned stderr + rc, data-driven negative form).
- **H07** missing bind information: internal proc whose formal `q` has no explicit dcl →
  `HIR-E03` "explicit formal dcl required in P0", rc 2, zero stdout (bind gives an
  undeclared formal NO row — the typed missing-information channel, not an inference).
- H01–H05 re-run UNCHANGED (same expected files, byte-compare).

New in-repo semantic-authority test binary `ocaml/hir/semtest.ml` (executable in the
`pli80_hir` directory, never in `ocaml/bin/`; links `pli80` + `pli80_hir` only — the P0 F1
exe-dir law says extra stanzas in `ocaml/hir/` do not move `pli80c.exe`; re-verified S1):
for each POSITIVE fixture it asserts, against the LIVE bind-produced env (never against dump
text):
1. every `Hir.sym` field equals the env symbol projection (sid/key/orig/scope/storage/line/type);
2. every `Var sid` in a body resolves, from the REFERRING procedure's scope, through
   `Semantic_env.resolve` to exactly that symbol — nearest-binding/shadowing is checked
   against bind rows, not dump strings (H03: `g(x)`'s `sym(0)` must be the OUTER x;
   inner x `sym(3)` must NOT be reachable by that reference);
3. declaration order: env `esym`s of every block are in bind row order; sids ascend in the
   documented pre-order;
4. procedure/formal relationship: `Hir.proc.params` equals the sids of the block's formal
   set resolved in the proc's own scope, in bind `sptrs` order; formal storage flag set;
5. return type: `Hir.proc.ret` equals `type_of_rt` of the block's bind `pl_ret` rendering
   agreement checked;
6. parent/child: every env block's `eparent`/`enclosing` matches the AST nesting of the
   fixture (checked from env data itself against the parsed AST shape);
7. every `Call_e/Call_s` pid has a bind signature with arity = number of args (bind cells).
Output contract: success prints ONE line `SEMANTIC-AUTHORITY OK <n> refs / <m> syms` rc 0;
any violated invariant prints `SEM-FAIL …` lines to stderr, rc 1, zero stdout.
Negative control (proves the checks are not vacuous): `--corrupt` runs a deliberate wrong-sid
query and must print SEM-FAIL, never OK.
`tools/hir_test.py` gains: run `semtest.exe` twice per positive fixture (determinism S7), rc
must be 0; F10 grep (S5): after comment strip, `hir_build.ml` contains `Bind` only at the
alias line and the single `bind_program` call; S8 grep: `semantic_env.ml` contains no `\bHir\b`
reference (env independent of the IR) and passes the same F8 purity patterns.

### P1-b.5 FIXED arithmetic typing audit (brief Step 5 — no change authorized)

Measured state at `aaf295f0` (`hir_build.ml lower_arith_node` + `target.ml` + arch doc §4):
- language-level proposed rule: `+`/`-` → `max(p1,p2)+1`, `*` → `p1+p2`, scale 0, carried as
  the `typing` string `language-rule:max+1` / `language-rule:prec-sum`;
- prototype normalization: result above `profile.max_fixed_precision` (15, Oracle_backed for
  DECLARATIONS only, E1415..E1432) is CLAMPED to the ceiling and the node string names both
  the rule and the clamp plus `DR intermediate typing unmeasured [TBD]` (P0 hop-2 amendment,
  RESULTS §3.3);
- oracle-backed historical behavior: NONE of the intermediate-typing fields is oracle-backed;
  `Target.fixed_arithmetic_typing.value = None`, source `Language_rule …` (NOT promoted).
The three layers stay strictly separated; P1-b changes NO typing code, NO rule strings, NO
expected dumps. Any structural issue found during the migration is documented for a separate
phase, not folded into this seam.

### P1-b.6 Facts Bind does NOT expose (carried into RESULTS; each is a documented gap, never inferred)

1. Parent/child procedure edges (flat `pl_procs`) — nesting shape read from the AST [O].
2. Per-`BEGIN` scoping — bind merges BEGIN/DO declarations into the frame block (HIR-E11
   refusal retained unchanged).
3. Expression result typing (arch doc §1.3) — no bind function types an expression.
4. Qualified/suffix use resolution — lives in codegen (`resolve_suffix`), out of env scope.
5. INITIAL values, EXTERNAL static/varying descriptor detail, ON-unit facts (`pl_on` exists
   in bind but is NOT projected by P1-b — documented exclusion).
6. sid/scope/pid identity — an interface contract, not a bind fact.

### P1-b.7 Falsification criteria (each a STOP-and-fix gate, mirroring §P0.8)

- **S1** `pli80c.exe` sha256 stays `172595d5…` after EVERY build-touching step (fresh
  `--build-dir` at close). Moved = attribute first-hand; never accept silently.
- **S2** `hir/expected/*` files byte-UNCHANGED (git diff empty); H01–H05 pass unchanged.
- **S3** full `python3 tools/e2e_gate.py` rc 0 with FROZEN counts 1328/1328, 190/190, 9/9,
  coverage 149 rows 0/0, census 16/0/25/0, prose 5 → `build/gate-e54p1b-reg.log`.
- **S4** `ocaml/lib/`, `ocaml/bin/`, `golden/`, `spec/` ledgers (claims 203 headers ending
  C380, inventory, coverage, census), `probes/`, `artefacts/` untouched; ZERO oracle.
- **S5** seam audit: post-migration `hir_build.ml` (comments stripped) references `Bind` only
  via the alias + one `bind_program` call; `semantic_env.ml` is the only HIR-path reader of
  bind layout fields.
- **S6** semtest rc 0 on every positive fixture; `--corrupt` control FAILS loudly (tool not
  vacuous).
- **S7** every new binary output deterministic across two fresh processes.
- **S8** `semantic_env.ml` free of F8 byte-layout vocabulary and of `\bHir\b`; no `Hir` type
  in any public signature; no offset/cell-size/section/pool/reloc value crosses the seam.
- **S9** ZERO oracle calls / no new claim / no coverage promotion.
- **S10** every `SEM-FAIL`/`HIR-E*` diagnostic text and code produced by the migrated path
  is byte-identical to the `aaf295f0` path for the same input (checked on all fixtures;
  predicted order-drift case in §P1-b.3 stays loud and is recorded, not hidden).

### P1-b.8 Work order (exact order)

1. (this commit) §P1-b pre-registration.
2. Implement `ocaml/hir/semantic_env.ml` + `dune` `(modules …)`; build rc 0; S1.
3. Migrate `hir_build.ml`; build rc 0; S1; H01–H05 unchanged via hir_test (S2).
4. Measure H06/H07 behaviour, write fixtures + pinned negatives; S6/S7.
5. `semtest.ml` + `tools/hir_test.py` extension; full hir_test rc 0 (S2/S5/S6/S8).
6. FULL gate rc 0 → `build/gate-e54p1b-reg.log` (S3); re-check S1 on a FRESH build dir.
7. Close: RESULTS §P1-b (+ before/after dependency map + unexposed-fact list + P1-a
   proposed order), arch doc update, durables + guard checkpoint. STOP — P1-a NOT started.

### P1-b.9 Expected outcomes (pre-registered, falsified-not-forced)

All frozen numbers stay frozen (S1/S3 — nothing the gate touches moves). H01–H05 byte-stable.
Two new pinned negative fixtures. One new tested seam module. Zero historical bytes, zero
oracle, ledger stays C380. Deviations (predicted): none in behaviour EXCEPT the §P1-b.3
multi-refusal-order note; any further deviation is recorded VERBATIM, never forced away.

### Dashboard update

| slice | status | gate log | notes |
|---|---|---|---|
| P1-b | **CLOSED 2026-11-08** (hop 4) | `build/gate-e54p1b-reg.log` (rc 0, FROZEN counts ALL HIT) | ZERO oracle; RESULTS §P1-b (S1–S10 measured panel, dependency map, §P1-b.6 list, THREE measured notes); arch doc §7-1; `ocaml/lib`+`ocaml/bin` byte-clean verified; **P1-a PROPOSED ONLY — NOT authorized, NOT started** |



---

## §P1-a1 — Pre-registration: Arrays and Addressable References (committed BEFORE any `ocaml/hir/` byte)

**Authorized by the operator 2026-11-08** (message reproduced VERBATIM as §P1-a1.0 below).
Campaign slice **E2E-54/P1-a1** — the arrays/addressable-refs slice of the P1-a roadmap
family (RESULTS §P1-b.6 proposed order, item 1: arrays), promoted to an authorized phase by
that explicit operator decision. Type of work: **backend architecture, ZERO oracle calls**
(none planned or authorized). Starting reference:
`9174ad441a33e49499b8fffa30054290f540242b` (verified first-hand at hop-1 session start and
re-verified first-hand at hop-2 start: `dune build` rc 0; `pli80c.exe` sha256 `172595d5…`;
`tools/hir_test.py` rc 0 H01–H07 + semtest live/corrupt + F4/F7/F8/F9/F10/S8).

PUT/GET, the BEGIN/DO hygiene repair, MIR code generation and any historical-compiler
refactor are explicitly NOT started or authorized by this slice (brief close clause).

**Transcription note (honest):** the brief below is reproduced character-for-character from
the operator message as stored in the session transcript
(`01a1bd4d-a12c-73ad-8fbc-6a67fb7548e7`); the stored text begins with a stray leading `g`
immediately before the title, which is reproduced as received rather than silently repaired.

### P1-a1.0 Operator brief (verbatim)

> g# DRPLi — E2E-54/P1-a1: Arrays and Addressable References
>
> ## Operator authorization
>
> The operator authorizes the next architectural slice, **E2E-54/P1-a1**, focused on one-dimensional arrays and addressable references in the new HIR.
>
> Starting Git reference: `9174ad441a33e49499b8fffa30054290f540242b`.
>
> E2E-54/P0 and P1-b are CLOSED.
>
> This campaign does not modify the historical PL/I-80 compiler or implement MIR code generation.
>
> ## Objective
>
> Extend the backend-neutral HIR with a sound model of:
>
> - One-dimensional array declarations.
> - Semantic element types.
> - Declared lower and upper bounds.
> - Constant and variable subscripts.
> - Array-element reads.
> - Array-element assignments.
> - Addressability of scalar variables versus array elements.
>
> Establish the abstraction that a future backend will use for memory access without importing DR's physical layout.
>
> ## Phase 1 — Preregister and verify semantic authority
>
> Read the existing P0/P1-b architecture and scientific results.
>
> Inspect `Ast.dim`, `Bind.bind_arrays`, `Bind.bind_rows`, `Bind.frame_decls`, `Semantic_env` and existing array tests.
>
> Preregister a specific P1-a1 contract in `spec/lab-evidence/e2e54/PLAN.md` before changing source files.
>
> Verify first-hand which facts the binder actually produces:
>
> 1. Array identity and element type.
> 2. Lower and upper bounds.
> 3. Number of dimensions.
> 4. Index-expression types.
> 5. Array versus scalar resolution.
>
> **Do not assume that a dimension written in the AST has already been semantically validated by Bind.**
>
> Distinguish bind-established facts from syntactic facts and unmeasured behavior.
>
> If the binder lacks a required semantic fact, document that gap and restrict the subset. Do not construct a competing array binder.
>
> ## Phase 2 — Semantic_env projection
>
> Extend `ocaml/hir/semantic_env.ml` with the smallest array-description interface justified by the verified binder.
>
> Keep the projection:
>
> - Typed.
> - Deterministic.
> - Independent of HIR.
> - Free of physical byte offsets and element strides.
>
> Do not expose storage-layout tuples as semantic array descriptors.
>
> Support one-dimensional arrays only in this slice.
>
> Explicitly refuse unsupported dimension expressions and multidimensional forms rather than guessing their semantics.
>
> ## Phase 3 — HIR extension
>
> Introduce a backend-neutral representation of:
>
> - Array types or array-shaped symbols.
> - Bounds as semantic quantities.
> - Indexed element references.
> - Addressable assignment targets.
> - Reads of array-element values.
>
> Keep the distinction between an *lvalue* and its loaded value explicit enough for later backend lowering.
>
> For example, these operations must not collapse into the same HIR node:
>
> ```pli
> x = a(i);
> a(i) = x;
> ```
>
> The first reads an element. The second designates an element as an assignment target.
>
> A physical address, byte stride, `LXI`, pointer cell or LINK-80 relocation is not a valid HIR representation of this distinction.
>
> Preserve evaluation-order and side-effect information explicitly. Do not assert a historical evaluation-order law without evidence.
>
> No SSA conversion is required.
>
> ## Phase 4 — HIR construction
>
> Extend `Hir_build` for the measured subset only.
>
> Use `Semantic_env` as the exclusive semantic lookup interface.
>
> Do not add direct Bind layout access in `Hir_build`.
>
> Start with FIXED BINARY arrays, with a conservative supported precision band.
>
> Include:
>
> - A fixed lower-bound array.
> - An array with a non-default lower bound.
> - A constant index.
> - An index held in a scalar variable.
> - An element read.
> - An element assignment.
>
> Preserve scalar behavior and existing diagnostics.
>
> Out-of-range constant indices, unsupported dimensions and unsupported element types require explicit, deterministic handling.
>
> Do not manufacture runtime bounds checks or assume their historical behavior. Record the intended future backend policy separately.
>
> ## Phase 5 — Tests and falsification
>
> Add focused fixtures and expected HIR dumps.
>
> Test:
>
> - Symbol identity and array-element type.
> - Bound preservation.
> - Variable-subscript resolution.
> - Read versus write semantics.
> - Deterministic evaluation structure.
> - Unsupported arrays and invalid references.
> - No silent lowering.
> - Cross-checks against the live Semantic_env and Bind authority.
>
> Extend `semtest` where necessary.
>
> Preserve H01–H07 and their expected outputs and diagnostic bytes.
>
> Ensure the tests are non-vacuous by deliberately corrupting an array descriptor or reference and observing a failure.
>
> ### Known BEGIN hang
>
> The pre-existing infinite recursion in BEGIN discovery remains a documented defect.
>
> Do not fix it incidentally in this array slice.
>
> Use bounded test execution so a regression or known hang cannot stall the campaign indefinitely. Record the behavior and preserve its classification.
>
> A separate, preregistered hygiene repair can follow P1-a1.
>
> ## Historical invariance
>
> Mandatory:
>
> - `pli80c.exe` SHA-256 unchanged:
>   `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`
> - Full historical gate RC 0.
> - 1328/1328 byte-exact specimens.
> - 190/190 negative tests.
> - 9/9 divergence controls.
> - Coverage unchanged at 149 contracts.
> - Ledger unchanged, ending C380.
> - No historical `.REL` or oracle regeneration.
> - No edits under `ocaml/lib/` or `ocaml/bin/`.
>
> No new DR claim, COVERAGE promotion or corpus reclassification is authorized.
>
> ## Deliverables and closure
>
> Produce:
>
> - P1-a1 preregistration and measured RESULTS.
> - Extended Semantic_env array projection.
> - Extended HIR addressability representation.
> - Updated HIR construction path.
> - Positive and negative fixtures.
> - Semantic-authority tests.
> - Updated backend-boundary architecture document.
> - Full regression evidence.
> - A proposed next-step roadmap.
>
> Use explicit-path commits. Never stage `handoff.config.json`. Do not push.
>
> Continue through safe Handoff renewals if available.
>
> **Close P1-a1 and STOP. Do not automatically begin PUT/GET, the BEGIN repair or MIR code generation.**
>
> Success means a future backend can distinguish scalar storage, array storage, indexed references and loaded values using portable HIR semantics, with every fact traceable to the existing frontend authority and no historical compiler regression.

(Verbatim law: the brief above is the operator message EXACTLY as stored, including the
stray leading `g` on the first line; headings are un-demoted so the quote renders the
received text character-for-character.)

### P1-a1.1 Measured semantic authority (Phase 1 — ACCEPTED facts, hop 1 + hop 2)

Every fact below was measured FIRST-HAND against the LIVE binder with the throwaway
instrument `ocaml/scratch-p1a1/` (untracked, NEVER committed; it builds with the project and
does NOT move `pli80c.exe` — S1 re-verified with it present). Raw records:
`build/p1a1-probe-1.log` (20 programs A01..A22) and `build/p1a1-probe-2.log` (11 new
programs A23..A33 PLUS a full reproduction run of the 20 probe-1 inputs — all 20 blocks
machine-compared BYTE-IDENTICAL, all RCs equal). Nothing is read from codegen; nothing is
quoted from the manual. Facts are the LEARNINGS record § "E2E-54/P1-a1 hop 1" + hop-2
addendum; this table is the contract's summary and the probe inputs are their evidence.

| fact | statement | evidence |
|---|---|---|
| A-1 | `bind_rows` carries the **ELEMENT** type; an array row is shape-identical to a scalar row; arrayness lives ONLY in the separate channel `bind_arrays` / `proc_layout.pl_arrays = (lower name, lb, ub, elem_bytes)` (`bind.ml:1588`, `:1954`, `:2560`) | A01 |
| A-2 | Single bound ⇒ `lb = 1` default; `lo:hi` pair preserved verbatim (`a(0:4)` ⇒ `(0,4)`) | A01, A02, A16 |
| A-3 | **Dimensionality is a BINDER PRECONDITION, never a recorded count** — no dims field exists; `a(3,4)` ⇒ `Failure "codegen: [TBD] multi-dimensional or assumed-size array [C159] (DR's 2-D is row-major, last subscript fastest -- characterized, not implemented)"`; `a(*)` ⇒ `Pli80.Parser.Parse_error(_, "expected expression")` (does not even parse) | A09, A10 |
| A-4 | Bind records **NOTHING** about index expressions in uses — constant, variable and compound subscripts are equally invisible; subscript text exists only in the AST (`Esuffix`) ⇒ index typing is an HIR-side documented rule, never a bind fact (gap §P1-b.6 item 4) | A16, A22 |
| A-5 | **FALSIFIED: "a written `ddims` is a validated array."** `dcl a(1)` gets NO array record — the `nelem > 1` gate (`bind.ml:1058`) drops single-element arrays into scalar-indistinguishability; THIS is the recorded codegen crash class. HIR law: dims written + no array record ⇒ loud typed refusal, never a silent scalar collapse | A11 |
| A-6 | Bounds must be NON-NEGATIVE DECIMAL LITERALS: `a(n)` ⇒ `Failure "codegen: [TBD] non-constant array dimension [C159] (only literal bounds are sizeable at bind time)"`; `a(-1:1)` same (a minus is `Eprefix`, not `Enumber`); `a(5:1)` ⇒ `Failure "codegen: [TBD] array upper bound below lower bound"`; `static` ⇒ `Failure "codegen: [TBD] STATIC array is not independently characterized [C159/AB5] ..."` — all reach the CLI unchanged as **HIR-E01** (bind refusal channel) | A12, A13, A14, A18 |
| A-7 | Element band bind RECORDS for FIXED BINARY: **p = 7** (esz 1, the `RTbin 7` class arm) and **p = 8..15** (esz 2, the `elem_sz = 2` size arm); typeless `fixed` ⇒ element row `FIXED BINARY(15,0)`; `bin(16)` dies EARLIER at the precision ceiling `bind: FIXED BINARY(16) exceeds DR's FIXED precision limit 15 (PL/I-80 V1.4 says NOT IMP) [TBD]` | probe-1 A21, A17, A05 |
| A-8 | Array facts are **PER-BLOCK**: a nested proc's `pl_arrays` lists only its OWN arrays; an enclosing array is NOT copied into the child layout — it must resolve through the env's AST-nesting chain (eparent walk), exactly as enclosing scalars do | A15 |
| A-9 | Bind performs **NO out-of-range subscript check**: `a(9)` with `dcl a(3)` and `a(0)` with `lb=1` both pass bind untouched ⇒ no bounds law exists in the authority; HIR's handling is its OWN explicit deterministic rule; DR's historical behaviour stays `[TBD]` (future-backend policy recorded separately, brief Phase 4) | A22 |
| A-10 | bin(p<7) refusal MEASURED (closes the A-7 owed re-measure): `dcl a(3) fixed bin(p)`, p = 1, 3, 6 ⇒ `Failure "codegen: [TBD] array of 1-byte elements [C159] (only FIXED BINARY(15) / typeless FIXED, i.e. 2-byte elements, are measured; DECIMAL, FLOAT, BIT and CHARACTER arrays refuse)"`, and **`bind_rows` is EMPTY at the refusal point** (the row is not emitted) | A23, A24, A25 |
| A-11 | `bit(8)` refuses with the SAME 1-byte text — `bytes_of (RTbit n) = (n+7)/8` (`bind.ml:167`) ⇒ esz 1, `RTbit` not in the class list, size fallback fails. `bit(9..15)` would size 2 — **UNMEASURED, `[TBD]`, never inferred** | A28 |
| A-12 | `char(1)` refuses (1-byte text); `char(2)`/`char(3)` are **ACCEPTED** with records `esz=2`/`esz=3` — the refusal PROSE ("CHARACTER arrays refuse") is **inaccurate as prose**: the real rule is the UNION of three measured mechanisms — the class list `RTbin 7 | RTchar (3,false) | RTlabel | RTentry _`, the size-driven fallback `elem_sz = 2`, and an earlier death for `bin(16)`. HIR keys the subset on the projected RUNTIME TYPE + bounds; it may quote the refusal text verbatim but must NOT restate its prose as a language rule | A29 vs A07, A08 |
| A-13 | Nested procs OWN their array channel: `PL_PROC p pl_arrays=[b:1:2:2]` while the top block holds `(a,1,4,2)` | A30 |
| A-14 | **Structure-member arrays NEVER reach `bind_arrays`.** `dcl 1 s fixed bin(15), 2 a(3) fixed bin(15);` ⇒ `bind_arrays` EMPTY; two rows `key=a` and `key=s.a` typed `FIXED BINARY(15,0) MEMBER OF S@2`, `auto=false`; no subscript use recorded. ⇒ `Array1` is produced ONLY by the top-level-name × array-record merge; a member-shaped row never becomes an `Array1`. (The member-subscript USE form is unmeasured here.) | A31 |
| A-15 | **Subscript on a SCALAR name is invisible to bind:** `dcl y fixed bin(15); … y(1) = 2;` ⇒ ordinary scalar row, `bind_arrays` EMPTY, the use exists only in the AST ⇒ "is this name even an array" is decided by the MERGE (row without array record + subscripted use ⇒ HIR-side typed refusal, never a scalar collapse) | A32 |
| A-16 | **WHOLE-ARRAY use records nothing:** `a = 1;` with `dcl a(3)…` ⇒ array record present, ZERO subscript uses; bind gives no array-in-value-context fact; historical codegen behaviour `[TBD]`. HIR refuses whole-array use as its own explicit subset rule | A33 |
| A-17 | (tooling law) **probe determinism:** the identical instrument over the identical 20 probe-1 inputs reproduced every block byte-for-byte in fresh processes — the A-facts are a property of the binder, not of the session | probe-2 reproduction section |

### P1-a1.2 Subset contract (what P1-a1 LOWERS; everything else refuses LOUDLY)

One construct class is added: **one-dimensional arrays of FIXED BINARY elements**, lowerable
in read and designate position, exactly where the binder produced a record for them.

Admitted (ALL conditions necessary; each traces to a measured fact):
1. **1-D only.** `ddims = [Dim_bound (lo, Some hi)]` or `[Dim_bound (ub, None)]` — a second
   dimension cannot even reach bind (A-3), so every array symbol HIR can see is 1-D by
   construction; a **2-subscript USE** of an array name is a source defect and refuses (§P1-a1.7 E14).
2. **Element `FIXED BINARY` within the MEASURED band:** `SFixed_bin p` with **p ∈ {7} ∪ {8..15}
   = 7..15** (A-7, A-10: bin(1..6) never produces a record; bin(16) dies in bind). Typeless
   `fixed` is in-band because bind gives it the element row `FIXED BINARY(15,0)` (A-7).
3. **Bounds are the binder's own** non-negative decimal literals (A-6 — anything else is
   already a HIR-E01 bind death before HIR sees the program); `lo`/`hi` are carried as
   SEMANTIC quantities (declared index limits), never as sizes, strides or offsets.
4. **`nelem > 1` holds** — guaranteed because bind records an array ONLY under that gate
   (A-5); dims-without-record therefore REFUSES (rule below), it cannot silently pass.
5. **Array identity is the merge** `bind_rows` key × `bind_arrays`/`pl_arrays` lowered name
   (A-1, A-8); member-shaped rows never merge (A-14).

Refused loudly (typed, deterministic, line-carrying; NEW codes where the class is new):
- dims written + NO array record (`a(1)`, `a(1:1)`, member arrays) → **existing `HIR-E03`
  kept byte-identical in wording** for the declaration path (A-5/A-14): `array declaration
  for <name> is outside the P0 subset` (the guard branch now means "outside the admitted
  array subset"; the text stays because it remains TRUE of these shapes);
- subscripted use of a name whose merged symbol is NOT an array (scalar A-15) → **E12**;
- whole-array use of an array name (bare `a` in value or target position, A-16) → **E13**;
- use with a subscript-count ≠ 1 → **E14**;
- constant subscript outside `[lo, hi]` (A-9 — HIR's OWN law, DR behaviour `[TBD]`) → **E12**;
- array whose ELEMENT type is outside the band (e.g. `char(2)`/`char(3)` arrays, which bind
  DOES record — A-12) → the existing `HIR-E02` channel with an array-specific wording (§P1-a1.5);
- any array reaching HIR through a record with no matching row (defensive split-channel
  inconsistency guard) → **E14**;
- `esz` (element BYTES) is physical and is **DROPPED at first touch** — like the row offset
  (T1 law), it crosses NOTHING (A-1, brief Phase 2: "free of physical byte offsets and element strides").

No bounds CHECK is manufactured: the out-of-range CONSTANT refusal is a compile-time subset
decision, not a runtime check; the record-not-vs-value policy is stated in §P1-a1.5 and the
historical behaviour stays `[TBD]` (brief Phase 4 — "do not manufacture runtime bounds checks
or assume their historical behavior").

### P1-a1.3 HIR node contract (Phase 3 — `ocaml/hir/hir.ml`)

```ocaml
type ty += Array1 of { elem : ty; lo : int; hi : int }
    (** 1-D array: element type + declared LOWER/UPPER index bounds (A-2); NO stride,
        NO element size, NO placement — those are layout (T6). *)

type expr_kind +=
  | Elem_read of { base : int; subs : expr list }
      (** LOAD of element [base(subs)]; [ex_ty] = the element type; [subs] has EXACTLY
          ONE element (subset gate); effect = union of the subscript effects. *)
  | Elem_ref  of { base : int; subs : expr list }
      (** LVALUE designator of element [base(subs)]; [ex_ty] = the element type; legal
          ONLY as an `Assign.target`. *)
```

- **Read vs designate can NEVER collapse:** two distinct constructors. The node is made
  statically honest by a new `target` variant (same adjudicated pattern as the P0 hop-2
  `effect`→`ef_kind` rename: an internal representation rename, dumps and diagnostic bytes
  unchanged — §P1-a1.5 proves H01–H04/H06/H07 byte-frozen):

```ocaml
type target = T_var of { sid : int } | T_elem of { base : int; subs : expr list }
(* Assign.target : expr  becomes  Assign.target : target  (constructor name unchanged) *)
```

  `Elem_read` in target position is UNEXPRESSIBLE; `Elem_ref` in value position cannot be
  produced by the lowering (value path never constructs it) and semtest I8 rejects it anyway.
- **Bounds live on the TYPE, not on the node:** `base` is a sid whose projected `Hir.sym.sty`
  is `Array1 { elem; lo; hi }` — nodes stay minimal, no duplicated state, dumps recover the
  bounds through `Hir.program` when printing (dump gains a symbols argument; this is
  rendering, not representation).
- **Addressability (brief "scalar vs array element"):** scalars stay `Var { sid; addressable =
  true }` (existing field, existing value); an array element's addressability IS the
  `Elem_ref` designator node — a designated lvalue that is never a loaded value. The `stype`
  classification question (arch §1.4) is NOT re-opened here.
- **Dump wording (MEASURED pins, never hand-written; §P1-a1.5 review law):**
  - `elem_read sym(<base>)[<lo>:<hi>] : <elem-ty>  [<eff>, line <n>]`
  - `elem_ref sym(<base>)[<lo>:<hi>] : <elem-ty>  [<eff>, line <n>]`
  with the subscript expression nested one level below (same indent law as call args);
  **the dump prints BOUNDS, never a byte count, stride or size** (T6); the F4 hex-shaped-token
  audit still applies (bounds are decimal).
- **Evaluation order:** subscripts evaluate left-to-right (trivially, the single element);
  the assign line keeps its existing `order: target address then value` wording — for an
  `Elem_ref` target "address" designates computing the element designation from the base
  row and the evaluated subscript. This ordering is an **HIR representation choice, NOT a
  DR law** — DR's historical evaluation order is UNMEASURED `[TBD]` (brief Phase 3: do not
  assert an order law without evidence). No SSA (brief Phase 3).
- `Convert` and the language-rule typing are UNTOUCHED: element assignment reuses the scalar
  fixed→fixed `Convert` machinery with the same `reason` wording.

### P1-a1.4 `Semantic_env` API additions (Phase 2 — `ocaml/hir/semantic_env.ml`)

Amendments to the §P1-b.2 surface (the contract's own amendment mechanism; additions only,
no existing field or function changes):

```ocaml
type stype += SArray1 of { elem : stype; lo : int; hi : int }
    (* AMENDMENT (P1-a1): arrayness is a SEPARATE symbol field below; this constructor is
       never produced by `type_of_rt` (bind array rows carry the ELEMENT type — A-1); it
       exists for `pp_stype` rendering of merged array symbols. *)

type array1 = { a_elem : stype; a_lo : int; a_hi : int }
    (* `esz' is DROPPED at the first touch (like the row offset, T1/S8-class law). *)

type symbol += { … ; e_array : array1 option }   (* None = bind gave no array record *)
```

- **Merge law:** inside `register_block`, the block's `bind_arrays` list (the same channel
  probe-1/probe-2 read: `Bind.bind_arrays blk` — per-block, A-8/A-13) is joined to the
  projected rows by the lowered key. A row with a matching array record gains
  `e_array = Some { a_elem = <row stype>; a_lo = lb; a_hi = ub }`; its `epr` stays bind's
  VERBATIM element-type rendering (A-1); `eline`/`estorage`/`esid` assignment are UNCHANGED
  (scalar dumps must not move — T2).
- **Guard law (split-channel inconsistency):** an array record whose lowered name matches NO
  row of the same block raises the typed refusal **E14** (defensive; no probe produced this
  shape — recorded as unexercised, like the P0 dup_free witness); duplicate array records for
  one name refuse on the same channel. Member-shaped rows never merge because members never
  enter `bind_arrays` (A-14 measured).
- `resolve`/`symbol`/`scope_syms` need NO change: the array record rides the symbol through
  the eparent chain (A-8 ⇒ enclosing arrays resolve exactly as enclosing scalars).
- `pp_stype (SArray1 {elem; lo; hi})` = `<pp elem> ARRAY[<lo>:<hi>]` — semantic wording, no
  byte vocabulary (T6).
- **NO `Hir` type enters this interface** (S8/T6 unchanged); no offset/stride/`bytes_of`/size
  word appears in CODE (comment strip) in `semantic_env.ml` or `hir.ml`.

### P1-a1.5 `Hir_build` changes (Phase 4 — the consumer keeps the subset gate)

- `project_syms`: for `e_array = None`, the scalar gate and its message are **byte-identical**
  (T10 — H06's `declared type CHAR(3) for c is outside the P0 HIR subset (FIXED BINARY scalars
  only)` must not move). For `e_array = Some { a_elem; a_lo; a_hi }`: map `a_elem` through the
  EXISTING `ty_of_rt` gate; in-band ⇒ `sty = Array1 { elem; lo; hi }`; out-of-band ⇒
  `HIR-E02` with the array wording `array element type <epr> for <key> is outside the P1-a1
  array subset (1-D FIXED BINARY(7..15) elements only)` — a NEW message on an EXISTING code.
- `Sdcl` path: the existing `ddims <> []` guard STAYS and keeps its exact text (E03); the
  **adjudication:** the guard is NARROWED to fire only when `ddims <> []` AND the resolved
  symbol carries `e_array = None` (dims-without-record — A-5/A-14), so an admitted array
  declaration lowers to the existing `Declare sid` node (its `Hir.sym.sty` is already the
  `Array1` projection); dims-without-record still dies with the UNCHANGED text (H10 pins it).
- Value path (`lower_expr`): `Esuffix(Eident n, [arg])` where `resolve` yields an array symbol
  ⇒ `Elem_read` (constant subscript: range-checked per §P1-a1.2, E12; variable subscript:
  lowered through the existing `lower_arith` FIXED BINARY gate); `Esuffix(Eident n, _)` with
  `n` a non-array symbol ⇒ E12; with `n` a procedure ⇒ existing `lower_call` UNCHANGED; with
  `n` unresolved ⇒ existing E04 wording UNCHANGED; subscript count ≠ 1 on an array ⇒ E14.
- Target path (`Sassign`): `lhs = Esuffix(Eident n, [ix])` on an array ⇒ `T_elem`; scalar ⇒
  E12; bare array name ⇒ E13. Bare-name scalar targets keep the existing path byte-identically.
- Whole-array use in value/argument position ⇒ E13. Calls with array actuals are OUT of the
  P1-a1 subset (descriptor passing is a future slice — brief Phase 4 lists only the six
  positive capabilities).
- **F10/T5 unchanged:** `Bind` still appears ONLY at the alias line and the one
  `bind_program` call; every array fact crosses via `Semantic_env` (`bind_arrays` is read
  EXCLUSIVELY inside `semantic_env.ml`).

New diagnostic codes, appended to the stable list in `diagnostic.ml` (existing codes NEVER
change meaning; T10):

| code | name | issued for | wording (deterministic, `[TBD]`-honest) |
|---|---|---|---|
| `HIR-E12` | `e_index` | subscript on a non-array symbol; out-of-range CONSTANT subscript | `subscript on <orig> … is not a 1-D array reference in the P1-a1 subset` / `constant subscript <k> for array <orig> is outside the declared bounds [<lo>:<hi>] (compile-time HIR subset rule; DR out-of-range behaviour unmeasured [TBD])` |
| `HIR-E13` | `e_whole_array` | array name used whole (value or target) | `whole-array use of <orig> is outside the P1-a1 subset (element references only)` |
| `HIR-E14` | `e_dims` | subscript count ≠ 1; orphan/duplicate array record (split-channel guard) | `subscript form for <orig> is outside the 1-D P1-a1 subset (n subscript(s))` / `bind array record for <key> has no matching row (split-channel inconsistency)` |

(The exact final strings are MEASURED from the implementation and pinned from actual output;
this table is the intent, the fixture pins are the evidence — measurement law.)

### P1-a1.6 Fixture plan (MEASURED pins — expected files are generated by running, reviewed line-by-line, never hand-written)

Format law (P0): CRLF line endings + `^Z` terminator (bare LF shifts every line −1 — measured
P0 law). Existing H01–H07 stay on disk; ids H08..H15 verified unused this session (`hir/`
holds only H01..H07; no `HIR-E12..14` anywhere; `spec/INVENTORY.txt` names are `E36H*`, not
`H*`).

| fixture | kind | content (capabilities covered) | expected |
|---|---|---|---|
| **H05** | **FLIPPED negative→positive** (adjudication below) | `dcl a(5) fixed bin(15); a(1) = 2;` | rc 0 dump with `elem_ref sym(0)[1:5]` + const 2; positive semtest + all corrupt modes |
| **H08** | positive | fixed lb, variable index, element READ + element WRITE: `dcl a(4) fixed bin(15);` `dcl i fixed bin(15);` `dcl t fixed bin(15);` `i = 2;` `t = a(i);` `a(i) = t + 1;` (ONE dcl item per statement — comma-continued item lists are unmeasured in the HIR path and stay out of fixture syntax) | `Elem_read`/`Elem_ref` with `Var i` subscript, Convert on assign |
| **H09** | positive | non-default lower bound + constant index + in-band bin(8) element + element read into a declared scalar: `dcl b(0:4) fixed bin(8);` `dcl y fixed bin(8);` `b(0) = 3;` `y = b(2);` | bounds `[0:4]` in dumps; const subscript accepted |
| **H10** | negative | dims-without-record (A-5): `dcl a(1) fixed bin(15);` | pinned stderr, E03 unchanged text |
| **H11** | negative | element type outside band but bind-RECORDED (A-12): `dcl a(3) char(2);` | pinned stderr, E02 array wording |
| **H12** | negative | subscript on a SCALAR (A-15): `dcl y fixed bin(15); y(1) = 2;` | pinned stderr, E12 |
| **H13** | negative | WHOLE-ARRAY use (A-16): `dcl a(3) fixed bin(15); a = 1;` | pinned stderr, E13 |
| **H14** | negative | 2-subscript use: `dcl a(3) fixed bin(15); a(1,2) = 3;` (parses; bind records nothing — A-3/A-4) | pinned stderr, E14 |
| **H15** | negative | out-of-range CONSTANT subscript (A-9): `dcl a(3) fixed bin(15);` `dcl i fixed bin(15);` `i = a(9);` | pinned stderr, E12 |

Every negative fixture must carry EXACTLY ONE refusal path (review before pinning) so no
multi-diagnostic order ambiguity can arise inside a fixture (the §P1-b.3 drift lesson).
Every fixture run under the existing `timeout=60` (T9).

**H05 flip adjudication (Phase-1 open item from hop 1, now EXECUTED as planned):** H05 IS the
P1-a1 core positive shape; behaviour is a function of input, so its negative pin cannot
survive. Disposition: `git mv hir/expected/H05.stderr.txt hir/expected/H05.rc
hir/expected/superseded/2026-11-09/` (same command moves the dated note file
`hir/expected/superseded/2026-11-09/README.md` — a one-paragraph dated record of WHY,
pointing here); the flipped fixture keeps its bytes (same input), the NEW `H05.txt` expected
dump is MEASURED and reviewed; H01–H04/H06/H07 expected bytes stay frozen and are verified
untouched by `git diff --exit-code` at every step (T2).

### P1-a1.7 Semantic-authority extension (`semtest.exe`, Phase 5)

New invariants, judged against the LIVE env + bind rows (never dump text), run on every
positive fixture (H01–H04, H05, H08, H09):

- **I8 (reference soundness):** every `Elem_read`/`T_elem` base sid resolves (from the
  REFERRING procedure's scope) to a symbol whose env `e_array` is `Some`, with the node's
  `ex_ty` equal to the env element projection mapped through `ty_of_rt`; no `Var` node ever
  carries an `Array1` type (whole-array silence is impossible).
- **I9 (bound preservation):** every array symbol's `(lo, hi)` equals the live
  `Bind.bind_arrays` triple for its block name — compared with `esz` DROPPED (the comparison
  would also catch an esz-leak by construction).
- **I10 (projection completeness):** every `bind_arrays` entry of every block appears as
  `Some e_array` on the env symbol with the matching key, and (subset) every `e_array` has an
  `Array1` `Hir.sym` type — never a silent drop.

Corrupt controls (non-vacuity, S6/T7): keep `--corrupt` (wrong sid) EXACTLY as at P1-b; add
`--corrupt-array-hi` (perturb one `a_hi` before the I9 comparison — the very same comparison
must reject it) and `--corrupt-array-base` (point one `Elem_read` base at a non-array sid —
I8 must reject it). Every corrupt mode prints only `SEM-FAIL:` lines, rc 1, zero stdout.
`tools/hir_test.py` runs each positive fixture through live + ALL corrupt modes, twice, fresh
processes (T8).

### P1-a1.8 Falsification criteria (each a STOP-and-fix gate, modelled on §P1-b.7)

- **T1** `pli80c.exe` sha256 stays `172595d5…` after EVERY build step, checked DIRECT (dune
  logs never print the sha — tooling law). Moved = attribute first-hand; never accept.
- **T2** `hir/expected/H01..04` + `H06/H07` (stderr+rc) byte-UNCHANGED at every step
  (`git diff --exit-code`); the ONLY adjudicated change is the H05 flip with its archived
  superseded bytes; `superseded/` is `git add`ed once and never rewritten.
- **T3** FULL `python3 tools/e2e_gate.py` rc 0 with FROZEN counts **1328/1328, 190/190, 9/9,
  coverage 149 rows 0/0, census 16/0/25/0, prose 5** → `build/gate-e54p1a1-reg.log`; ANY
  move = STOP, record VERBATIM, never force (the §P1-b gate law).
- **T4** `ocaml/lib/`, `ocaml/bin/`, `golden/`, ledgers byte-clean vs HEAD: ledger stays
  **C380** (203 `## C` headers); NO claim, NO coverage promotion, NO inventory touch; ZERO
  oracle calls in the whole slice.
- **T5** Bind seam: `hir_build.ml` (comment strip) mentions `Bind` ONLY at the EXACTLY two
  pinned lines (F10); `bind_arrays` is read ONLY inside `semantic_env.ml` (grep law extended
  this slice: `grep -rn "bind_arrays" ocaml/hir/ ocaml/bin/` → semantic_env.ml + semtest.ml
  ONLY — the test binary is an intentional authority reader, §P1-b.4 law).
- **T6** vocabulary: after the comment strip, `semantic_env.ml` and `hir.ml` contain NO
  `stride|offset|bytes|esz|size|reloc|pool|0x` match (extended F8 strip-grep; the F4 dump
  audit proves no byte count ever PRINTS); dump array lines carry bounds only.
- **T7** semtest array invariants I8/I9/I10 live on every positive fixture AND every corrupt
  mode fails loudly (wrong-`hi` descriptor, wrong reference base, plus the surviving sid
  control) — rc 1, zero stdout, all-`SEM-FAIL` stderr.
- **T8** determinism: every fixture and every semtest invocation run TWICE in fresh
  processes, byte-identical (rc, stdout, stderr).
- **T9** bounded execution: `timeout 60` per fixture run (the runner already does); the
  pre-existing BEGIN/DO discovery hang stays DOCUMENTED, classified pre-existing, and is
  NEVER fixed in this slice (brief "Known BEGIN hang").
- **T10** diagnostic stability: every code/wording for EXISTING paths byte-identical
  (HIR-E01..E11 on H01–H04/H06–H07 + the unchanged E03 array-decl text on H10); every NEW
  refusal gets a NEW stable code (E12/E13/E14) documented in `diagnostic.ml`; the brief's
  "H05 flipped" adjudication is the ONLY behaviour change to a previously pinned input.

### P1-a1.9 Work order (exact order — the successor contract)

1. (this commit) §P1-a1 pre-registration, by explicit paths, BEFORE any `ocaml/hir/` byte.
2. `ocaml/hir/semantic_env.ml` (§P1-a1.4) → `dune build` rc 0 → T1 → commit.
3. `ocaml/hir/hir.ml` (§P1-a1.3) → build rc 0 → T1 → commit.
4. `ocaml/hir/hir_build.ml` + `diagnostic.ml` (§P1-a1.5) → build rc 0 → T1 → commit.
5. Fixtures H08..H15 + the H05 flip (§P1-a1.6): MEASURE actual outputs, review every dump
   line against §P1-a1.3 BEFORE pinning; expected files copied from measured output, never
   hand-written; hir_test partial green; commit.
6. `ocaml/hir/semtest.ml` (I8/I9/I10 + new corrupt modes) + `tools/hir_test.py` extension →
   full `timeout 600 python3 tools/hir_test.py` rc 0 → commit.
7. FULL gate rc 0 → `build/gate-e54p1a1-reg.log` (T3); fresh `dune build --build-dir
   _build-e54p1a1` rc 0 with ZERO `Error` + sha check of the kept exe against `172595d5…`.
8. CLOSE: `RESULTS.md` §P1-a1 (T1–T10 panel WITH measured values; dependency notes; any drift
   recorded VERBATIM, never fitted), `docs/architecture/backend-boundary.md` §7-2
   (addressability/array projection), PLAN dashboard row P1-a1 **CLOSED**, proposed next
   roadmap (PUT/GET, BEGIN hygiene, MIR) as **PROPOSED ONLY**; durables + guard checkpoint.
9. **STOP — close P1-a1 only. Do NOT begin PUT/GET, the BEGIN repair or MIR.**

### P1-a1.10 Expected outcomes (pre-registered, falsified-not-forced)

Frozen numbers stay frozen (T1/T3/T4 — nothing the gate touches moves). H01–H04/H06/H07
byte-stable through all five code steps; H05 flips EXACTLY as adjudicated. Six positive
fixtures, six negative pins, three new semtest invariants, three new corrupt controls, three
new diagnostic codes. Deviations predicted and honestly open:
- the OCaml **record-field evaluation order** law (§P1-b hop-2 measurement) may reorder two
  independent refusals inside a single construct — every fixture is designed to carry ONE
  refusal path to keep this unexposed; if exposed, record VERBATIM;
- the `Assign.target` type change is an internal refactor: any dump-byte movement is a
  STOP-and-attribute event (T2), not a re-pin;
- `char(2)`/`char(3)` arrays get `e_array = Some` from bind but refuse at the element gate:
  if a fixture exposes a DIFFERENT first refusal, that is the §P1-b.3 registration-order
  drift class again — record, never fit.

### P1-a1.11 Dashboard update

| slice | status | gate log | notes |
|---|---|---|---|
| P1-a1 | **CLOSED 2026-11-09** (hop 3) | `build/gate-e54p1a1-reg.log` rc 0 FROZEN 1328/1328, 190/190, 9/9, 149 rows 0/0, census 16/0/25/0, prose 5 | ZERO oracle; env Array1 + HIR Elem_read/Elem_ref/target + E12/E13/E14; fixtures H01–H09 positive/pins H10–H15 + H05 flip; semtest I1 array-aware + I8/I9/I10 + 3 corrupt modes; T1 `172595d5…` held; RESULTS §P1-a1 |


---

## §P1-a2 — Pre-registration: Procedure Arguments and Indirect References (committed BEFORE any `ocaml/hir/` byte)

**Authorized by the operator 2026-11-10** (brief reproduced VERBATIM as §P1-a2.0 below).
Campaign slice **E2E-54/P1-a2** — the procedure-arguments/addressable-references slice of
the P1-a family. Type of work: **backend architecture, ZERO oracle calls** (none planned
or authorized). Starting reference:
`b716daf057a221ec8b6016c74ed6d6bf80aaccbf` (verified first-hand at hop-1 session start
and re-verified first-hand each hop: `dune build` rc 0; `pli80c.exe` sha256 `172595d5…`;
`tools/hir_test.py` rc 0 full panel; ledger 203 `## C` headers ending **C380**;
`ocaml/lib`+`ocaml/bin` byte-clean). Re-verified FIRST-HAND again at this commit
(session 01a1bee4, renewal 2/12): build rc 0, exe `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`,
203 headers ending C380, `git status --porcelain -- ocaml/lib ocaml/bin` EMPTY,
`ls hir/fixtures | grep -c 'H1[6-9]\|H2[0-9]'` = **0** (ids H16.. FREE, re-confirmed as
this contract requires).

P0, P1-b and P1-a1 are CLOSED; this slice re-uses their evidence and touches none of it.
MIR generation, PUT/GET, the BEGIN/DO hang repair, decimal typing and the DR-specific ABI
are explicitly NOT started or authorized by this slice (brief §9).

### P1-a2.0 Operator brief (verbatim)

> # DRPLi — E2E-54/P1-a2: Procedure Arguments and Indirect References
>
> ## Operator authorization
>
> The operator authorizes **E2E-54/P1-a2**, a zero-oracle architectural campaign to prepare procedure calls, formal parameters and indirect references for future backends including MIR.
>
> Starting reference: `b716daf057a221ec8b6016c74ed6d6bf80aaccbf`.
>
> P0, P1-b and P1-a1 are CLOSED. Do not reopen them or modify their historical evidence.
>
> ### Objective
>
> Establish a semantic distinction between:
>
> - An expression evaluated to a value.
> - An addressable scalar variable.
> - An addressable array element.
> - A formal parameter referring to a caller-provided entity.
> - An actual argument whose passing semantics are not yet established.
>
> This distinction must be represented without embedding Intel 8080 addresses, DR-specific descriptors, PLILIB conventions or MIR instructions.
>
> The long-term objective is to allow multiple backends to implement PL/I parameter semantics correctly, without duplicating the frontend.
>
> ## 1. Recovery and preregistration
>
> Read:
>
> - `AGENTS.md` and `PROTOCOL.md`
> - `spec/lab-evidence/e2e54/PLAN.md`
> - `spec/lab-evidence/e2e54/RESULTS.md`
> - `docs/architecture/backend-boundary.md`
> - `ocaml/hir/{semantic_env,hir,hir_build,backend,semtest}.ml`
>
> Verify HEAD, guard status, worktree dirt, the historical compiler fingerprint and the existing HIR tests.
>
> Write the complete P1-a2 preregistration in `spec/lab-evidence/e2e54/PLAN.md` and commit it before any source changes.
>
> No oracle calls are authorized.
>
> ## 2. Audit parameter semantics FIRST
>
> Inspect the current binder and historical code generator.
>
> Identify the actual sources of information about:
>
> 1. Formal parameter declarations and types.
> 2. Procedure signatures and arity.
> 3. Actual argument syntax and resolved types.
> 4. Passing by value, reference, descriptor or other mechanisms.
> 5. Array-element actuals versus whole-array actuals.
> 6. Aliasing between actual parameters.
> 7. Modifications to a formal becoming observable by its caller.
> 8. Evaluation order of actual argument expressions.
>
> For every finding classify the evidence as:
>
> - Bind-authoritative semantic fact.
> - PL/I language rule with explicit supporting documentation.
> - DR implementation-specific behavior backed by existing claims/goldens.
> - Unmeasured or unknown.
>
> Important: a pointer cell or descriptor emitted by DR is evidence about DR's ABI. It is not automatically a portable semantic rule.
>
> Read existing claims and goldens selectively where necessary. Do not create new oracle evidence.
>
> ### Existing evaluation-order assumption
>
> The P0 HIR describes call arguments as evaluated left-to-right.
>
> Audit whether the available evidence really establishes this as an execution-order guarantee, rather than merely source order.
>
> If not established, record this limitation explicitly and propose a representation distinguishing ordered argument positions from guaranteed evaluation order.
>
> Do not silently perpetuate an unsupported execution-order assumption.
>
> ## 3. Semantic_env extension
>
> Expose the smallest justified formal/actual semantic interface.
>
> The interface should distinguish:
>
> - Parameter identity.
> - Declared semantic type.
> - Procedure ownership and lexical scope.
> - Parameter position.
> - Available passing-mode evidence.
> - Unknown or unsupported passing modes.
>
> Retain Bind as the sole authoritative source for its recorded facts.
>
> Do not independently derive procedure signatures from AST syntax when Bind provides an authoritative signature.
>
> Use AST solely for explicitly identified structural or syntactic facts.
>
> The public projection must contain no physical descriptor layout, stack offset or machine address.
>
> ## 4. HIR reference model
>
> Extend the existing addressability model introduced by P1-a1.
>
> Represent a designator separately from reading its value.
>
> A scalar variable and an indexed array element should be usable as addressable argument candidates.
>
> Avoid adding an unrestricted pointer type with invented dereference semantics.
>
> Introduce explicit actual-argument forms or passing requirements only where justified by evidence.
>
> The representation must make it impossible for a backend to silently treat an unresolved reference-passing requirement as ordinary by-value passing.
>
> A semantically unknown case must remain explicitly unknown or be rejected with a stable diagnostic.
>
> Keep the distinction between:
>
> - Source-level aliasing and reference semantics.
> - Physical pointer and descriptor representations selected by a backend.
>
> ## 5. Narrow lowering subset
>
> Use existing P0 and P1-a1 functionality.
>
> Target a small representative set of internal procedure calls involving:
>
> - Scalar variable actuals.
> - Constant or arithmetic-expression actuals.
> - An array element actual.
> - Formal parameter reads and writes, where supported.
> - Two formals receiving potentially aliased actuals.
>
> Only admit forms whose semantic passing requirements can be justified.
>
> Where evidence is insufficient, create a negative test with a precise diagnostic, rather than inventing behavior.
>
> Do not support whole-array actuals, arbitrary pointer dereferences, based structures or external ABI calls merely because their syntax parses.
>
> A valid outcome is a small number of supported new constructs plus accurately documented unsupported cases.
>
> ## 6. Semantic-authority tests
>
> Extend `semtest` to verify the new reference and parameter relationships against the live Semantic_env.
>
> Include non-vacuous corruption controls for:
>
> - Wrong formal identity.
> - Wrong actual-reference base.
> - Wrong argument position or type.
> - Wrong known passing requirement, if such a requirement is represented.
>
> Preserve H01–H15 and their existing expected outputs and diagnostic contracts unless an explicit, evidence-backed adjudication requires a change.
>
> Add new positive and negative fixtures with reviewed expected dumps.
>
> Check deterministic output and refusal behavior.
>
> Do not let tests silently skip reference checks because the selected fixture happens not to exercise them.
>
> Use bounded execution: the pre-existing BEGIN/DO discovery hang remains out of scope.
>
> ## 7. Historical compiler invariants
>
> Mandatory:
>
> - `pli80c.exe` SHA-256 remains exactly `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`.
> - Full compile-tier gate RC 0.
> - Historical byte-exact panel: 1328/1328.
> - Negative panel: 190/190.
> - Divergence panel: 9/9.
> - Coverage: 149 rows, zero errors and warnings.
> - Historical census: 16 EXACT, 0 DIFFERS, 25 REFUSED, 3 NO_ORACLE.
> - Claims ledger remains at C380.
> - No modification to historical golden objects, inventory, census or coverage.
>
> Keep `ocaml/lib/` and `ocaml/bin/` byte-identical.
>
> Keep the separate `ocaml/hir/` build isolation that preserves the historical executable fingerprint.
>
> Run the existing HIR test suite and full compile-tier gate. Do not launch the external rune-ci runtime/audit tiers for this HIR-only phase.
>
> ## 8. Deliverables
>
> Produce and commit:
>
> - P1-a2 preregistration.
> - Parameter-passing evidence and unknowns matrix.
> - Semantic_env extensions.
> - HIR designator and argument representation, as justified.
> - Narrow HIR lowering extensions.
> - Positive and negative fixtures.
> - Semantic-authority and corruption tests.
> - Updated `docs/architecture/backend-boundary.md`.
> - P1-a2 RESULTS and full regression measurements.
> - A proposed next-step roadmap.
>
> Any unsupported or unproven construct must be reported as such, never counted as supported merely because a HIR node exists.
>
> ## 9. Scope discipline
>
> Do not implement MIR generation.
>
> Do not introduce a second binder or type checker.
>
> Do not refactor historical Codegen.
>
> Do not fix the BEGIN/DO hang incidentally.
>
> Do not expand PUT/GET, decimal typing or the DR-specific ABI.
>
> Do not modify `GOAL.md` or previous scientific evidence.
>
> Never stage `handoff.config.json`, destroy unrelated working state or push.
>
> Use explicit-path commits and safe Handoff renewals.
>
> At completion, close P1-a2, attest the checkpoint and STOP. The successor phase requires a separate operator decision.
>
> ### Success criterion
>
> The HIR can accurately distinguish procedure argument values from addressable references, and can represent or explicitly refuse the parameter semantics required by future code generators.
>
> Every accepted semantic fact has identifiable provenance. Every unknown remains visible.
>
> Historical byte-exact compilation is unchanged.
>
> **Operator authorization: E2E-54/P1-a2 is approved. Preregister and proceed.**

(Verbatim law: the block above is the operator brief EXACTLY as recovered from the parent
transcript `01a1beba-124f-74ee-84fe-84e837f466b2` into the ignored file
`build/p1a2-brief-recovered.md` (224 lines, sha256
`58fb3e4f0f3acb6ffa0ac8bb4fa8fdf6aa8a69056667ad4ad4462b27881a6ecd`), every line prefixed
with the markdown blockquote marker `> ` and NOTHING else — headings un-demoted, blank
lines carried as bare `>`. The embedding was machine-verified line-by-line: stripping the
`> ` prefix from the embedded block reproduces the source file byte-for-byte
(`cmp` rc 0, 224/224 lines). The P1-a1 tooling law applies: a blockquote must prefix
EVERY line, verified against the source, never transformed-and-trusted.)

### P1-a2.1 Parameter-semantics evidence and unknowns matrix (brief §2 audit, CLOSED)

Audit method (hops 1–2, sessions 01a1beba/01a1beca): all six `ocaml/hir/` units read in
full; the binder authorities read first-hand at `ocaml/lib/bind.ml` — `call_site`
(`:1650-1669`), `proc_layout.pl_ptrs` (`:1952`, built `List.mapi (fun i f -> (f, base +
2*i)) formals` at `:2557`), the passing-mechanism decision tree `section2`
(`:~2370-2545`), the call-site collector `pl_stmt_calls` (`:2052+`); claim bodies read:
**C093** (`spec/CLAIMS.md:859`; the predecessor hop quoted `:855` — the heading is
measured at `:859`, the four-line slip recorded, content unchanged), **C130** (`:2036`),
**C358** (`:8480`) as `## C` ledger headers, and **C145** (`:2668`, §E2E-14 header
`:2665`), **C167** (`:3196`), **C172** (`:3369`), **C173** (`:3391`), **C175** (`:3415`)
as inline `Cnnn.` paragraphs under `## E2E-nn` phase headers — quoting them never moves
the 203-header ledger count. Evidence classes are the brief §2 four-way classification.

**STANDING LAW (all rows, verified first-hand):** every `cs_slot`, `cs_temps`,
`cs_copies` and `pl_ptrs` integer is a **PHYSICAL DATA address, pool-exclusive**
(`bind.ml:1650-1669`; the `cur` allocation fold at `section2`). It is evidence about
**DR's ABI**, never a portable semantic rule (brief §2 warning). **No such integer ever
crosses the HIR seam**: the `Semantic_env` projection converts every cell fact to a
SYMBOLIC classification at its first touch (the same first-touch drop law as the P1-a1
element width, §P1-a1.4), and falsifier T6 below greps for it. The `cs_args` lists are
physical AST node identities — the env may use node IDENTITY for matching and SYNTAX for
classification, and exports nothing but names, positions and symbolic modes.

| # | Question (brief §2) | Finding | Class | Anchor |
|---|---|---|---|---|
| 1 | Formal parameter declarations and types | Bind lays one 2-byte pointer cell per formal in **bind's own formal order** (`pl_ptrs` keys, `List.mapi` at `bind.ml:2557`); the ORDER is semantic (position i of the signature), the ADDRESS is physical and dropped. A formal WITH an explicit `dcl` row carries its declared type as a bind row in the callee block (fact A-1 re-applies: an array-named formal SHARES the element-type row — hence the `cs_dec` array-formal exclusion). A formal WITHOUT a row gets none: P0 already refuses (`HIR-E03` wording, pinned by H07). | [bind-fact] | `bind.ml:1952`, `:2557`, `:2411-2433`; `semantic_env.ml` `proc_sig.sptrs/sptr_count`; §P1-b.2 Bind-flat-registry law |
| 2 | Procedure signatures and arity | Arity is `sptr_count` (the `pl_ptrs` cell count), returns is `pl_ret`/`sret_pr`, recursion is `pl_rec`/`pl_attr_rec`; external entries live in the separate `pl_exts` channel (params count, ret, ptypes). No HIR-side signature may ever be re-derived from AST syntax where bind provides the record (brief §3). | [bind-fact] | `bind.ml:1952-1974`; `semantic_env.ml` `sig_of_pl`, `entry_sig`; semtest I4/I5 (live) |
| 3 | Actual argument syntax and resolved types | Bind records every call site's argument EXPRESSIONS in source order as `cs_args : Ast.expr list` (physical nodes of the same parsed tree; collector `pl_stmt_calls`, statement calls included). Bind records NOTHING about whether an actual's type matches the formal: no claim, golden or probe measures a DR actual/formal type-compatibility rule. | [bind-fact] (syntax, order) / **[unmeasured]** (type compatibility) | `bind.ml:1651`, `:2052-2135`, `:2541`; §P1-a1 fact A-4 (binder blind to index expressions) generalizes |
| 4 | Passing by value, reference, descriptor or other | The CALLER allocates one 2-byte pointer cell per argument, contiguously, contents = link-time address constants, emission interleaved per argument; ONE `LXI H,*A(slot)`+CALL for the block; arity-1 peeled deref vs arity≥2 block copy. In bind's own record: `cs_temps i = Some` **iff** arg i is an expression needing a value cell — bare names, `Enumber` and array-ELEMENT actuals get NONE (`:2448-2457` comment: "getting this wrong would add a DATA byte AND shift every later anonymous-cell number"); DEC expression actuals size at the FORMAL width (`cs_dec`, [E2E-52/P3-13]); DEC widening copy-in temps (`cs_copies`, [C358]) EXCLUDE caller-formal names (E27B forwarding), STATIC rows, array heads and recursive/RECURSIVE callees. | [DR-ABI-backed] (the descriptor/cell machinery) + [bind-fact] (the per-position records are bind's) | [C093] `CLAIMS.md:859-887`; [C145] `:2668` (two-phase numbering); [C358] `:8480`; `bind.ml` `section2` `:2376-2545` |
| 5 | Array-element vs whole-array actuals | **There is NO array calling convention**: an element actual rides the ordinary pointer-formal descriptor (constant index `LXI H,<a+off>;SHLD`; runtime index the ladder then `SHLD`), bind allocates it NO value cell, and the EA2 RUNTIME witness proves the callee mutated the ORIGINAL cells through both index forms. A WHOLE array as an actual is UNMEASURED (no claim, no golden) — and C175's "no array calling convention" is exactly why inventing one is forbidden: refused BY NAME on the new code E15. | [DR-ABI-backed] (element) / **[unmeasured]** (whole array) | [C175] `CLAIMS.md:3415-3433` (AB7, PASSARAY, EA2 runtime); `bind.ml:2389-2401` (`is_arr_hd`) |
| 6 | Aliasing between actual parameters | Two actuals naming the same variable (or the same array) receive descriptor cells whose contents address the SAME caller cell — the descriptor law of [C093] makes this the only coherent reading, but NO experiment runs a program whose callee mutates through two aliased actuals: multi-actual aliasing is **[unmeasured]**. The HIR therefore makes aliasing VISIBLE (two designators with the same sid/base) and asserts NOTHING about it; the subset admits aliased pairs because reference semantics [C093] is per-argument and copying would contradict it — recorded as a representation choice pending measurement. | [DR-ABI-backed] per-argument reference; **[unmeasured]** aliased-pair runtime | [C093] `:880+`; [C130] `:2036` (E28C: mutation reaches the original cell TWO levels up) |
| 7 | Formal modifications visible to the caller | **Formals are passed BY REFERENCE, so writing a formal writes the caller's variable** — [R2011 runtime: `mid` received `a` and 3 became 5]; E28C repeats it through a FORWARDING formal (prints 3, not 2). The old codegen still refuses formal stores (`store to pointer formal unproven`, negative N55) — that is the HISTORICAL backend's caution, not a language or HIR rule; the HIR records the reference requirement and lets a backend decide. | [DR-ABI-backed] | [C093] `CLAIMS.md:880-887`; [C130] `:2036-2065` |
| 8 | Evaluation order of actual argument expressions | ADJUDICATED in §P1-a2.2: DR's EMISSION order per [C093] (interleaved, source order) backs the dump wording; E28B pins argument POSITIONS semantically (a swap prints 35, the linked program prints 53). Language-level order of EVALUATION remains **[unmeasured] [TBD]**. | [DR-ABI-backed] (emission) / [unmeasured] (language) | [C093] `:876-880`; [C130] E28B semantic witness `:2036+` |

Gap rows honest-by-construction (brief §2 "Unmeasured or unknown" is a real category):
actual/formal TYPE compatibility (row 3), whole-array actuals and multi-actual aliasing
runtime (rows 5, 6), language evaluation order (row 8), and the BY-NAME default semantics
of PL/I actuals (DR implements address passing; the language rule itself is not
documented-support by any manual read in this campaign → **[unmeasured]**, never cited).

### P1-a2.2 The ORDERED-vs-EVALUATION-ORDER adjudication (brief §2, DECIDED not deferred)

Reproduced from `LEARNINGS.md` § "E2E-54/P1-a2 hop 2" and the `PROGRESS.md` hop-2
heading, which are the accepted records:

> **ADJUDICATION (brief §2 "existing evaluation-order assumption") — DECIDED, not
> deferred:** the dump wording `args left-to-right` is NOT an unsupported claim needing
> retraction — it is DR-ABI-backed for the measured shapes by [C093] (interleaved
> per-argument materialisation, source order). But it is an *emission*-order fact about
> DR's ABI, not a portable PL/I execution-order guarantee, and PL/I language
> order-of-evaluation of actuals remains **[unmeasured]/[TBD]**. DECISION: KEEP the
> wording (H01–H15 bytes stay frozen — NO named drift needed) and document in
> `PLAN.md` §P1-a2 + the `hir.ml` header that the ordered `arg N` list is a
> REPRESENTATION ordering (source/positional order = bind's own `cs_args` order) whose
> only backed execution-order evidence is [C093] for internal fixed-type calls, with
> DEC/array/external shapes unmeasured.

Consequences fixed by this slice: the `hir.ml` header gains exactly that documentation;
no dump byte changes; `Hir` keeps argument POSITIONS (`arg N` = bind formal position,
per [C093]'s per-argument law), never claiming an evaluation ORDER beyond the cited
emission evidence. The brief's alternative ("propose a representation distinguishing
ordered argument positions from guaranteed evaluation order") is satisfied by the type
itself: an ordered list of positions, each carrying a passing REQUIREMENT, no node
claiming order-of-evaluation.

### P1-a2.3 `Semantic_env` parameter-API amendment (brief §3)

Additions ONLY; nothing existing changes shape (P1-a1 precedent: append and document).

1. **Passing-mode evidence (symbolic, offsets dropped at first touch):**

   ```ocaml
   type passing_mode =
     | PM_value_cell    (** bind allocated an anonymous value cell (cs_temps Some) [C145] **)
     | PM_own_cell      (** no cell: a bare name or array-ELEMENT actual designates its own storage **)
     | PM_immediate     (** Enumber actual: bind allocates no cell; DR materialises a descriptor constant [C093] **)
     | PM_copy_in       (** cs_copies Some: DEC widening copy-in temp [C358]; outside the lowering subset, refused by rule **)
     | PM_unknown       (** typed unknown: bind's record and the argument syntax disagree — never silently lowered **)
   ```

   `t` gains a private projected-site table built ONCE in `create` from
   `plan.Bind.pl_calls`: `{ cs_proc; cs_args }` kept VERBATIM (names and physical node
   identities), while `cs_temps`/`cs_copies` are projected to `bool list` (Some→true)
   and `cs_dec` is carried as-is; `cs_slot` is DROPPED at first touch — no integer ever
   enters the env record (T6 grep below pins the readers).

2. **Lookup:** `call_evidence : t -> caller_scope:int -> callee_key:string ->
   Ast.expr list -> call_evidence option`. Matching law: the first recorded site (bind
   DFS order) whose `cs_proc` equals the lowered callee key and whose `cs_args` are
   PHYSICALLY (`==`) the same `Ast.expr` nodes being lowered. Determinism: `cs_args`
   nodes are the very nodes of the parsed block handed to `Hir_build.build` (verified
   first-hand: the collector walks the AST; `bind_program` is re-run on the SAME tree),
   so identity is stable across the two bind reads in a process; two zero-arity sites to
   the same callee are indistinguishable but carry EMPTY evidence lists, so first-match
   is provably harmless. Per position `i`, the mode is computed by bind's OWN
   discriminators, never re-derived: `copies[i]` ⇒ `PM_copy_in`; else `temps[i]` ⇒
   `PM_value_cell`; else the argument SYNTAX (an [O]-class organization, like the Formal
   flag): `Eident` ⇒ `PM_own_cell`, `Enumber` ⇒ `PM_immediate`, a 1-subscript `Esuffix`
   on a name whose env symbol carries `e_array = Some` ⇒ `PM_own_cell`; anything else —
   including `temps[i] = true` on a bare name/`Enumber`/element (an internal
   inconsistency) — ⇒ `PM_unknown`. `None` (no recorded site) is a typed absence: the
   LOWERING refuses loudly (E16), never assumes a mode.

3. **Formal descriptions (identity, position, type, ownership):** `proc_sig` gains
   `sformals : formal_desc list`, computed in `register_block` from bind's own views:

   ```ocaml
   type formal_desc = {
     f_pos   : int;            (** 0-based, bind pl_ptrs order **)
     f_key   : string;         (** lowered formal name (bind fact) **)
     f_sid   : int option;     (** env symbol in the CALLEE's own scope; None = bind laid no row **)
     f_stype : stype option;   (** declared row type; None exactly when f_sid is None **)
     f_scope : int;            (** owning (callee) scope — ownership and lexical scope, brief §3 **)
   }
   ```

   Resolution is the callee block's OWN `esyms` association (never `resolve` up the
   chain: a formal that shadows an outer name is the [C358] shape — the callee's row
   wins). `f_sid` is the same sid the env assigned to that row (§P1-b identity contract
   unchanged). Accessor `formals_of : t -> int -> formal_desc list option` (None = no
   bind signature; typed `Not_found` for an out-of-range pid, as §P1-b.2).

4. The public interface still references NO `Hir` type (S8), exports no integer that is
   not an identity/position/line (S8/T6), and Bind remains the sole authority (S5).

### P1-a2.4 HIR designator and argument representation (brief §4)

P1-a1 introduced designation for assignment targets (`target = T_var | T_elem`). P1-a2
generalizes the SAME notion — a designator is a location designation whether it is an
assignment target or an argument reference — and keeps it distinct from value expressions:

```ocaml
type designator =
  | D_var of { sid : int }
  | D_elem of { base : int; subs : expr list }   (** exactly one subscript (subset gate) **)

type target = designator      (** Assign.target keeps its name; T_var/T_elem RENAME to D_var/D_elem **)

type actual_form =
  | A_value of expr
      (** by-value requirement: the callee receives a value; the caller's storage is NOT
          addressable through it. The expression is never itself a bare-name read on this
          path: the classifier routes every bare name/element actual to A_reference. **)
  | A_reference of designator
      (** reference requirement: the callee can read AND write the designated caller cell
          [C093 R2011; C130 E28C; C175 EA2]. Constructed ONLY by the classifier from a
          bare name or an element designation — never from an expression. **)

type actual = { af : actual_form; ac_ty : ty; ac_ef : ef_kind; ac_line : int }
```

`Call_e.args` and `Call_s.args` become `actual list`. The representation law the brief
demands ("impossible for a backend to silently treat an unresolved reference-passing
requirement as ordinary by-value passing") holds BY CONSTRUCTION: the two requirements
are different constructors; there is no bool, no default, and no `A_value` ever built
from a bare name or element designator (the lowering and semtest I11/I12 both police it).
An unclassified case is NEVER representable — lowering refuses (E15/E16/E17) instead of
inventing a node. No unrestricted pointer type and NO invented dereference is added:
`Ptrty` stays as P0 had it, and no HIR node dereferences anything.

**Dump rendering (T2 law — H01–H15 bytes FROZEN):** the call lines keep their exact
current text (`call proc(N) ... [args left-to-right]`, adjudication §P1-a2.2), the
`arg i` label lines stay, and a nested argument prints at `indent + 2` (the P0 hop-4
indent law). `A_value e` prints `dump_expr e` — byte-identical to today (H04's
`const 2 : ... [pure, line 3]`). `A_reference (D_var {sid})` prints exactly the line the
old `Var` node printed: `var sym(%d) : %s  [%s, line %d]` with `ac_ef` (pure) — H03's
arg 0 byte-for-byte. `A_reference (D_elem ...)` prints
`elem_ref %s : %s  [%s, line %d]` (designator rendering via the shared
`dump_designator`, the old `dump_target` generalized; the assign-target bytes are the
same lines, so H08/H09/T_elem pins are untouched — the rename changes NO bytes). No new
dump line ever carries a size, count or address (F4/T6).

`hir.ml` header gains: the §P1-a2.2 adjudication paragraph (ordered representation,
[C093]-backed emission, language order [TBD]) and the P1-a2 representation notes above.

### P1-a2.5 Narrow lowering subset (brief §5) and BY-NAME refusals

Internal, non-recursive callees only (existing E07 recursion refusal UNCHANGED); arity
from bind `sptr_count` (existing E07 wording unchanged). Argument positions lower through
the env evidence (§P1-a2.3) with this decision list — every admitted form traces to a
matrix row:

- **bare caller variable** (auto/static OR formal — a formal forwarded onward is [C130],
  the E27B route bind itself licenses by suppressing the copy-in) with `PM_own_cell`,
  env symbol projected and NOT an array ⇒ `A_reference (D_var sid)`; the read-only flag
  mirrors the existing Var lowering (`addressable = true` semantics, designators ARE
  locations);
- **array element actual** (1-subscript `Esuffix` on an `e_array` name) with
  `PM_own_cell` ⇒ `A_reference (D_elem ...)` — subscript lowered through the EXISTING
  `lower_index` (constant in-bounds rule, E12/E14 wording unchanged) [C175];
- **constant / arithmetic / nested-call expression actual** with `PM_immediate` (literal)
  or `PM_value_cell` (any other expression, incl. a nested call — the [C145] `D3` shape)
  ⇒ `A_value (lower_arith expr)` — the EXISTING expression gate unchanged inside;
- **type discipline:** every actual must have the callee's declared formal type EXACTLY
  (`f_stype` through the P0 gate, image `ac_ty = formals type`): any mismatch refuses
  with the NEW code **E17** naming both types and marking DR's conversion behaviour
  **[TBD]** — row 3 of the matrix says NO evidence licenses a silent conversion, so none
  is invented (H03/H04 are type-equal; their bytes do not move);
- **statement-position calls WITH arguments** (`call p(x);` — the parser's Esuffix
  target) now lower to `Call_s` (today they die on the pre-existing E04 wording "only
  direct procedure calls are lowered in P0" — this is the INTENDED new coverage, brief
  §5; no fixture pins that text, recorded as an honest behaviour change); the zero-arg
  `call q;` / `q;` path keeps its EXACT current route and bytes.

New codes (appended; existing codes keep their meaning — T10):

- **HIR-E15 `e_arg_whole_array`** — whole-array actual: `call p(a);` where `a` projects
  `Array1`. BY NAME, element designators only, [C175] "no array calling convention" +
  row 5 unmeasured. (Behaviour change, recorded: TODAY that input dies on E13
  `whole-array use of a is outside the P1-a1 subset (element references only)` from the
  value path; P1-a2's argument classifier owns argument position, E13 keeps its P1-a1
  meaning for value/target positions. NO existing fixture passes an array as an actual —
  H19 measures the new pin; the E13 wording itself is untouched and still pinned by H13.)
- **HIR-E16 `e_arg_evidence`** — typed-unknown passing evidence: no recorded bind site
  matches the call node, or a position classifies `PM_unknown`, or an admitted shape is
  contradicted by bind's record. UNREACHABLE by construction if bind's collector is
  exhaustive (it claims to be — the [E2E-11/CALL] full-coverage note); documented as an
  UNEXERCISED defensive witness exactly like the P0 `dup_free` and P1-a1 §P1-a1.5(e)
  guards — never fitted, never silently accepted.
- **HIR-E17 `e_arg_type`** — actual/formal declared-type mismatch at an argument
  position, naming both sides and quoting the [TBD].

Refusal order INSIDE `lower_call` is frozen as today: callee lookup → arity check →
argument lowering (this is where E15/E16/E17 fire) → recursion check → RETURNS gate.
BASED / POINTER-typed actuals, qualified names (`a.b`, `a->b`) and built-ins never reach
the classifier: their declared types die at `project_syms` (E02, unchanged) or at
`lower_expr`'s existing E04/E06 wording; a call to an EXTERNAL entry dies today on the
pre-existing E06 "no bind-registered procedure" wording (the registry admits only
`pl_procs`/`pl_top`) — recorded honestly as an EXISTING named refusal, NOT a new code;
this slice adds no reachability there.

### P1-a2.6 Semantic-authority tests (brief §6): invariants I11–I13 + corrupt controls

A NEW collection pass `collect_calls : Hir.program -> call_site_item list` walks bodies
and returns, per call, the OWNING proc, callee pid and the `actual list` itself — the
walked REFERENCE ITEMS (`R_var`/`R_call`/`R_elem`) and their counts DO NOT CHANGE (an
`A_reference` designator still contributes exactly the item its old expression node
contributed), so every existing `SEMANTIC-AUTHORITY OK n/m` line keeps its measured
numbers. All three new invariants judge the LIVE env (and through it bind), never dump
text (S6 law), and each is driven by a SHARED comparison function also used by its
corrupt control (non-vacuity law, §P1-a1.7).

- **I11 designator soundness:** every argument `A_reference`: `D_var sid` resolves — via
  `SE.symbol` AND via `SE.resolve` from the CALLER's scope back to that same sid
  (shadowing-aware, the I2 comparison function reused verbatim) — and its env symbol has
  `e_array = None` (a whole array can never be a designator); `D_elem base subs` runs the
  EXISTING `elem_ref_mismatch` (the I8 function) with the owning caller proc.
- **I12 passing-evidence alignment:** for every collected call, `SE.call_evidence` from
  the CALLER's scope answers `Some ce`; `List.length ce.ce_args = nargs = arity
  (sptr_count)`; and per position: `A_reference` ⇒ `PM_own_cell`;
  `A_value (Const _)` ⇒ `PM_immediate`; any other `A_value` ⇒ `PM_value_cell`;
  `PM_copy_in`/`PM_unknown` can never back an admitted HIR node. Shared comparison
  `arg_evidence_mismatch env caller_pid callee_key args : string option`.
- **I13 formal-API alignment:** for every HIR proc, `SE.formals_of pid` answers `Some`
  with `f_pos = i` in order, `f_key` = the `sptrs` entry, `f_sid = Some params[i]`
  (P0's explicit-dcl gate already refuses `None`), and `f_stype` = the env row behind
  that sid — the formal ORDER contract (matrix row 1/2) checked against bind, not AST.

Corrupt controls (each perturbs ONE input, re-runs THE SAME comparison, and must see it
REJECT; each prints `nothing was proven` LOUDLY (rc 1) when the fixture has nothing of
that kind):
- `--corrupt-formal` — swap two `f_sid`s (or shift one by +1000) before the I13
  comparison (wrong formal IDENTITY);
- `--corrupt-actual-base` — repoint one argument designator's sid at a different
  projected symbol before the I11 comparison (wrong ACTUAL base);
- `--corrupt-arg-position` — drop one `ce_args` position (arity disagreement) or replace
  one mode by a different position's before the I12 comparison (wrong argument
  POSITION-or-TYPE);
- `--corrupt-mode` — flip one `PM_own_cell` to `PM_value_cell` (or vice versa) before
  the I12 comparison (wrong PASSING REQUIREMENT).

Output contract unchanged: live rc 0 exactly one `SEMANTIC-AUTHORITY OK` line, empty
stderr; every control rc 1, ZERO stdout, all-`SEM-FAIL:` stderr (S6/T7).

### P1-a2.7 Fixture plan (MEASURED pins — expected files are copies of reviewed actual output, never hand-written)

Ids verified UNUSED first-hand TWICE (hop 2 at `71ee96d0`, this hop before writing):
`ls hir/fixtures | grep -c 'H1[6-9]\|H2[0-9]'` = 0. All fixtures CRLF line endings +
`^Z` terminator (P0 law: bare LF shifts every line), **ONE dcl item per statement**
(the standing convention), every fixture run under `timeout 60`.

- **H16 (positive):** statement-position call WITH arguments — `call bump(x, y + 1);` —
  callee formal READ and formal WRITE in the body (row 7 shapes; the write is legal in
  HIR representation, its runtime visibility [C093]-backed). Exercises `Call_s` with
  `A_reference` + `A_value(PM_value_cell)`.
- **H17 (positive):** array-element actuals `call bump(a(2), i);` (constant index) and
  an ALIASED pair `call bump(x, x);` (row 6, representation-visible aliasing).
- **H18 (positive):** forwarding chain `call outer(x); outer: procedure(y); call inner(y);`
  ([C130] E27B/E28C shape, two levels; inner writes y — the HIR records both reference
  requirements).
- **H19 (negative, ONE refusal):** whole-array actual `call bump(a);` ⇒ E15 pin.
- **H20 (negative, ONE refusal):** precision-mismatched actual `dcl v fixed bin(7);
  call bump(v);` (formal bin(15)) ⇒ E17 pin.
- **H21 (positive):** nested call actual `y = dbl(dbl(2));` — the [C145] two-phase value
  cell shape in HIR representation (`A_value (Call_e ...)`), arity/RETURNS gates
  unchanged.

`E16` gets NO fixture by design: it is a defensive witness (see §P1-a2.5); if any probe
makes it fire, that is a falsifier STOP, not a fixture. Predictions for review BEFORE
pinning (falsify, never fit): H16's dump is the existing `call proc(N)  [line L; args
left-to-right]` line + `arg 0`/`arg 1` labels + designator/value lines as §P1-a2.4
specifies; no existing expected byte moves; the OK-line counts for H01–H09 stay exactly
as recorded at §P1-a1 close.

### P1-a2.8 Falsification criteria (each a STOP-and-fix gate, modelled on §P1-a1.8)

- **T1** `pli80c.exe` sha256 stays `172595d5…` after EVERY build step, checked DIRECT
  (dune logs never print the sha — tooling law). Moved = STOP and attribute first-hand.
- **T2** `git diff --exit-code -- hir/expected` CLEAN at every step: H01–H15 bytes and
  the superseded archive are FROZEN; the §P1-a2.2 adjudication is explicitly a
  keep-bytes decision; `hir/expected/superseded/` is never rewritten.
- **T3** FULL `python3 tools/e2e_gate.py` rc 0 with FROZEN counts **1328/1328, 190/190,
  9/9, coverage 149 rows 0/0, census 16/0/25/0, prose 5** →
  `build/gate-e54p1a2-reg.log`; ANY move = STOP, record VERBATIM, never force. Fresh
  `--build-dir _build-e54p1a2` rc 0 with ZERO `Error` (hist ≈122); the fresh-dir exe sha
  is checked against the KEPT exe (fresh-dir logs record rc+headers only).
- **T4** `ocaml/lib/`, `ocaml/bin/`, `golden/`, `spec/CLAIMS.md`, `spec/INVENTORY.txt`,
  coverage ledgers byte-clean vs HEAD; ledger stays **C380** (203 headers); NO new claim,
  NO coverage/inventory/golden touch; ZERO oracle in the whole slice.
- **T5** Bind seam: `hir_build.ml` (comment strip) mentions `Bind` ONLY at the EXACTLY
  two pinned lines (F10; today `:41` alias + `:557` `bind_program` — the pinned LINE
  CONTENTS, which edits may shift). NEW this slice: `pl_calls`, `cs_temps`, `cs_copies`,
  `cs_dec` and `bind_arrays` occur ONLY inside `semantic_env.ml` (projection) and
  `semtest.ml` (intentional authority reader) — RAW grep, comments included; `cs_slot`
  appears ONLY in `bind.ml` (no reader at all — its int is dropped unread).
- **T6** vocabulary: after the comment strip, `semantic_env.ml` and `hir.ml` contain NO
  `stride|offset|bytes|esz|size|reloc|pool|0x` match (existing grep) — and NO integer
  physicality enters the env record: the site projection carries booleans, names, AST
  node identities and positions ONLY (structural, reviewed line-by-line at commit).
- **T7** non-vacuity: live + ALL SEVEN corrupt modes (three existing + four new) run on
  EVERY positive fixture; each control rc 1, ZERO stdout, all-`SEM-FAIL` stderr; a
  fixture with nothing to perturb says `nothing was proven` LOUDLY.
- **T8** determinism: every fixture and every semtest invocation runs TWICE in fresh
  processes, byte-identical (rc, stdout, stderr) — the existing runner law.
- **T9** bounded execution: every fixture under `timeout 60`; the pre-existing BEGIN/DO
  discovery hang stays DOCUMENTED, never fixed here (brief §9).
- **T10** diagnostic stability: every code/wording for EXISTING paths byte-identical —
  H06/H07/H10–H15 pins unchanged, E13 keeps its P1-a1 value/target meaning; the NEW
  refusals get NEW stable codes E15/E16/E17 documented in `diagnostic.ml`; the ONLY
  sanctioned behaviour changes are the §P1-a2.5 statement-call-with-arguments acceptance
  and the whole-array-actual E13→E15 handover, each recorded here BEFORE any code byte.

### P1-a2.9 Work order (exact order — the successor contract)

1. (this commit) §P1-a2 pre-registration committed BY EXPLICIT PATHS (`PLAN.md` only),
   BEFORE any `ocaml/hir/` byte (PROTOCOL #1).
2. `ocaml/hir/semantic_env.ml` (§P1-a2.3) → `dune build` rc 0 → T1 DIRECT →
   `tools/hir_test.py` rc 0 (all existing green) → commit.
3. `ocaml/hir/hir.ml` + `ocaml/hir/hir_build.ml` + `ocaml/hir/diagnostic.ml`
   (§P1-a2.4/.5 — ONE commit: the `args : actual list` change breaks its consumers, the
   P1-a1 hop-3 law) → build rc 0 → T1 → hir_test rc 0 (H01–H15 ALL green, T2 clean).
4. Fixtures H16..H21 (§P1-a2.7): MEASURE outputs under `timeout 60`, review every dump
   line against §P1-a2.4 BEFORE pinning, expected files copied from measured output;
   hir_test rc 0 with the new fixtures picked up by the glob; commit.
5. `ocaml/hir/semtest.ml` (I11–I13 + four new corrupt modes) + `tools/hir_test.py`
   (new modes in `SEM_MODES`, the extended T5 grep list) → FULL `timeout 600
   python3 tools/hir_test.py` rc 0 → commit.
6. FULL gate rc 0 → `build/gate-e54p1a2-reg.log` (T3); fresh `dune build --build-dir
   _build-e54p1a2` rc 0 ZERO `Error` + kept-exe sha check.
7. CLOSE: `RESULTS.md` §P1-a2 (T1–T10 panel WITH measured values; every deviation
   recorded VERBATIM, never fitted — incl. whatever the measured fixtures actually say),
   `docs/architecture/backend-boundary.md` §7-3 (parameter/argument projection), PLAN
   dashboard row P1-a2 **CLOSED**, proposed next roadmap as **PROPOSED ONLY**; durables +
   guard checkpoint.
8. **STOP — close P1-a2 only. No MIR, no PUT/GET, no BEGIN repair, no further slice
   without a separate operator decision.**

### P1-a2.10 Expected outcomes (pre-registered, falsified-not-forced)

Frozen numbers stay frozen (T1/T3/T4). H01–H15 byte-stable through every step (T2/T10).
Six new fixtures (four positives, two negative pins), three new invariants, four new
corrupt controls, three new diagnostic codes, one env API amendment, one HIR type
amendment. Honestly open, predicted drift surfaces:
- the OCaml record-field evaluation-order law (§P1-b hop 2 measurement): every fixture
  carries exactly ONE refusal path, so a multi-refusal reorder should NOT appear; if it
  does, record VERBATIM;
- whether bind's site records really share PHYSICAL nodes with the CLI's tree (§P1-a2.3
  matching law) is ASSERTED from reading the collector but MEASURED only when H16 goes
  green — an E16 refusal on H16 is the falsifier for this assumption, and then identity
  matching is re-audited (never replaced by a positional guess);
- the alias-pair and nested-call shapes are [C093]/[C145]-adjacent but individually
  UNMEASURED at runtime; the fixtures pin HIR REPRESENTATION only — RESULTS §P1-a2 must
  say so next to each number;
- `nothing was proven` will fire on several positives for the new corrupt modes (H01–H02
  have no calls at all) — expected, loud, rc 1; not a failure.

### P1-a2.11 Dashboard update

| slice | status | gate log | notes |
|---|---|---|---|
| P1-a2 | **CLOSED 2026-11-10** | `build/gate-e54p1a2-reg.log` rc 0 FROZEN 1328/1328-190/190-9/9-149 rows 0/0-16/0/25/0-prose 5; fresh `_build-e54p1a2` rc 0 ZERO Error hist 122, sha == kept `172595d5…` | ZERO oracle; env passing-mode/formal API `426293dd`; HIR `actual`/`designator` + lowering `cfaad741`; fixtures H16–H21 `96e995fd`; semtest I11–I13 + 4 corrupt controls + hir_test SEM_MODES ×7 `735b43af`; T1–T10 ALL PASS (RESULTS §P1-a2); roadmap PROPOSED ONLY — STOP |

## §P1-h — Pre-registration: BEGIN/DO Discovery Hygiene (committed BEFORE any `ocaml/hir/` byte)

**Authorized by the operator 2026-11-10** (brief reproduced VERBATIM as §P1-h.0 below).
Campaign slice **E2E-54/P1-h** — the narrow, zero-oracle correctness repair of the HIR
procedure-discovery hang recorded as a pre-existing defect in §P1-b.5 note 3 (classified
at pre-migration `aaf295f0`). Type of work: **infrastructure correctness, ZERO oracle
calls** (none planned or authorized). Starting reference:
`cf6202bfa3eef1262b45f1ff41b30e63b81a7d28` (verified first-hand at this session's start).

**Baseline VERIFIED first-hand at session start (2026-11-10), not copied from the brief:**

- `git rev-parse HEAD` = `cf6202bfa3eef1262b45f1ff41b30e63b81a7d28` ✓ (the operator's
  stated starting reference; the tree carries only the operator's `handoff.config.json`
  edit — NEVER staged — plus ignored/untracked working debris, left untouched)
- `dune build` rc = 0; `sha256sum _build/default/bin/pli80c.exe` =
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` ✓
- `timeout 900 python3 tools/hir_test.py` rc = 0 — **120 ok** lines; ALL 11 semtest/live
  OK numbers at their pinned values (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3
  H09 3/2 H16 12/5 H17 12/5 H18 7/3 H21 5/2)
- FULL gate rc = 0 → `build/gate-e54p1h-baseline.log` (1537 lines): **1328/1328**
  byte-exact, **190/190** negative, **9/9** divergence, coverage **149 rows, 0 errors,
  0 warnings**, census **EXACT 16 / DIFFERS 0 / REFUSED 25 / NO_ORACLE 3**, prose **5** ✓
- `spec/CLAIMS.md`: 203 `^## C` headers; ledger ENDS **C380** ✓
- Guard budget: this is a FRESH operator-started session (`01a1bfe1…`, `reason: startup`);
  the last verified chain closed at 11/12 and the operator archived/reset it per policy —
  this session's chain count is 0 with cap 12 (`handoff.config.json`, authoritative).
  No renewal has been used or requested in this phase so far.
- Fixture ids **H22..H29 FREE**: `ls hir/fixtures | grep -c 'H2[2-9]'` = 0 and
  `ls hir/expected | grep -c 'H2[2-9]'` = 0 (the `H24..H29` hits in `tools/e2e_gate.py`
  are the unrelated `E36H*` specimen namespace).

P0, P1-b, P1-a1 and P1-a2 are CLOSED; this slice re-uses their evidence and touches
none of it. PUT/GET, MIR, the P2 oracle-typing campaign and broader scope refactoring
are explicitly NOT started or authorized by this slice (brief §7).

### P1-h.0 Operator brief (verbatim)

> # DRPLi — E2E-54/P1-h: BEGIN/DO Discovery Hygiene
>
> ## Operator authorization
>
> The operator authorizes E2E-54/P1-h, a narrow, zero-oracle correctness repair for the existing HIR procedure-discovery hang.
>
> Starting Git reference: `cf6202bfa3eef1262b45f1ff41b30e63b81a7d28`.
>
> P0, P1-b, P1-a1 and P1-a2 are CLOSED.
>
> This phase fixes a previously measured HIR infrastructure defect. It does not expand PL/I language semantics or modify the historical compiler.
>
> ## 1. First-hand recovery and preregistration
>
> Read AGENTS.md, PROTOCOL.md, E2E-54 PLAN/RESULTS and the active Handoff contract.
>
> Verify current HEAD, worktree state, guard budget and the full historical baseline.
>
> Preregister P1-h in `spec/lab-evidence/e2e54/PLAN.md` and commit before changing source.
>
> The known defect was recorded in P1-b:
>
> A statement-level `BEGIN` block causes `Semantic_env.register_children` to recurse into its enclosing block's original statement list instead of traversing the nested block.
>
> This creates an infinite discovery loop.
>
> Reproduce the failure under a short explicit timeout, preserving the witness and baseline exit status.
>
> Do not let the reproduction run indefinitely.
>
> ## 2. Root-cause audit
>
> Inspect `ocaml/hir/semantic_env.ml`, especially `register_children`.
>
> Confirm whether the current non-Bproc branch:
>
> ```ocaml
> register_children st plan parent
> ```
>
> revisits the same `parent.east.bstmts`.
>
> Review how procedure discovery and lexical ownership are currently distinguished.
>
> Establish the exact traversal requirements for:
>
> - A bare BEGIN.
> - Nested BEGIN/DO blocks.
> - Sibling procedures.
> - A procedure declared inside a BEGIN.
> - A BEGIN containing declarations.
> - A BEGIN nested inside a procedure.
>
> Do not infer new per-BEGIN lexical scope semantics: Bind does not currently expose them.
>
> ## 3. Minimal correction
>
> Separate:
>
> 1. The statement subtree being traversed.
> 2. The enclosing procedure's semantic environment.
>
> The traversal must descend into the nested block's statements while preserving the correct enclosing procedure context.
>
> Prefer a minimal structural visitor to a new semantic binder.
>
> Ensure each nested block is visited once along its structural path.
>
> Do not create new scope IDs for BEGIN/DO unless explicitly supported by existing semantic authority.
>
> Do not invent procedure signatures or symbol ownership.
>
> If a nested declaration cannot be represented safely, refuse with a typed diagnostic instead of silently flattening incompatible scopes.
>
> Preserve all existing procedure registration order, stable IDs and diagnostics wherever the behavior is already correct.
>
> ## 4. Focused regression witnesses
>
> Add independently reviewed positive and negative fixtures covering:
>
> - An empty BEGIN.
> - A BEGIN containing ordinary statements.
> - Two sibling BEGIN blocks.
> - Nested BEGIN blocks.
> - A procedure discovered beneath a BEGIN, where supported by Bind.
> - A BEGIN with declarations that must remain unsupported.
> - Existing procedure shadowing and forwarding behavior.
>
> Every fixture must terminate promptly.
>
> Include an independently checked structural traversal invariant and a non-vacuous corruption or regression control.
>
> A test that merely completes without hanging is insufficient: it must also verify that no statements or procedures were duplicated, dropped or assigned the wrong owner.
>
> Preserve all previously pinned HIR dumps and diagnostic bytes unless an explicitly documented correction requires a new expected result.
>
> ## 5. Historical invariants
>
> Mandatory:
>
> - No edits under `ocaml/lib/` or `ocaml/bin/`.
> - No oracle calls.
> - No changes to historical goldens, inventory, census or coverage.
> - No scientific claim beyond C380.
> - `pli80c.exe` SHA-256 remains `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`.
> - Full byte-tier gate RC 0.
> - 1328/1328 byte-exact, 190/190 negative, 9/9 divergence.
> - Existing HIR semantic-authority and corruption tests continue passing.
>
> Run build and test commands separately. Check every exit code directly.
>
> Do not invoke external rune-ci runtime or audit tiers for this HIR-only work.
>
> ## 6. Handoff budget
>
> The last verified chain was at 11/12 renewals.
>
> Inspect the current actual state before proceeding.
>
> Do not silently reset the chain or raise its cap.
>
> If renewal becomes unavailable, preserve the complete recovery state and finalize according to PROTOCOL.md. Report the actual reason.
>
> Do not use filesystem-wide discovery or unrelated infrastructure changes.
>
> ## 7. Deliverables
>
> - P1-h preregistration.
> - Reproducer demonstrating the original hang.
> - Minimal correction in the independent HIR path.
> - Focused positive and negative tests.
> - Structural discovery invariants.
> - Complete regression results.
> - Updated architecture and scientific campaign documentation.
> - Durable Handoff checkpoint.
>
> Use explicit-path commits; never stage `handoff.config.json`. Do not push.
>
> Close P1-h and STOP.
>
> Do not automatically begin PUT/GET, MIR, the P2 oracle-typing campaign or broader scope refactoring.
>
> **Success criterion:** BEGIN/DO discovery terminates correctly, procedure ownership and registration remain sound, unsupported scopes refuse explicitly, and historical compilation is unchanged.

Embedding law applied (LEARNINGS hop-2): every brief line carries the blockquote
prefix; the brief is otherwise byte-faithful — no word, number, path or constraint
altered. (Line-wrap inside the brief is the operator's own; this file reproduces it
as received in this session.)

### P1-h.1 Root-cause audit — MEASURED facts (this session, all first-hand)

Anchors verified first-hand at `cf6202b`.

- **M-1 Reproduction (pre-fix).** Three scratch inputs (`ocaml/scratch-p1h/`, never
  committed; raw witness kept at `build/e54p1h-hang-witness.log`), each under
  `timeout 20` — never run unbounded:
  - `BEG1.pli` — bare statement-level `begin; x = 1; end;` in main ⇒ **rc 124**
    (timeout), ZERO stdout, ZERO stderr.
  - `BEG2.pli` — Bproc sibling `p` FIRST, then a bare BEGIN ⇒ **rc 2**
    `HIR-E11: line 3: duplicate internal procedure name p (bind-legal? P0 refuses
    rather than guess)` — a BOGUS refusal: `p` was registered once by the first pass
    and AGAIN when the discovery re-walked main's list.
  - `BEG3.pli` — bare BEGIN nested inside procedure `p` ⇒ **rc 124** (timeout).
  Matches §P1-b.5 note 3 exactly (rc 124, no stack growth; bogus duplicate with a
  preceding sibling).
- **M-2 Defect site CONFIRMED.** `ocaml/hir/semantic_env.ml:511-563`:
  `register_children st plan parent` iterates `parent.east.Ast.bstmts` (:563). The
  non-Bproc branch (:559-561) calls `register_children st plan parent` — i.e. re-enters
  the SAME list, re-reading the SAME `Sproc` node forever. Answer to the brief's
  question: **yes**, the current non-Bproc branch revisits the same
  `parent.east.bstmts`. The Bproc branch (:518-556) is structurally correct
  (registry lookup, duplicate guard :540-543, pid/scope/sid pre-order allocation,
  recursive descent into the REGISTERED block).
- **M-3 Bind's own discovery law.** `ocaml/lib/bind.ml:2204-2231` (`collect` inside
  `bind_program`): for every `Ast.Sproc` child, **regardless of `bkind`**, bind descends
  (`else collect pb`, :2230); only `Bproc` children are registered (`bkind = Ast.Bproc`
  guard). Traversal is DFS, parents before children, source order within each list —
  the order `pl_procs` carries (`proc_layout` comment `DFS: parents before children`,
  `bind.ml:1975`). `collect` does NOT descend into `Sdobegin` lists, `Sif` arms or loop
  bodies (`_ -> ()`). The env's own comment (semantic_env.ml:507-510) states this mirror
  law; the buggy branch VIOLATED it.
- **M-4 No per-BEGIN lexical authority in Bind.** `Bind.frame_decls` (`bind.ml:390-408`)
  flattens `Sdcl` statements from the block's OWN statement region (descending into
  `Sdobegin` groups and `IF`/`DO WHILE` bodies) but **stops at `Sproc`** (`Sproc _ -> ()`,
  :403): a declaration written inside a BEGIN block produces NO row in the enclosing
  frame. Measured witness `BEG4.pli` (BEGIN placed inside an `IF` arm so discovery is
  not the blocker): **rc 2, `HIR-E03: line 5: declaration x produced no bind row in this
  block`** — the LIVE typed refusal channel for BEGIN-contained declarations is the
  existing `E03` no-bind-row arm of `lower_stmt`'s `Sdcl` case, NOT the `bdecls <> []`
  `e_scope` guards (`hir_build.ml:676-680` and `:954-958`): the parser sets `bdecls = []`
  on BEGIN blocks (`parser.ml:889`), so those guards are DEAD for parser-produced ASTs.
  Recorded honestly; the dead guards are NOT removed (they still guard structurally
  built blocks; removal is scope change, §P1-b.4 fact 2 unchanged).
- **M-5 DO groups refuse by name at lowering.** A bare `do; … end;` is an `Sdobegin`
  statement (parser law, recorded in bind.ml:1807-1809). Measured `BEG5.pli` (procedure
  inside a do-group) and `BEG6.pli` (plain do-group): both **rc 2, `HIR-E05: line 3:
  statement DO; group is outside the P0 HIR subset`** (`hir_build.ml:148`). Discovery never
  has to descend into `Sdobegin`: `collect` does not discover through it either (M-3), so
  nothing can be hidden from registration that bind itself hides, and lowering refuses
  the group loudly before any of its contents could be silently dropped.
- **M-6 Conditional-position nested procedures (PRE-EXISTING, out of scope, recorded
  not fitted).** Discovery walks only BLOCK-level statement lists (`collect` likewise).
  A procedure defined inside a conditional-position nested block is NOT bind-registered:
  `BEG7.pli` (`call p` to such a `p`) dies LOUD — rc 2 `HIR-E06: line 8: call target p is
  no bind-registered procedure`; `BEG8.pli` (same `p`, never called) currently ACCEPTS
  rc 0 with `p` silently absent from the dump. This asymmetry is carried by the LOWERING
  path (`lower_stmt`'s `Sproc Bproc -> []` arm, which assumes registration), predates
  this slice, is unchanged by it, and its DR-oracle behaviour is `[TBD]` (no oracle
  authorized). NOT touched by P1-h per the brief's narrow scope; recorded here so a
  future slice can own it.
- **M-7 The independent checker already encodes the correct law.** `semtest.ml`'s
  `ast_nesting` (invariant I6, `semtest.ml:1062-1111`) recurses into the NESTED block's
  own statements with the SAME parent for non-Bproc `Sproc` children, and its comment
  records the pre-fix hang and the fact that its BEGIN arm never ran for a fixture. I6
  judges the live env against a physically re-derived AST nesting table (block identity
  by `==`, pid pre-order, `eparent`/`SE.enclosing` agreement) — after the repair this
  becomes the exercised, independently checked structural traversal invariant (brief §4).

### P1-h.2 Correction contract (minimal structural visitor)

ONE file changes: `ocaml/hir/semantic_env.ml`. Per brief §3, separate the statement
subtree being traversed from the enclosing procedure's semantic environment:

- Introduce `discover_stmts st plan ctx (ss : Ast.stmt list)` — the structural visitor.
  `ctx` is the ENCLOSING procedure's `block_env` (semantic owner); `ss` is the statement
  subtree under traversal. The `Ast.Sproc` arms:
  - `Bproc` child: registration body **verbatim and unchanged** (name guard, second-
    authority registry lookup, duplicate guard, pid/pre-order ids, `procs_by_name`
    prepend, `register_block st ctx.escope …`, then descend into the NEW env's own
    statements);
  - non-Bproc child (BEGIN/DO): `discover_stmts st plan ctx ib.Ast.bstmts` — descend
    into the nested block's OWN statements under the SAME ctx. No scope id, no pid, no
    signature, no ownership is invented; BEGIN shares the enclosing procedure's scope
    (M-3/M-4; §P1-b.4 fact 2).
- `register_children st plan parent` becomes exactly
  `discover_stmts st plan parent parent.east.Ast.bstmts`.
- Termination: the parser AST is a finite tree and recursion strictly descends the
  nesting structure; each nested block is visited exactly once along its structural
  path (no re-walk of an ancestor list). Depth is source nesting depth.
- Non-targets (explicit): no change to `hir_build.ml`, `hir.ml`, `diagnostic.ml`,
  `backend.ml`, `ocaml/lib/**`, `ocaml/bin/**`; no new diagnostic; no scope semantics;
  no `Sdobegin` descent (M-5); the M-6 lowering asymmetry is NOT touched.
- Preservation law (predicted, falsified by T2/T4): for any program whose block tree
  contains no non-Bproc nested block, the visitor produces the IDENTICAL sequence of
  registrations — every H01–H21 dump, diagnostic byte, OK number and gate panel is
  byte-identical. Shapes containing statement-level BEGIN/DO previously HUNG or
  bogus-refused; they now traverse.

### P1-h.3 `semtest.ml` amendment — shared comparisons + two non-vacuous controls

Per the §P1-a2.6 shared-comparison law (the control runs THE SAME code as the
invariant, never a copy):

- Extract I6's per-pair ownership comparison (the body of the `List.iter` over the
  `pairs` list plus the block-count/identity checks it shares) into a shared function
  used VERBATIM by the live I6 and by both new corrupt controls.
- `--corrupt-owner`: take the independently re-derived nesting pairs and reparent ONE
  pair at a physical block that is NOT its AST parent (prefer a different procedure's
  block; with only one nested procedure, use the child itself — self-parenting must
  fail the `eparent`/pre-order/`enclosing` arms). Re-run the shared comparison; it MUST
  reject. A fixture with no nested procedure prints `nothing was proven`, rc 1.
- `--corrupt-discovery`: DROP one nesting pair before re-running the shared comparison —
  simulating discovery that duplicated the owner's list or hid a procedure: the count
  invariant (`N env blocks for M AST-nested procedures (main is the extra)`) and the
  missing-block arm MUST reject. A fixture with no nested procedure prints
  `nothing was proven`, rc 1.
- The `SEMANTIC-AUTHORITY OK <n> refs / <m> syms` line is unchanged in meaning and
  count for every existing fixture (I6 gains no counted item).
- `tools/hir_test.py`: `SEM_MODES` gains the two flags (live + NINE corrupt modes); the
  docstring/`SEM-FAIL` contract text updated to match. No T5 grep-list change (the new
  code reads no bind field that was not already on the seam list; `ast_nesting` is pure
  AST + env).

### P1-h.4 Fixtures (ids H22–H29; every shape measured FIRST, expected = copy of
reviewed measured output, never hand-written; CRLF + `^Z`; every run under `timeout 60`)

| id | shape (brief §4 coverage) | predicted outcome |
|---|---|---|
| H22 | bare empty `begin; end;` in main | rc 0 dump; main body shows NO phantom statement; determinism |
| H23 | BEGIN containing ordinary statements (`x = 1; y = x + 1;`) | rc 0; statements appear EXACTLY ONCE, inlined in order, in `proc(0)` body |
| H24 | two sibling BEGIN blocks, each with one statement | rc 0; both statements once, in source order |
| H25 | BEGIN nested inside BEGIN (two levels) with one statement | rc 0; statement once |
| H26 | procedure `p` declared under a statement-level BEGIN in main, plus `call p;` | rc 0; `p` discovered ONCE (PROC + SCOPE lines), owner = main scope |
| H27 | BEGIN nested inside procedure `q` (q called from main); the BEGIN contains a statement AND a nested procedure `r` | rc 0; `r` discovered ONCE with parent = `q` (dump scopes/pids pinned); q's body inlines the BEGIN statement once |
| H28 | REGR: M-1/BEG2 shape — Bproc sibling `p` then a bare BEGIN assigning `x` | rc 0 (the bogus `duplicate internal procedure name` refusal must be GONE); exactly ONE `PROC … name=p` line |
| H29 | BEGIN containing a `dcl` (M-4 shape at statement level) | rc 2, ZERO stdout, stderr byte-pinned to the existing typed `HIR-E03 … produced no bind row in this block` (the unsupported scope refuses explicitly; NOT flattened) |

Existing procedure shadowing and forwarding behavior (brief §4 last bullet) is held by
the FROZEN existing pins: H18 (three-pid forwarding chain, [C130] E27B) and the I13
shadow-law comparisons on H16/H17 stay byte- and count-identical (T2/T4); no new fixture
re-pins them.

Non-vacuity of the traversal invariant on the new fixtures: H26/H27/H28 give I6
non-empty `pairs` lists, so `--corrupt-owner` and `--corrupt-discovery` must fire SEM-FAIL
rc 1 on them (brief §4: completion without hanging is insufficient — ownership and
no-dup/no-drop are asserted structurally, and the dump bytes pin statement identity).

### P1-h.5 Falsifiers (each a STOP-and-attribute gate, never re-fit)

- **T1** `pli80c.exe` sha256 stays `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` after EVERY build step, checked DIRECT.
- **T2** every PREVIOUS `hir/expected/*` byte unchanged: `git diff --exit-code -- hir/expected` shows additions only (new H22–H29 files; existing files untouched). H01–H21 stay green.
- **T3** `dune build` rc 0, ZERO `Error`; at close, fresh `dune build --build-dir _build-e54p1h` rc 0, ZERO `Error`, warning hist **122**, fresh exe sha computed separately == kept exe.
- **T4** `timeout 900 python3 tools/hir_test.py` rc 0; ALL 11 existing semtest OK numbers unmoved; every corrupt mode (existing seven + the two new) rc 1, ZERO stdout, all-`SEM-FAIL` stderr on every positive fixture; new positives H22–H28 each run live + 9 corrupt modes green.
- **T5** reproduction held + repaired: the pre-fix witness `build/e54p1h-hang-witness.log` stays as measured (rc 124 / rc 2 / rc 124); post-fix re-run of the SAME scratch inputs under `timeout 20` terminates promptly (BEG1/BEG3 no longer 124; BEG2 no longer the bogus duplicate) — recorded in RESULTS with the actual exit statuses.
- **T6** ZERO oracle: no oracle, cpmsim, LINK-80, `--runtime`, `--link-run` or rune-ci invocation; only `dune build`, `tools/hir_test.py`, `tools/e2e_gate.py` (byte tier), `git`, and the HIR/semtest binaries on scratch fixtures.
- **T7** `git diff --exit-code -- ocaml/lib ocaml/bin` EMPTY at every commit; goldens/inventory/census/coverage untouched; ledger stays 203 `## C` headers ending **C380**; NO new claim (this slice is infrastructure; its "facts" are reads of this repository's own bind implementation, classified [bind-fact], never DR claims).
- **T8** seam greps hold after the edits: F10 (Bind alias + one `bind_program` in hir_build — unchanged file), S8 (semantic_env.ml still `Hir`-free after comment strip), F8, F7, F4 hex audit, F9, T5 cs_*/bind_arrays reader list still exactly {semantic_env.ml, semtest.ml}, `cs_slot` nowhere, T6 vocabulary strip-clean.
- **T9** structural invariant non-vacuity: at least one new positive fixture (H26/H27/H28) proves BOTH new corrupt controls reject real perturbations (SEM-FAIL naming the perturbed proc), and at least one existing nested-proc fixture (H03 or H18) proves the controls still fire for the pre-existing shapes.
- **T10** FULL gate rc 0 → `build/gate-e54p1h-reg.log` with FROZEN panels **1328/1328, 190/190, 9/9, 149 rows 0/0, census 16/0/25/0, prose 5**. Any move = STOP, attribute first-hand, revert; historical compilation is unchanged.

### P1-h.6 Predicted drift surfaces

- Only programs containing statement-level non-Bproc `Sproc` blocks change behaviour:
  from hang (124)/bogus-duplicate (E11) to traversal. NONE of H01–H21, the 1328 goldens
  or the 190 negatives contains a HIR-path BEGIN/DO at statement level (the hang is the
  proof: no committed fixture hit it). Zero drift is therefore PREDICTED and pinned by
  T2/T4/T10; any observed move is a STOP event.
- New code words (`discover_stmts`, `--corrupt-owner`, `--corrupt-discovery`) join the
  F8/T6/T5 grep surface — stripped-code greps must stay clean; names chosen free of the
  forbidden vocabulary.

### P1-h.7 Work order

1. Baseline first-hand verification + reproduction witness — **DONE** (this session, §P1-h header + M-1).
2. This pre-registration committed BY EXPLICIT PATHS before ANY `ocaml/hir/` byte (PROTOCOL #1).
3. `semantic_env.ml` per §P1-h.2 → build rc 0 (DIRECT rc) → T1 → hir_test rc 0 → post-fix reproduction re-run (T5) → commit (explicit paths).
4. Fixtures H22–H29: measure each shape in scratch first, review every dump line against the traversal law (owner/pid/duplication), then `cp` measured output to `hir/expected/` → hir_test rc 0 → commit.
5. `semtest.ml` §P1-h.3 + `tools/hir_test.py` SEM_MODES/docstring → hir_test rc 0 (T4, T9) → commit.
6. FULL gate rc 0 FROZEN → `build/gate-e54p1h-reg.log`; fresh `--build-dir _build-e54p1h` (T3).
7. CLOSE: `RESULTS.md` §P1-h (panel WITH measured values + deviations + reproduction set), `docs/architecture/backend-boundary.md` update, PLAN dashboard row CLOSED, durables + guard checkpoint → commit.
8. **STOP** — no PUT/GET, no MIR, no P2, no broader scope refactoring (brief §7).

Standing constraints (every hop): ZERO oracle; ledger stays C380; `ocaml/lib`+`ocaml/bin`
byte-clean; `handoff.config.json` NEVER staged; no push; explicit-path commits only;
`eval "$(opam env)"` in every shell; rc checked DIRECT; NEVER batch a build with tests
that consume its artifacts; every fixture under `timeout 60`; scratch
(`ocaml/scratch-p1h/`) NEVER committed; `superseded/` never rewritten; H01–H21 frozen.

### P1-h.8 Dashboard

| slice | status | notes |
|---|---|---|
| P1-h | **CLOSED 2026-11-10** | BEGIN/DO discovery hygiene; ZERO oracle; correction `7144b3f1`, fixtures `500c668f`, semtest/runner `e004fa3e`; panel RESULTS §P1-h (T1–T10 ALL PASS, gate FROZEN 1328-190-9-149-16/0/25/0-prose 5 ALL HIT, zero drift measured) |

---

## §P1-m0 — Pre-registration: First Native MIR AOT Compilation (committed BEFORE any compiler-source modification)

Operator-authorized slice **E2E-54/P1-m0** (2026-11-09): the first experimental native
AOT path PL/I source → Parser + Bind → `Semantic_env` + `Hir_build` → typed `Hir.program`
→ NEW `Mir_backend` → deterministic MIR text → pinned MIR native object generator
(out-of-tree `libmir.a` from the pinned laboratory) → ELF x86-64 `ET_REL` `.o` → system C
linker + minimal driver → native executable → independently verified result. No JIT at
runtime, no oracle calls, no historical-byte change. This section is committed by explicit
paths BEFORE any `ocaml/` compiler-source byte (PROTOCOL #1).

### P1-m0.0 Operator brief (verbatim)

Recovered VERBATIM from the operator turn of session
`01a1c07e-5269-7161-b5f4-4904817cf26e` (transcript JSONL), stored at the ignored path
`build/p1m0-brief-true.md` and machine-compared against this embedding: the stripped
blockquote below equals the source BYTE-FOR-BYTE (362 content lines, 361 newlines, NO
trailing newline — recorded honestly; an earlier hand copy differed only by the missing
final newline and was replaced by the extraction).

> # DRPLi — E2E-54/P1-m0: First Native MIR AOT Compilation
>
> ## Operator authorization
>
> The operator authorizes **E2E-54/P1-m0**, the first experimental native AOT compilation path from DRPLi's existing PL/I frontend through typed HIR and MIR.
>
> The goal is to produce and execute **genuine native machine code originating from PL/I source**, not to implement a complete production backend.
>
> Last verified public repository HEAD:
>
> `118e91dc39d57a36c28081b5957566743ff27f2a`
>
> The P1-h guard reported checkpoint g674 locally. Inspect the actual local HEAD and Handoff state before proceeding; do not assume the remote contains every finalized guard block.
>
> E2E-54/P0, P1-b, P1-a1, P1-a2 and P1-h are CLOSED.
>
> This new slice is authorized. Preregister it under `spec/lab-evidence/e2e54/PLAN.md` before changing compiler source files.
>
> ## 1. Deliverable and success criterion
>
> Demonstrate this complete execution path:
>
> ```text
> Actual PL/I source file
>        |
>        v
> Existing Parser + Bind
>        |
>        v
> Semantic_env + Hir_build
>        |
>        v
> Typed Hir.program
>        |
>        v
> NEW Mir_backend
>        |
>        v
> MIR textual representation
>        |
>        v
> Pinned MIR native object generator
>        |
>        v
> ELF x86-64 relocatable .o
>        |
>        v
> System C linker + minimal test driver
>        |
>        v
> Native executable
>        |
>        v
> Verified independently expected result
> ```
>
> **The final executable must execute previously generated native machine code. It must not parse MIR or invoke a JIT at runtime.**
>
> The generated `.o` must contain actual machine code produced from the HIR.
>
> A handwritten MIR demo, generated C compiled by GCC, or a program returning a hardcoded answer is NOT sufficient evidence.
>
> ## 2. Work from verified dependencies
>
> Existing independent laboratory:
>
> `https://github.com/cyrilmhansen/mir-madc-aot-lab`
>
> Pin:
>
> - Laboratory commit `ccc92c5c650b4385b4f42c9493725ae1415ab2e5`
> - MADC submodule commit `f541a7a54624869e29b01f2f30b174bc0329eea5`
>
> The maintained MIR implementation lives under `madc/third_party/mir`.
>
> Relevant proven entry points:
>
> - `src/microbench/aot_corpus.c`
> - `src/microbench/mir_elf_multimodule_demo.c`
> - `scripts/run-linux-aot-benchmarks.sh`
> - `docs/RESULTS.md`
> - `docs/ISSUES.md`
>
> Check the known local laboratory path first. If absent, obtain the pinned checkout in a new disposable, ignored dependency directory, provided network access is available.
>
> Do not search the entire filesystem.
>
> Do not modify the external laboratory or advance its pinned revisions.
>
> ### Native object API
>
> The laboratory already demonstrates:
>
> ```c
> MIR_scan_string(ctx, mir_text);
> /* Load modules, initialize generator, and link. */
> MIR_gen_set_object_mode(ctx, 1);
> /* Generate the selected MIR functions. */
> MIR_gen_object_emit(ctx, &buffer, &size);
> ```
>
> Use the laboratory's actual complete initialization/generation/finalization sequence. The abbreviated example above is not itself a complete driver.
>
> Use the system linker to link the emitted object into the test executable.
>
> Do not use `MIR_object_load` for P1-m0; a known multi-module/import relocation defect remains recorded in the lab.
>
> The first execution target is Linux x86-64 ELF. Do not add macOS/AArch64 cross-compilation to this phase.
>
> ## 3. Extremely narrow PL/I subset
>
> Begin with a **zero-argument, integer-returning procedure**.
>
> A candidate source shape, to validate against the ACTUAL parser and HIR builder before adopting:
>
> ```pli
> calc: procedure returns(fixed bin(15));
>    dcl x fixed bin(15);
>    x = 6 * 7;
>    return (x);
> end calc;
> ```
>
> Expected result: 42.
>
> Adapt syntax only according to observed parser behavior. Do not silently change the meaning of the test.
>
> Prefer a genuine procedure-only PL/I module, represented through the existing Bind/HIR pipeline.
>
> If that shape is not supported, investigate an existing HIR-supported alternative. Any test-only exported entry must be explicitly identified as a harness convention rather than an invented PL/I language rule.
>
> ### Initial supported operations
>
> - Integer constants.
> - FIXED BINARY scalar locals.
> - Simple assignments.
> - Addition, subtraction and multiplication.
> - Unary negation if straightforward.
> - Return of a scalar integer.
>
> The first milestone does NOT need:
>
> - Procedure parameters.
> - Array references.
> - Pointer or BASED accesses.
> - Nested calls.
> - External functions.
> - PUT/GET.
> - PLILIB.
> - Decimal or floating-point arithmetic.
> - ON conditions.
> - Full PL/I program startup semantics.
>
> IF/ELSE may be added only after the straight-line milestone passes, within the same preregistered small subset.
>
> Loops and recursive calls are outside this slice.
>
> ## 4. Numeric semantics — do not silently invent them
>
> The current HIR carries FIXED BINARY precision and scale, but some DR arithmetic semantics remain unmeasured.
>
> For the first prototype, use a documented native integer carrier such as MIR `i64`.
>
> This is a backend representation choice, NOT a claim that PL/I-80 integers are 64-bit.
>
> Restrict accepted programs to a domain where the following are independently guaranteed:
>
> - Integral values.
> - No arithmetic overflow.
> - No uncharacterized conversion.
> - No uninitialized-value read.
> - No division or floating-point behavior.
>
> For the initial no-argument functions, conservative static constant/interval analysis is acceptable.
>
> If a program can leave this proven-safe domain, refuse with an explicit diagnostic rather than assume wrapping, saturation or trapping semantics.
>
> Do not upgrade the `Target.profile` unknown fields into invented known facts.
>
> ## 5. New MIR backend
>
> Add an isolated implementation under `ocaml/hir/`, conceptually:
>
> - `mir_backend.ml`
> - `pli80mir.ml` or another explicitly named opt-in CLI
>
> Implement the existing `Backend.BACKEND` contract, producing a deterministic MIR textual artifact.
>
> The backend should consume the actual `Hir.program`, including its symbols, statements and typed expressions.
>
> Do not parse the HIR dump text.
>
> Do not parse PL/I a second time.
>
> Do not bypass `Semantic_env` or `Hir_build`.
>
> Choose an explicit single native export, with a documented C ABI for the test driver.
>
> Every unsupported HIR node must fail loudly. A partial or failed compilation must leave no misleading successful `.mir` or `.o` artifact.
>
> Keep MIR-specific types, opcodes, register choices and ABI details in the backend implementation, never in `Hir` or `Semantic_env`.
>
> Do not introduce MIR into the historical `pli80` library.
>
> ## 6. Native emitter tool
>
> Add a small, reproducible host-side tool, based on the pinned MIR API, which:
>
> 1. Reads the MIR text produced by `Mir_backend`.
> 2. Parses and validates it with the pinned MIR library.
> 3. Enables native object generation.
> 4. Emits an ELF relocatable `.o`.
> 5. Returns a nonzero exit code on failure.
>
> Prefer a small C bridge linked to the pinned `libmir.a`.
>
> No dependence on the MADC language frontend is needed: MIR itself is the backend input.
>
> Generated objects, logs and temporary executables belong in ignored build directories.
>
> Do not commit machine-specific object files.
>
> ## 7. Native execution and independent oracle
>
> Create a minimal C test driver that calls the exported native function and checks an independently specified expected result.
>
> For the initial test, it may verify that the function returns 42.
>
> The oracle must be established independently of the generated MIR and HIR dump.
>
> Add at least three successful cases, if the initial milestone permits:
>
> 1. Constant arithmetic.
> 2. Local variable assignment followed by arithmetic and return.
> 3. A second nontrivial arithmetic expression, preferably exercising negative integers or operator precedence.
>
> Add at least two negative cases, including an unsupported HIR operation and a construct with unproven numeric semantics.
>
> No positive test should pass merely because the backend ignored an operation.
>
> Use a corruption control that deliberately changes an emitted arithmetic operation or expected result and proves the native test detects the discrepancy.
>
> ### Native-artifact verification
>
> Inspect and preserve:
>
> - `readelf -h` (ELF machine and object type).
> - `readelf -r` (relocations, if present).
> - `nm` (the intended exported symbol).
> - Native disassembly of the generated function.
> - Successful system-linker output.
> - Native execution status and observed result.
> - Dynamic dependencies of the final executable.
>
> Demonstrate that the runtime executable does not require MIR, MADC, the OCaml compiler or the PL/I frontend.
>
> The build-time native emitter may of course depend on `libmir`.
>
> Execute the native binary in at least two fresh processes.
>
> ## 8. Tests and determinism
>
> Create a dedicated MIR AOT test runner.
>
> It must verify:
>
> - The PL/I source is really parsed and lowered through the existing HIR construction path.
> - MIR text generation is deterministic.
> - Each successful `.mir` is accepted by the MIR parser.
> - Native object emission succeeds.
> - Linking succeeds.
> - The exported function executes with the correct result.
> - Negative cases refuse without partial artifacts.
> - The corruption control fails as designed.
>
> Keep independently specified expected results separate from generated output.
>
> Do not silently overwrite expected data with new compiler output.
>
> ## 9. Historical regression requirements
>
> The historical compiler must remain byte-identical:
>
> `pli80c.exe SHA-256 = 172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`
>
> Mandatory validation:
>
> - Existing HIR suite passes (P1-h baseline: 220 OK).
> - Full compile-tier gate RC 0.
> - 1328/1328 byte-exact `.REL`.
> - 190/190 negative tests.
> - 9/9 divergence tests.
> - Coverage 149 rows, zero errors/warnings.
> - Corpus census unchanged.
> - Claims ledger unchanged at C380.
>
> Do not modify:
>
> - `ocaml/lib/`
> - `ocaml/bin/`
> - Historical goldens
> - Existing scientific claims
> - Inventory, census or coverage
> - `GOAL.md`
>
> No DR oracle calls.
>
> No external Rune CI runtime/audit runs are required for this isolated native prototype.
>
> Check build/test commands and exit codes separately.
>
> ## 10. Deliverables
>
> Produce:
>
> - Preregistered `PLAN.md` section for P1-m0.
> - New MIR backend implementation.
> - Opt-in PL/I-to-MIR CLI.
> - Reproducible MIR-to-ELF-object emitter.
> - Native C test driver.
> - Positive and negative PL/I fixtures.
> - Automated native AOT tests.
> - Verified ELF/relocation/disassembly evidence.
> - Explicit unsupported-semantics matrix.
> - Updated `docs/architecture/backend-boundary.md`.
> - Measured `RESULTS.md` section with the complete end-to-end evidence.
>
> Clearly distinguish:
>
> - Successfully lowered HIR.
> - Successfully generated MIR.
> - Successfully emitted a native object.
> - Successfully linked a native executable.
> - Successfully executed with the expected result.
>
> These are separate milestones. Do not report end-to-end success unless the final native execution has passed.
>
> ## 11. Operating constraints and stop condition
>
> Use explicit-path commits.
>
> Never stage `handoff.config.json`.
>
> Do not reset or clean unrelated working state.
>
> Do not push.
>
> Use safe Handoff renewals where available; respect the actual chain state.
>
> If the pinned MIR dependency cannot be obtained or the object emitter is unavailable, record the precise environmental blocker. Do not replace the requested MIR backend with a C-only compilation path and claim success.
>
> If full native execution succeeds, record the working commands and results, close P1-m0, finalize the checkpoint and STOP.
>
> Do not automatically extend the compiler to parameters, arrays, I/O, macOS, AArch64 or a production backend.
>
> ### Success criterion
>
> **At least one real PL/I procedure is compiled through the existing frontend and typed HIR into MIR-generated native code, linked into an executable and run successfully against an independent expected result.**
>
> No JIT is required at runtime, no historical compiler bytes change, and unsupported semantics remain explicit.
>
> **Operator authorization: E2E-54/P1-m0 is approved. Preregister and proceed.**

### P1-m0.1 Dependency acquisition and MEASURED environment facts (this session, first-hand)

All facts below were measured BEFORE this pre-registration, in scratch only (no compiler
source touched). Each is falsifiable by re-running the named command.

- **D-1 lab pin.** No local laboratory existed (checked the known paths
  `thirdparty/mir-madc-aot-lab`, `~/mir-madc-aot-lab`, `~/projects/sushiworks/mir-madc-aot-lab`
  and `find /home/john -maxdepth 3 -iname '*madc*'` — all empty, consistent with RESULTS §5
  `[TBD — lab not reachable]`, which said "without network"; network IS available this session).
  Per brief §2 the pinned checkout was obtained by `git clone` into the git-IGNORED,
  disposable directory `thirdparty/mir-madc-aot-lab`, checked out at lab commit
  `ccc92c5c650b4385b4f42c9493725ae1415ab2e5` (verified `git rev-parse HEAD`) with submodule
  `madc` at `f541a7a54624869e29b01f2f30b174bc0329eea5` (verified `git submodule update --init madc`
  + `git rev-parse HEAD`). The lab is NEVER modified: `libmir.a` is built strictly
  OUT-OF-TREE (§D-2) and `git status` inside the lab stays clean (checked DIRECT at close).
- **D-2 out-of-tree libmir.** `make -f GNUmakefile BUILD_DIR=$PWD/../../../../build/p1m0-deps/mir-obj
  <abs>/build/p1m0-deps/mir-obj/libmir.a -j8` (run from `madc/third_party/mir`) rc 0, producing
  `build/p1m0-deps/mir-obj/libmir.a` (10 337 202 B at first build; size is NOT pinned — it is
  machine-specific build output under ignored `build/`). MEASURED tooling law: the make rule
  needs the BUILD_DIR to pre-exist for the `libmir.a` goal alone when invoked from a different
  cwd; `mkdir -p` first. The archive embeds `-DGITCOMMIT=f541a7a5…` (the MADC pin) in object
  metadata — build-time provenance, not a runtime dependency.
- **D-3 the complete emitter sequence** is `src/microbench/aot_corpus.c` `prepare_capture` +
  `emit_artifact("object", …)`: `MIR_init` → `MIR_scan_string` → for every module of
  `MIR_get_module_list`: `MIR_load_module` → `MIR_gen_init` → `MIR_gen_set_object_mode(ctx,1)`
  → `MIR_link(ctx, MIR_set_gen_interface, NULL)` → `MIR_gen(ctx, item)` for every selected
  `MIR_func_item` → `MIR_gen_object_emit(ctx,&buf,&size)` → write → `MIR_gen_finish` →
  `MIR_finish`. `MIR_object_load` is NOT used (brief §2; the lab `docs/ISSUES.md` records the
  combined imported-call/data relocation defect in the loaded-object path).
- **D-4 MIR text format (measured by working probe, pinned sample `ext.mir`).** A module is
  `M0:\tmodule` … `\tendmodule`; a function is `<name>:\tfunc\ti64` with `\tlocal\ti64:a, …`,
  instructions, `endfunc`, then `\texport <name>` BEFORE `endmodule`. MEASURED: omitting
  `endfunc` is a PARSE ERROR ("absent endfunc") — the backend must emit it. Binary ops are
  3-operand register form (`mul t2, t0, t1`), immediate loads go through `mov t, <decimal>`,
  unary is `neg r, x`, exit is `ret <reg>`. `endfunc`, `export`, `endmodule` are required.
- **D-5 host toolchain.** `Linux x86-64`, `gcc (GCC) 16.2.1`, `GNU Make 4.4.1`, binutils
  `readelf`/`nm`/`objdump` present. This is a NATIVE x86-64 host — the lab's Linux caveats
  (QEMU TCG timings, Darwin failures) do not apply to correctness of the ELF path here.
- **D-6 full native chain PROVEN on hand-written MIR in the EXACT emitted form** (scratch,
  never the deliverable claim — this only pins the toolchain, not the backend): emitter linked
  against the pinned `libmir.a` produced an `REL (Fichier de réadressage)` /
  `Advanced Micro Devices X86-64` object exporting `T calc` / `T pli80_m01` whose disassembly
  is real code (`48 c7 c0 2a 00 00 00 mov $0x2a,%rax; c3 ret`); `gcc -O2 drv.o` linked; the
  executable printed 42 with `ldd` showing ONLY `linux-vdso.so.1`, `libc.so.6`,
  `ld-linux-x86-64.so.2`; `readelf -r` showed relocations only in `.rela.eh_frame` (two
  `R_X86_64_PC32` against `.text`) — CODE relocations NONE for this shape. MEASURED: MIR
  identifiers accept `_` and digits (`pli80_m01` works). Constant folding happens inside
  `MIR_gen` (a mul chain emitted as one `mov $imm`) — expected results are therefore verified
  by EXECUTION, never by disassembly shape.
- **D-7 PL/I shapes measured through the ACTUAL pipeline** (`pli80hir.exe` on scratch CRLF+^Z
  files, all first-hand this session):
  - The brief's candidate shape parses and lowers EXACTLY as written:
    `calc: procedure returns(fixed bin(15));` with one `dcl x fixed bin(15);`,
    `x = 6 * 7;`, `return (x);` → rc 0, one `PROC 0 … params=[] returns=FIXED BINARY(15,0)`,
    `assign` + `return value`. NO `options(main)` is needed (adding it also parses; the
    fixture uses the brief's plain form). No syntax adaptation was required.
  - `M02` (`y = 10; z = y + 5; return (z * 3);`) and `M03` (`r = 2 - 3 * 4; return (-r);`)
    lower rc 0; the parser produces the expected PRECEDENCE (`2 - (3 * 4)` nests under the
    `binop -`), unary minus lowers to `negate`, and NO `Convert` appears (same-type target).
  - `N1` (read of never-assigned `x`) LOWERS rc 0 in HIR — the unproven-initialization check
    is therefore a MIR-backend duty, not an HIR refusal. `N2` (IF), `N5` (array element
    assign + read) and `N7` (DO WHILE) also LOWER rc 0 — unsupported-operation refusals live
    in the MIR backend. `N3` (bin(15)→bin(7) assignment) lowers WITH `Convert` nodes — the
    uncharacterized-conversion refusal lives in the MIR backend.
  - `N4` (`dcl c character(3)`) dies `HIR-E02 … outside the P0 HIR subset` rc 2 and `N6`
    (literal `40000`) dies `HIR-E08 … outside the P0 bin(15) literal domain` rc 2 — BEFORE
    any MIR code runs. These two pins double as the proof that `pli80mir` cannot bypass
    `Hir_build` (brief §5): if the new CLI refused them with a MIR-E code, the bypass claim
    would be FALSIFIED.
  - MEASURED line-number quirk: scratch files whose internal newlines are LF-only report
    `SYM … line=1` for the first `dcl` (the lexer's CR handling), while full-CRLF fixtures
    report the visible source line; the committed fixtures therefore follow the H-series law
    (full CRLF + ^Z) and every expected file is a COPY of reviewed measured output
    (measured-first), never hand-written.
- **D-8 test-suite vocabulary constraints (read first-hand from `tools/hir_test.py`).**
  `F8_PATTERNS` is applied to EVERY `ocaml/hir/*.ml` (glob) after nested-comment strip:
  no `\bRel80\b`, `\bCodegen\b`, `\bbytes_of\b`, `\bop_[A-Za-z_]+`, `0x[0-9a-fA-F]+`, 8080
  mnemonics (`\b(MOV|…|Z|C|M|P)\b` — single UPPERCASE letters are words!) and
  `\b(size|offset|reloc|pool)\b` even inside strings. The new units therefore name things
  with lowercase MIR vocabulary (`mir_text`, `tmp`, `mov`/`mul` as MIR mnemonics in lowercase
  strings are safe; the forbidden mnemonics are matched word-anchored and UPPERCASE-only
  except that lowercase MIR `mov` never matches `\bMOV\b`). F7/T5/T6 file sets are untouched.
  Any F8/T5/T6/F10/S8 movement is a STOP event, never a pattern edit.

### P1-m0.2 Native subset contract — what `Mir_backend` LOWERS; everything else refuses BY NAME

The backend consumes the typed `Hir.program` produced by the EXISTING `Hir_build.build`
(no second parse, no dump parsing, no `Semantic_env` bypass — brief §5). Accepted shape:

- The program contains EXACTLY ONE procedure (`procs = [p]`); the export is selected by
  `--export NAME`, matching `p.name` case-insensitively (PL/I name folding; the CLI option
  and the `pli80_` symbol prefix are HARNESS CONVENTIONS, not PL/I language rules — brief §3).
  Refusals: no match, `name = None`, or more than one procedure → `HIR-E20`.
- `p.params = []` and `p.ret = Some (Fixed_bin (p_, 0))` with `1 ≤ p_ ≤` the profile's
  `max_fixed_precision` ceiling (15, Oracle-backed field; NOT reinterpreted as a DR claim).
  Anything else → `HIR-E20` (signature outside the native subset).
- Statements (in order): `Declare` (accepted as a no-op — registers are allocated from the
  program's `syms`, and the lowering re-checks each declared symbol's type/storage),
  `Assign { target = D_var; value }`, and EXACTLY ONE `Return (Some e)` as the FINAL
  statement. `Return None`, a second `Return`, a non-final `Return`, or no `Return` →
  `HIR-E18` (fall-through/implicit-return semantics are unmeasured [TBD]; no MIR is invented
  for them). `Stop` → `HIR-E18` (startup/end semantics out of scope, brief §3).
- Targets: `D_var` only; `D_elem` (and thus ANY array use) → `HIR-E18`.
- Expressions: `Const`, `Var`, `Bin (Add|Sub|Mul)`, `Neg` — each with `ex_ty` a
  `Fixed_bin (p, 0)` whose sids belong to the export proc's own scope. `Bin` relational ops,
  `Call_e`, `Elem_read`, `Elem_ref`, `Convert` → refusal; `Convert` is `HIR-E19`
  (uncharacterized conversion, brief §4), all others `HIR-E18`. Any `ex_ef = Unknown_ef`
  → `HIR-E18` (a call's effect is unmodelled here).
- Symbols for the export proc: storage `Auto` only; `Static` (initial values unmeasured),
  `Formal`, `External_sym` → `HIR-E18`. Types `Fixed_bin (p, s≠0)`, `Fixed_dec`, `Char`,
  `Bit`, `Ptrty`, `Array1`, … → `HIR-E18` (typing refusal) or `HIR-E19` when the construct
  would also leave the numeric domain — the code chosen names the PRIMARY reason in the
  message; both are loud rc 2 with ZERO stdout.

MEASURED-FIRST predictions (falsifiable; pin what is actually observed, never fit):
M01/M02/M03 → rc 0 MIR text; N1 → E19 uninitialized read; N2 → E18 `if`; N3 → E19 `convert`;
N5 → E18 array designation; N7 → E18 `while`; N4 → E02 and N6 → E08 (both from the EXISTING
HIR channel, unchanged).

### P1-m0.3 Numeric-safety contract (brief §4) — refuse, never assume

The native carrier is MIR `i64`. This is a REPRESENTATION CHOICE: PL/I-80 `FIXED BINARY`
widths are whatever DR measured them to be; nothing here claims DR uses 64-bit integers, and
NO `Target.profile` `Unknown` field is upgraded to a fact.

Accepted programs are restricted to a statically PROVEN-SAFE domain, decided by the backend
over the typed HIR before any MIR is emitted:

1. **Straight-line only** (no control flow in the subset), so initialization and intervals are
   exact, not approximated: a simple forward walk. A `Var` read of a sid not previously
   ASSIGNED on that path → `HIR-E19` "uninitialized read". (Measured: HIR itself accepts N1.)
2. **Interval analysis** with closed integer intervals: `Const` → `[v,v]` (`v` decimal text as
   written; a non-canonical or signed literal text → `HIR-E19`); `Var` → the sid's current
   interval; `Add`/`Sub` → endpoint arithmetic; `Mul` → the four endpoint products' extremes;
   `Neg` → flip. EVERY intermediate interval must lie inside the declared-precision VALUE
   WINDOW `W(p) = [-(2^(p-1)-1), 2^(p-1)-1]` of the node's own `Fixed_bin (p, 0)` type — the
   window DR's own bin(15) literal evidence admits (Oracle-backed profile field; for p = 15:
   ±32767, the same ±32767 domain in which the byte-exact goldens live). Outside `W(p)` the
   backend REFUSES `HIR-E19` (no wrapping, no saturation, no trapping is assumed — profile
   `overflow_behavior` stays UNKNOWN and is HONOURED by refusing). Inside the window every
   faithful integer representation agrees, so the result is representation-independent;
   i64 contains every window trivially (p ≤ 15 ⇒ |v| ≤ 32767; products ≤ 2^30 inside OCaml
   `int`, exact, no silent truncation at the analysis level).
3. The RETURN value interval must lie inside `W(p_ret)`.
4. No division, no float, no DECIMAL appears in the subset (the HIR typing already refuses
   what it cannot type); scale ≠ 0 → `HIR-E19`/E02 as measured.

If ANY doubt remains the program is REFUSED with an explicit diagnostic; a refusal is total:
rc 2, zero stdout, no `-o` file, no `.o` (the emitter is never reached).

### P1-m0.4 MIR text emission contract (deterministic, reviewable)

- One module per compilation: `M0:\tmodule` … `\tendmodule`, exactly one `func` + its `export`.
- Function label = `pli80_` ^ (lowercased export name); `func\ti64`, zero formal arguments;
  `endfunc` then `\texport <label>` then `\tendmodule` (D-4: `endfunc` is MANDATORY).
- One `local i64:v<sid>` register per `Auto` symbol of the export proc (ascending sid, from
  the program's `syms`) and one `local i64:t<k>` per temporary, numbered by a monotonically
  increasing counter in EVALUATION ORDER (HIR order: left before right, target before value —
  the same order the dump records; `order:` is spelled `eval`, never `offset`).
- Lowering per node: `Const c` → fresh temp `t<k>`, `mov t<k>, c`; `Var s` → fresh temp,
  `mov t<k>, v<s>`; `Add/Sub/Mul` → lower left/right then fresh `t<k>`, `add|sub|mul t<k>, t<i>, t<j>`;
  `Neg` → `neg t<k>, t<i>`; `Assign` → lower value then `mov v<sid>, t<k>`; `Return e` → lower
  then `ret t<k>`. Every value ends in a freshly named temp; NO re-use of temp names.
- The artifact is a pure function of the `Hir.program` — no timestamps, no addresses, no hash
  iteration; determinism is tested by two fresh processes per fixture (byte-equal stdout).

### P1-m0.5 File set (explicit paths), CLI and emitter contracts

NEW or MODIFIED compiler-side files (all under the `pli80_hir` library/dir — the historical
`pli80` library and `ocaml/lib`/`ocaml/bin` are NOT touched, brief §5/§9):

- `ocaml/hir/mir_backend.ml` (NEW) — module `Mir : Backend.BACKEND` with
  `type artifact = { entry_sym : string; mir_text : string }`. MIR-specific types/opcodes/
  register names/ABI live ONLY here (brief §5).
- `ocaml/hir/diagnostic.ml` (MODIFY — APPEND ONLY): three new stable codes after the E17
  block, no existing code changes meaning:
  `HIR-E18 e_mir_node` (HIR construct outside the P1-m0 native subset),
  `HIR-E19 e_mir_numeric` (numeric semantics outside the proven-safe domain),
  `HIR-E20 e_mir_export` (export selection/signature outside the native subset).
- `ocaml/hir/pli80mir.ml` (NEW CLI, opt-in): `usage: pli80mir [--profile NAME] --export NAME [-o OUT.mir] INPUT.PLI`.
  Pipeline: read file → strip at first ^Z (same convention as `pli80hir.ml`, copied honestly)
  → `Pli80.Parser.parse_source` → `Pli80_hir.Hir_build.build` → `Mir.compile ~profile prog`
  (via `Backend.Driver (Mir)`). Success → MIR text on stdout AND the `-o` file (written only
  after `Ok`); rc 0. ANY refusal (parse, bind, HIR, backend) → diagnostics on stderr, rc 2,
  ZERO stdout, NO output file — a failed compile leaves no misleading `.mir` artifact.
  Missing `--export`/unknown profile → rc 2 usage error. No MIR, no emitter, no C linker is
  invoked by the OCaml side at any point.
- `ocaml/hir/dune` (MODIFY): add `mir_backend` to the library `(modules …)` list; add an
  `(executable (name pli80mir) (modules pli80mir) (libraries pli80 pli80_hir))` stanza.
  Nothing in the historical `ocaml/bin/dune` changes (F1 remedy; T2 below re-pins the exe sha).

Host-side native tooling (committed SOURCES only; all outputs land under ignored `build/`):

- `tools/mir_aot/mir2o.c` (NEW) — the small C bridge per D-3's full sequence: `usage: mir2o
  -f IN.mir OUT.o`; nonzero rc on every failure (read, parse, load, link, zero functions
  generated, emit, write); emits the ELF relocatable `.o` via `MIR_gen_set_object_mode` +
  `MIR_gen_object_emit`; `MIR_gen_finish`/`MIR_finish` on every exit path. It generates EVERY
  `MIR_func_item` of the loaded modules (the backend emits exactly one). No MADC, no
  `MIR_object_load`, no JIT execution.
- `tools/mir_aot/build_native.sh` (NEW) — reproducible build: (1) verify lab pin
  (`git -C thirdparty/mir-madc-aot-lab rev-parse HEAD == ccc92c5…` and
  `git -C …/madc rev-parse HEAD == f541a7a5…`, FAIL LOUD naming the exact blocker if the
  checkout is absent or moved — brief §11; no re-pin, no network fallback, no C-only
  substitution); (2) `make -f GNUmakefile` `libmir.a` out-of-tree into
  `build/p1m0-deps/mir-obj/` (mkdir first, D-2); (3) `gcc -O2 -Wall -Wextra -Werror
  -I<mir-src> mir2o.c <libmir.a> -ldl -lm -o build/p1m0-deps/mir2o`. The lab tree stays
  `git`-clean (checked after every step).
- `tools/mir_aot/native_check.c` (NEW) — minimal C driver: compiled with
  `-DENTRY=<exported symbol> -DEXPECTED=<long>`; declares `extern long ENTRY(void);`, calls
  it once, prints the returned value as decimal, exits 0 iff it equals `EXPECTED`. The C ABI
  contract (documented): zero arguments; return in the SysV x86-64 `i64` slot; no PL/I
  startup, no descriptor, no runtime.
- `tools/mir_aot_test.py` (NEW runner, §P1-m0.7).
- Fixtures `hir/mir-fixtures/M01.pli M02.pli M03.pli N1.pli … N7.pli` (CRLF + ^Z, one dcl
  item/statement — the H-series law); expected MIR pins `hir/mir-expected/M*.mir`, negative
  pins `hir/mir-expected/N*.stderr.txt` + `.rc`, ALL measured-first (§P1-m0.6).
  These are ADDITIONS: `hir/fixtures`, `hir/expected` and every existing file in them stay
  byte-frozen (T2).

### P1-m0.6 Fixtures and INDEPENDENT expected results

The expected results below are computed by HAND from the arithmetic of each source program,
recorded HERE before any run, and kept in the runner's own table — NEVER derived from the
MIR text, the HIR dump, the object or the disassembly (brief §7/§8).

| fixture | source arithmetic (by hand) | expected |
|---|---|---|
| M01 (`calc`, brief candidate) | `x = 6 * 7; return x` → 42 | **42** |
| M02 | `y = 10; z = y + 5; return z * 3` → 15 × 3 = 45 | **45** |
| M03 | `r = 2 - 3 * 4; return -r` → 2 − 12 = −10; negate → 10 | **10** |

Negative fixtures (all must refuse at the MIR boundary unless the row says the refusal comes
from the EXISTING HIR channel — those pin the no-bypass property): N1 (unproven
initialization), N2 (IF), N3 (Convert), N5 (arrays), N7 (DO WHILE) → new E-codes; N4 (E02),
N6 (E08) → existing HIR channels. Each negative pin records rc, EMPTY stdout and the exact
stderr bytes (same discipline as the H-series); additionally the runner asserts that with
`-o out.mir` the output file DOES NOT EXIST after every refusal, and that no `.o` is ever
produced for a refused program.

### P1-m0.7 Test runner panel (each check DIRECT rc, separate commands; never batched)

`tools/mir_aot_test.py` (python3, stdlib only) runs, per positive fixture:

1. `pli80mir --export <n> -o tmp.mir M.pli` TWICE in fresh processes → rc 0, byte-equal
   stdout, stdout == the reviewed `hir/mir-expected/M*.mir` pin (addition-only pin law:
   expected files are COPIES of reviewed measured output at the fixture step, never
   regenerated over a pin without an explicit supersede record).
2. `mir2o -f M.mir M.o` rc 0 (this also IS the MIR-parser acceptance check, brief §8).
3. Evidence capture into `build/mir-aot/`: `readelf -h` (must say `Type: REL` and
   `Machine: Advanced Micro Devices X86-64`), `readelf -r`, `nm` (must list `T pli80_<n>`),
   `objdump -d` (the generated function's native instructions), `ldd` of the final program
   (must NOT list libmir/MADC/OCaml — only libc/vdso/loader).
4. `gcc -O2 -DENTRY=pli80_<n> -DEXPECTED=<value> native_check.c M.o -o M.exe` rc 0; run the
   executable in TWO fresh processes: rc 0 and stdout exactly `<value>`.
5. Pipeline proof: the same fixture through `pli80hir.exe` also exits 0 (the HIR path itself
   is green — a MIR success whose HIR dump failed would be a contradiction).

Per negative fixture: run `pli80mir` twice (fresh procs) → pinned rc 2, ZERO stdout, pinned
stderr bytes, deterministic, and NO output file (brief §5 "no misleading artifact"). The
emitter is NOT run for negatives.

Corruption controls (non-vacuity, brief §7): (C-a) take the M01 emitted MIR and replace the
`mul` instruction with `add` (6+7 = 13 ≠ 42), re-emit, re-link, run: the native test MUST
exit nonzero and report the differing value; (C-b) rebuild the SAME unmodified `.o` driver
with `-DEXPECTED=43`: MUST exit nonzero. Both prove the pass is an EXECUTION result, not a
tautology. If either control "passes", the runner fails (a gate that cannot fail is not a
gate, PROTOCOL #8).

### P1-m0.8 Falsification criteria (each a STOP-and-attribute gate, modelled on §P1-h.5)

- **T1** `pli80c.exe` sha256 stays `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`
  after EVERY build step, checked DIRECT.
- **T2** every PREVIOUS `hir/expected/*` and `hir/fixtures/*` byte unchanged
  (`git diff --exit-code -- hir/expected hir/fixtures` clean; the MIR pins live in NEW
  directories and never inside the frozen set).
- **T3** `timeout 900 python3 tools/hir_test.py` rc 0 with **220 OK** and ALL 11 existing
  semtest OK numbers UNMOVED (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2
  H16 12/5 H17 12/5 H18 7/3 H21 5/2); F7/F8/F10/S8/T5/T6 greps stay green over the NEW
  files automatically (glob) — any hit is a STOP (rename code, never weaken a pattern).
- **T4** FULL compile-tier gate rc 0 → `build/gate-e54p1m0-reg.log` with FROZEN panel
  **1328/1328, 190/190, 9/9, 149 rows 0/0, census 16/0/25/0, prose 5**. Any move = STOP,
  attribute, revert. Plus fresh `dune build --build-dir _build-e54p1m0` rc 0, ZERO `Error`,
  warning hist **122**, fresh exe sha (computed separately) == kept exe.
- **T5** `git diff --exit-code -- ocaml/lib ocaml/bin` EMPTY at every commit; goldens,
  inventory, census, coverage untouched; ledger stays 203 `## C` headers ending **C380**;
  NO new claim (native execution of MIR is DRPLi engineering evidence, not DR behaviour —
  the DR oracle is never consulted for it; the i64 carrier is explicitly NOT a DR claim).
- **T6** ZERO oracle: no DR compiler, cpmsim, LINK-80, `--runtime`, `--link-run` or rune-ci
  invocation anywhere in this slice.
- **T7** the pinned lab + submodule stay at their exact commits and `git status`-clean
  (no lab file, pin or revision modified); the lab path stays git-IGNORED from the DRPLi
  repository; nothing under `build/` is committed.
- **T8** determinism: both fresh-process runs of every positive fixture byte-equal
  (MIR text) and both native runs report the same value; the MIR text of each fixture is
  EXACTLY the committed pin.
- **T9** non-vacuity: the runner proves BOTH corruption controls fail natively (and says
  so explicitly); independently specified expected results (42/45/10) live ONLY in the
  runner table + this PLAN, never in generated artifacts.
- **T10** no positive test passes by IGNORED work: every positive fixture's MIR text must
  contain one `func` + `export`, its `.o` must export the symbol (nm), and the value must
  come from execution; the N-fixtures each name the construct they refuse.
- **T11** `handoff.config.json` NEVER staged; explicit-path commits only; no push.

### P1-m0.9 Work order (exact order — the successor contract)

1. Baseline first-hand verification (build rc 0; exe `172595d5…`; `hir_test.py` rc 0, 220 OK)
   — **DONE** (this session, log `build/p1m0-baseline-hirtest.log` — copy of the first run).
2. This pre-registration committed BY EXPLICIT PATHS before any `ocaml/` compiler-source
   byte (PROTOCOL #1): `spec/lab-evidence/e2e54/PLAN.md` only.
3. Implement `ocaml/hir/diagnostic.ml` (append E18/E19/E20) + `mir_backend.ml` +
   `pli80mir.ml` + `dune` stanza → `dune build` rc 0 (DIRECT) → T1 → T2 → `hir_test.py` rc 0
   (T3) → ONE commit (the library list change and its consumers land together).
4. Fixtures + pins: create `hir/mir-fixtures/*.pli` (CRLF+^Z, the shapes already measured in
   scratch §D-7; review EVERY emitted MIR line against §P1-m0.4 BEFORE pinning),
   `cp` measured output to `hir/mir-expected/` → hir_test still rc 0 → commit. Predictions
   in §P1-m0.2 are falsified-not-fitted; deviations recorded here and in RESULTS.
5. `tools/mir_aot/{mir2o.c,build_native.sh,native_check.c}` + `tools/mir_aot_test.py`;
   build script rc 0; full runner rc 0 (all panels incl. evidence + corruption controls) →
   commit.
6. FULL gate rc 0 → `build/gate-e54p1m0-reg.log`; fresh `--build-dir _build-e54p1m0` (T4).
7. CLOSE: `RESULTS.md` §P1-m0 (T1–T11 WITH measured values; the five MILESTONES stated
   separately per brief §10 — HIR lowered / MIR generated / object emitted / executable
   linked / native execution; the explicit unsupported-semantics matrix; every deviation
   recorded NOT fitted), update `docs/architecture/backend-boundary.md` (§7-5), PLAN
   dashboard CLOSED, durables + guard checkpoint.
8. **STOP** (brief §11). IF/ELSE, parameters, arrays, calls, I/O, macOS/AArch64, production
   backend are NOT authorized by this slice; each needs its own pre-registration.

### P1-m0.10 Expected outcomes and the unsupported-semantics matrix (pre-registered)

Expected: all three positives lower, emit deterministic MIR, produce an `ET_REL` x86-64
`.o`, link with the system linker and EXECUTE returning 42 / 45 / 10; all five MIR-level
negatives refuse loudly with E18/E19 (and no artifact), the two HIR-level negatives keep
their existing E02/E08 channels; both corruption controls fail natively; every historical
number unmoved. If native execution fails anywhere, the slice records the precise failing
step and STOPs at the milestone it reached — partial success is reported by MILESTONE, never
as end-to-end.

Unsupported-semantics matrix (the slice's honest boundary; each row refuses, none guesses):
control flow (IF/WHOLE-block branching) — deferred milestone (brief §3 permits IF/ELSE only
AFTER this slice passes, never silently); loops/recursion — refused; calls (any `Call_e`,
`Call_s`, nested procs) — refused; parameters/return of a non-integer — refused; arrays —
refused; `Convert` (any precision/scale change, DEC, CHAR) — refused (rounding/overflow
profile-UNKNOWN honoured); uninitialized reads — refused (static straight-line flow);
values leaving `W(p)` — refused (overflow behaviour UNKNOWN honoured); `Static`/`External`
storage — refused; multi-procedure programs and fall-through/implicit return — refused;
division/floating point — outside the HIR subset already; DEC/character data — outside the
HIR subset already. `Target.profile` fields `overflow_behavior`, `rounding_rules`,
`float_semantics` REMAIN Unknown and are honoured by refusal, never defaulted (brief §4).

### P1-m0.11 Dashboard update

| slice | status | notes |
|---|---|---|
| P1-m0 | **CLOSED 2026-11-09** | first native MIR AOT path PROVEN end-to-end: five milestones ALL passed, 42/45/10 EXECUTED natively, T1–T11 ALL PASS; RESULTS §P1-m0; roadmap amended §RD-COSMO (`186a59d6`) |
| P1-mC | **CLOSED 2026-11-09** | Cosmopolitan static-link feasibility ANSWERED POSITIVELY: the genuine unchanged MIR objects link into plain static Linux x86-64 ELF (no PT_INTERP/DT_NEEDED, no APE step) and EXECUTE 42/45/10; pinned cosmocc-4.0.2; runner rc 0 (25 checks); gate FROZEN ALL HIT; RESULTS §P1-mC, arch §7-6; P1-m1 remains PROPOSED ONLY |


## §RD-COSMO — Operator roadmap amendment: Cosmopolitan as preferred native libc (VERBATIM; ROADMAP decision, NOT a §P1-m0 scope change)

Recorded VERBATIM from the operator turn of session
`01a1c0dc-4504-700d-bdb6-dc2b98a19e20` (transcript JSONL), stored at the ignored path
`build/p1m0-amendment-true.md` and machine-compared against this embedding: the stripped
blockquote below equals the source BYTE-FOR-BYTE (40 content lines, 39 newlines, NO
trailing newline). This amendment does NOT change the already-preregistered §P1-m0
acceptance criteria (PLAN §P1-m0.2–§P1-m0.11 stand VERBATIM) and authorizes NO new code.
ACTION AT §P1-m0 CLOSE-OUT (§P1-m0.9 step 7): record the PROPOSED stages P1-mC, P1-m1 and
the future portable-native items VERBATIM-IN-SPIRIT (as listed below) in
`spec/lab-evidence/e2e54/RESULTS.md` §P1-m0 roadmap subsection AND in
`docs/architecture/backend-boundary.md`; each subsequent stage still requires its own
PROTOCOL #1 pre-registration and explicit operator authorization.

> # E2E-54 — Operator roadmap amendment: Cosmopolitan as preferred native libc
>
> The operator selects **Cosmopolitan Libc as the preferred standard C runtime for future DRPLi/MIR native executables**.
>
> Short-term target: Linux x86-64 static ELF. APE is NOT required unless it becomes trivial at no significant additional complexity.
>
> This is a ROADMAP decision, not authorization to expand the active P1-m0 implementation.
>
> At P1-m0 close-out, record the following PROPOSED stages in RESULTS and `docs/architecture/backend-boundary.md`:
>
> **P1-mC — Cosmopolitan static-link feasibility**
>
> - Reuse the genuine `.o` produced from PL/I → HIR → MIR.
> - Pin a Cosmopolitan/cosmocc toolchain version.
> - Investigate `x86_64-unknown-cosmo-cc` with `-moptlinux`.
> - Build a small native C test driver with Cosmopolitan.
> - Attempt static linking with the MIR-generated object.
> - Verify ABI compatibility, relocations, native execution, expected result and absence of `PT_INTERP` / `DT_NEEDED`.
> - Preserve GCC/glibc linking as a diagnostic reference, not the preferred deployment target.
> - Do not substitute generated C for MIR-generated machine code.
>
> **P1-m1 — Minimal PL/I console runtime**
>
> - Implement small C adapters for integer/string input and output.
> - Link the adapters against Cosmopolitan.
> - Explicitly distinguish PL/I I/O semantics from the underlying libc functions.
> - Test EOF, input errors, buffer bounds and deterministic output.
> - Do not reimplement PLILIB wholesale.
>
> **Future — Portable native formats**
>
> - Investigate ARM64 native output.
> - Investigate APE only after the static ELF integration works.
> - Keep HIR and MIR lowering independent of the selected libc and final executable format.
>
> The build-time MIR emitter may still depend on host libraries. The static-link requirement concerns the GENERATED executable.
>
> Do not change the already-preregistered P1-m0 acceptance criteria or active code scope. Each subsequent stage requires its own PROTOCOL #1 preregistration and operator authorization.
>
> **Architectural principle: Cosmopolitan-first native runtime, backend-independent HIR, no mandatory glibc runtime dependency.**

<!-- RD-COSMO-END -->

## §P1-mC — Pre-registration: Cosmopolitan static-link feasibility (committed BEFORE any source or test-tooling modification)

Operator authorization of 2026-11-09 (brief reproduced in §P1-mC.0 below; recovered from the
session transcript at the ignored path `build/p1mc-brief.md`). Scope: link the GENUINE
MIR-generated native objects of §P1-m0 against a PINNED official Cosmopolitan/cosmocc
toolchain and verify a plain static Linux x86-64 ELF (NO APE requirement, NO glibc runtime
dependency). This is a linker/runtime FEASIBILITY slice: `ocaml/lib` and `ocaml/bin` are NOT
touched, HIR/`Semantic_env`/MIR lowering semantics are FROZEN as delivered by §P1-m0, the
historical gate must stay green, and no PL/I I/O is implemented. §RD-COSMO (above) is the
roadmap authority; this section is its first stage's CONTRACT.

### P1-mC.0 Operator brief (essential contract, abridged from the authorized brief)

Starting reference `1b23900e4c9d8ec193583b45949f367671869c93`; E2E-54/P1-m0 CLOSED and its
42/45/10 results authoritative. Target: static Linux x86-64 ELF; APE NOT required. (1) Verify
HEAD/worktree/fingerprint/toolchain, preregister here and COMMIT the plan before any source or
test-tooling change; preserve P1-m0 results unaltered. (2) Use the official
`github.com/jart/cosmopolitan` distribution and its `tool/cosmocc/README.md`; inspect local
toolchains first, else acquire a SPECIFIC official release in an IGNORED dependency directory;
record exact version, archive checksum, executable identity and options; never rely on an
unversioned `latest` in the reproducible build; investigate `-moptlinux` (AVX CPU requirement)
and `-mtinylinux` (compact runtime) and record OBSERVED behaviour rather than assuming
equivalence; prefer the architecture-specific compiler if that is what yields a plain ELF; do
NOT add an APE conversion step just to pass. (3) Re-run the existing P1-m0 pipeline to generate
M01 `pli80_calc`→42, M02 `pli80_m02`→45, M03 `pli80_m03`→10 with `pli80mir` and the `mir2o`
emitter UNCHANGED; record object hashes before linking; the SAME `.o` must feed both the
existing gcc/glibc diagnostic link and the new Cosmopolitan link. No C translation of PL/I, no
handwritten replacement function, no object rewriting, no second code-generation path. (4)
Establish a Cosmopolitan-ONLY control first (start, call a local integer function, print an
integer, exit status; record format/static properties/output) to separate a broken installation
from MIR incompatibility — a passing control is NOT proof of MIR integration. (5) Link each
genuine MIR `.o` with the pinned toolchain via the EXISTING `tools/mir_aot/native_check.c`
driver with only the minimum build-system change; evaluate separately object acceptance,
export resolution, zero-argument `i64` ABI, startup linkage, native execution, absence of
dynamic dependencies; on failure retain exact diagnostics and CLASSIFY the failure (object
format / relocation / linker script / ABI / startup / unresolved symbol / toolchain
configuration); do NOT patch MIR blindly to make a link pass. (6) Inspect every successful
executable (`file`, `readelf -h/-l/-d`, `nm`, `objdump -d`): native x86-64, NO `PT_INTERP`, NO
`DT_NEEDED`, no glibc/libmir/libmadc/OCaml dependency, MIR-originating code present, correct
result in TWO fresh processes; statically linked libc code inside the executable is EXPECTED;
`ldd` is supplementary only; if a launcher script or APE artifact appears, identify it as such
and do NOT label it a verified static ELF. (7) Keep the independent expected values 42/45/10
(never derived from MIR text, disassembly or output) and run BOTH non-vacuity controls on the
Cosmopolitan path (C-a corrupted arithmetic must give a wrong value and fail; C-b wrong
expected must fail); keep the dynamic-link result as a diagnostic reference. (8) Regression
boundaries (below). (9) Deliverables: focused P1-mC test script + reproducible build
instructions, logs/maps/ELF inspections/symbols/disassembly under ignored `build/`, commit the
preregistration + scripts + docs by explicit paths, result matrix, toolchain/configuration
record, update `spec/lab-evidence/e2e54/RESULTS.md` and
`docs/architecture/backend-boundary.md`, PROPOSE (do not implement) the P1-m1 console-I/O
roadmap. Never stage `handoff.config.json`; never reset/clean unrelated state; no push.
(10) Stop condition: at least one REAL PL/I-originating MIR object linked with Cosmopolitan
into a verified static Linux ELF, executed natively with the independently expected result,
historical compiler unchanged; prefer all three; on an environmental/linker blocker document
the precise stage and reproduce the failure — a truthful partial beats substitution. Then close
P1-mC, attest the checkpoint and STOP.

### P1-mC.1 MEASURED environment facts (this session, first-hand — before any code byte)

- HEAD `1b23900e…`; `git diff --exit-code -- ocaml/lib ocaml/bin` rc 0; kept exe
  `sha256(ocaml/_build/default/bin/pli80c.exe)` = `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`
  (verified DIRECT); P1-m0 evidence `build/mir-aot/{M01,M02,M03}.{mir,o,exe}` present from the
  closed slice; `build/p1m0-deps/mir2o` present; lab pins untouched.
- NO system Cosmopolitan: `command -v cosmocc` empty. Only foreign vendored copy:
  `/home/john/Téléchargements/llamafile/.cosmocc/3.9.7/` (another project's dependency; it has
  `lib/{,tiny,optlinux}` and NO `tinylinux`) — inspected, NOT used.
- PINNED ACQUISITION (ignored `build/p1mc-deps/`): `cosmocc-4.0.2.zip`, the latest official
  release asset (tag `4.0.2`, published 2025-01-06), size 441 763 966 B (== GitHub asset
  size), **SHA-256 `85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44`**;
  `bin/cosmocc --version` = `cosmocc (GCC) 14.1.0`; bundled ld = `x86_64-linux-cosmo-ld`
  (GNU binutils from the distribution), gcc driver
  `bin/x86_64-linux-cosmo-gcc` (raw) and `bin/x86_64-unknown-cosmo-cc` (wrapper script).
- **`-mtinylinux` IS NOT SUPPORTED by 4.0.2** — zero occurrences in its README or wrapper
  scripts; only `-mtiny`, `-mdbg`, `-moptlinux` exist. The mode is documented ONLY on
  post-release `master`. FALSIFIED prediction (recorded, not fitted): the brief's
  "investigate `-mtinylinux` as a possible default" cannot be executed on a pinned official
  release; per the brief's own rule ("Use whichever is supported by the pinned toolchain") the
  slice measures `-moptlinux` (Linux-optimized) and `-mtiny` (size-optimized, portable) and
  records `-mtinylinux` as UNAVAILABLE.
- **Host `binfmt_misc` blocker (measured):** the toolchain's APE helper programs (`*.ape`,
  `fixupobj`, `ape-x86_64.elf`) carry `MZ` magic; this machine registers the `DOSWin` binfmt,
  so every wrapper-script step is executed by **wine** — a 4-line `-c` compile exceeded a
  100 s `timeout`; `COSMO_APE=native` did not help. Output artifacts are still produced
  (non-executable, since the final `chmod.ape` step dies) and RUN NATIVELY once `chmod +x`:
  `-moptlinux` → 840 944 B `ELF 64-bit LSB executable, x86-64, (GNU/Linux), statically linked`
  printing `42` rc 0; `-mtiny` → 216 504 B `(SYSV) statically linked`, same result.
  ⇒ classify **toolchain configuration / environmental**, NOT object-format or ABI.
  Work-around to be measured: drive `x86_64-linux-cosmo-gcc`/`-ld.bfd` DIRECTLY with the flags
  the wrapper records in `BUILDLOG` (no `.ape` helper on the link path); the raw-toolchain use
  is explicitly documented by Cosmopolitan ("Using these grants full control over your
  compiler"; "zero expectation of support … all responsibility for ABI-related flags"), so the
  flag set used here must be recorded VERBATIM as a slice decision.
- AVX: host CPU flags include `avx avx2 avx512f`; 4.0.2 `-moptlinux` claims AMD-K8+ (2003)
  while `master` claims `-mavx`/post-2011 — record BOTH, judge by EXECUTION on this host.

### P1-mC.2 Scope and frozen boundaries

AUTHORIZED: new `tools/mir_aot_cosmo_test.py`; minimal additions under `tools/mir_aot/`
(a Cosmopolitan link recipe + optional raw-toolchain shim script); `spec/lab-evidence/e2e54/`
(PLAN/RESULTS); `docs/architecture/backend-boundary.md`; `LEARNINGS.md`/`PROGRESS.md`/
`HANDOFF.md` prose. FORBIDDEN: ANY byte under `ocaml/lib/` or `ocaml/bin/`; any change to
`ocaml/hir/` (HIR/`Semantic_env`/MIR lowering FROZEN), `tools/mir_aot/mir2o.c`,
`native_check.c` (driver reused UNCHANGED; only the LINK command changes), the MIR pins in
`hir/mir-*`, historical goldens/inventory/coverage/census, `thirdparty/` (never advanced).
No PL/I I/O, no APE step, no ARM64, no object rewriting, no C substitution for MIR code, no
second code-generation path. ZERO oracle: no DR compiler, cpmsim, LINK-80, `--runtime`,
`--link-run`, Rune CI.

### P1-mC.3 Result expectations (INDEPENDENT, never re-derived from MIR/disassembly/output)

M01 → **42**, M02 → **45**, M03 → **10** — the §P1-m0.6 hand-computed values, unchanged. Two
fresh processes per fixture. Controls, on the Cosmopolitan path: C-a (`mul`→`add` in M01 MIR,
re-emitted, re-LINKED WITH COSMOPOLITAN) must EXECUTE and report **13**, and the test must
FAIL; C-b (unmodified M01 `.o`, `-DEXPECTED=43`) must FAIL. If either control passes, the
runner fails.

### P1-mC.4 Falsifiers (each a STOP-and-attribute gate)

- **CT1** `pli80c.exe` sha256 `172595d5…` held DIRECT before and after every step; `git diff
  --exit-code -- ocaml/lib ocaml/bin ocaml/hir hir/` rc 0 at every commit.
- **CT2** the object fed to Cosmopolitan is BYTE-IDENTICAL (sha256) to the object fed to the
  gcc/glibc diagnostic link, and both come from `pli80mir` + unchanged `mir2o` in this run.
- **CT3** for every PASSING executable: `readelf -l` shows NO `PT_INTERP`; `readelf -d` reports
  no dynamic section / NO `DT_NEEDED`; `file` says statically linked x86-64 ELF; `nm` lists the
  `pli80_<name>` symbol; `objdump -d` contains the MIR-originating function; two fresh
  executions give the independent value. A launcher script or APE artifact is reported AS SUCH,
  never counted as a static ELF.
- **CT4** the Cosmopolitan-only control (no MIR object) is recorded separately; a control
  success is never described as MIR integration, and a control failure is classified as a
  broken toolchain, not an MIR defect.
- **CT5** full historical gate rc 0 with FROZEN panel 1328/1328-190/190-9/9-149 rows 0/0-16/0/
  25/0-prose 5 → `build/gate-e54pmc-reg.log`; `timeout 900 python3 tools/hir_test.py` rc 0
  (220 ok, 11 numbers UNMOVED); `timeout 900 python3 tools/mir_aot_test.py` rc 0 (27 checks,
  gcc/glibc path preserved as diagnostic reference); fresh `dune build --build-dir
  _build-e54pmc` rc 0, ZERO `Error`, warning hist 122, sha == kept exe.
- **CT6** zero oracle; ledger stays 203 `## C` headers ending **C380** (native-linking
  feasibility is DRPLi engineering evidence, never a DR claim); `handoff.config.json` NEVER
  staged; explicit paths only; no push; nothing under `build/` committed; every command under
  a short `timeout` (operator constraint).

### P1-mC.5 Work order (successor contract)

1. Commit THIS pre-registration (explicit path `spec/lab-evidence/e2e54/PLAN.md`) BEFORE any
   source/test-tooling byte. — **DONE** (this commit).
2. Measure the raw-toolchain link recipe that avoids the `.ape`/wine path (`BUILDLOG` capture;
   record the flag list VERBATIM); rebuild `build/p1m0-deps/mir2o` if absent
   (`sh tools/mir_aot/build_native.sh`), re-run the P1-m0 pipeline for M01/M02/M03, record the
   three `.o` sha256 values BEFORE linking.
3. Cosmopolitan-ONLY control: build + run a trivial C driver with the pinned toolchain; record
   format, static properties, output, exit status. No MIR object involved.
4. Link the three genuine MIR `.o` with Cosmopolitan (`native_check.c` unchanged, `-DENTRY`/
   `-DEXPECTED` from the §P1-m0.6 table); on failure keep exact diagnostics and classify per
   §RD-COSMO categories; do NOT patch MIR.
5. Write `tools/mir_aot_cosmo_test.py` (positives: emit → object sha record → link → ELF panel
   CT3 → two fresh runs; both controls C-a/C-b on the Cosmopolitan path; evidence into
   `build/mir-cosmo/`), run to rc 0, commit scripts+docs.
6. Full regression CT5; then RESULTS §P1-mC (result matrix: control / object acceptance /
   static link / native execution) + arch doc update + PROPOSED P1-m1 roadmap (integer and
   string console I/O through Cosmopolitan — NOT implemented here); close, attest, **STOP**.

---

## §P1-m1 — Pre-registration: Minimal console I/O over the native MIR path (committed BEFORE any repository source byte)

Operator authorization of 2026-11-10: **P1-m1 (minimal console I/O) is AUTHORIZED** as the
third §RD-COSMO stage — the roadmap row recorded PROPOSED in RESULTS §P1-mC.5 and PLAN
§P1-m0.8, promoted to an authorized slice by that explicit operator decision (audit recorded
in `LEARNINGS.md` § "E2E-54/P1-m1 hop 1"; the contract reproduced here is the authoritative
brief for this slice). Type of work: **backend engineering, ZERO oracle calls** (none
planned or authorized; console semantics are DRPLi engineering evidence, never DR claims —
the ledger stays 203 headers ending **C380**). Starting reference `61129bd2` (the §P1-mC
close commit; verified first-hand at hop 1); pre-registration hop 3 HEAD `96610195` (zero
repo code byte since the starting reference; baseline trio green at `612275bb` and re-verified
at this HEAD: `dune build` rc 0; kept exe
`172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` DIRECT; `ocaml/lib` +
`ocaml/bin` byte-clean).

All design authority for this slice was MEASURED in three probe hops and is digested in
`LEARNINGS.md` §§ "E2E-54/P1-m1 hop 1/2/3" — READ hop 2 + hop 3 FIRST. Every prediction in
this section either cites a first-hand measurement (hops 1–3 scratch probes in the IGNORED
`build/p1m1-scratch/`, NEVER committed) or is explicitly marked UNPROVEN and will be
measured-first at pin time.

### P1-m1.0 Milestones (SEPARATE deliverables)

- **m1a — integers.** `put list(<integer expression>);` and `get list(<scalar variable>);`
  over the console runtime, end to end: HIR lowering → MIR emission (import/protos/labels/
  branches) → mir2o object with undefined host imports → Cosmopolitan static link → native
  execution with observable stdout/stderr/exit-status. GREEN means: fixtures M04/M05 pinned,
  the m1a negative pins landed, the runner panel for m1a legs rc 0, and the full FROZEN
  regression panel (§P1-m1.9) all hit.
- **m1b — characters (LITERAL put ONLY).** `put list('<printable literal>');`. Character
  VARIABLES are blocked by the EXISTING `HIR-E02` declaration refusal (`dcl c character(3)`
  is refused today; `hir/mir-fixtures/N4.pli` pins it) — documented, NEVER a new refusal; a
  char-variable put stays unreachable until declaration support exists. m1b lands only after
  m1a is green; m1a stays independently deliverable.

CLOSE after both milestones: RESULTS §P1-m1 + `docs/architecture/backend-boundary.md` §7-7
+ dashboard CLOSED + durables, then **STOP** — IF/ELSE in MIR, file streams, FORMAT/EDIT,
ON-unit handling, char declarations, APE, ARM64 and production-backend adoption all remain
PROPOSED ONLY and each needs its own PROTOCOL #1 pre-registration plus explicit operator
authorization.

### P1-m1.1 MEASURED design facts (hops 1–3, first-hand; this section pre-registers, it does not re-measure)

1. **Zero-pin law (accepted):** every candidate console form (`put skip;`, `put page;`,
   `put file(f) list(x);`, `put edit(x)(b(15));`, `put item(i);`, `put from(x);`,
   `put list('<lit>');`, `put list(x, y);`, `get list(x + 1);`, `get list(a(1));`,
   `get list('z');`, `on error put list(x);`) PARSES through the frozen parser and dies
   today at the EXISTING catch-all `HIR-E05: line N: statement PUT|GET|ON unit is outside
   the P0 HIR subset`; NO existing fixture (H-series or M-series) contains put/get, so
   accepting the subset moves ZERO committed pins.
2. **Line-number law (accepted, measured both directions):** LF fixtures report LOW
   statement lines; CRLF+`^Z` fixtures report EXACT lines. Every new pin is measured on
   CRLF+`^Z` fixture bytes.
3. **Trailing control items are NOT pinnable (accepted):** `put list(x) skip;` and
   `get list(x) skip;` die in the PARSER via the pre-existing UNCAUGHT `Parse_error` hole
   (rc 2, zero stdout, OCaml `Fatal error: exception Pli80.Parser.Parse_error(...)` on
   stderr; recorded in P1-m0 hop 2, identical in `pli80hir.exe`). They get NO E21 arm and NO
   negative pin. LEADING control items (`Pi_ctl` items, e.g. `put skip;`) ARE E21 arms.
4. **Precision ceiling is the E01 bind channel (accepted):** `dcl x fixed bin(16)` (and a
   `returns(fixed bin(16))` result) dies at `HIR-E01` — the existing no-bypass bind refusal
   ("FIXED BINARY(16) exceeds DR's FIXED precision limit 15 ... [TBD]"). Declaration-level
   precision is therefore NOT an E22 arm; only what the bind channel lets through can reach
   the console gates.
5. **Additive mir2o route PROVEN (accepted, hop 2):** registering every `MIR_import_item`
   with `MIR_load_external(ctx, name, (void *) pli_ext_dummy)` BEFORE `MIR_link` makes strong
   host imports emit as UNDEFINED STRONG ELF symbols (the dummy address never enters the
   object; `nm -u` shows `U pli_console_*`, `U exit`); a module WITHOUT imports takes ZERO
   extra steps and its object is BYTE-IDENTICAL to the frozen §P1-m0 pin (M01 measured);
   objects deterministic ×2. The pinned madc fork itself is NEVER touched.
6. **Production layout PROVEN (accepted, hop 2 probes probe2/probe4, glibc; re-read hop 3):**
   exact module/func/proto/import/string/label/branch/local shape reproduced VERBATIM in
   §P1-m1.5 below; zero-arg proto `p_nl:\tproto\ti64` parses and calls fine; string items
   escape `\"` and `\\` and decode to exact bytes (31-byte literal verified byte-for-byte);
   one `import` line listing ONLY the used names in canonical order.
7. **Runtime ABI + status laws MEASURED (accepted, hop 2; §P1-m1.6):** statuses
   OK=0 EOF=1 BAD=2 RANGE=3 IOERR=4; get skips leading space/tab/CR/LF, accepts an optional
   sign, the digit run ends at the first non-digit WHICH IS CONSUMED (`123abc` → 123 OK),
   EOF after a complete number is a GOOD read, lone `-` → BAD, a digit run longer than the
   24-byte scan buffer → RANGE, a value outside `[lo,hi]` → RANGE; any nonzero status
   fail-fasts through `exit(status)` (observable nonzero process rc); `exit()` flushes stdio
   so earlier partial stdout still appears — EOF never masquerades as success; cosmo tiny
   end-to-end ran: stdout EXACTLY `42\nHello, console!\n124\n`, `driver-return=124` on
   stderr, rc 0 (and failure legs rc 2 / rc 1 with partial output preserved).
8. **WINDOW LAW (accepted, critical for fixtures):** after `get list(x)` the provable
   interval of `x` IS the full declared window `W(p) = ±(2^(p-1)-1)`; any later arithmetic
   that can leave `W(p)` refuses `HIR-E19` (e.g. `x = x + 1` after a bin(15) get dies —
   16384 > 16383). Console fixtures therefore PUT/RETURN the got value directly.
9. **Parser/AST shape facts (accepted, hop 1–2 reads):** `parse_put`/`parse_get` ALWAYS set
   `stream=None`; a bare file name arrives as an `on_opts` entry `FILE(ident)`; the LIST
   route arrives as `kind=List_` with `items = ctl_items @ [Pi_data ...]`; `'Hello'` lowers
   from `Estring` (the lexer folds doubled quotes); `put from(x)` parses AST-INDISTINGUISH-
   ABLY from `put list(x)` (deviation §P1-m1.10-1).
10. **F8 vocabulary law (accepted):** the strip-greps glob ALL `ocaml/hir/*.ml`; new code
    strings must avoid `\b(size|offset|reloc|pool)\b` (say "len"), hex `0x...` (say
    "32..126"), `op_`, and UPPERCASE mnemonic words INCLUDING single letters (C, M, P, Z...).
    Lowercase MIR mnemonics (`call`, `ret`, `mov`, `local`, `import`) are safe.

### P1-m1.2 Accepted-syntax contract (the FINAL subset after m1a + m1b; anything else refuses LOUDLY)

A `Sput` lowers iff ALL hold:
- `stream = None` and `on_opts = []` (default console stream only);
- `kind = List_`;
- `items` contains EXACTLY ONE item and it is `Pi_data e`;
- either (m1a) `e` lowers through the EXISTING `lower_expr` subset (integer-valued
  `FIXED BINARY(p,0)`, p in 1..15 — every HIR integer expression qualifies after the E02/E08/
  E19 channels have had their say; a literal above `W(15)` keeps refusing `HIR-E08`, an
  uninitialized variable read keeps refusing `HIR-E19`, an unresolved name keeps refusing
  `HIR-E06` — the EXISTING channels, never bypassed);
- or (m1b) `e` is `Ast.Estring s` with `String.length s >= 1` and EVERY character in the
  printable console range 32..126 (empty literal → `HIR-E22`; out-of-range character such
  as a TAB → `HIR-E22`).

A `Sget` lowers iff ALL hold:
- `stream = None` and `on_opts = []`;
- `kind = List_` (`get edit`/`get const` kinds refuse `HIR-E21`);
- `items` contains EXACTLY ONE `Pi_data e`;
- `e` is a bare name `Eident` whose name resolves through the EXISTING `resolve`/
  Semantic_env channel (unresolved keeps `HIR-E06`);
- the resolved symbol is a scalar (NOT an array row) of type `FIXED BINARY(p,0)` with
  automatic storage — an array designation (whole or `a(i)`) or any expression target
  (`x + 1`, `'z'`) refuses `HIR-E21` BY SHAPE.

Statement-position invariants inherited UNCHANGED from §P1-m0: the export procedure stays
zero-argument with a `FIXED BINARY(p,0)` result and a straight-line body ending in
`RETURN(expr)`; `put`/`get` are ordinary statements inside that body (any position after the
declarations that the body law already allows).

### P1-m1.3 Refusal contract — `diagnostic.ml` APPENDS two codes (append-only law; no existing code changes meaning)

`let e_io_construct = "HIR-E21"` (* console PUT/GET construct outside the subset — arms BY
NAME: statement options (the `io_opt` key, e.g. FILE); kind (EDIT/ITEM and the GET kinds);
leading control items (SKIP/PAGE/LINE); item count /= 1; item class (not a single data
item); GET target shape (not a scalar name designation) *)

`let e_io_domain = "HIR-E22"` (* console domain outside the subset: a PUT literal outside
the printable range 32..126; an empty PUT literal; a defensive non-FIXED-BINARY(p,0) I/O
operand TYPE, expected UNEXERCISED because the declaration channels (E02/E01) precede it —
same honest status as the P1-a2 E16 arm *)

Arms fire at LOWERING (`hir_build.ml`), BEFORE any MIR decision, in this order: options →
kind → item scan (any `Pi_ctl` → ctl arm; count /= 1 → item-count arm; non-`Pi_data` class →
item-class arm) → data-expression lowering (existing channels) → literal charset/empty (m1b)
→ GET target shape (after `resolve`, before anything else touches the symbol). Every message
NAMES the offending construct (falsifier T10 discipline). During m1a (before m1b) a literal
PUT item refuses via the item-class arm; that arm's literal wording is TRANSIENT (m1b
replaces it) and gets NO committed pin — honest note, no superseded record needed because no
pin existed.

Trailing control items are OUT of scope of this contract (fact 3: parser death, unpinnable).
`ON` units stay the EXISTING `HIR-E05 statement ON unit ...` catch-all — untouched.
`put from(x)` is ACCEPTED as a list put (§P1-m1.10-1).

### P1-m1.4 HIR representation contract — `ocaml/hir/hir.ml` ADDITIVE (existing bytes frozen)

```
type put_source =
  | P_value of expr                          (** m1a: an integer expression  *)
  | P_text  of { text : string }             (** m1b: a validated literal    *)
```
new `stmt_kind` arms `Put of put_source` and `Get of designator` (only `D_var` is ever
produced — reference-position designators REUSE `Hir.designator` resolved through the
EXISTING `resolve`; NO new name resolver, NO new node for arrays). `dump_stmt` gains (bytes
modeled on the existing `return value`/`assign` lines; `[line N]` is the statement line):

- `P_value`: `put value  [line N]` then the expression dumped at indent+1 (shared `dump_expr`);
- `P_text`: `put literal  [line N]` then at indent+1 one line `literal '<text>'  [line N]`;
- `Get d`: `get  [line N]` then the designator dumped at indent+1 through the SHARED
  `dump_designator` (`Pure`, symbol-projection type text — exactly the assignment-target rendering).

`stmt_kind_name` (mir_backend) gains `"put"` / `"get"` for the body-end diagnostic. NO H
fixture contains put/get, so every committed H dump byte is unchanged (T2); the dump shapes
above are reviewed in scratch runs of the M fixtures through `pli80hir.exe` and are NOT
pinned under `hir/expected` (this slice's pins live in `hir/mir-*` only).

### P1-m1.5 MIR-backend emission contract — `ocaml/hir/mir_backend.ml` ADDITIVE (layout PROVEN in probe2/probe4)

A procedure WITHOUT console statements emits the EXISTING bytes EXACTLY (M01/M02/M03 pins
and every H dump byte-frozen; CT2/T9 re-check). With console statements the module gains,
IN THIS ORDER:

1. protos (only the ones used, fixed relative order p_put, p_get, p_text, p_nl, p_exit),
   VERBATIM as measured:
   `p_put:\tproto\ti64, i64:v` / `p_get:\tproto\ti64, i64:out, i64:lo, i64:hi` /
   `p_text:\tproto\ti64, i64:s, i64:n` / `p_nl:\tproto\ti64` / `p_exit:\tproto\ti64:c`
2. exactly ONE import line listing ONLY the used host names in canonical order:
   `\timport\tpli_console_put_i64, pli_console_get_i64, pli_console_put_text, pli_console_put_nl, exit`
   (`exit` is always among them when any console call exists — the shared tail uses it);
3. string items `s<k>:\tstring\t"<escaped>"` (m1b), numbered by FIRST USE of each DISTINCT
   literal text, escaping exactly `"` → `\"` and `\` → `\\` (measured decode); placed after
   the import line, before the func item;
4. the func locals gain, after the existing ascending `v<sid>` registers and BEFORE the
   ascending `t<k>` temps: `st` (status register, once, when any console call exists) and
   `a1` (the single get slot, once, when any `Get` exists);
5. statement shapes (tab-indented like every other instruction):
   - `put value`: lower the expression per §P1-m0.3 (interval proof incl. — its own declared
     window), then `call p_put, pli_console_put_i64, st, <reg>`, `bne Lfail, st, 0`,
     `call p_nl, pli_console_put_nl, st`, `bne Lfail, st, 0` (the backend closes EVERY put
     statement with a newline — line-oriented statements; the runtime itself never adds one);
   - `put literal`: `mov <t>, <len>` (the text's character count — never the word "size"),
     `call p_text, pli_console_put_text, st, s<k>, <t>`, `bne Lfail, st, 0`, then `p_nl` as
     above;
   - `get`: `alloca a1, 8`, `call p_get, pli_console_get_i64, st, a1, <lo>, <hi>` where
     (lo,hi) = `W(p)` of the target's declared precision, `bne Lfail, st, 0`,
     `mov v<sid>, i64:(a1)`; the environment then maps `sid` to EXACTLY (lo,hi) (WINDOW LAW);
   - EVERY console call is followed by its own `bne Lfail, st, 0`;
6. the SHARED failure tail AFTER the body's final `ret` and before `endfunc`:
   `Lfail:` (own line, no indent) then `\tcall p_exit, exit, st` and `\tret st`.

An `assign` to, `put` of, or `return` of an uninitialized-after-nothing variable keeps the
EXISTING `HIR-E19` wording; the `Get` arm refuses the mirrored defensive wording "assignment
to sym(N) which was never declared" pattern if no `Declare` preceded it. Multiple `Get`
statements each emit their own `alloca a1, 8` (same instruction, measured pattern repeated;
only single-get modules are pinned).

### P1-m1.6 mir2o additive change + committed console runtime + driver (tools/)

- `tools/mir_aot/mir2o.c` gains EXACTLY the hop-2 probe block VERBATIM-IN-SPIRIT: the
  `pli_ext_dummy` function plus the import-registration double loop BEFORE `MIR_link`
  (context lines `mod`/`it` already exist in the pinned file; the loop variables reuse the
  ones already in scope). `build_native.sh` UNCHANGED (it compiles this file with
  `-Werror` — the block compiles clean in the probe). `thirdparty/` lab pinned
  `ccc92c5c`/`f541a7a5` NEVER touched or advanced. **CT2 re-check MANDATORY at first build:**
  the three frozen no-IO objects keep their recorded sha256 values `78656e6c…`,
  `3822f777…`, `02c15b1b…` (measured byte-equal again in P1-mC).
- NEW committed runtime `tools/mir_aot/pli_console.c` (from the MEASURED scratch
  `build/p1m1-scratch/pli_console2.c`): the five extern "C" entry points
  `pli_console_put_i64`, `pli_console_get_i64`, `pli_console_put_text`, `pli_console_put_nl`
  (each returning the `long` status) and the status constants OK=0 EOF=1 BAD=2 RANGE=3
  IOERR=4; put functions emit NO newline; get per the §P1-m1.1-7 parsing laws; document the
  ABI in the file header. This runtime is DRPLi's OWN minimal console layer — PL/I I/O
  semantics stay DISTINCT from libc (no stdio passthrough beyond getchar/putchar-level use);
  NOT wholesale PLILIB; NOT oracle-judged.
- NEW committed driver `tools/mir_aot/console_check.c` (from the MEASURED scratch
  `console_check_probe.c`): `-DENTRY=<pli80_name>` REQUIRED (`#error` otherwise); calls
  ENTRY once; prints NOTHING on stdout; prints `driver-return=<v>` + newline on stderr;
  returns rc 0 on normal completion (an I/O failure NEVER returns — the MIR tail calls
  `exit(status)`).
- Link recipe = the EXISTING `tools/mir_aot/cosmo_link.sh tiny <out> -- <driver+runtime+object>`
  (tiny mode PROVEN for this shape in hop 2); no APE step, no launcher, no glibc fallback
  (the glibc reference remains available for diagnosis exactly as in §P1-m0).

### P1-m1.7 Fixtures and INDEPENDENT expected results (recorded HERE, BEFORE any run; measured-first pins NEVER hand-written)

NEW fixtures continue the series in `hir/mir-fixtures/` (CRLF on every line + `^Z`,
one dcl item/statement, program names as listed; run under `timeout 60` as
`pli80mir.exe --export <name> [-o f.mir] <fixture>`):

- `M04.pli` **io1** (m1a, put path): `io1: procedure returns(fixed bin(15)); dcl x fixed
  bin(15); x = 6 * 7; put list(x); return (x); end io1;`
- `M05.pli` **iorw** (m1a, get+put roundtrip): `iorw: procedure returns(fixed bin(15));
  dcl n fixed bin(15); get list(n); put list(n); return (n); end iorw;`
- `M06.pli` **msg1** (m1b, literal): `msg1: procedure returns(fixed bin(15)); dcl x fixed
  bin(15); x = 6 * 7; put list('DR PL/I-80 hello from Cosmo!!'); put list(x); return (x);
  end msg1;` (the literal is EXACTLY 29 characters — hand-checked).

INDEPENDENT expected behaviour (hand-computed HERE; NEVER re-fit from output):

| fixture | leg | stdin | expected stdout (EXACT bytes) | expected stderr | rc |
|---|---|---|---|---|---|
| M04 io1 | run | (empty) | `42\n` (3 B) | `driver-return=42\n` | 0 |
| M05 iorw | good | `123\n` | `123\n` (4 B) | `driver-return=123\n` | 0 |
| M05 iorw | sign+terminator | `-42x` | `-42\n` (4 B) | `driver-return=-42\n` | 0 |
| M05 iorw | not-a-number | `abc\n` | `` (empty — get fails before any output) | — | 2 (BAD) |
| M05 iorw | eof | `` (empty) | `` | — | 1 (EOF) |
| M05 iorw | outside W(15) | `20000\n` | `` | — | 3 (RANGE; 20000 > 16383) |
| M06 msg1 | run | (empty) | `DR PL/I-80 hello from Cosmo!!\n42\n` (EXACTLY 33 B) | `driver-return=42\n` | 0 |

Pins (measured-first, `cp` of reviewed output, NEVER hand-written): `hir/mir-expected/M04.mir`,
`M05.mir`, `M06.mir` (reviewed line-by-line against §P1-m1.5 BEFORE pinning; stdout bytes,
`-o` file byte-equal). Negatives `hir/mir-fixtures/N8..N21.pli` with `N*.stderr.txt` + `N*.rc`
pins (zero stdout, no `-o` file, deterministic ×2 — the §P1-m0 refusal-totality law):

| id | statement (one per fixture, CRLF+^Z) | expected refusal (measured-first; wording may deviate — the CODE and NAMED arm may not) |
|---|---|---|
| N8 | `put skip;` | `HIR-E21` ctl arm, names SKIP |
| N9 | `put page;` | `HIR-E21` ctl arm, names PAGE |
| N10 | `put file(f) list(x);` (f undcl) | `HIR-E21` options arm, names FILE (checked BEFORE name resolution — fact 1) |
| N11 | `put edit(x)(b(15));` | `HIR-E21` kind arm, names EDIT |
| N12 | `put item(i);` (i declared bin(15), assigned) | `HIR-E21` kind arm, names ITEM |
| N13 | `put list(x, y);` | `HIR-E21` item-count arm (names the count 2) |
| N14 | `get list(x + 1);` | `HIR-E21` target-shape arm |
| N15 | `get list(a(1));` (a an array row) | `HIR-E21` target-shape arm |
| N16 | `get list('z');` | `HIR-E21` target-shape arm (literal) |
| N17 | `put list('');` | `HIR-E22` empty-literal arm — PARSE UNPROVEN (lexer quote folding); if the parser dies instead, record the deviation and keep the arm defensive-UNEXERCISED |
| N18 | `put list('a<TAB>b');` | `HIR-E22` charset arm (names the position and the offending code point WITHOUT hex — F8) |
| N19 | `dcl x fixed bin(16); ... put list(x);` | EXISTING `HIR-E01` bind channel, wording byte-identical to the probe (no-bypass pin) |
| N20 | `dcl c character(3); ... put list(x);` | EXISTING `HIR-E02` declaration channel (no-bypass pin) |
| N21 | `on error put list(x);` | EXISTING `HIR-E05` catch-all "ON unit" (no-bypass pin) |

Additional no-bypass pins MAY be added while measuring (e.g. `put list(40000)` → `HIR-E08`,
`put list(y)` uninitialized → `HIR-E19`) — additive only, each justified by the no-bypass law.
Every negative is REFUSAL AT LOWERING: the MIR emitter is never reached, rc 2, zero stdout.

### P1-m1.8 Test runner panel — NEW `tools/mir_aot_console_test.py` (every command DIRECT rc, separate processes, NEVER batched)

- **V0** prerequisites: `pli80mir.exe`/`pli80hir.exe` built; `build/p1m0-deps/mir2o` (re)built
  from the COMMITTED `mir2o.c` via `build_native.sh`; cosmo toolchain pinned (K0 law).
- **V1 CT2 no-IO integrity:** re-emit M01/M02/M03 → `.mir` byte-equal to pins; re-emit `.o`
  with the NEW mir2o → sha256 EQUAL to the frozen values of §P1-m1.6 (the additive change is
  byte-invisible to no-IO modules); determinism ×2 fresh processes.
- **V2 pin panel (new fixtures):** M04/M05/M06 `.mir` == pins ×2 fresh; N8..N21 pinned rc +
  pinned stderr bytes, ZERO stdout, NO `-o` file; pipeline proof: each positive fixture
  through `pli80hir.exe` rc 0 (the HIR path itself green, no bypass; dump reviewed against
  §P1-m1.4 during measurement).
- **V3 link panel:** per positive: mir2o `.o` rc 0; `cosmo_link.sh tiny` with
  `console_check.c -DENTRY=pli80_<name>` + `pli_console.c` + object → static ELF; sanity:
  first bytes `0x7fELF`, `file` static x86-64, `readelf -lW` has NO `PT_INTERP`, `nm` lists
  `T pli80_<name>` and NO remaining undefined `pli_console_*`/`exit` (all resolved by the link).
- **V4 run legs:** the §P1-m1.7 table, EXACT stdout bytes (compare raw bytes, not lines),
  EXACT stderr bytes for success legs, exact rc; EVERY leg in a FRESH process; determinism
  re-run for at least one success and one failure leg.
- **V5 non-vacuity controls (perturbations live ONLY in scratch copies under ignored `build/`;
  committed sources NEVER perturbed; if a control PASSES, this runner FAILS):**
  - **C-a wrong arithmetic:** M04 MIR with the emitted `mul` replaced by `add` → the program
    EXECUTES and prints `13\n` — the expected-`42\n` leg MUST FAIL (proves the bytes are judged).
  - **C-b ignored status:** a scratch copy of `pli_console.c` whose `pli_console_get_i64`
    returns OK on the not-a-number path → the `abc` leg now exits 0 instead of 2 and MUST FAIL.
  - **C-c EOF-as-success:** a scratch copy returning OK with value 0 at EOF → the empty-stdin
    leg now prints `0\n` rc 0 instead of rc 1 and MUST FAIL.
- Evidence → ignored `build/mir-console/`. The runner NEVER regenerates pins.

### P1-m1.9 Falsifiers (each a STOP-and-attribute gate; FROZEN regression panel)

- **T1** kept exe `172595d5…` verified DIRECT before and after EVERY build step.
- **T2** `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc 0 at
  every step; ALL committed H dumps byte-frozen (no H fixture contains put/get — fact 1).
- **T3** `timeout 900 python3 tools/hir_test.py` rc 0: **220 ok**, ALL 11 frozen semtest
  numbers UNMOVED (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2 H16 12/5
  H17 12/5 H18 7/3 H21 5/2); F8 strip-greps green over the NEW/EDITED `ocaml/hir/*.ml`.
- **T4** FULL gate rc 0 FROZEN ALL HIT: byte panel **1328/1328**, negatives **190/190**,
  divergence **9/9**, coverage **149 rows 0/0**, census **16/0/25/0**, prose **5** →
  `build/gate-e54p1m1-reg.log`.
- **T5** `timeout 900 python3 tools/mir_aot_test.py` rc 0 — **27 checks** (the §P1-m0 pins
  M01–M03 and N1–N7 unmoved by the additive mir2o).
- **T6** `timeout 900 python3 tools/mir_aot_cosmo_test.py` rc 0 — **25 checks**.
- **T7** `tools/mir_aot_console_test.py` rc 0, AND all three V5 controls observed FAILING
  loudly first-hand (non-vacuity never faked).
- **T8** fresh `cd ocaml && timeout 900 dune build --build-dir _build-e54p1m1` rc 0, ZERO
  `Error`, warning history **122**, fresh exe sha == kept `172595d5…` (computed separately).
- **T9** V1 CT2 byte-identity of the three frozen `.o` (the additive mir2o changes no-IO bytes
  NOWHERE).
- **T10** refusals name their construct (every E21/E22 pin names its arm; no silent drop —
  a lowered console statement appears in the MIR exactly once, reviewed line-by-line).
- **T11** ZERO oracle; ledger stays 203 headers ending **C380**; `handoff.config.json` NEVER
  staged; explicit-path commits only; scratch (`build/p1m1-scratch/`, `ocaml/scratch-*`,
  `build/mir-console/`) NEVER committed; thirdparty lab never advanced; no push; `eval
  "$(opam env)"` every shell; rc DIRECT; never batch build with tests; short timeouts
  everywhere (60 per fixture, 900 per suite).

### P1-m1.10 Deviations recorded IN ADVANCE (honest, never fitted away)

1. `put from(x);` is AST-INDISTINGUISHABLE from `put list(x);` in the frozen parser (hop 2
   read) ⇒ it is ACCEPTED as a list put; no E21 kind arm can name it. Recorded here and in
   RESULTS; never a parser change in this slice.
2. Trailing control items die in the PARSER (uncaught `Pli80.Parser.Parse_error` — a
   pre-existing hole recorded in P1-m0 hop 2, identical in `pli80hir.exe`); no HIR pin is
   possible, so the subset boundary there is a parser message, not `HIR-E21`.
3. The madc-fork object emitter cannot express WEAK imports from MIR text; this slice lands
   a justified ADDITIVE change in OUR `mir2o.c` instead (§P1-m1.6) — the lab stays untouched,
   the no-IO bytes stay byte-frozen (T9).
4. Character VARIABLES stay blocked by the EXISTENT `HIR-E02` declaration channel; m1b is
   literal-only BY CONSTRUCTION of the current subset (fact: N4 already pins the declaration
   refusal). No new refusal is invented for something already impossible.
5. New diagnostic WORDING (exact bytes of E21/E22 messages) is pinned MEASURED-FIRST; the
   tables above pre-register the CODE + NAMED ARM, not the letters; any wording deviation
   gets recorded, never hidden.
6. The H dump representation of `Put`/`Get` (§P1-m1.4) is reviewed in scratch but NOT pinned
   under `hir/expected` in this slice — the fixture panel authorized for P1-m1 is the MIR
   one; extending the H panel is a future slice decision.

### P1-m1.11 Work order (successor contract — exact order)

1. Commit THIS pre-registration (explicit path `spec/lab-evidence/e2e54/PLAN.md`) BEFORE any
   repository source byte. — **DONE** (this commit).
2. **m1a HIR half:** append `HIR-E21`/`HIR-E22` to `ocaml/hir/diagnostic.ml`; extend
   `ocaml/hir/hir.ml` (`put_source`, `Put`, `Get`, dump arms per §P1-m1.4); extend
   `ocaml/hir/hir_build.ml` `lower_stmt` with the `Ast.Sput`/`Ast.Sget` arms implementing
   §P1-m1.2/.3 IN THE PRE-REGISTERED ORDER (m1a: literal data items refuse via the
   item-class arm); MINIMAL `semtest.ml` compile-adapt preserving every walk count.
   `dune build` rc 0 → T1 → `timeout 900 python3 tools/hir_test.py` rc 0 (220 ok, 11 numbers
   UNMOVED) → commit explicit `ocaml/hir/` paths.
3. **m1a MIR half:** extend `mir_backend.ml` per §P1-m1.5 (console statements lower; every
   no-IO procedure keeps the byte-identical path); land the §P1-m1.6 additive block in
   `tools/mir_aot/mir2o.c`; rebuild via `sh tools/mir_aot/build_native.sh`; V1/CT2 byte-check
   FIRST-HAND; commit m1a fixtures/pins MEASURED-FIRST: `M04.pli`, `M05.pli` and negatives
   N8..N16, N19..N21 (N17/N18 land with m1b), reviewing every MIR line against §P1-m1.5
   before pinning; T1/T2/T3 green; commit.
4. **m1b:** accept the validated literal item (charset/empty arms) in `hir_build.ml`; add the
   `p_text`/`s<k>` emission in `mir_backend.ml`; `tools/mir_aot/{pli_console.c,console_check.c}`
   committed from the MEASURED probe sources (header documents the ABI); build → T1 → T3 →
   pin `M06.pli` + M06.mir + N17/N18 measured-first → commit explicit paths.
5. **runner:** write `tools/mir_aot_console_test.py` per §P1-m1.8 with the expected bytes
   copied from §P1-m1.7 (NEVER from a run); run → rc 0; observe C-a/C-b/C-c FAILING loudly;
   commit.
6. FULL regression T4/T5/T6/T8 (gate → `build/gate-e54p1m1-reg.log`; fresh build-dir hist
   122, sha == kept) — each as its own command, rc DIRECT.
7. CLOSE: RESULTS §P1-m1 (milestones m1a/m1b SEPARATELY; T-panel WITH measured values; the
   §P1-m1.10 deviations + any measured deviation; unsupported-semantics matrix; reproduction
   set), `docs/architecture/backend-boundary.md` §7-7, dashboard row CLOSED, durables
   (LEARNINGS hop line, PROGRESS live heading → closure, HANDOFF recovery heading) + guard
   attest → **STOP**.

### P1-m1.12 Dashboard update

| slice | status | notes |
|---|---|---|
| P1-m1 | **CLOSED 2026-11-10** (steps 2–7 landed; runner rc 0 43 checks; FULL FROZEN regression ALL HIT) | minimal console I/O over the native MIR path: m1a integers AND m1b literal characters DELIVERED SEPARATELY; ZERO oracle; ledger 203/C380; deviations incl. `cu_nl = cu_put || cu_text`, N17 parse PROVEN, runner first-run defect fixed honestly; RESULTS §P1-m1; next stages PROPOSED ONLY |

## §P1-mD — Pre-registration: native DWARF source debugging of AOT MIR objects (committed BEFORE any repository source byte)

Operator authorization of 2026-11-10: **native source-level debugging of the AOT MIR path is
AUTHORIZED** (brief: D1 file/line + breakpoints + stepping + backtrace, D2 variable inspection,
SEPARATE milestones). Type of work: **backend engineering, ZERO oracle calls** (none planned or
authorized; debugger behaviour is DRPLi engineering evidence, never a DR claim — the ledger stays
203 headers ending **C380**). Starting reference `1e14ada6` (§P1-m1 close; verified first-hand at
P1-mD hop 1); this pre-registration lands at HEAD `d48564b6` with **zero repo code bytes** since
the starting reference. Baseline re-verified first-hand each hop: `dune build` rc 0; kept exe
`172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` DIRECT; `ocaml/lib` +
`ocaml/bin` byte-clean; ledger 203/C380.

All design authority is MEASURED in three probe hops against the PINNED lab (`ccc92c5c` /
`f541a7a5`, never advanced, never edited) and the pinned Cosmopolitan toolchain
(`build/p1mc-deps`, never edited) in the IGNORED scratch `build/p1mD-scratch/` (NEVER committed):
`LEARNINGS.md` §§ "E2E-54/P1-mD hop 1/2/3" — READ hop 2 + hop 3 FIRST. Every expectation below
either cites a first-hand measurement or is explicitly marked MEASURED-FIRST at pin time.

### P1-mD.0 Milestones (SEPARATE deliverables)

- **D1 — file/line truth.** `break <file>.pli:<line>`, `run`, `stepi`, `info line`, `info source`,
  and **`bt`** on the pinned cosmo link, PROVEN end-to-end in scratch hop 3 on M05: `.debug_frame`
  (named, survives `ape.lds` of EVERY mode) carries the MIR FDEs and gdb 18.1 unwinds
  `#0 pli80_iorw at M05.pli:4` → `#1 main`. GREEN means: the runner panel (§P1-mD.6) rc 0 with
  every leg on the link/mode proven in scratch (§P1-mD.1 fact 9) and the full FROZEN regression
  (§P1-mD.8) all hit.
- **D2 — variable inspection.** `print <source-name>` at a breakpoint reads the homed slot.
  PROVEN in scratch for the M05 scalar (`print n` → `$1 = 77` on glibc, tiny and optlinux links).
  Scope of THIS slice: **scalar non-param variables homed via `MIR_set_reg_debug_home`**; params,
  deref/aggregate homes and arrays stay OUT (the API supports them — `add_var(deref_p,
  member_offset)` — but nothing is claimed unmeasured; a follow-up slice may extend). D2 lands
  only after D1 is green; D1 is independently deliverable.

CLOSE after both milestones (or D1 green + D2 closed-with-measured-scope): RESULTS §P1-mD +
`docs/architecture/backend-boundary.md` + dashboard + durables, then **STOP**. Everything else
(production-backend adoption, `put edit` debugging, multi-CU, APE) remains PROPOSED ONLY.

### P1-mD.1 MEASURED design facts (hops 1–3, first-hand; this section pre-registers, it does not re-measure)

1. **Stamping is PUBLIC and pre-gen (accepted):** `insn->file_id` / `insn->line` (mir.h) are set on
   the parsed `func->insns` BEFORE generation; `gen_record_line` (mir-gen.c:439) skips ONLY when
   line==0 AND file_id==0 ⇒ **line-0 insns MUST carry file_id 0**. `label` insns ARE members of
   `func->insns` (M05 `pli80_iorw` = **14** insns: hop-2 FALSIFIED the hop-1 guess otherwise); the
   line list MUST cover EVERY entry in dlist order.
2. **line_map coalescing (accepted):** stamping 14 insns (lines 3×4, 4×5, 5×2, 0×3) yields exactly
   3 `line_map` rows `22→3, 97→4, 139→5` in `.text` of offset 192, size 182; `code_len`/`line_map`/
   `cfi` are filled on the object-mode path although `machine_code` stays NULL — hence
   `MIR_object_find_symbol` for the `.text` section offset (AOT law).
3. **Debug codegen config (accepted):** level 0 + `MIR_set_inline_permission(0)` +
   `MIR_set_spill_all(1)` + `MIR_func_debug_homes_only(func)` + `MIR_set_reg_debug_home(reg, func)`
   per homed var; reg number = index in `func->vars` **+ 1**; `MIR_reg_frame_offset` → **−8**;
   `MIR_debug_add_var(name, 0, type, −8, 0, 0)`; DWARF shows `DW_OP_fbreg −8`, `frame_base
   DW_OP_reg6`. The gen DEFAULT level is 2 (mir-gen.c:11438) — the debug switches MUST NEVER touch
   the default path.
4. **`.eh_frame` capture is unconditional (accepted, hop 3):** on x86-64 object mode
   `gen_eh_capture` (mir-gen.c:11006, `#if GEN_EH_OBJECT_P`) appends CIE+FDE per non-`jret_p`
   function whenever `func->cfi != NULL && code_len != 0`; **no public runtime switch exists** to
   suppress it, and `struct MIR_object` internals (incl. `ehframe.len`) are opaque.
5. **The pinned fallback law (accepted):** mir-debug.c:1561/2320 — the debug builder emits
   `.debug_frame` (from the `MIR_debug_add_func` cfi, i.e. the very same `func->cfi` bytes)
   **exactly when the object's `.eh_frame` is EMPTY**; `MIR_debug_add_func`'s own header comment
   documents this design ("written to .debug_frame unless the artifact has .eh_frame").
6. **Cosmo link layout is the ONLY cosmo blocker (accepted, D-a + D-b discriminated):** the pinned
   `ape.lds` (tiny 149 / optlinux 147 / dbg 149) folds `KEEP(*(.eh_frame))` INTO the `.data`
   output section ⇒ no named `.eh_frame`, no `PT_GNU_EH_FRAME` ⇒ gdb cannot discover the MIR FDE
   (the frame layout itself is standard; a plain-C `-g` control backtraces via fp-scan heuristics).
   The SAME `M05_dbg.o` through the SYSTEM gcc link keeps a real `.eh_frame` + `PT_GNU_EH_FRAME`
   and gdb `bt` is GREEN ⇒ **MIR CFI is VALID**; the blocker is purely the pinned lds. NO lds or
   toolchain change is authorized. Conversely `.debug_frame` IS kept as its own named output
   section by ape.lds of EVERY mode (tiny/dbg line 202, optlinux 199) and survives the link.
7. **The public read-back route (accepted, hop 3 probe 2, M05 end-to-end):**
   `MIR_gen_object_emit` (capture WITHOUT attached debug builder) → structural ELF section drop of
   `.eh_frame` + `.rela.eh_frame` → `MIR_object_create` + `MIR_object_read` (public merge reader;
   concatenates sections at their alignments, unifies symbols, rebases relocations) →
   `MIR_debug_init`/`add_file`/`base_type`/`find_symbol`/`add_func(line_map, cfi)`/
   `reg_frame_offset`/`add_var` → `MIR_object_set_debug` BEFORE `MIR_object_emit`. Result measured:
   named `.debug_frame` 0x40 + `.rela.debug_frame` (3 relocations — FDE CIE-pointer and PC slots
   against `.text`, exactly AOT-linkable); NO `.eh_frame`; `decodedline` rows identical to the
   direct route; `.text`/`.data`/`.mir.addrpool` BYTE-IDENTICAL and `nm` sets IDENTICAL vs the
   hop-2 direct `.o`.
8. **glibc diagnostic link (accepted, hop 3):** `gcc -O2 -DENTRY=pli80_iorw
   tools/mir_aot/pli_console.c tools/mir_aot/console_check.c M05_dbg.o -o …exe` keeps `.eh_frame`
   (section + PT_GNU_EH_FRAME + PT_LOAD mapping); kept as DIAGNOSTIC REFERENCE leg only — the
   deliverable link stays cosmo (RD-COSMO).
9. **GDB evidence (accepted, gdb 18.1, `-batch -nx -ex "set debuginfod enabled off"`):** M05
   direct-route `.o` on glibc link AND on cosmo tiny/optlinux: `break M05.pli:4` resolves
   (relocated; shows the real PL/I source line of the CRLF+`^Z` fixture), `print n` = 77, `stepi`
   +97→+100 stays on line 4, `info line` = `+97..+139` exactly the line_map bounds, `info source`
   producer `mir-debug` DWARF 4. **bt: GREEN glibc link and GREEN on cosmo tiny + optlinux via the
   read-back `.debug_frame` route** (`#0 pli80_iorw` → `#1 main`, saved regs from CFI); the
   hop-2 garbage-bt reproducers stand as evidence.
10. **`-DEXPECTED` deviation (accepted, hop 2):** `console_check.c` ignores `-DEXPECTED` (declares
    no EXPECTED by contract); the runner judges stdout bytes — deviation recorded, never fitted.

### P1-mD.2 Exact CLI (ADDITIVE flags; default behaviour FROZEN)

- `pli80mir [-g] [--debug-map MAP] --export NAME -o OUT.mir IN.pli` — with `-g` the backend ALSO
  writes the sidecar debug map (section P1-mD.3). Default path (no `-g`, no `--debug-map`): the
  `.mir` bytes and all existing pins UNMOVED; with `-g` the `.mir` bytes themselves are ALSO
  byte-identical (the sidecar is a separate file; the map path defaults to `OUT.mir` + `.p1md`
  when `-g` is given without `--debug-map`; `--debug-map` without `-g` is a usage error rc 2).
- `mir2o -f IN.mir OUT.o [--debug-map MAP]` — without the flag: byte-identical behaviour (all
  §P1-m0/§P1-m1/§P1-mC pins UNMOVED; the debug code MUST call NOTHING on this path). With the
  flag: §P1-mD.4. Exit-code convention continues mir2o's existing table (usage 2, input 3, …)
  with NEW codes measured-first for map read (7), map validation (8), ELF drop (9), read-back
  (10); every refusal prints its named reason.

### P1-mD.3 Sidecar debug-map format and validation law

Text file, line-oriented; any deviation is a LOUD refusal, never a silent drop:

    p1md 1
    mir <64-hex sha256 of the EXACT OUT.mir bytes>
    file <absolute path of the .pli source>
    func <func-item index in module order> <MIR function name>
    insn <func-name> <i> <MIR_insn_name opcode> <line>     (one PER func->insns entry, i from 0,
                                                            dlist order, LABELS INCLUDED;
                                                            unlocated tail rows carry line 0)
    var <mir-local-name> <source-name>                      (MIR v<sid> sanitized name → sorig)

mir2o validates BEFORE annotating anything (all-or-nothing): magic + version; sha256 of the input
`.mir` bytes (self-contained embedded C implementation — no external dependency); every `func`
name resolves; `insn` count per func EQUALS the parsed `func->insns` length; every opcode name
matches `MIR_insn_name` at its index; no duplicate `insn`/`var` records; every `var` MIR name
exists in `func->vars`; the `file` path is absolute. Refusal rc ≠ 0 names the exact mismatch
(count, index, expected-vs-got opcode, duplicate key, bad sha). On the backend side mir_backend
emits one `insn` record per instruction it WRITES (it knows labels it emits) with the HIR line
already carried by the existing `ex_line`/`st_line` fields — NO second line resolver, NO dump
parsing, NO regex (hop-1 audit law); unlocated trailing instructions get line 0.

### P1-mD.4 mir2o debug-mode sequence (the PROVEN probe-2 route, in order)

1. Load `.mir` into the context (as today); parse + fully validate the sidecar (§P1-mD.3).
2. Stamp `insn->file_id`/`insn->line` (line 0 ⇒ file_id 0) on every listed func.
3. Enable the debug codegen config (§P1-mD.1 fact 3) for each debug func: level 0,
   inline-permission 0, spill_all, `homes_only` + one `debug_home` per sidecar `var` record
   (multiple homes per func: MEASURED-FIRST at implementation; M05 pins the single-home case).
4. Imports/link/gen exactly as the default path (same `MIR_load_external` dummy route).
5. `MIR_gen_object_emit` → plain capture in memory; **in-C structural ELF drop** of `.eh_frame`
   and `.rela.eh_frame` (re-index `sh_link`/`sh_info`/`st_shndx`, drop the section symbol, rewrite
   `e_shstrndx`-relative tables as needed — pure ELF bookkeeping, ZERO DWARF semantics, NO
   subprocess, NO temp file). A malformed result is caught LOUDLY by step 6's reader return.
6. `MIR_object_create` + `MIR_object_read` (rc −1 ⇒ refuse with the reader's `err_msg`).
7. Fresh `MIR_debug` builder: `add_file` (id law §P1-mD.1), `base_type` carrier label
   `"fixed bin(15)"` SIGNED size 8 (truthful 8-byte carrier; final label wording MEASURED-FIRST
   and pinned from output, per §P1-m1.10.5 law), then per func `find_symbol` → `add_func`
   (`func->line_map`, `func->cfi`) and per var `reg_frame_offset` (failure ⇒ refusal, never a
   silent un-homed var) + `add_var`; `MIR_object_set_debug` BEFORE `MIR_object_emit`; write
   `OUT.o`.

### P1-mD.5 Fixtures and pins (MEASURED-FIRST; ADDITIVE only)

- D1/D2 fixture: **M05** (`hir/mir-fixtures/M05.pli`, CRLF+`^Z` bytes; the MIR pin `M05.mir`
  stays BYTE-IDENTICAL — the sidecar is a NEW expected file, e.g. `hir/mir-debug-expected/M05.p1md`
  (new ADDITIVE directory; hir pins FROZEN, mir pins ADDITIVE law respected).
- Pins written only from measured CLI output; the debug `.o` is pinned by sha256 recorded in the
  runner table (byte-pinned sidecar + sha-pinned `.o` + gdb evidence files, never the other way
  round; NEVER fit tests to output).
- Negative panel: sidecar tamper refusals (sha/count/opcode/dup) pinned as rc ≠ 0 + message arms.

### P1-mD.6 Runner panel — NEW `tools/mir_aot_debug_test.py`

Per fixture, every command DIRECT rc, separate processes, NEVER batched with builds:
(1) `pli80mir -g --debug-map MAP --export … -o OUT.mir IN.pli`; (2) `mir2o -f OUT.mir
OUT.o --debug-map MAP`; (3) readelf panel laws on OUT.o: named `.debug_frame` PRESENT, `.eh_frame`
ABSENT, `.rela.debug_frame` present, `decodedline` rows == pin, `frames-interp` decodes CIE+FDE,
`nm T pli80_*`; (4) cosmo **optlinux** link (primary; tiny as secondary leg) via
`tools/mir_aot/cosmo_link.sh`, `chmod +x` law; (5) EXEC: stdin pin → stdout bytes EXACT;
(6) gdb batch legs: `break M05.pli:4`, `run`, `print n`, `stepi`, `info line`, `info source`,
`bt` (assert `#0 pli80_iorw … M05.pli:4` and `#1 … main`), `continue` (exit 0) — evidence captured
to `build/mir-debug/`; (7) controls, each OBSERVED FAILING LOUDLY FIRST (non-vacuity never faked):
**D-C1** no-debug link ⇒ `break M05.pli:4` does NOT resolve; **D-C2** sidecar sha tampered ⇒
`mir2o` refuses rc ≠ 0; **D-C3** insn-count/opcode tampered ⇒ refuses rc ≠ 0. Plus the glibc
diagnostic-reference leg (§P1-mD.1 fact 8) recorded as evidence, not as a delivery gate.

### P1-mD.7 Environment laws (all measured first-hand)

gdb 18.1; batch mode `-batch -nx` with `set debuginfod enabled off`; `ptrace_scope` 1 works;
cosmo artifacts are `rw-r--r--` after link ⇒ **`chmod +x` REQUIRED**; link stderr carries known
benign wine/fixme noise (judge stdout/rc only); `LC_ALL=C` for parsed tool output; timeouts: 60
per fixture leg, 120 per cosmo link, ≤120 per gdb batch, 900 per suite; `eval "$(opam env)"` in
every shell; rc checked DIRECT; never batch `dune build` with tests; no push; explicit-path
commits; scratch never committed; config never staged; lab pins never advanced.

### P1-mD.8 Falsifiers (each a STOP-and-attribute gate; FROZEN regression panel)

- **T1** kept exe `172595d5…` verified DIRECT before/after every build step.
- **T2** `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc 0 at every
  step (hir pins FROZEN; `ocaml/lib`/`ocaml/bin` untouched); ALL existing `hir/mir-expected/*.mir`
  byte-UNMOVED with and without `-g`.
- **T3** `timeout 900 python3 tools/hir_test.py` rc 0: **220 ok**, 11 frozen semtest numbers
  UNMOVED; F8 strip-greps green over new/edited `ocaml/hir/*.ml`.
- **T4** FULL gate rc 0 FROZEN ALL HIT: byte panel **1328/1328**, negatives **190/190**,
  divergence **9/9**, coverage **149 rows 0/0**, census **16/0/25/0**, prose **5** →
  `build/e54pmD-reg-gate.log`.
- **T5** `timeout 900 python3 tools/mir_aot_test.py` rc 0 — **27 checks** (default mir2o bytes
  unmoved). **T6** `timeout 900 python3 tools/mir_aot_cosmo_test.py` rc 0 — **25 checks**.
- **T7** `tools/mir_aot_debug_test.py` rc 0 with ALL controls D-C1/D-C2/D-C3 observed failing
  loudly first-hand.
- **T8** fresh `cd ocaml && timeout 900 dune build --build-dir _build-e54pmD` rc 0, ZERO
  `Error`, warning history **122**, fresh exe sha == kept `172595d5…` (computed separately).
- **T9** the no-`--debug-map` `mir2o` output stays byte-identical to the frozen `.o` panel on
  every existing fixture (CT2-style cmp legs, never replaced by sha).
- **T10** sidecar refusal panel: each malformed-map arm pinned MEASURED-FIRST (rc + first line).
- **T11** ZERO oracle; ledger stays 203/C380; `handoff.config.json` NEVER staged; explicit-path
  commits only; `build/p1mD-scratch/` and `build/mir-debug/` NEVER committed; lab (
  `thirdparty/mir-madc-aot-lab`) and `build/p1mc-deps`/`build/p1m0-deps` NEVER edited or advanced;
  no push.

### P1-mD.9 Complexity-stop thresholds and FORBIDDEN routes

STOP and attribute (exact reproducer + interface diagnosis) if: the ELF drop/read-back round trip
refuses a valid image; `MIR_object_read`+`set_debug` mislocates any symbol/reloc (panel mismatch);
multiple `debug_home`s per func misbehave (then land the single-home subset, record the boundary
honestly); or any gdb leg fails on the PROVEN link/mode. FORBIDDEN, ever: a new DWARF generator;
editing `ape.lds`, the pinned toolchain or the lab; a repo-owned replacement linker script;
fitting gdb assertions to garbage output; reusing `-g` on the DEFAULT gen path. D2 may close
DEFERRED with its measured blocker while D1 stands.

### P1-mD.10 Work order (successor contract — exact order)

1. `ocaml/hir/mir_backend.ml` ADDITIVE: sidecar emission (lines from existing `ex_line`/`st_line`,
   sorig from `sid` law; `-g` opt-in; default path calls NOTHING) → build → byte-identity T-panel.
2. `pli80mir` CLI flags; measured-first sidecar pin under the new ADDITIVE expected dir.
3. `tools/mir_aot/mir2o.c` debug mode (§P1-mD.4; validate-then-annotate; embedded sha256; in-C ELF
   drop; NO new subprocess/dependency) + refusal arms.
4. Fixtures/pins measured-first; runner `tools/mir_aot_debug_test.py` + gdb evidence + controls
   D-C1/D-C2/D-C3 observed failing loudly first; then the FULL FROZEN regression T1–T11.
5. CLOSE: RESULTS §P1-mD (milestones D1/D2 SEPARATELY; deviations + unsupported-scope matrix),
   `docs/architecture/backend-boundary.md`, dashboard row, durables + guard attest → **STOP**.

### P1-mD.11 Dashboard update

| slice | status | notes |
|---|---|---|
| P1-mD | **CLOSED 2026-11-11 (hop 7; D1 and D2 SEPARATELY BOTH GREEN)** | native DWARF debugging of AOT MIR objects landed: `-g` sidecar map (byte-frozen default path), `mir2o --debug-map` validate-then-annotate, in-C `.eh_frame` drop + `.debug_frame` read-back route; gdb battery GREEN incl. `bt` on cosmo optlinux and `print n = $1 = 77`; runner `tools/mir_aot_debug_test.py` rc 0 23 checks, D-C1/D-C2/D-C3 failing loudly; FULL FROZEN regression T1–T11 ALL HIT; ZERO oracle; commits `a22dc0a5`→`b400b3b9`→`b0966931`→`b14756e9`→`2e8fdc9e`→close |

## §P1-m2 — Pre-registration: native control flow (IF/ELSE and bounded DO WHILE) (committed BEFORE any repository source byte)

Operator authorization of 2026-11-12: **E2E-54/P1-m2 AUTHORIZED** — a bounded extension of the
native MIR backend to PL/I `IF/ELSE` (m2a) and `DO WHILE` (m2b), executed through the existing
HIR → MIR AOT → Cosmopolitan static-ELF pipeline, preserving sound numeric analysis and the
P1-mD DWARF sidecar. The full brief is preserved VERBATIM at the IGNORED `build/p1m2-brief-true.md`
(same law as P1-m0/P1-mD). Type of work: **backend engineering, ZERO oracle calls** (none planned
or authorized; nothing here is or becomes a DR historical claim — the ledger stays 203 headers
ending **C380**). Starting reference `2609d0ea` (§P1-mD close; verified first-hand at P1-m2 hop 1,
baseline ALL GREEN); this pre-registration lands BEFORE any source byte, hop-1 recon committed at
`5abe9c82` with ZERO repo source byte.

All design authority is MEASURED in hop 1 against the PINNED lab (`ccc92c5c`/`f541a7a5`, never
advanced, never edited), the pinned Cosmopolitan toolchain (`build/p1mc-deps`, never edited) and
the LIVE parser/hir_build/mir_backend, in the IGNORED scratch `build/p1m2-scratch/` (NEVER
committed): `LEARNINGS.md` § "E2E-54/P1-m2 hop 1" — READ IT VERBATIM FIRST. Every expectation below
either cites a first-hand measurement or is explicitly marked MEASURED-FIRST at pin time. No
expected byte in this section was produced by running the compiler on a fixture pinned below —
the expectations are hand-derived here, BEFORE any run.

### P1-m2.0 Milestones (SEPARATE deliverables)

- **m2a — conditional branches and control-flow joins.** `Hir.If` (with and without ELSE, nested,
  all six relational operators `Eq/Ne/Lt/Le/Gt/Ge`) lowers to native MIR branches; the value-
  interval environment gains a SOUND join (drop-not-inherit + interval hull, §P1-m2.2). GREEN
  means: the `choose` fixture (brief §4) EXECUTES both arms in fresh cosmo-tiny processes with the
  §P1-m2.5 byte expectations; the m2a gate (§P1-m2.11) passes; the corruption control C-M2a
  (§P1-m2.7) fails natively as designed.
- **m2b — bounded `DO WHILE` loops and loop-state invariants.** `Hir.While` lowers to the PROVEN
  header/backedge shape (§P1-m2.3, `probe_loop.mir`/`probe_loop_ind.mir` executed values 3) with
  the RESTRICTED counted-loop proof — initialized induction variable, constant nonzero monotonic
  step, relational guard, every iteration value AND the exact exit value inside the declared
  window; anything else refuses EXPLICITLY, never silently. GREEN means: `count` EXECUTES three
  genuine body iterations natively (stdout `0\n1\n2\n`, return `3`), zero/one-iteration and
  descending fixtures hold their independently derived values, the loop corruption control
  C-M2b fails natively, and §P1-m2.3's proof is written down such that every accepted loop's value
  set was hand-checked.

**Complete the m2a gate before implementing m2b** (brief §1). CLOSE after both (or m2a GREEN +
m2b closed-DEFERRED with its measured blocker, brief §12): RESULTS §P1-m2 (m2a/m2b SEPARATELY),
`docs/architecture/backend-boundary.md`, dashboard row, durables, then **STOP** — no next phase is
authorized automatically (brief §12).

### P1-m2.1 MEASURED design facts (hop 1, first-hand; this section pre-registers, it does not re-measure)

1. **HIR shapes (accepted, live parser):** the brief's `choose`/`count` sources parse VERBATIM
   (scratch `CHOOSE.pli`/`COUNT.pli`, CRLF+`^Z`, `pli80hir.exe` rc 0). `if c then s; else s;` →
   `Ast.Sif` → `Hir.If {cond; then_; else_}`; `do while(c); … end;` → `Sdowhile` →
   `Hir.While {cond; body}`; both carry `stmt list` arms in SOURCE ORDER. A relational condition is
   `Hir.Bin {op; left; right; typing="language-rule:relational"}` with `ex_ty = Condty` and
   `ex_ef = Pure` for pure operands; `y = -1` lowers to `Neg {e = Const "1"}` (the `Neg` arm exists).
2. **MIR branch/label syntax PROVEN on the pinned parser+emitter with NATIVE execution** (scratch
   `probe_{labels,ind,loop,loop_ind}.mir`, all rc 0, glibc-exec values 1, 7, 3 — LEARNINGS hop 1):
   `blt L, x, y` / `bge L, x, y` take the LABEL FIRST and branch when the signed 64-bit comparison
   is TRUE; the next instruction runs when false (no delay slot); unconditional `jmp L`; labels on
   their OWN line, tab-indented OR unindented — both parse; **label scope is the whole module ⇒ CF
   label names MUST be globally unique in the artifact**. Mnemonics `beq/bne/ble/bgt` are documented
   (MIR.md) but `beq/ble/bgt/ne-inversion` EXECUTION is MEASURED-FIRST at the first fixture that
   needs each (PREDICTION, never pin-authority: the §P1-m2.2 inversion table holds).
3. **Current backend anchors (read first-hand this hop):** the value env is `Int_map.find_opt sid
   env : (int*int) option` — ABSENCE means "not definitely initialized" (the existing straight-line
   law); `window p = ±(2^(p-1)-1)`; `in_window`, `show_iv`, `prove`, the fresh-temp counter `fresh ()`
   (`t<k>`, evaluation order), the string-item counter `s<k>`, `declared`, `v_regs`, and the shared
   unindented `Lfail:` tail. `Hir.If`/`Hir.While` are refused TODAY at mir_backend.ml:441/446
   (HIR-E18) — those refusals, and only those, are replaced (§2 of the brief). Console legs:
   `cu_put/cu_get/cu_text` are a TOP-LEVEL fold over `body` — nested uses are INVISIBLE to it, so
   the fold must become a recursive walk (deviation law §P1-m2.8 item 0: straight-line bytes stay
   byte-identical because the walk visits the same statements in the same order).
4. **Fixture/pin law (accepted):** new PL/I fixtures are CRLF+`^Z` in the NEW ADDITIVE directories
   `hir/mir-cf-fixtures/` (inputs) and `hir/mir-cf-expected/` (pins), generated with the hop-1
   scratch tool `build/p1m2-scratch/mkpli.py`; pins are `cp` of measured CLI output ONLY after
   line-by-line review against this section (NEVER hand-written); negatives pin rc + stderr bytes
   with ZERO stdout and NO `-o` file (refusal totality, §P1-m0 law).

### P1-m2.2 m2a contract — IF/ELSE lowering, labels, joins (`ocaml/hir/mir_backend.ml` ONLY)

Emission (every instruction rides the existing `emit ?line` with the IF statement's `st_line`;
the condition operands lower through the EXISTING `lower` at their own `ex_line`):

- `if cond then THEN else ELSE` (cf-n counts IF statements in source order from 1):

      <lower cond operands -> rl, rr>
      b<cc>  Lthen<n>, rl, rr
      jmp    Lelse<n>
      Lthen<n>:
      <THEN in env-copy>
      jmp    Ljoin<n>
      Lelse<n>:
      <ELSE in env-copy>
      Ljoin<n>:

- `if cond then THEN` (no ELSE — the else path is the IDENTITY):

      <lower cond operands -> rl, rr>
      b<inv-cc>  Ljoin<n>, rl, rr
      <THEN in env-copy>
      Ljoin<n>:

  where `inv-cc` inverts the guard so the body is SKIPPED when the condition is false. The
  inversion table (Lt→Ge, Le→Gt, Gt→Le, Ge→Lt, Eq→Ne, Ne→Eq) is PROVEN ONLY for Lt→Ge and Ge→Lt
  (hop-1 probes); the other rows are MEASURED-FIRST at their fixtures — a mismatch is a falsifier,
  never a re-fit.
- `lower_cond env e ltarget` accepts EXACTLY a `Hir.Bin` relational node with `op ∈ {Eq,Ne,Lt,Le,
  Gt,Ge}` whose two operands lower through the existing integer `lower` (each operand keeps its
  OWN declared-type window proof — no new type rule; a `Convert`, an unknown-effect operand, a
  condition literal, or any other shape refuses BY NAME at HIR-E18). The relational node's `Condty`
  is never passed to `bin_p`.
- **Label discipline:** a NEW counter `cf_n` (names `Lthen<n>`/`Lelse<n>`/`Ljoin<n>`,
  `Lh<n>`/`Lx<n>`) INDEPENDENT of `fresh ()`; names are globally unique (fact 1.2); the control
  flow NEVER emits, reuses or shadows `Lfail`; the failure tail stays the single shared unindented
  tail after the body's final `ret`.
- **Join law (the scientific core; brief §3):** each arm lowers in a COPY of the pre-IF env; arms
  never share mutable state. At `Ljoin<n>` the env is merged per sid: `Some a` + `Some b` →
  `(min lo, max hi)` (sound hull); `Some` + `None` → `None` (**DROP — never inherit an assignment
  executed only in the opposite arm**); `None` + `None` → `None`. Untouched variables keep their
  prior state (both sides equal). A missing ELSE is the identity arm in that merge. NO
  branch-condition interval refinement in m2a (permitted but not required; deferred honestly).
  Early/nested `RETURN` inside an arm keeps its existing refusal (the ONE final top-level
  `RETURN(expr)` law is UNCHANGED). Existing-window checks apply INSIDE each arm unchanged — the
  window law is never weakened.
- The final `RETURN(expr)` lowers with the JOINED env, so a variable live only on one path reads as
  uninitialized → HIR-E19 (see the message amendment, §P1-m2.8 item 0).

### P1-m2.3 m2b contract — bounded DO WHILE + counted-loop proof

Loop emission (cf counter shared with m2a; loop k gets `Lh<k>`/`Lx<k>`), the PROVEN hop-1 shape
(`probe_loop.mir` executed 3):

      Lh<k>:
      <lower cond operands -> rl, rr>          (reevaluated EVERY iteration)
      b<inv-cc>  Lx<k>, rl, rr
      <body in env-copy of the header env>
      jmp  Lh<k>
      Lx<k>:

- **Recognized counted-loop form (the whole of m2b's acceptance; everything else refuses BY
  NAME, HIR-E18 unless a numeric window is the primary reason, then HIR-E19):**
  1. the guard is `Var sid OP expr_B` with `OP ∈ {Lt,Le,Gt,Ge}` (Eq/Ne guards cannot prove
     monotonic exit — refuse); `expr_B` lowers to a CONSTANT interval `[blo,bhi]` in the pre-loop
     env (no read of any variable the body writes);
  2. `sid` is definitely initialized immediately before the loop as a CONSTANT interval
     `[iv0,iv0]` (an assignment of a proved constant — including the `Neg` form);
  3. the body contains EXACTLY ONE write to `sid` and it is the monotonic step
     `sid = sid + C` or `sid = sid - C` where `C` is a positive integer literal (`Bin{Add/
     Sub;left=Var sid;right=Const}` with `c = ±C ≠ 0` computed exactly); ANY other statement
     touching `sid` (assign, GET, compound) anywhere in the body tree → refuse;
  4. direction match: `OP ∈ {Lt,Le} ⇒ c > 0`; `OP ∈ {Gt,Ge} ⇒ c < 0` (a mismatched guard is a
     non-terminating form the proof cannot discharge → refuse);
  5. **exact exit value** (integers are exact; `p ≤ 15` so every product fits the 63-bit OCaml
     int): for `c > 0`, `T = bhi` for `Lt` and `bhi + 1` for `Le` (first failing value guard);
     `exit = iv0` if `iv0 ≥ T` (ZERO iterations) else `iv0 + c * ceil((T - iv0) / c)`;
     for `c < 0`, `T = blo` for `Gt` and `blo - 1` for `Ge`; `exit = iv0` if `iv0 ≤ T` else
     `iv0 + c * ceil((iv0 - T) / (-c))`. (For a literal bound `B`: `T = B` (Lt), `B+1` (Le),
     `B` (Gt), `B-1` (Ge).)
  6. **window obligation (the brief's "each update stays inside the declared precision"):** the
     smallest/largest value taken inside the body is `iv0` and the last pre-exit iterate; require
     `min(iv0, exit) ≥ W_lo` and `max(iv0, exit) ≤ W_hi` for `sid`'s declared precision; the guard
     bound interval must also lie within the operand's window via the EXISTING `lower` proofs.
- **Loop-state discipline (brief §5):** the header env for `sid` is the single exit-value interval
  `[exit, exit]`; inside the body `sid` is refined to the values the guard admits
  (`Lt`: `[iv0, T-1]`, `Le`: `[iv0, T]`, `Gt`: `[T+1, iv0]`, `Ge`: `[T, iv0]`) — sound by the
  monotonic direction. EVERY other sid written by ANY body statement (assign or GET, at any
  nesting depth) is DROPPED (`None`) at the header — a body assignment is NEVER treated as
  definitely executed, and multi-iteration accumulation is out of the subset (refusal names it);
  a sid written ONLY inside a loop has `None` after `Lx<k>` (zero-iteration path); variables not
  written by the body keep their pre-loop env. The zero-iteration path is exact: `exit = iv0`.
- Nested `While` inside a body refuses BY NAME (nested loops out of the subset); a nested `If` is
  admitted ONLY through the m2a machinery (its own join) and its arms must not write the `sid`.
- Condition reevaluation is structural (the guard lowers INSIDE `Lh<k>` every time — never peeled);
  the backedge `jmp Lh<k>` is mandatory; the loop body may contain PUT/GET (console legs unchanged;
  `Lfail` still shared and never per-iteration).

### P1-m2.4 Numeric-safety invariants (NEVER weakened; falsifiers if violated)

- I1 the window law: every arithmetic node is proved inside its declared window exactly as today —
  branches and loops add NO bypass; the `prove`/Assign/Return checks are unchanged.
- I2 drop-not-inherit: no expression ever lowers with an env entry that was assigned on only one
  path (join law §P1-m2.2/§P1-m2.3). A `Some` may NEVER override a `None`.
- I3 interval hulls are over ACTUAL arm intervals only — never widened by hand, never clamped to
  the window (which would lie about the bound).
- I4 GET inside a branch/loop records EXACTLY the runtime-proved `[lo,hi]` window (existing law).
- I5 the exit-value formula is exact integer arithmetic (ceil on ints); a zero or negative step, a
  bound interval overlapping the iteration domain, or any guard direction mismatch REFUSES — an
  unprovable loop is never accepted to make a fixture pass.
- I6 existing straight-line bytes: every artifact for a program WITHOUT If/While is byte-identical
  to its `hir/mir-expected/` pin (§P1-m0/m1/mD pins are falsifiers, not references to re-fit).

### P1-m2.5 Fixtures and INDEPENDENT expected results (recorded HERE, BEFORE any run)

Procedure names are case-folded for `--export`. All fixture files CRLF+`^Z` via
`build/p1m2-scratch/mkpli.py`. Positive MIR pins = `cp` of reviewed measured stdout; native legs
per §P1-m2.6.

POSITIVE — m2a (cosmo TINY exec via the console driver; stdout bytes and `driver-return=` are the
independent expectations, hand-computed from PL/I semantics — never from generated code):

| id | proc | program (essence) | stdin | stdout | driver-return | rc |
|---|---|---|---|---|---|---|
| CF01 | `choose` | brief §4 verbatim shape: `get x; if x < 0 then y = -1; else y = 1; put list(y); return (y)` | `-2\n` | `-1\n` | -1 | 0 |
| | | | `0\n` | `1\n` | 1 | 0 |
| | | | `7\n` | `1\n` | 1 | 0 |
| CF02 | `nocls` | `y = 7; get x; if x > 5 then y = 9; put list(y); return (y)` (IF without ELSE; join hull [7,9]) | `10\n` | `9\n` | 9 | 0 |
| | | | `5\n` | `7\n` | 7 | 0 |
| CF03 | `nest` | `get x; if x < 0 then y = -1; else if x = 0 then y = 0; else y = 2; put; return` (nested IF, Eq arm) | `-3\n` | `-1\n` | -1 | 0 |
| | | | `0\n` | `0\n` | 0 | 0 |
| | | | `5\n` | `2\n` | 2 | 0 |
| CF04 | `eqne` | `get x; if x ^= 3 then y = 1; else y = -1; if x >= 2 then y = y + 10; else y = y - 10; put; return` (Ne + Ge; both signed directions) | `3\n` | `9\n` | 9 | 0 |
| | | | `4\n` | `11\n` | 11 | 0 |
| | | | `1\n` | `-9\n` | -9 | 0 |
| CF05 | `iocond` | `get x; if x <= 0 then y = -2; else get list(y); put list(y); return (y)` (console calls INSIDE branches; Le) | `5\n7\n` | `7\n` | 7 | 0 |
| | | | `-1\n` | `-2\n` | -2 | 0 |
| | | | `5\nabc\n` | `` (empty) | — (exit 2 via Lfail) | 2 |
| | | | `abc\n` | `` (empty) | — | 2 |

POSITIVE — m2b (executed legs per §P1-m2.6):

| id | proc | program (essence) | stdout | driver-return / native value | rc |
|---|---|---|---|---|---|
| CF06 | `count` | brief §6 verbatim: `i = 0; do while (i < 3); put list(i); i = i + 1; end; return (i)` — THREE genuine iterations | `0\n1\n2\n` | 3 | 0 |
| CF07 | `zero` | `i = 5; do while (i < 2); i = i + 1; end; return (i)` — ZERO iterations (guard false at entry; exit = iv0) | `` | 5 | 0 |
| CF08 | `oneit` | `i = 2; do while (i <= 2); i = i + 1; end; return (i)` — exactly ONE iteration (Le; exit = 2 + 1*ceil(1/1) = 3) | `` | 3 | 0 |
| CF09 | `loopcond` | `i = 0; j = 9; do while (i < 2); if i = 0 then put list(j); i = i + 1; end; put list(i); return (i)` (IF inside loop; body writes ONLY the IV) | `9\n2\n` | 2 | 0 |
| CF10 | `stepdn` | `i = 6; do while (i > 2); put list(i); i = i - 2; end; return (i)` (descending c = -2; exit = 6 - 2*ceil(4/2) = 2) | `6\n4\n` | 2 | 0 |

CF07/CF08 have NO console leg: native verification is the glibc `native_check` leg (EXPECTED =
the returned value) AND a cosmo-tiny leg (`driver-return=`). CF07 additionally falsifies the
zero-iteration discipline; the CF06 exit value `3` is the brief's own independent expectation.

NEGATIVE (compile-time refusals; each rc 2, ZERO stdout, NO `-o` file, deterministic ×2 fresh
processes; PREDICTED code/first-reason recorded here, MEASURED-FIRST at pin time — a deviation is
recorded, never fitted):

| id | proc | program | PREDICTED refusal |
|---|---|---|---|
| CFN1 | `cfn1` | brief §3 second example: `get x; if x > 0 then y = 1; put list(y); return (y)` (y initialized on ONE path only) | HIR-E19 uninitialized read of y — join DROPPED it (message per the §P1-m2.8-0 amendment) |
| CFN2 | `cfn2` | `dcl y fixed bin(3); get x; if x > 0 then y = 3; else y = 4; put; return` (branch that overflows the declared type) | HIR-E19 Assign-window inside the ELSE arm (`[4,4]` leaving `[-3,3]`) |
| CFN3 | `cfn3` | `do while (i < 3); i = i + 1; end;` with NO init of i (uninitialized IV) | HIR-E19 uninitialized induction variable (named) |
| CFN4 | `cfn4` | `i = 0; do while (i < 3); i = 2; end;` (body write is not the recognized monotonic step) | HIR-E18 body writes the induction variable outside the recognized step form |
| CFN5 | `cfn5` | `i = 0; do while (i < 2); j = 0; do while (j < 2); j = j + 1; end; i = i + 1; end;` (nested loop) | HIR-E18 nested loop outside the proven subset |
| CFN6 | `cfn6` | `dcl i fixed bin(3); i = 0; do while (i < 4); i = i + 1; end; return (i)` (update escapes W(3)=±3) | HIR-E19 Assign-window at the step (`[1,4]` leaving `[-3,3]`) |

### P1-m2.6 Native validation panel methodology (brief §10, per positive)

(1) real PL/I → Parser/Bind/HIR (pipeline proof `pli80hir.exe` rc 0 on the same fixture);
(2) deterministic MIR: `pli80mir --export <p> -o X.mir fixture` TWICE in FRESH processes — stdout,
`-o` file and the reviewed `hir/mir-cf-expected/<id>.mir` pin all byte-equal;
(3) `mir2o -f X.mir X.o` rc 0 (this run IS the pinned-parser acceptance);
(4) cosmo TINY link via `tools/mir_aot/cosmo_link.sh` (timeout 120, `chmod +x` law) + no-`-g`
object; static-ELF laws: no `PT_INTERP`, no dynamic section/`DT_NEEDED`, `nm T pli80_<n>`;
(5) EXEC each stdin leg in a FRESH process (timeout 60): stdout bytes EXACT, rc EXACT,
`driver-return=<v>` on stderr per the console-driver contract;
(6) negatives: the §P1-m2.5 table arms; NO emitter run for negatives.
The existing `pli_console.c`/`console_check.c`/`cosmo_link.sh`/`mir2o.c` are UNTOUCHED (brief §8):
m2a/m2b emit the SAME import/proto/tail structure.

### P1-m2.7 Corruption controls (non-vacuity; DISPOSABLE copies under `build/` only)

- **C-M2a (branch polarity):** take CF01's measured `.mir` copy and flip the conditional branch
  mnemonic (`blt` → `bge` — the two hop-1-PROVEN mnemonics). Re-`mir2o`, re-link, execute stdin
  `-2\n`: the program MUST take the WRONG arm — stdout `1\n` where the independent expectation is
  `-1\n` ⇒ the native test FAILS. A control that merely greps for a branch is insufficient (brief
  §6).
- **C-M2b (backedge removal):** take CF06's measured `.mir` copy and delete the loop's
  `jmp Lh<k>` backedge instruction; re-`mir2o`, re-link, execute: stdout MUST NOT equal `0\n1\n2\n`
  (prediction: exactly ONE iteration, `0\n`) ⇒ the native test FAILS.
- Controls run inside the new CF runner and MUST be observed failing LOUDLY first-hand; a control
  that passes fails the suite. Perturbations touch ONLY ignored `build/mir-cf/` copies, NEVER a
  pin, NEVER the compiler.

### P1-m2.8 Pre-registered amendments to PRE-EXISTING artifacts (the §2-vs-§9 contradiction, resolved honestly BEFORE any code)

The brief simultaneously REQUIRES (§2) "Replace only these refusals [`Hir.If`/`Hir.While` at
HIR-E18] with justified, explicitly tested lowering" and (§9) "No changes to existing HIR or MIR
expected files" + "MIR AOT: 27 checks" green. These are **contradictory as literally stated**:
`hir/mir-expected/N2.*` pins the exact E18 if-refusal and `N7.*` the exact E18 while-refusal, so
implementing §2 necessarily invalidates those pins. Resolution (operator brief authorizes the
replacement; the deviation is recorded here IN ADVANCE, never silently):

- **item 0 (message truthfulness):** the uninitialized-read refusal (mir_backend `Hir.Var` arm)
  says "on the only path of this straight-line body" — FALSE once joins exist. AMENDED to name
  the true reason ("not definitely initialized on every reachable path"). Blast radius: the
  pre-existing straight-line pin **`hir/mir-expected/N1.stderr.txt` is RE-MEASURED** (rc 2 and the
  zero-artifact law UNCHANGED). This is a WORDING amendment forced by P1-m2's own semantics.
- **item 1:** **`hir/mir-expected/N2.rc` + `N2.stderr.txt` are DELETED** — the fixture `n2: … if
  x = 1 then x = 2; return (x);` BECOMES a positive under §2: `x` initialized [1,1]; THEN arm [2,2];
  ELSE identity [1,1]; join hull **[1,2] ⊆ W(15)** ⇒ accepted (brief §3: IF without ELSE with a
  PRE-INITIALIZED variable is sound). `N2.pli` MOVES to the `mir_aot_test.py` POSITIVES panel with
  the INDEPENDENT value **2** (hand-derived: `x = 1` assigns 1; the guard `x = 1` is TRUE; the
  THEN arm assigns 2; there is no ELSE — the returned value is 2). Additive pin `hir/mir-expected/N2.mir` (measured-first).
- **item 2:** **`hir/mir-expected/N7.stderr.txt` is RE-MEASURED at m2b** (fixture stays a
  negative — the uninitialized IV still refuses, now with the §P1-m2.3 CFN3-class reason;
  predicted HIR-E19 named, MEASURED-FIRST; `N7.rc` = 2 unchanged). At m2a landing (m2b not yet
  implemented) N7 keeps its CURRENT while-refusal.
- **item 3:** `tools/mir_aot_test.py` NEGATIVES/POSITIVES tables gain those rows — the historical
  **check count 27 becomes 4 positives×6 + 6 negatives + 2 controls = 32**; recorded as a
  measured deviation (the suite stays GREEN and its semantics are strictly stronger). All OTHER
  pins (M01–M06, N1 [modulo item 0], N3–N6, N8–N21) are byte-FROZEN falsifiers; the `cu_*` top-level
  fold becoming a recursive walk must leave EVERY existing `.mir` pin and the P1-mC/P1-m1/P1-mD
  `.o`/map hashes byte-identical (I6).
Nothing else — not `ocaml/lib`, `ocaml/bin`, `hir/expected`, `hir/fixtures`, the historical gate,
or the ledger — moves. If measurement shows ANY other pre-existing byte moving, that is a STOP-
and-attribute falsifier, never a re-pin.

### P1-m2.9 DWARF sidecar compatibility (brief §7)

- Control-flow instructions are emitted through the existing `emit ?line` with the statement's
  `st_line`, so the §P1-mD.3 sidecar counts and opcode-validates branches, jumps AND label insns
  automatically (labels ARE insns — P1-mD hop-2 accepted fact); no new sidecar record type.
- Existing debug pins UNMOVED: `hir/mir-debug-expected/M05.p1md` and the debug `.o` sha
  `cb263c2c…3984782` are byte-frozen falsifiers (no fixture with If/While today carries `-g`
  pins); the non-debug `.mir` bytes and default objects stay byte-identical (T2/T9).
- New `-g` legs: CF01 through `pli80mir -g` → reviewed sidecar (every CF insn counted, branch/jmp/
  label rows at the IF statement line); `mir2o --debug-map` → cosmo **optlinux** → gdb
  `break CF01.pli:<branch line>` + `run` + `print x`/`print y` on BOTH arms' lines + `continue`
  (exit 0). CF06 loop: DWARF line table (`readelf --debug-dump=decodedline`) MUST show the loop
  body line; a gdb leg stepping the backedge (e.g. `break CF06.pli:<put line>`, three `continue`s
  hitting `i = 0/1/2`) where feasible — evidence to ignored `build/mir-cf/`.
- D2 scope is NOT expanded (no params/arrays/optimized homes); NO handwritten DWARF.

### P1-m2.10 Runner — NEW `tools/mir_aot_cf_test.py` (ADDITIVE panel; historical suites UNMOVED)

Separate panel (brief §9 "Run new test panels separately"): V0 prerequisites; V1 pins
(pli80mir ×2 fresh procs, stdout == `-o` == pin, line-by-line review was done at pin time); V2
negative arms (rc/stderr pins, zero stdout, no file, ×2); V3 native legs (§P1-m2.6 per positive:
mir2o → cosmo tiny → fresh-process stdin legs → exact bytes/rc/driver-return; CF07/CF08 also the
glibc native_check leg); V4 corruption controls C-M2a/C-M2b **observed failing loudly**; V5 static
laws (`readelf -d`: no PT_INTERP/DT_NEEDED); evidence files under `build/mir-cf/` (NEVER
committed). Every leg a DIRECT rc, separate processes, short timeouts (60 per fixture leg, 120 per
link, 900 per suite). The DWARF legs (§P1-m2.9) run in the EXISTING debug-test idiom from the
repo root (cwd law), evidence under `build/mir-cf/`.

### P1-m2.11 Gate and falsifiers (each a STOP-and-attribute gate)

**m2a gate (BEFORE m2b):** MIR text accepted by the pinned parser (mir2o rc 0 on CF01–CF05);
correct native execution of BOTH arms (CF01 legs, §P1-m2.5 bytes); stable MIR over fresh
processes; valid cosmo static links (§P1-m2.6); existing console failure behaviour UNCHANGED
(console runner 43 checks green); corruption control C-M2a FAILS natively.
**m2b gate:** §P1-m2.3 proof written + implemented; CF06 executes ≥3 genuine iterations; loop
controls fail natively; refused forms refuse BY NAME (CFN3–CFN6).

FULL FROZEN regression (T-panel, each its OWN command, rc DIRECT, never batched):
- **T1** kept exe `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` DIRECT before/after every build.
- **T2** `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc 0 every step.
- **T3** `timeout 900 python3 tools/hir_test.py` rc 0 **220 ok**, 11 frozen numbers UNMOVED, F8 green.
- **T4** FULL gate rc 0 FROZEN ALL HIT **1328/1328-190/190-9/9-149 rows 0/0-16/0/25/0-prose 5** → `build/e54p1m2-reg-gate.log`.
- **T5** `mir_aot_test.py` rc 0 (per §P1-m2.8: 27 pre-m2a; post-m2a the amended panel — deviations recorded).
- **T6** `mir_aot_cosmo_test.py` rc 0 **25**. **T7-console** `mir_aot_console_test.py` rc 0 **43**. **T7-debug** `mir_aot_debug_test.py` rc 0 **23** (from repo root).
- **T8** fresh `cd ocaml && timeout 900 dune build --build-dir _build-e54p1m2` rc 0 ZERO `Error`, warning hist **122**, fresh exe sha == kept (computed separately).
- **T9** every existing `hir/mir-expected/*.mir` byte-UNMOVED (M01–M06 + the surviving negatives); CT2 `.o` shas `78656e6c…/3822f777…/02c15b1b…` held; debug `.o` pin held.
- **T10** the NEW CF panel (§P1-m2.10) rc 0 with C-M2a/C-M2b observed failing loudly.
- **T11** ZERO oracle; ledger stays **203/C380**; `handoff.config.json` NEVER staged; explicit-path commits; scratch `build/p1m2-scratch/`, `build/mir-cf/`, `build/mir-*` NEVER committed; lab `ccc92c5c`/`f541a7a5` + `build/p1m*-deps`/`build/p1mc-deps` NEVER edited/advanced; no push.

### P1-m2.12 Complexity-stop thresholds and FORBIDDEN routes

STOP and attribute (exact reproducer) if: the pinned parser refuses any PROVEN branch form; the
counted-loop proof cannot discharge a §P1-m2.5 fixture (then REFUSE that fixture honestly and
record the limitation — brief §5 "record the exact limitation"); any pre-existing byte moves
outside §P1-m2.8; a cosmo leg needs a toolchain change. FORBIDDEN, ever: weakening I1–I5; a general
abstract interpreter / fixpoint solver (explicitly NOT required); re-pinning a failing native test
to its output; a second control-flow representation in Semantic_env; re-parsing PL/I in the
backend; new C runtime files; touching `pli_console.c`/`cosmo_link.sh`/`mir2o.c` without a
preregistered, independently reproduced defect; early/nested RETURN, parameters, arrays, FILE
streams, ON conditions, string variables (out of scope, brief §11). m2b may close DEFERRED with its
measured blocker while m2a stands (brief §12).

### P1-m2.13 Work order (successor contract — exact order)

1. **THIS COMMIT**: pre-registration (§P1-m2, explicit path `spec/lab-evidence/e2e54/PLAN.md`).
2. **m2a implementation** in `ocaml/hir/mir_backend.ml` ONLY (+ the §P1-m2.8-item-0 message and the
   recursive `cu_*` walk): build → T1 → T2 → hir_test 220 → cmp ALL existing `hir/mir-expected/*.mir`
   UNMOVED → §P1-m2.8 items 0/1 re-measurement (N1 stderr, N2 to positive) + `mir_aot_test.py`
   amendment → mir_aot/console/debug suites.
3. m2a fixtures CF01–CF05 + CFN1–CFN2 MEASURED-FIRST (review EVERY MIR line vs §P1-m2.2 before
   `cp`; determinism ×2; negatives ×2), native panel, C-M2a observed failing loudly; commit m2a
   (explicit paths) — **m2a gate CLOSED here**.
4. **m2b**: implementation (§P1-m2.3) → same gates → fixtures CF06–CF10 + CFN3–CFN6 measured-first
   → native panel + C-M2b → N7 re-pin (§P1-m2.8 item 2) → commit.
5. DWARF legs (§P1-m2.9): CF01 `-g` sidecar reviewed vs §P1-m2.3-insn law; gdb branch-line
   breakpoint + both-arm prints; CF06 line-table/backedge evidence.
6. FULL FROZEN regression T1–T11 (each its OWN command).
7. NEW runner `tools/mir_aot_cf_test.py` committed (written to §P1-m2.5/§P1-m2.10 BEFORE its first
   run; expected bytes COPIED from §P1-m2.5, NEVER from output; runner defects fixed honestly).
8. CLOSE: RESULTS §P1-m2 (m2a/m2b SEPARATELY + accepted/unsupported matrix + deviations),
   `docs/architecture/backend-boundary.md` §7-9, PLAN dashboard row, durables + guard attest →
   **STOP** — no next phase authorized without the OPERATOR.

### P1-m2.14 Dashboard update

| slice | status | notes |
|---|---|---|
| P1-m2 | **CLOSED 2026-11-12** (hops 1–7; m2a `ac56dd1d`, m2b `9672455b`, sidecar fix `f7750038`, runner `2c08a90b` rc 0 **83 measured checks**) | native control flow GREEN end-to-end: IF/ELSE with drop-not-inherit joins and bounded DO WHILE with the exact counted-loop proof; every §P1-m2.5 leg EXECUTED byte-exactly natively; C-M2a/C-M2b/W3 observed failing loudly inside the runner; §P1-m2.8 amendments landed exactly as pre-registered (N2→positive 2, N7 re-pin, 27→32); FULL FROZEN regression ALL HIT; RESULTS §P1-m2 + arch §7-9; **STOP — no next phase authorized without the OPERATOR** |

## §P1-m3 — Pre-registration: native procedure calls (by-value m3a, by-reference/aliasing m3b, value-call Call_e m3c) (committed BEFORE any repository source byte)

Operator authorization (recorded at hops 1–4, LEARNINGS §§ "E2E-54/P1-m3 hop 1/2/3/4" + hop-5
probe results, READ VERBATIM FIRST): **E2E-54/P1-m3 AUTHORIZED** — extend the native MIR backend
from one procedure to a REACHED SET of procedures with real calls, through the existing
HIR → MIR AOT → Cosmopolitan static-ELF pipeline. The OPERATOR BRIEF WAS NEVER SAVED (no
`build/p1m3-brief-true.md` exists); only the hop-1/hop-2 recorded expectation bytes survive
(`show` → stdout `5\n4\n`, driver-return 4; `alias(x,x)` → `7\n` ret 7; `alias(x,x+0)` differential
→ `2\n7\n` ret 7). The fixture programs below are MINE, honoring those recorded values; deviations
are RECORDED, NEVER fitted. Type of work: **backend engineering, ZERO oracle calls**; nothing here
is or becomes a DR historical claim — the ledger stays 203 headers ending **C380**. Starting
reference `b335280a`→`ff3b8c4e`→HEAD (hops 1–5; baseline verified first-hand each hop); this
pre-registration lands BEFORE any source byte (PROTOCOL #1).

All design authority is MEASURED first-hand against the PINNED lab (`ccc92c5c`/`f541a7a5`, never
advanced/edited), the pinned `build/p1m0-deps/mir2o` and `build/p1mc-deps` toolchain (never
edited), the LIVE parser/hir_build/mir_backend, and the pinned MIR syntax law (MIR.md). No
expected byte below was produced by running the compiler on a fixture pinned below — every
expectation is hand-derived HERE, BEFORE any run.

### P1-m3.0 Milestones (SEPARATE deliverables)

- **m3a — by-value calls.** A REACHED set of procedures lowers to one MIR module: callee-first
  emission, per-callee protos, HOME-PASS ABI (§P1-m3.2). Every actual is `A_value` (literal or
  expression); `Call_s` to a void callee lowers; a value callee ends `RETURN(expr)`. GREEN means:
  CALL02–CALL05 + CALL09 EXECUTE their §P1-m3.6 bytes natively; every existing pin is byte-UNMOVED
  (I6); the corruption control C-M3a fails natively; the m3a gate (§P1-m3.12) passes.
- **m3b — by-reference actuals and aliasing.** `A_reference (D_var)` actuals pass the caller's
  entry-hoisted HOME; the callee's writes are visible through the alias; env widening after calls;
  uninitialized-by-ref refusal. GREEN means: CALL01 (`5\n4\n` dr 4), CALL06A (`7\n` dr 7) and the
  differential CALL06B (`2\n7\n` dr 7) and the mixed-mode discriminator CALL10 (`7\n9\n` dr 9 —
  see the DEVIATION pre-registered in §P1-m3.10 item 5) EXECUTE exactly; CALLN8/CALLN10 land as
  predicted (N10 now POSITIVE); C-M3b fails natively; the m3b gate passes.
- **m3c — value-position calls (`Call_e`).** Admitted ONLY as the whole RHS of an Assign or the
  whole expression of a Return, all actuals `A_value`; result interval `W(ret-p)`. GREEN means:
  CALL07/CALL08 EXECUTE; CALLN9 refuses; C-M3c fails natively; the m3c gate passes.

**Complete the m3a gate before implementing ANY m3b byte; the m3b gate before ANY m3c byte.**
CLOSE after all three (or later milestones closed-DEFERRED with measured blockers while earlier
ones stand): RESULTS §P1-m3 (m3a/m3b/m3c SEPARATELY), `docs/architecture/backend-boundary.md`
§7-10, dashboard row, durables, then **STOP** — no next phase is authorized automatically.

### P1-m3.1 MEASURED design facts (hops 1–5, first-hand; this section pre-registers, it does not re-measure)

1. **HIR (hir_build read first-hand, hops 3–4):** passing-mode dispatch is PER-SITE on the ACTUAL
   syntax: `PM_immediate`/`PM_value_cell` require `ex_ty = formal_ty` (HIR-E17) and yield
   `A_value`; `PM_own_cell` (bare name) yields `A_reference (D_var sid | D_elem)`; `PM_copy_in`
   refuses E16; whole-array E15. `Call_s` to a value-returning proc refuses **HIR-E07**
   ("statement-level call to function <key> discards a value; unlowered in P0") on BOTH arms ⇒ the
   backend NEVER sees a value-discarding `Call_s` (hop-3 clause FALSIFIED/moot). `Call_e` with no
   bind RETURNS fact refuses E07 ("has no bind RETURNS fact"). Direct self-recursion refuses E07
   ("recursive procedure <key> is outside the P0 subset"); MUTUAL recursion is HIR-blind ⇒ BACKEND
   DFS cycle refusal. HIR-E11 makes folded procedure names unique ⇒ the `pli80_<folded>` symbol is
   unique by construction; the `_<pid>` collision suffix is UNREACHABLE in the subset (recorded,
   no fixture, no invented negative). Entry is `procs` head: `pid 0`, `is_main`; `proc` carries
   `pid/name/scope/params/ret/body`; NO `parent` field — parentage = scope graph (§P1-m3.2 law 2).
2. **MIR syntax EXECUTION-PROVEN (hop-2 probes + hop-5 y1/y2, all executed green):** callee title
   carries formals (`func i64, i64:x` = result type FIRST, then arg regs; `func i64:m` = void WITH
   formals; `func` = void no-formals; `func i64` = value no-formals); formals are NOT in `local`;
   call row `call <proto>, <name>, <res…>, <args…>` (result operands iff the PROTO has a leading
   bare result type; the callee name may be a DEFINED func — `R_X86_64_PC32` into .text, nm shows
   non-exported callee as LOCAL `t`); result regs live in the CALLER locals; per-func register
   scoping (`t1` reused in two funcs); func items MUST be CALLEE-FIRST (forward def ⇒ mir2o rc 1
   `undeclared name`); module-scope labels — cross-func branch target or undefined target ⇒ mir2o
   **SEGFAULT rc 139 SILENT**; duplicate definition ⇒ clean rc 1; `alloca <reg>, 8` at function
   ENTRY in ANY func; callee store through a passed home is observed by the caller (alias EXEC);
   by-value write isolation (x8 EXEC 38); caller vregs live across calls (x7 EXEC 111 — NO manual
   save/restore); **a NO-RESULT func REJECTS `ret <op>`** — measured error VERBATIM: `func
   pli80_out: in instruction 'ret': number of operands in return does not correspond number of
   function returns. Expected 0, got 1` ⇒ VOID failure tails end with BARE `ret` (hop-5 y2).
3. **Backend anchors (first-hand):** refusals today — multi-proc E20 at mir_backend.ml:131 (the arm
   §P1-m3.9 replaces); `Hir.Call_s` E18 at :922; `Hir.Call_e` E18 at :295; auto vars live in
   registers `v<sid>`; `fresh ()` numbers `t<k>` module-wide; `cf_n` numbers `Lthen/Lelse/Ljoin/
   Lh/Lx` module-wide; `declared : Int_map` precision per sid; `v_regs` filters
   `scope = p.scope && sstorage = Auto`; locals line = ascending `v<sid>` then `st?` then `a1?`
   then ascending `t<k>`; protos used-only, fixed relative order, BEFORE the ONE import line;
   `exit` ALWAYS imported (failure tail). Diagnostic codes (diagnostic.ml): backend E18 node /
   E19 numeric / E20 export (NOT E13).
4. **Fixture/pin law (unchanged):** new inputs CRLF+`^Z` in the NEW ADDITIVE directories
   `hir/mir-call-fixtures/`, pins (MEASURED-FIRST `cp` after line-by-line review vs this section,
   NEVER hand-written) in `hir/mir-call-expected/`; generated with `build/p1m2-scratch/mkpli.py`;
   negatives pin rc + stderr bytes with ZERO stdout and NO `-o` file, ×2 fresh processes.

### P1-m3.2 ABI and emission contract (`ocaml/hir/mir_backend.ml` ONLY; THE binding law)

1. **Selection:** `prog.procs` non-empty; entry = head (`pid 0`); `--export` must fold-equal the
   ENTRY name (the existing message shape stays); entry `params = []` and entry `ret = Some
   Fixed_bin(p,0)` keep their EXISTING E20 refusals (entries remain value-returning,
   zero-parameter — unchanged law).
2. **Reachability + validation (pre-lowering scans, in this order):**
   (a) NESTING: for every NON-ENTRY proc p whose scope has a CHILD scope (a proc lexically inside
   a subsidiary — the CAND09/depth-2 shape), refuse E18 by name ("a nested procedure inside a
   subsidiary procedure is outside the native subset"); the scan runs for ALL non-entry procs
   BEFORE dropping, so an unreached depth-2 proc still refuses (CALLN6). Nesting inside the ENTRY
   (ordinary siblings) is the accepted shape.
   (b) DFS from the entry over `Call_s`/`Call_e` pids (arguments left-to-right, statements in
   source order); a revisit of a node ON THE CURRENT PATH ⇒ refuse E18 NAMING the cycle path; a
   direct self-call is caught HIR-side first and never reaches here.
   (c) UNREACHED procs are **DROPPED** from the artifact (their bodies were never lowered; bind
   already validated them) — the CALL09 pin falsifies the drop.
   (d) per reachable proc: portable folded name; every `dcl` row inside the proc already lowers
   `Declare sid` (formals included — the existing `declare` must route `sstorage = Formal` as the
   already-registered arg register instead of refusing); formal `dcl` type must equal the
   `bin_p`-admitted type; a VALUE callee's FINAL body statement must be `Return (Some expr)`
   (fall-through or bare `RETURN;` ⇒ E18 by name); a VOID callee's tail is a bare `ret`; a `Return
   (Some …)` inside a VOID callee and early/`If`/`While`-nested `Return` keep the EXISTING
   subsidiary refusals.
3. **Emission order:** func items in DFS POST-ORDER (callees before callers; ties resolved by
   ascending pid), entry LAST and the ONLY `export`. Module layout (multi-proc):
   `M0:\tmodule` / callee protos `pc<pid>:\tproto\t[i64, ][i64:v<s1>[, i64:v<s2>…]]` (used-only,
   ascending pid; a value callee has the LEADING BARE `i64` result) / console protos (existing
   fixed relative order, used-only across ALL funcs) / the ONE import line (existing canonical
   order + `exit`) / func items / `\texport pli80_<entry-folded>` / `\tendmodule`. SINGLE-proc
   programs emit the CURRENT bytes EXACTLY (no `pc0`, `Lfail`, same lines) — falsifier I6.
4. **Func item shape:** title `pli80_<folded>:\tfunc\t[i64, ][i64:v<s1>[, …]]` (bare leading
   result type iff the proc `ret <> None`; formal regs in DECLARATION order, EXCLUDED from the
   locals line; callee accesses formals ONLY via `i64:(v<sid>)`). Locals line, ascending within
   each class: own `Auto` ascending `v<sid>`; then `st` (iff THIS func contains any console call);
   then `a1` (iff this func contains GET); then `h<sid>` (this func's by-ref homes, ascending sid,
   m3b); then `hv<k>` (this func's value cells, ascending k, m3b); then the func's `t<k>` temps in
   MODULE-WIDE ascending numbering (the existing `fresh ()` counter continues across funcs).
   Entry hoists (`alloca <reg>, 8` as the first instructions after `func`/`local`): `a1` (GET law,
   existing), then each `h<sid>`, then each `hv<k>` — ALL hoisted at ENTRY, never at the call site
   (no per-iteration stack growth).
5. **Failure tails:** per func, after its final `ret`: `Lfail_0:` (entry pid 0) / `Lfail_<pid>:`
   (subsidiary) with `call p_exit, exit, st` then **`ret st` in the ENTRY (value func)** and **BARE
   `ret` in EVERY VOID func** (hop-5 measured law; the exit call never returns anyway). When the
   REACHED set is exactly one func the tail is the EXISTENT shared `Lfail:` with `ret st` —
   byte-frozen (I6). `p_exit`'s proto carries the leading bare `i64` result so the `call …, st`
   row is legal in void funcs too.
6. **Actual lowering (HOME-PASS; one representation for ALL sites):** every call passes ADDRESSES.
   - `A_value x`: lower `x` in the CALLER env through the existing `lower` (its own window proof;
     E17 typing already HIR-side) → `rv`; fresh cell `hv<k>` (module-wide counter):
     `alloca hv<k>, 8` hoisted at caller entry + `mov i64:(hv<k>), <rv>` immediately before the
     `call`; pass `hv<k>`. The cell is REWRITTEN at every call and NEVER read back by the caller
     (copy semantics). One `hv<k>` PER (call-site, argument-position); a call inside a loop reuses
     its cells.
   - `A_reference (D_var sid)` (m3b): sid must be an `Auto` of the CALLER proc (else E18 by name);
     `D_elem` refuses E18 (arrays outside the subset). The caller gives sid a HOME `h<sid>` for the
     WHOLE func: `alloca h<sid>, 8` at entry; while designated, EVERY read/write of sid rides
     `i64:(h<sid>)` (the var has NO register). If the caller env proves sid UNINITIALIZED
     (`find_opt = None`) at the call site, refuse E19 by name (the callee could read garbage). The
     HOME REG `h<sid>` is passed.
   - The callee's formal sids enter the callee env with interval `W(formal-precision)` (a sound
     over-approximation; no caller-interval propagation in m3).
7. **Call rows:** void callee (`Call_s`): `call pc<pid>, pli80_<folded>, <argregs…>` (NO result
   operand). Value callee (`Call_e`, m3c): the CALLER declares one fresh result reg `r<k>` in ITS
   locals (class order after `hv<k>`, ascending) and emits `call pc<pid>, pli80_<folded>, r<k>,
   <argregs…>`; the result interval is `W(ret-p)` (no interprocedural value propagation — sound
   over-approximation); the value-position admission is §P1-m3.5.
8. **Env law across calls (brief-safety core):** after a call, EVERY caller sid designated by a
   by-ref actual in that call widens to its declared `W(p)` (I2); by-value actuals change NOTHING
   (x8 write-isolation; the value cell is dead afterwards); caller locals NOT passed keep their
   env (x7 live-across-call is a MIR-allocator property, PROVEN). Window checks (I1) keep
   validating every read.
9. **`-g` / `--debug-map` with a REACHED multi-proc set:** refuse E18 BY NAME (the §P1-mD.3 sidecar
   format is hard single-func: one `func 0`, one instruction table). Single-proc `-g` bytes stay
   byte-frozen.
10. **Label law (hop-2 SEGFAULT hazard):** every branch target (`Lfail_<pid>`, `Lthen/Lelse/Ljoin/
    Lh/Lx`) is defined IN THE SAME func and is module-unique; `cf_n` stays module-wide.

### P1-m3.3 m3a scope precisely

Items 1–5, 6 (`A_value` only), 7 (void), 8 (by-value half), 10, plus the `Hir.Call_s` arm replacing
mir_backend.ml:922 and the E20 arm replacement (§P1-m3.9). An `A_reference` actual refuses E18 BY
NAME ("by-reference actual argument N of call to <key> is admitted at milestone P1-m3b") — this is
CALLN10, the milestone discriminator, DELETED at m3b landing (§P1-m3.9 item 2).

### P1-m3.4 m3b scope precisely

Item 6 `A_reference`/home law + item 8 widening + uninitialized-by-ref E19 + `D_elem` E18; the
CALLN10 arm DELETED and its fixture re-measured as POSITIVE behaviour (its PASS is part of the m3b
gate); CALL01/06A/06B/10 fixtures + pins + native legs; C-M3b.

### P1-m3.5 m3c scope precisely

`Hir.Call_e` lowers ONLY in the two admitted shapes: `Assign (D_var sid, ex)` where `ex` is the
`Call_e` node WHOLE, and `Return (Some ex)` where `ex` is the WHOLE expression (value callee as the
FINAL statement — the value-entry law). A `Call_e` anywhere else (inside a `Bin`, a `Convert`, a
PUT item, a GET target, a condition operand) refuses E18 by name (CALLN9). All actuals must be
`A_value`; a value callee MUST end `RETURN(expr)` (law 2d). Result reg + interval per §P1-m3.2-7.
Value callees reached ONLY via `Call_e` may now also be VOID-mixed; CALL05/CALL08 pin both tail
shapes.

### P1-m3.6 Fixtures and INDEPENDENT expected results (recorded HERE, BEFORE any run)

All files CRLF+`^Z` via `build/p1m2-scratch/mkpli.py`. `--export` names the ENTRY (folded,
case-insensitive). Value legs run BOTH the glibc `native_check` driver (`-DENTRY=pli80_<entry>
-DEXPECTED=<v>`, stdout `<v>\n`, rc 0) AND the cosmo-tiny console-driver leg (stdout EXACT, stderr
`driver-return=<v>\n`, rc 0). Every derivation is by PL/I semantics ONLY — never from generated
MIR.

POSITIVE — m3a (no by-ref actuals; every bare-name use is m3b):

CALL02.pli — entry `call02` (void callee with a LOCAL, expression actual):

    call02: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 2;
       call side(4 + x);
       put list(x);
       return (x);
       side: procedure(n);
          dcl n fixed bin(15);
          dcl t fixed bin(15);
          t = n + 1;
       end side;
    end call02;

  Hand-derivation: x = 2; actual 4+2 = 6 by value; side computes t = 7 into a LOCAL — x is
  UNTOUCHED; `put list(x)` prints 2. Expected: **stdout `2\n`, driver-return=2, native_check
  EXPECTED=2**, rc 0. (Honors the CAND06 program verbatim.)

CALL03.pli — entry `two` (two calls; live-across-call; NO console ⇒ no stdout at all):

    two: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 30;
       call side(5);
       x = x + 7;
       call side(9);
       return (x);
       side: procedure(m);
          dcl m fixed bin(15);
       end side;
    end two;

  Derivation: 30 + 7 = 37; the void callee reads nothing. Expected: **native_check EXPECTED=37
  stdout `37\n` rc 0; tiny console-driver stdout `` (EMPTY), `driver-return=37\n`, rc 0**.

CALL04.pli — entry `chain` (transitive chain entry→mid→leaf; console PUT inside the DEEPEST
callee; all actuals by value via `+ 0`):

    chain: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 51;
       call mid(x + 0);
       x = x + 40;
       return (x);
       mid: procedure(m);
          dcl m fixed bin(15);
          dcl t fixed bin(15);
          t = m + 40;
          call leaf(t + 0);
       end mid;
       leaf: procedure(d);
          dcl d fixed bin(15);
          put list(d);
       end leaf;
    end chain;

  Derivation: mid receives 51; t = 91; leaf PUTs 91 (`91\n`); leaf cannot write d's actual; x = 51
  + 40 = 91. Expected: **stdout `91\n`, driver-return=91, EXPECTED=91**, rc 0. (The `91` coincidence
  is arithmetic, not fitted: 51 + 40 = 91 and 51 + 40 = 91.)

CALL05.pli — entry `retvoid` (VOID callee ending with BARE `RETURN;` — the law decision of this
pre-registration: a void callee's `Return None` lowers to bare `ret`; a VALUE callee with
fall-through or bare `RETURN;` refuses E18 by name; hop-3 "DECIDE + WRITE"):

    retvoid: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 9;
       call nope(1);
       return (x);
       nope: procedure(a);
          dcl a fixed bin(15);
          RETURN;
       end nope;
    end retvoid;

  Derivation: callee writes nothing reachable; returns 9. Expected: **EXPECTED=9 (stdout `9\n`);
  tiny stdout ``, `driver-return=9\n`, rc 0**.

CALL09.pli — entry `uncalled` (unreached-sibling DROP POSITIVE — the pin MUST show exactly TWO
func items, `pli80_dsub` then `pli80_uncalled`; `pli80_dead` ABSENT):

    uncalled: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 3;
       call dsub(x + 0);
       return (x);
       dsub: procedure(q);
          dcl q fixed bin(15);
       end dsub;
       dead: procedure(r);
          dcl r fixed bin(15);
       end dead;
    end uncalled;

  Derivation: dead is unreached; x = 3 unchanged. Expected: **EXPECTED=3; tiny stdout ``,
  `driver-return=3\n`, rc 0**; pin law above is a REVIEW criterion (a dead func present =
  falsifier).

POSITIVE — m3b (by-reference homes; the recorded brief values):

CALL01.pli — entry `main3` (the brief's `show` CONTRACT `5\n4\n` dr 4; program mine — the brief was
never saved; `show` receives x by REFERENCE and PUTs it):

    main3: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 5;
       call show(x);
       put list(4);
       return (4);
       show: procedure(b);
          dcl b fixed bin(15);
          put list(b);
       end show;
    end main3;

  Derivation: x = 5 designated; show PUTs the home's value 5; main PUTs literal 4; returns 4. The
  MIR-level bytes of exactly this program were ALREADY EXECUTED by probe y2 (hop 5). Expected:
  **stdout `5\n4\n`, `driver-return=4\n`, rc 0; EXPECTED=4** (the recorded brief bytes VERBATIM).

CALL06A.pli — entry `aliasin` (aliasing; brief family `7\n` dr 7):

    aliasin: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 2;
       call alias(x, x);
       put list(x);
       return (x);
       alias: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          b = 7;
          a = b;
       end alias;
    end aliasin;

  Derivation: BOTH actuals designate the SAME home h(x); `b = 7` writes x := 7; `a = b` reads 7
  writes 7; caller PUTs 7, returns 7. Expected: **stdout `7\n`, `driver-return=7\n`, EXPECTED=7**
  (recorded brief value honored).

CALL06B.pli — entry `diffal` (the DIFFERENTIAL: same aliasing callee, second actual a VALUE copy
⇒ the callee sees the PRE-CALL value; binding text, single version):

    diffal: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 2;
       call alias(x, x + 0);
       put list(x);
       return (x);
       alias: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          a = 7;
          put list(b);
       end alias;
    end diffal;

  Derivation: `a` designates x's home; `b` is a value cell holding the PRE-CALL copy 2. Inside the
  callee `a = 7` writes x := 7 through the home; `put list(b)` prints the COPY 2; the caller then
  PUTs x = 7 and returns 7. Expected: **stdout `2\n7\n`, `driver-return=7\n`, EXPECTED=7** (the
  recorded brief differential VERBATIM — the copy-vs-alias DISCRIMINATOR: a wrong ABI passing x's
  home twice would print `7\n7\n`).

CALL10.pli — entry `mixmod` (MIXED-MODE discriminator: ONE callee whose BOTH formals are
designated at site 1 and VALUES at site 2 — impossible under any per-formal fixed representation;
the HOME-PASS law makes it legal; binding text, single version):

    mixmod: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       dcl y fixed bin(15);
       x = 2;
       y = 2;
       call clob(x, x);
       put list(x);
       call clob(20, 40);
       x = x + y;
       return (x);
       clob: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          b = 3;
          a = 7;
       end clob;
    end mixmod;

  Derivation (binding): site 1 passes BOTH actuals by reference (same home h(x)); `b = 3` writes
  x := 3; `a = 7` writes x := 7; `put list(x)` prints **7**. Site 2 passes VALUES 20 and 40 into
  the two value cells; the callee writes ONLY the cells (b's cell ← 3, a's cell ← 7) — caller
  x = 7 and y = 2 are UNCHANGED (by-value write isolation); `x = x + y` = 9. Expected: **stdout
  `7\n9\n`, `driver-return=9\n`, EXPECTED=9**. **DEVIATION PRE-REGISTERED (§P1-m3.10 item 5):
  the hop-4 panel sketched `7\n34\n` dr 48 for a program whose text was never saved; with the
  hop-4 callee shape (`b = 7; a = b;`) the sketch leaves `y` UNINITIALIZED at `x = x + y` —
  honestly UNDERIVABLE; this binding text replaces the sketch, recorded BEFORE any run.**

POSITIVE — m3c (Call_e whole shapes):

CALL07.pli — entry `thrice` (whole-RHS Assign; three value actuals):

    thrice: procedure returns(fixed bin(15));
       dcl z fixed bin(15);
       z = thrice3(1, 2, 3);
       put list(z);
       return (z);
       thrice3: procedure(a, b, c) returns(fixed bin(15));
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          dcl c fixed bin(15);
          dcl t fixed bin(15);
          t = a + b + c;
          return (t);
       end thrice3;
    end thrice;

  Derivation: 1+2+3 = 6. Expected: **stdout `6\n`, `driver-return=6\n`, EXPECTED=6**.

CALL08.pli — entry `wret` (whole-Return Call_e; honors hop-3's recorded `ret 42`; value actual is
an EXPRESSION so no by-ref is involved):

    wret: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 41;
       return (addone(x + 0));
       addone: procedure(n) returns(fixed bin(15));
          dcl n fixed bin(15);
          dcl t fixed bin(15);
          t = n + 1;
          return (t);
       end addone;
    end wret;

  Derivation: (41+0) + 1 = 42. Expected: **EXPECTED=42 (stdout `42\n`); tiny stdout ``,
  `driver-return=42\n`, rc 0**.

NEGATIVE (each predicted code + REFUSING LAYER; rc 2, ZERO stdout, NO `-o` file, ×2 fresh
processes; MEASURED-FIRST — a deviation is RECORDED, never fitted):

| id | entry (export) | program | PREDICTED refusal | LAYER | milestone |
|---|---|---|---|---|---|
| CALLN1 | `pval` | `pv: procedure(n) returns(fixed bin(15)); dcl n fixed bin(15); return (n); end pv;` entry `y = pv(1);` | E07 `procedure pv used as a value: P0 admits calls only` | HIR | all |
| CALLN2 | `disc` | entry calls `call addone(1);` where addone RETURNS a value | E07 `statement-level call to function addone discards a value; unlowered in P0` | HIR | all |
| CALLN3 | `nar` | `call side(5);` where `side: procedure(a, b);` (arity 2, called with 1) | E07 `call to side passes 1 arguments to 2 bind-registered formals` | HIR | all |
| CALLN4 | `cyc` | entry `cyc` → `call p1(1);`; `p1(n): call p2(n);`; `p2(n): call p1(n);` (3-node cycle, CAND07) | E18 naming the cycle path | BACKEND | all |
| CALLN5 | `vusage` | `z = side2(5);` where `side2` is VOID (no RETURNS fact) | E07 `procedure side2 has no bind RETURNS fact: value use unlowered` | HIR | all |
| CALLN6 | `nest2` | CAND09 shape: entry → `call mid(x + 0);`, `mid` CONTAINS `deep` (deep NEVER called) | E18 nested procedure outside the subset (validation scan, unreached does NOT rescue) | BACKEND | all |
| CALLN7 | `main3` (CALL01 text) | SAME program compiled with `-g --debug-map <map>` | E18 multi-proc debug refusal BY NAME; NO `.mir`, NO map written | BACKEND | m3b+ |
| CALLN8 | `uninit` | `dcl y …; call alias(y, y);  y = 1; …` (by-ref actual of a NEVER-ASSIGNED var) | E19 uninitialized-by-reference refusal | BACKEND | m3b |
| CALLN9 | `deep9` | `z = thrice3(1, 2, 3) + 5;` (Call_e INSIDE a larger expression) | E18 value-position call outside the whole-RHS/whole-Return shapes | BACKEND | m3c |
| CALLN10 | `refm3a` | `x = 2; call clob2(x, x); …` with clob2 void writing formals (CALL10-site shape) | m3a: E18 by-reference actual admitted only at milestone m3b; **TRANSITIONAL — DELETED at m3b landing**, fixture then must lower clean (m3b gate) | BACKEND | m3a only |

NEGATIVE program texts (binding, full; CRLF+`^Z`; the PREDICTED reasons above cite these exact
programs):

CALLN1.pli — entry `pval` (procedure used as a value; HIR):

    pval: procedure returns(fixed bin(15));
       dcl y fixed bin(15);
       y = pv(1);
       return (y);
       pv: procedure(n) returns(fixed bin(15));
          dcl n fixed bin(15);
          return (n);
       end pv;
    end pval;

CALLN2.pli — entry `disc` (statement call discarding a value; HIR):

    disc: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 1;
       call addone(x + 0);
       return (x);
       addone: procedure(n) returns(fixed bin(15));
          dcl n fixed bin(15);
          dcl t fixed bin(15);
          t = n + 1;
          return (t);
       end addone;
    end disc;

CALLN3.pli — entry `nar` (arity mismatch; HIR):

    nar: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 1;
       call side(x + 0);
       return (x);
       side: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
       end side;
    end nar;

CALLN4.pli — entry `cyc` (3-node cycle; BACKEND DFS names the path):

    cyc: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 1;
       call p1(x + 0);
       return (x);
       p1: procedure(n);
          dcl n fixed bin(15);
          call p2(n + 0);
       end p1;
       p2: procedure(n);
          dcl n fixed bin(15);
          call p1(n + 0);
       end p2;
    end cyc;

CALLN5.pli — entry `vusage` (value use of a VOID callee; HIR E07 no-RETURNS):

    vusage: procedure returns(fixed bin(15));
       dcl z fixed bin(15);
       z = side2(5);
       return (z);
       side2: procedure(m);
          dcl m fixed bin(15);
       end side2;
    end vusage;

CALLN6.pli — entry `nest2` (depth-2 nesting, CAND09 shape; BACKEND; the nested `deep` is NEVER
called — unreached does NOT rescue):

    nest2: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 4;
       call mid(x + 0);
       return (x);
       mid: procedure(m);
          dcl m fixed bin(15);
          dcl u fixed bin(15);
          u = m;
          deep: procedure(dd);
             dcl dd fixed bin(15);
             dd = 1;
          end deep;
       end mid;
    end nest2;

CALLN7 — NO separate program: the CALL01.pli text compiled with `-g --debug-map <map>` (backend
multi-proc debug refusal; pins rc 2 + stderr, NO `.mir`, NO map file).

CALLN8.pli — entry `uninit` (by-ref actual of a NEVER-ASSIGNED variable; BACKEND E19; m3b):

    uninit: procedure returns(fixed bin(15));
       dcl y fixed bin(15);
       call al(y, y);
       y = 1;
       return (y);
       al: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          a = 1;
       end al;
    end uninit;

CALLN9.pli — entry `deep9` (Call_e INSIDE a larger expression; BACKEND; m3c):

    deep9: procedure returns(fixed bin(15));
       dcl z fixed bin(15);
       z = thrice3(1, 2, 3) + 5;
       return (z);
       thrice3: procedure(a, b, c) returns(fixed bin(15));
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          dcl c fixed bin(15);
          dcl t fixed bin(15);
          t = a + b + c;
          return (t);
       end thrice3;
    end deep9;

CALLN10.pli — entry `refm3a` (by-ref actual at m3a; TRANSITIONAL, deleted at m3b):

    refm3a: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 2;
       call clob2(x, x);
       return (x);
       clob2: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          a = 7;
       end clob2;
    end refm3a;

SELF-RECURSION note (accepted pre-registered fact, NO new fixture): `rp: procedure(n); call
rp(n); end rp;` refuses HIR-E07 `recursive procedure rp is outside the P0 subset` (read first-hand
at hir_build.ml:425) — HIR-side, never reaches the backend DFS.

### P1-m3.7 Native validation panel methodology (per positive; §P1-m2.6 idiom)

(1) pipeline proof `pli80hir.exe <fixture>` rc 0 (HIR admits); (2) `pli80mir --export <entry> -o
X.mir fixture` TWICE in FRESH processes — `-o` file byte-equal to the reviewed
`hir/mir-call-expected/<id>.mir` pin (EVERY line reviewed against §P1-m3.2 BEFORE the `cp`; the
pin is NEVER hand-written); (3) `build/p1m0-deps/mir2o -f X.mir X.o` rc 0 (pinned-parser acceptance;
THIS run is the syntax authority); (4) glibc leg `gcc -O0 -DENTRY=pli80_<entry> -DEXPECTED=<v>
tools/mir_aot/native_check.c X.o -o …` + EXEC (stdout `<v>\n`, rc 0); (5) cosmo TINY console leg
(`tools/mir_aot/cosmo_link.sh tiny`, WITH `tools/mir_aot/pli_console.c` + `console_check.c`,
timeout 120, `chmod +x`, fresh-process exec vs the §P1-m3.6 bytes; console fixtures MUST link
`pli_console.c`); (6) static laws: no `PT_INTERP`, no dynamic section, `nm T pli80_<entry>` and
subsidiaries present as LOCAL `t` symbols; (7) negatives: rc 2 + stderr pins + ZERO stdout + NO `-o`
file, ×2. Timeouts 60 per leg.

### P1-m3.8 Corruption controls (non-vacuity; DISPOSABLE copies under `build/p1m3-scratch/` ONLY — never a pin, never the compiler)

- **C-M3a (order law):** take a measured m3a pin `.mir` copy and move the CALLEE func item AFTER
  its caller (the x5-proven failure); re-`mir2o` MUST FAIL (rc 1 `undeclared name`) — the native
  panel step for the perturbed copy fails LOUDLY (a link/exec that silently succeeds = falsifier
  that the control is vacuous).
- **C-M3b (home vs value):** on a DISPOSABLE CALL06B copy, replace the by-ref actual register
  `h<sid>` in the FIRST call row with the caller's value copy (pass `hv<…>` for BOTH args — the
  wrong ABI); re-`mir2o`, link, EXEC: stdout MUST NOT equal `2\n7\n` (prediction `7\n7\n` — the
  alias dies). Observed failing LOUDLY inside the runner.
- **C-M3c (result corruption):** on a DISPOSABLE CALL07 copy, insert `add <rt>, <rt>, 1`
  immediately BEFORE the callee's final `ret <rt>` (perturb the RETURNED value only). Re-`mir2o`
  (rc 0 expected — the artifact stays valid), link the glibc driver with the ORIGINAL
  `-DEXPECTED=6`: the EXECUTED value is 7 ⇒ `native_check` rc 1 ⇒ the native panel step for the
  perturbed copy fails LOUDLY; the runner treats a control that PASSES (executes 6) as SUITE
  FAILURE.
- Every control MUST be OBSERVED failing first-hand during its milestone; a control that executes
  the CORRECT bytes is itself a falsifier (the test is vacuous).

### P1-m3.9 Pre-registered amendments to PRE-EXISTING artifacts (the complete list; nothing else moves)

- **item 1 (E20 arm replacement):** the blanket multi-proc refusal at mir_backend.ml:131
  ("P1-m0 exports exactly one procedure…") is REPLACED by the §P1-m3.2-1/2 selection+validation
  arms. NO pre-existing pinned negative exercises the multi-proc arm (grep of every
  `hir/mir-expected/*.stderr.txt` + `hir/mir-cf-expected/*.stderr.txt` for `exactly one procedure`
  is EMPTY — verified first-hand this hop), so NO existing pin changes.
- **item 2 (TRANSITIONAL CALLN10):** the m3a by-ref refusal + its fixture/pins are DELETED at m3b
  landing (the §P1-m2.8 idiom); the deletion is pre-registered HERE; the CALL10/CALL06 family then
  covers the same code as POSITIVES.
- **item 3 (multi-func `Lfail` rename):** ONLY when the REACHED set has >1 func; the SINGLE-func
  artifact keeps `Lfail:` byte-EXACT (I6 falsifier).
- FROZEN FALSIFIERS (byte-IDENTICAL through ALL of m3a/m3b/m3c): EVERY `hir/mir-expected/*` (M01–
  M06, N2.mir, all N*.rc/.stderr.txt), EVERY `hir/mir-cf-expected/*`, `hir/mir-debug-expected/*`
  (M05.p1md), the CT2 `.o` shas `78656e6c…/3822f777…/02c15b1b…`, the debug `.o`
  `cb263c2c…3984782`. Suite counts: `mir_aot_test.py` **32**, cosmo **25**, console **43**, debug
  **23**, CF **83** — all UNMOVED; the gate **1328/1328-190/190-9/9-149 rows 0/0-16/0/25/0-prose
  5**; fresh `--build-dir _build-e54p1m3` hist **122** sha == kept `172595d5…`; hir_test **220
  ok**/11 numbers UNMOVED. `ocaml/lib`, `ocaml/bin`, `hir/expected`, `hir/fixtures` stay
  byte-clean (T2).

### P1-m3.10 Deviations recorded IN ADVANCE (honest, never fitted)

1. hop-4 pre-registered the void failure tail as `ret st`; mir2o REJECTED it (hop-5 measured
   VERBATIM); the LAW is bare `ret` on void tails — §P1-m3.2-5 states the measured law.
2. The brief was never saved; the CALL fixture PROGRAMS are mine, honoring the recorded bytes
   `5\n4\n`/`7\n`/`2\n7\n` exactly where an honest program yields them.
3. The `_<pid>` collision suffix is UNREACHABLE (HIR-E11) — the code path may exist but NO fixture
   exercises it (recorded like CFN6).
4. The narrow-formal/window-overflow-at-formal class is UNEXERCISABLE (E17 typing: every literal/
   binop actual is `FIXED BINARY(15,0)`) — no fixture (recorded).
5. The hop-4 CALL10 note `7\n34\n` dr 48 was NEVER reproducible from any initialized program whose
   text survives; the settled CALL10 (with `dcl y; y = 2`) derives `7\n9\n` dr 9 — recorded HERE
   BEFORE any run (this pre-registration OVERRIDES the hop-4 sketch; the hop-4 panel was explicitly
   "full texts + independent derivations GO IN THE PLAN").
6. The CALL panel check count is MEASURED (no formula), like the CF 27→32 precedent.
7. FALSIFICATION PRESERVED (hop 10, measured, never fitted): against the ORIGINAL §P1-m3.6 texts,
   the pre-registered POSITIVES CALL02/CALL04 refused `HIR-E19 … binop '+' … leaving the
   declared-precision window [-16383,16383] of FIXED BINARY(15,0)` at line 10, and the CALLN1
   negative measured BACKEND E18, not the predicted HIR E07. Recorded and adjudicated by the
   OPERATOR in §P1-m3.15 (option (a)); the original §P1-m3.6 blocks stand above as history.

### P1-m3.11 Numeric-safety invariants (NEVER weakened; falsifiers if violated)

- I1 the window law unchanged (every arithmetic read proved inside its declared window, incl.
  inside every subsidiary body).
- I2 no read EVER lowers with a `Some` that a call could invalidate: by-ref-designated sids widen
  to `W(declared)` after each call that passes them; uninitialized-by-ref refuses E19.
- I3 by-value isolation: a `Call_e`/`Call_s` result carries `W(ret-p)`/callee-env intervals ONLY;
  no caller interval survives into a callee and vice versa (no interprocederal propagation is
  claimed).
- I4 the DROP law never drops a DESIGNATED home's initialization state silently past a widening —
  widening is monotone to `W(p)`, never to `Some` narrower.
- I5 label law: every branch target same-func + module-unique (SEGFAULT hazard).
- I6 SINGLE-proc bytes byte-identical to every existing pin (mir + cf + debug + `.o` shas above).

### P1-m3.12 Gate and falsifiers (each a STOP-and-attribute gate)

**m3a gate:** build → T1 `172595d5…` DIRECT → T2 clean → hir_test 220/11 → cmp EVERY mir + CF pin
UNMOVED; CALL02–CALL05 + CALL09 pins reviewed + native legs (§P1-m3.7) green; CALLN1–CALLN6 +
CALLN10 refuse as predicted (layers included); C-M3a observed failing loudly.
**m3b gate (BEFORE any m3c byte):** all of m3a re-green; CALL01/06A/06B/10 green natively (brief
bytes VERBATIM); CALLN7/CALLN8 predicted refusals; CALLN10 fixture now POSITIVE (arm deleted);
C-M3b loud.
**m3c gate:** all prior re-green; CALL07/08 green; CALLN9 refuses; C-M3c loud.
FROZEN regression (T1–T11, each OWN command): gate → `build/e54p1m3-reg-gate.log` FROZEN ALL HIT;
T3 220/11; mir_aot 32; cosmo 25; console 43; debug 23 (repo root); CF 83; fresh `_build-e54p1m3`
hist 122 sha == kept; T10 = NEW `tools/mir_aot_call_test.py` (measured count, controls loud inside);
T11 ZERO oracle, ledger 203/C380, config unstaged.

### P1-m3.13 Work order (successor contract — exact order)

1. **THIS COMMIT:** pre-registration §P1-m3 (explicit path `spec/lab-evidence/e2e54/PLAN.md`)
   BEFORE any source byte (PROTOCOL #1).
2. **m3a** in `ocaml/hir/mir_backend.ml` ONLY (+ the `declare` Formal routing if needed) → gates
   each OWN command (build → T1 → T2 → hir 220/11 → cmp ALL pins UNMOVED) → measured-first
   ADDITIVE `hir/mir-call-fixtures/CALL02–CALL05, CALL09, CALLN1–CALLN6, CALLN10.pli` +
   `hir/mir-call-expected/` pins → §P1-m3.7 native legs → C-M3a LOUD → commit explicit paths =
   **m3a gate CLOSED**.
3. **m3b** (§P1-m3.4) → same gates → CALL01/06A/06B/10 + CALLN7/CALLN8 measured-first; CALLN10
   deletion (fixture + pins removed as §P1-m3.9-2) → native → C-M3b LOUD → commit = **m3b gate**.
4. **m3c** (§P1-m3.5) → gates → CALL07/08 + CALLN9 → C-M3c LOUD → commit = **m3c gate**.
5. Runner `tools/mir_aot_call_test.py` WRITTEN TO §P1-m3.6/.7 (expected bytes COPIED from this
   section, NEVER from output) BEFORE its first run; run FROM REPO ROOT; fix RUNNER defects only;
   controls failing LOUDLY inside → commit explicit path.
6. FULL FROZEN regression T1–T11 each OWN command.
7. CLOSE: RESULTS §P1-m3 (m3a/m3b/m3c SEPARATELY + T-panel WITH values + deviations + matrix +
   reproduction + commit chain), `docs/architecture/backend-boundary.md` §7-10, dashboard row
   CLOSED, durables + guard attest → **STOP** — no next phase authorized without the OPERATOR.

### P1-m3.14 Complexity-stop thresholds and FORBIDDEN routes

STOP-and-attribute (exact reproducer) if: the pinned parser refuses ANY §P1-m3.1-2 proven shape at
a fixture; a per-func register/temp interaction forces a redesign (hop-2 scoping is PROVEN); any
pre-existing byte moves outside §P1-m3.9; a value cell's stack growth cannot be hoisted; a cosmo
leg needs a toolchain change. FORBIDDEN ever: weakening I1–I5; interprocedural value analysis;
early/nested `RETURN` in subsidiaries; arrays/`D_elem`; FILE streams; `PUT EDIT`; changing
`pli_console.c`/`console_check.c`/`mir2o.c`/`cosmo_link.sh`; touching lab/deps; re-pinning a
failing native test to its output; oracle runs. Later milestone bytes BEFORE its gate: FORBIDDEN.

### P1-m3.15 OPERATOR AMENDMENT (dated 2026-11-13; operator ruling on the hop-10 STOP-and-attribution: option (a) APPROVED; applied in session 01a1cb2b at HEAD `de41ac39`)

**Authority and limits.** The operator adjudicated the hop-10 contradiction (C1 CALL02/CALL04
E19 refusals; C2 CALLN1 layer) in favor of **option (a)**: THIS section amends the §P1-m3.6
fixture texts for CALL02 and CALL04 and the §P1-m3.6 negative-table CALLN1 prediction row. This
is an explicit authorization to amend the existing preregistration — it is **NOT** authorization
to weaken the numeric-safety laws I1–I5 (§P1-m3.11), to add interprocedural value analysis, or to
otherwise alter any binding law (§P1-m3.14 stays in force verbatim). P1-m3a remains OPEN until
every §P1-m3.12 gate passes under the amended contract. The original §P1-m3.6 texts and
determinations STAND IN THIS FILE AS HISTORY (retained above, not deleted); where they conflict
with this section, THIS section OVERRIDES them; nothing else in §P1-m3.0–.14 changes.

**Preserved evidence (hop 10 first-hand).** With the original texts, CALL02 and CALL04 refused
E19 at line 10 (reproducers kept in ignored `build/p1m3-scratch/g9/CALL02.stderr`,
`CALL04.stderr`); pre-existence of the refusing law was PROVEN by the entry-only scratch
`W100.pli` refusing the identical message class on the committed tree. **These E19 refusals are
recorded as VALID EVIDENCE of the conservative declared-window analysis (I1) behaving exactly as
designed — NOT compiler defects.** The §P1-m3.6 POSITIVE expectations for those two fixtures were
a pre-registration DESIGN ERROR: §P1-m3.2-6 seeds every callee formal at the FULL declared window
W(p) (no call-site knowledge crosses the procedure boundary), so `n + 1`/`m + 40` on a formal of
`FIXED BINARY(15,0)` is unprovable by construction, and §P1-m3.14 forbids the only alternatives.
CALLN1: the original row predicted HIR E07; measured is the PRE-EXISTING BACKEND E18 value-position
arm (committed `mir_backend.ml:297`; `pli80hir` admits the fixture rc 0). No compiler change is
authorized to force the original HIR-side diagnostic; the PREDICTION is what is corrected.

**Technical acceptance law (preserved; both facts distinct).** (1) A caller that knows its own
exact local value (`x = 51` in entry scope) can safely evaluate `x + 40` — proven at the caller's
own window facts; the amended CALL04 keeps this leg UNCHANGED. (2) A separately compiled callee
may NOT assume its formal `m` equals 51 (or any call-site value) — its environment seeds the
formal at FULL W(p) only. Neither fact may be silently collapsed into the other; the amendment
exercises (2) with window-provable `+ 0` arithmetic on the formal while keeping the ABI law
load-bearing.

**Amendment A1 — CALL02.pli (entry `call02`):** line 10 `t = n + 1;` is REPLACED by `t = n + 0;`.
This test **no longer claims nonzero arithmetic on the callee formal**; it still lowers a VOID
callee with a LOCAL reading a by-value formal. Binding amended text (CRLF+`^Z` via
`build/p1m2-scratch/mkpli.py`):

    call02: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 2;
       call side(4 + x);
       put list(x);
       return (x);
       side: procedure(n);
          dcl n fixed bin(15);
          dcl t fixed bin(15);
          t = n + 0;
       end side;
    end call02;

INDEPENDENT expected results (hand-derived here, unchanged by the amendment): x = 2; the actual
4 + 2 = 6 is passed BY VALUE; `side` computes t = 6 + 0 = 6 into its OWN LOCAL — x is UNTOUCHED;
`put list(x)` prints 2. Expected **stdout `2\n`, `driver-return=2`, native_check EXPECTED=2**,
rc 0.

**Amendment A2 — CALL04.pli (entry `chain`):** line 10 `t = m + 40;` is REPLACED by `t = m + 0;`.
The CALLER's own `x = x + 40` (line 5, entry scope, window-proven by law fact (1)) is UNCHANGED,
and the THREE-PROCEDURE chain entry→mid→leaf with the DEEPEST-CALLEE console `put list(d)` remains
MANDATORY coverage. Binding amended text:

    chain: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 51;
       call mid(x + 0);
       x = x + 40;
       return (x);
       mid: procedure(m);
          dcl m fixed bin(15);
          dcl t fixed bin(15);
          t = m + 0;
          call leaf(t + 0);
       end mid;
       leaf: procedure(d);
          dcl d fixed bin(15);
          put list(d);
       end leaf;
    end chain;

INDEPENDENT expected results (hand-derived here): x = 51; the actual 51 + 0 = 51 is passed by
value to `mid`; `mid` computes t = 51 + 0 = 51; the by-value copy 51 goes to `leaf`, which PUTs it
(**stdout `51\n`** — CHANGED from the original `91\n`); `leaf` cannot write d's actual; the caller
computes x = 51 + 40 = 91 and returns it — **PL/I return remains 91** (`driver-return=91`,
native_check EXPECTED=91), rc 0. The original `91\n` expectation and its "91 coincidence" note are
SUPERSEDED by this paragraph and kept only as §P1-m3.6 history.

**Amendment A3 — CALLN1 row (PROGRAM TEXT UNCHANGED):** the §P1-m3.6 negative-table prediction
becomes **E18, layer BACKEND**, measured VERBATIM `HIR-E18: line 3: MIR backend: a value-position
call is outside the native subset (brief §3)`; the refusal-totality laws (rc 2, ZERO stdout, no
`-o` artifact, ×2 fresh processes) are unchanged. The original prediction and its falsification
are preserved above, in §P1-m3.10 item 7 and in LEARNINGS § hop 10.

**Gate reading.** §P1-m3.12's `CALL02–CALL05 + CALL09` clause is evaluated against THE AMENDED
TEXTS (A1/A2) and the amended CALLN1 row (A3). Pins for the two amended fixtures are
MEASURED-FIRST from the amended fixtures, reviewed line-by-line against §P1-m3.2 BEFORE any `cp`,
and each pin's MEANING is reviewed against this amended independent contract — a pin is never
accepted merely because it matches observed output. No DR oracle is involved anywhere in this
amendment (backend engineering only; ledger stays 203 headers / C380).

### P1-m3.16 OPERATOR AMENDMENT B (dated 2026-11-11 by the git/system clock — the date of the m3a close chain through HEAD `021a496c`; operator brief **E2E-54/P1-m3b APPROVED, P1-m3c NOT authorized**; issued by the OPERATOR and applied verbatim in the m3b session BEFORE any m3b source or fixture byte, PROTOCOL #1)

**Authority and limits.** The operator authorized P1-m3b (genuine by-reference parameter
passing) on top of the CLOSED m3a gate (`2be30a9c`, checkpoint g764) and, in the SAME brief,
amended three points of the §P1-m3 pre-registration BEFORE implementation: **B1** (CALL10
numeric safety), **B2** (C-M3b control direction), **B3** (CALLN10 transition procedure).
This section OVERRIDES §P1-m3.6 (CALL10 text and expectations), §P1-m3.8 (the C-M3b
procedure) and §P1-m3.9 item 2 / §P1-m3.13 step 3 (the CALLN10 migration mechanics) where
they conflict; the original blocks STAND ABOVE AS HISTORY (PROTOCOL #2 — nothing deleted).
NOTHING here weakens I1–I5 (§P1-m3.11) or §P1-m3.14; interprocedural value analysis, early/
nested subsidiary RETURN, arrays, FILE streams and m3c bytes remain FORBIDDEN. The HOME-PASS
ABI of §P1-m3.2 is unchanged in shape: by-ref rides the caller entry-hoisted home `h<sid>`
exactly as §P1-m3.2-6 already specified.

**Why the original predictions were not valid.**

- **B1 (CALL10).** The original §P1-m3.6 text ends

      call clob(20, 40);
      x = x + y;
      return (x);

  and pre-registered stdout `7\n9\n`, `driver-return=9`. That expectation CONTRADICTS the
  plan's own numeric law: by §P1-m3.2-8/I2 the call `clob(x, x)` passes `x` by reference, so
  the caller env MUST widen `x` to the FULL declared window W(15) = [-16383, 16383] after the
  call (the caller cannot know what the callee wrote); `y = 2` is preserved (by-value, I3).
  Then `x + y` can reach 16385, OUTSIDE the declared window of `FIXED BINARY(15,0)`, so the
  FROZEN window law I1 refuses `x = x + y;` with HIR-E19 — exactly the mechanism whose VALID
  evidence §P1-m3.10 item 7 and §P1-m3.15 preserve for CALL02/CALL04. The pre-registered
  positive was therefore UNSATISFIABLE by construction; the §P1-m3.10 item 5 note ("derives
  `7\n9\n` dr 9") is superseded. The only honest fixes were an interprocedural narrowing
  (FORBIDDEN, §P1-m3.14) or a text amendment (approved).
- **B2 (C-M3b).** The original §P1-m3.8 procedure — replace the FIRST (by-reference) actual
  `h<sid>` in the CALL06B call row with the caller's value cell — does NOT produce the
  predicted `7\n7\n`: BOTH formals would then designate the value cell `hv<k>` holding the
  pre-call copy; the callee `a = 7; put list(b);` would print the cell's 7 and the caller's
  untouched `x = 2` would print 2 — stdout `2\n7\n`, IDENTICAL to the correct bytes. The
  control as written was VACUOUS. The inverse mutation (below) is the non-vacuity fix.
- **B3 (CALLN10).** §P1-m3.9-2/§P1-m3.13-3 said the transitional negative is "DELETED" and
  "re-measured as POSITIVE" without naming the mechanics; the operator now prescribes them
  (retirement with provenance, source survival, auditable mapping) below.

**Amendment B1 — CALL10.pli (entry `mixmod`), numeric-safe second observation.** The single
statement `x = x + y;` (line 9 of the original) is REPLACED by `put list(x);`. NOTHING else
changes: `dcl y fixed bin(15);` and `y = 2;` REMAIN (the amended program no longer READS y;
an unused-but-initialized local is legal and registers normally). Binding amended text
(CRLF+`^Z` via `build/p1m2-scratch/mkpli.py`):

    mixmod: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       dcl y fixed bin(15);
       x = 2;
       y = 2;
       call clob(x, x);
       put list(x);
       call clob(20, 40);
       put list(x);
       return (x);
       clob: procedure(a, b);
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          b = 3;
          a = 7;
       end clob;
    end mixmod;

INDEPENDENT derivation (PL/I semantics only; no call-site value crosses a boundary):
site 1 `clob(x, x)` designates `x` TWICE — ONE home `h(x)`; inside the callee `b = 3` then
`a = 7` both write that single cell, so x = 7; the first `put list(x)` prints **7**. Site 2
`clob(20, 40)` passes two INDEPENDENT value cells; the callee writes ONLY the cells — caller
`x` and `y` are UNTOUCHED (by-value write isolation, x8 PROVEN); the second `put list(x)`
prints the still-current 7. `return (x)` is window-proved because the abstract env carries
`x : W(15)` after site 1 (NOT the point 7 — the amendment forbids propagating the first
call's concrete result into the environment; only the runtime cell holds 7) and W(15) ⊆ the
result window of `returns(fixed bin(15))`. **Amended expectation: stdout `7\n7\n`,
`driver-return=7\n`, process rc 0; glibc `native_check -DEXPECTED=7` EXEC rc 0.** The
program validates MIXED PASSING MODES at one callee with NO interprocedural value analysis.

**Amendment B2 — C-M3b (home vs value), inverse mutation.** On a DISPOSABLE copy of the
MEASURED CALL06B pin under `build/p1m3-scratch/` ONLY (never a pin, never the compiler,
never `hir/mir-call-fixtures/CALL06B.pli` or its accepted bytes): replace the SECOND call
argument — the by-VALUE cell address `hv<k>` — in the single call row with the FIRST
argument's by-reference HOME address:

    original:  call pc<n>, pli80_alias, h<x>, hv<m>
    corrupted: call pc<n>, pli80_alias, h<x>, h<x>

The corrupted callee sees BOTH formals designating the caller variable `x`: `a = 7` writes
x := 7 through the shared home and `put list(b)` reads the SAME cell, printing 7; the caller
then prints x = 7. **Independently expected corrupted stdout: `7\n7\n`** — which MUST FAIL
LOUDLY against the original, correct CALL06B expectation `2\n7\n` (the exact discriminator:
`7\n7\n` is precisely what a home-vs-value ABI bug would produce). The corrupted program
MUST genuinely `mir2o`, link and EXECUTE (rc 0, `driver-return=7\n`) — the LOUD failure is
the stdout mismatch against the pinned contract, not a toolchain error. §P1-m3.8's C-M3b
bullet is superseded by THIS paragraph; the original stands above as history.

**Amendment B3 — CALLN10 transition (concrete migration procedure).** The m3a-only refusal
arm ("by-reference actual argument N of call to <key> is admitted at milestone P1-m3b") and
its negative expectation pins are RETIRED at m3b as follows; the negative diagnostic MUST
NOT remain an accepted m3b result:

1. The two m3a NEGATIVE pins `hir/mir-call-expected/CALLN10.rc` and
   `hir/mir-call-expected/CALLN10.stderr.txt` are `git rm`'d (explicit paths) in the m3b
   implementation commit. Historical provenance: they were MEASURED-FIRST at the m3a gate
   commit `2be30a9c` (registered in §P1-m3.6 as the m3a TRANSITIONAL discriminator and
   pre-registered for retirement in §P1-m3.9 item 2); their full bytes remain forever in the
   git history of that commit, and this section names the retirement.
2. The SOURCE FIXTURE `hir/mir-call-fixtures/CALLN10.pli` SURVIVES UNCHANGED under the same
   id — the auditable mapping is: same fixture name, retired negative pins (history at
   `2be30a9c`), NEW positive pin `hir/mir-call-expected/CALLN10.mir` (measured-first) plus
   the full §P1-m3.7 native legs recorded in this milestone's evidence. The validation cannot
   silently disappear: a successor that deletes either side sees the panel fail.
3. The ORIGINAL source text (verified first-hand at the m3b start, byte-for-byte the §P1-m3.6
   binding block) must COMPILE AND EXECUTE successfully under m3b. Independent derivation:
   `x = 2;` `call clob2(x, x)` passes ONE home twice; `clob2` writes `a = 7` through the
   shared cell, so caller x = 7; no console statement exists; `return (x)` returns 7.
   **Positive expectation: stdout EMPTY, `driver-return=7\n`, process rc 0; glibc
   `native_check -DEXPECTED=7` EXEC rc 0.** (A new m3b negative covering the by-ref family
   is NOT added: see the D_elem paragraph — that guard arm is UNREACHABLE end-to-end and is
   recorded, like §P1-m3.10 items 3/4, with NO invented fixture.)

**D_elem (array-element reference actual) — guard arm + reachability law.** §P1-m3.2-6's
`D_elem` E18 refusal arm is implemented; end-to-end it is UNREACHABLE: the backend's frozen
`declare`/`bin_p` law refuses EVERY array declaration (`dcl arr fixed bin(15) (10);` ⇒
HIR-E18 "type … is outside the native integer subset") and HIR itself refuses array-element
assignment (P1-a1/E18-class), so NO reachable program can present an array element as a
by-reference actual. PROVEN first-hand in the m3b session (scratch probe recorded here and
in LEARNINGS, never fitted). The m3b NEGATIVE panel therefore exercises: CALLN7 (multi-proc
`-g` E18 — already-pinned law, verified live against the NEW `CALL01.pli` fixture), CALLN8
(uninitialized by-ref E19 — the NEW pinned negative, §P1-m3.6 text), the retained m3a
negatives CALLN1–CALLN6 (unchanged), and the D_elem arm by CODE INSPECTION plus the array-
declaration refusal measured as the earlier-layer witness (deviation class of §P1-m3.10
items 3/4, recorded; runner greps the static `D_elem` arm).

**Implementation addendum (loop hoists — pre-registered, not a law change).** §P1-m3.2-6
requires value cells/homes hoisted at ENTRY, "never at the call site (no per-iteration stack
growth)" — §P1-m3.14 makes a non-hoistable cell a STOP. The §P1-m2.3 verification pass over
a loop body rewinds `insns`/`tmp_n`/`cf_n` but NOT the `hv` allocator, so a `Call_s` inside a
verified loop body would DOUBLE-ALLOCATE dead value cells (a latent m3a defect NO m3a fixture
reaches — recorded, never fitted). m3b rewinds the `hv` allocator and the `hv` cell list in
that discarded pass too (rewind-on-discard idiom); every loop body in the panel is then
hoist-clean by construction. Also pre-registered (conservative refusals, I2/I4): (R1) a loop
BODY that passes a variable by reference DROPS that sid from the post-loop env (drop-not-
inherit — a callee write in any iteration is invisible to the header env) unless the body
itself re-initializes it; (R2) passing the loop INDUCTION VARIABLE by reference inside the
body REFUSES the counted-loop shape — the step proof cannot hold; (R3) the per-proc HOME set
is discovered by a pre-body scan, so one home per designated sid exists BEFORE the first
lowered instruction and `v<sid>` never appears in that func's locals (the var has NO
register, §P1-m3.2-6 verbatim).

**Gate reading (m3b, under B1–B3).** §P1-m3.12's m3b gate is evaluated as: all of m3a
re-green (fixtures and pins of the CLOSED gate UNMOVED — including the seven m3a negative
pins, CALLN10's TWO negative pins EXCEPTED as retired per B3 with the provenance recorded
here and accounted in the m3b commit); CALL01 `5\n4\n` dr 4; CALL06A `7\n` dr 7; CALL06B
`2\n7\n` dr 7; **CALL10 (B1) `7\n7\n` dr 7**; **CALLN10 (B3) positive EMPTY dr 7**; every
positive through the full §P1-m3.7 panel (×2 determinism, reviewed pins, mir2o, glibc, cosmo
tiny static, nm, static laws); CALLN7/CALLN8 refuse as predicted (rc 2, ZERO stdout, NO
artifact, ×2); **C-M3b (B2) fails LOUDLY against `2\n7\n` with corrupted stdout `7\n7\n`**;
the FROZEN §P1-m3.9 falsifier panel byte-UNMOVED. No m3c byte. Zero oracle (backend
engineering; ledger stays 203 headers / C380).

### P1-m3.17 OPERATOR AMENDMENT C (dated 2026-11-11 by the git/system clock — the m3c chain; operator brief **"DRPLi — E2E-54/P1-m3c: Operator Amendment D and Gate Completion"**, §2 "Commit operator amendments C and D FIRST" + §4 "m3c validation panel"; amendments **C and D APPROVED**, m3c implementation+validation **APPROVED**, aggregate runner and overall §P1-m3 CLOSE **NOT AUTHORIZED**; issued by the OPERATOR and applied verbatim in the m3c session BEFORE any m3c source or fixture byte, PROTOCOL #1)

**Authority and limits.** The operator adjudicated the hop-14 STOP-and-attribution (brief §3
admission vs brief §6/§1/§7 + §P1-m3.12 "all m3a negatives still valid", irreconcilable at CALLN1)
and, in the SAME brief, amended the two numeric-unprovable m3c positives **before** implementation.
This section OVERRIDES §P1-m3.6 (the CALL07 and CALL08 program texts and their expected bytes) and
§P1-m3.8 (the **C-M3c** procedure) where they conflict; the original blocks STAND ABOVE AS HISTORY
(PROTOCOL #2 — nothing is deleted or edited). The m3c admission scope §P1-m3.5 and the HOME-PASS
ABI law §P1-m3.2/.7 are **NOT** changed by this amendment — the operator's §3 wording ("whole-RHS
`Assign(D_var sid, Call_e ...)`", "final `Return(Some(Call_e ...))`", all actuals `A_value`, nested
`Call_e` / `Convert` / PUT / condition refusals, recursion refusals, result interval the callee's
full declared `W(p)`, no caller-constant propagation, no callee-result narrowing, pure-argument
`Pure` classification is NOT an interprocedural purity guarantee) is exactly the law already
pre-registered there, so no law text moves. Invariants I1–I5 (§P1-m3.11) are NOT weakened and §P1-m3.14
stays in force verbatim: **interprocedural value analysis/narrowing remains FORBIDDEN**. No DR oracle
is involved (backend engineering; ledger stays 203 headers ending C380).

**Why the original §P1-m3.6 positives were unsatisfiable (measured first-hand, reproducers kept).**
The original texts are mechanically re-extracted from the §P1-m3.6 blocks above and re-measured in
the m3c chain (ignored scratch only: `build/p1m3-scratch/g15/ORIG07.pli` 367 B,
`build/p1m3-scratch/g15/ORIG08.pli` 276 B — each byte-verified EQUAL to its §P1-m3.6 binding block,
CRLF+`^Z`; refusals re-run in the landing session into `build/p1m3-scratch/g16/`):

- on the COMMITTED pre-m3c backend both refuse EARLIER, at the frozen backend value-position arm:
  `HIR-E18: line 3: MIR backend: a value-position call is outside the native subset (brief §3)`
  (ORIG07) and the same message at `line 4` (ORIG08), rc 2, ZERO stdout, NO `-o` artifact;
- under the §3 admission (the hop-14 prototype backend) the ORIGINAL CALL07 refuses
  `HIR-E19: line 11: binop '+' on operands proved within [-16383,16383] and [-16383,16383] can reach
  [-32766,32766], leaving the declared-precision window [-16383,16383] of FIXED BINARY(15,0);
  overflow behaviour is profile-UNKNOWN and is never assumed (brief §4)` and the ORIGINAL CALL08
  refuses `HIR-E19: line 8: binop '+' on operands proved within [-16383,16383] and [1,1] can reach
  [-16382,16384], leaving the declared-precision window [-16383,16383] of FIXED BINARY(15,0);
  overflow behaviour is profile-UNKNOWN and is never assumed (brief §4)`.

The mechanism is the plan's own law, not a defect: §P1-m3.2-6 seeds every callee formal at the FULL
declared window `W(p)` with NO call-site knowledge crossing the boundary (I3), so `t = a + b + c` and
`t = n + 1` on `FIXED BINARY(15,0)` formals are unprovable **by construction** — the identical
falsification class preserved by §P1-m3.15 (A1/A2) and §P1-m3.16 (B1). The only two honest routes were
interprocedural narrowing (FORBIDDEN, §P1-m3.14) or a fixture-text amendment (approved here). The
original expectations (`6\n` dr 6; `42`/`EXPECTED=42`) are SUPERSEDED by C1/C2 below and kept as history.

**Amendment C1 — CALL07.pli (entry `thrice`, callee `pick3`): whole-RHS `Assign(D_var, Call_e)` with
THREE by-value actuals and console output from the CALLEE.** Binding text VERBATIM from the operator
brief (CRLF+`^Z` via `build/p1m2-scratch/mkpli.py`, generated MECHANICALLY from this block quote and
byte-verified against it):

    thrice: procedure returns(fixed bin(15));
       dcl z fixed bin(15);
       z = pick3(1, 2, 3);
       put list(z);
       return (z);
       pick3: procedure(a, b, c) returns(fixed bin(15));
          dcl a fixed bin(15);
          dcl b fixed bin(15);
          dcl c fixed bin(15);
          dcl t fixed bin(15);
          put list(a);
          put list(b);
          t = c;
          return (t);
       end pick3;
    end thrice;

INDEPENDENT derivation (PL/I semantics only; no call-site value crosses the boundary): the entry
evaluates the three literal actuals left to right (1, 2, 3 — all `A_value`, so §P1-m3.5 admits the
whole-`Call_e` RHS) and calls `pick3`; inside the callee `put list(a)` prints **1** and `put list(b)`
prints **2** — these are observable console effects of the CALLEE and MUST appear before the caller's
own output (left-to-right / callee-before-caller-return order, §P1-m3.2); `t = c` is a pure COPY of
the third formal (which the callee env seeds at the full `W(15)`) into the callee's own local, so NO
arithmetic is proved and I1 is trivially satisfied; `return (t)` ends the value callee at its final
statement (law 2d) and the `Call_e` node carries interval `W(15)` (§P1-m3.2-7 — no narrowing); the
caller assigns that result to `z` and `put list(z)` prints **3**; `return (z)` returns 3 and `W(15) ⊆`
the entry's declared result window, so the entry `Return` is window-proved. **Expected: stdout
`1\n2\n3\n`, `driver-return=3\n`, process rc 0; glibc `native_check -DENTRY=pli80_thrice
-DEXPECTED=3` EXEC rc 0; cosmo-tiny console leg EXACTLY those bytes.** This fixture is the m3c
whole-RHS positive AND the observable-console-effect-in-a-subsidiary-with-value-call positive.

**Amendment C2 — CALL08.pli (entry `wret`, callee `identity`): whole-`Return` `Call_e`, result
returned without ever being stored.** Binding text VERBATIM from the operator brief:

    wret: procedure returns(fixed bin(15));
       dcl x fixed bin(15);
       x = 41;
       return (identity(x + 0));
       identity: procedure(n) returns(fixed bin(15));
          dcl n fixed bin(15);
          dcl t fixed bin(15);
          t = n + 0;
          return (t);
       end identity;
    end wret;

INDEPENDENT derivation: the actual is the EXPRESSION `x + 0`, evaluated in the CALLER env where `x` is
proved 41 (the caller-side fact preserved in §P1-m3.15 — the caller may use its own window facts), and
is passed `A_value`; `identity` seeds `n` at FULL `W(15)` and computes `t = n + 0`, whose sum interval
`[-16383,16383] + [0,0] = [-16383,16383]` stays inside `W(15)` — window-provable with NO knowledge of
the call site; `return (t)` yields interval `W(15)`; the entry's `Return (Some Call_e)` is the second
admitted §P1-m3.5 shape (whole expression, value callee as the FINAL statement). No `put` statement
exists in either procedure ⇒ **stdout EMPTY**, and the returned value is `41 + 0 + 0 = 41`.
**Expected: stdout EMPTY, `driver-return=41\n`, process rc 0; glibc `native_check
-DENTRY=pli80_wret -DEXPECTED=41` EXEC rc 0; cosmo-tiny console leg EMPTY stdout +
`driver-return=41\n`.** Together C1/C2 pin BOTH admitted shapes (whole-RHS Assign, whole-Return) plus
the CALL05/CALL08 void-vs-value tail pair already claimed by §P1-m3.5.

**Amendment C3 — C-M3c REDEFINED (result corruption; supersedes the §P1-m3.8 C-M3c bullet, whose
`-DEXPECTED=6` belongs to the superseded text).** On a DISPOSABLE copy of the MEASURED, AMENDED
CALL07 `.mir` pin under `build/p1m3-scratch/` ONLY (never a pin, never the compiler, never
`hir/mir-call-fixtures/CALL07.pli`), perturb ONLY the value the callee returns: insert
`add <rt>, <rt>, 1` immediately BEFORE the callee `pick3`'s final `ret <rt>` (`<rt>` = that function's
result register), i.e. returned value 3 → 4. The mutated artifact MUST then
(1) `mir2o -f` rc 0 — the MIR stays syntactically and semantically VALID (a control that fails only
because the corrupted MIR is rejected does **NOT** count and is itself a falsifier of non-vacuity);
(2) genuinely LINK and EXECUTE — predicted corrupted observations: console stdout `1\n2\n4\n` with
`driver-return=4\n`, and the glibc driver run with the **UNCHANGED** `-DEXPECTED=3` returning
**rc 1** (the value 4 ≠ 3) — the native panel step for the perturbed copy therefore fails LOUDLY.
A control that executes 3 is VACUOUS (the suite fails). If the pinned parser refuses the immediate
form of `add`, the measured deviation is RECORDED and the equivalent register form is used — never a
silent fit.

**Gate reading (m3c positives, amended).** §P1-m3.12's clause "CALL07/08 green" is evaluated against
THESE texts and THESE bytes. Pins are MEASURED-FIRST, every MIR line reviewed against §P1-m3.2/.5
BEFORE any `cp`, determinism ×2 in fresh processes, and each pin's MEANING reviewed against this
independent contract — a pin is never accepted merely because it matches observed output. No m3c byte
exists in the repository before this section is committed (PROTOCOL #1).

### P1-m3.18 OPERATOR AMENDMENT D (dated 2026-11-11 by the git/system clock; same operator brief as §P1-m3.17 — §2 "Amendment D — CALLN1 migration" + §5 "Frozen regressions"; **APPROVED** by the OPERATOR and applied verbatim in the m3c session BEFORE any m3c source or fixture byte, PROTOCOL #1)

**Authority and limits.** The operator explicitly authorizes the transition of **CALLN1** from an
m3a/m3b NEGATIVE fixture into an m3c POSITIVE fixture, and names it an **explicitly authorized
exception** to the frozen m3a/m3b negative-pin requirements of §P1-m3.9/§P1-m3.12/§P1-m3.15/§P1-m3.16.
ALL other frozen pins stay byte-UNMOVED: every `hir/mir-expected/*`, `hir/mir-cf-expected/*`,
`hir/mir-debug-expected/*`, the CT2/debug `.o` shas, the suite counts (mir_aot 32, cosmo 25, console
43, debug 23, CF 83), the gate counts, and EVERY negative pin except the two files retired here
(CALLN10's two pins were already retired at m3b under §P1-m3.16 B3 — accounted, not re-touched).
The brief FORBIDS the alternative: **no artificial special case may be introduced to keep rejecting
CALLN1** — the general §P1-m3.5/§3 admission is implemented and CALLN1 lands as a positive because it
is exactly the admitted shape. This is NOT authorization for the aggregate runner
`tools/mir_aot_call_test.py`, for the overall §P1-m3 CLOSE, for any oracle call, or for weakening
I1–I5/§P1-m3.14.

**Prediction and refusal history (PROTOCOL #2 — preserved, not rewritten).**
1. §P1-m3.6 registered CALLN1 as a NEGATIVE predicted `E07 procedure pv used as a value: P0 admits
   calls only`, layer **HIR**, milestone "all".
2. §P1-m3.15 **Amendment A3** corrected that PREDICTION (program text unchanged) to layer **BACKEND**,
   measured VERBATIM `HIR-E18: line 3: MIR backend: a value-position call is outside the native
   subset (brief §3)`.
3. The two negative pins were MEASURED-FIRST and landed in the m3a GATE commit **`2be30a9c`** and have
   been re-measured first-hand at every later milestone (hop-14, hop-15 and the landing session start:
   rc 2, stderr byte-equal to the pin, ZERO stdout, NO `-o` artifact).
4. That refusal was CORRECT for m3a and m3b — §P1-m3.5 admits `Call_e` in value position only at m3c.
   When the operator authorized the m3c admission (brief §3), CALLN1's program
   `y = pv(1);` became exactly `Assign (D_var y, whole Call_e)` with all-`A_value` actuals, so the
   §3 admission and the "all m3a negatives still valid" clause became MUTUALLY UNSATISFIABLE; hop 14
   STOPped and attributed the contradiction (prototype compiled CALLN1 rc 0 and mir2o produced a
   1408 B object — the negative pin was PROVABLY DEAD), and the operator resolved it by THIS
   retirement rather than by a special case. Mechanics follow the §P1-m3.16 B3 precedent.

**Retirement mechanics (executed in the m3c IMPLEMENTATION commit, i.e. AFTER the commit that lands
this section).**
1. `git rm hir/mir-call-expected/CALLN1.rc hir/mir-call-expected/CALLN1.stderr.txt` — explicit paths;
   historical provenance commit **`2be30a9c`** (with §P1-m3.15 A3's prediction correction); the full
   bytes remain forever in that commit's git history and this section names the retirement.
2. The SOURCE FIXTURE `hir/mir-call-fixtures/CALLN1.pli` SURVIVES **BYTE-IDENTICAL** and unchanged in
   meaning as an m3c POSITIVE input: 213 B, sha256
   `33d248d05428397735caeb8de6834b7a04dc764e38225204439796c5be6f376a` (verified first-hand at the m3c
   baseline and re-verified at every gate; any change to this file is a STOP-and-attribute).
3. NEW measured-first positive pin `hir/mir-call-expected/CALLN1.mir`, every line reviewed against
   §P1-m3.2/.5 BEFORE the `cp`, determinism ×2 in fresh processes, NEVER hand-written.
4. Auditable mapping (same idiom as B3): same fixture name, retired negative pins (history
   `2be30a9c`), new positive pin plus the full §P1-m3.7 native legs recorded in this milestone's
   evidence — a successor that deletes either side sees the panel fail; the validation cannot silently
   disappear.

**Independent positive expectation (hand-derived HERE, BEFORE any run).** Program (§P1-m3.6 text,
unchanged): entry `pval` assigns `y = pv(1);` and returns `y`; callee `pv(n)` returns its formal.
The literal actual `1` is `A_value`; the callee's `return (n)` reads the formal through
`i64:(v<sid>)` and the value travels ONLY through the caller-local MIR result register `r<k>`; the
`Call_e` node carries interval `W(15)` (§P1-m3.2-7), so `y` keeps `W(15)` after the call (I3/I4: NO
caller-side narrowing to the point 1) and the entry's `return (y)` is window-proved inside `W(15)`.
No `put` statement exists ⇒ **stdout EMPTY**; the PL/I value returned is 1. **Expected: stdout EMPTY,
`driver-return=1\n`, process rc 0; glibc `native_check -DENTRY=pli80_pval -DEXPECTED=1` EXEC rc 0;
cosmo-tiny console leg EMPTY stdout + `driver-return=1\n`; static laws and `nm T pli80_pval` +
subsidiary `t pli80_pv`.**

**Gate reading (m3c, complete).** §P1-m3.12's m3c gate is evaluated as: all m3a/m3b re-green with
their pins byte-UNMOVED (m3a positives CALL02–05/CALL09; m3b positives CALL01/06A/06B/10 + the B3
positive CALLN10; negatives CALLN2–CALLN6, CALLN7, CALLN8) — **the CALLN1 negative pair EXCEPTED as
retired here, with provenance accounted above**; NEW positives CALL07 (C1), CALL08 (C2), CALLN1 (D)
green through the FULL §P1-m3.7 panel (HIR admission, ×2 determinism, reviewed measured-first pins,
mir2o, glibc ×2, cosmo-tiny ×2, static laws, `nm`); NEW negative CALLN9 refuses **E18 BY NAME** at the
nested-value-call arm (rc 2, ZERO stdout, NO artifact, ×2; the whole-RHS/whole-Return admission must
NOT admit `thrice3(1, 2, 3) + 5`); **C-M3c (C3) fails LOUDLY** while producing a valid, linkable,
executing artifact; the FROZEN §P1-m3.9 falsifier panel byte-UNMOVED. Zero oracle; ledger 203 headers
ending C380; `handoff.config.json` never staged; no push.

### P1-m3.19 Dashboard update

| slice | status | notes |
|---|---|---|
| P1-m3 | **CLOSED 2026-11-13** (hops 1–18 + close session; m3a `2be30a9c`, m3b `1394f074`, m3c `5d8d2a4a`, runner `eb1031a9` rc 0 **86 measured checks**) | native procedure calls GREEN end-to-end: HOME-PASS ABI (callee formals via `i64:(v<sid>)`, `A_reference` → caller entry-hoisted `alloca h<sid>,8` home with visible aliasing, `A_value` → per-slot `hv<k>` cells), callee-first post-order assembly with the entry LAST and ONE `export`, monotone post-call widening to `W(declared)`, `Call_e` only as whole-RHS/whole-`Return` with `W(ret-p)` and NO interprocedural narrowing; 13 positives EXECUTED byte-exactly on BOTH glibc and cosmo-tiny legs ×2 fresh, 8 negatives pinned by named refusal and LAYER; C-M3a/C-M3b/C-M3c all observed failing LOUDLY inside the committed runner; four operator amendments (A/B/C/D) each committed to the PLAN before the byte it authorized, two negative pairs retired with named provenance (the only artifacts that moved); FULL FROZEN regression ALL HIT (gate 1328/1328-190/190-9/9-149 rows 0/0-census 16/0/25/0-prose 5, hir 220, mir_aot 32, cosmo 25, console 43, debug 23, CF 83, DWARF pins UNMOVED, fresh build hist 122 sha==`172595d5…`, ledger 203/C380, T2 clean); RESULTS §P1-m3 + arch §7-10; **STOP — no next phase authorized without the OPERATOR** |

## §P2-DIFF-1 — Pre-registration: differential behavioral validation of the 8080 and native MIR backends (committed BEFORE any pilot fixture, manifest or runner byte)

**Operator brief:** E2E-54/P2-DIFF-1, authorized 2026-11-13 (the brief text is NOT stored in the
repository; the original §1–§10 are reproduced VERBATIM in `LEARNINGS.md` § "E2E-54/P2-DIFF-1
pre-registration hop"; the 2026-11-13 OPERATOR REFINEMENT of the pilot — approved after the
operator's independent inspection of the committed fixtures — is recorded in §P2-DIFF-1.2 below
and is the binding pilot list). This section is the PROTOCOL #1 pre-registration: every
expectation below is derived from the PL/I SOURCE TEXT by hand, BEFORE any pilot execution; NO
expectation is read back from any compiler's generated code or runtime output.

**This is an integration and behavioral-validation campaign, NOT a compiler-development campaign.**
No compiler source, no MIR/ABI, no golden, no claims-ledger byte is modified. The original Digital
Research `PLI.COM` compiler is NEVER executed (ZERO oracle; the ledger stays 203 headers ending
C380). The historical LINK-80, PLILIB.IRL and the CP/M simulator ARE authorized and are the
execution substrate of the historical lane; they are NOT the DR compiler oracle and every report
must say so.

### P2-DIFF-1.0 Scope, objective and the two lanes

Objective: a reproducible and falsifiable demonstration of ACTUAL cross-backend behavioral
agreement or disagreement on a precisely defined common observable — the complete ordered
program-console output of one and the same PL/I source program, executed by two real toolchains:

* **8080 lane (historical execution substrate):** `pli80c.exe -d <fixture> → .REL` → historical
  `LINK-80` 1.31 + `PLILIB.IRL` → `.COM` → `cpmsim` under the documented CP/M prompt protocol.
* **Native lane:** `pli80mir.exe --export <entry> <fixture> → .mir` (pinned bytes) →
  `build/p1m0-deps/mir2o -f` → genuine `ET_REL` x86-64 object → pinned Cosmopolitan `tiny` static
  link with `tools/mir_aot/pli_console.c` + `tools/mir_aot/console_check.c` → native ELF execution.

Both lanes execute the SAME committed source bytes (SAME-SOURCE, §P2-DIFF-1.2). No new PL/I
fixtures are authorized; the four sources below are reused byte-for-byte as committed.

### P2-DIFF-1.1 Measured facts on which this pre-registration rests (all first-hand, prior hops)

1. FROZEN baseline (baseline hop, 2026-11-13, each command its OWN rc): gate 1328/1328 — 190/190 —
   9/9 — coverage 149 rows 0/0 — census 16/0/25/0 — prose 5; hir 220; mir_aot 32; cosmo 25;
   console 43; debug 23; CF 83; call 86; ledger 203/C380; compiler sha
   `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281`.
2. 8080-COMPILE feasibility sweep (baseline hop): every pilot source compiles with `pli80c -d`
   rc 0 — CF06 256 B (code 54/data 2), CALL04 256 B (97/16), CALL06B 384 B (94/12), CALL07 384 B
   (117/16). **This is COMPILE-stage evidence only. LINK and RUN on CP/M are MEASURED ONLY for
   CALL06B** (recon probe: `pli80c -d` → LINK 1.31, `parse_undefined` EMPTY on the FULL segment,
   CODE 1834 / DATA 01CF / COMMON 00E6 → `CALL06B.COM` → cpmsim run, console region
   `        2         7^M` before the `D>` prompt). **CF06, CALL04 and CALL07 have NO committed
   LINK-80 or CP/M execution witness — their historical executability is a hypothesis of this
   pilot, not a claim.**
3. Native lane: all four sources carry committed `.mir` pins consumed by the GREEN runners
   (`hir/mir-cf-expected/CF06.mir`, `hir/mir-call-expected/CALL04.mir`, `CALL06B.mir`,
   `CALL07.mir`); the native console bytes were pre-registered in §P1-m2.5 and §P1-m3.6 (as
   amended) and executed ×2 there: CF06 `0\n1\n2\n`, CALL04 `51\n`, CALL06B `2\n7\n`, CALL07
   `1\n2\n3\n`.
4. CP/M toolchain availability verified first-hand (pre-registration hop): `oracle/linkrun.py`
   imports, `SIM` = `/home/john/pli/cpm/z80pack/cpmsim/cpmsim` EXISTS, all four DR tools
   (`LINK.COM LIB.COM RMAC.COM PLILIB.IRL`) in `artefacts/`, both boot seeds present.
5. 8080 console format law (README §6 + [C352]): FIXED numeric `PUT LIST` items print in a
   10-position right-justified field; items of ONE statement are separated by one blank; separate
   `put list(...)` statements do NOT line-terminate; the exit chain appends EXACTLY ONE final
   newline. Native console: `pli_console_put_i64` prints plain decimal, `pli_console_put_nl` closes
   every PUT statement (one item per line); the `driver-return=<v>` diagnostic goes to the
   driver's **stderr** — stdout is the program's own output alone.
6. Input-channel asymmetry (baseline hop): the two lanes' `get` channels differ (plain stdin vs
   PLILIB `?SYSIN` with a one-`^Z` script). **Every pilot case is GET-free** — no input stream
   exists on either lane, so no channel difference can enter the comparison.

### P2-DIFF-1.2 Feasibility classification and the pilot history (including the operator refinement)

The brief's three classifications: **SAME-SOURCE** (identical source bytes on both lanes),
**SHARED-CORE** (two wrappers around an identical core, compared by construction),
**NOT-COMPARABLE** (no demonstrated common observable). Never merged into one undifferentiated
"parity PASS".

The ORIGINAL proposal (5 cases, pre-refinement): D01 M02, D02 CF06, D03 CALL02, D04 CALL06B,
D05 CALL07. The OPERATOR REFINEMENT (2026-11-13, APPROVED) changes two entries:

* **D01 = M02 (`hir/mir-fixtures/M02.pli`) is EXCLUDED from the executable comparison** —
  NOT-COMPARABLE: it performs no PL/I console output; it returns 45. The native driver's
  `driver-return` observation is NOT directly comparable to the CP/M emulator's process status
  (the CP/M exit convention is not a PL/I return value — see §P2-DIFF-1.3). It is recorded as a
  feasibility case with NO demonstrated common observable, NOT as a failed compiler test.
* **D03 = CALL02 is REPLACED by CALL04** — CALL02 (`call side(4 + x); put list(x);`) prints the
  caller's own `x = 2`, assigned BEFORE the call; the callee `side` performs no output, so the
  printed `2` is weak evidence that the callee ever executes (a no-op callee would print the same
  vector). CALL04 has a transitive `chain → mid → leaf` call chain whose `51` is printed by the
  DEEPEST procedure — it cannot appear unless both subsidiary calls execute — stronger behavioral
  discrimination.

The four EXECUTED pilots (all SAME-SOURCE, all existing committed fixtures, all reused
byte-for-byte WITHOUT editing, all GET-free):

| ID | Committed fixture | SHA-256 (measured 2026-11-13, this session) | Native entry (`--export`) | 8080 entry | Independent expected PL/I console vector |
|---|---|---|---|---|---|
| D02 | `hir/mir-cf-fixtures/CF06.pli` | `bb2ba55e8e27dca1fde994a564f790c0b3fd1b5a82c9483a578c04fe3440da2f` | `count` | LINK-80 main procedure | `[0, 1, 2]` |
| D03 | `hir/mir-call-fixtures/CALL04.pli` | `72c418e4d21b80cf2e7a20eee41c6846a3f27532be3c6b8b971d13bb716e8906` | `chain` | LINK-80 main procedure | `[51]` |
| D04 | `hir/mir-call-fixtures/CALL06B.pli` | `f0e915dd51f49c644448a291919658f1e055878f485c7654cbb50f61b8503cf8` | `diffal` | LINK-80 main procedure | `[2, 7]` |
| D05 | `hir/mir-call-fixtures/CALL07.pli` | `0b2d3bdc2f9d54907fd7bb975b4fef2ade95b16f027a374652e83f5b2650977f` | `thrice` | LINK-80 main procedure | `[1, 2, 3]` |

**SAME-SOURCE is a REQUIREMENT, not a label: the runner verifies the sha256 of the file it feeds
to BOTH lanes against this table BEFORE any execution; any mismatch is a SOURCE-stage failure
(BLOCKED), never a comparison.** The four sources are the SAME BYTES on both lanes — the only
difference is the INVOCATION (native `--export <entry>` selects the entry symbol; the 8080 lane
lets LINK-80 treat the outermost procedure as the COM program). This is a difference of invocation,
not of source bytes.

### P2-DIFF-1.3 Independence and limitation of the two entry mechanisms

* **Native:** the MIR backend requires the entry to be a zero-argument
  `PROCEDURE ... RETURNS(FIXED BIN(p,0))` whose body ends with `RETURN(expr)`; `--export` must
  fold-match the head procedure name. The `console_check` driver calls `pli80_<entry>`, prints
  the program's own PUT bytes to **stdout**, and reports the returned value to **stderr** as
  `driver-return=<v>`.
* **8080:** the historical LINK-80 (with PLILIB.IRL) selects the outermost procedure as the
  program's MAIN entry; the program's exit chain (PLILIB `?STOPX`) returns CP/M's process
  status — which is NOT the PL/I return value of the entry procedure.
* **THE LIMITATION (binding):** the two entry mechanisms are independent — the native driver does
  not go through CP/M, LINK-80 or PLILIB, and the 8080 lane never uses `--export`. They are
  therefore legitimate for the COMMON observable (the program-console output), but the pilot
  claims NOTHING about the return values: on the 8080 lane the entry's PL/I return value is
  NEVER observed (no CP/M equivalent of `driver-return` exists and the process status is not a
  PL/I value). `driver-return` is lane-specific native evidence and is EXCLUDED from the
  differential comparison. **Agreement on the console vector does NOT prove unobserved return
  values, call mechanisms, or full PL/I semantic equivalence** — the D01 exclusion exists
  precisely because the only proposed common observable there was a return value.

### P2-DIFF-1.4 Independently derived expected sequences (hand-derived from the source text HERE, BEFORE any pilot run)

All four sources are `fixed bin(15)`; no `get` statement; the only console events are the
numbered `put list` statements below, in statement order.

**D02 — CF06, entry `count`.** `i = 0;` then `do while (i < 3)`: `put list(i)` (→ 0), `i = i + 1`;
next guard `1 < 3` true: output 1, increment; next guard `2 < 3` true: output 2, increment; next
guard `3 < 3` FALSE: loop ends. The function returns 3, but the return value is NOT part of the
common observation. **Expected console sequence: 0, 1, 2.**

**D03 — CALL04, entry `chain`.** `x = 51;` then `call mid(x + 0)`: the value 51 is passed to
`mid`; `mid` sets `t = m + 0` = 51 and calls `leaf(t + 0)`; `leaf` executes `put list(d)` — **the
only PUT in the program, printed by the DEEPEST procedure** — giving 51. The caller then sets
`x = x + 40` = 91 and returns 91; the caller's subsequent change is NOT observed on the console
(return value excluded, §P2-DIFF-1.3). **Expected console sequence: 51.**

**D04 — CALL06B, entry `diffal`.** `x = 2;` then `call alias(x, x + 0)`: the first actual is a
bare name → by-reference (the SAME variable cell); the second is an expression → the computed
value 2. In `alias`: `a = 7` writes THROUGH the alias to the caller's `x`; `put list(b)` prints
the value-parameter `b`, which still holds 2 — **output 2**. After the call, the caller executes
`put list(x)` — `x` is now 7 — **output 7**. The return value (7) is not observed. **Expected
console sequence: 2, 7.**

**D05 — CALL07, entry `thrice`.** `z = pick3(1, 2, 3)`: `pick3` executes `put list(a)` → 1,
`put list(b)` → 2, then `t = c` and `return (t)` = 3; the caller assigns `z = 3` and executes
`put list(z)` → 3. **Expected console sequence: 1, 2, 3.**

These expectations come from direct source-level reasoning ONLY — never from either compiler's
generated code or runtime output.

### P2-DIFF-1.5 The console observation boundary (per lane) — raw evidence kept SEPARATELY

* **8080 lane:** the program-output region is the span established by the FS-01 anchor law
  (already implemented in `tools/functional_runner.py::_run_lane_b`): from the program-name
  echo `\r\r\n` to the first terminator (`D>` prompt / `I/O ran` / end of transcript),
  WITHOUT consuming a preceding newline; a region whose terminator is NOT preceded by a newline
  is an ambiguous cut → UNKNOWN/FAIL, never a guess. Boot banner, echoes, prompts and the
  `I/O ran` line are OUTSIDE the region; ALL of them (the full raw transcript) are preserved
  as separate evidence and never compared. The region itself is preserved as raw bytes
  (`<case>.console.bin`) AND as the raw full transcript — the raw bytes are never overwritten by
  the normalized form.
* **Native lane:** the program-output region is the process **stdout** alone, captured in a
  fresh process; stderr (`driver-return=<v>`) and the exit status are recorded as SEPARATE
  lane-specific evidence and are NOT part of the common observation. Raw stdout bytes preserved
  separately from the normalized vector.
* **Both:** no other source of "output" exists. The observation is the COMPLETE ordered integer
  sequence within the isolated program-output region — never numeric substrings extracted from
  the whole emulator transcript (brief §5: arbitrary numeric substrings of the whole transcript
  would match the boot banner, the LINK dimensions, or the `I/O ran` milliseconds).

### P2-DIFF-1.6 The comparator / normalization law (strict; order, multiplicity, completeness preserved)

The normalized observation is the **ordered signed-decimal integer vector**
`[v1, v2, …]` of the region's integer tokens. Extraction is admitted only when ALL of:

1. **Region proof:** the boundary is the §P2-DIFF-1.5 cut (8080) or the process stdout (native);
   nothing outside the region is read.
2. **Every integer recognized:** every token in the region parses as a signed decimal integer
   (8080 fields are 10-position right-justified; the native form is plain decimal per line);
   the token count is reported explicitly.
3. **Nothing silently discarded:** after removing whitespace (space, CR, LF, TAB) the region
   must be EMPTY — any other byte is a failure (or an explicit unclassified result), never a
   silent accept.
4. **Order and multiplicity preserved:** the vector is the token sequence in order; duplicates
   and repeats are kept as-is. No sorting, no deduplication.
5. **Completeness — a missing result is a FAILURE, not an empty success:** an empty region, or
   a vector shorter than the expected sequence, is a comparison FAIL.

Raw formatting differences are NEVER erased: the raw bytes (8080 console region; native stdout)
are retained independently of the normalized vector and are reported in the evidence. The
`collapse-spaces-v1` law of the historical gate is NOT used here; the comparator is the integer
vector, and it is the ONLY thing compared across lanes. (The 8080 and native raw byte forms
legitimately differ — 10-position fields vs plain lines — so raw byte equality across lanes is
NOT required and NOT claimed; the raw bytes are preserved per lane for audit.)

### P2-DIFF-1.7 The three-way comparison and the seven verdict classes

Comparison law: **each lane is compared with the independent expectation FIRST, then the two
lanes are compared with each other.** Verdicts (per case):

| Class | Meaning |
|---|---|
| `BOTH-PASS` | 8080 observed == expectation AND native observed == expectation |
| `8080-ONLY` | 8080 == expectation; native != expectation (both executed) |
| `NATIVE-ONLY` | native == expectation; 8080 != expectation (both executed) |
| `BOTH-FAIL-SAME` | both lanes executed, both produced the SAME observation that != expectation |
| `DIVERGENT` | both lanes executed, both != expectation, and the two lanes differ from each other |
| `BLOCKED` | a stage failed BEFORE any behavioral comparison could be made: compiler refusal, link undefined-symbol, crash/timeout, missing artifact, unverifiable boundary, source-hash mismatch |
| `NOT-COMPARABLE` | the case has no demonstrated common observable (e.g. D01 M02: return value only) |

Two never-count-as-success laws (binding): (a) a matching pair of INCORRECT outputs is
`BOTH-FAIL-SAME`, never `BOTH-PASS` (equivalence of agreement is not equivalence of correctness);
(b) a failed compiler, unresolved linker symbol, crash, timeout or absent artifact is NEVER
reported as a successful runtime comparison — it is `BLOCKED` (infrastructure failure), kept
strictly distinct from behavioral disagreement.

### P2-DIFF-1.8 Fresh-process repetition, per-stage return codes, failure classification, raw evidence

* Every successfully comparable case runs **at least TWICE per lane in fresh execution contexts**
  (fresh process for the native lane; fresh isolated CP/M workspace for the 8080 lane). Determinism
  is recorded for the NORMALIZED observation and the RAW program output SEPARATELY.
* Every stage (COMPILE / LINK / RUN / NATIVE-MIR / NATIVE-MIR2O / NATIVE-LINK / NATIVE-EXEC) has
  its OWN recorded return code and witness; the pty driver's own timeout is a distinct witness
  from the guest's; the historical exit-code law of `oracle/run.py` (0 done / 1 timeout / 2
  sim-died) is used to classify (NEVER collapsed).
* Every failure is classified: `source` (hash mismatch), `compiler` (refusal of the committed
  source), `linker` (undefined symbols), `emulator`/`host` (sim-died, launch failure, timeout),
  `behavior` (an executed comparison that disagrees).
* Every run keeps: the FULL raw transcript (8080) / raw stdout+stderr+rc (native), the isolated
  program-output region, the normalized vector, and the per-stage evidence — all under an IGNORED
  scratch root, never overwriting goldens or prior evidence.

### P2-DIFF-1.9 The differential runner — `tools/dual_backend_test.py` (written only after ≥1 case has been executed comparably on both lanes)

Reuse law: the runner REUSES the existing machinery — `tools/functional_runner.py`'s stage
safety/workspace machinery and `oracle/linkrun.py` (`new_run`, `session`, `parse_undefined`,
`TOOLS`, the FS-01 anchor cut) for the 8080 lane; `tools/mir_aot_call_test.py`'s pinned
`mir2o`/cosmo-tiny recipes (with `pli_console.c` + `console_check.c`, `chmod +x` law) for the
native lane. It does NOT create a new CP/M framework, does NOT re-implement LINK-80 handling,
and does NOT duplicate the Cosmopolitan build recipe. Requirements: strict source-hash validation
against the §P2-DIFF-1.2 table; executed stages only (never simulated); explicit timeouts
(compile 60, link 120, run 120, native 60–120); isolated scratch artifacts; raw output and
transcript retention; deterministic normalized observations; per-stage return-code evidence;
selectable case execution (`--case D02` etc.); a human-readable report AND a machine-readable
summary; the full seven-class verdict taxonomy; correct infrastructure-vs-behavior distinction.
If a manifest is needed it is a SEPARATE file under `spec/` — never part of the historical
golden or coverage registries.

### P2-DIFF-1.10 Comparator falsification controls (non-vacuity)

Using DISPOSABLE reference copies ONLY (the committed sources and executables are never touched):

* **C-DF1 (change one expected integer):** corrupt one expected vector entry by hand; the
  comparator MUST reject the (otherwise correct) observed vector against it.
* **C-DF2 (delete one mandatory output item):** remove one required item from the expected
  vector; the comparator MUST reject the complete observed vector against it.
* **C-DF3 (permute two mandatory items whose values differ):** swap two items of DIFFERENT
  values in the expected vector; the comparator MUST reject the ordered observed vector against
  it.

Each corruption is a comparator-SENSITIVITY test: the corrupted expectation must FAIL against the
REAL, unmodified observation — the rejection must come from the comparator, not from a syntactically
invalid input (a test that fails only because its corrupted input is syntactically invalid is NOT
sufficient evidence of sensitivity).

### P2-DIFF-1.11 Known risks (recorded BEFORE the run)

* **Terminal framing:** the CP/M pty transcript carries echo/CR artifacts (`\r\r\n`); a stale
  `D>` echo can satisfy a `##WAIT` and abort the program before it printed anything (prompt-sync
  law: send CR, wait for the FRESH prompt, then invoke — already implemented in the functional
  runner; reused verbatim).
* **CP/M output formatting:** the 10-position field / no-line-terminator / single-final-newline
  law ([C352], README §6) means raw bytes legitimately differ across lanes; the comparator must
  NOT compare raw bytes across lanes.
* **Linker undefined symbols:** LINK-80 writes a `.COM` even with UNRESOLVED symbols ([C137]);
  the FULL transcript segment must be parsed with `parse_undefined`, never a truncated slice.
* **Unproven historical LINK/RUN for three of the four cases:** only CALL06B has a committed
  link+run witness. CF06/CALL04/CALL07 link/run are UNMEASURED; if a case fails at LINK or RUN
  it is `BLOCKED` for that case and the campaign still reports the other three — a compile
  success is NOT claimed to be executable.
* **Unobserved PL/I return values:** not part of any verdict; never inferred.
* **Emulator timing:** the sim runs with unlimited CPU speed; the run timeout is bounded
  (120 s) and a timeout is a distinct witness class, never a "pass".

### P2-DIFF-1.12 Predicted outcomes and falsifiers (per case; the observable sequence is predicted, NOT an exact byte layout)

* **D02 (CF06):** predict BOTH-PASS — normalized vector `[0,1,2]` on BOTH lanes; 8080 raw output
  one line (10-position fields, exact raw layout UNMEASURED); native stdout `0\n1\n2\n`.
  Falsifier: any vector other than `[0,1,2]` on either lane — e.g. `[0,1,2,3]` (a fourth PUT
  after the loop), `[1,2,3]` (off-by-one), `[0,1]` (missing iteration), a hang (loop never
  terminates), an empty region, or a LINK/RUN failure (BLOCKED).
* **D03 (CALL04):** predict BOTH-PASS — `[51]` on both lanes; native stdout `51\n`. Falsifier:
  `[]` (the deepest `leaf` did not execute — callee failure), `[51,91]` or `[91]` (the caller's
  later change leaked into the console — impossible under the source, so such a witness means
  a boundary or codegen defect), `[51]` printed twice (duplication), or a LINK/RUN failure.
* **D04 (CALL06B):** predict BOTH-PASS — `[2,7]` on both lanes; native stdout `2\n7\n`; the
  8080 raw region is ALREADY MEASURED as `        2         7\r\n` (recon probe). Falsifier:
  `[7,7]` (aliasing lost — the known signature of the C-M3b control), `[2,2]` (the by-ref store
  lost), `[2]` (caller PUT missing), an order swap, or a LINK/RUN failure.
* **D05 (CALL07):** predict BOTH-PASS — `[1,2,3]` on both lanes; native stdout `1\n2\n3\n`.
  Falsifier: `[1,2]` (the returned value NOT used by the caller), `[1,2,3,3]` (an extra PUT),
  a wrong third value (return-path corruption), or a LINK/RUN failure.

A falsified prediction is STOP-and-attribute (PROTOCOL #1): recorded, NOT silently repaired.

### P2-DIFF-1.13 Frozen regression panel (after the pilot + runner; each command its OWN measured rc — no count is hardcoded as a success criterion)

`tools/e2e_gate.py` (expect 1328/1328 — 190/190 — 9/9 — coverage 149 rows 0/0 — census 16/0/25/0
— prose 5); `tools/hir_test.py` (220); `tools/mir_aot_test.py` (32); `tools/mir_aot_cosmo_test.py`
(25); `tools/mir_aot_console_test.py` (43); `tools/mir_aot_debug_test.py` (23); `tools/mir_aot_cf_test.py`
(83); `tools/mir_aot_call_test.py` (86); all existing MIR/CF pins UNMOVED (byte-compare);
`spec/CLAIMS.md` 203 headers ending C380; the historical compiler SHA-256
`172595d5…aca281` from a fresh build dir. NO `--runtime` / `--link-run` extended gate modes in
this campaign.

### P2-DIFF-1.14 Work order, complexity stop, FORBIDDEN routes

1. **This pre-registration commit** (ONE explicit path, `spec/lab-evidence/e2e54/PLAN.md`) —
   BEFORE any fixture, manifest or runner byte.
2. Pilot measured-first: each of the four cases, both lanes, fresh contexts, ≥2 executions per
   lane per case; raw + normalized + per-stage evidence kept separately.
3. After ≥1 case has actually been executed comparably on BOTH lanes, write
   `tools/dual_backend_test.py` (this PLAN §P2-DIFF-1.9 is its written-to-PLAN-before-run spec);
   run it; run the three comparator falsification controls INSIDE the runner.
4. Full frozen regression panel (§P2-DIFF-1.13), each command its own rc.
5. RESULTS `## §P2-DIFF-1` (complete, with the four-case verdict table, source and tool
   identities, repetition and falsification evidence, limitations); a concise additive
   `docs/architecture/backend-boundary.md` note IF justified; durables (HANDOFF/PROGRESS/
   LEARNINGS) and the verified checkpoint; then STOP.

**Complexity stop:** if any pilot case fails at COMPILE on the 8080 lane (contradicting the
measured sweep), or the pilot cannot be executed on a lane with a BOUNDED harness fix, STOP and
report — do not extend the campaign into new functionality.
**FORBIDDEN routes (binding):** no compiler source change; no MIR/ABI/golden/pin/claims change;
no new PL/I fixture; no execution of the original DR `PLI.COM`; no `git add -A`/`reset`/`clean`;
never stage `handoff.config.json`; no push; no modification of the historical golden/coverage
registries; no claim that console agreement proves return-value or call-mechanism equivalence;
no extended gate modes.

### P2-DIFF-1.15 Dashboard row (CLOSED/OPEN row added at close)

| slice | status | notes |
|---|---|---|
| P2-DIFF-1 | **CLOSED 2026-11-13** (recon/baseline/pre-registration/pilot sessions `01a1d39e`→`01a1d4d5`; pre-registration `ddff0717` BEFORE any fixture/manifest/runner byte; runner `50b88594` first run rc **0** — **4/4 BOTH-PASS**, **14** comparator controls **ALL REJECTED**, **18** measured checks) | the differential method LANDED and is FEASIBLE: four SAME-SOURCE pilots (D02 CF06 `count` `[0,1,2]`, D03 CALL04 `chain` `[51]` — PUT in the DEEPEST procedure, D04 CALL06B `diffal` `[2,7]` — by-ref aliasing, D05 CALL07 `thrice` `[1,2,3]` — returned value used by the caller) execute the identical committed source bytes on BOTH backends and agree with the hand-derived expectations AND with each other, ×2 fresh per lane, raw bytes/transcript/region kept SEPARATELY; D01 M02 recorded **NOT-COMPARABLE** (no console observable). The pre-registered risk that CF06/CALL04/CALL07 had no LINK/RUN witness is RESOLVED — all three link clean (`parse_undefined` EMPTY on the FULL segment) and run on CP/M. **NOT a DR oracle comparison**: the linker/runtime are Digital Research's, the COMPILER is mine; `PLI.COM` never ran. FULL FROZEN PANEL ALL HIT and every panel log byte-identical to the baseline's (gate 1328/1328-190/190-9/9-149 rows 0/0-census 16/0/25/0-prose 5, hir 220, mir 32, cosmo 25, console 43, debug 23, CF 83, call 86, pins UNMOVED, DWARF standalone UNMOVED, fresh build hist 122 sha==`172595d5…aca281`, ledger 203/C380, T2 clean); ZERO compiler/MIR/golden/pin/claims byte. RESULTS §P2-DIFF-1; **STOP — the campaign ends here, any extension needs a NEW operator brief** |

---

## §P2-DIFF-2 — Pre-registration: differential-runner hardening, integrated PL/I programs, and one bounded OCaml responsibility extraction (committed BEFORE any runner or compiler behaviour change and BEFORE any new experiment)

**Operator brief:** E2E-54/P2-DIFF-2, authorized 2026-11-13. The brief text is NOT stored in the
repository. This section is the PROTOCOL #1 pre-registration for the whole campaign; §P2-DIFF-1
above is **CLOSED and immutable** and is never edited by this campaign.

**Character of the campaign.** Integration + harness-validity + maintainability. It is NOT a
compiler-development campaign and NOT a DR oracle campaign: the original Digital Research
`PLI.COM` is **NEVER executed** (ZERO oracle; the scientific ledger stays 203 headers ending
**C380**; no new claim is derivable from any of this, because nothing here observes DR). The
historical LINK-80 1.31, `PLILIB.IRL` and the CP/M simulator ARE authorized and ARE the
execution substrate of the 8080 lane — but the object code on that lane is produced by the
**reproduction compiler**, which is mine; every report must keep that distinction.

**Long-term objective served:** grow a corpus of *complete executable programs* judged against
*independent specifications*, on both backends, and reduce the structural complexity of the OCaml
implementation where a real seam exists.

### P2-DIFF-2.0 Measured baseline (this session 01a1d53d, start HEAD `7e45868b`, 2026-11-13, each command its OWN rc, logs under `build/e54p2diff2/`)

| item | command | rc | measured |
|---|---|---|---|
| gate (compile tier) | `python3 tools/e2e_gate.py` | 0 | **1328/1328** byte-exact / 0 fail, **190/190** negatives, **9/9** divergences, coverage **149 rows 0/0**, census **16/0/25/0**, prose **5** |
| hir | `python3 tools/hir_test.py` | 0 | **220** checks |
| MIR AOT | `python3 tools/mir_aot_test.py` | 0 | **32** |
| Cosmopolitan | `python3 tools/mir_aot_cosmo_test.py` | 0 | **25** |
| console | `python3 tools/mir_aot_console_test.py` | 0 | **43** |
| debug | `python3 tools/mir_aot_debug_test.py` | 0 | **23** |
| control flow | `python3 tools/mir_aot_cf_test.py` | 0 | **83** |
| procedure calls | `python3 tools/mir_aot_call_test.py` | 0 | **86** |
| differential (current runner) | `python3 tools/dual_backend_test.py` | 0 | **4/4 BOTH-PASS**, 14 controls, 18 checks |
| functional runner hostile suite | `python3 tools/test_functional_runner.py` | 0 | **211/211** |
| historical compiler | `sha256sum ocaml/_build/default/bin/pli80c.exe` | 0 | `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` |
| ledger | `grep -c '^## C' spec/CLAIMS.md` | 0 | **203** headers, last `## C380` |
| pins | `git diff --exit-code -- ocaml/hir/` | 0 | clean |

Every panel log above is **byte-identical** (`cmp`) to the corresponding P2-DIFF-1 baseline log
(`build/e54p2diff-baseline-*.log`, `build/e54p2diff-reg-gate.log`): the tree is at the same
observable state as the previous campaign's close. MEASURED PRE-EXISTING and NOT fixed (recorded,
never silently repaired): `tools/test_functional_dashboard.py` **rc 1**, sole verbatim FAIL
`integration: unmapped COVERAGE rows are listed, not dropped` — the stale HARDCODED `**26**`
check (documented since E2E-52/P1; unchanged by this campaign).

The four existing differential source SHAs re-verified first-hand: CF06 `bb2ba55e…`, CALL04
`72c418e4…`, CALL06B `f0e915dd…`, CALL07 `0b2d3bdc…`.

### P2-DIFF-2.1 Stage A — the three runner defects, stated as hypotheses with falsifiers

Independent inspection of `tools/dual_backend_test.py` at `50b88594`/`7e45868b` (read first-hand,
quoted below) identifies THREE validity defects. Each is a hypothesis about the CURRENT code,
each with a test that must FAIL against the current code and PASS after the fix.

**H-A1 (determinism does not affect validity).** `rec["verdict"] = verdict(case["expected"],
v80[0] if v80 else None, vn[0] if vn else None)` — the verdict is computed from the FIRST
observation of each lane only. `determinism_8080` / `determinism_native` are recorded but never
consulted, and a missing second observation is silently ignored.
*Falsifier of the fix:* a case where run 1 matches the expectation and run 2 does not (on either
lane) must NOT be `BOTH-PASS`; a case where either lane yielded fewer than two complete
observations must NOT be `BOTH-PASS`; the raw second observation must still be preserved in the
report and the failure must be attributed to the lane/run that produced it.

**H-A2 (native process status is not checked).** `run_native_lane` returns `{"ok": True, …,
"rc": p.returncode}` after `exec` without ever testing `p.returncode`; the aggregation code reads
only `stdout`. A native process that CRASHES or exits with a runtime I/O status (the §P1-m1
status law `OK0/EOF1/BAD2/RANGE3/IOERR4`) can therefore be recorded as a successful lane as long
as its stdout happens to match.
*Falsifier of the fix:* an injected lane result with matching stdout and a non-zero process
`rc` must NOT be `BOTH-PASS` and must be classified as an infrastructure/execution failure.
*Status policy (pre-registered, consistent with the committed driver):* `tools/mir_aot/
console_check.c` prints `driver-return=<v>` to **stderr** and returns `0` on normal completion;
the runtime failure tail `exit(status)`s with a NONZERO status (0 is never reached on the failure
path). Therefore the native process status is a **validity requirement: `rc == 0`**, and the
`driver-return` value remains a lane-specific diagnostic that is NOT a cross-backend observable.
The PL/I function's return value and the process status are two different things and are kept in
separate report fields.

**H-A3 (the exit-code contract is self-contradictory).** The module docstring says
`exit codes: 0 every case BOTH-PASS and all controls failed LOUDLY; 1 otherwise (a behavioral
verdict, a BLOCKED case, …)`; the code comment at the verdict-reporting block says
`verdicts are REPORTED, only BLOCKED cases and control failures are runner errors`. The code
implements the second (`return 0 if not report["failures"] else 1`, and only BLOCKED/control
failures are appended to `failures`). So a `DIVERGENT`/`8080-ONLY`/`BOTH-FAIL-SAME` measurement
exits 0 — a scientific result that must be retained, but a silent signal for a CI gate.
*Adjudicated policy (binding for the fix):*
1. A completed measurement is ALWAYS retained and reported — divergent outcomes included.
   No successful execution is discarded or rewritten.
2. The DEFAULT (diagnostic) mode's exit code keeps its **existing meaning**: `0` iff the run
   produced no `failures` entry (no BLOCKED case, no vacuous control); a semantic verdict is
   still a reported outcome, not a runner error. Changing it would silently change the meaning of
   an existing interface (the brief forbids that).
3. A new explicit `--strict` (gating) mode makes the runner exit non-zero for ANY result outside
   the acceptance criterion — every compared case `BOTH-PASS`, all controls rejected, no
   infrastructure failure.
4. The machine-readable report distinguishes the two failure classes WITHOUT renaming or
   redefining any existing field: `infrastructure_failure` (a lane that could not produce a
   complete, valid, repeated observation) and `semantic_divergence` (a completed measurement whose
   verdict is not `BOTH-PASS`) are new ADDITIVE lists; `failures`, `cases`, `verdict`, `controls`,
   `normalized_*`, `raw_*`, `determinism_*`, `lane` keep their existing meanings.

**Adversarial tests (A4).** A NEW hostile suite `tools/test_dual_backend.py` (check-style,
self-counting, like `tools/test_functional_runner.py`): `python3 tools/test_dual_backend.py`,
exit 0 iff every check passes. NO compiler, LINK-80, cpmsim, emulator or oracle process is
launched by it: the lane functions are INJECTED (the hardened runner gains a `run_cases(...,
lane_fns=…)` seam whose default is the real `run_8080_lane`/`run_native_lane`), and the comparator
attacked with disposable expectations. Minimum required cases (brief §3/A4):

| # | attack | expected verdict under the hardened law |
|---|---|---|
| T1 | 8080 run1 correct, run2 wrong | NOT `BOTH-PASS` (determinism/validity failure) |
| T2 | 8080 run1 wrong, run2 correct | NOT `BOTH-PASS` |
| T3 | native run1 correct, run2 wrong | NOT `BOTH-PASS` |
| T4 | native run1 correct, run2 with non-zero process `rc` | NOT `BOTH-PASS`, infrastructure failure |
| T5 | correct stdout, native `rc` nonzero | NOT `BOTH-PASS` (H-A2) |
| T6 | missing second execution / missing observation on either lane | NOT `BOTH-PASS`, infrastructure failure |
| T7 | both lanes produce the SAME wrong vector | `BOTH-FAIL-SAME`, never `BOTH-PASS` |
| T8 | normalization rejects unexpected text and an incomplete vector | raises (never silent) |
| T9 | exit-code law: divergent case is reported and retained; default mode `0`/`1` per its existing meaning; `--strict` mode non-zero | measured |
| T10 | observation attribution preserved: the failing run's raw bytes are kept in the report | measured |

The suite MUST be committed and run against the CURRENT runner FIRST (demonstrating the old
behaviour), and only then against the fixed runner. Stage A is committed independently of
Stage B and Stage C.

### P2-DIFF-2.2 The overlapping capability set (Stage B feasibility analysis, read first-hand)

Derived from the ACTUAL sources, not from documents: `ocaml/hir/hir_build.ml` (the HIR subset
gate), `ocaml/hir/hir.ml` (the closed node grammar), `ocaml/hir/mir_backend.ml` (the native
subset + the interval/join/counted-loop/call laws), and the 25 existing positive fixtures
(`hir/mir-fixtures`, `hir/mir-cf-fixtures`, `hir/mir-call-fixtures`). The 8080 lane uses the
historical `pli80c` path, which is the byte-exact DR reproduction and is strictly more permissive
than the HIR/MIR subset for the constructs below; the differential therefore runs on the
INTERSECTION, and the intersection is what the programs are designed inside.

| capability | native (HIR + MIR) | measured witness |
|---|---|---|
| entry: outermost/zero-param `returns(fixed bin(15))`, one final top-level `RETURN(expr)` | required | M01–M06, CF01–CF10, CALL01–CALL10 |
| `if`/`else` with the six relational operators, arms nested | YES | CF01–CF05 |
| bounded `DO WHILE` (counted-loop proof: `iv` point-initialized, `iv = iv ± <positive literal>` EXACTLY once, guard `iv <op> <constant point>`, direction match, no nested loop, IV not by-ref in a body call) | YES | CF06–CF10 |
| join law: one-arm assignment ⇒ the sid is `None` afterwards (drop-not-inherit) | enforced | CF02/CF04, `hir_test` CFN1 |
| loop-exit law: every body-written sid (top-level `Assign`/`Get` in the body list, or a by-ref actual of a body `Call_s`) is DROPPED after the loop; the IV survives at its exact exit value | enforced | §P1-m2.3, CF09 |
| `call` statement to a VOID procedure: by-reference bare-name actuals (home-pass, real aliasing) and by-value expression actuals | YES | CALL01/04/05/06A/06B/10 |
| `x = f(<all-by-value actuals>)` as a whole RHS; a bare-name or literal actual is BY REFERENCE by bind's own evidence, so a value call needs an expression actual (the `n + 0` idiom is the proven witness) | YES | CALL04/07/08/10 |
| result of a value call = the callee's FULL declared window `W(q)` — **no interprocedural narrowing** | enforced | §P1-m3 I3, `wret`/`thrice` |
| after a `Call_s` with a by-ref actual, that sid widens to `W(declared)` | enforced | §P1-m3.2-8 |
| every literal: plain non-negative decimal, ≤ 9 digits, typed `bin(default p)`, ≤ `bin(15)` (the ceiling is 15) | enforced | `hir_build.lower_lit` |
| every intermediate expression: type-equal operands + exact interval inside `W(15)` (±32767) or the node is refused | enforced | §P1-m0.3, `lower` |

**CORRECTION (Stage-C close, 2026-11-13; the text above is the pre-registration and stands as
history).** The row `W(15) (±32767)` and the row `literals … ≤ bin(15)` are TWO DIFFERENT
quantities and the table conflated them. MEASURED: `W(15) = ±(2^14-1) = ±16383` (the
`decimal_int`/`window` law, the refusal text `leaving the declared-precision window
[-16383,16383]`), while `32767` is the 8080 lane's `bin15_fits` LITERAL-IMMEDIATE ceiling
(`codegen.ml:1459`) — the two DIF programs are unaffected (their literals are 1..6300) and the
panel confirms it; the binding INTERSECTION for a lane pair is `±16383`. Evidence: RESULTS
§P2-DIFF-2.7; the probe (disposable, ZERO repo byte) compiled `x = 20000` and `x = 32767` on
`dcl x fixed bin(15)`: 8080 rc 0 with the `0x4E20`/`0x7FFF` immediates, native rc 2 both times.
| `put list(<one item>)` — one value or one printable literal; NO control items, NO multiple items, NO `PUT EDIT`, NO stream | YES | M04–M06, CF01–CF10 |
| `get list(<scalar>)` | native only in this campaign (the 8080 lane runs with a one-`^Z` script: an EOF is a nonzero status) | §P1-m1 |
| `dcl` statements before the body; `fixed bin(p,0)` only; no `STATIC`/`EXTERNAL`/`ENTRY` | enforced | all fixtures |

NOT available on BOTH lanes (each is a documented blocker, not a gap to be papered over):
`DO n = … TO …` (the parser has no `FOR` form in the HIR subset — `Sdoto` refuses), `DO` groups
(`Sdobegin` → HIR-E05), `GOTO`/labels, `SELECT`, arrays (`D_elem`/`Elem_read` refuse `E18`),
`FIXED DECIMAL`, character/`VARCHAR` data, division, `**`, `&`, `|`, `^` on arithmetic values,
built-in functions, recursion, nested procedures, early/nested `RETURN`, `PUT EDIT`, `FILE`/
`GET`, non-`STOP` program end, `>15`-bit precision. **No new numeric semantics, no array, no
`GET`/`PUT EDIT` is added in this campaign** (brief §4).

### P2-DIFF-2.3 The two integrated programs (design, prediction, and independence)

Both are ORIGINAL, self-contained, deterministic programs (no `GET`, no input). They are NOT
enlarged copies of any existing fixture. Sources: `hir/dif-fixtures/DIF01.pli` (entry `tariff`)
and `hir/dif-fixtures/DIF02.pli` (entry `steps`), committed with the conventional encoding
(ASCII, CRLF, `^Z`-terminated) and SHA-256 recorded BEFORE any execution.

**DIF01 "tariff" — rule-based calculation.** A telephone-style tariff: three subscriber classes
with a per-unit charge, a fixed deposit, and a class-dependent surcharge. Interacts: nested
`IF`/`ELSE` rule selection, `+`/`-`/`*` arithmetic, a `Call_s` to a void `report` procedure
(by-reference actual + a by-value expression actual), a value `Call_e` to `tier`, and a
deterministic repetition of the rule set. Hand-derived expected console vector (the ONLY
observable; the entry's return value is NOT compared):

```
tier(100)  = 100*18 = 1800
tier(10)   = 10*40  = 400
tier(1)    = 1*120  = 120
report(1, 5):  5*1200 = 6000 ; 6000 + 300 = 6300
report(2, 1):  1*1200 = 1200 ; 1200 + 300 = 1500
report(3, 2):  2*1200 = 2400 ; 2400 + 600 = 3000
```
expected vector `[6300, 1500, 3000, 1800, 400, 120]` — derived from the ALGORITHM and the source
text here, before either compiler is run, and never from any output.

**DIF02 "steps" — bounded sequence processing.** The absolute deviation of each step of a bounded
counted sequence from its midpoint, doubled and offset. Interacts: bounded `DO WHILE` with the
counted-loop proof, scalar state, a `Call_s` to a VOID procedure whose by-reference actual is
modified by the callee (real aliasing) and re-read, a value `Call_e`, and per-iteration output.
Hand-derived expected vector: `d = |i-5|` for `i = 1..8` → `4,3,2,1,1,2,3,4`; `scale(d) = d*2+1`
→ `[9, 7, 5, 3, 3, 5, 7, 9]`.

**Independence law (brief §4, binding).** The algorithm, the expected vector and the invariants of
each program are written HERE, in this pre-registered commit, BEFORE the source files exist in
the tree; the sources are then prepared, SHA-verified and committed; only then does the
differential run. If a prediction is falsified, the ORIGINAL prediction and the falsifying
evidence are both preserved (PROTOCOL #2) — no fitting, no re-derivation from an output.
Expected OUTCOME classes: `BOTH-PASS` for both, or a documented precise blocker (a named
`HIR-E1x` refusal, a `my-gap` 8080 compile failure, or a lane-status failure) with the smallest
meaningful general solution recorded. A compilation refusal is a scientific result.

**Predictions and falsifiers (Stage B).**
* H-B1: every program compiles on the historical path (`pli80c -d`, rc 0, no `[TBD]` refusal).
  Falsified by any nonzero rc.
* H-B2: every program lowers to MIR and the emitted `.mir` passes `mir2o` and links (rc 0).
  Falsified by any named refusal (which then IS the blocker).
* H-B3: the 8080 lane links (`parse_undefined` empty) and runs with the `done (prompt returned)`
  witness and the FS-01 region cut. Falsified by any stage failure.
* H-B4: both lanes produce the hand-derived vector in BOTH fresh executions → `BOTH-PASS`.
  Falsified by any other verdict; a divergent verdict is retained and reported.
* H-B5: the hardened comparator's controls still all reject (non-vacuity).

### P2-DIFF-2.4 Stage C — the `Mir_numeric` extraction (audit first, then ONE responsibility)

`ocaml/hir/mir_backend.ml` is 1936 lines whose `compile` function holds procedure selection,
numeric analysis, definite initialization, control-flow joins, call conventions, MIR emission and
textual assembly. The authorized candidate seam is the **pure numeric-domain algebra**: the
declared-precision window, containment, interval display, hull/point tests, and the exact
interval arithmetic of `+ - *`/negation. The pure candidates found in the current code are
`window` (mir_backend.ml:120), `in_window` (:124), `show_iv` (:126), `decimal_int` (:131), the
`Add`/`Sub`/`Mul` interval algebra in `lower` (:645–:657), the `Neg` flip (:668), and the
`Some/Some` hull arm of `join_env` (:684).
*Invariants (pre-registered):*
1. Behavioural equivalence: the extracted operations are exact integer functions; the MIR
   artifacts, the diagnostic strings and the refusal ORDER must be byte-identical (the whole
   panel is the proof).
2. Dependency law: the new module imports NOTHING from MIR emission, mutable instruction state,
   `rel80`/REL-80 layout, or compiler-global state; its only allowed dependency is `Hir` (for
   the `Fixed_bin` type) or nothing at all.
3. No new numeric acceptance rule: the extraction MOVES code, it does not add, widen or narrow a
   domain.
4. The historical compiler is byte-identical: `pli80c.exe` sha `172595d5…aca281` and the gate
   1328/1328, and `ocaml/lib`/`ocaml/bin` untouched (the extraction lives only in `ocaml/hir/`).
*STOP condition:* if the audit shows the numeric algebra is NOT separable at these call sites
(e.g. it needs the emission context or the diagnostic attribution), the extraction is NOT
performed and the reason is reported; no cosmetic substitute is performed.

### P2-DIFF-2.5 Documentation correction (brief §5)

`docs/architecture/backend-boundary.md` §7-11 currently states that the two lanes "share the
parser, the binder and the HIR". The measured pipeline (§0 of the same document) is:
`pli80c` = Parser → Bind → **Codegen** (never constructs `Hir.program`); `pli80mir` = Parser →
Bind → `Semantic_env` → `Hir_build` → **Hir** → MIR. The corrected text must say: the parser and
bind are the shared semantic foundations; the NATIVE MIR backend consumes the HIR; the historical
Intel 8080 backend still uses the existing `codegen.ml` path and does NOT consume the HIR. No
architectural migration is claimed.

### P2-DIFF-2.6 Frozen regression panel (the same panel as §P2-DIFF-1.13, plus the new suite)

`tools/e2e_gate.py` (1328/1328 — 190/190 — 9/9 — 149 rows 0/0 — 16/0/25/0 — prose 5);
`tools/hir_test.py` (220); `tools/mir_aot_test.py` (32); `tools/mir_aot_cosmo_test.py` (25);
`tools/mir_aot_console_test.py` (43); `tools/mir_aot_debug_test.py` (23); `tools/mir_aot_cf_test.py`
(83); `tools/mir_aot_call_test.py` (86); `tools/test_dual_backend.py` (NEW, measured count);
`tools/dual_backend_test.py` (the four EXISTING cases must remain `BOTH-PASS` under the hardened
law); all existing MIR/CF/call pins UNMOVED (`git diff --exit-code -- hir/`); the historical
compiler sha `172595d5…aca281` from a fresh build dir; `spec/CLAIMS.md` 203 headers ending C380.
NO `--runtime` / `--link-run` extended gate mode. Each command its OWN measured rc.

### P2-DIFF-2.7 Work order (each stage an independent commit set), STOP conditions

1. **This pre-registration** (ONE explicit path) — committed BEFORE any runner or compiler
   behaviour change and BEFORE any new fixture.
2. **Stage A:** (a) `tools/test_dual_backend.py` committed and RUN against the current runner —
   the old behaviour must be demonstrated (recorded rc, the FAILing checks verbatim);
   (b) the hardened `tools/dual_backend_test.py`; (c) the suite re-run green; (d) the four
   existing differential cases re-run. Stage A is committed and CLOSED before Stage B starts.
3. **Stage B:** the two sources + their reference specifications committed; then the differential
   run; then the capability matrix + the blocker list.
4. **Stage C:** the audit, the `Mir_numeric` module, its independent tests, the equivalence
   panel; the §7-11 correction; committed separately.
5. **Close:** RESULTS `## §P2-DIFF-2`, the dashboard row, the durables, the checkpoint.

**STOP conditions (binding):** (i) any Stage-A test that CANNOT distinguish the old behaviour
from the new — stop and re-audit the test; (ii) a Stage-B program that needs a missing feature —
stop that program, document the exact blocker, do NOT weaken the program to make it pass, and do
NOT extend the compiler; (iii) a Stage-C seam that is not safely separable — STOP and report, no
cosmetic alternative; (iv) any panel regression or any pin/golden move — STOP and attribute;
(v) any temptation to run `PLI.COM` — forbidden, full stop.

**FORBIDDEN routes (binding):** no execution of the original DR `PLI.COM`; no behavioural change
to the historical compiler (`ocaml/lib`, `ocaml/bin`); no golden regeneration; no change to any
historical claim; no new MIR ABI; no new numeric acceptance rule; no general rewrite of the
historical code generator; no `git add -A`/`reset`/`clean`; never stage or modify
`handoff.config.json` (the operator's edit stays unstaged); no push; no automatic handoff
renewal.

### P2-DIFF-2.8 Dashboard row (added at close)

| slice | status | notes |
|---|---|---|
| P2-DIFF-2 | **Stages A+B CLOSED 2026-11-13** (pre-registration `41fca33e` BEFORE any runner/test/fixture byte; Stage A(a) `06a7fdbf` — the suite RUN against the UNMODIFIED runner, measured rc **1**, 4 FAIL + 3 missing groups; STOP-and-attribute amendments `e789de65` (PLAN §P2-DIFF-2.9 A/B/C) then `2dd43db0` (T7c fixed, T4 implemented); Stage A(b) `55e43285` — the hardened runner, suite **29/29** rc 0, the four historical cases **rc 0** in BOTH modes, 14/14 controls REJECTED, Stage A committed independently; Stage B `db3fda9c` (the two sources + the two `.mir` pins + this §P2-DIFF-2.10, committed BEFORE any differential execution) then `52c5bf68` (the runner's D06/D07 entries)) | the three runner defects H-A1/H-A2/H-A3 were **REAL** and the fix is **measured**: the hardened runner validates BOTH executions of EACH lane, enforces the pre-registered native status law `rc == 0`, and separates `infrastructure_failure` from `semantic_divergence` (ADDITIVE fields, no existing field redefined). **Two integrated programs, six-case run rc 0 in BOTH modes: 6/6 `BOTH-PASS`, determinism `(True,True)` on all twelve lane executions, 22/22 controls REJECTED, 28 checks**; D06 `tariff` `[6300,1500,3000,1800,400,120]` and D07 `steps` `[9,7,5,3,3,5,7,9]` — the PRE-REGISTERED vectors, unchanged (the DIF01 source defect was caught by hand-tracing BEFORE the run, §P2-DIFF-2.4 of RESULTS). The full frozen panel §P2-DIFF-2.6 hit with every log `cmp`-IDENTICAL to the campaign baseline; compiler `172595d5…aca281`; ledger 203/C380; `git diff --exit-code -- ocaml/` and `-- hir/` both rc 0. **NOT a DR oracle comparison**: the linker/runtime are Digital Research's, the COMPILER is mine, `PLI.COM` never ran. **STAGE C — CLOSED** (see §P2-DIFF-2.11): the extraction `f1f3c1ab` + the additive tool
`97c0fa29`; the whole frozen panel green with the extraction, every log `cmp`-identical to the
baseline except the single disclosed hir F8 file-count line; `pli80c.exe` `172595d5…aca281`; all
32 `.mir` pins re-measured byte-equal; `git diff --exit-code -- hir/` and `-- ocaml/` rc 0; the
§P2-DIFF-2.2 `±32767`/`W(15)` conflation FALSIFIED by measurement (the intersection is `±16383`) |

### P2-DIFF-2.9 Amendments A/B/C — STOP-and-attribute (operator-approved 2026-11-13, committed BEFORE any runner or test byte is amended; PROTOCOL #1)

A fresh independent review of the files published at HEAD `042c208f` found THREE methodological
contradictions in the campaign's own pre-registered artifacts. The operator authorized the
three corrections below. The campaign stays OPEN; no new campaign is opened. The original texts
are quoted VERBATIM and are NOT overwritten — the pre-registration above stands as history;
this section is the binding amendment (the §P1-m3.15/.16/.17/.18 precedent).

**A — the T7c fixture was WRONG (adversarial suite `tools/test_dual_backend.py`, commit `06a7fdbf`).**
The pre-registered check at lines 251–254 reads:

```python
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [lane_native("9\n9\n"), lane_native("9\n9\n")])
    check("T7c both lanes the same WRONG vector, twice each -> BOTH-FAIL-SAME",
          v is not None and v["verdict"] == "BOTH-FAIL-SAME", str(v and v["verdict"]))
```

The injected observations are `[1,2]` on the 8080 lane and `[9,9]` on the native lane against
the disposable case's expected `[1,2]`; the check nonetheless demands `BOTH-FAIL-SAME`. Under
the §P2-DIFF-1.7 verdict law that configuration is `8080-ONLY` — one lane matches the
expectation, the other does not. The fixture never exercised the class it claimed.
*Disposition:* the initial test and its error are preserved in the protocol history (commit
`06a7fdbf`, pre-fix log `build/e54p2diff2/stageA-pretest.log` — neither is rewritten). The
injected observations are corrected so BOTH lanes produce `[9,9]` (genuinely the same wrong
vector, twice each), keeping the expected verdict `BOTH-FAIL-SAME`. The check label and the
asserted verdict are unchanged; only the injection is amended.

**B — DIF02 was MATHEMATICALLY CONTRADICTORY (PLAN §P2-DIFF-2.3, commit `41fca33e`).**
The pre-registered text at lines 6286–6288 reads:

> Hand-derived expected vector: `d = |i-5|` for `i = 1..8` → `4,3,2,1,1,2,3,4`;
> `scale(d) = d*2+1` → `[9, 7, 5, 3, 3, 5, 7, 9]`.

The formula and the values are incompatible: `|i-5|` for `i = 1..8` is `4,3,2,1,0,1,2,3` —
not symmetric, and it contains `0` (which would scale to `1`, not `3`). The predicted `d`-vector
`4,3,2,1,1,2,3,4` does not follow from the stated formula.
*Disposition:* the operator KEEPS the original symmetric-sequence objective and the expected
vector `[9, 7, 5, 3, 3, 5, 7, 9]`. The definition of `d` is amended (the distance is computed
from the centre between 4 and 5, on both sides):

- if `i <= 4`, `d = 5 - i`;
- otherwise (`i > 4`), `d = i - 4`;
- then `scale(d) = 2*d + 1`.

For `i = 1..8` this yields `d = 4,3,2,1,1,2,3,4` and `scale = 9,7,5,3,3,5,7,9` — the
ORIGINALLY PREDICTED vector, unchanged. The old prediction, its error and the justification of
this amendment are preserved above; no re-derivation from any output occurs. **TIMING LAW
(binding): the DIF02 source must NOT be created before THIS amendment commit exists** — the
independence law of §P2-DIFF-2.3 requires the corrected definition to be committed first.

**C — the T4 control was pre-registered but NOT implemented (PLAN §P2-DIFF-2.1 table row T4,
commit `41fca33e`, vs the suite at `06a7fdbf`).**
The pre-registered attack T4 reads:

> | T4 | native run1 correct, run2 with non-zero process `rc` | NOT `BOTH-PASS`, infrastructure failure |

The suite never implemented it: T5 attacks a single run's `rc` and `assess_run` never sees the
run-2 status; the pre-fix run (rc 1, 4 FAIL + 3 missing groups) therefore demonstrated H-A1/H-A2
but NOT the run-2-masking case.
*Disposition:* the T4 check is added to the adversarial suite in the hardened section. The
first correct observation must NEVER mask the second execution's failure; the result must carry
an infrastructure-failure classification (`infrastructure_failure`), and the verdict must not be
`BOTH-PASS`. This is an ADDITION of the pre-registered attack, not a relaxation: no verdict
classification is weakened anywhere to make any test pass.

**Amended order of operations (binding, operator chronology 2026-11-13):** (1) this
amendment is committed with ONLY `spec/lab-evidence/e2e54/PLAN.md`; (2) the suite
`tools/test_dual_backend.py` is corrected (T7c injection, T4 added) and committed as its own
explicit path; (3) the runner hardening (Stage A(b)) proceeds per §P2-DIFF-2.7-2 with the
hardened checks INCLUDING T4; (4) the four existing differential cases, the frozen panel
(§P2-DIFF-2.6), and Stage A is committed independently before Stage B. Standing constraints
unchanged: ZERO oracle (`PLI.COM` never runs); no compiler/golden/claims/pin change; no push;
`handoff.config.json` never staged; explicit paths; rc DIRECT.

**D — found during Stage A(b) implementation: the T9a block of the suite carried the SAME
fixture defect as A.** `f80_div` injected `lane80("1\n2\n")` — the EXPECTED vector — against
`lane_native("9\n9\n")`, so under the §P2-DIFF-1.7 verdict law the configuration is
`8080-ONLY`, never the `DIVERGENT` the check (and the pre-registered T9 row) asserts. This is
a fixture defect, not a runner defect: the hardened runner measured it correctly (the first
post-fix suite run reported `FAIL T9a … [8080-ONLY]`). The injection is corrected to a truly
divergent fixture — BOTH lanes wrong AND different from each other (`[1,3]` vs `[9,9]`);
the check label, the asserted verdict and the retention law are unchanged. The original
injection and its error stay in the protocol history at `06a7fdbf`; no verdict classification
was weakened.

### P2-DIFF-2.10 Stage B — the two integrated sources, their measured compilation and the pin record

Committed WITH the two sources and their two `.mir` pins, BEFORE any differential execution
(independence law §P2-DIFF-2.3).  Everything below was measured first-hand in this session; the
expected vectors are the §P2-DIFF-2.3 ones, **UNCHANGED** (the amendment §P2-DIFF-2.9-B definition
for DIF02 is what the source implements).

**The sources (final, committed with this record).**  Encoding convention verified first-hand
against all 55 committed fixtures: ASCII, every line CRLF-terminated, exactly ONE trailing `^Z`
(`hir/dif-fixtures/DIF01.pli` 1249 B, `DIF02.pli` 521 B — the drafts carried 4 and 2 `^Z` bytes
and were normalized to the convention).

| case | source | sha256 | entry | nfuncs | expected vector |
|---|---|---|---|---|---|
| D06 | `hir/dif-fixtures/DIF01.pli` | `011dc4e7fc1e1d4b4e50d525817829b3dc7923b904dfb31537a977838d59bdaf` | `tariff` | 3 | `[6300, 1500, 3000, 1800, 400, 120]` |
| D07 | `hir/dif-fixtures/DIF02.pli` | `15ce8bcddf2f76149261e86f0d9f5b06d2999d236f3681a322862e24cea8489a` | `steps` | 2 | `[9, 7, 5, 3, 3, 5, 7, 9]` |

**The pins (measured first, reviewed line-by-line against §P2-DIFF-2.2/2.3 BEFORE the copy, ×2
fresh executions, `--export` stdout byte-identical to the `-o` file and to the second run).**

| pin | sha256 | bytes |
|---|---|---|
| `hir/dif-expected/DIF01.mir` | `ca313ff305e7a66b51747e9f5ff72abaed596e88a78cb0a7bb639aacfb64676c` | 3974 |
| `hir/dif-expected/DIF02.mir` | `cdcb84fee357e69efcd3e9c6feae78062e2ff24cdcd527ad3725e91125f24742` | 1404 |

**Measured compilation (each command its own DIRECT rc, `LC_ALL=C`, evidence in the ignored
`build/e54p2diff2/stageB2/`, ×2 determinism on both the `.REL` and the `.mir`).**

* `pli80c.exe -d` (the historical 8080 path): DIF01 rc 0 `PROGRAM TARIFF  CODE=509 DATA=54
  ITEMS=546 -> 1152 bytes`; DIF02 rc 0 `PROGRAM STEPS  CODE=154 DATA=18 ITEMS=163 -> 384 bytes` —
  H-B1 holds for both (no `[TBD]` refusal).
* `pli80mir.exe --export <entry>`: rc 0 with ZERO stderr for both; `.mir` 3974 / 1404 bytes.
* `build/p1m0-deps/mir2o -f`: rc 0, `wrote 4488 bytes (3 function(s))` for DIF01 and
  `wrote 2360 bytes (2 function(s))` for DIF02 — the `nfuncs` 3 and 2 used by the runner's
  `MIR2O-FUNC-COUNT` check are MEASURED, not assumed.

**One source defect found and corrected BEFORE the run (PROTOCOL #2: the prediction stands, the
source is fixed).**  The first DIF01 draft computed the second bill as `u = 6 - 1` (u = 5), which
yields `a = 6000`, `b = 6300` — i.e. the vector `[6300, 6300, 3000, …]`, contradicting the
pre-registered `report(2, 1): 1*1200 = 1200; 1200 + 300 = 1500`.  The pre-registered vector is the
contract and the source is the thing that was wrong; `u = 6 - 1` was amended to `u = 2 - 1` (u = 1),
which reproduces the pre-registered 1500.  The amendment is a single MIR byte (`mov t15, 6` →
`mov t15, 2`, verified by `diff` of the two measured outputs); no expectation was re-derived from
any output.  Hand re-derivation of both vectors from the source text alone reproduces the
pre-registered sequences exactly.

**Three measured subset laws (accepted; they shaped the sources; see LEARNINGS § "Stage B hop").**

1. `pli80c` REFUSES a literal+literal `fixed bin` ADD — the `n + 0` value-actual idiom works only
   when `n` is a variable; literal MINUS literal does fold (the `u = 2 - 1`, `u = 11 - 1 - 8`
   steps).
2. The entry's `dcl`s are not visible to a subsidiary in the MIR backend: every subsidiary
   assignment target needs its own `dcl` (else `HIR-E18: assignment to sym(k) which was never
   declared in this body`).
3. A by-reference actual of a `Call_s` inside a loop body must be re-initialized INSIDE the body
   (the loop-exit drop law leaves the body environment without it).

**D06/D07 are the runner's two new CASES entries** (additive, `tools/dual_backend_test.py`); the
`nfuncs` values above are the measured ones.  The verdict law, the controls and the exit-code
policy are unchanged from §P2-DIFF-2.1.

**Stage B CLOSED (2026-11-13, the close hop).** The two sources and their pins are committed
(`db3fda9c`); the runner's D06/D07 entries are committed (`52c5bf68`); the full six-case run
measured **rc 0 in BOTH the default and the `--strict` modes — 6/6 `BOTH-PASS`**, determinism
`(True, True)` on all twelve lane executions, **22/22 controls REJECTED**, 28 measured checks, no
`infrastructure_failure`, no `semantic_divergence` — H-B1..H-B5 all HOLD, no STOP condition fired.
The complete evidence is `spec/lab-evidence/e2e54/RESULTS.md` §P2-DIFF-2.2/.3/.4; the frozen panel
§P2-DIFF-2.6 is reproduced in §P2-DIFF-2.8 there. **STAGE C remains open** (§P2-DIFF-2.4, the
`Mir_numeric` extraction) and is committed separately from the close.

### P2-DIFF-2.11 Stage C — the `Mir_numeric` extraction (CLOSED 2026-11-13)

The pre-registered §P2-DIFF-2.4 audit is COMPLETE and the seam IS separable: the extraction
(`ocaml/hir/mir_numeric.ml`, nine `let`s plus the `iv` type, importing NOTHING) is committed
**`f1f3c1ab`**, the additive panel tool **`tools/mir_numeric_test.py`** (41 checks, its own
non-vacuity measured) is **`97c0fa29`**. The measured constraint — `join_env` cannot move as a
whole because `Int_map` is a GENERATIVE `Map.Make` instance, so only the `Some`/`Some` hull moves
as `iv_hull` and the `Map.merge` stays — is a documented deviation, not a failure. NO STOP
condition fired: the whole frozen panel §P2-DIFF-2.6 is green with the extraction in place, every
log `cmp`-IDENTICAL to the campaign baseline (the sole disclosed exception being the hir F8 line,
which embeds the `ocaml/hir/*.ml` FILE COUNT and therefore moves `11 → 13` while the FROZEN 220
`ok` count stands); `pli80c.exe` is `172595d5…aca281` from a fresh build dir; `git diff --exit-code
-- hir/` and `-- ocaml/` are rc 0; all **32** committed `.mir` pins were re-measured from the
committed fixtures and are byte-equal. The finding, the four falsifications of the driver's own
hand-derived tables, the `±16383`-vs-`32767` correction above and the PRE-EXISTING latent defect
(`decimal_int ""` raises, unreachable from the compiler, deliberately NOT fixed under invariant 3)
are in RESULTS §P2-DIFF-2.7.

## §P2-DIFF-3 — Pre-registration: sound interprocedural return-value interval summaries (PROTOCOL #1; committed BEFORE any experimental source, compiler code or probe)

Operator brief E2E-54/P2-DIFF-3, authorized 2026-11-14. §P2-DIFF-1/2 CLOSED and immutable. ZERO
oracle (`PLI.COM` never runs); ledger 203/C380; historical compiler/goldens frozen. Baseline
measured at HEAD `4e857e09` (gate 1328/1328-190/190-9/9-149-0/0-16/0/25/0-prose 5; hir 220;
mir 32/cosmo 25/console 43/debug 23/CF 83/call 86; suite 29/29; runner 6/6 BOTH-PASS;
functional 211; mir_numeric 41; sha 172595d5…aca281; W(15)=±16383).

**H1:** `lower_call_e` returns `(rr, window cq)` — the callee's FULL declared window (mir_backend
.ml ~813, §P1-m3 I3). For some reached nonrecursive side-effect-free value procedures the HIR
body + declared formal windows prove a STRICTLY smaller return interval. NOT authorized:
call-site specialization, constant propagation from actuals, interprocedural side-effect
analysis, narrowing by-ref-written variables, recursion/fixpoints, new numeric semantics,
changes to existing negative fixtures. The summary is valid for EVERY input in the declared
formal windows.

**Subset (any violation → Unknown, never a new refusal):** pid≠0 value proc `ret = Some
Fixed_bin(q,0)`, 1≤q≤15; formals `Fixed_bin(p,0)` 1≤p≤15, seeded with EXACTLY `W(p)`; last
statement the top-level `Return (Some e)`; no other Return/While/Call_s/Call_e/Get/Put/Stop;
Assign only to `D_var` of own-scope scalars; expression grammar mirrors the backend `lower` law
(Const/Var definite-init/Bin Add-Sub-Mul type-equal/Neg) with the SAME window proof via
`Mir_numeric`; relational `Bin` only as `If` conditions (no interval recorded); `If` arms join
via the backend law verbatim (Some/Some hull `iv_hull`, drop-not-inherit on any None; missing
ELSE = identity path); `Unknown_ef` ⇒ Unknown; return interval escaping `W(q)` ⇒ Unknown.

**Soundness:** per-procedure closure (no globals; `declare` refuses foreign-scope syms; value
calls pass ONLY A_value cells, by-ref actuals refused E18) ⇒ result depends only on formals+own
locals; induction over the statement sequence (every env entry is a sound over-approximation on
every path; the join is the smallest hull covering both sides; every node window-proved with the
exact endpoint algebra). Invariant `actual_return_values ⊆ inferred ⊆ declared_window`; else
fallback. No fixpoint needed (DFS cycle refusal earlier).

**DIF03 “pricing” (entry `pricing`):** `classify(x)`: `if x<=5 then c=1; else if x<=50 then c=2;
else c=3; return(c)` — computed from control flow, NOT a constant; caller `cat = classify(n+0);
cost = cat*1200; put list(cost)` for n=2,20,200; expect **[1200,2400,3600]**; summary `[1,3]`
must be sound for ALL x∈[-16383,16383]. **DIF04 “production” (entry `production`):** counted
`do while` i=1; i<6; i=i+1 (IV laws preserved); `stepclass(s)`: `if s<=3 then c=1; else if s<=4
then c=2; else c=3; return(c)`; `cl = stepclass(i+0); w = cl*350; put list(w)` INSIDE the loop
(drop law); expect **[350,350,350,700,1050]**. TIMING LAW (brief §4, stronger than P2-DIFF-2):
final sources + spec + SHAs committed BEFORE ANY compilation of those bytes; no experiment on
uncommitted sources. Baseline-refusal experiment on the OLD backend: `pli80c -d` rc 0 AND
`pli80mir` refusal whose diagnostic names `binop '*'` operand `[-16383,16383]` leaving
`[-16383,16383]` (HIR-E19). Any OTHER refusal = unrelated blocker → STOP, preserve, report
minimum fix.

**Architecture (permitted edits ONLY):** (1) NEW `ocaml/hir/mir_return_summary.ml` — pure,
`type summary = Known of (int*int) | Unknown`, deterministic `pid → summary` map over the
reached set; deps ONLY `Hir` + `Mir_numeric` (no second interval impl); NO emission, NO
diagnostics, NO Target, NO refusal raising; F8-clean. (2) `mir_backend.ml`: ONE analysis call
after the validation scans (`folded_of`/`-g` law) and BEFORE the per-procedure lowering loop —
NO reordering of discovery/entry-first/callee-first/pinned order; in `lower_call_e` the returned
interval becomes the summary iff `Known iv ∧ in_window (window cq) iv` (defensive), else
`window cq`. (3) dune `(modules …)`. (4) Stage-C tests: `ocaml/hir/mirsumtest.ml` driver +
additive `tools/mir_return_summary_test.py` (NEVER hir_test.py — 220 frozen; the F8
`ocaml/hir/*.ml` file-count line moves 13→14 — the ONE disclosed exception).

**Stage C falsifiers (minimum):** constant return ⇒ point; 1/2/3 nested ⇒ `[1,3]`;
non-exhaustive assignment ⇒ Unknown; effectful body ⇒ Unknown; unsupported expr ⇒ Unknown;
escape ⇒ Unknown and backend still refuses; two callers ⇒ ONE identical summary; ±16383
boundaries; summary vs an INDEPENDENT concrete reference evaluator over the FULL domain
[-16383,16383]; a control that CORRUPTS an inferred interval while leaving the reference
untouched must fail LOUDLY (perturb the EXPECTATION, never the guard — the accepted Stage-C
method law). Preservation: all existing `.mir` pins byte-identical; the six D02–D07 cases and
the negative fixtures (incl. CALLN9, refused by SHAPE) unchanged.

**Stage D:** register DIF03/DIF04 as **D08/D09** (additive CASES entries, committed SHAs,
measured nfuncs, pins); both lanes ×2 fresh; default + `--strict`; FULL frozen panel §P2-DIFF-2.6
+ mir_numeric 41; fresh build `pli80c.exe` 172595d5…aca281; ledger 203/C380. No BOTH-PASS
fabricated; one pass + one precise failure preserved is an accepted outcome.

**STOP (binding):** unrelated refusal; any pin/golden/claims/negative-fixture move; unexplained
panel change; oracle temptation; any soundness doubt; any need to touch `ocaml/lib`/`ocaml/bin`,
the MIR ABI or the lowering order. Standing: no push; explicit paths; `handoff.config.json`
never staged; rc DIRECT; LC_ALL=C; never batch build+tests; timeouts 60/120/900; scratch
`build/` never committed.

### P2-DIFF-3.10 Dashboard row (added at close)

| slice | status | notes |
|---|---|---|
| P2-DIFF-3 | **CLOSED 2026-11-14** (Stages A–D) | Pre-registration `92d1887b` BEFORE any byte; Stage A sources `3928f130` (DIF03 `34ac5efb…`; DIF04 fixed at `5c4ac3c6` to `b25f0a84…`, the disclosed `<=`→`>` and `return(w)`→`return(i)` deviations); baseline refusal EXACTLY as pre-registered (`pli80c` rc 0 x2, `pli80mir` HIR-E19 on the `*` x2); Stage B `5c4ac3c6`+`e49da02d` (`mir_return_summary` + `lower_call_e` + `mirsumtest` 55 checks rc 0, three corrupt controls LOUD; the panel CAUGHT the `M`-alias F8 defect); Stage C `c85c0652` (`tools/mir_return_summary_test.py`, 11 checks, non-vacuous); Stage D `58923e75` (D08/D09, measured `nfuncs` 2, the measured-first pins; the 8-case run **8/8 BOTH-PASS in BOTH modes**, the pre-registered vectors `[1200,2400,3600]` and `[350,350,350,700,1050]` MEASURED on both lanes; 37 checks, 29/29 controls REJECTED). Full frozen panel green; mir_numeric `41→43` disclosed (the new pins were a real `KeyError` defect in the tool's static table). Compiler `172595d5…aca281`; ledger 203/C380; ZERO oracle. |


## §P2-DIFF-4 — Pre-registration: call-site interval specialization of the return-summary analysis (PROTOCOL #1; committed BEFORE any experimental source, probe or compiler byte)

Operator brief E2E-54/P2-DIFF-4, authorized 2026-11-14. §P2-DIFF-1/2/3 are CLOSED and IMMUTABLE —
nothing in this section edits them. ZERO oracle (`PLI.COM` never runs); ledger 203/C380; the
historical compiler, the goldens and every existing `.mir` pin are FROZEN. Baseline measured
FIRST-HAND this session at HEAD `c3576ccb` (the brief's own verified HEAD), logs
`build/e54p2diff4/base-*.log`: gate 1328/1328–190/190–9/9–149 rows 0/0–census 16/0/25/0–prose 5;
hir 220; mir_aot 32 / cosmo 25 / console 43 / debug 23 / CF 83 / call 86; hostile suite 29/29;
dual-backend runner **8/8 BOTH-PASS rc 0 in BOTH modes** (37 checks, 29/29 controls rejected);
functional 211/211; `mir_numeric_test` 43; `mir_return_summary_test` 11; `pli80c.exe`
`172595d5…aca281`; `git diff --exit-code -- hir/` and `-- ocaml/` rc 0; ledger 203 headers
ending C380. Every value above was MEASURED, not copied from the brief.

**WHAT THIS IS NOT.** This is NOT function cloning, NOT inlining, NOT partial evaluation, NOT
specialized machine-code generation, NOT path-feasibility/branch-condition refinement. The MIR
function for the callee stays GENERIC and byte-identical; the ABI, the exports, the call
convention, the register/label numbering, the per-slot HOME-PASS value cells and the instruction
order do not move. The ONLY new capability is that the caller may know a NARROWER interval for
the result of ONE specific call because it knows the intervals of the ACTUALS at that call.

### P2-DIFF-4.1 Hypotheses and falsifiers

**H1 (the integration hypothesis).** `lower_call_e` already computes, for each `A_value` actual,
the PROVEN interval `_iv` returned by `lower env x` (measured: `mir_backend.ml` ~803, the
`_iv` is discarded). Feeding those proven intervals into the EXISTING §P2-DIFF-3 evaluator as
the initial environment of the callee's formals yields, for the same procedure, a return
interval that is (a) SOUND for that call and (b) never wider than the context-independent
summary. FALSIFIER: any case where the specialized interval is NOT a subset of the
context-independent interval, or where a callee's own emitted bytes change, or where the
specialized analysis is `Unknown` where the context-independent one is `Known` (a
non-monotonicity — the lemma below says it cannot happen; if it does, the lemma is wrong and
the campaign STOPS).

**H2 (the admission hypothesis).** There exist complete, well-formed PL/I programs in the
measured intersection of the two backends that the 8080 path compiles rc 0 and the native path
refuses with `HIR-E19` on a `binop '*'` whose left operand is the context-independent full
window, and that the native path admits AFTER H1 — with the SAME callee implementation and the
same output vector on both lanes. FALSIFIER: the pre-change measurement (Stage A) shows the
predicted refusal is absent, or shows a DIFFERENT unsupported feature as the blocker, or the
post-change run disagrees on the console vector.

**H3 (the non-bypass hypothesis).** Call-site narrowing NEVER admits a callee whose own body is
not provable over the FULL declared formal window. FALSIFIER: a program whose callee is unsafe
over `W(p)` but compiles because one caller passes a small value.

**THE CORE INVARIANT (binding).** For every call site with actual intervals A:
`actual_returns(P, A) ⊆ specialized_summary(P, A) ⊆ declared_return_window(P)`. If it cannot be
proven, the backend falls back to the context-independent summary, then to the full window.
A narrower result is NEVER accepted merely to make a fixture pass.

### P2-DIFF-4.2 The exact specialization subset

The specialized entry point accepts the SAME procedure subset as §P2-DIFF-3 (verbatim —
`pid <> 0`, value procedure with `ret = Some (Fixed_bin(q,0))`, `1 <= q <= maxp`, every formal
`Fixed_bin(p,0)` with `1 <= p <= maxp`, the last statement the top-level `Return (Some e)`, no
other `Return`/`While`/`Call_s`/`Call_e`/`Get`/`Put`/`Stop`, `Assign` only to `D_var` of
own-scope scalars, the backend's mirrored `lower` expression grammar, the relational-`Bin`
condition law, the `If` arms joined by the drop-not-inherit hull law, the `Unknown_ef` and
escape rules) and adds EXACTLY these additional obligations on the supplied arguments. ANY
violation ⇒ `Unknown` — the analysis NEVER refuses, never raises, never emits:

1. `List.length actuals = List.length pp.params` (arity), same ORDER, and the callee pid is the
   one being called;
2. every supplied interval is a NON-EMPTY closed interval (`lo <= hi`);
3. every supplied interval is contained in `W(p)` of the corresponding formal's DECLARED
   precision (never a widened or foreign window);
4. every actual is the accepted `A_value` form (a by-reference actual is refused by the backend
   BEFORE this point — E18 — and the analysis independently rejects one it is ever handed);
5. the formal's symbol exists, has storage `Formal`, belongs to `pp.params`, and its declared
   type passes the `bin_p` precision law;
6. NO inference from caller MUTABLE STORAGE after the value copy — the analysis receives only
   the interval and the declared precision of the value that is actually copied into the
   `hv<k>` cell, never a caller sid, never a caller environment entry;
7. the seeds REPLACE exactly the `seed_formals` line of `summary_of`; nothing else changes.

**SCOPE RESTRICTION (binding, the operator's decision).** NO branch-condition path refinement.
Both `If` arms stay conservatively considered and joined with the existing `Mir_numeric.iv_hull`
law. Path feasibility is a SEPARATE research problem and is FORBIDDEN in this campaign; the two
candidate programs are designed to succeed under a branch-INSENSITIVE analysis.

### P2-DIFF-4.3 Abstract-domain soundness argument

(a) **The evaluator is monotone in the formal seeds.** Every interval rule of the shared
evaluator — `iv_add`, `iv_sub`, `iv_mul` (the four-corner hull), `iv_neg`, `iv_hull`, the `Var`
read (the identity in the interval), `add_env` (an overwrite, the new interval is env-independent
for the target), the `Const` point, the drop-not-inherit join, and every `in_window` GATE — is
monotone non-decreasing in each input endpoint, and the `declared` list is computed from the
STATEMENTS, never from `env`. Hence narrowing a formal's seed can only narrow the derived
intervals; it can never turn a `Known` into an `Unknown` and can never widen an endpoint.
(b) **Per-procedure closure** (unchanged from §P2-DIFF-3): the callee is a closed function of its
formals and own locals — foreign-scope declarations are refused by `declare`, value calls pass
only `A_value` cells, by-ref actuals at a value call are refused (E18) — so the callee's result
depends on NOTHING but the values copied in at this call.
(c) **Induction over the statement sequence** (unchanged): each env entry is a sound
over-approximation of the value on every reachable path; the join is the smallest hull covering
both arms; every node is window-proved with the SAME endpoint algebra the backend uses
(`Mir_numeric` is the single interval authority).
(d) **Therefore** `specialized(P, A) ⊆ specialized(P, W) = context-independent(P) ⊆ W(q)` for
every `A ⊆ W`, and by (c) `actual_returns(P, A) ⊆ specialized(P, A)`. The backend keeps the
defensive `in_window (window cq)` re-check as a SECOND, independent guard.
(e) **No runtime assumption is introduced.** The interval is a proof about one call site; the
generated code is identical, so the invariant holds for the real machine execution trivially —
the specialization cannot change what runs, only what the caller is allowed to KNOW.
(f) **The callee's own obligation is untouched**: `lower_proc` still seeds every formal with the
FULL `W(p)` (`mir_backend.ml` ~995 `env0`). If the callee is unsafe over `W(p)`, the whole
program still refuses — H3 is a property of the ARCHITECTURE, not of a test.

### P2-DIFF-4.4 The two candidate programs and their INDEPENDENT expected outputs

The expected vectors below are derived from the APPLICATION ALGORITHM by hand, written here
BEFORE the sources exist and before any compiler has seen them. Neither compiler contributes an
expected value anywhere.

**DIF05 — capped billing (entry `billing`, subsidiary `capped_units`).**
Algorithm: `capped_units(x) = min(x, 20)` expressed as a full `IF/ELSE` assigning a local, then
ONE final `RETURN`. The entry computes three bills from the quantities 3, 12, 30, each
`bill = capped_units(quantity) * 500`, and PUTs each. Hand-derived output:
`min(3,20)*500 = 1500`; `min(12,20)*500 = 6000`; `min(30,20)*500 = 20*500 = 10000` ⇒
**[1500, 6000, 10000]**.
Why it tests specialization: with the full declared formal window the multiplication operand is
`[-16383,16383]`, and `±16383*500 = ±8191500` leaves `W(15) = [-16383,16383]`. The branch-
INSENSITIVE join over the actual interval gives `[3,20]`, `[12,20]`, `[20,30]` respectively —
`×500` gives `[1500,10000]`, `[6000,10000]`, `[10000,15000]`, every one inside `W(15)`. The
analysis need NOT know which arm executes. NOTE (pre-registered, honest): the context-
independent summary of `min(x,20)` is `[1,20]`, which ALSO fits `×500` — so the third call site
(`30`) is the load-bearing one: its specialized interval `[20,30]` differs from the context-
independent `[1,20]`, and the pre-change refusal is attributable to the FULL WINDOW only because
the analysis today returns `Known [1,20]` — recorded here so the attribution is checked, not
assumed.

**DIF06 — bounded batch (entry `batch`, subsidiary `limited_step`).**
Algorithm: a counted loop over the integer steps 1..4 (`do while (i < 5)`, start 1, step 1); each
iteration computes `limited_step(i) * 700` and PUTs it; `limited_step(x) = min(x, 12)`.
Hand-derived output: `1*700=700`, `2*700=1400`, `3*700=2100`, `4*700=2800` ⇒
**[700, 1400, 2100, 2800]**.
Why it matters: the actual is NOT a constant — inside the recognized counted loop the IV carries
the proven NON-POINT interval `[iv0, t0-1] = [1,4]` (measured law, `mir_backend.ml` ~1358). The
branch-insensitive callee analysis gives `[1,12]`; `×700 = [700,8400] ⊆ W(15)`. The full window
gives `±16383*700 = ±11468100` ⇒ refusal. NO path-feasibility analysis is required.
Both sources use the established by-value actual idiom (`<name> + 0`) because a bare name is
classified BY REFERENCE by the binder, and both respect the counted-loop drop law (the PUT is
INSIDE the loop; the entry returns the IV, which is definitely initialized at the loop exit).

**Subset pre-flight (PROPOSED, each MEASURED in Stage A before any implementation):** the
comparison is the `>`-oriented form only (the E2E-3b subset is `<`, `>`, `=`, `^=`; `<=`/`>=` are
MEASURED 8080 refusals — CF04/05/08); every subsidiary carries its own `dcl`; one data item per
`put list`; literals ≤ 32767; no literal×literal multiplication; no `GET`.

### P2-DIFF-4.5 Expected pre-change refusals (the Stage-A baseline measurement)

For each of the two committed sources, BEFORE any implementation byte:
- `pli80c.exe -d IN.PLI OUT.REL` ⇒ rc **0** (the historical compiler is my reproduction; the DR
  oracle is never invoked — the 8080 lane is a compile+link+run of MY `.REL`);
- `pli80mir.exe --export <entry> IN.PLI` ⇒ rc **2**, ZERO stdout, NO `.mir`, the diagnostic
  `HIR-E19 … MIR backend: the value of … can reach [-8191500,8191500]` (DIF05) /
  `[-11468100,11468100]` (DIF06) `…, leaving the declared-precision window [-16383,16383] …` on
  the `binop '*'` fed by the value call.
ANY OTHER refusal, or NO refusal, is an unrelated blocker or a false hypothesis ⇒ **STOP and
attribute**; do NOT manufacture a refusal; any replacement source requires a PRE-EXECUTION
additive amendment (§P2-DIFF-4.9 style). The attribution must name the exact operand interval,
because the difference between "the full declared window" and "the context-independent summary"
is exactly what the campaign is about.

### P2-DIFF-4.6 The OCaml architectural boundaries (the PERMITTED edits, complete list)

1. `ocaml/hir/mir_return_summary.ml` — extend IN PLACE. One new pure entry point; the conceptual
   API is
   `summary_of_actuals : maxp:int -> Hir.program -> int -> params:int list -> actuals:(int*int) list -> summary`
   (exact form to be fixed by the code; it takes the callee pid, the callee's formal sids in
   order, and the proven interval of each actual, in that order). `summary_of` is REWRITTEN to be
   `summary_of_actuals` with the FULL-window seeds, so there is ONE internal evaluator and ZERO
   duplicated statement/expression traversal — this is the campaign's anti-duplication
   requirement, and the context-independent API and ALL its existing semantics are preserved
   byte-for-byte. Every one of the §P2-DIFF-4.2 validations returns `Unknown`, never a refusal.
   The module keeps its dependency law (ONLY `Hir` + `Mir_numeric`) and stays clean of the Y4/
   Y6 pattern lists.
2. `ocaml/hir/mir_backend.ml` — `lower_call_e` ONLY: capture `(cell, iv)` per actual from the ONE
   existing `lower env x` (left-to-right order, exactly one lowering per actual, the same
   `hv<k>` allocation, the same `mov i64:(hv<k>), <rv>` emission), then request the specialized
   summary AFTER the existing validation, and choose `specialized` when it is `Known` and inside
   `window cq`, else the existing context-independent `Known` when it is inside, else `window cq`.
   NO change to the context-independent `summaries` call site, NO new analysis call anywhere
   else, NO emission, NO ordering, NO ABI, NO label/register numbering change.
3. `ocaml/hir/mirsumtest.ml` — extend IN PLACE (the driver is the Stage-C vehicle).
4. `tools/mir_return_summary_test.py` — the frozen literals it pins (`LIVE_OK` check count, the
   `--corrupt-*` stderr tables) move as a DIRECT, DISCLOSED consequence of (3). The change is
   explicit, recorded, and verified to leave every OTHER check unchanged.
5. `tools/mir_numeric_test.py` — the static `EXPORTS` table gains the two new fixture names. This
   is the SAME real defect class the §P2-DIFF-3 close disclosed (`KeyError 'DIF03'`): the tool
   enumerates pins dynamically but the name table is static. The count moves 43 → 45 (per pin).
6. `tools/dual_backend_test.py` — two ADDITIVE `CASES` entries (D10/D11), committed SHAs, the
   MEASURED `nfuncs`, the measured-first pins.
7. `hir/dif-fixtures/DIF05.pli`, `DIF06.pli` and `hir/dif-expected/DIF05.mir`, `DIF06.mir`.
8. `docs/architecture/backend-boundary.md` — a new additive section (the last one is `## 7-13`;
   the missing `7-14` for §P2-DIFF-3 is recorded as a DOCUMENTATION GAP in RESULTS, not silently
   patched by renumbering history).
9. `spec/lab-evidence/e2e54/{PLAN.md,RESULTS.md}`, the durables.
**FORBIDDEN:** any new `ocaml/hir/*.ml` file (MEASURED constraint: the X3/Y5 checks require the
`ocaml/hir/*.ml` count to stay 15 and the hir log to differ from the campaign baseline in exactly
the F8 line); any edit to `ocaml/lib/`, `ocaml/bin/`, `ocaml/hir/{hir.ml,hir_build.ml,
semantic_env.ml,target.ml,diagnostic.ml,backend.ml}`, the MIR ABI, `mir2o`, the Cosmopolitan
recipe, the goldens, `spec/CLAIMS.md` (NO new compiler-behaviour claim is admissible without an
oracle experiment, and ZERO oracle runs), any existing `.mir` pin, any existing negative pin.

### P2-DIFF-4.7 Positive and hostile tests (Stage C)

MANDATORY POSITIVES (each with a hand-derived expectation literal written BEFORE the run, and
each cross-checked against the driver's INDEPENDENT concrete reference evaluator, exhaustively
over the finite actual domain where computationally feasible):
- identity specialized to a POINT actual; identity specialized to a NON-POINT actual interval;
- the `min`-shaped IF/ELSE function specialized to a point and to a non-point interval, with the
  hull over both arms (no path refinement);
- the SAME function called with DISTINCT argument intervals producing DISTINCT summaries (the
  context-independent summary must be provably equal to the full-window seed);
- a FULL-WINDOW actual reproducing EXACTLY the old context-independent summary (the no-change
  law);
- a bounded-loop actual interval `[1,4]`;
- MULTIPLE formals with distinct intervals and PRESERVED argument order (and the permuted-order
  case rejected);
- boundary samples at `-16383`, `16383`, `12`, `20` and at the input-interval endpoints;
- the two REAL committed fixtures DIF05/DIF06 parsed through `Hir_build` and specialized at their
  real call sites, compared with the concrete reference over the actual interval.
MANDATORY HOSTILES (each ⇒ `Unknown`, i.e. the conservative fallback, never a new refusal):
- an actual interval OUTSIDE the formal's declared `W(p)`; an EMPTY interval (`lo > hi`);
- a MISSING or EXTRA actual; an arity mismatch; an incorrect parameter ORDER/unknown formal sid;
- an undeclared or non-`Formal` storage symbol handed as a parameter;
- an `A_reference` actual; an `Unknown_ef` actual interval source;
- an unsupported expression (Convert / Elem_read / relational value / nested Call_e) and an
  effectful procedure body (`Put`/`Get`/`Stop`/`While`/`Call_s`/early `Return`);
- a formal MODIFIED locally inside the callee (the seed must be overwritten, not merged);
- an inferred interval accidentally NARROWER than a reachable concrete result — falsified by the
  exhaustive concrete comparison;
- **THE PIVOTAL ONE (H3):** an expression that is unsafe over the callee's FULL declared domain
  must NOT become admissible merely because one caller passes a small value. Two legs: (i) at the
  analysis level, the specialized summary may be narrow while the context-independent one is
  `Unknown` — that is legal and must be stated explicitly; (ii) at the BACKEND level, a program
  whose callee overflows `W(p)` must still refuse the WHOLE program (the callee is lowered once
  with the full seeds), measured on a real fixture.
NON-VACUITY: at least THREE corrupt controls that perturb the INFERRED/specialized interval (or
the supplied actual) and NEVER the comparison guard or the concrete reference — the accepted
§P2-DIFF-2/3 method law — every one OBSERVED failing loudly (rc 1, pinned exact stderr bytes,
ZERO stdout). A control that passes is not a control.

### P2-DIFF-4.8 Existing negative fixtures; regression and byte-preservation requirements

NO existing negative may change verdict, message or pin. The known MIR/HIR negatives were listed
and NONE of them refuses for a reason the specialization could remove (measured: CALLN2/N3/N5 are
HIR-level; N4/N6/N7/N8/N9 and CFN1..N6 are shape/loop/effect based; CALLN9 refuses by SHAPE).
The full frozen panel is re-run after the implementation, each command with its OWN measured rc:
gate 1328/1328–190/190–9/9–149 rows 0/0–census 16/0/25/0–prose 5; hir 220; mir_aot 32; cosmo 25;
console 43; debug 23; CF 83; call 86; hostile suite 29/29; functional 211; `mir_numeric_test`;
`mir_return_summary_test`; the runner in BOTH modes; EVERY committed `.mir` pin re-measured
byte-equal from its committed fixture (the behavioural-equivalence proof that the specialization
moved NO emission); `pli80c.exe` sha `172595d5…aca281` from a FRESH build dir;
`git diff --exit-code -- hir/ ocaml/` rc 0 at each stage boundary; ledger 203/C380. Any pin move,
any panel-count change other than the two disclosed tool literals, any negative that flips
without the specialization being its PRE-REGISTERED reason ⇒ **STOP and attribute**. Known
unrelated defects (`decimal_int ""` raising; the stale dashboard assertion) stay OUTSIDE this
campaign. Stage D: both lanes ×2 fresh contexts, complete numeric output compared to the
independent vectors, raw regions and full transcripts preserved, the comparator controls run, and
`nfuncs` VERIFIED from mir2o's own stderr, never guessed. Success registers DIF05 as **D10** and
DIF06 as **D11**, growing the dual-backend corpus from 8 to 10 complete programs. A failure is
PRESERVED as evidence; a green count is never permission to change an expectation.

### P2-DIFF-4.9 STOP conditions (binding)

STOP and attribute (additive amendment, never a silent repair) on: the Stage-A refusal being
absent or attributable to a different feature; the callee needing a weaker rule to compile;
`specialized ⊄ context-independent` or `specialized ⊄ W(q)` anywhere; any soundness doubt; any
path-feasibility temptation; any need to add an `ocaml/hir/*.ml` file, to touch `ocaml/lib`,
`ocaml/bin`, the MIR ABI, the lowering order, an existing pin, a golden, a negative pin or
`spec/CLAIMS.md`; any unexplained panel movement; any oracle temptation. Standing: no push;
explicit paths; `handoff.config.json` NEVER staged; no `git add -A`/`reset --hard`/`clean`; rc
DIRECT; `LC_ALL=C`; `eval "$(opam env)"`; never batch build+tests; timeouts 60/120/900; scratch
`build/` never committed; `mirsumtest` from the REPO ROOT; NEVER hand-edit a managed block.

### P2-DIFF-4.10 Work order (each stage an independent, independently understandable commit)

(1) THIS pre-registration, alone, by explicit path, BEFORE any other byte. (2) Stage A: the two
independent ALGORITHMIC specifications committed; then the final `.pli` bytes, encoding verified
(CRLF + exactly one `^Z`), SHA-256 recorded, committed; and ONLY THEN the old-backend
measurement. (3) Stage B: the focused architecture audit write-up, the module extension, the
`lower_call_e` integration, the driver's live families green, the frozen panel green. (4) Stage
C: the positive/hostile/non-vacuity table, the two disclosed tool updates. (5) Stage D: D10/D11
registered, both lanes, both modes, measured pins. (6) The close: RESULTS §P2-DIFF-4, the PLAN
dashboard row, the arch section, the durables, the finalized checkpoint. **STOP after P2-DIFF-4
is measured and closed; any new phase needs a separate operator brief.**

### P2-DIFF-4.11 Stage-A STOP-and-attribute and PRE-EXECUTION additive amendment (2026-11-14, session 01a1d998)

**MEASURED (the pre-registered Stage A baseline, executed on the committed sources at
`d276743b` — DIF05 `97610d42…7239e62c` 561 B, DIF06 `feb5e037…f90846` 460 B, encoding verified
CRLF-only, one `^Z`, `last3 = b'\r\n\x1a'`):**

- 8080 lane `pli80c.exe -d`: **rc 0 for BOTH** — `PROGRAM BILLING CODE=206 DATA=20 ITEMS=228 ->
  512 bytes`; `PROGRAM BATCH CODE=124 DATA=12 ITEMS=137 -> 384 bytes` (the pre-registered 8080
  acceptance, measured; logs `build/e54p2diff4/stageA/`).
- Native lane `pli80mir.exe --export <entry>`: **rc 2, ZERO stdout, NO `.mir`** — but the
  diagnostic is **`HIR-E18: line 5: MIR backend: a value-position call is outside the native
  subset (brief §3)`** (DIF05) / **`HIR-E18: line 6: …`** (DIF06), NOT the pre-registered
  `HIR-E19` on the `*`. The predicted refusal is **attributable to a different feature**: the
  §P2-DIFF-4.4 design text (`bill = capped_units(q + 0) * 500`) nests the `Call_e` inside a
  `Binop`, and the measured native subset — the m3c admission law VERBATIM at
  `mir_backend.ml` ~737 — admits a `Call_e` ONLY as the **whole RHS of an Assign to a `D_var`**
  (or the whole expression of the final `Return`); any other position keeps the pre-existing
  E18 refusal (the CALLN9 shape law). This is a SOURCE-DESIGN defect, not a hypothesis
  failure: H1/H2/H3 stand; the window reasoning below is unchanged. Per §P2-DIFF-4.5 the
  STOP-and-attribute fired; no refusal was manufactured; this amendment is the PRE-EXECUTION
  additive record that the operator's chronology requires, committed BEFORE any replacement
  source byte and before any compiler run on new bytes.

**AMENDED DESIGN (the ONLY change: the call moves to a whole-RHS assignment; the algorithm,
the entry names, the subsidiary names, the `+ 0` value-actual idiom, the `>`-oriented IFs, the
`put list` positions and BOTH pre-registered expectation vectors are UNCHANGED):**

- `DIF05.pli` (entry `billing`): `dcl q, cat, bill fixed bin(15);` then for each quantity
  3, 12, 30: `q = <k>;` `cat = capped_units(q + 0);` `bill = cat * 500;` `put list(bill);`
  `return (bill);` and the subsidiary `capped_units(x)`: `if x > 20 then c = 20; else c = x;`
  `return (c);` — the exact DIF03 (`pricing`) shape.
- `DIF06.pli` (entry `batch`): `dcl i, cl, v fixed bin(15);` `i = 1;` `do while (i < 5);`
  `cl = limited_step(i + 0);` `v = cl * 700;` `put list(v);` `i = i + 1;` `end;`
  `return (i);` and the subsidiary `limited_step(x)`: `if x > 12 then c = 12; else c = x;`
  `return (c);` — the exact DIF04 (`production`) shape.
- The superseded bytes `d276743b` remain in history as the measured evidence; the replacement
  sources are committed (again BEFORE any compiler run) with freshly recorded SHAs.

**CORRECTED PRE-REGISTERED NOTE (the §P2-DIFF-4.4 "honest note" was wrong in its arithmetic,
and the correction strengthens the attribution).** The context-independent summary of
`capped_units` is NOT `[1,20]`: the summary is computed with the FULL declared-formal seed
`W(15) = [-16383,16383]`, so the branch-insensitive hull of `c = 20` and `c = x` is
`[-16383, 16383]` — the FULL window — and the same for `limited_step`. Hence the pre-change
`cat`/`cl` carry the full window, the multiplication `cat * 500` / `cl * 700` is exactly the
pre-registered `HIR-E19` with the full-window operand, and the pre-registered products
`±16383*500 = ±8191500` and `±16383*700 = ±11468100` are the expected refusals. The
`[1,20]`/`[1,12]` reading was the value of `min` over the POSITIVE domain; the analysis
domains are the full declared windows.

**RE-MEASURED PREDICTION (binding for the amended Stage A):** `pli80c.exe -d` rc 0 (both,
unchanged); `pli80mir.exe --export <entry>` rc 2, ZERO stdout, NO `.mir`, EXACTLY
`HIR-E19: line 7: binop '*' on operands proved within [-16383,16383] and [500,500] can reach
[-8191500,8191500], leaving the declared-precision window [-16383,16383] of FIXED BINARY(15,0);
overflow behaviour is profile-UNKNOWN and is never assumed (brief §4)` for DIF05 and
`HIR-E19: line 8: … within [-16383,16383] and [700,700] can reach [-11468100,11468100] …`
for DIF06 (line numbers from the amended layouts above). Any other refusal ⇒ STOP again.

**POST-CHANGE EXPECTATION (Stage B, unchanged in substance):** the specialized summaries are
`[3,20]`, `[12,20]`, `[20,30]` (DIF05) and `[1,12]` (DIF06, the loop IV interval `[1,4]`
hulled with the `12` arm), giving `bill ∈ [1500,10000] ∪ … ⊆ W(15)` at every call site and
`v ∈ [700,8400]`; the whole program then admits; the console vectors stay
`[1500,6000,10000]` and `[700,1400,2100,2800]` — the pre-registered independent expectations.

### P2-DIFF-4.12 Dashboard row (CLOSED 2026-11-14)

**E2E-54/P2-DIFF-4 — CALL-SITE INTERVAL SPECIALIZATION — CLOSED.** Stages A (the E18
STOP-and-attribute, the §4.11 PRE-EXECUTION amendment, the amended refusal measured exactly:
`pli80c` rc 0, `pli80mir` rc 2 `HIR-E19` `±8191500`/`±11468100`), B (the module extension +
`lower_call_e` `(cell, iv)` capture; the refusals GONE rc 0), C (`mirsumtest` 116 checks — the
owed numbers MEASURED: DIF05 [3,3]/[12,12]/[30,30] → [3,20]/[12,20]/[20,30], DIF06 [1,4] →
[1,12], both context-independent summaries the full window; the tool 14), D (the measured-first
pins `DIF05.mir` 1887 B `3f9080f2…`, `DIF06.mir` 1182 B `be63ee89…`; `nfuncs` 2/2 MEASURED;
D10/D11 with the pre-registered vectors; the runner **10/10 BOTH-PASS in BOTH modes**, 37/37
controls REJECTED). The frozen panel green twice (after Stage C and after Stage D), every
baseline log `cmp`-IDENTICAL; the disclosed tool counts: `mir_numeric` 43→45,
`mir_return_summary` 11→14; `pli80c.exe` `172595d5…aca281` from a fresh build; `git diff
--exit-code -- hir/`/`-- ocaml/` rc 0; ledger 203/C380; ZERO oracle. Full record: RESULTS
§P2-DIFF-4. **STOP — any extension needs a NEW operator brief (§4.10).**
