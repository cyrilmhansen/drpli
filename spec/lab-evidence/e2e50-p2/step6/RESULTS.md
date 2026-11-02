# E2E-50/P2 step 6 — ACTUALS (executed 2026-11-02, renewal hop 6)

Authority: `HANDOFF.md` → Next action (E2E-50/P2 step 6); predictions in `PLAN.md` (committed
BEFORE any run at `690c3a1`). Falsified prediction text stays here and in PLAN.md as written
(PROTOCOL #2). No COVERAGE/CLAIMS/RUNTIME promotion comes out of step 6 (PLAN limit).

## §0 Method and substrate identities

- Lab (READ-ONLY): HEAD `43e38ba` verified BEFORE and AFTER the build; the same three untracked
  entries before and after (`icybox-full_bw.1.log`, `local-icybox-full-0-verify.state`,
  `scripts/view-optimist.sh`). Only the gitignored `_build` was written.
- `dune build bin/main.exe` rc=0 → `/home/john/pli/lab/_build/default/bin/main.exe`
  sha256 `da2b34b9d0125764e39f88bab97441e440f68a7d92dd3dcc62def3e4d53ca676` (pli80-run).
- **FALSIFIED (plan detail, kept):** hop-5 learned prose said `dune build bin/main.exe` produces
  `_build/default/bin/pli80-run.exe` — it does NOT: dune prints `Error: Don't know how to build
  pli80-run.exe` for the public name. The runner therefore received
  `--pli80-run /home/john/pli/lab/_build/default/bin/main.exe` explicitly; the harness records the
  path + hash in its identity block. (The old `_build/install/default/bin/pli80-run` exists from a
  prior `@install`; NOT used — the freshly built binary is the audited one.)
- Evidence roots (ignored working state, NEVER committed): Lane A `build/functional/20261102T002357Z`,
  Lane B `build/functional/20261102T002522Z`, census `build/functional/20261102T002857Z`;
  classification probes `build/functional/probe-full{,2}` (single-test re-runs of TABLE-00/01,
  same verdicts reproduced).
- Commands run (bounded, lane-labelled; never the oracle campaign, never the full runtime tier,
  never Rune CI): `functional_runner.py --tests FX-00 FX-01 --double-run --pli80-run <main.exe>`;
  `functional_runner.py --tests TABLE-00 TABLE-01`; `functional_runner.py --census
  <TABLE00.COM> <TABLE01.COM> --pli80-run <main.exe>`; plus `--stages`-ceiling probes used to
  localise the §3 noise.

## §1 Predictions vs ACTUALS

| id | lane | predicted (PLAN.md) | ACTUAL as measured |
|---|---|---|---|
| FX-00 | A | PASS; stdout `FX-00 CORE OK\r\nBDOS2-OK\r\n`; census {0,2,9,11,12}, **13 calls** (1×9, 10×2, 1×11, 1×12, 1×0), term `bdos:0` | **PASS**. Console capture byte-exact as declared (od verified). Double-run: `run.console.bin` == `run2.console.bin` (`cmp` rc=0) — the audit 2.20 determinism law PROVED EXECUTED for the first time. Trace term `bdos:0` ✓. **CALL COUNT FALSIFIED: actual 14** (1×9 + 10×2 + 1×11 + 1×12 + 1×0 = 14; the PLAN's own distribution sums to 14 — the written total "13" was an arithmetic slip; distribution correct). |
| FX-01 | A | FAIL, attr=`emulator`, stopped at RUN; rc=1, stderr `pli80-run: unsupported BDOS function 1`; stdout DISCARDED (audit 2.18); ASSERT never runs | **FAIL attr=emulator** exactly as intended (first executed typed-attribution case). stderr verbatim ✓; `.discarded-stdout.bin` retained; NO `console.bin`, no ASSERT record (chain stopped at RUN ✓). NEW MEASURED FACT: the discarded capture is **0 bytes** although the trace shows the fn-9 banner ALREADY WRITTEN at step 3 (`BDOS 3 9 0112`, then `BDOS 6 1 0112`) — on the error path the emulator discards even already-buffered prior output, not just pending writes. Audit 2.18 CONFIRMED on the real substrate. |
| TABLE-00 | B COMPILE | pass, ~896 B, `-d` code=358 data=30 | **pass** — `PROGRAM TABLE00 CODE=358 DATA=30 ITEMS=401 -> 896 bytes` (identical to hop 2). |
| TABLE-01 | B COMPILE | pass, ~1536 B, code=627 data=50 | **pass** — `CODE=627 DATA=50 ITEMS=668 -> 1536 bytes`. |
| TABLE-00/01 | B LINK | PASS with parse_undefined(FULL)==[] | **PASS** — `PLILIB RQST` present, ZERO `UNDEFINED` lines in the FULL segment; `.COM` exported 7552 / 7808 B (sha256 pinned in evidence; the [C137] trap did not apply: single-module + PLILIB). |
| TABLE-00/01 | B RUN | done witness rc=0, anchor found | **done** — prompt-sync session returned `D>`, console region extracted; FIRST functional execution of a PL/I program compiled by DRPLi (and first PLILIB program run in this round). CPU 15.9M t-states (TABLE-00) under cpmsim. |
| TABLE-00/01 | B ASSERT | unpredictable; any mismatch stays FAIL/`undefined`, never narrowed | **FAIL attr=`undefined`** both — exactly the pre-registered policy; attribution NOT narrowed (§2 analyses the evidence but the verdict stays `undefined` until a discriminating run). |
| TABLE00/01.COM | census | UNMEASURED hypothesis "pure-PUT needs fn 2 + terminate only" (PROPOSED) | **FALSIFIED + BLOCKER MEASURED.** Both `.COM`s' FIRST BDOS call is **fn 25** (PLILIB init; trace `BDOS 58 25 FFFA`); the audited emulator fails typed `pli80-run: unsupported BDOS function 25`, rc=1, stdout discarded. Audit §4 open question 1 ANSWERED (partial): a LINK-80'd PLILIB program CANNOT run on the free core — blocked at init; the full census on the audited emulator remains UNMEASURED. Audit §4 line 116's "static-only call sites (1, 5, 9, 25)" — fn 25 is now DYNAMIC on the linked-program path (the OPTIMIST census was the transient compiler, a different substrate class). |

## §2 The two framing laws (evidence; no claim promotion in step 6)

CONTENT ≡ REFERENCE, both programs: every value (`SUM= -1 POS= 3 MAX= 12`,
`N= 6 FIRST= 12 LAST= 5`; `SORTED: -3 -3 0 1 4 7 7 12` incl. negatives+duplicates,
`SUM= 25 N= 8 LOW= -3 HIGH= 12`) matches the independent `reference.py` derivation exactly. The
first functional validation of compiler+runtime output is therefore **semantically clean**; the
FAILs are framing only:

- **F1 (harness anchor law).** Lane B extraction cuts the console region with
  `(?=\nD>)`; the program's FINAL CRLF is thus split — the `\n` is consumed with the prompt, the
  `\r` stays in the capture. `normalize_v1` rewrites `\r\n`→`\n` only, so a terminal lone `\r`
  survives: TABLE-00 line 2 = `N= 6 FIRST= 12 LAST= 5\r` ≠ declared line. Pure harness artifact;
  TABLE-00's FAIL is F1 ALONE. Under the gate substring law it is invisible; the stricter v1 stream
  law (documented deviation, README §4) exposed it exactly as designed.
- **F2 (DR PLILIB print-wrap law, measured).** TABLE-01's 8-item PUT LIST line wrapped after item
  6: line 0 = **79 columns** then CRLF; continuation = items 7, 8 (21 columns; the first
  continuation item printed with an 8-space leading gap — the 12-column-cell numeric law differs
  at line start). Item cells measured: label 7 cols, first numeric right-ends col 16, subsequent
  items +12 cols each. ORIGIN DETERMINED BY MEASUREMENT — the CRLF is GUEST-written: a pty never
  injects CR into an output stream, and the transcript's pty-side session echoes show the ONLCR
  doubling `\r\r\n`, while the wrap is a single `\r\n`. Classification: historical-runtime (DR
  PLILIB) formatting; NOT a compiler defect, NOT my-gap; recorded as measured knowledge,
  promotion requires its own pre-registered oracle round (mission limit).
- TABLE-01 FAIL = F1 + F2. Expectations must NEVER be edited to match the capture (law L3); a
  future amendment may declare F2 only as an independently stated law.

## §3 Harness noise found (localised by bounded probes, mechanism accepted)

`len 128` prints on the RUNNER'S STDOUT during TABLE-01's LINK stage only (reproduced twice;
TABLE-00 never prints it; `--stages SOURCE..COMPILE` and `..LINK`-blocked probes print nothing).
MECHANISM (read `oracle/cpmwork.py:216`): `export()` invokes cpmcp with `check=False` and NO
stdout/stderr capture — the host tool's stdio is INHERITED by the harness process, so any cpmcp
chatter lands inside the runner's own stdout. The string `len 128` itself is an external cpmtools
debug print (cpmsim binary contains no such format string — `strings` checked); ROOT CAUSE
`proposed`, mechanism `accepted`. STEP-7 DEBT: capture (or DEVNULL) cpmcp stdio in `export()`,
add a hostile-suite pin that the runner's stdout carries ONLY rendered records.

## §4 Other measured notes

- Workspace SAFETY correctly refused a /tmp evidence root at LINK import
  (`safety-refused: import source outside allowed roots`) — fail-closed, BLOCKED attr=`host`,
  no lane executed; in-repo `build/functional/…` works. Confirms the hop-5 note about /tmp roots.
- Runner exit codes: rc=1 whenever any FAIL is present (both FX and TABLE batches), census probe
  rc=0 (it is not a verdict). Verdict tallies: Lane A PASS=1 FAIL=1; Lane B FAIL=2; census
  measured×2.
- `spec/functional/tests/__pycache__` exists (ignored); oracle import + derivation subprocess are
  print-clean.

## §5 Step-6 verdict

Predicted-vs-actual scorecard: FX-00 PASS ✓ (one arithmetic falsification: 14 calls, not 13);
FX-01 FAIL/`emulator` intended ✓; COMPILE ✓✓, LINK ✓✓, RUN-done ✓✓, ASSERT FAIL/`undefined` per
policy ✓✓; census hypothesis FALSIFIED → honest Package-A blocker recorded. Blockers preserved
for step 7/8: (1) v1 anchor law leaves terminal `\r` (F1); (2) expectations declare no PLILIB wrap
law (F2) — amendment must be a declared law, never a capture; (3) free core cannot host PLILIB
programs (BDOS 25 at init); (4) cpmcp stdio leak into harness stdout (§3). No compiler, oracle,
gate, or COVERAGE byte was touched.
