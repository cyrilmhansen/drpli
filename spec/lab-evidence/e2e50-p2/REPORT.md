# E2E-50/P2 — round report (step 8, 2026-11-02)

Authority for the mission and the step sequence: `HANDOFF.md` → Next action (operator mission
brief, bootstrapped 2026-11-02). This report is the round's own summary; it promotes nothing,
claims no DR law (that is `spec/CLAIMS.md`'s job) and adds no verdict beyond the committed
evidence in `step6/RESULTS.md` and `step7/RESULTS.md`.

## 1. Delivered

| step | deliverable | commit |
|---|---|---|
| 0 | documentary bootstrap (P1 close-out inconsistencies measured and fixed) | `459f51e` |
| 1–2 | `docs/emulator-audit.md` (capability matrix 2.1–2.20 + two-package redistribution matrix) | `97ad1f0` |
| 3–4 | `spec/functional/tests/README.md` (schema `pli80-functional/1`, laws L1/L2/L3, stage chain, verdict + attribution law), `docs/functional-testing.md`, TABLE-00/01 + `reference.py` | `a6163ef` |
| 5 p1 | `tools/functional_runner.py` | `8523eda` |
| 5 p2 | `tools/test_functional_runner.py` hostile suite (13 cases) + two harness defect fixes | `d40aafb`, `149c6e2` |
| 6 p1 | pre-registration `step6/PLAN.md`, Lane A fixtures FX-00/FX-01 + generator, `--census` probe, labelled README §3 amendment | `690c3a1` |
| 6 p2 | **execution evidence** `step6/RESULTS.md` (executed hop 6, independently re-verified and committed hop 7) | `68348ac`, prose `ec9d396` |
| 7 | cpmcp stdio debt measured/fixed/re-measured, CLI stdout-grammar pin (suite 171→182), Lane A fallback repaired and proven, `docs/functional-results.md` | `958c204`, `cdc5d13`, prose `545dcf1` |

## 2. MEASURED (executed, not inferred)

* **The functional axis exists and runs.** Four executed verdicts on two lanes: FX-00 **PASS**
  (lane A), FX-01 **FAIL** attr=`emulator` (lane A, the intended outcome and the round's first
  executed typed attribution), TABLE-00/TABLE-01 **FAIL** attr=`undefined` (lane B, ASSERT stage),
  plus a **BDOS census probe** (a measurement, deliberately not a verdict).
* **First functional execution of a DRPLi-compiled PL/I program** — and the first PLILIB program
  run in this project's own round: COMPILE (896 B / 1536 B), LINK (`PLILIB   RQST` present, ZERO
  `UNDEFINED` lines on the FULL segments — the [C137] trap did not apply), `.COM` 7552/7808 B,
  RUN `done` rc=0 under cpmsim (15.9M t-states for TABLE-00).
* **Semantics clean where it matters:** CONTENT ≡ REFERENCE for both programs — every aggregate
  and the whole sorted multiset (negatives + duplicates) match the independently written
  `reference.py` derivation. The FAILs are *framing*: F1 the harness anchor law leaves a terminal
  lone `\r`; F2 a measured DR PLILIB 79-column print-wrap whose CRLF is proven guest-written.
* **Audit §2.20 determinism law proved by execution:** `--double-run` console captures byte-equal
  (`cmp` rc=0) for FX-00.
* **Audit §2.18 confirmed and strengthened on the real substrate:** on an error path `pli80-run`
  discards output already buffered *before* the failing call (FX-01's discarded capture is 0 bytes
  although the trace shows the banner written at step 3). Failure evidence needs `--trace`.
* **Audit open question 1 answered (partially) by measurement:** both linked `.COM`s issue
  **BDOS 25 as their first call** (PLILIB init) and the free core fails typed — so a
  LINK-80'd PLILIB program cannot run on Package-A's emulator as it stands. The full
  linked-program census is still UNMEASURED.
* **The harness cannot launder noise into evidence:** `Run.export()`'s cpmcp child is redirected
  (measured pre/post fix, prediction committed before the post-fix run); the CLI stdout grammar is
  pinned closed, and the pin is proven NON-vacuous by re-introducing a chatty child — foreign
  chatter is caught while the verdict stays PASS (noise is never evidence in either direction).
* **Fail-closed substrate behaviour works on the real substrate:** Workspace SAFETY refused a /tmp
  evidence root (BLOCKED attr=`host`, no lane executed); absent dependencies name the missing path.
* **Gate verification at HEAD `545dcf1` — compile tier, rc=0, ACTUALS exactly as printed:**
  `e2e gate: 1174 byte-exact / 0 fail of 1174`; `negative panel clean (181/181 refused)` with
  `E46K14: ... [dr-refuses]` UNMOVED; `divergence panel 9/9`; `coverage_check: 133 rows, 0 errors,
  0 warnings`; census `EXACT 15 / DIFFERS 0 / REFUSED 26 / UNEXPECTED 0` (UNCHANGED);
  `file prose check: 5 active files clean`. Independently cross-checked: `grep -c BYTE-EXACT` =
  1174. No scientific byte changed in the round, so the panel is the same one E2E-49/P4 closed.

## 3. FALSIFIED during the round (kept as written, PROTOCOL #2)

* hop-5: `dune build bin/main.exe` yields `pli80-run.exe` — dune rejects the public name; the
  audited binary is `bin/main.exe` (and the install-directory name has no extension).
* hop-5 prose + ledger quotations: the hostile suite "has 148 checks" — the HEAD artifact printed
  **171**. The suite now self-counts (182 with C14) so a document must quote the artifact.
* The pre-registered FX-00 census total "13 calls" — actual 14 (the PLAN's own distribution sums
  to 14; the written total was an arithmetic slip).
* The PROPOSED "pure-PUT needs fn 2 + terminate only" linked-program census — falsified by BDOS 25
  at init (§2).
* Bootstrap-era: commit `4eb6582`'s claim that the `## Discoveries` glued heading pair "does NOT
  exist in the manual region" — falsified by byte read and corrected in `459f51e`.

## 4. UNMEASURED / BLOCKED (the honest perimeter)

* Runtime semantics of anything: this round measured **four** functional verdicts on two programs
  of one family. `spec/RUNTIME.txt` gained no row; no `?SCCCM`/condition runtime semantics are
  claimed (byte tier unchanged).
* Whether TABLE-01's FAIL is compiler, runtime-lib or framing: attribution is hard-wired
  `undefined` until a discriminating run separates them. F2 is a *measurement of behaviour*, not
  yet an oracle-backed law.
* The full linked-program BDOS census (blocked behind BDOS 25 support on the free core).
* TABLE-02 is **withheld**: "verified" here means executed evidence, not "it compiles".
* `len 128`'s root cause (external cpmtools build) — mechanism accepted, cause proposed.
* Package A licensing: the single hard blocker is the operator's decision on the UNLICENSED lab;
  decided by nobody here, and no restricted asset was copied.
* LOAN2's prescan my-gap and CREATE's `%include` front-end gap remain untouched standing debts.

## 5. Bounded P3 proposal (PROPOSALS ONLY — no execution, no authorisation implied)

1. **P3-a Harness anchor fix (F1).** Make the Lane B console extraction keep the program's
   trailing CRLF, pin both directions in the hostile suite, re-run TABLE-00 → expect a real PASS.
   Cheap, no oracle needed, no scientific byte.
2. **P3-b Declare F2 from the oracle side.** A pre-registered probe round on DR measuring PLILIB
   `PUT LIST` wrap/column law (79 columns, 12-column numeric cells, continuation gap); only then
   may TABLE-01's expectation be re-declared **by law**, never by capture (L3). Would give the
   first lane-B PASS and a candidate `spec/RUNTIME.txt` row (runtime tier is delegated to
   `rune-ci`, so promotion needs that builder's evidence).
3. **P3-c Free-core BDOS 25.** Decide (operator) whether the Runes lab is Package-A licensable,
   then whether BDOS 25 (and the rest of the PLILIB init path) is implemented upstream; re-run the
   census probe to complete audit open question 1.
4. **P3-d TABLE-02.** Only after 0/1 verify by execution: add a third program that exercises a
   capability currently DIVERGENT (`TRAVERSAL_RELOAD`) so the functional axis can disagree with
   the byte axis on purpose.
5. **Not proposed:** PLILIB reimplementation, mass benchmark porting, third-party import before
   rights are verified, any COVERAGE promotion without evidence.

## 6. Boundary compliance

`/home/john/pli/*` stayed read-only (lab HEAD `43e38ba` and the same three untracked entries
verified before and after every build; only the lab's ignored `_build` was written). The operator's
`handoff.config.json` edit was never staged, cleaned or reverted. No `git clean`, no `reset --hard`,
no `add -A`; every commit is explicit-path. `GOAL.md` untouched; no compiler implementation change;
no push; no automatic P3. Compiler/LINK-80/cpmsim/emulator processes ran ONLY as the P2 harness
defines them (bounded, isolated evidence roots, lane-labelled): step 6's three commands and step 7's
three probes. The full CP/M runtime tier and Rune CI were not run; the compile-tier gate was run
once, for step 8 verification.
