#!/usr/bin/env python3
"""bitfit.py -- which bit of w1 tracks which OPEN option?

w1 is a 16-bit word DR emits as a compile-time IMMEDIATE.  Across the corpus its
low bits stay put for one organisation/mode combination and its high three bits
(0x1000, 0x2000, 0x4000) move with the presence of LINESIZE, PAGESIZE and
ENVIRONMENT.  This script does not assume that; it tests, for every bit, whether
the bit splits the sample set cleanly along each option flag, and reports the
bits where no flag explains it.

Reads OPEN-MATRIX.tsv (written by openmatrix.py).  Rows whose w1 is not an IMM
(variable-valued options: the word is built by code outside the block) are listed
separately and never used to support a bit claim.
"""
import csv
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

def composite(r):
    """The two derived columns the raw option words do not give you.

    ORG is the file ORGANISATION DR was told to use; a statement that names none
    (P072H `open file(f) input;') still gets STREAM, because that is what a bare
    `declare f file;' means -- the row's own w1 confirms it, it is the same value
    as an explicit `stream' with the same mode.
    MODE is what the file is opened FOR; a statement with no mode keyword is an
    INPUT open (that is PL/I's default, and E16A/E17A's w1 equals P021's explicit
    `input' value 0x0E90, so DR agrees).
    """
    org = ('KEYED' if r['keyed'] == 'Y' else 'DIRECT' if r['direct'] == 'Y'
           else 'STREAM')
    mode = ('PRINT' if r['print'] == 'Y' else 'OUTPUT' if r['output'] == 'Y'
            else 'UPDATE' if r['update'] == 'Y' else 'APPEND' if r['append'] == 'Y'
            else 'INPUT')
    st = r['statement'].upper()
    # LINESIZE/PAGESIZE are taken from the STATEMENT, not from the literal-only matrix
    # column: COPYLPT's `pagesize(pagesize) linesize(pagewidth)' sets both bits with
    # variables, so what the bit marks is the PRESENCE of the option, not a literal.
    return {'ORG': org, 'MODE': mode,
            'TITLE': 'Y' if r['title-kind'] in ('lit', 'var') else '-',
            'ENV': r['environment'],
            'LINESIZE': 'Y' if re.search(r'\bLINESIZE\s*\(', st) else '-',
            'PAGESIZE': 'Y' if re.search(r'\bPAGESIZE\s*\(', st) else '-',
            'F': 'Y' if r['F'].startswith('Y') else '-',
            'B': 'Y' if r['B'].startswith('Y') else '-'}


FLAGS = ['ORG', 'MODE', 'TITLE', 'ENV', 'LINESIZE', 'PAGESIZE', 'F', 'B']


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'OPEN-MATRIX.tsv')),
                               delimiter='\t'))
    imm = [r for r in rows if r['w1'].startswith('IMM:')]
    pre = [r for r in rows if not r['w1'].startswith('IMM:')]
    print('%d OPEN sites; %d with an immediate w1, %d built outside the block'
          % (len(rows), len(imm), len(pre)))
    for r in pre:
        print('   excluded (w1 = %s): %-9s %s' % (r['w1'], r['program'], r['statement'][:70]))
    print()
    print('the whole w1 population:')
    seen = defaultdict(list)
    for r in imm:
        seen[int(r['w1'].split('0x')[1], 16)].append(
            '%s:%s' % (r['program'], r['line']))
    for v in sorted(seen):
        print('   0x%04X (%5d)  %s' % (v, v, ', '.join(seen[v])))
    print()
    print('bit x option: does the bit separate rows with the option set from rows without?')
    hdr = '%-6s %-18s %s' % ('bit', 'option', 'verdict')
    print(hdr)
    for bit in range(16):
        m = 1 << bit
        setb = [r for r in imm if int(r['w1'].split('0x')[1], 16) & m]
        un = [r for r in imm if not int(r['w1'].split('0x')[1], 16) & m]
        if not setb or not un:
            print('%-6s %-18s %s' % ('0x%04X' % m, '(constant %s)' % ('set' if setb else 'clear'),
                                     'no discrimination in this population'))
            continue
        verdicts = []
        comps = {id(r): composite(r) for r in imm}
        for f in FLAGS:
            def val(r, f=f):
                v = comps[id(r)][f]
                return '-' if v in ('-', '') else v
            a = set(val(r) for r in setb)
            b = set(val(r) for r in un)
            if a and b and not (a & b):
                verdicts.append('%s: set only when %s=%s' % (f, f, ','.join(sorted(a))))
        print('%-6s %-18s %s' % ('0x%04X' % m, '', '; '.join(verdicts) or
                                 'NOT cleanly explained by any single option column'))
    print()
    print('per-row option summary (immediate w1 only):')
    print('   %-9s %-6s %-7s %-6s %-6s' % ('prog', 'line', 'org', 'mode', 'title'))
    for r in imm:
        c = composite(r)
        print('   %-9s %-6s %-7s %-6s %-6s  %s' % (
            r['program'], r['line'], c['ORG'], c['MODE'], c['TITLE'], r['w1']))
    print()
    print('   %-9s %-6s %-5s %-5s %-4s %-4s %-4s %-4s %-4s %-4s %-7s %s' % (
        'prog', 'line', 'title', 'env', 'F', 'B', 'keyd', 'dire', 'stre', 'in', 'out/up/pr', 'w1'))
    for r in imm:
        print('   %-9s %-6s %-5s %-5s %-4s %-4s %-4s %-4s %-4s %-4s %-4s%-3s %s' % (
            r['program'], r['line'], r['title-kind'], r['environment'], r['F'], r['B'],
            r['keyed'], r['direct'], r['stream'], r['input'],
            r['output'] + r['update'] + r['print'], '', r['w1']))


if __name__ == '__main__':
    main()
