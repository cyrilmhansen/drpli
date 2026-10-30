#!/usr/bin/env python3
"""E2E-48/P2e probe generator (round 5 of the E48 bank, E48E1..E48E8).

Writes probes/E48En.PLI with CRLF terminators -- [C193] (b): DR answers an LF-only
source with UNEXPECTED EOF on every file, so this generator, like mkprobes.py of the
rounds before it, joins lines with crlf.  Every emitted line is <= 71 columns: the
FIRST P2d run died because a single-line purpose comment past column 72 lost its `*/'
(spec/lab-evidence/e2e48-p2d/RESULTS.md s0, golden/e48p2d kept as evidence).

Run from the repo root:  python3 spec/lab-evidence/e2e48-p2e/mkprobes.py

Every probe attacks ONE recorded [TBD] of the `spec/lab-evidence/e2e48-p2d/RESULTS.md`
section 3 list (plus the `= '0'b' VALUE form left open in e2e48-p1 RESULTS s3.2), and
every prediction in HYPOTHESES.md is derived from a committed DR object or a recorded
law of spec/CLAIMS.md, never from memory.  Two probes (E48E6, E48E7) are deliberately
VERDICT-UNKNOWN: they ask whether DR accepts at all, and a `dr-refuses' answer is a
result, not a failure (PROTOCOL Part 1 #3/#4).
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E48E{n}:
  procedure options(main);
{comment}"""

DECL_B = "  dcl b bit(1) static initial('0'b);\n"


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns."""
    segs = textwrap.wrap("[E2E-48/P2e] " + note, width=width - 9)
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

# ---- the biased store ladder's two remaining edges: c = 1 and c < 0  ([C324] [TBD])
P[1] = probe(
    1,
    "store-ladder edge c = 1.  The materialiser is witnessed at c = 0 (A7 000C), c = 2 and "
    "c = 3 (E48D8 [C324]) and c >= 4 (A7 003A [C143]); c = 1 itself has never appeared, and "
    "hl_bias's |b| <= 3 threshold is measured in TEST (E48A13) and in the STORE (E48D8) but "
    "only for |c| >= 2.",
    DECL_B + "  dcl k fixed bin(15);\n",
    "  b = (k = 1);\n"
    "  put list('B=', b);\n",
    "  stop;\nend E48E1;\n",
)

P[2] = probe(
    2,
    "store-ladder edge with a NEGATIVE compare constant: c = -2.  The ladder is never "
    "witnessed at a negative c on either route ([C143] pins +5, [C324] pins +2/+3).",
    DECL_B + "  dcl k fixed bin(15);\n",
    "  b = (k = -2);\n"
    "  put list('B=', b);\n",
    "  stop;\nend E48E2;\n",
)

# ---- the negated VALUE over a ladder other than `= 0'  ([C310]/s3.2 [TBD])
P[3] = probe(
    3,
    "a negated condition as a STORE VALUE over the DCX ladder: ^(k = 2).  [C310] pins the "
    "value negation ONLY for ^(k = 0), where DR emits the ^=0 bytes ADI FF/SBB A with no "
    "ladder at all; the ladder head under `^' has never been sampled.",
    DECL_B + "  dcl k fixed bin(15);\n",
    "  b = ^(k = 2);\n"
    "  put list('B=', b);\n",
    "  stop;\nend E48E3;\n",
)

P[4] = probe(
    4,
    "the same negated VALUE over the LXI B ladder: ^(k = 5), i.e. the [C143] >= 4 head "
    "with the [C095]-negated tail C6 FF/9F.  One statement only: the negated `= 0' form is "
    "already pinned by E48A11, so this object isolates the ladder head under `^'.",
    DECL_B + "  dcl k fixed bin(15);\n",
    "  b = ^(k = 5);\n"
    "  put list('B=', b);\n",
    "  stop;\nend E48E4;\n",
)

# ---- `= '0'b' as a VALUE  (e2e48-p1 RESULTS s3.2 [TBD]; codegen refuses it by name)
P[5] = probe(
    5,
    "the bit-literal compare as a STORE VALUE: f = (b = '0'b).  [C310] pins the '1'b value "
    "form (E48A10 0006, LDA/ANI 80/SUI 80 then the flag tail); the '0'b spelling exists as a "
    "TEST (E11D/E20B/E20E/E21A) but never as a materialised value.  Does DR invert the mask, "
    "retarget the tail, or refuse?",
    DECL_B + "  dcl f bit(1) static initial('0'b);\n",
    "  f = (b = '0'b);\n"
    "  put list('F=', f);\n",
    "  stop;\nend E48E5;\n",
)

# ---- truthiness of a CHARACTER VARYING member (E46K14's shape, fresh key)
P[6] = probe(
    6,
    "truthiness of an internal CHARACTER VARYING member used as a bare condition -- the "
    "E46K14 shape with a fresh module name.  NO golden of ANY program in this repository "
    "tests a character operand without a compare, so this probe decides whether my named "
    "refusal is a DR rule (dr-refuses) or a gap (my-gap).",
    "  dcl\n"
    "    1 rec,\n"
    "      2 line char(14) varying,\n"
    "      2 nxt fixed bin(15);\n"
    "  dcl k fixed bin(15);\n",
    "  if line then k = 1;\n"
    "  put list('K=', k);\n",
    "  stop;\nend E48E6;\n",
)

# ---- literal-left TEST compare against a FIXED CHARACTER member
P[7] = probe(
    7,
    "a literal-left TEST compare whose right operand is a level-numbered FIXED CHARACTER "
    "member.  [C297] shows DR accepting that member class on the PUT file route with "
    "MVI A,declared-length / ?SLCTS, and [C326] measures the same orientation on a VARYING "
    "member with ?SCCVM; no object names a helper for a FIXED character compare.",
    "  dcl\n"
    "    1 rec,\n"
    "      2 name char(3),\n"
    "      2 nxt fixed bin(15);\n"
    "  dcl k fixed bin(15);\n",
    "  if 'AB' = rec.name then k = 1;\n"
    "  put list('K=', k);\n",
    "  stop;\nend E48E7;\n",
)

# ---- a BIT(1) item behind a file attach (s3 [TBD])
P[8] = probe(
    8,
    "a BIT(1) item behind a file attach: put file(outf) list(b, 'X').  [C325] measures the "
    "non-final bit item on the CONSOLE route with its own ?PNBOP tail and one final ?QIOOP; "
    "[C296] measures the file statement as attach + N item chains + one ?QIOOP.  No object "
    "combines the two.",
    DECL_B + "  dcl outf file;\n",
    "  open file(outf) stream output title('E8OUT DAT');\n"
    "  put file(outf) list(b, 'X');\n"
    "  close file(outf);\n",
    "  stop;\nend E48E8;\n",
)


def main():
    for n, text in sorted(P.items()):
        path = os.path.join(PROBES, "E48E%d.PLI" % n)
        with open(path, "wb") as fh:
            fh.write(text.encode() + b"\x1a")
        print("wrote %s (%d bytes, maxcol %d)"
              % (path, len(text) + 1, max(len(x) for x in text.split("\r\n"))))


if __name__ == "__main__":
    main()
