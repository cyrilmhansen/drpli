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
| P1-b | **OPEN 2026-11-08** (operator-authorized; §P1-b pre-registered this commit) | (close: `build/gate-e54p1b-reg.log`, FROZEN counts) | ZERO oracle; seam module `ocaml/hir/semantic_env.ml`; `ocaml/lib/`+`ocaml/bin/` byte-clean mandatory |

