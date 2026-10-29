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

## Last verified state

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

## Unfinished operations

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

## Next action

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
checkpoint-generation: 3
checkpoint-id: g3-0c5843a47674
checkpoint-kind: auto
content-delta: none
readiness: unattested
status: checkpoint (guard level 3, remaining ~9000, session 01a188a6-36ee-708a-affc-0a4c9333a1c9)
checkpointed: 2026-10-29T17:12:41.572Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 7ddf764d69ab80a04269d44a7fd01b96787e74799aaa8c18226baac64da3fa61
source-handoff: 6dff3309341bf5e65d3ced1e4021e6e565ae4a8f2833beb2e008f07566800cb7
source-learnings: a045846945dd3949bc9425561f3f41dad007eb9ba6523b8fa055ff6906d2e53e
source-config: 8e66b82b71db399633cd776d6a5329e70c0eb09173121cfb303569d5f6ba6bf3


### Last verified state
guard level 3; checkpoint requested (auto at level 3)

### Unfinished operations
- (none recorded)

### Next action
**[INFRA TEST WINDOW — 2026-10-29]** This section is deliberately swapped for the operator-
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

### Guard notes
deployment validated in the real Pi runtime (Phase D read-only: no writes, no .pi-guard/, dry-run /handoff; Phase E writable: schema-v3 checkpoint current + identity-consistent + attested; level-3 auto-checkpoint preserved substantive notes). HEAD at commit time: ce8d19f on main, tree clean. Renewal OFF, enforceClosing OFF, readOnly now false. No compiler/oracle/golden/spec/tool file touched; no gate run.
<!-- guard:end checkpoint -->
