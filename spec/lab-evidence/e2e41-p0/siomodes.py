#!/usr/bin/env python3
"""siomodes.py -- the (HL, DE, BC) triple DR sets up before every ?SIOOP attach.

The console routes this compiler already reproduces set only DE and BC:
    LXI D,0x0252 ; LXI B,<next statement> ; CALL ?SYSPR      (put list)
    LXI D,0x0290 ; LXI B,<next statement> ; CALL ?SYSIN      (get list)
A NAMED file does the same three instructions but loads HL with the file's control
block first and calls ?SIOOP instead [COPY, P072H, E16C, ...].  So the DE word is the
one thing that has to be derived per file, and this table lists every DE value DR was
observed to use, next to the same file's OPEN w1, so the relation between the two can
be stated from samples instead of from a guess.

The OPEN w1 is matched by the COMMON group name HL points at -- that is the file.

Run:  python3 siomodes.py            (writes SIOMODES.txt next to this script)
"""
import collections
import csv
import glob
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for _p in (HERE, os.path.join(ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import e41rel as E       # noqa: E402
import openblocks as OB  # noqa: E402


def group_of(rmap, a):
    p = rmap.get(a) or rmap.get(a + 1)
    if not p:
        return None
    return p[2] or p[0]


def main():
    # every OPEN site's w1, by program + COMMON group
    w1of = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(HERE, 'OPEN-MATRIX.tsv')), delimiter='\t'):
        g = r['cb-group'].split('/')[1] if '/' in r['cb-group'] else r['cb-group']
        if r['w1'].startswith('IMM:'):
            w1of[(r['program'], g)].add(int(r['w1'][4:], 16))
    rows = []
    seen = set()
    for p in sorted(set(glob.glob(os.path.join(ROOT, 'golden', '**', '*.REL'),
                                  recursive=True))):
        try:
            _ev, code, rmap, ext, layout, total = E.replay(p)
        except Exception:                              # noqa: BLE001
            continue
        if not any(v == '?SIOOP' for v in ext.values() if v):
            continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        if h in seen:
            continue
        seen.add(h)
        program = os.path.basename(os.path.dirname(p))
        I = OB.decode(code)
        starts = sorted(I)
        for slot in sorted(ext):
            if ext[slot] != '?SIOOP':
                continue
            call = slot - 1
            i = starts.index(call) if call in starts else None
            if i is None:
                continue
            hl = de = bc = None
            nxt = []
            for a in starts[max(0, i - 5):i]:
                op, mn, n = I[a]
                if op == 0x21:
                    hl = group_of(rmap, a + 1) or ('0x%04X' % (code[a + 1] | (code[a + 2] << 8)))
                elif op == 0x11:
                    de = code[a + 1] | (code[a + 2] << 8)
                elif op == 0x01:
                    bc = rmap.get(a + 1)
            after = [ext.get(a + 1) for a in starts[i + 1:i + 6] if I[a][0] == 0xCD]
            rows.append(dict(program=program, rel=os.path.relpath(p, ROOT),
                             call='%04X' % call, hl=hl or '-',
                             de='%04X' % de if de is not None else '-',
                             bc='continuation' if bc else '-',
                             after=' '.join(x for x in after if x),
                             w1='/'.join('%04X' % v for v in sorted(w1of.get((program, hl), [])))
                             or '-'))
    out = os.path.join(HERE, 'SIOMODES.txt')
    with open(out, 'w') as fh:
        fh.write('# every ?SIOOP (named-file stream attach) in the distinct DR objects,\n')
        fh.write('# with the file it names, the DE mode word, and that file\'s OPEN w1\n')
        fh.write('# (from OPEN-MATRIX.tsv, matched on the COMMON group HL points at).\n')
        fh.write('# `after\' lists the routines called between this attach and the next\n')
        fh.write('# attach or statement -- the item-conversion chain the route runs.\n\n')
        fh.write('%-9s %-6s %-9s %-8s %-13s %-8s %s\n' % ('program', 'call', 'HL file',
                                                          'DE', 'same file OPEN w1',
                                                          'BC', 'routines after the attach'))
        for r in rows:
            fh.write('%-9s %-6s %-9s 0x%-6s %-13s %-8s %s\n' % (
                r['program'], r['call'], r['hl'], r['de'], r['w1'], r['bc'], r['after']))
    print('%s: %d attach sites in %d distinct objects' % (out, len(rows), len(seen)))
    # the relation, stated as data
    same = diff = 0
    print()
    print('DE vs OPEN w1 (same file):')
    for r in rows:
        if r['w1'] == '-':
            continue
        for v in r['w1'].split('/'):
            w = int(v, 16)
            d = int(r['de'], 16)
            tag = 'DE == w1 & ~0x4800' if d == (w & ~0x4800) else 'DE != w1 & ~0x4800'
            print('   %-9s %-9s w1=0x%04X DE=0x%04X  %-20s  delta bits 0x%04X' % (
                r['program'], r['hl'], w, d, tag, w ^ d))
            same += tag.startswith('DE ==')
            diff += not tag.startswith('DE ==')
    print('   %d of %d sampled attaches equal w1 with the TITLE(0x0800) and '
          'ENVIRONMENT(0x4000) bits cleared' % (same, same + diff))
    print('   %d match, %d do not' % (same, diff))


if __name__ == '__main__':
    main()
