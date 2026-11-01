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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C336' spec/CLAIMS.md` etc.;
     the E2E-49/P1 block starts at `grep -n '^## C333'` (~line 7610); the E2E-48 family is
     C309..C332, E2E-49/P1 is C333..C336. The ledger CURRENTLY ENDS at **C336** — no claim
     ids are owed. [C330] carries the labelled E2E-49/P1 CORRECTION append (positional
     length law); the falsified text is kept as written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p1/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P1 CLOSED (FULL compile-tier GATE rc=0 measured at `0a8ceff`, 2026-11-01)

- Gate ACTUALS as printed at `0a8ceff`: byte panel **1131 byte-exact / 0 fail of 1131**
  (E49A1..A4 all four BYTE-EXACT vs `golden/e49p1`), negative panel **181/181** refused
  (E46K14 prints `[dr-refuses]`, pinned marker `comparison of the internal CHARACTER
  member REC.LINE` UNMOVED), divergence panel **9/9**, coverage **122 rows, 0 errors,
  0 warnings**, census **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**, file prose
  **5 active files clean**. `dune build` rc=0 on this tree. Runtime/link-run tiers
  remain delegated to the external rune-ci builders (unchanged policy).
- Landing chain: pre-registration `9b3d860`, fill-in `0e9cc3d`, ONE oracle run 4 ok/4 —
  all ACCEPTS, no dr-refuses — goldens + RESULTS `c8285cb`, arm 1 `fee935e` (member-LEFT
  lowering, XCHG staging, positional lengths, `is_test_left` twin), arm 2 `b044b7c` (bare
  spelling `ImemFb`; admission deliberately ASYMMETRIC — bare member-RIGHT keeps refusing;
  the numeric ?IS22N guard widened to refuse exactly the admitted set), learnings `f95b872`,
  step 6 `0a8ceff` (claims C333..C336 from RESULTS §2 ONLY + labelled C330 correction +
  INVENTORY 4 rows via the sanctioned `--update-inventory`, census re-snapshot counts
  unchanged, COVERAGE 4 rows + SUPERSEDED note).
- Byte tier ONLY: NO `spec/RUNTIME.txt` row came or comes from this round (RESULTS §3).
- Working tree at this checkpoint: ONLY the operator's `handoff.config.json` edit plus the
  guard-written managed-block refresh; never stage, commit or revert the config edit.

## Next action — E2E-49/P1 is CLOSED; NO new scientific action is authorized until the OPERATOR names the next round

1. Candidate pool (each needs its OWN pre-registered round — hypotheses committed BEFORE
   any oracle run, PROTOCOL). From `spec/lab-evidence/e2e49-p1/RESULTS.md` §3: `?SCCCM` in
   a STORE (either orientation) and any fixed-member store value; member-vs-member
   compares; literal-vs-literal fixed compares; BASED members in conditions; truthiness
   of a FIXED member (bare or qualified — [C332] measured only the VARYING `BIT REQ`); a
   BARE fixed member on the RIGHT of a literal; over-extent in the LITERAL-LEFT
   orientation and over-extent INITIAL/STORE; `^( ... )` composition. Still open from
   `spec/lab-evidence/e2e48-p2e/RESULTS.md` §3: `^=` over a ladder, bare `-0` spelling,
   runtime length rewrite, empty-varying PUT output, `BIT REQ` acceptance elsewhere, PUT
   EDIT of a bit item. Separate recorded debts, NOT arms: CREATE's `%include` front-end
   gap and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71
   cols CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no
   push; never stage/commit/revert the operator's `handoff.config.json` edit; renewal
   values live ONLY in `handoff.config.json` / `/guard status`.

## Unfinished operations

- None — the E2E-49/P1 round is CLOSED (FULL GATE rc=0 measured at `0a8ceff`).

## Discoveries not yet incorporated

- None outstanding. Compiler law: `spec/CLAIMS.md` C309..C336 (E2E-48 family C309..C332,
  E2E-49/P1 C333..C336, each round derived from its own RESULTS §2 ONLY); durable method
  lessons are classified in `LEARNINGS.md`. The stale `README.md` rolling status remains
  recorded as deferred work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 70
checkpoint-id: g70-5b5572a0b3e4
checkpoint-kind: auto
content-delta: none
readiness: attested
status: checkpoint (guard level 4, remaining ~4861, session 01a1946d-2fad-704c-9bbd-42078c146c52)
checkpointed: 2026-11-01T00:29:16.794Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: e3ac18edcda488086e872e2d1e32f02a692bdb97d870491b5893183fdf817555
source-handoff: 057939ec81da0ae1da3eaf6d2c22ef64e48bc819fa6279e8eb18c2e20a98d847
source-learnings: 056b49d7ef6c4074962b795266d7bb772715b2033b4f19c0610b1be04c0b0567
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a1946d-2fad-704c-9bbd-42078c146c52
readiness-at: 2026-11-01T00:29:25.070Z
readiness-checkpoint: g70-5b5572a0b3e4
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P1 is CLOSED; NO new scientific action is authorized until the OPERATOR names the next round

1. Candidate pool (each needs its OWN pre-registered round — hypotheses committed BEFORE
   any oracle run, PROTOCOL). From `spec/lab-evidence/e2e49-p1/RESULTS.md` §3: `?SCCCM` in
   a STORE (either orientation) and any fixed-member store value; member-vs-member
   compares; literal-vs-literal fixed compares; BASED members in conditions; truthiness
   of a FIXED member (bare or qualified — [C332] measured only the VARYING `BIT REQ`); a
   BARE fixed member on the RIGHT of a literal; over-extent in the LITERAL-LEFT
   orientation and over-extent INITIAL/STORE; `^( ... )` composition. Still open from
   `spec/lab-evidence/e2e48-p2e/RESULTS.md` §3: `^=` over a ladder, bare `-0` spelling,
   runtime length rewrite, empty-varying PUT output, `BIT REQ` acceptance elsewhere, PUT
   EDIT of a bit item. Separate recorded debts, NOT arms: CREATE's `%include` front-end
   gap and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71
   cols CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no
   push; never stage/commit/revert the operator's `handoff.config.json` edit; renewal
   values live ONLY in `handoff.config.json` / `/guard status`.

### Guard notes
E2E-49/P1 arms 1+2 landed (fee935e, b044b7c); HEAD f0d592b. Durable state is current: HANDOFF Next-action and PROGRESS Current phase carry measured ACTUALS (E49A1..A4 all four whole-file byte-exact vs golden/e49p1; E48 sweep 52/52; registered panel 1127/1127 byte-exact; out-of-scope refusals rc=2 re-measured; E46K14 marker unmoved; dune rc=0; FULL gate OWED, never claimed). Exact next action = STEP 6: claims C333..C336 from spec/lab-evidence/e2e49-p1/RESULTS.md s2 ONLY + labelled positional-law correction APPENDED at C330 keeping falsified text (PROTOCOL #2); INVENTORY 4 specimen rows after E48E8; census re-snapshot python3 tools/corpus_census.py; COVERAGE.tsv 4 rows (schema spec/COVERAGE-SCHEMA.md); commit; then FULL gate python3 tools/e2e_gate.py (expect 1131 byte-exact, neg 181/181, div 9/9, coverage 122 rows 0 errors) and record ACTUALS; then CLOSE (prose rewrite, archive superseded prose verbatim from committed blobs to docs/history/2026-11-01-e49p1-closed.md + README index, LEARNINGS close notes, update HANDOFF ledger-end pointer past C332, /handoff finalize, stop or await operator). Keep refusing: STORE, member-vs-member, literal-vs-literal, BASED, truthiness, bare member-RIGHT, over-extent literal-LEFT, ^( ); no RUNTIME row; no push; never touch the operator handoff.config.json edit.
<!-- guard:end checkpoint -->
