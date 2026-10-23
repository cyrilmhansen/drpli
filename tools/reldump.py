#!/usr/bin/env python3
"""LINK-80 / Microsoft 8080 REL bitstream decoder (v3).

Format per Nestor80 RelocatableFileFormat.md (matches LINK-80 guide §1.6):
  * absolute byte      : '0' + 8 bits (MSB-first chars)
  * relocatable value  : '1' + 2 seg bits (01 code, 10 data, 11 common)
                         + 16 bits LITTLE-ENDIAN
  * link item          : '1' + '00' + 4-bit type
        types 0-4  : symbol field only
        types 5-7  : relocatable value + symbol field
        types 8-14 : relocatable value only
        type 15    : nothing (EOF); type 14 (END-PROGRAM) pads to byte
        symbol field = 3-bit count + count*8 ASCII bits
Chain semantics (type 6 CHAIN-EXT / 12 CHAIN-ADDR): value = ADDRESS of
first chain slot; each slot holds a code-relative link whose 16-bit
value = address of the NEXT slot (0 terminates). The linker walks the
chain writing the resolved symbol value at each slot address.
"""
import sys

TYPES = {0: 'EXTDEF', 1: 'SEL-COMMON', 2: 'PROG-NAME', 3: 'REQ-LIBRARY',
         4: 'EXTENSION', 5: 'DEF-COMMON-SIZE', 6: 'CHAIN-EXT',
         7: 'DEF-PUBLIC', 8: 'EXT-MINUS-OFF', 9: 'EXT-PLUS-OFF',
         10: 'DEF-DATA-SIZE', 11: 'SET-LC', 12: 'CHAIN-ADDR',
         13: 'DEF-CODE-SIZE', 14: 'END-PROGRAM', 15: 'END-FILE'}
SEGS = {1: 'code', 2: 'data', 3: 'common'}

class BR:
    def __init__(self, d):
        self.d = d; self.p = 0
    def bit(self):
        if self.p // 8 >= len(self.d): raise EOFError
        b = (self.d[self.p >> 3] >> (7 - (self.p & 7))) & 1
        self.p += 1; return b
    def bits(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | self.bit()
        return v
    def val16(self):
        lo = self.bits(8); hi = self.bits(8)
        return hi << 8 | lo
    def name(self):
        n = self.bits(3)
        return ''.join(chr(self.bits(8)) for _ in range(n))
    def pad(self):
        self.p = (self.p + 7) & ~7

def decode(path, verbose=True):
    d = open(path, 'rb').read()
    br = BR(d)
    items = []
    data_bytes = []      # (prog-or-data addr determined by last SET-LC, byte)
    lc = ('code', 0)
    addr = 0
    seg = 'code'
    try:
        while True:
            st = br.p
            if br.bit() == 0:
                b = br.bits(8)
                items.append((st, 'DATA', seg, addr, b))
                data_bytes.append((seg, addr, b))
                addr += 1
                continue
            cls = br.bits(2)
            if cls:
                v = br.val16()
                items.append((st, 'RELOC', SEGS[cls], None, v))
                addr += 2
                continue
            t = br.bits(4)
            val = None; nm = None
            if 5 <= t <= 14:
                s = br.bits(2)
                if s == 0:   # absolute-valued field (sizes, LC values)
                    val = ('abs', br.val16())
                else:
                    val = (SEGS[s], br.val16())
            if 0 <= t <= 7 and t != 4:
                nm = br.name()
            elif t == 4:
                nm = br.name()   # extension: symbol bytes carry ext code
            if t == 14:
                br.pad()
            items.append((st, 'LINK-' + TYPES[t], None, val, nm))
            if t == 11 and val:
                seg, addr = val[0], val[1]
            if t == 15:
                break
    except EOFError:
        items.append((br.p, 'EOF?', None, None, None))
    if verbose:
        print(f'===== {path} ({len(d)} bytes, bits consumed {br.p}/{len(d)*8})')
        for st, kind, s, a, v in items:
            # [E2E-11 step 3b fix] the `a' slot holds a (SEGMENT, ADDRESS) tuple
            # for every LINK record whose payload is an address -- including
            # LINK-CHAIN-ADDRESS, whose target word is the ONLY thing that says
            # which forward CALL site the chain hangs from.  The old formatter
            # tested isinstance(a, int), so a tuple printed as nothing at all and
            # two files whose chain targets differed looked IDENTICAL in this
            # dump while `cmp` said they differed.  That blind spot is what made
            # me write down a false claim about E25F (see CLAIMS C123).
            if isinstance(a, tuple):
                af = "%s %04X" % (str(a[0]), a[1])
            elif isinstance(a, int):
                af = "%04X" % a
            elif a is None:
                af = ""
            else:
                af = str(a)
            print(f'  @{st:5} {kind:14} {s if s else ""} {af} {v if not isinstance(v,int) else hex(v)}')
    return items, data_bytes



# ---------------------------------------------------------------------------
# Regression test for THIS tool.  [E2E-11 step 3b] the formatter hid every
# (SEGMENT, ADDRESS) tuple payload, so two files whose LINK-CHAIN-ADDRESS
# targets differed printed as IDENTICAL here, and I recorded a false byte-parity
# claim about E25F on the strength of that dump (retracted in CLAIMS C123).  The
# lesson is not "be careful with dumps" -- it is that a decoder's omission is
# invisible inside its own output, so the omission needs an external check.
#
# These expectations are field-level (what decode() returns) AND textual (what a
# human reads), because the bug was in the human-facing layer while the parsed
# data was already correct.  Pinned against DR goldens, not my own output, so
# the test cannot pass by both producer and consumer drifting together.
# ---------------------------------------------------------------------------
SELFTEST = [
    # path, record type, occurrence, expected address field, why it matters
    ("golden/e2e129/E27C/E27C.REL", "LINK-CHAIN-ADDR", 0, ("code", 0x0014),
     "forward CALL site #1 in the pointer-forwarding probe"),
    ("golden/e2e129/E27C/E27C.REL", "LINK-CHAIN-ADDR", 1, ("code", 0x001A),
     "site #2 -- hiding this is what produced the false 'identical' reading"),
    ("golden/e2e129/E27C/E27C.REL", "LINK-DEF-DATA-SIZE", 0, ("abs", 0x000C),
     "size fields are absolute-valued; a regression here would mean the "
     "absolute/relocatable split moved"),
    ("golden/e2e143/E29A/E29A.REL", "LINK-CHAIN-EXT", 1, ("code", 0x000C),
     "external ENTRY chain slot; CHAIN-EXT carries no name field, so its "
     "symbol slot must read ?STOPX"),
]


def selftest():
    """Returns 0 iff every pinned field decodes as expected."""
    bad = []
    for path, kind, occ, want, why in SELFTEST:
        try:
            items, _ = decode(path, verbose=False)
        except Exception as e:                       # noqa: BLE001
            bad.append(f"{path}: unreadable ({e})")
            continue
        got = [it for it in items if it[1] == kind]
        if len(got) <= occ:
            bad.append(f"{path}: {kind}#{occ} missing "
                       f"(found {len(got)}) -- {why}")
            continue
        have = got[occ][3]
        if have != want:
            bad.append(f"{path}: {kind}#{occ} field decoded as {have!r}, "
                       f"expected {want!r} -- {why}")
        # the value must also be VISIBLE in what a human is shown
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            decode(path)
        line = [l for l in buf.getvalue().splitlines() if kind in l]
        word = "%04X" % want[1]
        if not any(word in l for l in line):
            bad.append(f"{path}: {kind}#{occ} value {word} absent from the "
                       f"printed dump (formatter hiding a field again) -- {why}")
    if bad:
        print("reldump SELFTEST FAILED:")
        for b in bad:
            print("  " + b)
        return 1
    print(f"reldump selftest: {len(SELFTEST)} pinned fields OK")
    return 0

if __name__ == '__main__':
    if sys.argv[1:2] == ['--selftest']:
        sys.exit(selftest())
    for f in sys.argv[1:]:
        decode(f)
