# E2E-54/P0 RESULTS — backend-neutral HIR foundation (zero-oracle slice)

Campaign **E2E-54** (brief recorded VERBATIM as §0 of `PLAN.md`, commit `c89a9df3`).
Phase **§P0** CLOSED **2026-11-08** at hop 4 (session chain `01a1bbbd` → `01a1bbe1` →
`01a1bc01` → this successor, renewals 1–3 of a cap-12 chain).

**Oracle runs this phase: ZERO.** No probe, no CP/M, no cpmsim, no LINK-80. No claim was
created or modified: `spec/CLAIMS.md` still has **203** `## C` headers, ending **C380**.
`spec/COVERAGE.tsv`, `spec/INVENTORY.txt`, `spec/census/`, every `golden/` directory,
`probes/`, `artefacts/`, `manuals/`, `extracted/`, `references/` and `oracle/disks/`
were not touched. `ocaml/lib/` and `ocaml/bin/` are byte-clean vs HEAD (verified
`git status --porcelain ocaml/lib ocaml/bin` empty at every hop close). No push.

## 1. What §P0 delivered (all NEW paths, zero historical bytes)

| file | role |
|---|---|
| `ocaml/hir/diagnostic.ml` (32 L) | typed stable-code diagnostics `HIR-E00..E11`; rendering pure (code + line + msg) |
| `ocaml/hir/target.ml` (101 L) | `Target.profile` with provenance per field (`Oracle_backed` / `Language_rule` / `Unknown`); profiles `dr-pli80-v1.4` + all-unknown `generic32-unspecified` (§P0.9) |
| `ocaml/hir/hir.ml` (233 L) | typed HIR: `ty`/`sym`/`scope`/`expr`/`stmt`/`proc`/`program` + deterministic dumper; NO byte size, offset, opcode, register, pool or address anywhere (§P0.3, F8) |
| `ocaml/hir/hir_build.ml` (780 L) | read-only adapter `(Ast.block × Bind.prog_layout) → Hir.program` for the P0 subset; loud refusal otherwise |
| `ocaml/hir/backend.ml` (60 L) | brief §7 `module type BACKEND` + `Null` witness + `Driver` functor + `module _ = Driver(Null)` compile-time test (hop 4) |
| `ocaml/hir/pli80hir.ml` (70 L) | CLI: dump on stdout rc 0; refusal ⇒ diagnostics on stderr, rc 2, ZERO stdout |
| `ocaml/hir/dune` | library `pli80_hir` + executable `pli80hir` (explicit `(modules …)`) |
| `hir/fixtures/H01..H05.pli` | fixture corpus (CRLF + bare `^Z`) |
| `hir/expected/H0{1..4}.txt`, `H05.stderr.txt`, `H05.rc` | reviewed expected dumps + pinned negative contract |
| `tools/hir_test.py` (229 L) | §P0.7 runner: expected-dump compare, double-run determinism, rc/stdout contract, F4 hex audit, F7/F8 greps (nested-comment strip), nonzero exit on failure |
| `docs/architecture/backend-boundary.md` | audit (draft `41dc2d2c`, finalised at this close) |

No historical pipeline file was rewired; `pli80c` never links `pli80_hir` (F1/F7).

## 2. Falsifier panel (pre-registered §P0.8) — every measured value

- **F1 historical binary invariance — PASS (after remedy).** First attempt MOVED
  `pli80c.exe` to `81d6122f07d290586064de8c47681a6a251c9d8aeac609dc1b4147899a1c5297`
  (+40 B, identical `nm` symbol count). Attributed FIRST-HAND (scratch T0–T3 trees from
  `git archive HEAD`): an extra **executable stanza in `ocaml/bin/`** moves EVERY bin exe
  — dune's per-scope `Dune__exe` alias (`bin/.pli80c.eobjs/dune__exe.ml-gen`) enumerates
  all exe roots of the directory, changing `pli80c.ml`'s own `.cmx/.o`. Hop-1/2 belief
  "unused units are never linked" **FALSIFIED for exe directories**; extra LIBRARY
  stanzas verified harmless (`pli80.cma/.cmxa` byte-identical). Remedy (hop 3): all new
  units + CLI into separate library dir `ocaml/hir/`; `ocaml/bin/dune` restored to HEAD
  exactly. Re-verified GREEN on fresh build dirs (`_build-e54p0h3b`, `_build`) and
  TWICE again at hop 4 (after the hir.ml indent edit, after `backend.ml`):
  `sha256 ocaml/_build/default/bin/pli80c.exe` =
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` (== kept
  `ocaml/_build-e53p4h15` exe == armed fingerprint of record). Drift evidence kept
  (ignored): `ocaml/_build-e54p0h3/…/pli80c.exe` = `ab02dbc523c9cc55bd34990027c2141ac8fb87c51f1acc74392bbd166dfd555d`.
- **F2 byte-tier gate rc 0, counts FROZEN — PASS.** `python3 tools/e2e_gate.py` rc 0
  DIRECT → `build/gate-e54p0-reg.log`: sweep **1328/1328** byte-exact, negative
  **190/190**, divergence **9/9**, coverage **149 rows 0 errors 0 warnings**, census
  **EXACT 16 / DIFFERS 0 / REFUSED 25 / UNEXPECTED 0 / NO_ORACLE 3**, prose **5**.
  ZERO movement — the prediction in §P0.8/F2 held; no wiring revert was needed.
- **F3 historical surfaces untouched — PASS** (measured at close, §"header" above):
  no modified tracked file under `golden/ spec/ probes/ artefacts/ manuals/ extracted/
  references/ oracle/disks/` (the `??` untracked `dir.txt`/`summary.txt` entries under
  `golden/` are pre-existing working state from E2E-52/53, never staged); ledger 203
  headers; `handoff.config.json` NEVER staged (operator edit stays dirty-in-tree).
- **F4 determinism + no address shapes — PASS.** `tools/hir_test.py` runs every fixture
  in TWO fresh processes and compares rc/stdout/stderr byte-for-byte (the CLI handles
  one file per process, so this subsumes the in-process dimension); all identical. Hex
  audit `[0-9a-f]{6,}` over every dump: ZERO matches against an EMPTY documented-value
  allowlist — no token in any dump can be an address, pid, timestamp or hash.
- **F5 stable identities — PASS.** sids are pure source order (ascending `sid` =
  pre-order bind rows). Scratch witness (kept out of the pre-registered 5-fixture set):
  swapping the two `dcl` lines of an H01-shaped program swaps `sym(0)/sym(1)` between
  `x` and `y` and every reference follows deterministically.
- **F6 no second binder — PASS (audit).** Every name→meaning channel in
  `hir_build.ml` reads bind-seeded structures: `resolve` walks `bi_syms` (built from
  `rows_of_block` over bind layout rows), proc lookup uses `procs_by_name` (from
  `plan.pl_procs`), formal/return facts from `pl_ret`/`pl_ptrs`; `find_dcl` flattens via
  `Bind.frame_decls` (bind's own flattener); `check_top_authority` is a consistency
  check over two bind views, not an independent resolution; name lowercase key uses
  `Bind.pl_l`. The `List.mem key formals` storage classifier consumes the AST's
  syntactic parameter list (position/ordering fact), while TYPE and existence still come
  from the bind row. No `List.assoc` re-resolution over raw AST names bypasses bind.
- **F7 separation — PASS.** After stripping nested `(* *)` comments, `codegen.ml`,
  `rel80.ml`, `pli80c.ml` contain ZERO hits for `\b(Hir|Hir_build|Target|Diagnostic|Backend)\b`
  (raw grep also zero — the stripper guards the *reverse* false-positive direction and
  is proven non-vacuous by a planted-violation control inside the test session).
- **F8 HIR purity — PASS.** After the same strip, all six `ocaml/hir/*.ml` units are
  clean of `\bRel80\b`, `\bCodegen\b`, `bytes_of`, `\bop_[a-zA-Z_]+`, `0x[0-9a-fA-F]+`,
  8080 mnemonics (`MOV|MVI|LXI|DAD|INX|DCX|PCHL|SHLD|LHLD|STA|LDA|CALL|JMP|XCHG|HLT|…`)
  and the byte-layout words `size|offset|reloc|pool`. `Hir.ty` carries precision+scale
  only. Documented exception: the dump string `"order: target address then value"` is an
  evaluation-order phrase in language terms; no numeric address ever appears in a dump
  (audited by F4), so `address` is deliberately NOT an F8 token.
  (`op_` patterns are word-anchored: unanchored `op_` false-positives on `relop_name`
  and `top_authority` — measured.)
- **F9 negative silence — PASS.** H05 (array `dcl`) refuses `HIR-E03: line 2: array
  declaration for a is outside the P0 subset`, rc **2**, stdout **0 bytes**, stderr
  byte-pinned in `hir/expected/H05.stderr.txt` with rc in `H05.rc`. The hop-2
  prediction (ddims guard fires at the `Sdcl` lowering, the dcl itself passing
  `register_block` as an element-RTbin row) was CONFIRMED by measurement.

## 3. Deviations and amendments vs PLAN §P0 (adopted-in-code, recorded here)

1. **Library name `pli80_hir`** (not `pli80hir`): an OCaml executable cannot reference a
   wrapped library of the same name it shadows — forced by measurement at hop 3.
2. **File-set relocation:** §P0.2 placed `hir/diagnostic/target/backend/hir_build.ml` in
   `ocaml/lib/` and `pli80hir.ml` in `ocaml/bin/`; ALL live in `ocaml/hir/` instead
   (F1 remedy §P0.8(1) executed; the exe-dir `Dune__exe` coupling LAW above is the
   reason). Mixed library+executable directory requires explicit `(modules …)` on both
   stanzas. `ocaml/lib/dune` and `ocaml/bin/dune` are at HEAD exactly.
3. **Precision-ceiling CLAMP (design amendment, hop 2):** a language-rule result
   precision above the profile ceiling (e.g. `bin(15)+bin(15)` → 16, or `15+15=30`) is
   CLAMPED to the profile ceiling and the clamp is named in the node's `typing`/`reason`
   string together with `DR intermediate typing unmeasured [TBD]`. Refusing instead —
   the original reading — made §P0.6's own fixture arithmetic (`i = i + 1`) unlowerable.
   NOT a DR claim; a future pre-registered experiment can revise the profile field only.
4. **BEGIN-inline lowering (F9-soundness amendment, hop 2):** a statement-level
   `Sproc` block with `Bbegin`/`Bdo` and NO declarations has its statements INLINED
   into the enclosing body (previously silently dropped); with declarations it refuses
   `HIR-E11` (per-block scoping not exposed by bind). Silent dropping was the failure
   mode this falsifier exists to catch.
5. **`find_dcl` real defect fixed (hop 3):** it read `blk.bdecls`, which is `[]` for the
   corpus statement-shaped declaration form (the `codegen.ml:15729` trap) — every SYM
   line silently fell back to the block line and names printed lowered-key. Fixed via
   `Bind.frame_decls`; witness `dcl Zz` → `name=Zz key=zz line=2`.
6. **CRLF law (fixture format):** fixtures are CRLF + bare `^Z` like every oracle
   specimen; with bare LF the lexer's CR counting shifts EVERY reported source line by
   −1 (LF-only FALSIFIED for position fidelity). `IF … THEN/ELSE` takes NO `end;`
   (anchor `artefacts/DEPREC.PLI:85`).
7. **Call-dump arg indent (adjudication, hop 4):** `arg N` and its expression printed
   at the SAME indent in the H03/H04 dumps; adjudicated to the nested shape — argument
   expressions dump at `indent + 2`, one level below their `arg N` label, in BOTH
   `Call_e` and `Call_s`; rule documented in the `hir.ml` header. Expected dumps
   regenerated from the rebuilt compiler (indent lines only; H01/H02 unchanged — no
   call nodes).
8. **Negative expected form:** §P0.6 left the H05 contract's file encoding open;
   `tools/hir_test.py` is data-driven — a fixture is positive iff `expected/<name>.txt`
   exists, negative iff `expected/<name>.stderr.txt` + `<name>.rc` exist (both pinned
   byte-exact).
9. **`ir.ml` untouched, unreferenced, never renamed** (§P0.3 commitment re-verified; it
   is the `$V` instrument and stays a separate scientific surface).

## 4. Fixture review (§P0.3 line-by-line, hop 4)

Every line of all five expected dumps was reviewed against §P0.3 before the fixtures
commit (`2504633a`): sids ascending pre-order; scopes (`SCOPE 1 parent=0 kind=proc(1)`);
`fixed` without args = `FIXED BINARY(15,0)` (bind `RTbin 15` — hop-2 discovery, so the
P401-shape H04 needed no downgrade); explicit `convert 15,0 -> 7,0` on `z = x + 1`
(operand ≠ target); single loop form pre-test `DO WHILE`; call args ordered
left-to-right, nested under their label; `return value` carries the expression; `stop`
statement; NO SSA, no register/byte vocabulary (F8 surface). H03 shadowing: outer `x`
sid 0 scope 0 vs inner `x` sid 3 scope 1, formal `p` sid 2 `storage=formal`; `g(x)`
resolves to `sym(0)` — correct scope attribution on every reference.

## 5. §P0.10 MIR study — `[TBD — lab not reachable]`

Checked WITHOUT network per §P0.10: no local clone of `cyrilmhansen/mir-madc-aot-lab`
exists in this environment (repo tree searched; `find /home/john -maxdepth 3 -iname
'*madc*'` empty; `thirdparty/` holds only `PLI-2000` and `z80pack`; the
`~/Téléchargements/mir-master*.zip` archives are an unrelated upstream Mir snapshot —
zero `madc` hits — and personal downloads are out of scope). No findings were consulted;
no dependency was added. Integration points for a future MIR layer remain the §5 list in
`docs/architecture/backend-boundary.md` (pre-registered, unchanged).

## 6. Migration roadmap (PROPOSED — P1 is NOT authorized; operator decision required)

Everything below is a PROPOSAL derived from the §1/§2 audit; NONE is started, and each
step requires its own pre-registration (and, where DR behaviour changes, its own oracle
campaign per PROTOCOL #1):

1. **P1-a (zero-oracle):** widen the HIR subset construct-by-construct (per-block BEGIN
   scopes once bind exposes them, arrays, PUT/GET statements), extending the fixture
   corpus each time; historical pipeline still untouched.
2. **P1-b (zero-oracle):** a read-only `Semantic_env` projection over `prog_layout`
   (types without offsets), shared by `Hir_build` — arch doc §7 item 1.
3. **P2 (needs a pre-registered oracle experiment FIRST):** measure DR's internal
   expression typing via `$V`-stream witnesses (`ir.ml` instrument) to replace the
   `Unknown` profile field — NEVER by analogy with emitted bytes.
4. **P3+ (byte-tier risk, budget separately):** a real `BACKEND` instance emitting REL
   records from HIR, validated by whole-file `cmp` against the kept goldens BEFORE any
   rewiring; `pli80c` stays on the historical path until a full campaign parities every
   panel. The safety list (arch doc §6) forbids refactoring `layout`, `lower_hl`,
   `rel80.ml`, `ir.ml` and the refusal surfaces without exactly such a campaign.

## 7. Reproduction (the §P0.7 command set)

```bash
cd ocaml && eval "$(opam env)" && dune build                # rc 0, ZERO Error
python3 tools/hir_test.py                                   # rc 0 (fixtures + F4/F7/F8/F9)
sha256sum ocaml/_build/default/bin/pli80c.exe               # 172595d52be44c9ead… (F1)
python3 tools/e2e_gate.py                                   # rc 0, frozen counts (F2)
```

## 8. Commits (explicit paths, hop order)

hop 1: `c89a9df3` (PLAN §0+§P0), `41dc2d2c` (audit draft).
hop 3: `10061276` (F1 remedy — `ocaml/hir/` library), `bb8793aa` (find_dcl fix),
`0356c44e` + `349266d3` (durables + guard g614).
hop 4: `65d21d47` (arg-indent adjudication), `2504633a` (fixtures + expected),
`b607c156` (`tools/hir_test.py`), `e6946096` (`backend.ml`), this close-out.

---

# E2E-54/P1-b RESULTS — Semantic Environment Projection (zero-oracle slice)

Phase **§P1-b** CLOSED **2026-11-08** at hop 4 (sessions `01a1bcc7` → `01a1bce0` →
`01a1bd02` → `01a1bd21`, renewals 1–3 of a cap-12 chain
`chain:01a1bcc7-fdf9-71ea-9e0a-5bfb1d8da449`). Pre-registered as PLAN §P1-b (operator
brief VERBATIM as §P1-b.0; authorization 2026-11-08); executed against starting reference
`aaf295f0257659c4b3bd8d070bd14a306cc36780`.

**Oracle runs this phase: ZERO.** No probe, no CP/M, no cpmsim, no LINK-80. No claim was
created or modified: `spec/CLAIMS.md` still has **203** `## C` headers, ending **C380**.
`spec/COVERAGE.tsv`, `spec/INVENTORY.txt`, `spec/census/`, every `golden/` directory,
`probes/`, `artefacts/`, `manuals/`, `extracted/`, `references/` and `oracle/disks/`
were not touched (S4/S9, verified first-hand at close: `git status --porcelain` shows
ZERO modified tracked file under those paths). `ocaml/lib/` and `ocaml/bin/` are
byte-clean vs HEAD at every hop close. No push.

## P1-b.1 What §P1-b delivered (brief Step 7 deliverables)

| deliverable | measured form |
|---|---|
| documented `Semantic_env` API | `ocaml/hir/semantic_env.ml` (**476 L**): read-only projection over `(Ast.block × Bind.prog_layout)`; own `stype` (physical components dropped at the boundary), `symbol`/`proc_sig`/`block_env`/`entry_sig`; typed `Not_found of {scope}` vs `None`; `epr`/`sret_pr` carry `Bind.rty_str` VERBATIM; NO `Hir` type in the interface; full surface contract in PLAN §P1-b.2 (with the one documented amendment,
§P1-b.5 note 1 below) |
| migrated HIR construction path | `ocaml/hir/hir_build.ml` **625 L** (was 780 at `aaf295f0`; migration commit `dfe1435a` = +225/−380 = **−155 net**): all table-reconstruction machinery moved behind the env; only Bind reference left is the alias (`:41`) + one `Bind.bind_program` call (`:557`); subset gate `ty_of_rt : SE.stype -> ~pr -> …`, eager sid-ordered `Hir.sym` projection, all lowering, typing and diagnostic texts UNCHANGED |
| semantic-authority tests | `ocaml/hir/semtest.exe` (**455 L**, in `pli80_hir` dir — P0 F1 exe-dir law): 7 invariants judged against the LIVE env and bind rows, never dump text; `--corrupt` non-vacuity control |
| targeted negative fixtures | `hir/fixtures/H06.pli` (`dcl c char(3);` → `HIR-E02` quoting bind's own `CHAR(3)`) and `H07.pli` (formal `q` with no dcl → `HIR-E03` "produced no bind row"), both CRLF+`^Z`, rc-pinned negatives (`acd7955e`) |
| before/after dependency map | §P1-b.2 below |
| unexposed-fact list | §P1-b.4 below (PLAN §P1-b.6 carried VERBATIM) |
| proposed P1-a order | §P1-b.5 below — **PROPOSED ONLY; P1-a is NOT authorized and was NOT started** |
| test-runner extension | `tools/hir_test.py` (now **332 L**): semtest live+corrupt ×2 per positive fixture (S6/S7), F10 Bind-seam grep (pins the EXACT two lines), S8 env-independence grep |

## P1-b.2 Before/after dependency map (audit §P1-b.1, measured outcome)

| audit site | machinery at `aaf295f0` (before) | after migration |
|---|---|---|
| 4 `rows_of_block` | bind rows re-keyed per block, offset dropped in `hir_build` | deleted; `Semantic_env.create` owns row projection (`esyms`, bind order) |
| 6 `find_dcl` | `Bind.frame_decls` scan + key policy in `hir_build` | deleted; `Semantic_env.find_dcl` (same bind channel, same `Bind.pl_l` key) |
| 11 `resolve` | parent-chain walk over private `bi_syms` tables | deleted; `Semantic_env.resolve` (chain = AST nesting shape [O] over bind rows [P]) |
| 14 `procs_by_name` | private name→pid registry assembled in `hir_build` | deleted; `Semantic_env.procedure` + `blocks`/`main_block`/`block_of_pid`/`enclosing` |
| 15 `lower_call` bind reads | direct `pl_ptrs`/`pl_ret`/`pl_rec`/`pl_attr_rec` reads | deleted; `Semantic_env.signature` (`sptrs`/`sptr_count`/`sret`/`srec`/`sattr_rec`) |
| 16 `params_of` | AST `bparams` → sids via private block tables | `block_env.eformals` + `esyms`; the HIR-E03 "explicit formal dcl required in P0" refusal stays in the CONSUMER (typed missing-information honouring, message unchanged) |
| 1/2/3/9/10/17 | authority call, top-proc identity, guards, Auto/Static, `ty_of_rt`, `Sdcl` guards | unchanged classes: [P] facts now read through the env; the **subset gate stays in `Hir_build`** |
| 18 literal/arith typing | `Language_rule` profile logic, NOT bind | unchanged in the consumer (§P1-b.5 audit: three layers stay separated; zero typing edits this phase) |

**Class [D] result (stated honestly, as pre-registered): NONE.** P1-b removes
*table-reconstruction machinery*, not duplicate semantic resolution — P0 F6 had already
established no second resolver exists. The phase's measurable gain is ownership and
testability: one module owns the reconstruction sites and is judged directly against bind
by `semtest` (7 live invariants), with the dump/diagnostic bytes frozen across the seam
(S2/S10).

## P1-b.3 Falsifier panel (pre-registered §P1-b.7) — every measured value

- **S1 historical binary — PASS.** `pli80c.exe` sha256
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held after EVERY
  build-touching step (after the `semantic_env` stanza, after the migration, after the
  `semtest` exe stanza) AND at close on the FRESH build dir: `build/e54p1b-freshbuild.log`
  (`dune build --build-dir _build-e54p1b`) rc **0**, ZERO `Error`, hist **122** warning
  headers (baseline count), and `sha256sum
  ocaml/_build-e54p1b/default/bin/pli80c.exe` re-computed first-hand at hop-4 close ==
  `172595d5…` (identical to `_build/default`). The log itself records only rc + headers;
  the sha is verified against the kept exe — a fresh-dir log never prints it.
- **S2 expected dumps frozen — PASS.** `git diff --exit-code -- hir/expected/` rc **0**
  THROUGH the migration and at close; H01–H05 stdout compared byte-for-byte every run:
  H01 **1753 B**, H02 **1808 B**, H03 **1608 B**, H04 **1090 B**. The seam is
  behaviour-preserving to the byte.
- **S3 full gate — PASS, ZERO movement.** `python3 tools/e2e_gate.py` rc **0 DIRECT** →
  `build/gate-e54p1b-reg.log`: sweep **1328/1328** byte-exact, negative **190/190**,
  divergence **9/9**, coverage **149 rows 0 errors 0 warnings**, census **EXACT 16 /
  DIFFERS 0 / REFUSED 25 / UNEXPECTED 0** (NO_ORACLE 3), prose **5**. All FROZEN counts
  hit exactly (§P1-b.9 prediction confirmed; no wiring revert needed).
- **S4 historical surfaces untouched — PASS.** `ocaml/lib/`, `ocaml/bin/`, `golden/`,
  `spec/` ledgers, `probes/`, `artefacts/` show ZERO modified tracked files at close
  (verified first-hand); ledger **203** headers ending **C380**; `handoff.config.json`
  NEVER staged (operator edit stays dirty-in-tree).
- **S5/F10 Bind seam — PASS.** After nested-comment strip, `hir_build.ml` references
  `Bind` at EXACTLY two lines, pinned by name in `tools/hir_test.py`: `:41`
  `module Bind = Pli80.Bind` (alias) and `:557`
  `let plan = Bind.bind_program blk in` (the single authority call). `semantic_env.ml`
  is the only HIR-path reader of bind layout fields.
- **S6 semantic authority — PASS.** `semtest.exe` per positive fixture (run twice,
  see S7): H01 `SEMANTIC-AUTHORITY OK 4 refs / 3 syms`, H02 `7 refs / 2 syms`,
  H03 `7 refs / 4 syms`, H04 `4 refs / 2 syms` — all rc **0**. Non-vacuity control:
  `--corrupt` FAILS loudly on every fixture — rc **1**, one `SEM-FAIL` line on stderr,
  **ZERO stdout** (never prints OK).
- **S7 determinism — PASS.** Every fixture AND every semtest run executes in two fresh
  processes with byte-identical rc/stdout/stderr (subsumes the in-process dimension,
  same contract as P0 F4).
- **S8 env independence + purity — PASS.** `semantic_env.ml` code (comment-stripped)
  contains no `\bHir\b` reference — the env is IR-independent — and passes all F8
  byte-layout patterns; `tools/hir_test.py` F8 now sweeps **8** `ocaml/hir/*.ml` files,
  all clean of 7 patterns; F7 separation re-verified (3 historical files, 5 patterns).
- **S9 zero oracle / no promotion — PASS.** No oracle call; no claim; no coverage row;
  no inventory/census/goldens touch (see header).
- **S10 diagnostics byte-identical — PASS.** Positive fixtures produce NO diagnostics
  (S2 covers their stdout bytes); negatives are byte-pinned stderr + rc 2 + ZERO
  stdout: H05 `HIR-E03: line 2: array declaration for a is outside the P0 subset`,
  H06 `HIR-E02: line 2: declared type CHAR(3) for c is outside the P0 HIR subset
  (FIXED BINARY scalars only)` (bind wording via the carried `epr`), H07
  `HIR-E03: line 5: explicit formal dcl required in P0: parameter q produced no bind
  row`. `SEM-FAIL` texts come from the test binary, not the compiler path.
- **Predicted drift (PLAN §P1-b.3 note) — NOT EXPOSED.** The adjudicated multi-refusal order
  drift (registration guards now run in `env.create` before subset projection) requires
  a program combining two independent refusals; none of H01–H07 does (each negative is
  single-refusal). Every frozen byte held; nothing had to be re-adjudicated.

## P1-b.4 Facts Bind still does NOT expose (PLAN §P1-b.6, carried VERBATIM)

1. Parent/child procedure edges (flat `pl_procs`) — nesting shape read from the AST [O].
2. Per-`BEGIN` scoping — bind merges BEGIN/DO declarations into the frame block (HIR-E11
   refusal retained unchanged).
3. Expression result typing (arch doc §1.3) — no bind function types an expression.
4. Qualified/suffix use resolution — lives in codegen (`resolve_suffix`), out of env scope.
5. INITIAL values, EXTERNAL static/varying descriptor detail, ON-unit facts (`pl_on` exists
   in bind but is NOT projected by P1-b — documented exclusion).
6. sid/scope/pid identity — an interface contract, not a bind fact.

Each is a documented gap; none was inferred into the interface.

## P1-b.5 Measured notes (recorded, NOT fitted)

1. **`SFormat` amendment to the projection surface.** The pre-registered `stype` has no
   constructor for `Bind.RTformat`, but `type_of_rt` must be TOTAL (a total projection is
   the contract's own requirement). One constructor `SFormat` was added **by amendment**
   — the mechanism §P1-b.2 itself prescribes ("additions only by amendment") — documented
   at the module head and in the hop-2 commit (`512d939f`). No behaviour depends on it in
   the P0/P1-b subset (formats still refuse through the subset gate).
2. **OCaml record-field evaluation-order law (H07 measurement).** The first H07 draft
   had the procedure BODY read the undeclared formal `q`; it died **`HIR-E06` (use line,
   undeclared name) BEFORE** the intended `HIR-E03` — OCaml does not guarantee that
   record fields evaluate left-to-right, so a `block_info` construction may lower `body`
   before `params = params_of bi`. Measured IDENTICAL on the pre-migration `aaf295f0`
   tree ⇒ pre-existing at P0 hop-2 code, NOT P1-b drift. Recorded, NEVER fitted: the
   final H07 body does not reference `q`, so the typed missing-information refusal
   (`HIR-E03 … produced no bind row`) is the honest first diagnostic. Consequence: on
   this path, multi-defect programs can report either diagnostic first; which one is
   OCaml-eval-order-dependent, and that is a *consumer* property, not a bind fact.
3. **Bare BEGIN/DO blocks HANG `register_children` (pre-existing defect).** A
   statement-level `begin; … end;` (parser `parse_begin_block` → `Ast.Sproc` with
   `bkind = Bbegin`) makes the non-Bproc discovery branch recurse on the ENCLOSING
   block's own statement list, re-reading the same `Sproc` forever: timeout rc **124**,
   no stack growth; with a preceding Bproc sibling it first yields a bogus
   `duplicate internal procedure name` refusal. Measured IDENTICALLY on the
   pre-migration `aaf295f0` scratch build and the migrated path
   (`build/e54p1b3-scratch/BEG1.pli`, ignored) ⇒ **PRE-EXISTING** (P0 hop-2 code,
   carried verbatim through the migration), NOT P1-b drift. Recorded per the `nelem=1`
   law — never silently fixed in a refactor slice; repair = proposed hygiene slice.

## P1-b.6 P1-a proposed order (PROPOSED — NOT authorized, NOT started)

Derived from §P1-b.1/§P1-b.4; each construct needs its own pre-registration and, where
DR behaviour is in question, its own oracle campaign (PROTOCOL #1):

1. **Arrays** — bind already carries element rows and dims through `esyms`/
   `find_dcl`; needs an HIR `ty` extension + fixtures first (no new bind facts required).
2. **PUT/GET statements** — statement surface only; word-by-word against existing
   codegen evidence already claimed (C159..C380 family).
3. **Per-block BEGIN scopes** — BLOCKED by unexposed fact 2; requires either a bind-side
   projection of frame block structure (a separate pre-registered phase) or an explicit
   [O] organization contract in `Semantic_env` read from the AST — never inference.
4. The FIXED intermediate-typing question stays with P2 (oracle `$V` witnesses), NOT P1-a.

## P1-b.7 Reproduction (the §P1-b regression set)

```bash
cd ocaml && eval "$(opam env)" && dune build              # rc 0, ZERO Error
python3 tools/hir_test.py                                 # rc 0: H01–H07, semtest live+corrupt ×2, F4/F7/F8/F9/F10/S8
sha256sum ocaml/_build/default/bin/pli80c.exe             # 172595d52be44c9ead…  (S1)
cd ocaml && dune build --build-dir _build-e54p1b          # rc 0 (S1 fresh dir; log build/e54p1b-freshbuild.log)
python3 tools/e2e_gate.py                                 # rc 0, frozen counts (S3; log build/gate-e54p1b-reg.log)
grep -c '^## C' spec/CLAIMS.md                            # 203, last header C380 (S4/S9)
```

## P1-b.8 Commits (explicit paths, hop order)

hop 1: `a2e4f62c` — §P1-b pre-registration in PLAN (operator brief VERBATIM, 19-site
audit, API contract, S1–S10 falsifiers) at the `aaf295f0` baseline.
hop 2: `512d939f` (`semantic_env.ml` + dune modules, SFormat amendment),
`dfe1435a` (migration, −155 net, S1/S2/S5 green), `acd7955e` (H06/H07 measured pins).
hop 3: `00a58a44` (`semtest.exe` + `hir_test.py` extension), gate + fresh-build logs
(ignored evidence under `build/`), durables `3afdd9ee` + `00c7ade8`.
hop 4: this close-out (RESULTS §P1-b + arch §7-1 + PLAN dashboard CLOSED) + durables.

---

# E2E-54/P1-a1 RESULTS — Arrays and Addressable References (zero-oracle slice)

Phase **§P1-a1** CLOSED **2026-11-09** at hop 3 (sessions `01a1bd4d` → `01a1bd6f` →
`01a1bd86` → `01a1bd9f` → this session, renewals 1–4 of cap 12, chain
`chain:01a1bd4d-a12c-73ad-8fbc-6a67fb7548e7`). Pre-registered as PLAN §P1-a1 (operator
brief VERBATIM as §P1-a1.0, commit `00276d4d` — the PROTOCOL #1 gate landed BEFORE any
`ocaml/hir/` byte); executed against starting reference `55a357e5`.

**Oracle runs this phase: ZERO.** No probe, no CP/M, no cpmsim, no LINK-80. No claim
created or modified: `spec/CLAIMS.md` still has **203** `## C` headers, ending **C380**
(verified first-hand at close). `spec/COVERAGE.tsv`, `spec/INVENTORY.txt`, `spec/census/`,
every `golden/`, `probes/`, `artefacts/`, `manuals/`, `extracted/`, `references/`,
`oracle/disks/` untouched; `ocaml/lib/` and `ocaml/bin/` byte-clean vs HEAD at every step
(T4). No push.

## P1-a1.1 What §P1-a1 delivered

| deliverable | measured form |
|---|---|
| env array projection | `ocaml/hir/semantic_env.ml` (**561 L**): `SArray1{elem;lo;hi}` stype (NEVER produced by `type_of_rt` — bind rows carry the ELEMENT type, fact A-1), `array1`/`e_array` merged by lowered key from `Bind.bind_arrays` per block (A-8/A-13), physical element width DROPPED at first touch in `arrays_of` (T6), split-channel guards on `HIR-E14` (UNEXERCISED by any probe, recorded honestly like the P0 dup_free witness), `pp_stype … ARRAY[lo:hi]`; sid/scope/pid assignment UNCHANGED |
| HIR nodes | `ocaml/hir/hir.ml` (**324 L**): `ty Array1{elem;lo;hi}`, `Elem_read`/`Elem_ref`, `target = T_var | T_elem` (AMENDMENT beyond the predecessor's constructor list — internal, dumps frozen), syms-threaded dump + `dump_target`, bounds printed, NEVER a byte count (F4/T6) |
| build gate + lowering | `ocaml/hir/hir_build.ml` (**774 L**, commit `e9990241`): `project_syms` e_array branch on the shared add emitter (scalar gate byte-identical, H06 pin holds); band gate bin(7..15) elements else E02 array wording; `lower_index` const range-check E12; `lower_array_ref` E12/E14; Sassign via `assign_value` with `T_var`/`T_elem`; ddims guard NARROWED to dims-without-record (E03 text byte-identical, H10 pin); F10 seam still EXACTLY the two pinned Bind lines |
| diagnostics | `diagnostic.ml` appended stable codes `HIR-E12 e_index` / `HIR-E13 e_whole_array` / `HIR-E14 e_dims`; existing codes never changed meaning (T10) |
| fixtures | **7 positive** (H01–H05, H08, H09) + **7 negative pins** (H06, H07, H10–H15) — H08..H15 CRLF+^Z, ONE refusal path each, expected files COPIES OF MEASURED OUTPUT (`32cc4373`); H05 flipped negative→positive via `git mv` into `hir/expected/superseded/2026-11-09/` + dated README; superseded bytes never rewritten |
| semantic authority | `ocaml/hir/semtest.ml` (**734 L**, `1399ff1a`): I1 array-aware; I8 reference soundness (base resolves at the REFERRING scope, node `ex_ty` = env element image, no `Var` carries `Array1`); I9 bound preservation (3-tuple compare vs LIVE `Bind.bind_arrays`, esz dropped); I10 projection completeness; THREE corrupt controls |
| test runner | `tools/hir_test.py` (**409 L**): positives × CLI×2 + semtest LIVE + ALL THREE corrupt modes ×2 fresh processes; T5 raw `bind_arrays` reader grep; T6 strip-grep |

## P1-a1.2 Falsifier panel (pre-registered §P1-a1.8) — every measured value

- **T1 — PASS.** `pli80c.exe` sha256 held after every step; full
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held after EVERY
  build step (steps 2/3+4/6) checked DIRECT, and at close: fresh
  `dune build --build-dir _build-e54p1a1` rc **0**, ZERO `Error`, hist **122** headers
  (`build/e54p1a1-freshbuild.log` records rc+headers only; sha re-computed first-hand ==
  kept exe — fresh-dir logs never print it).
- **T2 — PASS.** `git diff --exit-code -- hir/expected` rc **0** at every step: H01
  **1753 B**, H02 **1808 B**, H03 **1608 B**, H04 **1090 B**, H06/H07 stderr pins frozen;
  the ONLY adjudicated change is the H05 flip (new `H05.txt` **497 B**, `elem_ref
  sym(0)[1:5]` at the statement line).
- **T3 — PASS, ZERO movement.** `python3 tools/e2e_gate.py` rc **0 DIRECT** →
  `build/gate-e54p1a1-reg.log`: sweep **1328/1328** byte-exact, negatives **190/190**,
  divergence **9/9**, coverage **149 rows 0 errors 0 warnings**, census **16/0/25/0**
  (NO_ORACLE 3), prose **5**. All FROZEN counts hit exactly (§P1-a1.10 prediction
  confirmed; no wiring revert needed).
- **T4 — PASS.** `ocaml/lib/`, `ocaml/bin/`, `golden/`, ledgers byte-clean vs HEAD at
  every step (verified first-hand); ledger **203** headers ending **C380**; ZERO oracle.
- **T5 — PASS.** F10: `hir_build.ml` mentions `Bind` only at `:41` alias + the one
  `bind_program` call. `grep -rn bind_arrays ocaml/hir ocaml/bin` (RAW, comments
  included) → readers EXACTLY `semantic_env.ml` + `semtest.ml` (the test binary is the
  intentional authority reader, §P1-b.4 law).
- **T6 — PASS.** After nested-comment strip, `semantic_env.ml` and `hir.ml` contain NO
  `\b(stride|offset|bytes|esz|size|reloc|pool)\b` and NO `0x`; dumps print bounds only.
- **T7 — PASS.** Live: H01 `4 refs / 3 syms`, H02 `7/2`, H03 `7/4`, H04 `4/2` (UNCHANGED
  from P1-b), H05 `1/1`, H08 `7/3`, H09 `3/2` — all rc **0**, stderr empty. Corrupt:
  `--corrupt` rejects the wrong sid everywhere (I1 comparison); `--corrupt-array-hi`
  rejected (`bind records [a[1:5]], env projects [a[1:6]]`) on H05/H08/H09 and printed
  `nothing was proven` on H01–H04; `--corrupt-array-base` rejected (`element base sym(1)
  (i) carries no array record`) on H08/H09 and printed `nothing was proven` on H01–H04
  (no element reference) and H05 (no non-array symbol). Every corrupt run: rc **1**,
  ZERO stdout, all-`SEM-FAIL` stderr.
- **T8 — PASS.** Every fixture and every semtest invocation ×2 fresh processes, rc +
  stdout + stderr byte-identical (the runner's determinism arms).
- **T9 — PASS.** `timeout 60` per fixture/semtest run throughout; the pre-existing
  BEGIN/DO discovery hang stays DOCUMENTED, classified pre-existing at `aaf295f0`, NOT
  fixed in this slice.
- **T10 — PASS.** H01–H04/H06/H07 bytes frozen (T2); H10 E03 array-decl text
  byte-identical to the old H05-era wording; every NEW refusal carries a NEW stable code
  pinned from measurement: H11 E02 array wording, H12 E12, H13 E13, H14 E14 (`2
  subscript(s)`), H15 E12 out-of-range at statement line 4.

## P1-a1.3 Deviations and measured notes (recorded, NOT fitted)

1. **FALSIFIED predecessor checkpoint claim:** the hop-3 `hir.ml` draft was NOT
   "COMPLETE on disk" — the tree DID NOT BUILD (`List.assoc_opt` vs `sym list`, two
   mojibaked `§`, semtest Warning 8); mechanically fixed at `e9990241`. LEARNINGS law:
   a checkpoint claim is a PROPOSAL until a build says otherwise.
2. **§P1-a1.6 prediction FALSIFIED by measurement (confirmed):** H08 has NO Convert —
   `t + 1` is type-equal to the bin(15) element after the precision CLAMP; H09 is the
   Convert witness (const `3` : bin(15,0) → bin(8) element). Pinned from output.
3. **H14 parse UNPROVEN in the contract → RESOLVED by measurement:** a 2-subscript use
   PARSES (as `Esuffix` with 2 args) and dies E14 exactly as pre-registered.
4. **Registration-order law (H11):** `project_syms` precedes lowering, so an out-of-band
   array element yields a SINGLE E02 (array wording) — the §P1-b.3 drift class stayed
   unexposed because every negative fixture carries exactly ONE refusal path.
5. **Steps 3+4 landed in ONE commit** (`e9990241`): the `Assign.target` type change
   breaks its consumers — the work order's per-step commits were impossible without a
   non-building intermediate; deviation named in the commit message.
6. **`diagnostic.ml` paired with step 2**, not step 4 (§P1-a1.9): the env guard needs
   `e_dims` when the projection lands — recorded deviation.
7. **e_unresolved defensive choice (unspecified in the contract):** an unresolved
   `Esuffix` assignment target rides the existing NO-bind-row channel; no fixture
   reaches it (UNEXERCISED, like the split-channel guards).
8. **KNOWN RED → resolved honestly:** the step-3 tree shipped with `hir_test.py` RED
   9× (semtest/live on H05/H08/H09 — I1 not array-aware); step 4 fixed the TEST (the
   projection was already correct), rc 0, no expected byte was touched.
9. **I8 `T_elem` carries no node type** (§P1-a1.3 representation choice): the shared
   `elem_ref_mismatch` checks base soundness and skips the element-image check
   (`ety = None`) for targets — live and corrupt-array-base run THE SAME code.
10. **Two build warnings fixed in-stream** (`write` field made read via the I8
    message; dead `found` binding dropped) — tooling hygiene, no behaviour content.

## P1-a1.4 Facts Bind still does NOT expose (carried, unchanged from §P1-b.4, plus)

7. Index-expression typing/bounds checking — bind records NOTHING about subscripts
   (A-4/A-9); the E12 constant range-check is a documented HIR-side rule, DR
   out-of-range behaviour UNMEASURED `[TBD]`.
8. Descriptor/actual array passing — out of the P1-a1 subset; array actuals refuse
   through the existing call gates (future slice).
9. `esz`/placement — dropped at the projection boundary BY LAW (T6); HIR arrays are
   semantic (element type + declared bounds) only.

## P1-a1.5 Reproduction (the §P1-a1 regression set)

```bash
cd ocaml && eval "$(opam env)" && dune build              # rc 0; exe 172595d5… (T1)
python3 tools/hir_test.py                                 # rc 0: H01–H09,H10–H15 pins,
                                                          # semtest live+3 corrupt ×2,
                                                          # F4/F7/F8/F9/F10/S8 + T5/T6
python3 tools/e2e_gate.py                                 # rc 0 frozen 1328/190/9/149-0-0/16-0-25-0/5
cd ocaml && dune build --build-dir _build-e54p1a1         # rc 0 ZERO Error hist 122
grep -c '^## C' spec/CLAIMS.md                            # 203, ending C380
```

## P1-a1.6 Commits (explicit paths, hop order)

hop 1: Phase-1 measurement (A-1..A-9 + scratch probe, `build/p1a1-probe-1.log` ignored);
hop 2: band measurement A-10..A-17 + **§P1-a1 PRE-REGISTRATION `00276d4d`** (+ durables
`7a418c47`); hop 3: `3c4a2a25` (env projection + `e_dims`), `e9990241` (hir nodes +
build gate, ONE commit, includes the non-building-draft fixes), `32cc4373` (fixtures
H08..H15 + H05 flip); this session (hop 3-steps-completion): `1399ff1a` (§P1-a1.7
semtest I1/I8/I9/I10 + 3 corrupt modes + hir_test T5/T6), gate + fresh-build logs
(ignored evidence under `build/`), then this close-out (RESULTS §P1-a1 + arch §7-2 +
PLAN dashboard CLOSED) + durables.

## P1-a1.7 Roadmap (PROPOSED ONLY — operator decision governs)

PUT/GET statements; BEGIN/DO hygiene repair (pre-existing hang); MIR lab (still
`[TBD — lab not reachable]`). NONE is authorized by this close; each needs its own
pre-registration (PROTOCOL #1). **STOP after P1-a1 closure.**

---

# E2E-54/P1-a2 RESULTS — Procedure Arguments and Indirect References (zero-oracle slice)

Phase **§P1-a2** CLOSED **2026-11-10** (sessions `01a1beba` → `01a1beca` → `01a1bee4` →
`01a1bf03` → `01a1bf18` → `01a1bf2e` → `01a1bf4a` → `01a1bf62` → `01a1bf74` → hop 10 →
`01a1bfa3` → this close session; chain `chain:01a1beba-124f-74ee-84fe-84e837f466b2`,
renewals 0–11 of cap 12). Pre-registered as PLAN §P1-a2 (operator brief VERBATIM as
§P1-a2.0, commit `3446dd85` — the PROTOCOL #1 gate landed BEFORE any `ocaml/hir/` byte);
executed against starting reference `b716daf0`.

**Oracle runs this phase: ZERO.** No probe, no CP/M, no cpmsim, no LINK-80. No claim
created or modified: `spec/CLAIMS.md` still has **203** `## C` headers, ending **C380**
(verified first-hand at close). `spec/COVERAGE.tsv`, `spec/INVENTORY.txt`, `spec/census/`,
every `golden/`, `probes/`, `artefacts/`, `manuals/`, `extracted/`, `references/`,
`oracle/disks/` untouched; `ocaml/lib/` and `ocaml/bin/` byte-clean vs HEAD at every step
(T4). No push.

## P1-a2.1 What §P1-a2 delivered

| deliverable | measured form |
|---|---|
| evidence matrix | PLAN §P1-a2.1: the brief's 8 parameter-semantics questions classified [bind-fact]/[language-rule]/[DR-ABI-backed]/[unmeasured] with measured CLAIMS anchors (C093 `:859`, C130 `:2036`, C145 `:2668`, C167 `:3196`, C175 `:3415`, C358 `:8480`); standing law: every `cs_*`/`pl_ptrs` int is PHYSICAL and never crosses the seam |
| adjudication | §P1-a2.2 (brief §2): `args left-to-right` KEPT — DR-ABI-BACKED as an EMISSION-order fact [C093]; language-level evaluation order remains [unmeasured] [TBD]; H01–H15 bytes stay frozen, `hir.ml` header carries the adjudication |
| env parameter API | `ocaml/hir/semantic_env.ml` (**756 L**, `426293dd`): `passing_mode` symbolic classifier (PM_value_cell/PM_own_cell/PM_immediate/PM_copy_in/PM_unknown; copy-in > recorded-cell > syntax; inconsistency ⇒ PM_unknown, never a guess); `call_site` projection built ONCE at `create` — `cs_slot` DROPPED UNREAD, `cs_temps` Some⇒bool, `cs_dec` as-is, `cs_args` PHYSICAL nodes for identity matching only; `call_evidence` first-DFS-site match by callee key + `(==)` node list (typed None ⇒ E16 at lowering); `formal_desc`/`sformals`/`formals_of` via callee-OWN-esyms resolution (C358 shadow law) |
| HIR representation | `ocaml/hir/hir.ml` (**398 L**, `cfaad741`): `designator = D_var{sid} | D_elem{base;subs}` (`target = designator` rename of P1-a1 `T_var/T_elem`, DUMP BYTES UNCHANGED); `actual_form = A_value of expr | A_reference of designator` — by-value CANNOT masquerade as reference by construction; `actual {af;ac_ty;ac_ef;ac_line}`; shared `dump_designator`/`dump_actual` |
| lowering | `ocaml/hir/hir_build.ml` (**1042 L**, `cfaad741` + `735b43af`): MODE-FIRST `lower_actual`, evidence-driven `lower_args` (typed absence ⇒ E16, never positional-guess), frozen `lower_call` refusal order, NEW statement-position Esuffix arm ⇒ `Call_s` (E04 kept for non-procedure heads; Eident zero-arg route untouched, `args=[]`-guarded); Bind seam still EXACTLY alias + one `bind_program` (F10) |
| diagnostics | `diagnostic.ml` (**62 L**): NEW stable codes `HIR-E15 e_arg_whole_array` / `HIR-E16 e_arg_evidence` (UNEXERCISED defensive witness, no fixture by design) / `HIR-E17 e_arg_type`; E13 keeps its P1-a1 meaning; H19's whole-array actual moved E13→E15 as pre-registered |
| fixtures | **11 positive** (H01–H05, H08, H09, H16, H17, H18, H21) + **10 negative pins** (H06, H07, H10–H15, H19, H20) — H16–H21 MEASURED (`96e995fd`), CRLF+^Z, expected files COPIES OF REVIEWED MEASURED OUTPUT; every dump line checked against §P1-a2.4 BEFORE pinning |
| semantic authority | `ocaml/hir/semtest.ml` (**1501 L**, `735b43af`): I11 designator soundness (`var_mismatch` extracted from I2 and REUSED verbatim; `e_array = None` clause; `elem_ref_mismatch` shared with I8); I12 passing-evidence alignment (`arg_evidence_mismatch`: key equality → `ce_args` length → `sptr_count` → `ce_dec` length → positional mode law); I13 formal-API alignment (`formals_mismatch`: length, `f_pos = i`, `f_key` vs syntax, `f_sid` vs `params[i]`, `f_stype` vs env row); `collect_calls` AST↔HIR 1:1 lockstep walker (the PHYSICAL-node pairing the env needs); SEVEN corrupt modes, each running THE SAME comparison function as its invariant |
| test runner | `tools/hir_test.py` (**438 L**): `SEM_MODES` ×7 on EVERY positive; T5 extended RAW grep list `pl_calls|cs_temps|cs_copies|cs_dec|bind_arrays` (readers ONLY `semantic_env.ml`+`semtest.ml`) + `cs_slot` NOWHERE in `ocaml/hir`; F8 vocabulary strip-grep extended to the new semtest strings |

## P1-a2.2 Falsifier panel (pre-registered §P1-a2.8) — every measured value

- **T1 — PASS.** `pli80c.exe` sha256
  `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held after EVERY
  build step (recorded at hops 2/3/4/5/6/7/9/10/11, each checked DIRECT — dune logs never
  print the sha) and re-verified first-hand at this close; fresh
  `dune build --build-dir _build-e54p1a2` exe sha == kept exe (computed separately, below).
- **T2 — PASS.** `git diff --exit-code -- hir/expected` rc **0** at every step and at close:
  H01 **1753 B**, H02 **1808 B**, H03 **1608 B**, H04 **1090 B**, H05 **497 B** (P1-a1 flip)
  and H06–H15 pins FROZEN through every type change; `superseded/` never rewritten. The
  six NEW files (added at `96e995fd`, frozen since): H16.txt **2572 B**, H17.txt **2173 B**,
  H18.txt **1509 B**, H21.txt **1188 B**, H19.stderr.txt **211 B**, H20.stderr.txt **163 B**.
- **T3 — PASS, ZERO movement.** `python3 tools/e2e_gate.py` rc **0 DIRECT** →
  `build/gate-e54p1a2-reg.log` (1537 lines): sweep **1328/1328** byte-exact, negatives
  **190/190**, divergence **9/9**, coverage **149 rows 0 errors 0 warnings**, census
  **16/0/25/0** (NO_ORACLE 3), prose **5**. All FROZEN counts hit exactly (§P1-a2.10
  prediction confirmed; no wiring revert needed). Fresh `dune build --build-dir
  _build-e54p1a2` rc **0**, ZERO `Error`, hist **122** warning headers
  (`build/e54p1a2-freshbuild.log` records rc+headers only).
- **T4 — PASS.** `ocaml/lib/`, `ocaml/bin/`, `golden/`, `spec/CLAIMS.md`,
  `spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/census/` byte-clean vs HEAD at close
  (`git diff --exit-code` rc **0**, verified first-hand); ledger **203** headers ending
  **C380**; NO new claim, NO coverage/inventory/golden touch; ZERO oracle in the whole slice.
- **T5 — PASS.** F10: `hir_build.ml` references `Bind` ONLY at the `:41` alias and the
  single `bind_program` call (pinned by CONTENT — the call sits at `:974` after the slice's
  growth). RAW greps (comments included), all enforced by `tools/hir_test.py`:
  `pl_calls`, `cs_temps`, `cs_copies`, `cs_dec`, `bind_arrays` each have readers EXACTLY
  `['ocaml/hir/semantic_env.ml', 'ocaml/hir/semtest.ml']`; `cs_slot` appears NOWHERE in
  `ocaml/hir` (nor `ocaml/bin`) — its descriptor-slot int is dropped UNREAD at the
  projection boundary (the two pre-existing `semantic_env.ml` comments and two
  `hir_build.ml` comments naming it were reworded; deviation §P1-a2.3-4).
- **T6 — PASS.** After nested-comment strip, `semantic_env.ml` and `hir.ml` contain NO
  `\b(stride|offset|bytes|esz|size|reloc|pool)\b` and NO `0x` (harness: "2 files clean");
  the site projection carries booleans, names, AST node identities and positions ONLY —
  reviewed line-by-line at `426293dd`.
- **T7 — PASS.** Non-vacuity: **11 positives × 7 corrupt modes = 77** control lines, every
  run rc **1**, ZERO stdout, all-`SEM-FAIL` stderr. Spot-checked FIRST-HAND at close:
  `--corrupt-formal` proves on H16 ("formal p of proc(1) projects sid 1003, bind's row
  says 3") and on H04 (sid 1001 vs 1); `--corrupt-actual-base` proves on H16 ("repointed
  sym(0)->sym(3) … name p resolves from scope 0 to nothing" — KEY LAW: a VISIBLE alias
  would pass I2, so the candidate must be caller-invisible) and says
  `nothing was proven` on H04 (no reference actual); `--corrupt-arg-position` proves on
  both (length arm trips first: "positional evidence list disagrees in length — impossible
  by bind construction"); `--corrupt-mode` proves on H16 ("argument 0 needs its own cell
  (bind recorded a value cell)") and says `nothing was proven` on H04 (immediate-only —
  EXACTLY as §P1-a2.6 predicted). Live counts: H01 `4/3`, H02 `7/2`, H03 `7/4`, H04 `4/2`
  (UNCHANGED since P1-b), H05 `1/1`, H08 `7/3`, H09 `3/2`, and NEW
  **H16 `12 refs / 5 syms`, H17 `12/5` (the aliased pair `call bump(x, x)` yields TWO
  identical `var sym(2)` lines — this pins HIR REPRESENTATION only, never runtime
  aliasing behaviour), H18 `7/3` (three-pid forwarding chain, [C130] E27B route;
  representation only), H21 `5/2` (nested `A_value (Call_e)`; representation only)**.
  ALL 11 OK numbers byte-unmoved from hop 11's commit-time run to this close.
- **T8 — PASS.** Every fixture and every semtest invocation ×2 fresh processes, rc +
  stdout + stderr byte-identical (all 120 harness `ok` lines carry `deterministic`).
- **T9 — PASS.** `timeout 60` per fixture/semtest run throughout (harness envelope); the
  pre-existing BEGIN/DO discovery hang stays DOCUMENTED (classified at `aaf295f0`), NOT
  fixed in this slice.
- **T10 — PASS.** H06/H07/H10–H15 pins byte-identical (harness: H10 E03, H11 E02,
  H12 E12, H13 E13, H14 E14, H15 E12); the ONLY sanctioned behaviour changes landed as
  pre-registered: statement-call-with-arguments accepted (new `Call_s` coverage —
  H16/H17/H18/H21) and the whole-array actual E13→E15 handover (H19; H13's E13 pin
  unmoved). New refusals carry NEW stable codes in `diagnostic.ml`: H19
  `HIR-E15 … whole-array actual a at argument 0 … no array calling convention [C175] …
  unmeasured [TBD]`; H20 `HIR-E17 … argument 0 … FIXED BINARY(7,0) but the formal is
  FIXED BINARY(15,0); DR's conversion at an argument position is unmeasured [TBD]`.
  **E16 has NO fixture by design** — defensive witness, UNEXERCISED (recorded honestly).

## P1-a2.3 Deviations and measured notes (recorded, NOT fitted)

1. **FALSIFIED (hop 6):** the pre-code audit's prediction that P0 `params_of` E03 stays
   the FIRST refusal for an undeclared formal is FALSE — blocks lower pid-ascending, so
   the CALLER lowers first and H07 died E16. `formal_ty` now RE-EMITS the pinned E03
   channel/wording from the callee's own `bparams` line; H07 bytes restored exactly.
2. **Walker `ci_key` defect found and fixed (hop 11):** the predecessor's never-built
   uncommitted draft computed the statement-call key with `eident_key` of the Esuffix
   target — raised "not an identifier" on every positive with args (H16–H18 FAIL); the
   key must come from the head identifier node. Committed in `735b43af`.
3. **I13 main-block law (measured, hop 11):** `SE.formals_of env 0` answers **None** for
   MAIN programs — the outer block carries NO bind `proc_layout` record (the env's own
   i4/i5 law). First version failed ALL H01–H09; I13 tolerates None exactly when
   `params = []`, else loud.
4. **T5 raw-grep law forced comment rewords:** `cs_slot` occurrences in two
   `semantic_env.ml` comments (hop 9) and `pl_calls` in two `hir_build.ml` comments
   (hop 11) were reworded — RAW greps include comments, so literal bind field names may
   not survive anywhere outside the two authorized readers.
5. **corrupt-arg-position: DROP arm only.** §P1-a2.6 pre-registered an OR (drop a
   position, or swap two modes); only the drop (`List.tl ce_args`) was implemented — the
   length arm trips first and the swap would exercise the identical positional
   comparison one step further. Recorded honestly, not silently narrowed.
6. **`arg_evidence_mismatch` arm order:** the pre-registered order put the per-shape
   mismatch arms before the `PM_copy_in`/`PM_unknown` refusals — in OCaml that would be
   DEAD CODE (bottom-up subsumption); arms reordered without changing semantics.
   `f_key` is compared against `String.lowercase_ascii` of the block's `eformals`
   (sptrs and f_key share one bind origin; the comparison tests the SYNTAX).
7. **`nothing_proven` grammar:** the what-string must CARRY the "no" — the message reads
   `had <what> to perturb (nothing was proven)`; first two new calls passed
   "a multi-position evidence list"/"an own/value-cell passing mode" and read as if
   something existed; fixed to "no …" wording BEFORE commit.
8. **FALSIFIED stdlib assumptions (hop 9 design):** `Option.flatten` and `List.mapi2`
   DO NOT EXIST in the OCaml 5.4 stdlib — use nested-option match and `combine`+`mapi`.
9. **`elem_ref_mismatch` scope-generalized** (commit `735b43af`): shared with the new
   I11 D_elem arm by parameterizing the resolving scope; the P1-a1 I8 call site is
   byte-identical in behaviour (all H08/H09 numbers unmoved).
10. **`dump_designator` signature deviation (hop 6):** `dvar_ty : int -> string`
    (rendering-only — the assign-target role passes `pp_sym_ty syms sid`, an actual
    passes `fun _ -> pp_ty ac_ty`); representation detail, no semantics.
11. **Tooling law re-measured (hop 8):** the FIRST `dune build` in a fresh container can
    return rc 1 with ZERO output — rc must always be checked DIRECT/re-run.
12. **ACCEPTED AND CONFIRMED (hop 6/7): the PHYSICAL-NODE MATCHING LAW HOLDS** — bind's
    recorded `pl_calls` sites really share the CLI's own `Ast.expr` nodes; H03/H04
    (expression route) and H16–H18 (statement route) all matched; zero spurious E16.
    A fixture dying E16 would have FALSIFIED it (§P1-a2.10); it did not.
13. **UNEXERCISED, recorded honestly:** the Eident zero-arg `Call_s` exclusion arm
    (`ci_ast_args = None`) is walked but never positively exercised — no positive fixture
    contains `call q;`/bare `q;`; I12 skips it by design. E16 remains a defensive witness.

## P1-a2.4 Facts Bind still does NOT expose (carried from §P1-a1.4, plus)

10. Argument EVALUATION ORDER at the language level — [C093] backs DR's EMISSION order
    only; the ordered `arg N` list is a REPRESENTATION ordering (§P1-a2.2) `[TBD]`.
11. Runtime EFFECTS of argument aliasing, forwarding and nested actuals — H17/H18/H21 pin
    HIR REPRESENTATION only; DR behaviour for the aliased pair and the nested-call actual
    is UNMEASURED `[TBD]` (C093/C130 back the general by-reference law, not these shapes).
12. Conversion at an argument position (actual/formal type mismatch) — refused E17, DR
    behaviour UNMEASURED `[TBD]`.
13. Whole-array actuals, BASED/pointer/external argument ABIs — refused E15/E07 by NAME;
    no DR calling convention exists for arrays [C175] but the shapes are unmeasured `[TBD]`.
14. DEC copy-in beyond the recorded boolean (`cs_copies` Some⇒bool): the widened-temp
    mechanics stay in bind/codegen, never in HIR.

## P1-a2.5 Reproduction (the §P1-a2 regression set)

```bash
cd ocaml && eval "$(opam env)" && dune build       # rc 0; exe 172595d5… (T1)
python3 tools/hir_test.py                          # rc 0: 120 ok — H01–H21 CLI double-runs,
                                                   # semtest LIVE + SEVEN corrupt modes ×11
                                                   # positives, F4/F7/F8/F9/F10/S8, T5/T6
python3 tools/e2e_gate.py                          # rc 0 FROZEN 1328/1328-190/190-9/9-
                                                   # 149 rows 0/0-16/0/25/0-prose 5
cd ocaml && dune build --build-dir _build-e54p1a2  # rc 0 ZERO Error hist 122; exe sha == kept
grep -c '^## C' spec/CLAIMS.md                     # 203, ending C380
```

## P1-a2.6 Commits (explicit paths, hop order)

hop 3: **§P1-a2 PRE-REGISTRATION `3446dd85`** (PLAN.md only, BEFORE any `ocaml/hir/`
byte); hop 4: `426293dd` (semantic_env parameter API); hop 6: `cfaad741` (STEP 3 —
hir.ml + hir_build.ml + diagnostic.ml + semtest compile-adapt, ONE commit); hop 7:
`96e995fd` (STEP 4 — fixtures H16–H21 measured + pinned); hops 8/9: `db3421f2` +
`3f997e35` (STEP 5 design audit + HANDOFF entries, durables only — the `cs_slot` comment
reword was drafted uncommitted at hop 9 and rode `735b43af`);
hop 11: `735b43af` (STEP 5 — semtest I11–I13 + walker + 4 corrupt controls + hir_test
SEM_MODES ×7 + T5 extension); this close: RESULTS §P1-a2 + arch §7-3 + PLAN dashboard
CLOSED + gate/fresh logs (ignored evidence under `build/`) + durables.

## P1-a2.7 Roadmap (PROPOSED ONLY — operator decision governs)

PUT/GET statements; BEGIN/DO hygiene repair (pre-existing hang); MIR lab (still
`[TBD — lab not reachable]`); broader argument subsets (DEC copy-in representation,
external/pointer ABIs) only with their own oracle evidence. NONE is authorized by this
close; each needs its own pre-registration (PROTOCOL #1). **STOP after P1-a2 closure.**

---

# §P1-h — BEGIN/DO discovery hygiene (CLOSED 2026-11-10)

E2E-54/P1-h — the narrow, ZERO-oracle correctness repair of the pre-existing HIR
procedure-discovery hang, pre-registered as PLAN §P1-h (operator brief VERBATIM as
§P1-h.0, commit `04bccbac` — the PROTOCOL #1 gate landed BEFORE any `ocaml/hir/` byte).
Sessions: hop 1 `01a1bfe1` (fresh startup, preregistration `04bccbac`, correction
`7144b3f1`, durables `d1f89ed7`) → this hop 2 `01a1c00b` (renewal 1/12), chain
`chain:01a1bfe1-3e0a-763c-ab64-5e545a345d30`.

**Oracle runs this phase: ZERO.** No probe, no CP/M, no cpmsim, no LINK-80, no gate
beyond the byte tier. No claim created or modified: `spec/CLAIMS.md` still has **203**
`## C` headers ending **C380** (verified first-hand at close). This slice makes NO DR
behaviour claim — its "facts" are reads of this repository's own bind implementation,
classified [bind-fact]. `ocaml/lib/`, `ocaml/bin/`, `golden/`, `spec/INVENTORY.txt`,
`spec/COVERAGE.tsv`, `spec/census/` byte-clean at every step (T7); no push.

## P1-h.1 What §P1-h delivered

| deliverable | measured form |
|---|---|
| root-cause audit | PLAN §P1-h.1, facts M-1..M-7 measured first-hand at `cf6202b`: defect at `semantic_env.ml:511-563` (the non-Bproc branch re-entered the OWNER's own `bstmts`); bind's own law `bind.ml:2204-2231` (collect descends EVERY `Sproc` child, registers only `Bproc`); `Bind.frame_decls` (`bind.ml:390-408`) STOPS at `Sproc` |
| correction | `ocaml/hir/semantic_env.ml` (`7144b3f1`): `discover_stmts st plan ctx ss` separates the statement subtree under traversal from the enclosing procedure's env; non-Bproc child descends the NESTED block's OWN `bstmts` under the SAME ctx (BEGIN shares the parent scope — no scope/pid/signature/ownership invented); `register_children` is its one-line entry; Bproc registration body kept VERBATIM. Termination follows structurally (finite parser tree, strictly descending recursion, each block once along its path) |
| fixtures | **H22–H29** MEASURED-FIRST in `ocaml/scratch-p1h/` (CRLF+^Z, one dcl item per statement, `timeout 60` each), expected files are `cp` of reviewed measured output, never hand-written — 7 new positives + 1 new negative pin (`500c668f`) |
| independent authority | `ocaml/hir/semtest.ml` (`e004fa3e`): I6's whole comparison extracted VERBATIM into the SHARED `ownership_mismatches env blk pairs`; live I6 and BOTH new controls run that same code (§P1-a2.6 law); `--corrupt-owner` reparents one re-derived pair at a block that is NOT its AST parent, `--corrupt-discovery` drops one pair |
| test runner | `tools/hir_test.py`: `SEM_MODES` = live + **NINE** corrupt modes on every positive; docstring + PASS line reworded honestly; T5 grep list unchanged (the new code reads no bind field beyond the seam list) |

## P1-h.2 Falsifier panel (pre-registered §P1-h.5) — every measured value

- **T1 — PASS.** `pli80c.exe` sha256 `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held after EVERY build step, checked DIRECT (steps 4/5/close), and the fresh `--build-dir _build-e54p1h` exe sha equals the kept exe (computed SEPARATELY).
- **T2 — PASS.** `git diff --exit-code -- hir/expected` rc **0** at steps 4, 5 and close: H01–H21 byte-frozen through the discovery repair (additions only). NEW files: H22.txt **425 B**, H23.txt **950 B**, H24.txt **681 B**, H25.txt **425 B**, H26.txt **581 B**, H27.txt **950 B**, H28.txt **693 B**, H29.stderr.txt **66 B** + H29.rc **2**.
- **T3 — PASS.** `dune build` rc **0** DIRECT, ZERO `Error`; fresh `dune build --build-dir _build-e54p1h` rc **0**, ZERO `Error`, warning hist **122** (`build/e54p1h-freshbuild.log` records rc+headers only).
- **T4 — PASS.** `timeout 900 python3 tools/hir_test.py` rc **0** — step 4 run **184 ok**, step 5 run **220 ok**, zero FAIL lines. ALL **11** existing semtest OK numbers UNMOVED: H01 `4/3`, H02 `7/2`, H03 `7/4`, H04 `4/2`, H05 `1/1`, H08 `7/3`, H09 `3/2`, H16 `12/5`, H17 `12/5`, H18 `7/3`, H21 `5/2`. NEW live counts: H22 `1/1`, H23 `3/2`, H24 `2/2`, H25 `1/1`, H26 `2/1`, H27 `3/2`, H28 `2/1`. Every corrupt mode (existing seven + the two new) rc **1**, ZERO stdout, all-`SEM-FAIL` stderr on every positive (**18 positives × 9 = 162** control lines).
- **T5 — PASS, reproduction held AND repaired** (both witnesses kept; `timeout 20`, never unbounded):

  | input | pre-fix (`cf6202b`, `build/e54p1h-hang-witness.log`) | post-fix (`e004fa3e`, `build/e54p1h-repro-postfix.log`) |
  |---|---|---|
  | BEG1 bare statement `begin; x=1; end;` | **rc 124** hang, 0 B streams | rc **0**, 425 B dump |
  | BEG2 Bproc `p` then a bare BEGIN | **rc 2 BOGUS** `HIR-E11: line 3: duplicate internal procedure name p` | rc **0**, 693 B, exactly ONE `PROC … name=p` |
  | BEG3 BEGIN inside procedure `p` | **rc 124** hang | rc **0**, 680 B |
  | BEG4 `dcl` in a BEGIN | rc 2 `HIR-E03: line 5 … no bind row` | rc 2 **unchanged** (66 B) |
  | BEG5/BEG6 DO groups | rc 2 `HIR-E05 … DO; group` | rc 2 **unchanged** (66 B each) |
  | BEG7 call to a conditional-position proc | rc 2 `HIR-E06 … no bind-registered procedure` | rc 2 **unchanged** (63 B) — M-6 pre-existing, NOT touched |
  | BEG8 same `p`, never called | rc 0, `p` silently absent (500 B) | rc 0 **unchanged** — M-6 carried |

- **T6 — PASS.** ZERO oracle in the whole slice: only `dune build`, `tools/hir_test.py`, `tools/e2e_gate.py` (byte tier), `git`, and `pli80hir.exe`/`semtest.exe` on scratch fixtures.
- **T7 — PASS.** `git diff --exit-code -- ocaml/lib ocaml/bin` rc **0** at every commit; goldens/inventory/census/coverage untouched; ledger **203** headers ending **C380**; NO new claim.
- **T8 — PASS.** Seam greps held after the edits (harness-green in the same runs): F10 Bind alias + one `bind_program`; S8 `semantic_env.ml` still `Hir`-free (comment strip); F8/F7/F4 hex audit/F9; T5 readers of `pl_calls|cs_temps|cs_copies|cs_dec|bind_arrays` exactly `['ocaml/hir/semantic_env.ml', 'ocaml/hir/semtest.ml']`; `cs_slot` NOWHERE; T6 vocabulary strip-clean (new words `discover_stmts`, `nesting_pairs`, `ownership_mismatches`, `blk_name`, `--corrupt-owner`, `--corrupt-discovery` carry no forbidden token).
- **T9 — PASS, non-vacuity FIRST-HAND at close** (not inferred from the harness): `--corrupt-owner` on **H26** → `proc p reparented at p rejected as it must: invariant 6: proc(1) eparent is not the enclosing block's scope`; on **H27** → `proc q reparented at r …`; on **H28** → `proc p reparented at p …`; on pre-existing **H03** → `proc g reparented at g …` and on **H18** → `proc outer reparented at inner …`. `--corrupt-discovery` on **H26/H28/H03** → `2 env blocks for 0 AST-nested procedures (main is the extra)`, on **H27/H18** → `3 env blocks for 1 …`. On the array/no-nested-proc positives (H01, H05) BOTH controls say `corrupt control had no nested procedure block to perturb (nothing was proven)` and exit 1 — never a silent pass.
- **T10 — PASS, ZERO movement.** FULL gate rc **0** DIRECT → `build/gate-e54p1h-reg.log` (1537 lines): byte sweep **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows / 0 errors / 0 warnings**, census **16/0/25/0** (NO_ORACLE 3), prose **5**. Every FROZEN count hit exactly (§P1-h.6 zero-drift prediction confirmed; no revert needed).

## P1-h.3 Deviations and measured notes (recorded, NOT fitted)

1. **H22 empty `begin; end;` PARSSES** — §P1-h.4 flagged its parseability UNPROVEN. Measured: rc 0, 425 B, main body shows NO phantom statement (only `declare sym(0)`, the following `assign` at line 5, `stop`), deterministic. The pre-registration resolved honestly by measurement, not by assumption.
2. **`Ast.name` is a record, not a string** — the first draft of `blk_name` returned `b.Ast.bname` directly and failed the build (`This constant has type string but an expression was expected of type Ast.name`); fixed to `n.Ast.orig`. Caught at build, zero commits affected.
3. **`--corrupt-owner` arm coverage, stated honestly**: the "reparent at ANOTHER procedure's block" arm is exercised only by fixtures with ≥2 nested procedures (**H27**, **H18**); with a single nested procedure the control self-parents (**H26**, **H28**, **H03**) and the `eparent` arm trips (pre-order and `enclosing` stand behind it, untripped). Both arms are the SAME shared comparison.
4. **Dead guards kept**: the `bdecls <> []` → `e_scope` guards (`hir_build.ml:676-680`, `:954-958`) are DEAD for parser-produced ASTs (`parser.ml:889` always sets `bdecls = []`). **FALSIFIED** (hop 1): "BEGIN-contained declarations are refused by the HIR-E11 bdecls guard" — the LIVE typed channel is `HIR-E03 … produced no bind row in this block`, now pinned by H29. The guards are NOT removed (they still guard structurally built blocks; removal is scope change).
5. **M-6 carried, NOT fitted**: the conditional-position nested-procedure asymmetry (loud `HIR-E06` when such a proc is called, silent absence when it is not) predates this slice, is unchanged by it (BEG7/BEG8 re-measured identical post-fix), and its DR-oracle behaviour is `[TBD]` — no oracle authorized. A future slice may own it.
6. **Statement identity vs runtime**: H23/H24/H25/H27/H28 pin that a BEGIN's statements are inlined EXACTLY ONCE in the enclosing procedure's HIR body, in source order, with correct line numbers — an HIR REPRESENTATION statement, never a runtime/execution-order claim (no oracle).
7. **OCaml scope law** (hop 1, self-caught): a wrapper defined AFTER a `let rec` is out of scope inside the recursive body — the Bproc branch must call `discover_stmts` directly rather than the later `register_children`.
8. **Zero-drift preservation law CONFIRMED**: for every tree with no statement-level non-Bproc block (all H01–H21, the 1328 goldens, the 190 negatives) the visitor produces the IDENTICAL registration sequence — measured, not assumed (T2/T4/T10).

## P1-h.4 Facts still NOT exposed / carried unknowns

- M-6 conditional-position nested blocks: silent drop of an uncalled proc (`[TBD]` oracle).
- `dcl` inside a nested BEGIN: refused via E03; DR's own scoping behaviour **[TBD — no oracle authorized]**.
- BEGIN/DO inside `Sdobegin` groups: lowering refuses by name (E05) before discovery could matter; DO-group discovery descent remains unmeasured.
- Language-level evaluation order of actuals: still [unmeasured] [TBD] (carried from §P1-a2.2).

## P1-h.5 Reproduction (the §P1-h regression set)

```bash
cd ocaml && eval "$(opam env)" && dune build          # rc 0; T1: sha256 _build/default/bin/pli80c.exe
timeout 900 python3 tools/hir_test.py                 # rc 0; 220 ok; live + 9 corrupt × 18 positives
timeout 900 python3 tools/e2e_gate.py                 # rc 0; 1328/1328-190/190-9/9-149-16/0/25/0-5
cd ocaml && dune build --build-dir _build-e54p1h      # rc 0, ZERO Error, hist 122, sha == kept exe
# per-fixture control spot check:
ocaml/_build/default/hir/semtest.exe --corrupt-owner hir/fixtures/H27.pli      # rc 1, SEM-FAIL only
ocaml/_build/default/hir/semtest.exe --corrupt-discovery hir/fixtures/H26.pli   # rc 1, SEM-FAIL only
```

## P1-h.6 Commits (explicit paths, hop order)

hop 1: **preregistration `04bccbac`** (PLAN.md §P1-h only, BEFORE any `ocaml/hir/` byte);
**correction `7144b3f1`** (`ocaml/hir/semantic_env.ml`); durables `d1f89ed7`; guard
`b1bc3631`. hop 2: **fixtures `500c668f`** (`hir/fixtures/H22..H29.pli` +
`hir/expected/H22..H29.*`); **semtest + runner `e004fa3e`** (`ocaml/hir/semtest.ml`,
`tools/hir_test.py`); this close: RESULTS §P1-h + arch §7-4 + PLAN dashboard CLOSED +
ignored evidence logs (`build/gate-e54p1h-baseline.log`, `build/gate-e54p1h-reg.log`,
`build/e54p1h-hang-witness.log`, `build/e54p1h-repro-postfix.log`,
`build/e54p1h-freshbuild.log`) + durables.

## P1-h.7 Roadmap (PROPOSED ONLY — operator decision governs)

M-6 conditional-position nested-procedure hygiene; MIR lab (still `[TBD — not reachable]`);
PUT/GET; broader argument subsets; P2+. NONE is authorized by this close; each needs its
own PROTOCOL #1 pre-registration committed BY EXPLICIT PATHS before any code byte.
**STOP after P1-h closure.**

---

# §P1-m0 — First native MIR AOT compilation (CLOSED 2026-11-09)

Zero-oracle slice E2E-54/P1-m0 (pre-registered `19a7c2c2`; implementation `241f2a79`;
fixtures+pins `57e0450f`; native tooling `5dc2356a` + runner `180162fa`). The complete
path PL/I source → existing Parser+Bind → `Semantic_env`/`Hir_build` → typed `Hir.program`
→ NEW `Mir_backend` → deterministic MIR text → pinned MIR object generator (out-of-tree
`libmir.a`, lab `ccc92c5c…` + madc `f541a7a5…`) → ELF x86-64 `ET_REL` `.o` → system C
linker + minimal driver → **native executable EXECUTING with the independently expected
result**. No JIT at runtime, no MIR parsing at runtime, zero oracle, zero historical bytes.

## P1-m0.1 What §P1-m0 delivered

| deliverable | measured form |
|---|---|
| MIR backend | `ocaml/hir/mir_backend.ml` (`241f2a79`): typed `Hir.program` → deterministic MIR text per §P1-m0.4; §P1-m0.2 native subset with BY-NAME refusals; §P1-m0.3 exact-interval numeric proof inside `W(p)=±(2^(p-1)-1)`; refuse-not-assume |
| diagnostics | `ocaml/hir/diagnostic.ml` APPENDED `HIR-E18 e_mir_node` / `HIR-E19 e_mir_numeric` / `HIR-E20 e_mir_export`; no existing code changed meaning |
| opt-in CLI | `ocaml/hir/pli80mir.ml`: `usage: pli80mir [--profile NAME] --export NAME [-o OUT.mir] INPUT.PLI`; `--export` REQUIRED (case-fold match); `-o` written only after `Ok` and BEFORE stdout, so every refusal leaves ZERO stdout and NO file; `Backend.Driver` + `For`-functor witness; `ocaml/lib`/`ocaml/bin` untouched |
| fixtures + pins | `hir/mir-fixtures/{M01,M02,M03,N1..N7}.pli` CRLF+^Z (`57e0450f`); `hir/mir-expected/` = `cp` of reviewed measured output — `M01.mir` 187 B, `M02.mir` 269 B, `M03.mir` 248 B, seven `N*.stderr.txt` + `N*.rc` (`2`) — measured-first, ADDITIVE (frozen H-series untouched) |
| emitter | `tools/mir_aot/mir2o.c` — the complete measured D-3 sequence (`MIR_link(ctx, MIR_set_gen_interface, NULL)` mandatory); `MIR_object_load` NOT used; nonzero rc everywhere; `gen_finish`/`finish` on every exit path (`5dc2356a`) |
| build script | `tools/mir_aot/build_native.sh` — pin-checks BOTH revs, FAILS LOUD naming the blocker, no re-pin/network/C-substitution; `libmir.a` strictly out-of-tree (D-2 mkdir-first law); `gcc -O2 -Wall -Wextra -Werror … -ldl -lm` |
| driver | `tools/mir_aot/native_check.c` — `-DENTRY`/`-DEXPECTED` (both `#error`-enforced), prints decimal, exits 0 iff equal; expected values live ONLY in the runner's §P1-m0.6 table |
| runner | `tools/mir_aot_test.py` (`180162fa`): §P1-m0.7 panel — determinism ×2 fresh procs, pin equality, parser acceptance, `readelf -h/-r`, `nm`, `objdump -d`, `ldd` evidence → `build/mir-aot/`, link + TWO native runs, pipeline proof via `pli80hir.exe`, negatives with NO artifact, TWO corruption controls |

## P1-m0.2 The five milestones (brief §10 — stated SEPARATELY; all five PASSED)

1. **HIR lowered** — all three positive fixtures through the EXISTING path: `pli80hir.exe` rc 0 (runner P5, no bypass); N1/N2/N3/N5/N7 also lower rc 0 in HIR (their refusals are MIR-backend duties, D-7); N4/N6 die in `Hir_build` (E02/E08) BEFORE any MIR code runs — the no-bypass pins.
2. **MIR generated** — `pli80mir.exe` rc 0; deterministic text byte-equal across two fresh processes and equal to the reviewed pins; every line conforms to §P1-m0.4 (one module, `func i64` zero args, `v<sid>` ascending then `t<k>` in evaluation order left-before-right — verified against M03's `2-(3*4)` precedence and M02's chain — every value into a fresh temp, mandatory `endfunc`, `export` before `endmodule`).
3. **Object emitted** — `mir2o -f M.mir M.o` rc 0 on the REAL CLI artifact: three `ET_REL` `Advanced Micro Devices X86-64` objects of 1144 B each; `nm` lists exactly `T pli80_calc` / `T pli80_m02` / `T pli80_m03`; relocations ONLY in `.rela.eh_frame` (2 × `R_X86_64_PC32` against `.text`) — CODE relocations NONE for these shapes. Sizes are `MIR_gen` constant-folding output, machine-build dependent, NOT pinned; results are judged by EXECUTION, never by disassembly shape (D-6 law).
4. **Executable linked** — `gcc -O2 -DENTRY=… -DEXPECTED=… native_check.c M.o` rc 0 for all three; 16 008 B dynamic executables.
5. **Native execution** — TWO fresh processes per fixture: `pli80_calc` → **42**, `pli80_m02` → **45**, `pli80_m03` → **10**, rc 0 each, stdout exactly the decimal line; `ldd` lists ONLY `linux-vdso.so.1`, `libc.so.6`, `/lib64/ld-linux-x86-64.so.2` — the runtime needs NO libmir, NO MADC, NO OCaml, NO PL/I frontend (the BUILD-TIME emitter may and does depend on `libmir.a` — brief §7; see also §RD-COSMO below).

**End-to-end success is claimed: the final milestone passed.**

## P1-m0.3 Falsifier panel (pre-registered §P1-m0.8) — every measured value

- **T1 — PASS.** `pli80c.exe` sha256 `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held DIRECT at session start (before any action), at steps 3/4 (prior hops), and before the fresh build; the fresh `--build-dir _build-e54p1m0` exe sha (computed SEPARATELY) equals the kept exe.
- **T2 — PASS.** `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc **0** at every step; the MIR pins live in NEW directories `hir/mir-fixtures/` + `hir/mir-expected/` and never inside the frozen set.
- **T3 — PASS.** `timeout 900 python3 tools/hir_test.py` rc **0** = **220 ok**, ZERO FAIL, ALL 11 existing semtest OK numbers UNMOVED (H01 `4/3` H02 `7/2` H03 `7/4` H04 `4/2` H05 `1/1` H08 `7/3` H09 `3/2` H16 `12/5` H17 `12/5` H18 `7/3` H21 `5/2`); F7/F8/F10/S8/T5/T6 green over the NEW `ocaml/hir/*.ml` files (glob) at step 3 and over unchanged files thereafter; the MIR dirs are NOT read by `hir_test.py` (log `build/p1m0-step4-hirtest.log`).
- **T4 — PASS.** FULL compile-tier gate rc **0** DIRECT → `build/gate-e54p1m0-reg.log` (1537 lines): byte sweep **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows / 0 errors / 0 warnings**, census **16/0/25/0** (NO_ORACLE 3), prose **5**. FROZEN counts ALL HIT, zero movement. Fresh `dune build --build-dir _build-e54p1m0` rc **0**, ZERO `Error`, warning hist **122** (`build/e54p1m0-freshbuild.log`).
- **T5 — PASS.** `git diff --exit-code -- ocaml/lib ocaml/bin` EMPTY at every commit; goldens/inventory/census/coverage untouched; ledger **203** `## C` headers ending **C380**; NO new claim (native MIR execution is DRPLi engineering evidence, never DR behaviour; the i64 carrier is explicitly NOT a DR claim).
- **T6 — PASS.** ZERO oracle: no DR compiler, cpmsim, LINK-80, `--runtime`, `--link-run` or rune-ci invocation anywhere in the slice — only `dune build`, the two HIR CLIs, `tools/hir_test.py`, `tools/e2e_gate.py` (byte tier), `tools/mir_aot/build_native.sh`, `tools/mir_aot_test.py`, `gcc`, binutils, `git`.
- **T7 — PASS.** Lab re-verified at this session's start AND after the build script: `git -C thirdparty/mir-madc-aot-lab rev-parse HEAD` = `ccc92c5c650b4385b4f42c9493725ae1415ab2e5`, `madc` = `f541a7a54624869e29b01f2f30b174bc0329eea5`, `git status --porcelain` EMPTY (0 lines) at every check; path stays git-IGNORED; nothing under `build/` committed.
- **T8 — PASS.** Both fresh-process runs of every positive byte-equal (MIR text) and equal to the committed pin; both native runs per fixture returned the same value; negatives deterministic on pinned stderr bytes.
- **T9 — PASS, non-vacuity FIRST-HAND.** C-a (`mul t3, t1, t2` → `add t3, t1, t2` in the emitted M01 MIR, re-emitted, re-linked against `EXPECTED=42`): native run **FAILED** as designed, execution reported **13**, nonzero rc. C-b (unmodified `M01.o`, `-DEXPECTED=43`): **FAILED**, rc nonzero, real value 42 ≠ 43. The runner FAILS itself if a control passes. Expected results 42/45/10 live ONLY in the runner table + PLAN §P1-m0.6.
- **T10 — PASS.** Every positive MIR text contains exactly one `func` + one `export`; every `.o` exports its symbol per `nm`; every value came from EXECUTION; each N-fixture's diagnostic NAMES the construct it refuses (see pins: `uninitialized read of sym(0)`, `if is outside the P1-m0 native subset`, `conversion FIXED BINARY(15,0) -> FIXED BINARY(7,0)`, `type FIXED BINARY(15,0) ARRAY[1:3]`, `a while loop`…).
- **T11 — PASS.** `handoff.config.json` NEVER staged (left dirty, operator-owned); explicit-path commits only (`git status` verified before each); no push.

## P1-m0.4 Deviations and measured notes (recorded, NOT fitted)

1. **N5 wording** (hop 2, kept): §P1-m0.2 predicted refusal naming the "array designation"; measured E18 arrives at the `declare` step naming the declared **TYPE** (`FIXED BINARY(15,0) ARRAY[1:3]`) — a `Declare` lowers before the element assignment is reached. Code as pre-registered; the pin records what was measured.
2. **`For`/`~export` contract resolution** (hop 2): `Backend.BACKEND` fixes `compile` to `~profile` + program, but §P1-m0.2 makes the export NAME a subset decision (`HIR-E20`). Resolved by `Mir_backend.compile ~profile ~export prog` plus the `For(E : EXPORT)` functor supplying the `BACKEND` instance — contract semantics unchanged (the backend alone refuses; every MIR name lives only in `mir_backend.ml`).
3. **Runner first-run defect (self-caught, fixed honestly)**: P2 initially fed `mir2o` a path the panel never wrote (`rc 3 cannot read input`); the runner now copies the REAL CLI `-o` artifact into `build/mir-aot/` before emitting. No pin, no fixture, no compiler file was involved; the FAILING first run is recorded here.
4. **F8 single-uppercase-letter LAW** (hop 2, measured the hard way, pattern NOT weakened): a single UPPERCASE letter anywhere in `ocaml/hir/*.ml` code trips the 8080-mnemonic grep — `'A'..'Z'` char range rewritten on `Char.code` (65..90); one-letter module `M` renamed `Entry`.
5. **UNEXERCISED arm**: `--profile generic32-unspecified` dies `HIR-E10` inside `Hir_build` BEFORE the backend, so `mir_backend`'s ceiling-Unknown `e_profile` arm is never exercised through the CLI — recorded, not force-fed.
6. **CARRIED pre-existing defect (recorded, NOT fitted, out of scope)**: `Pli80.Parser.Parse_error` is not caught by either HIR CLI (`pli80mir.exe` behaves identically to `pli80hir.exe`: rc 2, fatal text, zero stdout); no parser edits are authorized in this slice.
7. **CRLF re-measurement**: the hop-2 refusals were measured on LF-only scratch, whose line numbers are shifted (lexer CR handling, D-7). Every committed pin was produced from the CRLF+^Z fixtures and carries VISIBLE source line numbers (N1 line 3, N2 line 4, N3 line 5, N4 line 2, N5 line 2, N6 line 3, N7 line 3).
8. **Multi-proc `HIR-E20` arm EXERCISED** live on the frozen `hir/fixtures/H16.pli` (hop 2), so the "more than one procedure" refusal is not an unexercised witness.
9. **`libmir.a`/object sizes are build outputs, NOT pins** (10 337 202 B archive; three identical 1144 B objects from constant folding) — no size claim is made.

## P1-m0.5 Unsupported-semantics matrix (the slice's honest boundary; every row REFUSES, none guesses)

Control flow (IF/branching) — E18, deferred per brief §3 (IF/ELSE only in a LATER preregistered milestone, never silently); loops/recursion — E18; calls (`Call_e`/`Call_s`) and nested/multi-procedure programs — E20 (signature/shape) or E18 (expression site); parameters — E20 (non-empty `params`); non-integer return — E20; arrays (`D_elem`, element read/ref) — E18; `Convert` (any precision/scale change, DEC, CHAR) — E19 (rounding/overflow profile-UNKNOWN); uninitialized reads — E19 (static straight-line flow); values leaving `W(p)` — E19 (overflow UNKNOWN HONOURED, never assumed); `Static`/`External`/`Formal` storage — E18; `Stop`/fall-through/implicit return — E18; division/floating point, DEC/character data — refused EARLIER by the existing HIR channels (E02/E08; no-bypass pins); `Target.profile` fields `overflow_behavior`/`rounding_rules`/`float_semantics` REMAIN Unknown and are honoured by refusal, never defaulted (brief §4).

## P1-m0.6 Reproduction (the §P1-m0 regression set)

```bash
cd ocaml && eval "$(opam env)" && dune build        # rc 0; T1: sha256 _build/default/bin/pli80c.exe
timeout 900 python3 tools/hir_test.py               # rc 0; 220 ok; 11 numbers unmoved (T3)
sh tools/mir_aot/build_native.sh                    # rc 0; pin-checks + out-of-tree libmir + emitter
timeout 900 python3 tools/mir_aot_test.py           # rc 0; ALL 27 checks (42/45/10 EXECUTED; controls fail)
timeout 900 python3 tools/e2e_gate.py               # rc 0; 1328/1328-190/190-9/9-149-16/0/25/0-5 (T4)
cd ocaml && dune build --build-dir _build-e54p1m0   # rc 0, ZERO Error, hist 122, sha == kept exe
```

## P1-m0.7 Commits (explicit paths, hop order)

hop 1: pre-registration **`19a7c2c2`** (PLAN §P1-m0 ONLY, before any compiler byte; brief VERBATIM machine-verified 362 lines/NO trailing newline); durables `ac322afd`.
hop 2: implementation **`241f2a79`** (`ocaml/hir/{mir_backend,pli80mir,diagnostic,dune}`); durables `c4938310`; guard `3dbb174d` (g679, `handoff_finalize` attested).
hop 3 (this close): roadmap amendment recorded VERBATIM **`186a59d6`** (§RD-COSMO below); fixtures+pins **`57e0450f`**; native tooling **`5dc2356a`**; runner **`180162fa`**; this close commit = RESULTS §P1-m0 + arch §7-5 + PLAN dashboard CLOSED + §RD-COSMO action executed; ignored evidence `build/p1m0-step4/`, `build/mir-aot/`, `build/gate-e54p1m0-reg.log`, `build/e54p1m0-freshbuild.log`.

## P1-m0.8 Roadmap (PROPOSED ONLY — operator decision governs)

The operator roadmap amendment of 2026-11-09 (recorded VERBATIM in PLAN **§RD-COSMO**, commit `186a59d6`) selects **Cosmopolitan Libc as the preferred standard C runtime for future DRPLi/MIR native executables**; short-term target Linux x86-64 **static ELF** (APE NOT required unless trivial). Architectural principle: **Cosmopolitan-first native runtime, backend-independent HIR, no mandatory glibc runtime dependency**. The gcc/glibc linkage proven by this slice is EXPLICITLY demoted to a **diagnostic reference**, not the preferred deployment target; the static-link requirement concerns the GENERATED executable (the build-time MIR emitter may still depend on host libraries). The PROPOSED stages, NOT authorized by this close — each requires its own PROTOCOL #1 pre-registration committed BY EXPLICIT PATHS and explicit operator authorization:

- **P1-mC — Cosmopolitan static-link feasibility**: reuse the GENUINE `.o` produced from PL/I → HIR → MIR; pin a Cosmopolitan/cosmocc toolchain version; investigate `x86_64-unknown-cosmo-cc` with `-moptlinux`; build a small native C test driver with Cosmopolitan; attempt static linking with the MIR-generated object; verify ABI compatibility, relocations, native execution, expected result, and ABSENCE of `PT_INTERP` / `DT_NEEDED`; preserve GCC/glibc linking as a diagnostic reference, NOT the preferred deployment target; do NOT substitute generated C for MIR-generated machine code.
- **P1-m1 — Minimal PL/I console runtime**: small C adapters for integer/string input and output; linked against Cosmopolitan; PL/I I/O semantics explicitly DISTINGUISHED from the underlying libc functions; test EOF, input errors, buffer bounds and deterministic output; do NOT reimplement PLILIB wholesale.
- **Future — portable native formats**: investigate ARM64 native output; investigate APE ONLY after the static ELF integration works; keep HIR and MIR lowering independent of the selected libc and of the final executable format.

This close also SUPERSEDES the P1-h.7 note "MIR lab (still `[TBD — not reachable]`)": the laboratory is PINNED, reachable and MEASURED (D-1..D-6, T7); the historical compiler remains byte-identical.
**STOP after §P1-m0 closure (brief §11).** IF/ELSE, parameters, arrays, calls, I/O, macOS/AArch64 and any production backend remain UNAUTHORIZED.

## §P1-mC — Cosmopolitan static-link feasibility — CLOSED 2026-11-09 (session 01a1c194, hop 2)

Question (§RD-COSMO / brief §10): can the **genuine** PL/I→HIR→MIR→`mir2o` objects of
§P1-m0 be linked with a **pinned official Cosmopolitan** toolchain into a **plain static
Linux x86-64 ELF** (no APE step, no glibc runtime) that **executes natively** with the
independently expected results, with the historical compiler untouched? **ANSWER: YES —
ALL THREE FIXTURES.** No `ocaml/` byte changed; the driver `native_check.c` and the emitter
`mir2o.c` are UNCHANGED — only the link command differs.

### P1-mC.1 Result matrix (the four separable stages, per §P1-mC.5 step 6)

| stage | M01 `pli80_calc` | M02 `pli80_m02` | M03 `pli80_m03` | evidence |
|---|---|---|---|---|
| toolchain control (CT4, **no MIR object**) | PASS optlinux + tiny: static ELF, prints 42, rc 0 ×2 fresh procs | (control is M01-shaped) | — | `build/mir-cosmo/control.{optlinux,tiny}.exe`, `K1_control_*.{file,readelf_h,readelf_l,readelf_d}.txt` |
| object acceptance (`mir2o` unchanged; CT2) | `.o` sha256 `78656e6cbaced50e…` recorded BEFORE linking, == `build/mir-aot/M01.o` | `3822f7773ff78683…` == `M02.o` | `02c15b1bec53ed33…` == `M03.o` | `build/mir-cosmo/M0*.o.sha256` |
| static link (cosmo_link.sh, `ld`+`ape.lds`+`-lcosmo`) | rc 0, 840 984 B, exe sha `83c352ea5be7e865…`; tiny 216 544 B `a76ce2d20320190c…`; two links of one object byte-identical | rc 0, 840 984 B | rc 0, 840 984 B | `M0*.optlinux.link.optlinux.log`, `MODES.txt` |
| native execution (+CT3 panel + controls) | **42** in TWO fresh procs, rc 0 | **45** ×2, rc 0 | **10** ×2, rc 0 | `M0*_P4optlinux.*.txt`, runner log |

CT3 panel, every passing executable (all identical in shape): first bytes `0x7f 'ELF'`
(NOT `MZ` — no APE/launcher artifact); `file` → `ELF 64-bit LSB executable, x86-64, version
1 (GNU/Linux) [optlinux] / (SYSV) [tiny], statically linked`; `readelf -hW` → `EXEC` /
`Advanced Micro Devices X86-64`; `readelf -lW` → **no `PT_INTERP`**, LOAD segments only;
`readelf -dW` → "There is no dynamic section in this file." (**no `DT_NEEDED`** — no glibc,
no libmir, no libmadc, no OCaml dependency is even expressible); `nm` → `T pli80_calc` at
`0x401e20` (likewise `pli80_m02`, `pli80_m03`); `objdump -d` → the MIR-originating function
present; `ldd` (supplementary) → "not a dynamic executable".

Non-vacuity, on the **Cosmopolitan** path (§P1-mC.3): **C-a** M01 MIR `mul`→`add`, re-emitted
and RE-LINKED WITH COSMOPOLITAN → **executes 13** and the driver FAILS rc 1; **C-b**
unmodified `M01.o` with `-DEXPECTED=43` → reports 42 and FAILS rc 1. If either had passed,
the runner would have failed.

### P1-mC.2 Falsifier panel (pre-registered §P1-mC.4) — measured values

- **CT1 PASS** — `pli80c.exe` sha256 `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` held DIRECT before and after every step; `git diff --exit-code -- ocaml/lib ocaml/bin ocaml/hir hir/` rc 0 at every commit (this slice touches ZERO compiler source).
- **CT2 PASS** — the object fed to Cosmopolitan is byte-identical to the object fed to gcc/glibc (table above), and both were produced in THIS run by `pli80mir` (stdout == the frozen `hir/mir-expected/M*.mir` pins, two fresh processes each) + the UNCHANGED `mir2o`.
- **CT3 PASS** — panel above, per artifact; no launcher/APE artifact was ever counted as a static ELF.
- **CT4 PASS** — the Cosmopolitan-only control is recorded SEPARATELY (matrix row 1) and is described as toolchain health only, never as MIR integration.
- **CT5 PASS** — FULL gate rc 0 FROZEN **ALL HIT**: byte panel **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows 0/0**, census **16 EXACT / 0 DIFFERS / 25 REFUSED / 0 UNEXPECTED**, prose **5** files clean → `build/gate-e54pmc-reg.log` (1538 lines); `timeout 900 python3 tools/hir_test.py` rc 0 **220 ok**, ZERO real FAIL, **ALL 11 frozen numbers UNMOVED** (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2 H16 12/5 H17 12/5 H18 7/3 H21 5/2) → `build/hirtest-e54pmc-reg.log`; `timeout 115 python3 tools/mir_aot_test.py` rc 0 **27 checks** (gcc/glibc path preserved as the diagnostic reference) → `build/miraot-e54pmc-reg.log`; fresh `dune build --build-dir _build-e54pmc` rc 0, **ZERO `Error`**, warning history **122**, fresh exe sha == kept exe (computed separately) → `build/e54pmc-freshbuild.log`; `timeout 115 python3 tools/mir_aot_cosmo_test.py` rc 0 **25 checks** in 48 s (twice: `build/cosmo-runner-1.log`, `-2.log`).
- **CT6 PASS** — ZERO oracle (no DR compiler, cpmsim, LINK-80, `--runtime`, `--link-run`, Rune CI); ledger unchanged at 203 `## C` headers ending **C380** (native-linking feasibility is DRPLi engineering evidence, never a DR claim); `handoff.config.json` never staged; explicit paths only; nothing under `build/` committed; no push; every command under a short timeout.

### P1-mC.3 Toolchain and configuration record

- **Pin:** official `cosmocc-4.0.2.zip` (release tag `4.0.2`), 441 763 966 B, SHA-256
  `85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44`, in the git-IGNORED
  `build/p1mc-deps/`; `x86_64-linux-cosmo-gcc (GCC) 14.1.0`. `cosmo_link.sh --toolchain`
  re-verifies the archive hash and refuses to download or substitute anything.
- **Route:** the RAW architecture compiler, NOT the `cosmocc`/`cosmocross` wrapper, with the
  flag list the wrapper itself recorded in its `BUILDLOG` (captured VERBATIM for both modes;
  only the path prefix normalized): `-D__COSMOPOLITAN__ -D__COSMOCC__ -include
  libc/integral/normalize.inc -fportcosmo -fno-semantic-interposition -Wno-implicit-int
  -mno-tls-direct-seg-refs [-mred-zone | -mno-red-zone …] -fno-pie -nostdinc -isystem
  $COSMO/include` + `$LIB/ape-no-modify-self.o $LIB/crt.o` + inputs + `-static -no-pie
  -nostdlib -fuse-ld=bfd -Wl,-z,noexecstack -L$LIB -L$COSMO/x86_64-linux-cosmo/lib -Wl,-T,
  $LIB/ape.lds -Wl,-z,common-page-size=4096 -Wl,-z,max-page-size=16384 -lcosmo
  -fno-omit-frame-pointer`. **No `fixupobj`, no `objcopy`/`zipcopy`, no `.com` conversion,
  no launcher** — the APE post-processing branch of the wrapper is exactly what the target
  format does not need.
- **Host law (measured, `strace -e trace=execve`):** every program in the distribution is an
  APE file (`MZqFpD='` at offset 0) and this host's `binfmt_misc` `DOSWin` (magic `4d5a`,
  offset 0) claims them with **wine**; the wrapper's `.ape` HELPER steps made a whole
  `cosmocross` link exceed 90 s. Launching the raw compiler through the distribution's own
  native ELF loader `bin/ape-x86_64.elf` takes ~1 s and yields a **byte-identical** artifact
  (measured both ways, `83c352ea…`); `COSMO_LOADER=0` reproduces the direct/wine route. No
  system configuration was changed and none is required by the recipe.

### P1-mC.4 Deviations and measured notes (recorded, NOT fitted)

1. **`-mtinylinux` is UNAVAILABLE** on the pinned official release (zero occurrences in its
   README/scripts; documented only on post-release `master`). Measured `-moptlinux` and
   `-mtiny` instead and recorded both; no unversioned `master` build was trusted.
2. **By-hand flag derivation for `-mtiny` was WRONG and the BUILDLOG capture corrected it:**
   `cosmocross` excludes any mode ending in `tiny` from `-fpatchable-function-entry=18,16
   -fno-inline-functions-called-once`; my reconstruction had added them. Law adopted: capture
   the wrapper's BUILDLOG, never reconstruct flags.
3. **Hop-1 framing falsified:** the wine stall is the wrapper's `.ape` HELPER steps, not the
   toolchain binaries — `ld.bfd`/`cc1` under wine complete in well under a second.
4. **A Cosmopolitan static ELF embeds APE machinery as data** (`objdump -d` opens a `.head`
   section with `ape_cod_vaddr` holding a second copy of the image, used by APE startup). The
   FILE is a plain ELF the kernel loads natively: no `MZ` header, no PT_INTERP, no launcher.
   Recorded so no reader mistakes the embedded copy for an APE artifact.
5. The runner's own check count is **25** (panel granularity chosen in step 5); §P1-mC.4/CT5
   refers to "the panel", not a fixed number — the historical `mir_aot_test.py` stays at 27.
6. Optlinux vs tiny differ observably: `840 984 B` `ELF version 1 (GNU/Linux)` with debug
   info vs `216 544 B` `(SYSV)`, not stripped; both static, both correct. Judge by EXECUTION.
7. `ldd` on a static ELF exits NONZERO ("not a dynamic executable") — used as supplementary
   evidence only, per brief §6.

### P1-mC.5 Roadmap after P1-mC — **PROPOSED ONLY, NOTHING AUTHORIZED**

- **P1-m1 — Minimal PL/I console runtime (§RD-COSMO wording, PROPOSED):** small C adapters
  for integer and string input/output, LINKED AGAINST COSMOPOLITAN; explicitly DISTINGUISH
  PL/I I/O semantics (record structure, `PUT`/`GET` editing, `EOF`, `ENDFILE`, `SIZE`,
  `SKIP`, `PAGE`) from the underlying libc functions; test EOF, input errors, buffer bounds
  and deterministic output; **do NOT reimplement PLILIB wholesale**. Any such slice needs its
  own PROTOCOL #1 pre-registration and explicit operator authorization.
- **Future (§RD-COSMO, PROPOSED):** ARM64 native output before any APE work; APE only after
  the static-ELF integration is production; keep HIR and MIR lowering independent of the
  selected libc and of the final executable format (this slice confirms the objects are
  libc-agnostic: the SAME `.o` links under glibc and under Cosmopolitan).
- Still OUT of scope everywhere: production backend adoption, IF/ELSE/loops and parameters in
  MIR, real PUT/GET, and any DR-behaviour claim — the ledger stays **C380**.

### P1-mC.6 Reproduction

    eval "$(opam env)"; cd ocaml && dune build                      # rc 0, exe 172595d5…
    sh tools/mir_aot/build_native.sh                                # build/p1m0-deps/mir2o
    sh tools/mir_aot/cosmo_link.sh --toolchain                      # pin + identity
    python3 tools/mir_aot_cosmo_test.py                             # rc 0, 25 checks
    python3 tools/mir_aot_test.py                                   # rc 0, 27 checks (reference)
    python3 tools/hir_test.py; python3 tools/e2e_gate.py            # rc 0, FROZEN ALL HIT

Toolchain acquisition (out-of-band, ignored): fetch `cosmocc-4.0.2.zip`, verify SHA-256
`85b8c37a…3f44`, extract into `build/p1mc-deps/`.

## §P1-m1 — Minimal console I/O over the native MIR path — CLOSED 2026-11-10 (hop 9, session 01a1c2a9)

Question (§P1-m1.0): can the native MIR path (PL/I → HIR → MIR text → additive `mir2o` →
genuine MIR object → pinned Cosmopolitan static link) execute **console I/O** — `PUT LIST`
of an integer expression and of a printable literal, and `GET LIST` of a declared binary
scalar — with **independently hand-computed output bytes**, fail-fast status semantics and
a FROZEN historical panel? **ANSWER: YES for both milestones.** Nothing here is a DR
behaviour claim: console semantics are DRPLi engineering evidence; **ZERO oracle**; the
ledger stayed 203 headers / **C380**.

### P1-m1.1 Milestones delivered (SEPARATELY, per §P1-m1.0)

**m1a — integers (PUT/GET of `FIXED BIN(p,0)` values).** `ocaml/hir/`: `HIR-E21
e_io_construct` + `HIR-E22 e_io_domain` APPENDED (append-only law; no existing code
changes meaning); `hir.ml` ADDITIVE `put_source = P_value of expr | P_text of { text }` +
statement arms `Put of put_source` / `Get of designator` (shared `Hir.designator`, shared
`resolve` — no new name resolver) with §P1-m1.4 dump bytes; `hir_build.ml` `Sput`/`Sget`
arms in the PRE-REGISTERED order (options → kind → item scan ctl/count/class →
`lower_expr` through the EXISTING channels → GET target-shape after resolve).
`mir_backend.ml` emits §P1-m1.5: used-only protos `p_put,p_get,p_text,p_nl,p_exit` before
ONE canonical import line; locals `v<sid>`, `st?`, `a1?`, `t<k` in order; PUT = lower +
`call p_put` + `bne Lfail, st, 0` + `call p_nl` + `bne`; GET = `alloca a1, 8` + `call p_get
st, a1, lo, hi` + `bne` + `mov v<sid>, i64:(a1)` with env `sid := W(p)` (WINDOW LAW — the
post-get interval is exactly the declared window, so widening arithmetic after a GET
refuses E19); EVERY console call carries its own `bne`; ONE shared unindented `Lfail:`
tail (`call p_exit, exit, st` + `ret st`) — fail-fast, EOF never masquerades as success.
`tools/mir_aot/mir2o.c` landed the PROVEN ADDITIVE `MIR_load_external`-before-`MIR_link`
block (strong host imports become undefined symbols resolved at link; the madc fork's
lack of weak imports from MIR text is deviation 3 of §P1-m1.10). Commits `c3db9ffc` (HIR
half) + `d6ccb333` (MIR half + M04/M05 + N8..N16,N19..N21 measured-first pins, ZERO
deviations across the 12 arms).

**m1b — characters (literal PUT only).** `hir_build.ml`: the transient m1a item-class
refusal of `Ast.Estring` was REPLACED by the two pre-registered E22 arms — empty literal;
first character outside codes **32..126** naming the 1-based position and the DECIMAL code
point (never hex — F8 law) — and a validated literal lowers to `H.P_text`.
`mir_backend.ml`: `cu_text` joins the console-use summary; `p_text`/`pli_console_put_text`
join the fixed proto/import order at position 3; `s<k>` string items (FIRST USE of each
DISTINCT text in body order; escapes only `"`→`\"`, `\`→`\\`) after the import line and
before the `func` item; the literal statement emits the PROVEN probe2 shape `mov <t>, <len>`
+ `call p_text, pli_console_put_text, st, s<k>, <t>` + `bne` + `p_nl` + `bne`.
`tools/mir_aot/{pli_console.c,console_check.c}` committed with bodies **byte-identical** to
the measured hop-2 probes (headers rewritten to document the ABI: statuses
OK0/EOF1/BAD2/RANGE3/IOERR4; the put functions emit NO newline — the BACKEND closes every
PUT; the driver declares `extern long long ENTRY(void)`, prints nothing on stdout and
`driver-return=<v>` on stderr). Pins `M06.pli`/`M06.mir` (714 B) + N17/N18
measured-first CRLF+^Z. Commit `73b47176`. Character VARIABLES remain blocked by the
EXISTING `HIR-E02` declaration channel (deviation 4 of §P1-m1.10 — m1b is literal-only BY
CONSTRUCTION).

### P1-m1.2 Falsifier panel (pre-registered §P1-m1.9) — every measured value

- **T1 PASS** — kept exe `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` verified DIRECT at every hop (hops 5, 6, 7, 8 and this close).
- **T2 PASS** — `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc 0 at every step and at close (measured first-hand 2026-11-10); no H fixture contains put/get, so accepting them moved ZERO H pins.
- **T3 PASS** — `timeout 900 python3 tools/hir_test.py` rc 0 = **220 ok**, ZERO FAIL, ALL 11 frozen semtest numbers UNMOVED (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2 H16 12/5 H17 12/5 H18 7/3 H21 5/2) → ignored `build/p1m1-hop7-hirtest.log`; F8 strip-greps green over the edited `ocaml/hir/*.ml`.
- **T4 PASS** — FULL gate rc 0 **FROZEN ALL HIT**: byte panel **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows 0/0**, census **16 EXACT / 0 DIFFERS / 25 REFUSED / 0 UNEXPECTED**, prose **5** → `build/gate-e54p1m1-reg.log` (1537 lines).
- **T5 PASS** — `timeout 900 python3 tools/mir_aot_test.py` rc 0 **27 checks** (M01–M03 EXECUTE 42/45/10; N1–N7 unmoved by the additive mir2o; C-a executes 13 and C-b 42≠43 both FAIL).
- **T6 PASS** — `timeout 900 python3 tools/mir_aot_cosmo_test.py` rc 0 **25 checks** (frozen .o shas + optlinux/tiny static links + controls, all reproduced this session).
- **T7 PASS** — `timeout 900 python3 tools/mir_aot_console_test.py` rc 0 **43 checks**, first-ever run 2026-11-10 (commit `bf060051`). ALL V4 legs EXECUTED in fresh processes with the §P1-m1.7 bytes verified EXACT: M04 `42\n` (3 B) + stderr `driver-return=42\n` rc 0; M05 good `123\n` rc 0; sign+terminator (`-42x`) `-42\n` rc 0; not-a-number (`abc\n`) EMPTY stdout rc **2**; eof EMPTY stdout rc **1**; outside-W(15) (`20000\n`) EMPTY stdout rc **3**; M06 `DR PL/I-80 hello from Cosmo!!\n42\n` **EXACTLY 33 B** rc 0 + `driver-return=42\n`. Determinism: M04/run and M05/eof reproduced byte-equal in SECOND fresh processes. **ALL THREE CONTROLS FAILED LOUDLY first-hand:** C-a `mul`→`add` EXECUTED `13\n` (rc 0, `driver-return=13`) and its expected-42 leg FAILED; C-b (scratch `pli_console_get_i64` returning OK on the BAD path) turned the `abc` leg into rc 0 / `0\n` and FAILED; C-c (OK-with-0 at EOF) turned the empty-stdin leg into rc 0 / `0\n` and FAILED. Perturbations lived ONLY in scratch copies under ignored `build/mir-console/`; the committed sources were never touched.
- **T8 PASS** — fresh `dune build --build-dir _build-e54p1m1` rc 0, **ZERO `Error`**, warning history **122** (`build/e54p1m1-freshbuild.log`), fresh exe sha == kept `172595d5…` (computed separately).
- **T9 PASS** — V1 CT2 byte-identity FIRST-HAND: M01/M02/M03 `.mir` == pins ×2 fresh procs and the no-IO `.o` shas EQUAL the frozen §P1-m1.6 values `78656e6cbaced50ed5792742c5b6f47b043607f555364fd014d7e207fbdb0627` / `3822f7773ff786838bed43f53863ba8774a690f7c2c01dac1b64be1d313e94d6` / `02c15b1bec53ed3374a31e92fecf9d157f5ece7e0c326ec5ecd8aeebd0017c75` AND are byte-identical to the §P1-m0 `build/mir-aot/M0*.o` — the additive import block changes no-IO bytes NOWHERE.
- **T10 PASS** — every refusal NAMES its construct (measured pin bytes, V2): N8 SKIP, N9 PAGE, N10 FILE (options arm BEFORE name resolution), N11 EDIT, N12 ITEM, N13 item-count 2, N14 expression / N15 array element / N16 literal GET targets (E21 shape), N17 empty literal, N18 character 2 code point 9 (E22 charset, DECIMAL); N19/N20/N21 keep the EXISTING E01/E02/E05 channels byte-pinned (no bypass). Console statements appear in the MIR EXACTLY ONCE (M04 477 B / M05 582 B / M06 714 B reviewed line-by-line against §P1-m1.5 before pinning).
- **T11 PASS** — ZERO oracle (no DR compiler, cpmsim, LINK-80, Rune CI); ledger 203 `## C` headers ending C380; `handoff.config.json` NEVER staged; explicit-path commits only; scratch never committed; lab `ccc92c5c`/`f541a7a5` clean and never advanced; no push; every fixture `timeout 60`, every suite `timeout 900`; every command a DIRECT rc.

Execution evidence (link panel, V3): console objects recorded BEFORE linking —
M04 `561801c5…` (1968 B), M05 `81615f12…` (2256 B), M06 `cd216cb3…` (2488 B); each linked
`cosmo_link.sh tiny` with `console_check.c -DENTRY=pli80_<n>` (NO `-DEXPECTED` — the runner
judges the bytes) + `pli_console.c` into a plain static x86-64 ELF (235 904 / 235 936 /
236 016 B): `0x7fELF`, `file` statically linked, **NO PT_INTERP**, `nm T pli80_<n>`, NO
undefined `pli_console_*`/`exit`. Evidence files in ignored `build/mir-console/`.

### P1-m1.3 Deviations and measured notes (recorded, NOT fitted)

1. **The six §P1-m1.10 pre-recorded deviations stand as written**: `put from(x)` is
AST-INDISTINGUISHABLE from `put list(x)` and is ACCEPTED (frozen parser, no change in this
slice); trailing control items die in the PARSER (pre-existing uncaught `Parse_error`,
identical in `pli80hir.exe` — NOT an E21 pin, no pin exists); the WEAK-import route was
FALSIFIED by probe — the justified ADDITIVE `mir2o.c` block was landed instead (§P1-m1.6);
character variables stay blocked by the EXISTING E02; E21/E22 wording is pinned
MEASURED-FIRST (codes + named arms as pre-registered); the H dumps of `Put`/`Get` were
reviewed in scratch but NOT pinned under `hir/expected` in this slice.
2. **`cu_nl = cu_put || cu_text` (hop 8)** — §P1-m1.5 tied the `p_nl` proto and the
`pli_console_put_nl` import to `cu_put` alone; the backend closes EVERY PUT (value or
literal) with the newline call, so a literal-only procedure must still import `p_nl`.
Contract law honoured ("only the protos/imports used"); recorded, not hidden.
3. **N17 parse PROVEN GOOD (hop 8)** — §P1-m1.7 listed `put list('');` as PARSE UNPROVEN
with a fallback if the lexer died; measured: it parses and reaches the E22 EMPTY arm (rc 2,
pinned `N17.stderr.txt` + `N17.rc`, deterministic ×2). The empty arm is EXERCISED, not
defensive; the fallback branch was not needed.
4. **Runner first-run defect (self-caught, fixed honestly; this hop)** — the first-ever
execution died in `text_of`: `read_text(encoding="replace")` — `replace` is an errors
codec, not an encoding (`LookupError`). Corrected to `encoding="utf-8",
errors="replace"`; the failing first run is recorded here. NO expected byte, NO pin and NO
compiler file was involved; the second run was rc 0.
5. **Console-runner check count is 43** (panel granularity chosen in the written runner);
§P1-m1.8 pre-registered the panels, not a number. The historical runners stay at 27 and 25.

### P1-m1.4 Unsupported-semantics matrix (the slice's honest boundary; every row REFUSES or stays OUTSIDE the accepted syntax — none guesses)

Console syntax OUTSIDE the subset: `PUT FILE/SOURCE` options → E21 (before resolution);
`PUT EDIT`/`PUT ITEM`/`PUT FROM`-as-const kinds → E21 (FROM accepted as LIST, deviation 1);
control items `SKIP/PAGE/LINE` anywhere in the list → E21; trailing control items → parser
death (deviation 1); multiple data items → E21 (names the count); `GET` targets that are
expressions, array elements or literals → E21 target-shape; uninitialized GET target →
EXISTING E19; unresolved name → EXISTING E06; empty or charset-invalid literal → E22;
`fixed bin(16)` → EXISTING E01; character declarations → EXISTING E02; `ON` units →
EXISTING E05. Data OUTSIDE the subset: DEC/floating point/character-valued PUT/GET items,
`PUT SKIP` handling, `ENDFILE`/`END`/`SIZE` conditions (runtime statuses exist in the C
adapters but are NOT wired to PL/I conditions — fail-fast process exit is the observable
semantics), records/lists of items, buffered formatting, `EDIT` pictures — never lowered,
loudly refused or unreachable by the accepted-syntax gate. Everything outside the slice
unchanged: IF/ELSE/loops/parameters/arrays in MIR stay E18/E20 from §P1-m0.

### P1-m1.5 Roadmap after P1-m1 — **PROPOSED ONLY, NOTHING AUTHORIZED**

Character-variable output (`PUT LIST(chvar)`) behind a future declaration subset; PL/I
condition designators (`ON ENDFILE`, `ENDFILE=`) mapping the runtime statuses instead of
fail-fast exit; `PUT EDIT` formatting; file streams; the parser-hole repair for trailing
control items; adoption of the MIR path as a production backend; ARM64/APE formats
(§RD-COSMO); every broader semantics slice. Each needs its own PROTOCOL #1
pre-registration and explicit operator authorization. The ledger stays **C380**.

### P1-m1.6 Reproduction (the §P1-m1 regression set)

```bash
eval "$(opam env)"; cd ocaml && dune build                     # rc 0; T1 exe 172595d5…
sh tools/mir_aot/build_native.sh                               # rc 0; mir2o from mir2o.c
sh tools/mir_aot/cosmo_link.sh --toolchain                     # pin + identity
timeout 900 python3 tools/mir_aot_console_test.py              # rc 0; 43 checks; controls FAIL
timeout 900 python3 tools/mir_aot_test.py                      # rc 0; 27 checks (reference)
timeout 900 python3 tools/mir_aot_cosmo_test.py                # rc 0; 25 checks
timeout 900 python3 tools/hir_test.py                          # rc 0; 220 ok; 11 unmoved
timeout 900 python3 tools/e2e_gate.py                          # rc 0; FROZEN ALL HIT
cd ocaml && timeout 900 dune build --build-dir _build-e54p1m1  # rc 0; ZERO Error; hist 122; sha==kept
```

### P1-m1.7 Commits (explicit paths, hop order)

pre-registration `51231164` (PLAN §P1-m1 ONLY, BEFORE any repo code byte); step 2 m1a HIR
`c3db9ffc`; step 3 m1a MIR + fixtures `d6ccb333`; step 4 m1b literal put + runtime/driver
+ M06/N17/N18 `73b47176`; step 5 runner `bf060051`; step 7 CLOSE (this section + arch
§7-7 + dashboard CLOSED + durables). Interstitial durables/checkpoints: `695206df`,
`ee126055`, `661c73f2`, `7eccc4ef`.

---

## §P1-mD — Native DWARF source debugging of MIR AOT objects — CLOSED 2026-11-11 (hops 1–7, sessions 01a1c52f→01a1c63f)

Pre-registered as PLAN §P1-mD (PROTOCOL #1 gate: committed `a22dc0a5` + boundary
`d48564b6` **BEFORE any repo source byte**, after three scratch probe hops);
executed in work-order §P1-mD.10 steps 1–5. ZERO oracle throughout: this is
native-toolchain engineering evidence, never a DR claim.

### P1-mD.1 Milestones delivered (SEPARATELY, per §P1-mD.0)

**D1 — file/line truth (breakpoints, stepping, backtrace): PASS.** On the pinned
cosmo **optlinux** debug link (tiny secondary, glibc diagnostic reference), the
full gdb 18.1 battery is GREEN first-hand, twice (hop-7 scratch leg and the
runner's W6 — `build/mir-debug/gdb_optlinux_battery.log`): `break M05.pli:4`
resolves (`Breakpoint 1 at 0x402241: file …/hir/mir-fixtures/M05.pli, line 4.`);
`run` hits `Breakpoint 1, pli80_iorw () at …M05.pli:4` showing the real PL/I
line `put list(n);` of the CRLF+`^Z` fixture; `stepi` advances to
`0x0000000000402244` **staying on line 4**; `info line *pli80_iorw+97` =
`starts at …<pli80_iorw+97> and ends at 0x40226b <pli80_iorw+139>` — exactly the
pinned line-map bounds (22/97/139); `info source` = the pinned CU, `Producer is
mir-debug.`, `Compiled with DWARF 4`; **`bt` = `#0  0x0000000000402244 in
pli80_iorw () at …M05.pli:4` / `#1  0x0000000000401e65 in main ()`** (the hop-2 `ape.lds` `.eh_frame`
fold blocker definitively closed by the `.debug_frame` read-back route, hop-3
D-a/D-b discrimination); `continue` prints `77` and `[Inferior … exited
normally]`; gdb rc 0. The object laws underneath: named `.debug_frame` PROGBITS
0x40 + `.rela.debug_frame` (sh_info→12), **NO `.eh_frame`/`.rela.eh_frame`
anywhere**, decodedline rows 3@0xc0, 3@0xd6, 4@0x121, 5@0x14b + the 0x176 end
row, `frames-interp` decodes CIE + FDE `pc=00000000000000c0..0000000000000176`,
`nm T pli80_iorw`; EXEC stdin `77\n` → stdout EXACTLY `77\n`, stderr
`driver-return=77\n`, rc 0 (optlinux ×2 fresh procs + tiny ×1).

**D2 — variable inspection: PASS within the pre-registered scope** (scalar
non-parameter auto variables homed via `MIR_set_reg_debug_home`): at the hit,
`print n` → **`$1 = 77`** on the cosmo optlinux debug link (runner W6) and on
the glibc diagnostic leg; the sidecar `var v0 n` row drives the DWARF
`DW_OP_fbreg −8` (hop-2/3 measured). Parameters, deref/aggregate homes, arrays
and multiple homes per func stay OUT of scope — nothing is claimed for them.

### P1-mD.2 Falsifier panel (pre-registered §P1-mD.8) — every measured value

- **T1 PASS** — kept exe `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` verified DIRECT at session start and again after the fresh build (this hop).
- **T2 PASS** — `git diff --exit-code -- hir/expected ocaml/lib ocaml/bin` rc 0 at every step and at close; ALL six `hir/mir-expected/*.mir` byte-UNMOVED with and without `-g` (hop-5/6 cmp panel; re-exercised every runner W1 leg: file pin == stdout pin == regenerated bytes).
- **T3 PASS** — `timeout 900 python3 tools/hir_test.py` rc 0 = **220 ok**, ZERO FAIL, ALL 11 frozen semtest numbers UNMOVED (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2 H16 12/5 H17 12/5 H18 7/3 H21 5/2) → `build/e54pmD-reg-hirtest.log`; F8 strip-greps green.
- **T4 PASS** — FULL gate rc 0 **FROZEN ALL HIT**: byte panel **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows 0 errors / 0 warnings**, census **16 EXACT / 0 DIFFERS / 25 REFUSED / 0 UNEXPECTED**, prose **5** → `build/e54pmD-reg-gate.log` (1537 lines).
- **T5 PASS** — `timeout 900 python3 tools/mir_aot_test.py` rc 0 **27 checks**.
- **T6 PASS** — `timeout 900 python3 tools/mir_aot_cosmo_test.py` rc 0 **25 checks**.
- **T7 PASS** — `timeout 900 python3 tools/mir_aot_debug_test.py` rc 0 = **23 checks**, first-ever run 2026-11-11 (commit `2e8fdc9e`); **ALL THREE CONTROLS OBSERVED FAILING LOUDLY INSIDE THE RUNNER** (values in P1-mD.3).
- **T8 PASS** — fresh `dune build --build-dir _build-e54pmD` rc 0, **ZERO `Error`**, warning history **122** (`build/e54pmD-freshbuild.log`), fresh exe sha == kept `172595d5…` (computed separately).
- **T9 PASS** — the no-`--debug-map` `mir2o` output stays byte-identical: hop-7 ran explicit CT2 cmp legs ×2 after EVERY fix (compile, sha, ELF-drop), and the close regression re-held `build/mir-aot/M01.o` `78656e6c…`, `M02.o` `3822f777…`, `M03.o` `02c15b1b…` (mir_aot_test regenerates and `cmp`s; shas verified DIRECT this close). The runner's D-C1 preflight additionally EXECUTES the no-debug link (`77`).
- **T10 PASS** — sidecar refusal arms MEASURED-FIRST (hop 7, tampered SCRATCH copies only; §P1-mD.3 validation law): rc **7** unreadable map (named reason, NO file); rc **8** ×7 — sha flip (`sha MISMATCH … map says … digest to …`), count (map 13 records vs 14 parsed insns), opcode (`expected 'add', parsed 'alloca'`), order/duplicate index (`insn index 3 out of order (expected 5 …)`), var-missing (`v9 is not a named register of pli80_iorw`), duplicate var, bad magic — EVERY arm names its exact mismatch and writes NO object.
- **T11 PASS** — ZERO oracle (no DR compiler, cpmsim, LINK-80, Rune CI); ledger **203 `## C` headers ending C380** (verified at HEAD this hop); `handoff.config.json` NEVER staged; explicit-path commits only; `build/p1mD-scratch/` and `build/mir-debug/` NEVER committed; lab `thirdparty/mir-madc-aot-lab` (ccc92c5c/f541a7a5, re-verified by `build_native.sh` before the runner run) and `build/p1m*-deps`/`build/p1mc-deps` NEVER edited or advanced; no push; timeouts 60/120/900.

### P1-mD.3 Control panel (non-vacuity, §P1-mD.7 of the runner) — failing loudly

- **D-C1** — the NO-DEBUG link (default `mir2o`, no `--debug-map`) EXECUTES 77
  (preflight `ok`), but `break M05.pli:4` answers `No source file named
  M05.pli.` / `Make breakpoint pending … [answered N; input not from terminal]`
  / `The program is not being run.`, **gdb rc 1**, NO breakpoint ever set
  (`build/mir-debug/runner/gdb_nodebug_control.log`). The debug evidence is not
  free-standing.
- **D-C2** — sha-tampered sidecar → `mir2o` refuses **rc 8** naming
  `sha MISMATCH`, **NO object written**.
- **D-C3** — count-tampered (last `insn` record deleted, 13 vs 14) → **rc 8**
  `count MISMATCH`; opcode-tampered (insn 0 `alloca`→`add`) → **rc 8**
  `opcode MISMATCH`; both write NO object.
Perturbations lived ONLY in scratch copies under ignored `build/mir-debug/`;
the committed pins and sources were never touched.

### P1-mD.4 Deviations and measured notes (recorded, NOT fitted)

1. **The embedded C sha256 `K[56]` was WRONG (hop-6 "table correct" claim
   FALSIFIED).** The draft carried hex `0x0748f8ee`; the TRUE FIPS constant is
   `0x748f82ee` = hop-5's decimal `1955562222` (which `sha256.ml` always had
   right) — a one-digit hex transcription that a hand-copied "canonical" table
   REPEATED. Caught FIRST-HAND by the measured-first sha law itself (rc 8
   against the pinned map, whose sha equals Python `hashlib`). Fixed (one
   constant); the fixed C impl matches `hashlib` on lengths 0/3/55/56/63/64/65/
   1000 AND on `M05.mir` (`f41b358e…`). **Law accepted: a hand-copied constant
   table is NOT an independent oracle — only hashlib/derivation is authority.**
2. **`elf_drop_named` read every section name from `str->sh_name` instead of
   `sh[i].sh_name`** — all names collapsed to one string and rc 9 reported
   `.eh_frame appears 0 times`. Fixed (one site); T9 re-held after BOTH fixes.
3. Compile defect: `new_sec_off`/`new_sec_size` maybe-uninitialized on an early
   `goto done` (`-Werror`); fixed with the file's existing `= NULL` pattern.
4. **The sidecar `file` row is cwd-DEPENDENT** (hop-6 measured: verbatim
   `getcwd`-concat, `..` kept); ALL map pins and runner legs therefore run FROM
   THE REPOSITORY ROOT (the runner's `run()` pins `cwd=REPO`).
5. **Runner first-ever run defects (close session, self-caught, fixed honestly;
   NO expected byte or pin involved):** (a) `cli_leg` built argv WITHOUT the
   input fixture — every W1 leg died rc 2 `one input .pli file is required`;
   (b) the W6 `info line` assertion expected `<pli80_iorw+97> and ends at
   <pli80_iorw+139>` but gdb interleaves the end address (`…+97> and ends at
   0x40226b <pli80_iorw+139>`) — the assertion was re-assembled around the SAME
   pinned +97/+139 tokens. Pre-run review also replaced the stale loop variable
   in the `readelf_panel` 0x176 end-row check with the direct check (same
   expected value). Third run: rc 0, 23 checks.
6. **`Source language is c.`** in `info source` — the mir-debug DWARF producer
   records the CU language as C; recorded, not hidden; no assertion depends on
   it. Likewise the wine/`fixme:` link noise on stderr stays BENIGN (§P1-mD.7):
   links are judged by rc + artifact bytes only.
7. `console_check.c` ignores `-DEXPECTED` (carried §P1-mD.1 fact 10) — the
   runner judges EXECUTED BYTES.
8. The debug `.o` is **BYTE-IDENTICAL to the hop-3 objcopy probe `M05_dbg2.o`**
   (3464 B) — the in-C structural ELF drop reproduces objcopy exactly; sha256
   `cb263c2c69c1f31f456f8391fc7694f9418d4c32044e0ad2cc385a0e33984782` recorded
   BEFORE linking (§P1-mD.5 pin law).

### P1-mD.5 Unsupported-scope matrix (the slice's honest boundary)

| construct | status | evidence |
|---|---|---|
| scalar non-param `AUTO fixed bin(15)` var, ONE debug_home | **SUPPORTED, MEASURED** | M05: `var v0 n`, `print n` = `$1 = 77`, DW_OP_fbreg −8 |
| multiple `debug_home`s per func | OUT of scope | §P1-mD.9 boundary: the single-home subset landed honestly |
| parameters (`add_var` formal semantics) | UNMEASURED, OUT | nothing claimed; API exists |
| deref / aggregate homes (`member_offset`, `deref_p`) | UNMEASURED, OUT | arrays/records refuse upstream in HIR anyway |
| multi-`func` module / multi-CU sidecar maps | contract allows rows; UNMEASURED | M05 pins EXACTLY ONE `func 0 pli80_iorw` row + 14 `insn` rows + 1 `var` row |
| `.eh_frame`-based debugging on cosmo links | IMPOSSIBLE with the pinned `ape.lds` (hop-2 blocker, preserved as evidence) | `.debug_frame` named-section route is the landed truth |
| APE binaries, ARM64, production-backend adoption, `put edit` debugging | **PROPOSED ONLY** | each needs its own PROTOCOL #1 pre-registration + operator authorization |

### P1-mD.6 Reproduction

```bash
eval "$(opam env)"
cd ocaml && dune build                                   # rc 0; T1 exe 172595d5…
sh tools/mir_aot/build_native.sh                         # rc 0; mir2o from committed mir2o.c; lab pins verified
sh tools/mir_aot/cosmo_link.sh --toolchain               # pin + identity
timeout 900 python3 tools/mir_aot_debug_test.py          # rc 0; 23 checks; D-C1/C2/C3 FAIL LOUDLY
timeout 900 python3 tools/mir_aot_test.py                # rc 0; 27 checks
timeout 900 python3 tools/mir_aot_cosmo_test.py          # rc 0; 25 checks
timeout 900 python3 tools/hir_test.py                    # rc 0; 220 ok; 11 numbers UNMOVED
timeout 900 python3 tools/e2e_gate.py                    # rc 0; FROZEN ALL HIT
cd ocaml && timeout 900 dune build --build-dir _build-e54pmD   # rc 0; ZERO Error; hist 122; sha==kept
```

(The debug runner MUST be run from the repository root — cwd law, deviation 4.)

### P1-mD.7 Commits (explicit paths, hop order)

pre-registration `a22dc0a5` (PLAN §P1-mD; boundary `d48564b6`) BEFORE any repo
source byte; step 1+2 `b400b3b9` (`sha256.ml` + ADDITIVE `mir_backend.ml`
sidecar); step 2 (CLI + pin) and hop-5 remainder `b0966931` (`pli80mir -g`/
`--debug-map`, four rc-2 usage arms measured, `hir/mir-debug-expected/M05.p1md`
measured-first, determinism ×2); step 3 `b14756e9` (`tools/mir_aot/mir2o.c`
debug mode: validate-then-annotate, in-C ELF drop, read-back, rc 7/8/9/10
measured-first; the K[56] and `str->sh_name` defects caught by measurement and
fixed); step 4 runner `2e8fdc9e` (`tools/mir_aot_debug_test.py`, first-ever run
rc 0, 23 checks, controls failing loudly); step 5 CLOSE (this commit: RESULTS
§P1-mD + arch §7-8 + dashboard CLOSED + LEARNINGS + durables). Interstitial
durables: `8eee4bd3`, `ef1106be`, `907f58c3`-era hops' checkpoint commits,
`5277ecfc`, `a0617b6e`, `610ecd5f`.

## §P1-m2 — Native control flow: IF/ELSE and bounded DO WHILE — CLOSED 2026-11-12 (hops 1–7, sessions 01a1c673→01a1c708)

Pre-registered as PLAN §P1-m2 (PROTOCOL #1 gate: committed `d6bb1274` **BEFORE
any repository source byte**, after one recon hop); executed in work-order
§P1-m2.13 steps 2–8. ZERO oracle throughout: backend engineering evidence,
never a DR claim — the ledger stays **203 headers ending C380**.

### P1-m2.1 Milestones delivered (SEPARATELY, per §P1-m2.0)

**m2a — conditional branches and control-flow joins: PASS** (commit `ac56dd1d`).
`Hir.If` (with and without ELSE, nested) lowers to the §P1-m2.2 shapes with the
six relational operators; the join is **drop-not-inherit + sound interval hull**
(`Some`+`Some` → hull, `Some`+`None` → `None` — an assignment executed on one
path is never inherited); each arm lowers in a copy of the pre-IF env; the
window law I1 applies inside arms unchanged; `Hir.Var` refusal reworded to the
truthful "not definitely initialized on every reachable path" (§P1-m2.8 item 0).
GREEN first-hand: CF01 `choose` EXECUTED both arms natively (stdin `-2` →
`-1\n`, `0`/`7` → `1\n`, driver-return on stderr); all 15 §P1-m2.5 m2a stdin
legs executed byte-exactly on cosmo **tiny** static links; the pinned parser
(`mir2o`) accepted every emitted form (beq/bne/ble/bge measured-first per the
inversion table, Lt→Ge/Ge→Lt already hop-1 proven); corruption control
**C-M2a FAILED LOUDLY** (`blt`→`bge` flip EXECUTED the wrong arm, `1\n` where
`-1\n` was the independent expectation); CFN1/CFN2 refuse rc 2 with pinned
stderr, zero stdout, no artifact ×2; §P1-m2.8 amendments LANDED (N1 stderr
re-pinned path-truth; N2 refusal pins DELETED, `N2.mir` additive measured-first
pin, N2 became a POSITIVE with hand-derived value **2**; `mir_aot_test.py`
27→**32** recorded deviation).

**m2b — bounded `DO WHILE` + counted-loop proof: PASS** (commit `9672455b`).
`Hir.While` lowers to the hop-1-PROVEN header/backedge shape (§P1-m2.3): guard
reevaluated EVERY iteration (never peeled), inverted branch to `Lx<k>`,
mandatory `jmp Lh<k>` backedge; counter `cf_n` shared with m2a and **rewound
around the discarded verification pass** (deviation 4). The counted-loop proof
accepts ONLY: guard `Var sid OP const-interval` (OP ∈ Lt/Le/Gt/Ge), IV
definitely initialized to a constant, EXACTLY one body write = monotonic
`sid = sid ± C` literal step, direction match, and the EXACT exit value
`iv0 + c·ceil(...)` inside the declared window (zero-iteration path exact:
`exit = iv0`); every body-written non-IV sid is DROPPED at the header; nested
loops, IV writes outside the step, Eq/Ne guards and direction mismatches refuse
BY NAME. GREEN first-hand: CF06 `count` (brief §6 verbatim) executed THREE
genuine iterations (`0\n1\n2\n`, driver-return=3) and CF07 zero-iteration
(ret 5), CF08 exactly-one (Le, exit 3), CF09 IF-inside-loop (`9\n2\n` ret 2),
CF10 descending c=−2 (`6\n4\n` ret 2) all EXECUTED the INDEPENDENT §P1-m2.5
bytes; glibc native_check legs CF07=5/CF08=3 ×2 fresh procs; CFN3..CFN6 refuse
by name (rc 2, zero stdout, no `-o`, deterministic ×2); N7 re-pinned measured-first
per §P1-m2.8 item 2 (stays rc 2, now the named uninitialized-IV E19);
**C-M2b FAILED LOUDLY** (deleting `jmp Lh1` on a disposable copy EXECUTED
exactly ONE iteration `0\n`, prediction of §P1-m2.7).

**DWARF sidecar compatibility (§P1-m2.9): PASS.** No new sidecar record type was
needed — labels ARE insns, and the label rows must record opcode `label`
(defect caught first-hand at hop 5, fix committed `f7750038`; `.mir` bytes
untouched by construction: the assembly drops the line). CF01 `-g`: 27-row
sidecar reviewed row-by-row (24 body + the 3 line-0 fail-tail records; branch/
`jmp`/`label` rows at the IF line 5), debug object 3616 B byte-identical ×2,
named `.debug_frame` + `.rela.debug_frame`, NO `.eh_frame`; **gdb break
CF01.pli:5 hit on BOTH arms** (stdin `-2` → x=-2, y=-1; stdin `7` → x=7, y=1 —
next,next discipline, hop-5 stale-slot lesson). CF06 `-g`: 22-row sidecar;
debug object 3264 B sha `499169b4…` **byte-identical across sessions**;
decodedline rows 3@0xa0, 3@0xb2, **4@0xbc, 5@0xcf, 6@0xf9, 4@0x10a**, 8@0x113 —
the loop line 4 appears TWICE (guard AND backedge) as required; optlinux debug
link EXECUTES `0\n1\n2\n` driver-return=3 unchanged; **gdb break CF06.pli:5 hit
THREE times with `print i` = $1=0/$2=1/$3=2** (the backedge on the real
machine). W3 non-vacuity: the same break on the NO-debug link refuses
(`No source file named CF06.pli`, gdb rc nonzero). Existing debug pins
(M05.mir, M05.p1md, `.o` sha `cb263c2c…3984782`) UNMOVED (runner W4).

### P1-m2.2 Falsifier panel (T1–T11) — every measured value (close-session runs, each its OWN command)

- **T1 PASS** — kept exe `172595d52be44c9ead2404674f02bcce3ba7fc252915e13ce10040a5d5aca281` verified DIRECT this session (and again at the fresh build below).
- **T2 PASS** — `git diff --exit-code -- hir/expected hir/fixtures ocaml/lib ocaml/bin` rc 0 at close; every runner leg re-compares regenerated bytes against the committed pins.
- **T3 PASS** — `tools/hir_test.py` rc 0 **220 ok**, 11 frozen semtest numbers UNMOVED (H01 4/3 H02 7/2 H03 7/4 H04 4/2 H05 1/1 H08 7/3 H09 3/2 H16 12/5 H17 12/5 H18 7/3 H21 5/2), F8 green → `build/e54p1m2-reg-hir.log`.
- **T4 PASS** — FULL gate rc 0 **FROZEN ALL HIT**: byte panel **1328/1328**, negatives **190/190**, divergence **9/9**, coverage **149 rows 0/0**, census **16/0/25/0**, prose **5** → `build/e54p1m2-reg-gate.log`.
- **T5 PASS** — `tools/mir_aot_test.py` rc 0 **32 checks** (the §P1-m2.8-3 amendment), positives 42/45/10/**2** EXECUTED, 6 negatives, C-a/C-b fail natively → `build/e54p1m2-reg-miraot.log`.
- **T6 PASS** — `tools/mir_aot_cosmo_test.py` rc 0 **25 checks** → `build/e54p1m2-reg-cosmo.log`.
- **T7 PASS** — `tools/mir_aot_console_test.py` rc 0 **43 checks** (CT2 no-IO objects byte-frozen under the recursive `cu_*` walk — §P1-m2.8 item 0 blast radius held); `tools/mir_aot_debug_test.py` rc 0 **23 checks** from the repo root → `build/e54p1m2-reg-{console,debug}.log`.
- **T8 PASS** — fresh `dune build --build-dir _build-e54p1m2` rc 0, **ZERO `Error`**, warning history **122**, fresh exe sha == kept (computed separately).
- **T9 PASS** — EVERY existing `hir/mir-expected/*.mir` byte-UNMOVED (I6 falsifier re-run hop 6: 12 positive pins stdout==file==pin ×2 fresh procs, every negative rc/stderr/zero-artifact UNMOVED; N7 moved ONLY as §P1-m2.8 item 2 authorizes); CT2 `.o` shas `78656e6c…/3822f777…/02c15b1b…` and the M05 debug `.o` sha held inside the re-run suites; CF01/CF06 `-g` `.mir` byte-equal to their non-debug pins.
- **T10 PASS** — NEW `tools/mir_aot_cf_test.py` rc 0 **83 checks (MEASURED count, not a formula)**: V0 prerequisites + K0 toolchain identity; V1 CF01..CF10 pins ×2 fresh procs; V2 CFN1..CFN6 pinned rc/stderr/zero-stdout/NO artifact ×2; V3 pipeline proof (all ten positives also lower through `pli80hir` rc 0); V4 ten static tiny links (no PT_INTERP, no dynamic section, `nm T pli80_<n>`, no undefined console symbols) + EVERY §P1-m2.5 leg EXECUTED byte-exactly in fresh procs (20 stdin legs incl. the two BAD(2)-via-Lfail rc-2 arms) + glibc legs + determinism re-runs; V5 **C-M2a AND C-M2b OBSERVED FAILING LOUDLY INSIDE**; W1/W2 DWARF (row tables, byte-identical objects, section laws, decodedline, debug exec, gdb both IF arms + three-hit loop breakpoint); **W3 no-debug break OBSERVED refusing**; W4 existing debug pins UNMOVED (commit `2c08a90b`).
- **T11 PASS** — ZERO oracle (no DR compiler/cpmsim/LINK-80/Rune CI); ledger **203/C380** verified at close HEAD; `handoff.config.json` NEVER staged; explicit-path commits only; scratch `build/p1m2-scratch/`, `build/mir-cf/`, `build/mir-*` NEVER committed; lab `ccc92c5c`/`f541a7a5` and `build/p1m*-deps`/`build/p1mc-deps` NEVER edited or advanced (mir2o rebuilt from the COMMITTED `tools/mir_aot/mir2o.c`, lab pins verified by `build_native.sh`); no push; timeouts 60/120/900.

### P1-m2.3 Deviations and measured notes (recorded, NOT fitted)

1. **§P1-m2.8 pre-registered amendments LANDED exactly as written** (they are
   not post-hoc re-fits): N1 stderr re-pinned to the truthful uninitialized-path
   wording; N2 converted to a POSITIVE (value **2**) with its stale refusal pins
   deleted and an additive `N2.mir` pin; N7 re-pinned at m2b (stays rc 2);
   `mir_aot_test.py` check count **27 → 32**.
2. **CFN2 measures the CONVERSION refusal, not the planned Assign-window arm.**
   The pre-registered prediction (Assign `[4,4]` leaving `[-3,3]`) cannot fire:
   `hir_build` always wraps a literal into `fixed bin(3)` in `Convert 15→3`, and
   the existing conversion law refuses FIRST at line 6 (E19, pinned measured-
   first). Refusal law and negativity UNCHANGED; recorded, not re-plumbed.
3. **CFN6 same family:** the pre-existing E19 Convert fires at line 3 (`i = 0;`
   literal into `fixed bin(3)`) BEFORE any loop machinery — the §P1-m2.3 item 5
   step-window check is **structurally UNEXERCISABLE** by any fixture in the
   current subset (every small-precision IV must init from a literal; a
   GET-initialized IV is a non-point interval, also refused). The check exists
   in code and refuses by name; no fixture proves it — honest limitation.
4. **`cf_n` rewind fix (hop 5, my catch):** the DISCARDED CFN6 verification
   body pass consumed one `cf_n` per body-If, so CF09 emitted sparse
   `Ljoin3` — violating §P1-m2.2 "labels in source order, dense". `cf_n` is now
   saved/restored around the discarded pass (like `insns`/`tmp_n`); CF09
   re-measured `Lh1/Lx1 + Ljoin2`; CF06/07/08 pins verified UNMOVED.
5. **Sidecar label-opcode defect (hop 5, caught by `mir2o` rc 8, fix committed
   `f7750038`):** a MIR label directive is an insn NAMED `label`; the sidecar
   opcode map's first-token rule wrongly recorded label NAMES on CF paths. Rows
   whose text ends `:` now record `label`. The hand-written `Lfail` tail always
   did; the M05 pin never exercised a mid-body label at the head of the emitted
   list. `.mir` bytes and every non-debug byte are untouched by construction.
6. **CF runner first-ever-run defects (close hop, self-caught; NO expected byte,
   NO pin, NO compiler file):** (a) the static-ELF law required capitalized
   `"No dynamic section"` but readelf prints lowercase `There is no dynamic
   section in this file.` — 10 links + 20 exec legs + 2 determinism legs failed
   in cascade; fixed to the committed cosmo-runner idiom (fail iff `NEEDED`
   present or the phrase absent), verified against the recorded `readelf_d`
   evidence; (b) **C-M2b predicted wrong-behaviour rc 1**, conflating the PL/I
   exit value with the driver process status — the recorded first-run
   observation is `rc 0 stdout b'0\n' stderr b'driver-return=1\n'` (the §P1-m1
   driver contract: rc is the I/O status OK0/EOF1/BAD2/RANGE3/IOERR4, the
   returned value rides on stderr), exactly the hop-5 native measurement and the
   §P1-m2.7 prediction of ONE iteration; fixed to `rc 0`; (c) sidecar `var`
   rows were split on TAB although `mir_backend` writes `var v<sid> <sorig>`
   with a SPACE — W1 found `[]` for both fixtures. Second run: rc 0, **83**
   measured checks, controls failing loudly INSIDE.
7. **Console cosmo links MUST include `tools/mir_aot/pli_console.c`** (hop 6: a
   hand-invoked link without it died rc 1 `undefined reference to
   pli_console_*`); the committed runners always passed it; recorded so the
   recipe is never hand-copied wrong again.
8. **Operational (host, not repository):** a `git add` died with SIGBUS leaving
   a stale zero-byte `.git/index.lock`; recovered by proving NO git process was
   alive, then removing that EXACT path (`00471053` re-committed cleanly). The
   tree and history were untouched.

### P1-m2.4 Accepted/unsupported matrix (the slice's honest boundary)

| construct | status | evidence |
|---|---|---|
| `IF THEN ELSE` / `IF THEN` (no ELSE = identity arm), ALL six relational ops | **SUPPORTED, NATIVELY EXECUTED** | CF01 (Lt, both arms), CF02 (Gt skip/taken), CF03 (nested, Eq arm), CF04 (Ne + Ge, signed ±) |
| join law: hull on `Some`+`Some`, **DROP** on `Some`+`None` | **SUPPORTED, PROVEN LOUDLY** | CF02 hull `[7,9]` executes 9/7; CFN1 refuses the one-path `y` read by name |
| console PUT/GET inside branches (each call keeps its own `bne Lfail`) | **SUPPORTED, NATIVELY EXECUTED** | CF05 five legs incl. BAD(2) rc 2 via the shared `Lfail` tail |
| `DO WHILE` with counted-loop proof (constant init, monotonic literal step, direction match, exact exit, window) | **SUPPORTED, NATIVELY EXECUTED** | CF06 3 iterations, CF07 zero, CF08 one (Le), CF10 descending −2; exit values 3/5/3/2 EXACT |
| `IF` inside the loop body (IV untouched in arms) | **SUPPORTED, NATIVELY EXECUTED** | CF09 `9\n2\n` ret 2 (dense labels via the cf_n rewind) |
| uninitialized IV / non-step IV write / nested loop / Eq-Ne guard / direction mismatch | **REFUSED BY NAME** (E18/E19), never silently | CFN3/CFN4/CFN5 rc 2, zero stdout, no artifact ×2 |
| early/nested `RETURN`, branch-condition interval refinement, general fixpoint | OUT of subset (unchanged refusals; explicitly NOT required) | §P1-m2.2/.12 |
| `-g` DWARF sidecar + gdb for control-flow programs (scalar auto, single home) | **SUPPORTED, GDB-VERIFIED** | CF01 both arms; CF06 three-hit backedge; W3 refuses without `-g` |
| parameters, aggregates, arrays, FILE streams, `ON` conditions, `PUT EDIT`, multi-CU, APE, ARM64, production-backend adoption | **PROPOSED ONLY** | each needs its own PROTOCOL #1 pre-registration + operator authorization |

### P1-m2.5 Reproduction

```bash
eval "$(opam env)"
cd ocaml && dune build                              # rc 0; T1 exe 172595d5… DIRECT
sh tools/mir_aot/build_native.sh                    # rc 0 (mir2o from committed C; lab pins verified)
cd /home/john/projects/sushiworks/pli80             # REPO ROOT (cwd law)
timeout 900 python3 tools/mir_aot_cf_test.py        # rc 0; 83 measured checks; C-M2a/C-M2b/W3 FAIL LOUDLY inside
timeout 900 python3 tools/mir_aot_test.py           # rc 0; 32 checks
timeout 900 python3 tools/mir_aot_cosmo_test.py     # rc 0; 25 checks
timeout 900 python3 tools/mir_aot_console_test.py   # rc 0; 43 checks
timeout 900 python3 tools/mir_aot_debug_test.py     # rc 0; 23 checks (repo root)
timeout 900 python3 tools/hir_test.py               # rc 0; 220 ok; 11 numbers UNMOVED
timeout 900 python3 tools/e2e_gate.py               # rc 0; FROZEN ALL HIT
cd ocaml && timeout 900 dune build --build-dir _build-e54p1m2   # rc 0; ZERO Error; hist 122; sha==kept
```

### P1-m2.6 Commits (explicit paths, hop order)

pre-registration `d6bb1274` (PLAN §P1-m2, PROTOCOL #1) BEFORE any source byte;
hop-2 durables `81ec5498`/`5abe9c82`-era baseline; **m2a `ac56dd1d`**
(`mir_backend.ml` §P1-m2.2 + §P1-m2.8 items 0/1 + `mir_aot_test.py` 32 + CF01..
CF05/CFN1..CFN2 measured-first pins); hop-4 durables `71b7d56e`; **m2b
`9672455b`** (§P1-m2.3 + cf_n rewind + CF06..CF10/CFN3..CFN6 + N7 re-pin);
**sidecar label fix `f7750038`** (`mir_backend.ml`, gates re-green first-hand);
hop-6 durables `ab66668a`, renewal boundary `00471053`, operational record
`518a5827`; **CF runner `2c08a90b`** (`tools/mir_aot_cf_test.py`, first-ever run
rc 0, 83 measured checks, three runner defects fixed honestly); CLOSE (this
commit: RESULTS §P1-m2 + arch §7-9 + dashboard CLOSED + LEARNINGS + durables).
