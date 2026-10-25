#!/usr/bin/env python3
"""[E2E-40/P9] How many operand-preservation tails does DR's whole corpus contain, and how many of
them sit at a SECOND add (the only population a compound-left rule could change)?

Reads every golden/**/*.REL through tools/dis80.code_and_xrefs, which indexes the code section by
LOGICAL address: a relocated 16-bit operand contributes no bytes to the file but does advance the
address, so those slots are filled with 0x00.  That is safe here and only here because every byte
position tested below is a spelled-out opcode; which CELL an operand names is a separate question
answered from DR's linked .COM in ADD_REGIONS.txt, never by this scan [C264].
"""
import glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dis80

PUSH = (0xE5, 0x2A, 0xD1, 0x19)   # PUSH H / LHLD lo hi / POP D / DAD D   (6 bytes with the operand)
XCHG = (0xEB, 0x2A, 0x19)         # XCHG / LHLD lo hi / DAD D             (5 bytes with the operand)

def main():
    files = sorted(glob.glob("golden/**/*.REL", recursive=True))
    park = swap = park2 = swap2 = 0
    park_files = swap_files = set()
    second_sites = []
    for f in files:
        try:
            code, _ = dis80.code_and_xrefs(f)
        except Exception:
            continue
        if not code:
            continue
        n = max(code) + 1
        b = bytes(code.get(i, 0) for i in range(n))
        for i in range(len(b) - 6):
            if b[i] == PUSH[0] and b[i+1] == PUSH[1] and b[i+4] == PUSH[2] and b[i+5] == PUSH[3]:
                park += 1; park_files.add(f)
                # instruction immediately before the park: if it is DAD D, this is a second ADD
                if i and b[i-1] == 0x19:
                    # and the DAD D must itself close a park/swap tail -> a real second add site
                    park2 += 1; second_sites.append((f, hex(i)))
        for i in range(len(b) - 5):
            if b[i] == XCHG[0] and b[i+1] == XCHG[1] and b[i+4] == XCHG[2]:
                swap += 1; swap_files.add(f)
                if i and b[i-1] == 0x19:
                    swap2 += 1; second_sites.append((f, hex(i), "xchg"))
    print("files scanned        %d" % len(files))
    print("DR park sites        %d in %d files" % (park, len(park_files)))
    print("DR swap sites        %d in %d files" % (swap, len(swap_files)))
    print("park  at a second add %d" % park2)
    print("swap  at a second add %d" % swap2)
    print("second-add sites:")
    for s in second_sites:
        print("   ", s)

main()

# NOTE (added after the first run, when the raw output was mis-read as 11 + 5 SITES): the listings
# above count FILES, and the runtime panel keeps a second copy of every program it executes under
# golden/e32rt_<NAME>/.  Deduplicate by base name before turning this output into a claim.
# See golden/e45/CORPUS_SCAN.txt for the deduplicated reading.
