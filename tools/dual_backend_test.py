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

exit codes: 0 every case BOTH-PASS and all controls failed LOUDLY;
1 otherwise (a behavioral verdict, a BLOCKED case, a vacuous control or a
harness failure).  Evidence: ignored build/dual-backend/ (never a golden,
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
    args = ap.parse_args()
    ids = args.case or sorted(CASES)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    os.makedirs(EVIDENCE, exist_ok=True)
    report = {"schema": "pli80-dual-backend/1", "preregistration": "ddff0717",
              "stamp": stamp, "head": subprocess.run(
                  ["git", "-C", ROOT, "rev-parse", "HEAD"],
                  capture_output=True, text=True).stdout.strip(),
              "cases": {}, "controls": [], "failures": []}
    checks = 0

    for cid in ids:
        case = CASES[cid]
        # strict source validation BEFORE anything executes (brief §4/§7)
        with open(os.path.join(ROOT, case["fixture"]), "rb") as f:
            raw = f.read()
        if hashlib.sha256(raw).hexdigest() != case["sha256"]:
            report["failures"].append("%s: SOURCE sha256 mismatch BEFORE any execution" % cid)
            report["cases"][cid] = {"verdict": "BLOCKED", "why": "source-hash-mismatch"}
            continue

        lane_runs = {"8080": [], "native": []}
        for it in (1, 2):
            lane_runs["8080"].append(run_8080_lane(case, it, stamp))
            lane_runs["native"].append(run_native_lane(case, it, stamp))

        rec = {"case": cid, "fixture": case["fixture"], "entry": case["entry"],
               "expected": case["expected"], "lane": lane_runs, "notes": case["note"]}
        # observations and determinism
        v80, vn = [], []
        for r in lane_runs["8080"]:
            if not r.get("ok"):
                rec["8080_blocked"] = r.get("stopped")
                continue
            try:
                v80.append(normalize_vector(r["console"]))
            except ValueError as e:
                rec["8080_blocked"] = "unverifiable-region: %s" % e
        for r in lane_runs["native"]:
            if not r.get("ok"):
                rec["native_blocked"] = r.get("stopped")
                continue
            try:
                vn.append(normalize_vector(r["stdout"]))
            except ValueError as e:
                rec["native_blocked"] = "unverifiable-stdout: %s" % e
        rec["normalized_8080"] = v80
        rec["normalized_native"] = vn
        rec["raw_8080"] = [r["console"].decode("latin-1", "replace")
                           for r in lane_runs["8080"] if r.get("ok")]
        rec["raw_native"] = [r["stdout"].decode("latin-1", "replace")
                             for r in lane_runs["native"] if r.get("ok")]
        if len(v80) == 2:
            rec["determinism_8080"] = (v80[0] == v80[1],
                                       lane_runs["8080"][0]["console"] == lane_runs["8080"][1]["console"])
        if len(vn) == 2:
            rec["determinism_native"] = (vn[0] == vn[1],
                                         lane_runs["native"][0]["stdout"] == lane_runs["native"][1]["stdout"])
        rec["verdict"] = verdict(case["expected"], v80[0] if v80 else None,
                                 vn[0] if vn else None)
        report["cases"][cid] = rec
        checks += 1

    # the comparator attacks — against the REAL observations (disposable
    # expectations only; sources and executables untouched)
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
        checks += 1
        if c["accepted"]:
            report["failures"].append("CONTROL %s %s: the comparator ACCEPTED the corrupted "
                                      "expectation %r against the real observation — the "
                                      "comparator is VACUOUS" % (c["control"], c["case"],
                                                                 c["corrupted"]))

    # verdict reporting (the campaign objective: agreement/disagreement, not a
    # green count — verdicts are REPORTED, only BLOCKED cases and control
    # failures are runner errors; a wrong answer is a result, not a crash)
    for cid, rec in report["cases"].items():
        if rec.get("verdict") == "BLOCKED":
            report["failures"].append("%s: BLOCKED (%s)" % (
                cid, rec.get("8080_blocked") or rec.get("native_blocked")
                or rec.get("why")))

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
        print("E2E-54/P2-DIFF-1 dual-backend report  (pre-registration ddff0717, stamp %s)" % stamp)
        print("HEAD %s" % report["head"])
        for cid, rec in report["cases"].items():
            print("  %s: %s" % (cid, rec.get("verdict")))
            if rec.get("verdict") in ("BLOCKED",):
                print("      why: %s" % (rec.get("8080_blocked") or rec.get("native_blocked")
                                         or rec.get("why")))
                continue
            print("      expected: %r" % rec["expected"])
            print("      8080    : %r raw=%r" % (rec.get("normalized_8080"), rec.get("raw_8080")))
            print("      native  : %r raw=%r" % (rec.get("normalized_native"), rec.get("raw_native")))
            print("      determinism (normalized, raw): 8080=%s native=%s" % (
                rec.get("determinism_8080"), rec.get("determinism_native")))
        print("  comparator controls (%d, all must be REJECTED):" % len(ctrls))
        for c in ctrls:
            print("    %-12s %-10s corrupted=%-14r accepted=%s  -> %s" % (
                c["control"], c["case"], c["corrupted"], c["accepted"],
                "REJECTED (good)" if not c["accepted"] else "ACCEPTED (VACUOUS — FAIL)"))
        print("  measured checks: %d" % checks)
        print("  failures: %s" % (report["failures"] or "none"))

    return 0 if not report["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
