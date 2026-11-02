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
  correctness from presence of code). [**LANDED** at renewal hop 1: `docs/emulator-audit.md`
  §1-4 capability matrix rows 2.1–2.20; every cited lab path/line re-verified read-only at
  write time (lab HEAD `43e38ba` unchanged); new accepted measurements in `LEARNINGS.md`
  § hop-1 subsection — notably `pli80-run` DISCARDS buffered program output on every error
  path (stdout valid only at exit 0; failure evidence needs `--trace`)]
- 2. License/redistribution audit → two-package matrix (free core / historical-compat) in the
  same document; record blockers, recommend options, decide no operator-level license.
  Do NOT copy restricted assets into any prospective package. [**LANDED** in the same
  document §5-7: single hard Package-A blocker = operator license decision on the UNLICENSED
  lab; `research/{minimal-baseline,host-compiler}` now classified DR-image derivatives from
  re-read READMEs (open question CLOSED); QX10CPMPlus classified proprietary/unresolved,
  excluded (open question CLOSED); no license decided, no restricted asset copied]
- 3. Functional-test specification format under `spec/functional/` (independence law: BYTE ≠
  correct, exit 0 ≠ correct; failure-origin attribution among compiler/runtime/emulator/source/
  undefined must be measured, never assumed). [**LANDED** hop 2: `spec/functional/tests/README.md`
  schema `pli80-functional/1` + `docs/functional-testing.md`; independence laws L1/L2/L3 (L2 =
  [C137] UNDEFINED-SYMBOLS law + never-truncate-the-transcript corollary); stage chain
  SOURCE→DERIVATION→COMPILE→LINK→RUN→ASSERT with spec-declared not-applicable; verdict law
  PASS/FAIL/BLOCKED/UNKNOWN, skipped-stage-never-PASS; typed attribution enum from evidence
  only; gate comparison law quoted at `tools/e2e_gate.py:5646-5685`, the v1 stream law is
  deliberately stricter (documented deviation); v1 capability perimeter fixed from COVERAGE]
- 4. TABLE corpus: TABLE-00 (traverse/aggregate), TABLE-01 (sort; ordering, multiplicity,
  count, sum, independently computed reference sequence), TABLE-02 only if 0/1 verify; fixed
  inputs incl. negatives/duplicates; provenance headers; original work recorded as such. [**LANDED**
  hop 2: `spec/functional/tests/TABLE-00.{PLI,json}`, `TABLE-01.{PLI,json}`, `reference.py`
  (stdlib-only; table01 expects Python's OWN sorted multiset). Original-work provenance headers,
  CRLF+`^Z`≤71 cols, sha256-pinned sources, capabilities all re-validated against COVERAGE;
  scalar-copy stable rank sort honours the AB11/LR9 element-compare refusals. Spec-validation
  checks all pass; both compile against the current binary (896 B code=358 data=30 / 1536 B
  code=627 data=50). TABLE-02 WITHHELD: "verify" means executed step-6 evidence, not compiling]
- 5. Harness `tools/functional_runner.py` + tests proving absent deps, timeouts, malformed
  output and mismatched assertions cannot be mistaken for success. [**PART 1 LANDED** hop 3
  `8523eda`: harness implements README §3/4/5/8/9/11 mechanically — fail-closed validation,
  SOURCE sha256+encoding, DERIVATION in its own process, COMPILE via local `pli80c.exe -d`,
  LINK through `oracle/cpmwork.py` Workspace with `parse_undefined` on the FULL segment,
  lane-labelled RUN ([C308] witnesses done/timeout/sim-died/wall-clock-timeout), complete-stream
  `collapse-spaces-v1` ASSERT with `!text` negatives, unrun/skipped stage never PASS,
  attribution never narrowed (assert mismatch = `undefined`), `--double-run` determinism proof,
  `--stages` ceiling, all external layers injectable. Measured: py_compile rc=0, --help rc=0,
  bounded real run `--stages SOURCE,DERIVATION` on TABLE-00/01 -> SOURCE+DERIVATION pass, both
  verdicts UNKNOWN (COMPILE unrun), PASS=0. **PART 2 LANDED hop 4 `d40aafb`+`149c6e2`:** hostile suite `tools/test_functional_runner.py`, 148 checks rc=0, no external process (pure oracle import); the suite FOUND two harness defects, fixed in the same commit: `_rname` undefined (attempted Lane A RUN crashed, Lane B laundered harness-exception) and eager first_diff=None TypeError in `assert_stream` on differ-by-length streams. Measured nuance: DERIVATION/ASSERT are evaluation stages unaffected by `--stages`; a SOURCE..RUN ceiling PASSes on earned ASSERT evidence]
- 6. Execution evidence: Lane A free-core fixture via the audited emulator where facilities
  permit; Lane B TABLE attempt via local compiler + historical LINK-80/PLILIB, dependency lane
  labelled; classify and preserve blockers honestly. Never substitute an unlabelled emulator.
  [**PRE-REGISTERED + LANDED PART 1** hop 5 `690c3a1`: PLAN.md commits every predicted verdict
  BEFORE any run (PROTOCOL #1); Lane A fixtures FX-00 (BDOS 9/2/11/12/0, PASS expected) +
  FX-01 (BDOS 1 typed error, FAIL/`emulator` expected) with generator
  `tools/mk_functional_fixture.py` (--check rc=0), specs, `reference.py:fx00/fx01` derivations,
  labelled README 3 amendment (`capabilities: []` legal ONLY for Lane-A-only fixtures; lane B
  still fails closed; hostile suite rc=0 148 checks unchanged), and the harness `--census`
  substrate probe for audit open question 1. **EXECUTION REMAINS**: build pli80-run in the lab's
  ignored `_build`, run Lane A (FX-00 double-run determinism, FX-01 typed error), then Lane B
  TABLE-00/01 COMPILE->LINK->RUN->ASSERT, then the census probe of the exported .COM.
  **PART 2 LANDED — EXECUTED** hop 6, verified read-only against the preserved evidence and
  committed by the successor hop 7 at `68348ac` (`spec/lab-evidence/e2e50-p2/step6/RESULTS.md`;
  evidence roots ignored under `build/functional/`): FX-00 **PASS** + double-run capture `cmp`
  rc=0 (audit 2.20 proved EXECUTED; call total 14 — PLAN's written "13" an arithmetic slip,
  distribution correct, kept); FX-01 **FAIL attr=`emulator`** as intended (first executed typed
  attribution; audit 2.18 CONFIRMED and STRENGTHENED — the discarded capture is 0 bytes though
  the trace shows the fn-9 banner written at step 3); **first functional execution of a
  DRPLi-compiled PL/I program**: TABLE-00/01 COMPILE 896/1536 B, LINK PASS (FULL segments ZERO
  `UNDEFINED` lines, `PLILIB   RQST` present, .COM 7552/7808 B), RUN `done` rc=0, **ASSERT FAIL
  attr=`undefined`** (never narrowed) — CONTENT ≡ REFERENCE for both programs, semantics clean;
  both FAILs are FRAMING: F1 harness anchor law (terminal lone CR after the `(?=\nD>)` cut) and
  F2 measured DR PLILIB 79-column print-wrap (guest-written CRLF proven; promotion needs its own
  oracle round). **Census:** BOTH linked .COMs issue BDOS **25 as their FIRST call** (PLILIB
  init) and the audited emulator fails typed rc=1 — "pure-PUT" census hypothesis FALSIFIED, audit
  open question 1 ANSWERED-partial: the free core cannot host PLILIB programs; full
  linked-program census UNMEASURED.]
- 7. Minimal functional-results reporting (reuse P1 model or a separate small report; NO
  reporting-system rewrite; scientific verdicts unchanged; no COVERAGE promotion without
  evidence). [**LANDED** hop 7: `958c204` + `cdc5d13` — the step-6 §3 debt PAID and MEASURED
  (pre-fix probe printed `len 128` on the runner's stdout; the prediction was committed BEFORE the
  post-fix run, which printed ZERO foreign lines with verdict/rc UNCHANGED; `cpmwork.Run.export()`
  now redirects cpmcp stdio symmetrically with import_local/mkfs, the `ok` bool contract intact so
  no gate weakens). Lane A fallback repaired to the MEASURED `LANE_A_CANDIDATES` (hop-6
  falsification) and proven on the real substrate: `FX-00` WITHOUT `--pli80-run` -> lane A **PASS**,
  capture identical to step 6. Hostile suite +C14: CLI stdout grammar CLOSED (record/evidence/
  verdicts only), non-vacuous via a simulated chatty child; **171 → 182 checks**, rc=0. Report =
  `docs/functional-results.md` (a rendering of step6/step7 `RESULTS.md`, four executed verdicts +
  the census probe, F1/F2 framing, honest limits, P3 candidates as proposals; NO dashboard rewrite,
  no COVERAGE/CLAIMS change). HONESTY MEASUREMENT: the prose "148 checks" was FALSIFIED — the HEAD
  artifact printed 171; the suite now self-counts, so documents must quote the artifact.]
- 8. Verification + short report (measured / failed / unmeasured), bounded P3 proposal, CLOSE
  (byte-verified archive per convention), `handoff_finalize`, STOP. [**PART 1 LANDED** hop 7
  `d648bcd`: `spec/lab-evidence/e2e50-p2/REPORT.md` — delivered table, MEASURED / FALSIFIED /
  UNMEASURED sections, boundary compliance, and the bounded P3 proposal (P3-a anchor fix, P3-b
  declare F2 from the oracle side, P3-c free-core BDOS 25 + license decision, P3-d TABLE-02 — all
  PROPOSALS, no execution). **FULL COMPILE-TIER GATE rc=0 measured by this session at HEAD
  `545dcf1`, ACTUALS AS PRINTED:** byte panel **1174 byte-exact / 0 fail of 1174** (independent
  cross-check `grep -c BYTE-EXACT` = 1174), negative **181/181** with the E46K14 `[dr-refuses]`
  pinned marker UNMOVED, divergence **9/9**, coverage **133 rows 0 errors 0 warnings**, census
  **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0** (UNCHANGED), prose **5 active files clean**.
  **REMAINING (close only):** the byte-verified archive + CLOSED rewrite + `handoff_finalize` —
  see Unfinished operations.]

Boundary law: never renew mid-Git-operation or while an emulator process runs; `/home/john/pli/*`
read-only; the operator's `handoff.config.json` edit stays unstaged, untouched; never
`git clean`/`reset --hard`/`add -A`; no push.

## Unfinished operations

- E2E-50/P2 step 8 CLOSE ONLY remains (steps 0–7 delivered: bootstrap `459f51e`; audit `97ad1f0`; spec
  format, law, TABLE corpus and reference in the hop-2 commit `a6163ef`; **harness step-5 part 1
  LANDED hop 3 at `8523eda`**). **Step 5 PART 2 LANDED hop 4 (`d40aafb`,`149c6e2`): 13 required cases, 148 checks, rc=0, NO compiler/LINK-80/cpmsim/emulator process; harness defects `_rname` and `assert_stream` first_diff=None found by the suite and fixed. **Step 6
  EXECUTED hop 6** (runs bounded and lane-labelled; Lane A via the audited emulator, Lane B via
  local compiler + historical LINK-80/PLILIB under cpmsim); ACTUALS verified read-only against the
  preserved evidence and committed hop 7 at `68348ac` — FX-00 PASS + determinism proved; FX-01
  FAIL/`emulator` intended (audit 2.18 confirmed, strengthened); first functional execution of
  DRPLi-compiled TABLE-00/01 (content ≡ reference; ASSERT FAILs are framing F1/F2, attribution
  stays `undefined`); census fn-25 blocker measured (free core cannot host PLILIB programs).
  **FIRST ACTION for the successor: step 7** — minimal functional-results reporting (reuse the P1
  model or a separate small report; NO reporting-system rewrite; scientific verdicts unchanged; NO
  COVERAGE promotion) plus the step-6 §3 debt: capture/DEVNULL cpmcp stdio in
  `oracle/cpmwork.py export()` and a hostile-suite pin that runner stdout carries ONLY rendered
  records; then step 8 (report + bounded P3 proposal + CLOSE + finalize). **Step 7 LANDED hop 7
  (`958c204`, `cdc5d13`): the cpmcp debt measured/fixed/re-measured, the Lane A fallback repaired
  and proven on the real substrate (FX-00 PASS with no `--pli80-run`), the hostile suite at 182
  checks with the CLI stdout grammar pinned closed and non-vacuously, and the small report
  `docs/functional-results.md` delivered. FIRST ACTION for the successor: step 8** — verification
  (`python3 tools/e2e_gate.py`, compile tier only: the round touched no scientific byte, but the
  round's own harness/doc changes must pass the gate; record ACTUALS as printed), the short round
  report (measured / failed / unmeasured), the BOUNDED P3 proposal (F1 anchor fix, F2 declared
  from the oracle side, BDOS-25 free-core question, TABLE-02 — all proposals, no execution),
  the byte-verified close archive of the superseded prose under `docs/history/`, then
  `handoff_finalize` and STOP. No push; no automatic P3.
  **STEP-8 CLOSE PROCEDURE for the successor (exact, bounded; no compiler/oracle/gate/emulator
  run is needed — the gate ACTUALS are already recorded at `d648bcd`):**
  (1) `git rev-parse HEAD` must be `d648bcd` (or a descendant) and the tree clean apart from the
  operator's `handoff.config.json` edit and the guard's managed blocks; `/handoff verify` the
  checkpoint (refresh + re-attest if stale).
  (2) Archive the superseded prose VERBATIM into `docs/history/2026-11-02-e50p2-closed.md`: the
  HANDOFF `## Next action` mission brief + durable sequence and `## Unfinished operations` as they
  stand at `d648bcd` (and any earlier generation you find superseded mid-round: the hop-5 and
  arms-era instructions quoted in PROGRESS), the PROGRESS `## Current phase` hop stack and its
  `## Next action` prose; add an index row to `docs/history/README.md`.
  (3) BYTE-VERIFY every archived block: re-extract each stated region with
  `git show <rev>:<file>` and `cmp` it against the written block — report n/n BYTE-EXACT from the
  measurement, never from intent (the e49p4 precedent measured "two planned" as four actual
  generations).
  (4) Rewrite HANDOFF Next action / PROGRESS Current phase to **E2E-50/P2 CLOSED** with the last
  verified state (gate ACTUALS above, ledger ENDS at C351 unchanged, byte panel 1174, coverage
  133, suite 182 checks self-counted) and the next action = NO active round: a successor without
  an operator instruction confirms HEAD/tree, `/handoff verify`, records state, STOPS; the P3
  candidate list is `spec/lab-evidence/e2e50-p2/REPORT.md` §5 (a shortlist, never an
  authorisation).
  (5) LEARNINGS close note (accepted: gate rc=0 ACTUALS at `545dcf1`; the round's falsifications
  already recorded hops 6–7), then `handoff_finalize` and STOP. No push. (hostile suite over the landed harness, `check()`-style like
  `tools/test_functional_dashboard.py`, NO compiler/LINK-80/cpmsim/emulator process — every
  external layer is injectable via `Host(subprocess_run=, sim_session=, link_deps=,
  workspace_factory=, run_factory=)`):
  (1) absent deps → BLOCKED named by path, never PASS; (2) wall-clock timeout vs `timeout`(rc=1)
  vs `sim-died`(rc=2) → three distinct witnesses, none PASS; (3) malformed output (no
  `>>> LINK D:` segment / no console anchor) → UNKNOWN; (4) UNDEFINED SYMBOLS beyond char 120 in
  the FULL segment + a .COM present → FAIL (L2/[C137]); (5) assertion mismatch → FAIL with
  attribution `undefined` (never narrowed); (6) unknown spec field / `null` required field /
  empty `expected.console` / forbidden or REFUSED-or-DIVERGENT capability / lane-A `link_targets`
  / lane-B `artifact` / multi link_target / `file_expectations` → spec FAIL attr `source` with NO
  lane stage run; (7) source or artifact sha256 mismatch → SOURCE FAIL `source`; (8) derivation
  drift → FAIL `source`; (9) `--stages` ceiling → unrun stage ⇒ UNKNOWN, never PASS; (10) Lane A
  rc≠0 ⇒ stdout discarded (audit 2.18), typed runner-error ⇒ FAIL `emulator`, unclassified ⇒
  UNKNOWN; (11) `--double-run` equal ⇒ PASS possible, differing ⇒ UNKNOWN; (12) positive control:
  stubbed PASS reachable end-to-end (else the suite is vacuous); (13) `render_line`/records never
  print PASS for BLOCKED/UNKNOWN. Then step 6 (Lane A hand-crafted .COM fixture + Lane B TABLE
  attempt via local compiler + historical LINK-80/PLILIB under cpmsim, BDOS census = open
  question #1), step 7 (minimal reporting, no COVERAGE promotion), step 8 (report + bounded P3
  proposal + CLOSE + finalize). Harness defects seen but NOT yet fixed (verify first): compile
  `-d` banner parse is optional; Lane A artifact identity recorded by hash; `evidence:` printed
  relative to repo root (ugly for /tmp roots).
  fail-closed schema validation (unknown fields are errors); SOURCE sha256 check; DERIVATION
  double-check via `reference.py:derive()`; COMPILE via the local `pli80c.exe`; LINK through the
  `oracle/cpmwork.py` Workspace machinery applying `oracle/linkrun.py` `parse_undefined` to the
  FULL segment — never a [:120] slice; RUN per lane; ASSERT = complete normalized stream,
  collapse-spaces-v1 (README § 4); verdicts per § 8 (skipped/unrun stage never PASS; timeouts
  record WHICH termination witness class, [C308] lesson); typed attribution per § 9 (Lane A
  stdout valid only at exit 0 — failure evidence needs `--trace`). Plus the hostile test suite
  proving absent deps, timeouts, malformed output and mismatched assertions cannot be mistaken
  for success, and the audit § 2.20 determinism double-run proof (lane-labelled).
  Then step 6 (Lane A hand-crafted .COM fixture under the audited emulator; Lane B TABLE attempt
  via local compiler + historical LINK-80/PLILIB under cpmsim — restricted tools user-supplied,
  never packaged; measure the linked-program BDOS census, open question #1; never the oracle
  campaign), step 7 (minimal reporting reusing the P1 model; no COVERAGE promotion), step 8
  (report measured/failed/unmeasured + bounded P3 proposal + CLOSE with byte-verified archive +
  finalize). Hard limits unchanged: no compiler implementation changes, no push, no GOAL or
  handoff.config.json edits, no oracle campaign or full runtime tier, DR binaries never
  distributable, UNKNOWN/BLOCKED never rendered PASS, `/home/john/pli/*` read-only (lab builds
  touch only its ignored `_build`).
- Standing scientific debts unchanged (`PROGRESS.md` → Pending: LOAN2 prescan, CREATE `%include`);
  this round does not touch them.
- At this boundary: no half-finished Git operation, no emulator process running, `ocaml/`
  untouched (build only).

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
checkpoint-generation: 131
checkpoint-id: g131-46049167bd73
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 1, remaining ~11302, session 01a199c0-2008-7280-b553-bdc13929ba82)
checkpointed: 2026-11-02T01:18:40.071Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 6c786836472422375f4d49b0251b1e6b0af6cf7d6ad4e6de7d3892ebaebc1188
source-handoff: 91545486e6315283483788c62dbbd43fad9144435f631001f899e58da81a2cd1
source-learnings: 7c20ad5f942dbcae8486e25b37f9deaa3587dd66d27dd3d702e2efe67e4ef89b
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a199c0-2008-7280-b553-bdc13929ba82
readiness-at: 2026-11-02T01:18:40.075Z
readiness-checkpoint: g131-46049167bd73
### Last verified state
guard level 1; checkpoint requested (renewal tool refresh)

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
  correctness from presence of code). [**LANDED** at renewal hop 1: `docs/emulator-audit.md`
  §1-4 capability matrix rows 2.1–2.20; every cited lab path/line re-verified read-only at
  write time (lab HEAD `43e38ba` unchanged); new accepted measurements in `LEARNINGS.md`
  § hop-1 subsection — notably `pli80-run` DISCARDS buffered program output on every error
  path (stdout valid only at exit 0; failure evidence needs `--trace`)]
- 2. License/redistribution audit → two-package matrix (free core / historical-compat) in the
  same document; record blockers, recommend options, decide no operator-level license.
  Do NOT copy restricted assets into any prospective package. [**LANDED** in the same
  document §5-7: single hard Package-A blocker = operator license decision on the UNLICENSED
  lab; `research/{minimal-baseline,host-compiler}` now classified DR-image derivatives from
  re-read READMEs (open question CLOSED); QX10CPMPlus classified proprietary/unresolved,
  excluded (open question CLOSED); no license decided, no restricted asset copied]
- 3. Functional-test specification format under `spec/functional/` (independence law: BYTE ≠
  correct, exit 0 ≠ correct; failure-origin attribution among compiler/runtime/emulator/source/
  undefined must be measured, never assumed). [**LANDED** hop 2: `spec/functional/tests/README.md`
  schema `pli80-functional/1` + `docs/functional-testing.md`; independence laws L1/L2/L3 (L2 =
  [C137] UNDEFINED-SYMBOLS law + never-truncate-the-transcript corollary); stage chain
  SOURCE→DERIVATION→COMPILE→LINK→RUN→ASSERT with spec-declared not-applicable; verdict law
  PASS/FAIL/BLOCKED/UNKNOWN, skipped-stage-never-PASS; typed attribution enum from evidence
  only; gate comparison law quoted at `tools/e2e_gate.py:5646-5685`, the v1 stream law is
  deliberately stricter (documented deviation); v1 capability perimeter fixed from COVERAGE]
- 4. TABLE corpus: TABLE-00 (traverse/aggregate), TABLE-01 (sort; ordering, multiplicity,
  count, sum, independently computed reference sequence), TABLE-02 only if 0/1 verify; fixed
  inputs incl. negatives/duplicates; provenance headers; original work recorded as such. [**LANDED**
  hop 2: `spec/functional/tests/TABLE-00.{PLI,json}`, `TABLE-01.{PLI,json}`, `reference.py`
  (stdlib-only; table01 expects Python's OWN sorted multiset). Original-work provenance headers,
  CRLF+`^Z`≤71 cols, sha256-pinned sources, capabilities all re-validated against COVERAGE;
  scalar-copy stable rank sort honours the AB11/LR9 element-compare refusals. Spec-validation
  checks all pass; both compile against the current binary (896 B code=358 data=30 / 1536 B
  code=627 data=50). TABLE-02 WITHHELD: "verify" means executed step-6 evidence, not compiling]
- 5. Harness `tools/functional_runner.py` + tests proving absent deps, timeouts, malformed
  output and mismatched assertions cannot be mistaken for success. [**PART 1 LANDED** hop 3
  `8523eda`: harness implements README §3/4/5/8/9/11 mechanically — fail-closed validation,
  SOURCE sha256+encoding, DERIVATION in its own process, COMPILE via local `pli80c.exe -d`,
  LINK through `oracle/cpmwork.py` Workspace with `parse_undefined` on the FULL segment,
  lane-labelled RUN ([C308] witnesses done/timeout/sim-died/wall-clock-timeout), complete-stream
  `collapse-spaces-v1` ASSERT with `!text` negatives, unrun/skipped stage never PASS,
  attribution never narrowed (assert mismatch = `undefined`), `--double-run` determinism proof,
  `--stages` ceiling, all external layers injectable. Measured: py_compile rc=0, --help rc=0,
  bounded real run `--stages SOURCE,DERIVATION` on TABLE-00/01 -> SOURCE+DERIVATION pass, both
  verdicts UNKNOWN (COMPILE unrun), PASS=0. **PART 2 LANDED hop 4 `d40aafb`+`149c6e2`:** hostile suite `tools/test_functional_runner.py`, 148 checks rc=0, no external process (pure oracle import); the suite FOUND two harness defects, fixed in the same commit: `_rname` undefined (attempted Lane A RUN crashed, Lane B laundered harness-exception) and eager first_diff=None TypeError in `assert_stream` on differ-by-length streams. Measured nuance: DERIVATION/ASSERT are evaluation stages unaffected by `--stages`; a SOURCE..RUN ceiling PASSes on earned ASSERT evidence]
- 6. Execution evidence: Lane A free-core fixture via the audited emulator where facilities
  permit; Lane B TABLE attempt via local compiler + historical LINK-80/PLILIB, dependency lane
  labelled; classify and preserve blockers honestly. Never substitute an unlabelled emulator.
  [**PRE-REGISTERED + LANDED PART 1** hop 5 `690c3a1`: PLAN.md commits every predicted verdict
  BEFORE any run (PROTOCOL #1); Lane A fixtures FX-00 (BDOS 9/2/11/12/0, PASS expected) +
  FX-01 (BDOS 1 typed error, FAIL/`emulator` expected) with generator
  `tools/mk_functional_fixture.py` (--check rc=0), specs, `reference.py:fx00/fx01` derivations,
  labelled README 3 amendment (`capabilities: []` legal ONLY for Lane-A-only fixtures; lane B
  still fails closed; hostile suite rc=0 148 checks unchanged), and the harness `--census`
  substrate probe for audit open question 1. **EXECUTION REMAINS**: build pli80-run in the lab's
  ignored `_build`, run Lane A (FX-00 double-run determinism, FX-01 typed error), then Lane B
  TABLE-00/01 COMPILE->LINK->RUN->ASSERT, then the census probe of the exported .COM.
  **PART 2 LANDED — EXECUTED** hop 6, verified read-only against the preserved evidence and
  committed by the successor hop 7 at `68348ac` (`spec/lab-evidence/e2e50-p2/step6/RESULTS.md`;
  evidence roots ignored under `build/functional/`): FX-00 **PASS** + double-run capture `cmp`
  rc=0 (audit 2.20 proved EXECUTED; call total 14 — PLAN's written "13" an arithmetic slip,
  distribution correct, kept); FX-01 **FAIL attr=`emulator`** as intended (first executed typed
  attribution; audit 2.18 CONFIRMED and STRENGTHENED — the discarded capture is 0 bytes though
  the trace shows the fn-9 banner written at step 3); **first functional execution of a
  DRPLi-compiled PL/I program**: TABLE-00/01 COMPILE 896/1536 B, LINK PASS (FULL segments ZERO
  `UNDEFINED` lines, `PLILIB   RQST` present, .COM 7552/7808 B), RUN `done` rc=0, **ASSERT FAIL
  attr=`undefined`** (never narrowed) — CONTENT ≡ REFERENCE for both programs, semantics clean;
  both FAILs are FRAMING: F1 harness anchor law (terminal lone CR after the `(?=\nD>)` cut) and
  F2 measured DR PLILIB 79-column print-wrap (guest-written CRLF proven; promotion needs its own
  oracle round). **Census:** BOTH linked .COMs issue BDOS **25 as their FIRST call** (PLILIB
  init) and the audited emulator fails typed rc=1 — "pure-PUT" census hypothesis FALSIFIED, audit
  open question 1 ANSWERED-partial: the free core cannot host PLILIB programs; full
  linked-program census UNMEASURED.]
- 7. Minimal functional-results reporting (reuse P1 model or a separate small report; NO
  reporting-system rewrite; scientific verdicts unchanged; no COVERAGE promotion without
  evidence). [**LANDED** hop 7: `958c204` + `cdc5d13` — the step-6 §3 debt PAID and MEASURED
  (pre-fix probe printed `len 128` on the runner's stdout; the prediction was committed BEFORE the
  post-fix run, which printed ZERO foreign lines with verdict/rc UNCHANGED; `cpmwork.Run.export()`
  now redirects cpmcp stdio symmetrically with import_local/mkfs, the `ok` bool contract intact so
  no gate weakens). Lane A fallback repaired to the MEASURED `LANE_A_CANDIDATES` (hop-6
  falsification) and proven on the real substrate: `FX-00` WITHOUT `--pli80-run` -> lane A **PASS**,
  capture identical to step 6. Hostile suite +C14: CLI stdout grammar CLOSED (record/evidence/
  verdicts only), non-vacuous via a simulated chatty child; **171 → 182 checks**, rc=0. Report =
  `docs/functional-results.md` (a rendering of step6/step7 `RESULTS.md`, four executed verdicts +
  the census probe, F1/F2 framing, honest limits, P3 candidates as proposals; NO dashboard rewrite,
  no COVERAGE/CLAIMS change). HONESTY MEASUREMENT: the prose "148 checks" was FALSIFIED — the HEAD
  artifact printed 171; the suite now self-counts, so documents must quote the artifact.]
- 8. Verification + short report (measured / failed / unmeasured), bounded P3 proposal, CLOSE
  (byte-verified archive per convention), `handoff_finalize`, STOP. [**PART 1 LANDED** hop 7
  `d648bcd`: `spec/lab-evidence/e2e50-p2/REPORT.md` — delivered table, MEASURED / FALSIFIED /
  UNMEASURED sections, boundary compliance, and the bounded P3 proposal (P3-a anchor fix, P3-b
  declare F2 from the oracle side, P3-c free-core BDOS 25 + license decision, P3-d TABLE-02 — all
  PROPOSALS, no execution). **FULL COMPILE-TIER GATE rc=0 measured by this session at HEAD
  `545dcf1`, ACTUALS AS PRINTED:** byte panel **1174 byte-exact / 0 fail of 1174** (independent
  cross-check `grep -c BYTE-EXACT` = 1174), negative **181/181** with the E46K14 `[dr-refuses]`
  pinned marker UNMOVED, divergence **9/9**, coverage **133 rows 0 errors 0 warnings**, census
  **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0** (UNCHANGED), prose **5 active files clean**.
  **REMAINING (close only):** the byte-verified archive + CLOSED rewrite + `handoff_finalize` —
  see Unfinished operations.]

Boundary law: never renew mid-Git-operation or while an emulator process runs; `/home/john/pli/*`
read-only; the operator's `handoff.config.json` edit stays unstaged, untouched; never
`git clean`/`reset --hard`/`add -A`; no push.

### Guard notes
E2E-50/P2 hop 7 close-out. HEAD 68831ff (steps 0-7 LANDED; step 8 PART 1 landed: gate rc=0 measured at 545dcf1 with ACTUALS AS PRINTED, round report spec/lab-evidence/e2e50-p2/REPORT.md at d648bcd). REMAINING = STEP-8 CLOSE ONLY, a docs-only operation: follow HANDOFF.md -> Unfinished operations -> "STEP-8 CLOSE procedure for the successor" (verbatim archive of superseded HANDOFF/PROGRESS prose into docs/history/2026-11-02-e50p2-closed.md, byte-verify EVERY block by cmp against its stated rev and report n/n from measurement, add docs/history/README.md index row, rewrite HANDOFF Next action + PROGRESS Current phase to E2E-50/P2 CLOSED incl. the recorded gate ACTUALS (byte panel 1174/0, neg 181/181 E46K14 UNMOVED, div 9/9, cov 133/0/0, census 15/0/26/0 unchanged, prose 5 clean, suite self-counts 182), the no-active-round successor instruction, the P3 shortlist pointer (REPORT.md section 5 = shortlist, never an authorisation), LEARNINGS close note, then handoff_finalize and STOP). NO compiler/oracle/LINK-80/cpmsim/emulator/gate run is needed to close. Limits: /home/john/pli/* read-only; operator handoff.config.json stays unstaged/untouched; never git clean/reset --hard/add -A; explicit-path commits only; no push; no automatic P3; never renew mid-git-op or while an emulator runs.
<!-- guard:end checkpoint -->
