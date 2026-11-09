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
