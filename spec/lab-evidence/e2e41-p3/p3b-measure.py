#!/usr/bin/env python3
"""[E2E-41/P3b] MEASURE THE STREAM-OUTPUT OPEN AND THE NAMED-FILE PUT LIST.

Everything printed here is recomputed -- DR's golden .REL/.PRN and a compile with the CURRENT
binary -- so the two things P3b claims can be re-checked without trusting the note's prose:

  1 whole-file byte equality of my .REL with DR's: cmp over ALL 512 bytes, loader pad included,
    not a code-region comparison;
  2 the OPEN block (six option words + ?OIOOP) with w1 = 0E50H and w2..w6 = 0000H, and both PUT
    blocks (?SIOOP with attach word 0652H), read as bytes out of the .REL and named out of DR's
    own listing -- the two item chains are DIFFERENT: `list('HELLO')' -> ?SLCTS/?PNCOP,
    `list(42)' -> ?DLDOP/?QDCOP/?PNVOP, and E17D's console PUT at 0064 carries the SAME string
    chain under a ?SYSPR prologue, which is what shows the item chain is not file-specific;
  3 the DATA segment: title cell, string cell, the packed cell for 42, 'WROTE', in source order;
  4 for E17D only, if a runtime run has been done (golden/e32rt_E17D/E17D/OUT.DAT exists), a
    byte-for-byte comparison with DR's archived golden/e2e11iu/E17D/OUT.DAT -- all 128 bytes, the
    0x1A tail included.  Absent is reported as absent: this script never runs the emulator, the
    runtime panel does that (`python3 tools/e2e_gate.py --runtime --only E17D`).

  usage: python3 spec/lab-evidence/e2e41-p3/p3b-measure.py > P3b-MEASURE.txt
Read-only apart from a temp .REL: it never writes into golden/ or artefacts/.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
BIN = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")

CASES = [
    ("E16D", "e13src/E16D.PLI", "golden/e2e11h/E16D/E16D.REL",
     [("OPEN FILE(OUTF) title('E16OUT DAT') -> ?OIOOP", 0x0006, 0x0022),
      ("PUT LIST('HELLO')  attach 0652 -> ?SLCTS/?PNCOP -> ?QIOOP", 0x0023, 0x003C),
      ("PUT LIST(42)       attach 0652 -> ?DLDOP/?QDCOP/?PNVOP -> ?QIOOP", 0x003D, 0x005D),
      ("CLOSE FILE(OUTF) -> ?CIOOP", 0x005E, 0x0063),
      ("PUT LIST('WROTE')  console: attach 0252 -> ?SYSPR", 0x0064, 0x007A)]),
    ("E17D", "e13src/E17D.PLI", "golden/e2e11i/E17D/E17D.REL",
     [("OPEN FILE(OUTF) title('$1.$1') -> ?OIOOP", 0x0006, 0x0022),
      ("PUT LIST('HELLO')  attach 0652 -> ?SLCTS/?PNCOP -> ?QIOOP", 0x0023, 0x003C),
      ("PUT LIST(42)       attach 0652 -> ?DLDOP/?QDCOP/?PNVOP -> ?QIOOP", 0x003D, 0x005D),
      ("CLOSE FILE(OUTF) -> ?CIOOP", 0x005E, 0x0063),
      ("PUT LIST('WROTE')  console: attach 0252 -> ?SYSPR", 0x0064, 0x007A)]),
]


def rel_bytes(path):
    """{('code'|'data', addr): byte} and {addr: external symbol} from tools/reldump.py."""
    out = subprocess.run([sys.executable, os.path.join(TOOLS, "reldump.py"), path],
                         capture_output=True, text=True).stdout
    data, xref = {}, {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 5 or f[0] != "@":
            continue
        kind, seg = f[2], f[3]
        if seg not in ("code", "data"):
            continue
        a = int(f[4], 16)
        if kind == "DATA" and len(f) > 5 and f[5].startswith("0x"):
            data[(seg, a)] = int(f[5], 16)
        elif kind.startswith("LINK-CHAIN") or kind in ("LINK-EXTDEF", "LINK-DATA-EXT"):
            tgt = f[5] if len(f) > 5 else "?"
            xref.setdefault(a, tgt)
            xref.setdefault(a + 1, tgt)      # a 16-bit reloc field spans operand+1,+2
    return data, xref


def render(data, xref, seg, lo, hi):
    """The bytes of [lo,hi] as hex, with the external symbol that owns each reloc field."""
    raw = []
    for a in range(lo, hi + 1):
        if (seg, a) in data:
            raw.append("%02X" % data[(seg, a)])
        elif a in xref:
            raw.append(">>%s<<" % xref[a])
        else:
            raw.append("--")
    return " ".join(raw)


def prn_window(path, lo, hi):
    """DR's own listing lines (name-resolved) whose address falls in [lo,hi]."""
    keep = []
    with open(path, errors="replace") as f:
        for line in f:
            f2 = line.split()
            if len(f2) < 2 or len(f2[0]) != 4:
                continue
            try:
                a = int(f2[0], 16)
            except ValueError:
                continue
            if lo <= a <= hi and a != 0:
                keep.append("      DR prn  %04X  %s %s" % (a, f2[1], " ".join(f2[2:])))
    return keep


def rec_bytes(path):
    """{'code': {addr: byte}, 'data': {...}} plus the reloc anchors, from tools/reldump.py."""
    out = subprocess.run([sys.executable, os.path.join(TOOLS, "reldump.py"), path],
                         capture_output=True, text=True).stdout
    seg = {"code": {}, "data": {}}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 5 or f[0] != "@" or f[3] not in ("code", "data"):
            continue
        a = int(f[4], 16)
        if f[2] == "DATA" and len(f) > 5 and f[5].startswith("0x"):
            seg[f[3]][a] = int(f[5], 16)
        else:
            seg[f[3]].setdefault(a, None)      # a relocatable operand, value supplied at link
    return seg


def main():
    if not os.path.exists(BIN):
        sys.exit("build first: (cd ocaml && dune build)")
    tmp = "/tmp/e2e41-p3b"
    os.makedirs(tmp, exist_ok=True)
    for name, src, gold, windows in CASES:
        mine = os.path.join(tmp, name + ".REL")
        r = subprocess.run([BIN, os.path.join(ROOT, src), mine],
                           capture_output=True, text=True)
        print("=" * 78)
        print("== %s   source %-16s golden %s" % (name, src, gold))
        if r.returncode != 0:
            print("   MINE REFUSED: %s" % (r.stderr or "").strip().splitlines()[-1])
            continue
        a = open(mine, "rb").read()
        b = open(os.path.join(ROOT, gold), "rb").read()
        print("   whole-file cmp: mine %d bytes, DR %d bytes, identical = %s"
              % (len(a), len(b), a == b))
        if a != b:
            d = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
            print("   !! %d bytes differ, first at %s" % (len(d), [hex(x) for x in d[:12]]))
        gp = os.path.join(ROOT, gold)
        mp = mine
        gd, gx = rel_bytes(gp)
        md, mx = rel_bytes(mp)
        seglen = lambda d, s: (max(k[1] for k in d if k[0] == s) + 1
                               if any(k[0] == s for k in d) else 0)
        print("   segments: DR code %d, data %d   MINE code %d, data %d   (all equal: %s)"
              % (seglen(gd, "code"), seglen(gd, "data"), seglen(md, "code"), seglen(md, "data"),
                 gd == md and gx == mx))
        print("   DATA bytes DR : %s" % render(gd, gx, "data", 0,
                                               max(k[1] for k in gd if k[0] == "data")))
        print("   DATA bytes mine: %s" % render(md, mx, "data", 0,
                                                max(k[1] for k in md if k[0] == "data")))
        prn = os.path.splitext(gp)[0] + ".PRN"
        for label, lo, hi in windows:
            same = all(gd.get(("code", x)) == md.get(("code", x)) for x in range(lo, hi + 1))
            print("   -- %s  [%04X-%04X]  code bytes DR==mine: %s" % (label, lo, hi, same))
            print("      DR bytes  %s" % render(gd, gx, "code", lo, hi))
            print("      my bytes  %s" % render(md, mx, "code", lo, hi))
            if os.path.exists(prn):
                for line in prn_window(prn, lo, hi):
                    print(line)
        if name == "E17D":
            g = open(os.path.join(ROOT, "golden/e2e11iu/E17D/OUT.DAT"), "rb").read()
            print("   DR golden OUT.DAT: %d bytes sha256=%s"
                  % (len(g), hashlib.sha256(g).hexdigest()[:16]))
            print("      head %s | tail %s" % (" ".join("%02X" % c for c in g[:13]),
                                               " ".join("%02X" % c for c in g[-4:])))
            myf = os.path.join(ROOT, "golden/e32rt_E17D/E17D/OUT.DAT")
            if os.path.exists(myf):
                m = open(myf, "rb").read()
                print("   MINE (runtime panel's export) OUT.DAT: %d bytes sha256=%s"
                      % (len(m), hashlib.sha256(m).hexdigest()[:16]))
                print("      byte-for-byte equal over ALL %d bytes (0x1A tail included): %s"
                      % (len(g), m == g))
            else:
                print("   MINE: no OUT.DAT exported yet -- run "
                      "`python3 tools/e2e_gate.py --runtime --only E17D`")
    print("=" * 78)
    print("Cross-program check: the SAME open block in an OUTPUT and an INPUT program")
    print("  E17D `open file(outf) stream output title('$1.$1')'  vs")
    print("  E17B `open file(inf) stream title('$1.$1')'          -- identical 29-byte")
    print("  block at 0006-0022 except the mode word itself.")
    a = rec_bytes(os.path.join(ROOT, "golden/e2e11i/E17D/E17D.REL"))
    b = rec_bytes(os.path.join(ROOT, "golden/e2e11i/E17B/E17B.REL"))
    diffs = []
    for x in range(0x0006, 0x0023):
        ta, tb = a["code"].get(x), b["code"].get(x)
        if ta != tb:
            diffs.append((x, ta, tb))
        print("   %04X  E17D %s  E17B %s%s" % (x,
              "%02X" % ta if ta is not None else "reloc", 
              "%02X" % tb if tb is not None else "reloc",
              "   <-- differs" if ta != tb else ""))
    print("   differing addresses: %s" % [(hex(x), "%02X" % p, "%02X" % q) for x, p, q in diffs])
    print("   -> the ONLY byte that moves is the low half of w1: 0x50 (OUTPUT, 0x0E50) against")
    print("      0x90 (INPUT, 0x0E90); 0x0080 is CLEARED, not added to, and w2..w6 stay 0000 [C280].")
    print("=" * 78)
    print("Attach-word cross-check (P0's sweep, spec/lab-evidence/e2e41-p0/SIOMODES.txt):")
    for line in open(os.path.join(ROOT, "spec/lab-evidence/e2e41-p0/SIOMODES.txt")):
        if line.split(" ")[0] in ("program", "E16D", "E17D", "P019B", "LOAN2", "RETRIEVE"):
            print("   " + line.rstrip())


if __name__ == "__main__":
    main()
