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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C326' spec/CLAIMS.md` etc.;
     the newest E2E-48 block starts at `grep -n '^## C309'` (~line 7170). The ledger CURRENTLY
     ENDS at **C326**: ids C327+ are OWED by the next action's step 6 — their absence is the
     recorded state, not corruption.
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Current round evidence: `spec/lab-evidence/e2e48-p2e/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-48/P2e lowering (verified at `046046a`, 2026-10-31)

- Arms 1 + 2 + 3 + 4 of the six RESULTS §2 arms are DONE, committed and measured (`d18c6ab`,
  `bab0d16`, `e49902a`, `046046a`): E48E1..E48E5 + E48E7 byte-identical. ARM 4 (`046046a`, §2.4): str_side admits QUALIFIED fixed member as `ImemF (key,cap)` (spelling gate orig<>m.name; [C258] fold = ONE Eident key, LEARNINGS 2026-10-31); str_cmp_shape_fix = 21 *D(member)/11 *D(pool)/06 len/3E cap/CD ?SCCCM + [C309] skip, TEST-ONLY; demand twin is_test_right widens ONLY literal-LEFT clause of prescan_cond; DATA 000B = golden. Gate at 046046a rc=0 ACTUALS: 1120/0, 181/181 E46K14 UNMOVED, 9/9, 113/0, 15/0/26/0, sweeps 45/45, multiset 126; E46K14's pinned refusal
  RE-MEASURED through the binary with gate CRLF+`^Z` semantics — marker unchanged, NOT
  re-pinned (re-run at `e49902a`: 181/181, 0 anomalies, marker unmoved); its `imem_refuse`
  WHY-string cites `golden/e48p2e/E48E6/E48E6.PRN` as a MEASURED dr-refuses (append,
  original verbatim); the NEG_META *category* re-classification (unmeasured -> dr-refuses)
  is still step-6 work. Arm 3 (`e49902a`, RESULTS §2.3): `bit_cond_mat`'s `Eq` fallback
  admits `Ast.Ebit "0"` on a `Vbit1` left — `3A *D(b) / E6 80 / D6 01 / 9F` + the caller's
  `STA` = 11 bytes (E48E5 0006..0010, the `'1'b` head WITHOUT the `D6 80` step); no pool
  cell demanded, prescan untouched; E48E6 KEEPS refusing through the new binary (no
  `.REL`). **ARM 5 NOT STARTED; step 6 (claims C327..C332/registration/gate/COVERAGE) OWED.** No `ocaml/` edit is half-done.
- Laws and refusals: `spec/lab-evidence/e2e48-p2e/RESULTS.md` §2 (six laws) and §3 (what
  stays unmeasured) are the authority; claims are owed as C327+ (next action step 6).
- E48E6 (`if line then`, CHARACTER VARYING member as bare condition) is **dr-refuses**
  (`BIT REQ`, no `.REL`); it is NOT a specimen and gets no `.REL`-based row.
- Regression baselines in force: e48p1 24/24, e48p2c 9/9, e48p2db 10/10, e48p2retire 2/2;
  FULL GATE baseline 1120 byte-exact / 0 fail (`adbfa2a`), negative 181/181, divergence 9/9,
  coverage 113 rows 0 errors (`218b474`), census 15/0/26/0; clean-rebuild warning multiset 126.
  EVERY one re-measured at `e49902a` (arm 3) with identical ACTUALS (rc=0).

## Next action — E2E-48/P2e STEP 6 COMMITTED (`809af8d` + `0e64c8b`); ONE step remains: FULL GATE

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

## Step 6 record (this session, verified)

- Claims C327..C332 appended to spec/CLAIMS.md from RESULTS §2 ONLY, bytes re-derived
  this session from the goldens with chaindump.py/reldump.py (accepted); [C296]
  ANNOTATION carries the VERIFIED spelling: attach operand `21 *C(0000)` = `RELOC
  common 0x0` at 0023 of BOTH E46M1 and E48E8, `load_file_cb` (codegen.ml:1229) emits
  `reloc st Common 0` — round 5's "CODE self-address" is labelled superseded in the
  [C296] annotation, the HYPOTHESES.md addendum (original kept verbatim) and LEARNINGS.
- Appends (originals kept): [C310] ANNOTATION 3, [C313] ANNOTATION 2, [C324], [C325].
- e2e_gate.py: SPECIMENS.update E48E1..E48E5,E48E7,E48E8 BYTE TIER ONLY (E48E6 NOT a
  specimen); NEG_META["E46K14"] = ("dr-refuses", BIT REQ + .PRN + [C332]) override
  AFTER the K2..K15 loop (E46K10 precedent). --update-inventory reviewed line-by-line:
  7 specimen rows + E46K14 reason swap, total 1127. census --check: counts identical
  15/0/26/0 (metadata-only json delta committed). coverage_check: 118 rows 0 errors;
  5 new rows + 6 annotated rows committed with coverage-stats.json at `0e64c8b`.
- NOT re-run this session: the FULL GATE (owed above) and the clean-rebuild warning
  multiset re-check.

## Unfinished operations

- **No half-finished edit.** Step 6 is COMMITTED (`809af8d`, `0e64c8b`); the ONE
  unfinished item is the FULL GATE run + ACTUAL report above. Nothing else is owed.
- The working tree at this checkpoint carries ONLY the operator's `handoff.config.json` edit.

## Discoveries not yet incorporated

- None outstanding. Durable method lessons are already classified in `LEARNINGS.md`; compiler
  law lives in `spec/CLAIMS.md` (C327+ owed by step 6, from `e2e48-p2e/RESULTS.md` §2 ONLY).
  The stale `README.md` rolling status is recorded as deferred work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status log:
  `docs/history/README.md` (extracted verbatim at `f3a4c60`).
- Renewal: the E2E-48 phase chain closed at its configured cap; state archived under
  `.pi-guard/archives/`. Effective renewal values are in `handoff.config.json` (authoritative) —
  never this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 62
checkpoint-id: g62-084ed7b0c916
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~981, session 01a19293-88a6-70b4-8abc-b0ee77b4885e)
checkpointed: 2026-10-31T15:49:27.325Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 97a384c521b7216ef7d4ae81256018c6200858179a119d352cba7284cb5c470b
source-handoff: aec8d333d3360349ab44258d27d5b35b2a77417406e4b6ad515703af0cf8f3bd
source-learnings: 9afe3635eeaeeb410e3cb30f468815221fb1a26fc29ed4a80ced4f5b74847503
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19293-88a6-70b4-8abc-b0ee77b4885e
readiness-at: 2026-10-31T15:49:27.327Z
readiness-checkpoint: g62-084ed7b0c916
### Last verified state
guard level 4; checkpoint requested (renewal tool refresh)

### Unfinished operations
- (none recorded)

### Next action
— E2E-48/P2e STEP 6 COMMITTED (`809af8d` + `0e64c8b`); ONE step remains: FULL GATE

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

### Guard notes
E2E-48/P2e step 6 COMMITTED at 809af8d (claims C327..C332 from RESULTS §2; [C296] COMMON-reloc annotation — round 5's CODE-self-address misreading superseded traceably; appends [C310]/[C313]/[C324]/[C325]; NEG_META[E46K14]=dr-refuses override after the K2..K15 loop; SPECIMENS.update E48E1..E48E5,E48E7,E48E8 BYTE TIER ONLY; --update-inventory reviewed line-by-line, 1127 rows; census --check counts identical 15/0/26/0) and 0e64c8b (5 new COVERAGE rows STOR.BIT1_COND_LADDER_SIGN/STOR.BIT1_COND_NEG_LADDER/STOR.BIT1_ZERO_LIT_VALUE/COND.FIXED_MEMBER_TEST_SCCCM/IO.PUT_BIT1_FILE_ITEM + 6 annotated rows, coverage_check 118 rows 0 errors, coverage-stats.json committed). Build rc=0 this session. ONLY remaining work: FULL GATE run `python3 tools/e2e_gate.py` at HEAD 0e64c8b — report ACTUAL (before registration 1120/0; expect 1127/0, neg 181/181 E46K14 marker unmoved, div 9/9, cov 118/0, census 15/0/26/0, multiset 126 not re-checked); if rc=0, rewrite HANDOFF/PROGRESS closing prose and finalize. Exact spec in HANDOFF.md ## Next action. Tree: operator handoff.config.json edit only — never stage/commit/revert it. No push. Goldens untouched; §3 shapes not implemented.
<!-- guard:end checkpoint -->
