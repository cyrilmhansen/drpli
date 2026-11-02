# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — FS-01 CLOSED (2026-11-02; first two functional PASSes, Lane B; baseline HEAD `876ed9e`)

FS-01 (operator mission "first two functional PASSes") COMPLETE: TABLE-00 and TABLE-01 **PASS**
on Lane B. F1 fixed in the harness (`tools/functional_runner.py` `_run_lane_b` anchor law —
program's final CRLF retained, prompt never captured, newline-less terminator →
`console-terminator-ambiguous` UNKNOWN fail-closed; hostile suite C15, 12 checks, suite self-count
**194** all pass). F2 isolated by a TABLE-01 **output-statements-only** revision (two ~54-column
labelled lines; algorithm/inputs/invariants unchanged; source sha `4881f187…`; expectation
DERIVED from declared design + README § 6 law, never captured; PLILIB wrap law stays `proposed`).
Executed ACTUALS + evidence roots in `docs/functional-results.md` § 5 and `HANDOFF.md`;
baseline FAIL reproduction, PASS run, `--double-run` (byte-equal) and Lane-A unchanged check
(FX-00 PASS / FX-01 FAIL `emulator`) under `build/functional/fs01*` (ignored).
P2 FAIL evidence preserved; no compiler/golden/ledger/COVERAGE/`ocaml/` byte touched.
**No active round**: a successor without an operator instruction confirms HEAD/tree,
`/handoff verify`, records state and STOPS. Open items = `docs/functional-results.md` § 3/§ 5 +
`spec/lab-evidence/e2e50-p2/REPORT.md` § 5 (P3-b law declaration, P3-c BDOS-25/license, P3-d
TABLE-02 remain PROPOSALS; P3-a DONE by FS-01). Operator `handoff.config.json` edit stays
unstaged; no push.
## Previous phase — E2E-50/P2 CLOSED (2026-11-02; functional-testing foundation + emulator/redistribution audit; FULL compile-tier gate rc=0 measured at `545dcf1`, recorded `d648bcd`; CLOSE completed by a docs-only session)

Round COMPLETE. Mission, the durable step sequence 0–8 and every hop record (incl. the
falsified-prediction text kept per PROTOCOL #2) are archived VERBATIM and byte-verified —
**23/23 blocks BYTE-EXACT**, completeness sweep over all 8 Next-action / 7 Unfinished /
8 Current-phase / 2 Next-action-stub generations: 0 unarchived lines — in
`docs/history/2026-11-02-e50p2-closed.md`. Last verified state, landing chain and executed
verdicts (FX-00 PASS + determinism; FX-01 FAIL/`emulator` intended; TABLE-00/01 first
functional execution of a DRPLi-compiled program, CONTENT ≡ REFERENCE, ASSERT FAILs framing
F1/F2 attr=`undefined`; census BDOS-25 free-core blocker measured) live in `HANDOFF.md` →
Last verified state; round report `spec/lab-evidence/e2e50-p2/REPORT.md`. No scientific byte,
claim, COVERAGE row, INVENTORY/RUNTIME/census entry or golden changed; `ocaml/` untouched.
**No active round**: a successor without an operator instruction confirms HEAD/tree,
`/handoff verify`, records state and STOPS. P3 shortlist `spec/lab-evidence/e2e50-p2/REPORT.md`
§5 — never an authorisation. Operator `handoff.config.json` edit stays unstaged; no push.
## Previous phase — E2E-50/P1 CLOSED (2026-11-02; deliverables `4cad695`; close docs-only)

Functional dashboard round COMPLETE, docs-only and evidence-only: compiler, oracle, LINK-80,
cpmsim, Rune CI and the gate were NEVER RUN this round; no ocaml/golden/ledger/COVERAGE/INVENTORY/
census byte changed. Landed at `4cad695`: taxonomy validation fixes (4 typed misses; 30 capability
rows; every cited id/name now re-validated on EVERY dashboard run), `spec/functional/programs.tsv`
(44 HISTORICAL/16 FOCUSED/8 MICROPROBE), `tools/functional_dashboard.py` + 30-check test suite,
generated `docs/functional-status.md` (views A–E), `README.md` rolling-status replacement,
labelled [E2E-50/P1 CORRECTION(S)] in `LEARNINGS.md`. Checks measured at `4cad695`: tests rc=0,
dashboard `--check` rc=0, `coverage_check.py` rc=0 (133 rows 0/0), `file_prose_check.py` rc=0
(5 active clean). Superseded prose archived byte-verified in `docs/history/2026-11-02-e50p1-closed.md`.
**No active round**: successor confirms HEAD/tree, `/handoff verify`, records state, STOPS. The
E2E-50/P2 candidate pool is the §E shortlist in `docs/functional-status.md` (a shortlist, never an
authorisation). Operator `handoff.config.json` edit stays unstaged; no push.

## Earlier phase — E2E-49/P4 CLOSED (FULL compile-tier gate rc=0 measured by the step-6 session at HEAD `5b0ccde`, recorded `882f77c`; CLOSE completed by the docs-only closing session — ledger C348..C351, byte panel 1174, coverage 133 rows)

- Round (OPERATOR-authorized 2026-11-01; PLAN committed at bootstrap `bc6ee4f`): composite
  FIXED/TEST bank — ordered relations with a LITERAL (panel G, E49G1..G8), BARE spellings in
  ordered relations (panel H, E49H1..H6), the unequal-extent relation matrix (panel I,
  E49I1..I6), negated compares (panel J, E49J1..J4); shared P3 DECL + tail so the [C309] fills
  and [C314] frames stay comparable. Pre-registration `328eb3f` committed BEFORE any oracle call
  (24 probes CRLF+`^Z` ≤71 cols + mkprobes.py + HYPOTHESES + BASELINE-MINE with the ACTUAL
  binary at `398fa2c`: panels A/B/D refused rc=2 BY NAME — the code-reading predictions held —
  and panel C accepted); **NO separate fill-in commit in this round** (P3 had `0a46824`); ONE
  grouped batch run, tag `e49p4`, **24 ok / 24 — NO dr-refuses** (18 `my-gap` G/H/J, 6 already
  byte-exact I); goldens + `spec/lab-evidence/e2e49-p4/RESULTS.md` `13fca5b`; traceable wording
  repair `9799f1d`.
- Arms (each committed ALONE, new goldens whole-file BYTE-EXACT, out-of-scope refusals rc=2,
  FULL gate rc=0 at each — panel 1150 then, e49p4 unregistered): a `c515377` (`str_cmp_shape_fix_rel`
  widened to `ImemFb` on BOTH sides; H1..H6; no prescan twin); b `ec904c1` (NEW
  `str_cmp_shape_fix_lit_rel` — LITERAL vs the QUALIFIED `ImemF`, both written orientations; the
  ORDER law REKEYS the template on the FIRST LOWERED operand, staged `EB` vs the SIX-byte direct
  `11` head measured; positional immediates + the [C342] collapse; JNC `d2`/JC `da`; G1..G8; the
  inherited "prescan DEMAND twins MUST widen in the same commit" note FALSIFIED, [C152]
  verified); c `47c2194` (NegL admits ONLY the four goldened rewrites `^(=)`→`^=`,
  `^(<)`→`>=`, `^(<=)`→`>` by ONE recursion on the synthesized complement — ZERO new bytes; the
  inherited `Gt->Le` instruction FALSIFIED, no golden exists for `^(>)`, `^(>=)`, `^( ^= )`).
  Regression sweep at arm c: 47/47 BYTE-EXACT (A,B,C,D,E,F,G,H,I).
- Step 6: part 1 `aec53e1` (claims **C348..C351** from RESULTS §2 ONLY; ledger ENDS at **C351**);
  part 1b `9c42f3b` (FOUR labelled [E2E-49/P4 CORRECTION(S)] blocks at [C335]/[C337]/[C344]/
  [C346], falsified sentences quoted verbatim); docs `19ab4e0`/`e13311c`; registration `cc43963`
  (SPECIMENS +24 round bank; sanctioned `--update-inventory` panel 1150 → **1174**; census
  re-snapshot counts UNCHANGED 15/0/26/0, metadata only); part 2a `dbaf004` (four COVERAGE rows
  RELATION_LITERAL / RELATION_QUALIFICATION / RELATION_UNEQUAL_MATRIX / CMP_NEGATED_COMPLEMENT;
  **133 rows 0/0**; stats re-snapshotted); part 2b `5aeac87` (`COND.CMP_LENGTHS_POSITIONAL`
  EXTENDED to EXACT:14 + four labelled SUPERSEDED/WIDENED clauses, all five quotes byte-checked
  vs the pre-edit blob `cc43963`, ORDER law cited **[C104]**, never legacy [C027]/[C072]); part
  2c `5b0ccde` (labelled WORDING CORRECTION at [C348] — "ALL FOUR relations" contradicted its own
  `<`/`>=` enumeration; equal-attribute `>` NEVER sampled; RESULTS §2.1 carries the same slip and
  stands as written, [C342] COUNT NOTE precedent). TRACEABLE SLIP (PROTOCOL #2, `9799f1d`
  precedent): part 2b's ORIGINAL message `55053bd` (amended to `5aeac87` before anything
  referenced it) also overstated `<=` as never sampled — E49F3 collapses at 3/3 stacked
  ([C346]); the committed row text and the [C348] correction govern.
- FULL compile-tier gate at `5b0ccde` rc=0, ACTUALS as printed: byte panel **1174 byte-exact /
  0 fail of 1174** (all twenty-four e49p4 specimens whole-file BYTE-EXACT at 256 bytes), negative
  **181/181** (E46K14 `[dr-refuses]`, pinned marker UNMOVED), divergence **9/9**, coverage
  **133 rows, 0 errors, 0 warnings**, census **15/0/26/0**, prose **5 active files clean**.
  `dune build` rc=0. BYTE TIER ONLY — no `spec/RUNTIME.txt` row came or comes from this round.
  MEASURED GATE DESIGN: the gate prints coverage/census/prose, then the INVENTORY integrity check
  ABORTS rc=2 BEFORE the byte panel while SPECIMENS leads INVENTORY.txt — the byte-panel ACTUAL
  always comes from the post-`--update-inventory` run (the P3 `4b51bc0` cycle, now understood).
- CLOSE (docs-only session, operator authorization 2026-11-01): superseded prose archived
  byte-verified — **16/16 blocks BYTE-EXACT** against their stated git ranges (`19ab4e0`,
  `e13311c`, `882f77c`, `5c52bba`) — in `docs/history/2026-11-01-e49p4-closed.md`, FOUR HANDOFF
  generations (the planned "two" measured as four by section hashing) plus the PROGRESS
  close-era STATUS stack, both superseded Current-phase headings, the surviving P2 CLOSED
  previous-phase record, the STALE bootstrap-era next-action stub, the P3-frozen Verified
  evidence and the P3-era Blockers; HANDOFF/PROGRESS rewritten to CLOSED; LEARNINGS close notes;
  `docs/history/README.md` index row added. NEXT: NO active round — a successor session without
  an operator instruction confirms HEAD and tree, runs `/handoff verify`, records state and
  STOPS; candidate pool in `HANDOFF.md` → Next action. No push; no P5; operator
  `handoff.config.json` edit stays unstaged.

## Next action

The ONE active spec lives in `HANDOFF.md` -> its single level-2 Next-action heading: **NO
ACTIVE ROUND** (FS-01 CLOSED 2026-11-02; prior E2E-50/P2 CLOSED same day). A successor without
an operator instruction confirms HEAD/tree, runs `/handoff verify`, records state and STOPS.
PROGRESS does not restate it (PROTOCOL: handoff docs point at claims/specs, never duplicate
authority).
## Verified milestones (provenance: `docs/history/README.md`; evidence: `spec/lab-evidence/`)

- E2E-48/P1 — 24/24 probes byte-identical + registered, claims C309–C316, gate 1098/0: `992ccad`.
- E2E-48/P2c CLOSED — arms `14c7321`…`e21281a` era, RETIRE promotions, claims C317–C320,
  FULL GATE 1109/0 negative 182/182: `f67cc6d`; COVERAGE rows + appends: `ef0a198`.
- E2E-48/P2d — run 1 botched (>72-col comments; kept `67bf83c`), wrap `60a2c06`, run 2 10/10
  `d28ff5e`; claims C321–C326 `aa4b5b4`; six arms `6545b5d`/`6491981`/`a72ce43`/`18a06c0`/
  `1e8acb2`/`e21281a`; registration + FULL GATE 1120/0, negative 181/181, census 15/0/26/0,
  INVENTORY 1301: `adbfa2a`; COVERAGE 113 rows 0 errors: `218b474`.
- E2E-48/P2e round 5 — pre-registration `421656a` committed BEFORE the oracle; one run
  7 ok / 8 (E48E6 `BIT REQ` = dr-refuses; P-E6 MISS kept in RESULTS §1); goldens + RESULTS
  `e2b77ba`; lowering arms 1–3 `d18c6ab`/`bab0d16`/`e49902a` (arm-3 spec archived in
  `docs/history/2026-10-31-p2e-arm3-closed.md`).
- E2E-48/P2e CLOSED — arm 4 `046046a`, arm 5 `c215ea0`, step 6 `809af8d`+`0e64c8b`, docs
  `0749fa6`; claims C327–C332, inventory 1127, coverage 118 rows 0 errors; FULL compile-tier
  GATE rc=0 ACTUAL 1127/0 (neg 181/181, div 9/9, census 15/0/26/0, prose clean) measured at
  `0749fa6` 2026-10-31; closing prose archived in `docs/history/2026-10-31-p2e-closed.md`.
- E2E-49/P1 CLOSED — operand-inverted FIXED compares (member LEFT of literal): pre-registration
  `9b3d860` before the oracle; run 4 ok/4; arms `fee935e`/`b044b7c`; claims C333–C336 + labelled
  C330 CORRECTION; registration panel 1131, coverage 122 rows; FULL GATE rc=0 1131/0 (neg 181/181,
  div 9/9, cov 122/0/0, census 15/0/26/0, prose clean) measured at `0a8ceff`; archive
  `docs/history/2026-11-01-e49p1-closed.md`.
- E2E-49/P2 CLOSED — member-vs-member FIXED TEST compares: pre-registration `3bd9417` before the
  oracle; run 5 ok/5; arm 1 `b1e9221` (stacked parking + equal-extent collapse); claims C337–C341;
  registration panel 1136, coverage 125 rows 0 errors (`0abf1c1`/`8c1d2ee`/`d5983e8`); FULL GATE
  rc=0 **1136/0** (neg 181/181, div 9/9, cov 125/0/0, census 15/0/26/0, prose clean) measured at
  `d5983e8`; archive `docs/history/2026-11-01-e49p2-closed.md`.
- E2E-49/P3 CLOSED — composite FIXED/TEST bank (equal-attribute collapse in BOTH literal
  templates, qualification invisible, over-extent literal-LEFT, ordered relations):
  pre-registration `3659f5d` before the oracle; run 14 ok/14, NO dr-refuses; arms
  `a540fa7`/`0a1b80c`/`cde3258`; claims C342–C347 + labelled corrections at C335–C338 and
  the citation fix at C346 (`4df35bb`); registration panel 1150, coverage 129 rows 0 errors
  0 warnings (`4b51bc0`/`8d3b024`/`8771e1e`); FULL GATE rc=0 **1150/0** (neg 181/181,
  div 9/9, cov 129/0/0, census 15/0/26/0, prose clean) measured at `4df35bb`, recorded
  `1f611f5`; two-generation archive `docs/history/2026-11-01-e49p3-closed.md`.

- E2E-49/P4 CLOSED — composite FIXED/TEST bank (ordered relations with a LITERAL on BOTH `?SCCCM` literal templates with the ORDER-law rekey, qualification invisibility transferred, the complete unequal-extent relation matrix NO-ARM, `^( )` on the complement object):
  pre-registration `328eb3f` before the oracle (BASELINE-MINE binary `398fa2c`); run 24 ok/24, NO dr-refuses (18 my-gap, 6 exact); arms `c515377`/`ec904c1`/`47c2194`; claims C348–C351 +
  labelled corrections at C335/C337/C344/C346 (`9c42f3b`) and the WORDING correction at C348 (`5b0ccde`); registration panel 1174, coverage 133 rows 0 errors 0 warnings
  (`cc43963`/`dbaf004`/`5aeac87`); FULL GATE rc=0 **1174/0** (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean) measured at `5b0ccde`, recorded `882f77c`;
  four-generation archive `docs/history/2026-11-01-e49p4-closed.md`.


- E2E-50/P1 CLOSED — functional dashboard (evidence-infrastructure audit; capability taxonomy 30 rows validated; 68-program inventory in 3 origin classes; deterministic read-only dashboard + 30 tests; generated docs/functional-status.md views A–E incl. ranked §E candidate shortlist; stale README rolling status replaced; labelled LEARNINGS corrections incl. RUNTIME 71-names falsification). Deliverables `4cad695`; no compiler/oracle/gate run; no scientific byte.

## Completed

*Scientific — recorded, not re-run by this session:*
- `PUT FILE … SKIP` behaviour measured on DR and lowered byte-exactly: `E46N11`–`E46N22`
  bank, 18 specimens added → **1074 byte-exact / 0 fail** recorded in
  `spec/lab-evidence/e2e42-p2c/RESULTS.md` §8; runtime panel 71/71 as recorded.
- Gate tiering + `--link-run` able to fail; slow CP/M arms delegated to the external
  `rune-ci` builders (`GATE-TIERS.md`, `spec/notes/rune-ci-external-gate.md`).
- The `timeout-or-hang` collapse in `oracle/run.py`/`linkrun.py` re-measured by exit code:
  51 timeouts, 2 emulator deaths (`PD7`, `PD9`), 2 that do terminate (`RFACT`, `V5`) —
  `[C308]`, and the `HANG_ARMS` / `NO_RUN_ARMS` / `NO_LINK_ARMS` split in `tools/e2e_gate.py`.

*Infrastructure — performed and verified by this session (see `HANDOFF.md` for the boundary):*
- `.gitignore`: appended only the `# Pi Handoff runtime state` / `.pi-guard/` rule; all
  pre-existing oracle/golden/build/thirdparty rules verified still matching.
- Extension installed at `.pi/extensions/context-guard/{index,core,config,checkpoint,renewal}.ts`,
  taken from the pinned Git revision (bytes verified by SHA-256 and blob id against
  `v0.1.0-dev.1` / `2ea6219`); nothing else from the source repo was copied.
- Skill installed at `.agents/skills/pi-handoff/{SKILL.md,references/bootstrap.md,references/commands.md}`.
- `handoff.config.json` written: `readOnly: true` during validation, `enforceClosing: false`,
  `autoCheckpointAtHandoffLevel: false`, renewal disabled, `generationReserve: 20000`
  (initial policy value, not yet tuned).
- Durable files created: `AGENTS.md`, `GOAL.md`, `PROTOCOL.md`, `HANDOFF.md`, `PROGRESS.md`,
  `LEARNINGS.md`.
- **Phase D (read-only) passed in the real Pi runtime**: extension loaded with no import/TS
  errors; `/guard status` reported read-only mode + the real model/window/reserve; `/handoff
  verify` reported `missing` without writing; `/handoff ready check` evaluated without
  attesting; `/guard simulate 30000` → level 1, `/guard simulate 10000` → level 3 with **no**
  checkpoint written; `/handoff` reported a dry run; no `.pi-guard/` directory was created; every
  tracked file hash, the ignored-file count (471 102) and the profile settings were unchanged.
- **Phase E (writable) passed**: `/handoff` → `g1-01ad31c23339`, generation 1,
  content-delta `initial`, freshness `current`; `/handoff ready check` → READY with four blocking
  PASSes; `/handoff ready` → attested; both blocks shared one transactional identity.
  A level-3 automatic checkpoint (`checkpoint-kind: auto`) then preserved a substantive
  "Last verified state" line and a "Guard notes" block **verbatim**, leaving all manual prose
  outside the managed blocks byte-identical, and left `GOAL.md`/`LEARNINGS.md` untouched.


## Pending
- **LOAN2's new prescan my-gap** (`variable i declared with conflicting kinds; decimal pool prescan
  needs one unambiguous type map [TBD]`): measured cause, fix NOT attempted. `codegen.ml:12460-12490`
  builds ONE global `pd_vars` name -> vkind map for the DEC-pool prescan, and LOAN2 declares `i`
  `fixed decimal(4,2)` at line 32 and `fixed bin` at line 211 — two scopes, both legal, DR accepts
  (its golden exists). Making the prescan scope-aware touches ~15 `List.assoc_opt … cx.pd_vars`
  call sites whose prescan deliberately runs WITHOUT statement context, so it is a design change,
  not an arm. It needs its own measured plan; do not start it on faith.
- CREATE remains NOT byte-exact; its measured blocker is still the front-end `%include` gap
  (`pli80c.ml` never expands INCLUDE). Do NOT implement any unmeasured shape from the
  [TBD] list in RESULTS section 3.
- **Renewal chain:** the E2E-48 phase chain closed at its configured cap; its state file is
  archived under `.pi-guard/archives/` and a new session starts a fresh count per
  `handoff.config.json` — the config and `/guard status` are authoritative for enablement,
  autoRenew and cap; this file quotes no numbers.

## Verified evidence

The FULL compile-tier gate rc=0 at HEAD `545dcf1` with ACTUALS AS PRINTED (byte panel 1174
byte-exact / 0 fail of 1174; negative 181/181, E46K14 `[dr-refuses]` UNMOVED; divergence 9/9;
coverage 133/0/0; census 15/0/26/0 UNCHANGED; prose 5 active clean) was MEASURED by the
step-8 session and recorded at `d648bcd` — NOT re-run by this docs-only close (the mission
required no compiler/oracle/gate/emulator run to close). Measured by THIS closing session
(2026-11-02): HEAD `e7664ed`, tree clean apart from the operator's `handoff.config.json`
edit; checkpoint g131 **current** via replay of the guard's strip+rstrip SHA-256 prose law;
the 23 close-archive blocks re-extracted from `459f51e`/`a6163ef`/`149c6e2`/`690c3a1`/
`218c9be`/`ec9d396`/`545dcf1`/`d648bcd`/`68831ff`/HEAD and byte-compared — **23/23
BYTE-EXACT**; every line lost by any superseded generation verified present verbatim in the
archive. Round evidence: `spec/lab-evidence/e2e50-p2/{PLAN.md,step6/RESULTS.md,
step7/RESULTS.md,REPORT.md}`, `spec/functional/tests/`, ignored evidence roots under
`build/functional/`; earlier rounds `spec/lab-evidence/e2e48-*/`, `e2e49-p*/`; closed-round
records: `docs/history/`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 134
checkpoint-id: g134-8670cffbd6b1
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 2
checkpointed: 2026-11-02T05:42:58.426Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: d51d63a0ccb3c98a63290ac3f66f520f2b2f8aaa80de8111d6c59dbc6ebe433e
source-handoff: c41743fc2bf4e0c95cf1a50c8b0fb11b2b01c492aeaa132861397704a65af895
source-learnings: 677fdf0d532d7f117a8e57f4d064b678784e0ce82c2ab34b5e022669873d0362
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: ` below. TABLE-00 and
  TABLE-01 executed to **PASS** on Lane B after (a) the harness F1 anchor fix in `tools/functional_runner.py`
  (`_run_lane_b`: capture now ends at `D>`/`I/O ran`/`\Z` WITHOUT eating the program's final CRLF;
  a region not newline-terminated before its terminator is `console-terminator-ambiguous` UNKNOWN,
  fail closed) with hostile-suite case C15 (12 checks; suite self-count **194**, all pass), and
  (b) a TABLE-01 **output-statements-only** revision isolating the test from PLILIB's measured
  79-col wrap (source sha256 `4881f187ef1ad9651c48950b76a6cdd959fdcc980ef989580a0fbfa43c0b0863`,
  1366 B, CRLF/^Z/≤71 cols; algorithm/inputs/invariants unchanged; expectation derived from the
  declared design + README § 6 law via `reference.py:table01`, never captured). Executed ACTUALS:
  TABLE-00 .REL 896 B, COM 7552 B, 93 console bytes, complete-stream 2 lines; TABLE-01 .REL 1536 B
  (code=644 data=50), COM 7808 B, 178 console bytes, 3 lines; LINK both `parse_undefined=[]`;
  RUN `done` witness; `--double-run` captures byte-equal. Evidence roots (ignored working state,
  gitignored `build/`): baseline FAIL reproduction `build/functional/fs01-baseline/`, PASS run
  `build/functional/fs01/`, double-run `build/functional/fs01-double/`, Lane-A unchanged check
  `build/functional/fs01-laneA/` (FX-00 PASS, FX-01 FAIL `emulator` intended). Report:
  `docs/functional-results.md` § 5.
- Preserved/untouched: P2 FAIL evidence `spec/lab-evidence/e2e50-p2/step6/RESULTS.md`; all
  goldens, `artefacts/`, `oracle/disks/`, manuals, `ocaml/`, `spec/CLAIMS.md` (ledger ENDS C351),
  `spec/COVERAGE.tsv`; PLILIB wrap law stays `proposed` (NOT characterized — FS-01 boundary).
  Compiler binary used as-built: `pli80c.exe` sha256 `edce9e0e…` (recorded in every PASS record).
- Prior round: E2E-50/P2 CLOSED `876ed9e` (gate ACTUALS 1174/0, 181/181, 9/9, 133/0/0, census
  15/0/26/0, prose 5 clean recorded `d648bcd`; close archive `docs/history/2026-11-02-e50p2-closed.md`).
readiness-by: session:01a19ab0-a226-737d-a44a-126b617c91da
readiness-at: 2026-11-02T05:42:58.429Z
readiness-checkpoint: g134-8670cffbd6b1
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P4 RESULTS §3 remainders (with the surviving P1/P2/P3/P2e §3 entries) stay named
  refusals until a pre-registered round measures them: NO runtime semantics for `?SCCCM`
  (what it returns and how JNC/JC/JZ read it is NOT claimed — byte tier, no `spec/RUNTIME.txt`
  row may come from these families); STORE value or STORE target with any of the new shapes
  (relation-with-literal, bare-in-relation, negated compare); literal-vs-literal in any
  relation; BASED members in a condition; fixed-member truthiness; `<>`/`><` spellings; `&`/`|`
  composition of conditions; `^( )` over a relation WITH A LITERAL operand; `^( )` over an
  over-extent or a BARE spelling; `^(` `^=` `)` double negation; ordered relations with a
  literal at UNEQUAL attributes beyond the G3..G6 `>`/`<=` sample; bare spellings in the
  equal-length literal template under a relation (only bare `=` is measured, E49D4); the
  equal-attribute `>` collapse inside a relation (NEVER sampled in any bank — the [C348]
  WORDING CORRECTION); `^=` over a ladder; over-extent in INITIAL/STORE; bare `-0` spelling;
  runtime length rewrite; empty-varying PUT output; PUT EDIT of a bit item.
  Shapes REMOVED from this list by P4 MEASUREMENT: ordered relations with a LITERAL operand on
  BOTH literal templates ([C348]); BARE spellings inside an ORDERED relation, member-pair mixes
  included ([C349], extending [C344]); the unequal-extent STRICT-vs-WEAK combinations "beyond
  F2/F4's single pair" — the COMPLETE 4x2 matrix is measured, no arm ([C350]); `^( ... )`
  composition over the four goldened compare shapes ([C351], the un-witnessed negations above
  keep refusing) — the P3-era wording is preserved verbatim in
  `docs/history/2026-11-01-e49p4-closed.md`.
- E2E-50/P2 functional axis (measured, recorded; no byte-tier effect): Lane-B ASSERT framing
  F1 (harness anchor law — P3-a proposal) and F2 (DR PLILIB 79-col print-wrap — declare from
  the oracle side before any expectation change, P3-b); the free core cannot host PLILIB
  programs (BDOS 25 first call, measured; full census UNMEASURED); Package-A licensing =
  operator decision. Details `spec/lab-evidence/e2e50-p2/REPORT.md` §2/§4/§5.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).

- E2E-50/P2 CLOSED — functional-testing foundation + emulator/redistribution audit: audits
  `docs/emulator-audit.md`/`docs/functional-testing.md`/`docs/functional-results.md`; schema
  `pli80-functional/1` + TABLE-00/01 + FX-00/01 + `reference.py` under `spec/functional/tests/`;
  harness `tools/functional_runner.py` + hostile suite 182 checks self-counting; executed
  verdicts FX-00 PASS, FX-01 FAIL/`emulator` (intended), TABLE-00/01 first functional execution
  of a DRPLi-compiled program (CONTENT ≡ REFERENCE; ASSERT FAILs framing F1/F2, attr
  `undefined`); census BDOS-25 free-core blocker measured. Deliverables `d648bcd` (+`68831ff`);
  FULL GATE rc=0 1174/0 (neg 181/181, div 9/9, cov 133/0/0, census 15/0/26/0, prose clean)
  measured at `545dcf1`, recorded `d648bcd`; 23-block byte-verified close archive
  `docs/history/2026-11-02-e50p2-closed.md`.
