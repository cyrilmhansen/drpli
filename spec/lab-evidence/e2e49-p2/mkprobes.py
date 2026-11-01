#!/usr/bin/env python3
"""E2E-49/P2 probe generator (MEMBER-vs-MEMBER FIXED-character compares in TEST, E49B1..E49B5).

Writes probes/E49Bn.PLI with CRLF terminators plus the ^Z byte -- [C193] (b): DR answers
an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is <= 71 columns:
the measured law that killed P2d run 1 (spec/lab-evidence/e2e48-p2d/RESULTS.md s0).

Run from the repo root:  python3 spec/lab-evidence/e2e49-p2/mkprobes.py

The round attacks the shape BOTH prior rounds named as having no object: a FIXED
CHARACTER member compared with ANOTHER FIXED CHARACTER member in TEST
(`golden/e48p2e/E48E7' RESULTS s3; `golden/e49p1' RESULTS s3; [C330]/[C333] "what this
does NOT license").  Every fixed compare object so far has exactly ONE internal member
and ONE pooled literal, so two laws recorded for the fixed family COINCIDE on all five
objects and cannot be separated:

  - [C333]'s staging law: the member is loaded FIRST into HL and staged through XCHG
    into DE when it is the LEFT operand (E49A1/A2/A3/A4);
  - [C191]'s final law: HL ENDS on the RIGHT operand, DE on the LEFT -- and the
    varying cell-vs-cell witness [E29C6] shows DR materializing BOTH addresses
    directly in that orientation (`LXI H,<right> / LXI D,<left>', no XCHG).

With TWO member operands both laws are satisfiable by TWO different byte sequences:
Form S `21 *D(right) / 11 *D(left)' (direct, 16 bytes, CODE 65 like E48E7) versus Form
M `21 *D(left) / EB / 21 *D(right)' (staged, 17 bytes, CODE 66 like E49A1).  The equal-
length pair E49B1/E49B2 (operands INVERTED) separates them on one byte: EB.  The
unequal-length pair E49B3/E49B4 re-tests [C334]'s POSITIONAL length law (B = the LEFT
operand's attribute, A = the RIGHT's) on an operand pair where BOTH attributes are
declared extents -- a law never measured there.  E49B5 measures the `^=' skip byte in
the member-vs-member head.

Scope discipline (operator ruling 2026-11-01): TEST conditions ONLY, CHARACTER FIXED,
NON-BASED, level-numbered internal members, QUALIFIED spellings ONLY (bare is not
measured by this round and its P1 gate asymmetry stands).  STOREs, BASED members,
literal-vs-literal, truthiness, bare spellings and `^( ... )' composition stay OUT and
keep refusing.
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E49B{n}:
  procedure options(main);
{comment}"""

# One record, THREE fixed CHARACTER members (two of length 3, one of length 2) plus
# the plain k and the measured `put list' tail -- the E49A/E48E7 template, kept so the
# skip fill ([C309]) and the [C314] pool-first DATA layout stay comparable across objects.
DECL = "  dcl\n" \
       "    1 rec,\n" \
       "      2 na char(3),\n" \
       "      2 nb char(3),\n" \
       "      2 s2 char(2);\n" \
       "  dcl k fixed bin(15);\n"

TAIL = "  put list('K=', k);\n"


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns."""
    segs = textwrap.wrap("[E2E-49/P2] " + note, width=width - 9)
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


def probe(n, note, body):
    return (HDR.format(n=n, comment=wrapped_comment(note))
            + DECL + body + TAIL + "  stop;\nend E49B%d;\n" % n).replace("\n", "\r\n")


P = {}

# ---- the member-vs-member compare itself, EQUAL lengths: the Form S / Form M
# ---- discriminator (one byte: EB) between the two coinciding laws.
P[1] = probe(
    1,
    "a FIXED member compared with ANOTHER FIXED member, equal extents, QUALIFIED both "
    "sides.  [C330] s3 and [C333] s3 name member-vs-member as NO OBJECT; E49A1 staged "
    "its member-left cell through EB and E48E7 loaded its member-right cell straight "
    "into HL, so the recorded laws CANNOT predict this head -- Form S `21 *D(nb) / "
    "11 *D(na)' versus Form M `21 *D(na) / EB / 21 *D(nb)' both end HL on the right "
    "([C191]).  EB here or not is the measured answer.",
    "  if rec.na = rec.nb then k = 1;\n",
)

# ---- the inverted pair: the same compare with the operands swapped.
P[2] = probe(
    2,
    "the member-vs-member compare with the operands INVERTED (E49B1 reversed).  Under "
    "either accepted form this object must equal E49B1 with the two member-cell "
    "relocations swapped in their slots -- if instead B1 and B2 come out byte-identical, "
    "the encoding does NOT follow the written side and [C334]'s positional law breaks "
    "for member pairs.",
    "  if rec.nb = rec.na then k = 1;\n",
)

# ---- unequal extents, longer LEFT: [C334]'s positional law on an all-member pair.
P[3] = probe(
    3,
    "member-vs-member with UNEQUAL extents, the LONGER one on the LEFT: char(3) vs "
    "char(2).  [C334]'s positional law (B = LEFT operand's attribute, A = RIGHT's) was "
    "measured only on member-vs-literal pairs; here both attributes are DECLARED "
    "extents, so the pair predicts `06 03 / 3E 02'.  Falsifiers: `06 02 / 3E 03' "
    "(side-inverted), `06 02 / 3E 02' (min), `06 03 / 3E 03' (max), refusal.",
    "  if rec.na = rec.s2 then k = 1;\n",
)

# ---- unequal extents, shorter LEFT: the inversion of E49B3.
P[4] = probe(
    4,
    "the INVERSION of E49B3: char(2) on the LEFT, char(3) on the RIGHT.  The positional "
    "law predicts the length pair SWAPPED with the operands (`06 02 / 3E 03'); a pair "
    "identical to E49B3's instead would show the lengths keyed by CLASS (e.g. shorter-"
    "in-B) and re-open [C330]'s falsified polarity reading for member pairs.",
    "  if rec.s2 = rec.na then k = 1;\n",
)

# ---- ^= on the member-vs-member head: the CA skip byte in this orientation.
P[5] = probe(
    5,
    "the member-vs-member compare with ^=.  [C333] measured the CA skip byte in the "
    "?SCCCM family only member-vs-LITERAL (E49A3); [C072] says CA everywhere.  This "
    "measures the skip byte on a member-vs-member head -- same head as E49B1's winner, "
    "skip 0xca, fill = the next statement ([C309]).",
    "  if rec.na ^= rec.nb then k = 1;\n",
)


def main():
    for n, text in sorted(P.items()):
        path = os.path.join(PROBES, "E49B%d.PLI" % n)
        with open(path, "wb") as fh:
            fh.write(text.encode() + b"\x1a")
        print("wrote %s (%d bytes, maxcol %d)"
              % (path, len(text) + 1, max(len(x) for x in text.split("\r\n"))))


if __name__ == "__main__":
    main()
