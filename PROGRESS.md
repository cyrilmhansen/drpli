# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase

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

- Operator decisions (deliberately **not** taken by this session): project trust for `.pi/`
  auto-loading and `.agents/skills/` discovery; tuning `generationReserve` against the real
  budget (window 220 000, maxOutput 65 536 observed); whether to enable `enforceClosing`;
  whether to enable renewal (currently **off**, and the shell that launches Pi here exports
  `CONTEXT_GUARD_AUTO_RENEW=1`, which would override the config — see `LEARNINGS.md`); any push
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
- Infrastructure blockers, if any, will be named here from Phase D/E results; an extension
  that fails to load in the real Pi runtime is a failed deployment regardless of static checks.

## Next action

See `HANDOFF.md` → `## Next action`: read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7–§9,
`.../HYPOTHESES.md` and claims `C296`–`C308`, then write the candidate next phase as
pre-registered hypotheses and replace that section with one chosen, exact next step.
Infrastructure-wise: nothing further is authorized in this session beyond Phase D/E validation
and the reporting steps.
