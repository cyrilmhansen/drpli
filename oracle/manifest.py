#!/usr/bin/env python3
"""Write MANIFEST.sha256 (sha256sum-compatible format) for a golden tag dir.
Excludes MANIFEST.sha256 itself and *.session.txt (driver scripts, not oracle
output). Usage: manifest.py [tagdir ...]  (default: all golden/* dirs)."""
import hashlib, os, sys

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "golden")

def digest(d):
    h = hashlib.sha256()
    with open(d, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def manifest(tagdir):
    entries = []
    for root, _, files in os.walk(tagdir):
        for fn in sorted(files):
            if fn == "MANIFEST.sha256" or fn.endswith(".session.txt"):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, tagdir)
            entries.append(f"{digest(p)}  {rel}")
    out = os.path.join(tagdir, "MANIFEST.sha256")
    open(out, "w").write("\n".join(sorted(entries)) + "\n")
    print(f"{out}: {len(entries)} files")

if __name__ == "__main__":
    args = sys.argv[1:] or sorted(
        os.path.join(GOLDEN, d) for d in os.listdir(GOLDEN)
        if os.path.isdir(os.path.join(GOLDEN, d)))
    for a in args:
        manifest(a)
