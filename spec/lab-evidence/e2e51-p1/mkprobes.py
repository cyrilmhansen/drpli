#!/usr/bin/env python3
"""E2E-51/P1 probe generator (FIXED BINARY variable-divisor DIVISION -- E51A..E51L).

Writes probes/E51*.PLI with CRLF terminators plus the bare ^Z byte -- [C193] (b): DR
answers an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is
<= 71 columns (the law that killed the P2d run 1, spec/lab-evidence/e2e48-p2d/RESULTS.md
s0) and no apostrophe appears inside a comment (comment hygiene).

Run from the repo root:  python3 spec/lab-evidence/e2e51-p1/mkprobes.py

WHAT IS ALREADY SETTLED (do NOT re-measure; these are the controls this bank reuses):
  * [C089]  MOD: dividend -> HL, parked in DE across the divisor; VARIABLE divisor
            `PUSH H / LHLD d / POP D'; LITERAL divisor `MVI A,k / PUSH H / MOV L,A /
            ADD A / SBB A / MOV H,A / POP D'; CALL helper; result HL.
  * P080A (golden/probe48) FIXED BINARY `z = a / 3' -- constant-divisor DIV: the
            sign-extend ladder into HL, dividend parked by PUSH H/POP D into DE,
            CALL ?ID22N (ABI row id22n DE HL HL = word/word divide,
            spec/notes/plilib-entrypoints.txt).  Mine is byte-exact on it.
  * golden/f6probe/F005/F005.REL is an UNANALYSED-AS-A-CLAIM but EXISTING DR object
            for exactly `z = a / b' with plain `fixed` variables: LHLD a / PUSH H /
            LHLD b / POP D / CALL ?ID22N / SHLD z, CODE 0017, DATA 0006.  It is the
            oracle witness that DR ACCEPTS variable-divisor binary DIV; [C141] gives
            the parking laws around helper results.
  * NG16/NG17/NG19 (golden/negpanel1) show DR accepting FIXED DECIMAL variable DIV --
            they are NOT binary witnesses and are never cited for a binary rule.

THE OPEN MATRIX (12 rows, one controlled difference each, shared DECL
`dcl a fixed, b fixed, c fixed, z fixed' -- plain FIXED is DR's binary default at
16-bit storage, the same bank P080A/F005 use; E51K adds `dcl d fixed bin(7)'):

  E51A  z = a / b;                var/var reproduction control vs golden/f6probe/F005
  E51B  z = 1200 / b;             literal dividend, variable divisor
  E51C  z = (a + b) / c;          compound dividend, variable divisor
  E51D  z = a / (b + c);          variable dividend, compound divisor
  E51E  z = a / b / c;            chained division (left-associative)
  E51F  z = a / b + c;            quotient LEFT of an add
  E51G  z = c + a / b;            quotient RIGHT of an add
  E51H  put list(a / b);          quotient consumed by a numeric PUT item
  E51I  if a / b = c then z = 1;  quotient inside a condition
  E51J  z = -a / b;               unary-minus dividend (signed operand form)
  E51K  z = a / d;                1-byte fixed bin(7) divisor (N303 ladder family)
  E51L  z = a / 3;                constant-divisor control tied to P080A

Full per-row hypotheses, competing hypotheses, predicted distinguishing bytes and
falsification conditions are in HYPOTHESES.md (committed BEFORE the oracle call).
"""
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E51{n}:
  procedure options(main);
{comment}"""

# Shared bank: the P080A/F005 family.  Plain `fixed' is DR's FIXED BINARY default
# (16-bit cells); z is the store target of every non-PUT probe.
DECL = "  dcl a fixed, b fixed, c fixed, z fixed;\n"

STOP = "  stop;\n"


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns."""
    segs = textwrap.wrap("[E2E-51/P1] " + note, width=width - 9)
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


def probe(name, note, body, decl=DECL, stop=False):
    text = (HDR.format(n=name, comment=wrapped_comment(note))
            + decl + body
            + (STOP if stop else "")
            + "end E51%s;\n" % name)
    for ln in text.split("\n"):
        assert len(ln) <= 71, (name, len(ln), ln)
    return text.replace("\n", "\r\n")


P = {}

P["A"] = probe(
    "A",
    "PRIMARY: FIXED BINARY variable-divisor DIVISION, z = a / b.  The EXISTING DR "
    "object golden/f6probe/F005/F005.REL (plain-fixed bank, one statement) lowers it "
    "LHLD a / PUSH H / LHLD b / POP D / CALL ?ID22N / SHLD z, CODE 0017.  Mine refuses "
    "codegen: DIV by non-constant [TBD] (the HAMM-00 rev1 blocker).  This row repeats "
    "the settled shape inside the E51 bank to tie the new objects to the old witness: "
    "predicted CODE-SEGMENT bytes EQUAL to F005 modulo the extra variable reloc and the "
    "module-name record; refusal by DR would falsify the F005 reading.",
    "  z = a / b;\n",
)

P["B"] = probe(
    "B",
    "LITERAL dividend, VARIABLE divisor: z = 1200 / b.  Constant in DE is the MB3 "
    "multiply form (LHLD var / LXI D,k / CALL ?IM22N); DIV needs dividend DE = 1200 and "
    "divisor HL = b, so H-B-de predicts LHLD b / LXI D,x'04B0 / CALL ?ID22N / SHLD z.  "
    "H-B-stack: LXI H,1200 / PUSH H / LHLD b / POP D / ID22N.  H-B-conv: decimal pool "
    "conversion (the LR12 out-of-range family).  A DR refusal is H-B-refuse.",
    "  z = 1200 / b;\n",
)

P["C"] = probe(
    "C",
    "COMPOUND dividend over a VARIABLE divisor: z = (a + b) / c.  The P071A add law "
    "(LHLD a / XCHG / LHLD b / DAD D) leaves the sum in HL; the [C089] parking shape "
    "then applies to the SUM: H-C-park predicts ...DAD D / PUSH H / LHLD c / POP D / "
    "CALL ?ID22N / SHLD z, ONE store.  H-C-temp: DR materialises the sum into a temp "
    "cell (an extra SHLD/LHLD pair).  H-C-refuse: DR refuses a parenthesised dividend.",
    "  z = (a + b) / c;\n",
)

P["D"] = probe(
    "D",
    "VARIABLE dividend over a COMPOUND divisor: z = a / (b + c).  The dividend is "
    "already evidenced parked across a variable-divisor evaluation (F005); the question "
    "is whether the sum can be built INSIDE the parked region: H-D-inline predicts "
    "LHLD a / PUSH H / LHLD b / XCHG / LHLD c / DAD D / POP D / CALL ?ID22N / SHLD z.  "
    "H-D-temp predicts a materialised divisor cell; H-D-refuse a DR boundary on "
    "compound divisors (no binary witness exists either way today).",
    "  z = a / (b + c);\n",
)

P["E"] = probe(
    "E",
    "CHAINED DIVISION z = a / b / c (left-associative (a/b)/c).  DEC chaining is "
    "accepted (NG17) but DEC scale laws do not transfer to binary.  If DIV-chain "
    "feeding keeps the quotient in HL across the next parking, H-E-push predicts two "
    "ID22N calls with NO store between them; H-E-store predicts SHLD z then LHLD z "
    "between the calls.  H-E-refuse: a DR binary boundary.",
    "  z = a / b / c;\n",
)

P["F"] = probe(
    "F",
    "QUOTIENT LEFT of an add: z = a / b + c, i.e. (a/b) + c.  [C141] P7 shows DR "
    "reading the var AFTER the left helper result with XCHG (call - var); ADD is "
    "commutative so H-F-xchg predicts <div> / XCHG / LHLD c / DAD D / SHLD z.  "
    "H-F-push (the P5 form): <div> / PUSH H / LHLD c / POP D / DAD D.  H-F-store "
    "stores then reloads.  Any DR refusal is H-F-refuse.",
    "  z = a / b + c;\n",
)

P["G"] = probe(
    "G",
    "QUOTIENT RIGHT of an add: z = c + a / b.  [C141] P1 evaluates the call RIGHT side "
    "FIRST for var + call, so H-G-same predicts G byte-identical to F modulo relocs "
    "already identical (same order a, b, c): <div> / XCHG / LHLD c / DAD D / SHLD z.  "
    "H-G-leftfirst evaluates c into DE first (LHLD c / XCHG after the div would then "
    "carry DIFFERENT bytes); a difference between F and G falsifies orientation-free "
    "right-first evaluation for DIV operands.",
    "  z = c + a / b;\n",
)

P["H"] = probe(
    "H",
    "QUOTIENT consumed by a numeric PUT item: put list(a / b).  [C079] pins the chain "
    "expr->HL / MVI A,width / ?QICOP / ?PNVOP / ?QIOOP; expression items are accepted "
    "there (N304 a+1).  Predicted: F005-style div lowering, then the C079 numeric tail "
    "with width 9 (bin(15) law w = min(9, digits(32767)+4)).  H-H-refuse: DR refuses a "
    "DIV expression as a PUT item.",
    "  put list(a / b);\n",
)

P["I"] = probe(
    "I",
    "QUOTIENT inside a condition: if a / b = c then z = 1.  Equality is [C072]: the "
    "IS22N sub then MOV A,H / ORA L with the CA/JNZ skip family.  H-I-eq predicts "
    "<div> / PUSH H / LHLD c / POP D / CALL ?IS22N / 7C / B5 / skip-CA-then-0000-LAD / "
    "LXI H,1 / SHLD z.  H-I-refuse: an E2E-3b-style condition-subset boundary in DR "
    "itself.  This is the FIRST binary witness for a helper result as a compare "
    "operand; DEC compare claims do not transfer.",
    "  if a / b = c then z = 1;\n",
)

P["J"] = probe(
    "J",
    "SIGNED dividend: z = -a / b.  [C079] -x is <HL> / CALL ?IN20N.  H-J-in20 predicts "
    "LHLD a / CALL ?IN20N / PUSH H / LHLD b / POP D / CALL ?ID22N / SHLD z.  H-J-fuse: "
    "DR could negate after the divide (SAME quotient only if b divides evenly - bytes "
    "distinguish).  H-J-refuse.",
    "  z = -a / b;\n",
)

P["K"] = probe(
    "K",
    "SMALLER-PRECISION divisor: d is fixed bin(7), ONE storage byte (binder sizing per "
    "[C079] p<=7).  [N303] shows the MUL 1-byte RHS interleave: raw LDA / PUSH H / "
    "sign-extend ladder MOV L,A / ADD A / SBB A / MOV H,A / POP D.  H-K-ld predicts "
    "the identical interleave with CALL ?ID22N; H-K-lhld a plain LHLD (which would "
    "READ c TOO -- falsified instantly by the reloc count); H-K-conv a conversion call; "
    "H-K-refuse.",
    "  z = a / d;\n",
    decl=DECL + "  dcl d fixed bin(7);\n",
)

P["L"] = probe(
    "L",
    "CONSTANT-DIVISOR CONTROL: z = a / 3.  [C089]/P080A already pin DR and my byte-exact "
    "lowering (LHLD a / MVI A,03 / PUSH H / MOV L,A / ADD A / SBB A / MOV H,A / POP D / "
    "CALL ?ID22N / SHLD z).  This row rides the SAME oracle batch as the bank harness "
    "control: DR must accept and MINE must already be byte-exact whole-file against the "
    "new E51L golden; any miss means the batch or my constant path drifted, and every "
    "other row must then be re-read with suspicion.",
    "  z = a / 3;\n",
)


def main():
    os.makedirs(PROBES, exist_ok=True)
    names = sorted(P)
    for n in names:
        path = os.path.join(PROBES, "E51%s.PLI" % n)
        if os.path.exists(path):
            raise SystemExit("refusing to overwrite existing probe: " + path)
        with open(path, "wb") as fh:
            fh.write(P[n].encode() + b"\x1a")
        print(path, os.path.getsize(path))


if __name__ == "__main__":
    main()
