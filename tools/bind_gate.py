#!/usr/bin/env python3
"""Binder gate: dump $S via our OCaml binder and byte-diff against the
original compiler's $S goldens (golden/bind*/S/*.s.txt).
Known open gaps are allowlisted with their claim/probe references."""
import subprocess, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80bind.exe")

# file -> reason for expected residual diff (open probes)
KNOWN_GAPS = {
    "LOAN1": "auto-injected ROUND BUILTIN on decimal scale shrink [PROBE 60]",
    "ANNUITY": "injected CHAR/DEC/LOG builtins + FORMAT statics (62B unit) "
               "[PROBE 62]; function-descriptor lines deferred",
    "FLTPOLY": "nested-function descriptor lines (P FUNCTION / RETURNED / "
               "PARAMETER .*) + PARAMETERS on block header — v2 machinery",
}

def find_source(name):
    for d in ("artefacts", "probes"):
        p = os.path.join(ROOT, d, name + ".PLI")
        if os.path.exists(p):
            return p
    return None

def main():
    goldens = sorted(glob.glob(os.path.join(ROOT, "golden/bind*/S/*.s.txt")) +
                   glob.glob(os.path.join(ROOT, "golden/probe*/S/*.s.txt")) + glob.glob(os.path.join(ROOT, "golden/first8080u/S/*.s.txt")))
    exact = gaps = fails = 0
    for g in goldens:
        name = os.path.basename(g)[:-len(".s.txt")]
        src = find_source(name)
        if src is None:
            print(f"  SKIP {name} (no source)")
            continue
        r = subprocess.run([EXE, "--inc", os.path.join(ROOT, "artefacts"), src],
                           capture_output=True, text=True)
        mine = r.stdout
        theirs = open(g).read()
        if mine == theirs:
            exact += 1
            print(f"  EXACT {name}")
        elif name in KNOWN_GAPS:
            gaps += 1
            print(f"  GAP   {name}: {KNOWN_GAPS[name]}")
        else:
            fails += 1
            print(f"  FAIL  {name}:")
            import difflib
            for l in list(difflib.unified_diff(theirs.splitlines(),
                                               mine.splitlines(),
                                               "compiler", "binder", lineterm=""))[:14]:
                print("        " + l)
    print(f"bind gate: {exact} exact / {gaps} known-gap / {fails} FAIL of {len(goldens)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
