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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C347' spec/CLAIMS.md` etc.;
     the E2E-49/P3 block starts at `grep -n '^## C342'`; the E2E-48 family is C309..C332,
     E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341, E2E-49/P3 is C342..C347. The ledger
     CURRENTLY ENDS at **C347** — no claim ids are owed. [C330] carries the labelled
     E2E-49/P1 CORRECTION append (positional length law); [C335]–[C338] carry labelled P3
     CORRECTION appends and [C346] a labelled CITATION CORRECTION (the numeric ORDER law is
     [C104], never cite legacy [C027]/[C072] in provenance); falsified text is kept as
     written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p3/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/`, `e2e49-p1/` and
     `e2e49-p2/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P3 CLOSED (FULL compile-tier gate rc=0 measured by the step-6 session at HEAD `4df35bb`, recorded `1f611f5`; CLOSE prose + byte-verified two-generation archive completed by the docs-only closing session — ledger ENDS at C347, byte panel 1150, coverage 129 rows)

- Landing chain: pre-registration `3659f5d` (14 probes E49C1..C4/D1..D4/E1..E2/F1..F4 +
  mkprobes.py + HYPOTHESES + BASELINE-MINE at `685741c`) committed BEFORE any oracle call;
  fill-in `0a46824`; ONE grouped batch run, tag `e49p3`, **14 ok / 14, NO dr-refuses**
  (12 `my-gap`; E49E1/E2 already byte-exact, NO arm); goldens + RESULTS `ad90425`; arms a
  `a540fa7` / b `0a1b80c` / c `cde3258` (each ALONE, 14/14 goldens whole-file BYTE-EXACT,
  gate rc=0 at each); step 6 part 1 `4b51bc0` (claims C342..C347 from RESULTS §2 ONLY,
  labelled CORRECTION appends with originals verbatim at [C335]/[C336]/[C337]/[C338],
  SPECIMENS bank +14, sanctioned `--update-inventory` 14 rows — panel **1150** — census
  re-snapshot counts UNCHANGED); part 2a `8d3b024` (four COVERAGE rows, 129/0/0); part 2b
  `8771e1e` (`COND.CMP_LENGTHS_POSITIONAL` widened to EXACT:10 + five labelled SUPERSEDED
  clauses); part 2c `4df35bb` (labelled CITATION CORRECTION at [C346]); gate record
  `1f611f5`; close-partial `b07be23`; guard refresh `c140277`. Working tree at this
  boundary: ONLY the operator's `handoff.config.json` edit, the guard's managed blocks and
  this prose.
- FULL compile-tier gate ACTUALS AS PRINTED at `4df35bb` (rc=0): byte panel **1150
  byte-exact / 0 fail of 1150** (all fourteen e49p3 specimens print `BYTE-EXACT ... (256
  bytes)`); negative panel **181/181 refused**, E46K14 prints `refused [TBD] (comparison
  of the internal CHARACTER member REC.LINE) [dr-refuses]` — pinned marker UNMOVED;
  divergence panel **9/9**; coverage `coverage_check: 129 rows, 0 errors, 0 warnings`;
  census counts UNCHANGED **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**; file prose
  **5 active files clean**. `dune build` rc=0. Runtime/link-run tiers remain delegated to
  the external rune-ci builders (unchanged policy). BYTE TIER ONLY: no `spec/RUNTIME.txt`
  row came or comes from this round.
- Science landed: [C342] the equal-attribute collapse `06 n / 78` is a `?SCCCM`
  LENGTH-PAIR law measured in BOTH literal templates (settles [C338]'s [TBD]; COUNT NOTE:
  RESULTS §2.1 says "six", names seven — recorded in the claim, evidence untouched);
  [C343] `CA` is the `^=` skip on the DIRECT template too and the fill is the next
  statement ([C309]) in all fourteen; [C344] qualification of an internal FIXED member is
  INVISIBLE to every measured compare encoding — bare sides admitted (falsifies the
  [C335]/[C337] bare-side refusals); [C345] over-extent literal written LEFT accepted and
  pooled whole, NO ARM ([C336] transfers by measurement); [C346] ordered relations take
  the same `?SCCCM` helper and stacked parking, ORDER law (`<`/`>=` written, `>`/`<=`
  swapped — the [C104] numeric rule for characters) and BRANCH law (strict JNC `d2`, weak
  JC `da`), lengths positional on the LOWERED operands; [C347] head size follows the
  length pair in every template, DATA stays [C314]'s pool-first frame.
- Superseded prose — the P2 closing-era Last-verified-state, BOTH generations of the P3
  in-flight/close-owed HANDOFF next actions and PROGRESS current phases, the surviving P2
  CLOSED previous-phase record (frozen wording; an identical copy still lives in
  `PROGRESS.md` until the next close), the stale P2-era next-action stub, the P2-frozen
  Verified evidence and the P2-era Blockers wording — archived verbatim, every block
  byte-verified against its stated git range, in
  `docs/history/2026-11-01-e49p3-closed.md`. Goldens untouched except this round's
  `golden/e49p3`.

## Next action — E2E-49/P4 ACTIVE (OPERATOR-AUTHORIZED 2026-11-01): composite CHARACTER FIXED / TEST campaign, four panels, 24 specimens

1. READ `spec/lab-evidence/e2e49-p4/PLAN.md` FIRST — it is the durable, complete
   plan: bank E49G1..G8 (ordered relations with a LITERAL, both orientations),
   E49H1..H6 (BARE spellings in ordered relations), E49I1..I6 (unequal-extent
   relation matrix), E49J1..J4 (negated compares); shared P3 DECL+tail; hypotheses
   (H-A-sw/H-A-or/H-A-refuse; H-B-invis vs gate/mixed; C = arm-c transfer;
   H-D-inv/H-D-simpl/H-D-extra/H-D-refuse); the exact oracle command (tag `e49p4`,
   never `--reuse`); step-6 method (claims from C348, SPECIMENS +24,
   `--update-inventory`, census, COVERAGE, FULL gate ACTUALS); close procedure.
   Authorization covers measurement→arms→consolidation→closure across renewals;
   NOT P5, NOT push, NOT STORE/BASED/truthiness/literal-vs-literal/runtime.
2. NEXT CONCRETE STEP (nothing of P4 measured yet): PREREGISTER — clone P3
   mkprobes.py into e2e49-p4/, generate probes (CRLF+^Z, <=71 cols), record
   BASELINE-MINE.txt with the ACTUAL binary (expected from CODE READING, unverified:
   A/B/D refuse rc=2, C accepts on arm-c bytes), write HYPOTHESES.md, COMMIT ALL
   BEFORE any oracle call. Then ONE grouped `oracle/batch.py ... --tag e49p4`.
3. Standing: byte tier only; goldens untouched except new `golden/e49p4`; never
   touch the operator's `handoff.config.json` edit; renewal values ONLY in
   handoff.config.json / /guard status; `eval $(opam env)` before dune; never
   git clean/reset/add -A; NO PUSH.

## Unfinished operations

- (none) — E2E-49/P3 is CLOSED: arms a/b/c (`a540fa7`/`0a1b80c`/`cde3258`), claims
  C342..C347, registration (panel 1150), COVERAGE (129 rows, 0 errors, 0 warnings), the
  FULL compile-tier gate (rc=0 measured at `4df35bb`, recorded `1f611f5`) and the CLOSE
  (two-generation archive `docs/history/2026-11-01-e49p3-closed.md` byte-verified
  block-by-block, HANDOFF/PROGRESS/LEARNINGS rewritten, `docs/history/README.md` index
  updated) all landed. Standing debts live in `PROGRESS.md` → Pending; the candidate pool
  lives in the Next action above.

## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P3 discovery is incorporated: laws C342..C347 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p3/RESULTS.md` §2), the
  four new COVERAGE rows, the widening and the five labelled SUPERSEDED clauses in
  `spec/COVERAGE.tsv` (129 rows, 0 errors, 0 warnings). Open PROPOSALS (classified
  `proposed` in `LEARNINGS.md`, NOT law): bank the out-of-scope member-pair refusals as
  NEG-panel rows; "emit the head as ONE bundled thunk in written order" stays a codegen
  invariant evidenced per-shape — no ledger claim until discriminating probes exist. The
  stale `README.md` rolling status remains recorded as deferred work in `PROGRESS.md` →
  Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`;
  E2E-49/P3 two-generation close archive — in-flight prose at `4df35bb` AND the
  close-owed prose at `c140277` — `docs/history/2026-11-01-e49p3-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 89
checkpoint-id: g89-db496a27f9de
checkpoint-kind: auto
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~3265, session 01a196da-fa99-71b9-af89-536a51a8a317)
checkpointed: 2026-11-01T11:45:18.453Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: b1cc7ad6f855f16883e9d664b3fea2cd132d47634c2e1c705dfec1bc4c29d882
source-handoff: 49deaffc4e0066970c808f72a91fc61fce06499d28ca1cec5464b832f0f4b7a1
source-learnings: c540e3bf96d4d628dccde2eb21f321005398993b4f11dc7f3a0fc4618c0700a8
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a196da-fa99-71b9-af89-536a51a8a317
readiness-at: 2026-11-01T11:45:31.805Z
readiness-checkpoint: g89-db496a27f9de
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P4 ACTIVE (OPERATOR-AUTHORIZED 2026-11-01): composite CHARACTER FIXED / TEST campaign, four panels, 24 specimens

1. READ `spec/lab-evidence/e2e49-p4/PLAN.md` FIRST — it is the durable, complete
   plan: bank E49G1..G8 (ordered relations with a LITERAL, both orientations),
   E49H1..H6 (BARE spellings in ordered relations), E49I1..I6 (unequal-extent
   relation matrix), E49J1..J4 (negated compares); shared P3 DECL+tail; hypotheses
   (H-A-sw/H-A-or/H-A-refuse; H-B-invis vs gate/mixed; C = arm-c transfer;
   H-D-inv/H-D-simpl/H-D-extra/H-D-refuse); the exact oracle command (tag `e49p4`,
   never `--reuse`); step-6 method (claims from C348, SPECIMENS +24,
   `--update-inventory`, census, COVERAGE, FULL gate ACTUALS); close procedure.
   Authorization covers measurement→arms→consolidation→closure across renewals;
   NOT P5, NOT push, NOT STORE/BASED/truthiness/literal-vs-literal/runtime.
2. NEXT CONCRETE STEP (nothing of P4 measured yet): PREREGISTER — clone P3
   mkprobes.py into e2e49-p4/, generate probes (CRLF+^Z, <=71 cols), record
   BASELINE-MINE.txt with the ACTUAL binary (expected from CODE READING, unverified:
   A/B/D refuse rc=2, C accepts on arm-c bytes), write HYPOTHESES.md, COMMIT ALL
   BEFORE any oracle call. Then ONE grouped `oracle/batch.py ... --tag e49p4`.
3. Standing: byte tier only; goldens untouched except new `golden/e49p4`; never
   touch the operator's `handoff.config.json` edit; renewal values ONLY in
   handoff.config.json / /guard status; `eval $(opam env)` before dune; never
   git clean/reset/add -A; NO PUSH.

### Guard notes
E2E-49/P3 CLOSE COMPLETE (docs-only session): two-generation archive docs/history/2026-11-01-e49p3-closed.md byte-verified (11/11 blocks byte-exact vs git ranges at 4df35bb/c140277), draft blank-line join artifact repaired, README index row added (commit 739cd10); HANDOFF/PROGRESS rewritten to the CLOSED record (ledger C347, panel 1150/0, coverage 129/0/0, gate rc=0 measured by the step-6 session at 4df35bb recorded 1f611f5; Next action = AWAIT OPERATOR, no active round; Blockers updated per RESULTS s3, superseded wording verbatim in archive); LEARNINGS dated close notes (commit 1ff755e). No compiler/oracle/gate run; no ocaml/golden/claim/COVERAGE/config byte touched; operator handoff.config.json edit preserved unstaged; no push. Session stops here per mission.
<!-- guard:end checkpoint -->
