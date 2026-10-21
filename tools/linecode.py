#!/usr/bin/env python3
"""linecode -- show the code DR generated for the source line(s) you ask about.

DR's $C listing interleaves source and code:
      13 e 0070     return (t + sum(n - 1));
       0070       LHLD N A(0012)
       ...
This turns that into a queryable instrument: python3 tools/linecode.py FILE.PRN SUBSTR
prints only the code block following each matching source line.  Used in E2E-13 to read
the ADD/SUB/constant lowering out of DR's own listings instead of inferring it from bytes.
"""
import re, sys
pat = re.compile(r'^\s*\d+\s+[a-z]\s+([0-9A-F]{4})\s\s+(.*)$')
cod = re.compile(r'^\s+([0-9A-F]{4})\s\s+(.*)$')
def blocks(path):
    out, cur = [], None
    for l in open(path, errors='replace'):
        m = pat.match(l)
        if m:
            cur = {'src': m.group(2).rstrip(), 'code': []}
            out.append(cur); continue
        c = cod.match(l)
        if c and cur is not None:
            cur['code'].append((c.group(1), c.group(2).rstrip()))
    return out
if __name__ == '__main__':
    path, needle = sys.argv[1], sys.argv[2]
    for b in blocks(path):
        if needle.lower() in b['src'].lower():
            print("  %s" % b['src'][:78])
            for a, t in b['code']:
                print("      %s  %s" % (a, t))
