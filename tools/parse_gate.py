#!/usr/bin/env python3
"""Parser corpus gate (see spec/PERIMETER.md for the classification model):
 - all [S] sources must parse;
 - EXPECTED_REJECT: sources the ORIGINAL compiler rejects AND that our
   compiler-parity grammar also rejects;
 - STANDARD_SUPERSET: [M] sources the compiler rejects but the Subset-G
   standard (and our parser) accept — they MUST keep parsing."""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80parse.exe")

EXPECTED_REJECT = {
    "CALL.PLI":  "shipped source defect (dangling '*/ entry constant */')",
    "P023.PLI":  "[C] STRUCTURE keyword (not in Subset G either)",
    "P024.PLI":  "'p->.q' invalid; compiler flags SYNTAX in PASS 2",
    "P052C.PLI": "[M] binary ^ XOR: DR rejects; our parity grammar omits",
    "P052D.PLI": "[M] binary ^ XOR: DR rejects; our parity grammar omits",
    "P066B.PLI": "picture dcl group form + bare (pic) format ref: DR SYNTAX, parser rejects too",
}

STANDARD_SUPERSET = {
    "P068M.PLI": "[M] short-circuit &: / |: (Subset G 6.2.2.5/6): DR p1-SYNTAX",
    "P066C.PLI": "[M] PICTURE declared type (Subset G 3.2.5): DR p1-SYNTAX",
    "P067D.PLI": "[M] $/_ identifier starts (Subset G 1.1.3): DR SYNTAX",
}

def main():
    if not os.path.exists(EXE):
        print("build first: (cd ocaml && dune build)")
        return 2
    paths = sorted(
        os.path.join(d, f)
        for d in (os.path.join(ROOT, "artefacts"), os.path.join(ROOT, "probes"))
        for f in os.listdir(d) if f.upper().endswith(".PLI")
    )
    fails = 0
    ok = rejected = 0
    for p in paths:
        name = os.path.basename(p)
        r = subprocess.run([EXE, p], capture_output=True, text=True)
        parsed = r.returncode == 0
        if name in EXPECTED_REJECT:
            if parsed:
                print(f"  FAIL {name}: should be rejected ({EXPECTED_REJECT[name]})")
                fails += 1
            else:
                rejected += 1
        elif name in STANDARD_SUPERSET:
            if not parsed:
                print(f"  FAIL {name}: superset must parse ({STANDARD_SUPERSET[name]})")
                print("       ", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
                fails += 1
            else:
                print(f"  ok*  {name}: {STANDARD_SUPERSET[name]}")
                ok += 1
        else:
            if parsed:
                ok += 1
            else:
                print(f"  FAIL {name}: UNEXPECTED rejection")
                print("       ", (r.stdout or "").strip().splitlines()[-1:])
                fails += 1
    print(f"parse gate: {ok} ok / {rejected} parity-rejects / {fails} FAIL "
          f"of {len(paths)}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
