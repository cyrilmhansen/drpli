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

## Renewal test window (2026-10-29)

**Successor result (renewal 1/8, session 01a188a6, 17:12Z+):** renewal e2e **passed** — fresh
successor recovered the test task from durable files only, executed it (highest ledger claim
**C308**; no scientific file touched), durable chain counter verified in
`.pi-guard/renewal-state.json` (`renewalsDone: 1`, from checkpoint `g2-470d507dbf6c`). The
successor hit guard **level 3 at session start** (~9 000 remaining of 220 000) and the guard
auto-wrote unattested checkpoint `g3-0c5843a47674`; cause of start-pressure unexplained — see
`LEARNINGS.md` 2026-10-29 successor block (item marked [TBD]). Successor did not re-renew
(procedure: report and stop). **Pending closure:** restore genuine next action from pre-test
commit `a6eec67`, refresh + attest the checkpoint, end the test window.

An operator-authorized end-to-end renewal test is running: HANDOFF.md → Next action is
temporarily a harmless evidence-reading task; after the test it is restored from the
pre-test commit `a6eec67`, the checkpoint refreshed, attested and verified fresh.

## Next action

**[Test window 2026-10-29]** See `HANDOFF.md` → `## Next action` (currently the authorized
renewal e2e test; the genuine DRPLi action below is preserved and restored afterwards).
Genuine action: read `spec/lab-evidence/e2e42-p2c/RESULTS.md` §7–§9,
`.../HYPOTHESES.md` and claims `C296`–`C308`, then write the candidate next phase as
pre-registered hypotheses and replace that section with one chosen, exact next step.
Infrastructure-wise: nothing further is authorized in this session beyond Phase D/E validation
and the reporting steps.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 3
checkpoint-id: g3-0c5843a47674
checkpoint-kind: auto
content-delta: none
readiness: unattested
guard-level: 3
checkpointed: 2026-10-29T17:12:41.572Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 7ddf764d69ab80a04269d44a7fd01b96787e74799aaa8c18226baac64da3fa61
source-handoff: 6dff3309341bf5e65d3ced1e4021e6e565ae4a8f2833beb2e008f07566800cb7
source-learnings: a045846945dd3949bc9425561f3f41dad007eb9ba6523b8fa055ff6906d2e53e
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3
next-action: **[INFRA TEST WINDOW — 2026-10-29]** This section is deliberately swapped for the operator-
authorized end-to-end renewal test. The task for the session reading it now is the harmless
evidence read below — **not** compiler development:

> Read `spec/CLAIMS.md` and identify the highest-numbered claim and what it records (one short
> paragraph, reported in chat). Do **not** edit any project file. Do **not** run the compiler,
> the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`. When the context guard reports
> level-3 pressure and offers renewal, first ensure this session's state is recorded, then
> invoke the `handoff_renew` tool exactly once with a short note naming the test. The successor
> session must report — from the durable files alone — which task it recovered, then stop.

The genuine post-test DRPLi next action is preserved verbatim in git (`HANDOFF.md` at the
pre-test commit `a6eec67`) and summarized in `PROGRESS.md` → Next action; it is restored and
re-attested when this test window closes.
<!-- guard:end checkpoint -->
