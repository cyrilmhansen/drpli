#!/usr/bin/env python3
"""E2E-48/P2d probe generator (round 4 of the E48 bank, E48D1..E48D10).

Writes probes/E48Dn.PLI with CRLF terminators -- [C193] (b): DR answers an LF-only
source with UNEXPECTED EOF on every file, so this generator, like mkprobes.py /
mkprobes2.py / mkprobes.py of rounds 1-3, joins lines with crlf.

Run from the repo root:  python3 spec/lab-evidence/e2e48-p2d/mkprobes.py

Every probe attacks ONE recorded [TBD] of [C310] [C313] [C317] [C319] (the
spec/lab-evidence/e2e48-p2c/RESULTS.md section 3 list), and every prediction in
HYPOTHESES.md is derived from a committed DR object, never from memory.
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E48D{n}:
  procedure options(main);
{comment}"""

DECL_B = "  dcl b bit(1) static initial('0'b);\n"


def wrapped_comment(note, width=71):
    """DR truncates source lines past column 72 (e2e42-p2b RESULTS s6; re-measured
    by the botched first P2d run, golden/e48p2d: a 179..317-column single-line
    comment lost its '*/' and each probe died UNEXPECTED EOF).  Emit the purpose
    comment as multiple lines, every one <= 71 columns, E48C1's style."""
    segs = textwrap.wrap("[E2E-48/P2d] " + note, width=width - 9)
    lines = []
    for i, seg in enumerate(segs):
        if i == 0:
            lines.append("  /* " + seg)
        elif i == len(segs) - 1:
            lines.append("     " + seg + " */")
        else:
            lines.append("     " + seg)
    if len(segs) == 1:
        lines = ["  /* " + segs[0] + " */"]
    assert max(len(x) for x in lines) <= width, lines
    return "\n".join(lines) + "\n"


def probe(n, note, decls, body, tail):
    return (HDR.format(n=n, comment=wrapped_comment(note))
            + decls + body + tail).replace("\n", "\r\n")


P = {}

# ---- TITLE route: does the storage class of a VARIABLE title operand change any byte?
P[1] = probe(
    1,
    "static CHARACTER VARYING as an OPEN TITLE operand, OUTPUT side -- E46F5's own "
    "shape, re-measured with a distinct module name so the object is a fresh witness.",
    "  dcl outf file,\n"
    "      nm char(14) varying static initial('AB'),\n"
    "      k fixed bin(15);\n",
    "  open file(outf) stream output title(nm);\n"
    "  put file(outf) list('X');\n"
    "  close file(outf);\n",
    "  stop;\nend E48D1;\n",
)

P[2] = probe(
    2,
    "the SAME operand on the INPUT side -- [C288] measured option/operand "
    "orthogonality on AUTOMATIC cells (E46F1 output vs E46F3 input); this asks whether a "
    "STATIC cell is class-invariant on the input side too.",
    "  dcl inf file,\n"
    "      nm char(14) varying static initial('AB'),\n"
    "      k fixed bin(15);\n",
    "  open file(inf) stream input title(nm);\n"
    "  get file(inf) list(k);\n"
    "  close file(inf);\n",
    "  stop;\nend E48D2;\n",
)

P[3] = probe(
    3,
    "STATIC on CHARACTER (FIXED) as an OPEN TITLE operand -- E46F2 is the automatic "
    "fixed witness (the LXI H / MVI A,08 / ?SLCTS sequence); does DR pass the DECLARED length here "
    "too, and place the initialised cell in the static zone?",
    "  dcl outf file,\n"
    "      nm char(8) static initial('AB'),\n"
    "      k fixed bin(15);\n",
    "  open file(outf) stream output title(nm);\n"
    "  put file(outf) list('X');\n"
    "  close file(outf);\n",
    "  stop;\nend E48D3;\n",
)

# ---- the EMPTY static INITIAL (EXPR2's and FSCAN's blocker)
P[4] = probe(
    4,
    "the EMPTY literal on a STATIC CHARACTER VARYING.  EXPR2's own DR object puts a zero length "
    "byte plus ten blank bytes at DATA 000F for char(10); this isolates the cell and the PUT read "
    "of it in a whole file I can compare.",
    "  dcl s char(10) varying static initial(''),\n"
    "      k fixed bin(15);\n",
    "  put list('S=', s);\n",
    "  stop;\nend E48D4;\n",
)

P[5] = probe(
    5,
    "EMPTY literal on a STATIC CHARACTER (FIXED) -- the corpus witnesses (EXPR2:19, "
    "FSCAN:12/19) are all VARYING, so the fixed empty cell is unmeasured: five blanks, "
    "or a zero-length cell?",
    "  dcl s char(5) static initial(''),\n"
    "      k fixed bin(15);\n",
    "  put list('S=', s);\n",
    "  stop;\nend E48D5;\n",
)

# ---- store INTO a static cell (the other half of [C319]'s [TBD])
P[6] = probe(
    6,
    "STORE INTO a static CHARACTER (fixed): a two-character literal stored into a three-character "
    "static cell that already carries an initialiser.  "
    "My automatic route pools the source literal (scratch s1 grew DATA 3 -> 5); does DR pool "
    "again beside an already-initialised static cell, or copy into it?",
    DECL_B + "  dcl s char(3) static initial('AB');\n",
    "  s = 'CD';\n"
    "  put list('S=', s);\n",
    "  stop;\nend E48D6;\n",
)

P[7] = probe(
    7,
    "STORE INTO a static CHARACTER VARYING: does DR rewrite the LEADING LENGTH BYTE (E48C8 "
    "pins the cell as the two-length-byte cell measured by E48C8, which used a NON-EMPTY initial only, and does the pool grow?",
    DECL_B + "  dcl s char(10) varying static initial('AB');\n",
    "  s = 'CDE';\n"
    "  put list('S=', s);\n",
    "  stop;\nend E48D7;\n",
)

# ---- the biased-compare materialiser in a STORE (|c| in {1,2,3})
P[8] = probe(
    8,
    "the biased integer compare materialiser with |c| in 2 and 3 in a STORE -- [C310] pins only c = 0 "
    "and |c| >= 4 there, while the TEST route [C143] switches to `DCX H x c' at |c| <= 3 "
    "(E48A13 = 3 vs E48A12 = 4). Two targets, so each site is addressable.",
    DECL_B + "  dcl c bit(1) static initial('0'b),\n"
    "      k fixed bin(15);\n",
    "  b = (k = 2);\n"
    "  c = (k = 3);\n"
    "  put list('B=', b, 'C=', c);\n",
    "  stop;\nend E48D8;\n",
)

# ---- a BIT(1) item that is NOT final, and the value form of '0'b
P[9] = probe(
    9,
    "a BIT(1) PUT item that is NOT the final item -- all nine sites of [C313] are final, so "
    "the tail question (the bit tail replacing the shared literal tail, and then what follows) is unmeasured.",
    DECL_B + "  dcl k fixed bin(15);\n",
    "  put list(b, 'X');\n",
    "  stop;\nend E48D9;\n",
)

P[10] = probe(
    10,
    "an internal CHARACTER VARYING member as the RIGHT operand of a TEST compare -- [C318] "
    "measures member-LEFT in TEST and [C317] measures literal-LEFT in a STORE; TEST with the "
    "member on the right is the same orientation, unmeasured there.",
    "  dcl\n"
    "    1 rec,\n"
    "      2 line char(14) varying,\n"
    "      2 nxt fixed bin(15);\n"
    "  dcl k fixed bin(15);\n",
    "  rec.line = 'AB';\n"
    "  if 'AB' = line then k = 1;\n",
    "  put list('K=', k);\n"
    "  stop;\nend E48D10;\n",
)


def main():
    for n, text in sorted(P.items()):
        path = os.path.join(PROBES, "E48D%d.PLI" % n)
        with open(path, "wb") as fh:
            fh.write(text.encode() + b"\x1a")
        print("wrote %s (%d bytes)" % (path, len(text) + 1))


if __name__ == "__main__":
    main()
