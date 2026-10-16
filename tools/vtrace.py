#!/usr/bin/env python3
"""vtrace: extract per-source-line $V IR op chains from compiler batch
transcripts. Usage: vtrace.py <transcript-file...> [--name P068E5]"""
import re, sys

OP_RE = re.compile(r'^\s*\d{2}\s+([A-Z]{2,4})\s+(.*)$')
SRC_RE = re.compile(r'^\s*(\d+)\s+[a-e]\s+([0-9A-F]{4})\s+(.*)$')

def parse(path):
    raw = open(path, errors='replace').read()
    raw = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw).replace('\r', '')
    # second half (pass 2+3 listing) contains the IR; start from last
    # 'COMPILATION OF' occurrence per file and take IR lines.
    out = {}
    cur = None
    name = None
    for line in raw.split('\n'):
        m = re.search(r'COMPILATION OF: (\w+)', line)
        if m:
            name = m.group(1)
            out.setdefault(name, [])
            cur = None
            continue
        if name is None:
            continue
        m = SRC_RE.match(line)
        if m:
            lineno, off, text = m.groups()
            entry = (int(lineno), text.rstrip())
            out[name].append({'stmt': entry, 'ops': []})
            cur = out[name][-1]
            continue
        m = OP_RE.match(line)
        if m and cur is not None and out[name]:
            cur['ops'].append((m.group(1), m.group(2).rstrip()))
    return out

def main():
    args = sys.argv[1:]
    only = None
    if '--name' in args:
        i = args.index('--name')
        only = args[i + 1]
        args = args[:i] + args[i + 2:]
    for path in args:
        data = parse(path)
        for name, stmts in data.items():
            if only and name != only:
                continue
            interesting = [s for s in stmts if s['ops']]
            if not interesting:
                continue
            print(f"########## {name}")
            for s in interesting:
                (ln, text), ops = s['stmt'], s['ops']
                print(f"  L{ln}: {text}")
                for op, arg in ops:
                    print(f"      {op:<5} {arg}")
            print()

if __name__ == '__main__':
    main()
