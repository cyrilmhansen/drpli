#!/usr/bin/env python3
"""Extract per-file $S symbol-table sections from batch transcripts into
golden/<tag>/S/<NAME>.s.txt for byte-diffing against our own binder."""
import re, os, sys

def extract(transcript_dir):
    outdir = os.path.join(transcript_dir, 'S')
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(transcript_dir)):
        if 'transcript' not in fn or fn.endswith('.keep.txt'):
            continue
        raw = open(os.path.join(transcript_dir, fn), errors='replace').read()
        raw = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw).replace('\r', '')
        parts = re.split(r'COMPILATION OF: (\w+)', raw)
        for i in range(1, len(parts) - 1, 2):
            name, body = parts[i], parts[i + 1]
            j = body.find('SYMBOLS:')
            if j < 0:
                continue
            seg = body[j + len('SYMBOLS:'):]
            k = seg.find('NO ERROR(S) IN PASS 1')
            seg = seg[:k if k >= 0 else 4000]
            lines = [l.rstrip() for l in seg.split('\n')
                     if l.strip() and not l.strip().startswith('---')]
            # the SECOND full dump (pass-2 tail) repeats SYMBOLS; take first
            path = os.path.join(outdir, name + '.s.txt')
            if os.path.exists(path):
                continue
            with open(path, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            n += 1
    print(f"extracted {n} sections -> {outdir}")

if __name__ == '__main__':
    for d in sys.argv[1:]:
        extract(d)
