#!/usr/bin/env python3
"""Print DR's own text around the refusal for probes that produced no .REL."""
import pathlib, sys
tags = ("e42p2b", "e42p2b2", "e42p2b3")
for n in sys.argv[1:]:
    for t in tags:
        p = pathlib.Path("golden") / t / n / (n + ".PRN")
        if p.exists():
            break
    raw = p.read_bytes().split(b"\x1a")[0].decode("latin1")
    lines = [l.rstrip() for l in raw.replace("\r", "").split("\n") if l.strip(" \x0c")]
    print(f"===== {n} ({p}) =====")
    keep = [l for l in lines if any(k in l for k in
            ("IKY", "IFB", "IFO", "ERROR", "error", "SEVERE", "DISABLED", "STOP"))]
    print("\n".join(keep[:8]) if keep else "\n".join(lines[-12:]))
    # the source line the diagnostic points at
    for i, l in enumerate(lines):
        if "IKY" in l or "IFB" in l or "IFO" in l:
            print("   context:", " // ".join(x.strip()[:60] for x in lines[max(0, i - 3):i + 1]))
            break
