# PROGRESS.md — DRPLi

Manual prose wins over the managed block below it. Do not hand-edit the managed block.
This file tracks *working state*; compiler behaviour itself belongs to `spec/CLAIMS.md`.

## Current phase — E2E-48/P2e CLOSED; FULL GATE rc=0 measured in-session at `0749fa6` (2026-10-31); awaiting OPERATOR's next-round choice

- The round's ONE remaining debt ran and was verified THIS session: FULL compile-tier gate
  `python3 tools/e2e_gate.py` **rc=0**, ACTUAL **1127 byte-exact / 0 fail of 1127** (the seven
  P2e byte-tier specimens E48E1..E48E5, E48E7, E48E8 all BYTE-EXACT in the panel), negative
  **181/181** (E46K14 prints `[dr-refuses]`, pinned marker unmoved), divergence **9/9**,
  coverage **118 rows, 0 errors, 0 warnings**, census **15/0/26/0**, file prose clean.
  `dune build` rc=0 on this tree.
- Science: the round's laws are C327..C332 (from RESULTS §2 ONLY); §3 shapes stay unmeasured
  and NOT implemented; goldens untouched; E48E6 is a measured dr-refuses, not a specimen.
- Commits: prereg `421656a`, oracle + goldens `e2b77ba`, arms 1–5 `d18c6ab`/`bab0d16`/
  `e49902a`/`046046a`/`c215ea0`, step 6 `809af8d`+`0e64c8b`, docs `0749fa6`; superseded
  working-state prose archived verbatim in `docs/history/2026-10-31-p2e-closed.md`.
- NOT re-measured this session (recorded, not assumed): clean scratch-tree rebuild warning
  multiset — last measured 126 = 28/26/22/17/15/14/2/2 at `c215ea0`.
- Tree: operator's `handoff.config.json` edit ONLY (never stage/commit/revert). No push.
  Standing prohibitions (goldens, §3 shapes, probes ≤71 cols CRLF+`^Z`, `eval $(opam env)`,
  never name a probe variable `c`, no push) are in HANDOFF.md.

## Next action

The ONE active spec lives in `HANDOFF.md` → its single level-2 Next-action heading: the
E2E-48/P2e round is CLOSED, a successor session awaits the OPERATOR's named round, records
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

Measured by THIS session (2026-10-31, HEAD `0749fa6`), not quoted from a report: the FULL
compile-tier gate rc=0 with the ACTUALs recorded in Current phase (byte panel 1127/0 incl.
all seven E48E byte-tier specimens; negative 181/181 with E46K14 `[dr-refuses]` and its
marker unmoved; divergence 9/9; coverage 118 rows 0 errors; census 15/0/26/0; prose panel
clean) and `dune build` rc=0 on this tree. Per-arm measured ACTUALS (whole-file `cmp` at
`d18c6ab`..`c215ea0`, regression sweeps 45/45, E46K14 marker re-measurement through the
binary, warning multiset 126) stand recorded in git log and dated `LEARNINGS.md` sections;
the superseded working-state prose is archived in `docs/history/2026-10-31-p2e-closed.md`.
Round evidence: `golden/e48p2e/`,
`spec/lab-evidence/e2e48-p2e/{RESULTS,HYPOTHESES,BASELINE-MINE}`; closed-round records:
`docs/history/`.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 63
checkpoint-id: g63-84ac6f3924e4
checkpoint-kind: manual
content-delta: new
readiness: attested
guard-level: 4
checkpointed: 2026-10-31T15:50:12.984Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 97a384c521b7216ef7d4ae81256018c6200858179a119d352cba7284cb5c470b
source-handoff: aec8d333d3360349ab44258d27d5b35b2a77417406e4b6ad515703af0cf8f3bd
source-learnings: a406124d9f88614fd7d3b5ea43c083f01cad16b07484c2bb33b94c27f99a31a8
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8
next-action: — E2E-48/P2e STEP 6 COMMITTED (`809af8d` + `0e64c8b`); ONE step remains: FULL GATE

1. Run the FULL compile-tier gate: `cd /home/john/projects/sushiworks/pli80 &&
   python3 tools/e2e_gate.py` — **report ACTUAL numbers, never expected** (before this
   round's registration it was 1120/0; the 7 new byte-tier specimens make 1127 expected,
   but only the run decides). Expect negative 181/181 (E46K14 stays a refusal row, now
   dr-refuses, marker re-measured unmoved), divergence 9/9, coverage 118 rows 0 errors,
   census 15/0/26/0, prose clean, rc=0. The binary is built (`eval "$(opam env)" &&
   dune build` in ocaml/ was rc=0 this session; rebuild if the tree moved).
2. If rc=0: rewrite the HANDOFF/PROGRESS manual prose to close the phase (the managed
   block refreshes via /handoff or handoff_finalize; never hand-edit it), note that the
   E2E-48/P2e round is COMPLETE, and let the OPERATOR choose the next round (candidates
   are RESULTS §3: member-vs-member, BASED member, over-extent INITIAL/store, PUT EDIT
   bit item, `^(k = -c)` composition probe, `%include`/LOAN2 — each needs its own
   pre-registered round). If the gate FAILS: do not patch prose around it — classify the
   delta against the panels, fix only what the ACTUAL indicts, re-run, commit.
3. Standing: goldens untouched; §3 shapes NOT implemented; no push; never stage/commit/
revert the operator's `handoff.config.json` edit; renewal values live ONLY in
`handoff.config.json` / `/guard status`.
readiness-by: session:01a19293-88a6-70b4-8abc-b0ee77b4885e
readiness-at: 2026-10-31T15:50:12.987Z
readiness-checkpoint: g63-84ac6f3924e4
<!-- guard:end checkpoint -->

## Blockers

- Nothing is half-edited at this boundary; every item below is recorded evidence, not a guess.
- **Missing evidence is the limit, never a licence to guess** (`PROTOCOL.md` #4). The
  E2E-48/P2e RESULTS §3 shapes stay named refusals until a pre-registered round measures them:
  FIXED member in a condition STORE, member-vs-member compare, BASED member in a condition,
  over-extent INITIAL/store, `^=` over a ladder, `^(string compare)`, bare `-0` spelling,
  runtime length rewrite, empty-varying PUT output. No `spec/RUNTIME.txt` row may come from
  this phase family.
- CREATE is NOT byte-exact; measured front-end blocker: `pli80c.ml` never expands `%include`
  (proposal in `LEARNINGS.md` is `proposed, unverified` — needs its own pre-registered round).
- LOAN2's `conflicting kinds` prescan my-gap is a design change, not an arm (see Pending).
