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
   - `spec/CLAIMS.md`: read ONLY cited claim ids — `grep -n '^## C347' spec/CLAIMS.md` etc.;
     the E2E-49/P3 block starts at `grep -n '^## C342'`; the E2E-48 family is C309..C332,
     E2E-49/P1 is C333..C336, E2E-49/P2 is C337..C341, E2E-49/P3 is C342..C347. The ledger
     CURRENTLY ENDS at **C347** — no claim ids are owed. [C330] carries the labelled
     E2E-49/P1 CORRECTION append (positional length law); [C335]–[C338] carry labelled P3
     CORRECTION appends and [C346] a labelled CITATION CORRECTION (the numeric ORDER law is
     [C104], never cite legacy [C027]/[C072] in provenance); falsified text is kept as
     written (PROTOCOL #2).
   - `spec/COVERAGE.tsv`: header + `grep` the row KEY being edited (15 columns; schema
     `spec/COVERAGE-SCHEMA.md`; validator rules at `tools/coverage_check.py:203-247`).
   - `spec/INVENTORY.txt`: `grep` the specimen/refusal name only. `spec/RUNTIME.txt` and
     `spec/DIVERGENT.txt`: only rows named by the task.
   - Latest round evidence: `spec/lab-evidence/e2e49-p3/{RESULTS.md,HYPOTHESES.md,BASELINE-MINE.txt}`
     (round CLOSED); prior rounds under `spec/lab-evidence/e2e48-*/`, `e2e49-p1/` and
     `e2e49-p2/`.
5. Do **not** run the compiler, the oracle, LINK-80, cpmsim, Rune CI or `tools/e2e_gate.py`
   unless the session's actual task is compiler development or gate verification.

## Last verified state — E2E-49/P3 CLOSED (FULL compile-tier gate rc=0 measured by the step-6 session at HEAD `4df35bb`, recorded `1f611f5`; CLOSE prose + byte-verified two-generation archive completed by the docs-only closing session — ledger ENDS at C347, byte panel 1150, coverage 129 rows)

- Landing chain: pre-registration `3659f5d` (14 probes E49C1..C4/D1..D4/E1..E2/F1..F4 +
  mkprobes.py + HYPOTHESES + BASELINE-MINE at `685741c`) committed BEFORE any oracle call;
  fill-in `0a46824`; ONE grouped batch run, tag `e49p3`, **14 ok / 14, NO dr-refuses**
  (12 `my-gap`; E49E1/E2 already byte-exact, NO arm); goldens + RESULTS `ad90425`; arms a
  `a540fa7` / b `0a1b80c` / c `cde3258` (each ALONE, 14/14 goldens whole-file BYTE-EXACT,
  gate rc=0 at each); step 6 part 1 `4b51bc0` (claims C342..C347 from RESULTS §2 ONLY,
  labelled CORRECTION appends with originals verbatim at [C335]/[C336]/[C337]/[C338],
  SPECIMENS bank +14, sanctioned `--update-inventory` 14 rows — panel **1150** — census
  re-snapshot counts UNCHANGED); part 2a `8d3b024` (four COVERAGE rows, 129/0/0); part 2b
  `8771e1e` (`COND.CMP_LENGTHS_POSITIONAL` widened to EXACT:10 + five labelled SUPERSEDED
  clauses); part 2c `4df35bb` (labelled CITATION CORRECTION at [C346]); gate record
  `1f611f5`; close-partial `b07be23`; guard refresh `c140277`. Working tree at this
  boundary: ONLY the operator's `handoff.config.json` edit, the guard's managed blocks and
  this prose.
- FULL compile-tier gate ACTUALS AS PRINTED at `4df35bb` (rc=0): byte panel **1150
  byte-exact / 0 fail of 1150** (all fourteen e49p3 specimens print `BYTE-EXACT ... (256
  bytes)`); negative panel **181/181 refused**, E46K14 prints `refused [TBD] (comparison
  of the internal CHARACTER member REC.LINE) [dr-refuses]` — pinned marker UNMOVED;
  divergence panel **9/9**; coverage `coverage_check: 129 rows, 0 errors, 0 warnings`;
  census counts UNCHANGED **EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0**; file prose
  **5 active files clean**. `dune build` rc=0. Runtime/link-run tiers remain delegated to
  the external rune-ci builders (unchanged policy). BYTE TIER ONLY: no `spec/RUNTIME.txt`
  row came or comes from this round.
- Science landed: [C342] the equal-attribute collapse `06 n / 78` is a `?SCCCM`
  LENGTH-PAIR law measured in BOTH literal templates (settles [C338]'s [TBD]; COUNT NOTE:
  RESULTS §2.1 says "six", names seven — recorded in the claim, evidence untouched);
  [C343] `CA` is the `^=` skip on the DIRECT template too and the fill is the next
  statement ([C309]) in all fourteen; [C344] qualification of an internal FIXED member is
  INVISIBLE to every measured compare encoding — bare sides admitted (falsifies the
  [C335]/[C337] bare-side refusals); [C345] over-extent literal written LEFT accepted and
  pooled whole, NO ARM ([C336] transfers by measurement); [C346] ordered relations take
  the same `?SCCCM` helper and stacked parking, ORDER law (`<`/`>=` written, `>`/`<=`
  swapped — the [C104] numeric rule for characters) and BRANCH law (strict JNC `d2`, weak
  JC `da`), lengths positional on the LOWERED operands; [C347] head size follows the
  length pair in every template, DATA stays [C314]'s pool-first frame.
- Superseded prose — the P2 closing-era Last-verified-state, BOTH generations of the P3
  in-flight/close-owed HANDOFF next actions and PROGRESS current phases, the surviving P2
  CLOSED previous-phase record (frozen wording; an identical copy still lives in
  `PROGRESS.md` until the next close), the stale P2-era next-action stub, the P2-frozen
  Verified evidence and the P2-era Blockers wording — archived verbatim, every block
  byte-verified against its stated git range, in
  `docs/history/2026-11-01-e49p3-closed.md`. Goldens untouched except this round's
  `golden/e49p3`.

## Next action — E2E-49/P4: ARMS a/b/c ALL LANDED; STEP 6 IN PROGRESS (claims `aec53e1`; registration/inventory/census/COVERAGE/FULL-gate owed), then CLOSE

1. STATE (authoritative: `PROGRESS.md` Current phase STATUS): arm a `c515377`, arm b
   `ec904c1`, arm c `47c2194` — each committed ALONE, whole-file goldens BYTE-EXACT,
   sweep 47/47 at arm c, out-of-scope rc=2 by name (incl. 9 scratch negations), FULL
   gate rc=0 at every arm (panel 1150, e49p4 UNregistered). Step 6 part 1 `aec53e1`:
   claims **C348..C351** from RESULTS §2 ONLY; ledger ENDS at **C351** — no claim ids
   are owed.
2. NEXT CONCRETE STEPS (step 6 remainder, per spec/lab-evidence/e2e49-p4/PLAN.md §Procedure
   5; commit parts in the P3 style 4b51bc0/8d3b024/8771e1e): (i) SPECIMENS round-bank
   block +24 rows (E49G1..G8/H1..H6/I1..I6/J1..J4 vs golden/e49p4/<n>/<n>.REL) in
   tools/e2e_gate.py — panel expected 1174 but the ACTUAL printed number governs, never
   invent; (ii) sanctioned `python3 tools/e2e_gate.py --update-inventory` (spec/
   INVENTORY.txt rows); (iii) census re-snapshot per the `4b51bc0` recipe (counts UNLESS
   changed are reprinted by the gate); (iv) COVERAGE.tsv rows — byte tier only, widenings
   carry labelled SUPERSEDED clauses with quotes byte-checked against the pre-edit blob,
   provenance ids resolve via tools/coverage_check.py, the numeric ORDER law is [C104]
   NEVER legacy [C027]/[C072]; (v) FULL compile-tier gate rc=0 with ACTUALS AS PRINTED.
   Then CLOSE per PLAN §Procedure 6: archive superseded prose byte-verified vs stated git
   ranges BEFORE replacing (generations: arms-era + step-6-era), rewrite
   HANDOFF/PROGRESS/LEARNINGS, docs/history/README.md index row, exactly ONE active Next
   action, `/handoff finalize`, STOP.
3. Standing boundaries: operator authorization covers arms→consolidation→CLOSE across
   renewals; NOT P5, NOT push, NOT STORE/BASED/truthiness/literal-vs-literal/runtime
   (RESULTS §3 shapes keep refusing BY NAME). Byte tier only. `eval $(opam env)` before
   dune; goldens untouched (golden/e49p4 complete since `13fca5b`); never git
   clean/reset/add -A; the dirty handoff.config.json is the OPERATOR's standing edit —
   never touch/stage/commit/revert it.

## Unfinished operations

- **STEP 6 PARTS 2.. OWED** (renewal-3 checkpoint boundary): tree CLEAN apart from the
  operator's handoff.config.json edit and the guard-managed blocks + this prose; all
  scientific code/golden/claim work through `aec53e1` is COMMITTED and gate-verified.
  Nothing is half-edited in ocaml/. Next action 2 above is the exact owed sequence.
- (none else) — arms a/b/c landed and measured; nothing in ocaml/ awaits verification.


- E2E-49/P3 is CLOSED (historic): arms a/b/c (`a540fa7`/`0a1b80c`/`cde3258`), claims
  C342..C347, registration (panel 1150), COVERAGE (129 rows, 0 errors, 0 warnings), the
  FULL compile-tier gate (rc=0 measured at `4df35bb`, recorded `1f611f5`) and the CLOSE
  (two-generation archive `docs/history/2026-11-01-e49p3-closed.md` byte-verified
  block-by-block, HANDOFF/PROGRESS/LEARNINGS rewritten, `docs/history/README.md` index
  updated) all landed. Standing debts live in `PROGRESS.md` → Pending; the candidate pool
  lives in the Next action above.

## Discoveries not yet incorporated

- (none in the ledger) — every E2E-49/P3 discovery is incorporated: laws C342..C347 in
  `spec/CLAIMS.md` (derived ONLY from `spec/lab-evidence/e2e49-p3/RESULTS.md` §2), the
  four new COVERAGE rows, the widening and the five labelled SUPERSEDED clauses in
  `spec/COVERAGE.tsv` (129 rows, 0 errors, 0 warnings). Open PROPOSALS (classified
  `proposed` in `LEARNINGS.md`, NOT law): bank the out-of-scope member-pair refusals as
  NEG-panel rows; "emit the head as ONE bundled thunk in written order" stays a codegen
  invariant evidenced per-shape — no ledger claim until discriminating probes exist. The
  stale `README.md` rolling status remains recorded as deferred work in `PROGRESS.md` →
  Pending.

## History and pointers

- Superseded next-action sections, closed phase records and the full renewal-hop status
  log: `docs/history/README.md` (index; baseline extraction at `f3a4c60`; P2e closing-era
  prose `docs/history/2026-10-31-p2e-closed.md`; E2E-49/P1 closing-era prose AND the P2e
  close record `docs/history/2026-11-01-e49p1-closed.md`; E2E-49/P2 closing-era prose AND
  the surviving P1 closing-era sections `docs/history/2026-11-01-e49p2-closed.md`;
  E2E-49/P3 two-generation close archive — in-flight prose at `4df35bb` AND the
  close-owed prose at `c140277` — `docs/history/2026-11-01-e49p3-closed.md`).
- Renewal: effective renewal values are in `handoff.config.json` (authoritative) — never
  this file. The guard writes the managed block below via Handoff commands only.

<!-- guard:begin checkpoint -->
checkpoint-schema: 3
checkpoint-generation: 94
checkpoint-id: g94-8a7bc7cdd49f
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~3361, session 01a19707-67fc-71b9-af89-5373c8b376a8)
checkpointed: 2026-11-01T12:38:24.393Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: 946f687217d3fc194cbb3b39236d10a398e9f5eb8baf7e61fcb043a67398479c
source-handoff: 0d708967a5e36b1b2b3f1e180c86d73a1275fd89b4b900e8ca2867b7a509a08c
source-learnings: a33c9d64bb4a8a48f0cd9e5f50412532b66b0a6499894d71ed6c0cb289e479ad
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19707-67fc-71b9-af89-5373c8b376a8
readiness-at: 2026-11-01T12:38:24.397Z
readiness-checkpoint: g94-8a7bc7cdd49f
### Last verified state
guard level 4; checkpoint requested (renewal refresh (model))

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P4 ACTIVE: ARM a LANDED `c515377`; ARM b code-complete (G1..G8 BYTE-EXACT) — verification+commit OWED; then ARM c, step 6, CLOSE

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

### Guard notes
E2E-49/P4 IN FLIGHT, operator-authorized through CLOSE (never push; no P5). TREE STATE: ocaml/lib/codegen.ml has UNCOMMITTED ARM b edits (new encoder str_cmp_shape_fix_lit_rel + caller arm + prescan/refusal annotations) — verified: dune build rc=0, E49G1..G8 ALL whole-file BYTE-EXACT vs golden/e49p4 (direct head fixed to SIX bytes: 11 *D(pool) carries the operand; staged EB rows were exact first try). Handoff prose current in PROGRESS (STATUS block) + LEARNINGS (dated arm notes). NEXT = finish ARM b ALONE: (1) regression sweep A1..A4,B*,C*,D*,E*,F*,H*,I* compile+whole-file cmp (expect 35/35); (2) out-of-scope rc=2: E49J1..J4 (named negated refusal), scratch /tmp bare-member+literal relation (na < 'ABC' — must STILL refuse: arm b admits ImemF only), literal-vs-literal relation, rel-in-STORE; (3) FULL gate python3 tools/e2e_gate.py rc=0 (panel STILL 1150 — e49p4 unregistered; neg 181 E46K14 UNMOVED; cov 129/0/0; census 15/0/26/0); (4) commit ALONE in cde3258/c515377 style citing RESULTS s2.1 per-byte ACTUALS incl. the 6-vs-7-byte direct-head measurement and the FALSIFIED "prescan twins MUST widen" (EqR _ clause already mirrors; [C152] verified). THEN ARM c (spec in PROGRESS/HANDOFF): NegL arm of lower_test_skip0 admits ONLY goldened rewrites ^(Eq)->Ne (literal rows: literal-LEFT, ImemF right, len<=cap only = J3; qualified mm pair = J1), ^(Lt)->Ge qualified mm = J2, ^(Le)->Gt qualified mm = J4 — NO Gt->Le/Ge->Lt/Ne->Eq (no golden; predecessor note FALSIFIED by protocol #4); lower by recursion on synthesized complement EqR expr, zero new bytes; J goldens byte-exact, gate rc=0, commit alone. THEN step 6 per PLAN (claims C348.. from RESULTS s2 ONLY; SPECIMENS +24 in tools/e2e_gate.py, ACTUAL panel governs (expected 1174); sanctioned --update-inventory; census re-snapshot; COVERAGE rows w/ labelled SUPERSEDED clauses, cite [C104] not legacy; FULL gate ACTUALS) and CLOSE per PLAN s6 (byte-verified archive, ledger ends at new last claim). eval $(opam env) before dune; byte tier only; never git clean/reset/add -A; never touch handoff.config.json.
<!-- guard:end checkpoint -->
