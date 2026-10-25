#!/usr/bin/env python3
"""openblocks.py -- every file-open (and file-close) block in every object that has one.

HOW A BLOCK IS FOUND (no line numbers, no guessing):

  1. e41rel.replay() replays the object's bitstream, keeping the RELOC attached to
     each code byte.  (tools/reldump.py's disassembly TEXT truncates on large
     objects -- on COPYLPT it stops at code 00E6 of 2A02 bytes -- and a truncated
     byte map silently shortens every block decoded from it.)
  2. Instruction boundaries come from a linear decode with tools/dis80.py's DR80
     length table, learned from 60 matched DR listing/image pairs [C125/C137
     discipline].  Opcodes that table lacks (the single-byte MOV forms 47/60/65/68/6C)
     decode as `DB nn` with length 1, which keeps every boundary correct.
  3. A LINK-CHAIN-EXT record naming the routine (?OIOOP for OPEN, ?CIOOP for CLOSE)
     is anchored at the CALL's operand slot, so the CALL itself is at slot-1.
  4. Walk BACKWARD over instruction starts, collecting PUSH H words.  An OPEN block
     pushes exactly SIX words, so the walk stops as soon as it has six; it then keeps
     going only while the opcode belongs to a title prologue (INX SP, PUSH B, MOV B,A,
     XRA A, MVI A, CALL ?SLCTS|?SLVTS, LXI H) and stops after the instruction that
     supplies the title address (LXI H) or the no-title zero (XRA A).  Any other
     instruction ends the walk and the block is reported with whatever it found, so a
     shape outside this rule shows up as an anomaly instead of being silently absorbed.

WHAT EACH PUSHED WORD IS PRINTED AS

  IMM:<hex>    two DATA bytes -- a compile-time constant.
  REF:<desc>   the halves carry RELOC records -- an address, named by segment and,
               for COMMON, by the group the preceding SEL-COMMON selected.
  PRE          a half was set by code outside the block (a variable option value).
  MIXED        one half relocated, one immediate (never observed).

The IMM/REF split is the point of the tool.  In the LINKED .COM both look like plain
numbers, and reading a number as an address or a constant without checking the
relocation stream is the documented trap [C264]: ENTER's third push reads as `1F40`
in the image and is the constant 8000, the B(8000) buffer size.

Register state is tracked across the walk because DR does not always build a pushed
word with LXI H: `XRA A / MOV B,A / MOV H,B / MOV L,B` pushes 0x0000, and
`MOV L,H / MOV H,L / XCHG` collapses HL to a repeated byte.

CLI:
  python3 openblocks.py                       every distinct OPEN-bearing object
  python3 openblocks.py --routines=?CIOOP     the same walk for CLOSE
  python3 openblocks.py --only=ENTER,COPY     one or more programs, all copies
"""
import glob
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for _p in (HERE, os.path.join(ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import e41rel as E          # noqa: E402
from dis80 import DR80      # noqa: E402

OPEN_ROUTINES = ('?OIOOP',)
CLOSE_ROUTINES = ('?CIOOP',)
TITLE_CALLS = ('?SLCTS', '?SLVTS')
PUSH_H, PUSH_B, INX_SP, CALL, XRA_A, MVI_A, LXI = 0xE5, 0xC5, 0x33, 0xCD, 0xAF, 0x3E, 0x21
TITLE_OPS = {INX_SP, PUSH_B, 0x47, XRA_A, MVI_A, CALL, LXI}
LHLD = 0x2A          # HL <- a WORD in DATA: how DR loads a VARIABLE option value
HL_OPS = {LXI, 0x2E, 0x26, 0x6C, 0x65, 0x60, 0x68, 0xEB, LHLD}
SETUP_OPS = HL_OPS | {PUSH_H}
WORDS_PER_OPEN = 6
TAGS = ['w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7', 'w8']


def decode(code):
    """{addr: (opcode, mnemonic, length)} over the whole code segment."""
    out, pc, n = {}, 0, len(code)
    while pc < n:
        op = code[pc]
        info = DR80.get(op)
        if info is None:                   # opcode absent from the DR80 table
            out[pc] = (op, 'DB %02X' % op, 1)
            pc += 1
            continue
        ln = min(info[1], n - pc)          # a truncated tail stays inside the array
        out[pc] = (op, info[0], ln)
        pc += ln
    return out


def name_of(rmap, a):
    """How DR's own reloc would be printed for the operand half at code address `a'."""
    p = rmap.get(a)
    if not p:
        return None
    seg, idx, grp = p
    return '%s%s+0x%04X' % (seg, ('/%s/' % grp) if grp else '', idx)


def collect(rel, routines=OPEN_ROUTINES):
    """(blocks, common_bytes_total) for one .REL object.  See the module docstring."""
    _ev, code, rmap, ext, _layout, common_total = E.replay(rel)
    I = decode(code)
    ends = {}
    for a, (op, mn, n) in I.items():
        ends[a + n] = (a, op, mn, n)
    blocks = []
    for slot in sorted(a for a, nm in ext.items() if nm in routines):
        call = slot - 1
        addrs = [call]
        pc, pushes, done_title = call, 0, False
        while True:
            prev = ends.get(pc)
            if prev is None:
                break
            a, op, mn, n = prev
            if pushes >= WORDS_PER_OPEN or routines == CLOSE_ROUTINES:
                # past the six words: only a title prologue may still be behind us
                if op not in TITLE_OPS or (op == CALL and ext.get(a + 1) not in TITLE_CALLS):
                    break
                done_title = done_title or op in (LXI, XRA_A)
            elif op not in SETUP_OPS and not (op == CALL and ext.get(a + 1) in TITLE_CALLS):
                break
            addrs.append(a)
            if op == PUSH_H:
                pushes += 1
                if done_title:
                    break
            if done_title and op in (LXI, XRA_A) and a != addrs[0]:
                pass
            pc = a
        addrs.sort()
        seq, words = [], []
        H = L = B = A = None       # symbolic halves: ('IMM', v) / ('REF', (seg,idx,grp))

        def word():
            if H is None or L is None:
                return {'kind': 'PRE', 'hex': None, 'ref': None}
            if H[0] == L[0] == 'REF':
                return {'kind': 'REF', 'hex': None,
                        'ref': 'L:%s H:%s' % (H[1], L[1])}
            if H[0] == L[0] == 'IMM':
                return {'kind': 'IMM', 'hex': '%04X' % ((H[1] << 8) | L[1]), 'ref': None}
            if 'PRE' in (H[0], L[0]):
                return {'kind': 'PRE', 'hex': None,
                        'ref': 'value of the word at %s' % (H[1] if H[0] == 'PRE' else L[1])}
            return {'kind': 'MIXED', 'hex': None, 'ref': '%r/%r' % (H, L)}

        for a in addrs:
            op, mn, ln = I[a]
            if op == LXI:
                # the LOW half is the first operand byte (a+1), the HIGH half the second
                lo, hi = rmap.get(a + 1), rmap.get(a + 2)
                if lo or hi:
                    L = ('REF', name_of(rmap, a + 1) or '??????')
                    H = ('REF', name_of(rmap, a + 2) or '??????')
                else:
                    L = ('IMM', code[a + 1])
                    H = ('IMM', code[a + 2])
            elif op == LHLD:
                # HL <- the word stored at a DATA address: the value is a RUNTIME
                # variable's, so the pushed word is not knowable from the object
                L = H = ('PRE', name_of(rmap, a + 1) or 'data+0x%04X' % (
                    code[a + 1] | (code[a + 2] << 8)))
            elif op == 0x2E:
                L = ('IMM', code[a + 1])
            elif op == 0x26:
                H = ('IMM', code[a + 1])
            elif op == 0x6C:
                L = H
            elif op == 0x65:
                H = L
            elif op == 0x60:
                H = B
            elif op == 0x68:
                L = B
            elif op == 0xEB:
                H, L = L, H
            elif op == MVI_A:
                A = ('IMM', code[a + 1])
            elif op == XRA_A:
                A = ('IMM', 0)
            elif op == 0x47:
                B = A
            if op == PUSH_H:
                wd = word()
                wd['tag'] = TAGS[len(words)] if len(words) < len(TAGS) else 'w?'
                words.append(wd)
                tag = wd['tag']
                txt = '%04X  %-30s ; %s   -> %s' % (
                    a, mn, ' '.join('%02X' % code[a + i] for i in range(ln)),
                    ('IMM:0x' + wd['hex']) if wd['hex'] else (wd['ref'] or wd['kind']))
            elif op == CALL:
                nm = ext.get(a + 1, 'RELOC?')
                tag = 'title' if nm in TITLE_CALLS else 'call'
                txt = '%04X  %-30s ; %s   ; CHAIN-EXT -> %s' % (
                    a, 'CALL ' + str(nm),
                    ' '.join('%02X' % code[a + i] for i in range(ln)), nm)
            else:
                tag = 'title' if op in (PUSH_B, INX_SP, XRA_A, 0x47) else 'setup'
                note = {PUSH_B: 'push the title length byte',
                        INX_SP: 'drop the low half, keep SP even',
                        0x47: 'MOV B,A: copy the length to the high half',
                        XRA_A: 'no TITLE clause: length 0'}.get(op, '')
                lo, hi = rmap.get(a + 1), rmap.get(a + 2)
                if ln == 3 and (lo or hi):
                    txt = '%04X  %-30s ; %s   ; RELOC -> %s / %s' % (
                        a, mn, ' '.join('%02X' % code[a + i] for i in range(ln)),
                        name_of(rmap, a + 1) or '??????', name_of(rmap, a + 2) or '??????')
                else:
                    txt = '%04X  %-30s ; %s' % (
                        a, mn, ' '.join('%02X' % code[a + i] for i in range(ln)))
                if note:
                    txt += '   ; ' + note
            seq.append((a, tag, txt))
        cb = '-'
        for a, tag, txt in seq:
            if I[a][0] == LXI:
                p = rmap.get(a + 1) or rmap.get(a + 2)
                if p and p[0] == 'common' and p[2]:
                    cb = 'COMMON /%s/ +0x%04X' % (p[2], p[1])
                    break
        title = next((ext[a + 1] for a, tag, txt in seq
                      if I[a][0] == CALL and ext.get(a + 1) in TITLE_CALLS), '-')
        blocks.append({'routine': ','.join(routines), 'slot': slot, 'start': addrs[0],
                       'end': addrs[-1] + I[addrs[-1]][2], 'cb': cb, 'title': title,
                       'words': words, 'pushes': pushes,
                       'text': '\n'.join('    ' + t for _a, _tag, t in seq)})
    return blocks, common_total


def fmt(b):
    want = 0 if 'CIOOP' in b['routine'] else WORDS_PER_OPEN
    n = len(b['words'])
    head = ('  block %04X..%04X (%d bytes)  %d PUSH H, CALL %s at %04X   %s   '
            'title-helper=%s%s' % (b['start'], b['end'], b['end'] - b['start'], b['pushes'],
                                   b['routine'], b['slot'], b['cb'], b['title'],
                                   '' if n == want else
                                   '   *** %d words, expected %d ***' % (n, want)))
    lines = [head]
    for w in b['words']:
        lines.append('      %-3s = %s' % (w['tag'], 'IMM:0x' + w['hex'] if w['hex']
                                          else (w['ref'] or w['kind'])))
    lines.append(b['text'])
    return '\n'.join(lines)


def find_src(program):
    for cand in ('artefacts', 'probes', 'e13src'):
        p = os.path.join(ROOT, cand, program + '.PLI')
        if os.path.exists(p):
            return os.path.relpath(p, ROOT)
    return ''


def main():
    args = sys.argv[1:]
    routines = tuple(x for x in next((a.split('=', 1)[1] for a in args
                                     if a.startswith('--routines=')),
                                     '?OIOOP').split(',') if x)
    only = next((set(a.split('=', 1)[1].split(',')) for a in args
                 if a.startswith('--only=')), None)
    rows, seen = [], set()
    for p in sorted(set(glob.glob(os.path.join(ROOT, 'golden', '**', '*.REL'),
                                  recursive=True))):
        try:
            blocks, common_total = collect(p, routines)
        except Exception:
            continue
        if not blocks:
            continue
        program = os.path.basename(os.path.dirname(p))
        if only and program not in only:
            continue
        digest = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        if digest in seen and not only:
            continue
        seen.add(digest)
        src = find_src(program)
        stmts = ('; '.join('%d-%d: %s' % st for st in
                              E.open_stmts(os.path.join(ROOT, src)))
                   if src else '')
        print('== %s   [%s]   %d %s block(s), %d COMMON bytes, sha %s' % (
            os.path.relpath(p, ROOT), src or 'source not in repo', len(blocks),
            ','.join(routines), common_total, digest))
        for b in blocks:
            print(fmt(b))
        print()
        for b in blocks:
            rows.append(dict(program=program, rel=os.path.relpath(p, ROOT), src=src,
                             statement=stmts, start='%04X' % b['start'],
                             size=str(b['end'] - b['start']), pushes=str(b['pushes']),
                             cb=b['cb'], title=b['title'],
                             **{'w%d' % (i + 1): ('IMM:0x' + w['hex'] if w['hex']
                                                  else (w['ref'] or w['kind']))
                                for i, w in enumerate(b['words'])}))
    if '--emit-tsv' in args:
        import csv
        cols = (['program', 'rel', 'src', 'statement', 'start', 'size', 'pushes', 'cb',
                 'title'] + TAGS)
        path = os.path.join(HERE, 'OPEN-MATRIX.tsv')
        with open(path, 'w', newline='') as fh:
            wr = csv.DictWriter(fh, fieldnames=cols, delimiter='\t', restval='-',
                                lineterminator='\n', extrasaction='ignore')
            wr.writeheader()
            for r in rows:
                wr.writerow(r)
        print('%s: %d rows (%s)' % (path, len(rows), ','.join(routines)), file=sys.stderr)


if __name__ == '__main__':
    main()
