#!/usr/bin/env python3
"""Strip OCaml comments and string/char literals, then normalise whitespace.

  python3 tools/strip_comments.py <file.ml> > out.txt

This exists to PROVE a claim rather than assert it.  [E2E-42/P1c] is a documentation-and-
diagnostic episode: it may change comments and the text of refusal messages, and may not change
lowering.  "No logic changed" is not visible in a line diff, because a comment rewrite moves
hundreds of lines.  Diffing the two files AFTER removing everything this episode is allowed to
touch leaves only the code, so a residue diff of zero means no executable change, and a residue
diff of one function means exactly one -- and shows which.

Why not just diff with `-w` or read the diff: [C265] exists because a snapshot was reported as
matching when it did not, twice, in two consecutive episodes.  A check that can lie is worse than
no check, so this one is mechanical.

Limitations, stated rather than hidden:
  * Comments nest in OCaml and this handles `(*' / `*)' depth correctly, but it does not model
    string-boundary tricks inside comments (e.g. an unmatched `"' in prose).  OCaml's own lexer
    rejects those, so a file that compiles is safe.
  * Every string literal collapses to the single token "S", so this proves the CODE is
    unchanged while deliberately saying nothing about the TEXT -- which is the point.
  * Char literals collapse to 'C'.
"""
import re
import sys


def strip(src: str) -> str:
    out = []
    i, n, depth = 0, len(src), 0
    while i < n:
        c = src[i]
        if depth == 0 and c == '"':                      # string literal -> "S"
            i += 1
            while i < n:
                if src[i] == '\\':
                    i += 2
                    continue
                if src[i] == '"':
                    i += 1
                    break
                i += 1
            out.append('"S"')
            continue
        if c == '(' and i + 1 < n and src[i + 1] == '*':  # open comment
            depth += 1
            i += 2
            continue
        if depth and c == '*' and i + 1 < n and src[i + 1] == ')':
            depth -= 1
            i += 2
            continue
        if depth:
            i += 1
            continue
        if c == "'":                                      # char literal -> 'C'
            m = re.match(r"'(?:\\.|[^'\\])'", src[i:])
            if m:
                out.append("'C'")
                i += m.end()
                continue
        out.append(c)
        i += 1
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: strip_comments.py <file.ml>")
    sys.stdout.write(strip(open(sys.argv[1], encoding="utf-8", errors="replace").read()) + "\n")
