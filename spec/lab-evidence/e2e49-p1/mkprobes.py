#!/usr/bin/env python3
"""E2E-49/P1 probe generator (operand-INVERTED FIXED-character compares, E49A1..E49A4).

Writes probes/E49An.PLI with CRLF terminators plus the ^Z byte -- [C193] (b): DR answers
an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is <= 71 columns:
the measured law that killed P2d run 1 (spec/lab-evidence/e2e48-p2d/RESULTS.md s0).

Run from the repo root:  python3 spec/lab-evidence/e2e49-p1/mkprobes.py

The round attacks the ONE open reading of golden/e48p2e/E48E7/E48E7.REL ([C330]): in
`if 'AB' = rec.name then' HL carries the member and DE the pool literal, so [C191]'s
"HL = RIGHT operand" law and C326's "LXI H is ALWAYS the internal cell" wording and
C330's capacity-in-A/length-in-B polarity reading were ALL indistinguishable -- the
member was both the right operand AND the internal cell.  Writing the SAME compare with
the member on the LEFT separates them; RESULTS s3 and the claim [C330] itself name this
shape as unmeasured ("?SCCCM ... with the member on the LEFT: no object").

Scope discipline (operator ruling 2026-10-31): TEST conditions ONLY, CHARACTER FIXED,
NON-BASED, level-numbered internal members.  STOREs, BASED members, member-vs-member,
literal-vs-literal and truthiness of a fixed member stay OUT and keep refusing.
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E49A{n}:
  procedure options(main);
{comment}"""

# The record and scalar of golden/e48p2e/E48E7, verbatim ([C330]'s object):
# a level-numbered FIXED CHARACTER member `name char(3)' and a plain k.
DECL = "  dcl\n" \
       "    1 rec,\n" \
       "      2 name char(3),\n" \
       "      2 nxt fixed bin(15);\n" \
       "  dcl k fixed bin(15);\n"

TAIL = "  put list('K=', k);\n"


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns."""
    segs = textwrap.wrap("[E2E-49/P1] " + note, width=width - 9)
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
            + DECL + body + TAIL + "  stop;\nend E49A%d;\n" % n).replace("\n", "\r\n")


P = {}

# ---- the inversion itself: the member LEFT of the literal, same compare as E48E7
P[1] = probe(
    1,
    "operand inversion of golden/e48p2e/E48E7 [C330].  That object's single reading is "
    "ambiguous: HL carried the member, which was BOTH the right operand ([C191]'s "
    "\"HL = right\") and the internal cell ([C326]'s wording), and A carried the extent "
    "while B carried the literal length, class- and position-readings alike.  Here the "
    "member is written on the LEFT; [C330] itself names \"the FIXED member on the LEFT "
    "of a TEST\" as having no object.",
    "  if rec.name = 'AB' then k = 1;\n",
)

# ---- the same inverted compare with the BARE spelling of the member
P[2] = probe(
    2,
    "the inverted compare under the BARE member spelling: [C253]/[C258] fold `name' and "
    "`rec.name' to ONE cell, and [C318]'s corroboration (E46K3, golden/e48p2retire) "
    "proved spelling-invariance for a VARYING member in TEST; the FIXED spelling in a "
    "compare has NEVER been sampled bare -- my str_side admits only the qualified form "
    "(orig <> m.name).",
    "  if name = 'AB' then k = 1;\n",
)

# ---- the inverted compare with ^= : the CA skip byte in the FIXED family
P[3] = probe(
    3,
    "the inverted compare with ^=.  [C072] pins DR's ^= skip byte as CA in every sampled "
    "family, and arm 4 lowered the FIXED TEST ^= as a [C072] SYNTHESIS: E48E7 measured "
    "C2 only, and C330 says so.  This probe measures the CA byte in the ?SCCCM family "
    "itself, with the member on the left.",
    "  if rec.name ^= 'AB' then k = 1;\n",
)

# ---- the inverted compare with a literal LONGER than the extent
P[4] = probe(
    4,
    "the inverted compare with an OVER-EXTENT literal, 'ABCD' against char(3).  No "
    "object anywhere compares a fixed member with a longer literal: str_cmp_shape_fix's "
    "own comment records DR's verdict as [TBD] (not gated, matching the varying family's "
    "ungated MVI len arms), and [C191]'s truncation witness (E30T1, len 8 / cap 6) is a "
    "STORE.  This is a VERDICT question first: accept gives 06 04 / 3E 03 in the form "
    "this round selects; refuse makes it dr-refuses law.",
    "  if rec.name = 'ABCD' then k = 1;\n",
)


def main():
    for n, text in sorted(P.items()):
        path = os.path.join(PROBES, "E49A%d.PLI" % n)
        with open(path, "wb") as fh:
            fh.write(text.encode() + b"\x1a")
        print("wrote %s (%d bytes, maxcol %d)"
              % (path, len(text) + 1, max(len(x) for x in text.split("\r\n"))))


if __name__ == "__main__":
    main()
