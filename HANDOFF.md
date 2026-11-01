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
6. **E2E-50/P1 (active).** The functional dashboard reads existing canonical evidence only
   (`spec/INVENTORY.txt`, `spec/COVERAGE.tsv`, `spec/census/corpus-census.json`,
   `spec/census/coverage-stats.json`, `spec/RUNTIME.txt`, `spec/DIVERGENT.txt`,
   `tools/panel_keys.py`) plus the annotations in `spec/functional/`; it writes only
   `docs/functional-status.md` and never runs the compiler, the oracle or the gate. Do not
   re-derive census or panel numbers by compiling.

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
  `golden/e49p4`.## Next action — E2E-50/P1 CLOSED (2026-11-02; deliverables `4cad695`, close this commit)

The functional dashboard round is COMPLETE: validation fixes + `spec/functional/programs.tsv`
(68 programs, 3 origin classes never summed) + `tools/functional_dashboard.py` (reads canonical
evidence only, imports the gate module, compiles/runs NOTHING, deterministic, UNKNOWN never
rendered as success) + `tools/test_functional_dashboard.py` (30/30) + generated
`docs/functional-status.md` (views A–E) + the replaced `README.md` status section + the labelled
[E2E-50/P1 CORRECTION(S)] in `LEARNINGS.md`. Evidence-infrastructure audit in `LEARNINGS.md`
2026-11-02. Superseded prose archived byte-verified in
`docs/history/2026-11-02-e50p1-closed.md`.

NO active round exists. A successor session without an operator instruction confirms HEAD and the
tree, runs `/handoff verify`, records state and STOPS. The ranked candidate shortlist for the
operator's E2E-50/P2 choice lives in `docs/functional-status.md` §E (regenerate:
`python3 tools/functional_dashboard.py --check`; `--write` after any ledger change); the measured
boundaries live in `PROGRESS.md` → Blockers and Pending. This is a shortlist, NOT an
authorisation; any round needs the operator's authorization and PROTOCOL pre-registration.

Standing: never run compiler/oracle/gate in infrastructure sessions; never touch the operator's
`handoff.config.json` edit; renewal values ONLY in `handoff.config.json` / `/guard status`;
never `git clean`/`reset --hard`/`add -A`; no push.

## Unfinished operations

- (none) — E2E-49/P4 is CLOSED: arms a/b/c (`c515377`/`ec904c1`/`47c2194`), claims C348..C351
  plus the four labelled P4 CORRECTION blocks (`9c42f3b`) and the [C348] WORDING CORRECTION
  (`5b0ccde`), registration (panel 1174), COVERAGE (133 rows, 0 errors, 0 warnings), the FULL
  compile-tier gate (rc=0 measured at `5b0ccde`, recorded `882f77c`) and the CLOSE
  (four-generation archive `docs/history/2026-11-01-e49p4-closed.md` byte-verified block by
  block — 16/16 —, HANDOFF/PROGRESS/LEARNINGS rewritten, `docs/history/README.md` index
  updated) all landed. Standing debts live in `PROGRESS.md` → Pending; the candidate pool lives
  in the Next action above. Nothing in `ocaml/` is half-edited and no scientific byte awaits
  verification.## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P4 discovery is incorporated: laws C348..C351 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p4/RESULTS.md` §2), the four new
  COVERAGE rows, the `COND.CMP_LENGTHS_POSITIONAL` extension and the labelled SUPERSEDED/
  WIDENED clauses in `spec/COVERAGE.tsv` (133 rows, 0 errors, 0 warnings), and the labelled
  corrections at [C335]/[C337]/[C344]/[C346]/[C348]. Open PROPOSALS (classified `proposed` in
  `LEARNINGS.md`, NOT law): bank the out-of-scope member-pair and negated-TEST refusals as
  NEG-panel rows; "emit the head as ONE bundled thunk in written order" stays a codegen
  invariant evidenced per-shape — no ledger claim until discriminating probes exist; the [C351]
  inv/simpl readings are recorded as BYTE-CONVERGENT (pre-registered non-separability honoured,
  no reading preferred). The stale `README.md` rolling status remains recorded as deferred work
  in `PROGRESS.md` → Pending.## History and pointers

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
  this file. The guard writes the managed block below via Handoff commands only.<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 111
checkpoint-id: g111-8390f09cccc9
checkpoint-kind: auto
content-delta: none
readiness: attested
status: checkpoint (guard level 4, remaining ~4101, session 01a19879-f9d3-704f-a8a8-ce6c10803c9c)
checkpointed: 2026-11-01T19:27:13.882Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 60683014d988badc79801f13c56b6d88bb6d28f2c2060a3b212aaf621c65e2ee
source-handoff: 8a02d240c6d19f739cc2bcbef8bd1e0aaf692cd6a8e13846e4b1c919a104ee53
source-learnings: f6d88d7910a9d8de8d5e20b2df750ed89733ed00e14404087e57be25908465e6
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19879-f9d3-704f-a8a8-ce6c10803c9c
readiness-at: 2026-11-01T19:27:20.513Z
readiness-checkpoint: g111-8390f09cccc9
### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-50/P1 CLOSED (2026-11-02; deliverables `4cad695`, close this commit)

The functional dashboard round is COMPLETE: validation fixes + `spec/functional/programs.tsv`
(68 programs, 3 origin classes never summed) + `tools/functional_dashboard.py` (reads canonical
evidence only, imports the gate module, compiles/runs NOTHING, deterministic, UNKNOWN never
rendered as success) + `tools/test_functional_dashboard.py` (30/30) + generated
`docs/functional-status.md` (views A–E) + the replaced `README.md` status section + the labelled
[E2E-50/P1 CORRECTION(S)] in `LEARNINGS.md`. Evidence-infrastructure audit in `LEARNINGS.md`
2026-11-02. Superseded prose archived byte-verified in
`docs/history/2026-11-02-e50p1-closed.md`.

NO active round exists. A successor session without an operator instruction confirms HEAD and the
tree, runs `/handoff verify`, records state and STOPS. The ranked candidate shortlist for the
operator's E2E-50/P2 choice lives in `docs/functional-status.md` §E (regenerate:
`python3 tools/functional_dashboard.py --check`; `--write` after any ledger change); the measured
boundaries live in `PROGRESS.md` → Blockers and Pending. This is a shortlist, NOT an
authorisation; any round needs the operator's authorization and PROTOCOL pre-registration.

Standing: never run compiler/oracle/gate in infrastructure sessions; never touch the operator's
`handoff.config.json` edit; renewal values ONLY in `handoff.config.json` / `/guard status`;
never `git clean`/`reset --hard`/`add -A`; no push.

### Guard notes
E2E-50/P1 ACTIVE (functional dashboard). HEAD 8385605 committed; tree clean except the operator's unstaged handoff.config.json (never touch/stage/commit/revert it). DONE: evidence-infrastructure audit (in LEARNINGS.md 2026-11-02 sections) + spec/functional/README.md (canonical sources, six stages, three origin classes) + spec/functional/capabilities.tsv (36 capabilities -> COVERAGE row ids + census program names, no status column). TODO in exact order (HANDOFF.md -> Next action item 1 a–g): (a) validate every coverage_rows id against spec/COVERAGE.tsv field 1 and every corpus_programs name against spec/census/corpus-census.json rows and fix misses; (b) write spec/functional/programs.tsv reusing existing sources only; (c) write tools/functional_dashboard.py (read-only inputs, derives stages from INVENTORY + panel_keys.load() + committed census/coverage snapshots + RUNTIME.txt + NEG_META via importing the gate module — NEVER recompile or run the gate; deterministic; --write/--check; UNKNOWN never rendered as success) + tools/test_functional_dashboard.py; (d) generate docs/functional-status.md (views A–E incl. ranked candidate shortlist for E2E-50/P2); (e) replace the stale README.md "Current status (rolling)" section; (f) run the two dashboard checks + coverage_check.py + file_prose_check.py; (g) commit explicit paths then CLOSE (byte-verified archive into docs/history/, HANDOFF/PROGRESS to CLOSED, index row, handoff_finalize, STOP). Prohibited: compiler/oracle/LINK-80/cpmsim/rune-ci/e2e_gate runs, compiler behaviour changes, new oracle campaigns, PLILIB work, starting P2, push, editing handoff.config.json. No PL/I-80 tutorial exists — do not invent one.
<!-- guard:end checkpoint -->
