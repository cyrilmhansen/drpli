#!/usr/bin/env python3
"""Phase-1 stage 2: LINK-80 + PLILIB.IRL -> .COM, then EXECUTE programs
under cpmsim -8 with scripted console input.

  linkrun.py link  --tag first8080u --out link1 [--names A B| --all]
  linkrun.py run   --tag link1       --out run1  [--names ...]

Layout: C: = LINK.COM (+LIB/RMAC) + PLILIB.IRL; D: = .REL/.COM + data.
Link results land next to the source REL (to verify). Run sessions are
one-program-per-session so a hung program cannot poison the rest.
Default program stdin script: one EOF (^Z); override in INPUTS below.

Filesystem safety: identical guarantees to batch.py -- see cpmwork.py.
Boot seeds are copied per-run (never the originals touched); scratch disks
are freshly mkfs'd in a per-run workspace subdir; all tool calls are
shell=False argv lists with validated CP/M names; golden outputs are not
clobbered unless --reuse.
"""
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import cpmwork
from cpmwork import Workspace, Output, SafetyError, check_name

PROJ = os.path.dirname(ROOT)
ORIG = os.path.join(PROJ, "artefacts")
SEEDS = os.path.join(ROOT, "disks")
WORKSPACE = os.environ.get("PLI80_WORKSPACE", os.path.join(ROOT, "workspace"))
BOOT_SEEDS = {"a": "drivea.dsk", "b": "driveb.dsk"}
SIM = os.environ.get("CPMSIM",
        os.path.expanduser("~/pli/cpm/z80pack/cpmsim/cpmsim"))
TOOLS = ["LINK.COM", "LIB.COM", "RMAC.COM", "PLILIB.IRL"]

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


def new_run(ws, tag):
    run = cpmwork.Run(ws, tag)
    for d, seed in BOOT_SEEDS.items():
        run.seed(d, seed)
    return run


def session(run, script_lines, timeout, out, name):
    script = os.path.join(run.dir, f"{name}.session.txt")
    with open(script, "w") as f:
        f.write("\n".join(script_lines) + "\n")
    rc, tr = run.run_sim(SIM, script, timeout, {"CPMSIM_EXTRA": "-u"})
    tr = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", tr)
    out.write(".", f"{name}.transcript.txt", tr)
    return rc, tr


def link(ws, names, intag, outtag, batch, reuse):
    out = Output(os.path.join(PROJ, "golden"), outtag, allow_reuse=reuse)
    src_rel = os.path.join(PROJ, "golden", intag)
    for i in range(0, len(names), batch):
        batchn = names[i:i + batch]
        run = new_run(ws, f"link-{outtag}-{i // batch}")
        try:
            run.mkfs("c")
            run.mkfs("d")
            for t in TOOLS:
                p = os.path.join(ORIG, t)
                if os.path.exists(p):
                    run.import_local("c", p, t)
            for n in batchn:
                rel = os.path.join(src_rel, n, f"{n}.REL")
                if os.path.exists(rel):
                    run.import_local("d", rel, f"{n}.REL")
            lines = ["C:"] + [f"LINK D:{n}" for n in batchn] + ["##HALT"]
            rc, tr = session(run, lines, 40, out, f"link-batch{i // batch}")
            for n in batchn:
                ok = run.export("d", f"{n}.COM", out.dir,
                                allow_clobber=reuse)
                seg = re.search(rf">>> LINK D:{re.escape(n)}(.*?)(?=>>> |\Z)",
                                tr, re.S)
                msg = re.sub(r"\r+\n", " | ", seg.group(1).strip())[:120] if seg else ""
                print(f"   {n}: COM={ok} {msg}", flush=True)
        finally:
            run.cleanup()


def run_programs(ws, names, intag, outtag, timeout, reuse):
    out = Output(os.path.join(PROJ, "golden"), outtag, allow_reuse=reuse)
    src_com = os.path.join(PROJ, "golden", intag)
    for n in names:
        com = os.path.join(src_com, f"{n}.COM")
        if not os.path.exists(com):
            continue
        r = new_run(ws, f"run-{outtag}-{n}")
        try:
            r.mkfs("c")
            r.mkfs("d")
            r.import_local("d", com, f"{n}.COM")
            sess = (["C:", "D:", f"##SEND {n}\\r"]
                    + [f"##SEND {i}" for i in INPUTS.get(n, DEFAULT_INPUT)]
                    + ["##WAIT \\nD>", "##HALT"])
            rc, tr = session(r, sess, timeout, out, n)
            clean = re.sub(r">>> [^\n]*\n", "", tr)
            seg = re.search(rf"{re.escape(n)}\r\r\n(.*?)(?=\nD>|I/O ran|\Z)",
                            clean, re.S)
            o = seg.group(1) if seg else ""
            status = "done" if rc == 0 else "timeout-or-hang"
            out.write(".", f"{n}.output.txt", re.sub(r"\r\n?", "\n", o))
            print(f"   {n}: rc={rc} {status}", flush=True)
        finally:
            r.cleanup()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["link", "run"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=40)
    ap.add_argument("--reuse", action="store_true",
                    help="allow overwriting an existing golden out tag")
    a = ap.parse_args()
    ws = Workspace(WORKSPACE, SEEDS)
    src = os.path.join(PROJ, "golden", a.tag)
    if a.all:
        if a.stage == "link":
            names = sorted(check_name(d) for d in os.listdir(src)
                           if os.path.exists(os.path.join(src, d, d + ".REL")))
        else:
            names = sorted(check_name(d[:-4]) for d in os.listdir(src)
                           if d.endswith(".COM"))
    else:
        names = [check_name(n) for n in a.names] if a.names else None
    if not names:
        sys.exit("no names given (use --names or --all)")
    if a.stage == "link":
        link(ws, names, a.tag, a.out, a.batch, a.reuse)
    else:
        run_programs(ws, names, a.tag, a.out, a.timeout, a.reuse)


if __name__ == "__main__":
    try:
        main()
    except SafetyError as e:
        print(f"SAFETY: {e}", file=sys.stderr)
        sys.exit(3)
