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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C336' spec/CLAIMS.md` etc.;
     the E2E-49/P1 block starts at `grep -n '^## C333'` (~line 7610); the E2E-48 family is
     C309..C332, E2E-49/P1 is C333..C336. The ledger CURRENTLY ENDS at **C336** — no claim
     ids are owed. [C330] carries the labelled E2E-49/P1 CORRECTION append (positional
     length law); the falsified text is kept as written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p1/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P2 IN FLIGHT (arm 1 + step-6 part 1 committed at `0abf1c1`; FULL gate still OWED, never run this round)

- HEAD `0abf1c1` (chain: pre-registration `3bd9417`, fill-in `586c240`, oracle run + goldens +
  RESULTS `62f5622`, docs `1416f52`, **ARM 1 `b1e9221`**, **step 6 part 1 `0abf1c1`**). Working
  tree: only the operator's `handoff.config.json` edit, the guard's managed blocks and this
  session's prose. ARM 1 IS LANDED and `ocaml/` changed at `b1e9221`; step-6 part 1 changed NO
  compiler behaviour. The FULL compile-tier gate has NOT been run this round and nothing about it
  may be claimed until it is. `dune build` rc=0 measured on this tree.
- ARM 1 ACTUALS measured at `b1e9221`: all five `.REL` whole-file `cmp` BYTE-EXACT vs
  `golden/e49p2/`; E48/E49 sweep 61 byte-exact / 0 fail; INVENTORY-driven registered-panel sweep
  1131/1131 (pre-registration count); out-of-scope refusals all rc=2 (bare-anywhere mm, mm STORE,
  fixed truthiness, literal-vs-literal, mm `>`); E46K14 marker UNMOVED; the collapse verified NOT
  to leak into the literal template. Registration ACTUALS at `0abf1c1`: `--update-inventory` wrote
  exactly 5 specimen rows (panel **1136**), census counts UNCHANGED 15/0/26/0.
- Measured: E49B1..B5 all ACCEPTED (5 ok / 5, both passes clean; NO `dr-refuses`; every
  gap `my-gap`, baseline refused all five). Laws in RESULTS §2: member-vs-member takes
  `?SCCCM` with head `21 *D(left cell) / E5 (PUSH H) / 21 *D(right cell) / D1 (POP D)` —
  the [C141] STACK parking, NOT XCHG: BOTH pre-registered forms (H-S direct right-first,
  H-M staged) FALSIFIED, a fourth shape again; [C191] final law survives (HL=RIGHT, DE=
  LEFT), loads in WRITTEN order; EQUAL-EXTENT COLLAPSE `06 n / 78 (MOV A,B)` measured
  member-vs-member ONLY (three objects; unequal extents keep the two immediates,
  member-vs-literal equal-length stays [TBD] and the literal template must NOT collapse);
  [C334] positional lengths confirmed on an all-member pair (`06 03 / 3E 02` and its
  swap); inversion swaps the two `*D` reloc slots; `^=` skip CA in the stacked head;
  CODE 66/67, DATA 000C ([C314] unchanged). All five whole-file byte analyses are in
  RESULTS §1/§2.

### SUPERSEDED — E2E-49/P1 CLOSED (FULL compile-tier GATE rc=0 measured at `0a8ceff`, 2026-11-01; text kept verbatim, archive to docs/history at P2 close)

- Gate ACTUALS as printed at `0a8ceff`: byte panel **1131 byte-exact / 0 fail of 1131**
  (E49A1..A4 all four BYTE-EXACT vs `golden/e49p1`), negative panel **181/181** refused
  (E46K14 prints `[dr-refuses]`, pinned marker `comparison of the internal CHARACTER
  member REC.LINE` UNMOVED), divergence panel **9/9**, coverage **122 rows, 0 errors,
  0 warnings**, census **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**, file prose
  **5 active files clean**. `dune build` rc=0 on this tree. Runtime/link-run tiers
  remain delegated to the external rune-ci builders (unchanged policy).
- Landing chain: pre-registration `9b3d860`, fill-in `0e9cc3d`, ONE oracle run 4 ok/4 —
  all ACCEPTS, no dr-refuses — goldens + RESULTS `c8285cb`, arm 1 `fee935e` (member-LEFT
  lowering, XCHG staging, positional lengths, `is_test_left` twin), arm 2 `b044b7c` (bare
  spelling `ImemFb`; admission deliberately ASYMMETRIC — bare member-RIGHT keeps refusing;
  the numeric ?IS22N guard widened to refuse exactly the admitted set), learnings `f95b872`,
  step 6 `0a8ceff` (claims C333..C336 from RESULTS §2 ONLY + labelled C330 correction +
  INVENTORY 4 rows via the sanctioned `--update-inventory`, census re-snapshot counts
  unchanged, COVERAGE 4 rows + SUPERSEDED note).
- Byte tier ONLY: NO `spec/RUNTIME.txt` row came or comes from this round (RESULTS §3).
- Working tree at this checkpoint: ONLY the operator's `handoff.config.json` edit plus the
  guard-written managed-block refresh; never stage, commit or revert the config edit.

## Next action — E2E-49/P2 [step 6 part 2]: COVERAGE rows, FULL gate, then CLOSE

1. COVERAGE rows in `spec/COVERAGE.tsv` (exact plan in PROGRESS → Current phase): 3 NEW rows
   (`COND.FIXED_MEMBER_MEMBER_TEST` MEASURED EXACT:5; `COND.FIXED_CMP_EQUAL_EXTENT_COLLAPSE`
   MEASURED EXACT:3 with the scope warning in its boundary; `COND.CMP_INVERSION_SELECTS_SLOT`
   SINGLE_SAMPLE EXACT:2), widen `COND.CMP_LENGTHS_POSITIONAL` (+E49B3,E49B4, EXACT:8), and append
   labelled SUPERSEDED clauses to the boundary columns of `COND.FIXED_MEMBER_TEST_SCCCM`,
   `COND.FIXED_MEMBER_LEFT_TEST` and `COND.BIT1_NEG_TEST` (each still calls member-vs-member
   unmeasured/refused), originals verbatim. `python3 tools/coverage_check.py` must exit 0 (expect
   125 rows, 0 errors).
2. FULL gate `python3 tools/e2e_gate.py` — expect byte panel **1136 byte-exact / 0 fail**, negative
   **181/181** with E46K14 `[dr-refuses]` marker UNMOVED, divergence **9/9**, coverage rows 0
   errors, census **15/0/26/0**, prose clean. Record the ACTUALS AS PRINTED, then commit.
   STATUS measured at `8c1d2ee`: the 3 NEW COVERAGE rows are LANDED and
   `coverage_check.py` rc=0 on **125 rows, 0 errors, 0 warnings**; the WIDENING of
   `COND.CMP_LENGTHS_POSITIONAL` and the three labelled SUPERSEDED clauses are still OWED.
3. CLOSE: rewrite HANDOFF/PROGRESS prose (IN FLIGHT → CLOSED + SUPERSEDED), archive the superseded
   prose verbatim from the committed blobs to `docs/history/2026-11-01-e49p2-closed.md` + README
   index row, LEARNINGS close notes, ledger-end pointer past **C341**, `/handoff finalize`.
4. Standing: goldens untouched except this round's; §3 shapes NOT implemented (missing evidence is
   the limit, never a licence to guess); probes ≤71 cols CRLF+`^Z`; `eval $(opam env)` before dune;
   never name a probe variable `c`; no push; never stage/commit/revert the operator's
   `handoff.config.json` edit; renewal values live ONLY in `handoff.config.json` / `/guard status`;
   NO `spec/RUNTIME.txt` row from this round.
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

### SUPERSEDED — E2E-49/P1 closed / await-operator next action (text kept verbatim below, archive at P2 close)

1. Candidate pool (each needs its OWN pre-registered round — hypotheses committed BEFORE
   any oracle run, PROTOCOL). From `spec/lab-evidence/e2e49-p1/RESULTS.md` §3: `?SCCCM` in
   a STORE (either orientation) and any fixed-member store value; member-vs-member
   compares; literal-vs-literal fixed compares; BASED members in conditions; truthiness
   of a FIXED member (bare or qualified — [C332] measured only the VARYING `BIT REQ`); a
   BARE fixed member on the RIGHT of a literal; over-extent in the LITERAL-LEFT
   orientation and over-extent INITIAL/STORE; `^( ... )` composition. Still open from
   `spec/lab-evidence/e2e48-p2e/RESULTS.md` §3: `^=` over a ladder, bare `-0` spelling,
   runtime length rewrite, empty-varying PUT output, `BIT REQ` acceptance elsewhere, PUT
   EDIT of a bit item. Separate recorded debts, NOT arms: CREATE's `%include` front-end
   gap and LOAN2's scope-aware prescan (PROGRESS → Pending).
2. A successor session WITHOUT an operator instruction: confirm HEAD and tree
   (`git rev-parse HEAD && git status --porcelain=v1`), verify checkpoint freshness
   (`/handoff verify`), and STOP — record state, do not invent work.
3. Standing: goldens untouched except newly added round goldens; §3 shapes NOT
   implemented (missing evidence is the limit, never a licence to guess); probes ≤71
   cols CRLF+`^Z`; `eval $(opam env)` before dune; never name a probe variable `c`; no
   push; never stage/commit/revert the operator's `handoff.config.json` edit; renewal
   values live ONLY in `handoff.config.json` / `/guard status`.

## Unfinished operations

- **E2E-49/P2 IN FLIGHT** — arm 1 LANDED byte-exact (`b1e9221`) and step-6 part 1 is committed
  (claims C337..C341, SPECIMENS, INVENTORY 1136, census re-snapshot, at `0abf1c1`); the COVERAGE
  rows and the FULL compile-tier gate are OWED, and the gate has never been run this round — no
  gate result may be quoted for it.

## Discoveries not yet incorporated

- Compiler law: `spec/CLAIMS.md` C309..C336 — the E2E-49/P2 claims C337.. are OWED at
  step 6, to be derived ONLY from `spec/lab-evidence/e2e49-p2/RESULTS.md` §2 (rounds
  derive from their own RESULTS §2 ONLY). Method lessons accepted in `LEARNINGS.md`
  (E2E-49/P2 session section): parking is a per-shape property (enumerate MECHANISMS
  when laws coincide); the equal-extent collapse `06 n/78` is member-vs-member ONLY;
  `cmp -l` is octal/1-based. FALSIFIED, kept as written in RESULTS §1 + HYPOTHESES:
  forms H-S and H-M. The stale `README.md` rolling status remains recorded as deferred
  work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 76
checkpoint-id: g76-d9076dc64171
checkpoint-kind: auto
content-delta: none
readiness: unattested
status: checkpoint (guard level 4, remaining ~4969, session 01a194f5-edec-7103-bf3c-ac8e3f151b95)
checkpointed: 2026-11-01T02:56:49.078Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 9cd347d4f86346ec1f925955da656415b46bb71ad5e9a6d98036a454f49b7cc5
source-handoff: c1dfe8ed160e76ba78d09990a57e38cb9ccb001c949e97acdc1d1cd02e0c2dd5
source-learnings: b60cfc454e4ae25fa7b137c38ce5dd07f534045a8c5e4f0b869673b7e3eb440f
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


### Last verified state
guard level 4; checkpoint requested (auto at level 4)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P2 [step 6 part 2]: COVERAGE rows, FULL gate, then CLOSE

1. COVERAGE rows in `spec/COVERAGE.tsv` (exact plan in PROGRESS → Current phase): 3 NEW rows
   (`COND.FIXED_MEMBER_MEMBER_TEST` MEASURED EXACT:5; `COND.FIXED_CMP_EQUAL_EXTENT_COLLAPSE`
   MEASURED EXACT:3 with the scope warning in its boundary; `COND.CMP_INVERSION_SELECTS_SLOT`
   SINGLE_SAMPLE EXACT:2), widen `COND.CMP_LENGTHS_POSITIONAL` (+E49B3,E49B4, EXACT:8), and append
   labelled SUPERSEDED clauses to the boundary columns of `COND.FIXED_MEMBER_TEST_SCCCM`,
   `COND.FIXED_MEMBER_LEFT_TEST` and `COND.BIT1_NEG_TEST` (each still calls member-vs-member
   unmeasured/refused), originals verbatim. `python3 tools/coverage_check.py` must exit 0 (expect
   125 rows, 0 errors).
2. FULL gate `python3 tools/e2e_gate.py` — expect byte panel **1136 byte-exact / 0 fail**, negative
   **181/181** with E46K14 `[dr-refuses]` marker UNMOVED, divergence **9/9**, coverage rows 0
   errors, census **15/0/26/0**, prose clean. Record the ACTUALS AS PRINTED, then commit.
3. CLOSE: rewrite HANDOFF/PROGRESS prose (IN FLIGHT → CLOSED + SUPERSEDED), archive the superseded
   prose verbatim from the committed blobs to `docs/history/2026-11-01-e49p2-closed.md` + README
   index row, LEARNINGS close notes, ledger-end pointer past **C341**, `/handoff finalize`.
4. Standing: goldens untouched except this round's; §3 shapes NOT implemented (missing evidence is
   the limit, never a licence to guess); probes ≤71 cols CRLF+`^Z`; `eval $(opam env)` before dune;
   never name a probe variable `c`; no push; never stage/commit/revert the operator's
   `handoff.config.json` edit; renewal values live ONLY in `handoff.config.json` / `/guard status`;
   NO `spec/RUNTIME.txt` row from this round.
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

### Guard notes
E2E-49/P2 IN FLIGHT at 1416f52 (HEAD; goldens+RESULTS at 62f5622, pre-registration 3bd9417, fill-in 586c240). Oracle measured: 5 ok / 5, NO dr-refuses, all five my-gap. NEXT ACTION = ARM 1 exactly per spec/lab-evidence/e2e49-p2/RESULTS.md s2 (plan in HANDOFF Next-action + PROGRESS Current phase): op_mov_a_b=0x78; str_cmp_shape_fix_mm matching ONLY (ImemF,ImemF) qualified-qualified (any BARE side keeps refusing, s3); head 21 *D(left)/E5/21 *D(right)/D1; MVI B capl then MOV A,B iff capl=capr else MVI A capr; CD ?SCCCM; skip C2/CA fill->next; NO prescan change. Verify whole-file cmp vs golden/e49p2 for all five, E48/E49 sweeps, full INVENTORY panel (expect 1131 current + 5 new), refusals rc=2, E46K14 marker unmoved; commit arm alone. Then STEP 6: claims C337.. from s2 ONLY, SPECIMENS bank, --update-inventory, census, COVERAGE, FULL gate (expect 1136), record ACTUALS, CLOSE (archive prose to docs/history/2026-11-01-e49p2-closed.md, ledger-end pointer past C336, /handoff finalize). Both pre-registered forms were FALSIFIED (fourth shape: stack parking E5/D1); equal-extent collapse is member-vs-member ONLY -- never extend to the literal template (unmeasured). No RUNTIME row; no push; never touch the operator handoff.config.json edit.
<!-- guard:end checkpoint -->
