#!/usr/bin/env python3
"""E2E-49/P4 probe generator (COMPOSITE campaign: ORDERED RELATIONS with a LITERAL
operand, BARE spellings inside ordered relations, the UNEQUAL-EXTENT relation
matrix, NEGATED compares -- E49G1..G8, E49H1..H6, E49I1..I6, E49J1..J4).

Writes probes/E49*.PLI with CRLF terminators plus the ^Z byte -- [C193] (b): DR answers
an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is <= 71
columns: the measured law that killed P2d run 1 (spec/lab-evidence/e2e48-p2d/RESULTS.md s0).

Run from the repo root:  python3 spec/lab-evidence/e2e49-p4/mkprobes.py

Four panels, ONE bank, per the operator authorization of 2026-11-01:

  A  E49G1..G8  -- ORDERED RELATIONS with a LITERAL operand, all four relations,
      BOTH orientations written independently.  [C346] measured `< > <= >=` on the
      QUALIFIED member pair (same ?SCCCM head as =/^=, ORDER law: < and >= keep
      written order, > and <= are LOWERED SWAPPED; BRANCH law: strict skips JNC d2,
      weak skips JC da; lengths positional ON THE LOWERED operands; equal attributes
      collapse per [C342]).  Whether the ORDER law REKEYS the literal template (the
      staged EB head belongs to member-first, the direct 21/11 head to literal-first)
      or the WRITTEN orientation keeps its template is OPEN -- H-A-sw vs H-A-or,
      with H-A-refuse (a DR boundary like [C332]) as the third outcome.

  B  E49H1..H6  -- BARE spellings inside ORDERED RELATIONS.  [C344] proved the
      qualification fold invisible to EVERY measured compare encoding (=/^=, both
      templates); [C346]'s arm deliberately admits QUALIFIED pairs only, so bare
      sides in a relation are the unmeasured remainder.  H-B-invis predicts each H
      row byte-equals its law-constructed qualified twin (modulo module-name bytes
      and checksum); H-B-gate / H-B-mixed keep a DR boundary possible.

  C  E49I1..I6  -- the UNEQUAL-EXTENT relation matrix (char(3) vs char(2)), all
      relations and orientations, QUALIFIED pairs only -- completing F2/F4's single
      sampled pair.  Primary: DR accepts and the [C346] laws TRANSFER, so every
      object EQUALS my arm-c baseline bytes (NO arm).  Any deviation falsifies the
      transfer.

  D  E49J1..J4  -- NEGATED compares `^( ... )' on string heads -- the FIRST
      syntactic acceptance probe for this composition in the FIXED-CHARACTER
      family.  If accepted, the lowering is open: H-D-inv (skip byte INVERTED on
      the un-negated head: C2->CA, d2->da), H-D-simpl (operator rewritten to the
      complement -- SAME bytes as H-D-inv on these four shapes, non-separable,
      stated honestly), H-D-extra (extra branch/helper bytes), H-D-refuse (DR's
      boundary; keep refusing, no arm).  NO De Morgan assumption anywhere.

Scope discipline (operator ruling 2026-11-01): TEST conditions ONLY, CHARACTER
FIXED, NON-BASED, level-numbered internal members.  STOREs, literal-vs-literal,
BASED members, fixed truthiness and runtime semantics stay OUT; byte tier only.
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
    segs = textwrap.wrap("[E2E-49/P4] " + note, width=width - 9)
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

# ---------------- Panel A: ordered relations with a LITERAL operand ----------
P["G1"] = probe(
    "G1",
    "ORDERED relation `< ' with member LEFT, literal RIGHT, EQUAL attributes (char(3) "
    "vs 'ABC').  [C346] measured the relation family on QUALIFIED member pairs only; "
    "a literal operand in a relation has NO object.  `<' is written-order per the ORDER "
    "law, so H-A-sw and H-A-or predict the SAME staged template `21 *D / EB / 21 *D(pool)'; "
    "the discriminator is the equal-attribute COLLAPSE ([C342], keyed on the numbers, "
    "not the relation): 06 03 / 78 vs two immediates 06 03 / 3E 03.  Strict skips JNC d2.",
    "  if rec.na < 'ABC' then k = 1;\n",
)
P["G2"] = probe(
    "G2",
    "G1's INVERSION: literal LEFT, member RIGHT, `<', equal attributes.  H-A-or keeps "
    "the DIRECT literal-left head `21 *D(member) / 11 *D(pool)' (E48E7/C2's template, "
    "CODE 65); H-A-sw says `< ' is written-order too, so the same direct head is "
    "predicted HERE as well -- this row separates the hypotheses only where a swap "
    "would occur (G3..G6); refusal of any row is H-A-refuse, DR's boundary.",
    "  if 'ABC' < rec.na then k = 1;\n",
)
P["G3"] = probe(
    "G3",
    "ORDERED relation `> ' -- a SWAPPED relation per [C346] -- member LEFT, literal "
    "RIGHT, UNEQUAL attributes 3/2.  H-A-sw: the swap lowers `'AB' < rec.na'-style "
    "pair order, literal FIRST, so the head becomes the DIRECT template and the "
    "position immediates are `06 02 / 3E 03' read off the LOWERED operands; H-A-or: "
    "member-written-left keeps the STAGED `EB' head with `06 03 / 3E 02' written-order "
    "positionals.  The byte pair at 000D..0012 decides.  Strict: JNC d2.",
    "  if rec.na > 'AB' then k = 1;\n",
)
P["G4"] = probe(
    "G4",
    "G3's INVERSION: `> ' with literal LEFT, member RIGHT, 2/3 written.  H-A-sw: the "
    "swap lowers member-FIRST -- the STAGED `EB' head with positionals `06 03 / 3E 02'; "
    "H-A-or: direct literal-left head with `06 02 / 3E 03'.  Together with G3 this row "
    "tests whether the swap REKEYS the template choice or only the operand order.",
    "  if 'AB' > rec.na then k = 1;\n",
)
P["G5"] = probe(
    "G5",
    "`<= ' -- a SWAPPED weak relation -- member LEFT, literal RIGHT, literal OVER-EXTENT "
    "(char(3) vs 'ABCD').  Combines TWO unmeasured boundaries: the relation-with-literal "
    "family and over-extent under a relation ([C345] measured over-extent WHOLE-POOL for "
    "= only, in the written orientation).  H-A-sw: lowered literal-FIRST, direct head, "
    "`06 04 / 3E 03'; H-A-or: staged head, `06 03 / 3E 04'.  Weak skips JC da.  Refusal "
    "of the over-extent spelling here would be a relation-specific [C336]/[C345] boundary.",
    "  if rec.na <= 'ABCD' then k = 1;\n",
)
P["G6"] = probe(
    "G6",
    "G5's INVERSION: `<= ' with the OVER-EXTENT literal LEFT, member RIGHT.  H-A-sw: "
    "lowered member-FIRST -- staged `EB' head, positionals `06 03 / 3E 04'; H-A-or: "
    "direct head, `06 04 / 3E 03'.  The pool must hold 'ABCD' whole iff [C345] transfers "
    "to relations -- a TRUNCATED pool literal or a min/max length reading falsifies it.",
    "  if 'ABCD' <= rec.na then k = 1;\n",
)
P["G7"] = probe(
    "G7",
    "`>= ' -- WRITTEN order per the [C346] ORDER law -- member LEFT, literal RIGHT, "
    "equal attributes.  H-A-sw and H-A-or predict the SAME staged template here; the "
    "discriminators are the COLLAPSE (06 03 / 78 iff [C342] keys on numbers in this "
    "template too) and the weak skip byte JC da.  Fourth relation's own witness.",
    "  if rec.na >= 'ABC' then k = 1;\n",
)
P["G8"] = probe(
    "G8",
    "`>= ' with literal LEFT, member RIGHT, equal attributes.  Written order again per "
    "the ORDER law, so both template hypotheses coincide on the direct head; collapse "
    "and skip byte are the open bytes.  Completion of the 4-relations x 2-orientations "
    "literal matrix at equal attributes.",
    "  if 'ABC' >= rec.na then k = 1;\n",
)

# ---------------- Panel B: BARE spellings inside ordered relations -----------
P["H1"] = probe(
    "H1",
    "BARE LEFT, qualified RIGHT in an ordered relation: `na < rec.nb'.  [C344] proved "
    "qualification INVISIBLE to every measured compare encoding (= and ^=, both "
    "templates); [C346]'s rel arm deliberately admits QUALIFIED pairs only, so this "
    "spelling is unmeasured.  H-B-invis: byte-identical to the E49F1 golden but the "
    "module-name bytes and checksum (stacked head, collapse 06 03 / 78, JNC d2).",
    "  if na < rec.nb then k = 1;\n",
)
P["H2"] = probe(
    "H2",
    "qualified LEFT, BARE RIGHT, SWAPPED relation: `rec.na > nb' (3/3 written, equal "
    "extents).  Twin built from the laws: `> ' swaps, collapse 06 03 / 78 survives the "
    "swap (keyed on numbers, [C346]), strict JNC d2.  A PASS-2 refusal here would be a "
    "qualification gate INSIDE the relation family only -- invisible to =/^= per [C344] "
    "-- a first-class DR boundary, not noise.",
    "  if rec.na > nb then k = 1;\n",
)
P["H3"] = probe(
    "H3",
    "BARE/BARE in a SWAPPED weak relation: `na <= nb' (3/3).  Twin: swap loads nb first, "
    "collapse 06 03 / 78, weak JC da -- the bare twin of the E49F3 shape modulo names. "
    "All three spellings accepted => the relation encoder ignores qualification "
    "entirely, exactly as [C344] found for =/^=.",
    "  if na <= nb then k = 1;\n",
)
P["H4"] = probe(
    "H4",
    "`nb >= na' -- BARE/BARE, WRITTEN-order weak, and deliberately the SAME LOWERED "
    "operand order as F3's swap (nb first, na second).  H-B-invis predicts H4 byte-"
    "equals the E49F3 golden but module names: two DIFFERENT written spellings collapsing "
    "to ONE object is a strong transfer test of the ORDER law onto bare operands.",
    "  if nb >= na then k = 1;\n",
)
P["H5"] = probe(
    "H5",
    "`na > rec.s2' -- the BARE-LEFT twin of E49F2 (unequal extents 3/2, swapped, strict). "
    "H-B-invis predicts the F2 golden's head exactly: swapped loads s2 first, positional "
    "`06 02 / 3E 03' on the LOWERED operands, JNC d2, two immediates (no collapse at "
    "unequal lengths).  Any refusal or byte drift falsifies [C344]-transfer for relations.",
    "  if na > rec.s2 then k = 1;\n",
)
P["H6"] = probe(
    "H6",
    "`s2 <= rec.na' -- BARE LEFT unequal extent, SWAPPED weak relation; the bare twin of "
    "Panel C's I5 (`rec.s2 <= rec.na').  H-B-invis: swap loads na first, `06 03 / 3E 02', "
    "JC da.  Completion of the bare/qualified pair for the unequal-extent weak cell.",
    "  if s2 <= rec.na then k = 1;\n",
)

# ---------------- Panel C: unequal-extent relation matrix (qualified) --------
P["I1"] = probe(
    "I1",
    "`rec.na < rec.s2' -- unequal extents 3/2, WRITTEN order (strict).  [C346]'s F2/F4 "
    "pair sampled `>' and `>= ' only; `< ' unequal and the weak relations unequal have "
    "NO object.  Primary: DR accepts and the laws transfer -- stacked head `21 *D(na) / "
    "E5 / 21 *D(s2) / D1 / 06 03 / 3E 02 / CD ?SCCCM', JNC d2, CODE 67, DATA 000C -- "
    "EQUAL to my arm-c baseline; falsified by refusal or any byte drift.",
    "  if rec.na < rec.s2 then k = 1;\n",
)
P["I2"] = probe(
    "I2",
    "`rec.s2 < rec.na' -- shorter member written LEFT, written order.  Positional law "
    "on lowered operands: `06 02 / 3E 03'; strict JNC d2.  The orientation completion of "
    "the `< ' cell.",
    "  if rec.s2 < rec.na then k = 1;\n",
)
P["I3"] = probe(
    "I3",
    "`rec.s2 > rec.na' -- the INVERSION PAIR of E49F2: same relation `>', extents swapped "
    "in writing.  `> ' is lowered SWAPPED, so na loads first: `06 03 / 3E 02', JNC d2. "
    "This row re-tests whether lengths follow the lowered operands in the OTHER unequal "
    "orientation (F2 measured one direction of the swap only).",
    "  if rec.s2 > rec.na then k = 1;\n",
)
P["I4"] = probe(
    "I4",
    "`rec.na <= rec.s2' -- swapped weak relation, unequal extents.  Swap loads s2 first: "
    "`06 02 / 3E 03'; weak JC da.  The weak unequal cell F4 could not separate (its "
    "written order was already short-first).",
    "  if rec.na <= rec.s2 then k = 1;\n",
)
P["I5"] = probe(
    "I5",
    "`rec.s2 <= rec.na' -- swapped weak, written short-first: lowered loads na first, "
    "`06 03 / 3E 02', JC da.  Fourth witness for the weak skip byte at unequal extents.",
    "  if rec.s2 <= rec.na then k = 1;\n",
)
P["I6"] = probe(
    "I6",
    "`rec.na >= rec.s2' -- the written-order twin of F4 at the same extents (3/2).  "
    "Expect `06 03 / 3E 02', JC da.  With I1..I5 this completes 4 relations x 2 "
    "orientations x unequal extents; every row is compared against my arm-c baseline "
    "bytes, which the primary hypothesis says are ALREADY DR's bytes (NO arm).",
    "  if rec.na >= rec.s2 then k = 1;\n",
)

# ---------------- Panel D: negated compares ----------------------------------
P["J1"] = probe(
    "J1",
    "NEGATED equality `^(rec.na = rec.nb)' -- FIRST acceptance probe for `^ ( )' on a "
    "FIXED CHARACTER string head (the numeric/fixed-bin NegL bank [C143] never touches "
    "strings).  If accepted: H-D-inv predicts the un-negated stacked head with skip C2 "
    "INVERTED to CA -- byte-identical to the E49B5 golden (`rec.na ^= rec.nb') but "
    "names; H-D-simpl (rewrite to ^=) gives the SAME bytes -- non-separable on this "
    "shape, stated.  H-D-extra shows extra branch/helper bytes; H-D-refuse is a DR "
    "boundary and then MY refusal stays.  NO De Morgan assumption.",
    "  if ^(rec.na = rec.nb) then k = 1;\n",
)
P["J2"] = probe(
    "J2",
    "`^(rec.na < rec.nb)' -- negated STRICT relation, equal extents.  H-D-inv: F1's "
    "written-order stacked head (collapse 06 03 / 78) with the JNC d2 skip INVERTED to "
    "JC da; H-D-simpl rewrites `< ' to `>= ' -- same head, same da -- again "
    "non-separable; H-D-extra: an extra branch or helper call distinguishes it.",
    "  if ^(rec.na < rec.nb) then k = 1;\n",
)
P["J3"] = probe(
    "J3",
    "`^('ABC' = rec.na)' -- negated equality on the LITERAL-LEFT DIRECT template, equal "
    "attributes.  H-D-inv: C2's direct head with C2-skip inverted to CA -- byte-equal to "
    "the E49C4 golden (`'ABC' ^= rec.na') but names; tests the collapse too (06 03 / 78, "
    "[C342] in the negated form).  Refusal here with acceptance in J1/J2 would name a "
    "literal-specific boundary on the composition.",
    "  if ^('ABC' = rec.na) then k = 1;\n",
)
P["J4"] = probe(
    "J4",
    "`^(rec.na <= rec.s2)' -- negated SWAPPED WEAK relation, unequal extents.  H-D-inv: "
    "the I4 head (swap, `06 02 / 3E 03') with the weak JC da inverted to strict JNC d2; "
    "H-D-simpl rewrites `<= ' to `> ' -- swapped too, same lowered head, same d2 -- "
    "non-separable.  The unequal-extent negated witness completes the matrix.",
    "  if ^(rec.na <= rec.s2) then k = 1;\n",
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
