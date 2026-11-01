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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C341' spec/CLAIMS.md` etc.;
     the E2E-49/P2 block starts at `grep -n '^## C337'` (~line 7699); the E2E-48 family is
     C309..C332, E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341. The ledger CURRENTLY
     ENDS at **C341** — no claim ids are owed. [C330] carries the labelled E2E-49/P1
     CORRECTION append (positional length law); the falsified text is kept as written
     (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p2/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/` and `e2e49-p1/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P2 CLOSED (FULL compile-tier gate rc=0 measured by the closing session at HEAD `d5983e8`, recorded `8926b83`; CLOSE prose + archive in the commit that carries this text)

- Landing chain: pre-registration `3bd9417` (probes E49B1..B5 + HYPOTHESES + BASELINE-MINE
  at `7fa763b`: all five refused rc=2 — every gap `my-gap`) committed BEFORE any oracle
  call; fill-in `586c240`; ONE oracle run 5 ok / 5, NO dr-refuses; goldens + RESULTS
  `62f5622`; docs `1416f52`; ARM 1 (codegen only, landed ALONE) `b1e9221` — five `.REL`
  whole-file BYTE-EXACT, E48/E49 sweep 61/61, registered-panel sweep 1131/1131,
  out-of-scope refusals rc=2, E46K14 marker UNMOVED; step 6 part 1 `0abf1c1` (claims
  C337..C341 from RESULTS §2 ONLY, SPECIMENS bank, `--update-inventory` 5 rows — panel
  1136 — census re-snapshot counts UNCHANGED); part 2a `8c1d2ee` (3 new COVERAGE rows);
  part 2b `d5983e8` (`COND.CMP_LENGTHS_POSITIONAL` widened to EXACT:8 + three labelled
  SUPERSEDED clauses); gate-record commit `8926b83`. Working tree at this boundary: ONLY
  the operator's `handoff.config.json` edit, the guard's managed blocks and this prose.
- FULL compile-tier gate ACTUALS AS PRINTED at `d5983e8` (rc=0): byte panel **1136
  byte-exact / 0 fail of 1136** (E49B1..B5 each `BYTE-EXACT ... (256 bytes)`); negative
  panel **181/181 refused**, E46K14 prints `refused [TBD] (comparison of the internal
  CHARACTER member REC.LINE) [dr-refuses]` — pinned marker UNMOVED; divergence panel
  **9/9**; coverage `coverage_check: 125 rows, 0 errors, 0 warnings`; census counts
  UNCHANGED **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**; file prose **5 active
  files clean**. `dune build` rc=0. Runtime/link-run tiers remain delegated to the
  external rune-ci builders (unchanged policy). BYTE TIER ONLY: no `spec/RUNTIME.txt`
  row came or comes from this round.
- Science landed: [C337] member-vs-member TEST takes `?SCCCM` with BOTH cells PARKED ON
  THE STACK (`21 *D(left)/E5/21 *D(right)/D1`) — parking is a per-shape property, `EB` is
  measured only vs a pooled literal, both pre-registered forms falsified; [C338]
  equal-extent collapse `06 n / 78` MEASURED member-vs-member ONLY (scope warning in the
  claim and in the COVERAGE boundary: the literal template KEEPS two immediates, the
  equal-length literal case is [TBD]); [C339] positional length law on an all-member pair
  (MIN/MAX/class readings dead); [C340] the written side selects the `*D` relocation slot;
  [C341] head size follows the length pair and a member pair pools NO literal (DATA 000C,
  [C314]).
- Superseded prose — the P2 in-flight sections AND the surviving P1 closing-era sections
  (self-labelled "archive at P2 close"), the stale P1-era next-action stub, the
  P1-frozen Verified evidence and the P1-era Blockers wording — archived verbatim in
  `docs/history/2026-11-01-e49p2-closed.md`. Goldens untouched except this round's
  `golden/e49p2`.

## Next action — E2E-49/P3 step 6: part 1 DONE (`4b51bc0`); remaining = COVERAGE (2a/2b), FULL gate record, CLOSE

1. DONE: arms a `a540fa7` / b `0a1b80c` / c `cde3258` (each ALONE, 14/14 goldens
   whole-file BYTE-EXACT, gate rc=0 at each; E49E1/E2 needed NO code). STEP 6 PART 1
   `4b51bc0`: claims **C342..C347** from `spec/lab-evidence/e2e49-p3/RESULTS.md` s2 ONLY
   (one claim per numbered law; ledger now ENDS at C347) + labelled CORRECTION appends,
   originals verbatim, at [C335] (bare RIGHT admitted), [C336] (literal-LEFT over-extent
   measured), [C337] (bare sides AND relations beyond `=`/`^=`), [C338] (scope warning
   dead); SPECIMENS +14; sanctioned `--update-inventory` -> panel **1150** (+14 rows);
   census re-snapshot counts UNCHANGED 15/0/26/0 (head `1da795d`, md5 `335d69c6`). FULL
   compile-tier gate **rc=0 measured at `4b51bc0`**, ACTUALS AS PRINTED: byte panel
   **1150 byte-exact / 0 fail of 1150** (all fourteen print `BYTE-EXACT ... (256 bytes)`),
   negative **181/181** (E46K14 pinned marker UNMOVED), divergence **9/9**, coverage
   **125 rows, 0 errors, 0 warnings**, census unchanged, prose **5 active files clean**;
   `dune build` rc=0. No `ocaml/` byte changed in part 1.
2. REMAINING — PART 2a (commit ALONE): FOUR NEW COVERAGE rows in `spec/COVERAGE.tsv`:
   `COND.FIXED_CMP_COLLAPSE_BOTH_TEMPLATES` (E49C1..C4, EXACT:4, MEASURED, [C342]/[C343]),
   `COND.FIXED_CMP_QUALIFICATION_INVISIBLE` (E49D1..D4, EXACT:4, MEASURED, [C344]),
   `COND.FIXED_CMP_OVER_EXTENT_LITERAL_LEFT` (E49E1,E49E2, EXACT:2, SINGLE_SAMPLE, [C345]),
   `COND.FIXED_RELATION_MEMBER_PAIR` (E49F1..F4, EXACT:4, MEASURED, [C346]); then
   `python3 tools/coverage_check.py` rc=0 (expect 129 rows, 0 errors). PART 2b (commit
   ALONE): widen `COND.CMP_LENGTHS_POSITIONAL` (+E49F2,E49F4 -> EXACT:10, provenance
   +[C346] +e2e49-p3 RESULTS, EXTENDED clause) and add labelled SUPERSEDED clauses
   (falsified text verbatim, PROTOCOL #2) to `COND.FIXED_MEMBER_TEST_SCCCM` (CA + collapse
   measured on THIS template; bare RIGHT admitted), `COND.FIXED_MEMBER_BARE_LEFT`
   ("left side only" was MY evidence boundary), `COND.FIXED_CMP_OVER_EXTENT` (literal-LEFT
   measured), `COND.FIXED_MEMBER_MEMBER_TEST` (bare sides; relations beyond `=`/`^=`),
   `COND.FIXED_CMP_EQUAL_EXTENT_COLLAPSE` (scope warning dead). 15 columns per the file
   header (id category construct contract perimeter manual_ref dr_status mine_status
   rel_parity runtime probes corpus boundary confidence provenance); no tabs inside fields,
   probes must be panel keys, every [Cnnn] must exist; model commits `8c1d2ee` / `d5983e8`.
3. FULL gate at the final part-2 tree, record ACTUALS AS PRINTED in a gate-record commit
   updating PROGRESS (model `8926b83`), then CLOSE: archive superseded prose verbatim to
   `docs/history/`, rewrite HANDOFF/PROGRESS to CLOSED, LEARNINGS close notes,
   `/handoff finalize`.
4. Standing: probes ≤71 cols CRLF+`^Z`; `eval $(opam env)` before dune; no var named `c`;
   goldens untouched except e49p3; NO spec/RUNTIME.txt row from the compare families;
   never touch the operator's `handoff.config.json` edit; renewal values ONLY in
   `handoff.config.json` / `/guard status`; no push.

## Unfinished operations

- (none) — E2E-49/P2 is CLOSED: arms, claims C337..C341, registration (panel 1136),
  COVERAGE (125 rows, 0 errors) and the FULL compile-tier gate (rc=0 measured at
  `d5983e8`, recorded `8926b83`) all landed. Standing debts live in `PROGRESS.md` →
  Pending; the candidate pool lives in the Next action above.

## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P2 discovery is incorporated: laws C337..C341 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p2/RESULTS.md` §2), the
  COVERAGE rows and labelled SUPERSEDED clauses in `spec/COVERAGE.tsv` (125 rows, 0
  errors). Open PROPOSALS (classified `proposed` in `LEARNINGS.md`, NOT law): bank the
  out-of-scope member-vs-member refusals as NEG-panel rows; "emit the head as ONE bundled
  thunk in written order" stays a codegen invariant evidenced per-shape — no ledger claim
  until discriminating probes exist. The stale `README.md` rolling status remains recorded
  as deferred work in `PROGRESS.md` → Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 82
checkpoint-id: g82-eb070d852cef
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 2, remaining ~9730, session 01a195fd-fc1b-7195-ad35-f2d9fed8e5b7)
checkpointed: 2026-11-01T07:47:06.190Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 48a8de5ecac96154fb79e4e692eb3312bacee30d36b8179dd40b83fddbbe8f5f
source-handoff: dd029d2a91aea64d93c7fd540cfc274109a1c702602ecc3ce2b10be5aca54d83
source-learnings: 429a1fdac726660656c505cec218e5de3240902bd8316ee9648ee46fa987b766
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a195fd-fc1b-7195-ad35-f2d9fed8e5b7
readiness-at: 2026-11-01T07:47:06.193Z
readiness-checkpoint: g82-eb070d852cef
### Last verified state
guard level 2; checkpoint requested (renewal tool refresh)

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P3 step 6 IN FLIGHT: claims, registration, COVERAGE, FULL gate; then CLOSE

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

### Guard notes
E2E-49/P3 ARMS ALL LANDED at HEAD 1da795d (arm a a540fa7, arm b 0a1b80c, arm c cde3258, docs checkpoint 1da795d): 14/14 golden/e49p3 objects whole-file BYTE-EXACT, FULL gate rc=0 at arm c (panel 1136/0, neg 181/181 E46K14 marker UNMOVED, div 9/9, cov 125/0/0, census 15/0/26/0, prose 5 clean), dune build rc=0, working tree clean except the operator's handoff.config.json edit. NEXT = STEP 6 ONLY (exact procedure in HANDOFF.md -> Next action item 2): claims from C342 derived ONLY from spec/lab-evidence/e2e49-p3/RESULTS.md s2 (ledger ends at C341, ~line 7699 block is P2's, mimic C337..C341 format); SPECIMENS +14 in tools/e2e_gate.py in the E49A/E49B round-bank style citing pre-registration 3659f5d (probes/E49{C1..C4,D1..D4,E1..E2,F1..F4}.PLI -> golden/e49p3/<N>/<N>.REL); sanctioned python3 tools/e2e_gate.py --update-inventory (panel 1136->1150); census re-snapshot per commit 0abf1c1's recipe; COVERAGE rows + labelled SUPERSEDED clauses (C338 scope, P1 left-side-only asymmetry, relations-beyond-=/^=) with originals verbatim per PROTOCOL #2; FULL compile-tier gate with ACTUALS AS PRINTED; then CLOSE per HANDOFF item 3 (archive superseded prose verbatim to docs/history/, rewrite HANDOFF/PROGRESS to CLOSED, LEARNINGS close notes, /handoff finalize). Discipline: no spec/RUNTIME.txt rows; bare-in-relation and every RESULTS s3 shape keep refusing; never touch the operator's handoff.config.json edit; no push.
<!-- guard:end checkpoint -->
