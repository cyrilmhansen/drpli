#!/usr/bin/env python3
"""p3a-measure.py -- the two E2E-41/P3a corrections, recomputed from committed artefacts.

Writes, next to itself:

  TITLE-CENSUS.txt   -- every OPEN site in spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv,
                        with its TITLE kind and its measured w1, plus the counts.
  E17D-OUT-DAT.txt   -- the OBSERVED facts about golden/e2e11iu/E17D/OUT.DAT (size,
                        payload bytes, fill bytes, the source OPEN statement, the DR
                        listing's OPEN block) and, separated from them, what is NOT
                        established about that size.

READ-ONLY with respect to the preserved measurements: the p0 directory, the e13src
sources and every golden are opened for reading only.  OPEN-MATRIX.tsv is the
population; this script does not modify it and does not re-decode any .REL.

Why it exists: three active documents (PERIMETER, COVERAGE.tsv, a codegen comment) and
three episode notes (P0, P1, P2) carried a TITLE count of 29 of 34, and four documents
attributed E17D's 128-byte OUT.DAT to an `environment(f(128))' clause.  Both numbers are
recomputable from files already in the repository, which is what this script does.
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MATRIX = os.path.join(ROOT, "spec", "lab-evidence", "e2e41-p0", "OPEN-MATRIX.tsv")
E17D_SRC = os.path.join(ROOT, "e13src", "E17D.PLI")
E17D_PRN = os.path.join(ROOT, "golden", "e2e11i", "E17D", "E17D.PRN")
E17D_REL = os.path.join(ROOT, "golden", "e2e11i", "E17D", "E17D.REL")
OUT_DAT = os.path.join(ROOT, "golden", "e2e11iu", "E17D", "OUT.DAT")


def census():
    with open(MATRIX, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    kinds = collections.Counter(r["title-kind"] for r in rows)
    lines = []
    lines.append("TITLE census, recomputed from spec/lab-evidence/e2e41-p0/"
                 "OPEN-MATRIX.tsv")
    lines.append("population: %d OPEN sites (the file is the measurement; it is read, "
                 "never rewritten)" % len(rows))
    lines.append("")
    lines.append("  title-kind  sites  helper   meaning")
    for kind, helper in (("lit", "?SLCTS"), ("var", "?SLVTS"), ("-", "none")):
        lines.append("  %-10s %5d   %-7s   %s"
                     % (kind, kinds.get(kind, 0), helper,
                        {"lit": "a literal-string TITLE clause",
                         "var": "a variable (non-literal) TITLE clause",
                         "-": "NO TITLE clause at all"}[kind]))
    present = kinds.get("lit", 0) + kinds.get("var", 0)
    lines.append("")
    lines.append("  TITLE PRESENT  = %d of %d sites  (literal %d + variable %d)"
                 % (present, len(rows), kinds.get("lit", 0), kinds.get("var", 0)))
    lines.append("  TITLE ABSENT   = %d of %d sites" % (kinds.get("-", 0), len(rows)))
    lines.append("")
    lines.append("and the option bit, independently: bit 0x0800 of the measured w1.")
    set_rows, clear_rows, disagree = [], [], []
    for r in rows:
        w = int(r["w1"].split("0x")[1], 16)
        has = bool(w & 0x0800)
        (set_rows if has else clear_rows).append(r)
        if has != (r["title-kind"] != "-"):
            disagree.append(r)
    lines.append("  0x0800 set    %d rows" % len(set_rows))
    lines.append("  0x0800 clear  %d rows" % len(clear_rows))
    lines.append("  bit disagrees with the presence of a TITLE clause in %d rows"
                 % len(disagree))
    lines.append("  => the bit tracks TITLE PRESENCE, literal or variable alike; the")
    lines.append("     count of sites carrying it is %d, not 29." % len(set_rows))
    lines.append("")
    lines.append("the %d TITLE-bearing sites, and where each one's title goes:"
                 % present)
    for kind in ("lit", "var"):
        rs = [r for r in rows if r["title-kind"] == kind]
        lines.append("  %s (%d):" % (kind, len(rs)))
        for r in rs:
            lines.append("    %-8s %-9s %-7s w1=%-9s helper=%-7s %s"
                         % (r["program"], r["line"], r["block-start"], r["w1"],
                            r["title-helper"], r["statement"]))
    lines.append("")
    lines.append("the %d titleless sites:" % kinds.get("-", 0))
    for r in rows:
        if r["title-kind"] == "-":
            lines.append("    %-8s %-9s %-7s w1=%-9s %s"
                         % (r["program"], r["line"], r["block-start"], r["w1"],
                            r["statement"]))
    lines.append("")
    lines.append("PROVENANCE OF THE WRONG NUMBERS: 29 appears in P0's bit table")
    lines.append("(section 7), in P1 section 13 item 1 (where an earlier 25 -- which is the")
    lines.append("LITERAL-title count, not the TITLE-present count -- is corrected upward),")
    lines.append("in P2 section 4, in PERIMETER, in COVERAGE.tsv's FILE.OPEN_STREAM row and")
    lines.append("in codegen.ml's open_mode_word comment.  Neither 25 nor 29 is reproducible")
    lines.append("from this file; 30 is.")
    lines.append("spec/lab-evidence/e2e41-p0/W1-BITFIT.txt states no count -- it reports")
    lines.append("`0x0800  TITLE: set only when TITLE=Y', which is what the rows above")
    lines.append("measure.  The artefacts are unchanged; only the prose counted wrong.")
    return "\n".join(lines) + "\n"


def outdat():
    src = open(E17D_SRC, "rb").read().decode("latin-1").replace("\r\n", "\n")
    prn = open(E17D_PRN, "rb").read().decode("latin-1").replace("\r\n", "\n")
    data = open(OUT_DAT, "rb").read()
    rel = open(E17D_REL, "rb").read()
    lines = []
    lines.append("E17D's output file: OBSERVED bytes, and what is NOT known about them.")
    lines.append("")
    lines.append("== 1. OBSERVED -- the file ==")
    lines.append("  path    golden/e2e11iu/E17D/OUT.DAT")
    lines.append("  size    %d bytes" % len(data))
    hist = collections.Counter(data)
    payload = data[:13]
    tail = data[13:]
    lines.append("  first 13 bytes  %r" % payload)
    lines.append("  remaining bytes %d of them, all one value: 0x%02X (SUB/^Z)"
                 % (len(tail), tail[0] if tail else 0))
    for b, n in sorted(hist.items()):
        shown = repr(chr(b))[1:-1] if 32 <= b < 127 else "^Z"
        lines.append("     0x%02X %-3s x %3d   %s"
                     % (b, shown, n, "filler" if b == 0x1A else "payload"))
    lines.append("")
    lines.append("  hex dump (16 bytes/line):")
    for off in range(0, len(data), 16):
        chunk = data[off:off + 16]
        hexs = " ".join("%02x" % b for b in chunk)
        txt = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append("     %04X  %-47s %s" % (off, hexs, txt))
    lines.append("")
    lines.append("== 2. OBSERVED -- how the file came to exist (committed DR evidence) ==")
    lines.append("  e13src/E17D.PLI, the source DR compiled:")
    for i, l in enumerate(src.rstrip("\x1a").split("\n"), 1):
        lines.append("     %d  %s" % (i, l))
    lines.append("")
    lines.append("  DR's own listing (golden/e2e11i/E17D/E17D.PRN), the OPEN statement and")
    lines.append("  its block, verbatim:")
    m = re.search(r"^\s*3 c 0006\s+open.*?(?=\s*\n\s*4 c )", prn, re.S | re.M)
    lines.extend("     " + l for l in m.group(0).rstrip().split("\n"))
    lines.append("")
    lines.append("  sizes DR printed:  "
                 + ", ".join(re.findall(r"^(CODE SIZE = .*|DATA AREA = .*)$",
                                        prn, re.M)))
    lines.append("  golden .REL size:  %d bytes (%s)" % (len(rel), E17D_REL))
    lines.append("  the run that produced OUT.DAT: `D>E17D OUT.DAT' -- see")
    lines.append("  golden/e2e11iu/E17D.transcript.txt (console `WROTE'), and")
    lines.append("  oracle/linkrun.py ARGS[\"E17D\"] = \"OUT.DAT\", "
                 "EXPORT_OUT[\"E17D\"] = [\"OUT.DAT\", \"OUT\"].")
    lines.append("")
    lines.append("== 3. WHAT IS ESTABLISHED FROM THE OBSERVATION ==")
    lines.append("  * The OPEN statement carries NO ENVIRONMENT clause.  The source above")
    lines.append("    has no `environment(...)' and DR's OPEN word is 0x0E50, in which bit")
    lines.append("    0x4000 (the ENVIRONMENT bit, OPEN-MATRIX/W1-BITFIT) is CLEAR; the two")
    lines.append("    record-size words w3/w4 are pushed as 0000 by the listing block above.")
    lines.append("  * The 13 payload bytes are exactly what the two PUT LIST statements")
    lines.append("    write: `'HELLO'' -- list-directed output QUOTES a character literal --")
    lines.append("    then `42' RIGHT-JUSTIFIED IN 5 columns, which is the `MVI A,05' width")
    lines.append("    DR emits before ?QDCOP for a 2-digit decimal literal (width = p+3).")
    lines.append("    No CR or LF appears between them or after them.")
    lines.append("  * The 0x1A fill BEGINS at offset 13, immediately after the payload; the")
    lines.append("    file is 128 bytes, so there are 115 filler bytes.")
    lines.append("")
    lines.append("== 4. WHAT IS NOT ESTABLISHED (hypothesis, not evidence) ==")
    lines.append("  WHY the file is 128 bytes rather than 13 is NOT measured by anything in")
    lines.append("  this repository.  CP/M FCB record padding is the obvious hypothesis --")
    lines.append("  a CP/M sequential file's directory extent counts 128-byte records, and")
    lines.append("  128 is exactly one record -- but the harness exports the file with")
    lines.append("  `cpmcp -f <fmt> <disk> 0:NAME dst' (oracle/cpmwork.py `export',")
    lines.append("  cpmtools), which takes the length from the directory extent, and")
    lines.append("  PLILIB may or may not write the filler.  Nothing")
    lines.append("  here separates those: no captured FCB dump, no directory record, no")
    lines.append("  second output file of a different length.")
    lines.append("")
    lines.append("  WITHDRAWN CLAIMS.  These sentences were written in earlier phases and")
    lines.append("  are false as stated:")
    lines.append("    P0 section 11: `E17D opens outf ... environment(f(128),b(8000))")
    lines.append("                  title(\'$2.$2\')\' -- and `One 128-byte record: independent")
    lines.append("                  corroboration of section 6\'s w4 = F(n)'.")
    lines.append("       E17D has no ENVIRONMENT clause at all and its title is '$1.$1';")
    lines.append("       the two halves of that sentence are OTHER programs' -- the")
    lines.append("       `f(128),b(8000)' is artefacts/ENTER.PLI:37 (w1 0x4D54, title")
    lines.append("       '$1.EMP') and `title(\'$2.$2\')' is COPY.PLI:13 / REPORT.PLI:29 /")
    lines.append("       probes/P021.PLI:4.  The corroboration of w4 = F(n) that P0 thought")
    lines.append("       this gave therefore never existed.")
    lines.append("    P1 section 4: `the 128-byte OUT.DAT of E17D comes from an open that")
    lines.append("                  spells F(128)'.")
    lines.append("    codegen.ml (w3/w4 comment): same sentence.")
    lines.append("    E41X5's NEG_META note (and the INVENTORY.txt row generated from it):")
    lines.append("    `... 128 bytes, from an open that spells F(128)'.")
    lines.append("  What the E17D run DOES corroborate is narrower: that a stream OUTPUT")
    lines.append("  open whose option words are all zero, followed by two PUT FILE LIST")
    lines.append("  statements and a CLOSE, produced a readable file whose payload is the")
    lines.append("  two items -- so the pushed words are accepted by DR's runtime and")
    lines.append("  CLOSE flushed the buffer.")
    return "\n".join(lines) + "\n"


def main():
    for name, text in (("TITLE-CENSUS.txt", census()),
                       ("E17D-OUT-DAT.txt", outdat())):
        p = os.path.join(HERE, name)
        with open(p, "w") as f:
            f.write(text)
        print("wrote %s (%d bytes)" % (os.path.relpath(p, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
