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



# ------------------------------------------------------- FC-01 corpus family (Lane B)
# Original representative programs (mission FC-01, 2026-11-02).  Each function below
# implements the program's SPECIFIED semantics in independent Python (stdlib only);
# the PL/I algorithm is never consulted (law L3).  Format law per README section 6:
# fixed numerics print right-justified in a field, literals at natural width, one
# blank between items after collapse-spaces-v1 -- so every expected line below is
# label + single-space-joined values.
#
# FRAMING (FC-01 hop 3, 2026-11-02): README section 6 framing law, measured on DR's own
# objects as [C352] (spec/lab-evidence/fc01-framing/; bare-skip spelling E29PS1 [C192]):
# a PUT SKIP executed as the FIRST output statement prints its own leading CRLF (the
# normalized stream opens with a blank line -> leading "" entry), and the program-exit
# chain appends EXACTLY ONE final CRLF REGARDLESS of line state -- also after a final
# bare PUT SKIP that had just terminated the line (-> one trailing "" entry).  Every
# Batch-A program's first executed output statement is `put skip list(...)` -> leading
# ""; MATH-00 additionally ends with a bare `put skip;` -> trailing "".  These entries
# are DERIVED from the measured law plus each program's declared statement sequence,
# never captured from any run (L3).

import math


def math00():
    """MATH-00: gcd(48,18) via math.gcd (the program uses repeated subtraction);
    divmod(107,3); odd-step accumulation 1+3+5+7+9; integer mean; remainder route.
    Framing [C352]: leading "" (first output stmt is PUT SKIP LIST) AND trailing ""
    (final bare PUT SKIP closes the line; the exit CRLF lands on the next line)."""
    g = math.gcd(48, 18)                      # 6
    q, r = divmod(107, 3)                     # 35, 2
    tot = sum(range(1, 10, 2))                # 25
    avg = tot // 5                            # 5
    return ["", "GCD= %d QUO= %d REM= %d" % (g, q, r),
            "TOT= %d AVG= %d %s" % (tot, avg, "ZERO-REM" if r == 0 else "NONZERO-REM"),
            ""]


def proc00():
    """PROC-00: sum of factorials 1..7 (math.factorial), iterative fib.
    fib(10)=55; printed square term is sq(fib(4)) = 3*3 = 9."""
    s = sum(math.factorial(i) for i in range(1, 8))       # 5913
    def fibi(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    return ["", "SUMFAC= %d FIB10= %d" % (s, fibi(10)),
            "SQFIB4= %d" % (fibi(4) ** 2)]   # first output stmt is PUT SKIP LIST ([C352])


HIST00_VALUES = [3, 14, 15, 92, 65, 35, 89, 7, 23, 81]


def hist00():
    """HIST-00: bucket ((v-1)//20)+1 over HIST00_VALUES, 5 buckets; peak bucket is the
    FIRST index attaining the max (the program scans with strict >)."""
    h = [0] * 5
    for v in HIST00_VALUES:
        h[(v - 1) // 20] += 1                 # buckets 1..5 -> h[0..4]
    mx = max(h)
    mv = h.index(mx) + 1
    return ["", "B1= %d B2= %d B3= %d" % tuple(h[0:3]),      # leading blank: [C352]
            "B4= %d B5= %d PEAK= %d" % (h[3], h[4], mv),
            "MAXN= %d" % mx]


def ptr00():
    """PTR-00: 5 nodes prepended with val=i*i -> LIFO [25,16,9,4,1]; sum 55; TOP is the
    last-prepended head 25; a full bounded walk ends at null -> NULLX= 1."""
    stack = [i * i for i in range(1, 6)][::-1]
    return ["", "SUMSQ= %d TOP= %d NULLX= %d" % (sum(stack), stack[0], 1)]  # [C352]


def strng00():
    """STRNG-00: rotate alpha/gamma/beta through a temp: w,x,y = beta,alpha,gamma.
    Three equality hits; the w=x test is false (no +100).  rec.name prints alone."""
    w, x, y = 'alpha', 'gamma', 'beta'
    t = w
    w = y
    y = x
    x = t
    hits = (w == 'beta') + (x == 'alpha') + (y == 'gamma') + (100 if w == x else 0)
    return ["", "W= %s HITS= %d" % (w, hits), "delta"]      # leading blank: [C352]


def dec00():
    """DEC-00: five FIXED DEC(9,2) contracts checked with decimal.Decimal: sum,
    difference, x*4, mixed 100+x, and a 3-step accumulation; count of exact matches."""
    from decimal import Decimal
    x, y = Decimal("12.50"), Decimal("7.25")
    checks = [x + y == Decimal("19.75"),
              x - y == Decimal("5.25"),
              x * 4 == Decimal("50.00"),
              Decimal(100) + x == Decimal("112.50"),
              x + x + x == Decimal("37.50")]
    return ["", "DECOK= %d" % sum(bool(c) for c in checks)]  # leading blank: [C352]


def flt00():
    """FLT-00: six FLOAT BINARY(24) contracts, all exactly representable in a 24-bit
    significand (2.5, 4.0, 10.25, 6.5, 1.5, 10.0): a*a+b, a+b, b-a, a*b, a+1 four
    times, and an expected-cell identity.  Python float64 is exact for these."""
    a, b = 2.5, 4.0
    checks = [a * a + b == 10.25, a + b == 6.5, 4.0 - 2.5 == 1.5,
              2.5 * 4.0 == 10.0, 2.5 + 4 * 1.0 == 6.5, 6.5 == 6.5]
    return ["", "FLTOK= %d" % sum(bool(c) for c in checks)]  # leading blank: [C352]


TAB02_T = [22, -5, 17, 0, 31, -5]


def tab02():
    """TABLE-02: LAST-match linear search for 17 (index 3, 1-based); a not-found search
    for 99 leaves 0; slice sum t[3..5] = 48; reverse copy u = reversed(t)."""
    pos = max((i + 1 for i, v in enumerate(TAB02_T) if v == 17), default=0)
    nf = max((i + 1 for i, v in enumerate(TAB02_T) if v == 99), default=0)
    sl = sum(TAB02_T[2:5])
    u = TAB02_T[::-1]
    return ["", "POS= %d NF= %d" % (pos, nf), "SLICE= %d" % sl,   # leading blank: [C352]
            "R1= %d R2= %d R6= %d" % (u[0], u[1], u[5])]


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
               "math00": math00, "proc00": proc00, "hist00": hist00,
               "ptr00": ptr00, "strng00": strng00, "dec00": dec00,
               "flt00": flt00, "tab02": tab02,
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
