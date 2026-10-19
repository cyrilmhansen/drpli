#!/usr/bin/env python3
"""E2E-11 step 0 -- BLOCKER-SET AUDIT (user correction #1).

Ranking candidates by the FIRST refusal my compiler prints is meaningless: most
remaining programs need several kinds at once, so a first-blocker ranking
systematically over-states the payoff of whatever happens to be checked first.

This driver runs `pli80deps.exe` (an AST + binder walk) over every corpus
program and reports, per program, the COMPLETE set of feature tags it touches.
The capability baseline is derived EMPIRICALLY, not asserted:

  SUPPORTED   a tag that occurs in at least one program my build reproduces
              byte-exactly today (the 9 accepted corpus programs + the probes
              registered on the e2e gate).  If DR's own output for it is already
              reproduced, the feature is implemented -- that is the strongest
              possible evidence.
  UNKNOWN     a tag that occurs only in programs I cannot reproduce.  It is a
              candidate blocker, not a proven one (a tag can appear in a program
              for a reason that needs no code, e.g. OPTIONS(MAIN)).

Then it answers the only question that matters for sequencing:

  (a) which programs are closable by implementing ONE feature;
  (b) which features co-occur so often that they form one coupled cluster;
  (c) which blockers are independent LANGUAGE features vs coupled IMPLEMENTATION
      requirements -- that judgement is made from the co-occurrence table, and
      the note writes it down with the evidence, not from a guess.

usage: python3 tools/blocker_audit.py [--csv]
"""
import collections
import os
import re
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPS = os.path.join(PROJ, "ocaml/_build/default/bin/pli80deps.exe")
GOLD = os.path.join(PROJ, "golden/first8080u")
SRC = os.path.join(PROJ, "artefacts")
BIN = os.path.join(PROJ, "ocaml/_build/default/bin/pli80c.exe")

# No tag is pre-classified away.  An earlier draft of this tool carried a
# NEUTRAL list ("this tag surely needs no code"), and that is exactly the
# shortcut that produced the first-blocker error it was meant to fix: a tag is
# only known-harmless if a byte-exact DR specimen already proves my build
# reproduces it.  So the baseline below is derived purely from programs my build
# reproduces, and every remaining tag is reported as a candidate blocker for me
# to judge -- with the co-occurrence data, not by assertion.
def corpus():
    """(name, src, golden) for every program that has a DR .REL."""
    rows = []
    for name in sorted(os.listdir(GOLD)):
        rel = os.path.join(GOLD, name, name + ".REL")
        src = os.path.join(SRC, name + ".PLI")
        if os.path.isfile(rel) and os.path.isfile(src):
            rows.append((name, src, rel))
    return rows


def build_state(rows):
    """Which programs my build reproduces byte-exactly right now."""
    exact = set()
    for name, src, rel in rows:
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), name + ".audit.rel")
        p = subprocess.run([BIN, src, out], capture_output=True)
        if p.returncode == 0 and open(out, "rb").read() == open(rel, "rb").read():
            exact.add(name)
    return exact


def tags_for(paths):
    """program -> {tag: (count, first_line, detail)}, plus parse/bind status."""
    if not paths:
        return {}
    out = subprocess.run([DEPS] + paths, capture_output=True, text=True).stdout
    prog = None
    res = {}
    for line in out.splitlines():
        if line.startswith("PROG "):
            prog = os.path.basename(line[5:]).replace(".PLI", "").upper()
            res[prog] = {"tags": {}, "status": []}
        elif line.startswith(("PARSE ", "BIND ")):
            res[prog]["status"].append(line)
        elif line.startswith("TAG ") and prog:
            parts = line[4:].split()
            tag = parts[0]
            count = int(parts[1].split("=")[1])
            first = int(parts[2].split("=")[1])
            detail = line.split(None, 4)[-1] if len(parts) > 3 else ""
            res[prog]["tags"][tag] = (count, first, detail.strip())
    return res


def gate_positives():
    """(src, golden) for every program the e2e gate reproduces byte-exactly.

    The capability baseline MUST include these, not only the 9 corpus programs.
    An earlier draft derived it from the corpus alone and consequently reported
    CALL_STMT as a blocker in 23 programs -- while P401/P402/IADD are gate
    positives that reproduce DR's internal CALL lowering byte-for-byte.  That is
    the same first-blocker error in a new costume: inferring capability from a
    small sample instead of from the evidence that exists."""
    txt = open(os.path.join(PROJ, "tools/e2e_gate.py")).read()
    out = []
    for m in re.finditer(r'\("([^"]+\.PLI)",\s*"([^"]+\.REL)"\)', txt):
        src, rel = m.group(1), m.group(2)
        if os.path.isfile(os.path.join(PROJ, src)):
            out.append((src, os.path.join(PROJ, rel)))
    return out


def refusal(name, src):
    """My compiler's own first complaint, if it has one."""
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), name + ".audit.ref")
    p = subprocess.run([BIN, src, out], capture_output=True, text=True)
    if p.returncode == 0:
        return None
    lines = (p.stderr or "").strip().splitlines()
    msg = lines[-1] if lines else "?"
    return msg.split('Failure("')[-1].rstrip('")')[:96]


def main():
    rows = corpus()
    exact = build_state(rows)
    info = tags_for([src for _, src, _ in rows])

    # capability baseline: tags occurring in ANY byte-exact specimen, corpus or
    # gate probe (verified byte-exact, not assumed)
    supported = collections.Counter()
    for name in exact:
        for t in info.get(name, {}).get("tags", {}):
            supported[t] += 1
    probe_info = tags_for([src for src, _ in gate_positives()])
    for src, rel in gate_positives():
        # only count a probe whose golden really matches right now
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "audit.probe.rel")
        p = subprocess.run([BIN, os.path.join(PROJ, src), out], capture_output=True)
        if p.returncode != 0 or not os.path.isfile(rel):
            continue
        if open(out, "rb").read() != open(rel, "rb").read():
            continue
        nm = os.path.basename(src).replace(".PLI", "").upper()
        for t in probe_info.get(nm, {}).get("tags", {}):
            supported[t] += 1

    blocker_sets = {}
    refusals = {}
    for name, src, _ in rows:
        if name in exact:
            continue
        ts = set(info.get(name, {}).get("tags", {}))
        blocker_sets[name] = ts - set(supported)
        refusals[name] = refusal(name, src)

    # feature -> programs that still need it
    feat_progs = collections.defaultdict(list)
    for name, bs in blocker_sets.items():
        for t in bs:
            feat_progs[t].append(name)

    if "--csv" in sys.argv:
        for name in sorted(blocker_sets):
            print("%s,%s" % (name, ";".join(sorted(blocker_sets[name]))))
        return

    print("E2E-11 STEP 0 -- BLOCKER-SET AUDIT")
    print("corpus programs with a DR .REL : %d" % len(rows))
    print("reproduced byte-exactly today   : %d  (%s)"
          % (len(exact), " ".join(sorted(exact))))
    print("capability baseline tags        : %d" % len(supported))
    print()
    print("== per-program COMPLETE blocker sets (not first-blocker) ==")
    for name in sorted(blocker_sets, key=lambda n: (len(blocker_sets[n]), n)):
        bs = blocker_sets[name]
        print("  %-9s %2d  %s" % (name, len(bs), ", ".join(sorted(bs))))
    print()
    print("== feature -> programs needing it (payoff ranking) ==")
    for feat, progs in sorted(feat_progs.items(),
                              key=lambda kv: (-len(kv[1]), kv[0])):
        print("  %-28s %2d  %s" % (feat, len(progs), " ".join(sorted(progs))))
    print()
    print("== closable by implementing exactly ONE feature ==")
    for name in sorted(blocker_sets):
        bs = blocker_sets[name]
        if len(bs) == 1:
            print("  %-9s needs only: %s" % (name, list(bs)[0]))
    print()
    print("== closable by TWO features (candidate milestone scope) ==")
    for name in sorted(blocker_sets):
        bs = blocker_sets[name]
        if len(bs) == 2:
            print("  %-9s %s" % (name, " + ".join(sorted(bs))))
    print()
    print("== co-occurrence: which unknown features always travel together ==")
    pairs = collections.Counter()
    for name in blocker_sets:
        bs = sorted(blocker_sets[name])
        for i, a in enumerate(bs):
            for b in bs[i + 1:]:
                pairs[(a, b)] += 1
    if not pairs:
        print("  (no two blocker sets co-occur -- every refused program needs one kind)")
    for (a, b), n in pairs.most_common(20):
        print("  %-26s + %-26s %d" % (a, b, n))
    print()
    print("== cross-check: blocker SET vs my compiler's first REFUSAL ==")
    print("   (a set that disagrees with the refusal means the tag walk is blind")
    print("    to a route-level gap -- conversions and peepholes carry no tag)")
    for name in sorted(blocker_sets):
        bs = sorted(blocker_sets[name])
        rf = refusals[name] or "compiled (byte-differs?)"
        blind = "  <-- TAG-BLIND" if not bs else ""
        print("  %-9s set=%-42s refuse=%s%s"
              % (name, (",".join(bs) or "EMPTY")[:42], rf[:54], blind))
    print()
    print("== parse/bind status for the refused set (front-end health) ==")
    for name, _, _ in rows:
        if name in exact:
            continue
        st = info.get(name, {}).get("status", [])
        bad = [x for x in st if "FAIL" in x]
        print("  %-9s %s" % (name, "; ".join(bad) if bad else "parse+bind ok"))


if __name__ == "__main__":
    main()
