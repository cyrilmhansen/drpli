#!/usr/bin/env python3
"""Bit-exact solver for LINK-80 .REL streams.

Rather than guessing ambiguous guide wording, we SEARCH for the unique
bit-consistent parse that reproduces KNOWN program bytes (from $C
listings) and known symbol names. Anchors:
  * first data bytes must be 06 00 02 cd (LXI B,0200 / CALL ?START)
  * chain-external head addresses match $C CALL operand addresses
"""
import sys

data = open(sys.argv[1] if len(sys.argv) > 1 else
            'golden/probe47/P060A/P060A.REL', 'rb').read()
bits = ''.join(format(b, '08b') for b in data)

# frames: data = '0'+8 ; prog-link = '1'+'01'+16 ; data-link='1'+'10'+16
# common='1'+'11'+16 ; special='1'+'00'+ctrl4(+fields)
# TRY: 16-bit fields little-endian ('lo first' => bits group by 8, swap)

def b16(s):  # interpret 16 bits as lo-byte-first
    lo = int(s[0:8], 2); hi = int(s[8:16], 2)
    return hi << 8 | lo

def chars(s):
    return ''.join(chr(int(s[i:i+8], 2)) for i in range(0, len(s), 8))

# locate the anchor stream for 06 00 02 cd as four consecutive frames
target = ''.join('0' + format(v, '08b') for v in (0x06, 0x00, 0x02, 0xCD))
p = bits.find(target)
print('anchor 06 00 02 cd frames at bit', p)
if p < 0:
    # maybe some of those are link slots; try just '06 00 02'
    t2 = ''.join('0' + format(v, '08b') for v in (0x06, 0x00, 0x02))
    p = bits.find(t2)
    print('anchor 06 00 02 at bit', p)

# walk forward as data frames until mismatch, print raw structure after
if p >= 0:
    i = p
    seq = []
    while i + 9 <= len(bits):
        if bits[i] == '0':
            seq.append(('D', int(bits[i+1:i+9], 2)))
            i += 9
        else:
            seq.append(('BIT1', bits[i:i+3]))
            break
    print('frames after anchor:', seq)
    print('raw @', i, ':', bits[i:i+40])

# also scan the whole file for all frame-boundary-aligned data bytes
# starting from anchor going BACKWARD to find item header
q = bits.rfind('100', 200, p - 1)
print('nearest 1xx before anchor:', q, bits[q:q+30])
