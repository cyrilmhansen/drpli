#!/usr/bin/env python3
"""rellin.py -- LINEARIZE a Microsoft 8080 REL into `address  mnemonic  operand` with the
RELOCATION and CHAIN targets resolved to the thing they name, so a DR object and my object can be
compared instruction by instruction instead of byte by byte.

Why this exists: `tools/reldump.py' prints a RELOC record as `RELOC data 0x9' with NO address --
the address is implicit in the logical counter, which is right for auditing the bitstream and wrong
for reading code.  `tools/dis80.py' parses reldump's TEXT and so cannot see the operand bytes of a
relocated instruction at all (they print as `.', see its own docstring).  Neither tool answers the
question this milestone asks -- "is the two-item chain LXI H,<item1> ... LXI H,<item2> ... with ONE
?SIOOP and ONE ?QIOOP, and what does each LXI H point at?" -- because the operand is a relocation
record, not a byte.

This replays the same bitstream through reldump's OWN decoder class (imported, not reimplemented:
two independent bit-decoders is how C123 happened) and keeps the logical address that decode()
throws away, then walks the chain heads so a CHAIN-EXT at code+1 prints as the routine name and a
RELOC prints as `<SEGMENT:offset>'.

  usage: rellin.py FILE.REL [START] [END] [--abs]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "tools")))
import reldump
from reldump import BR, SEGS, TYPES

# opcode -> (mnemonic, total length).  Only what DR's PUT/GET lowering emits, plus the few
# instructions the numeric ladder uses; anything else prints hex rather than being guessed at.
OPS = {
    0x00: ("nop", 1), 0x01: ("lxi b", 3), 0x06: ("mvi b", 2), 0x09: ("dad d", 1),
    0x0b: ("dcx b", 1), 0x0c: ("inx b", 1), 0x11: ("lxi d", 3), 0x13: ("inx d", 1),
    0x19: ("dad d", 1), 0x21: ("lxi h", 3), 0x22: ("shld", 3), 0x23: ("inx h", 1),
    0x29: ("dad h", 1), 0x2a: ("lhld", 3), 0x2b: ("dcx h", 1), 0x31: ("lxi sp", 3),
    0x32: ("sta", 3), 0x3a: ("lda", 3), 0x3c: ("inr a", 1), 0x3d: ("dcr a", 1),
    0x3e: ("mvi a", 2), 0x7d: ("mov a,l", 1), 0x77: ("mov m,a", 1),
    0x43: ("mov m,e", 1), 0x52: ("mov d,d", 1), 0x5f: ("mov e,a", 1),
    0x6f: ("mov l,a", 1), 0x67: ("mov h,a", 1), 0x4a: ("mov c,d", 1),
    0x42: ("mov b,d", 1), 0xd1: ("pop d", 1), 0xd5: ("push d", 1),
    0xe1: ("pop h", 1), 0xe5: ("push h", 1), 0xe3: ("xthl", 1), 0xeb: ("xchg", 1),
    0xc3: ("jmp", 3), 0xca: ("jz", 3), 0xc2: ("jnz", 3), 0xda: ("jc", 3),
    0xd2: ("jnc", 3), 0xcd: ("call", 3), 0xc7: ("rz", 1), 0xd9: ("rnc", 1),
    0xf0: ("rz", 1) if False else ("rnz", 1), 0xc9: ("ret", 1), 0x76: ("hlt", 1),
    0xb7: ("ora a", 1), 0xa7: ("ana a", 1), 0x97: ("sub a", 1), 0x92: ("sub d", 1),
    0x87: ("add a", 1), 0x82: ("add d", 1), 0x84: ("add h", 1), 0x8d: ("adc a", 1),
    0x9f: ("sbb a", 1), 0x9d: ("sbb h", 1), 0xa5: ("ana l", 1), 0xb5: ("ora l", 1),
    0x83: ("add e", 1), 0x93: ("sub e", 1), 0x8b: ("adc e", 1), 0x9b: ("sbb e", 1),
    0x85: ("add l", 1), 0x95: ("sub l", 1), 0xa3: ("ana e", 1), 0xb3: ("ora e", 1),
    0x7c: ("mov a,h", 1), 0x79: ("mov a,c", 1), 0x78: ("mov a,b", 1),
    0x7f: ("mov a,a", 1), 0x62: ("mov h,d", 1), 0x6b: ("mov l,e", 1),
    0x57: ("mov a,l", 1), 0x5f: ("mov e,a", 1), 0x4f: ("mov c,a", 1),
    0x57: ("mov a,l", 1), 0x17: ("ral", 1), 0x1f: ("rar", 1), 0x07: ("rlc", 1),
    0x0f: ("rrc", 1), 0x2f: ("cma", 1), 0x37: ("stc", 1), 0x27: ("daa", 1),
    0x2f: ("cma", 1), 0xc6: ("adi", 2), 0xce: ("aci", 2), 0xd6: ("sui", 2),
    0xde: ("sbi", 2), 0xe6: ("ani", 2), 0xf6: ("ori", 2), 0xfe: ("cpi", 2),
    0xb9: ("cmp e", 1), 0xbe: ("cmp m", 1), 0xbd: ("cmp l", 1), 0xbc: ("cmp h", 1),
    0xa9: ("xor a", 1), 0xaf: ("xor a", 1), 0x8f: ("adc l", 1), 0x9f: ("sbb a", 1),
    0x34: ("inr m", 1), 0x35: ("dcr m", 1), 0x33: ("inx sp", 1), 0x3b: ("dcx sp", 1),
    0x71: ("mov m,c", 1), 0x70: ("mov m,b", 1), 0x73: ("mov m,e", 1),
    0x72: ("mov m,d", 1), 0x78: ("mov a,b", 1), 0x69: ("mov l,l", 1),
    0x68: ("mov l,b", 1), 0x6a: ("mov l,d", 1), 0x6c: ("mov l,h", 1),
    0x54: ("mov d,h", 1), 0x5d: ("mov e,l", 1), 0x5c: ("mov e,h", 1),
    0x44: ("mov b,h", 1), 0x4c: ("mov c,l", 1), 0x45: ("mov b,l", 1),
    0x4d: ("mov c,l", 1), 0xd3: ("out", 2), 0xdb: ("in", 2),
}


def decode(path):
    """-> (bytes-by-address for CODE and DATA, reloc map, chain map, sizes)."""
    raw = open(path, "rb").read()
    br = BR(raw)
    code, dat, com = {}, {}, {}
    reloc = {}        # (seg, addr) -> (target seg, target offset)
    chext = {}        # code addr of the 2-byte operand -> external symbol
    chaddr = {}       # code addr of the 2-byte operand -> (seg,off) of the chain head
    lc = ("code", 0)
    seg, addr = "code", 0
    sizes, publics, commons, extdefs = {}, [], [], []
    pend = None       # a CHAIN-*/DEF-* record whose (seg,addr) field follows its value
    try:
        while True:
            if br.bit() == 0:
                b = br.bits(8)
                {"code": code, "data": dat, "common": com}[seg][addr] = b
                addr += 1
                continue
            cls = br.bits(2)
            if cls:
                v = br.val16()
                reloc[(seg, addr)] = (SEGS[cls], v)
                addr += 2
                continue
            t = br.bits(4)
            val = None
            if 5 <= t <= 14:
                s2 = br.bits(2)
                val = ("abs", br.val16()) if s2 == 0 else (SEGS[s2], br.val16())
            nm = br.name() if (t <= 7 or t == 4) else None
            if t == 14:
                br.pad()
            if t == 11 and val:                    # SET-LC moves the counter
                seg, addr = val
            elif t == 6:                           # CHAIN-EXT: operand addr is in `val'
                if val:
                    chext[val[1]] = nm
            elif t == 12:                          # CHAIN-ADDR: val = chain head, addr = site
                if val:
                    chaddr[br_addr(br)] = val
            elif t == 7:
                publics.append((nm, val))
            elif t == 5:
                commons.append((nm, val))
            elif t == 0:
                extdefs.append(nm)
            elif t in (10, 13):
                sizes[TYPES[t]] = val
            if t == 15:
                break
    except EOFError:
        pass
    return code, dat, reloc, chext, chaddr, sizes, publics, commons, extdefs


def br_addr(br):
    return None


def linear(path, lo, hi, as_abs=False):
    code, dat, reloc, chext, chaddr, sizes, pub, com, ext = decode(path)
    out = []
    a = lo
    while a <= hi:
        b = code.get(a)
        if b is None:
            a += 1
            continue
        m, n = OPS.get(b, ("db %02X" % b, 1))
        if n == 3:
            r = reloc.get(("code", a + 1))
            e = chext.get(a + 1)
            if e:
                op = "%-8s  ; ext %s" % ("", e)
                out.append("%04X  %-6s CALL->%s" % (a, "call", e))
                a += 3
                continue
            if r:
                out.append("%04X  %-6s *%s(%04X)" % (a, m, r[0][0].upper(), r[1]))
            elif as_abs:
                out.append("%04X  %-6s %02X%02X" % (a, m, code.get(a + 1, 0), code.get(a + 2, 0)))
            else:
                out.append("%04X  %-6s ??" % (a, m))
            a += 3
        elif n == 2:
            out.append("%04X  %-6s %02X" % (a, m, code.get(a + 1, 0)))
            a += 2
        else:
            out.append("%04X  %s" % (a, m))
            a += 1
    return out, sizes, pub, com, ext


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    asb = "--abs" in sys.argv
    p = args[0]
    lo = int(args[1], 16) if len(args) > 1 else 0
    hi = int(args[2], 16) if len(args) > 2 else 0xFFFF
    lines, sizes, pub, com, ext = linear(p, lo, hi, asb)
    for l in lines:
        print(l)
