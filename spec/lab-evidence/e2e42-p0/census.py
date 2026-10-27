#!/usr/bin/env python3
"""[E2E-42/P0] THE OPEN OPTION CENSUS, RECOMPUTED FROM THE AST, NOT FROM SUBSTRINGS.

E2E-41/P0 built spec/lab-evidence/e2e41-p0/OPEN-MATRIX.tsv by substring-matching option
words in the SOURCE TEXT of each OPEN statement, and that is how the counts got wrong: the
substring `output' also occurs in the NAME of a FILE operand, so
`KEYFILE:16  open file(input)' was scored as carrying an INPUT OPTION and
`LOAN2:54/56  open file(output)' as carrying an OUTPUT OPTION [C287].

This script counts from spec/lab-evidence/e2e42-p0/AST-OPEN-SITES.txt instead -- the
`opts=[...]' lists pli80tree.exe dumped for all 34 measured historical OPEN statements, one
row per statement, options in SOURCE ORDER.  An option key there is a PARSED key, so an
operand name can never be mistaken for one and no masking step is needed.  (The first draft
of this script masked `FILE(...)' textually and still missed: `PRINT' is not in the
dump's vocabulary as an option at all in some rows, and masking is a repair of the wrong
method rather than a fix.  Counting parsed keys is the method.)

Run from the repository root:  python3 spec/lab-evidence/e2e42-p0/census.py
Its output is spec/lab-evidence/e2e42-p0/OPEN-CENSUS.txt, which is what [C287] quotes.
"""
import io
import re
import collections

SRC = "spec/lab-evidence/e2e42-p0/AST-OPEN-SITES.txt"


def split_opts(text):
    """Top-level option tokens of a dump like `FILE(outf) STREAM OUTPUT TITLE('$1.$1')'.

    An option with no operand is a bare word; one with an operand is `KEY(...)'.  Operand
    parens nest (`ENVIRONMENT((comma[(call f[128]), (call b[1024])]))') and contain quotes,
    so the scan tracks both depth and quoting and only a depth-0 `)' closes an operand."""
    out, i = [], 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        m = re.match(r"[A-Za-z][A-Za-z]*", text[i:])
        if not m:
            i += 1
            continue
        key, i = m.group(0).upper(), i + m.end()
        if i < len(text) and text[i] == "(":
            depth, j, instr = 1, i + 1, False
            while j < len(text) and depth:
                c = text[j]
                if c == "'":
                    instr = not instr
                elif not instr:
                    if c == "(":
                        depth += 1
                    elif c == ")":
                        depth -= 1
                j += 1
            out.append((key, text[i + 1:j - 1]))
            i = j
        else:
            out.append((key, ""))
    return out


def rows():
    for line in io.open(SRC, encoding="utf-8"):
        if "opts=[" not in line or line.startswith("#"):
            continue
        f = line.split()
        yield f[0], f[1], split_opts(line.split("opts=[", 1)[1].rsplit("]", 1)[0])


def keys(o):
    return [k for k, _ in o]


def main():
    all_rows = list(rows())
    cnt = collections.Counter()
    lit, var, both, neither = 0, 0, 0, 0
    titles, no_mode, out_no_stream, in_rows, out_rows = [], [], [], [], []
    for prog, ln, opts in all_rows:
        cnt.update(keys(opts))
        ks = keys(opts)
        if "INPUT" in ks and "OUTPUT" in ks:
            both += 1
        if "INPUT" in ks:
            in_rows.append("%s:%s" % (prog, ln))
        if "OUTPUT" in ks:
            out_rows.append("%s:%s" % (prog, ln))
            if "STREAM" not in ks:
                out_no_stream.append("%s:%s [%s]" % (prog, ln, " ".join(ks)))
        if "INPUT" not in ks and "OUTPUT" not in ks:
            neither += 1
            no_mode.append("%s:%s  %s" % (prog, ln, " ".join(ks)))
        for k, v in opts:
            if k == "TITLE":
                if v.startswith("'"):
                    lit += 1
                else:
                    var += 1
                    titles.append("%s:%s  title(%s)" % (prog, ln, v))

    print("# [E2E-42/P0] OPEN OPTION CENSUS -- recomputed from the PARSED option lists")
    print("# source: AST-OPEN-SITES.txt (pli80tree.exe over the 34 measured historical OPENs)")
    print("# generator: census.py, same directory.  [C287]")
    print()
    print("sites=%d   %s" % (len(all_rows),
                             "  ".join("%s=%d" % (k.lower(), cnt[k]) for k in sorted(cnt))))
    print("TITLE operands: literal=%d  variable=%d" % (lit, var))
    print("mode partition: INPUT=%d (%s)   OUTPUT=%d (%s)   both=%d   neither=%d"
          % (cnt["INPUT"], ", ".join(in_rows), cnt["OUTPUT"], ", ".join(out_rows), both, neither))
    print("the mode partition accounts for every site: %d + %d - %d + %d = %d = sites"
          % (cnt["INPUT"], cnt["OUTPUT"], both, neither, len(all_rows)))
    print()
    print("OUTPUT rows that omit the STREAM keyword (%d):" % len(out_no_stream))
    for r in out_no_stream:
        print("  " + r)
    print()
    print("rows naming NEITHER INPUT nor OUTPUT (%d) -- these are the print / attribute-only" % len(no_mode))
    print("forms, and they are why `a missing mode means INPUT' cannot be read off the corpus:")
    for r in no_mode:
        print("  " + r)
    print()
    print("VARIABLE TITLE operands (%d sites) -- the ?SLCTS/?SLVTS split, [C288]:" % var)
    for t in titles:
        print("  " + t)


main()
