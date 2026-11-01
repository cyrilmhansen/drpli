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

## Next action — E2E-49/P4: STEP 6 ALL LANDED; ONE step OWED: CLOSE per PLAN §6, then STOP

1. STATE (authoritative: `PROGRESS.md` Current phase STATUS 2026-11-01 renewal-5):
   step 6 is COMPLETE end to end — claims `aec53e1` (C348..C351) + ledger corrections
   `9c42f3b` (four labelled P4 CORRECTION blocks) + registration `cc43963` (SPECIMENS
   +24, sanctioned `--update-inventory` panel **1174**, census re-snapshot counts
   UNCHANGED 15/0/26/0) + COVERAGE part 2a `dbaf004` (four rows, **133/0/0**) + part
   2b `5aeac87` (EXTENDED CMP_LENGTHS_POSITIONAL to EXACT:14 + four labelled
   SUPERSEDED/WIDENED clauses, quotes byte-checked vs pre-edit blob) + part 2c
   `5b0ccde` (labelled WORDING CORRECTION at [C348]; `<=` is sampled at 3/3 — F3 —
   only equal-attribute `>` was NEVER sampled; the superseded 55053bd message wording
   stands as written, recorded traceably). FULL compile-tier gate **rc=0 measured at
   HEAD `5b0ccde`**, ACTUALS AS PRINTED: byte panel **1174 byte-exact / 0 fail of
   1174** (all 24 e49p4 specimens BYTE-EXACT 256 bytes), negative **181/181**
   (E46K14 `[dr-refuses]` UNMOVED), divergence **9/9**, coverage **133 rows 0/0**,
   census UNCHANGED, prose **5 files clean**; `dune build` rc=0.
2. NEXT CONCRETE STEP — THE CLOSE ONLY (PLAN §6): (a) identify the superseded prose
   generations — the arms-era HANDOFF/PROGRESS sections and this step-6-era prose —
   and archive them VERBATIM into `docs/history/2026-11-01-e49p4-closed.md`, EACH
   block byte-verified against its stated git range (use `git show <range>:<file>`;
   verify BEFORE replacing; the two-generation P3 close
   `docs/history/2026-11-01-e49p3-closed.md` is the pattern); (b) rewrite
   HANDOFF.md (Closed-state section, ONE Next action = the no-active-round stub:
   successor without operator instruction confirms HEAD/tree, `/handoff verify`,
   records state, STOPS; candidate pool: RESULTS §3 named refusals, STORE/BASED/
   truthiness/literal-vs-literal, `<>`/`><`, `^( > )`/`^( >= )`/`^( ^= )`, equal-
   attribute `>` collapse, bank-the-negated-refusals proposal) and PROGRESS.md
   (P4 CLOSED record; P2/P3 previous-phase prose moves to history); update
   LEARNINGS.md only if new findings arise during the close; (c) add the
   `docs/history/README.md` index row; (d) run `handoff_finalize`; (e) STOP. No P5
   without operator authorization.
3. Standing boundaries: operator authorization covers arms→consolidation→CLOSE across
   renewals; NOT P5, NOT push, NOT STORE/BASED/truthiness/literal-vs-literal/runtime
   (RESULTS §3 shapes keep refusing BY NAME). Byte tier only. `eval $(opam env)` before
   dune; goldens untouched (golden/e49p4 complete since `13fca5b`); never git
   clean/reset/add -A; the dirty handoff.config.json is the OPERATOR's standing edit —
   never touch/stage/commit/revert it.

## Unfinished operations

- **CLOSE OWED** (renewal-5 checkpoint boundary, HEAD `5b0ccde` + this prose):
  step 6 is COMPLETE and gate-verified (see Next action 1). The tree is dirty ONLY
  in the guard-managed blocks of HANDOFF.md/PROGRESS.md, this prose, and the
  operator's `handoff.config.json` standing edit. Remaining work is the CLOSE
  sequence in Next action 2 (byte-verified two-generation archive into
  `docs/history/2026-11-01-e49p4-closed.md`, rewrite HANDOFF/PROGRESS/LEARNINGS,
  README index row, ONE Next action, `handoff_finalize`, STOP). Nothing in `ocaml/`
  is half-edited; no scientific byte awaits verification.
- (none else) — ledger ENDS at C351 with the [C348] correction landed; no claim ids
  owed; registration/coverage debts all paid.


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
checkpoint-generation: 100
checkpoint-id: g100-f3ad491aa9c1
checkpoint-kind: manual
content-delta: new
readiness: attested
status: checkpoint (guard level 4, remaining ~-3873, session 01a19735-c0cb-71b9-af89-537a8f523410)
checkpointed: 2026-11-01T13:26:46.074Z
source-goal: 730790b648a1e1d14b76243cfe8bc17eea2ba9cd8527f204f9c8d4dbcc527c9d
source-progress: becf1f9fd08520c5585e48de9291ee933b65bed486a305436c295240ff98e0bc
source-handoff: f1f92c45ebfdfd604cca2e36d6c6c25cc8e1b1bbeca656333fdf9000f0aa0302
source-learnings: 7e285c25b3b51b33790f35d55558c64f2139b6f26d24c192c3fc64c636bea140
source-config: 43186947fdaf3f3b9f425f8ce1b144a8227ce1d7bec2b7aeafb32e9f0572dea8


readiness-by: session:01a19735-c0cb-71b9-af89-537a8f523410
readiness-at: 2026-11-01T13:26:46.078Z
readiness-checkpoint: g100-f3ad491aa9c1
### Last verified state
guard level 4; checkpoint requested (renewal refresh (model))

### Unfinished operations
- (none recorded)

### Next action
— E2E-49/P4: ARMS a/b/c ALL LANDED; STEP 6 IN PROGRESS (claims `aec53e1`; registration/inventory/census/COVERAGE/FULL-gate owed), then CLOSE

1. STATE (authoritative: `PROGRESS.md` Current phase STATUS): arm a `c515377`, arm b
   `ec904c1`, arm c `47c2194` — each committed ALONE, whole-file goldens BYTE-EXACT,
   sweep 47/47 at arm c, out-of-scope rc=2 by name (incl. 9 scratch negations), FULL
   gate rc=0 at every arm (panel 1150, e49p4 UNregistered). Step 6 part 1 `aec53e1`:
   claims **C348..C351** from RESULTS §2 ONLY; ledger ENDS at **C351** — no claim ids
   are owed.
2. NEXT CONCRETE STEPS (step 6 remainder; HEAD NOW `9c42f3b` = ledger part 1b: FOUR
   labelled [E2E-49/P4 CORRECTION(S)] blocks at [C335]/[C337]/[C344]/[C346], quotes
   byte-checked; dune rc=0; ocaml/ untouched). DIRTY NOW: tools/e2e_gate.py holds the
   UNCOMMITTED SPECIMENS +24 round-bank block (E49G1..G8/H1..H6/I1..I6/J1..J4 vs
   golden/e49p4/<n>/<n>.REL; P4 had NO separate fill-in commit -- pre-registration
   328eb3f, BASELINE-MINE binary 398fa2c, goldens+RESULTS 13fca5b, repair 9799f1d, arms
   c515377/ec904c1/47c2194). Sequence: (i) run `python3 tools/e2e_gate.py` on that tree
   -- the ACTUAL printed panel governs (expected 1174); all 24 must print BYTE-EXACT
   256 bytes; (ii) sanctioned `python3 tools/e2e_gate.py --update-inventory`;
   (iii) census re-snapshot per the `4b51bc0` recipe (`python3 tools/corpus_census.py`;
   counts expected UNCHANGED 15/0/26/0 -- the gate reprints actuals); commit (i)-(iii)
   as ONE registration commit (4b51bc0 style); (iv) COVERAGE part 2a: FOUR new rows
   COND.FIXED_RELATION_LITERAL (E49G1..G8, EXACT:8, MEASURED, [C348]),
   COND.FIXED_RELATION_QUALIFICATION (E49H1..H6, EXACT:6, MEASURED, [C349]),
   COND.FIXED_RELATION_UNEQUAL_MATRIX (E49I1..I6, EXACT:6, MEASURED, [C350]),
   COND.FIXED_CMP_NEGATED_COMPLEMENT (E49J1..J4, EXACT:4, MEASURED, [C351]); byte tier
   only; `python3 tools/coverage_check.py` rc=0 re-snapshots coverage-stats.json
   (expected 133 rows 0/0); (v) part 2b widenings + labelled SUPERSEDED clauses, quotes
   byte-checked vs the pre-edit blob: COND.CMP_LENGTHS_POSITIONAL EXTENDED +G3..G6
   EXACT:14; COND.FIXED_CMP_QUALIFICATION_INVISIBLE, COND.FIXED_RELATION_MEMBER_PAIR,
   COND.FIXED_MEMBER_MEMBER_TEST, COND.FIXED_CMP_COLLAPSE_BOTH_TEMPLATES; cite [C104]
   NEVER legacy [C027]/[C072]; (vi) part 2c: labelled WORDING CORRECTION at [C348]
   (4df35bb style): its collapse sentence says ALL FOUR relations but enumerates only
   G1/G2 (`<`) and G7/G8 (`>=`); family witnesses F1 `<`, F3 `<=`, G1/G2 `<`, G7/G8
   `>=`; equal-attribute `>` NEVER sampled; RESULTS s2.1 carries the same slip -- quote
   both verbatim, evidence file untouched; (vii) FULL gate rc=0, ACTUALS AS PRINTED;
   then CLOSE per PLAN s6: archive superseded prose (arms-era + step-6-era) byte-
   verified vs stated git ranges BEFORE replacing into docs/history/, rewrite
   HANDOFF/PROGRESS/LEARNINGS, docs/history/README.md index row, ONE active Next
   action, handoff_finalize, STOP.
3. Standing boundaries: operator authorization covers arms→consolidation→CLOSE across
   renewals; NOT P5, NOT push, NOT STORE/BASED/truthiness/literal-vs-literal/runtime
   (RESULTS §3 shapes keep refusing BY NAME). Byte tier only. `eval $(opam env)` before
   dune; goldens untouched (golden/e49p4 complete since `13fca5b`); never git
   clean/reset/add -A; the dirty handoff.config.json is the OPERATOR's standing edit —
   never touch/stage/commit/revert it.

### Guard notes
E2E-49/P4 step 6: ledger part 1b LANDED (9c42f3b — four labelled P4 CORRECTION blocks at [C335]/[C337]/[C344]/[C346], quotes byte-checked; dune rc=0). Docs e13311c. TREE DIRTY ONLY IN: tools/e2e_gate.py UNCOMMITTED SPECIMENS +24 round-bank block + operator handoff.config.json (never touch) + guard blocks. OWED NEXT (exact sequence in HANDOFF Next action 2): (i) python3 tools/e2e_gate.py on that tree — ACTUAL printed panel governs (expected 1174), all 24 e49p4 BYTE-EXACT 256 bytes; (ii) sanctioned --update-inventory; (iii) census re-snapshot (tools/corpus_census.py, counts expected 15/0/26/0); commit (i)-(iii) as ONE registration commit 4b51bc0 style; (iv) COVERAGE part 2a FOUR new rows RELATION_LITERAL(G,H8 EXACT:8)/RELATION_QUALIFICATION(H EXACT:6)/RELATION_UNEQUAL_MATRIX(I EXACT:6)/CMP_NEGATED_COMPLEMENT(J EXACT:4) all MEASURED byte-tier, coverage_check expect 133/0/0; (v) part 2b widenings: CMP_LENGTHS_POSITIONAL EXTENDED +G3..G6 EXACT:14 + SUPERSEDED clauses at FIXED_CMP_QUALIFICATION_INVISIBLE, FIXED_RELATION_MEMBER_PAIR, FIXED_MEMBER_MEMBER_TEST, FIXED_CMP_COLLAPSE_BOTH_TEMPLATES (quotes byte-checked vs pre-edit blob; cite [C104] NEVER legacy); (vi) part 2c labelled WORDING CORRECTION at [C348]: 'ALL FOUR relations' contradicts own G1/G2/G7/G8 enumeration — equal-attribute '>' never sampled; RESULTS §2.1 slip quoted verbatim, evidence untouched; (vii) FULL gate rc=0 ACTUALS AS PRINTED. Then CLOSE per PLAN §6 (two-generation byte-verified archive arms-era+step-6-era into docs/history/, rewrite HANDOFF/PROGRESS/LEARNINGS, README index row, ONE Next action, handoff_finalize, STOP). NEVER push, no P5, byte tier only, eval $(opam env) before dune, never git clean/reset/add -A, never touch handoff.config.json.
<!-- guard:end checkpoint -->
