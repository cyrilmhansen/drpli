#!/usr/bin/env python3
"""E2E-48/P1 probe writer -- condition forms: `^bit(1)`, and a condition stored
into a BIT(1).

Format rules, and the evidence for each, are inherited from
`../e2e42-p2c/mkprobes.py` and are enforced here rather than remembered:

  1. EVERY line ends CRLF, including the last; the file ends `...<CRLF>0x1A`.
     [C303] as corrected by P2c: DR tolerates bare LF in the BODY and requires a
     CR on the LAST line; strict CRLF everywhere satisfies both, so this writer
     emits nothing else (no LF-mode pair is needed -- P2c already measured it).
  2. `end <name>;`, never `end <name>.`
  3. Line 1 is `<name>:` matching the filename.
  4. No line longer than 72 columns; no tabs.
  5. ASCII only -- DR's reader and our lexer both take plain bytes.
  6. Every loop is self-terminating and every program ends with an explicit
     `stop;`, so a specimen that is later LINKed and RUNNED cannot hang the
     emulator ([C308]: a registered "hang" that was really a budget is a cost we
     do not want to pay again).

Bit literals are written in their LITERAL form (`'0'b`, `'1'b`) rather than
through `%replace true/false` on purpose: the `%replace` route is already
measured by FLTPOLY2/CREATE, and keeping it out of these probes means a MISS
cannot be confused with a preprocessor question.
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


# ---------------------------------------------------------------- P1: the loop
probe("E48A1", """\
E48A1:
  procedure options(main);
  /* [E2E-48/P1] THE NEGATED BIT TEST IN A LOOP HEAD.  CREATE:31
     spells exactly this and DR carries it at 0052-0058 as
     LDA/ORA/FA plus the 5-byte skip chain whose tail is
     JMP-back.  Mine refuses it: `condition form not in
     E2E-3b subset [TBD]: (^ eofile)'. */
  dcl b bit(1) static initial('0'b);
  dcl n fixed bin(15);
  n = 0;
  do while(^b);
     n = n + 1;
     put list('.');
     if n = 3 then b = '1'b;
  end;
  put list('N=', n);
  stop;
end E48A1;
""")

# ------------------------------------------------------- P2: IF/ELSE with ^bit
probe("E48A2", """\
E48A2:
  procedure options(main);
  /* [E2E-48/P1] THE NEGATED BIT TEST IN AN IF, WITH AN ELSE.
     CREATE:35 has `if ^eofile then do; ... end;' with NO else;
     this asks whether the ELSE is reached through the same
     5-byte chain, which no object in the tree shows. */
  dcl b bit(1) static initial('0'b);
  if ^b then
     put list('T');
  else
     put list('F');
  stop;
end E48A2;
""")

# --------------------------------------------- P3: bare bit test, static bit
probe("E48A3", """\
E48A3:
  procedure options(main);
  /* [E2E-48/P1] CONTROL: the POSITIVE bare-bit test on a
     STATIC bit, spelled directly (FLTPOLY2 measures this with a
     %replace'd `true').  The skip byte is the open question:
     [C112] writes JNZ for the `= 0'b' form, FLTPOLY2 0075 is JP
     for the bare test, and the EXCLUSIVE-OR family keeps the
     [C072] CA defect. */
  dcl b bit(1) static initial('0'b);
  if b then
     put list('T');
  else
     put list('F');
  stop;
end E48A3;
""")

# ------------------------------------------ P4: `= bit literal' as a condition
probe("E48A4", """\
E48A4:
  procedure options(main);
  /* [E2E-48/P1] `b = '1'b' AND `b = '0'b' AS CONDITIONS, in one
     object, on a STATIC bit.  E11D pins the ANI/SUI ladder
     outside a loop; the skip byte it pins is JNZ, which is not
     what a bare-bit test uses.  This row decides whether the
     ladder keeps JNZ here. */
  dcl b bit(1) static initial('0'b);
  if b = '1'b then
     put list('ONE');
  if b = '0'b then
     put list('ZERO');
  stop;
end E48A4;
""")

# ---------------------------------------------- P5: the AUTOMATIC bit cell
probe("E48A5", """\
E48A5:
  procedure options(main);
  /* [E2E-48/P1] THE SAME NEGATED TEST ON AN AUTOMATIC BIT(1).
     RETRIEVE:17/34 and DIOCOPY:40/109 declare `eofile bit(1)'
     with NO static and test `^eofile'; their objects are in
     golden/first8080u but neither compiles in this compiler for
     OPEN/BASED reasons, so the automatic bit cell's test is
     UNMEASURED here.  Prediction: identical 3A/B7/FA, one-byte
     cell, AUTO STORAGE +1 ([C114]). */
  dcl b bit(1);
  dcl n fixed bin(15);
  b = '0'b;
  n = 0;
  do while(^b);
     n = n + 1;
     if n = 2 then b = '1'b;
  end;
  put list('N=', n);
  stop;
end E48A5;
""")

# ------------------------------- P6: the STORED CONDITION, CREATE's own shape
probe("E48A6", """\
E48A6:
  procedure options(main);
  /* [E2E-48/P1] THE STORE OF A CONDITION INTO A BIT(1), exactly
     CREATE:34: `eofile = (name = 'EOF')'.  DR at 008F-00A0, 16
     bytes: LXI H,varying / XCHG / LXI H,literal / MVI A,n /
     CALL ?SCVCM / SUI 01 / SBB A / STA cell.  The last three are
     [C095]'s flag trick, then [C079]'s 32-with-inline-reloc
     store; the store form (not the comparison) is the question. */
  dcl b bit(1) static initial('0'b);
  dcl name char(30) varying;
  name = 'AB';
  b = (name = 'EOF');
  put list('B=', b);
  stop;
end E48A6;
""")

# ------------------------------ P7: the stored condition, fixed binary = 0
probe("E48A7", """\
E48A7:
  procedure options(main);
  /* [E2E-48/P1] THE OTHER CONDITION CLASSES, one per statement,
     all stored into the same bit cell.  `k = 0' is the class
     [C095] pins as a boolean operand (LXI H / MOV A,M / INX H /
     ORA M / SUI 01 / SBB A); whether the STA simply appends is
     UNMEASURED.  `k = 5' has no boolean sample at all. */
  dcl b bit(1) static initial('0'b);
  dcl k fixed bin(15);
  k = 0;
  b = (k = 0);
  put list('P=', b);
  b = (k = 5);
  put list('Q=', b);
  stop;
end E48A7;
""")

# --------------------------------- P8: the stored condition with `^='
probe("E48A8", """\
E48A8:
  procedure options(main);
  /* [E2E-48/P1] `b = (k ^= 0)'.  `^=' is DR's ASCII spelling of
     NOT-EQUAL and its skip byte is the [C072] CA defect in every
     context measured so far (integer var/literal, DEC, mod).  A
     materialising `^=' has no sample: does the defect travel? */
  dcl b bit(1) static initial('0'b);
  dcl k fixed bin(15);
  k = 3;
  b = (k ^= 0);
  put list('R=', b);
  stop;
end E48A8;
""")

# ------------------------------------ P9: a relational stored into a bit
probe("E48A9", """\
E48A9:
  procedure options(main);
  /* [E2E-48/P1] `b = (k > 0)'.  [C095] records `>' only as the
     FIRST operand of a FLOAT conjunction, where DR uses the raw
     signed-comparison byte AS the boolean and materialises
     nothing.  Predicted UNMEASURED here, and a refusal
     (`COMP REQ ?') is as informative as a lowering. */
  dcl b bit(1) static initial('0'b);
  dcl k fixed bin(15);
  k = 3;
  b = (k > 0);
  put list('S=', b);
  stop;
end E48A9;
""")

# ----------------------------- P10: a bit-literal compare stored into a bit
probe("E48A10", """\
E48A10:
  procedure options(main);
  /* [E2E-48/P1] `f = (b = '1'b)'.  The ANI 80 / SUI 80 ladder
     ([C112], E11D) has never been materialised into a byte; if
     DR accepts, the boolean comes from SUI/SBB on the ladder's
     result. */
  dcl b bit(1) static initial('0'b);
  dcl f bit(1);
  f = (b = '1'b);
  put list('U=', f);
  stop;
end E48A10;
""")

# ------------------------------- P11: `b = ^(...)' -- negating a STORED value
probe("E48A11", """\
E48A11:
  procedure options(main);
  /* [E2E-48/P1] `b = ^(k = 0)'.  Distinct from P14: there `^'
     negates a TEST, here it negates a VALUE.  Whether DR emits
     CMA (0x2F) after the flag trick, inverts the compare, or
     refuses is UNMEASURED. */
  dcl b bit(1) static initial('0'b);
  dcl k fixed bin(15);
  k = 0;
  b = ^(k = 0);
  put list('V=', b);
  stop;
end E48A11;
""")

# -------------------------------- P12: the stored condition in a loop test
probe("E48A12", """\
E48A12:
  procedure options(main);
  /* [E2E-48/P1] THE COMBINATION CREATE USES: store the condition
     result, then test its negation, in one loop.  If P1 and P6
     both hold, this object should carry BOTH shapes and nothing
     new; if DR emits something else for the pair, the two shapes
     are not independent. */
  dcl b bit(1) static initial('0'b);
  dcl name char(30) varying;
  dcl n fixed bin(15);
  n = 0;
  do while(^b);
     n = n + 1;
     name = 'AB';
     b = (name = 'EOF');
     if n = 4 then b = '1'b;
  end;
  put list('N=', n);
  stop;
end E48A12;
""")

# ------------------------- P13: `^' as a TEST operator on a general condition
probe("E48A13", """\
E48A13:
  procedure options(main);
  /* [E2E-48/P1] `if ^(k = 0) then' and `do while(^(n = 3))'.
     The parser gives both an Econd around a relation; whether DR
     has a NOT-condition lowering at all is UNMEASURED (the corpus
     uses `^' only on bit cells and inside strings). */
  dcl k fixed bin(15);
  dcl n fixed bin(15);
  k = 0;
  n = 0;
  if ^(k = 0) then
     put list('A');
  do while(^(n = 3));
     n = n + 1;
  end;
  put list('N=', n);
  stop;
end E48A13;
""")

# ------------------------------ P14: a bit cell as a conjunction operand
probe("E48A14", """\
E48A14:
  procedure options(main);
  /* [E2E-48/P1] `if k = 0 & b then'.  [C095] pins the fixed-bin
     and DECIMAL boolean operands; a BIT(1) operand has no sample,
     and my `lower_bool' refuses it.  A bit cell is ONE byte, so
     the 2-byte `= 0' tail cannot read it -- that is exactly why
     this needs DR's own bytes. */
  dcl b bit(1) static initial('1'b);
  dcl k fixed bin(15);
  k = 0;
  if k = 0 & b then
     put list('YES');
  else
     put list('NO');
  stop;
end E48A14;
""")

# --------------------------------- P15: PUT of a BIT(1) variable (predicted
#                                    refusal)
probe("E48A15", """\
E48A15:
  procedure options(main);
  /* [E2E-48/P1] `put list(b)' on a BIT(1).  No DR object in the
     tree prints a bit string and my refusal text says so; this
     probe turns that absence-of-witness into a MEASUREMENT.  A
     .REL here would open a bit-output route this compiler has
     never lowered; `COMP REQ ?' here is a dr-refuses row. */
  dcl b bit(1) static initial('1'b);
  put list(b);
  stop;
end E48A15;
""")


def check():
    bad = []
    for name, body in PROBES:
        lines = body.split("\n")
        if lines[-1] != "":
            bad.append("%s: body must end with a newline" % name)
        lines = lines[:-1]
        for i, line in enumerate(lines, 1):
            if len(line) > MAXCOL:
                bad.append("%s:%d is %d columns (limit %d)"
                           % (name, i, len(line), MAXCOL))
            if "\t" in line:
                bad.append("%s:%d has a tab" % (name, i))
            if not re.match(r"^[\x20-\x7e]*$", line):
                bad.append("%s:%d is not printable ASCII" % (name, i))
        if not lines or lines[0] != name + ":":
            bad.append("%s: line 1 must be `%s:', found %r"
                       % (name, name, lines[0] if lines else None))
        if not lines[-1].strip().startswith("end %s;" % name):
            bad.append("%s: last line must be `end %s;'" % (name, name))
        if not re.match(r"^end [A-Z][A-Z0-9]*;$", lines[-1].strip()):
            bad.append("%s: terminator must be `end <name>;' exactly" % name)
        if len(name) > 8 or not re.match(r"^E48A[0-9]+$", name):
            bad.append("%s: not a CP/M-8 name in this bank's form" % name)
    seen, dupes = set(), set()
    for n, _b in PROBES:
        if n in seen:
            dupes.add(n)
        seen.add(n)
    if dupes:
        bad.append("duplicate probe names: %s" % sorted(dupes))
    for n in sorted(seen):
        if os.path.exists(os.path.join(OUT, n + ".PLI")):
            bad.append("%s: probes/%s.PLI already exists -- nothing is "
                       "overwritten" % (n, n))
    return bad


def main():
    bad = check()
    if bad:
        for b in bad:
            print("REFUSED: " + b, file=sys.stderr)
        return 1
    written = []
    for name, body in sorted(PROBES):
        text = body.rstrip("\n")
        data = text.replace("\n", "\r\n").encode("ascii") + b"\r\n\x1a"
        assert data.count(b"\n") == data.count(b"\r\n")
        path = os.path.join(OUT, name + ".PLI")
        with open(path, "wb") as f:
            f.write(data)
        written.append((name, len(data)))
    for n, sz in written:
        print("wrote probes/%s.PLI (%d bytes)" % (n, sz))
    print("%d probes, all strict-CRLF + 0x1A, all <= %d columns"
          % (len(written), MAXCOL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
