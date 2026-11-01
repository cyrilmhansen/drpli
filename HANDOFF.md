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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C341' spec/CLAIMS.md` etc.;
     the E2E-49/P2 block starts at `grep -n '^## C337'` (~line 7699); the E2E-48 family is
     C309..C332, E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341. The ledger CURRENTLY
     ENDS at **C341** — no claim ids are owed. [C330] carries the labelled E2E-49/P1
     CORRECTION append (positional length law); the falsified text is kept as written
     (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p2/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/` and `e2e49-p1/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P2 CLOSED (FULL compile-tier gate rc=0 measured by the closing session at HEAD `d5983e8`, recorded `8926b83`; CLOSE prose + archive in the commit that carries this text)

- Landing chain: pre-registration `3bd9417` (probes E49B1..B5 + HYPOTHESES + BASELINE-MINE
  at `7fa763b`: all five refused rc=2 — every gap `my-gap`) committed BEFORE any oracle
  call; fill-in `586c240`; ONE oracle run 5 ok / 5, NO dr-refuses; goldens + RESULTS
  `62f5622`; docs `1416f52`; ARM 1 (codegen only, landed ALONE) `b1e9221` — five `.REL`
  whole-file BYTE-EXACT, E48/E49 sweep 61/61, registered-panel sweep 1131/1131,
  out-of-scope refusals rc=2, E46K14 marker UNMOVED; step 6 part 1 `0abf1c1` (claims
  C337..C341 from RESULTS §2 ONLY, SPECIMENS bank, `--update-inventory` 5 rows — panel
  1136 — census re-snapshot counts UNCHANGED); part 2a `8c1d2ee` (3 new COVERAGE rows);
  part 2b `d5983e8` (`COND.CMP_LENGTHS_POSITIONAL` widened to EXACT:8 + three labelled
  SUPERSEDED clauses); gate-record commit `8926b83`. Working tree at this boundary: ONLY
  the operator's `handoff.config.json` edit, the guard's managed blocks and this prose.
- FULL compile-tier gate ACTUALS AS PRINTED at `d5983e8` (rc=0): byte panel **1136
  byte-exact / 0 fail of 1136** (E49B1..B5 each `BYTE-EXACT ... (256 bytes)`); negative
  panel **181/181 refused**, E46K14 prints `refused [TBD] (comparison of the internal
  CHARACTER member REC.LINE) [dr-refuses]` — pinned marker UNMOVED; divergence panel
  **9/9**; coverage `coverage_check: 125 rows, 0 errors, 0 warnings`; census counts
  UNCHANGED **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**; file prose **5 active
  files clean**. `dune build` rc=0. Runtime/link-run tiers remain delegated to the
  external rune-ci builders (unchanged policy). BYTE TIER ONLY: no `spec/RUNTIME.txt`
  row came or comes from this round.
- Science landed: [C337] member-vs-member TEST takes `?SCCCM` with BOTH cells PARKED ON
  THE STACK (`21 *D(left)/E5/21 *D(right)/D1`) — parking is a per-shape property, `EB` is
  measured only vs a pooled literal, both pre-registered forms falsified; [C338]
  equal-extent collapse `06 n / 78` MEASURED member-vs-member ONLY (scope warning in the
  claim and in the COVERAGE boundary: the literal template KEEPS two immediates, the
  equal-length literal case is [TBD]); [C339] positional length law on an all-member pair
  (MIN/MAX/class readings dead); [C340] the written side selects the `*D` relocation slot;
  [C341] head size follows the length pair and a member pair pools NO literal (DATA 000C,
  [C314]).
- Superseded prose — the P2 in-flight sections AND the surviving P1 closing-era sections
  (self-labelled "archive at P2 close"), the stale P1-era next-action stub, the
  P1-frozen Verified evidence and the P1-era Blockers wording — archived verbatim in
  `docs/history/2026-11-01-e49p2-closed.md`. Goldens untouched except this round's
  `golden/e49p2`.

## Next action — E2E-49/P2 CLOSED; await the OPERATOR's named round

1. Candidate pool (each item needs its OWN pre-registered round — hypotheses committed
   BEFORE any oracle call, PROTOCOL). From `spec/lab-evidence/e2e49-p2/RESULTS.md` §3:
   any BARE spelling in a member-vs-member pair (bare-bare, bare-qualified,
   qualified-bare); the equal-extent collapse for member-vs-LITERAL (`char(3)` against a
   3-char literal in TEST — one probe settles [C338]'s [TBD]); `?SCCCM` in a STORE
   (either orientation) and any fixed-member store value; literal-vs-literal fixed
   compares; BASED members in conditions; the truthiness of a FIXED member; over-extent
   member pairs; relations beyond `=`/`^=`; `^( ... )` composition. Still open from
   `spec/lab-evidence/e2e49-p1/RESULTS.md` §3 and `spec/lab-evidence/e2e48-p2e/RESULTS.md`
   §3: a BARE fixed member on the RIGHT of a literal (P1 asymmetry), over-extent
   literal-LEFT and over-extent INITIAL/STORE, `^=` over a ladder, bare `-0` spelling,
   runtime length rewrite, empty-varying PUT output, `BIT REQ` acceptance elsewhere, PUT
   EDIT of a bit item. The P1 §3 entry "member-vs-member" is MEASURED now ([C337]) and
   leaves the pool. Separate recorded debts, NOT arms: CREATE's `%include` front-end gap
   and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71 cols
   CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no push;
   never stage/commit/revert the operator's `handoff.config.json` edit; renewal values
   live ONLY in `handoff.config.json` / `/guard status`; NO `spec/RUNTIME.txt` row may
   come from the compare families until a runtime round measures them.

## Unfinished operations

- (none) — E2E-49/P2 is CLOSED: arms, claims C337..C341, registration (panel 1136),
  COVERAGE (125 rows, 0 errors) and the FULL compile-tier gate (rc=0 measured at
  `d5983e8`, recorded `8926b83`) all landed. Standing debts live in `PROGRESS.md` →
  Pending; the candidate pool lives in the Next action above.

## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P2 discovery is incorporated: laws C337..C341 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p2/RESULTS.md` §2), the
  COVERAGE rows and labelled SUPERSEDED clauses in `spec/COVERAGE.tsv` (125 rows, 0
  errors). Open PROPOSALS (classified `proposed` in `LEARNINGS.md`, NOT law): bank the
  out-of-scope member-vs-member refusals as NEG-panel rows; "emit the head as ONE bundled
  thunk in written order" stays a codegen invariant evidenced per-shape — no ledger claim
  until discriminating probes exist. The stale `README.md` rolling status remains recorded
  as deferred work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 78
checkpoint-id: g78-1b72c36b40c7
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 0, remaining ~30777, session 01a1950c-7ba6-7103-bf3c-ac92bd64aa79)
checkpointed: 2026-11-01T03:19:44.645Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 55e9941c4988b8d60c5c866dab55fa3335d6c311d06aa3e4ee996900e1011dc2
source-handoff: 54d12600052a2ad9901f0f1bde81c38461c5a1f124ee11b6fbc936f31f597374
source-learnings: 5667698bed5d92670a8ffd3369cde314f683693191ed573f515213571f5ba976
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a1950c-7ba6-7103-bf3c-ac92bd64aa79
readiness-at: 2026-11-01T03:19:44.648Z
readiness-checkpoint: g78-1b72c36b40c7
### Last verified state
guard level 0; checkpoint requested (finalize: E2E-49/P2 CLOSED at 29243e3 (step 6 part 2b d5983e8: COVERAGE widening EXACT:8 + 3 labelled SUPERSEDED clauses, coverage_check rc=0 125 rows 0 errors; FULL gate rc=0 MEASURED at d5983e8, recorded 8926b83: byte panel 1136/0 with E49B1..B5 byte-exact, negative 181/181 E46K14 marker UNMOVED, divergence 9/9, census 15/0/26/0, prose clean; close: archive docs/history/2026-11-01-e49p2-closed.md byte-verified from 8926b83 blobs + README row, HANDOFF/PROGRESS prose CLOSED-era rewrite, ledger-end pointer C341, LEARNINGS close notes). NEXT: await the OPERATOR's named round -- successor without an instruction confirms HEAD/tree, /handoff verify, records state, STOPS. Candidate pool in HANDOFF Next action (bare-spelling member pairs, char(3)-vs-3-char-literal collapse probe per [C338] TBD, STORE, literal-vs-literal, BASED, truthiness, over-extent, relations beyond =/^=, ^( ), P2e debts). Discipline: eval $(opam env) before dune; keep refusing every RESULTS s3 shape; NO spec/RUNTIME.txt row from the compare families; goldens untouched except e49p2; never touch the operator's handoff.config.json edit; no push.)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P2 CLOSED; await the OPERATOR's named round

1. Candidate pool (each item needs its OWN pre-registered round — hypotheses committed
   BEFORE any oracle call, PROTOCOL). From `spec/lab-evidence/e2e49-p2/RESULTS.md` §3:
   any BARE spelling in a member-vs-member pair (bare-bare, bare-qualified,
   qualified-bare); the equal-extent collapse for member-vs-LITERAL (`char(3)` against a
   3-char literal in TEST — one probe settles [C338]'s [TBD]); `?SCCCM` in a STORE
   (either orientation) and any fixed-member store value; literal-vs-literal fixed
   compares; BASED members in conditions; the truthiness of a FIXED member; over-extent
   member pairs; relations beyond `=`/`^=`; `^( ... )` composition. Still open from
   `spec/lab-evidence/e2e49-p1/RESULTS.md` §3 and `spec/lab-evidence/e2e48-p2e/RESULTS.md`
   §3: a BARE fixed member on the RIGHT of a literal (P1 asymmetry), over-extent
   literal-LEFT and over-extent INITIAL/STORE, `^=` over a ladder, bare `-0` spelling,
   runtime length rewrite, empty-varying PUT output, `BIT REQ` acceptance elsewhere, PUT
   EDIT of a bit item. The P1 §3 entry "member-vs-member" is MEASURED now ([C337]) and
   leaves the pool. Separate recorded debts, NOT arms: CREATE's `%include` front-end gap
   and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71 cols
   CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no push;
   never stage/commit/revert the operator's `handoff.config.json` edit; renewal values
   live ONLY in `handoff.config.json` / `/guard status`; NO `spec/RUNTIME.txt` row may
   come from the compare families until a runtime round measures them.

### Guard notes
E2E-49/P2 CLOSED at 29243e3 (step 6 part 2b d5983e8: COVERAGE widening EXACT:8 + 3 labelled SUPERSEDED clauses, coverage_check rc=0 125 rows 0 errors; FULL gate rc=0 MEASURED at d5983e8, recorded 8926b83: byte panel 1136/0 with E49B1..B5 byte-exact, negative 181/181 E46K14 marker UNMOVED, divergence 9/9, census 15/0/26/0, prose clean; close: archive docs/history/2026-11-01-e49p2-closed.md byte-verified from 8926b83 blobs + README row, HANDOFF/PROGRESS prose CLOSED-era rewrite, ledger-end pointer C341, LEARNINGS close notes). NEXT: await the OPERATOR's named round -- successor without an instruction confirms HEAD/tree, /handoff verify, records state, STOPS. Candidate pool in HANDOFF Next action (bare-spelling member pairs, char(3)-vs-3-char-literal collapse probe per [C338] TBD, STORE, literal-vs-literal, BASED, truthiness, over-extent, relations beyond =/^=, ^( ), P2e debts). Discipline: eval $(opam env) before dune; keep refusing every RESULTS s3 shape; NO spec/RUNTIME.txt row from the compare families; goldens untouched except e49p2; never touch the operator's handoff.config.json edit; no push.
<!-- guard:end checkpoint -->
