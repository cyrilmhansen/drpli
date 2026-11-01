#!/usr/bin/env python3
"""E2E-49/P3 probe generator (COMPOSITE campaign: equal-length member-vs-literal,
member QUALIFICATION, literal-LEFT over-extent, ORDERED RELATIONS -- E49C1..C4,
E49D1..D4, E49E1..E2, E49F1..F4).

Writes probes/E49*.PLI with CRLF terminators plus the ^Z byte -- [C193] (b): DR answers
an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is <= 71
columns: the measured law that killed P2d run 1 (spec/lab-evidence/e2e48-p2d/RESULTS.md s0).

Run from the repo root:  python3 spec/lab-evidence/e2e49-p3/mkprobes.py

Four panels, ONE bank, per the operator authorization of 2026-11-01:

  A  E49C1..C4  -- member-vs-LITERAL compare where the literal length EQUALS the
      declared extent (char(3) vs 'ABC'), BOTH orientations, = and ^=.  Settles the
      [TBD] of [C338]: the equal-extent collapse `06 n / 78' is measured
      member-vs-member ONLY; every fixed member-vs-literal object so far (E48E7 2/3,
      E49A1/A3 3/2, E49A4 3/4) carried TWO immediates because the lengths were never
      equal.  The two orientations are decided INDEPENDENTLY -- no shared rule is
      presupposed.

  B  E49D1..D4  -- member QUALIFICATION in a member-vs-member pair: bare/qualified,
      qualified/bare, bare/bare, plus the BARE fixed member to the RIGHT of a literal
      ('AB' = na), the P1 asymmetry (E49A2 proved bare admitted LEFT-of-literal,
      [C335]; E48E7's literal-left route has only ever been sampled qualified).
      Compared against goldens/e49p2/E49B1 (mm) and goldens/e48p2e/E48E7 +
      goldens/e49p1/E49A2 (literal pairs) to isolate the effect of the WRITTEN name.

  C  E49E1..E2  -- literal LONGER than the member's extent, literal written on the
      LEFT ('ABCD' = rec.na, ^=).  [C336] measured over-extent with the MEMBER LEFT /
      literal RIGHT (accepted, pooled WHOLE); the literal-LEFT orientation keeps its
      [TBD] (P1 RESULTS s3) and E49A4's inverse must NOT be extrapolated.

  D  E49F1..F4  -- ORDERED RELATIONS (<, >, <=, >=) between internal qualified FIXED
      CHARACTER members, equal and unequal extents.  NEVER probed; helper, mechanism
      and branches are open.  The PLILIB.IRL symbol table (a preserved historical
      input, not an experiment) shows a second `?CX*' family beside the four measured
      `?SC*' compare helpers -- a prior, not a law: NOTHING about ?SCCCM or the
      =/^= rules may be presupposed for these rows, and acceptance itself is open
      ([C332] proved DR draws boundaries inside this operand class).

Scope discipline (operator ruling 2026-11-01): TEST conditions ONLY, CHARACTER FIXED,
NON-BASED, level-numbered internal members.  STOREs, literal-vs-literal, BASED
members, truthiness and `^( ... )' composition stay OUT and keep refusing.
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E49{n}:
  procedure options(main);
{comment}"""

# The E49B shared record (P2): three fixed CHARACTER members (two of length 3, one of
# length 2) plus the plain k and the measured `put list' tail -- kept so the skip fill
# ([C309]) and the [C314] pool-first DATA layout stay comparable across objects.
DECL = "  dcl\n" \
       "    1 rec,\n" \
       "      2 na char(3),\n" \
       "      2 nb char(3),\n" \
       "      2 s2 char(2);\n" \
       "  dcl k fixed bin(15);\n"

TAIL = "  put list('K=', k);\n"


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns."""
    segs = textwrap.wrap("[E2E-49/P3] " + note, width=width - 9)
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


def probe(name, note, body):
    return (HDR.format(n=name, comment=wrapped_comment(note))
            + DECL + body + TAIL + "  stop;\nend E49%s;\n" % name).replace("\n", "\r\n")


P = {}

# ---------------- Panel A: equal-length member-vs-LITERAL (the [C338] TBD) ----
P["C1"] = probe(
    "C1",
    "member LEFT, literal RIGHT, lengths EQUAL (char(3) vs 'ABC').  [C338] measures the "
    "equal-extent collapse `06 n / 78' member-vs-member ONLY and its scope warning names "
    "THIS shape [TBD]: E49A1/A3/A4 (3/2, 3/2, 3/4) always carried two immediates because "
    "the lengths differed.  H-AK-M keeps `EB / 06 03 / 3E 03' (CODE 66, E49A1's template); "
    "H-AC-M collapses to `06 03 / 78' (CODE 65).  One byte decides it.",
    "  if rec.na = 'ABC' then k = 1;\n",
)
P["C2"] = probe(
    "C2",
    "the INVERSION of E49C1: literal LEFT, member RIGHT, lengths EQUAL.  E48E7 (2/3) "
    "carried `21 *D(member) / 11 *D(pool) / 06 02 / 3E 03' -- direct, no EB, CODE 65.  "
    "No shared rule is presupposed with E49C1: H-AK-L keeps `06 03 / 3E 03' (CODE "
    "65); H-AC-L collapses to `06 03 / 78' (CODE 64).  A split verdict between the two "
    "orientations is a first-class outcome.",
    "  if 'ABC' = rec.na then k = 1;\n",
)
P["C3"] = probe(
    "C3",
    "E49C1's shape under ^= : the CA skip byte in the equal-length member-left literal "
    "template ([C072]/[C333] measured CA in this family member-vs-literal 3/2 and "
    "member-vs-member 3/3; the equal literal case has no object).  Length collapse or "
    "not is the same A-panel discriminator as E49C1.",
    "  if rec.na ^= 'ABC' then k = 1;\n",
)
P["C4"] = probe(
    "C4",
    "E49C2's shape under ^= : CA skip on the literal-left equal-length head.  Kept as "
    "its own witness so the skip byte is measured in BOTH orientations at equal "
    "lengths, independent of what C1/C2 show.",
    "  if 'ABC' ^= rec.na then k = 1;\n",
)

# ---------------- Panel B: qualification of the compared members -------------
P["D1"] = probe(
    "D1",
    "member-vs-member compare, BARE LEFT and QUALIFIED RIGHT (`na = rec.nb'), equal "
    "extents.  E49B1 measured the qualified-qualified head `21 *D(left) / E5 / 21 "
    "*D(right) / D1 / 06 03 / 78 / CD ?SCCCM'; [C335] proved the [C253]/[C258] fold "
    "invisible to the encoding member-LEFT-of-literal.  If the fold is invisible here "
    "too the object equals E49B1 byte for byte but the module-name bytes; a PASS-2 "
    "refusal would be a new dr-refuses boundary.",
    "  if na = rec.nb then k = 1;\n",
)
P["D2"] = probe(
    "D2",
    "the mirror: QUALIFIED LEFT, BARE RIGHT (`rec.na = nb').  Same alternatives as "
    "E49D1; an acceptance here with refusal there (or vice versa) is an "
    "orientation-specific qualification boundary -- exactly the shape of P1's asymmetry "
    "and a first-class reading, not noise.",
    "  if rec.na = nb then k = 1;\n",
)
P["D3"] = probe(
    "D3",
    "BARE/BARE member-vs-member (`na = nb').  If DR admits all three spellings, D1/D2/"
    "D3 and E49B1 form a byte-identical quartet (modulo module names) and the encoding "
    "ignores qualification entirely; any byte difference in the relocations or a refusal "
    "names a qualification effect the ledger has never seen.",
    "  if na = nb then k = 1;\n",
)
P["D4"] = probe(
    "D4",
    "BARE fixed member to the RIGHT of a literal (`'AB' = na') -- the P1 asymmetry: "
    "E49A2 admitted bare LEFT-of-literal ([C335]) and P1 RESULTS s2.4 scopes that "
    "finding to the left side; E48E7's literal-left route has only ever been sampled "
    "QUALIFIED.  If accepted, byte-identical to E48E7 but the module name; if refused, "
    "the asymmetry becomes a measured DR law instead of an untested mirror.",
    "  if 'AB' = na then k = 1;\n",
)

# ---------------- Panel C: over-extent literal on the LEFT -------------------
P["E1"] = probe(
    "E1",
    "literal LEFT, longer than the extent: 'ABCD' vs rec.na char(3).  E49A4 measured "
    "the INVERSE orientation (member LEFT, literal RIGHT: [C336] ACCEPTED, literal "
    "pooled WHOLE, positional `06 03 / 3E 04') and P1 RESULTS s2.6 explicitly refuses "
    "to extrapolate to this one.  H-CE accepts on E48E7's direct template with "
    "positional lengths `06 04 / 3E 03' and the full pool; falsifiers: refusal, a "
    "TRUNCATED pool literal, or min/max length readings.",
    "  if 'ABCD' = rec.na then k = 1;\n",
)
P["E2"] = probe(
    "E2",
    "E49E1 under ^= : the CA skip byte on an over-extent literal-left head -- the first "
    "object pairing those two attributes; E48E7 shows C2, E49A3 shows CA at 3/2.  The "
    "verdict of E49E1 governs; this row measures the skip byte if it accepts.",
    "  if 'ABCD' ^= rec.na then k = 1;\n",
)

# ---------------- Panel D: ordered relations ---------------------------------
P["F1"] = probe(
    "F1",
    "ORDERED RELATION `< ' between two qualified FIXED members, equal extents. NEVER "
    "probed: helper, parking, branch byte are ALL open.  Candidates: ?SCCCM + a "
    "flag-conditional skip (C2/CA are equality branches, cannot express <); a DIFFERENT "
    "helper (PLILIB.IRL shows a second ?CX* family -- a prior from a preserved "
    "historical input, not a law); or a PASS-2 refusal like E48E6's BIT REQ. Nothing "
    "from =/^= may be presupposed.",
    "  if rec.na < rec.nb then k = 1;\n",
)
P["F2"] = probe(
    "F2",
    "ordered relation `> ' with UNEQUAL extents (char(3) vs char(2)).  If accepted "
    "with immediates, [C334]'s positional law predicts B = LEFT extent 3, A = RIGHT "
    "extent 2; min/max/keyed readings are the falsifiers -- the same discriminators "
    "E49B3/B4 killed for =, re-tested here because no transfer may be assumed.",
    "  if rec.na > rec.s2 then k = 1;\n",
)
P["F3"] = probe(
    "F3",
    "ordered relation `<= ' between equal-extent members.  A distinct skip byte or "
    "helper from F1 is possible -- the four relations are not one mechanism.  Verdict, "
    "helper, lengths and branch are each measured independently in the object.",
    "  if rec.na <= rec.nb then k = 1;\n",
)
P["F4"] = probe(
    "F4",
    "ordered relation `>= ' with UNEQUAL extents and the SHORTER member on the LEFT.  "
    "The inversion pair of F2 for the positional law, and the fourth relation's own "
    "branch encoding; refusal of any row is DR's boundary, recorded as such.",
    "  if rec.s2 >= rec.na then k = 1;\n",
)


def main():
    for n, text in sorted(P.items()):
        path = os.path.join(PROBES, "E49%s.PLI" % n)
        with open(path, "wb") as fh:
            fh.write(text.encode() + b"\x1a")
        print("wrote %s (%d bytes, maxcol %d)"
              % (path, len(text) + 1, max(len(x) for x in text.split("\r\n"))))


if __name__ == "__main__":
    main()
