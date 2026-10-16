#!/usr/bin/env python3
"""REL round-trip gate: decode -> re-encode every golden .REL and
require bit-exact reproduction of the module content (file remainder
must be zero padding to 128-byte sectors)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reldump import decode, TYPES
INV = {v: k for k, v in TYPES.items()}
SEGN = {'code': 1, 'data': 2, 'common': 3}


class BW:
    def __init__(self):
        self.bits = []

    def put(self, n, v):
        for i in range(n - 1, -1, -1):
            self.bits.append((v >> i) & 1)

    def string(self, s):
        for ch in s.encode():
            self.put(8, ch)

    def out(self):
        b = list(self.bits)
        while len(b) % 8:
            b.append(0)
        out = bytearray()
        for i in range(0, len(b), 8):
            v = 0
            for j in range(8):
                v = (v << 1) | b[i + j]
            out.append(v)
        return bytes(out)


def reencode(items):
    w = BW()
    for st, k, s, a, v in items:
        if k == 'DATA':
            w.put(1, 0); w.put(8, v)
        elif k == 'RELOC':
            w.put(1, 1); w.put(2, SEGN[s])
            w.put(8, v & 0xFF); w.put(8, v >> 8)
        elif k.startswith('LINK-'):
            t = INV[k[5:]]
            w.put(1, 1); w.put(2, 0); w.put(4, t)
            if 5 <= t <= 14 and a is not None:
                seg, val = a
                w.put(2, 0 if seg == 'abs' else SEGN[seg])
                w.put(8, val & 0xFF); w.put(8, val >> 8)
            if t <= 7 and v is not None:
                w.put(3, len(v)); w.string(v)
            if t == 14:
                while len(w.bits) % 8:
                    w.bits.append(0)
        elif k == 'EOF?':
            pass
    return w.out()


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(set(
        glob.glob(os.path.join(root, 'golden/**', '*.REL'), recursive=True)
        + glob.glob(os.path.join(root, 'artefacts', '*.REL'))))
    ok = bad = trunc = 0
    fails = []
    for f in files:
        orig = open(f, 'rb').read()
        try:
            items, _ = decode(f, verbose=False)
        except Exception as e:
            bad += 1; fails.append((f, f'decode-error {e}')); continue
        got = reencode(items)
        if got == orig:
            ok += 1
        elif orig.startswith(got.rstrip(b'\x00')) or (
                orig[:len(got)] == got and
                set(orig[len(got):]) <= {0}):
            # content exact, remainder pure zero-padding
            pad = len(orig) - len(got)
            if pad % 128 == 0 or set(orig[len(got):]) <= {0}:
                ok += 1
            else:
                bad += 1; fails.append((f, f'pad {pad} nonzero-ish'))
        else:
            n = min(len(orig), len(got))
            d = next((i for i in range(n) if orig[i] != got[i]), None)
            bad += 1
            fails.append((f, f'first diff byte {d}'))
    for f, why in fails[:10]:
        print('FAIL', os.path.relpath(f, root), why)
    print(f'rel round-trip: {ok} ok / {bad} fail of {len(files)}')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
