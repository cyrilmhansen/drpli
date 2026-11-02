# E2E-50/P2 step 7 — ACTUALS (executed 2026-11-02, renewal hop 7)

Authority: `HANDOFF.md` → Next action (E2E-50/P2 step 7: minimal functional-results reporting +
the step-6 §3 debt). The scientific ACTUALS of the round stay in `../step6/RESULTS.md`; nothing
here restates them as independent authority (PROTOCOL #7) and nothing here promotes a claim:
**no COVERAGE / CLAIMS / RUNTIME / INVENTORY / census byte changed in step 7.**

## §1 The cpmcp stdio debt (step 6 §3) — measured, fixed, measured again

PREDICTION (committed at `958c204` BEFORE the post-fix run, PROTOCOL #1): after redirecting the
cpmcp child in `oracle/cpmwork.py Run.export()`, the same bounded probe prints ZERO foreign lines
and the LINK stage record/verdict are unchanged.

| probe | command (bounded, isolated evidence root, lane-labelled) | ACTUAL |
|---|---|---|
| PRE-fix | `functional_runner.py --tests TABLE-01 --stages SOURCE,COMPILE,LINK --evidence build/functional/step7-prefix-probe` | rc=1; stdout line 1 = **`len 128`** (foreign), line 2 = `TABLE-01 lane B UNKNOWN [RUN: stage ceiling]`; leak REPRODUCED exactly as step 6 §3 described |
| POST-fix | same command, `--evidence build/functional/step7-postfix-probe` | rc=1; stdout = `  TABLE-01   lane B  UNKNOWN  [RUN: stage ceiling]` + `evidence:` + `verdicts:` — **`grep -c 'len 128'` = 0**; verdict and rc UNCHANGED ⇒ the fix removes noise without touching evidence |

Fix: `Run.export()` now passes `stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT`, symmetric
with `import_local`/`mkfs` in the same file. The failure contract is unchanged — `ok =
os.path.isfile(dst) and os.path.getsize(dst) > 0` is still the ONLY thing callers consume
(`oracle/batch.py:135`, `oracle/linkrun.py:352/442/497`, `tools/functional_runner.py:888`); none
of them parses cpmcp chatter, so no gate loses the ability to fail (PROTOCOL #8). Cost, stated
honestly: cpmcp's own diagnostics are now unavailable to the harness on this path (as they
already were for imports/mkfs).

Root cause of the STRING itself remains `proposed` (an external cpmtools debug print; the cpmsim
binary contains no such format string — step 6 §3), so it is recorded, not "explained away".

## §2 Lane A substrate fallback — the hop-6 falsification repaired and measured

`Host.pli80_run_path()` fell back to `/home/john/pli/lab/_build/default/bin/pli80-run.exe`, a
dune PUBLIC name that `dune build` does not produce (FALSIFIED by step 6 §0). The list is now the
module constant `LANE_A_CANDIDATES` — the two MEASURED paths, freshest build first.

* Resolver identity (pure file check, NO emulator process): `Host().pli80_run_path()` →
  `/home/john/pli/lab/_build/default/bin/main.exe`, sha256 prefix `da2b34b9d0125764` — byte-the-
  same binary as the step-6 §0 audited runner.
* Executed Lane A probe WITHOUT `--pli80-run`:
  `functional_runner.py --tests FX-00 --evidence build/functional/step7-laneA-resolver` →
  `FX-00 lane A PASS`, `verdicts: PASS=1`, rc=0; capture `od` = `FX-00 CORE OK CR LF BDOS2-OK CR LF`,
  identical to the step-6 Lane A capture. The fallback therefore works on the real substrate.

## §3 The stdout-grammar pin (harness cannot be polluted unnoticed)

`main()` gained a `host=` TEST SEAM (the CLI never uses it) so the suite can render CLI output
with no external process. Case C14 of `tools/test_functional_runner.py` adds 11 checks
(**171 → 182**, rc=0, zero external processes):

* `cpmwork.Run.export` source pin: child stdio redirected + the bool contract still present.
* `LANE_A_CANDIDATES` pinned as data, plus two BEHAVIOURAL resolver cases through a scoped
  `os.path.isfile` stub (fallback name chosen; `""` when neither exists so BLOCKED can name it).
* CLI stdout grammar proven CLOSED for a stubbed end-to-end lane-B PASS: every non-empty line is
  a record (`  <id> lane <A|B> <VERDICT>…`), an `evidence:` line, or the `verdicts:` census.
* NON-VACUITY: the stub child is made to print `len 128` on inherited stdout — exactly what the
  real cpmcp did — and the detector catches it (`violations == ["len 128"]`) while the verdict and
  rc stay PASS/0: **noise is never evidence, in either direction**.

## §4 Honesty measurement found on the way (falsified prose, kept per PROTOCOL #2)

The handoff/learnings prose quoted the hostile suite as **"148 checks"**. Re-measured from the
artifact at HEAD: the committed suite printed **171** PASS lines (ran rc=0). The number in the
documents was a stale copy, not a measurement. Fixed structurally: `check()` now counts, and the
summary prints the total (`all 182 …`), so a document must quote the artifact.

**ACCEPTED:** suite self-count = 182 (rc=0); pre-C14 count = 171 (rc=0, measured by running the
HEAD blob from a scratch copy, deleted afterwards); the "148" figure is FALSIFIED as a current
count (it was accurate at hop 4 only).

## §5 Reporting deliverable

`docs/functional-results.md` — a SMALL report of the executed functional verdicts, pointing at
this evidence and at `../step6/RESULTS.md` as the authorities. It is a rendering of committed
evidence, not a second ledger: it adds no verdict, promotes nothing, and is explicitly labelled so
at the top. The P1 dashboard (`tools/functional_dashboard.py`) was NOT extended (its inputs are
canonical ledgers; step-6/7 evidence lives in ignored working state) — no reporting-system rewrite
(PROTOCOL: reuse, don't rebuild).

## §6 Checks run for this step

`py_compile` rc=0 (`functional_runner.py`, `test_functional_runner.py`, `oracle/cpmwork.py`);
hostile suite rc=0 (182); `tools/test_functional_dashboard.py` rc=0;
`tools/functional_dashboard.py --check` rc=0; `tools/file_prose_check.py` rc=0 (5 active clean);
`ocaml` `dune build` rc=0 (build only, no source touched). External processes in step 7: the two
bounded TABLE-01 COMPILE+LINK probes and one Lane A FX-00 run (plus the step-6 runs). No oracle
campaign, no full runtime tier, no Rune CI, no gate run in step 7.
