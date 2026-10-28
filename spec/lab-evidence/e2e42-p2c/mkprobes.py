#!/usr/bin/env python3
"""E2E-42/P2c probe writer.

Writes probes/E46N*.PLI as CP/M sources.  FORMAT RULES, and the evidence for
each, are in PROCESS.md; they are enforced here rather than remembered:

  1. EVERY line ends CRLF, including the last.  [C303] states that "DR refuses
     LF outright"; that is NOT what the artifacts say (see PROCESS.md's
     correction -- E46M33 as submitted and accepted has EIGHT bare-LF body
     lines and DR listed all nine lines with correct numbers).  What the
     accepted/refused pairs actually discriminate is the FINAL line's
     terminator: an LF-terminated last line before the ^Z is what produced
     `UNEXPECTED EOF'.  Strict CRLF everywhere satisfies the real rule and
     every accepted probe in the corpus, so this writer emits nothing else.
  2. The file ends `...<CRLF>0x1A`.
  3. `end <name>;`, never `end <name>.`  (measured: E46M35).
  4. The first line is `<name>:` matching the filename, so a probe cannot be
     filed under one name and compiled as another.  (E46M36, as committed,
     has label `E46M35:' and filename E46M36.PLI -- E46M36.PLI line 1.)
  5. No line longer than 72 columns; DR truncates at 233 and an unterminated
     /* then swallows the rest of the file (commit 5de6b08's aborted run).
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", ".."))
OUT = os.path.join(ROOT, "probes")
MAXCOL = 72

PROBES = []


def probe(name, body, eol="crlf"):
    """`eol` is the line-ending mode.  Every probe in this bank is written
    strict-CRLF EXCEPT the protocol pair, which exists to settle what [C303]
    got wrong and declares its mode explicitly."""
    PROBES.append((name, body, eol))


# =============================================================== sub-phase A
# The bare FILE SKIP and FILE SKIP + LIST -- the two shapes E41X9 and E41X6
# refuse.  Both are carried by DR's CREATE (01AA-01BD and 01C1-01DF), but
# CREATE is a corpus program and can never be a specimen, so these probes
# re-measure the shapes in isolation.

probe("E46N1", """\
E46N1:
  procedure options(main);
  /* [E2E-42/P2c] THE BARE FILE SKIP, alone in an object.
     E41X9 refuses this today.  CREATE:41/45 spell it and
     DR carries it at 01AA-01BD: 12-byte named-file
     attach, MVI A,01, CALL ?SKPOP, CALL ?QIOOP.  20
     bytes, and NO item chain. */
  dcl outf file;
  open file(outf) stream output title('N1OUT DAT');
  put file(outf) skip;
  close file(outf);
end E46N1;
""")

probe("E46N2", """\
E46N2:
  procedure options(main);
  /* [E2E-42/P2c] FILE SKIP THEN ONE LITERAL.  CREATE:44 is
     this shape with 'EOF'; here with 'A' so the pool cell
     is one byte.  The question is ORDER: does DR attach
     the SKIP before the item chain (CREATE says yes) and
     is there one close for the whole statement? */
  dcl outf file;
  open file(outf) stream output title('N2OUT DAT');
  put file(outf) skip list('A');
  close file(outf);
end E46N2;
""")

probe("E46N3", """\
E46N3:
  procedure options(main);
  /* [E2E-42/P2c] FILE SKIP BEFORE A VARYING VARIABLE.
     A SKIP is a control item and a variable is an operand;
     [C293] says mixing the two classes has never been
     accepted on the named-file route, and this is the
     first time DR is asked directly. */
  dcl outf file, v char(20) varying;
  open file(outf) stream output title('N3OUT DAT');
  put file(outf) skip list(v);
  close file(outf);
end E46N3;
""")

probe("E46N4", """\
E46N4:
  procedure options(main);
  /* [E2E-42/P2c] FILE SKIP WITH A TWO-ITEM LIST.  P2b's H1
     was confirmed: one attach and one close per PUT
     STATEMENT.  This asks whether a control item changes
     that -- three chains under one attach would say no,
     two attaches would say yes. */
  dcl outf file;
  open file(outf) stream output title('N4OUT DAT');
  put file(outf) skip list('A','B');
  close file(outf);
end E46N4;
""")

probe("E46N5", """\
E46N5:
  procedure options(main);
  /* [E2E-42/P2c] TWO SUCCESSIVE BARE FILE SKIPs.  CREATE:41
     and 45 are this pair with work between them; here
     nothing is between, so a coalescing front end would
     show as one 20-byte block instead of two. */
  dcl outf file;
  open file(outf) stream output title('N5OUT DAT');
  put file(outf) skip;
  put file(outf) skip;
  close file(outf);
end E46N5;
""")

# ------------------------------------------------------- ordering contrasts

probe("E46N6", """\
E46N6:
  procedure options(main);
  /* [E2E-42/P2c] OUTPUT THEN SKIP, two statements.  Pairs
     with E46N7: the two must differ ONLY in the order of
     the two statement blocks. */
  dcl outf file;
  open file(outf) stream output title('N6OUT DAT');
  put file(outf) list('A');
  put file(outf) skip;
  close file(outf);
end E46N6;
""")

probe("E46N7", """\
E46N7:
  procedure options(main);
  /* [E2E-42/P2c] SKIP THEN OUTPUT, two statements -- the
     mirror of E46N6. */
  dcl outf file;
  open file(outf) stream output title('N7OUT DAT');
  put file(outf) skip;
  put file(outf) list('A');
  close file(outf);
end E46N7;
""")

# ------------------------------------------------------ routing (the bug)

probe("E46N8", """\
E46N8:
  procedure options(main);
  /* [E2E-42/P2c] THE ROUTING CONTRAST, INSIDE ONE OBJECT.
     A console `put skip;' (REVERSE:00FE, 17 bytes, ends
     in ?SYSPR) and a file `put file(outf) skip;'
     (CREATE:41, 20 bytes, ends in ?SIOOP then ?QIOOP) in
     the SAME program.  The current matcher takes its
     bare-control arm BEFORE it looks at the FILE option
     and tests the STREAM option first, so it sends the
     FILE one to ?SYSPR.  This object is the witness that
     says whether the implementation kept them apart: the
     console one must reach ?SYSPR and the file one must
     NOT. */
  dcl outf file;
  open file(outf) stream output title('N8OUT DAT');
  put skip;
  put file(outf) skip;
  close file(outf);
end E46N8;
""")

probe("E46N15", """\
E46N15:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME ROUTING.  Console text on either
     side of a FILE SKIP.  A misrouted skip shows up as an
     extra line break in the CONSOLE transcript and a
     missing one in the FILE -- a judgement on output, not
     on .REL bytes, and it cannot be satisfied by making
     CREATE byte-exact alone. */
  dcl outf file;
  open file(outf) stream output title('N15OUT DAT');
  put list('CON');
  put file(outf) list('A');
  put file(outf) skip;
  put file(outf) list('B');
  put list('AGAIN');
  close file(outf);
  stop;
end E46N15;
""")

# --------------------------------------------------- unmeasured controls

probe("E46N9", """\
E46N9:
  procedure options(main);
  /* [E2E-42/P2c] COUNTED FILE SKIP, literal count.  DR
     carries this behind a PRINT open this compiler
     refuses: COPYLPT:67 is 0295-02A6 = attach, MVI A,04,
     ?SKPOP, ?QIOOP, 20 bytes -- the BARE length with a
     different count byte.  Asked here behind a stream
     OUTPUT open. */
  dcl outf file;
  open file(outf) stream output title('N9OUT DAT');
  put file(outf) skip(2);
  close file(outf);
end E46N9;
""")

probe("E46N10", """\
E46N10:
  procedure options(main);
  /* [E2E-42/P2c] FILE PAGE.  COPYLPT:53 is 0215-0226 =
     attach, CALL ?PAGOP, CALL ?QIOOP, 18 bytes, behind a
     PRINT open.  ?PAGOP has never appeared in an object
     of mine on EITHER route.  P2c's perimeter says keep
     PAGE refused, so this probe records DR's verdict and
     the byte cost without claiming it. */
  dcl outf file;
  open file(outf) stream output title('N10OUT DAT');
  put file(outf) page;
  close file(outf);
end E46N10;
""")

probe("E46N18", """\
E46N18:
  procedure options(main);
  /* [E2E-42/P2c] FILE SKIP WITH AN EXPRESSION COUNT.
     COPYLPT:81 `skip(spaces)' is 030C-0321 = attach,
     LHLD, MOV A,L, ?SKPOP, ?QIOOP -- 22 bytes, two more
     than the literal form. */
  dcl outf file, n fixed bin;
  n = 3;
  open file(outf) stream output title('N18OUT DAT');
  put file(outf) skip(n);
  close file(outf);
end E46N18;
""")

# ---------------------------------------------------------------- runtimes
# Every runtime probe CLOSEs the file; [C279] measured that E16D's close
# flushes, and a missing close is an undefined destination, not a probe.
# E46N11/E46N16 are a PAIR whose only difference is the SKIP statement, so
# the two exported files' difference IS the bytes a FILE SKIP writes -- no
# assumption about CR, LF or record padding is needed to read the answer.

probe("E46N11", """\
E46N11:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME: BARE SKIP BETWEEN TWO ITEMS,
     as three statements.  Control E46N16 writes the same
     two items with NO skip. */
  dcl outf file;
  open file(outf) stream output title('N11OUT DAT');
  put file(outf) list('A');
  put file(outf) skip;
  put file(outf) list('B');
  close file(outf);
  stop;
end E46N11;
""")

probe("E46N16", """\
E46N16:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME CONTROL: E46N11 with the SKIP
     STATEMENT REMOVED and nothing else changed.  [C295]
     and [C299] predict its payload exactly: each item is
     apostrophe-quoted, items take one blank between them
     across statement boundaries, and a PUT never
     terminates its line -- so `'A' 'B'` is 7 bytes. */
  dcl outf file;
  open file(outf) stream output title('N16OUT DAT');
  put file(outf) list('A');
  put file(outf) list('B');
  close file(outf);
  stop;
end E46N16;
""")

probe("E46N12", """\
E46N12:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME: BARE SKIP BEFORE ANY OUTPUT.
     Does a file skip advance from the CURRENT position or
     from the start of a record that has nothing written
     in it yet?  E46N11 answers the other half. */
  dcl outf file;
  open file(outf) stream output title('N12OUT DAT');
  put file(outf) skip;
  put file(outf) list('A');
  close file(outf);
  stop;
end E46N12;
""")

probe("E46N13", """\
E46N13:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME: FILE SKIP WITH A LIST, spelled
     exactly as CREATE:44 spells it.  The item follows the
     skip INSIDE one statement, so the question is whether
     the skip's bytes come before the item's text. */
  dcl outf file;
  open file(outf) stream output title('N13OUT DAT');
  put file(outf) skip list('EOF');
  close file(outf);
  stop;
end E46N13;
""")

probe("E46N14", """\
E46N14:
  procedure options(main);
  /* [E2E-42/P2c] RUNTIME: THREE SUCCESSIVE BARE FILE
     SKIPs between two items.  E46N11 has one; three minus
     one, divided by two, is the bytes of one skip even if
     a skip is not a fixed length. */
  dcl outf file;
  open file(outf) stream output title('N14OUT DAT');
  put file(outf) list('A');
  put file(outf) skip;
  put file(outf) skip;
  put file(outf) skip;
  put file(outf) list('B');
  close file(outf);
  stop;
end E46N14;
""")

# ------------------------------------------- the four controls P2c refuses
# Mission: "one negative each for FILE PAGE, FILE LINE, FILE AFTER, and FILE
# BEFORE".  PAGE is E46N10.  These three are asked of DR anyway -- DR's
# verdict is what makes a refusal OUR perimeter rather than an untested gap.
# AFTER and BEFORE are the interesting ones: they die in the PARSER today
# (`PUT: expected LIST/EDIT/ITEM/FROM'), one stage EARLIER than a codegen
# refusal, so they are a different kind of negative and must be recorded as
# such.

probe("E46N21", """\
E46N21:
  procedure options(main);
  /* [E2E-42/P2c] NEGATIVE: FILE LINE.  `ctl_keys' is
     SKIP/PAGE/LINE (parser.ml:134), so LINE parses as a
     control item and `file_items' refuses it by class and
     position.  Nothing of mine, and nothing in the corpus,
     measures what DR emits for it behind a stream-output
     attach -- COPYLPT's LINE uses are GET, not PUT, and
     are on a printer file. */
  dcl outf file;
  open file(outf) stream output title('N21OUT DAT');
  put file(outf) line(2) list('A');
  close file(outf);
end E46N21;
""")

probe("E46N22", """\
E46N22:
  procedure options(main);
  /* [E2E-42/P2c] NEGATIVE: FILE AFTER.  This does not
     reach codegen at all -- `AFTER' is not in the PUT
     option keys, so the parser stops at `PUT: expected
     LIST/EDIT/ITEM/FROM'.  A PARSE negative, not a
     lowering negative; if DR accepts it, the gap is
     ours at a different stage. */
  dcl outf file;
  open file(outf) stream output title('N22OUT DAT');
  put file(outf) after(2) list('A');
  close file(outf);
end E46N22;
""")

probe("E46N23", """\
E46N23:
  procedure options(main);
  /* [E2E-42/P2c] NEGATIVE: FILE BEFORE.  The mirror of
     E46N22. */
  dcl outf file;
  open file(outf) stream output title('N23OUT DAT');
  put file(outf) before(2) list('A');
  close file(outf);
end E46N23;
""")

# ------------------------------------------------ the [C303] protocol pair
# Two probes, byte-identical sources except for line endings, asked of DR in
# the same session.  [C303] says "DR refuses LF outright", but the probe the
# SAME episode records as ACCEPTED (E46M33, golden/e42p2b5) has 8 bare-LF
# body lines and DR listed all nine lines with correct numbers; the one that
# died of UNEXPECTED EOF (E46M36) is the one whose LAST line has no CR
# before the ^Z.  These two say which of the two variables matters.

probe("E46N19", """\
E46N19:
  procedure options(main);
  /* [E2E-42/P2c] PROTOCOL CONTROL.  Strict CRLF on every
     line including the last, then 0x1A.  E46N20 is this
     same program with the CRs removed and NOTHING else
     changed -- not even the title length, so a successful
     E46N20 must have identical CODE and DATA. */
  dcl outf file, v char(10) varying;
  v = 'DELTA';
  open file(outf) stream output title('N19OUT DAT');
  put file(outf) list(v);
  close file(outf);
end E46N19;
""")

probe("E46N20", """\
E46N20:
  procedure options(main);
  /* [E2E-42/P2c] PROTOCOL DISCRIMINATOR, and the
     deliberately malformed one -- this probe is written
     with a bare LF at the end of EVERY line INCLUDING the
     last, then 0x1A, which is exactly the shape of
     E46M36.  If DR refuses it while accepting E46N19,
     bare LF anywhere is fatal and [C303] stands.  If DR
     accepts it, then what killed E46M36 was the missing
     CR on the LAST line, and [C303]'s wording is wrong. */
  dcl outf file, v char(10) varying;
  v = 'DELTA';
  open file(outf) stream output title('N19OUT DAT');
  put file(outf) list(v);
  close file(outf);
end E46N20;
""", eol="lf")

# ---------------------------------------------------- CREATE integration

probe("E46N17", """\
E46N17:
  procedure options(main);
  /* [E2E-42/P2c] CREATE's OWN TAIL, spelled out.  Line 39
     is the six-item list P2b lowered ([C296]); 41, 44 and
     45 are the three SKIP statements P2c needs.  CREATE
     opens with a VARIABLE title, which is why a corpus
     program cannot be a specimen; here the title is a
     literal and the record layout is CREATE's, so this
     object is the byte witness for CREATE:39-45 without
     needing CREATE's own bytes. */
  dcl outf file;
  dcl name char(30) varying, addr char(30) varying,
        city char(20) varying, state char(10) varying,
        zip  fixed dec(6), phone char(12) varying;
  open file(outf) stream output title('N17OUT DAT');
  /* the title length is 10, matching the model's DATA */
  put file(outf) list(name,addr,city,state,zip,phone);
  put file(outf) skip;
  put file(outf) skip list('EOF');
  put file(outf) skip;
  close file(outf);
end E46N17;
""")


def check():
    bad = []
    for name, body, _eol in PROBES:
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
        if not lines or lines[0] != name + ":":
            bad.append("%s: line 1 must be `%s:', found %r"
                       % (name, name, lines[0] if lines else None))
        if not lines[-1].strip().startswith("end %s;" % name):
            bad.append("%s: last line must be `end %s;'" % (name, name))
        if not re.match(r"^end [A-Z][A-Z0-9]*;$", lines[-1].strip()):
            bad.append("%s: terminator must be `end <name>;' exactly" % name)
        if _eol not in ("crlf", "lf"):
            bad.append("%s: unknown eol mode %r" % (name, _eol))
    dupes = set()
    seen = set()
    for n, _b, _e in PROBES:
        if n in seen:
            dupes.add(n)
        seen.add(n)
    if dupes:
        bad.append("duplicate probe names: %s" % sorted(dupes))
    return bad


def main():
    bad = check()
    if bad:
        for b in bad:
            print("REFUSED: " + b, file=sys.stderr)
        return 1
    written = []
    for name, body, eol in sorted(PROBES):
        text = body.rstrip("\n")
        if eol == "crlf":
            # STRICT CRLF on every line INCLUDING THE LAST, then 0x1A.
            data = text.replace("\n", "\r\n").encode("ascii") + b"\r\n\x1a"
        else:
            # bare LF everywhere INCLUDING the last line before the 0x1A.
            data = text.encode("ascii") + b"\n\x1a"
        path = os.path.join(OUT, name + ".PLI")
        with open(path, "wb") as f:
            f.write(data)
        if eol == "crlf":
            assert data.count(b"\n") == data.count(b"\r\n")
        written.append((name, len(data)))
    for n, sz in written:
        print("wrote probes/%s.PLI (%d bytes)" % (n, sz))
    print("%d probes, all strict-CRLF + 0x1A, all <= %d columns"
          % (len(written), MAXCOL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
