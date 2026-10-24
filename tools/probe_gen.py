#!/usr/bin/env python3
"""Bounded differential probe generator [E2E-38/P4].

The point of this tool is not the programs, it is the ORDER of operations:

  1. expand a template into N concrete sources,
  2. validate every template by compiling it with MY compiler and recording the
     outcome BEFORE any oracle time is spent,
  3. emit CP/M-shaped files (CRLF, trailing ^Z) -- a bare-LF source makes PL/I-80
     say `UNEXPECTED EOF' and still leaves a .PRN behind, so "there is a print
     file" is not "it compiled" [C249],
  4. hand the accepted names to oracle/batch.py for a DR round trip,
  5. compare mine against DR and classify: EXACT / DIFFERS / mine-refuses-DR-accepts
     / both-refuse.

A campaign where every row says the same thing is a measurement of the template,
not of the language: E2E-37's first built-in sweep declared `fixed binary(31)' in
every row, which my own compiler refuses, so all 55 rows failed identically on a
defect of mine.  Step 2 is what stops that happening again, and it is also what
found, in the run recorded here, that four of my sixteen comparison templates
were themselves outside my accepted subset (literal-on-left, `>=', `<=', pointer
equality) while DR accepts all four [C247].

Usage:
  python3 tools/probe_gen.py --family compare --emit artefacts   # steps 1-3
  python3 tools/probe_gen.py --family static  --emit artefacts
  python3 tools/probe_gen.py --validate                          # step 2 only
  python3 tools/probe_gen.py --classify --tag e37e               # step 5 vs a DR run

Exit status: 0 if every template reached at least stage "compiled-by-mine" or was
deliberately built as a negative control; 1 otherwise, with the list printed.
That is a FAILING build, by design: a template that cannot generate a comparison
has not measured anything.
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artefacts")
BIN = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")

# ---------------------------------------------------------------- templates
# Each template: (name, note, list-of-(value-label, body)) where `body' is the
# procedure body.  Two families, per [C246][C247][C248]: comparisons (where the
# PB4 wrong-value defect lives) and STATIC structure members (where the corpus's
# largest single refusal reason lives).
COMPARE = {
    "note": "relation x operand-class x literal position; every row prints the "
            "value that shows whether the branch was taken [C246]",
    "rows": [
        ("local-literal-true",  "if n > 3 branch with n=1 -> not taken"),
        ("local-literal-false", "if 3 > n branch with n=1 -> taken"),
        ("formal-literal",      "same through a FIXED parameter"),
        ("based-literal-1",     "BASED value, z=1: value says not taken, address says taken"),
        ("based-literal-3",     "BASED value, z=3: the boundary itself"),
        ("based-literal-4",     "BASED value, z=4: value and address agree"),
        ("literal-left-based",  "if 3 < q: DR accepts, my subset refuses [C247]"),
        ("ge",                  "if n >= 1: DR accepts, my subset refuses [C247]"),
        ("le",                  "if n <= 1: DR accepts, my subset refuses [C247]"),
        ("pointer-eq",          "if nx = addr(z): the pointer-store read-back [C244][C247]"),
    ],
}
STATIC = {
    "note": "parent-level storage class x member type x member INITIAL; the "
            "negative control is a member INITIAL with no static parent [C250]",
    "rows": [
        ("two-fixed",      "1 g static, 2 a fixed initial(7), 2 b fixed initial(9)"),
        ("nested-char",    "1 o static, 2 m, 3 a fixed initial(3), 2 c char(4) initial('abcd')"),
        ("control-aut",    "CONTROL: 1 o, 2 a fixed initial(3) -> DR's own NOT STATIC"),
        ("mixed",          "static parent, one member INITIAL, one without"),
        ("bit8",           "DIOCALLS' shape: 2 maxsize bit(8) initial('80'b4) + a varying sibling"),
        ("char-varying",   "FSCAN/LOAN2/REPORT's shape: char(n) var initial('...')"),
    ],
}
BODY = {
    "local-literal-true":  "declare n fixed;\n   n = 1;\n   if n > 3 then n = 100;\n   put list('n=', n);",
    "local-literal-false": "declare n fixed;\n   n = 1;\n   if 3 > n then n = 100;\n   put list('n=', n);",
    "formal-literal":      "declare r fixed;\n   r = 0;\n   call sub(1);\n   put list('r=', r);\n   stop;\n sub: procedure(x);\n   declare x fixed;\n   if x > 3 then x = 100;\n   r = x;\n   end sub;",
    "based-literal-1":     "declare p pointer, q based(p) fixed, z fixed;\n   z = 1;\n   p = addr(z);\n   if q > 3 then do; q = q + 4; end;\n   put list('q=', q);",
    "based-literal-3":     "declare p pointer, q based(p) fixed, z fixed;\n   z = 3;\n   p = addr(z);\n   if q > 3 then do; q = q + 4; end;\n   put list('q=', q);",
    "based-literal-4":     "declare p pointer, q based(p) fixed, z fixed;\n   z = 4;\n   p = addr(z);\n   if q > 3 then do; q = q + 4; end;\n   put list('q=', q);",
    "literal-left-based":  "declare p pointer, q based(p) fixed, z fixed;\n   z = 1;\n   p = addr(z);\n   if 3 < q then do; q = q + 4; end;\n   put list('q=', q);",
    "ge":                  "declare n fixed;\n   n = 1;\n   if n >= 1 then n = 100;\n   put list('n=', n);",
    "le":                  "declare n fixed;\n   n = 1;\n   if n <= 1 then n = 100;\n   put list('n=', n);",
    "pointer-eq":          "declare p pointer, z fixed, m fixed;\n   declare 1 s based(p), 2 a fixed, 2 nx pointer;\n   allocate s set(p);\n   z = 12;\n   nx = addr(z);\n   m = 0;\n   if nx = addr(z) then m = 1;\n   put list('match=', m);\n   free s;",
    "two-fixed":           "declare t fixed;\n   declare 1 g static, 2 a fixed initial(7), 2 b fixed initial(9);\n   t = a + b;\n   put list('s=', t);",
    "nested-char":         "declare 1 o static, 2 m, 3 a fixed initial(3), 2 c char(4) initial('abcd');\n   put list('a=', a, 'c=', c);",
    "control-aut":         "declare 1 o, 2 a fixed initial(3);\n   put list('a=', a);",
    "mixed":               "declare t fixed;\n   declare 1 o static, 2 a fixed initial(5), 2 b fixed;\n   b = 2;\n   t = a + b;\n   put list('t=', t);",
    "bit8":                "declare t fixed;\n   declare 1 o static, 2 b bit(8) initial('80'b4), 2 c fixed initial(1);\n   t = c;\n   put list('t=', t, 'b=', b);",
    "char-varying":        "declare 1 o static, 2 s char(6) var initial('abcdef');\n   put list('s=', s);",
}


def prog(name, body):
    tail = "" if "end sub" in body else "   stop;"
    return "%s: procedure options(main);\n   %s\n%s\nend %s;\n" % (
        name, body.replace("\n", "\n   ").rstrip(), tail, name)


def cpm(text):
    """CRLF line endings + the ^Z that CP/M needs to see end-of-file [C249]."""
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode() + b"\x1a"


def emit(family, outdir):
    rows = (COMPARE if family == "compare" else STATIC)["rows"]
    names = []
    for i, (key, _note) in enumerate(rows):
        n = "E38%s%d" % ("C" if family == "compare" else "S", i + 1)
        path = os.path.join(outdir, n + ".PLI")
        with open(path, "wb") as f:
            f.write(cpm(prog(n, BODY[key])))
        names.append(n)
        print("wrote %s  (%s)" % (path, key))
    print("\nDR round trip:\n  python3 oracle/batch.py %s --switches '$L$D' --tag <tag>"
          % " ".join(names))
    return names


def compile_mine(path):
    """Return (ok, reason).  The artefact is the authority, never the exit status
    of a pipeline -- that is how [C245] was manufactured [C249]."""
    out = "/tmp/probe_gen.rel"
    if os.path.exists(out):
        os.remove(out)
    p = subprocess.run([BIN, path, out], capture_output=True, text=True)
    if os.path.exists(out):
        return True, ""
    msg = (p.stderr or p.stdout).strip().split("\n")[-1]
    return False, msg.replace("Fatal error: exception ", "")[:110]


def validate(family, outdir):
    rows = (COMPARE if family == "compare" else STATIC)["rows"]
    bad = []
    for i, (key, note) in enumerate(rows):
        n = "E38%s%d" % ("C" if family == "compare" else "S", i + 1)
        path = os.path.join(outdir, n + ".PLI")
        if not os.path.exists(path):
            bad.append((n, key, "NOT EMITTED"))
            continue
        ok, why = compile_mine(path)
        print("%-8s %-18s %s" % (n, key, "compiled" if ok else "REFUSED: " + why))
        if not ok and key != "control-aut":
            bad.append((n, key, why))
    if bad:
        print("\n%d template(s) did not reach my codegen; each is a finding, not a failure to"
              " hide:\n  - if DR accepts it, it is a coverage gap (register a COVERAGE row)" % len(bad))
    return bad


def classify(family, tag, outdir):
    rows = (COMPARE if family == "compare" else STATIC)["rows"]
    tally = {}
    for i, (key, _n) in enumerate(rows):
        name = "E38%s%d" % ("C" if family == "compare" else "S", i + 1)
        gold = os.path.join(ROOT, "golden", tag, name, name + ".REL")
        src = os.path.join(outdir, name + ".PLI")
        if not os.path.exists(gold):
            verdict = "DR-NO-REL (rejected or not run)"
        else:
            ok, why = compile_mine(src) if os.path.exists(src) else (False, "no source")
            if not ok:
                verdict = "mine REFUSES, DR ACCEPTS  <- gap"
            else:
                a, b = open("/tmp/probe_gen.rel", "rb").read(), open(gold, "rb").read()
                first = next((hex(i) for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
                verdict = "EXACT" if len(a) == len(b) and first is None \
                    else "DIFFERS at %s (mine %d, dr %d bytes)" % (first, len(a), len(b))
        tally[verdict.split()[0]] = tally.get(verdict.split()[0], 0) + 1
        print("%-8s %-18s %s" % (name, key, verdict))
    print("\ntally:", tally)
    return tally


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=["compare", "static"], default="compare")
    ap.add_argument("--emit", metavar="DIR")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--classify", action="store_true")
    ap.add_argument("--tag", default="e37e")
    ap.add_argument("--outdir", default=ART)
    ap.add_argument("--crlf-eof", nargs=2, metavar=("IN", "OUT"),
                    help="single-file mode: read IN (LF, no marker), write OUT as CP/M text "
                         "(CRLF + ^Z).  [C249]: a source without ^Z makes PL/I-80 print "
                         "UNEXPECTED EOF and still leave a .PRN, so the harness, not a shell "
                         "one-liner, owns this")
    a = ap.parse_args()
    if a.crlf_eof:
        src, dst = a.crlf_eof
        body = open(src).read().rstrip("\n").replace("\r", "")
        open(dst, "wb").write((body.replace("\n", "\r\n") + "\r\n\x1a").encode("ascii"))
        print("cp/m source %s (%d bytes, CRLF + ^Z)" % (dst, os.path.getsize(dst)))
        return 0
    if a.emit:
        emit(a.family, a.emit)
    if a.validate:
        bad = validate(a.family, a.outdir)
        if bad:
            return 1
    if a.classify:
        classify(a.family, a.tag, a.outdir)
    if not (a.emit or a.validate or a.classify):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
