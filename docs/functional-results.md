# Functional Results — what has actually been executed

**E2E-50/P2 step 7 deliverable** (2026-11-02), **FS-01 addendum** (2026-11-02, § 5), **FC-01
addenda** (2026-11-02, §§ 6–7). A deliberately SMALL report.

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
| MATH-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA — spec framing defect, § 6) | — | gcd/division/accumulation semantics; complete-stream match incl. [C352] framing blanks (4 lines); double-run byte-equal |
| PROC-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | factorials/fibonacci/helper-value PUT; 3 lines; double-run byte-equal |
| HIST-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | bucket histogram + peak scan; 4 lines; double-run byte-equal |
| PTR-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | self-referential structure chain walk (sums of squares, null test); 2 lines; double-run byte-equal |
| STRNG-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | string rotation + equality hits, CHARACTER member PUT; 3 lines; double-run byte-equal |
| DEC-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | five FIXED DEC(9,2) decimal identities; 2 lines; double-run byte-equal |
| FLT-00 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | six FLOAT BINARY(24) identities; 2 lines; double-run byte-equal |
| TABLE-02 | B | SOURCE→…→RUN→ASSERT | **PASS** (FC-01 hop 3; was FAIL at batchA) | — | LAST-match search, not-found, slice sum, reverse copy; 4 lines; double-run byte-equal |
| BUILTIN-00 | B | SOURCE→DERIVATION→COMPILE | **FAIL** (blocker-probe deliverable) | `compiler` | rev2 measures the built-in LENGTH refusal verbatim; rev1 hit the char-store refusal first — probe fixed at hop 4 (§ 7) |
| STRCAT-00 | B | SOURCE→DERIVATION→COMPILE | **FAIL** (blocker-probe deliverable) | `compiler` | `\|\|` concatenation refuses on the char-store path; message verbatim (§ 7) |
| COND-00 | B | SOURCE→DERIVATION→COMPILE | **FAIL** (blocker-probe deliverable) | `compiler` | `\|`-composed condition refused, the `\|` form shown in the message (§ 7) |
| DEC-01 | B | SOURCE→DERIVATION→COMPILE | **FAIL** (blocker-probe deliverable) | `compiler` | fractional DEC literal in additive position refused (§ 7) |
| FLT-01 | B | rev1 SOURCE→…→ASSERT; rev2 SOURCE→DERIVATION→COMPILE | rev1 **PASS** (probe falsification); rev2 **FAIL** (deliverable) | `compiler` | rev1 compared via a variable — the proven cell route; rev2 puts `(a + b)` DIRECT in the compare and measures the computed-FLOAT-operand refusal (§ 7) |
| EDIT-00 | B | SOURCE→DERIVATION→COMPILE | **FAIL** (blocker-probe deliverable) | `compiler` | PUT EDIT counted `SKIP(1)` refused — only the bare form is sampled (§ 7) |
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
  `spec/COVERAGE.tsv`, and the corpus is 2 programs of one family. *(FC-01 hop 3 supersession,
  § 6: Batch-A adds **8 more executed PASSes** across 6 more families — twelve programs total;
  still a corpus, still not coverage.)*
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

## 6. FC-01 hop 3 (2026-11-02): framing amendment — Batch-A executes 8/8 PASS on lane B

Hop 2 executed the 8 Batch-A programs on lane B: **8/8 FAIL at ASSERT only** — every LINK and
RUN stage ran to its typed witness and EVERY content line matched the reference; the deltas
were stream-framing blank lines. The fc01-framing oracle round then MEASURED the law on DR's
own objects (`[C352]`: a first-statement `PUT SKIP` prints its own leading CRLF; the exit chain
appends exactly one final CRLF unconditionally, also after a final bare `PUT SKIP;` — H2
conditional-flush falsified and kept as written; my FCPS `.REL`s byte-exact to DR's on all
three shapes). The FAILs were therefore classified **spec expectation defects**, not compiler
or runtime gaps. The `build/fc01/batchA/` FAIL records and evidence stay ON RECORD as written —
never laundered (README § 8/§ 9).

* **Schema amendment (representation, derived from [C352], never captured):** `expected.console`
  entries are STRINGS and `""` is a legal entry asserting an **exact blank line** at its
  position; a bare `"!"` is rejected (negatives are `!text`), non-string entries are rejected,
  and the empty-list and **complete-stream laws are NOT weakened** — an extra or missing blank
  still FAILs (`tools/functional_runner.py`; README § 3/§ 4 representation amendment + § 6
  framing-law paragraph citing `[C352]`/FCPS1-3/E29PS1 `[C192]`).
* **Hostile suite:** new case **C16** (16 checks: schema accept/reject; ASSERT PASS on the
  FCPS3 leading-blank and FCPS1 trailing-blank shapes with the captures pinned byte-exact;
  FAIL on unexpected/missing blanks and on a whitespace-only line; `!text` still composes),
  plus the C6 mutation swap (obsolete `""`-rejected pin → non-string and bare-`!` rejections,
  net +1). Suite self-count: **211 checks, all passing** (MEASURED from the run, was 194);
  `python3 tools/test_functional_runner.py` rc=0.
* **Re-derivation:** all 8 Batch-A expectations gain the leading `""` (every program's first
  executed output statement is `put skip list(...)`, verified statement-by-statement against
  the committed sources); **MATH-00** also gains the trailing `""` (final bare `put skip;` +
  the unconditional exit CRLF). The **programs are UNCHANGED** — source shas stand; only
  `reference.py` and the 8 spec JSONs were re-derived (DERIVATION two-way check green before
  any lane ran).
* **Executed verdicts** (git HEAD `7cf920c` as recorded in every record; the harness/spec
  diff was uncommitted at execution and landed immediately after as `51d64bd` + `122981a`;
  compiler `pli80c.exe` sha256 `edce9e0e…`; cpmsim
  sha256 `5b882561…`; evidence root `build/fc01/batchA2/`, ignored working state; every LINK
  `parse_undefined=[]`, every RUN `done` witness):

  | test | COMPILE `.REL` | LINK `.COM` | RUN console | ASSERT |
  |---|---|---|---|---|
  | MATH-00 | pass, 1280 B (code=422 data=18) | `MATH00.COM` 7808 B | 93 B | complete-stream match, 4 lines (leading + trailing blank) |
  | PROC-00 | pass, 1024 B (code=391 data=10) | `PROC00.COM` 7936 B | 57 B | complete-stream match, 3 lines |
  | HIST-00 | pass, 1280 B (code=526 data=40) | `HIST00.COM` 7808 B | 107 B | complete-stream match, 4 lines |
  | PTR-00 | pass, 768 B (code=339 data=14) | `PTR00.COM` 7552 B | 52 B | complete-stream match, 2 lines |
  | STRNG-00 | pass, 768 B (code=289 data=101) | `STRNG00.COM` 7552 B | 34 B | complete-stream match, 3 lines |
  | DEC-00 | pass, 1792 B (code=625 data=54) | `DEC00.COM` 8320 B | 20 B | complete-stream match, 2 lines |
  | FLT-00 | pass, 1024 B (code=387 data=40) | `FLT00.COM` 8320 B | 20 B | complete-stream match, 2 lines |
  | TABLE-02 | pass, 1280 B (code=548 data=34) | `TAB02.COM` 7680 B | 93 B | complete-stream match, 4 lines |

* **Determinism:** `--double-run` over all eight → 8/8 PASS again, second console captures
  byte-equal (`build/fc01/batchA2-double/`). **Unchanged specs unaffected:** FX-00, FX-01,
  TABLE-00, TABLE-01 pass SOURCE+DERIVATION under the new validator (bounded ceiling ⇒ honest
  UNKNOWN verdicts, never PASS).
* Commands: `python3 tools/functional_runner.py --lane B --tests MATH-00 PROC-00 HIST-00
  PTR-00 STRNG-00 DEC-00 FLT-00 TABLE-02 --evidence build/fc01/batchA2
  --json-out build/fc01/batchA2/records.json` (+ `--double-run` variant).
* **Untouched by this hop:** `ocaml/`, all goldens, `artefacts/`, `oracle/disks/`,
  `spec/CLAIMS.md` (ledger still ends at **C352** — no new claim came from execution; the run
  validates expectations, per [C205] it is not a compiler-semantics claim), `spec/COVERAGE.tsv`.
  FCPS1..3 SPECIMENS registration stays owed to a gate hop. No functional PASS here promotes any
  ledger row.

## 7. FC-01 hops 3–4 (2026-11-02): Batch-B blocker probes — measured my-compiler refusals, messages verbatim

Batch B is SIX blocker probes (specs + programs + derivations landed at `2c67c05`), one per
named FC-01 blocker class. A blocker probe's DELIVERABLE is the typed COMPILE FAIL with my
compiler's refusal message recorded VERBATIM (README § 9) — these FAILs are correct evidence,
never failures of the test. Each `expected.console` is the FUTURE design derived from the
declared semantics plus the README § 6 format law and the [C352] framing (leading `""`), never
captured (L3). Sources are CRLF/^Z/≤71 columns; DERIVATION two-way check passed in every record.

**Rev1 run (hop 3)** — git HEAD `38216e3` at execution (spec diff uncommitted, landed
immediately after as `2c67c05`); compiler sha256 `edce9e0e…`; evidence root
`build/fc01/batchB/` (ignored working state, KEPT AS WRITTEN); verdicts PASS=1 FAIL=5:

* `BUILTIN-00` — COMPILE fail, attr `compiler`:
  `Fatal error: exception Failure("codegen: char store from non-literal [TBD]")` — but this is
  the **wrong** refusal: rev1 stored `t = substr(s,1,3)` FIRST and codegen refused the char
  store before the built-in path was reached. Rev2 owed.
* `STRCAT-00` — COMPILE fail, attr `compiler`, same `char store from non-literal [TBD]`
  message. Honest note: the `||` construct itself refuses ON the char-store path (a `char(n)`
  store of a concatenation); the concatenation value path is therefore NOT separately
  isolated by this probe — recorded as measured.
* `COND-00` — COMPILE fail, attr `compiler`:
  `Fatal error: exception Failure("codegen: condition form not in E2E-3b subset [TBD]: (| (cond (= i 2)) (cond (= i 5)))")` —
  the `|` composition named in the message: deliverable met.
* `DEC-01` — COMPILE fail, attr `compiler`:
  `Fatal error: exception Failure("codegen: fractional DEC literal aligned to a decimal partner [TBD] (only an integral literal is pinned in additive or compare position [R608/R507])")` —
  deliverable met.
* `FLT-01` — **UNEXPECTEDLY PASSED** (all six stages): .REL 384 B (code=113 data=14,
  items=152), `FLT01.COM` 7680 B (sha256 `f5d6a3f6…`), 21 console bytes, complete-stream
  match, 2 lines. This is a **probe-design falsification kept as written** (PROTOCOL #2):
  rev1 computed `c = a + b` into a variable and compared the VARIABLE — a proven cell route —
  so the shape under test (the computed expression itself in the compare) was never exercised.
  The PASS says nothing new about the blocker; rev1 records stay on disk, never laundered.
* `EDIT-00` — COMPILE fail, attr `compiler`:
  `Fatal error: exception Failure("codegen: PUT EDIT counted SKIP/PAGE is unsampled [TBD] (only the bare form's second byte 0xFF has been observed)")` —
  `SKIP(1)` named in the expectation is exactly what refused; deliverable met.

**Rev2 run (hop 4)** — the two mis-isolating probes revised and re-run ALONE; git HEAD
`91dd3a7` at execution (spec diff uncommitted, landed immediately after in this commit);
compiler sha256 `edce9e0e…`; evidence root `build/fc01/batchB-rev2/`; verdicts PASS=0 FAIL=2;
both chains stopped at COMPILE (LINK/RUN/ASSERT unrun):

| test | source (rev2) | verdict | refusal message (verbatim) |
|---|---|---|---|
| FLT-01 | `FLT-01.PLI` sha256 `30da237c…`, 1147 B — `if (a + b) = 6.5` DIRECT compare | COMPILE FAIL, attr `compiler` | `Fatal error: exception Failure("codegen: computed FLOAT operand in a comparison is unsampled [TBD] (every DR float compare sample addresses two cells or two formal derefs [R3070-R3077, R3079, FLTPOLY]; a comparison against an accumulator value has none -- so nothing is emitted before this refusal)")` |
| BUILTIN-00 | `BUILTIN-00.PLI` sha256 `8b90ff2c…`, 1094 B — SUBSTR store dropped, `n = length(s)` FIRST | COMPILE FAIL, attr `compiler` | `Fatal error: exception Failure("codegen: expression form not in int subset [TBD]")` |

Both rev2 refusals are the **named blockers themselves** measured: the computed-FLOAT-compare
shape (FLT-01) and the built-in LENGTH call as an expression form (BUILTIN-00). The BUILTIN-00
expectation was re-derived with the SUBSTR item removed — `["", "LEN= 10"]` (the extent law:
`LENGTH` of `char(10)` is 10 whatever is stored); `reference.py:builtin00` updated in the same
commit; the DERIVATION stage passed under both rev2 records. The future designs
(`FLT1OK= 1`, `LEN= 10`) remain asserted expectations for when the blockers are armed.

**Classification and limits.** These FAILs are `my-gap` evidence in the strongest available
functional form: my compiler's own `[TBD]` markers, byte-verbatim, produced through the
lane-B harness chain. They are NOT DR statements — no oracle ran in this hop — so NOTHING is
promoted to a claim: `spec/CLAIMS.md` still ends at **C352**; `spec/COVERAGE.tsv` is unchanged
(133 rows); `ocaml/`, goldens, `artefacts/` and `oracle/disks/` untouched. The rev1 evidence
root `build/fc01/batchB/` stays on disk unmodified beside `build/fc01/batchB-rev2/` —
revisions ADD evidence, they never rewrite it.

Commands: rev1 `python3 tools/functional_runner.py --lane B --tests BUILTIN-00 STRCAT-00
COND-00 DEC-01 FLT-01 EDIT-00 --evidence build/fc01/batchB
--json-out build/fc01/batchB/records.json`; rev2 `python3 tools/functional_runner.py
--lane B --tests FLT-01 BUILTIN-00 --evidence build/fc01/batchB-rev2
--json-out build/fc01/batchB-rev2/records.json`.
