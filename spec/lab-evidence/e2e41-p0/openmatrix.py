#!/usr/bin/env python3
"""openmatrix.py -- inventory + argument matrix of every DR OPEN block in the repo.

Writes two files next to this script:

  OPEN-INVENTORY.txt   every .REL under golden/ (and extracted/, if any) that carries a
                       CHAIN-EXT for an open routine, with its SHA-256 prefix, so the
                       duplicates across golden/first, golden/first8080u and
                       golden/bind1 show up as duplicates instead of extra evidence.

  OPEN-MATRIX.tsv      one row per OPEN SITE (not per program): the source statement,
                       each option word in push order with its .REL kind
                       (IMM = constant in the object, REF = relocated address,
                       PRE = value built outside the block), the title helper called,
                       and the COMMON group holding the file's control block.

The row is joined to its SOURCE statement by order: the i-th ?OIOOP call site in the
object is the i-th OPEN statement in the program text.  That is true for every object
scanned here (the block count equals the statement count in all of them, checked in
OPEN-BLOCKS.txt), and it is what lets the matrix carry option columns at all.

Run:  python3 openmatrix.py
"""
import csv
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for _p in (HERE, os.path.join(ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import e41rel as E          # noqa: E402
import openblocks as OB     # noqa: E402

SRCDIRS = ['artefacts', 'probes', 'e12src', 'e13src', 'e14src', 'e15src', 'e16src',
           'e17src', 'e18src', 'e19src', 'e20src', 'e21src', 'e22src']
COLS = ['program', 'rel', 'line', 'statement', 'keyed', 'direct', 'stream',
        'input', 'output', 'update', 'append', 'print', 'environment',
        'F', 'B', 'linesize-literal', 'pagesize-literal', 'title-kind',
        'title-helper', 'cb-group', 'block-start', 'block-bytes',
        'w1', 'w2', 'w3', 'w4', 'w5', 'w6']


def find_source(base):
    for d in SRCDIRS:
        for suf in ('.PLI', '.PL', '.pli'):
            c = os.path.join(ROOT, d, base + suf)
            if os.path.exists(c):
                return c
    return None


def opt_flags(text):
    """Which option words the SOURCE statement spells.  Literal-valued LINESIZE and
    PAGESIZE are separated from variable-valued ones because only the former can
    appear as an immediate in the object."""
    t = text.upper()
    g = lambda p: 'Y' if re.search(p, t) else '-'      # noqa: E731
    env = re.search(r'ENVIRONMENT\s*\(([^)]*)\)', t)
    fnum = re.search(r'\bF\s*\(\s*(\d+)', env.group(1)) if env else None
    bnum = re.search(r'\bB\s*\(\s*(\d+)', env.group(1)) if env else None
    return dict(
        keyed=g(r'\bKEYED\b'), direct=g(r'\bDIRECT\b'), stream=g(r'\bSTREAM\b'),
        input=g(r'\bINPUT\b'), output=g(r'\bOUTPUT\b'), update=g(r'\bUPDATE\b'),
        append=g(r'\bAPPEND\b'), print_=g(r'\bPRINT\b'),
        env='Y' if env else '-',
        f=('Y:' + fnum.group(1)) if fnum else '-',
        b=('Y:' + bnum.group(1)) if bnum else '-',
        linesize=g(r'\bLINESIZE\s*\(\s*\d+\s*\)'),
        pagesize=g(r'\bPAGESIZE\s*\(\s*\d+\s*\)'),
        title=('lit' if re.search(r"TITLE\s*\(\s*'", t) else
               ('var' if re.search(r'TITLE\s*\(\s*[A-Z_$]', t) else '-')),
    )


def word_field(w):
    if w['hex']:
        return 'IMM:0x' + w['hex']
    return w['ref'] or w['kind']


def main():
    paths = sorted(set(glob.glob(os.path.join(ROOT, 'golden', '**', '*.REL'),
                                 recursive=True)
                       + glob.glob(os.path.join(ROOT, 'extracted', '**', '*.REL'),
                                   recursive=True)))
    scanned = 0
    dig = {}
    for p in paths:
        try:
            blocks, _total = OB.collect(p)
        except Exception:                                  # noqa: BLE001
            continue
        scanned += 1
        if not blocks:
            continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        dig.setdefault(h, []).append((p, len(blocks)))
    inv = os.path.join(HERE, 'OPEN-INVENTORY.txt')
    n = 0
    with open(inv, 'w') as fh:
        fh.write('# DR objects carrying an OPEN lowering (a CHAIN-EXT for ?OIOOP)\n')
        fh.write('# %d .REL files scanned under golden/ and extracted/ (%d parsed)\n'
                 % (len(paths), scanned))
        fh.write('# grouped by SHA-256 prefix: one block per DISTINCT object, listing\n'
                 '# every path with those exact bytes -- golden/first, first8080u and\n'
                 '# bind1 hold copies of the same oracle output, and a copy is not\n'
                 '# independent evidence.\n')
        for h, lst in sorted(dig.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            n += len(lst)
            fh.write('\n%s  %d OPEN block(s)\n' % (h, lst[0][1]))
            for p, _c in lst:
                fh.write('    %s\n' % os.path.relpath(p, ROOT))
        fh.write('\n%d distinct objects, %d file copies\n' % (len(dig), n))
    print('%s: %d distinct objects, %d file copies' % (inv, len(dig), n))

    tsv = os.path.join(HERE, 'OPEN-MATRIX.tsv')
    rows = []
    for h, lst in sorted(dig.items()):
        p = lst[0][0]
        base = os.path.basename(p)[:-4]
        src = find_source(base)
        stmts = E.open_stmts(src) if src else []
        blocks, _total = OB.collect(p)
        for bi, b in enumerate(blocks):
            st = stmts[bi] if bi < len(stmts) else (0, 0, '(source has fewer OPENs)')
            f = opt_flags(st[2])
            r = dict(program=base, rel=os.path.relpath(p, ROOT),
                     line='%d-%d' % (st[0], st[1]), statement=st[2],
                     keyed=f['keyed'], direct=f['direct'], stream=f['stream'],
                     input=f['input'], output=f['output'], update=f['update'],
                     append=f['append'], print=f['print_'], environment=f['env'],
                     F=f['f'], B=f['b'], **{'linesize-literal': f['linesize'],
                                            'pagesize-literal': f['pagesize'],
                                            'title-kind': f['title'],
                                            'title-helper': b['title'],
                                            'cb-group': b['cb'],
                                            'block-start': '%04X' % b['start'],
                                            'block-bytes': str(b['end'] - b['start'])})
            for i, w in enumerate(b['words']):
                r['w%d' % (i + 1)] = word_field(w)
            rows.append(r)
    with open(tsv, 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=COLS, delimiter='\t', restval='-',
                            lineterminator='\n', extrasaction='ignore')
        wr.writeheader()
        for r in rows:
            wr.writerow(r)
    print('%s: %d rows (%d columns)' % (tsv, len(rows), len(COLS)))
    for r in rows:
        print('  %-9s %-6s %-46s w1=%-10s w2=%-9s w3=%-9s w4=%-9s w5=%-9s w6=%-9s  %s %s'
              % (r['program'], r['line'], r['statement'][:46], r['w1'], r['w2'], r['w3'],
                 r['w4'], r['w5'], r['w6'], r['title-kind'], r['cb-group']))


if __name__ == '__main__':
    main()
