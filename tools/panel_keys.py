#!/usr/bin/env python3
"""[E2E-40/P9a] Which probe names are registered, and in which panel.

Coverage rows cite probe lists in their `probes` column and `.REL` parity counts
(`EXACT:n` / `MIXED:e/d`) in `rel_parity`.  Those counts have drifted away from the
panel three times now, and each drift got argued about by hand instead of recomputed.
This resolves every cited name against the machine-maintained registration files:

  exact      -- kind=specimen in spec/INVENTORY.txt   (982 entries at E2E-40/P9)
  refused    -- kind=refusal  in spec/INVENTORY.txt   (129 entries at E2E-40/P9)
  divergent  -- a row of spec/DIVERGENT.txt (comments and the header line skipped)
  unlisted   -- cited but registered nowhere.  `artefacts/ST12.PLI` is the standing
                example: a FILE reference, not a panel key, so it must not be counted
                as an extra exact specimen.

spec/INVENTORY.txt is the authority for the first two because the gate maintains it
(`tools/e2e_gate.py --update-inventory`) and aborts when it disagrees with the live
panel.  Parsing `SPECIMENS` out of e2e_gate.py with `ast` is NOT enough -- only 466 of
the 982 entries are literal dict keys, the rest arrive through `SPECIMENS[x] = ...`
inside loops over source inventories, so a hand-rolled parser silently under-counts.
Reading the generated table avoids that class of error entirely.

Usage:
  tools/panel_keys.py NAME [NAME ...]
  tools/panel_keys.py --row DECL.MEMBER_SCOPE
"""
import io
import os
import sys

INV, DIV, COV = "spec/INVENTORY.txt", "spec/DIVERGENT.txt", "spec/COVERAGE.tsv"


def load(root="."):
    exact, refused, divergent = set(), set(), set()
    p = os.path.join(root, INV)
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8", errors="replace"):
            if line.startswith("#") or not line.strip():
                continue
            f = line.split("\t")
            if len(f) >= 2:
                if f[1] == "specimen":
                    exact.add(f[0])
                elif f[1] == "refusal":
                    refused.add(f[0])
    p = os.path.join(root, DIV)
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8", errors="replace"):
            if line.startswith("#") or not line.strip():
                continue
            f = line.split("\t")
            if len(f) >= 4 and f[0].strip() and f[0].strip() != "name":
                divergent.add(f[0].strip())
    return exact, divergent, refused


def classify(name, exact, divergent, refused):
    if name in exact:
        return "exact"
    if name in divergent:
        return "divergent"
    if name in refused:
        return "refused"
    return "unlisted"


def row_probes(row, root="."):
    for line in io.open(os.path.join(root, COV), encoding="utf-8"):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) > 10 and f[0] == row:
            return [x.strip() for x in f[10].split(",") if x.strip()], f[8]
    sys.exit("no such coverage row: %s" % row)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exact, divergent, refused = load(root)
    argv = sys.argv[1:]
    cited = []
    current = None
    if argv and argv[0] == "--row":
        if len(argv) < 2:
            sys.exit("--row needs a coverage row name")
        cited, current = row_probes(argv[1], root)
        print("row %s   rel_parity as written: %s" % (argv[1], current))
    else:
        cited = argv
    print("panel: %d exact, %d divergent, %d refused" % (len(exact), len(divergent), len(refused)))
    tally = {}
    for n in cited:
        c = classify(n, exact, divergent, refused)
        tally[c] = tally.get(c, 0) + 1
        print("  %-22s %s" % (n, c))
    print("tally:", " ".join("%s=%d" % kv for kv in sorted(tally.items())))
    e, d, r, u = (tally.get(k, 0) for k in ("exact", "divergent", "refused", "unlisted"))
    print("classified (registered as a panel entry of some kind): %d of %d cited"
          % (e + d + r, len(cited)))
    if cited:
        print("suggested rel_parity for the classified set: "
              "MIXED:%d/%d   (%d exact + %d divergent + %d refused; %d cited name(s) "
              "unregistered and excluded)" % (e, e + d + r, e, d, r, u))


main()
