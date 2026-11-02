# Functional Results — what has actually been executed

**E2E-50/P2 step 7 deliverable** (2026-11-02). A deliberately SMALL report.

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
| TABLE-00 | B | SOURCE→…→RUN→ASSERT | **FAIL** | `undefined` | compile, link (zero `UNDEFINED` lines), run all succeeded; the ASSERT differs by the **terminal lone `\r`** the harness anchor law leaves behind (framing, see §2) |
| TABLE-01 | B | SOURCE→…→RUN→ASSERT | **FAIL** | `undefined` | same, plus the measured DR PLILIB 79-column print-wrap (framing, see §2) |
| census probe | A | substrate probe | *measured, not a verdict* | — | both linked `.COM`s call **BDOS 25 first** (PLILIB init); the free core refuses typed ⇒ a PLILIB program cannot run on lane A today |

Step-7 re-probes (`step7/RESULTS.md` §1–2): the same `TABLE-01` COMPILE+LINK probe now prints **no
foreign line** on the runner's stdout (the cpmcp stdio leak is closed), and `FX-00` still PASSes
with the emulator resolved from the corrected fallback list.

## 2. Why the two lane-B FAILs are not semantic failures

**CONTENT ≡ REFERENCE for both programs.** Every aggregate and the complete sorted multiset
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
first be declared as an independently stated law.

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
