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

## Last verified state — E2E-49/P1 IN FLIGHT (arms 1+2 landed: `fee935e`, `b044b7c`; FULL GATE not yet run this round; prior P2e record follows, superseded)

- Arm 2 measured at `b044b7c` (this session, after `dune build` rc=0): E49A1..E49A4 ALL
  whole-file BYTE-EXACT vs `golden/e49p1` (E49A2 flipped from rc=2 to exact — the arm's
  object); E48-family sweep **52/52** 0 DIFF (e48p1+e48p2c+e48p2db+e48p2retire+e48p2e,
  incl. E48E7 literal-left regression); the **full registered specimen panel 1127/1127
  BYTE-EXACT, 0 fail** (every `spec/INVENTORY.txt` specimen row re-compiled and whole-file
  `cmp`'d — direct proof no output moved elsewhere); out-of-scope refusals re-measured
  through the binary (bare member-RIGHT, fixed truthiness bare+qualified, fixed STORE
  target, member-vs-member, literal-vs-literal, flag-trick over a bare fixed member) all
  rc=2 named refusals; E46K14 marker `comparison of the internal CHARACTER member
  REC.LINE` UNMOVED. FULL gate NOT run — owed at step 6, never claimed.
- The prior round's FULL-gate record (HEAD `0749fa6`, rc=0): byte panel **1127 byte-exact /
  0 fail of 1127**, negative panel **181/181** refused (E46K14's row prints `[dr-refuses]`,
  pinned marker unmoved), divergence panel **9/9**, coverage **118 rows, 0 errors, 0
  warnings**, census **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**, file prose **5
  active files clean**. NOT re-measured this session (recorded, not assumed): the clean
  scratch-tree rebuild warning multiset (last measured 126 = 28/26/22/17/15/14/2/2 at
  `c215ea0`).
- Science authority: this round's claims are NOT YET in the ledger — step 6 derives
  **C333..C336** from `spec/lab-evidence/e2e49-p1/RESULTS.md` §2 ONLY plus the labelled
  positional-law correction APPENDED at C330 (keep the falsified text, PROTOCOL #2).
  E48 family remains C309..C332; the ledger CURRENTLY ENDS at **C332**. Goldens were not
  touched except the NEW `golden/e49p1`.
- Landing chain: pre-registration `9b3d860`, fill-in `0e9cc3d`, oracle run + goldens +
  RESULTS `c8285cb`, arm 1 `fee935e`, arm 2 `b044b7c`. Superseded closing-era prose
  (old Last-verified-state, FULL-GATE next action, step-6 record, prior-arms prose,
  verified-evidence, stale debts bullet) archived verbatim in
  `docs/history/2026-10-31-p2e-closed.md`.

## Next action — E2E-49/P1: STEP 6 (ledger + registration) then FULL GATE, then CLOSE (prior P2e "await operator" text below is SUPERSEDED by the operator's 2026-10-31 authorization of this round)

**ACTIVE PLAN (exact, also in PROGRESS.md → Current phase):** lineage = prediction SHA
`9b3d860`, fill-in `0e9cc3d`, oracle run + goldens + `spec/lab-evidence/e2e49-p1/RESULTS.md`
(4 ok / 4, all ACCEPTS, no dr-refuses) at `c8285cb`, arm 1 (qualified member-LEFT lowering,
XCHG staging, positional lengths, `is_test_left` twin) at `fee935e`, arm 2 (BARE fixed
spelling member-LEFT as new `str_side` variant `ImemFb`; `str_cmp_shape_fix` member-left arm
= or-pattern `ImemF`/`ImemFb`, literal-RIGHT arm keeps `ImemF` alone; `is_test_left` widened
in the SAME commit; numeric ?IS22N ident-vs-ident guard now refuses bare-fixed pairs it used
to mis-lower) at `b044b7c` — ACTUALS at `b044b7c`: dune rc=0; E49A1..A4 ALL four whole-file
BYTE-EXACT; E48 sweep 52/52; registered panel 1127/1127 BYTE-EXACT 0 fail; out-of-scope
refusals re-measured rc=2 (bare member-RIGHT, fixed truthiness bare+qualified, STORE,
member-vs-member, literal-vs-literal, flag-trick); E46K14 marker UNMOVED. Measured laws
(RESULTS s2): inverted fixed TEST = `21 *D(member) / EB / 21 *D(pool) / 06 extent / 3E len /
CD ?SCCCM / skip`; length immediates POSITIONAL (B = LEFT, A = RIGHT) — falsifies [C330]'s
class-polarity reading; name does not flip; ^= CA measured; bare spelling byte-identical but
module-name bytes; over-extent literal accepted, pooled whole. **(1) STEP 6:** claims
**C333..C336** derived ONLY from RESULTS §2 (predecessor mapping: C333 = s2.1 incl. s2.3
no-name-flip and s2.5 CA skip; C334 = s2.2 positional law; C335 = s2.4 spelling invariance
+ bare-RIGHT gate asymmetry; C336 = s2.6 over-extent ACCEPT member-left; regroup ONLY if the
evidence demands it — ids contiguous from C333, ledger ends at the last one) + the labelled
correction APPENDED at **C330** (keep falsified text verbatim, PROTOCOL #2); **INVENTORY**
4 specimen rows E49A1..A4 after the E48E8 row (or `python3 tools/e2e_gate.py
--update-inventory`, the sanctioned tool, then inspect the diff precisely); census
re-snapshot `python3 tools/corpus_census.py` + record counts (expect EXACT 15 / DIFFERS 0 /
REFUSED 26 / UNEXPECTED 0; the 1127-row sweep already proves no specimen moved);
**COVERAGE.tsv** 4 rows (schema `spec/COVERAGE-SCHEMA.md`, validator rules
`tools/coverage_check.py:203-247`; expect 122 rows 0 errors); commit ledger work. **(2)
FULL GATE** `python3 tools/e2e_gate.py` (expect **1131** byte-exact / 0 fail; negative
181/181 E46K14 marker unmoved; div 9/9; coverage 0 errors; census check; prose panel) —
record ACTUALS as printed, never claim unverified. **(3) CLOSE:** rewrite HANDOFF + PROGRESS
with real ACTUALS, archive superseded prose VERBATIM from committed blobs (not the dirty
managed blocks) to `docs/history/2026-11-01-e49p1-closed.md` + README index row, LEARNINGS
close notes, commit, `/handoff finalize`, renew or stop. OUT OF SCOPE, keep refusing
(RESULTS s3): STORE fixed member both orientations, member-vs-member, literal-vs-literal,
BASED, fixed truthiness, bare member-RIGHT, over-extent literal-LEFT ([TBD]), `^( )`; NO
`spec/RUNTIME.txt` row from this round; no push; never stage/commit/revert the operator's
`handoff.config.json` edit.

### Superseded (E2E-48/P2e close, kept as written)

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
checkpoint-generation: 66
checkpoint-id: g66-487495b2e408
checkpoint-kind: auto
content-delta: none
readiness: attested
status: checkpoint (guard level 4, remaining ~4033, session 01a19445-2627-704c-9bbd-41fe19a81649)
checkpointed: 2026-10-31T23:50:55.048Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 709b60b7ffcd2d9e69d68ba96f186e8a641ca3ce03c7d927f97a2dddd779f239
source-handoff: 9c6ac47b842acfdb3d1d95c8dfa31a2856e987c124eb629d0a831e4d02422391
source-learnings: aaf0cbe5e1ea2596649b58d021372e099e910814f17b9b61a393b266168864c0
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19445-2627-704c-9bbd-41fe19a81649
readiness-at: 2026-10-31T23:51:20.848Z
readiness-checkpoint: g66-487495b2e408
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P1: arm 2 (bare spelling) then step 6 (ledger) + FULL GATE (prior P2e "await operator" text below is SUPERSEDED by the operator's 2026-10-31 authorization of this round)

**ACTIVE PLAN (exact, also in PROGRESS.md → Current phase):** lineage = prediction SHA
`9b3d860`, fill-in `0e9cc3d`, oracle run + goldens + `spec/lab-evidence/e2e49-p1/RESULTS.md`
(4 ok / 4, all ACCEPTS, no dr-refuses) at `c8285cb`, arm 1 lowering at `fee935e` with
ACTUALS E49A1/A3/A4 whole-file BYTE-EXACT, E49A2 still refuses (arm 2's object), E48E7
regression exact, E48 sweep 43/43, dune rc=0. Measured laws (RESULTS s2): inverted fixed
TEST = `21 *D(member) / EB / 21 *D(pool) / 06 extent / 3E len / CD ?SCCCM / skip`; length
immediates POSITIONAL (B = LEFT, A = RIGHT) — falsifies [C330]'s capacity-in-A reading
(append labelled correction at C330, keep text); name does not flip; ^= CA measured;
over-extent literal accepted, pooled whole. (1) ARM 2: `str_side` Eident admits BARE fixed
as new `ImemFb (orig,cap)`; `str_cmp_shape_fix` member-LEFT arm matches `ImemF`/`ImemFb`,
literal-RIGHT arm keeps `ImemF` only (bare member-RIGHT unmeasured); widen `is_test_left`
in the SAME commit; annotate superseded bare sentences; build, E49A2 whole-file cmp, no
output moves elsewhere, commit codegen.ml with ACTUALS. (2) STEP 6: claims C333..C336 from
RESULTS s2 ONLY + C330 correction; INVENTORY 4 specimen rows after E48E8; census
re-snapshot; 4 COVERAGE.tsv rows; commit; then FULL gate `python3 tools/e2e_gate.py`
(expect 1131 byte-exact; negative 181/181 E46K14 marker unmoved; div 9/9; coverage 0
errors) and record ACTUALS. (3) CLOSE: rewrite this + PROGRESS with real ACTUALS, archive
superseded prose to docs/history/, commit, /handoff finalize, renew or stop. OUT OF SCOPE,
keep refusing (e2e49-p1 RESULTS s3): STORE fixed member, member-vs-member,
literal-vs-literal, BASED, fixed truthiness, bare member-RIGHT, over-extent literal-LEFT
([TBD]), `^( )`; NO RUNTIME row; no push; never touch the operator config edit.

### Guard notes
E2E-48/P2e round CLOSED and verified this session: FULL compile-tier GATE python3 tools/e2e_gate.py rc=0 at HEAD 0749fa6 with ACTUAL 1127 byte-exact / 0 fail of 1127 (seven E48E byte-tier specimens in panel), negative 181/181 (E46K14 [dr-refuses], marker unmoved), divergence 9/9, coverage 118 rows 0 errors, census 15/0/26/0, prose clean; dune build rc=0. Closing prose committed at 5417de0 (HANDOFF/PROGRESS rewritten, docs/history/2026-10-31-p2e-closed.md archive, LEARNINGS close notes, ledger pointer now C332, no ids owed). NOT re-measured (recorded): clean-rebuild warning multiset (last 126 at c215ea0). Next action: await the OPERATOR's next-round choice; successor without instruction records state and stops. Goldens untouched; RESULTS s3 shapes not implemented; tree carries only the operator handoff.config.json edit after this refresh — never stage/commit/revert it; no push.
<!-- guard:end checkpoint -->
