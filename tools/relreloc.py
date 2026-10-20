#!/usr/bin/env python3
"""Full Intel INTTEL80 REL record decoder, including every RELOC field.

tools/reldump.py reads only the class + first 16-bit value of a RELOC, which is
enough to keep the stream in sync but hides the T / R / E fields.  Those fields
are the whole question for E25F: DR encodes the FIRST forward CALL as a
CHAIN-ADDR and the SECOND one (same callee!) as something the listing prints as
`CALL S`, and I need to know which addressing mode and which external symbol it
actually names before I can lower repeated forward calls.

Usage: python3 tools/relreloc.py FILE.REL
"""
import sys

TYPES = {0: 'EXTDEF', 1: 'SEL-COMMON', 2: 'LNK-2', 3: 'LNK-3', 4: 'LNK-4',
         5: 'DEF-PUBLIC', 6: 'DEF-COMMON', 7: 'COM-EXT', 8: 'SUB-EXT',
         9: 'EXT-VEC', 10: 'EQV-VEC', 11: 'SET-LC', 12: 'DEF-COMMON-SIZE',
         13: 'LNK-13', 14: 'END-PROGRAM', 15: 'END-FILE'}
SEGS = {0: 'ABS', 1: 'CODE', 2: 'DATA', 3: 'EXT'}


class BR:
    def __init__(self, data):
        self.b = ''.join(f"{x:08b}" for x in data)
        self.p = 0

    def bit(self):
        v = int(self.b[self.p], 2)
        self.p += 1
        return v

    def bits(self, n):
        v = int(self.b[self.p:self.p + n], 2)
        self.p += n
        return v

    def val16(self):
        lo = self.bits(8)
        hi = self.bits(8)
        return lo | (hi << 8)

    def name(self):
        n = self.bit()
        cnt = 4 + 4 * n
        raw = bytes(self.bits(8) for _ in range(cnt))
        trail = self.bits(4) if n else self.bits(4)
        return raw.rstrip(b'\0').decode('latin1'), f'ext-hi={trail:02x}'


def main(path):
    d = open(path, 'rb').read()
    br = BR(d)
    lc = ('code', 0)
    addr = 0
    seg = 'code'
    exts = []
    while br.p + 1 <= len(br.b):
        st = br.p
        if br.bit() == 0:
            b = br.bits(8)
            print(f"@{st:5d} DATA   {seg} {addr:04X} = {b:02X}")
            addr += 1
            continue
        cls = br.bits(2)
        if cls:
            # RELOC record: 11 TT R[1] E[4] ...  (Intel layout)
            T = br.bits(2)
            if T == 3:
                print(f"@{st:5d} RELOC  (long/16-bit-address form, unsupported here)")
                break
            R = br.bit()
            rel = br.val16()          # relative-to address
            if R == 0:
                ra = br.val16()       # relocation-area address
            else:
                ra = None
            E = br.bits(4)
            ext = None
            if E != 0:
                ext = br.val16() if E in (1, 2, 3) else br.bits(8)
            tseg = SEGS[T] if T < 3 else '??'
            rseg = SEGS[R] if R < 3 else '??'
            print(f"@{st:5d} RELOC  T={tseg} reladdr={rel:04X} R={'self' if R==1 else rseg}"
                  f" relocarea={'-' if ra is None else format(ra, '04X')}"
                  f" E={E}{' ext=' + str(ext) if ext is not None else ''}"
                  f"  (target {seg} {addr:04X})")
            addr += 2
            continue
        t = br.bits(4)
        val = None
        nm = None
        if 5 <= t <= 14:
            s = br.bits(2)
            val = ('ABS', br.val16()) if s == 0 else (SEGS[s].lower(), br.val16())
        if t in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14):
            nm = br.name()
        if t == 14:
            br.p += 8 - (br.p % 8) if br.p % 8 else 0
        if t == 0:
            exts.append(nm[0] if nm else '?')
            print(f"@{st:5d} EXTDEF {nm}")
        else:
            print(f"@{st:5d} {TYPES.get(t, 'TYPE' + str(t))} val={val} name={nm}")
        if t == 11 and val:
            seg, addr = val[0], val[1]
        if t == 15:
            print(f"@{st:5d} END-FILE")
            break
    if exts:
        print("external symbol table:", exts)


if __name__ == '__main__':
    main(sys.argv[1])
