#!/usr/bin/env python3
"""Parser corpus gate: run the OCaml parser over all artefacts/ + probes/
sources and check accept/reject parity against the ORIGINAL COMPILER's
sweep results (expected-reject list documented below). Exit non-zero on
mismatch. Re-run after every parser change."""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80parse.exe")

# Sources the ORIGINAL compiler rejects (see spec/CLAIMS C013, C041, probes16):
EXPECTED_REJECT = {
    "CALL.PLI":   "shipped source defect (dangling '*/ entry constant */')",
    "P023.PLI":   "negative probe: STRUCTURE keyword is cut (compiler: NO DCL cascade)",
    "P024.PLI":   "negative probe: 'p->.q' invalid (compiler: SYNTAX raised in PASS 2)",
}

def sweep(paths):
    ok, bad = [], []
    for p in paths:
        r = subprocess.run([EXE, p], capture_output=True, text=True)
        name = os.path.basename(p)
        if r.returncode == 0:
            ok.append(name)
        else:
            bad.append((name, (r.stdout + r.stderr).strip().splitlines()[-1]))
    return ok, bad

def main():
    if not os.path.exists(EXE):
        print("build first: (cd ocaml && dune build)")
        return 2
    paths = sorted(
        os.path.join(d, f)
        for d in (os.path.join(ROOT, "artefacts"), os.path.join(ROOT, "probes"))
        for f in os.listdir(d) if f.upper().endswith(".PLI")
    )
    ok, bad = sweep(paths)
    failed = {n for n, _ in bad}
    unexpected_ok = failed ^ set(EXPECTED_REJECT) and set()
    missing_rejects = {n for n in EXPECTED_REJECT if n not in failed}
    extra_rejects = failed - set(EXPECTED_REJECT)
    print(f"parsed OK: {len(ok)}   rejected: {len(bad)}   (expected rejects: {len(EXPECTED_REJECT)})")
    for n, msg in bad:
        tag = "expected" if n in EXPECTED_REJECT else "UNEXPECTED"
        print(f"  [{tag:9}] {n}: {msg}")
    if missing_rejects or extra_rejects:
        print("GATE FAIL")
        print("  parser accepted should-reject:", missing_rejects)
        print("  parser rejected should-accept:", extra_rejects)
        return 1
    print("GATE PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
