#!/usr/bin/env python3
"""Per-statement DR code trace, for deriving lowering laws from $C listings.

Usage: traces.py N.PRN [N.PRN ...] [--src DIR]

Pairs each $L source-statement line in a DR listing with the code that DR
emitted for it, and reports the FLOAT arithmetic entry points used.  This is
how the ?FX44L / ?FX44R operand-mode rule was derived: a .REL file tells you
which externs a program references, a statement-aligned trace tells you which
expression shape produced each one.
"""
import sys, os, re

FEXT = re.compile(r"\?(F[ASMD]44[LRS]|FX44M|F[ASMD]\w+|\w+)\b")
CODE_RE = re.compile(r"^\$L:\s*(\w{4}):((?:\s+\w{2})+)\s*(.*)$")


def stmt_lines(prn_path, src_path):
    src = open(src_path, "r", errors="replace").read() if src_path else ""
    stmts = []
    for raw in src.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        t = raw.split("*")[1].strip() if raw.startswith("*") else raw.strip()
        if t:
            stmts.append(t)
    out = []          # (address, bytes, tail_text) per code trace line
    for line in open(prn_path, "r", errors="replace"):
        m = CODE_RE.match(line.rstrip("\n"))
        if m:
            out.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return stmts, out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    srcdir = "e13src"
    for a in sys.argv[1:]:
        if a.startswith("--src"):
            srcdir = a.split("=", 1)[1] if "=" in a else "e13src"
    for p in args:
        name = os.path.basename(p)[:-4]
        src = os.path.join(srcdir, name + ".PLI")
        stmts, codes = stmt_lines(p, src)
        # statements containing a FLOAT arithmetic operator, in order of
        # appearance in the source, are paired with the code blocks that
        # mention a ?F*44* entry point.
        fext_blocks = []
        cur = []
        for (_a, _b, tail) in codes:
            ms = re.findall(r"\?F\w+", tail)
            if ms:
                cur.extend(ms)
            elif cur:
                fext_blocks.append(cur)
                cur = []
        if cur:
            fext_blocks.append(cur)
        interesting = [s for s in stmts
                       if re.search(r"[+\-*/]", s) and "=" in s
                       and not s.lower().startswith("dcl")]
        print("=== %s" % name)
        for i, blk in enumerate(fext_blocks):
            stmt = interesting[i] if i < len(interesting) else "?"
            print("   %-34s  %s" % (stmt[:34], " ".join(blk)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
