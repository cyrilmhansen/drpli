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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C332' spec/CLAIMS.md` etc.; the
     E2E-48/P2e block starts at `grep -n '^## C327'` (~line 7478); the whole E2E-48 family is
     C309..C332. The ledger CURRENTLY ENDS at **C332** — no claim ids are owed.
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Current round evidence: `spec/lab-evidence/e2e48-p2e/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P2e CLOSED (FULL GATE measured in-session at `0749fa6`, 2026-10-31)

- The round's ONE remaining debt — the FULL compile-tier gate `python3 tools/e2e_gate.py` — was
  run to completion **this session** at HEAD `0749fa6` (tree = step-6 commits `809af8d`+`0e64c8b`
  plus documentation commits; `dune build` rc=0 beforehand): **rc=0**. ACTUALS, as printed by the
  run: byte panel **1127 byte-exact / 0 fail of 1127** — the seven P2e byte-tier specimens
  `E48E1`..`E48E5`,`E48E7`,`E48E8` are all `BYTE-EXACT` whole-file rows inside the panel —
  negative panel **181/181** refused (E46K14's row prints `[dr-refuses]`, pinned marker
  `comparison of the internal CHARACTER member REC.LINE` unmoved), divergence panel **9/9**,
  coverage **118 rows, 0 errors, 0 warnings**, census **EXACT 15 / DIFFERS 0 / REFUSED 26 /
  UNEXPECTED 0**, file prose **5 active files clean**. NOT re-measured this session (recorded,
  not assumed): the clean scratch-tree rebuild warning multiset (last measured 126 =
  28/26/22/17/15/14/2/2 at `c215ea0`).
- Science authority: claims **C327..C332** (`spec/CLAIMS.md`) derived ONLY from
  `spec/lab-evidence/e2e48-p2e/RESULTS.md` §2; §3 lists what stays unmeasured and those shapes
  stay NOT implemented. E48E6 is a measured `dr-refuses` (`BIT REQ`, no `.REL`), is NOT a
  specimen, and E46K14 keeps its refusal row. Goldens were not touched this round.
- Landing chain: pre-registration `421656a`, oracle run + goldens `e2b77ba`, arms 1–5
  `d18c6ab`/`bab0d16`/`e49902a`/`046046a`/`c215ea0`, step 6 `809af8d`+`0e64c8b`, handoff docs
  `0749fa6`. Superseded closing-era prose (old Last-verified-state, FULL-GATE next action,
  step-6 record, prior-arms prose, verified-evidence, stale debts bullet) archived verbatim in
  `docs/history/2026-10-31-p2e-closed.md`.

## Next action — E2E-48/P2e CLOSED; awaiting the OPERATOR's next-round choice (no compiler work is authorized meanwhile)

1. **No new scientific action is authorized in this repository until the operator names the
   next round.** Candidate pool (all from `spec/lab-evidence/e2e48-p2e/RESULTS.md` §3, each
   needing its OWN pre-registered round — hypotheses committed BEFORE any oracle run,
   PROTOCOL): member-vs-member compares; `?SCCCM` in a STORE or with the member on the LEFT;
   literal-vs-literal fixed compares; BASED members in conditions; over-extent INITIAL/store;
   `BIT REQ` acceptance elsewhere (bare scalar `char`, `^`, `&`); PUT EDIT of a bit item;
   `^(k = -c)` composition. Separate recorded debts, NOT arms: CREATE's `%include` front-end
   gap and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched; §3 shapes NOT implemented (missing evidence is the limit,
   never a licence to guess); no push; never stage/commit/revert the operator's
   `handoff.config.json` edit; renewal values live ONLY in `handoff.config.json` /
   `/guard status`.

## Unfinished operations

- None — the E2E-48/P2e round is CLOSED (FULL GATE rc=0 measured at `0749fa6`). The working
  tree at this checkpoint carries ONLY the operator's `handoff.config.json` edit plus the
  guard-written managed-block refresh; never stage, commit or revert the config edit.

## Discoveries not yet incorporated

- None outstanding. Compiler law: `spec/CLAIMS.md` C309..C332 (E2E-48 family, derived per
  round from that round's RESULTS §2 ONLY); durable method lessons are classified in
  `LEARNINGS.md`. The stale `README.md` rolling status remains recorded as deferred work in
  `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status log:
  `docs/history/README.md` (index; baseline extraction at `f3a4c60`, P2e closing-era prose
  added at the round close 2026-10-31: `docs/history/2026-10-31-p2e-closed.md`).
- Renewal: the E2E-48 phase chain closed at its configured cap; state archived under
  `.pi-guard/archives/`. Effective renewal values are in `handoff.config.json` (authoritative) —
  never this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 64
checkpoint-id: g64-994f3db1f7d5
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~72837, session 01a192a7-7efe-70b4-8abc-b0f23bdb2a52)
checkpointed: 2026-10-31T16:01:33.021Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 18467d0bdb9ea66368fd82c861782fc504ccf21166379366b61f8e7ef958050b
source-handoff: 1760ab27164392c6824c97240319731d41b99f26a4cacede995e7b7e26b20933
source-learnings: 56c54d2d71aa3b6d71ae3be0c85ca917b1c4b178c7fe8b78832d892ec0e06bf1
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a192a7-7efe-70b4-8abc-b0f23bdb2a52
readiness-at: 2026-10-31T16:01:33.024Z
readiness-checkpoint: g64-994f3db1f7d5
### Last verified state
guard level 0; checkpoint requested (finalize: E2E-48/P2e round CLOSED and verified this session: FULL compile-tier GATE python3 tools/e2e_gate.py rc=0 at HEAD 0749fa6 with ACTUAL 1127 byte-exact / 0 fail of 1127 (seven E48E byte-tier specimens in panel), negative 181/181 (E46K14 [dr-refuses], marker unmoved), divergence 9/9, coverage 118 rows 0 errors, census 15/0/26/0, prose clean; dune build rc=0. Closing prose committed at 5417de0 (HANDOFF/PROGRESS rewritten, docs/history/2026-10-31-p2e-closed.md archive, LEARNINGS close notes, ledger pointer now C332, no ids owed). NOT re-measured (recorded): clean-rebuild warning multiset (last 126 at c215ea0). Next action: await the OPERATOR's next-round choice; successor without instruction records state and stops. Goldens untouched; RESULTS s3 shapes not implemented; tree carries only the operator handoff.config.json edit after this refresh — never stage/commit/revert it; no push.)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48/P2e CLOSED; awaiting the OPERATOR's next-round choice (no compiler work is authorized meanwhile)

1. **No new scientific action is authorized in this repository until the operator names the
   next round.** Candidate pool (all from `spec/lab-evidence/e2e48-p2e/RESULTS.md` §3, each
   needing its OWN pre-registered round — hypotheses committed BEFORE any oracle run,
   PROTOCOL): member-vs-member compares; `?SCCCM` in a STORE or with the member on the LEFT;
   literal-vs-literal fixed compares; BASED members in conditions; over-extent INITIAL/store;
   `BIT REQ` acceptance elsewhere (bare scalar `char`, `^`, `&`); PUT EDIT of a bit item;
   `^(k = -c)` composition. Separate recorded debts, NOT arms: CREATE's `%include` front-end
   gap and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched; §3 shapes NOT implemented (missing evidence is the limit,
   never a licence to guess); no push; never stage/commit/revert the operator's
   `handoff.config.json` edit; renewal values live ONLY in `handoff.config.json` /
   `/guard status`.

### Guard notes
E2E-48/P2e round CLOSED and verified this session: FULL compile-tier GATE python3 tools/e2e_gate.py rc=0 at HEAD 0749fa6 with ACTUAL 1127 byte-exact / 0 fail of 1127 (seven E48E byte-tier specimens in panel), negative 181/181 (E46K14 [dr-refuses], marker unmoved), divergence 9/9, coverage 118 rows 0 errors, census 15/0/26/0, prose clean; dune build rc=0. Closing prose committed at 5417de0 (HANDOFF/PROGRESS rewritten, docs/history/2026-10-31-p2e-closed.md archive, LEARNINGS close notes, ledger pointer now C332, no ids owed). NOT re-measured (recorded): clean-rebuild warning multiset (last 126 at c215ea0). Next action: await the OPERATOR's next-round choice; successor without instruction records state and stops. Goldens untouched; RESULTS s3 shapes not implemented; tree carries only the operator handoff.config.json edit after this refresh — never stage/commit/revert it; no push.
<!-- guard:end checkpoint -->
