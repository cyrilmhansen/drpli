# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

**E2E-48/P1 — the condition-form half of CREATE: `^bit(1)` tests, conditions stored into
BIT(1), and the DATA-area static/automatic law. In progress at this checkpoint.**

*Done (measured/committed this session, 2026-10-29):* goldens already committed at `ece657e`
(24 programs, 15/15 + 9/9 accepted); **`spec/lab-evidence/e2e48-p1/RESULTS.md`** written with
every byte reading re-derived from the `.REL` records — prediction-vs-verdict over P1-P15 and
R1-R8, all MISSes kept (P15 `put list(b)` **accepted** against a predicted refusal; P6/P7/P11
spelling misses; the "8-byte/5-byte-chain" miscount). RESULTS §5 **falsifies** three inherited
readings: the "DR `DAD H` bias defect" (golden bytes 0x09 = standard DAD B, bias applied —
root cause: a mnemonic typo in `chaindump.py`, fixed in the same commit **388673b**); CREATE's
"16-byte LHLD" SCVCM store (actual **18 bytes** `LXI H,var / XCHG / LXI H,lit`, vs **17 bytes**
`LXI H,lit / LXI D,var` at every E48 site — the **discriminator is [TBD]**); FLTPOLY2's `2A`
store (actual `0x21`). The **DATA-size double-count is FIXED** (bind's `section2` `span` no
longer charges STATIC rows, commit **a8d1c3a**): E48A3/E48A4 now compile **byte-identical** to
the goldens and the gate held **1074 byte-exact / 0 fail**, census unchanged (15 EXACT).

*Not done (the continuation):* the golden-pinned codegen arms (`^b` test → `3A/B7/FA`, `^(cond)`
skip inversion `C2→CA`, the per-class materialisers ending `32 <cell>`, the `&`-bit operand
`PUSH PSW/LDA/POP B/ANA B` under one `F2`, the `?QB08C/?PNBOP` bit PUT item, STATIC-on-
CHARACTER per E48B6) — exact arm locations and reusable helpers are recorded in `HANDOFF.md`
→ Next action step 5; then panel registration, claims **C309+**, INVENTORY/COVERAGE, gate,
census.

**E2E-42/P2c — the named-file `SKIP` bank: pre-registered, measured, lowered, and the
harness/audit layer that came out of it.** Recorded HEAD for the scientific work:
`1e5fe03` (panel +18 byte-exact objects, `[C303]` corrected) through `0a50fc4`
(`E2E-42/P2c [doc]`, 2026-10-29). Evidence:
`spec/lab-evidence/e2e42-p2c/{HYPOTHESES,RESULTS,GATE-TIERS}.md`,
`probes/E46N*.PLI`, `golden/e42p2c*/`, `golden/e42p2cdr/`, claims `[C296]`–`[C308]`.

Parallel to it, this session ran an **infrastructure phase**: deploying Pi Handoff
(context-guard `v0.1.0-dev.1`, commit `2ea6219`) into DRPLi, validating it read-only (Phase D)
and then in one controlled writable session (Phase E). **That infrastructure phase is now
complete**; nothing else in it is pending except operator decisions listed below. Infrastructure
never outranks the compiler work above; it changes no implementation strategy and no evidence.

## Completed

*Scientific — recorded, not re-run by this session:*
- `PUT FILE … SKIP` behaviour measured on DR and lowered byte-exactly: `E46N11`–`E46N22`
  bank, 18 specimens added → **1074 byte-exact / 0 fail** recorded in
  `spec/lab-evidence/e2e42-p2c/RESULTS.md` §8; runtime panel 71/71 as recorded.
- Gate tiering + `--link-run` able to fail; slow CP/M arms delegated to the external
  `rune-ci` builders (`GATE-TIERS.md`, `spec/notes/rune-ci-external-gate.md`).
- The `timeout-or-hang` collapse in `oracle/run.py`/`linkrun.py` re-measured by exit code:
  51 timeouts, 2 emulator deaths (`PD7`, `PD9`), 2 that do terminate (`RFACT`, `V5`) —
  `[C308]`, and the `HANG_ARMS` / `NO_RUN_ARMS` / `NO_LINK_ARMS` split in `tools/e2e_gate.py`.

*Infrastructure — performed and verified by this session (see `HANDOFF.md` for the boundary):*
- `.gitignore`: appended only the `# Pi Handoff runtime state` / `.pi-guard/` rule; all
  pre-existing oracle/golden/build/thirdparty rules verified still matching.
- Extension installed at `.pi/extensions/context-guard/{index,core,config,checkpoint,renewal}.ts`,
  taken from the pinned Git revision (bytes verified by SHA-256 and blob id against
  `v0.1.0-dev.1` / `2ea6219`); nothing else from the source repo was copied.
- Skill installed at `.agents/skills/pi-handoff/{SKILL.md,references/bootstrap.md,references/commands.md}`.
- `handoff.config.json` written: `readOnly: true` during validation, `enforceClosing: false`,
  `autoCheckpointAtHandoffLevel: false`, renewal disabled, `generationReserve: 20000`
  (initial policy value, not yet tuned).
- Durable files created: `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`, `HANDOFF.md`, `PROGRESS.md`,
  `LEARNINGS.md`.
- **Phase D (read-only) passed in the real Pi runtime**: extension loaded with no import/TS
  errors; `/guard status` reported read-only mode + the real model/window/reserve; `/handoff
  verify` reported `missing` without writing; `/handoff ready check` evaluated without
  attesting; `/guard simulate 30000` → level 1, `/guard simulate 10000` → level 3 with **no**
  checkpoint written; `/handoff` reported a dry run; no `.pi-guard/` directory was created; every
  tracked file hash, the ignored-file count (471 102) and the profile settings were unchanged.
- **Phase E (writable) passed**: `/handoff` → `g1-01ad31c23339`, generation 1,
  content-delta `initial`, freshness `current`; `/handoff ready check` → READY with four blocking
  PASSes; `/handoff ready` → attested; both blocks shared one transactional identity.
  A level-3 automatic checkpoint (`checkpoint-kind: auto`) then preserved a substantive
  "Last verified state" line and a "Guard notes" block **verbatim**, leaving all manual prose
  outside the managed blocks byte-identical, and left `GOAL.md`/`LEARNINGS.md` untouched.

## Pending

- **E2E-48/P1 continuation** — see `HANDOFF.md` → `## Next action — E2E-48/P1 step 5`: land
  the golden-pinned codegen arms, register `E48A*/E48B*` in the byte panel, write C309+ from
  RESULTS §3, update INVENTORY/COVERAGE, run the gate, re-run the census. The
  CREATE-vs-E48 SCVCM load-order discriminator is `[TBD]` and must be MEASURED (a new
  pre-registered probe round) before it is implemented; CREATE EXACT depends on it.
- **Operator decision taken 2026-10-29:** project trust granted (exact path, production
  profile); renewal ENABLED (`enabled/autoRenew true`, `maxRenewals 8`,
  `generationReserve 20000` retained); Pi auto-compaction disabled for this project only via
  `.pi/settings.json` — global profile settings untouched. Remaining open decisions: tuning
  `generationReserve` against the real budget, whether to enable `enforceClosing`, any push
  to GitHub (none authorized, none performed).
- Open documentation item: `README.md` "Current status (rolling)" is stale at E2E-1/C067.
- Compiler-side, as recorded by P2c (not started here): `CREATE` still fails on `^eofile` in a
  `DO WHILE` condition and on storing a condition into `BIT(1)`; `pli80c`'s `data=` summary
  number is wrong and deliberately unfixed; P0's residual `my-gap` rows (`E46H1` keyed direct
  input, `E46H3` record input, `E46H4` sequential input, unlowered `PAGESIZE`/`LINESIZE`/
  `ENVIRONMENT`, `OUTPUT` without `STREAM`) remain.

## Verified evidence

Read, not re-run, during this deployment: `spec/CLAIMS.md` (`[C296]`–`[C308]`; ledger ends at
`## C308`), `spec/lab-evidence/e2e42-p2c/RESULTS.md`, `.../GATE-TIERS.md`,
`.../HYPOTHESES.md`, `spec/notes/e2e42-p0-front-end-integrity.md`,
`spec/notes/rune-ci-external-gate.md`, `spec/INVENTORY.txt`, `spec/COVERAGE.tsv`,
`spec/RUNTIME.txt`, `spec/DIVERGENT.txt`, `spec/PERIMETER.md`, `SOURCES.md`.

Measured by this session: `git rev-parse HEAD` = `0a50fc4c745838e3af1641c8a6f68fd17ed1371a`
on `main`; clean tree; 12 028 tracked / 471 102 ignored files; nested repos at
`c6f0f2d` (PLI-2000) and `91fd28e` (z80pack), both clean; Pi 1.4.0; profile
`/home/john/.sushi/pi` (compaction enabled, unchanged); 417 G free on `/home`.

Measured by this session about the infrastructure: the nine installed files hash-match the
pinned release (`git show 2ea6219:<path>`); `/guard status` reports window 220 000 /
maxOutput 65 536 / reserve 20 000 (9.1 % of the window) and `renewal: policy
enabled=false autoRenew=false`; checkpoint identities `g1-01ad31c23339` and
`g2-f3ea401c1ad5` were produced by real guard writes, and both were later superseded by the
final deployment checkpoint.

## Blockers

- No scientific blocker was created or removed by this session.
- **No infrastructure blocker remains from this deployment**: Phases A–E all passed, the guard
  loads in the real runtime, and both the read-only and the writable validations behaved as
  specified. Two conditions are recorded, not concealed:
  (a) the level-3 auto-checkpoint test left the chain at generation 2 before the final
  deployment checkpoint was written — an honest refresh, not a repeated uncontrolled one;
  (b) the inherited `CONTEXT_GUARD_AUTO_RENEW=1` is now neutralized for controlled launches
  by stripping it (`env -u`); `handoff.config.json` is authoritative (see `PROTOCOL.md` → Load).

## Renewal test window (2026-10-29) — **CLOSED, PASSED**

Operator-authorized end-to-end renewal test, run as a real model-driven renewal (RPC-mode child
session, production profile, trust-based auto-load, no `-e`, synthetic level-3 threshold
`CONTEXT_GUARD_SYNTHETIC_REMAINING=9000`):

- Parent `01a188a5-2c00-708a-affc-0a48428f85d5` reported `autoCompactionEnabled=false` live;
  read the durable files, invoked `handoff_renew` exactly once (trigger `model`); guard refreshed
  + attested checkpoint `g2-470d507dbf6c` and switched to successor
  `01a188a6-36ee-708a-affc-0a4c9333a1c9`, which started with **3 messages** (identity +
  recovery), i.e. fresh context recovered from durable files only — no transcript replay, zero
  compaction events in either session.
- Durable counter verified in `.pi-guard/renewal-state.json`: `renewalsDone: 1/8`,
  `renewedFromCheckpointId: g2-470d507dbf6c`, chain `chain:01a188a5-…`, `stopped: false`.
- Successor identified and executed the test task from the files alone (highest claim **C308**),
  wrote its results into the durable prose, and stopped without re-renewing.
- The successor's ~9 000-remaining start reading was the test harness's own synthetic override
  (re-read at every session_start in the process), **not** an anomaly — resolved in
  `LEARNINGS.md`.
- Only `HANDOFF.md`, `PROGRESS.md`, `LEARNINGS.md` and the guard-written managed blocks were
  touched; directory-listing checksums of every protected tree (artefacts/manuals/extracted/
  references/oracle/golden/probes/build/ocaml/spec/tools/thirdparty) verified unchanged; global
  profile `settings.json` untouched; `trust.json` holds only the pre-existing exact-path entries.
- Closure (this session): genuine Next action restored verbatim from `a6eec67`, checkpoint
  refreshed and re-attested.

## Next action

See `HANDOFF.md` → `## Next action — E2E-48/P1 step 5, the exact continuation (codegen arms)`
(seven numbered items, starting with the `Eprefix(NegL, …)` arm in `lower_test_skip0`, with
all arm locations and reusable helpers already measured and recorded there).

See `HANDOFF.md` → `## Next action`: read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7–§9,
`.../HYPOTHESES.md` and claims `C296`–`C308`, then write the candidate next phase as
pre-registered hypotheses and replace that section with one chosen, exact next step.
The renewal test window is closed; infrastructure needs nothing further this session.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 5
checkpoint-id: g5-e13e44ea140a
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 2
checkpointed: 2026-10-29T18:11:29.070Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 93031c01c2ed5f95b67826d9cd92f0d400d436e921bc20b2b937e9d675778f65
source-handoff: e0f6bba9928e0362253cd831b1b1e337a01ba4db67c5d70f9549090857aba524
source-learnings: 3cbc63e02f60bff8668bcc549782a5dc7f4f3491c3c243e6724fcea2713e6f40
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3
next-action: — E2E-48/P1, the exact continuation

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
readiness-by: session:01a188bf-e7a9-7470-93c0-80d7f44bde5e
readiness-at: 2026-10-29T18:11:29.074Z
readiness-checkpoint: g5-e13e44ea140a
<!-- guard:end checkpoint -->
