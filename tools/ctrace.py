#!/usr/bin/env python3
"""$C code-trace extractor for PL/I-80 transcripts.

Usage:
  tools/ctrace.py golden/.../transcript-batch*.txt [--name P071A] [--full]

Default output: per-program compact summary (code size, line map,
RTL CALL histogram). --full prints the whole interleaved listing.
Parses the `C: Code Trace Only` / `$I` interlist sections:
  ; LINE nnnn
       AAAA       MNEM  operands
  CODE SIZE = hhhh / DATA AREA = hhhh
"""
import sys, re, collections

ANSI = re.compile(rb'\x1b\[[0-9;]*[a-zA-Z]')

def programs(files):
    text = ""
    for f in files:
        with open(f, 'rb') as fh:
            text += ANSI.sub(b'', fh.read()).decode('latin1')
    text = text.replace('\r', '')
    # split at COMPILATION OF headers
    parts = re.split(r'COMPILATION OF: (\S+)', text)
    out = []
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i+1]
        # only keep sections that contain a code trace marker
        if re.search(r'C: Code Trace|I: Interlist', body):
            lines = []
            cur_line = None
            for m in re.finditer(
                    r'(?:;\s*LINE\s+(\d+))|'
                    r'^\s{5,}([0-9A-Fa-f]{4})\s{3,}(\w+)\s*(.*?)\s*$|'
                    r'CODE SIZE\s*=\s*([0-9A-F]{3,4})|'
                    r'DATA AREA\s*=\s*([0-9A-F]{3,4})',
                    body, re.M):
                ln, addr, mn, ops, cs, da = m.groups()
                if ln:
                    cur_line = int(ln)
                elif addr:
                    lines.append((int(addr, 16), mn, ops, cur_line))
                elif cs:
                    lines.append((-1, '.CODESIZE', cs, None))
                elif da:
                    lines.append((-1, '.DATAAREA', da, None))
            out.append((name, lines))
    return out

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    want = None
    full = '--full' in sys.argv
    if '--name' in sys.argv:
        want = sys.argv[sys.argv.index('--name') + 1]
        args = [a for a in args if a != want and a != '--name']
    progs = programs(args)
    hist = collections.Counter()
    mnem = collections.Counter()
    for name, lines in progs:
        if want and name != want:
            continue
        cs = next((v for a, m, v, _ in lines if m == '.CODESIZE'), '?')
        da = next((v for a, m, v, _ in lines if m == '.DATAAREA'), '?')
        code = [(a, m, o, l) for a, m, o, l in lines if m[0] != '.']
        print(f"### {name}  code={cs} data={da} instrs={len(code)}")
        for m, o, l in ((m, o, l) for _, m, o, l in code):
            if m == 'CALL' and o.strip().startswith('?'):
                hist[o.strip()[1:]] += 1
            mnem[m] += 1
        if full:
            cur = object()
            for a, m, o, l in code:
                if l != cur:
                    cur = l
                    print(f"  L{l}:")
                print(f"    {a:04X} {m:<6} {o}")
        else:
            # per-line first/last addr summary
            per = collections.OrderedDict()
            for a, m, o, l in code:
                per.setdefault(l, []).append((a, m, o))
            for l, ins in per.items():
                print(f"  L{l}: {len(ins)} instrs  {ins[0][1]}..{ins[-1][1]} @{ins[0][0]:04X}")
    if not want:
        print("\n--- CALL histogram (all progs in files given) ---")
        for k, v in sorted(hist.items(), key=lambda x: -x[1]):
            if k:
                print(f"  ?{k:<12} x{v}")
        print("--- mnemonic top ---")
        for k, v in sorted(mnem.items(), key=lambda x: -x[1])[:18]:
            print(f"  {k:<7} {v}")

if __name__ == '__main__':
    main()
