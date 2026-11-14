#!/usr/bin/env python3
"""E2E-54/P2-DIFF-1 — the dual-backend DIFFERENTIAL behavioral runner.

Pre-registered in spec/lab-evidence/e2e54/PLAN.md §P2-DIFF-1 (commit
ddff0717, BEFORE any fixture or runner byte).  This file is written to that
PLAN before its first execution; it is the COMMITTED form of the measured
pilot that already ran DISPOSABLY in build/e54p2-scratch/pilot/ (two
BOTH-PASS rounds, four SAME-SOURCE cases).

WHAT THIS IS — a behavioral comparison of the SAME source bytes on two real
toolchains, judged on ONE common observable (the program's own console
output):

    8080 lane (historical EXECUTION substrate — the linker and runtime are
    Digital Research's, but the COMPILER IS MINE: this is NOT the DR
    compiler oracle and never invokes PLI.COM):
        pli80c.exe -d  ->  .REL  ->  LINK-80 1.31 + PLILIB.IRL  ->  .COM
        ->  cpmsim  (fresh isolated workspace per execution)

    native lane:
        pli80mir.exe --export <entry>  ->  .mir (byte-identical to the
        committed pin)  ->  mir2o  ->  ET_REL  ->  pinned Cosmopolitan
        `tiny` static link (pli_console.c + console_check.c)  ->  fresh
        process execution

THE COMPARISON LAW (§P2-DIFF-1.6/.7): each lane is compared with the
INDEPENDENTLY DERIVED expected integer vector FIRST (hand-derived from the
PL/I source in the PLAN — never from any output), then the two lanes are
compared.  The normalized observation is the COMPLETE ordered
signed-decimal integer vector of the isolated program-output region; raw
bytes, raw transcripts and the extracted region are kept SEPARATELY.  A
matching pair of WRONG outputs is BOTH-FAIL-SAME, never BOTH-PASS; a
compiler/linker/emulator failure is BLOCKED, never a behavioral verdict.
`driver-return` (native stderr) is lane-specific evidence and is NOT part
of the common observation.  Agreement on the console vector proves NOTHING
about unobserved return values, call mechanisms or full PL/I equivalence.

The four cases (SAME-SOURCE: identical committed bytes, sha-verified BEFORE
every execution): D02 CF06 `count` [0,1,2]; D03 CALL04 `chain` [51] (the
PUT is in the DEEPEST procedure); D04 CALL06B `diffal` [2,7] (by-ref
aliasing); D05 CALL07 `thrice` [1,2,3] (a returned value used by the
caller).  D01 (M02) is NOT-COMPARABLE by pre-registered decision — it has
no PL/I console output; its only observation is a return value the 8080
lane never shows.

The two INTEGRATED programs of §P2-DIFF-2.10 (Stage B, original sources
written for this campaign, same SAME-SOURCE law): D06 DIF01 `tariff`
[6300,1500,3000,1800,400,120] (void by-ref+by-value calls, nested if/else
hulls, three value calls whose results the caller prints) and D07 DIF02
`steps` [9,7,5,3,3,5,7,9] (the counted do-while loop, the amended
§P2-DIFF-2.9-B deviation, callee-modified by-reference home re-read, PUT
inside the loop).

The two SUMMARY-ADMITTED programs of §P2-DIFF-3 (Stage D, original sources
committed at 3928f130/5c4ac3c6 BEFORE any compilation of those bytes — the
stronger timing law): D08 DIF03 `pricing` [1200,2400,3600] (the nested-IF
classifier `classify` returns 1/2/3; the return-value summary [1,3] admits
`cat * 1200` on the native lane, which the OLD backend refused with HIR-E19)
and D09 DIF04 `production` [350,350,350,700,1050] (counted do-while 1..5,
`stepclass` summary [1,3] admits `cl * 350`, PUT INSIDE the loop, the
disclosed `return (i)` IV deviation).  The expected vectors are the
pre-registered §P2-DIFF-3 ones, hand-derived, never from any output.

The two CALL-SITE-SPECIALIZED programs of §P2-DIFF-4 (Stage D, original
sources committed at c6257034 BEFORE any compilation of those bytes — the
stronger timing law): D10 DIF05 `billing` [1500,6000,10000] (the min-shaped
`capped_units` returns 20 or x; its CONTEXT-INDEPENDENT summary is the FULL
window and the OLD backend refused HIR-E19 on `cat * 500`; the per-call-site
specialization [3,20]/[12,20]/[20,30] admits the mul) and D11 DIF06 `batch`
[700,1400,2100,2800] (counted do-while 1..4, `limited_step` returns 12 or x;
the loop-IV actual [1,4] specializes to [1,12] and admits `cl * 700`, PUT
INSIDE the loop, `return (i)` is NOT observed).  The expected vectors are
the pre-registered §P2-DIFF-4 ones, hand-derived, never from any output.

COMPARATOR FALSIFICATION (§P2-DIFF-1.10): after the real observations are
in hand, the comparator is attacked with THREE DISPOSABLE corrupted
expectations (change / delete / permute — sources and executables
untouched); a corrupted expectation that the comparator ACCEPTS against the
real, unmodified observation is a RUNNER FAILURE.  If a control passes,
this runner fails.

usage (from the REPO ROOT):
    eval "$(opam env)" && python3 tools/dual_backend_test.py
    eval "$(opam env)" && python3 tools/dual_backend_test.py --case D04
    eval "$(opam env)" && python3 tools/dual_backend_test.py --json
    eval "$(opam env)" && python3 tools/dual_backend_test.py --strict   # GATE mode

exit codes (the §P2-DIFF-2.1 H-A3 adjudication):
  DEFAULT (diagnostic) mode — the EXISTING meaning, unchanged: 0 iff the run
  produced no `failures` entry (no BLOCKED case, no vacuous control); a
  semantic verdict is a REPORTED outcome, not a runner error.
  --strict (gate) mode — additionally non-zero for ANY result outside the
  acceptance criterion: every compared case BOTH-PASS, every control
  REJECTED, no infrastructure failure.
Evidence: ignored build/dual-backend/ (never a golden,
never the coverage registry).  Timeouts: compile 60, link 120, run 120,
native 60/120 (§P2-DIFF-1.9).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import functional_runner as fr  # noqa: E402  (the REUSED stage machinery)

PLIMIR = os.path.join(ROOT, "ocaml", "_build", "default", "hir", "pli80mir.exe")
MIR2O = os.path.join(ROOT, "build", "p1m0-deps", "mir2o")
RECIPE = os.path.join(ROOT, "tools", "mir_aot", "cosmo_link.sh")
RUNTIME = os.path.join(ROOT, "tools", "mir_aot", "pli_console.c")
DRIVER = os.path.join(ROOT, "tools", "mir_aot", "console_check.c")
EVIDENCE = os.path.join(ROOT, "build", "dual-backend")

# ---------------------------------------------------------------------------
# The PRE-REGISTERED table (PLAN §P2-DIFF-1.2, commit ddff0717).  Sources are
# the committed fixtures, reused byte-for-byte; the expected vectors are the
# hand-derived sequences of §P2-DIFF-1.4 — NEVER read from any output.
# ---------------------------------------------------------------------------
CASES = {
    "D02": {
        "fixture": "hir/mir-cf-fixtures/CF06.pli",
        "sha256": "bb2ba55e8e27dca1fde994a564f790c0b3fd1b5a82c9483a578c04fe3440da2f",
        "entry": "count", "tag": "CF06",
        "expected": [0, 1, 2],
        "pin": "hir/mir-cf-expected/CF06.mir",
        "nfuncs": 1,
        "note": "counted `do while`: guard i<3, three PUTs of the CURRENT i before the "
                "increment; the return value 3 is NOT observed",
    },
    "D03": {
        "fixture": "hir/mir-call-fixtures/CALL04.pli",
        "sha256": "72c418e4d21b80cf2e7a20eee41c6846a3f27532be3c6b8b971d13bb716e8906",
        "entry": "chain", "tag": "CALL04",
        "expected": [51],
        "pin": "hir/mir-call-expected/CALL04.mir",
        "nfuncs": 3,
        "note": "transitive chain -> mid -> leaf; the ONLY PUT is in the DEEPEST procedure; "
                "the caller's later x=91 and the return 91 are NOT observed",
    },
    "D04": {
        "fixture": "hir/mir-call-fixtures/CALL06B.pli",
        "sha256": "f0e915dd51f49c644448a291919658f1e055878f485c7654cbb50f61b8503cf8",
        "entry": "diffal", "tag": "CALL06B",
        "expected": [2, 7],
        "pin": "hir/mir-call-expected/CALL06B.mir",
        "nfuncs": 2,
        "note": "alias(x, x+0): one by-reference cell + one by-value copy; the callee's "
                "a=7 writes through to the caller's x; the callee prints the value copy 2",
    },
    "D05": {
        "fixture": "hir/mir-call-fixtures/CALL07.pli",
        "sha256": "0b2d3bdc2f9d54907fd7bb975b4fef2ade95b16f027a374652e83f5b2650977f",
        "entry": "thrice", "tag": "CALL07",
        "expected": [1, 2, 3],
        "pin": "hir/mir-call-expected/CALL07.mir",
        "nfuncs": 2,
        "note": "pick3(1,2,3) prints 1 and 2, RETURNS 3; the caller assigns the return and "
                "prints 3 — the returned value IS observed only because the source prints it",
    },
    # §P2-DIFF-2.10 — the two INTEGRATED programs (Stage B).  Sources and pins
    # committed BEFORE the differential run; the expected vectors are the
    # pre-registered §P2-DIFF-2.3 ones (DIF02 under the §P2-DIFF-2.9-B amended
    # definition), hand-derived from the algorithm and never from any output.
    "D06": {
        "fixture": "hir/dif-fixtures/DIF01.pli",
        "sha256": "011dc4e7fc1e1d4b4e50d525817829b3dc7923b904dfb31537a977838d59bdaf",
        "entry": "tariff", "tag": "DIF01",
        "expected": [6300, 1500, 3000, 1800, 400, 120],
        "pin": "hir/dif-expected/DIF01.mir",
        "nfuncs": 3,
        "note": "integrated tariff: three void bill(b, c+0) calls (by-reference home + "
                "by-value copy, the 8080 refuses a literal+literal ADD) whose bills are "
                "6000+600-300, 1200+300, 2400+300+300; then three tier(u+0) value calls "
                "(nested if/else hulls 100/10/1 times 18/40/120) printed by the caller; "
                "the entry's return value is NOT observed",
    },
    "D07": {
        "fixture": "hir/dif-fixtures/DIF02.pli",
        "sha256": "15ce8bcddf2f76149261e86f0d9f5b06d2999d236f3681a322862e24cea8489a",
        "entry": "steps", "tag": "DIF02",
        "expected": [9, 7, 5, 3, 3, 5, 7, 9],
        "pin": "hir/dif-expected/DIF02.mir",
        "nfuncs": 2,
        "note": "integrated steps: counted do while (i < 9) over i = 1..8, d = 5 - i for "
                "i < 5 else i - 4 (the §P2-DIFF-2.9-B amended definition), scale = 2*d + 1, "
                "a void adjust(h, s+0) that writes the by-reference home and the caller's "
                "re-read s = h; the PUT is INSIDE the loop (the loop-exit drop law); the "
                "return value 9 is NOT observed",
    },
    # §P2-DIFF-3 Stage D — the two SUMMARY-ADMITTED programs.  The sources are
    # the committed Stage-A fixtures (DIF03 at 3928f130 unchanged; DIF04 at
    # 5c4ac3c6 with the disclosed `return (w)` -> `return (i)` deviation, the
    # output vector unchanged); the pins are the measured-first Stage-D
    # outputs.  Expected vectors are the pre-registered §P2-DIFF-3 ones.
    "D08": {
        "fixture": "hir/dif-fixtures/DIF03.pli",
        "sha256": "34ac5efb91520ee5f9d13dfe1d12b6185b805727e1552814ed9a49131595b2e1",
        "entry": "pricing", "tag": "DIF03",
        "expected": [1200, 2400, 3600],
        "pin": "hir/dif-expected/DIF03.mir",
        "nfuncs": 2,
        "note": "nested-IF classifier: classify(x) computes 1/2/3 by control flow "
                "(x > 5 -> x > 50 -> 3 else 2; else 1); the return-value summary [1,3] "
                "admits cat * 1200 on the native lane (the OLD backend refused HIR-E19); "
                "three n = 2/20/200 calls with the n + 0 value-actual idiom, PUT of each "
                "cost; the entry's return (cost) is NOT observed",
    },
    "D09": {
        "fixture": "hir/dif-fixtures/DIF04.pli",
        "sha256": "b25f0a84409d38c9dbbc3e7a6a3abb6488c673f94c8269b38f505c9802d68906",
        "entry": "production", "tag": "DIF04",
        "expected": [350, 350, 350, 700, 1050],
        "pin": "hir/dif-expected/DIF04.mir",
        "nfuncs": 2,
        "note": "counted do while (i < 6) over i = 1..5; stepclass(s) computes 1/2/3 "
                "(s > 4 -> 3; s > 3 -> 2; else 1) with the summary [1,3] admitting "
                "cl * 350 (the OLD backend refused HIR-E19); the PUT of w is INSIDE the "
                "loop (the drop law); the disclosed return (i) — the IV, definitely "
                "initialized at the loop exit — is NOT observed",
    },
    # §P2-DIFF-4 Stage D — the two CALL-SITE-SPECIALIZED programs.  The sources
    # are the committed Stage-A fixtures (c6257034, the §P2-DIFF-4.11 amended
    # shape); the pins are the measured-first Stage-D outputs.  Expected vectors
    # are the pre-registered §P2-DIFF-4 ones (hand-derived, never from output).
    "D10": {
        "fixture": "hir/dif-fixtures/DIF05.pli",
        "sha256": "1e09787fcde6118d30c0b733ae83f422b417a06742b13a9c6fbe1d6f59cf397c",
        "entry": "billing", "tag": "DIF05",
        "expected": [1500, 6000, 10000],
        "pin": "hir/dif-expected/DIF05.mir",
        "nfuncs": 2,
        "note": "min-shaped capped_units(x) returns 20 or x (the hull of BOTH arms — "
                "the analysis never decides the condition); its context-independent "
                "summary is the FULL window and the OLD backend refused HIR-E19 on "
                "cat * 500; the per-call-site specialization [3,3]->[3,20], "
                "[12,12]->[12,20], [30,30]->[20,30] admits the mul; three q = 3/12/30 "
                "calls with the n + 0 value-actual idiom, PUT of each bill; the "
                "entry's return (bill) is NOT observed",
    },
    "D11": {
        "fixture": "hir/dif-fixtures/DIF06.pli",
        "sha256": "eebace68680501724ca4699201b9e3eb3b9800ed6ea4ed5f8da63c65bd4d6e41",
        "entry": "batch", "tag": "DIF06",
        "expected": [700, 1400, 2100, 2800],
        "pin": "hir/dif-expected/DIF06.mir",
        "nfuncs": 2,
        "note": "counted do while (i < 5) over i = 1..4; limited_step(x) returns 12 "
                "or x; the loop-IV actual [1,4] specializes the summary to [1,12] "
                "(the OLD backend refused HIR-E19 on cl * 700 with the full-window "
                "operand); the PUT of v is INSIDE the loop (the drop law); the "
                "return (i) — the IV, definitely initialized at the loop exit — is "
                "NOT observed",
    },
}

VERDICTS = ("BOTH-PASS", "8080-ONLY", "NATIVE-ONLY", "BOTH-FAIL-SAME",
            "DIVERGENT", "BLOCKED", "NOT-COMPARABLE")


# --------------------------------------------------------------------------- §P2-DIFF-1.6 comparator
def normalize_vector(region: bytes) -> list[int]:
    """The COMPLETE ordered signed-decimal integer vector of the isolated
    program-output region.  The five extraction proofs (§P2-DIFF-1.6):
    (1) the region is the caller-supplied isolated region (never the whole
    transcript); (2) every token is a signed decimal integer; (3) nothing
    but whitespace is discarded (split() removes ONLY whitespace, every
    remaining token is parsed); (4) order and multiplicity preserved (no
    sort, no dedup); (5) an empty/missing region is a FAILURE, never an
    empty success.  Raises ValueError on any violation — the caller treats
    that as an unclassified/blocked observation, never silent acceptance."""
    if not region:
        raise ValueError("empty program-output region — a missing result is a FAILURE")
    s = region.decode("latin-1")
    toks = s.split()
    if not toks:
        raise ValueError("region carries no integer token at all: %r" % s)
    out = []
    for t in toks:
        if not re.fullmatch(r"[+-]?\d+", t):
            raise ValueError("non-integer token %r in region %r (nothing may be "
                             "silently discarded)" % (t, s))
        out.append(int(t))
    return out


def compare(expected: list[int], observed: list[int]) -> bool:
    """The comparator under test: exact ordered vector equality (§P2-DIFF-1.6:
    order, multiplicity, completeness).  A missing or extra item is a
    failure; so is a permutation."""
    return list(expected) == list(observed)


# --------------------------------------------------------------------------- the 8080 lane
def run_8080_lane(case: dict, it: int, tag: str) -> dict:
    """Fresh isolated workspace per execution (the REUSED functional-runner
    stage machinery: SOURCE sha-verify, COMPILE, LINK with parse_undefined on
    the FULL segment, RUN with the FS-01 anchor cut).  Returns an evidence
    dict; `console' present ONLY when the region boundary was verified."""
    ev = os.path.join(EVIDENCE, "8080", case["tag"], "%s-it%d" % (tag, it))
    os.makedirs(ev, exist_ok=True)
    host = fr.Host()
    spec = {
        "id": case["tag"],
        "source": {"file": case["fixture"], "sha256": case["sha256"],
                   "encoding": "CRLF, ^Z-terminated, ASCII"},
        "limits": {"compile_timeout_s": 60, "link_timeout_s": 120, "run_timeout_s": 120},
        "console_input": "^Z",   # GET-free fixtures: the default one-^Z script
    }
    ctx = fr.LaneCtx(test_id="%s.it%d.%s" % (case["tag"], it, tag),
                     lane_entry={"lane": "B", "link_targets": [case["tag"]]},
                     spec=spec, spec_dir=ROOT, evidence=ev, host=host,
                     stage_ceiling=set(), console_input="^Z")
    stages = []
    for fn in (fr.stage_source, fr.stage_compile, fr.stage_link, fr.stage_run):
        st = fn(ctx)
        stages.append({"stage": st.name, "status": st.status, "witness": st.witness,
                       "attribution": st.attribution, "detail": st.detail,
                       "evidence": st.evidence})
        if st.status != "pass":
            return {"ok": False, "stopped": st.name, "stages": stages}
    return {"ok": True, "stages": stages,
            "console": ctx.console_raw,
            "com_sha256": hashlib.sha256(ctx.com_path and open(ctx.com_path, "rb").read()).hexdigest()}


# --------------------------------------------------------------------------- the native lane
def run_native_lane(case: dict, it: int, tag: str) -> dict:
    """The pinned recipe: pli80mir --export (stdout == the committed pin),
    mir2o -f, cosmo `tiny` link WITH pli_console.c + console_check.c (chmod
    +x law), fresh-process execution.  Per-stage rc recorded.  Program
    stdout, driver stderr and rc are kept SEPARATELY."""
    ev = os.path.join(EVIDENCE, "native", case["tag"], "%s-it%d" % (tag, it))
    os.makedirs(ev, exist_ok=True)
    env = dict(os.environ, LC_ALL="C")
    stages = []

    def stage(name, argv, timeout):
        r = subprocess.run(argv, capture_output=True, timeout=timeout, cwd=ROOT, env=env)
        open(os.path.join(ev, "%s.stdout" % name), "wb").write(r.stdout)
        open(os.path.join(ev, "%s.stderr" % name), "wb").write(r.stderr)
        stages.append({"stage": name, "rc": r.returncode})
        return r

    try:
        m = stage("mir", [PLIMIR, "--export", case["entry"], "-o",
                          os.path.join(ev, "out.mir"), os.path.join(ROOT, case["fixture"])], 60)
        if m.returncode != 0 or m.stderr != b"":
            return {"ok": False, "stopped": "MIR", "stages": stages}
        pin = open(os.path.join(ROOT, case["pin"]), "rb").read()
        if m.stdout != pin:
            return {"ok": False, "stopped": "MIR-PIN-CONSISTENCY", "stages": stages}
        o = stage("mir2o", [MIR2O, "-f", os.path.join(ev, "out.mir"),
                            os.path.join(ev, "out.o")], 120)
        if o.returncode != 0 or not os.path.isfile(os.path.join(ev, "out.o")):
            return {"ok": False, "stopped": "MIR2O", "stages": stages}
        if ("%d function(s)" % case["nfuncs"]) not in o.stderr.decode("latin-1", "replace"):
            return {"ok": False, "stopped": "MIR2O-FUNC-COUNT", "stages": stages}
        exe = os.path.join(ev, "out.exe")
        c = stage("cosmo", ["sh", RECIPE, "tiny", exe, "--",
                            os.path.join(ev, "out.o"), RUNTIME, DRIVER,
                            "-DENTRY=pli80_%s" % case["entry"]], 120)
        if c.returncode != 0 or not os.path.isfile(exe):
            return {"ok": False, "stopped": "COSMO-LINK", "stages": stages}
        os.chmod(exe, 0o755)   # the cosmo chmod +x law
        p = stage("exec", [exe], 60)
        open(os.path.join(ev, "stdout.raw"), "wb").write(p.stdout)
        return {"ok": True, "stages": stages, "stdout": p.stdout, "stderr": p.stderr,
                "rc": p.returncode}
    except subprocess.TimeoutExpired:
        stages.append({"stage": "timeout", "rc": None})
        return {"ok": False, "stopped": "TIMEOUT", "stages": stages}


# --------------------------------------------------------------------------- the verdict law
def verdict(expected: list[int], got80: list[int] | None, gotn: list[int] | None) -> str:
    """The SEVEN classes (§P2-DIFF-1.7).  A lane that did not produce an
    observation is NOT a wrong answer — the caller reports BLOCKED when the
    failure was infrastructure; this function only compares observations."""
    if got80 is None or gotn is None:
        return "BLOCKED"
    ok80 = compare(expected, got80)
    okn = compare(expected, gotn)
    if ok80 and okn:
        return "BOTH-PASS"
    if ok80:
        return "8080-ONLY"
    if okn:
        return "NATIVE-ONLY"
    if got80 == gotn:
        return "BOTH-FAIL-SAME"      # a matching pair of WRONG outputs is NEVER success
    return "DIVERGENT"


# --------------------------------------------------------------------------- §P2-DIFF-2.1 hardened run/case validation
def assess_run(lane: str, result, expected) -> dict:
    """Validate ONE lane execution result (the H-A2 fix): the lane must be a
    well-formed result of run_8080_lane/run_native_lane (or an injected test
    double of the same shape) with every stage passing, and its complete
    observation must normalize.  THE NATIVE STATUS LAW (pre-registered in
    §P2-DIFF-2.1, derived from tools/mir_aot/console_check.c): the driver
    RETURNS 0 on normal completion and the runtime failure tail exits
    NONZERO, so a native process status rc != 0 is an INVALID observation no
    matter what its stdout shows — the PL/I return value (the
    driver-return=... stderr diagnostic) is a DIFFERENT field and is never
    the process status.  Returns {"ok": bool, "obs": list|None, "reason":
    str}; the expected vector is never consulted here — a wrong-but-valid
    observation is a VERDICT, not a validity failure (assess_case)."""
    if not isinstance(result, dict):
        return {"ok": False, "obs": None, "reason": "missing lane result (a run that never happened)"}
    if not result.get("ok"):
        return {"ok": False, "obs": None,
                "reason": "lane blocked at stage %r" % (result.get("stopped"),)}
    stages = result.get("stages")
    if not isinstance(stages, list) or not stages:
        return {"ok": False, "obs": None, "reason": "no stage evidence"}
    if lane == "8080":
        if "console" not in result:
            return {"ok": False, "obs": None, "reason": "no isolated console region"}
        for st in stages:
            if not isinstance(st, dict) or st.get("status") != "pass":
                return {"ok": False, "obs": None,
                        "reason": "stage %r is not passing" % (st.get("stage") if isinstance(st, dict) else st,)}
        raw = result["console"]
    elif lane == "native":
        if not any(isinstance(st, dict) and st.get("stage") == "exec" for st in stages):
            return {"ok": False, "obs": None, "reason": "the native lane never reached exec"}
        if "stdout" not in result or "rc" not in result:
            return {"ok": False, "obs": None,
                    "reason": "result is not a native-lane result (no stdout/rc)"}
        if result["rc"] != 0:
            return {"ok": False, "obs": None,
                    "reason": "native process status rc=%r violates the rc == 0 status law" % (result["rc"],)}
        raw = result["stdout"]
    else:
        return {"ok": False, "obs": None, "reason": "unknown lane %r" % (lane,)}
    try:
        obs = normalize_vector(raw)
    except ValueError as e:
        return {"ok": False, "obs": None, "reason": "unnormalizable observation: %s" % e}
    return {"ok": True, "obs": obs, "reason": ""}


def assess_case(cid: str, case: dict, expected, lane_8080, lane_native, stamp: str = "") -> dict:
    """Validate BOTH executions of EACH lane (the H-A1 fix): a verdict comes
    from verdict() ONLY when every lane produced exactly two complete, valid
    observations and the two observations of a lane are the SAME normalized
    vector; a missing/non-pairing second observation, a lane that never
    reached exec, a native rc != 0 or a non-deterministic pair is an
    INFRASTRUCTURE FAILURE — never a silent pass, never a behavioural
    verdict.  All raw/normalized/determinism fields keep their §P2-DIFF-1.6
    meanings; infrastructure_failure and semantic_divergence are ADDITIVE
    (§P2-DIFF-2.1 rule 4)."""
    lane_runs = {"8080": [], "native": []}
    for it in (1, 2):
        lane_runs["8080"].append(lane_8080(case, it, stamp))
        lane_runs["native"].append(lane_native(case, it, stamp))
    rec = {"case": cid, "fixture": case["fixture"], "entry": case["entry"],
           "expected": list(expected), "lane": lane_runs, "notes": case.get("note", "")}
    a80 = [assess_run("8080", r, expected) for r in lane_runs["8080"]]
    an = [assess_run("native", r, expected) for r in lane_runs["native"]]
    rec["assess_8080"] = a80
    rec["assess_native"] = an
    v80 = [a["obs"] for a in a80 if a["ok"]]
    vn = [a["obs"] for a in an if a["ok"]]
    rec["normalized_8080"] = v80
    rec["normalized_native"] = vn
    rec["raw_8080"] = [r["console"].decode("latin-1", "replace")
                       for r, a in zip(lane_runs["8080"], a80) if a["ok"]]
    rec["raw_native"] = [r["stdout"].decode("latin-1", "replace")
                         for r, a in zip(lane_runs["native"], an) if a["ok"]]
    if len(v80) == 2:
        rec["determinism_8080"] = (v80[0] == v80[1],
                                   lane_runs["8080"][0]["console"] == lane_runs["8080"][1]["console"])
    if len(vn) == 2:
        rec["determinism_native"] = (vn[0] == vn[1],
                                     lane_runs["native"][0]["stdout"] == lane_runs["native"][1]["stdout"])
    infra = []
    for i, a in enumerate(a80):
        if not a["ok"]:
            infra.append("8080 run %d: %s" % (i + 1, a["reason"]))
    for i, a in enumerate(an):
        if not a["ok"]:
            infra.append("native run %d: %s" % (i + 1, a["reason"]))
    if len(v80) != 2:
        infra.append("8080: only %d of 2 required observations completed" % len(v80))
    if len(vn) != 2:
        infra.append("native: only %d of 2 required observations completed" % len(vn))
    if not infra and rec["determinism_8080"][0] is False:
        infra.append("8080: the two fresh executions are NOT deterministic")
    if not infra and rec["determinism_native"][0] is False:
        infra.append("native: the two fresh executions are NOT deterministic")
    if infra:
        rec["infrastructure_failure"] = infra
        rec["verdict"] = "BLOCKED"   # an infrastructure failure is NEVER a behavioural verdict
    else:
        rec["infrastructure_failure"] = []
        rec["verdict"] = verdict(list(expected), v80[0], vn[0])
    rec["semantic_divergence"] = (rec["verdict"] != "BOTH-PASS"
                                  and not rec["infrastructure_failure"])
    # The suite reads v.get("record", v); a NON-CIRCULAR self-copy keeps the
    # report json-serializable (the committed P2-DIFF-1 lesson: never let the
    # report carry a cycle or raw bytes the default= cannot render).
    rec["record"] = {k: v for k, v in rec.items() if k != "record"}
    return rec


def run_cases(ids, cases, lane_fns=None, strict=False, stamp=None) -> dict:
    """The runner entry point used by BOTH the CLI and the adversarial suite
    (the lane_fns injection seam, §P2-DIFF-2.1): build the complete report
    and return it; the exit decision is exit_code(report, strict)."""
    return build_report(ids, cases, lane_fns=lane_fns, strict=strict, stamp=stamp)


def exit_code(report: dict, strict: bool = False) -> int:
    """The adjudicated exit-code law (§P2-DIFF-2.1, H-A3): DEFAULT mode keeps
    the EXISTING meaning — 0 iff the run produced no `failures` entry (no
    BLOCKED case, no vacuous control).  STRICT (gate) mode additionally exits
    non-zero for ANY result outside the acceptance criterion: every compared
    case BOTH-PASS, every control REJECTED, no infrastructure failure."""
    if report["failures"]:
        return 1
    if strict:
        if report["infrastructure_failure"]:
            return 1
        for rec in report["cases"].values():
            if rec.get("verdict") != "BOTH-PASS":
                return 1
        for c in report["controls"]:
            if c["accepted"]:
                return 1
    return 0


def build_report(ids, cases, lane_fns=None, strict=False, stamp=None) -> dict:
    """The machine-readable report (§P2-DIFF-2 schema 2).  The lane functions
    are the INJECTION SEAM: the real run_8080_lane/run_native_lane are the
    defaults; the adversarial suite injects doubles (NO subprocess ever runs
    in the suite).  `strict` is recorded in the report; the exit decision is
    exit_code(report, strict)."""
    if lane_fns is None:
        lane_fns = {"8080": run_8080_lane, "native": run_native_lane}
    if stamp is None:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    report = {"schema": "pli80-dual-backend/2", "preregistration": "41fca33e + §P2-DIFF-2.9",
              "stamp": stamp, "strict": strict,
              "head": subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
              "cases": {}, "controls": [], "failures": [],
              "infrastructure_failure": [], "semantic_divergence": []}
    for cid in ids:
        case = cases[cid]
        # strict source validation BEFORE anything executes (brief §4/§7); only
        # for real cases with a committed fixture — the suite injects doubles.
        if case["fixture"] != "injected/double.pli":
            with open(os.path.join(ROOT, case["fixture"]), "rb") as f:
                raw = f.read()
            if hashlib.sha256(raw).hexdigest() != case["sha256"]:
                report["failures"].append("%s: SOURCE sha256 mismatch BEFORE any execution" % cid)
                report["cases"][cid] = {"verdict": "BLOCKED", "why": "source-hash-mismatch",
                                        "infrastructure_failure": ["source-hash-mismatch"]}
                report["infrastructure_failure"].append(cid)
                continue
        rec = assess_case(cid, case, case["expected"],
                          lane_fns["8080"], lane_fns["native"], stamp=stamp)
        report["cases"][cid] = rec
        if rec["verdict"] == "BLOCKED":
            why = rec.get("infrastructure_failure") or rec.get("why")
            report["failures"].append("%s: BLOCKED (%s)" % (cid, why))
            report["infrastructure_failure"].append(cid)
        elif rec["verdict"] != "BOTH-PASS":
            # a completed measurement that disagrees: RETAINED, reported,
            # NOT a runner failure in the default mode (§P2-DIFF-2.1 rules 1/2)
            report["semantic_divergence"].append(cid)
    # comparator controls against the REAL observations (disposable expectations
    # only; sources and executables untouched) — the §P2-DIFF-1.10 law is unchanged
    observed = {}
    for cid, rec in report["cases"].items():
        if rec.get("normalized_8080") and rec.get("normalized_native"):
            if rec["normalized_8080"] == rec["normalized_native"]:
                observed[cid] = rec["normalized_8080"][0]
            else:   # divergent lanes: the two lanes get their OWN control set
                observed[cid] = rec["normalized_8080"][0]
                observed[cid + "-native"] = rec["normalized_native"][0]
    ctrls = comparator_controls(observed)
    report["controls"] = ctrls
    for c in ctrls:
        if c["accepted"]:
            report["failures"].append("CONTROL %s %s: the comparator ACCEPTED the corrupted "
                                      "expectation %r against the real observation — the "
                                      "comparator is VACUOUS" % (c["control"], c["case"],
                                                                 c["corrupted"]))
    return report


# --------------------------------------------------------------------------- §P2-DIFF-1.10 comparator controls
def comparator_controls(observed: dict) -> list[dict]:
    """Three DISPOSABLE corrupted expectations against the REAL, UNMODIFIED
    observations.  The sources and executables are untouched; the
    corruption lives only in the expected vector in memory.  A corrupted
    expectation that the comparator ACCEPTS is a control PASS — which is a
    RUNNER FAILURE (non-vacuity)."""
    controls = []
    for cid, case in CASES.items():
        got = observed.get(cid)
        if got is None:
            continue
        exp = case["expected"]
        # C-DF1 change one expected integer
        if len(exp) >= 1:
            corrupt = list(exp)
            corrupt[-1] = corrupt[-1] + 1000
            controls.append({"control": "C-DF1", "case": cid,
                             "corrupted": corrupt,
                             "accepted": compare(corrupt, got),
                             "law": "change one expected integer"})
        # C-DF2 delete one mandatory output item (the FULL observation must
        # still be rejected against the truncated expectation)
        if len(exp) >= 2:
            corrupt = list(exp[:-1])
            controls.append({"control": "C-DF2", "case": cid,
                             "corrupted": corrupt,
                             "accepted": compare(corrupt, got),
                             "law": "delete one mandatory output item"})
        # C-DF3 permute two mandatory items with DIFFERENT values
        if len(exp) >= 2 and exp[0] != exp[1]:
            corrupt = list(exp)
            corrupt[0], corrupt[1] = corrupt[1], corrupt[0]
            controls.append({"control": "C-DF3", "case": cid,
                             "corrupted": corrupt,
                             "accepted": compare(corrupt, got),
                             "law": "permute two items whose values differ"})
        # completeness: the comparator must ALSO reject an EMPTY observation
        # presented as a full result (the "missing result is a failure" law)
        controls.append({"control": "C-DF2-empty", "case": cid,
                         "corrupted": [],
                         "accepted": compare([], got),
                         "law": "an empty expectation is never accepted against a real observation"})
    return controls


# --------------------------------------------------------------------------- the runner
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--case", action="append", choices=sorted(CASES),
                    help="run only this case (repeatable)")
    ap.add_argument("--json", action="store_true", help="emit the machine-readable summary")
    ap.add_argument("--strict", action="store_true",
                    help="GATE mode (§P2-DIFF-2.1): exit non-zero for ANY result outside "
                         "every case BOTH-PASS, every control REJECTED, no infrastructure "
                         "failure; the report itself is unchanged (everything is retained)")
    args = ap.parse_args()
    ids = args.case or sorted(CASES)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    os.makedirs(EVIDENCE, exist_ok=True)
    report = build_report(ids, CASES, strict=args.strict, stamp=stamp)
    checks = len(report["cases"]) + len(report["controls"])

    # Lane evidence is held in memory as raw BYTES (the observation itself); the JSON report
    # renders them latin-1 (byte-for-byte, lossless in both directions).  The untouched raw
    # artifacts are also on disk: run.console.bin / run.raw-transcript.txt (8080) and
    # out.stdout / stdout.raw (native).
    def _json_default(o):
        if isinstance(o, (bytes, bytearray)):
            return bytes(o).decode("latin-1")
        return str(o)

    with open(os.path.join(EVIDENCE, "report-%s.json" % stamp), "w") as f:
        json.dump(report, f, indent=1, default=_json_default)

    if args.json:
        print(json.dumps(report, indent=1, default=_json_default))
    else:
        print("E2E-54/P2-DIFF dual-backend report  (schema %s, stamp %s, mode %s)"
              % (report["schema"], stamp, "STRICT" if args.strict else "default"))
        print("HEAD %s" % report["head"])
        for cid, rec in report["cases"].items():
            print("  %s: %s" % (cid, rec.get("verdict")))
            if rec.get("verdict") == "BLOCKED":
                print("      why: %s" % (rec.get("infrastructure_failure") or rec.get("why")))
                continue
            print("      expected: %r" % rec["expected"])
            print("      8080    : %r raw=%r" % (rec.get("normalized_8080"), rec.get("raw_8080")))
            print("      native  : %r raw=%r" % (rec.get("normalized_native"), rec.get("raw_native")))
            print("      determinism (normalized, raw): 8080=%s native=%s" % (
                rec.get("determinism_8080"), rec.get("determinism_native")))
        print("  semantic divergence (retained, NOT failures): %s" % (report["semantic_divergence"] or "none"))
        print("  infrastructure failures (case ids): %s" % (report["infrastructure_failure"] or "none"))
        print("  comparator controls (%d, all must be REJECTED):" % len(report["controls"]))
        for c in report["controls"]:
            print("    %-12s %-10s corrupted=%-14r accepted=%s  -> %s" % (
                c["control"], c["case"], c["corrupted"], c["accepted"],
                "REJECTED (good)" if not c["accepted"] else "ACCEPTED (VACUOUS — FAIL)"))
        print("  measured checks: %d" % checks)
        print("  failures: %s" % (report["failures"] or "none"))

    return exit_code(report, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
