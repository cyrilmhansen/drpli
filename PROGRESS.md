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
checkpoint-generation: 12
checkpoint-id: g12-b9a7bfdfd150
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-10-29T20:14:46.078Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 300ed1c3a101f42da5f851cdf78cabad91879c5fce93ee9e8078c56dd862995c
source-handoff: d8c627c77f70e481592000c272fb50fb1f199abc65cddff8655668fe6dc8ee0e
source-learnings: 123479d0c781a1ca2ebc186ad04a3754ce3ae21837dc4f1b878e5322e64f768d
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
2. **`spec/COVERAGE.tsv` rows** - started but NOT written (this session reached the format check
   only, then hit level 3). Format facts MEASURED here, so do not re-derive them: **15** tab-separated
   columns (`id category construct contract perimeter manual_ref dr_status mine_status rel_parity
   runtime probes corpus boundary confidence provenance`); `manual_ref` is column 6, which the FIRST
   table of `spec/COVERAGE-SCHEMA.md` omits - trust the second table and an existing row such as
   `COND.GE_LE`. `probes` = comma-separated INVENTORY keys (E48A1..E48B9 are on the panel now, so they
   resolve); `corpus` = names from the 44-program census (CREATE, EXPR2, FSCAN, LOAN2, MPMCALLB,
   REPORT all qualify); `provenance` = space-separated `[Cnnn]` (C309-C316 exist); use
   `manual_ref = NONE:<why>` to stay clear of the OCR page check. `tools/coverage_check.py` line 8 and
   213: a `MEASURED`/`SINGLE_SAMPLE` row must name at least one probe that one of its OWN cited claims
   also names - cite the claim carrying the specimen ([C313] names E48A15/A6/A7/B8). Drafted rows:
   COND.BIT1_NEG_TEST (E48A1,A2,A5,A12,A13,B1,B7 EXACT:7, [C309][C311]); STOR.BIT1_COND_STORE
   (E48A6..A12,B8,B9 EXACT:9, [C310], boundary = the load-order / |c|<=3 / ='0'b [TBD]s);
   COND.AND_BIT1_OPERAND (E48A14 EXACT:1, SINGLE_SAMPLE, [C312]); IO.PUT_BIT1_ITEM (E48A15,A6,A7,B8
   EXACT:4, runtime NONE because no transcript was captured, [C313]); DECL.STATIC_CHAR (E48B5,B6,B7
   EXACT:3, mine_status PARTIAL because STATIC-on-CHARACTER VARYING still refuses, [C314]).
   Validate with `python3 tools/coverage_check.py` (exit 0), then `python3 tools/e2e_gate.py`: the row
   count goes 102 -> 107 and the byte panel must stay 1098 byte-exact / 0 fail.
3. `%include` in the main pipeline (CREATE's real blocker) — bigger, and needs its own
   pre-registered round for DR's search order/case rules.

Commands to start either way:
  `git rev-parse HEAD` -> expect `992ccad` or a descendant; `git status --porcelain=v1` -> expect
  clean (or only handoff files); `python3 tools/e2e_gate.py` -> **1098 byte-exact / 0 fail**.
readiness-by: session:01a18927-3b36-7470-93c0-80e28e177244
readiness-at: 2026-10-29T20:14:46.080Z
readiness-checkpoint: g12-b9a7bfdfd150
<!-- guard:end checkpoint -->

## Verified evidence

Measured by the session that closed E2E-48/P1 (2026-10-29/30), not quoted from a report:

- `python3 tools/e2e_gate.py` at HEAD `992ccad` -> **1098 byte-exact / 0 fail of 1098**; negative
  panel 184/184 refused; divergence 9/9; coverage 102 rows / 0 errors; census `--verify` clean
  (EXACT 15, DIFFERS 0, REFUSED 26, UNEXPECTED 0); rc=0. Three earlier gate runs in the same
  session, before registration, each measured 1074/0.
- 24-probe sweep (`pli80c.exe probes/$n.PLI` then whole-file `cmp` vs `golden/e48p1/$n/$n.REL`)
  -> **24 BYTE-IDENTICAL**; it was 14/24 when this session started.
- `dune build` rc=0; warning multiset compared cache-neutrally against the `df4b9c8` tree in a
  scratch copy -> identical (kinds 11/26/27/32/39/57/8/9 = 22/15/28/2/14/2/17/26).
- `tools/corpus_census.py --check <prev>` twice -> counts IDENTICAL both times; five `msg` deltas,
  all of them the compiler advancing (CREATE, REPORT, MPMCALLB, EXPR2/FSCAN/LOAN2 wording).
- Authorities read: `spec/lab-evidence/e2e48-p1/RESULTS.md` sections 1-6, `golden/e48p1/`,
  claims **C309-C316** in `spec/CLAIMS.md`.

## Blockers

- None scientific is open, and nothing is half-edited; the tree is clean at this boundary.
- What limits further parity is **missing evidence**, never a licence to guess: the CREATE-vs-E48
  SCVCM load-order discriminator (18-byte `LXI H,var / XCHG` vs 17-byte `LXI H,lit / LXI D,var`)
  was not varied by any probe in this bank, so CREATE's completion stays `[TBD]` until an E48C
  round measures it (C310). Same for the store forms and PUT shapes listed in C310/C313/C314.
- CREATE's measured blocker is front-end: `pli80c.ml` does no `%include` expansion, so
  `get list (name)` (from `artefacts/RECORD.DCL`) refuses on an unbound name. Proposed, unverified.
