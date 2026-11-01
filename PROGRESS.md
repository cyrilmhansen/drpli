# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-49/P4 IN FLIGHT: ARMS a/b/c ALL LANDED; step 6 IN PROGRESS (claims committed; registration/inventory/census/COVERAGE/FULL-gate + CLOSE owed)

- STATUS 2026-11-01 (renewal-3 session, accepted): **ALL THREE ARMS LANDED, each ALONE with
  whole-file goldens + sweep + out-of-scope rc=2 + FULL gate rc=0**: arm a `c515377` (rel arm
  widened to ImemFb BOTH sides; H1..H6 exact; sweep 29/29; gate 1150/0). Arm b `ec904c1`
  (`str_cmp_shape_fix_lit_rel`: QUALIFIED ImemF vs LITERAL ONLY, template keyed on FIRST LOWERED
  operand staged-EB/direct-11, positional pair + [C342] collapse, d2/da, SIX-byte direct head —
  LXI D carries the *D(pool) operand itself; G1..G8 BYTE-EXACT; sweep A..I 35/35 (43/43 incl. G);
  out-of-scope rc=2 J1..J4 + scratch bare+literal-rel + lit-lit-rel + rel-in-STORE; FULL gate
  rc=0 1150/0, neg 181/181 E46K14 UNMOVED, cov 129/0/0, census 15/0/26/0). Arm c `47c2194`
  (NegL arm admits ONLY the four goldened rewrites ^(Eq)->Ne [mm pair = J1, literal-LEFT
  qualified right len<=cap = J3], ^(Lt)->Ge mm = J2, ^(Le)->Gt mm = J4 — NO ^(Gt)/^(Ge)/^(Ne)
  [no golden; predecessor "Gt->Le" entry FALSIFIED as instruction, PROTOCOL #4]; lowering is ONE
  recursion on the synthesized complement expr, lower_test_skip0 now `let rec`, ZERO new bytes;
  prescan UNTOUCHED — Eprefix descends, literal-LEFT twin already demands J3's cell; J1..J4
  BYTE-EXACT CODE 66/66/64/67 per RESULTS; sweep 47/47 incl. G,H,I; 9 scratch negations refused
  rc=2 by name; FULL gate rc=0 1150/0, neg 181/181, div 9/9, cov 129/0/0, census 15/0/26/0,
  prose clean). MEASURED at arm b: FALSIFIED inherited note "prescan DEMAND twins MUST widen in
  the same commit" — `wants` keyed on `EqR _`, twins already mirror; [C152] verified.
  **STEP 6 OPENED**: part 1 `aec53e1` — claims **C348..C351** appended from RESULTS s2 ONLY,
  ledger now ENDS at **C351** (C348 rel+literal rekey; C349 canonicality/qualification-invis
  transfer; C350 I-matrix no-arm transfer incl. I5==I6; C351 ^( )=complement object, inv/simpl
  NON-SEPARABILITY honored — claim prefers no reading).
  OWED (step 6 parts 2..): SPECIMENS +24 (G1..G8,H1..H6,I1..I6,J1..J4) round-bank block in
  tools/e2e_gate.py (panel expected 1150+24=1174 — the ACTUAL printed number governs); sanctioned
  `python3 tools/e2e_gate.py --update-inventory`; census re-snapshot per the 4b51bc0 recipe
  (counts UNLESS changed); COVERAGE rows (byte tier; widenings with labelled SUPERSEDED clauses,
  quotes byte-checked vs the pre-edit blob, cite [C104] never legacy); FULL gate rc=0 with
  ACTUALS AS PRINTED; then CLOSE per PLAN s6: byte-verified archive of superseded prose vs stated
  git ranges, HANDOFF/PROGRESS/LEARNINGS rewritten, docs/history/README.md index row, ONE active
  Next action, handoff_finalize, STOP. NEVER push; no P5. Old bullets below are the run-era record;
  superseded wording above the STATUS line stands as history per PROTOCOL #2 (archive at CLOSE).

- ACCEPTED (measured this session): pre-registration `328eb3f` (24 probes CRLF+^Z
  <=71col verified; BASELINE-MINE with the ACTUAL binary at 398fa2c: A/B/D all refuse
  rc=2 by name, C accepts on arm-c bytes; HYPOTHESES per-row) committed BEFORE any
  oracle call. ONE grouped run tag e49p4 -> 24 ok/24, NO dr-refuses, all PRN clean
  both passes. Goldens+RESULTS `13fca5b`, wording repair `9799f1d`. Verdicts (every
  row HIT; falsified alternatives recorded): **Panel A** H-A-sw CONFIRMED, H-A-or
  FALSIFIED at G3..G6 (ORDER law rekeys the literal template: lowered member-first
  = staged EB / literal-first = direct 11; positional immediates + [C342] collapse on
  LOWERED operands; BRANCH d2/da; [C345] over-extent pooled WHOLE). **Panel B**
  H-B-invis CONFIRMED (bare mixes == qualified twins byte-for-byte but packed name
  bytes offsets 4..6/18..19/26..28; H4 == golden F3: the LOWERED pair is canonical).
  **Panel C** whole-file cmp ZERO differing bytes vs my arm-c baseline -> NO ARM
  (transfer measured; I5==I6 but names). **Panel D** DR ACCEPTS `^( )` on string
  heads; each object == the complement's object byte-equal (J1≡B5, J3≡C4, J4≡F2,
  J2≡F1-head+skip da); H-D-inv/H-D-simpl BYTE-CONVERGENT (non-separable, stated);
  H-D-extra FALSIFIED. Classification: 18 my-gap (G,H,J), 6 exact (I), 0 dr-refuses.
- NEXT ACTION (step 4, three arms by MECHANISM, each ALONE, whole-file goldens +
  regression sweep + out-of-scope rc=2 + FULL gate rc=0 per arm): (a) widen
  `str_cmp_shape_fix_rel` (codegen.ml ~7302) to match `ImemFb` BOTH sides (H1..H6;
  no prescan twin); (b) NEW ordered-relation-with-LITERAL route off the
  `str_cmp_shape_fix` Eq/Ne arms for Lt/Le/Gt/Ge keyed on the FIRST LOWERED operand
  (staged EB vs direct 11, positional pair + collapse, skip d2/da) — prescan DEMAND
  twins `is_test_left`/`is_test_right` (~3000-3076) widen IN THE SAME COMMIT
  ([C152]); (c) NegL arm `lower_test_skip0` (~7736): accept string compares under
  `^` by rewriting to the complement (Eq->Ne, Lt->Ge, Le->Gt, Gt->Le) and lowering
  the complement object verbatim. Then step 6: claims C348.. from RESULTS §2 ONLY
  (D-panel claim must state the inv/simpl non-separability); SPECIMENS +24 (panel
  expected 1174 — ACTUAL printed number governs); `--update-inventory`; census; new
  COVERAGE rows (byte tier); FULL gate ACTUALS; CLOSE per PLAN §6. NEVER push.
- Superseded bootstrap block below (pre-run expectations, PROPOSED at the time):

<!-- phase-p4-bootstrap-marker -->

- (superseded 2026-11-01 by the run above) Bootstrap MEASURED this session (accepted): HEAD b1f72d6 == expected; tree clean
  except the operator handoff.config.json edit; checkpoint g87 CURRENT (prose-hash
  recompute + guard session state); fresh session, renewal chain state absent
  (done 0/12 per config). E2E-49/P4 opened: PLAN.md committed with HANDOFF/PROGRESS
  pointers; HANDOFF Next action = P4 ACTIVE (the P3 CLOSED record it replaced is
  preserved verbatim in docs/history/2026-11-01-e49p3-closed.md — archive verified
  at close; treat this as accepted only after that grep).
- UNVERIFIED (proposed, from code reading ONLY — verify by running the binary in
  BASELINE-MINE before preregistering): str_cmp_shape_fix_rel (codegen.ml:7302)
  matches ImemF/ImemF only → Panels A/B refuse rc=2; Panel C accepts on arm-c bytes
  (predictions in PLAN §Panel C); NegL arm (~7736) refuses string compares → Panel D
  refuses. Prescan twins is_test_left/is_test_right (~3000-3076) must widen IN THE
  SAME COMMIT as any literal-relation lowering (one predicate, [C152]).
- NEXT STEP: pre-registration commit (probes E49G*/H*/I*/J*.PLI + mkprobes.py +
  HYPOTHESES.md + BASELINE-MINE.txt) BEFORE any oracle call; then the single
  grouped batch run tag e49p4. Full procedure, commands and boundaries:
  spec/lab-evidence/e2e49-p4/PLAN.md and HANDOFF.md -> Next action.
- P3 CLOSED record (gate rc=0 measured at 4df35bb, recorded 1f611f5; panel 1150/0,
  coverage 129/0/0, ledger C347): unchanged below, byte-preserved from the close.

## Previous phase — E2E-49/P2 CLOSED (FULL compile-tier gate rc=0 measured at HEAD `d5983e8`, recorded `8926b83`)

- Round (OPERATOR-authorized 2026-11-01): member-vs-member FIXED CHARACTER compares in
  TEST. Pre-registration `3bd9417` committed BEFORE any oracle call (probes E49B1..B5,
  HYPOTHESES, BASELINE-MINE at `7fa763b`: baseline refused all five rc=2 — every gap
  `my-gap`, NO dr-refuses); fill-in `586c240`; ONE oracle run 5 ok / 5; goldens +
  `spec/lab-evidence/e2e49-p2/RESULTS.md` `62f5622`; docs `1416f52`.
- Arm 1 `b1e9221` (codegen only, committed ALONE): `op_mov_a_b = 0x78`; encoder
  `str_cmp_shape_fix_mm` matching the QUALIFIED pair `ImemF/ImemF` ONLY; stacked head as
  ONE bundled thunk in written order; collapse `06 capl / 78` iff `capl = capr` else
  `3E capr`; `?SCCCM`; C2/CA + [C309] fill; NO prescan change. ACTUALS on that tree:
  five goldens whole-file BYTE-EXACT; E48/E49 sweep 61/61; registered panel 1131/1131;
  out-of-scope refusals rc=2; collapse verified NOT to leak into the literal template.
- Step 6: part 1 `0abf1c1` (claims C337..C341 from RESULTS §2 ONLY; SPECIMENS E49B1..B5;
  sanctioned `--update-inventory` 5 rows → panel **1136**; census re-snapshot counts
  UNCHANGED 15/0/26/0); part 2a `8c1d2ee` (3 new COVERAGE rows); part 2b `d5983e8`
  (widening of `COND.CMP_LENGTHS_POSITIONAL` to EXACT:8 + three labelled SUPERSEDED
  clauses — PROTOCOL #2, originals verbatim).
- FULL gate at `d5983e8` rc=0, ACTUALS as printed: byte panel **1136 byte-exact / 0 fail
  of 1136**, negative **181/181** (E46K14 `[dr-refuses]`, marker UNMOVED), divergence
  **9/9**, coverage **125 rows, 0 errors, 0 warnings**, census **15/0/26/0**, prose
  **5 active files clean**. `dune build` rc=0. BYTE TIER ONLY — no `spec/RUNTIME.txt` row
  came or comes from this round.
- Laws: [C337] stacked-cell parking in the member-vs-member `?SCCCM` head (per-shape
  mechanism; `EB` only vs pooled literals); [C338] equal-extent collapse `06 n/78`,
  member-vs-member ONLY — literal template keeps two immediates (equal-length literal
  case [TBD]); [C339] positional lengths on an all-member pair; [C340] written side
  selects the `*D` slot; [C341] head size follows the length pair, member pair pools no
  literal (DATA 000C, [C314]).
- Keep refusing (RESULTS §3): ANY BARE spelling in a member pair; the equal-extent
  collapse for member-vs-literal; STORE; literal-vs-literal; BASED; fixed truthiness;
  over-extent; relations beyond `=`/`^=`; `^( )`.
- NEXT: NO active round — a successor session without an operator instruction confirms
  HEAD and tree, runs `/handoff verify`, records state and STOPS; candidate pool in
  `HANDOFF.md` → Next action. Superseded prose (this round's IN FLIGHT sections AND the
  surviving P1 closing-era sections AND the stale P1-era stubs/evidence/Blockers) is
  archived verbatim in `docs/history/2026-11-01-e49p2-closed.md`. No push; operator
  `handoff.config.json` edit stays unstaged.

## Next action

The ONE active spec lives in `HANDOFF.md` -> its single level-2 Next-action heading: E2E-49/P4
ACTIVE, pre-registration owed first; PLAN at spec/lab-evidence/e2e49-p4/PLAN.md.

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
- **Deferred documentation work (recorded, operator-aware):** `README.md` "Current status
  (rolling)" is stale (ends at E2E-1/C067); it was deliberately NOT touched by the Mission-1
  documentation consolidation. Never use it for status — the ledger and this file are authority.

## Verified evidence

The FULL compile-tier gate rc=0 at HEAD `4df35bb` with ACTUALS AS PRINTED (byte panel
1150 byte-exact / 0 fail of 1150 incl. all fourteen e49p3 specimens whole-file at 256
bytes; negative 181/181 with the E46K14 `[dr-refuses]` pinned marker UNMOVED; divergence
9/9; coverage 129 rows 0 errors 0 warnings; census EXACT 15 / DIFFERS 0 / REFUSED 26 /
UNEXPECTED 0; prose 5 active files clean; `dune build` rc=0) was MEASURED by the step-6
session and recorded at `1f611f5` — NOT re-run since and not re-runnable in a docs-only
session; no scientific byte changed after `4df35bb`. Measured by THIS closing session
(docs-only, 2026-11-01): git HEAD `c140277` with a clean tree apart from the operator's
`handoff.config.json` edit; the eleven archive blocks byte-compared to their stated git
ranges at `4df35bb`/`c140277` — ALL BYTE-EXACT; the draft's `d256013`-prose claim and the
P2 previous-phase identity claim between generations. Per-arm ACTUALS (whole-file `cmp`
at each arm, sweeps, out-of-scope refusals rc=2) stand in git log and dated `LEARNINGS.md`
sections. Round evidence: `golden/e49p3/`,
`spec/lab-evidence/e2e49-p3/{RESULTS,HYPOTHESES,BASELINE-MINE,mkprobes.py}`; earlier
rounds `spec/lab-evidence/e2e49-p{1,2}/` and `spec/lab-evidence/e2e48-*/`; closed-round
records: `docs/history/`.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 94
checkpoint-id: g94-8a7bc7cdd49f
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-11-01T12:38:24.393Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 946f687217d3fc194cbb3b39236d10a398e9f5eb8baf7e61fcb043a67398479c
source-handoff: 0d708967a5e36b1b2b3f1e180c86d73a1275fd89b4b900e8ca2867b7a509a08c
source-learnings: a33c9d64bb4a8a48f0cd9e5f50412532b66b0a6499894d71ed6c0cb289e479ad
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: — E2E-49/P4 ACTIVE: ARM a LANDED `c515377`; ARM b code-complete (G1..G8 BYTE-EXACT) — verification+commit OWED; then ARM c, step 6, CLOSE

0a. STATE: see `PROGRESS.md` Current phase STATUS (authoritative this session): arm a
   committed alone with FULL gate rc=0; arm b = new `str_cmp_shape_fix_lit_rel` encoder
   (QUALIFIED member vs LITERAL ONLY; staged-EB/direct-11 keyed on FIRST LOWERED operand,
   positional pair + [C342] collapse, d2/da; direct head SIX bytes — `11` carries the pool
   operand) + caller arm + annotations; prescan twins needed NO change ([C152] verified;
   "twins MUST widen" falsified). ARM b OWED: sweep A..I, out-of-scope rc=2 (J rows,
   bare+literal scratch, lit-lit scratch, rel-in-STORE), FULL gate rc=0, commit ALONE.
   ARM c per PROGRESS spec (only ^(Eq)->Ne, ^(Lt)->Ge, ^(Le)->Gt; NO un-witnessed rewrites).

0. LANDED this session: pre-registration `328eb3f` (24 probes + mkprobes.py +
   HYPOTHESES + BASELINE-MINE, measured with the ACTUAL binary, committed BEFORE the
   oracle); ONE grouped batch run tag e49p4 -> **24 ok / 24, NO dr-refuses**; goldens +
   RESULTS committed together `13fca5b` (+ wording repair `9799f1d`). Verdicts: Panel A
   **H-A-sw CONFIRMED** (the ORDER law REKEYS the literal template: lowered member-first
   = staged EB, lowered literal-first = direct 11; H-A-or FALSIFIED at G3..G6), positional
   immediates on LOWERED operands, [C342] collapse at 3/3 in BOTH literal templates under
   all four relations, BRANCH d2/da transfers, [C345] over-extent pooled WHOLE; Panel B
   **H-B-invis CONFIRMED** (bare mixes == qualified twins byte-for-byte but packed name
   bytes; H4 `nb >= na` == golden F3); Panel C **WHOLE-FILE BYTE-EXACT vs my arm-c
   baseline, NO ARM** (transfer MEASURED, I5==I6 but names); Panel D DR **ACCEPTS** `^( )`
   on string heads, each object is the COMPLEMENT's object byte-equal (J1≡B5, J3≡C4,
   J4≡F2, J2≡F1-head+da); H-D-inv/H-D-simpl BYTE-CONVERGENT (pre-registered
   non-separability — claims must not prefer a reading); H-D-extra FALSIFIED.
   Classification: 18 `my-gap` (G1..G8,H1..H6,J1..J4), 6 already-byte-exact (I), 0
   dr-refuses. Evidence: `spec/lab-evidence/e2e49-p4/{BASELINE-MINE.txt,HYPOTHESES.md,RESULTS.md}`,
   `golden/e49p4/`.
   NEXT (step 4, PLAN): THREE arms by MECHANISM, each ALONE with whole-file byte
   verification + regression sweep + FULL gate rc=0 before the next:
   (a) widen `str_cmp_shape_fix_rel` (codegen.ml ~7302) from `ImemF/ImemF` to also
       match `ImemFb` on BOTH sides — H1..H6 are byte-equal to the qualified lowering,
       NO prescan twin (member pair pools no literal); verify H* goldens whole-file
       byte-exact + F*/I* regression + out-of-scope still rc=2.
   (b) NEW route for ORDERED relations with a LITERAL side: extend the Eq/Ne literal
       pair (`str_cmp_shape_fix` arms) to `Lt/Le/Gt/Ge` — key template on FIRST LOWERED
       operand (member-first = staged EB, literal-first = direct), positional pair +
       collapse on LOWERED operands, skip d2/da; the prescan DEMAND twins
       `is_test_left`/`is_test_right` (~3000-3076) MUST widen IN THE SAME COMMIT
       ([C152] one-predicate invariant).
   (c) NegL arm of `lower_test_skip0` (~7736): accept string compares by rewriting
       `^(op)` to the complement (Eq->Ne, Lt->Ge, Le->Gt, Gt->Le) and lowering exactly
       the complement object (J1≡B5, J2≡F1+da, J3≡C4, J4≡F2); NO extra bytes.
   Then step 6 (claims from C348 from RESULTS §2 ONLY; SPECIMENS +24 in e2e_gate
   (panel expected 1150+24=1174 — the ACTUAL printed number governs); sanctioned
   `--update-inventory`; census re-snapshot; COVERAGE rows; FULL gate ACTUALS) and
   CLOSE per PLAN. NEVER push.
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
readiness-by: session:01a19707-67fc-71b9-af89-5373c8b376a8
readiness-at: 2026-11-01T12:38:24.397Z
readiness-checkpoint: g94-8a7bc7cdd49f
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P3 RESULTS §3 remainders (with the surviving P1/P2/P2e §3 entries) stay named
  refusals until a pre-registered round measures them: FIXED member in a STORE (either
  orientation), literal-vs-literal fixed, BASED member in a condition, fixed-member
  truthiness, `^( ... )` composition, `^=` over a ladder, over-extent in INITIAL/STORE,
  BARE spellings inside an ORDERED RELATION (the relation arm admits QUALIFIED pairs
  only until measured), ordered relations with a LITERAL operand, `<>`/`><` spellings,
  unequal-extent STRICT vs WEAK combinations beyond F2/F4's single pair, the collapse in
  a swapped head with unequal lengths (per-operand-position, measured once), bare `-0`
  spelling, runtime length rewrite, empty-varying PUT output, PUT EDIT of a bit item.
  Shapes REMOVED from this list by P3 MEASUREMENT: ANY BARE spelling in a member pair and
  the bare RIGHT of a literal ([C344]); the equal-attribute collapse for member-vs-LITERAL
  and in both literal templates ([C342], settling [C338]'s [TBD]); over-extent literal
  written LEFT ([C345]); relations beyond `=`/`^=` on the QUALIFIED pair ([C346]) — the
  P2-era wording is preserved verbatim in `docs/history/2026-11-01-e49p3-closed.md`. No
  `spec/RUNTIME.txt` row may come from these families.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).
