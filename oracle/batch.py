#!/usr/bin/env python3
"""Phase-0 golden runner: compile artefacts/*.PLI with the PL/I-80 v1.4
oracle under z80pack cpmsim (-8 pure-8080) and archive outputs.

Design note (user-verified): cpmsim cannot see disk image changes made by
the host while it runs -> one simulator session per batch; fresh compiler
disk per batch; outputs extracted after halt.

Usage:
  batch.py --all [--switches '$D'] [--batch-size 4] [--tag first]
  batch.py DEMO ACK [--switches '$L$D']
Outputs:
  golden/<TAG>/<NAME>/NAME.PRN, NAME.REL, transcript.txt, dir.txt
"""
import argparse, os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
ART  = os.environ.get("PLI_SRC", os.path.join(PROJ, "artefacts"))
ORIG = os.path.join(PROJ, "artefacts")
DISKS = os.path.join(ROOT, "disks")
COMPILER = ["PLI.COM", "PLI0.OVL", "PLI1.OVL", "PLI2.OVL", "PLILIB.IRL"]
CONTEXT  = ["RECORD.DCL", "FCB.DCL", "DIO80.DCL", "DIOMOD.DCL",
            "MPMDIO.DCL", "MATSIZE.LIB", "Z80.LIB"]
FMT = "ibm-3740"

MKFS = "/usr/bin/mkfs.cpm" if os.path.exists("/usr/bin/mkfs.cpm") else "mkfs.cpm"
CPMCP = "/usr/bin/cpmcp" if os.path.exists("/usr/bin/cpmcp") else "cpmcp"

def sh(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          **kw)

def build_disk(names):
    # C: compiler + context (fixed), D: fresh work disk (sources+outputs)
    for d in ("c", "d"):
        sh(f"rm -f {DISKS}/drive{d}.dsk && {MKFS} -f {FMT} {DISKS}/drive{d}.dsk")
    for f in COMPILER + CONTEXT:
        src = os.path.join(ORIG, f)
        if os.path.exists(src):
            sh(f"{CPMCP} -f {FMT} {DISKS}/drivec.dsk {src} 0:{f}")
    for n in names:
        sh(f"{CPMCP} -f {FMT} {DISKS}/drived.dsk {os.path.join(ART, n+'.PLI')} 0:{n}.PLI")
    # %INCLUDE resolves to the SOURCE drive (manual 2.6, confirmed C014)
    for f in CONTEXT:
        src = os.path.join(ORIG, f)
        if os.path.exists(src):
            sh(f"{CPMCP} -f {FMT} {DISKS}/drived.dsk {src} 0:{f}")

def run_session(names, switches, outdir):
    script = os.path.join(outdir, "session.txt")
    with open(script, "w") as f:
        f.write("C:\n")
        for n in names:
            f.write(f"PLI D:{n} {switches}\n")
        f.write("##HALT\n")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "run.py"),
                        "--disks", DISKS, "--timeout", "240", script],
                       capture_output=True)
    transcript = r.stdout.decode("latin-1")
    transcript = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", transcript)
    open(os.path.join(outdir, "transcript.txt"), "w").write(transcript)
    return r.returncode, transcript

def extract(name, outdir):
    got = {}
    dl = os.path.join(outdir, "dir.txt")
    with open(dl, "w") as f:
        f.write(sh(f"cpmls -l -f {FMT} {DISKS}/drived.dsk").stdout.decode())
    for ext in ("PRN", "REL"):
        dst = os.path.join(outdir, f"{name}.{ext}")
        r = subprocess.run(f"cpmcp -f {FMT} {DISKS}/drived.dsk 0:{name}.{ext} {dst}",
                           shell=True, capture_output=True)
        got[ext] = (r.returncode == 0 and os.path.exists(dst)
                    and os.path.getsize(dst) > 0)
        if not got[ext] and os.path.exists(dst):
            os.remove(dst)
    return got

def classify(transcript, name):
    starts = [m.start() for m in re.finditer(rf">>> PLI (?:D:)?{name}( |$)", transcript)]
    if not starts:
        return "incomplete"
    ends = [m.start() for m in re.finditer(r">>> ", transcript) if m.start() > starts[0]]
    seg = transcript[starts[0]:ends[0] if ends else len(transcript)]
    if (re.search(r"NO ERROR\(S\) IN PASS 1", seg)
            and re.search(r"NO ERROR\(S\) IN PASS 2", seg)
            and not re.search(r"\b[1-9][0-9]* ERROR\(S\) IN PASS", seg)):
        return "ok"
    if re.search(r"ERROR\(S\) IN PASS", seg):
        return "diag"
    return "incomplete"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--switches", default="$L$D")
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args()
    names = a.names
    if a.all:
        names = sorted(os.path.splitext(f)[0].upper()
                       for f in os.listdir(ART) if f.endswith(".PLI"))
    gdir = os.path.join(PROJ, "golden", a.tag)
    os.makedirs(gdir, exist_ok=True)
    results = {}
    for i in range(0, len(names), a.batch_size):
        batch = names[i:i+a.batch_size]
        print(f"== batch {batch}", flush=True)
        build_disk(batch)
        rc, tr = run_session(batch, a.switches, gdir)
        for n in batch:
            od = os.path.join(gdir, n)
            os.makedirs(od, exist_ok=True)
            got = extract(n, od)
            results[n] = dict(status=classify(tr, n), outputs=got)
            print(f"   {n}: {results[n]}", flush=True)
        # keep transcripts per batch too
        shutil.copy(os.path.join(gdir, "transcript.txt"),
                    os.path.join(gdir, f"transcript-batch{i//a.batch_size}.txt"))
    with open(os.path.join(gdir, "summary.txt"), "w") as f:
        for n, r in sorted(results.items()):
            f.write(f"{n}\t{r['status']}\t"
                    f"PRN={r['outputs'].get('PRN')} REL={r['outputs'].get('REL')}\n")
    print("summary:", sum(1 for r in results.values() if r['status']=='ok'),
          "ok /", len(results), "->", gdir)

if __name__ == "__main__":
    main()
