#!/usr/bin/env python3
"""Corpus sweep: classify every DR corpus program against MY current build.

EXACT   = raw .REL byte-identical to golden/first8080u/<N>/<N>.REL
DIFFERS = my build emitted a .REL that is not byte-identical
REFUSED = my build failed (exception), i.e. the program needs an
          unimplemented feature -- the refusal text is printed.
"""
import os, subprocess, sys, collections, tempfile

PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BIN = os.path.join(PROJ, "ocaml/_build/default/bin/pli80c.exe")
SRC = os.path.join(PROJ, "artefacts")
GOLD = os.path.join(PROJ, "golden/first8080u")

rows = []
for name in sorted(os.listdir(GOLD)):
    rel = os.path.join(GOLD, name, name + ".REL")
    src = os.path.join(SRC, name + ".PLI")
    if not (os.path.exists(rel) and os.path.exists(src)):
        continue
    out = os.path.join(tempfile.gettempdir(), name + ".rel")
    p = subprocess.run([BIN, src, out], capture_output=True, text=True)
    if p.returncode != 0:
        msg = (p.stderr or "").strip().splitlines()
        m = msg[-1] if msg else "?"
        m = m.split('Failure("')[-1].rstrip('")')
        rows.append(("REFUSED", name, m[:88]))
    else:
        same = open(out, "rb").read() == open(rel, "rb").read()
        rows.append(("EXACT" if same else "DIFFERS", name, ""))

c = collections.Counter(r[0] for r in rows)
for st, name, m in rows:
    if st == "EXACT":
        print("EXACT    %-10s %s" % (name, m))
for st, name, m in rows:
    if st != "EXACT":
        print("%-9s %-10s %s" % (st, name, m))
print("\ncorpus: %d/%d EXACT, %d DIFFERS, %d REFUSED of %d programs"
      % (c["EXACT"], len(rows), c["DIFFERS"], c["REFUSED"], len(rows)))
