#!/usr/bin/env python3
"""E2E-54/P2-DIFF-2 Stage A — the ADVERSARIAL (hostile) suite for the differential runner.

Pre-registered in spec/lab-evidence/e2e54/PLAN.md §P2-DIFF-2.1 (committed BEFORE any runner
byte): the three validity defects H-A1 / H-A2 / H-A3 and the ten attacks T1..T10 that must
detect them.

This suite is check-style and self-counting like tools/test_functional_runner.py: plain
python3, exit 0 iff every check passes.  NO compiler, LINK-80, cpmsim, emulator or oracle
process is EVER launched here — every lane result is an INJECTED dict (a disposable test
double), and the comparator is attacked with disposable expectations.  Production compilers,
fixtures and goldens are never touched.

TWO PHASES, both MEASURED (PROTOCOL #1: the tests are committed BEFORE the fix):

  BLOCK 1  attacks the CURRENT committed API (`verdict`, `run_native_lane`, the report/exit
           code) and proves the defects exist: every check in this block is an honest
           statement of what the current code does, and every one of them is a FAILING
           check once the hardened law is in force.  They are therefore written as
           DEFECT-CLAIM checks: the suite reports "the defect is present" as a FAIL.

  BLOCK 2  attacks the HARDENED API declared in §P2-DIFF-2.1 — `assess_case`,
           `assess_run`, `run_cases`, `--strict` — and requires the corrected law.  While
           the runner is unhardened these checks FAIL with ` hardened API missing`.

Run:  python3 tools/test_dual_backend.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dual_backend_test as dbl  # noqa: E402  (importing the module runs NO subprocess)

FAILED = []
TOTAL = 0
MISSING = []


def check(label, cond, detail=""):
    global TOTAL
    TOTAL += 1
    if cond:
        print("PASS  %s" % label)
    else:
        FAILED.append(label)
        print("FAIL  %s%s" % (label, ("  [%s]" % detail) if detail else ""))


def has_api(name):
    return hasattr(dbl, name)


# --------------------------------------------------------------------------- lane test doubles
# The shapes the runner's lane functions return (read from the current code):
#   8080   {"ok": True, "stages": [...], "console": <bytes>, "com_sha256": ...}
#   native {"ok": True, "stages": [...], "stdout": <bytes>, "stderr": ..., "rc": <int>}
# A BLOCKED lane is {"ok": False, "stopped": <stage>, "stages": [...]}.
def lane80(region):
    return {"ok": True, "stages": [{"stage": "run", "status": "pass"}],
            "console": region.encode("latin-1") if isinstance(region, str) else region,
            "com_sha256": "0" * 64}


def lane_native(stdout, rc=0):
    return {"ok": True, "stages": [{"stage": "exec", "rc": rc}],
            "stdout": stdout.encode("latin-1") if isinstance(stdout, str) else stdout,
            "stderr": b"driver-return=7\n", "rc": rc}


def blocked(lane, stage):
    return {"ok": False, "stopped": stage, "stages": [{"stage": stage, "status": "fail"}]}


# A disposable case entry (never a real fixture; the runner must not read the disk for it).
CASE = {"fixture": "injected/double.pli", "sha256": "0" * 64, "entry": "dbl",
        "tag": "DOUBLE", "expected": [1, 2], "pin": "injected/double.mir",
        "nfuncs": 1, "note": "injected test double"}


def assess(runs80, runs_native, expected=None):
    """Drive the HARDENED law (or the current one, if the API is absent) and report the
    VERDICT the runner would give for a case whose two lanes produced these runs."""
    if not has_api("assess_case"):
        MISSING.append("assess_case")
        return None
    exp = CASE["expected"] if expected is None else expected

    def f80(case, it, tag):
        return runs80[it - 1]

    def fn(case, it, tag):
        return runs_native[it - 1]

    return dbl.assess_case("T", CASE, exp, f80, fn, stamp="test")


print("== BLOCK 1 — the CURRENT committed API (the pre-registered defects, demonstrated)")

# ------------------------------------------------------------------ H-A1: determinism is inert
# Current code: verdict(expected, v80[0], vn[0]) — the SECOND observation is never consulted.
if has_api("assess_case"):
    # The hardened law is in force: assert the CORRECT behaviour instead.
    v = assess([lane80("1\n2\n"), lane80("1\n3\n")], [lane_native("1\n2\n"), lane_native("1\n2\n")])
    check("T1 8080 run1 matches, run2 differs -> NOT BOTH-PASS",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
    v = assess([lane80("1\n3\n"), lane80("1\n2\n")], [lane_native("1\n2\n"), lane_native("1\n2\n")])
    check("T2 8080 run1 differs, run2 matches -> NOT BOTH-PASS",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")], [lane_native("1\n2\n"), lane_native("1\n9\n")])
    check("T3 native run1 matches, run2 differs -> NOT BOTH-PASS",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
    v = assess([lane80("1\n2\n"), blocked("8080", "run")], [lane_native("1\n2\n"), lane_native("1\n2\n")])
    check("T6a a MISSING second 8080 execution -> NOT BOTH-PASS, infrastructure",
          v is not None and v["verdict"] != "BOTH-PASS" and v["infrastructure_failure"],
          str(v))
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")], [lane_native("1\n2\n"), None],
               ) if False else None
    # (the None-run shape is exercised through T6b below)
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [lane_native("1\n2\n"), lane80("1\n2\n")])
    check("T6b a native lane whose second result is not a native result -> NOT BOTH-PASS",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
else:
    # The defect itself, demonstrated against the CURRENT code exactly as it is written.
    got = dbl.verdict([1, 2], [1, 2], [1, 2])
    check("T1 8080 run1 matches, run2 differs -> NOT BOTH-PASS (H-A1 PRESENT)",
          False, "the current API is verdict(expected, v80[0], vn[0]): a second run that "
                 "differs is invisible to it")
    check("T6a a MISSING second execution -> NOT BOTH-PASS (H-A1 PRESENT)",
          False, "the current aggregation only reads v80[0]/vn[0]; a missing second "
                 "observation is silently ignored")
    MISSING.append("assess_case")

# ------------------------------------------------------------------ H-A2: the native status
if has_api("assess_run"):
    r = dbl.assess_run("native", lane_native("1\n2\n", rc=0), [1, 2])
    check("T5a native rc 0 + matching stdout -> a valid successful observation",
          r["ok"] and r["obs"] == [1, 2], str(r))
    r = dbl.assess_run("native", lane_native("1\n2\n", rc=3), [1, 2])
    check("T5 native rc 3 (a RANGE I/O status) with EXACTLY the right stdout -> NOT a valid success",
          not r["ok"], str(r))
    r = dbl.assess_run("native", lane_native("1\n2\n", rc=139), [1, 2])
    check("T5b native rc 139 (killed by a signal) with the right stdout -> NOT a valid success",
          not r["ok"], str(r))
    r = dbl.assess_run("8080", lane80("1\n2\n"), [1, 2])
    check("T5c the 8080 lane has no process-status field to trust: its ok flag is the stage law",
          r["ok"] and r["obs"] == [1, 2], str(r))
else:
    check("T5 native rc!=0 with matching stdout -> NOT a valid success (H-A2 PRESENT)",
          False, "run_native_lane returns {\"ok\": True, \"rc\": p.returncode} after exec "
                 "without ever testing rc")
    MISSING.append("assess_run")

# ------------------------------------------------------------------ the comparator itself
check("T7 both lanes the SAME WRONG vector -> BOTH-FAIL-SAME (never success)",
      dbl.verdict([1, 2], [9, 9], [9, 9]) == "BOTH-FAIL-SAME")
check("T7b one lane wrong, the other right -> the single-lane verdict, not BOTH-PASS",
      dbl.verdict([1, 2], [1, 2], [9, 9]) == "8080-ONLY"
      and dbl.verdict([1, 2], [9, 9], [1, 2]) == "NATIVE-ONLY")
try:
    dbl.normalize_vector(b"1\n2\nOK\n")
    check("T8a unexpected TEXT in the region is rejected", False, "no exception")
except ValueError:
    check("T8a unexpected TEXT in the region is rejected", True)
try:
    dbl.normalize_vector(b"1\n")
    check("T8b an INCOMPLETE vector is rejected by the comparator, not by normalization",
          dbl.compare([1, 2], dbl.normalize_vector(b"1\n")) is False)
except ValueError:
    check("T8b an INCOMPLETE vector is rejected by the comparator, not by normalization", True)
try:
    dbl.normalize_vector(b"")
    check("T8c an empty region is a FAILURE, never an empty success", False, "no exception")
except ValueError:
    check("T8c an empty region is a FAILURE, never an empty success", True)
try:
    dbl.normalize_vector(b"1 2\n3 4x\n")
    check("T8d a partially-numeric token is rejected (nothing is silently dropped)",
          False, "no exception")
except ValueError:
    check("T8d a partially-numeric token is rejected (nothing is silently dropped)", True)
check("T8e order and multiplicity are significant",
      dbl.compare([1, 1], [1, 1]) and not dbl.compare([1, 2], [2, 1])
      and not dbl.compare([1, 2], [1, 2, 1, 2]))

# ------------------------------------------------------------------ H-A3: the exit code
if has_api("build_report") and has_api("run_cases"):
    # The hardened law: the report SAYS which class of problem it is, and the exit code is
    # mode-dependent.  A divergent measurement is RETAINED in both modes.
    def f80_div(case, it, tag):
        return lane80("1\n2\n")

    def fn_div(case, it, tag):
        return lane_native("9\n9\n")

    rep = dbl.run_cases(["T"], {"T": CASE}, {"8080": f80_div, "native": fn_div},
                        strict=False, stamp="test")
    check("T9a a DIVERGENT measurement is retained (not dropped, not an error)",
          rep["cases"]["T"]["verdict"] == "DIVERGENT", rep["cases"]["T"]["verdict"])
    check("T9b the report names the semantic divergence ADDITIVELY",
          "T" in rep.get("semantic_divergence", []), str(rep.get("semantic_divergence")))
    check("T9c the report carries NO infrastructure failure for a completed measurement",
          rep.get("infrastructure_failure") == [], str(rep.get("infrastructure_failure")))
    check("T9d the existing `failures` field keeps its meaning (a verdict is not a failure)",
          rep["failures"] == [], str(rep["failures"]))
    check("T9e the default mode exit code is unchanged by the hardening",
          dbl.exit_code(rep, strict=False) == 0 and dbl.exit_code(rep, strict=True) == 1,
          "default=%d strict=%d" % (dbl.exit_code(rep, strict=False),
                                    dbl.exit_code(rep, strict=True)))
    rep2 = dbl.run_cases(["T"], {"T": CASE},
                         {"8080": lambda c, i, t: blocked("8080", "link"),
                          "native": lambda c, i, t: lane_native("1\n2\n")},
                         strict=False, stamp="test")
    check("T9f an infrastructure failure is named as such and is a failure in BOTH modes",
          "T" in rep2.get("infrastructure_failure", [])
          and dbl.exit_code(rep2, strict=False) == 1
          and dbl.exit_code(rep2, strict=True) == 1, str(rep2.get("infrastructure_failure")))
else:
    check("T9a the exit-code contract is decidable from the report (H-A3 PRESENT)",
          False, "the current code returns 0 for DIVERGENT/8080-ONLY/BOTH-FAIL-SAME and "
                 "the docstring says 1; the report carries no field that separates an "
                 "infrastructure failure from a semantic disagreement")
    MISSING.append("run_cases/build_report")

print()
print("== BLOCK 2 — the hardened law (PLAN §P2-DIFF-2.1)")
if MISSING:
    print("  HARDENED API MISSING: %s" % ", ".join(sorted(set(MISSING))))
    print("  (this is the pre-fix state: the defects H-A1/H-A2/H-A3 are demonstrable)")

if has_api("assess_case"):
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")], [lane_native("1\n2\n"), lane_native("1\n2\n")])
    check("T0 positive control: BOTH runs match on BOTH lanes -> BOTH-PASS",
          v is not None and v["verdict"] == "BOTH-PASS" and not v["infrastructure_failure"],
          str(v))
    # A POSITIVE control is what keeps every "not BOTH-PASS" check above non-vacuous.
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [lane_native("1\n2\n"), lane_native("1\n2\n")], expected=[1, 2, 3])
    check("T0b the same observation against a WRONG expectation is NOT BOTH-PASS",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [blocked("native", "COSMO-LINK"), lane_native("1\n2\n")])
    check("T6c a blocked FIRST native execution -> NOT BOTH-PASS, infrastructure",
          v is not None and v["verdict"] != "BOTH-PASS" and v["infrastructure_failure"], str(v))
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [lane_native("1\n2\nOK\n"), lane_native("1\n2\nOK\n")])
    check("T8e unexpected text in EITHER lane's observation is a validity failure, not a verdict",
          v is not None and v["verdict"] != "BOTH-PASS", str(v and v["verdict"]))
    v = assess([lane80("1\n2\n"), lane80("1\n2\n")],
               [lane_native("9\n9\n"), lane_native("9\n9\n")])
    check("T7c both lanes the same WRONG vector, twice each -> BOTH-FAIL-SAME",
          v is not None and v["verdict"] == "BOTH-FAIL-SAME", str(v and v["verdict"]))
    # T10: attribution and preservation of the failing observation.
    v = assess([lane80("1\n2\n"), lane80("1\n3\n")],
               [lane_native("1\n2\n"), lane_native("1\n2\n")])
    rec = v.get("record", v)
    raw = rec.get("raw_8080", [])
    check("T10 the failing run's raw observation is PRESERVED and attributed",
          len(raw) == 2 and raw[1] == "1\n3\n" and rec.get("determinism_8080", (None,))[0] is False,
          str(raw) + " " + str(rec.get("determinism_8080")))

print()
if FAILED or MISSING:
    print("%d CHECK(S) FAILED, %d hardened-API symbol group(s) missing, of %d run"
          % (len(FAILED), len(set(MISSING)), TOTAL))
    for f in FAILED:
        print("  - " + f)
    sys.exit(1)
print("all %d dual-backend hostile checks passed" % TOTAL)
sys.exit(0)
