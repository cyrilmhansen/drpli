#!/usr/bin/env python3
"""E2E-48/P1 round 2 -- the discriminating follow-ups to the E48A1..E48A15 bank.

Same format rules as mkprobes.py (strict CRLF + 0x1A, `end <name>;', <=72 columns,
ASCII, self-terminating, explicit `stop;'); the rules and their evidence are in
that file's docstring and are not restated here.

WHY A SECOND BANK.  Round 1 answered the condition questions but left three
things unpinned, and one NEW defect appeared that round 1 itself discovered:

  * `if ^b then do; ... end;' with NO else -- CREATE:35's exact spelling.  E48A2
    had an else, and the no-else form is what CREATE needs.
  * DATA-area size when a STATIC cell is present and there are NO automatics.
    E48A3/E48A4 came out 4 and 9 against DR's 3 and 8 -- exactly one byte too
    many, always.  My formula is `sy_total + pool_total + max(auto, pl_total) +
    2*temps` and `pl_total` (bind's top-block section total) is 1 even for a
    STATIC bit, so the static byte is counted twice whenever it dominates the
    max.  FLTPOLY2 hides this because its automatics (4-byte floats) are bigger
    than the static byte.  PROTOCOL #4: I do not get to decide DR's rule from my
    own arithmetic -- these probes measure it.
  * whether the `= literal' STORE and the condition STORE can share one pool
    cell, and where the varying cell sits relative to the pool.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", ".."))
OUT = os.path.join(ROOT, "probes")
MAXCOL = 72

PROBES = []


def probe(name, body):
    PROBES.append((name, body))


# ---- the no-else forms, which is what CREATE actually spells ----------------
probe("E48B1", """\
E48B1:
  procedure options(main);
  /* [E2E-48/P1 r2] `if ^b then do; ... end;' with NO ELSE, which
     is CREATE:35 exactly.  E48A2 measured the WITH-else form;
     CREATE needs this one. */
  dcl b bit(1) static initial('0'b);
  dcl n fixed bin(15);
  n = 0;
  do while(^b);
     n = n + 1;
     if ^b then
        do;
        n = n + 1;
        end;
     if n = 4 then b = '1'b;
  end;
  put list('N=', n);
  stop;
end E48B1;
""")

probe("E48B2", """\
E48B2:
  procedure options(main);
  /* [E2E-48/P1 r2] a bare `if b then do; ... end;' (positive,
     no else) on a STATIC bit: the control for E48B1, and the
     FLTPOLY2 shape spelled directly. */
  dcl b bit(1) static initial('1'b);
  if b then
     do;
     put list('Y');
     end;
  put list('E');
  stop;
end E48B2;
""")

# ---- the DATA-area discriminators ------------------------------------------
probe("E48B3", """\
E48B3:
  procedure options(main);
  /* [E2E-48/P1 r2] THE MINIMAL STATIC CASE: one static bit, one
     literal, no automatics, no stop.  If DR's DEF-DATA-SIZE is 2
     the static cell is NOT part of bind's top section total; if
     it is 3 my formula's shape is right and something else
     charges the byte. */
  dcl b bit(1) static initial('0'b);
  put list('T');
end E48B3;
""")

probe("E48B4", """\
E48B4:
  procedure options(main);
  /* [E2E-48/P1 r2] STATIC BIT + ONE AUTOMATIC, same literal.
     Discriminates "statics are outside the section total" (DR
     would be 1 + 1 + 2 = 4) from "the static byte is the
     section" (DR would be 1 + 1 + 2 = 4 too) -- so read the
     ADDRESSES, not just the size: b at 0000, 'T' at 0001, n at
     0002 is the [C114] layout. */
  dcl b bit(1) static initial('0'b);
  dcl n fixed bin(15);
  n = 1;
  put list('T', n);
  stop;
end E48B4;
""")

probe("E48B5", """\
E48B5:
  procedure options(main);
  /* [E2E-48/P1 r2] TWO STATIC BITS, no automatics: does the
     static section charge 2, or 1 (last-cell-wins)?  E20B/E20D
     pinned one static only. */
  dcl b bit(1) static initial('0'b);
  dcl c bit(1) static initial('1'b);
  if b then
     put list('B');
  if c then
     put list('C');
  stop;
end E48B5;
""")

probe("E48B6", """\
E48B6:
  procedure options(main);
  /* [E2E-48/P1 r2] A STATIC CHARACTER: my codegen refuses every
     STATIC except BIT(1) ("unsampled [TBD]"), and EXPR2, FSCAN,
     LOAN2, MPMCALLB and REPORT all stop there.  This measures
     DR's cell for the simplest one -- the evidence the next phase
     needs, whether or not this phase uses it. */
  dcl s char(3) static initial('AB');
  put list(s);
  stop;
end E48B6;
""")

probe("E48B7", """\
E48B7:
  procedure options(main);
  /* [E2E-48/P1 r2] TWO STATIC BITS and a STATIC FILE-like order:
     static cell adjacency (b at 0000, c at 0001) with a literal
     ABOVE them, i.e. the [C114] block order with two statics. */
  dcl b bit(1) static initial('1'b);
  dcl c bit(1) static initial('0'b);
  if ^b then
     put list('N');
  if c then
     put list('P');
  else
     put list('Q');
  stop;
end E48B7;
""")

# ---- store/condition interaction with the pool ------------------------------
probe("E48B8", """\
E48B8:
  procedure options(main);
  /* [E2E-48/P1 r2] `name = 'AB'' THEN `b = (name = 'AB')': one
     literal used by a varying store AND by the comparison.  If
     DR dedups it to ONE cell the pool is 2 bytes, not 4, and the
     SCVCM's MVI A operand names the same cell the store wrote. */
  dcl b bit(1) static initial('0'b);
  dcl name char(30) varying;
  name = 'AB';
  b = (name = 'AB');
  put list('R=', b);
  stop;
end E48B8;
""")

probe("E48B9", """\
E48B9:
  procedure options(main);
  /* [E2E-48/P1 r2] the automatic bit cell's ADDRESS next to the
     pool and next to a varying cell -- E48A5 put `b' at 0002 with
     the 2-byte 'N=' pool below it; here the pool is bigger, so a
     shift proves the automatics start ABOVE the pool ([C114]). */
  dcl name char(30) varying;
  dcl b bit(1);
  name = 'ABCDEFGH';
  b = (name = 'EOF');
  do while(^b);
     put list('.');
     name = 'EOF';
     b = (name = 'EOF');
  end;
  put list('DONE');
  stop;
end E48B9;
""")


def check():
    bad = []
    for name, body in PROBES:
        lines = body.rstrip("\n").split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > MAXCOL:
                bad.append("%s:%d is %d columns (limit %d)"
                           % (name, i, len(line), MAXCOL))
            if "\t" in line or not re.match(r"^[\x20-\x7e]*$", line):
                bad.append("%s:%d is not printable ASCII / has a tab" % (name, i))
        if lines[0] != name + ":":
            bad.append("%s: line 1 must be `%s:'" % (name, name))
        if not re.match(r"^end [A-Z][A-Z0-9]*;$", lines[-1].strip()):
            bad.append("%s: last line must be `end <name>;'" % name)
        if len(name) > 8:
            bad.append("%s: not a CP/M-8 name" % name)
    seen, dupes = set(), set()
    for n, _b in PROBES:
        if n in seen:
            dupes.add(n)
        seen.add(n)
    if dupes:
        bad.append("duplicate names: %s" % sorted(dupes))
    for n in sorted(seen):
        if os.path.exists(os.path.join(OUT, n + ".PLI")):
            bad.append("%s: probes/%s.PLI exists -- nothing is overwritten" % (n, n))
    return bad


def main():
    bad = check()
    if bad:
        for b in bad:
            print("REFUSED: " + b, file=sys.stderr)
        return 1
    for name, body in sorted(PROBES):
        data = body.rstrip("\n").replace("\n", "\r\n").encode("ascii") + b"\r\n\x1a"
        assert data.count(b"\n") == data.count(b"\r\n")
        with open(os.path.join(OUT, name + ".PLI"), "wb") as f:
            f.write(data)
        print("wrote probes/%s.PLI (%d bytes)" % (name, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
