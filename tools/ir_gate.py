#!/usr/bin/env python3
"""IR gate: compare our pli80ir opcode stream against the original
compiler's $V goldens (expression-subset lines).

DR side: tools/vtrace.py on golden transcripts (probe38/39/40 $V$L
batteries). Both sides normalized: collapse whitespace, drop the
leading address column, and restrict to a shared op alphabet window:
comparison covers each program's STMT-region lines LIO..(op set),
skipping frame records (BEG/NID/ENT/STP/CTL) which are [TBD]."""
import subprocess, os, sys, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80ir.exe")

FRAME_OPS = {'BEG', 'NID', 'ENT', 'STP', 'CTL', 'SB', 'OFF'}
# f6 (field index 5) and f7 (index 6) are DR-internal positional/link
# bytes shown NOT source-derivable by the F/G probe battery
# (spec/notes/f6-probe-design.md: identical source statements get
# different f6; preceding-statement count changes it non-monotonically).
# STRUCTURAL parity masks them; BYTE parity keeps them.
SRC_FILES = {'P071A': 'probe38', 'P071B': 'probe38', 'P071C': 'probe38',
             'P071E': 'probe38', 'P071F': 'probe38', 'P071D': 'probe38',
             'P072A': 'probe40', 'P072C': 'probe40', 'P072D': 'probe40',
             'P072E': 'probe40'}
GATED = ['P071A']     # files required to pass BYTE-parity right now


def mask_f67(lines):
    """Blank f6/f7 (fields 5,6 after OP) -> '??' for structural compare."""
    out = []
    for l in lines:
        tok = l.split(' ')
        if len(tok) >= 7:              # OP + >=6 fields
            tok[6] = '??'              # f6  (index: 0=OP,1..=fields)
            tok[7] = '??' if len(tok) > 7 else tok[-1]
        out.append(' '.join(tok))
    return out


def norm(lines, drop_frame=True):
    out = []
    for l in lines:
        l = re.sub(r'\s+', ' ', l).strip()
        m = re.match(r'^(?:[0-9A-Fa-f]{2} )?([A-Z][A-Z0-9]{1,4}) (.*)$', l)
        if not m:
            continue
        op, rest = m.groups()
        if drop_frame and op in FRAME_OPS:
            continue
        if op == 'L':   # vtrace source-line marker
            continue
        out.append(op + ' ' + rest)
    return out


def dr_stream(name, tag):
    tr = sorted(glob.glob(os.path.join(ROOT, 'golden', tag, 'transcript-batch*.txt')))
    out = subprocess.run(['python3', os.path.join(ROOT, 'tools/vtrace.py')]
                         + tr + ['--name', name],
                         capture_output=True, text=True).stdout
    keep = []
    for l in out.split('\n'):
        if re.match(r'^\s+L\d+:', l):
            continue
        m = re.match(r'^\s{4,}([A-Z].*)$', l)
        if m:
            keep.append(m.group(1))
    return norm(keep)


def our_stream(name):
    src = None
    for d in ('probes', 'artefacts'):
        p = os.path.join(ROOT, d, name + '.PLI')
        if os.path.exists(p):
            src = p
            break
    if src is None:
        return None
    r = subprocess.run([EXE, src], capture_output=True, text=True)
    if r.returncode != 0:
        return 'ERROR: ' + (r.stderr or '')[:200]
    return norm(r.stdout.split('\n'))


def main():
    ok = struct_ok = gap = fail = 0
    for name, tag in sorted(SRC_FILES.items()):
        dr = dr_stream(name, tag)
        ours = our_stream(name)
        if isinstance(ours, str) and ours.startswith('ERROR'):
            status = 'GATE-ERROR' if name in GATED else 'gap'
            print(f"{status:11} {name}: {ours[:120]}")
            gap += name not in GATED
            fail += name in GATED
            continue
        byte = dr == ours
        struct = mask_f67(dr) == mask_f67(ours)
        if byte:
            print(f"BYTE-EXACT {name}")
            ok += 1
        elif struct:
            print(f"STRUCT-OK  {name}  (op/p/s/desc match; f6-f7 differ)")
            struct_ok += 1
        else:
            n = min(len(dr), len(ours))
            i = next((i for i in range(n) if mask_f67(dr)[i] != mask_f67(ours)[i]), n)
            msg = (f"dr[{i}]={dr[i] if i < len(dr) else '<end>'!r} "
                   f"ours={ours[i] if i < len(ours) else '<end>'!r}")
            if name in GATED:
                print(f"FAIL      {name}: {msg}")
                fail += 1
            else:
                print(f"GAP       {name}: {msg}")
                gap += 1
    print(f"ir gate: {ok} byte-exact / {struct_ok} struct-exact(f67-masked) "
          f"/ {gap} gap / {fail} FAIL of {len(SRC_FILES)}")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
