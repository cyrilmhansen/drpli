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
