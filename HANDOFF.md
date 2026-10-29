# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.

## Recovery instructions

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1 | wc -l`
   Expect branch `main` and an empty porcelain output; a dirty tree is investigated, never
   cleaned (`AGENTS.md` → Protected).
2. Read `AGENTS.md`, `PROTOCOL.md`, `GOAL.md`, then this file's `## Last verified state`, then
   `PROGRESS.md` and `LEARNINGS.md`.
3. Check checkpoint freshness with `/handoff verify` (extension auto-loaded — the project is
   trusted; see `PROTOCOL.md` → Load). `stale` or `missing` means: re-derive state from commits and lab evidence,
   then refresh with `/handoff`. Do not trust this file's managed block over its prose.
4. Load the authoritative evidence for whatever you are about to do:
   `spec/CLAIMS.md` (claims ledger, C001…C308 at the time of writing),
   `spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`,
   and the newest `spec/lab-evidence/e2e42-p2c/` reports.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P1 (scientific session, measured 2026-10-29)

See `PROGRESS.md` → Current phase for the same content; the short form: round 1 (E48A1..A15)
pre-registered at `284b630`, measured 15 ok/15; round 2 (E48B1..B9) pre-registered at
`3401821`, measured 9 ok/9; goldens in `golden/e48p1/` (uncommitted). DR laws measured this
phase, all read out of the `.REL` records:

- `^b` test on BIT(1): `3A <cell> / B7 / FA + 5-byte chain` (8 bytes; CREATE 0052, E48A1 000C,
  E48A5 0011, E48A12 000C, E48B1, E48B7); positive form identical with `F2` (E48A3 0006, E48B2,
  FLTPOLY2 0075). `DO WHILE` chain tail is `C3 <loop head>` written after the loop and patched
  back through `SET-LC/RELOC` (CREATE 01BE, E48A1 0041, E48A12 0049); IF/ELSE false chain
  targets the else (E48A2 000B→0027).
- `b = (cond)`: compare, then **[C095]'s** `D6 01 / 9F`, then `32 <cell>` (STA, inline DATA
  reloc [C079]). CREATE's `(name = 'EOF')` = 16 bytes; E48A6/E48B8/E48B9 reproduce it exactly.
- Materialiser by class: varying-vs-literal `LXI H,v / XCHG / LXI H,lit / MVI A,n / CALL
  ?SCVCM`; `k = 0` → `LXI H,k / MOV A,M / INX H / ORA M`; `k = 5` → `LHLD k / LXI B,FFFB / DAD
  H`(0x09) **not `DAD B`** (DR's own bias defect); `k ^= 0` and `^(k = 0)` → `ADI FF / SBB A`;
  `k > 0` → `XOR A / CMP M / INX H / SBB A`; `b = '1'b` → `LDA / ANI 80 / SUI 80` + flag trick.
- `^(cond)` in a test **inverts the skip byte** (`C2 JNZ → CA JZ`, E48A13); `if k = 0 & b then`
  materialises a bit operand as `PUSH PSW / LDA b / POP B / ANA B` under one `F2` (E48A14).
- `put list(b)` is **accepted**: `LDA cell / MVI B,01 / CALL ?QB08C / CALL ?PNBOP` (7 objects).
- STATIC bits are DATA-absolute and adjacent (E48B5 0000/0001); `dcl s char(3) static
  initial('AB')` is accepted, cell `41 42 20`, and the PUT reuses that cell — DATA area 3, zero
  pool bytes (E48B6). I refuse both today.
- **My defect, root-caused**: DR's `DEF-DATA-SIZE` is 3/2/4/5 for E48A3/B3/B5/B7 where mine is
  4/3/5/6 (+1 every time). `codegen.ml:12340` = `sy_total + pool_total + max auto_bytes
  layout.pl_total + 2*temps`, and `bind.ml` `section2`'s `span` (≈2146) charges STATIC rows, so
  a static byte is counted twice whenever statics dominate the `max` (FLTPOLY2 masks it). Found
  with temporary `E48DBG` instrumentation, since reverted; `ocaml/` is clean.

## Last verified state (Pi Handoff deployment window — superseded above for work state)

Verified **in the deployment session itself** (i.e. measured now, not quoted from a report):

- Repo `/home/john/projects/sushiworks/pli80`, branch `main`; scientific HEAD
  `0a50fc4c745838e3af1641c8a6f68fd17ed1371a`, with the 2026-10-29 infrastructure chain on top
  (`aa03eeb` renewal activation, `88248b1` renewal e2e test record, plus the closure commits);
  working tree clean (0 porcelain lines) at every checkpoint of this window.
- 12 028 tracked files; 471 102 ignored files present; 37 entries at the repository root.
- Nested third-party repos untouched and clean: `thirdparty/PLI-2000` @
  `c6f0f2ddd9c2100781ce6fb65d79d3039ac94e2a`, `thirdparty/z80pack` @
  `91fd28eb04e675c2127df88ed3f40675e15282e2`.
- `/tmp/wt_base` worktree and `.git/worktrees/` metadata left exactly as found; no branch
  switched; no `clean`/`reset`/destructive checkout run.
- Pi 1.4.0 at `/usr/bin/pi` under the production profile `/home/john/.sushi/pi`;
  `.sushibeta/pi` not used.
- Pi Handoff `v0.1.0-dev.1` (`2ea6219`) is installed and **validated in the real runtime**:
  the extension loads, `/guard status` reports model `sushi/Qwen3.8-Flash-Next-Sushi-STQ-2.75bpw`,
  window 220 000, maxOutput 65 536, reserve 20 000; read-only mode wrote nothing; a controlled
  writable session produced schema-v3 checkpoint blocks in both files, `current` freshness and a
  `READY` attestation, and a level-3 automatic checkpoint preserved substantive notes verbatim.
  Manual prose outside the managed blocks was byte-identical before and after every guard write;
  `GOAL.md`/`LEARNINGS.md` were never written by the guard; all runtime files stayed inside the
  ignored `.pi-guard/`.

Verified **from committed reports, NOT re-run in this session** (treat as recorded results,
not as fresh measurements):

- Latest recorded gate verdict (`spec/lab-evidence/e2e42-p2c/RESULTS.md` §8, and the commits
  `1e5fe03`…`0a50fc4` on top of it): 1074 byte-exact / 0 fail, negative panel 184/184 refused,
  divergence panel 9/9, coverage 102 rows, runtime panel 71/71 as recorded.
- Phase: **E2E-42/P2c** — named-file `PUT FILE … SKIP` bank pre-registered, measured against DR,
  and lowered; claims through **[C308]**.
- Known open scientific item recorded there: `CREATE` still does not compile; remaining blockers
  are `^eofile` inside a `DO WHILE` condition and a store into `BIT(1)` from a condition — neither
  related to PUT. Also recorded, deliberately unfixed: `pli80c`'s `wrote … (data=N)` summary line
  reports a number that is not the DATA segment length.

## Unfinished operations — E2E-48/P1 (open at this checkpoint)

- `golden/e48p1/` (24 DR programs: E48A1..A15, E48B1..B9, plus summaries and transcripts)
  exists on disk and is **NOT YET COMMITTED**. It is this phase's oracle evidence — stage it
  explicitly, never regenerate or rewrite it.
- `spec/lab-evidence/e2e48-p1/RESULTS.md` is **not written** yet; the prediction-vs-verdict
  table over the 15+9 pre-registered rows is owed, and must keep both MISSes.
- No `spec/CLAIMS.md` rows yet (next free id **C309**); no `INVENTORY.txt` / `COVERAGE.tsv`
  rows; **no OCaml change made**; the gate has not been run for this phase.
- Build note (measured): `dune` is not on `PATH`; use `cd ocaml && opam exec --switch=default
  -- dune build` (72 pre-existing warnings). Binary: `ocaml/_build/default/bin/pli80c.exe`.

## Unfinished operations (Pi Handoff deployment)

- **None in progress.** The Pi Handoff deployment (Phases A–E) is complete, and on
  2026-10-29 the operator authorized and live-tested the renewal activation (project trust,
  compaction disabled project-wide, `renewal.enabled/autoRenew`, cap 8). The remaining
  operator decisions listed in `PROGRESS.md` → Pending (reserve tuning, closing enforcement,
  push) stay **open by design** and are not half-applied.
- No compiler work was started, continued or left half-done in this session. Nothing in
  `ocaml/`, `spec/`, `tools/`, `golden/`, `oracle/` or `probes/` was touched by it, and no gate
  was executed by it.
- No commit was made on behalf of any scientific result; the only authorized commits from this
  session are infrastructure commits over: `.gitignore`, `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`,
  `HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md`, `handoff.config.json`,
  `.pi/extensions/context-guard/*.ts`, `.agents/skills/pi-handoff/**`.

## Next action — E2E-48/P1, the exact continuation

1. `cd /home/john/projects/sushiworks/pli80 && git rev-parse HEAD` → expect `3401821…` or a
   descendant; `git status --porcelain=v1` → expect only `?? golden/e48p1/`.
2. Write `spec/lab-evidence/e2e48-p1/RESULTS.md` §1-§3 — prediction-vs-verdict over
   `HYPOTHESES.md`'s P1-P15 and R1-R8, every byte reading re-derived from the goldens
   (`python3 spec/lab-evidence/e2e42-p2b/chaindump.py golden/e48p1/<N>/<N>.REL`,
   `python3 tools/reldump.py ...` for DATA sizes and chain fills). Keep the MISSes.
3. Commit the evidence: `git add golden/e48p1 spec/lab-evidence/e2e48-p1/RESULTS.md && git
   commit -m "E2E-48/P1 [dr]: 24-probe condition-form and DATA-area bank measured"` (nothing
   pre-existing lives inside `golden/e48p1`; never `git add -A`).
4. Fix the DATA-size double-count in `ocaml/lib/bind.ml` `section2`'s `span` (≈2146): exclude
   STATIC-class rows (the `stc` decision is bind.ml ≈995; `bind_rows` carries the auto flag).
   Rebuild, then `python3 tools/e2e_gate.py` must still print **1074 byte-exact / 0 fail**
   before any codegen work — the fix may not move an existing specimen.
5. Implement in `ocaml/lib/codegen.ml` only what a golden pins: `Eprefix(NegL, Eident Vbit1)`
   test arm (`3A/B7/FA`) beside the existing `Vbit1` arm (≈7395); `b = (cond)` = materialiser +
   `0x32` (replacing the refusal at ≈8220); the per-class materialisers measured in
   `HANDOFF.md` → Last verified state (including DR's `DAD H` bias defect and the `ADI FF/SBB
   A` negation); the `^(cond)` skip inversion `C2→CA`; the `&`-bit operand in `lower_bool`;
   the `?QB08C/?PNBOP` bit PUT item; STATIC-on-CHARACTER per E48B6. Register `E48A*/E48B*` in
   `tools/e2e_gate.py`'s `SPECIMENS` against `golden/e48p1/<N>/<N>.REL`.
6. Write claims **C309+**, `INVENTORY.txt`/`COVERAGE.tsv` rows, run the gate, commit, re-run
   `python3 tools/corpus_census.py --check` — CREATE is this phase's target EXACT (15 → 16).

## Next action (historical — deployment window)

**Not established by this session.** A deployment session deliberately did not choose the
compiler's next task, and inventing one here would put an unmeasured intention into the file a
fresh session trusts. The first action of the next session is therefore evidence-reading, not
implementation:

> Read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7 (CREATE blockers), §8 (the recorded gate
> verdict) and §9 (the unfixed `data=` reporting defect), plus
> `spec/lab-evidence/e2e42-p2c/HYPOTHESES.md`, plus claims `C296`–`C308` in `spec/CLAIMS.md`,
> then `spec/INVENTORY.txt` rows whose refusal text names `^eofile` or a `BIT(1)` condition store.
> Expected output: the candidate next phases written as *pre-registerable hypotheses* (e.g. the
> `^eofile`-in-`DO WHILE` condition form, the `BIT(1)` condition store, the `data=` reporting defect
> in `pli80c`'s summary line). Pick one, write its probe bank and predictions, commit them **before**
> any oracle run — and replace this section with the exact chosen command.

## Discoveries not yet incorporated

- **Renewal e2e test 2026-10-29 — PASSED and closed.** Durable chain, attested-handoff
  recovery, file-only successor bootstrap and auto-checkpoint preservation all verified
  (renewal 1/8, parent `01a188a5-2c00-708a-affc-0a48428f85d5` → successor
  `01a188a6-36ee-708a-affc-0a4c9333a1c9`, checkpoint `g2-470d507dbf6c`). The successor's
  start-pressure reading (~9 000 remaining) was **not** an anomaly: the test deliberately set
  `CONTEXT_GUARD_SYNTHETIC_REMAINING=9000` in the child *process* environment, and that
  synthetic override is re-read at every session_start in the process — by design, not
  measurement. The INFRA TEST WINDOW is closed: the genuine next action above was restored
  verbatim from `a6eec67`. Full record: `PROGRESS.md` → Renewal test window; lessons in
  `LEARNINGS.md`.

- `AGENTS.md`'s reading order, the guard's managed-block rules and `PROTOCOL.md` Part 2 are new to
  this repository; nothing in `spec/` has been reconciled against them, and nothing in `spec/`
  needed reconciling (the guard writes no scientific file).
- `README.md` "Current status (rolling)" is stale relative to the ledger: it still ends at
  **E2E-1 / C067** ("Next: widen codegen to RTL-call arithmetic …"), while HEAD is deep in E2E-42.
  It was deliberately **not** edited here (it is outside the authorized file list for this
  deployment) and is not to be used for status. Correcting it is an open, low-risk documentation
  task for a normal session.
- `generationReserve: 20000` in `handoff.config.json` is an **initial policy value**, not a
  verified fit for the model actually used on DRPLi. It should be checked against the real
  context window and max-output budget reported by `/guard status` before being treated as tuned.
- **Resolved 2026-10-29 (operator decision):** project trust was granted for the exact path
  `/home/john/projects/sushiworks/pli80` (plain `pi` from the project root now auto-discovers
  the extension and the skill; verified in the session started 16:58 UTC — parent cmdline is
  bare `pi`, guard loaded once). Renewal is ENABLED in `handoff.config.json`
  (`enabled/autoRenew true`, `maxRenewals 8`) and Pi auto-compaction is disabled for this
  project via `.pi/settings.json`. Controlled launches strip the inherited
  `CONTEXT_GUARD_AUTO_RENEW=1` with `env -u CONTEXT_GUARD_AUTO_RENEW` so the project config is
  authoritative (see `PROTOCOL.md` → Load).
- Managed checkpoint blocks were hand-edited **once**, deliberately, as the E2 test of the
  level-3 auto-checkpoint preservation path (a `TEST-E2-*` marker, since superseded by the final
  `/handoff` write). Outside such an explicit test, blocks are guard-written only.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 5
checkpoint-id: g5-e13e44ea140a
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 2, remaining ~14331, session 01a188bf-e7a9-7470-93c0-80d7f44bde5e)
checkpointed: 2026-10-29T18:11:29.070Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 93031c01c2ed5f95b67826d9cd92f0d400d436e921bc20b2b937e9d675778f65
source-handoff: e0f6bba9928e0362253cd831b1b1e337a01ba4db67c5d70f9549090857aba524
source-learnings: 3cbc63e02f60bff8668bcc549782a5dc7f4f3491c3c243e6724fcea2713e6f40
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3


readiness-by: session:01a188bf-e7a9-7470-93c0-80d7f44bde5e
readiness-at: 2026-10-29T18:11:29.074Z
readiness-checkpoint: g5-e13e44ea140a
### Last verified state
guard level 2; checkpoint requested (renewal tool refresh)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48/P1, the exact continuation

1. `cd /home/john/projects/sushiworks/pli80 && git rev-parse HEAD` → expect `3401821…` or a
   descendant; `git status --porcelain=v1` → expect only `?? golden/e48p1/`.
2. Write `spec/lab-evidence/e2e48-p1/RESULTS.md` §1-§3 — prediction-vs-verdict over
   `HYPOTHESES.md`'s P1-P15 and R1-R8, every byte reading re-derived from the goldens
   (`python3 spec/lab-evidence/e2e42-p2b/chaindump.py golden/e48p1/<N>/<N>.REL`,
   `python3 tools/reldump.py ...` for DATA sizes and chain fills). Keep the MISSes.
3. Commit the evidence: `git add golden/e48p1 spec/lab-evidence/e2e48-p1/RESULTS.md && git
   commit -m "E2E-48/P1 [dr]: 24-probe condition-form and DATA-area bank measured"` (nothing
   pre-existing lives inside `golden/e48p1`; never `git add -A`).
4. Fix the DATA-size double-count in `ocaml/lib/bind.ml` `section2`'s `span` (≈2146): exclude
   STATIC-class rows (the `stc` decision is bind.ml ≈995; `bind_rows` carries the auto flag).
   Rebuild, then `python3 tools/e2e_gate.py` must still print **1074 byte-exact / 0 fail**
   before any codegen work — the fix may not move an existing specimen.
5. Implement in `ocaml/lib/codegen.ml` only what a golden pins: `Eprefix(NegL, Eident Vbit1)`
   test arm (`3A/B7/FA`) beside the existing `Vbit1` arm (≈7395); `b = (cond)` = materialiser +
   `0x32` (replacing the refusal at ≈8220); the per-class materialisers measured in
   `HANDOFF.md` → Last verified state (including DR's `DAD H` bias defect and the `ADI FF/SBB
   A` negation); the `^(cond)` skip inversion `C2→CA`; the `&`-bit operand in `lower_bool`;
   the `?QB08C/?PNBOP` bit PUT item; STATIC-on-CHARACTER per E48B6. Register `E48A*/E48B*` in
   `tools/e2e_gate.py`'s `SPECIMENS` against `golden/e48p1/<N>/<N>.REL`.
6. Write claims **C309+**, `INVENTORY.txt`/`COVERAGE.tsv` rows, run the gate, commit, re-run
   `python3 tools/corpus_census.py --check` — CREATE is this phase's target EXACT (15 → 16).

### Guard notes
E2E-48/P1 in progress. Durable state is committed at 8285ba0 (tree clean). Continue from HANDOFF.md -> "## Next action — E2E-48/P1, the exact continuation": (1) write spec/lab-evidence/e2e48-p1/RESULTS.md as the prediction-vs-verdict table over HYPOTHESES.md's P1-P15 + R1-R8 rows, re-deriving every byte reading from golden/e48p1/*.REL (keep both MISSes: G3's "my compiler refuses every shape" and P15's predicted refusal of `put list(b)`); (2) fix the DATA-size double-count in ocaml/lib/bind.ml section2's `span` so STATIC-class rows are not charged (codegen.ml:12340 then needs no change), rebuild with `cd ocaml && opam exec --switch=default -- dune build`, and require python3 tools/e2e_gate.py to still print 1074 byte-exact / 0 fail before any codegen work; (3) implement only golden-pinned arms in codegen.ml (^bit test 3A/B7/FA, condition->BIT(1) store ending D6 01/9F/32, the per-class materialisers including DR's DAD H bias defect and ADI FF/SBB A negation, ^(cond) skip inversion C2->CA, & with a bit operand, ?QB08C/?PNBOP bit PUT item, STATIC-on-CHARACTER per E48B6); (4) register E48A*/E48B* in tools/e2e_gate.py SPECIMENS, write claims C309+, update INVENTORY/COVERAGE, run the gate, re-run the census (CREATE target EXACT). Never rewrite existing goldens; stage explicit paths only; do not push.
<!-- guard:end checkpoint -->
