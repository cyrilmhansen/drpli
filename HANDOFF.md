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
6. **E2E-50/P2 (active).** Functional-testing foundation + emulator/redistribution audit. The
   external Runes lab `/home/john/pli/lab` (and `/home/john/pli/cpm`, `/home/john/pli/runes-full-runs`)
   is **READ-ONLY** this round: never commit, edit, clean, reformat or relocate anything there.
   Compiler/LINK/emulator runs occur ONLY as the P2 harness defines them (bounded, isolated,
   lane-labelled); never the oracle campaign, the full CP/M runtime tier or Rune CI builders.
   The P1 dashboard (`tools/functional_dashboard.py`) stays read-only over canonical evidence
   and regenerates only `docs/functional-status.md`.

## Last verified state — E2E-49/P4 CLOSED (FULL compile-tier gate rc=0 measured by the step-6 session at HEAD `5b0ccde`, recorded `882f77c`; CLOSE prose + byte-verified four-generation archive completed by the docs-only closing session — ledger ENDS at C351, byte panel 1174, coverage 133 rows)

- Landing chain: PLAN/bootstrap `bc6ee4f` under the OPERATOR authorization of 2026-11-01
  (panels A–D, oracle, arms, consolidation, closure; P5 and push NOT authorized);
  pre-registration `328eb3f` (24 probes E49G1..G8/H1..H6/I1..I6/J1..J4 + mkprobes.py +
  HYPOTHESES + BASELINE-MINE with the ACTUAL binary at `398fa2c` — panels A/B/D refused rc=2
  BY NAME, panel C accepted) committed BEFORE any oracle call; **P4 had NO separate fill-in
  commit** (unlike P3 `0a46824`); ONE grouped batch run, tag `e49p4`, **24 ok / 24, NO
  dr-refuses** (18 `my-gap`: G, H, J; 6 already byte-exact: I, whole-file `cmp` ZERO differing
  bytes, NO arm); goldens + RESULTS `13fca5b`, traceable wording repair `9799f1d`; arms a
  `c515377` / b `ec904c1` / c `47c2194` (each ALONE, whole-file goldens BYTE-EXACT, regression
  sweep 47/47 at arm c, out-of-scope refusals rc=2, FULL gate rc=0 at each with the panel at
  1150 — e49p4 not yet registered); step 6 part 1 `aec53e1` (claims C348..C351 from RESULTS §2
  ONLY) + part 1b `9c42f3b` (four labelled [E2E-49/P4 CORRECTION(S)] blocks at [C335]/[C337]/
  [C344]/[C346], falsified sentences verbatim) + docs `19ab4e0`/`e13311c`; registration
  `cc43963` (SPECIMENS +24, sanctioned `--update-inventory` panel 1150 → 1174, census
  re-snapshot counts UNCHANGED); part 2a `dbaf004` (four COVERAGE rows, 133/0/0); part 2b
  `5aeac87` (`COND.CMP_LENGTHS_POSITIONAL` EXTENDED to EXACT:14 + four labelled SUPERSEDED/
  WIDENED clauses, quotes byte-checked vs the pre-edit blob `cc43963`, ORDER law cited [C104],
  never legacy); part 2c `5b0ccde` (labelled WORDING CORRECTION at [C348]); gate record
  `882f77c`; attestation `cbdcbe2`; CLOSE authorization `5c52bba`. Working tree at this
  boundary: ONLY the operator's `handoff.config.json` edit, the guard's managed blocks and
  this prose.
- FULL compile-tier gate ACTUALS AS PRINTED at `5b0ccde` (rc=0): byte panel **1174 byte-exact /
  0 fail of 1174** (all twenty-four e49p4 specimens print `BYTE-EXACT ... (256 bytes)`
  whole-file); negative panel **181/181 refused**, E46K14 prints `refused [TBD] (comparison of
  the internal CHARACTER member REC.LINE) [dr-refuses]` — pinned marker UNMOVED; divergence
  panel **9/9**; coverage `coverage_check: 133 rows, 0 errors, 0 warnings`; census counts
  UNCHANGED **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**; file prose **5 active files
  clean**. `dune build` rc=0. Runtime/link-run tiers remain delegated to the external rune-ci
  builders (unchanged policy). BYTE TIER ONLY: no `spec/RUNTIME.txt` row came or comes from
  this round.
- Science landed: [C348] an ORDERED RELATION with a LITERAL is accepted on BOTH `?SCCCM`
  literal templates and the ORDER LAW REKEYS the template — the LOWERED pair, not the written
  pair, selects staging (`EB` vs direct `11`, six-byte direct head) and the positional
  immediates, with the [C342] collapse at the relations actually sampled (`<`, `>=`), the
  [C346] BRANCH law (strict JNC `d2`, weak JC `da`) and [C345] over-extent pooled WHOLE
  (arm b `ec904c1`); [C349] qualification invisibility TRANSFERS to the relation family and
  the LOWERED pair plus strictness is the whole object (H4 == golden F3 == H3; arm a
  `c515377`, no new bytes, no prescan twin — the inherited "twins must widen in the same
  commit" note is FALSIFIED, [C152] verified); [C350] the [C346] laws measured on the COMPLETE
  unequal-extent 4-relation × 2-orientation matrix, byte-identical to the arm-c baseline, NO
  ARM, `<=`-swapped equals `>=`-written (I5 == I6 but names); [C351] `^( ... )` over a FIXED
  CHARACTER compare is ACCEPTED and lands on the COMPLEMENT's object byte-for-byte — the skip
  follows the (possibly flipped) relation, never the negation syntax; H-D-extra falsified and
  the inv/simpl readings are BYTE-CONVERGENT, so the claim PREFERS NO READING (arm c
  `47c2194`; the inherited `Gt->Le` entry is falsified as an instruction — only the four
  goldened rewrites are admitted). The [C348] WORDING CORRECTION states that equal-attribute
  `>` was NEVER sampled in any bank.
- Superseded prose — FOUR HANDOFF Next-action/Unfinished prose generations (the P3 CLOSED
  Last-verified-state carried unchanged through the round; the arms-era Next action at
  `19ab4e0`, its renewal-4 rewrite at `e13311c`, the step-6-era CLOSE instruction at `882f77c`
  and the close-authorized instruction at `5c52bba`), the PROGRESS close-era Current-phase
  STATUS stack incl. both superseded arms-era/step-6-era headings, the surviving P2 CLOSED
  previous-phase record, the stale bootstrap-era PROGRESS next-action stub, the P3-frozen
  Verified evidence and the P3-era Blockers — archived verbatim, every block byte-verified
  against its stated git range (16/16 BYTE-EXACT), in
  `docs/history/2026-11-01-e49p4-closed.md`. Goldens untouched except this round's
  `golden/e49p4`.

## Next action — E2E-50/P2 ACTIVE (operator mission brief, bootstrapped 2026-11-02)

**Mission (EXPLICIT OPERATOR AUTHORIZATION E2E-50/P2).** Establish the first practical foundation
for testing PL/I-80 programs by FUNCTIONAL correctness, independent of byte-for-byte DR
target: (1) audit the project's own 8080/CP/M emulator (the Runes lab at `/home/john/pli/lab`,
READ-ONLY) — technical capability matrix + provenance/license/redistribution audit; (2) a small
progressive ORIGINAL corpus (family **TABLE**) with independently specified expected behaviour;
(3) a minimal deterministic execution/validation harness with two lanes (A redistributable core,
B historical PL/I compatibility) and typed verdicts PASS/FAIL/BLOCKED/UNKNOWN — a skipped stage
is never PASS. Deliverable docs: `docs/emulator-audit.md`, `docs/functional-testing.md`.
NOT authorized: compiler implementation changes, PLILIB reimplementation, mass benchmark porting,
third-party benchmark import before rights are verified, changes to `GOAL.md`,
`handoff.config.json`, global Pi config, external Runes sources; NO push, NO automatic P3.

Durable sequence (completed evidence in brackets; explicit-path commits only):
- 0. Documentary bootstrap: P1 close-out inconsistencies measured at HEAD and fixed; this
  mission recorded as the single authority. [landed in the bootstrap commit]
- 1. Emulator technical audit — Intel 8080 core, CP/M BDOS/BIOS, COM loading, console, files,
  determinism, limits, tests — capability matrix IMPLEMENTED/PARTIAL/MISSING/UNTESTED/
  KNOWN DEFECT into `docs/emulator-audit.md`; safe lab tests may be RUN (never infer
  correctness from presence of code). [reconnaissance DONE; measured findings incl. the re-run
  of the lab's 7 test executables (all rc=0) are recorded in `LEARNINGS.md`
  § "2026-11-02 — E2E-50/P2 bootstrap + emulator audit"; the audit DOCUMENT is owed —
  write it from those entries, re-verifying each cited file]
- 2. License/redistribution audit → two-package matrix (free core / historical-compat) in the
  same document; record blockers, recommend options, decide no operator-level license.
  Do NOT copy restricted assets into any prospective package. [evidence gathered in the same
  LEARNINGS section — lab UNLICENSED (single-author history), z80pack MIT, superzazu/8080 MIT,
  DR binaries RESTRICTED, CP/M system Caldera-conditional, exercisers mixed; matrix write owed]
- 3. Functional-test specification format under `spec/functional/` (independence law: BYTE ≠
  correct, exit 0 ≠ correct; failure-origin attribution among compiler/runtime/emulator/source/
  undefined must be measured, never assumed). [pending]
- 4. TABLE corpus: TABLE-00 (traverse/aggregate), TABLE-01 (sort; ordering, multiplicity,
  count, sum, independently computed reference sequence), TABLE-02 only if 0/1 verify; fixed
  inputs incl. negatives/duplicates; provenance headers; original work recorded as such. [pending]
- 5. Harness `tools/functional_runner.py` + tests proving absent deps, timeouts, malformed
  output and mismatched assertions cannot be mistaken for success. [pending]
- 6. Execution evidence: Lane A free-core fixture via the audited emulator where facilities
  permit; Lane B TABLE attempt via local compiler + historical LINK-80/PLILIB, dependency lane
  labelled; classify and preserve blockers honestly. Never substitute an unlabelled emulator.
  [pending]
- 7. Minimal functional-results reporting (reuse P1 model or a separate small report; NO
  reporting-system rewrite; scientific verdicts unchanged; no COVERAGE promotion without
  evidence). [pending]
- 8. Verification + short report (measured / failed / unmeasured), bounded P3 proposal, CLOSE
  (byte-verified archive per convention), `handoff_finalize`, STOP. [pending]

Boundary law: never renew mid-Git-operation or while an emulator process runs; `/home/john/pli/*`
read-only; the operator's `handoff.config.json` edit stays unstaged, untouched; never
`git clean`/`reset --hard`/`add -A`; no push.

## Unfinished operations

- E2E-50/P2 steps 1–8. FIRST ACTION for the successor (renewal hop 1 of the P2 chain):
  confirm HEAD (expect `9c779a4` + guard block commit), tree clean except the operator's
  `handoff.config.json`; then WRITE `docs/emulator-audit.md` — technical capability matrix
  (IMPLEMENTED/PARTIAL/MISSING/UNTESTED/KNOWN DEFECT) + two-package redistribution matrix —
  from the ACCEPTED entries in `LEARNINGS.md` §§ 2026-11-02 E2E-50/P2 (re-verify each cited
  lab path at write time; lab is READ-ONLY; its tests already re-ran rc=0 this chain), keep
  PROPOSED items labelled, add the blockers/release-readiness path; commit explicit paths.
  Then steps 3–8 per the sequence above.
- Standing scientific debts unchanged (`PROGRESS.md` → Pending: LOAN2 prescan, CREATE `%include`);
  this round does not touch them.
- At this boundary: no half-finished Git operation, no emulator process running, `ocaml/` untouched.

## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P4 discovery is incorporated: laws C348..C351 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p4/RESULTS.md` §2), the four new
  COVERAGE rows, the `COND.CMP_LENGTHS_POSITIONAL` extension and the labelled SUPERSEDED/
  WIDENED clauses in `spec/COVERAGE.tsv` (133 rows, 0 errors, 0 warnings), and the labelled
  corrections at [C335]/[C337]/[C344]/[C346]/[C348]. Open PROPOSALS (classified `proposed` in
  `LEARNINGS.md`, NOT law): bank the out-of-scope member-pair and negated-TEST refusals as
  NEG-panel rows; "emit the head as ONE bundled thunk in written order" stays a codegen
  invariant evidenced per-shape — no ledger claim until discriminating probes exist; the [C351]
  inv/simpl readings are recorded as BYTE-CONVERGENT (pre-registered non-separability honoured,
  no reading preferred). P2 BOOTSTRAP MEASUREMENT (falsification, kept per PROTOCOL #2): commit
  `4eb6582` asserted the second glued heading pair `## Discoveries` "does NOT exist in the manual
  region — FALSIFIED by direct measurement"; a byte read of HEAD `942aa78` shows the manual
  glue pairs (`verification.## Discoveries`, `Pending.## History and pointers`) and the
  `golden/e49p4.## Next action` pair, ALL THREE are in the manual region — the close session
  measured only the guard's own rendering. Corrected in the
  P2 bootstrap commit; `4eb6582`'s commit message stands as written (immutable record).

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
  `5c52bba` (identical at HEAD `b5f792c`) — `docs/history/2026-11-01-e49p4-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 115
checkpoint-id: g115-3d39846f732e
checkpoint-kind: auto
content-delta: none
readiness: attested
status: checkpoint (guard level 4, remaining ~4798, session 01a19902-5793-7280-b553-bda51e005404)
checkpointed: 2026-11-01T21:52:59.512Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: dd064a4a956f3460f0c49ce7926d123b3e45acc281d1443aaab7979b127cd515
source-handoff: e66309a9cf512a761432a865891b8fe41d95014873cbf48f34ffb5f203fb71ed
source-learnings: 4ceba92bb908cf025c644c39bbedd42fed21c15905a6c540f29b67602225efd6
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19902-5793-7280-b553-bda51e005404
readiness-at: 2026-11-01T21:52:59.519Z
readiness-checkpoint: g115-3d39846f732e
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-50/P2 ACTIVE (operator mission brief, bootstrapped 2026-11-02)

**Mission (EXPLICIT OPERATOR AUTHORIZATION E2E-50/P2).** Establish the first practical foundation
for testing PL/I-80 programs by FUNCTIONAL correctness, independent of byte-for-byte DR
target: (1) audit the project's own 8080/CP/M emulator (the Runes lab at `/home/john/pli/lab`,
READ-ONLY) — technical capability matrix + provenance/license/redistribution audit; (2) a small
progressive ORIGINAL corpus (family **TABLE**) with independently specified expected behaviour;
(3) a minimal deterministic execution/validation harness with two lanes (A redistributable core,
B historical PL/I compatibility) and typed verdicts PASS/FAIL/BLOCKED/UNKNOWN — a skipped stage
is never PASS. Deliverable docs: `docs/emulator-audit.md`, `docs/functional-testing.md`.
NOT authorized: compiler implementation changes, PLILIB reimplementation, mass benchmark porting,
third-party benchmark import before rights are verified, changes to `GOAL.md`,
`handoff.config.json`, global Pi config, external Runes sources; NO push, NO automatic P3.

Durable sequence (completed evidence in brackets; explicit-path commits only):
- 0. Documentary bootstrap: P1 close-out inconsistencies measured at HEAD and fixed; this
  mission recorded as the single authority. [landed in the bootstrap commit]
- 1. Emulator technical audit — Intel 8080 core, CP/M BDOS/BIOS, COM loading, console, files,
  determinism, limits, tests — capability matrix IMPLEMENTED/PARTIAL/MISSING/UNTESTED/
  KNOWN DEFECT into `docs/emulator-audit.md`; safe lab tests may be RUN (never infer
  correctness from presence of code). [reconnaissance DONE; measured findings incl. the re-run
  of the lab's 7 test executables (all rc=0) are recorded in `LEARNINGS.md`
  § "2026-11-02 — E2E-50/P2 bootstrap + emulator audit"; the audit DOCUMENT is owed —
  write it from those entries, re-verifying each cited file]
- 2. License/redistribution audit → two-package matrix (free core / historical-compat) in the
  same document; record blockers, recommend options, decide no operator-level license.
  Do NOT copy restricted assets into any prospective package. [evidence gathered in the same
  LEARNINGS section — lab UNLICENSED (single-author history), z80pack MIT, superzazu/8080 MIT,
  DR binaries RESTRICTED, CP/M system Caldera-conditional, exercisers mixed; matrix write owed]
- 3. Functional-test specification format under `spec/functional/` (independence law: BYTE ≠
  correct, exit 0 ≠ correct; failure-origin attribution among compiler/runtime/emulator/source/
  undefined must be measured, never assumed). [pending]
- 4. TABLE corpus: TABLE-00 (traverse/aggregate), TABLE-01 (sort; ordering, multiplicity,
  count, sum, independently computed reference sequence), TABLE-02 only if 0/1 verify; fixed
  inputs incl. negatives/duplicates; provenance headers; original work recorded as such. [pending]
- 5. Harness `tools/functional_runner.py` + tests proving absent deps, timeouts, malformed
  output and mismatched assertions cannot be mistaken for success. [pending]
- 6. Execution evidence: Lane A free-core fixture via the audited emulator where facilities
  permit; Lane B TABLE attempt via local compiler + historical LINK-80/PLILIB, dependency lane
  labelled; classify and preserve blockers honestly. Never substitute an unlabelled emulator.
  [pending]
- 7. Minimal functional-results reporting (reuse P1 model or a separate small report; NO
  reporting-system rewrite; scientific verdicts unchanged; no COVERAGE promotion without
  evidence). [pending]
- 8. Verification + short report (measured / failed / unmeasured), bounded P3 proposal, CLOSE
  (byte-verified archive per convention), `handoff_finalize`, STOP. [pending]

Boundary law: never renew mid-Git-operation or while an emulator process runs; `/home/john/pli/*`
read-only; the operator's `handoff.config.json` edit stays unstaged, untouched; never
`git clean`/`reset --hard`/`add -A`; no push.

### Guard notes
E2E-50/P2 renewal hop 1. Durable state: HANDOFF.md -> Next action FIRST ACTION; LEARNINGS.md 2026-11-02 sections hold all accepted audit recon + open questions. Commits: 459f51e (bootstrap), aded7b3 (g112), 38c8e5d (recon), 9c779a4 (open questions), plus this guard block commit. Do: write docs/emulator-audit.md from LEARNINGS entries, re-verifying cited lab paths read-only (/home/john/pli/lab, HEAD 43e38ba; NEVER edit external tree; building lab tests writes only ignored _build and may be skipped — suite already rc=0). Then steps 3-8 (spec format, TABLE corpus, harness, Lane A/B evidence, minimal reporting, close). Hard limits: no compiler changes, no push, no GOAL.md/handoff.config.json edits, no oracle campaign, DR binaries never in distributable artifacts, UNKNOWN/BLOCKED never rendered as PASS.
<!-- guard:end checkpoint -->
