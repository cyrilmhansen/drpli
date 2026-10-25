#!/usr/bin/env python3
"""iowindows.py -- the code AROUND every file-I/O routine call in the historical programs.

openblocks.py decodes OPEN (and CLOSE) blocks exactly.  This tool answers the narrower
question a first implementation slice needs: for the other I/O routines DR chains to,
what does the code immediately before and after the CALL look like, and is it the same
in every program that uses the routine?

It prints, for one object per program, up to four instructions before each call and two
after, with the operand of every relocated slot named.  Nothing here is a conclusion --
the point is to see which routines share a shape (so one lowering can serve them) and
which need their own probe work before any claim can be made.

Routines listed: the OPEN family (?OIOOP), CLOSE (?CIOOP), the stream attach
(?SIOOP), the io-close that follows a list (?QIOOP), WRITE (?WNIOP), and the console
file anchors already reproduced by this compiler (?SYSIN console input, ?SYSPR output).

Run:  python3 iowindows.py            (writes IOWINDOWS.txt next to this script)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for _p in (HERE, os.path.join(ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import e41rel as E       # noqa: E402
import openblocks as OB  # noqa: E402

PROGS = ['COPYLPT', 'COPY', 'CREATE', 'DEPREC', 'ENTER', 'KEYFILE', 'LOAN2', 'REPORT',
         'RETRIEVE', 'UPDATE']
ROUTINES = ['?OIOOP', '?CIOOP', '?SIOOP', '?QIOOP', '?WNIOP', '?SYSIN', '?SYSPR',
            '?GNVOP', '?SSVFS', '?QCIOP', '?PAGOP']
BACK, FWD = 4, 2


def line(code, rmap, I, a):
    op, mn, n = I[a]
    raw = ' '.join('%02X' % code[a + i] for i in range(n) if a + i < len(code))
    extra = ''
    lo, hi = rmap.get(a + 1), rmap.get(a + 2)
    if n == 3 and (lo or hi):
        extra = '   ; RELOC -> %s / %s' % (OB.name_of(rmap, a + 1) or '??????',
                                           OB.name_of(rmap, a + 2) or '??????')
    elif n == 3:
        extra = '   ; IMM 0x%04X' % (code[a + 1] | (code[a + 2] << 8))
    elif n == 2:
        extra = '   ; IMM 0x%02X' % code[a + 1]
    return '      %04X  %-22s ; %-9s%s' % (a, mn, raw, extra)


def main():
    print('# windows around each file-I/O CALL, one object per historical program')
    print('# routines: %s' % ' '.join(ROUTINES))
    for prog in PROGS:
        rel = None
        for base in ('first8080u', 'first', 'bind1'):
            c = os.path.join(ROOT, 'golden', base, prog, prog + '.REL')
            if os.path.exists(c):
                rel = c
                break
        if rel is None:
            print('\n== %s: no object in golden/' % prog)
            continue
        _ev, code, rmap, ext, layout, total = E.replay(rel)
        I = OB.decode(code)
        by_addr = {}
        for a, (op, mn, n) in I.items():
            by_addr[a] = (op, mn, n)
        starts = sorted(by_addr)
        print('\n== %s   %s   code=%d bytes, COMMON=%d bytes' % (
            prog, os.path.relpath(rel, ROOT), len(code), total))
        counts = {}
        for slot in sorted(ext):
            nm = ext[slot]
            if nm not in ROUTINES:
                continue
            counts[nm] = counts.get(nm, 0) + 1
            call = slot - 1
            i = starts.index(call) if call in starts else None
            if i is None:
                print('   %s at slot %04X: CALL operand is not an instruction start'
                      % (nm, slot))
                continue
            print('   --- %s call at %04X' % (nm, call))
            for a in starts[max(0, i - BACK):min(len(starts), i + 1 + FWD)]:
                print(line(code, rmap, I, a))
        print('   call counts: %s' % ' '.join('%s=%d' % kv for kv in sorted(counts.items())))


if __name__ == '__main__':
    main()
