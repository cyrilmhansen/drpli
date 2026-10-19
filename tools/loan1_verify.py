#!/usr/bin/env python3
"""Independent verification of LOAN1's amortisation schedule.

Nothing here reads my compiler or DR's .REL/.COM bytes: it recomputes the loan
from the SOURCE's own declarations and arithmetic, using Python's `decimal`,
and compares against the console transcript the linked programs produced.
Three variants of the interest term are carried, because DR's division
TRUNCATES before ROUND sees the value [C086/C087] and the truncation scale is
implementation-visible only through the schedule:

  exact   : round_half_away( P * i / 1200 , 2 )      -- full precision
  trunc2  : round_half_away( trunc(P * i / 1200, 2), 2 )
  trunc5  : round_half_away( trunc(P * i / 1200, 5), 2 )

If all three agree with the transcript for every row, the schedule is right
regardless of which internal scale DR actually used; a row where they differ
is reported as TIE-SENSITIVE rather than quietly averaged away.
"""
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

TRANSCRIPT = sys.argv[1] if len(sys.argv) > 1 else None


def round2(x):
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def trunc(x, n):
    return x.quantize(Decimal(1).scaleb(-n), rounding=ROUND_DOWN)


def schedule(P0, i, pmt0, variant):
    P, PMT, m, y = Decimal(P0), Decimal(pmt0), 0, 0
    rows = []
    while P > 0:
        if m % 12 == 0:
            y += 1
        m += 1
        before = P
        interest = variant(P, i)
        P = round2(P + interest)
        if P < PMT:
            PMT = P
        rows.append((m, y, before, PMT, P - PMT))
        P = round2(P - PMT)
        if len(rows) > 400:
            raise SystemExit("did not terminate")
    return rows


VARIANTS = {
    "exact":  lambda P, i: round2(P * i / Decimal(1200)),
    "trunc2": lambda P, i: round2(trunc(P * i / Decimal(1200), 2)),
    "trunc5": lambda P, i: round2(trunc(P * i / Decimal(1200), 5)),
}

if TRANSCRIPT:
    txt = open(TRANSCRIPT, encoding="latin-1").read().replace("\r", "\n")
    seen = []
    year = 0
    for line in txt.splitlines():
        mm = re.match(r"\s*Year\s+(\d+)\s*$", line)
        if mm:
            year = int(mm.group(1))
            continue
        mm = re.match(r"\s*(\d+)\s+(-?\d+\.\d{2})\s+(-?\d+\.\d{2})\s*$", line)
        if mm:
            seen.append((int(mm.group(1)), year, Decimal(mm.group(2)),
                         Decimal(mm.group(3))))
    print("transcript rows: %d" % len(seen))
else:
    seen = None

P0, i, pmt = "500.00", Decimal("14.00"), "22.10"
for name, v in VARIANTS.items():
    rows = schedule(P0, i, pmt, v)
    print("\n%s: %d rows, last = %s" % (name, len(rows), rows[-1][:4]))
    if seen:
        bad = []
        for r, s in zip(rows, seen):
            # r = (m, y, principal_before, payment, principal_after)
            if (r[0], r[1], r[2], r[3]) != (s[0], s[1], s[2], s[3]):
                bad.append((r, s))
        if len(rows) != len(seen):
            bad.append(("ROW COUNT", len(rows), len(seen)))
        if bad:
            print("  DIFFERS from transcript in %d place(s): %s" % (len(bad), bad[:3]))
        else:
            print("  MATCHES the transcript on all %d rows" % len(seen))

# tie-sensitivity report: rows where the exact and truncated variants differ
ref = schedule(P0, i, pmt, VARIANTS["exact"])
for name in ("trunc2", "trunc5"):
    alt = schedule(P0, i, pmt, VARIANTS[name])
    diff = [(a[0], a[3], b[3]) for a, b in zip(ref, alt) if a[3] != b[3]]
    print("TIE-SENSITIVE rows, %s vs exact: %d %s" % (name, len(diff), diff[:5]))
