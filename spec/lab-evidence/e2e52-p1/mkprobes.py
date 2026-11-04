#!/usr/bin/env python3
"""E2E-52/P1 probe generator (scope-aware DEC pool prescan -- LOAN2 blocker, E52A..E52J).

Writes probes/E52*.PLI with CRLF terminators plus the bare ^Z byte -- [C193] (b): DR
answers an LF-only source with UNEXPECTED EOF on every file.  Every emitted line is
<= 71 columns and the files contain NO apostrophes at all (no string literals; comment
hygiene per the E2E-52 hop-1 survey).  Keys E52A..E52J were checked against
spec/INVENTORY.txt and probes/ BEFORE writing (C193 (c)): no collision.

Run from the repo root:  python3 spec/lab-evidence/e2e52-p1/mkprobes.py

WHAT THIS BANK MEASURES (one controlled difference per row).  The motivating gap:
artefacts/LOAN2.PLI refuses at codegen with "variable i declared with conflicting
kinds; decimal pool prescan needs one unambiguous type map [TBD]" while DR accepts it
(golden/first/LOAN2/LOAN2.REL, 7680 B, DATA 0x035A, CODE 0x09A0).  The outer main
block declares i fixed decimal(4,2); current_year declares formal I fixed decimal
(10,2); line declares i fixed bin.  My pd_vars (codegen.ml:13438) is ONE flat global
name->vkind map and refuses any cross-scope kind clash.

SETTLED CONTROLS this bank reuses (never re-derived):
  * [C187] N6: a same-named local is a DISTINCT cell (outer A(000C), inner A(000E))
            -- DR accepts cross-scope homonyms; same-kind homonyms compile on MINE
            today (hop-1 scratch S1: rc=0, 256 B).
  * [C178]/E2E-24: DEC-literal pool cells dedup on the ENCODER BYTE IMAGE
            (LQ6: p=6 vs p=7 same 4-byte image, one cell; LQA: dec(5) store and an
            integer store share one cell).  Whether that dedup spans SCOPES is what
            E52A/E52F measure.
  * DEC cell bytes = ceil((p+1)/2): dec(4,2)=3, dec(7,2)=4, dec(9,2)=5 [R507/LOAN1].
  * [C131]: DEC formal writes take the ?DSTOP route for a variable source; a literal
            store into a DEC formal compiles on MINE today (hop-1 scratch S2: rc=0,
            256 B, DATA 0x000F) -- the E52G residual risk is only the SHADOW clash.
  * A bare-literal store into a fixed bin target allocates NOTHING at lowering
            (LXI H,immediate / SHLD) unless the value exceeds bin(15) [C178/C215].

THE BANK (frame: E52X label, procedure options(main), statements first then nested
procedures, call q; spelling, end E52X;):

  E52A  homonym, SAME type both scopes, both i = 3 -- control (compiles today) and
        the cross-scope IMAGE-DEDUP question: one 3-byte cell vs two.
  E52B  outer i fixed dec(4,2) / inner i fixed dec(9,2), both i = 3 -- the LOAN2
        conflicting-kinds class in miniature; pool 3+5=8 vs a single outer-typed cell.
  E52C  DEC outer / inner i fixed bin -- CODE discriminator: inner store immediate
        LXI H,0003 / SHLD (lexical) vs LXI H,*S + DLDOP (outer-typed global map).
  E52D  fixed bin outer / i fixed dec(7,2) inner -- DATA discriminator: lexical pool
        4 vs outer-typed pool 0.
  E52E  inner stores to NON-shadowed outer o fixed dec(9,2) -- an own-rows-only
        prescan would MISS the 5-byte cell; accumulation (outer rows stay visible)
        must see it.
  E52F  different names (a outer, b inner), same type, same value -- separates image
        dedup from name/scope-keyed dedup: one 3-byte cell vs two.
  E52G  formal shadow: q procedure(i), dcl i fixed dec(9,2); i = 3 inside; outer
        i fixed dec(4,2); i = 3; call q(i); -- the LOAN2 current_year shape exactly.
  E52H  nested-nested: main x dec(4,2), mid m declares x dec(9,2) + store, innermost
        n (no own x) stores x = 3 -- does n resolve through m (mid 5-byte cell) or
        only through main (own+main env, 3-byte cell)?  CODE/reloc discriminator:
        both models dedup onto an EXISTING cell, DATA is 8 pool bytes either way.
  E52I  3-level chain, mid declares x dec(9,2), innermost TESTS it: if x > 0 then
        x = 1; -- the prescan_cond consumer through two levels; DATA discriminator
        (lexical pool 3+5+5 vs main-env pool 3+3+3).
  E52J  regression control, NO shadowing: proc-local d dec(9,2), d = 3, a do-while
        with the DEC literal compare d > 0 and the R608 aligned d = d - 1 -- guards
        the existing single-scope prescan path (compiles today, hop-1 scratch S4).

Full per-row competing hypotheses, predicted pool/DATA sizes and falsification
conditions are in HYPOTHESES.md (committed BEFORE the oracle call, as is this file
and BASELINE-MINE.txt).
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(ROOT, "..", "..", "..", "probes")

HDR = """E52{n}:
  procedure options(main);
{comment}"""


def wrapped_comment(note, width=71):
    """Emit the purpose comment as several lines, every one <= 71 columns.

    Hygiene (hop-1 survey): NO apostrophes and no backticks anywhere inside a
    generated probe; comment text is checked to be apostrophe-free below.
    """
    note = "[E2E-52/P1] " + note
    segs = []
    for para in note.split("\n"):
        words = para.split()
        cur = ""
        for wd in words:
            if wd == "|":            # explicit paragraph break marker
                segs.append(cur)
                cur = ""
                continue
            trial = (cur + " " + wd).strip()
            if len(trial) <= width - 9:
                cur = trial
            else:
                segs.append(cur)
                cur = wd
        segs.append(cur)
    segs = [s for s in segs if s]
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
    for ln in lines:
        assert len(ln) <= width, (width, ln)
    return "\n".join(lines) + "\n"


def probe(letter, note, body):
    text = HDR.format(n=letter, comment=wrapped_comment(note)) + body + "end E52%s;\n" % letter
    assert "'" not in text and "`" not in text, "apostrophe/backtick in probe"
    for ln in text.split("\n"):
        assert len(ln) <= 71, (letter, len(ln), ln)
    return text.replace("\n", "\r\n") + "\x1a"


P = {}

P["A"] = probe(
    "A",
    "CONTROL, SAME-TYPE HOMONYM: outer and inner i both fixed dec(4,2), both store "
    "the literal 3.  Compiles on MINE today (no kind clash).  DR must accept by "
    "[C187] N6 (distinct cells).  The open question is POOL DEDUP ACROSS SCOPES: "
    "both stores have the SAME 3-byte packed image, so an image-keyed pool shared "
    "program-wide gives ONE 3-byte cell (predicted DATA 3 pool + 3 + 3 vars = 9); "
    "a per-scope or name-keyed pool gives two cells (12).  H4-vs-H1.",
    "  dcl i fixed dec(4,2);\n"
    "  i = 3;\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl i fixed dec(4,2);\n"
    "     i = 3;\n"
    "     end q;\n",
)

P["B"] = probe(
    "B",
    "CONFLICTING-KINDS CLASS IN MINIATURE (LOAN2): outer i fixed dec(4,2), inner i "
    "fixed dec(9,2), both store 3.  MINE refuses TODAY at the prescan map.  A "
    "scope-aware (lexical, innermost-wins) type map predicts TWO pool cells -- 3 B "
    "for the outer target-precision image and 5 B for the inner -- pool 8, plus "
    "cells 3 + 5, DATA 16.  A global outer-wins type map would type BOTH stores at "
    "dec(4,2): ONE 3-byte cell, pool 3, DATA 11.  DATA-SIZE discriminates.",
    "  dcl i fixed dec(4,2);\n"
    "  i = 3;\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl i fixed dec(9,2);\n"
    "     i = 3;\n"
    "     end q;\n",
)

P["C"] = probe(
    "C",
    "DEC OUTER / BINARY INNER (homonym i): outer i fixed dec(4,2), inner i fixed "
    "bin, both i = 3.  The inner store is the discriminator: lexical resolution "
    "types it BINARY -- LXI H,immediate 0003 / SHLD, NO pool cell (pool stays 3 "
    "for the outer store); a global outer-typed map wrongly routes it through the "
    "DEC path LXI H,*S + DLDOP + ?DSTOP and would also need the pool.  Same DATA "
    "either way (predicted 3 pool + 3 + 2 vars), CODE BYTES distinguish.  MINE "
    "refuses today (Vdec vs Vint clash).",
    "  dcl i fixed dec(4,2);\n"
    "  i = 3;\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl i fixed bin;\n"
    "     i = 3;\n"
    "     end q;\n",
)

P["D"] = probe(
    "D",
    "BINARY OUTER / DEC INNER (homonym i): outer i fixed bin, inner i fixed "
    "dec(7,2), both i = 3.  Lexical resolution: the OUTER store is an immediate "
    "(no cell), the INNER store takes a 4-byte target-precision cell -- pool 4, "
    "DATA 4 + 2 + 4 = 10.  A global outer-wins map types the inner store BINARY: "
    "NO pool cell at all -- pool 0, DATA 6.  DATA-SIZE discriminates.  MINE "
    "refuses today (Vint vs Vdec clash).",
    "  dcl i fixed bin;\n"
    "  i = 3;\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl i fixed dec(7,2);\n"
    "     i = 3;\n"
    "     end q;\n",
)

P["E"] = probe(
    "E",
    "NON-SHADOWED OUTER WRITE: only main declares o fixed dec(9,2); the nested "
    "procedure q stores o = 3.  Compiles on MINE today (flat map contains o).  "
    "The row tests the ACCUMULATION half of the fix: a prescan carrying only "
    "each procedures OWN rows would see no o inside q, miss the 5-byte "
    "target-precision cell, and shift every later DATA address.  Predicted DR "
    "pool 5 + o cell 5, DATA 10.",
    "  dcl o fixed dec(9,2);\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     o = 3;\n"
    "     end q;\n",
)

P["F"] = probe(
    "F",
    "DIFFERENT NAMES, SAME IMAGE ACROSS SCOPES: outer a fixed dec(4,2) stores 3, "
    "inner b fixed dec(4,2) stores 3.  No homonym, compiles today.  The image-keyed "
    "dedup [C178] is name-blind, so a program-wide pool predicts ONE 3-byte cell "
    "(DATA 3 pool + 3 + 3 = 9); per-scope pools give two (12).  Together with A "
    "this separates scope-keyed from image-keyed dedup independent of shadowing.",
    "  dcl a fixed dec(4,2);\n"
    "  a = 3;\n"
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl b fixed dec(4,2);\n"
    "     b = 3;\n"
    "     end q;\n",
)

P["G"] = probe(
    "G",
    "FORMAL SHADOW -- THE LOAN2 CURRENT_YEAR SHAPE: outer i fixed dec(4,2) with "
    "i = 3; q takes formal i declared fixed dec(9,2) and stores the LITERAL 3 into "
    "it; main calls q(i).  The literal-to-formal DEC store itself compiles on MINE "
    "today without shadowing (hop-1 scratch S2 rc=0); this row adds the shadow, "
    "which my flat map refuses.  Lexical typing predicts the inner cell 3 B and "
    "the formal store cell 5 B (pool 8); the copy-in of a dec(4,2) actual into a "
    "dec(9,2) formal is the [C131] route.",
    "  dcl i fixed dec(4,2);\n"
    "  i = 3;\n"
    "  call q(i);\n"
    "  q: procedure(i);\n"
    "     dcl i fixed dec(9,2);\n"
    "     i = 3;\n"
    "     end q;\n",
)

P["H"] = probe(
    "H",
    "THREE SCOPES, INNER WRITE RESOLVES THROUGH MID: main x fixed dec(4,2) stores "
    "3; mid m declares x fixed dec(9,2) and stores 3; innermost n declares NO x and "
    "stores x = 3.  Lexical scoping binds ns x to Ms dec(9,2) cell -- the store "
    "image is 5 B and dedups onto Ms EXISTING cell (pool 3 + 5 = 8, DATA 16 "
    "including the two variable cells).  An own-plus-main-only environment binds it "
    "to MAINs dec(4,2) -- image 3 B, dedups onto main s cell, same DATA 16.  The "
    "DISCRIMINATOR IS CODE: which *S operand ns LXI H loads (3-byte vs 5-byte "
    "cell) and the DLDOP width byte.  MINE refuses today (main vs mid clash).",
    "  dcl x fixed dec(4,2);\n"
    "  x = 3;\n"
    "  call m;\n"
    "  m: procedure;\n"
    "     dcl x fixed dec(9,2);\n"
    "     x = 3;\n"
    "     call n;\n"
    "     n: procedure;\n"
    "        x = 3;\n"
    "        end n;\n"
    "     end m;\n",
)

P["I"] = probe(
    "I",
    "THREE SCOPES, INNER TEST THROUGH MID (prescan_cond consumer): main x dec(4,2) "
    "stores 3; mid m declares x dec(9,2) and stores NOTHING; innermost n tests "
    "x > 0 and stores x = 1.  Lexical typing sizes BOTH condition and store literals "
    "at dec(9,2): pool 3 + 5 + 5 = 13, DATA 21 with the two variable cells.  A "
    "main-only environment sizes them at dec(4,2): pool 9, DATA 17.  DATA-SIZE "
    "discriminates the prescan_cond consumer path directly.  MINE refuses today "
    "(main vs mid clash).",
    "  dcl x fixed dec(4,2);\n"
    "  x = 3;\n"
    "  call m;\n"
    "  m: procedure;\n"
    "     dcl x fixed dec(9,2);\n"
    "     call n;\n"
    "     n: procedure;\n"
    "        if x > 0 then x = 1;\n"
    "        end n;\n"
    "     end m;\n",
)

P["J"] = probe(
    "J",
    "REGRESSION CONTROL, NO SHADOWING: proc-local d fixed dec(9,2); d = 3; a "
    "do-while testing d > 0 with the R608 partner-aligned store d = d - 1 inside.  "
    "Compiles on MINE today (hop-1 scratch S4 rc=0, 384 B): three distinct 5-byte "
    "pool cells plus the d cell.  This row pins the EXISTING single-scope prescan "
    "against regression -- after the scope-aware change my object must stay "
    "byte-identical, and it ties the new bank to settled pool laws.",
    "  call q;\n"
    "  q: procedure;\n"
    "     dcl d fixed dec(9,2);\n"
    "     d = 3;\n"
    "     do while (d > 0);\n"
    "        d = d - 1;\n"
    "     end;\n"
    "     end q;\n",
)

ORDER = "ABCDEFGHIJ"


def main():
    os.makedirs(PROBES, exist_ok=True)
    for k in ORDER:
        name = "E52%s.PLI" % k
        path = os.path.join(PROBES, name)
        with open(path, "wb") as fh:
            fh.write(P[k].encode("latin-1"))
        print("wrote %s (%d bytes)" % (path, len(P[k])))


if __name__ == "__main__":
    main()
