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
    """Specified semantics of TABLE-01.PLI (FS-01 output revision, 2026-11-02): ascending
    ordering of the multiset (multiplicity preserved -- two -3s and two 7s survive), the sum
    invariant over the permutation, the count, and the low/high extremes.  Python's OWN sort
    is the independent reference SEQUENCE; the PL/I program's rank-placement algorithm is what
    is under test, never used here.

    Output DESIGN (declared by the revised program): the sorted values print on TWO short
    labelled lines (items 1-4, then 5-8) plus the aggregate line, so no line approaches
    PLILIB's measured 79-column wrap (E2E-50/P2 F2); algorithm, inputs and checked invariants
    are UNCHANGED.  Expected text is derived from the README section 6 format law -- a
    character literal prints unquoted at natural width, each fixed numeric prints in a
    right-justified field, so under collapse-spaces-v1 every item boundary is exactly ONE
    space: label, single space, space-separated values.  Derived, never captured (L3)."""
    srt = sorted(TABLE01_INPUT)                  # [-3, -3, 0, 1, 4, 7, 7, 12]
    return ["SORTED 1-4: " + " ".join(str(v) for v in srt[0:4]),
            "SORTED 5-8: " + " ".join(str(v) for v in srt[4:8]),
            "SUM= %d N= %d LOW= %d HIGH= %d"
            % (sum(TABLE01_INPUT), len(TABLE01_INPUT), srt[0], srt[-1])]



# ---------------------------------------------------------------- fixture family (Lane A)
# The Lane A substrate fixtures are ORIGINAL hand-encoded .COM images written for this
# round (spec/functional/tests/FX-*.asm, built by tools/mk_functional_fixture.py).  Their
# expected console stream is the text each source DECLARES it emits -- independent of the
# emulator's run output (README law L3).  A fixture verdict is evidence about the harness
# and the audited free-core substrate, NEVER about PL/I.

FX00_LINES = ["FX-00 CORE OK", "BDOS2-OK"]      # BDOS 9 banner, then BDOS 2 per char


def fx00():
    """FX-00.asm: banner via BDOS 9, then the literal characters "BDOS2-OK" + CR LF via
    ten BDOS 2 calls; BDOS 11/12 are called and their results discarded, BDOS 0 terminates.
    Each emitted line ends in CRLF, so the normalized stream is exactly these two lines."""
    return list(FX00_LINES)


def fx01():
    """FX-01.asm: banner via BDOS 9, THEN BDOS 1 (console input), which the audited
    emulator does not implement (docs/emulator-audit.md 2.12).  The declared stream can
    therefore never complete on this substrate: the honest Lane A verdict for FX-01 is FAIL
    with attribution `emulator', and that FAIL is the intended measurement (README 9
    admits `emulator' only from a typed runner error; audit 2.18 discards stdout there).
    The derivation states what the source declares it prints BEFORE the typed error."""
    return ["FX-01 BEFORE-TYPED-ERROR"]


DERIVATIONS = {"table00": table00, "table01": table01,
               "fx00": fx00, "fx01": fx01}


def derive(name):
    """Harness entry point: derivation function `name` -> list of expected lines."""
    if name not in DERIVATIONS:
        raise KeyError("no such derivation: %r" % name)
    return DERIVATIONS[name]()


if __name__ == "__main__":
    for _n in sorted(DERIVATIONS):
        for _l in DERIVATIONS[_n]():
            print("%s: %s" % (_n, _l))
