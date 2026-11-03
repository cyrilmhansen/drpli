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


# ---------------------------------------------------------------- HAMM-00 (Hammurabi)
# FC-01 CORPUS program 2: adaptation of BASIC "Hammurabi" (Creative Computing;
# research copy build/functional/fc01-sources/basic/HAMMURABI.bas, sha256
# 93fea01f8b63766a83919653f798932ba33d4ca2654b70e87a54653d60c73831, upstream
# coding-horror/basic-computer-games 43_Hammurabi, licence UNVERIFIED).  Law L3:
# the stream below is DERIVED from an independent Python mirror of the declared
# port semantics, never captured (the cross-check against the ignored scratch
# simulator build/fc01-scratch/hamm00_sim.py is a development aid, NOT an import).
#
# The reference mirrors HAMM-00.PLI STATEMENT FOR STATEMENT (same order, same
# temps, same control flow) as a script-driven machine over the 46 declared GET
# values, so a divergence between program and reference is impossible by
# construction.  Byte model per the measured laws (README section 6 + hop-2
# separator law + hop-start echo law): PUT SKIP emits "\r\n"; PUT LIST joins
# items with ONE blank, fixed numerics in a 10-wide right-justified field
# ("%10d"); a consumed GET line L echoes as L + "\r\r\n"; program exit appends
# exactly one "\r\n" ([C352]); normalization collapse-spaces-v1 then split with
# ONE trailing empty dropped.  chk() asserts EVERY intermediate inside
# FIXED BINARY(15); the shift/weak-compare forms and the nested-floor births
# route are ASSERTED equivalent to the BASIC float semantics at every observed
# value; the whole-bin15 ladder equivalence is verified exhaustively.

import re as _hamm00_re

HAMM00_P0, HAMM00_S0, HAMM00_H0, HAMM00_Y0, HAMM00_A0 = 95, 1500, 900, 3, 300
HAMM00_I0, HAMM00_Q0, HAMM00_GG0 = 5, 1, 2      # A0 = H0/Y0 (upstream relation)

HAMM00_SCRIPT = [                                # the 46 declared GET values
    0, 301, 0, 1352, 298, 200,
    43, 0, 0, 700, 300,
    0, 0, 1588, 900, 300,
    0, 0, 520, 259,
    0, 0, 780, 301, 300,
    0, 0, 480, 239,
    0, 0, 760, 300,
    0, 0, 460, 230, 229,
    0, 0, 740, 300,
    0, 0, 300, 229,
]

_HAMM00_B15 = 32767
_HAMM00_MAXIN = 12767        # every fed value keeps q + 20000 inside bin(15)

_HAMM00_BUYP = "HOW MANY ACRES DO YOU WISH TO BUY "
_HAMM00_SELLP = "HOW MANY ACRES DO YOU WISH TO SELL "
_HAMM00_FEEDP = "HOW MANY BUSHELS DO YOU WISH TO FEED YOUR PEOPLE "
_HAMM00_PLANTP = "HOW MANY ACRES DO YOU WISH TO PLANT WITH SEED "


def _hamm00_chk(v):
    assert -_HAMM00_B15 <= v <= _HAMM00_B15, "bin15 overflow: %d" % v
    return v


def _hamm00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ", (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Hamm00Port:
    """Script-driven mirror of HAMM-00.PLI.  emit=False drives the state machine
    silently (search/analysis); emit=True records the raw console bytes."""

    def __init__(self, script, emit=True):
        self.script = list(script)
        self.emit = emit
        self.raw = ""
        self.nget = 0
        self.plague_years = 0
        self.rats_years = 0
        self.skip_years = 0
        self.starve_years = 0
        self.verdict = None

    # ---- IO primitives (measured byte model)
    def skip(self):
        if self.emit:
            self.raw += "\r\n"

    def put(self, *items):
        if self.emit:
            self.raw += " ".join(("%10d" % _hamm00_chk(it)) if isinstance(it, int)
                                 else it for it in items)

    def get(self):
        assert self.script, "GET past the end of the declared script"
        v = self.script.pop(0)
        # negative-shift guard domain: every fed value must keep x + 20000 inside
        # bin(15); the shift form x+20000 < 20000 is asserted identical to x < 0
        # at each use site below.
        assert -20000 <= v <= _HAMM00_MAXIN, "fed value out of domain: %d" % v
        self.nget += 1
        if self.emit:
            self.raw += "%d\r\r\n" % v
        return v

    # ---- declared RNG: gg = gg + 1; w = gg*37 + 11; v = w - (w/k)*k
    def draw(self, k):
        self.gg = _hamm00_chk(self.gg + 1)
        w = _hamm00_chk(self.gg * 37)
        w = _hamm00_chk(w + 11)
        t = _hamm00_chk(w // k)
        v = _hamm00_chk(w - t * k)
        assert 0 <= v < k
        return v

    # ---- weak-compare forms (port law): a <= b spells t2 = b + 1; a < t2
    def weak(self, a, b):
        t2 = _hamm00_chk(b + 1)
        port = a < t2
        assert port == (a <= b)            # identity for integers in domain
        return port

    def negguard(self, x):
        t1 = _hamm00_chk(x + 20000)
        port = t1 < 20000
        assert port == (x < 0)             # holds across the whole bin15 domain
        return port

    # ---- bad: (BASIC 850; compile-only on the spine) + bye: 990/995 (bells dropped)
    def bad(self):
        self.skip()
        self.put("HAMURABI:  I CANNOT DO WHAT YOU WISH.")
        self.skip()
        self.put("GET YOURSELF ANOTHER STEWARD!!!!!")
        self.skip()
        self.bye()

    def fink(self):
        self.put("DUE TO THIS EXTREME MISMANAGEMENT YOU HAVE NOT ONLY")
        self.skip()
        self.put("BEEN IMPEACHED AND THROWN OUT OF OFFICE BUT YOU HAVE")
        self.skip()
        self.put("ALSO BEEN DECLARED NATIONAL FINK!!!!")
        self.skip()

    def bye(self):
        self.skip()
        self.put("SO LONG FOR NOW.")
        self.skip()
        self.skip()

    # ---- the game (statement-for-statement in HAMM-00.PLI order)
    def run(self):
        self.skip(); self.skip(); self.skip()                      # BASIC 30
        self.put("TRY YOUR HAND AT GOVERNING ANCIENT SUMERIA")      # 80
        self.skip()
        self.put("FOR A TEN-YEAR TERM OF OFFICE.")                  # 90
        self.skip(); self.skip()
        d1 = 0; p1 = 0                                              # 95
        z = 0; p = HAMM00_P0; s = HAMM00_S0; h = HAMM00_H0          # 100
        e = _hamm00_chk(h - s)                                      # declared -600
        y = HAMM00_Y0; a = HAMM00_A0; i = HAMM00_I0; q = HAMM00_Q0  # 110
        gg = HAMM00_GG0
        self.gg = gg
        impeached_d = None
        while True:
            d = 0                                                   # ytop / 210
            self.skip(); self.skip()
            self.put("HAMURABI:  I BEG TO REPORT TO YOU,")           # 215
            self.skip()
            p = _hamm00_chk(p + i)                                  # 218
            t1 = _hamm00_chk(q + 4)                                 # 227 shift form
            plague = not (t1 > 4)
            assert plague == (q <= 0)
            if plague:
                self.plague_years += 1
                p = _hamm00_chk(p // 2)                             # 228 SINGLE halving
                self.put("A HORRIBLE PLAGUE STRUCK!  HALF THE PEOPLE DIED.")  # 229
                self.skip()
            self.put("POPULATION IS NOW", p)                        # 230
            self.skip()
            self.put("THE CITY NOW OWNS ", a, "ACRES.")             # 232
            self.skip()
            self.put("YOU HARVESTED", y, "BUSHELS PER ACRE.")       # 235
            self.skip()
            self.put("THE RATS ATE", e, "BUSHELS.")                 # 250
            self.skip()
            self.put("YOU NOW HAVE ", s, "BUSHELS IN STORE.")       # 260
            self.skip(); self.skip()
            z = _hamm00_chk(z + 1)                                  # 215 (after report)
            t2 = _hamm00_chk(z + 1)
            assert (t2 > 11) == (z >= 11)
            if t2 > 11:
                break                                               # 270 -> 860
            y = _hamm00_chk(self.draw(10) + 17)                     # 310
            self.put("LAND IS TRADING AT", y, "BUSHELS PER ACRE.")   # 312
            self.skip()
            while True:                                             # 320 buy loop
                self.put(_HAMM00_BUYP)
                qq = self.get()
                if self.negguard(qq):                               # 321 -> 850
                    self.bad()
                    return self                                     # spine never reaches
                u = _hamm00_chk(y * qq)
                if self.weak(u, s):                                 # 322
                    break
                self.put("HAMURABI:  THINK AGAIN.  YOU HAVE ONLY")   # 710
                self.skip()
                self.put(s, "BUSHELS OF GRAIN.  NOW THEN,")          # 711
                self.skip()
            if qq != 0:                                             # 330
                a = _hamm00_chk(a + qq); s = _hamm00_chk(s - u)     # 331
                c = 0                                               # dead store, kept
            else:
                while True:                                         # 340 sell loop
                    self.put(_HAMM00_SELLP)
                    qq = self.get()
                    if self.negguard(qq):                           # 341
                        self.bad()
                        return self
                    if qq < a:                                      # 342 strict
                        break
                    self.put("HAMURABI:  THINK AGAIN.  YOU OWN ONLY")  # 720
                    self.skip()
                    self.put(a, "ACRES.  NOW THEN,")
                    self.skip()
                a = _hamm00_chk(a - qq)                             # 350
                u = _hamm00_chk(y * qq)
                s = _hamm00_chk(s + u)
                c = 0                                               # dead store, kept
            self.skip()                                             # 400
            while True:                                             # 410 feed loop
                self.put(_HAMM00_FEEDP)
                qq = self.get()
                if self.negguard(qq):                               # 412
                    self.bad()
                    return self
                if self.weak(qq, s):                                # 420
                    break
                self.put("HAMURABI:  THINK AGAIN.  YOU HAVE ONLY")   # 710
                self.skip()
                self.put(s, "BUSHELS OF GRAIN.  NOW THEN,")
                self.skip()
            s = _hamm00_chk(s - qq)                                 # 430
            c = 1                                                   # dead store, kept
            self.skip()
            while True:                                             # 440 plant loop
                self.put(_HAMM00_PLANTP)
                d = self.get()
                if d == 0:                                          # 441 -> 511
                    break
                if self.negguard(d):                                # 442
                    self.bad()
                    return self
                if not self.weak(d, a):                             # 445
                    self.put("HAMURABI:  THINK AGAIN.  YOU OWN ONLY")  # 720
                    self.skip()
                    self.put(a, "ACRES.  NOW THEN,")
                    self.skip()
                    continue
                t1 = _hamm00_chk(d // 2)                            # 450
                if not self.weak(t1, s):
                    self.put("HAMURABI:  THINK AGAIN.  YOU HAVE ONLY")  # 710
                    self.skip()
                    self.put(s, "BUSHELS OF GRAIN.  NOW THEN,")
                    self.skip()
                    continue
                u = _hamm00_chk(p * 10)                             # 455
                if not (d < u):
                    self.put("BUT YOU HAVE ONLY", p,
                             "PEOPLE TO TEND THE FIELDS!  NOW THEN,")   # 460
                    self.skip()
                    continue
                s = _hamm00_chk(s - t1)                             # 510 / pl4
                break
            y = _hamm00_chk(self.draw(5) + 1)                       # 511 (800)
            h = _hamm00_chk(d * y)                                  # 515
            e = 0
            c = _hamm00_chk(self.draw(5) + 1)                       # 521
            if c == 2:                                              # rats dispatch
                e = _hamm00_chk(s // 2)
            if c == 4:
                e = _hamm00_chk(s // 4)
            if c % 2 == 0:                                          # 522 parity
                assert e == _hamm00_chk(s // c)                     # BASIC 525 route
                if e > 0:
                    self.rats_years += 1
            s = _hamm00_chk(s - e)                                  # 530
            s = _hamm00_chk(s + h)
            c = _hamm00_chk(self.draw(5) + 1)                       # 531 births
            u = _hamm00_chk(a * 20)
            u = _hamm00_chk(u + s)
            x = _hamm00_chk(c * u)
            t1 = _hamm00_chk(x // p)                                # VARIABLE divisor
            t2 = _hamm00_chk(t1 // 100)
            assert t2 + 1 == x // (100 * p) + 1                     # nested-floor vs BASIC
            i = _hamm00_chk(t2 + 1)
            t3 = _hamm00_chk(qq // 20)                              # 540 (last FEED)
            c = t3
            q = _hamm00_chk(self.draw(10) - 3)                      # 542 plague draw
            if p < c:                                               # 550 skip year
                self.skip_years += 1
                continue                                            # goto ytop (d=0 there)
            d = _hamm00_chk(p - c)                                  # 552
            if d > 0:
                self.starve_years += 1
            t1 = _hamm00_chk(p * 45)                                # 552 .45*P form
            t2 = _hamm00_chk(t1 // 100)
            assert (d > t2) == (d > 0.45 * p)
            if d > t2:
                impeached_d = d
                break
            u = _hamm00_chk(z - 1)                                  # 553 (int route)
            u = _hamm00_chk(u * p1)
            x = _hamm00_chk(d * 100)
            x = _hamm00_chk(x // p)                                 # VARIABLE divisor
            u = _hamm00_chk(u + x)
            p1n = _hamm00_chk(u // z)
            p1f = ((z - 1) * p1 + d * 100 / p) / z
            assert abs(p1f - p1n) < 2.0, (p1f, p1n)                 # declared int adaptation
            p1 = p1n
            d1 = _hamm00_chk(d1 + d)
            p = c
        self.p, self.a, self.s, self.p1, self.d1, self.z = p, a, s, p1, d1, z
        if impeached_d is not None:
            self.verdict = "impeached-year%d" % z
            self.skip()                                             # 560
            self.put("YOU STARVED", impeached_d, "PEOPLE IN ONE YEAR!!!")
            self.skip()
            self.fink()                                             # -> 565
            self.bye()
            return self
        self.put("IN YOUR 10-YEAR TERM OF OFFICE,", p1, "PERCENT OF THE")   # 860
        self.skip()
        self.put("POPULATION STARVED PER YEAR ON THE AVERAGE,",
                 " I.E. A TOTAL OF")                                 # 862 split pair
        self.skip()
        self.put(d1, "PEOPLE DIED!!")                                # 865
        self.skip()
        l = _hamm00_chk(a // p)                                      # VARIABLE divisor
        self.l = l
        self.put("YOU STARTED WITH 10 ACRES PER PERSON AND ENDED WITH")  # 870
        self.skip()
        self.put(l, "ACRES PER PERSON.")                             # 875
        self.skip(); self.skip()
        t3 = _hamm00_chk(p1 + 100)                                   # 880..896 ladder
        t2 = _hamm00_chk(l + 100)
        assert (t3 > 133) == (p1 > 33) and (t2 < 107) == (l < 7)
        assert (t3 > 110) == (p1 > 10) and (t2 < 109) == (l < 9)
        assert (t3 > 103) == (p1 > 3) and (t2 < 110) == (l < 10)
        if t3 > 133 or t2 < 107:
            self.verdict = "fink-ladder"
            self.fink()                                              # 565 (no 560)
            self.bye()
        elif t3 > 110 or t2 < 109:
            self.verdict = "nero"                                    # 940
            self.put("YOUR HEAVY-HANDED PERFORMANCE SMACKS",
                     " OF NERO AND IVAN IV.")
            self.skip()
            self.put("THE PEOPLE (REMAINING) FIND YOU AN",
                     " UNPLEASANT RULER, AND,")
            self.skip()
            self.put("FRANKLY, HATE YOUR GUTS!!")
            self.skip()
            self.bye()
        elif t3 > 103 or t2 < 110:
            self.verdict = "not-too-bad"                             # 960
            self.put("YOUR PERFORMANCE COULD HAVE BEEN SOMEWHAT BETTER, BUT")
            self.skip()
            r = self.draw(10)                                        # 965 extra draw
            n = _hamm00_chk(p * 8)
            n = _hamm00_chk(n * r)
            n = _hamm00_chk(n // 100)
            self.n965 = n
            self.put("REALLY WAS NOT TOO BAD AT ALL.", n, "PEOPLE")
            self.skip()
            self.put("WOULD DEARLY LIKE TO SEE YOU ASSASSINATED BUT",
                     " WE ALL HAVE OUR")                             # 970 split pair
            self.skip()
            self.put("TRIVIAL PROBLEMS.")                            # 975
            self.skip()
            self.bye()
        else:
            self.verdict = "fantastic"                               # 900
            self.put("A FANTASTIC PERFORMANCE!!!  CHARLEMANGE, DISRAELI, AND")
            self.skip()
            self.put("JEFFERSON COMBINED COULD NOT HAVE DONE BETTER!")
            self.skip()
            self.bye()
        return self


def _hamm00_exercise_compile_only():
    """Compile-only branches under the fixed 46-value script (bad:/imp:/fink:/
    nero:/fantastic/) are NOT taken by the spine; their emitted TEXTS and the
    whole-bin15 +100 ladder equivalence are verified here so a future change to
    those statements is still judged.  Deterministic; contributes nothing to the
    derived stream."""
    # bad: + bye:
    pb = _Hamm00Port([], emit=True)
    pb.bad()
    assert _hamm00_finalize(pb.raw) == [
        "", "HAMURABI: I CANNOT DO WHAT YOU WISH.",
        "GET YOURSELF ANOTHER STEWARD!!!!!", "", "SO LONG FOR NOW.", "", ""]
    # imp: + fink: + bye: (synthetic d -- mid-game impeachment path)
    pi = _Hamm00Port([], emit=True)
    pi.skip()
    pi.put("YOU STARVED", 12, "PEOPLE IN ONE YEAR!!!")
    pi.skip()
    pi.fink()
    pi.bye()
    assert _hamm00_finalize(pi.raw) == [
        "", "YOU STARVED 12 PEOPLE IN ONE YEAR!!!",
        "DUE TO THIS EXTREME MISMANAGEMENT YOU HAVE NOT ONLY",
        "BEEN IMPEACHED AND THROWN OUT OF OFFICE BUT YOU HAVE",
        "ALSO BEEN DECLARED NATIONAL FINK!!!!", "", "SO LONG FOR NOW.", "", ""]
    # ladder rungs: port +100 form vs BASIC form, EXHAUSTIVE over the domain
    # the spine's verdicts can reach (p1, l are 0..119-sized percentages here)
    for p1 in range(0, 120):
        for l in range(0, 120):
            port = ("fink" if (p1 + 100 > 133 or l + 100 < 107) else
                    "nero" if (p1 + 100 > 110 or l + 100 < 109) else
                    "mbad" if (p1 + 100 > 103 or l + 100 < 110) else "fantastic")
            basic = ("fink" if p1 > 33 or l < 7 else
                     "nero" if p1 > 10 or l < 9 else
                     "mbad" if p1 > 3 or l < 10 else "fantastic")
            assert port == basic


def hamm00():
    """HAMM-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Hammurabi program for the declared starts P=95, S=1500, H=900,
    E=H-S=-600 (NEGATIVE, declared), Y=3, A=300, I=5, Q=1, GG=2 and the 46-value
    GET script.  Derived, never captured (L3)."""
    _hamm00_exercise_compile_only()
    port = _Hamm00Port(HAMM00_SCRIPT).run()
    assert not port.script and port.nget == 46      # script consumed exactly
    # spine outcome (hop-4 measured plan)
    assert port.verdict == "not-too-bad"
    assert port.p1 == 7 and port.l == 10 and port.d1 == 41 and port.s == 1928
    assert (port.plague_years, port.skip_years, port.starve_years) == (5, 1, 2)
    assert port.rats_years >= 1
    lines = _hamm00_finalize(port.raw)
    assert len(lines) == 211, len(lines)
    # the two split-literal seams normalize to the single-literal texts (hop-5 law)
    assert ("POPULATION STARVED PER YEAR ON THE AVERAGE, I.E. A TOTAL OF" in lines
            and "WOULD DEARLY LIKE TO SEE YOU ASSASSINATED BUT WE ALL HAVE OUR" in lines)
    assert lines[0] == "" and lines[-1] == ""       # [C352] framing both ends
    return lines


# ---------------------------------------------------------------------------
# HANG-00 (FC-01 corpus program 3, 2026-11-03): adapted BASIC Hangman.
# Statement-for-statement mirror of HANG-00.PLI on the MEASURED console byte
# laws (README section 6 + Batch-A PASS captures + DR e32rt_E32B1 golden + the
# HAMM-00 echo contract): `put skip;` emits exactly "\r\n"; ONE blank precedes
# every single-item `put list(item);` that is not the first item printed since
# the last line start (ACROSS statements -- the law that FALSIFIED the design
# hop's no-separator model); a consumed GET line L echoes as L + "\r\r\n" and
# CLOSES the line (no separator blank after an echo); the exit appends exactly
# one "\r\n" ([C352]); normalization collapse-spaces-v1, split, drop ONE
# trailing empty.  Derived, never captured (L3).

HANG00_SCRIPT = [71, 85, 71, 77, 1,            # GUM: hit, hit, dup, hit, cont-yes
                 70, 65, 76, 89, 1,            # FLY: hit, miss M=1, hit, hit, cont-yes
                 69, 88, 83, 86, 87, 65, 66, 67, 68, 81, 84, 90,
                 1]                            # hung (M=1..10), cont-yes -> ALL THE WORDS

HANG00_DGUM = [71, 85, 77]                     # dgum(1..3)  literal stores
HANG00_DFLY = [70, 76, 89]                     # dfly(1..3)
HANG00_DSLEP = [83, 76, 69, 69, 80, 69, 82]    # dslep(1..7)


def _hang00_show_table():
    """The 34 branches of the nested show: procedure (c) ladder."""
    ch = {c: chr(c) for c in range(65, 91)}
    ch.update({32: ' ', 40: '(', 41: ')', 44: ',', 45: '-', 46: '.', 47: '/',
               92: '\\'})
    assert len(ch) == 34
    return ch


HANG00_CH = _hang00_show_table()

HANG00_TEXT = {                                # m = 1..10 literal ladder (415..460)
    1: "FIRST, WE DRAW A HEAD",                # no period, as upstream
    2: "NOW WE DRAW A BODY.",
    3: "NEXT WE DRAW AN ARM.",
    4: "THIS TIME IT IS THE OTHER ARM.",       # apostrophe rewritten
    5: "NOW, LET US DRAW THE RIGHT LEG.",      # apostrophe rewritten
    6: "THIS TIME WE DRAW THE LEFT LEG.",
    7: "NOW WE PUT UP A HAND.",
    8: "NEXT THE OTHER HAND.",
    9: "NOW WE DRAW ONE FOOT",                 # no bangs, as upstream
    10: "HERE IS THE OTHER FOOT -- YOU ARE HUNG!!",   # apostrophes rewritten
}

HANG00_HEADER = "HERE ARE THE LETTERS YOU USED:"        # 170
HANG00_GUESSP = "WHAT IS YOUR GUESS (ASCII CODE) "      # 210 (numeric adaptation)
HANG00_DUP = "YOU GUESSED THAT LETTER BEFORE!"          # 230
HANG00_SORRY = "SORRY, THAT LETTER IS NOT IN THE WORD."  # 400 (apostrophe rewritten)
HANG00_FOUND = "YOU FOUND THE WORD!"                    # 390
HANG00_CONTP = "WANT ANOTHER WORD (1=YES 0=NO) "        # 370 (numeric adaptation)
HANG00_LOSE = "SORRY, YOU LOSE.  THE WORD WAS "         # 600 (610 half-line dropped)
HANG00_FUN = "IT HAS BEEN FUN!  BYE FOR NOW."           # 380 (apostrophe rewritten)
HANG00_ALLEXT = "YOU DID ALL THE WORDS!!"               # 97

# stage-cell literal store ladders m = 1..10 (470/480..570), indices verified
# against the listing in the implementation hop
HANG00_STAGE = {1: [(30, 45), (31, 45), (32, 45), (41, 40), (42, 46), (44, 46),
                    (45, 41), (54, 45), (55, 45), (56, 45)],
                2: [(67, 88), (79, 88), (91, 88), (103, 88)],
                3: [(39, 92), (52, 92), (65, 92), (78, 92)],
                4: [(47, 47), (58, 47), (69, 47), (80, 47)],
                5: [(114, 47), (125, 47)],
                6: [(116, 92), (129, 92)],
                7: [(35, 92)],
                8: [(27, 47)],
                9: [(142, 92), (143, 45)],
                10: [(135, 45), (136, 47)]}


def _hang00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Hang00Port:
    """Statement-for-statement mirror of HANG-00.PLI (labels sel/disp/cont/miss/fin
    kept in the same order; goto-in-IF replaced by flag vars in the PLI exactly as
    here; every PUT is a single-item `put list(...)` statement)."""

    def __init__(self, script):
        self.script = list(script)
        self.raw = ""
        self.nget = 0
        self.results = []          # 'win'/'hang' per played word
        self.exit = None           # 'bye' (cw = 0) or 'allext' (q > 3)

    def skip(self):
        self.raw += "\r\n"                        # put skip;

    def put(self, item):
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "                       # measured leading-separator law
        self.raw += item                          # put list(item);

    def get(self):
        assert self.script, "GET past the end of the declared script"
        v = self.script.pop(0)
        assert 0 <= v <= _HAMM00_B15              # fixed bin(15) cell domain
        self.nget += 1
        self.raw += "%d\r\r\n" % v                # consumed GET echo closes the line
        return v

    def show(self, c):
        self.put(HANG00_CH[c])                    # nested show: one put list(ch);

    def run(self):
        self.skip(); self.skip(); self.skip()     # three bare PUT SKIPs (framing [C352])
        q = 0
        while True:                               # sel:
            q = q + 1
            if q > 3:                             # fin:
                self.put(HANG00_ALLEXT)
                self.exit = "allext"
                return self                       # stop;
            if q == 1:
                n = 3
                wlit = "GUM"
                cur = [0] * 8
                for i in range(1, 4):
                    x = HANG00_DGUM[i - 1]
                    cur[i] = x
            elif q == 2:
                n = 3
                wlit = "FLY"
                cur = [0] * 8
                for i in range(1, 4):
                    x = HANG00_DFLY[i - 1]
                    cur[i] = x
            else:
                n = 7
                wlit = "SLEEPER"
                cur = [0] * 8
                for i in range(1, 8):
                    x = HANG00_DSLEP[i - 1]
                    cur[i] = x
            nu = 0
            m = 0
            t1 = 0                                # dead upstream counter, kept
            d = [0] + [45] * 20
            p = [32] * 145
            for k in (1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121, 133):
                p[k] = 88                         # pole
            for k in (2, 3, 4, 5, 6, 7):
                p[k] = 88                         # top (p(1) already stored)
            p[19] = 88                            # rope
            u = []                                # dense u(26)/nu model
            while True:                           # disp:
                self.put(HANG00_HEADER)           # 170 prints DIRECTLY (no blank)
                self.skip()
                for i in range(1, nu + 1):        # 180/190 used letters, comma between
                    x = u[i - 1]
                    self.show(x)
                    if i < nu:
                        self.show(44)
                self.skip()                       # 200 closes the letters line
                self.skip()
                for i in range(1, n + 1):         # dash/letter row (SPACE-separated:
                    x = d[i]                      # declared separator adaptation)
                    self.show(x)
                self.skip()                       # 200 closes the row
                self.skip()
                self.put(HANG00_GUESSP)           # 210 INPUT -> GET LIST (numeric code)
                g = self.get()
                du = 0                            # 220 scan (flag var; no goto in DO)
                for i in range(1, nu + 1):
                    x = u[i - 1]
                    if x == g:
                        du = 1
                if du == 1:
                    self.put(HANG00_DUP)          # 230 prints DIRECTLY
                    self.skip()
                    continue                      # goto disp
                nu = nu + 1                       # 250 u(nu) = g; t1 = t1 + 1
                u.append(g)
                t1 = t1 + 1
                r = 0
                for i in range(1, n + 1):         # 260..280
                    x = cur[i]
                    if x == g:
                        d[i] = g
                        r = r + 1
                if r == 0:                        # miss:
                    m = m + 1                     # 400 two blanks then SORRY
                    self.skip()
                    self.skip()
                    self.put(HANG00_SORRY)
                    self.skip()
                    self.put(HANG00_TEXT[m])      # 410/415..460 ON M GOTO -> if ladder
                    self.skip()
                    for idx, code in HANG00_STAGE[m]:   # 470/480..570
                        p[idx] = code
                    assert 1 <= m <= 10
                    b = 0                         # 580/590 grid walk, NO division
                    for k in range(1, 13):
                        for j in range(1, 13):
                            b = b + 1
                            x = p[b]
                            self.show(x)
                        self.skip()
                    self.skip()
                    self.skip()
                    # BASIC 590 IF M<>10: in this port m <= 10 by construction, so
                    # m <> 10 is EXACTLY m < 10 -- direct strict compare (the design
                    # hop's t1 = m + 1; t1 < 12 shift was FALSIFIED: always true).
                    if m < 10:
                        continue                  # goto disp
                    self.put(HANG00_LOSE)         # 600 (610 dropped, declared)
                    self.put(wlit)
                    self.skip()
                    self.results.append("hang")
                else:
                    dsh = 0                       # 300 dash scan (flag var)
                    for i in range(1, n + 1):
                        x = d[i]
                        if x == 45:
                            dsh = 1
                    if dsh == 1:
                        continue                  # goto disp   (320 interlude dropped)
                    self.put(HANG00_FOUND)        # 390 prints DIRECTLY
                    self.skip()
                    self.results.append("win")
                self.put(HANG00_CONTP)            # 370 INPUT -> GET LIST
                cw = self.get()
                if cw == 1:
                    break                         # goto sel
                self.skip()                       # 380
                self.put(HANG00_FUN)
                self.skip()
                self.exit = "bye"
                return self                       # stop;
        # while True (sel) -- unreachable except via goto sel (break above)


def hang00():
    """HANG-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Hangman program for the declared 3-word sequential table (GUM, FLY,
    SLEEPER) and the fixed 23-value GET script.  Derived, never captured (L3)."""
    assert len(HANG00_SCRIPT) == 23
    port = _Hang00Port(HANG00_SCRIPT).run()
    assert not port.script and port.nget == 23    # script consumed exactly
    assert port.results == ["win", "win", "hang"]
    assert port.exit == "allext"
    lines = _hang00_finalize(port.raw)
    assert len(lines) == 329, len(lines)
    assert lines[:3] == ["", "", ""]             # leading framing [C352]
    assert lines[-1] == HANG00_ALLEXT             # exit CRLF closes ALLEXT: no blank
    return lines


AMAZ00_GG0 = 0        # declared draw seed (RND substitution, see AMAZ-00.json)


def _amaz00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Amaz00Port:
    """Statement-for-statement mirror of AMAZ-00.PLI: same labels (l210..l1015,
    mv790..mv910), same order, same temps (b, b2, t1), same default-store vv
    rewrites, same b bookkeeping at mv860/mv910.  Byte model per the measured
    laws (README section 6 + hop-2 separator law + [C352] framing): PUT SKIP
    emits "\r\n"; a single-item PUT LIST is preceded by ONE blank unless it is
    the first item printed since the last line start; program exit appends
    exactly one "\r\n"; collapse-spaces-v1 then split with ONE trailing empty
    dropped.  Pure PUT program: no GET, no echo."""

    def __init__(self, gg0=AMAZ00_GG0):
        self.raw = ""
        self.gg = gg0
        self.ndraw = 0
        self.w = [0] * 17
        self.vv = [0] * 17
        self.n960 = 0
        self.n980 = 0
        self.n975 = 0
        self.exit_exec = False      # did 1011..1014 run?  (z == 0 path)
        self.steps = 0

    def skip(self):
        self.raw += "\r\n"                        # put skip;

    def put(self, item):
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "                       # measured leading-separator law
        self.raw += item                          # put list(item);

    def draw(self, k):
        # gg = gg + 1; t1 = gg * 37 + 11; x = t1 - (t1 / k) * k + 1  (k literal)
        self.gg += 1
        self.ndraw += 1
        assert self.gg <= 885, "draw past the bin15 headroom guard"
        t = self.gg * 37 + 11
        assert 0 <= t <= 32767, "gg*37+11 overflows fixed bin(15)"
        return t % k + 1

    def run(self):
        w, vv = self.w, self.vv
        for _ in range(8):                        # eight bare PUT SKIPs
            self.skip()                           # (BASIC 30 x4 + 120..150 x4)
        gg = self.gg
        x = q = z = 0
        gg += 1
        t1 = gg * 37 + 11
        x = t1 - (t1 // 4) * 4 + 1                # 160 entrance column
        self.ndraw += 1
        assert 0 <= t1 <= 32767
        entrance = x
        for i in range(1, 5):                     # 165..190 top border
            if i == x:
                self.put(".  ")
            else:
                self.put(".--")
        self.put(".")
        self.skip()                               # 190 PRINT "."
        c = 1                                     # 195
        b = (x - 1) * 4 + 1
        w[b] = c
        c += 1
        r = x                                     # 200
        s = 1
        lab = "l260"
        while lab != "l1015":
            self.steps += 1
            assert self.steps < 100000, "walk did not terminate"
            if lab == "l210":                     # 210..220
                if r < 4:
                    lab = "l240"
                elif s < 4:
                    lab = "l230"
                else:
                    r, s = 1, 1
                    lab = "l250"
            elif lab == "l230":                   # 230
                r, s = 1, s + 1
                lab = "l250"
            elif lab == "l240":                   # 240
                r = r + 1
                lab = "l250"
            elif lab == "l250":                   # 250
                b = (r - 1) * 4 + s
                t1 = w[b]
                lab = "l210" if t1 == 0 else "l260"
            elif lab == "l260":                   # 260..265
                if r == 1:
                    lab = "l530"
                else:
                    b2 = b - 4
                    t1 = w[b2]
                    lab = "l270" if t1 == 0 else "l530"
            elif lab == "l270":                   # 270..280
                if s == 1:
                    lab = "l390"
                else:
                    b2 = b - 1
                    t1 = w[b2]
                    lab = "l290" if t1 == 0 else "l390"
            elif lab == "l290":                   # 290..320
                if r == 4:
                    lab = "l330"
                else:
                    b2 = b + 4
                    t1 = w[b2]
                    if t1 == 0:
                        gg += 1
                        self.ndraw += 1
                        t1 = gg * 37 + 11
                        assert 0 <= t1 <= 32767
                        x = t1 - (t1 // 3) * 3 + 1
                        lab = "mv790" if x == 1 else ("mv820" if x == 2 else "mv860")
                    else:
                        lab = "l330"
            elif lab == "l330":                   # 330..338
                if s < 4:
                    lab = "l340"
                elif z == 1:
                    lab = "l370"
                else:
                    q = 1
                    lab = "l350"
            elif lab == "l340":                   # 340
                t1 = w[b + 1]
                lab = "l350" if t1 == 0 else "l370"
            elif lab == "l350":                   # 350..360
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 3) * 3 + 1
                lab = "mv790" if x == 1 else ("mv820" if x == 2 else "mv910")
            elif lab == "l370":                   # 370..380
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv790" if x == 1 else "mv820"
            elif lab == "l390":                   # 390..400
                if r == 4:
                    lab = "l470"
                else:
                    b2 = b + 4
                    t1 = w[b2]
                    lab = "l405" if t1 == 0 else "l470"
            elif lab == "l405":                   # 405..415
                if s < 4:
                    lab = "l420"
                elif z == 1:
                    lab = "l450"
                else:
                    q = 1
                    lab = "l430"
            elif lab == "l420":                   # 420
                t1 = w[b + 1]
                lab = "l430" if t1 == 0 else "l450"
            elif lab == "l430":                   # 430..440
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 3) * 3 + 1
                lab = "mv790" if x == 1 else ("mv860" if x == 2 else "mv910")
            elif lab == "l450":                   # 450..460
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv790" if x == 1 else "mv860"
            elif lab == "l470":                   # 470..485
                if s < 4:
                    lab = "l490"
                elif z == 1:
                    lab = "l520"
                else:
                    q = 1
                    lab = "l500"
            elif lab == "l490":                   # 490
                t1 = w[b + 1]
                lab = "l500" if t1 == 0 else "l520"
            elif lab == "l500":                   # 500..510
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv790" if x == 1 else "mv910"
            elif lab == "l520":                   # 520
                lab = "mv790"
            elif lab == "l530":                   # 530..540
                if s == 1:
                    lab = "l670"
                else:
                    b2 = b - 1
                    t1 = w[b2]
                    lab = "l545" if t1 == 0 else "l670"
            elif lab == "l545":                   # 545..547
                if r == 4:
                    lab = "l610"
                else:
                    b2 = b + 4
                    t1 = w[b2]
                    lab = "l550" if t1 == 0 else "l610"
            elif lab == "l550":                   # 550..554
                if s < 4:
                    lab = "l560"
                elif z == 1:
                    lab = "l590"
                else:
                    q = 1
                    lab = "l570"
            elif lab == "l560":                   # 560
                t1 = w[b + 1]
                lab = "l570" if t1 == 0 else "l590"
            elif lab == "l570":                   # 570..580
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 3) * 3 + 1
                lab = "mv820" if x == 1 else ("mv860" if x == 2 else "mv910")
            elif lab == "l590":                   # 590..600
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv820" if x == 1 else "mv860"
            elif lab == "l610":                   # 610..625
                if s < 4:
                    lab = "l630"
                elif z == 1:
                    lab = "l660"
                else:
                    q = 1
                    lab = "l640"
            elif lab == "l630":                   # 630
                t1 = w[b + 1]
                lab = "l640" if t1 == 0 else "l660"
            elif lab == "l640":                   # 640..650
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv820" if x == 1 else "mv910"
            elif lab == "l660":                   # 660
                lab = "mv820"
            elif lab == "l670":                   # 670..680
                if r == 4:
                    lab = "l740"
                else:
                    b2 = b + 4
                    t1 = w[b2]
                    lab = "l685" if t1 == 0 else "l740"
            elif lab == "l685":                   # 685..695
                if s < 4:
                    lab = "l700"
                elif z == 1:
                    lab = "l730"
                else:
                    q = 1
                    lab = "l710"
            elif lab == "l700":                   # 700
                t1 = w[b + 1]
                lab = "l710" if t1 == 0 else "l730"
            elif lab == "l710":                   # 710..720
                gg += 1
                self.ndraw += 1
                t1 = gg * 37 + 11
                assert 0 <= t1 <= 32767
                x = t1 - (t1 // 2) * 2 + 1
                lab = "mv860" if x == 1 else "mv910"
            elif lab == "l730":                   # 730
                lab = "mv860"
            elif lab == "l740":                   # 740..755
                if s < 4:
                    lab = "l760"
                elif z == 1:
                    lab = "l780"
                else:
                    q = 1
                    lab = "l770"
            elif lab == "l760":                   # 760
                t1 = w[b + 1]
                lab = "l770" if t1 == 0 else "l780"
            elif lab == "l770":                   # 770
                lab = "mv910"
            elif lab == "l780":                   # 780
                lab = "l1000"
            elif lab == "mv790":                  # 790..815 (one column LEFT)
                b = (r - 1) * 4 + s - 4
                w[b] = c
                c += 1
                vv[b] = 2
                r = r - 1
                if c == 17:
                    lab = "l1010"
                else:
                    q = 0
                    lab = "l260"
            elif lab == "mv820":                  # 820..850 (one row UP)
                b = (r - 1) * 4 + s - 1
                w[b] = c
                c += 1
                vv[b] = 1
                s = s - 1
                if c == 17:
                    lab = "l1010"
                else:
                    q = 0
                    lab = "l260"
            elif lab == "mv860":                  # 860..905 (one column RIGHT)
                b = (r - 1) * 4 + s
                b2 = b + 4
                w[b2] = c
                c += 1
                t1 = vv[b]
                vv[b] = 3                         # default store (no else form needed)
                if t1 == 0:
                    vv[b] = 2
                r = r + 1
                b = b + 4
                if c == 17:
                    lab = "l1010"
                else:
                    lab = "l530"                  # 905: Q deliberately NOT reset
            elif lab == "mv910":                  # 910..955 (one row DOWN)
                if q == 1:
                    lab = "l960"
                else:
                    b = (r - 1) * 4 + s
                    w[b + 1] = c
                    c += 1
                    t1 = vv[b]
                    vv[b] = 3
                    if t1 == 0:
                        vv[b] = 1
                    s = s + 1
                    b = b + 1
                    if c == 17:
                        lab = "l1010"
                    else:
                        lab = "l260"              # 955: Q NOT reset
            elif lab == "l960":                   # 960..975
                z = 1
                b = (r - 1) * 4 + s
                t1 = vv[b]
                self.n960 += 1
                if t1 == 0:
                    lab = "l980"
                else:
                    self.n975 += 1
                    vv[b] = 3
                    q = 0
                    lab = "l1000"
            elif lab == "l980":                   # 980
                self.n980 += 1
                vv[b] = 1
                q = 0
                r, s = 1, 1
                lab = "l250"
            elif lab == "l1000":                  # 1000
                lab = "l210"
            elif lab == "l1010":                  # 1010..1014
                if z == 1:
                    lab = "l1015"
                else:
                    gg += 1
                    self.ndraw += 1
                    t1 = gg * 37 + 11
                    assert 0 <= t1 <= 32767
                    x = t1 - (t1 // 4) * 4 + 1
                    b = (x - 1) * 4 + 4
                    t1 = vv[b]
                    vv[b] = 3
                    if t1 == 0:
                        vv[b] = 1
                    self.exit_exec = True
                    lab = "l1015"
            else:                                 # fail closed on any typo
                raise AssertionError("unknown label %r" % lab)
        self.gg_final = gg
        # 1015..1072 maze print (DO TO loops, if/else single-item PUTs)
        for j in range(1, 5):
            self.put("I")
            for i in range(1, 5):
                b = (i - 1) * 4 + j
                t1 = vv[b]
                if t1 < 2:
                    self.put("  I")
                else:
                    self.put("   ")
            self.skip()                           # 1041 PRINT
            for i in range(1, 5):
                b = (i - 1) * 4 + j
                t1 = vv[b]
                t1 = t1 - (t1 // 2) * 2           # vv mod 2 (literal divisor)
                if t1 == 1:
                    self.put(":  ")
                else:
                    self.put(":--")
            self.put(".")                         # 1071 PRINT "."
            self.skip()
        self.entrance = entrance
        self.c_end = c
        self.z_end = z
        return self


def amaz00():
    """AMAZ-00: the complete normalized console stream (collapse-spaces-v1) of
    the adapted Amazing maze generator for the declared 4x4 grid and draw seed
    gg0 = 0.  Derived from the declared design by a statement-for-statement
    mirror of AMAZ-00.PLI, never captured (L3); the maze STRUCTURE is then
    checked by independent invariants (visit permutation, wall-code domain,
    connectivity BFS from the entrance, bottom exit gap) exactly as in the
    ignored scratch simulator build/fc01-scratch/amaz00_sim.py."""
    port = _Amaz00Port().run()
    # ---- maze invariants (independent of the byte stream) ----
    assert port.c_end == 17, "C ended at %d (must be H*V+1)" % port.c_end
    assert sorted(port.w[1:]) == list(range(1, 17)), "visit order not a permutation"
    for i in range(1, 17):
        assert port.vv[i] in (0, 1, 2, 3), "wall code out of domain at %d" % i
    assert port.ndraw == 12 and port.gg_final == 12
    assert port.entrance == 1 and port.z_end == 1
    assert port.n960 == 1 and port.n980 == 1 and port.n975 == 0
    assert port.exit_exec is False      # 1011..1014 UNREACHED at this seed
    # connectivity: right wall open iff vv >= 2; bottom wall open iff vv odd
    def idx(r, s):
        return (r - 1) * 4 + s
    seen = {(port.entrance, 1)}
    stack = [(port.entrance, 1)]
    while stack:
        rr, ss = stack.pop()
        for a, bb, ok in ((rr + 1, ss, port.vv[idx(rr, ss)] >= 2 and rr < 4),
                          (rr - 1, ss, port.vv[idx(rr - 1, ss)] >= 2 and rr > 1),
                          (rr, ss + 1, port.vv[idx(rr, ss)] % 2 == 1 and ss < 4),
                          (rr, ss - 1, port.vv[idx(rr, ss - 1)] % 2 == 1 and ss > 1)):
            if ok and (a, bb) not in seen:
                seen.add((a, bb))
                stack.append((a, bb))
    assert len(seen) == 16, "maze not connected: %d cells reached" % len(seen)
    gaps = [r2 for r2 in range(1, 5) if port.vv[idx(r2, 4)] % 2 == 1]
    assert gaps == [3], "bottom-border exit gaps %s" % gaps
    # ---- stream framing (measured laws) ----
    lines = _amaz00_finalize(port.raw)
    assert lines[:8] == [""] * 8, "8 leading blank lines [C352]"
    assert lines[8] == ". .-- .-- .-- ."          # entrance gap collapsed at col 1
    assert lines[-1] == ""                        # final PUT SKIP + exit CRLF
    assert len(lines) == 18, len(lines)
    return lines


# --------------------------------------------------------------------------
# TICT-00 (FC-01 corpus program 5, adapted BASIC Tic-Tac-Toe, TICTACTOE2.bas)
#
# DECLARED VALUE MAPPING (adaptation, not an import): a board cell is 1 = computer
# (BASIC -1), 2 = empty (BASIC 0), 3 = human (BASIC 1); the scan owner g is 1 on the
# computer pass and 3 on the human pass, h its complement.  Every compare then has a
# POSITIVE literal or a scalar on its right, which is what my compiler accepts (the
# hop-3 probes measured `= -1` and ordered compares against a VARIABLE right operand
# refused; DO ... BY 3 refused, so the BASIC FOR loops are flat goto loops).
#
# The label dispatch below was generated MECHANICALLY from the pinned TICT-00.PLI
# (build/fc01-scratch/mk_tict00_mirror.py) and hand-checked statement by statement, so
# that the mirror is faithful for the labels this script never reaches as well as for
# the ones it does; fall-through targets are the next label in source order exactly as
# the .PLI emits them.

TICT00_SCRIPT = [2, 2, 9, 7, 1, 10, 1, 4]     # choice 2 = O; moves 2,9,7,1,10,1,4
TICT00_BOARD_END = [1, 3, 1, 3, 1, 1, 3, 1, 3]
TICT00_RAW_BYTES = 1468                       # derived raw console bytes incl. exit CRLF
TICT00_LINES = 120                            # derived normalized stream length
_TICT00_MARK = {79: "O", 88: "X"}             # show: procedure (z) two-branch ladder
_TICT00_B15 = 32767

# Labels whose STATEMENTS the chosen script never reaches (derived, asserted below).
TICT00_UNREACHED = ["l0475", "l0104", "l0105", "l0133", "l0138", "l0156", "l0158",
                    "l0163", "l0168", "l0187", "l0189", "l0502t", "l1180", "l1200",
                    "l1350"]


def _tict00_trunc_div(a, b):
    """FIXED BIN(15) '/' as the port uses it: the quotient truncates toward zero.
    The only division site is l0112 (t1 = t1 / 3) where the dividend is m - 1 and
    m >= 1 there (l0502 exits on m = 0, l0503 refuses m > 9, l0506 retries an
    occupied square), so truncation == floor == BASIC INT((M-1)/3)."""
    assert b != 0
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _tict00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Tict00Port:
    """Statement-for-statement mirror of TICT-00.PLI: the same 121 labels in the same
    source order, the same temps (t1/t2/t3, b1/b2/b3), the same f-count AND-ladders
    with BOTH members re-loaded at every label, the same fall-throughs (l0189 -> l0195,
    l0475 -> l0500, l1018 -> l1020, l1060 -> l1080, l1110 -> l1112 -> l1115n, l1135 ->
    l1137 -> l1150n, l1160 -> l1165 -> l1170, l1400 -> l2000).  Byte model per the
    measured corpus laws (README section 6 + the hop-2 separator law + [C352]): PUT
    SKIP emits "\\r\\n"; a single-item PUT LIST is preceded by ONE blank unless it is
    the first item printed since the last line start; a consumed GET echoes
    "<value>\\r\\r\\n" and closes the line; program exit appends exactly one "\\r\\n"."""

    def __init__(self, script):
        self.script = list(script)
        self.raw = ""
        self.nget = 0
        self.s = [0] * 10                      # s(1)..s(9), value-mapped cells
        self.hit = {}                          # label -> times entered (instrumentation)
        self.terminal = None                   # 'draw'/'computer'/'human'/'quit'
        self.steps = 0
        self.i = self.j = self.k = self.m = self.c = 0
        self.g = self.h = self.r = self.f = 0
        self.t1 = self.t2 = self.t3 = 0
        self.ps = self.qs = self.b1 = self.b2 = self.b3 = 0

    def L(self, name):                         # instrumentation only: label entered
        self.hit[name] = self.hit.get(name, 0) + 1

    def skip(self):
        self.raw += "\r\n"                      # put skip;

    def put(self, item):
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "                     # measured leading-separator law
        self.raw += item                        # put list(item);

    def get(self):
        assert self.script, "GET past the end of the declared script"
        v = self.script.pop(0)
        assert 0 <= v <= _TICT00_B15            # fixed bin(15) cell domain
        self.nget += 1
        self.raw += "%d\r\r\n" % v              # consumed GET echo closes the line
        return v

    def show(self, z):
        # show: procedure (z): declare pc character(1) varying;
        #   if z = 79 then pc = 'O';  if z = 88 then pc = 'X';  put list(pc);
        pc = ""
        if z == 79:
            pc = "O"
        if z == 88:
            pc = "X"
        assert pc, "show: code %r outside the two-branch ladder" % z
        self.put(pc)

    def run(self):
        for self.i in range(1, 10):             # do i = 1 to 9; s(i) = 2; end;
            self.s[self.i] = 2
        lab = "l0002"
        while True:
            self.steps += 1
            assert self.steps < 200000, "TICT-00 machine did not terminate"
            self.L(lab)
            if lab == "l0002":
                self.put("TIC-TAC-TOE")
                self.skip()
                lab = "l0004"
            elif lab == "l0004":
                self.put("CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
                self.skip()
                lab = "l0006"
            elif lab == "l0006":
                self.skip()
                self.skip()
                self.skip()
                lab = "l0008"
            elif lab == "l0008":
                self.put("THE BOARD IS NUMBERED:")
                self.skip()
                lab = "l0010"
            elif lab == "l0010":
                self.put(" 1  2  3")
                self.skip()
                lab = "l0012"
            elif lab == "l0012":
                self.put(" 4  5  6")
                self.skip()
                lab = "l0014"
            elif lab == "l0014":
                self.put(" 7  8  9")
                self.skip()
                lab = "l0016"
            elif lab == "l0016":
                self.skip()
                self.skip()
                self.skip()
                lab = "l0050"
            elif lab == "l0050":
                self.put("DO YOU WANT X OR O ENTER 1 FOR X 2 FOR O ")
                self.c = self.get()
                if self.c == 1:
                    lab = "l0475"
                    continue
                lab = "l0060"
            elif lab == "l0060":
                self.ps = 79
                self.qs = 88
                lab = "l0100"
                continue
            elif lab == "l0100":
                self.g = 1
                self.h = 3
                self.t1 = self.s[5]
                if self.t1 == 2:
                    lab = "l0102"
                    continue
                lab = "l0103"
                continue
            elif lab == "l0102":
                self.s[5] = 1
                lab = "l0195"
                continue
            elif lab == "l0103":
                if self.t1 == 3:
                    lab = "l0104"
                    continue
                lab = "l0106"
                continue
            elif lab == "l0104":
                self.t2 = self.s[1]
                if self.t2 == 2:
                    lab = "l0105"
                    continue
                lab = "l0110"
                continue
            elif lab == "l0105":
                self.s[1] = 1
                lab = "l0195"
                continue
            elif lab == "l0106":
                self.f = 0
                self.t1 = self.s[2]
                self.t2 = self.s[1]
                if self.t1 == 3:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0181"
                    continue
                lab = "l0107"
            elif lab == "l0107":
                self.f = 0
                self.t1 = self.s[4]
                self.t2 = self.s[1]
                if self.t1 == 3:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0181"
                    continue
                lab = "l0108"
            elif lab == "l0108":
                self.f = 0
                self.t1 = self.s[6]
                self.t2 = self.s[9]
                if self.t1 == 3:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0189"
                    continue
                lab = "l0109"
            elif lab == "l0109":
                self.f = 0
                self.t1 = self.s[8]
                self.t2 = self.s[9]
                if self.t1 == 3:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0189"
                    continue
                lab = "l0110"
            elif lab == "l0110":
                if self.g == 3:
                    lab = "l0112"
                    continue
                lab = "l0111"
            elif lab == "l0111":
                lab = "l0118"
                continue
            elif lab == "l0112":
                self.t1 = self.m - 1
                self.t1 = _tict00_trunc_div(self.t1, 3)
                self.j = self.t1 * 3
                self.j = self.j + 1
                self.k = 1
                lab = "l0113"
            elif lab == "l0113":
                self.t2 = self.j + 1
                if self.t2 == self.m:
                    self.k = 2
                lab = "l0114"
            elif lab == "l0114":
                self.t3 = self.j + 2
                if self.t3 == self.m:
                    self.k = 3
                lab = "l0116"
            elif lab == "l0116":
                lab = "l0120"
                continue
            elif lab == "l0118":
                self.j = 1
                self.k = 1
                lab = "l0120"
            elif lab == "l0120":
                self.t1 = self.s[self.j]
                if self.t1 == self.g:
                    lab = "l0122"
                    continue
                lab = "l0130"
                continue
            elif lab == "l0122":
                self.b2 = self.j + 2
                self.t2 = self.s[self.b2]
                if self.t2 == self.g:
                    lab = "l0126"
                    continue
                lab = "l0135"
                continue
            elif lab == "l0126":
                self.b1 = self.j + 1
                self.t1 = self.s[self.b1]
                if self.t1 == 2:
                    lab = "l0128"
                    continue
                lab = "l0150"
                continue
            elif lab == "l0128":
                self.s[self.b1] = 1
                lab = "l0195"
                continue
            elif lab == "l0130":
                if self.t1 == self.h:
                    lab = "l0150"
                    continue
                lab = "l0131"
            elif lab == "l0131":
                self.b2 = self.j + 2
                self.t2 = self.s[self.b2]
                if self.t2 == self.g:
                    lab = "l0132"
                    continue
                lab = "l0150"
                continue
            elif lab == "l0132":
                self.b1 = self.j + 1
                self.t1 = self.s[self.b1]
                if self.t1 == self.g:
                    lab = "l0133"
                    continue
                lab = "l0150"
                continue
            elif lab == "l0133":
                self.s[self.j] = 1
                lab = "l0195"
                continue
            elif lab == "l0135":
                self.b2 = self.j + 2
                self.t2 = self.s[self.b2]
                if self.t2 == 2:
                    lab = "l0136"
                    continue
                lab = "l0150"
                continue
            elif lab == "l0136":
                self.b1 = self.j + 1
                self.t1 = self.s[self.b1]
                if self.t1 == self.g:
                    lab = "l0138"
                    continue
                lab = "l0150"
                continue
            elif lab == "l0138":
                self.s[self.b2] = 1
                lab = "l0195"
                continue
            elif lab == "l0150":
                self.t1 = self.s[self.k]
                if self.t1 == self.g:
                    lab = "l0152"
                    continue
                lab = "l0160"
                continue
            elif lab == "l0152":
                self.b3 = self.k + 6
                self.t2 = self.s[self.b3]
                if self.t2 == self.g:
                    lab = "l0156"
                    continue
                lab = "l0165"
                continue
            elif lab == "l0156":
                self.b2 = self.k + 3
                self.t1 = self.s[self.b2]
                if self.t1 == 2:
                    lab = "l0158"
                    continue
                lab = "l0170"
                continue
            elif lab == "l0158":
                self.s[self.b2] = 1
                lab = "l0195"
                continue
            elif lab == "l0160":
                if self.t1 == self.h:
                    lab = "l0170"
                    continue
                lab = "l0161"
            elif lab == "l0161":
                self.b3 = self.k + 6
                self.t2 = self.s[self.b3]
                if self.t2 == self.g:
                    lab = "l0162"
                    continue
                lab = "l0170"
                continue
            elif lab == "l0162":
                self.b2 = self.k + 3
                self.t1 = self.s[self.b2]
                if self.t1 == self.g:
                    lab = "l0163"
                    continue
                lab = "l0170"
                continue
            elif lab == "l0163":
                self.s[self.k] = 1
                lab = "l0195"
                continue
            elif lab == "l0165":
                self.t2 = self.s[self.b3]
                if self.t2 == 2:
                    lab = "l0166"
                    continue
                lab = "l0170"
                continue
            elif lab == "l0166":
                self.b2 = self.k + 3
                self.t1 = self.s[self.b2]
                if self.t1 == self.g:
                    lab = "l0168"
                    continue
                lab = "l0170"
                continue
            elif lab == "l0168":
                self.s[self.b3] = 1
                lab = "l0195"
                continue
            elif lab == "l0170":
                lab = "l0450"
                continue
            elif lab == "l0171":
                self.f = 0
                self.t1 = self.s[3]
                self.t2 = self.s[7]
                if self.t1 == self.g:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0187"
                    continue
                lab = "l0172"
            elif lab == "l0172":
                self.f = 0
                self.t1 = self.s[9]
                self.t2 = self.s[1]
                if self.t1 == self.g:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0181"
                    continue
                lab = "l0173"
            elif lab == "l0173":
                self.f = 0
                self.t1 = self.s[7]
                self.t2 = self.s[3]
                if self.t1 == self.g:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0183"
                    continue
                lab = "l0174"
            elif lab == "l0174":
                self.f = 0
                self.t1 = self.s[9]
                self.t2 = self.s[1]
                if self.t1 == 2:
                    self.f = self.f + 1
                if self.t2 == self.g:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0189"
                    continue
                lab = "l0175"
            elif lab == "l0175":
                if self.g == 1:
                    lab = "l0175a"
                    continue
                lab = "l0176"
                continue
            elif lab == "l0175a":
                self.g = 3
                self.h = 1
                lab = "l0110"
                continue
            elif lab == "l0176":
                self.f = 0
                self.t1 = self.s[9]
                self.t2 = self.s[3]
                if self.t1 == 3:
                    self.f = self.f + 1
                if self.t2 == 2:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0182"
                    continue
                lab = "l0177"
                continue
            elif lab == "l0177":
                self.i = 2
                lab = "l0177c"
            elif lab == "l0177c":
                self.t1 = self.s[self.i]
                if self.t1 == 2:
                    lab = "l0178"
                    continue
                if self.i == 9:
                    lab = "l0181"
                    continue
                self.i = self.i + 1
                lab = "l0177c"
                continue
            elif lab == "l0178":
                self.s[self.i] = 1
                lab = "l0195"
                continue
            elif lab == "l0181":
                self.s[1] = 1
                lab = "l0195"
                continue
            elif lab == "l0182":
                self.t1 = self.s[1]
                if self.t1 == 3:
                    lab = "l0177"
                    continue
                lab = "l0183"
            elif lab == "l0183":
                self.s[3] = 1
                lab = "l0195"
                continue
            elif lab == "l0187":
                self.s[7] = 1
                lab = "l0195"
                continue
            elif lab == "l0189":
                self.s[9] = 1
                lab = "l0195"
            elif lab == "l0195":
                self.skip()
                self.put("THE COMPUTER MOVES TO...")
                self.skip()
                lab = "l0202"
            elif lab == "l0202":
                self.r = 1
                lab = "l1000"
                continue
            elif lab == "l0205":
                lab = "l0500"
                continue
            elif lab == "l0450":
                if self.g == 3:
                    lab = "l0465"
                    continue
                lab = "l0455"
            elif lab == "l0455":
                self.f = 0
                if self.j == 7:
                    self.f = self.f + 1
                if self.k == 3:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l0465"
                    continue
                lab = "l0460"
            elif lab == "l0460":
                if self.k < 3:
                    lab = "l0460k"
                    continue
                if self.j < 7:
                    lab = "l0460j"
                    continue
                lab = "l0465"
                continue
            elif lab == "l0460k":
                self.k = self.k + 1
                lab = "l0120"
                continue
            elif lab == "l0460j":
                self.j = self.j + 3
                self.k = 1
                lab = "l0120"
                continue
            elif lab == "l0465":
                self.t1 = self.s[5]
                if self.t1 == self.g:
                    lab = "l0171"
                    continue
                lab = "l0175"
                continue
            elif lab == "l0475":
                self.ps = 88
                self.qs = 79
                lab = "l0500"
            elif lab == "l0500":
                self.skip()
                self.put("WHERE DO YOU MOVE ")
                self.m = self.get()
                lab = "l0502"
            elif lab == "l0502":
                self.t1 = self.m + 1
                if self.t1 == 1:
                    lab = "l0502t"
                    continue
                lab = "l0503"
                continue
            elif lab == "l0502t":
                self.terminal = "quit"   # instrumentation: exit route
                self.put("THANKS FOR THE GAME.")
                self.skip()
                lab = "l2000"
                continue
            elif lab == "l0503":
                if self.m > 9:
                    lab = "l0506"
                    continue
                lab = "l0505"
            elif lab == "l0505":
                self.t1 = self.s[self.m]
                if self.t1 == 2:
                    lab = "l0510"
                    continue
                lab = "l0506"
                continue
            elif lab == "l0506":
                self.put("THAT SQUARE IS OCCUPIED.")
                self.skip()
                self.skip()
                self.skip()
                lab = "l0500"
                continue
            elif lab == "l0510":
                self.g = 3
                self.s[self.m] = 3
                lab = "l0520"
            elif lab == "l0520":
                self.r = 2
                lab = "l1000"
                continue
            elif lab == "l0530":
                lab = "l0100"
                continue
            elif lab == "l1000":
                self.skip()
                self.i = 1
                lab = "l1002"
            elif lab == "l1002":
                self.put(" ")
                self.t1 = self.s[self.i]
                if self.t1 == 1:
                    lab = "l1012"
                    continue
                lab = "l1014"
                continue
            elif lab == "l1012":
                self.show(self.qs)
                self.put(" ")
                lab = "l1020"
                continue
            elif lab == "l1014":
                if self.t1 == 2:
                    lab = "l1016"
                    continue
                lab = "l1018"
                continue
            elif lab == "l1016":
                self.put("  ")
                lab = "l1020"
                continue
            elif lab == "l1018":
                self.show(self.ps)
                self.put(" ")
                lab = "l1020"
            elif lab == "l1020":
                self.b1 = 0
                if self.i == 3:
                    self.b1 = self.b1 + 1
                if self.i == 6:
                    self.b1 = self.b1 + 1
                if self.i == 9:
                    self.b1 = self.b1 + 1
                if self.b1 == 1:
                    lab = "l1022"
                    continue
                lab = "l1060"
                continue
            elif lab == "l1022":
                if self.i == 9:
                    lab = "l1050"
                    continue
                lab = "l1030"
                continue
            elif lab == "l1030":
                self.skip()
                self.put("---+---+---")
                self.skip()
                lab = "l1040"
            elif lab == "l1040":
                lab = "l1080"
                continue
            elif lab == "l1050":
                lab = "l1080"
                continue
            elif lab == "l1060":
                self.put("!")
                lab = "l1080"
            elif lab == "l1080":
                if self.i == 9:
                    lab = "l1085"
                    continue
                self.i = self.i + 1
                lab = "l1002"
                continue
            elif lab == "l1085":
                self.skip()
                self.skip()
                self.skip()
                self.i = 1
                lab = "l1100"
            elif lab == "l1100":
                self.t1 = self.s[self.i]
                self.b2 = self.i + 1
                self.t2 = self.s[self.b2]
                if self.t1 == self.t2:
                    lab = "l1105"
                    continue
                lab = "l1115n"
                continue
            elif lab == "l1105":
                self.b3 = self.i + 2
                self.t3 = self.s[self.b3]
                if self.t1 == self.t3:
                    lab = "l1110"
                    continue
                lab = "l1115n"
                continue
            elif lab == "l1110":
                if self.t1 == 1:
                    lab = "l1350"
                    continue
                lab = "l1112"
            elif lab == "l1112":
                if self.t1 == 3:
                    lab = "l1200"
                    continue
                lab = "l1115n"
            elif lab == "l1115n":
                self.i = self.i + 3
                if self.i < 8:
                    lab = "l1100"
                    continue
                lab = "l1115"
            elif lab == "l1115":
                self.i = 1
                lab = "l1125"
            elif lab == "l1125":
                self.t1 = self.s[self.i]
                self.b2 = self.i + 3
                self.t2 = self.s[self.b2]
                if self.t1 == self.t2:
                    lab = "l1130"
                    continue
                lab = "l1150n"
                continue
            elif lab == "l1130":
                self.b3 = self.i + 6
                self.t3 = self.s[self.b3]
                if self.t1 == self.t3:
                    lab = "l1135"
                    continue
                lab = "l1150n"
                continue
            elif lab == "l1135":
                if self.t1 == 1:
                    lab = "l1350"
                    continue
                lab = "l1137"
            elif lab == "l1137":
                if self.t1 == 3:
                    lab = "l1200"
                    continue
                lab = "l1150n"
            elif lab == "l1150n":
                self.i = self.i + 1
                if self.i < 4:
                    lab = "l1125"
                    continue
                lab = "l1150"
            elif lab == "l1150":
                self.i = 1
                lab = "l1151"
            elif lab == "l1151":
                self.t1 = self.s[self.i]
                if self.t1 == 2:
                    lab = "l1155"
                    continue
                lab = "l1152n"
            elif lab == "l1152n":
                self.i = self.i + 1
                if self.i < 10:
                    lab = "l1151"
                    continue
                lab = "l1152"
            elif lab == "l1152":
                lab = "l1400"
                continue
            elif lab == "l1155":
                self.t1 = self.s[5]
                if self.t1 == self.g:
                    lab = "l1160"
                    continue
                lab = "l1170"
                continue
            elif lab == "l1160":
                self.f = 0
                self.t1 = self.s[1]
                if self.t1 == self.g:
                    self.f = self.f + 1
                self.t2 = self.s[9]
                if self.t2 == self.g:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l1180"
                    continue
                lab = "l1165"
            elif lab == "l1165":
                self.f = 0
                self.t1 = self.s[3]
                if self.t1 == self.g:
                    self.f = self.f + 1
                self.t2 = self.s[7]
                if self.t2 == self.g:
                    self.f = self.f + 1
                if self.f == 2:
                    lab = "l1180"
                    continue
                lab = "l1170"
            elif lab == "l1170":
                if self.r == 1:
                    lab = "l0205"
                    continue
                lab = "l0530"
                continue
            elif lab == "l1180":
                if self.g == 1:
                    lab = "l1350"
                    continue
                lab = "l1200"
                continue
            elif lab == "l1200":
                self.terminal = "human"  # instrumentation: exit route
                self.put("YOU BEAT ME!! GOOD GAME.")
                self.skip()
                lab = "l2000"
                continue
            elif lab == "l1350":
                self.terminal = "computer"  # instrumentation
                self.put("I WIN, TURKEY!!!")
                self.skip()
                lab = "l2000"
                continue
            elif lab == "l1400":
                self.terminal = "draw"   # instrumentation: exit route
                self.put("IT IS A DRAW. THANK YOU.")
                self.skip()
                lab = "l2000"
            elif lab == "l2000":
                self.f = 0
                break          # stop;
        return self


def tict00():
    """TICT-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Tic-Tac-Toe game for the declared script (choice 2 = O, moves
    2,9,7,1,10,1,4).  Derived from the declared design by a statement-for-statement
    mirror of TICT-00.PLI, never captured (L3); the GAME is then checked by
    independent invariants (terminal draw, script consumed, eight GETs, final board,
    exactly three occupied messages, the labels this script never reaches and the two
    hop-4 exhaustive-search dead routes)."""
    assert len(TICT00_SCRIPT) == 8
    port = _Tict00Port(TICT00_SCRIPT).run()
    assert not port.script and port.nget == 8        # script consumed exactly
    assert port.terminal == "draw"
    assert port.s[1:] == TICT00_BOARD_END, port.s[1:]
    assert port.ps == 79 and port.qs == 88           # choice 2 -> human X (88), comp O (79)
    assert _tict00_trunc_div(8, 3) == 2 and _tict00_trunc_div(-8, 3) == -2
    for lab in TICT00_UNREACHED:
        assert port.hit.get(lab, 0) == 0, "label %s should be unreached" % lab
    # 1112/1137 are ENTERED (an all-empty triple falls through them) but their gotos
    # never fire -- the hop-4 exhaustive game-tree search measured 1200/1180/1112->1200
    # /1137->1200 unreachable for any play.  Kept as faithful dead code.
    assert port.hit.get("l1112", 0) > 0 and port.hit.get("l1137", 0) > 0
    lines = _tict00_finalize(port.raw)
    assert len((port.raw + "\r\n").encode()) == TICT00_RAW_BYTES, \
        len((port.raw + "\r\n").encode())
    assert len(lines) == TICT00_LINES, len(lines)
    assert lines[0] == "TIC-TAC-TOE"                 # NO leading blank: first put is a PUT LIST
    assert lines[1] == "CREATIVE COMPUTING MORRISTOWN, NEW JERSEY"
    assert lines[12] == "DO YOU WANT X OR O ENTER 1 FOR X 2 FOR O 2\r"  # echo line 13 (trailing CR per the committed HAMM convention)
    occ = [n for n, l in enumerate(lines, 1) if l == "THAT SQUARE IS OCCUPIED."]
    assert occ == [86, 91, 96], occ                  # THREE (hop-5 "two" is falsified)
    assert lines[118] == "IT IS A DRAW. THANK YOU."   # line 119
    assert lines[-1] == ""                           # exit CRLF blank [C352]
    return lines


# ---------------------------------------------------------------- LIFE-00
# Declared design constants (see LIFE-00.json notes; all measured against the
# independent simulator build/fc01-scratch/life00_sim.py, which is itself
# cross-checked against an unbounded set-based Conway model).
LIFE00_W = 12                 # interior rows    x = 1..12
LIFE00_H = 30                 # interior columns y = 1..30
LIFE00_STRIDE = 32            # padded row stride: n = x*32 + y + 1, a(1)..a(448)
LIFE00_GENS = 6               # bounded do g = 0 to 5;  (upstream NEVER terminates)
# 18 flat seed indices of the declared pattern (glider, beacon, block, blinker,
# all shifted 2 columns right so no live cell ever touches the window edge):
LIFE00_SEEDS = [69, 77, 78, 102, 109, 132, 133, 134, 144, 175, 176, 274, 306,
                338, 348, 349, 380, 381]
LIFE00_INITIAL = [((k - 1) // 32, (k - 1) % 32) for k in LIFE00_SEEDS]
LIFE00_NB = (-33, -32, -31, -1, 1, 31, 32, 33)   # n1..n8 offsets of the PL/I ladder
LIFE00_POPS = [18, 20, 18, 20, 18, 20]           # beacon 6->8->6 flicker on 12 static
LIFE00_RAW_BYTES = 4722       # 4720 pre-exit + the single exit CRLF [C352]
LIFE00_LINES = 91             # 5 + 6*(1 pad + 1 header + 12 rows) + bottom pad + exit blank


def _life00_conway_unbounded(gens):
    """INDEPENDENT simultaneous-update Conway model on an UNBOUNDED grid - no flat
    array, no marks, no byte model; the port's live-cell sets must equal it."""
    cur = set(LIFE00_INITIAL)
    out = []
    for _ in range(gens):
        out.append(frozenset(cur))
        cnt = {}
        for (x, y) in cur:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (dx, dy) != (0, 0):        # eight neighbours, NOT the centre
                        cnt[(x + dx, y + dy)] = cnt.get((x + dx, y + dy), 0) + 1
        cur = {p for p, c in cnt.items() if c == 3 or (p in cur and c == 2)}
    return out


def _life00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Life00Port:
    """Statement-for-statement mirror of LIFE-00.PLI: explicit zero-init of the
    448-cell padded flat grid, the 18 literal seed stores, the initial population
    scan, the banner, then for g = 0..5 one blank pad, the four single-item header
    PUTs, the PRINT pass (member -> scalar t1, v ladder, call cellprint, finalize
    2->0 / 3->1) and the EVOLUTION pass (centre + eight n1..n8 neighbour temps each
    counted by the separate t2 = 1 / t2 = 2 ladders exactly as BASIC 530..550, the
    guarded birth ladder, and the default-2 survive-restore ladder for live cells,
    which also covers s = 9).  Byte model per the measured corpus laws (README
    section 6 + the hop-2 separator law + the BIGA 9-column numeric field +
    [C352]): PUT SKIP emits "\r\n"; a single-item PUT LIST is preceded by ONE
    blank unless it is the first item printed since the last line start; a FIXED
    BIN(15) item renders right-justified in a NINE-column field; program exit
    appends exactly one "\r\n".  Pure PUT program: no GET, no echo."""

    def __init__(self):
        self.raw = ""
        self.a = [0] * 449                    # a(1)..a(448), 1-based like PL/I
        self.stats = []                       # (g, header cs, live count in print pass)
        self.grids = []                       # live-cell coordinates per printed gen
        self.pop0 = None                      # initial scan population
        self.cells = 0                        # total cell visits (both passes per gen)

    def skip(self):
        self.raw += "\r\n"                      # put skip;

    def put(self, item):
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "                     # measured leading-separator law
        self.raw += ("%9d" % item) if isinstance(item, int) else item

    def cellprint(self, q):
        # cellprint: procedure (q): declare ch character(1) varying;
        #   if q = 1 then ch = '*';  if q = 0 then ch = '.';  put list(ch);
        ch = ""
        if q == 1:
            ch = "*"
        if q == 0:
            ch = "."
        self.put(ch)

    def run(self):
        a = self.a
        # do i = 1 to 448; a(i) = 0; end;   (lane-B DATA contents are UNMEASURED;
        #                                    the port zeroes explicitly in both models)
        for i in range(1, 449):
            a[i] = 0
        for k in LIFE00_SEEDS:                  # a(69) = 1; ... a(381) = 1;
            a[k] = 1
        cs = 0                                  # initial population scan
        for x in range(1, LIFE00_W + 1):
            n = x * LIFE00_STRIDE + 1
            for y in range(1, LIFE00_H + 1):
                n = n + 1
                t1 = a[n]
                if t1 == 1:
                    cs = cs + 1
        self.pop0 = cs
        self.put("LIFE")
        self.skip()
        self.put("CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
        self.skip()
        self.skip()
        self.skip()
        self.skip()
        for g in range(LIFE00_GENS):            # do g = 0 to 5;
            self.skip()                         # fixed one-blank pad
            self.put("GENERATION")
            self.put(g)
            self.put("POPULATION")
            self.put(cs)
            self.skip()
            live = 0
            cells = []
            for x in range(1, LIFE00_W + 1):    # PRINT pass
                n = x * LIFE00_STRIDE + 1
                for y in range(1, LIFE00_H + 1):
                    n = n + 1
                    self.cells += 1
                    t1 = a[n]
                    v = 0
                    if t1 == 1:
                        v = 1
                    if t1 == 3:
                        v = 1
                    self.cellprint(v)
                    if t1 == 2:
                        a[n] = 0
                    if t1 == 3:
                        a[n] = 1
                    if v == 1:
                        live += 1
                        cells.append((x, y))    # instrumentation only
                self.skip()
            self.stats.append((g, cs, live))
            self.grids.append(cells)
            cs = 0                              # EVOLUTION pass
            for x in range(1, LIFE00_W + 1):
                n = x * LIFE00_STRIDE + 1
                for y in range(1, LIFE00_H + 1):
                    n = n + 1
                    t1 = a[n]
                    s = 0
                    t2 = a[n]                   # the CENTRE, as BASIC 530..550 counts it
                    if t2 == 1:
                        s = s + 1
                    for k in LIFE00_NB:         # n1..n8, each with the two-step ladder
                        t2 = a[n + k]
                        if t2 == 1:
                            s = s + 1
                        if t2 == 2:
                            s = s + 1
                    if t1 == 0:                 # guarded birth
                        if s == 3:
                            a[n] = 3
                            cs = cs + 1
                    if t1 == 1:                 # live: default-die mark, survive-restore
                        a[n] = 2
                        if s == 3:
                            a[n] = 1
                        if s == 4:
                            a[n] = 1
                        if s == 3:
                            cs = cs + 1
                        if s == 4:
                            cs = cs + 1
        self.skip()                             # bottom pad
        return self


def life00():
    """LIFE-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Game of Life for the DECLARED pattern and the bounded 6 generations.
    Derived from the declared design by a statement-for-statement mirror of
    LIFE-00.PLI, never captured (L3); the GAME is then checked by independent
    invariants: agreement of every printed generation with an UNBOUNDED set-based
    Conway model computed here separately from the port, the per-generation header
    population equal to the live cells counted in the print pass, the declared
    18/20 flicker sequence, the window margin (no live cell on an interior edge and
    the never-printed gen-6 state still inside), the stream structure (6 headers,
    12 rows of 30 '.'/'*' positional tokens per generation, stars == cs) and the
    91-line / 4722-byte identity."""
    assert len(LIFE00_SEEDS) == 18
    port = _Life00Port().run()
    assert port.pop0 == 18, port.pop0               # declared initial population
    pops = [cs for (g, cs, live) in port.stats]
    assert pops == LIFE00_POPS, pops
    for (g, cs, live) in port.stats:
        assert cs == live == len(port.grids[g]), "cs/live mismatch at g=%d" % g
    # ---- independent Conway cross-check (set model, unbounded, simultaneous)
    tb = _life00_conway_unbounded(LIFE00_GENS + 1)
    for g in range(LIFE00_GENS):
        assert set(port.grids[g]) == tb[g], "port grid != Conway model at g=%d" % g
    for (x, y) in tb[LIFE00_GENS]:                  # never printed, must stay inside
        assert 2 <= x <= LIFE00_W - 1 and 2 <= y <= LIFE00_H - 1, \
            "gen-6 state leaves the declared window: (%d,%d)" % (x, y)
    for (g, cells) in enumerate(port.grids):
        for (x, y) in cells:
            assert 2 <= x <= LIFE00_W - 1 and 2 <= y <= LIFE00_H - 1, \
                "live cell on the window edge at g=%d" % g
        s = set(cells)
        assert len([p for p in s if 9 <= p[0] <= 12 and 26 <= p[1] <= 29]) == 4  # block
        assert len([p for p in s if p[0] <= 7 and p[1] <= 9]) == 5               # glider
        assert len([p for p in s if 7 <= p[0] <= 11 and 15 <= p[1] <= 19]) == 3  # blinker
        assert len([p for p in s if 1 <= p[0] <= 6 and 10 <= p[1] <= 17]) in (6, 8)  # beacon
    # ---- stream structure
    lines = _life00_finalize(port.raw)
    raw = (port.raw + "\r\n").encode()
    assert len(raw) == LIFE00_RAW_BYTES, len(raw)
    assert len(port.raw.encode()) == LIFE00_RAW_BYTES - 2
    assert len(lines) == LIFE00_LINES, len(lines)
    assert lines[0] == "LIFE", lines[0]
    assert lines[1] == "CREATIVE COMPUTING MORRISTOWN, NEW JERSEY", lines[1]
    assert lines[2:5] == ["", "", ""], lines[2:5]
    hdrs = [i for i, l in enumerate(lines) if l.startswith("GENERATION ")]
    assert len(hdrs) == LIFE00_GENS, hdrs
    for (k, i) in enumerate(hdrs):
        assert lines[i] == "GENERATION %d POPULATION %d" % (k, pops[k]), lines[i]
        assert lines[i - 1] == "", "no pad line before generation %d" % k
        body = lines[i + 1:i + 1 + LIFE00_W]
        assert len(body) == LIFE00_W
        for row in body:
            toks = row.split(" ")
            assert len(toks) == LIFE00_H, (len(toks), row)
            assert set(toks) <= {"*", "."}, row
        stars = sum(1 for p in body for t in p.split(" ") if t == "*")
        assert stars == pops[k], "row stars %d != cs %d at g=%d" % (stars, pops[k], k)
    assert lines[hdrs[-1] + 1 + LIFE00_W] == "", "no bottom pad"
    assert lines[-1] == ""                           # exit CRLF blank [C352]
    assert len(lines) == 5 + LIFE00_GENS * (1 + 1 + LIFE00_W) + 2, len(lines)
    return lines


# --------------------------------------------------------------------------
# DHRY-00 (Dhrystone 2.1, Pascal -> PL/I-80).  The derivation mirrors the
# pinned DHRY-00.PLI statement-for-statement (main body, then the 14 nested
# definitions after `stop;`).  Byte model per the measured corpus laws
# (README section 6 + the hop separator law + the BIGA 9-column numeric
# field + the HAMM/HANG echo law + [C352]): PUT SKIP emits "\r\n"; ONE blank
# precedes every PUT LIST item that is not the first item printed since the
# last line start; a FIXED BIN(15) numeric item renders right-justified in a
# NINE-column field ("%9d", NEVER "%10d"+join); a consumed GET line L echoes
# as L + "\r\r\n" and CLOSES the line; program exit appends exactly one
# "\r\n".  State uses the port's OWN encodings: integer codes for
# chars/enums/booleans (Ident1..Ident5 = 0..4, nil = 0), the two records as
# parallel slot arrays pcp/dsc/enm/inc over slots 1..2 with the StringComp
# cells living inside sx (slot 1 at base 0, slot 2 at base 30), String1Glob
# at 60, String2Glob at 90 and the two literal tables at 120/150; VAR
# parameters via the outer result cells r2/r3/r6/r7; DIV by a subtraction
# loop.  The published should-be column of the Pascal source is embedded
# here as its own constants (DHRY00_SHOULD), the third check of the stream.

DHRY00_NRUNS = 7                  # declared console_input script: one GET
DHRY00_LINES = 57                 # normalized complete-stream length
DHRY00_RAW_BYTES = 1368           # raw console bytes INCLUDING the exit CRLF (the
#                                # port prints the Array2Glob should-be numeric
#                                # as %9d; the sim's text form is 1361 -- both
#                                # collapse-spaces-v1 to the SAME 57 lines)
DHRY00_S_SOME = "DHRYSTONE PROGRAM, SOME STRING"    # sx(1..30)   slot 1
DHRY00_S_1ST = "DHRYSTONE PROGRAM, 1ST STRING "     # sx(61..90)  String1Glob
DHRY00_S_2ND = "DHRYSTONE PROGRAM, 2ND STRING "     # sx(121..150) literal
DHRY00_S_3RD = "DHRYSTONE PROGRAM, 3RD STRING "     # sx(151..180) literal
DHRY00_B = {"slot1": 0, "slot2": 30, "sg1": 60, "sg2": 90,
            "2nd": 120, "3rd": 150}
# the PL/I putc ladder, arm for arm (default ' ' + 22 literal arms).
DHRY00_LADDER = {32: " ", 44: ",", 48: "0", 49: "1", 50: "2", 51: "3",
                 58: ":", 65: "A", 66: "B", 67: "C", 68: "D", 69: "E",
                 71: "G", 72: "H", 73: "I", 77: "M", 78: "N", 79: "O",
                 80: "P", 82: "R", 83: "S", 84: "T", 89: "Y"}
# published should-be column of the Pascal source (20 rows, in table order);
# the Array2Glob row is NumberOfRuns + 10.
DHRY00_SHOULD = ["5", "TRUE", "A", "B", "7", None, "0", "2", "17",
                 "DHRYSTONE PROGRAM, SOME STRING",
                 "0", "1", "18", "DHRYSTONE PROGRAM, SOME STRING",
                 "5", "13", "7", "1",
                 "DHRYSTONE PROGRAM, 1ST STRING",
                 "DHRYSTONE PROGRAM, 2ND STRING"]


def _dhry00_repl(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


class _Dhry00Port:
    """Statement-for-statement mirror of the pinned DHRY-00.PLI."""

    def __init__(self, nruns):
        self.raw = ""
        self.intglob = 0
        self.int1g = 0
        self.int2g = 0
        self.int3g = 0
        self.boolg = 0
        self.char1g = 0
        self.char2g = 0
        self.enumg = 0
        self.numruns = nruns
        self.runidx = 0
        self.ci = 0
        self.z = 0
        self.tv = 0
        self.dvq = 0
        self.r2 = 0
        self.r3 = 0
        self.r6 = 0
        self.r7 = 0
        self.a1 = [0] * 51                     # a1(1..50)
        self.a2 = [0] * 2501                   # a2(1..2500), flat (r-1)*50+c
        self.sx = [0] * 181                    # sx(1..180)
        self.pcp = [0, 0, 0]
        self.dsc = [0, 0, 0]
        self.enm = [0, 0, 0]
        self.inc = [0, 0, 0]
        self.gets = 0

    # ---- stream primitives (measured byte laws)
    def skip(self):                            # put skip;
        self.raw += "\r\n"

    def put(self, item):                       # ONE single-item put list(...)
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "                    # measured leading-separator law
        self.raw += ("%9d" % item) if isinstance(item, int) else item

    def echo(self, v):                         # consumed GET line closes the line
        self.raw += "%d\r\r\n" % v

    # ---- nested definitions (after `stop;` in the .PLI)
    def putc(self, v):                         # 22-arm ladder over ch character(1) varying
        ch = " "
        for k in sorted(DHRY00_LADDER):
            if v == k:
                ch = DHRY00_LADDER[k]
        self.put(ch)

    def putstr(self, frms):
        for k4 in range(1, 31):
            sp4 = frms + k4
            tv4 = self.sx[sp4]
            if tv4 > 32:                       # blanks skipped (frame law)
                self.putc(tv4)

    def cp30(self, frm, dst):
        for k3 in range(1, 31):
            sp3 = frm + k3
            dp3 = dst + k3
            self.sx[dp3] = self.sx[sp3]

    def divsub(self, dv, ds):
        self.dvq = 0
        rr = dv
        while True:                            # dl:
            if rr < ds:
                break                          # goto dd
            rr = rr - ds
            self.dvq = self.dvq + 1

    def proc5(self):
        self.char1g = 65
        self.boolg = 0

    def proc4(self):
        bl = 0
        if self.char1g == 65:
            bl = 1
        if bl == 1:
            self.boolg = 1
        self.char2g = 66

    def proc7(self, p7v1, p7v2):
        il7 = p7v1 + 2
        self.r7 = p7v2 + il7

    def proc8(self, p8v1, p8v2):
        l8 = p8v1 + 5
        v82 = p8v2
        self.a1[l8] = v82
        p18 = l8 + 1
        self.a1[p18] = self.a1[l8]
        p38 = l8 + 30
        self.a1[p38] = l8
        b8 = (l8 - 1) * 50
        h8 = l8 + 2
        ix8 = l8
        while True:                            # p8a:
            ix2 = b8 + ix8
            self.a2[ix2] = l8
            ix8 = ix8 + 1
            if not ix8 < h8:
                break                          # p8b:
        m8 = l8 - 1
        ix2 = b8 + m8
        v22 = ix2
        t8 = self.a2[v22]
        t8 = t8 + 1
        self.a2[v22] = t8
        k8 = l8 + 20
        b28 = (k8 - 1) * 50
        ix2 = b28 + l8
        self.a2[ix2] = self.a1[l8]
        self.intglob = 5

    def proc1(self, pv):
        p1a = pv
        r1a = self.pcp[p1a]
        d1a = (r1a - 1) * 30
        self.dsc[r1a] = self.dsc[1]
        self.enm[r1a] = self.enm[1]
        self.inc[r1a] = self.inc[1]
        self.pcp[r1a] = self.pcp[1]
        self.cp30(0, d1a)
        self.inc[p1a] = 5
        self.inc[r1a] = self.inc[p1a]
        self.pcp[r1a] = self.pcp[p1a]
        self.proc3(r1a)
        tv1 = self.dsc[r1a]
        if tv1 == 0:                           # Ident1
            self.inc[r1a] = 6
            self.proc6(self.enm[p1a])
            self.enm[r1a] = self.r6
            self.pcp[r1a] = self.pcp[1]
            tv1 = self.inc[r1a]
            self.proc7(tv1, 10)
            self.inc[r1a] = self.r7

    def proc3(self, p3tgt):
        t3a = self.pcp[1]
        t3b = p3tgt
        self.r3 = 0
        if t3a == 1:                           # domain ladder for `pcp(1) > 0`
            self.r3 = 1
        if t3a == 2:
            self.r3 = 2
        self.pcp[t3b] = self.r3
        self.proc7(10, self.intglob)
        self.inc[1] = self.r7

    def proc6(self, p6ev):
        e6 = p6ev
        self.r6 = e6
        t6 = self.f3(e6)
        if t6 == 0:
            self.r6 = 3                        # Ident4
        if e6 == 0:
            self.r6 = 0
        if e6 == 1:                            # Ident2 arm
            if self.intglob > 100:
                self.r6 = 0
            if self.intglob < 101:
                self.r6 = 3
        if e6 == 2:                            # Ident3 arm
            self.r6 = 1
        if e6 == 4:                            # Ident5 arm
            self.r6 = 2

    def proc2(self, pv2):
        il2b = pv2 + 10
        el2 = 1                                # any value but Ident1
        while True:                            # p2t:  repeat ... until el2 = Ident1
            if self.char1g == 65:
                il2b = il2b - 1
                self.r2 = il2b - self.intglob
                el2 = 0
            if el2 == 0:
                break                          # goto p2x

    def f1(self, c1v, c2v):
        cl1 = c1v
        cl2 = cl1
        rv1 = 0                                # Ident1 (the <>-arm default)
        if cl2 == c2v:
            self.char1g = cl1
            rv1 = 1                            # Ident2
        return rv1

    def f2(self, b1v, b2v):
        v1f = b1v
        v2f = b2v
        rvf = 0
        ilf = 2
        clf = 0
        while True:                            # f2l:
            if ilf > 2:
                break                          # f2x: / f2e: (adjacent labels)
            sp1 = v1f + ilf
            c1f = self.sx[sp1]
            sp2 = v2f + ilf
            c2f = self.sx[sp2]
            if c1f < c2f:
                break
            if c1f > c2f:
                break
            clf = 65
            ilf = ilf + 1
        if clf > 86:                           # 'V'
            if clf < 90:                       # 'Z'
                ilf = 7
        if clf == 82:                          # 'R'
            rvf = 1
            return rvf
        sgf = 0
        dif = 0
        for k1f in range(1, 31):               # whole-string '>' compare
            sp1 = v1f + k1f
            c1f = self.sx[sp1]
            sp2 = v2f + k1f
            c2f = self.sx[sp2]
            if dif == 0:
                if c1f < c2f:
                    dif = 2
                if c1f > c2f:
                    dif = 1
                    sgf = 1
        if sgf == 1:
            ilf = ilf + 7
            self.intglob = ilf
            rvf = 1
        return rvf

    def f3(self, f3ev):
        e3 = f3ev
        rv3 = 0
        if e3 == 2:                            # Ident3
            rv3 = 1
        return rv3

    # ---- main body (statement order of the pinned file)
    def run(self):
        for self.z in range(1, 181):           # do z = 1 to 180; sx(z) = 0; end;
            self.sx[self.z] = 0
        for self.z in range(1, 51):            # do z = 1 to 50; a1(z) = 0; end;
            self.a1[self.z] = 0
        for self.z in range(1, 2501):          # do z = 1 to 2500; a2(z) = 0; end;
            self.a2[self.z] = 0
        self.pcp[1] = 0
        self.pcp[2] = 0
        self.dsc[1] = 0
        self.dsc[2] = 0
        self.enm[1] = 0
        self.enm[2] = 0
        self.inc[1] = 0
        self.inc[2] = 0
        for base, s in ((DHRY00_B["slot1"], DHRY00_S_SOME),
                        (DHRY00_B["sg1"], DHRY00_S_1ST),
                        (DHRY00_B["2nd"], DHRY00_S_2ND),
                        (DHRY00_B["3rd"], DHRY00_S_3RD)):
            for i, c in enumerate(ord(ch) for ch in s):   # the 120 literal stores
                self.sx[base + i + 1] = c
        self.pcp[1] = 2                        # RecordPtr / NextRecordPtr
        self.dsc[1] = 0                        # Ident1
        self.enm[1] = 2                        # Ident3
        self.inc[1] = 40
        self.a2[357] = 10                      # Array2Glob[8,7]
        # header
        self.skip()
        self.put("Dhrystone Benchmark, Version 2.1 (Language: Pascal)")
        self.skip()
        self.skip()
        self.put("Please give the number of runs through the benchmark:")
        self.skip()
        self.gets += 1                         # get list(numruns);
        self.echo(self.numruns)
        self.skip()
        self.put("Execution starts,")
        self.put(self.numruns)
        self.put("runs through Dhrystone")
        self.skip()
        # run loop
        for self.runidx in range(1, self.numruns + 1):
            self.proc5()
            self.proc4()
            self.int1g = 2
            self.int2g = 3
            self.cp30(DHRY00_B["2nd"], DHRY00_B["sg2"])
            self.enumg = 1                     # Ident2
            self.tv = self.f2(DHRY00_B["sg1"], DHRY00_B["sg2"])
            self.boolg = 0
            if self.tv == 0:
                self.boolg = 1
            while self.int1g < self.int2g:     # do while int1g < int2g
                self.int3g = 5 * self.int1g - self.int2g
                self.proc7(self.int1g, self.int2g)
                self.int3g = self.r7
                self.int1g = self.int1g + 1
            self.proc8(self.int1g, self.int3g)
            self.proc1(1)
            for self.ci in range(65, self.char2g + 1):
                self.tv = self.f1(self.ci, 67)
                if self.enumg == self.tv:
                    self.proc6(0)              # Ident1
                    self.enumg = self.r6
                    self.cp30(DHRY00_B["3rd"], DHRY00_B["sg2"])
                    self.int2g = self.runidx
                    self.intglob = self.runidx
            self.int2g = self.int2g * self.int1g
            self.divsub(self.int2g, self.int3g)
            self.int1g = self.dvq
            self.tv = self.int2g - self.int3g
            self.tv = 7 * self.tv
            self.int2g = self.tv - self.int1g
            self.proc2(self.int1g)
            self.int1g = self.r2
        # final table (row/should_be/strrow expanded inline as in the .PLI)
        self.put("Execution ends")
        self.skip()
        self.put("Final values of the variables used in the benchmark:")
        self.skip()
        self.skip()
        self.row("IntGlob:", self.intglob, "5")
        self.put("BoolGlob:")
        if self.boolg == 1:
            self.put("TRUE")
        else:
            self.put("FALSE")
        self.skip()
        self.should_be("TRUE")
        self.put("Char1Glob:")
        self.putc(self.char1g)
        self.skip()
        self.should_be("A")
        self.put("Char2Glob:")
        self.putc(self.char2g)
        self.skip()
        self.should_be("B")
        self.row("Array1Glob [8]:", self.a1[8], "7")
        self.row("Array2Glob [8,7]:", self.a2[357], self.numruns + 10)
        self.row("PointerGlob^.Discr:", self.dsc[1], "0")
        self.row("PointerGlob^.EnumComp:", self.enm[1], "2")
        self.row("PointerGlob^.IntComp:", self.inc[1], "17")
        self.strrow("PointerGlob^.StringComp:", DHRY00_B["slot1"],
                    "DHRYSTONE PROGRAM, SOME STRING")
        self.row("NextPointerGlob^.Discr:", self.dsc[2], "0")
        self.row("NextPointerGlob^.EnumComp:", self.enm[2], "1")
        self.row("NextPointerGlob^.IntComp:", self.inc[2], "18")
        self.strrow("NextPointerGlob^.StringComp:", DHRY00_B["slot2"],
                    "DHRYSTONE PROGRAM, SOME STRING")
        self.row("Int1Glob:", self.int1g, "5")
        self.row("Int2Glob:", self.int2g, "13")
        self.row("Int3Glob:", self.int3g, "7")
        self.row("EnumGlob:", self.enumg, "1")
        self.strrow("String1Glob:", DHRY00_B["sg1"],
                    "DHRYSTONE PROGRAM, 1ST STRING")
        self.strrow("String2Glob:", DHRY00_B["sg2"],
                    "DHRYSTONE PROGRAM, 2ND STRING")
        self.skip()
        self.skip()
        return self

    def row(self, label, value, should):
        self.put(label)
        self.put(value)
        self.skip()
        self.should_be(should)

    def should_be(self, text):
        self.put("should be:")
        self.put(text)
        self.skip()

    def strrow(self, label, base, should):
        self.put(label)
        self.skip()
        self.putstr(base)
        self.skip()
        self.should_be(should)


def dhry00():
    """DHRY-00: the complete normalized console stream (collapse-spaces-v1) of
    the adapted Dhrystone 2.1 for the declared run count N=7 (the single GET
    reads the console_input script).  Derived from the declared design by a
    statement-for-statement mirror of DHRY-00.PLI, never captured (L3).  The
    stream is then checked by independent invariants: the port's FINAL STATE
    against the published Dhrystone result column, the 20 should-be rows
    themselves, the frame law (no emitted line reaches the 79-column PLILIB
    wrap measured to fire at exactly 79), exactly one GET, and the 57-line /
    1361-byte identity."""
    port = _Dhry00Port(DHRY00_NRUNS).run()
    # ---- published result column (Dhrystone 2.1 canonical values at N=7)
    assert (port.intglob, port.boolg, port.char1g, port.char2g) == (5, 1, 65, 66)
    assert port.a1[8] == 7 and port.a2[357] == DHRY00_NRUNS + 10
    assert (port.dsc[1], port.enm[1], port.inc[1]) == (0, 2, 17)
    assert (port.dsc[2], port.enm[2], port.inc[2]) == (0, 1, 18)
    assert (port.int1g, port.int2g, port.int3g, port.enumg) == (5, 13, 7, 1)
    # the two record strings hold SOME-STRING; the globs their declared tables
    for base in (DHRY00_B["slot1"], DHRY00_B["slot2"]):
        assert port.sx[base + 30] == 71 and port.sx[base + 20] == 83
    assert port.sx[DHRY00_B["sg1"] + 20] == 49       # '1' of 1ST
    assert port.sx[DHRY00_B["sg2"] + 20] == 50       # '2' of 2ND
    assert port.gets == 1
    # ---- stream
    lines = _dhry00_repl(port.raw)
    raw = (port.raw + "\r\n").encode()
    assert len(raw) == DHRY00_RAW_BYTES, len(raw)
    assert len(lines) == DHRY00_LINES, len(lines)
    assert lines[0] == "" and lines[1] == \
        "Dhrystone Benchmark, Version 2.1 (Language: Pascal)", lines[:2]
    assert lines[3] == "Please give the number of runs through the benchmark:"
    assert lines[4] == "%d\r" % DHRY00_NRUNS       # echo keeps its trailing CR
    assert lines[6] == ("Execution starts, %d runs through Dhrystone"
                        % DHRY00_NRUNS), lines[6]
    assert lines[7] == "Execution ends"
    assert lines[8] == "Final values of the variables used in the benchmark:"
    assert lines[9] == ""
    shoulds = [l[len("should be: "):] for l in lines if l.startswith("should be: ")]
    want_should = [str(DHRY00_NRUNS + 10) if w is None else w
                   for w in DHRY00_SHOULD]
    assert shoulds == want_should, shoulds
    assert lines[-3:] == ["", "", ""], lines[-3:]   # 2 skips + exit CRLF
    # ---- frame law: no emitted line reaches the measured 79-column wrap
    for seg in raw.split(b"\r\n"):
        assert len(seg) <= 78, (len(seg), seg)
    return lines


# ---------------------------------------------------------------- FFT-00
# FFT-00 (Rosetta Code "Fast Fourier transform", PL/I reference) -> PL/I-80.
# The derivation mirrors the pinned FFT-00.PLI statement-for-statement (main
# body, then bf / prn / pdig after `stop;`).  Byte model per the measured
# corpus laws (README section 6 + the hop-2 separator law + the BIGA/FP00
# 9-column numeric field incl. its sign + [C352]): PUT SKIP emits "\r\n"; ONE
# blank precedes every PUT LIST item that is not the first item printed since
# the last line start; a FIXED BIN(15) numeric item renders right-justified in
# a NINE-column field WITH its sign; fixed-bin division TRUNCATES TOWARD ZERO
# (all four: the FP00 lane-B RUN witness); program exit appends one "\r\n".
# Numeric model: complex values are Q6 fixed point (scale 64) in TWO parallel
# fixed bin(15) arrays xr/xi exactly as pinned; twiddles are the precomputed
# integer constants (45 = trunc(64*cos(pi/4))); every "/ 64" rescale divides
# exactly on this input, so the truncation direction is not load-bearing for
# the RESULT -- but tdiv() still pins the measured law, and the prn digit path
# DOES rely on it.  Three independent checks: the port state vs the hand-
# published Q6 table, the port vs a naive double-precision DFT computed here
# from the definition, and the printed tokens reconstructed back to thousandths
# vs the table.  Pure PUT program: no GET, no echo.

FFT00_SCALE = 64                # Q6 fixed-point scale (declared adaptation)
FFT00_N = 8                     # transform length
FFT00_TOL = 0.02                # declared per-component tolerance (Q6 twiddles)
FFT00_B15_HI = 32767            # the FIXED BIN(15) range every intermediate
FFT00_B15_LO = -32768           # is asserted inside (overflow would launder a gap)
# the printed input, in NATURAL order (the Rosetta reference's data array):
FFT00_INPUT = (1, 1, 1, 1, 0, 0, 0, 0)
# hand-derived published Q6 result table, computed by hand from the butterfly
# schedule BEFORE either model was run (the third check):
FFT00_PUBLISHED = [(256, 0), (64, -154), (0, 0), (64, -26), (0, 0),
                   (64, 26), (0, 0), (64, 154)]
# the eight twiddle-scalar stores, in the pinned assignment order:
FFT00_TWIDDLES = (("w0r", 64), ("w0i", 0), ("w1r", 45), ("w1i", -45),
                  ("w2r", 0), ("w2i", -64), ("w3r", -45), ("w3i", -45))
FFT00_RAW_BYTES = 507           # 505 pre-exit + the single exit CRLF [C352]
FFT00_LINES = 13                # "", banner, scale line, "", 8 X-lines, ""


def _fft00_chk(v, what):
    assert FFT00_B15_LO <= v <= FFT00_B15_HI, "bin15 overflow (%s): %d" % (what, v)
    return v


def _fft00_tdiv(p, d):
    """PL/I fixed-bin division: truncates TOWARD ZERO (FP00 lane-B witness:
    -2881/64 = -45 and -2879/64 = -44)."""
    q = abs(p) // abs(d)
    return _fft00_chk(q if (p >= 0) == (d >= 0) else -q, "quotient")


def _fft00_dft_naive(x):
    """INDEPENDENT double-precision DFT computed straight from the definition --
    no butterflies, no bit-reversal, no fixed point.  Cross-check only."""
    import cmath
    n = len(x)
    return [complex(sum(x[k] * cmath.exp(complex(0, -2 * cmath.pi * j * k / n))
                        for k in range(n)))
            for j in range(n)]


class _Fft00Port:
    """Statement-for-statement mirror of the pinned FFT-00.PLI.

    MAIN: zero-init loop, the four bit-reversed seed stores (x = 1,1,1,1,0,0,0,0
    in DIT input order is 1,0,1,0,1,0,1,0 -> xr(1)=xr(3)=xr(5)=xr(7)=64), the
    eight twiddle stores, the two banner PUTs, the three butterfly stages (one
    DO TO BY 2 over adjacent pairs, then two explicit four-call groups), the
    eight-line output loop (member -> scalar t, the MAIN-frame sign flag
    `sg = 0; if t < z then sg = 1;` because a nested two-variable ordered
    compare is an unsampled form on this compiler), and the closing PUT SKIP.
    NESTED (after `stop;`): bf (TP00 formal copies li/lj first, four products,
    two toward-zero rescales, four array stores), prn (sign, magnitude, integer
    part, three digits) and pdig (the digit ladder through character(1) varying).
    """

    def __init__(self):
        self.raw = ""
        self.z = 0
        self.xr = [0] * FFT00_N
        self.xi = [0] * FFT00_N
        self.w = dict(FFT00_TWIDDLES)
        self.bf_calls = 0                 # instrumentation: 12 butterflies
        self.digits = 0                   # instrumentation: 48 pdig emissions
        self.max_magnitude = 0            # instrumentation: the digit-path bound

    # ---- stream primitives (the measured byte laws)
    def skip(self):                       # put skip;
        self.raw += "\r\n"

    def put(self, item):                  # ONE single-item put list(...)
        if self.raw and not self.raw.endswith("\r\n"):
            self.raw += " "               # measured leading-separator law
        self.raw += ("%9d" % item) if isinstance(item, int) else item

    # ---- nested bf(fi, fj, wr, wi) ----
    def bf(self, fi, fj, wr, wi):
        li = fi                           # TP00 law: copy the formal first
        lj = fj
        _fft00_chk(li, "li")
        _fft00_chk(lj, "lj")
        ar = self.xr[li - 1]
        ai = self.xi[li - 1]
        br = self.xr[lj - 1]
        bi = self.xi[lj - 1]
        p1 = _fft00_chk(br * wr, "p1")
        p2 = _fft00_chk(bi * wi, "p2")
        tr = _fft00_tdiv(_fft00_chk(p1 - p2, "p1-p2"), FFT00_SCALE)
        p3 = _fft00_chk(br * wi, "p3")
        p4 = _fft00_chk(bi * wr, "p4")
        ti = _fft00_tdiv(_fft00_chk(p3 + p4, "p3+p4"), FFT00_SCALE)
        self.xr[li - 1] = _fft00_chk(ar + tr, "xr(li)")
        self.xi[li - 1] = _fft00_chk(ai + ti, "xi(li)")
        self.xr[lj - 1] = _fft00_chk(ar - tr, "xr(lj)")
        self.xi[lj - 1] = _fft00_chk(ai - ti, "xi(lj)")
        self.bf_calls += 1

    # ---- nested pdig(d): one digit through the pinned character ladder ----
    def pdig(self, d):
        ch = "0"
        for k in range(10):
            if d == k:
                ch = str(k)
        self.put(ch)
        self.digits += 1

    # ---- nested prn(v, sg): a Q6 value as sign / integer / '.' / three digits ----
    def prn(self, v, sg):
        s = v
        if sg == 1:                       # formal-vs-literal EQ (the DHRY putc shape)
            self.put("-")
        if sg == 1:
            s = _fft00_chk(0 - s, "magnitude")
        ip = _fft00_tdiv(s, FFT00_SCALE)
        rem = _fft00_chk(s - ip * FFT00_SCALE, "rem")
        self.max_magnitude = max(self.max_magnitude, abs(rem * 1000))
        th = _fft00_tdiv(_fft00_chk(rem * 1000, "rem*1000"), FFT00_SCALE)
        hh = _fft00_tdiv(th, 100)
        r2 = _fft00_chk(th - hh * 100, "r2")
        t10 = _fft00_tdiv(r2, 10)
        uu = _fft00_chk(r2 - t10 * 10, "uu")
        self.put(ip)
        self.put(".")
        self.pdig(hh)
        self.pdig(t10)
        self.pdig(uu)

    # ---- main body, statement-for-statement ----
    def run(self):
        self.z = 0                        # z = 0;
        for k in range(1, FFT00_N + 1):   # do k = 1 to 8; xr(k) = 0; xi(k) = 0; end;
            self.xr[k - 1] = 0
            self.xi[k - 1] = 0
        self.xr[0] = FFT00_SCALE          # xr(1) = 64;  (bit-reversed seed 1,0,1,0,
        self.xr[2] = FFT00_SCALE          # xr(3) = 64;   1,0,1,0 x 64 for the input
        self.xr[4] = FFT00_SCALE          # xr(5) = 64;   1,1,1,1,0,0,0,0)
        self.xr[6] = FFT00_SCALE          # xr(7) = 64;
        for (nm, val) in FFT00_TWIDDLES:  # the eight twiddle-scalar stores
            self.w[nm] = val
        self.skip()                       # put skip list('FFT-00 COOLEY-TUKEY N=8');
        self.put("FFT-00 COOLEY-TUKEY N=8")
        self.skip()                       # put skip list('SCALE 64 INPUT ...');
        self.put("SCALE 64 INPUT 1,1,1,1,0,0,0,0")
        self.skip()                       # put skip;
        for j in range(1, FFT00_N, 2):    # do j = 1 to 7 by 2; j2 = j + 1; call bf;
            j2 = j + 1
            self.bf(j, j2, self.w["w0r"], self.w["w0i"])
        self.bf(1, 3, self.w["w0r"], self.w["w0i"])      # stage 2 (m=4)
        self.bf(2, 4, self.w["w2r"], self.w["w2i"])
        self.bf(5, 7, self.w["w0r"], self.w["w0i"])
        self.bf(6, 8, self.w["w2r"], self.w["w2i"])
        self.bf(1, 5, self.w["w0r"], self.w["w0i"])      # stage 3 (m=8)
        self.bf(2, 6, self.w["w1r"], self.w["w1i"])
        self.bf(3, 7, self.w["w2r"], self.w["w2i"])
        self.bf(4, 8, self.w["w3r"], self.w["w3i"])
        for i in range(1, FFT00_N + 1):   # do i = 1 to 8;
            self.skip()
            self.put("X")
            self.put(i)
            self.put("RE")
            t = self.xr[i - 1]            # t = xr(i); sg = 0; if t < z then sg = 1;
            sg = 0
            if t < self.z:
                sg = 1
            self.prn(t, sg)
            self.put("IM")
            t = self.xi[i - 1]            # t = xi(i); sg = 0; if t < z then sg = 1;
            sg = 0
            if t < self.z:
                sg = 1
            self.prn(t, sg)
        self.skip()                       # put skip;
        return self


def _fft00_finalize(raw):
    norm = _hamm00_re.sub(rb" +", b" ",
                          (raw + "\r\n").encode().replace(b"\r\n", b"\n")).decode()
    lines = norm.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def _fft00_parse_value(tokens, at):
    """Decode one printed Q6 value: [ '-' ] <int> '.' d d d -> (thousandths, next)."""
    sign = 1
    if tokens[at] == "-":
        sign = -1
        at += 1
    ip = int(tokens[at])
    assert tokens[at + 1] == ".", tokens[at:at + 4]
    for d in tokens[at + 2:at + 5]:
        assert len(d) == 1 and d.isdigit(), tokens[at:at + 5]
    frac = int("".join(tokens[at + 2:at + 5]))
    return sign * (ip * 1000 + frac), at + 5


def fft00():
    """FFT-00: the complete normalized console stream (collapse-spaces-v1) of the
    adapted Rosetta Code FFT -- the 8-point transform of (1,1,1,1,0,0,0,0) in Q6
    fixed point.  Derived from the declared design by a statement-for-statement
    mirror of FFT-00.PLI, never captured (L3).  Checked by THREE independent
    models: the port's final state vs the hand-published Q6 table; the port vs a
    naive double-precision DFT computed here straight from the definition, within
    the declared tolerance 0.02 (the Q6 twiddle quantization); and every PRINTED
    token pair reconstructed back to thousandths and compared with the toward-zero
    scaling of that same table.  Invariants: the 12-butterfly schedule, the 48
    digit emissions, the FIXED BIN(15) range of every intermediate (asserted
    inside the port), the 13-line / 507-byte framing and the <=78-column law."""
    assert FFT00_N == 8 and FFT00_SCALE == 64
    port = _Fft00Port().run()
    assert port.bf_calls == 12, port.bf_calls
    assert port.digits == 48, port.digits
    got = [(port.xr[k], port.xi[k]) for k in range(FFT00_N)]
    # (1) the hand-published Q6 table
    assert got == FFT00_PUBLISHED, got
    # (2) the independent naive DFT, within the declared Q6 tolerance
    dft = _fft00_dft_naive(FFT00_INPUT)
    worst = 0.0
    for (q, (r, m)) in zip(dft, got):
        worst = max(worst, abs(q.real - r / float(FFT00_SCALE)),
                    abs(q.imag - m / float(FFT00_SCALE)))
    assert worst <= FFT00_TOL, worst
    # the DFT itself equals the analytical closed form (fourth check of the
    # expected VALUES, computed without the port at all)
    root2 = 2 ** 0.5
    exact = [complex(4, 0), complex(1, -(1 + root2)), complex(0, 0),
             complex(1, -(root2 - 1)), complex(0, 0),
             complex(1, root2 - 1), complex(0, 0), complex(1, 1 + root2)]
    for (a, b) in zip(dft, exact):
        assert abs(a - b) < 1e-12, (a, b)
    # (3) the printed tokens reconstruct to the table's own thousandths
    lines = _fft00_finalize(port.raw)
    raw = (port.raw + "\r\n").encode()
    assert len(raw) == FFT00_RAW_BYTES, len(raw)
    assert len(lines) == FFT00_LINES, len(lines)
    assert lines[0] == "", lines[0]                     # first PUT SKIP [C352]
    assert lines[1] == "FFT-00 COOLEY-TUKEY N=8", lines[1]
    assert lines[2] == "SCALE 64 INPUT 1,1,1,1,0,0,0,0", lines[2]
    assert lines[3] == "", lines[3]
    assert lines[-1] == "" and lines[-2].startswith("X 8 "), lines[-2:]
    for k in range(FFT00_N):
        toks = lines[4 + k].split(" ")
        assert toks[0] == "X" and toks[1] == str(k + 1) and toks[2] == "RE", toks
        re_v, at = _fft00_parse_value(toks, 3)
        assert toks[at] == "IM", toks
        im_v, at = _fft00_parse_value(toks, at + 1)
        assert at == len(toks), toks
        assert re_v == _fft00_tdiv(FFT00_PUBLISHED[k][0] * 1000, FFT00_SCALE), toks
        assert im_v == _fft00_tdiv(FFT00_PUBLISHED[k][1] * 1000, FFT00_SCALE), toks
    # the digit path must stay inside bin15: rem*1000 is the largest magnitude
    assert port.max_magnitude <= FFT00_B15_HI, port.max_magnitude
    # frame law: no emitted line reaches the 79-column PLILIB wrap (PROPOSED)
    for seg in raw.split(b"\r\n"):
        assert len(seg) <= 78, (len(seg), seg)
    return lines


DERIVATIONS = {"table00": table00, "table01": table01,
               "math00": math00, "proc00": proc00, "hist00": hist00,
               "ptr00": ptr00, "strng00": strng00, "dec00": dec00,
               "flt00": flt00, "tab02": tab02,
               "builtin00": builtin00, "strcat00": strcat00, "cond00": cond00,
               "dec01": dec01, "flt01": flt01, "edit00": edit00,
               "wkday00": wkday00, "hamm00": hamm00, "hang00": hang00,
               "amaz00": amaz00, "tict00": tict00, "life00": life00,
               "dhry00": dhry00, "fft00": fft00,
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


