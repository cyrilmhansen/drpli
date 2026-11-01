# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-49/P2 IN FLIGHT (member-vs-member FIXED compares in TEST; oracle run measured, arms NOT yet implemented)

- Round authorized by the OPERATOR 2026-11-01. Pre-registration `3bd9417` (probes
  E49B1..E49B5 + mkprobes.py + HYPOTHESES.md + BASELINE-MINE.txt at HEAD `7fa763b`: all
  five refused rc=2 — all gaps `my-gap`) committed BEFORE any oracle call; prediction-SHA
  fill-in child `586c240`; ONE run `--tag e49p2 --switches '$L$D'` -> **5 ok / 5, NO
  dr-refuses**; goldens + `spec/lab-evidence/e2e49-p2/RESULTS.md` committed together at
  `62f5622`.
- MEASURED laws (RESULTS §2 ONLY): §2.1 member-vs-member takes `?SCCCM` with head
  `21 *D(left cell) / E5 (PUSH H) / 21 *D(right cell) / D1 (POP D)` — the [C141] STACK
  parking, NOT [C333]'s XCHG: BOTH pre-registered forms (H-S direct, H-M staged) were
  falsified, a fourth shape again; [C191] final law survives (HL=right, DE=left), load
  order is the WRITTEN order. §2.2 EQUAL-EXTENT COLLAPSE: equal extents emit
  `06 n / 78 (MOV A,B)`, no `MVI A`; unequal extents keep the two immediates — measured
  ONLY member-vs-member, the member-vs-literal equal-length case stays [TBD] and the
  literal template keeps two immediates. §2.3 [C334] positional law confirmed on an
  all-member pair (B3 `06 03 / 3E 02`, B4 `06 02 / 3E 03`; min/max/class falsifiers dead).
  §2.4 inversion swaps the two `*D` reloc slots (B1 vs B2 differ only name bytes + those
  slots). §2.5 `^=` skip CA in the stacked head (B5, fill -> 001D). §2.6 CODE 66 (collapse,
  17-byte head) / 67 (two immediates, 18-byte head), DATA 000C [C314] unchanged.
- NEXT: arm 1 in `ocaml/lib/codegen.ml` — add `op_mov_a_b = 0x78` next to `op_mov_b_a`
  (~line 636); new encoder `str_cmp_shape_fix_mm` after `str_cmp_shape_fix` (~line 7170)
  matching ONLY `Some (`ImemF _, Some (`ImemF _)` (BARE `ImemFb` on EITHER side stays
  refused — unmeasured, RESULTS §3); new `Eq|Ne` TEST arm in `lower_test_skip0` directly
  AFTER the `str_cmp_shape_fix` arm (~line 7880): head thunk (lxi_h/reloc/push_h/
  lxi_h/reloc/pop_d bundled in ORDER), `op_mvi_b`+capl, then `op_mov_a_b` IF capl=capr
  ELSE `op_mvi_a`+capr, `call_ext "?SCCCM"`, skip C2/CA, `st.last_imm <- None`, slot.
  NO prescan twin (no pooled literal — demand law untouched). Annotate the superseded
  "member-vs-member keeps refusing" sentences (str_cmp_shape_fix header, imem_refuse
  WHY) with labelled ADDENDA, originals verbatim (PROTOCOL #2). Verify: dune build; each
  E49B*.REL whole-file `cmp` byte-exact vs golden/e49p2; E48+E49 sweeps; full registered-
  panel sweep via INVENTORY rows; out-of-scope refusals still rc=2 (bare-anywhere mm, the
  STORE, truthiness, literal-vs-literal, BASED; E46K14 marker UNMOVED).
- Then STEP 6: claims C337.. derived ONLY from RESULTS §2; SPECIMENS bank E49B1..B5 in
  `tools/e2e_gate.py`; INVENTORY via sanctioned `--update-inventory` (5 rows after
  E49A4); census re-snapshot; COVERAGE rows; FULL gate `python3 tools/e2e_gate.py`
  (expect byte panel **1136**, neg 181/181, div 9/9); record ACTUALS; CLOSE (prose,
  docs/history archive, LEARNINGS, `/handoff finalize`).
- Keep refusing (RESULTS §3): any BARE spelling in a member-vs-member pair; the
  equal-extent collapse for member-vs-literal; STORE; literal-vs-literal; BASED;
  truthiness; over-extent; relations beyond `=`/`^=`; `^( )`. BYTE TIER ONLY — no
  `spec/RUNTIME.txt` row from this round. No push; operator `handoff.config.json` edit
  stays unstaged.

### SUPERSEDED — E2E-49/P1 CLOSED (2026-11-01; FULL compile-tier GATE rc=0 measured at `0a8ceff`)

- Round: operand-inverted FIXED compares (member LEFT of a literal in TEST), probes
  E49A1..A4 pre-registered `9b3d860` BEFORE any oracle call, fill-in `0e9cc3d`, ONE run
  4 ok/4, all ACCEPTS, no dr-refuses (goldens + RESULTS `c8285cb`); my baseline refused
  all four — every gap `my-gap`.
- Ledger at `0a8ceff`: C333 (XCHG staging = ORIENTATION law, measured for the FIXED class
  with *D operands; helper name carries no orientation; `^=` CA measured in the ?SCCCM
  family), C334 (length immediates POSITIONAL — B = LEFT attribute, A = RIGHT; falsifies
  [C330]'s class-polarity reading; labelled CORRECTION appended at C330, falsified text
  kept, PROTOCOL #2), C335 (bare-vs-qualified byte-identical but three module-name field
  bytes; admission deliberately asymmetric — bare member-RIGHT keeps refusing), C336
  (over-extent literal ACCEPTED, pooled WHOLE, member-left; literal-LEFT stays [TBD]).
- Arms: `fee935e` (member-LEFT lowering + positional return tuple + `is_test_left` twin),
  `b044b7c` (bare `ImemFb` variant, or-pattern member-LEFT arm, same-commit prescan
  widening, ?IS22N guard refusal widened exactly to the admitted set).
- Registration at `0a8ceff`: SPECIMENS bank E49A1..A4; INVENTORY via sanctioned
  `--update-inventory` (exactly 4 rows, panel 1131 entries); census re-snapshot counts
  UNCHANGED 15/0/26/0; COVERAGE 4 rows + labelled SUPERSEDED note on
  COND.FIXED_MEMBER_TEST_SCCCM.
- FULL GATE at `0a8ceff` rc=0: 1131 byte-exact / 0 fail (E49A1..A4 BYTE-EXACT), negative
  181/181 (E46K14 `[dr-refuses]`, marker UNMOVED), divergence 9/9, coverage 122 rows
  0 errors 0 warnings, census 15/0/26/0, prose 5 files clean. `dune build` rc=0. BYTE
  TIER ONLY — no `spec/RUNTIME.txt` row from this round.
- Close: superseded prose (this round AND the P2e close record AND the old Blockers)
  archived verbatim from committed blobs in `docs/history/2026-11-01-e49p1-closed.md`;
  README index row added; LEARNINGS close notes. No push.
- Keep refusing (e2e49-p1 §3 + e2e48-p2e §3): fixed member in STORE (both orientations),
  member-vs-member, literal-vs-literal, BASED, fixed truthiness, bare member-RIGHT,
  over-extent literal-LEFT, over-extent INITIAL/STORE, `^( )`, `^=` over a ladder, bare
  `-0`, runtime length rewrite, empty-varying PUT output, PUT EDIT bit item.

## Next action

The ONE active spec lives in `HANDOFF.md` → its single level-2 Next-action heading: the
E2E-49/P1 round is CLOSED, a successor session awaits the OPERATOR's named round, records
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

Measured by THIS session (2026-11-01, HEAD `0a8ceff`), not quoted from a report: the FULL
compile-tier gate rc=0 with the ACTUALS recorded in Current phase (byte panel 1131/0 incl.
all four E49A specimens; negative 181/181 with E46K14 `[dr-refuses]` marker unmoved; 9/9;
coverage 122 rows 0 errors; census 15/0/26/0; prose clean); `coverage_check.py` rc=0;
`file_prose_check.py` rc=0; `dune build` rc=0 on this tree. Per-arm ACTUALS (whole-file
`cmp` at `fee935e`/`b044b7c`, E48 sweep 52/52, full registered-panel sweep 1127/1127,
out-of-scope refusals rc=2) stand in git log and dated `LEARNINGS.md` sections. Round
evidence: `golden/e49p1/`, `spec/lab-evidence/e2e49-p1/{RESULTS,HYPOTHESES,BASELINE-MINE}`;
closed-round records: `docs/history/`.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 71
checkpoint-id: g71-4f3557084b8e
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 2
checkpointed: 2026-11-01T02:33:27.273Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 4e37911283356bdde8b701c044cd1f70a31ed8aaf4523ef029ffde5d7e746693
source-handoff: d3699fdff6b91fa2c0861190036038c92c8c8cb79790f8cdd206148db5707a62
source-learnings: c44737a635cdb1694aab0e3ccdb40f113d391c595ab5651804afdf3cfda5d3ad
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: — E2E-49/P2 [arm 1]: implement the measured member-vs-member lowering

1. ARM 1 (the only authorized scientific action now): implement EXACTLY what
   `spec/lab-evidence/e2e49-p2/RESULTS.md` §2 measures — file:line plan in PROGRESS →
   Current phase: `op_mov_a_b = 0x78`; encoder `str_cmp_shape_fix_mm` gated to the
   QUALIFIED-qualified pair `ImemF/ImemF` ONLY (any BARE side keeps refusing — RESULTS
   §3); stack-parked head bundled in written order; `06 b` then collapse `78` iff
   `capl = capr` ELSE `3E a`; `?SCCCM`; skip C2/CA + [C309] slot; NO prescan change (no
   pooled literal); labelled ADDENDA at the superseded sentences, originals verbatim.
   Verify: `dune build`; whole-file `cmp` of all five `.REL` vs `golden/e49p2/`; E48/E49
   sweeps; full INVENTORY-driven registered-panel sweep; out-of-scope refusals rc=2 with
   the E46K14 marker UNMOVED. Commit the arm ALONE with measured ACTUALS.
2. Then STEP 6: claims C337.. derived ONLY from RESULTS §2; SPECIMENS bank E49B1..B5 in
   `tools/e2e_gate.py`; INVENTORY via sanctioned `--update-inventory` (5 rows after
   E49A4, panel 1136); census re-snapshot; COVERAGE rows; FULL gate
   `python3 tools/e2e_gate.py` (expect byte panel **1136**, neg 181/181, div 9/9);
   record ACTUALS; then CLOSE (prose rewrite, archive superseded prose verbatim from
   committed blobs to `docs/history/2026-11-01-e49p2-closed.md` + README index row,
   LEARNINGS close notes, ledger-end pointer past C336, `/handoff finalize`).
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71
   cols CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no
   push; never stage/commit/revert the operator's `handoff.config.json` edit; renewal
   values live ONLY in `handoff.config.json` / `/guard status`; NO `spec/RUNTIME.txt`
   row from this round.
readiness-by: session:01a194de-4c92-7103-bf3c-ac8aa379f9a9
readiness-at: 2026-11-01T02:33:27.277Z
readiness-checkpoint: g71-4f3557084b8e
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a
  guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-49/P1 RESULTS §3 and E2E-48/P2e §3 shapes stay named refusals until a
  pre-registered round measures them: FIXED member in a STORE (either orientation),
  member-vs-member, literal-vs-literal fixed, BASED member in a condition, fixed-member
  truthiness, BARE fixed member on the RIGHT, over-extent literal-LEFT, over-extent
  INITIAL/store, `^=` over a ladder, `^(string compare)`, bare `-0` spelling, runtime
  length rewrite, empty-varying PUT output. No `spec/RUNTIME.txt` row may come from
  these families.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands
  `%include` (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own
  pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).
