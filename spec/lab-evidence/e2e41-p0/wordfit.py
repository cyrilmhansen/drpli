#!/usr/bin/env python3
"""wordfit.py -- test a CANDIDATE reading of the six pushed words against every sample.

The candidate, assembled from the historical programs and the old probes:

    w1  a bit-packed option word (see W1-BITFIT.txt for which bit tracks what)
    w2  the ORGANISATION selector, present only when the statement has an
        ENVIRONMENT clause:  STREAM = 0x08, DIRECT = 0x10, KEYED = 0x18
    w3  the B(n) buffer size from ENVIRONMENT, 0 when no B(n)
    w4  the F(n) value from ENVIRONMENT; 128 when ENVIRONMENT is present without F(n);
        0 when there is no ENVIRONMENT clause at all
    w5  the PAGESIZE(n) literal, 0 otherwise
    w6  the LINESIZE(n) literal, 0 otherwise

This script does not decide whether the candidate is true -- it reports, row by row,
where the candidate AGREES with the object and where it does not, so a claim can be
scoped to exactly the rows that support it.  Rows whose words are built by code
outside the block (w = PRE) are listed and never counted as agreement.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORG_W2 = {'KEYED': 0x18, 'DIRECT': 0x10, 'STREAM': 0x08}


def num(field):
    v = field.split('IMM:0x')[1] if field.startswith('IMM:0x') else None
    return int(v, 16) if v else None


def want(row, key):
    """The literal the SOURCE asks for in an option like B(n)/F(n)/PAGESIZE(n)."""
    g = re.search(key + r'\s*\(\s*(\d+)\s*\)', row['statement'], re.I)
    if not g:
        return None
    return int(g.group(1))


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'OPEN-MATRIX.tsv')),
                               delimiter='\t'))
    bad = []
    ok = 0
    skipped = []
    print('%-9s %-6s %-4s %-4s %-6s %-6s %-6s %-6s %-6s %s' % (
        'prog', 'line', 'env', 'org', 'w2', 'w3', 'w4', 'w5', 'w6', 'verdict'))
    for r in rows:
        ws = [num(r[k]) for k in ('w1', 'w2', 'w3', 'w4', 'w5', 'w6')]
        if any(w is None for w in ws):
            skipped.append(r)
            continue
        env = r['environment'] == 'Y'
        org = ('KEYED' if r['keyed'] == 'Y' else 'DIRECT' if r['direct'] == 'Y'
               else 'STREAM')
        f, b = want(r, 'F'), want(r, 'B')
        ps, ls = want(r, 'PAGESIZE'), want(r, 'LINESIZE')
        exp2 = ORG_W2[org] if env else 0
        exp3 = b if b is not None else 0
        exp4 = (f if f is not None else 128) if env else 0
        exp5 = ps if ps is not None else 0
        exp6 = ls if ls is not None else 0
        got = [r['environment'], org[:4], '%04X' % ws[1], '%04X' % ws[2],
               '%04X' % ws[3], '%04X' % ws[4], '%04X' % ws[5]]
        errs = []
        for nm, e, g in (('w2', exp2, ws[1]), ('w3', exp3, ws[2]), ('w4', exp4, ws[3]),
                         ('w5', exp5, ws[4]), ('w6', exp6, ws[5])):
            if e != g:
                errs.append('%s expected %s got %04X' % (nm, ('%04X' % e), g))
        ok += not errs
        bad.append((r, errs))
        print('%-9s %-6s %-4s %-4s %-6s %-6s %-6s %-6s %-6s %s' % (
            r['program'], r['line'], got[0], got[1], got[2], got[3], got[4], got[5],
            got[6], 'OK' if not errs else 'MISMATCH: ' + '; '.join(errs)))
    print()
    print('%d rows agree with the candidate, %d do not, %d rows have words built '
          'outside the block and test nothing' % (ok, sum(1 for _r, e in bad if e),
                                                  len(skipped)))
    for r in skipped:
        print('   untested: %-9s %s   [%s]' % (r['program'], r['statement'][:64],
                                               ' '.join(r[k] for k in
                                                        ('w1', 'w2', 'w3', 'w4', 'w5', 'w6'))))
    # which SOURCE shapes does the tested population actually cover?
    print()
    print('coverage of the tested population:')
    shapes = {}
    for r, e in bad:
        if e:
            continue
        org = ('KEYED' if r['keyed'] == 'Y' else 'DIRECT' if r['direct'] == 'Y'
               else 'STREAM')
        mode = ('PRINT' if r['print'] == 'Y' else 'OUTPUT' if r['output'] == 'Y'
                else 'UPDATE' if r['update'] == 'Y' else 'INPUT')
        shapes.setdefault((org, mode, r['environment'], r['F'].startswith('Y'),
                           r['B'].startswith('Y'), r['linesize-literal'] == 'Y',
                           r['pagesize-literal'] == 'Y', r['title-kind']), []).append(
            '%s:%s' % (r['program'], r['line']))
    for k in sorted(shapes):
        print('   org=%-7s mode=%-7s env=%-2s F=%-2s B=%-2s linesize=%-2s pagesize=%-2s '
              'title=%-4s  <- %s' % (k[0], k[1], k[2] == 'Y', k[3], k[4], k[5], k[6],
                                     k[7], ', '.join(shapes[k])))


if __name__ == '__main__':
    main()
