#!/usr/bin/env python3
"""dis80 -- disassemble the CODE segment of a PL/I-80 .REL, symbolically.

Purpose (E2E-13): DR's own $C listing shows generated code for ITS compile, but there is
no listing for the object MY compiler produced, and comparing raw bytes cannot answer
"which instruction does DR use here".  This decodes a REL's code segment into mnemonics,
leaving relocated operands VISIBLE as their link field so that a call target, a chain head
or a DATA address cannot be mistaken for an absolute constant:

    007E  LHLD 14              (plain)
    007E  LHLD <DATA->XREF #N> (relocated operand)

It parses the output of tools/reldump.py rather than re-implementing the bit-packed
decoder: reldump has a pinned selftest (C125/C137 discipline) and two independent
decoders of a format this subtle is an invitation to compare the wrong things.

Two modes.

  FILE.REL [start]  -- from the bit-packed object.  KNOWN LIMITATION (E2E-13): bytes
     belonging to some RELOC-carrying operands do not surface as DATA records in
     reldump's dump, so they print as `.'.  Use this to read link fields, not to prove
     the absence of a byte.
  --com FILE.COM [start] [end]  -- from a LINKED image, where every operand is resolved
     and the byte stream is unambiguous.  PL/I-80 .COM origin is 0x0100 and the program
     starts at 0x0101, so file offset = load address - 0x100.  This is the mode to use
     for comparing DR's code against mine: it shows what actually executes.

Usage:  python3 tools/dis80.py [--com] FILE [start-hex] [end-hex]
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

# DR's OWN mnemonic/length table, LEARNED from 60 matched ($C listing, linked .COM)
# pairs in golden/ (E2E-13).  For each program: parse the $C code lines, take the byte at
# (file offset == code address), and record opcode -> printed mnemonic and opcode ->
# address delta.  Candidate image offsets were accepted only when EVERY LXI line's byte
# was one of 01/11/21/31 and EVERY CALL line's byte was a CALL opcode -- two facts pinned
# independently by byte-exact goldens, so the offset is located without assuming the rest.
# 43 opcodes, ZERO printed with more than one mnemonic.
#
# Why this exists: I first hand-wrote an 8080 table from memory and it read 0xB6 as XRA,
# which made DR's `ORA M' zero test look like a compiler bug.  DR's own data says 0xB6 =
# ORA and 0xAF = XRA (ORA base 0xB0, XRA base 0xA8), agreeing with this project's
# parity-derived rules `0xaf=XRA A' and `CMP M=0xBE / SBB M=0x9E'.  My memory was the
# defect, not DR.  Opcodes absent from this table print as DB nn -- never guessed.
DR80 = {
    0x01: ('LXI  B', 3), 0x11: ('LXI  D', 3), 0x21: ('LXI  H', 3),
    0x06: ('MVI  B', 2), 0x0E: ('MVI  C', 2), 0x16: ('MVI  D', 2), 0x1E: ('MVI  E', 2),
    0x26: ('MVI  H', 2), 0x2E: ('MVI  L', 2), 0x3E: ('MVI  A', 2), 0x36: ('MVI  M', 2),
    0x0D: ('DCR  C', 1), 0x05: ('DCR  B', 1), 0x25: ('DCR  H', 1), 0x2D: ('DCR  L', 1),
    0x35: ('DCR  M', 1), 0x34: ('INR  M', 1), 0x0C: ('INR  C', 1), 0x2C: ('INR  L', 1),
    0x12: ('STAX D', 1), 0x02: ('STAX B', 1), 0x0A: ('LDAX B', 1), 0x1A: ('LDAX D', 1),
    0x13: ('INX  D', 1), 0x23: ('INX  H', 1), 0x03: ('INX  B', 1), 0x33: ('INX  SP', 1),
    0x0B: ('DCX  B', 1), 0x1B: ('DCX  D', 1), 0x2B: ('DCX  H', 1), 0x3B: ('DCX  SP', 1),
    0x09: ('DAD  B', 1), 0x19: ('DAD  D', 1), 0x29: ('DAD  H', 1), 0x39: ('DAD  SP', 1),
    0x22: ('SHLD', 3), 0x2A: ('LHLD', 3), 0x32: ('STA', 3), 0x3A: ('LDA', 3),
    0x87: ('ADD  A', 1), 0x80: ('ADD  B', 1), 0x86: ('ADD  M', 1),
    0x9F: ('SBB  A', 1), 0x97: ('SBB  M', 1), 0x9E: ('SBB  M', 1),
    0xA0: ('ANA  B', 1), 0xAF: ('XRA  A', 1), 0xB6: ('ORA  M', 1), 0xB7: ('ORA  A', 1),
    0xBE: ('CMP  M', 1), 0xBF: ('CMP  A', 1),
    0xC1: ('POP  B', 1), 0xD1: ('POP  D', 1), 0xF1: ('POP  PSW', 1),
    0xC5: ('PUSH B', 1), 0xD5: ('PUSH D', 1), 0xE5: ('PUSH H', 1), 0xF5: ('PUSH PSW', 1),
    0xC2: ('JNZ', 3), 0xCA: ('JZ', 3), 0xC3: ('JMP', 3), 0xCD: ('CALL', 3),
    0xF2: ('JP', 3), 0xFA: ('JM', 3), 0xC9: ('RET', 1), 0xEB: ('XCHG', 1), 0x00: ('NOP', 1),
}
# MOV r,m family 0x40-0x7F (dst bits 5-3, src bits 2-0, B C D E H L M A) -- learned
# directly for 0x56/0x5E/0x67/0x6F/0x7D/0x7E, all printed MOV, all consistent.
R8 = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
# ALU group, in the order DR's own table proves: 0x80 ADD, 0x88 ADC, 0x90 SUB, 0x98 SBB,
# 0xA0 ANA, 0xA8 XRA, 0xB0 ORA, 0xB8 CMP  (note: XRA BEFORE ORA -- the opposite of the
# order I first wrote from memory, which is what produced the false 0xB6=XRA reading).
ALU = ['ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP']

def decode(pc, b, xref):
    o = b[0]
    if not isinstance(o, int):
        return ('?' + str(o), 1)
    if 0x40 <= o <= 0x7F:
        if o == 0x76:
            return ('HLT', 1)
        return ('MOV  %s,%s' % (R8[(o >> 3) & 7], R8[o & 7]), 1)
    if 0x80 <= o <= 0xBF:
        return ('%s %s' % (ALU[(o >> 3) & 7], R8[o & 7]), 1)
    if o in DR80:
        mne, n = DR80[o]
        if n == 1:
            return (mne, 1)
        if n == 2:
            return ('%s %s' % (mne, _imm(b)), 2)
        return ('%s %s' % (mne, _addr(b) if mne[:3] not in ('LXI',) else _lxi(b)), 3)
    return ('DB %02X' % o, 1)

def _imm(b):
    return ('%02X' % b[1]) if isinstance(b[1], int) else str(b[1])

def _lxi(b):
    lo, hi = b[1], b[2]
    if isinstance(lo, int) and isinstance(hi, int):
        return '%04X' % (hi << 8 | lo)
    return '%s/%s' % (str(lo), str(hi))

def _addr(b):
    lo, hi = b[1], b[2]
    if isinstance(lo, int) and isinstance(hi, int):
        return '%04X' % (hi << 8 | lo)
    return '%s/%s' % (str(lo), str(hi))

def code_and_xrefs(path):
    """Parse reldump's text output: code bytes, plus which addresses carry a link field.

    A 16-bit reloc field in PL/I-80 .REL is anchored at the address of the operand LOW
    byte and covers that byte and the next: reldump shows `CALL ?SVBLK' as DATA code 003F
    0xcd with LINK-CHAIN-EXT code 0040 ?SVBLK, i.e. anchor = 003F+1.  Marking the anchor
    plus TWO bytes would swallow the following opcode, so the span is exactly 2.
    """
    out = subprocess.run([sys.executable, os.path.join(HERE, 'reldump.py'), path],
                         capture_output=True, text=True).stdout
    code, xref = {}, {}
    for line in out.splitlines():
        f = line.split()
        # reldump prints: `  @ <bit> <KIND> <SEG> <ADDR> <VALUE-or-TARGET>'
        #                    f[0]='@' f[1]=bit f[2]=KIND f[3]=SEG f[4]=ADDR f[5]=VALUE
        if len(f) < 5 or f[0] != '@':
            continue
        kind, seg = f[2], f[3]
        if seg != 'code':
            continue
        if kind == 'DATA':
            # `DATA code 0006 0x21'  ->  addr f[4] (no prefix), value f[5] (0x form)
            if len(f) < 6 or not f[5].startswith('0x'):
                continue
            code[int(f[4], 16)] = int(f[5], 16)
        else:
            a = int(f[4], 16)
            tgt = f[5] if len(f) > 5 else '?'
            for k in (a, a + 1):
                xref[k] = tgt
    return code, xref

def com_bytes(path, start, end):
    d = open(path, 'rb').read()
    # file offset = load address - 0x100 (CCP origin); program itself starts at 0x0101
    a = start if start else 0x0101
    b = end if end else 0x100 + len(d)
    return {i: d[i - 0x100] for i in range(a, min(b, 0x100 + len(d)))}, {}

def disasm(path, start=0):
    code, xref = code_and_xrefs(path)
    if not code:
        print('%s: no code bytes parsed' % path)
        return
    def byte(i):
        if isinstance(code.get(i), int):
            return code[i]
        if i in xref:
            return '<' + xref[i] + '>'
        return None
    if start:
        pc = min([a for a in sorted(code) if a >= start] or sorted(code))
    else:
        pc = min(sorted(code))
    end = max(code)
    while pc <= end:
        b = [byte(pc), byte(pc + 1), byte(pc + 2)]
        if b[0] is None:
            print('%04X  . (gap)' % pc); pc += 1; continue
        txt, n = decode(pc, b, xref)
        raw = ' '.join('%02X' % b[i] if isinstance(b[i], int) else
                       ('%-8s' % b[i] if b[i] else '  .') for i in range(min(n, 3)))
        print('%04X  %-26s ; %s' % (pc, txt, raw))
        pc += n

if __name__ == '__main__':
    args = sys.argv[1:]
    mode = 'rel'
    if args and args[0] == '--com':
        mode, args = 'com', args[1:]
    if args and args[0] == '--rel':
        mode, args = 'rel', args[1:]
    path = args[0]
    start = int(args[1], 16) if len(args) > 1 else 0
    end = int(args[2], 16) if len(args) > 2 else 0
    if mode == 'com':
        code, xref = com_bytes(path, start, end)
    else:
        code, xref = code_and_xrefs(path)
    if not code:
        print('%s: no code bytes parsed' % path); sys.exit(1)
    def byte(i):
        if isinstance(code.get(i), int):
            return code[i]
        if i in xref:
            return '<' + xref[i] + '>'
        return None
    pc = start if start else min(code)
    stop = end if end else max(code)
    while pc <= stop:
        b = [byte(pc), byte(pc + 1), byte(pc + 2)]
        if b[0] is None:
            print('%04X  . (gap)' % pc); pc += 1; continue
        txt, n = decode(pc, b, xref)
        raw = ' '.join('%02X' % b[i] if isinstance(b[i], int) else
                       ('%-8s' % b[i] if b[i] else '  .') for i in range(min(n, 3)))
        print('%04X  %-26s ; %s' % (pc, txt, raw))
        pc += n
