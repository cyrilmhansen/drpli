# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-50/P2 ACTIVE (operator mission brief 2026-11-02; functional-testing foundation + emulator/redistribution audit)

Mission, the durable step sequence 0–8 and the prohibitions live ONLY in `HANDOFF.md` → Next
action (single operational authority). Step 0 (documentary bootstrap) lands with this commit:
measured and fixed at HEAD `942aa78` — PROGRESS `## Next action` still declaring P1 ACTIVE
(stale: P1 is CLOSED at `4cad695`/`4eb6582`, checkpoint g111 verified current + attested this
session by prose-hash replay of the guard's own strip+sha256 law); the stale HANDOFF sentence
recording the README rolling status as deferred work (P1 replaced it; no README item exists in
Pending); three blankless headings in PROGRESS, three inline glued headings in HANDOFF
(incl. `golden/e49p4.## Next action`) and one glued guard-marker line (the only residual
blankless heading, `### Last verified state`, is INSIDE the guard's own rendering — never
hand-edited). `4eb6582`'s assertion that the `## Discoveries` pair "does NOT
exist in the manual region" is FALSIFIED by byte read of HEAD and corrected with the falsified
text quoted (PROTOCOL #2). No scientific claim, golden, ledger or `ocaml/` byte touched. The
emulator audit target is confirmed: `/home/john/pli/lab` (Runes `pli80_lab` dune project —
`lib/i8080`, `lib/cpm`, `lib/runner`, `lib/trace`), READ-ONLY this round.

Step 1 reconnaissance DONE: lab identity/shape, BDOS coverage, decoder status, license evidence
and the lab's own suite RE-RUN (7 executables rc=0 incl. 976,272-case alu_flags) are recorded
accepted in `LEARNINGS.md` § 2026-11-02; `docs/emulator-audit.md` (steps 1–2 deliverable) owed.
Boundary facts: lab HEAD `43e38ba`, single-author git history, NO LICENSE file (operator decision,
never added here); building tests writes only the lab's gitignored `_build/`.

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

The ONE active spec lives in `HANDOFF.md` -> its single level-2 Next-action heading: **E2E-50/P2
is ACTIVE; step 0 (documentary bootstrap) lands with this commit, steps 1–8 owed** (emulator
technical + redistribution audit, functional-test spec format, TABLE corpus with independent
expectations, harness with typed verdicts, Lane A/B execution evidence, minimal results
reporting, close report + bounded P3 proposal). No competing action exists anywhere else;
PROGRESS does not restate it
(PROTOCOL: handoff docs point at claims/specs, never duplicate authority).

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

The FULL compile-tier gate rc=0 at HEAD `5b0ccde` with ACTUALS AS PRINTED (byte panel 1174
byte-exact / 0 fail of 1174 incl. all twenty-four e49p4 specimens whole-file at 256 bytes;
negative 181/181 with the E46K14 `[dr-refuses]` pinned marker UNMOVED; divergence 9/9;
coverage 133 rows 0 errors 0 warnings; census EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0;
prose 5 active files clean; `dune build` rc=0) was MEASURED by the step-6 session and recorded
at `882f77c` — NOT re-run since and not re-runnable in a docs-only session; no scientific byte
changed after `5b0ccde` (`ocaml/` untouched since arm c `47c2194`; goldens complete since
`13fca5b`). Measured by THIS closing session (docs-only, 2026-11-01): git HEAD `b5f792c` with a
clean tree apart from the operator's `handoff.config.json` edit; the `5c52bba` prose == the HEAD
prose in BOTH `HANDOFF.md` and `PROGRESS.md` (only the guard managed blocks differ); the sixteen
archive blocks re-extracted and byte-compared to their stated git ranges at
`19ab4e0`/`e13311c`/`882f77c`/`5c52bba` — ALL BYTE-EXACT (16/16, independent re-read of the
written archive); each cross-generation identity claim in the annotations computed by SHA-256
over the extracted sections, and both superseded PROGRESS Current-phase bodies verified as
line-for-line subsets of the close-era block. Per-arm ACTUALS (whole-file `cmp` at each arm, the
47/47 sweep, the out-of-scope refusals rc=2) stand in git log and dated `LEARNINGS.md` sections.
Round evidence: `golden/e49p4/`,
`spec/lab-evidence/e2e49-p4/{RESULTS,HYPOTHESES,BASELINE-MINE,mkprobes.py,PLAN}`; earlier rounds
`spec/lab-evidence/e2e49-p{1,2,3}/` and `spec/lab-evidence/e2e48-*/`; closed-round records:
`docs/history/`.
<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 113
checkpoint-id: g113-4308f1e44641
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 2
checkpointed: 2026-11-01T21:52:25.453Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: dd064a4a956f3460f0c49ce7926d123b3e45acc281d1443aaab7979b127cd515
source-handoff: e66309a9cf512a761432a865891b8fe41d95014873cbf48f34ffb5f203fb71ed
source-learnings: 4ceba92bb908cf025c644c39bbedd42fed21c15905a6c540f29b67602225efd6
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: — E2E-50/P2 ACTIVE (operator mission brief, bootstrapped 2026-11-02)

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
readiness-by: session:01a19902-5793-7280-b553-bda51e005404
readiness-at: 2026-11-01T21:52:25.456Z
readiness-checkpoint: g113-4308f1e44641
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
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).