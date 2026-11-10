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
| P1-mD | OPEN (pre-registration committed at `d48564b6` + this commit; probes hops 1–3 green except hop-2 bt, RESOLVED via `.debug_frame` read-back route hop 3) | native DWARF debugging of AOT MIR objects; D1/D2 SEPARATE; ZERO oracle; cosmo bt GREEN via named `.debug_frame` |
