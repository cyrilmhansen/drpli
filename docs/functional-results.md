# Functional Results — what has actually been executed

**E2E-50/P2 step 7 deliverable** (2026-11-02), **FS-01 addendum** (2026-11-02, § 5). A
deliberately SMALL report.

This page **renders** evidence; it is not a ledger and it decides nothing. The authorities are
`spec/lab-evidence/e2e50-p2/step6/RESULTS.md` (execution ACTUALS) and
`spec/lab-evidence/e2e50-p2/step7/RESULTS.md` (the step-7 probes). The law behind every verdict is
`spec/functional/tests/README.md` (schema `pli80-functional/1`), summarised in
`docs/functional-testing.md`. Compiler behaviour itself is claimed ONLY in `spec/CLAIMS.md`;
**nothing on this page is a DR claim, and nothing here promotes a COVERAGE row.**

## 1. Verdicts executed so far

Two lanes, always labelled (lane A = the project's own free 8080/CP/M core, audited in
`docs/emulator-audit.md`; lane B = the historical toolchain — DR `LINK-80` + `PLILIB.IRL` under
cpmsim, user-supplied and never packaged).

| id | lane | stages reached | verdict | attribution | what it means |
|---|---|---|---|---|---|
| FX-00 | A | SOURCE→DERIVATION→RUN→ASSERT | **PASS** | — | hand-encoded substrate fixture; output byte-exact as declared; `--double-run` captures identical (`cmp` rc=0) — the determinism law proved by execution |
| FX-01 | A | SOURCE→DERIVATION→RUN | **FAIL** | `emulator` | INTENDED outcome: the free core has no BDOS 1, and the runner fails typed. A FAIL here is correct evidence, never a pass |
| TABLE-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FS-01; was FAIL at E2E-50/P2 close) | — | all six stages ran with typed success; ASSERT complete-stream match after the harness F1 anchor fix (§ 5) |
| TABLE-01 | B | SOURCE→…→RUN→ASSERT | **PASS** (FS-01; was FAIL at E2E-50/P2 close) | — | revised source (output statements only, § 5) prints three short lines; complete-stream match; determinism double-run byte-equal |
| census probe | A | substrate probe | *measured, not a verdict* | — | both linked `.COM`s call **BDOS 25 first** (PLILIB init); the free core refuses typed ⇒ a PLILIB program cannot run on lane A today |

Step-7 re-probes (`step7/RESULTS.md` §1–2): the same `TABLE-01` COMPILE+LINK probe now prints **no
foreign line** on the runner's stdout (the cpmcp stdio leak is closed), and `FX-00` still PASSes
with the emulator resolved from the corrected fallback list.

## 2. Why the two lane-B FAILs are not semantic failures

As executed at E2E-50/P2 close, **CONTENT ≡ REFERENCE for both programs.** Every aggregate and the complete sorted multiset
(including negatives and duplicates) match the independent `reference.py` derivation byte-for-byte
after normalisation. The mismatch is in the *framing* of the stream, not in the values:

* **F1 — harness anchor law.** The console region is cut at `(?=\nD>)`, so the program's final
  CRLF is split and a lone `\r` survives `collapse-spaces-v1`. A harness artifact; invisible under
  the gate's substring law, exposed by the deliberately stricter stream law as designed.
* **F2 — DR PLILIB print-wrap law (measured).** An 8-item `PUT LIST` line wraps after item 6 at 79
  columns; the wrap CRLF is guest-written (proven from the transcript's pty-side doubling). This is
  historical-runtime formatting, **not** a compiler defect and **not** `my-gap`. Promoting it to a
  claim needs its own pre-registered oracle round, which step 6 was not authorised to run.

Expectations were **never** edited to match a capture (law L3). If TABLE-01 is to pass, F2 must
first be declared as an independently stated law. *(FS-01 supersession, § 5: TABLE-01 later
passed by **isolating the test from F2** — a declared output redesign keeping every line inside
the measured wrap — not by declaring the wrap law, which stays `proposed`.)*

## 3. Honest limits of this page

* Four executed verdicts, from one round, on two programs and two substrate fixtures. That is a
  **foundation**, not coverage: the v1 perimeter (what a spec may even declare) is fixed by
  `spec/COVERAGE.tsv`, and the corpus is 2 programs of one family.
* Attribution of an ASSERT mismatch is hard-wired to `undefined` — narrowing it to
  `runtime-lib` needs a discriminating run that has not happened.
* Lane B runs on the **historical** toolchain; lane A cannot host PLILIB programs (BDOS 25 at
  init), so the two lanes are not interchangeable and a lane-A PASS proves nothing about PLILIB.
* Evidence roots live in ignored working state (`build/functional/<stamp>/`); the committed
  `RESULTS.md` files are the durable record. Re-running the harness produces a new stamped root,
  never a rewrite of the record.
* Nothing on this page changes the byte-exactness mission in `GOAL.md`: byte-exact and
  functionally-correct remain two independent axes, and both must be earned separately.

## 4. Open items feeding the next round (P3 candidates, proposals only)

1. Declare F2 (print-wrap) from the oracle side, then re-declare TABLE-01's expectation from law,
   not capture — that is what would turn the lane-B FAIL into a real verdict.
2. Fix F1 in the harness (the anchor law should not consume the program's trailing newline) and
   pin both directions in the hostile suite.
3. Free-core support for BDOS 25 (and then the full linked-program BDOS census) to open lane B on
   lane A's substrate — subject to the operator's package/license decision in
   `docs/emulator-audit.md` §6.
4. TABLE-02 is still **withheld**: "verified" in this project means executed evidence, not
   "compiles".

## 5. FS-01 (2026-11-02): the first two functional PASSes

Bounded operator mission: obtain verified functional PASSes for TABLE-00/TABLE-01 under lane B,
testing program behaviour, not the historical formatting details. The P2 FAIL evidence is
**preserved** (`spec/lab-evidence/e2e50-p2/step6/RESULTS.md` §2; baseline reproduction under
`build/functional/fs01-baseline/` reproduces both FAIL frames verbatim).

* **F1 fixed in the harness** (no scientific byte touched): the lane-B console extraction no
  longer cuts the program's final CRLF at the prompt anchor. New law
  `NAME[^\n]*\r\r\n(.*?)(?=D>|I/O ran|\Z)` **retains the program's trailing newline** and still
  never captures the prompt; a region whose terminator is **not** preceded by a newline is an
  ambiguous cut — `RUN UNKNOWN console-terminator-ambiguous`, never PASS. The normalization,
  split and complete-stream laws are unchanged: extra, missing or residue lines still FAIL
  (hostile suite C15, 12 new checks; suite 182 → **194**, all passing).
* **F2 isolated, not characterized**: the TABLE-01 program's **output statements only** were
  revised — the sorted values now print on two short labelled lines (`SORTED 1-4:`,
  `SORTED 5-8:`, ~54 raw columns each, far inside PLILIB's measured 79-col wrap). Algorithm,
  inputs and invariants (ordering, multiplicity, sum, count, extremes) are unchanged. PLILIB's
  wrap law is **not** promoted by this revision; it remains proposed, awaiting its own oracle
  round.
* **Expectation by derivation, never capture (L3)**: the new expected lines follow from the
  **declared output design** plus the README § 6 format law (fixed numerics in right-justified
  fields, literals at natural width, single blank between items) via
  `reference.py:table01`; the run then *confirmed* the prediction (raw od shows the exact
  10-column field layout the law derives).
* **Executed verdicts** (git HEAD `876ed9e`; compiler `pli80c.exe`
  sha256 `edce9e0e…`; TABLE-01.PLI rev FS-01 sha256 `4881f187ef1ad9651c48950b76a6cdd959fdcc980ef989580a0fbfa43c0b0863`,
  1366 bytes, CRLF/^Z/≤71 cols):

  | test | COMPILE | LINK | RUN | ASSERT | evidence root |
  |---|---|---|---|---|---|
  | TABLE-00 | pass, .REL 896 B (code=358 data=30) | pass, `TABLE00.COM` 7552 B, `parse_undefined=[]` | pass, done witness, 93 console bytes | pass, complete-stream match (2 lines) | `build/functional/fs01/TABLE-00-20261102T053612Z/lane-B/` |
  | TABLE-01 | pass, .REL 1536 B (code=644 data=50) | pass, `TABLE01.COM` 7808 B, `parse_undefined=[]` | pass, done witness, 178 console bytes | pass, complete-stream match (3 lines) | `build/functional/fs01/TABLE-01-20261102T053620Z/lane-B/` |

* **Determinism**: `--double-run` — both programs PASS again with byte-equal second console
  capture (`build/functional/fs01-double/`). **Lane A unchanged**: FX-00 PASS, FX-01
  FAIL attr=`emulator` as intended (`build/functional/fs01-laneA/`).
* Commands: `python3 tools/test_functional_runner.py`; `python3 tools/functional_runner.py
  --lane B --tests TABLE-00 TABLE-01 --evidence build/functional/fs01` (+`--double-run` and
  `--lane A --tests FX-00 FX-01` variants). No compiler, oracle, gate, COVERAGE, CLAIMS or
  historical-evidence file was modified.

**Remaining functional limitations** (unchanged by FS-01): attribution of assert mismatches is
still hard-wired `undefined` (no discriminating run); the v1 PLILIB wrap law is undeclared and
unclaimed; the free core still cannot host PLILIB programs (BDOS 25 at init); the corpus is two
programs of one family — a foundation, not coverage; no functional PASS promotes a COVERAGE row
or becomes a DR claim.
