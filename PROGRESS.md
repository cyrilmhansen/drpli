# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

**E2E-48/P1 is CLOSED: all 24 probes of `golden/e48p1/` are whole-file byte-identical and all 24
are registered on the byte panel. Gate measured 1098 byte-exact / 0 fail, negative 184/184,
divergence 9/9, coverage 102 rows 0 errors, census `--verify` clean.**

Commits this session (each verified by measurement, in order): `f839f52` census re-measured after
`371a12e` (the drift was CREATE advancing, not regressing) · `fa09b97` prescan demand
`bit_store_cond_bytes` (E48A12 exact; the store arm had allocated a pool cell the prescan never
demanded) · `df4b9c8` step 4, the BIT(1) PUT item `LDA / MVI B,01 / ?QB08C / ?PNBOP` with its own
tail replacing `?PNCOP` (23/24) · `613385b` step 5, STATIC-on-CHARACTER (full-extent blank-padded
cell, 0 pool bytes, read at the declared length) + census re-measured (24/24) · `992ccad` panel
registration (+24 SPECIMENS, INVENTORY 1098 via `--update-inventory`) and claims **C309-C316**.

**Pending (recorded, not started):** (a) `spec/COVERAGE.tsv` rows citing C309-C314 and the E48*
probes — `coverage_check` passes without them, so this is a documentation gap, not a red row;
(b) the `[TBD]` list inside C310/C313/C314, which needs a NEW pre-registered round (E48C) — the
CREATE-vs-E48 SCVCM load-order discriminator (18 vs 17 bytes) is the one that blocks a corpus
program; (c) CREATE is still NOT byte-exact and its measured blocker is now front-end:
`pli80c.ml` never expands `%include`, so `get list (name)` (declared in RECORD.DCL) refuses with an
unbound name. Do not implement any of these before the oracle has measured them.

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

- **E2E-48/P1 step 5, resumed** — see `HANDOFF.md` → `## Next action

See `HANDOFF.md` → `## Next action — E2E-48 round 2 (the [TBD] list), or the COVERAGE rows`.
E2E-48/P1 step 5 is closed (24/24 byte-identical, 1098/0 measured at `992ccad`); the successor
picks either the pre-registered E48C discriminator round, or the COVERAGE rows, or `%include`
(CREATE's measured front-end blocker) — in that order of value.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 10
checkpoint-id: g10-87f6c85a9ad6
checkpoint-kind: auto
content-delta: new
readiness: unattested
guard-level: 3
checkpointed: 2026-10-29T20:10:52.275Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: cee577b1760ea6379ccb2a0e9e06aa65351c103a38cf57d7ad610620b29d3b8a
source-handoff: c68194f2fbd8ac14cf6e9ab3884c71709c6502d3a314c0d24eae242b94a491f3
source-learnings: f5b7aec4086cd991c8643ab482d8a9704dc015587bef3b30952a698259e18d8c
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3
next-action: — E2E-48 round 2 (the [TBD] list), or the COVERAGE rows

Steps 1-5 and panel registration are DONE; E2E-48/P1 is closed at 24/24 byte-identical and
1098/0. Pick ONE, in this order of value:

1. **Pre-register E48C to measure the SCVCM load-order discriminator** (the only [TBD] that blocks
   a corpus program: CREATE's 18-byte store). Write the probe bank and the predictions, COMMIT them
   BEFORE any oracle run (PROTOCOL #1), then measure with `oracle/batch.py --tag e48p2c` (needs
   `--reuse` if the tag exists; it only ADDS programs). Candidates that vary the discriminator:
   the same `eofile = (name = 'EOF')` store in a DO-WHILE body vs a straight-line body vs behind a
   `put`; a VARYING **member** left operand (the `Mem` shape `bit_cond_mat` refuses today).
   Expected output: new goldens + a claim that names the rule, or a recorded `dr-refuses` row.
2. **`spec/COVERAGE.tsv` rows** for the shapes now lowered (categories COND/STOR/IO citing
   C309-C314 and the E48* probes — the probes are on the panel now, so citations validate).
   Then `python3 tools/coverage_check.py` and `python3 tools/e2e_gate.py` (must stay 1098/0).
3. `%include` in the main pipeline (CREATE's real blocker) — bigger, and needs its own
   pre-registered round for DR's search order/case rules.

Commands to start either way:
  `git rev-parse HEAD` -> expect `992ccad` or a descendant; `git status --porcelain=v1` -> expect
  clean (or only handoff files); `python3 tools/e2e_gate.py` -> **1098 byte-exact / 0 fail**.
<!-- guard:end checkpoint -->
