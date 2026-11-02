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


# ---------------------------------------------------------------- Batch B blocker probes
# FC-01 hop 3 (2026-11-02).  Six programs each exercise ONE construct that is a MEASURED
# MY-COMPILER refusal (hop-1 scratch logs; classification `my-gap' against DR's manual;
# NO DR statement here -- the oracle was not consulted for these shapes).  The DELIVERABLE
# of each spec is the typed COMPILE FAIL with the refusal message recorded VERBATIM; the
# expected stream below is the FUTURE design, derived from the declared semantics plus the
# README sec 6 format and framing laws ([C352] leading "" -- every probe's first output
# action is a SKIP), never captured (L3).  If a future arm makes a probe compile, the same
# expectation judges it honestly.

def builtin00():
    """BUILTIN-00 (rev2, FC-01 hop 4): LENGTH(char(10)) is the EXTENT 10, independent of
    the stored value.  The rev1 SUBSTR store is DROPPED -- its char-store refusal fired
    before the built-in path (falsification kept as written, build/fc01/batchB); the
    extent law stands unchanged."""
    return ["", "LEN= 10"]


def strcat00():
    """STRCAT-00: marker-only design -- fixed-char PUT extent layout is UNMEASURED, so no
    value from c = a || b is derived."""
    return ["", "CAT-ATTEMPTED"]


def cond00():
    """COND-00: | composition -- hits = #{i in 1..6 : i=2 or i=5} = 2."""
    hits = len([i for i in range(1, 7) if i in (2, 5)])
    return ["", "HITS= %d" % hits]


def dec01():
    """DEC-01: fractional literal operand -- 12.50 + 2.25 = 14.75 exactly (Decimal); the
    residual-to-zero check sets ok = 1."""
    from decimal import Decimal
    ok = 1 if Decimal("12.50") + Decimal("2.25") - Decimal("14.75") == 0 else 0
    return ["", "DEC1OK= %d" % ok]


def flt01():
    """FLT-01: computed compare operand -- 2.5 + 4.0 = 6.5, all three exactly
    representable in a 24-bit significand (same reasoning as flt00)."""
    ok = 1 if 2.5 + 4.0 == 6.5 else 0
    return ["", "FLT1OK= %d" % ok]


def edit00():
    """EDIT-00: PUT EDIT(n) (SKIP(1), F(6)) -- SKIP(1) is the first output action ->
    leading blank [C352]; F(6) of 42 is right-justified in 6 columns -> after
    collapse-spaces-v1 the single line is ' 42'; exit closes it (no trailing blank)."""
    return ["", " 42"]


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


# ------------------------------------------------- FC-01 corpus: adapted historical programs
# FC-01 OPERATOR OVERRIDE hop (2026-11-02): WKDAY-00 is an ADAPTATION of the BASIC
# "Weekday" program (Creative Computing; research copy
# build/functional/fc01-sources/basic/WEEKDAY.bas, upstream sha256 ccb9a9e5...,
# licence UNVERIFIED -- recorded, not asserted).  Law L3: the expected stream below is
# derived from an independent Python port of the ORIGINAL algorithm, never captured
# from any run.  The port is validated against Python datetime (stdlib, independent
# of this program) for 10 dates including both century-leap branches.

WKDAY_T = [0, 3, 3, 6, 1, 4, 6, 2, 5, 0, 3, 5]   # DATA 0,3,3,6,1,4,6,2,5,0,3,5
WKDAY_NAMES = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY",
               "THURSDAY", "FRIDAY", "SATURDAY"]
WKDAY_TODAY = (3, 24, 1979)    # fixed TODAY  (console INPUT replaced)
WKDAY_TARGET = (7, 16, 1969)   # fixed TARGET (console INPUT replaced)


def _wkday_b(m, d, y):
    """Day index b (1=SUNDAY..7=SATURDAY) by the ORIGINAL BASIC algorithm, integer
    form.  BASIC INT() is floor; every division operand here is non-negative, so
    floor == the PL/I FIXED truncate the program relies on (declared contract)."""
    def fint(x, n):
        assert x >= 0
        return x // n
    i1 = fint(y - 1500, 100)
    a = i1 * 5 + fint(i1 + 3, 4)        # BASIC float .75 tail is mod-invariant (>=0)
    i2 = a - fint(a, 7) * 7
    y2 = fint(y, 100)
    y3 = y - y2 * 100
    a = fint(y3, 4) + y3 + d + WKDAY_T[m - 1] + i2
    b = a - fint(a, 7) * 7 + 1
    if m <= 2:
        if y3 == 0:
            aa = i1 - 1
            leap = (aa - fint(aa, 4) * 4) == 0
        else:
            leap = (y - fint(y, 4) * 4) == 0
        if leap:
            if b == 0:
                b = 6                   # dead upstream too (b >= 1): kept as declared
            b = b - 1
    if b == 0:
        b = 7
    return b


def _wkday_split(k1):
    """Original subroutine 1370: I5 = INT(K1/365), I6 = INT(K1/30) of the remainder,
    I7 the residual days."""
    i5 = k1 // 365
    k1 -= i5 * 365
    i6 = k1 // 30
    i7 = k1 - i6 * 30
    return i5, i6, i7


def _wkday_block(a8, f100, k5, k6, k7):
    """One INT(F*A8) block with F = f100/100, in pure integer arithmetic.  The exact
    identity floor(a8*f/100) = q*f + floor(r*f/100) (q = a8//100, r = a8-q*100) keeps
    every product inside FIXED BINARY(15); both sides are computed and asserted."""
    k1 = (a8 // 100) * f100 + (((a8 - (a8 // 100) * 100) * f100) // 100)
    assert k1 == (a8 * f100) // 100     # identity holds for a8 >= 0
    out = _wkday_split(k1)
    k5 -= out[0]
    k6 -= out[1]
    k7 -= out[2]
    if k7 < 0:                          # lines 1450-1470 (K7 >= 0 test inverted)
        k7 += 30
        k6 -= 1
    if k6 <= 0:                         # line 1480 IF K6>0 THEN 1510, inverted
        k6 += 12
        k5 -= 1
    return out, (k5, k6, k7)


def wkday00():
    """WKDAY-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Weekday program for the fixed pair TODAY 3/24/1979, TARGET 7/16/1969.

    Framing [C352]: first output statement is `put skip list('DATE', ds)` -> leading
    ""; the final statement is a PUT SKIP LIST whose content ends unterminated and is
    closed by exactly one exit CRLF -> NO trailing "" entry.  Format law README
    section 6: literals at natural width, fixed numerics right-justified in a field,
    one space between items after normalization."""
    import datetime
    m1, d1, y1 = WKDAY_TODAY
    m, d, y = WKDAY_TARGET
    b = _wkday_b(m, d, y)
    name = WKDAY_NAMES[b - 1]
    # independent cross-check of the port against Python's own calendar
    assert name == datetime.date(y, m, d).strftime("%A").upper()
    for cm, cd, cy in [(3, 24, 1979), (1, 1, 1970), (2, 29, 1980), (12, 31, 1999),
                       (1, 1, 1900), (2, 29, 2000), (12, 25, 2023), (1, 1, 1583),
                       (3, 1, 1700)]:
        assert WKDAY_NAMES[_wkday_b(cm, cd, cy) - 1] == \
            datetime.date(cy, cm, cd).strftime("%A").upper()
    # tense: the original arithmetic encoding vs the bin15-safe lexicographic sign
    # test the PL/I program uses -- proven equivalent for valid dates (|D1-D| < 31,
    # 31*|M1-M| + |D1-D| < 372) and asserted here for the fixed inputs
    st = 1
    if y1 < y:
        st = 3
    if y1 == y:
        if m1 < m:
            st = 3
        if m1 == m:
            if d1 < d:
                st = 3
            if d1 == d:
                st = 2
    u = (y1 * 12 + m1) * 31 + d1
    v = (y * 12 + m) * 31 + d
    assert (u > v) == (st == 1) and (u == v) == (st == 2) and (u < v) == (st == 3)
    tense = {1: "WAS", 2: "IS", 3: "WILL BE"}[st]
    # age with 30-day-month borrows (the ORIGINAL convention, kept as declared)
    i5, i6, i7 = y1 - y, m1 - m, d1 - d
    if i7 < 0:
        i6 -= 1
        i7 += 30
    if i6 < 0:
        i5 -= 1
        i6 += 12
    assert i5 >= 0                      # ga = 1 path is the only one reached
    a8 = i5 * 365 + i6 * 30 + i7 + i6 // 2
    sleep, (k5, k6, k7) = _wkday_block(a8, 35, i5, i6, i7)
    eat, (k5, k6, k7) = _wkday_block(a8, 17, k5, k6, k7)
    lab = 1 if k5 <= 3 else (2 if k5 <= 9 else 3)
    play, (k5, k6, k7) = _wkday_block(a8, 23, k5, k6, k7)
    if k6 == 12:                        # lines 1530-1560
        k5 += 1
        k6 = 0
    return ["",
            "DATE %d/%d/%d %s A %s." % (m, d, y, tense, name),
            "",
            "AGE %d YEARS %d MONTHS %d DAYS" % (i5, i6, i7),
            "TOTAL DAYS %d" % a8,
            "YOU HAVE SLEPT %d YEARS %d MONTHS %d DAYS" % sleep,
            "YOU HAVE EATEN %d YEARS %d MONTHS %d DAYS" % eat,
            ["YOU HAVE PLAYED", "YOU HAVE PLAYED/STUDIED",
             "YOU HAVE WORKED/PLAYED"][lab - 1]
            + " %d YEARS %d MONTHS %d DAYS" % play,
            "YOU HAVE RELAXED %d YEARS %d MONTHS %d DAYS" % (k5, k6, k7),
            "YOU MAY RETIRE IN %d" % (y + 65)]


DERIVATIONS = {"table00": table00, "table01": table01,
               "math00": math00, "proc00": proc00, "hist00": hist00,
               "ptr00": ptr00, "strng00": strng00, "dec00": dec00,
               "flt00": flt00, "tab02": tab02,
               "builtin00": builtin00, "strcat00": strcat00, "cond00": cond00,
               "dec01": dec01, "flt01": flt01, "edit00": edit00,
               "wkday00": wkday00,
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


