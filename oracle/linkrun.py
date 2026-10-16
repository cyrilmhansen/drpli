#!/usr/bin/env python3
"""Phase-1 stage 2: LINK-80 + PLILIB.IRL -> .COM, then EXECUTE programs
under cpmsim -8 with scripted console input.

  linkrun.py link  --tag first8080u --out link1 [--names A B| --all]
  linkrun.py run   --tag link1       --out run1  [--names ...]

Layout: C: = LINK.COM (+LIB/RMAC) + PLILIB.IRL; D: = .REL/.COM + data.
Link results land next to the source REL (to verify). Run sessions are
one-program-per-session so a hung program cannot poison the rest.
Default program stdin script: one EOF (^Z); override in INPUTS below.
"""
import argparse, os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
ORIG = os.path.join(PROJ, "artefacts")
DISKS = os.path.join(ROOT, "disks")
FMT = "ibm-3740"
TOOLS = ["LINK.COM", "LIB.COM", "RMAC.COM", "PLILIB.IRL"]

# per-program console input lines (raw, escape-decoded by run.py ##SEND)
INPUTS = {
    "DEMO":       ["John\\r"],
    "DECPOLY":    ["1.4, 2.3, 5.67\\r", "0,0,0\\r"],
    "FLTPOLY":    ["1.4, 2.3, 5.67\\r", "0,0,0\\r"],
    "FLTPOLY2":   ["1.4, 2.3, 5.67\\r", "0,0,0\\r"],
    "LOAN1":      ["500\\r", "14\\r", "22.10\\r", "\\x1a"],
    "LOAN2":      ["$con\\r", "3000\\r", "14\\r", "144.03\\r", "0\\r", "11\\r", "80\\r", "12\\r", "0\\r", "\\x1a"],
    "ANNUITY":    ["32000\\r", "0\\r", "8.75\\r", "360\\r", "\\x1a"],
    "ACK":        ["\\x1a"],
    "COPY":       ["\\x1a"],
}
DEFAULT_INPUT = ["\\x1a"]

def sh(cmd):
    return subprocess.run(cmd, shell=True, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def newdisk(path):
    sh(f"rm -f {path} && mkfs.cpm -f {FMT} {path}")

def cp(disk, local, ondisk):
    sh(f"cpmcp -f {FMT} {disk} '{local}' 0:{ondisk}")

def session(script_lines, timeout, tagdir, name):
    os.makedirs(tagdir, exist_ok=True)
    spath = os.path.join(tagdir, f"{name}.session.txt")
    open(spath, "w").write("\n".join(script_lines) + "\n")
    env = dict(os.environ, CPMSIM_EXTRA="-u")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "run.py"),
                        "--disks", DISKS, "--timeout", str(timeout), spath],
                       capture_output=True, env=env)
    tr = r.stdout.decode("latin-1")
    tr = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", tr)
    open(os.path.join(tagdir, f"{name}.transcript.txt"), "w").write(tr)
    return r.returncode, tr

def link(names, intag, outtag, batch=3):
    gdir = os.path.join(PROJ, "golden", outtag)
    os.makedirs(gdir, exist_ok=True)
    for i in range(0, len(names), batch):
        batchn = names[i:i+batch]
        newdisk(f"{DISKS}/drivec.dsk"); newdisk(f"{DISKS}/drived.dsk")
        for t in TOOLS:
            cp(f"{DISKS}/drivec.dsk", os.path.join(ORIG, t), t)
        for n in batchn:
            rel = os.path.join(PROJ, "golden", intag, n, f"{n}.REL")
            if os.path.exists(rel):
                cp(f"{DISKS}/drived.dsk", rel, f"{n}.REL")
        lines = ["C:"] + [f"LINK D:{n}" for n in batchn] + ["##HALT"]
        rc, tr = session(lines, 40, gdir, f"link-batch{i//batch}")
        for n in batchn:
            ok = False
            r = subprocess.run(f"cpmcp -f {FMT} {DISKS}/drived.dsk "
                               f"0:{n}.COM {gdir}/{n}.COM 2>/dev/null",
                               shell=True, capture_output=True)
            ok = r.returncode == 0 and os.path.getsize(f"{gdir}/{n}.COM") > 0
            if not ok and os.path.exists(f"{gdir}/{n}.COM"):
                os.remove(f"{gdir}/{n}.COM")
            seg = re.search(rf">>> LINK D:{n}(.*?)(?=>>> |\Z)", tr, re.S)
            msg = re.sub(r"\r+\n", " | ", seg.group(1).strip())[:120] if seg else ""
            print(f"   {n}: COM={ok} {msg}", flush=True)
        shutil.copy(os.path.join(gdir, f"link-batch{i//batch}.transcript.txt"),
                    os.path.join(gdir, f"link-batch{i//batch}.transcript.keep.txt"))

def run(names, intag, outtag, timeout=40):
    gdir = os.path.join(PROJ, "golden", outtag)
    os.makedirs(gdir, exist_ok=True)
    for n in names:
        com = os.path.join(PROJ, "golden", intag, f"{n}.COM")
        if not os.path.exists(com):
            continue
        newdisk(f"{DISKS}/drivec.dsk"); newdisk(f"{DISKS}/drived.dsk")
        cp(f"{DISKS}/drived.dsk", com, f"{n}.COM")
        sess = (["C:", "D:", f"##SEND {n}\\r"]
                + [f"##SEND {i}" for i in INPUTS.get(n, DEFAULT_INPUT)]
                + ["##WAIT \\nD>", "##HALT"])
        rc, tr = session(sess, timeout, gdir, n)
        clean = re.sub(r">>> [^\n]*\n", "", tr)
        seg = re.search(rf"{n}\r\r\n(.*?)(?=\nD>|I/O ran|\Z)", clean, re.S)
        out = seg.group(1) if seg else ""
        status = "done" if rc == 0 else "timeout-or-hang"
        open(os.path.join(gdir, f"{n}.output.txt"), "w").write(
            re.sub(r"\r\n?", "\n", out))
        print(f"   {n}: rc={rc} {status}", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["link", "run"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=3)
    a = ap.parse_args()
    src = os.path.join(PROJ, "golden", a.tag)
    if a.all:
        if a.stage == "link":
            names = sorted(d for d in os.listdir(src)
                           if os.path.exists(os.path.join(src, d, d + ".REL")))
        elif a.stage == "run":
            names = sorted(d[:-4] for d in os.listdir(src)
                           if d.endswith(".COM"))
    else:
        names = a.names
    if names is None:
        sys.exit("no names given (use --names or --all)")
    if a.stage == "link":
        link(names, a.tag, a.out, a.batch)
    else:
        run(names, a.tag, a.out)

if __name__ == "__main__":
    main()
    # end
