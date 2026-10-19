#!/usr/bin/env python3
"""DR PL/I-80 v1.4 FLOAT BINARY(24) value model  (E2E-10 step 1, research only).

Pure Python.  Nothing here is imported by the OCaml compiler; the point is an
INDEPENDENT characterisation of DR's 4-byte float representation, validated
byte-for-byte against the literal pools DR actually emitted in
golden/e2e13/*/NAME.REL (see spec/notes/e2e10-step1-float-model.md).

Representation (all DIRECTLY OBSERVED, see OBSERVED table in the notes):

    byte 0  fraction bits  7..0     (little-endian)
    byte 1  fraction bits 15..8
    byte 2  bits 6..0 = fraction bits 22..16 ; bit 7 = SIGN (1 = negative)
    byte 3  characteristic (biased exponent)

    value = (-1)^sign * (1 + fraction/2**23) * 2**(byte3 - 129)
    zero  = all four bytes 0x00  (byte3 == 0 is a legal NORMAL exponent, so
                                  zero is a special case, not exp=0)
    range = |v| in [2**-129, 2**127); outside it DR pass 2 raises CONVERT
            (observed: 1E39, 1E-45, 1E-60, 1.8E38 rejected;
                      1E38, 1.6E38, 3E-39, 2E-39 accepted)
    no subnormals, no distinct negative zero (-0.0 -> 00 00 00 00)

Rounding: nearest, TIES AWAY FROM ZERO.  Pinned by exact integer ties:
    16777217 -> 16777218,  16777219 -> 16777220,
    -16777217 -> -16777218, -16777219 -> -16777220
    (round-half-even would have chosen 16777216 and -16777216.)
"""
import os, re, subprocess, sys
from fractions import Fraction as F
from decimal import Decimal

FRAC_BITS = 23
BIAS = 129
GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "golden", "e2e13")


class RangeError(Exception):
    """|value| outside DR's accepted float range."""


# ---------------------------------------------------------------- decode

def decode(b):
    """4 bytes -> exact Fraction (or F(0))."""
    assert len(b) == 4, b
    if bytes(b) == b"\x00\x00\x00\x00":
        return F(0)
    b0, b1, b2, e = b
    sign = -1 if (b2 & 0x80) else 1
    frac = ((b2 & 0x7F) << 16) | (b1 << 8) | b0
    return sign * (1 + F(frac, 1 << FRAC_BITS)) * F(2) ** (e - BIAS)


# ---------------------------------------------------------------- encode

def encode(x, tie="away"):
    """exact Fraction -> DR's 4 bytes.  tie: 'away' (DR, observed) or 'even'."""
    x = F(x)
    if x == 0:
        return b"\x00\x00\x00\x00"
    sign_bit = 0x80 if x < 0 else 0x00
    a = abs(x)
    # normalise: find k with 1 <= a / 2**k < 2
    k = 0
    while a >= 2 ** (k + 1):
        k += 1
    while a < 2 ** k:
        k -= 1
    v = a / F(2) ** k                       # significand in [1,2)
    scaled = (v - 1) * (1 << FRAC_BITS)     # exact
    n = int(scaled)
    rem = scaled - n
    if rem > F(1, 2) or (rem == F(1, 2) and tie == "away"):
        n += 1
    elif rem == F(1, 2) and tie == "even" and (n & 1):
        n += 1
    if n >= 1 << FRAC_BITS:                 # carry out of the fraction
        n = 0
        k += 1
    e = k + BIAS
    if e < 0 or e > 255:
        raise RangeError("magnitude 2**%d outside DR float range" % k)
    return bytes([n & 0xFF, (n >> 8) & 0xFF,
                  ((n >> 16) & 0x7F) | sign_bit, e & 0xFF])


def from_literal(text):
    """PL/I float literal as written ('1.5', '3E7', '-16777217') -> bytes.

    The decimal value is taken EXACTLY (no intermediate precision), which is
    what reproduces every observed pool cell -- see validate()."""
    t = text.strip().lower().replace(" ", "")
    neg = t.startswith("-")
    if neg:
        t = t[1:]
    if t.startswith("+"):
        t = t[1:]
    value = F(Decimal(t))
    if neg:
        value = -value
    return encode(value)


def value_of(text):
    """Literal as written -> the exact float value DR stored (Fraction)."""
    return decode(from_literal(text))


# ------------------------------------------------- extraction from the goldens

CELL_RE = re.compile(r"LXI +H,\* +S\(([0-9A-F]{4})\)")
SRC_RE = re.compile(r"^\s*(\d+) +[a-z] +[0-9A-F]{4} +(.*)$")
# Every numeric token in the statement text is a CANDIDATE for the pool cell
# (FFACT's `if i = 0 then return (1);` uses the 1, not the 0); a cell only
# counts as reproduced when the model matches it for at least one.
LIT_RE = re.compile(r"-?\d+(?:\.\d+)?(?:E[-+]?\d+)?")


def data_cells(rel):
    out = subprocess.run(["python3", os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "reldump.py"), rel],
        capture_output=True, text=True).stdout
    d = {}
    for l in out.splitlines():
        p = l.split()
        if len(p) >= 6 and p[2] == "DATA" and p[3] == "data":
            d[int(p[4], 16)] = int(p[5], 16)
    return d


def observed(name):
    """[(literal text, 4 bytes)] for one golden specimen, via its code trace."""
    rel = os.path.join(GOLDEN, name, name + ".REL")
    prn = os.path.join(GOLDEN, name, name + ".PRN")
    if not (os.path.exists(rel) and os.path.exists(prn)):
        return []
    d = data_cells(rel)
    t = open(prn, "rb").read().decode("latin-1").replace("\r", "")
    t = t[t.rindex("COMPILATION OF:"):]
    pairs, cur, seen = [], None, set()
    for l in t.split("\n"):
        m = SRC_RE.match(l)
        if m and m.group(2).strip() and not m.group(2).strip().startswith("*"):
            cur = m.group(2).strip()
        c = CELL_RE.search(l)
        if c:
            a = int(c.group(1), 16)
            if a in seen:
                continue
            seen.add(a)
            cell = bytes(d.get(a + i, 0) for i in range(4))
            # A trace line can carry several numbers ("if i = 0 then return (1)"):
            # the pool cell is one of them, so record every candidate and let
            # validate() accept a match on any -- attribution, not assertion.
            pairs.append((LIT_RE.findall(cur or ""), cell, cur or ""))
    return pairs


def validate(verbose=True):
    """Bucket every *S cell DR emitted:

      MATCHED       the model reproduces it from a numeric literal on that line
      UNCLASSIFIED  pool cell that is not a float literal (string literals live
                    in the same pool -- e.g. FLTPOLY's '       2' shows up as
                    20 20 20 20); listed with its ASCII reading, never counted
                    as a float-literal test.
      MISMATCH      a numeric candidate existed and NONE reproduces the bytes.
    """
    total = bad = other = 0
    fails = []
    unclass = []
    for name in sorted(os.listdir(GOLDEN)):
        if not os.path.isdir(os.path.join(GOLDEN, name)):
            continue
        for lits, cell, srcline in observed(name):
            if not lits:
                continue
            total += 1
            want = None
            for lit in lits:
                try:
                    if from_literal(lit) == cell:
                        want = lit
                        break
                except RangeError:
                    pass
            if want is None:
                # A quoted literal on the same line whose 4 bytes are all
                # printable ASCII means the cell is a STRING pool cell (FLTPOLY
                # shares one pool for floats and strings): exclude it from the
                # float-literal count rather than call it a mismatch.
                if ("'" in srcline
                        and all(32 <= c < 127 for c in cell)):
                    other += 1
                    unclass.append("%-6s %s -> [%s]"
                                   % (name, cell.hex(" "),
                                      "".join(chr(c) for c in cell)))
                elif lits:
                    bad += 1
                    fails.append((name, "/".join(lits), cell.hex(" "),
                                  "decoded=%.6e" % float(decode(cell))))
                else:
                    other += 1
                    printable = "".join(chr(c) if 32 <= c < 127 else "."
                                        for c in cell)
                    unclass.append("%-6s %s -> [%s] %r"
                                   % (name, cell.hex(" "), printable, lits))
            elif verbose:
                print("  OK   %-6s %-16s -> %s" % (name, want, cell.hex(" ")))
    for f in fails:
        print("  MISMATCH %-6s %-16s DR=%s  model=%s" % f)
    if other:
        print("  unclassified pool cells (not float literals): %d" % other)
        for u in unclass:
            print("    %s" % u)
    print("pool validation: %d/%d float-literal cells reproduced byte-exactly, "
          "%d mismatch, %d non-float pool cells excluded"
          % (total - bad, total, bad, other))
    return total, bad


# ---------------------------------------------------------------- unit tests

def selftest():
    ok = 0
    def eq(got, want, what):
        nonlocal ok
        assert got == want, "%s: got %s want %s" % (what, got.hex(" "), want.hex(" "))
        ok += 1
    # --- directly observed cells
    eq(from_literal("1.5"), bytes.fromhex("00004081"), "1.5 [R3001]")
    eq(from_literal("2"), bytes.fromhex("00000082"), "2 [R3001]")
    eq(from_literal("2.5"), bytes.fromhex("00002082"), "2.5 [R3003]")
    eq(from_literal("-1.5"), bytes.fromhex("0000c081"), "-1.5 [R3007]")
    eq(from_literal("0"), bytes.fromhex("00000000"), "zero [R3007]")
    eq(from_literal("0.5"), bytes.fromhex("00000080"), "0.5 [R3009]")
    eq(from_literal("0.9375"), bytes.fromhex("00007080"), "0.9375 [R3009]")
    eq(from_literal("1.00001525878906"), bytes.fromhex("80000081"), "2**-16 byte0 [R3006]")
    eq(from_literal("1.00000011920929"), bytes.fromhex("01000081"), "2**-23 byte0 [R3006]")
    # --- little-endian fraction: byte1 and byte0 both exercised
    eq(from_literal("0.1"), bytes.fromhex("cdcc4c7d"), "0.1 nearest-up [R3011]")
    eq(from_literal("-0.1"), bytes.fromhex("cdcccc7d"), "-0.1 sign [R3018]")
    eq(from_literal("12345.678"), bytes.fromhex("b6e6408e"), "12345.678 [R3011]")
    eq(from_literal("3E7"), bytes.fromhex("c0e16499"), "3E7 [R3008]")
    eq(from_literal("-3E7"), bytes.fromhex("c0e1e499"), "-3E7 [R3018]")
    eq(from_literal("1E-20"), bytes.fromhex("08e53c3e"), "1E-20 [R3008]")
    # --- ties: away from zero (NOT half-even)
    eq(from_literal("16777217"), bytes.fromhex("01000099"), "2**24+1 tie up [R3010]")
    eq(from_literal("16777219"), bytes.fromhex("02000099"), "2**24+3 tie up [R3020]")
    eq(from_literal("-16777217"), bytes.fromhex("01008099"), "neg tie away [R3020]")
    eq(from_literal("-16777219"), bytes.fromhex("02008099"), "neg tie away [R3020]")
    eq(from_literal("16777215"), bytes.fromhex("ffff7f98"), "2**24-1 exact [R3010]")
    eq(from_literal("50331649"), bytes.fromhex("0000409a"), "quarter ulp down [R3020]")
    # --- exponent boundaries observed
    eq(from_literal("1E38"), bytes.fromhex("997616ff"), "max exp byte 255 [R3019]")
    eq(from_literal("1.6E38"), bytes.fromhex("c2bd70ff"), "1.6E38 [R3024]")
    eq(from_literal("3E-39"), bytes.fromhex("1eab0201"), "exp byte 1 [R3022]")
    eq(from_literal("2E-39"), bytes.fromhex("7e392e00"), "exp byte 0 legal [R3023]")
    # --- range errors DR also reports (CONVERT, pass 2)
    for lit in ("1E39", "1.8E38", "1E-45", "1E-60"):
        try:
            from_literal(lit)
            raise AssertionError("%s should be out of range" % lit)
        except RangeError:
            ok += 1
    # --- decode round-trips every observed cell exactly back to a value DR
    #     prints as the literal (sanity, not a DR comparison)
    for lit in ("1.5", "2", "2.5", "-1.5", "0", "0.5", "0.9375", "0.1", "1E38",
                "2E-39", "16777217", "3E7", "12345.678", "1E-20"):
        v = decode(from_literal(lit))
        ref = F(Decimal(lit))
        tol = abs(ref) / 2 ** 22 + F(1, 2 ** 130)
        assert abs(v - ref) <= tol, (lit, float(v), float(ref))
        ok += 1
    print("floatmodel selftest: %d assertions passed" % ok)
    return ok


if __name__ == "__main__":
    selftest()
    total, bad = validate(verbose=("-v" in sys.argv))
    sys.exit(1 if bad else 0)
