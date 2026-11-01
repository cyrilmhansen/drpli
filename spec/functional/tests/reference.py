#!/usr/bin/env python3
"""Independent expected-value reference for the TABLE functional corpus.

E2E-50/P2 step 4 (2026-11-02).  Law L3 of `spec/functional/tests/README.md` section 4:
expected lines are DERIVED here -- from the independently specified semantics of each
program -- and never captured from DR, from my compiler, or from the program's own run.
Stdlib-only, pure functions, no arguments (fixed-input corpus), returning the COMPLETE
normalized console stream (collapse-spaces-v1) in stream order.

The step-5 harness runs `derive(name)` and requires its output to equal the spec's
`expected.console` before any lane executes; drift between this file and a spec is a
spec-source FAIL (attribution `source`), never a silent pass.
"""

TABLE00_INPUT = [12, -7, 0, 12, -23, 5]


def table00():
    """Specified semantics of TABLE-00.PLI: sum of all elements, count of strictly
    positive elements, maximum element; then extent count and first/last elements."""
    t = TABLE00_INPUT
    s = sum(t)                                   # 12-7+0+12-23+5 = -1
    c = len([v for v in t if v > 0])             # 12, 12, 5        -> 3
    m = max(t)                                   # 12
    return ["SUM= %d POS= %d MAX= %d" % (s, c, m),
            "N= %d FIRST= %d LAST= %d" % (len(t), t[0], t[-1])]


TABLE01_INPUT = [4, -3, 7, -3, 0, 7, 12, 1]


def table01():
    """Specified semantics of TABLE-01.PLI: ascending ordering of the multiset
    (multiplicity preserved -- two -3s and two 7s survive), the sum invariant over the
    permutation, the count, and the low/high extremes.  Python's OWN sort is the
    independent reference SEQUENCE; the PL/I program's rank-placement algorithm is
    what is under test, never used here."""
    srt = sorted(TABLE01_INPUT)                  # [-3, -3, 0, 1, 4, 7, 7, 12]
    return ["SORTED: " + " ".join(str(v) for v in srt),
            "SUM= %d N= %d LOW= %d HIGH= %d"
            % (sum(TABLE01_INPUT), len(TABLE01_INPUT), srt[0], srt[-1])]


DERIVATIONS = {"table00": table00, "table01": table01}


def derive(name):
    """Harness entry point: derivation function `name` -> list of expected lines."""
    if name not in DERIVATIONS:
        raise KeyError("no such derivation: %r" % name)
    return DERIVATIONS[name]()


if __name__ == "__main__":
    for _n in sorted(DERIVATIONS):
        for _l in DERIVATIONS[_n]():
            print("%s: %s" % (_n, _l))
