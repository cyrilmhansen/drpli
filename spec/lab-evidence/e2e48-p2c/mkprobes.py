#!/usr/bin/env python3
"""E2E-48/P2c probe generator (round 3 of the E48 bank, E48C1..E48C9).

Writes probes/E48Cn.PLI with CRLF terminators -- [C193] (b): DR answers an
LF-only source with UNEXPECTED EOF on every file, so this generator, like
mkprobes.py/mkprobes2.py of rounds 1 and 2, joins lines with crlf.

Run from the repo root:  python3 spec/lab-evidence/e2e48-p2c/mkprobes.py
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E48C{n}:
  procedure options(main);
  /* [E2E-48/P2c] {note} */
"""

TAIL = """  put list('B=', b);
  stop;
end E48C{n};
"""

DECL_B = "  dcl b bit(1) static initial('0'b);\n"
REC = "  dcl\n    1 rec,\n      2 name character(30) varying;\n"
FLAT = "  dcl name char(30) varying;\n"

# name: (note, decls, stmts, tail_override)
PROBES_SRC = {
    1: ("THE CONTROL of this bank: the flat-cell SCVCM store re-measured "
        "inside the E48C battery.  P1 predicts it keeps E48A6 0013's 17-byte "
        "`LXI H,lit / LXI D,var' so every other row here differs by ONE axis.",
        DECL_B + FLAT,
        "  name = 'AB';\n  b = (name = 'EOF');\n", None),
    2: ("THE DISCRIMINATOR, member side: `b = (rec.name = 'EOF')' on an "
        "INTERNAL automatic record.  CREATE 008F spells its member store "
        "18 bytes `LXI H,var / XCHG / LXI H,lit'; E48A6/A12 spell the flat "
        "cell 17 bytes `LXI H,lit / LXI D,var'.  If operand class (member "
        "vs flat) is the discriminator, this object carries CREATE's form.",
        REC + DECL_B,
        "  rec.name = 'AB';\n  b = (rec.name = 'EOF');\n", None),
    3: ("THE SAME statement spelled UNQUALIFIED, exactly CREATE:34.  If "
        "qualification is a front-end matter the store bytes are identical "
        "to E48C2's; a different spelling here would mean the two resolve "
        "to different operand classes.",
        REC + DECL_B,
        "  name = 'AB';\n  b = (name = 'EOF');\n", None),
    4: ("THE MEMBER STORE IN CREATE'S CONTEXT, a `do while(^b)' body -- "
        "exactly E48A12's loop with the member taking `name''s place.  "
        "E48A12 proved a flat cell keeps the 17-byte form inside a loop; "
        "if this object carries the 18-byte XCHG form, position is NOT "
        "the discriminator and class is.",
        REC + DECL_B + "  dcl n fixed bin(15);\n",
        "  n = 0;\n"
        "  do while(^b);\n"
        "     n = n + 1;\n"
        "     name = 'AB';\n"
        "     b = (name = 'EOF');\n"
        "     if n = 4 then b = '1'b;\n"
        "  end;\n",
        "  put list('N=', n);\n  stop;\nend E48C4;\n"),
    5: ("THE ORIENTATION, flat: `b = ('EOF' = name)'.  [C191] pins "
        "literal-on-the-left as a DIFFERENT helper with a DIFFERENT length "
        "register (?SCCVM, MVI B,len).  P5 predicts the store route follows "
        "the E29C9 TEST-route shape: LXI H,var / LXI D,lit / MVI B,n / "
        "?SCCVM, then the [C095] flag trick and STA.",
        DECL_B + FLAT,
        "  name = 'AB';\n  b = ('EOF' = name);\n", None),
    6: ("THE ORIENTATION, member: `b = ('EOF' = rec.name)'.  [C191]: "
        "`literal = member' needs NO XCHG because HL is already the right "
        "operand (E29C9 001C: LHLD / LXI D,*S / MVI B / ?SCCVM).  On an "
        "automatic member the address materializes directly, so P6 "
        "predicts LXI H,*D(rec) / LXI D,*S / MVI B,03 / ?SCCVM -- 16 "
        "bytes, the mirror of P5 plus the member cell.",
        REC + DECL_B,
        "  rec.name = 'AB';\n  b = ('EOF' = rec.name);\n", None),
    7: ("THE STATIC-LEAK LAYOUT QUESTION: a flat CHARACTER STATIC declared "
        "BEFORE an automatic record.  My binder propagates a level-0 "
        "storage class INTO every later structure unless the structure "
        "names one -- manual 6.2 speaks of structure LEVELS, and DR's own "
        "MPMCALLB declares `upper/lower static' at lines 48-50 and an "
        "automatic `1 cpb' at 166 and compiles.  This object measures "
        "where DR actually PLACES rec: automatic (above the pool, [C114]) "
        "or static (below it).  The store inside is P2's member shape.",
        "  dcl s char(3) static initial('AB');\n" + DECL_B + REC,
        "  rec.name = 'AB';\n  b = (rec.name = 'EOF');\n"
        "  put list('S=', s);\n", None),
    8: ("THE EXPLICIT STATIC VARYING CELLS: `dcl nm char(14) varying "
        "static initial('AB')' -- the attribute spelling of E46F5, EXPR2, "
        "FSCAN and LOAN2, which DR compiled (all four corpus witnesses "
        "are AUTHENTIC) but which no probe has ever put through a "
        "COMPARE.  P8 predicts DR accepts, lays the varying cell below "
        "the pool [C114], and that a flat static cell keeps the "
        "immediate-address 17-byte SCVCM form (its address, like a flat "
        "auto's, needs no load).",
        DECL_B + "  dcl nm char(14) varying static initial('AB');\n",
        "  b = (nm = 'EOF');\n  put list(nm);\n", None),
    9: ("THE MEMBER COMPARE IN TEST POSITION: `if rec.name = 'EOF' then'. "
        "The store battery cannot show the skip byte; E29C4 001C pins "
        "the BASED member test as LHLD / XCHG / LXI H,*S / MVI A / ?SCVCM "
        "/ JNZ, and [C191] pins `=' as C2.  P9 predicts the automatic "
        "member test is the same head with LXI H,*D for the member.",
        REC + DECL_B,
        "  rec.name = 'AB';\n  if rec.name = 'EOF' then b = '1'b;\n", None),
}


def src(n):
    note, decls, stmts, tail = PROBES_SRC[n]
    wrapped = "\n".join(textwrap.wrap(note, 66))
    s = HDR.format(n=n, note=wrapped) + decls + stmts + (tail or TAIL.format(n=n))
    return s.replace("\n", "\r\n")


def main():
    for n in sorted(PROBES_SRC):
        path = os.path.join(PROBES, "E48C%d.PLI" % n)
        with open(path, "wb") as f:
            f.write(src(n).encode("ascii"))
        print("wrote", path, len(src(n)) + src(n).count("\n"), "bytes (crlf)")


if __name__ == "__main__":
    main()
