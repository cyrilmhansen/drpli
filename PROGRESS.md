# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-49/P3 step 6 IN FLIGHT: part 1 LANDED (`4b51bc0`); COVERAGE 2a/2b + FULL gate record + CLOSE owed

- Chain: pre-registration `3659f5d` (14 probes E49C1..C4/D1..D4/E1..E2/F1..F4 +
  mkprobes.py + HYPOTHESES.md + BASELINE-MINE at 685741c) BEFORE any oracle call; fill-in
  `0a46824`; ONE grouped batch run, tag `e49p3`, **14 ok / 14 — NO dr-refuses**; goldens +
  RESULTS `ad90425`; arms a `a540fa7`, b `0a1b80c`, c `cde3258` (each ALONE, 14/14
  whole-file BYTE-EXACT, gate rc=0 at each; E49E1/E2 needed NO code).
- STEP 6 PART 1 `4b51bc0` (no `ocaml/` byte changed): claims **C342..C347** derived ONLY
  from RESULTS s2 (collapse = LENGTH-PAIR law in BOTH literal templates; CA + [C309] fill
  measured on the direct template; qualification invisible, bare RIGHT of a literal
  admitted; over-extent literal-LEFT accepted/pooled whole, NO ARM; ordered relations with
  the ORDER law (`<`,`>=` written / `>`,`<=` swapped) and BRANCH law (strict JNC `d2`, weak
  JC `da`) and positional lengths on LOWERED operands; sizes + [C314] DATA in all
  fourteen), labelled CORRECTION appends with originals verbatim at [C335]/[C336]/[C337]/
  [C338], SPECIMENS +14, sanctioned `--update-inventory` (panel **1150**, exactly +14
  rows), census re-snapshot counts UNCHANGED **15/0/26/0** (head `1da795d`, md5
  `335d69c6`). COUNT NOTE: RESULTS s2.1 says "six collapse objects" and NAMES SEVEN —
  recorded in [C342], evidence file untouched.
- ACTUALS measured by THIS session on the committed part-1 tree: `dune build` rc=0; FULL
  compile-tier gate `python3 tools/e2e_gate.py` **rc=0** — byte panel **1150 byte-exact /
  0 fail of 1150**, negative **181/181** (E46K14 `[dr-refuses]` pinned marker UNMOVED),
  divergence **9/9**, coverage **125 rows, 0 errors, 0 warnings**, census unchanged
  15/0/26/0, prose **5 active files clean**.
- NEXT: step 6 parts 2a/2b (COVERAGE rows + widening + labelled SUPERSEDED clauses) and
  the final FULL gate record, then CLOSE. EXACT procedure and planned row ids in
  `HANDOFF.md` -> Next action items 2-3.
- Working tree at this boundary: the guard's managed blocks in HANDOFF.md/PROGRESS.md plus
  the OPERATOR's `handoff.config.json` edit (never staged, never touched).

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

The ONE active spec lives in `HANDOFF.md` → its single level-2 Next-action heading: the
E2E-49/P2 round is CLOSED, a successor session awaits the OPERATOR's named round, records
state and stops. No competing action exists anywhere else; PROGRESS does not restate it
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

Measured by THIS session (2026-11-01), not quoted from a report: `dune build` rc=0 on this
tree; the FULL compile-tier gate rc=0 at HEAD `d5983e8` with the ACTUALS recorded in
Current phase (byte panel 1136 byte-exact / 0 fail of 1136 incl. all five E49B specimens
whole-file at 256 bytes; negative 181/181 with the E46K14 `[dr-refuses]` pinned marker
UNMOVED; divergence 9/9; coverage 125 rows 0 errors 0 warnings; census EXACT 15 / DIFFERS
0 / REFUSED 26 / UNEXPECTED 0; prose 5 active files clean); `coverage_check.py` rc=0 and
`file_prose_check.py` rc=0 on the close tree. Per-arm ACTUALS (whole-file `cmp` at
`b1e9221`, sweeps 61/61 and 1131/1131, out-of-scope refusals rc=2) stand in git log and
dated `LEARNINGS.md` sections. Round evidence: `golden/e49p2/`,
`spec/lab-evidence/e2e49-p2/{RESULTS,HYPOTHESES,BASELINE-MINE}`; earlier rounds
`spec/lab-evidence/e2e49-p1/` and `spec/lab-evidence/e2e48-*/`; closed-round records:
`docs/history/`.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 82
checkpoint-id: g82-eb070d852cef
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 2
checkpointed: 2026-11-01T07:47:06.190Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 48a8de5ecac96154fb79e4e692eb3312bacee30d36b8179dd40b83fddbbe8f5f
source-handoff: dd029d2a91aea64d93c7fd540cfc274109a1c702602ecc3ce2b10be5aca54d83
source-learnings: 429a1fdac726660656c505cec218e5de3240902bd8316ee9648ee46fa987b766
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: — E2E-49/P3 step 6 IN FLIGHT: claims, registration, COVERAGE, FULL gate; then CLOSE

1. ARMS DONE (each committed ALONE, 14/14 goldens whole-file BYTE-EXACT, gate rc=0 at
   each): a `a540fa7` (collapse in BOTH literal templates, E49C1..C4), b `0a1b80c`
   (`ImemFb` in fix_mm + Lit-LEFT arm + `is_test_right` twin, E49D1..D4), c `cde3258`
   (`str_cmp_shape_fix_rel` + EqR Lt/Le/Gt/Ge route QUALIFIED-QUALIFIED ONLY, swap
   `>`/`<=`, JNC d2/JC da, positional-collapse on LOWERED operands, E49F1..F4).
   E49E1/E2 needed NO code. Panel stayed 1136/0, neg 181/181 (E46K14 marker UNMOVED),
   bare-in-relation / rel-with-literal / relation-in-STORE / bare-mm STORE all rc=2.
2. STEP 6 (the active work): claims from **C342** derived ONLY from
   `spec/lab-evidence/e2e49-p3/RESULTS.md` §2 (the P3 block starts at the end of the
   C341 entry; mimic the C337..C341 format; the ledger currently ENDS at C341). Then
   SPECIMENS bank +14 in `tools/e2e_gate.py` (round-bank comment style of E49A/E49B,
   pre-registration cite `3659f5d`, probes/E49{C1..C4,D1..D4,E1..E2,F1..F4}.PLI ->
   golden/e49p3/<N>/<N>.REL); sanctioned `python3 tools/e2e_gate.py --update-inventory`
   (panel 1136 -> 1150); census re-snapshot per the P2 recipe (commit `0abf1c1` shows
   the exact commands); COVERAGE rows (new EXACT entries for the collapse law, the
   qualification fold, relations) + labelled SUPERSEDED clauses where P1/P2 boundaries
   were falsified (C338 scope, P1 left-side-only, relations-beyond-=^=) — PROTOCOL #2,
   originals verbatim; then FULL compile-tier gate, record ACTUALS AS PRINTED.
3. CLOSE: archive superseded prose verbatim to `docs/history/`, rewrite HANDOFF/
   PROGRESS to CLOSED, LEARNINGS close notes, `/handoff finalize`.
4. Standing: probes ≤71 cols CRLF+`^Z`; `eval $(opam env)` before dune; no var named
   `c`; goldens untouched except e49p3; NO spec/RUNTIME.txt row from the compare
   families; never touch the operator's `handoff.config.json` edit; renewal values
   ONLY in `handoff.config.json` / `/guard status`; no push.
readiness-by: session:01a195fd-fc1b-7195-ad35-f2d9fed8e5b7
readiness-at: 2026-11-01T07:47:06.193Z
readiness-checkpoint: g82-eb070d852cef
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P2 RESULTS §3 shapes (with the surviving P1 §3 and P2e §3 entries) stay named
  refusals until a pre-registered round measures them: ANY BARE spelling in a
  member-vs-member pair, the equal-extent collapse for member-vs-LITERAL ([C338] scope
  warning), FIXED member in a STORE (either orientation), literal-vs-literal fixed, BASED
  member in a condition, fixed-member truthiness, BARE fixed member on the RIGHT,
  over-extent in every orientation incl. INITIAL/STORE, relations beyond `=`/`^=`, `^=`
  over a ladder, `^(string compare)`, bare `-0` spelling, runtime length rewrite,
  empty-varying PUT output, PUT EDIT of a bit item. `member-vs-member` itself is NO
  LONGER on this list — E49B1..B5 measured it ([C337]); the P1-era wording is preserved
  verbatim in `docs/history/2026-11-01-e49p2-closed.md`. No `spec/RUNTIME.txt` row may
  come from these families.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).
