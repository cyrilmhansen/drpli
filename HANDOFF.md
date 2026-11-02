# HANDOFF.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file is the recovery entry point: exactly ONE active Next-action heading at level 2. Closed-phase
history is archived under `docs/history/` (index: `docs/history/README.md`); science is
authoritative only in `spec/CLAIMS.md` and `spec/lab-evidence/`.

## Recovery instructions

1. Confirm the repository and revision:
   `cd /home/john/projects/sushiworks/pli80 && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --porcelain=v1`
   A dirty `handoff.config.json` is the OPERATOR's standing edit — investigate, never clean,
   never stage, never commit, never revert it. `AGENTS.md` → Protected.
2. Lean recovery: Pi auto-loads `AGENTS.md`; read this file and `PROGRESS.md` NOW.
   `PROTOCOL.md` governs all scientific procedure and is consulted before any unclear
   scientific/policy action; `GOAL.md` and `LEARNINGS.md` remain authoritative and are read
   selectively by pointer. A deferred read never weakens the protocol.
3. Check checkpoint freshness with `/handoff verify`. `stale` or `missing` means: re-derive
   state from commits and lab evidence, then refresh and attest with `/handoff finalize`.
   Do not trust this file's managed block over its prose.
4. Load evidence SELECTIVELY — the ledgers are far larger than the working window; a
   complete read of any of them is prohibited for recovery:
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C351' spec/CLAIMS.md` etc.;
     the E2E-49/P4 block starts at `grep -n '^## C348'`; the E2E-48 family is C309..C332,
     E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341, E2E-49/P3 is C342..C347, E2E-49/P4 is
     C348..C351. The ledger CURRENTLY ENDS at **C351** — no claim ids are owed. [C330] carries
     the labelled E2E-49/P1 CORRECTION append (positional length law); [C335]–[C338] carry
     labelled P3 CORRECTION appends and [C346] a labelled CITATION CORRECTION (the numeric
     ORDER law is [C104], never cite legacy [C027]/[C072] in provenance); [C335]/[C337]/
     [C344]/[C346] additionally carry labelled [E2E-49/P4 CORRECTION(S)] blocks (`9c42f3b`)
     and [C348] a labelled [E2E-49/P4 WORDING CORRECTION] (`5b0ccde`); falsified text is kept
     as written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p4/{RESULTS.md,HYPOTHESES.md,
     BASELINE-MINE.txt,PLAN.md,mkprobes.py}` (round CLOSED); prior rounds under
     `spec/lab-evidence/e2e48-*/` and `spec/lab-evidence/e2e49-p{1,2,3}/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.
6. **No active round** (E2E-50/P2 CLOSED 2026-11-02). A successor WITHOUT an operator
   instruction confirms HEAD/tree, runs `/handoff verify`, records state and STOPS. The
   E2E-50/P3 shortlist is `spec/lab-evidence/e2e50-p2/REPORT.md` §5 — a shortlist, NEVER an
   authorisation. Standing boundary: `/home/john/pli/*` (Runes lab `/home/john/pli/lab`,
   `/home/john/pli/cpm`, `/home/john/pli/runes-full-runs`) is READ-ONLY for this project
   unless an operator brief authorizes otherwise.
## Last verified state — E2E-50/P2 CLOSED (FULL compile-tier gate rc=0 measured at HEAD `545dcf1`, recorded `d648bcd`; CLOSE completed by this docs-only session — ledger ENDS at C351 UNCHANGED, byte panel 1174, coverage 133 rows, hostile suite self-counts 182)

- Landing chain (explicit paths, no push): bootstrap `459f51e`; emulator + redistribution
  audit `97ad1f0` (`docs/emulator-audit.md`; Package-A blocker = operator license decision);
  law+schema+TABLE corpus `a6163ef` (`spec/functional/tests/`, `docs/functional-testing.md`);
  harness `8523eda`; hostile suite 13 cases `d40aafb`+`149c6e2`; pre-registration + FX fixtures
  + `--census` `690c3a1`+`218c9be`; execution hop 6 re-verified read-only and committed `68348ac`
  (+`ec9d396`); step 7 `958c204`+`cdc5d13`+`545dcf1` (cpmcp stdio debt paid; Lane-A fallback
  repaired/proven; CLI stdout grammar pinned 171→182; `docs/functional-results.md`); step-8
  part 1 `d648bcd` (`REPORT.md` + gate), prose `68831ff`, guard refresh `e7664ed`, CLOSE here.
- Executed verdicts: FX-00 **PASS** (double-run `cmp` rc=0); FX-01 **FAIL attr=`emulator`**
  intended; TABLE-00/01 **first functional execution of a DRPLi-compiled program** — COMPILE
  896/1536 B, LINK PASS zero `UNDEFINED` + `PLILIB   RQST`, RUN `done` rc=0, ASSERT FAIL
  attr=`undefined` (framing F1 anchor law / F2 measured DR PLILIB 79-col wrap; CONTENT ≡
  REFERENCE); census BDOS-25-first — free core cannot host PLILIB programs (measured), full
  census UNMEASURED. Details: `spec/lab-evidence/e2e50-p2/`, `docs/functional-results.md`.
- Gate ACTUALS as printed at `545dcf1` rc=0 (recorded `d648bcd`): byte panel **1174/0**
  (cross-check `grep -c BYTE-EXACT` = 1174), negative **181/181** E46K14 `[dr-refuses]` UNMOVED,
  divergence **9/9**, coverage **133/0/0**, census **15/0/26/0** UNCHANGED, prose **5 clean**.
  No scientific claim/COVERAGE/INVENTORY/RUNTIME/golden/`ocaml/` byte changed this round.
- Measured by THIS closing session (docs-only, 2026-11-02): HEAD `e7664ed`; tree clean apart
  from the operator's `handoff.config.json` edit; checkpoint g131 verified **current** by
  replaying the guard's strip-block+rstrip SHA-256 prose law; close archive **23/23 blocks
  BYTE-EXACT** (independent re-extraction + `cmp`) with a completeness sweep over all
  superseded generations (0 unarchived lines): `docs/history/2026-11-02-e50p2-closed.md`.
  No half-finished Git operation; no emulator running.
## Next action — NO ACTIVE ROUND (E2E-50/P2 CLOSED 2026-11-02)

A successor WITHOUT an explicit operator instruction: confirm HEAD/tree (`git rev-parse HEAD &&
git status --porcelain=v1`; a dirty `handoff.config.json` is the OPERATOR's standing edit — never
stage, clean, revert or commit it), run `/handoff verify`, record state, and **STOP**. No
E2E-50/P3, no compiler/oracle/LINK-80/cpmsim/emulator/gate work without operator authorization.
If authorized: shortlist = `spec/lab-evidence/e2e50-p2/REPORT.md` §5 (P3-a anchor fix; P3-b
declare PLILIB wrap law from the oracle; P3-c BDOS 25 + license decision; P3-d TABLE-02) —
PROPOSALS, never an authorisation. Standing debts unchanged (`PROGRESS.md` → Pending: LOAN2
prescan, CREATE `%include`). Boundary: `/home/john/pli/*` read-only; never
`git clean`/`reset --hard`/`add -A`; explicit-path commits; no push; never renew mid-Git-op or
while an emulator runs; renewal values ONLY in `handoff.config.json`.
## Unfinished operations

- (none) — E2E-50/P2 CLOSED: steps 0–8 delivered; gate ACTUALS recorded `d648bcd`; superseded
  prose archived byte-verified (23/23) in `docs/history/2026-11-02-e50p2-closed.md`.
- Standing scientific debts unchanged (`PROGRESS.md` → Pending: LOAN2 prescan, CREATE
  `%include`); this round did not touch them.
- At this boundary: no half-finished Git operation, no emulator process running, `ocaml/`
  untouched (build only).
## Discoveries not yet incorporated

- (none in the ledger) — all E2E-50/P2 findings are recorded in `docs/emulator-audit.md`,
  `docs/functional-testing.md`, `docs/functional-results.md`,
  `spec/lab-evidence/e2e50-p2/{PLAN.md,step6/RESULTS.md,step7/RESULTS.md,REPORT.md}` and the
  classified hop sections of `LEARNINGS.md`. Ledger ENDS at C351; the F2 PLILIB wrap observation
  stays `proposed` until an oracle round declares it.
## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`;
  E2E-49/P3 two-generation close archive — in-flight prose at `4df35bb` AND the
  close-owed prose at `c140277` — `docs/history/2026-11-01-e49p3-closed.md`;
  E2E-49/P4 four-generation close archive — the arms-era Next actions at `19ab4e0` and
  `e13311c`, the step-6-era CLOSE instruction at `882f77c`, the close-authorized prose at
  `5c52bba` (identical at HEAD `b5f792c`) — `docs/history/2026-11-01-e49p4-closed.md`; E2E-50/P1
  closing-era prose `docs/history/2026-11-02-e50p1-closed.md`; E2E-50/P2 close archive — 8
  Next-action and 7 Unfinished generations + PROGRESS hop stack, 23/23 byte-verified —
  `docs/history/2026-11-02-e50p2-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 133
checkpoint-id: g133-694fb6b0f23f
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~-2972, session 01a199d7-21e8-7280-b553-bdc514e83dbf)
checkpointed: 2026-11-02T01:49:48.373Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: e9c7fb89a8a2a6e96af0619d6476ee80c985701791e935849cd17c3a85d8e9ff
source-handoff: c5f96641b77765c3f979a53f3e1fd30585301702b437910b71d91e30fef2f426
source-learnings: ca97f3157ab61678a8d0451860092d3bae0d2e6e6431478275cc026701cba9c0
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a199d7-21e8-7280-b553-bdc514e83dbf
readiness-at: 2026-11-02T01:49:48.375Z
readiness-checkpoint: g133-694fb6b0f23f
### Last verified state
guard level 4; checkpoint requested (finalize: E2E-50/P2 CLOSED (step-8 close landed at fb817df: 23/23 byte-verified archive docs/history/2026-11-02-e50p2-closed.md, completeness sweep 0 unarchived lines; HANDOFF/PROGRESS rewritten to NO ACTIVE ROUND with the gate ACTUALS recorded at d648bcd; LEARNINGS close note; ledger C351 unchanged; no compiler/oracle/gate/emulator run; no push). Successor WITHOUT an operator instruction: confirm HEAD/tree, /handoff verify, record state, STOP. P3 shortlist = spec/lab-evidence/e2e50-p2/REPORT.md section 5 (proposals, never an authorisation).)

### Unfinished operations
- (none recorded)

### Next action
— NO ACTIVE ROUND (E2E-50/P2 CLOSED 2026-11-02)

A successor WITHOUT an explicit operator instruction: confirm HEAD/tree (`git rev-parse HEAD &&
git status --porcelain=v1`; a dirty `handoff.config.json` is the OPERATOR's standing edit — never
stage, clean, revert or commit it), run `/handoff verify`, record state, and **STOP**. No
E2E-50/P3, no compiler/oracle/LINK-80/cpmsim/emulator/gate work without operator authorization.
If authorized: shortlist = `spec/lab-evidence/e2e50-p2/REPORT.md` §5 (P3-a anchor fix; P3-b
declare PLILIB wrap law from the oracle; P3-c BDOS 25 + license decision; P3-d TABLE-02) —
PROPOSALS, never an authorisation. Standing debts unchanged (`PROGRESS.md` → Pending: LOAN2
prescan, CREATE `%include`). Boundary: `/home/john/pli/*` read-only; never
`git clean`/`reset --hard`/`add -A`; explicit-path commits; no push; never renew mid-Git-op or
while an emulator runs; renewal values ONLY in `handoff.config.json`.

### Guard notes
E2E-50/P2 CLOSED (step-8 close landed at fb817df: 23/23 byte-verified archive docs/history/2026-11-02-e50p2-closed.md, completeness sweep 0 unarchived lines; HANDOFF/PROGRESS rewritten to NO ACTIVE ROUND with the gate ACTUALS recorded at d648bcd; LEARNINGS close note; ledger C351 unchanged; no compiler/oracle/gate/emulator run; no push). Successor WITHOUT an operator instruction: confirm HEAD/tree, /handoff verify, record state, STOP. P3 shortlist = spec/lab-evidence/e2e50-p2/REPORT.md section 5 (proposals, never an authorisation).
<!-- guard:end checkpoint -->
