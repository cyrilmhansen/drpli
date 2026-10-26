#!/usr/bin/env python3
"""[E2E-41/P3b] WHAT FILE DOES E16D ACTUALLY CREATE?

`golden/e2e11iu' holds DR's own runs of E17A..E17D but NO run of E16D, and this harness'
EXPORT_OUT guess for E16D used to be ["OUTF.DAT", "E16OUT.DAT"] -- names that are NOT on the disk
after a run.  "No file under the two names I guessed" is not a measurement, so this probe compiles
E16D with the CURRENT binary, links it through the harness, runs it through the harness' own
`run_programs' (same session script, same drives, same tail rules -- nothing re-implemented) with
the run's cleanup disabled, then lists and exports the WHOLE D: image.  The name, the length and
the bytes come off the disk, not out of a table.

What it established (spec/lab-evidence/e2e41-p3/E16D-RUN.txt):
  * E16D creates the CP/M file `E16OUT' -- no extension -- because its OPEN carries the LITERAL
    title 'E16OUT DAT' and DR builds the FCB from the FILE variable's name (OUTF -> E16OUT is the
    TITLE, not the variable; see the note);
  * the file is exactly 128 bytes, 13 payload bytes + 115 x 0x1A, and its SHA-256 equals DR's own
    golden/e2e11iu/E17D/OUT.DAT;
  * exporting it needed oracle/cpmwork.py's F83_RE fixed -- the old pattern required a dot, so the
    guard refused the extensionless name and the harness reported "no file" for a program that had
    demonstrably written one.

Nothing in golden/ apart from the runtime-evidence dir golden/e32rt_E16D/ (which is where the
runtime panel puts its own material) is written; the CP/M run dir stays in the scratch workspace.

  usage: python3 spec/lab-evidence/e2e41-p3/p3b-e16d-run.py > E16D-RUN.txt
"""
import hashlib
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "oracle"))
import cpmwork                                     # noqa: E402
import linkrun                                     # noqa: E402

NAME, TAG = "E16D", "e32rt_E16D"
GOLDEN = os.path.join(ROOT, "golden/e2e11h/E16D/E16D.REL")
BIN = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")
adir = os.path.join(ROOT, "golden", TAG, NAME)
os.makedirs(adir, exist_ok=True)

rel = "/tmp/e2e41-p3b/E16D.REL"
os.makedirs(os.path.dirname(rel), exist_ok=True)
r = subprocess.run([BIN, os.path.join(ROOT, "e13src/E16D.PLI"), rel],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit("compile refused: " + (r.stderr or "").strip()[-200:])
same = open(rel, "rb").read() == open(GOLDEN, "rb").read()
print("### my build vs DR golden %s: %s" % (GOLDEN, "byte-identical" if same else "DIFFERS"))
if not same:
    sys.exit("refusing to run a non-byte-exact object")
shutil.copy(rel, os.path.join(adir, NAME + ".REL"))
shutil.copy(os.path.join(ROOT, "golden/e2e11h/E16D/E16D.PRN"),
            os.path.join(adir, NAME + ".PRN"))

ws = cpmwork.Workspace(linkrun.WORKSPACE, linkrun.SEEDS)
linkrun.link(ws, [NAME], TAG, TAG, 400, True)
com = os.path.join(ROOT, "golden", TAG, NAME + ".COM")
if not os.path.exists(com):
    sys.exit("link produced no %s" % com)
print("### linked %s (%d bytes) -- LINK-80's own image of my .REL" %
      (os.path.relpath(com, ROOT), os.path.getsize(com)))

# Disable ONLY the run-dir cleanup: everything else is the harness' own code path.
kept = []
cpmwork.Run.cleanup = lambda self: kept.append(self.dir)
linkrun.run_programs(ws, [NAME], TAG, TAG, 40, True)
if not kept:
    sys.exit("no run dir was recorded -- cleanup patch did not take")
run_dir = kept[-1]
disk = os.path.join(run_dir, "drived.dsk")
print("### run dir (scratch workspace, deleted afterwards): %s" % run_dir)
print("### drive d after the run (cpmls -l) -- EVERY file, name straight off the disk")
p = subprocess.run(["/usr/bin/cpmls", "-f", cpmwork.FMT, "-l", disk],
                   capture_output=True, text=True)
print(p.stdout.rstrip() or "(empty)")
if p.stderr.strip():
    print("cpmls stderr:", p.stderr.strip())
print("### every file on d: except the program itself, exported and hashed")
q = subprocess.run(["/usr/bin/cpmls", "-f", cpmwork.FMT, disk],
                   capture_output=True, text=True)
tmp = os.path.join(run_dir, "export")
os.makedirs(tmp, exist_ok=True)
found, paths = {}, {}
for line in q.stdout.splitlines():
    f = line.strip()
    if not f or f.upper() == NAME + ".COM":
        continue
    dst = os.path.join(tmp, f.upper())
    rr = subprocess.run(["/usr/bin/cpmcp", "-f", cpmwork.FMT, disk, "0:" + f, dst],
                        capture_output=True, text=True)
    if rr.returncode != 0 or not os.path.exists(dst):
        print("   %-14s cpmcp FAILED: %s" % (f, rr.stderr.strip()[:100]))
        continue
    b = open(dst, "rb").read()
    found[f.upper()] = b
    paths[f.upper()] = dst
    print("   %-14s %4d bytes sha256=%s" % (f, len(b), hashlib.sha256(b).hexdigest()[:16]))
    print("        first 32: %s" % b[:32].hex(" "))
    print("        as text : %r" % b[:64])
    print("        distinct tail byte: %s"
          % sorted({"%02X" % c for c in b[min(13, len(b)):]}))
g = open(os.path.join(ROOT, "golden/e2e11iu/E17D/OUT.DAT"), "rb").read()
print("### reference: DR's own golden/e2e11iu/E17D/OUT.DAT = %d bytes, sha256=%s"
      % (len(g), hashlib.sha256(g).hexdigest()[:16]))
for f, b in found.items():
    if f == NAME + ".COM":
        continue
    print("   %-14s == DR OUT.DAT byte for byte: %s (mine %d, DR %d)"
          % (f, b == g, len(b), len(g)))
    if b != g:
        at = next((i for i in range(min(len(b), len(g))) if b[i] != g[i]), min(len(b), len(g)))
        print("      first difference at byte %d: mine %r golden %r"
              % (at, b[max(0, at - 4):at + 4], g[max(0, at - 4):at + 4]))
# The runtime panel's own export, so `--runtime --only E16D' can find it.
# cpmls/cpmcp report the disk's own case (lower), so look the staged copy up upper-cased.
if "E16OUT" in paths:
    tgt = os.path.join(adir, "E16OUT")
    shutil.copy(paths["E16OUT"], tgt)
    print("### staged the measured file at %s (%d bytes) for the runtime row"
          % (os.path.relpath(tgt, ROOT), os.path.getsize(tgt)))
shutil.rmtree(run_dir, ignore_errors=True)
print("### run dir removed; golden/%s keeps the .REL/.PRN/.COM and the exported file" % TAG)
