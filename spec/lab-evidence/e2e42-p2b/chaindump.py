#!/usr/bin/env python3
"""chaindump.py -- linearize the CODE segment of a LINK-80 .REL into instructions whose
16-bit operands are labelled with what they actually ARE.

Why this exists (E2E-42/P2b): the question of this milestone is the SHAPE OF A CHAIN -- how many
`LXI H,<operand>` a two-item PUT has, whether a second ?SIOOP appears between the items, whether
one ?QIOOP closes the whole list.  `tools/reldump.py' prints the record stream, which shows those
operands as `RELOC data 0x9' with no indication of WHICH instruction they belong to, and
`tools/dis80.py' parses reldump's text and so cannot see a relocated operand's bytes at all (its own
docstring says so: they print as `.').  Neither answers "what is the second item's LXI H operand".

This replays the bitstream through reldump's OWN `BR' class -- the pinned decoder, not a second
implementation (two independent decoders of this format is how [C123] happened) -- and keeps the
three things reldump's item list discards:
  * the code ADDRESS each RELOC record covers (a RELOC consumes two logical addresses);
  * the code ADDRESS each LINK-CHAIN-EXT record patches;
  * which CHAIN-EXT belongs to which CALL, so `CD 00 00' prints as `CALL ?SLVTS'.

An operand is then printed as  `*D(0009)' / `*C(OUTF)' / `01AF'  -- a relocated DATA or COMMON
reference, or a literal -- and never as a bare number, because a number whose segment is unknown is
exactly the thing [C264] warns about.

  usage: chaindump.py FILE.REL [STARTHEX [ENDHEX]]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from reldump import BR, SEGS, TYPES        # noqa: E402  the pinned decoder, imported not rewritten

# opcode -> mnemonic (2 = one operand byte, 3 = a 16-bit operand slot).  Deliberately ONLY the
# instructions DR's PUT/GET/OPEN lowering is known to emit; an unknown opcode prints as `db'
# rather than being guessed at, because a wrong mnemonic in a committed evidence file is worse
# than no mnemonic.
OP = {
    # 0x09 fixed E2E-48/P1: was "dad d", contradicting golden bytes 0x09 at
    # E48A7:0040/E48A12:003E/E48B1:002E and this project's own learned constants
    # op_dad_b=0x09, op_dad_d=0x19 [C144].
    0x00: ("nop", 1), 0x01: ("lxi b", 3), 0x06: ("mvi b", 2), 0x09: ("dad b", 1),
    0x0b: ("dcx b", 1), 0x0c: ("inx b", 1), 0x11: ("lxi d", 3), 0x13: ("inx d", 1),
    0x19: ("dad d", 1), 0x21: ("lxi h", 3), 0x22: ("shld", 3), 0x23: ("inx h", 1),
    0x29: ("dad h", 1), 0x2a: ("lhld", 3), 0x2b: ("dcx h", 1), 0x31: ("lxi sp", 3),
    0x33: ("inx sp", 1), 0x34: ("inr m", 1), 0x35: ("dcr m", 1), 0x3b: ("dcx sp", 1),
    0x3c: ("inr a", 1), 0x3d: ("dcr a", 1), 0x3e: ("mvi a", 2),
    0x77: ("mov m,a", 1), 0x7d: ("mov a,l", 1), 0x7c: ("mov a,h", 1),
    0x5f: ("mov e,a", 1), 0x57: ("mov a,l", 1), 0x6f: ("mov l,a", 1), 0x67: ("mov h,a", 1),
    0x4f: ("mov c,a", 1), 0x47: ("mov b,a", 1), 0x79: ("mov a,c", 1), 0x78: ("mov a,b", 1),
    0x43: ("mov m,e", 1), 0x42: ("mov m,b", 1), 0x71: ("mov m,c", 1), 0x73: ("mov m,e", 1),
    0x72: ("mov m,d", 1), 0x70: ("mov m,b", 1),
    0xd1: ("pop d", 1), 0xd5: ("push d", 1), 0xe1: ("pop h", 1), 0xe5: ("push h", 1),
    0xe3: ("xthl", 1), 0xeb: ("xchg", 1), 0xc9: ("ret", 1), 0xc3: ("jmp", 3),
    0xca: ("jz", 3), 0xc2: ("jnz", 3), 0xda: ("jc", 3), 0xd2: ("jnc", 3), 0xdb: ("in", 2),
    0xe2: ("jpo", 3), 0xea: ("jpe", 3), 0xcc: ("cz", 3), 0xc4: ("cnz", 3), 0xdc: ("cc", 3),
    0xd4: ("cnc", 3), 0xcd: ("call", 3), 0xf0: ("rnz", 1), 0xc7: ("rz", 1), 0xd8: ("rc", 1),
    0xd0: ("rnc", 1), 0xc8: ("rz", 1), 0xc0: ("rnz", 1), 0xc9: ("ret", 1),
    0x76: ("hlt", 1), 0xb7: ("ora a", 1), 0xaf: ("xor a", 1), 0x2f: ("cma", 1), 0x37: ("stc", 1),
    0x27: ("daa", 1), 0x2e: ("mvi l", 2), 0x36: ("mvi m", 2), 0x3f: ("cmc", 1),
    0xc6: ("adi", 2), 0xce: ("aci", 2), 0xd6: ("sui", 2), 0xde: ("sbi", 2), 0xe6: ("ani", 2),
    0xf6: ("ori", 2), 0xfe: ("cpi", 2), 0xb9: ("cmp e", 1), 0xbe: ("cmp m", 1),
    0xbd: ("cmp l", 1), 0xbc: ("cmp h", 1), 0xa7: ("ana a", 1), 0x97: ("sub a", 1),
    0x87: ("add a", 1), 0x82: ("add d", 1), 0x84: ("add h", 1), 0x8b: ("adc e", 1),
    0x8f: ("adc l", 1), 0x92: ("sub d", 1), 0x95: ("sub l", 1), 0x9b: ("sbb e", 1),
    0x9d: ("sbb h", 1), 0x85: ("add l", 1), 0x83: ("add e", 1),
    0x0a: ("ldax b", 1), 0x1a: ("ldax d", 1), 0x02: ("stax b", 1), 0x12: ("stax d", 1),
    0x3a: ("lda", 3), 0x32: ("sta", 3), 0x07: ("rlc", 1), 0x0f: ("rrc", 1),
    0x17: ("ral", 1), 0x1f: ("rar", 1), 0x0d: ("dcr c", 1), 0x05: ("dcr b", 1),
    0x04: ("inr b", 1), 0x0c: ("inr c", 1), 0x14: ("inr d", 1), 0x1c: ("inr e", 1),
    0x15: ("dcr d", 1), 0x1d: ("dcr e", 1), 0x2d: ("dcr l", 1), 0x25: ("dcr h", 1),
    0x2c: ("inr l", 1), 0x24: ("inr h", 1),
}


def decode(path):
    """-> (code bytes, {addr: reloc target}, {addr: ext name}, {addr: chain-head}, sizes)"""
    raw = open(path, "rb").read()
    br = BR(raw)
    code, dat = {}, {}
    reloc, chext, chaddr = {}, {}, {}
    seg, addr = "code", 0
    sizes, publics, commons = {}, [], []
    try:
        while True:
            if br.bit() == 0:
                b = br.bits(8)
                (code if seg == "code" else dat)[addr] = b
                addr += 1
                continue
            cls = br.bits(2)
            if cls:
                v = br.val16()
                if seg == "code":
                    reloc[addr] = (SEGS[cls], v)
                addr += 2
                continue
            t = br.bits(4)
            val = None
            if 5 <= t <= 14:
                s2 = br.bits(2)
                val = ("abs", br.val16()) if s2 == 0 else (SEGS[s2], br.val16())
            nm = br.name() if (t <= 7) else None
            if t == 14:
                br.pad()
            if t == 11 and val:
                seg, addr = val
            elif t == 6 and val:
                chext[val[1]] = nm
            elif t == 12 and val:
                # CHAIN-ADDR: the record's ADDRESS field is the patched slot, its VALUE is the
                # chain head.  reldump's decode() puts the value in `a' and loses the slot, which
                # is the [C123] blind spot; here both are kept.
                chaddr[addr] = val
                addr += 2
            elif t == 7:
                publics.append((nm, val))
            elif t == 5:
                commons.append((nm, val, addr))
            elif t in (10, 13):
                sizes[TYPES[t]] = val
            if t == 15:
                break
    except EOFError:
        pass
    return code, reloc, chext, chaddr, sizes, publics, commons, dat


def dump(path, lo=0, hi=0xFFFF):
    code, reloc, chext, chaddr, sizes, pub, com, dat = decode(path)
    print("# %s: CODE %s  DATA %s" % (path,
          sizes.get("DEF-CODE-SIZE"), sizes.get("DEF-DATA-SIZE")))
    a = lo
    while a <= min(hi, max(code) if code else 0):
        if a not in code:
            a += 1
            continue
        b = code[a]
        mn, n = OP.get(b, ("db %02X" % b, 1))
        if n == 3:
            r, e = reloc.get(a + 1), chext.get(a + 1)
            if mn == "call":
                tgt = e or ("chain@%04X" % chaddr[a + 1][1] if a + 1 in chaddr else "??")
                print("%04X  call  %-10s        ; CD %02X %02X" % (a, tgt, code.get(a+1,0), code.get(a+2,0)))
            elif e:
                print("%04X  %-6s %-10s        ; chain-EXT head %s" % (a, mn, e, e))
            elif r:
                tag = {"data": "*D", "common": "*C", "code": "*CODE"}.get(r[0], "?" + r[0])
                print("%04X  %-6s %s(%04X)" % (a, mn, tag, r[1]))
            elif a + 1 in chaddr:
                print("%04X  %-6s chain(%04X)->%s" % (a, mn, chaddr[a+1][1], chaddr[a+1][0]))
            else:
                print("%04X  %-6s %04X" % (a, mn, code.get(a + 2, 0) << 8 | code.get(a + 1, 0)))
        elif n == 2:
            print("%04X  %-6s %02X" % (a, mn, code.get(a + 1, 0)))
        else:
            print("%04X  %s" % (a, mn))
        a += n


def instrs(path):
    """-> (list of (addr, mnemonic, operand-string), sizes dict).  The machine-readable form of
    `dump', for the comparisons in compare.py; the operand string carries the SEGMENT tag so a
    DATA 0009 and an absolute 0009 are never printed alike ([C264])."""
    code, reloc, chext, chaddr, sizes, pub, com, dat = decode(path)
    out, a = [], 0
    top = max(code) if code else 0
    while a <= top:
        if a not in code:
            a += 1
            continue
        b = code[a]
        mn, n = OP.get(b, ("db %02X" % b, 1))
        if n == 3:
            r, e = reloc.get(a + 1), chext.get(a + 1)
            if mn == "call":
                op = e or ("chain@%04X" % chaddr[a + 1][1] if a + 1 in chaddr else "??")
            elif e:
                op = e
            elif r:
                tag = {"data": "*D", "common": "*C", "code": "*CODE"}.get(r[0], "?" + r[0])
                op = "%s(%04X)" % (tag, r[1])
            elif a + 1 in chaddr:
                op = "chain(%04X)" % chaddr[a + 1][1]
            else:
                op = "%04X" % (code.get(a + 2, 0) << 8 | code.get(a + 1, 0))
        elif n == 2:
            op = "%02X" % code.get(a + 1, 0)
        else:
            op = ""
        out.append((a, mn, op))
        a += n
    return out, sizes


if __name__ == "__main__":
    p = sys.argv[1]
    lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xFFFF
    dump(p, lo, hi)
