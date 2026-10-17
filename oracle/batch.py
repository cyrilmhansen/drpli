#!/usr/bin/env python3
"""Phase-0 golden runner: compile artefacts/*.PLI with the PL/I-80 v1.4
oracle under z80pack cpmsim (-8 pure-8080) and archive outputs.

Design note (user-verified): cpmsim cannot see disk image changes made by
the host while it runs -> one simulator session per batch; fresh compiler
disk per batch; outputs extracted after halt.

Filesystem safety: ALL disk/scratch creation goes through cpmwork (per-run
workspace subdir, copied read-only boot seeds, fresh mkfs, shell=False,
CP/M-name validation, symlink rejection, no silent output clobber). See
cpmwork.py docstring. Nothing outside golden/<TAG> and the workspace is
written; nothing pre-existing is deleted.

Usage:
  batch.py --all [--switches '$D'] [--batch-size 4] [--tag first]
  batch.py DEMO ACK [--switches '$L$D'] [--reuse] [--keep-run]
Outputs:
  golden/<TAG>/<NAME>/NAME.PRN, NAME.REL, transcript.txt, dir.txt
"""
import argparse, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import cpmwork
from cpmwork import Workspace, Output, SafetyError, check_name

PROJ = os.path.dirname(ROOT)
ART  = os.environ.get("PLI_SRC", os.path.join(PROJ, "artefacts"))
ORIG = os.path.join(PROJ, "artefacts")
SEEDS = os.path.join(ROOT, "disks")            # read-only boot images live here
WORKSPACE = os.environ.get("PLI80_WORKSPACE", os.path.join(ROOT, "workspace"))
COMPILER = ["PLI.COM", "PLI0.OVL", "PLI1.OVL", "PLI2.OVL", "PLILIB.IRL"]
CONTEXT  = ["RECORD.DCL", "FCB.DCL", "DIO80.DCL", "DIOMOD.DCL",
            "MPMDIO.DCL", "MATSIZE.LIB", "Z80.LIB"]
BOOT_SEEDS = {"a": "drivea.dsk", "b": "driveb.dsk"}
SIM = os.environ.get("CPMSIM",
        os.path.expanduser("~/pli/cpm/z80pack/cpmsim/cpmsim"))


def build_disk(run, names):
    # A/B: copied read-only boot seeds; C: compiler+context (fresh mkfs);
    # D: fresh work disk (sources+outputs).
    for d, seed in BOOT_SEEDS.items():
        run.seed(d, seed)
    run.mkfs("c")
    run.mkfs("d")
    for f in COMPILER + CONTEXT:
        src = os.path.join(ORIG, f)
        if os.path.exists(src):
            run.import_local("c", src, f)
    for n in names:
        run.import_local("d", os.path.join(ART, n + ".PLI"), n + ".PLI")
    # %INCLUDE resolves to the SOURCE drive (manual 2.6, confirmed C014)
    for f in CONTEXT:
        src = os.path.join(ORIG, f)
        if os.path.exists(src):
            run.import_local("d", src, f)


def run_session(run, names, switches, out):
    script_txt = "C:\n" + "".join(f"PLI D:{n} {switches}\n" for n in names) \
                 + "##HALT\n"
    # session.txt is scratch -> lives in the per-run workspace, not golden
    script = os.path.join(run.dir, "session.txt")
    with open(script, "w") as f:
        f.write(script_txt)
    rc, transcript = run.run_sim(SIM, script, 240)
    transcript = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", transcript)
    return rc, transcript


def classify(transcript, name):
    starts = [m.start() for m in
              re.finditer(rf">>> PLI (?:D:)?{re.escape(name)}( |$)", transcript)]
    if not starts:
        return "incomplete"
    ends = [m.start() for m in re.finditer(r">>> ", transcript)
            if m.start() > starts[0]]
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
    ap.add_argument("--reuse", action="store_true",
                    help="allow adding into / overwriting an existing golden "
                         "tag dir (default REFUSES to touch pre-existing goldens)")
    ap.add_argument("--keep-run", action="store_true",
                    help="keep the per-run workspace dir instead of cleaning up")
    a = ap.parse_args()

    names = a.names
    if a.all:
        names = sorted(check_name(os.path.splitext(f)[0])
                       for f in os.listdir(ART) if f.endswith(".PLI"))
    names = [check_name(n) for n in names]

    ws = Workspace(WORKSPACE, SEEDS)
    out = Output(os.path.join(PROJ, "golden"), a.tag, allow_reuse=a.reuse)
    results = {}
    for i in range(0, len(names), a.batch_size):
        batch = names[i:i + a.batch_size]
        print(f"== batch {batch}", flush=True)
        run = cpmwork.Run(ws, f"{a.tag}-{i // a.batch_size}")
        try:
            build_disk(run, batch)
            rc, tr = run_session(run, batch, a.switches, out)
            for n in batch:
                od = out.subdir(n)
                got = {}
                out.write(n, "dir.txt", run.ls("d"))
                for ext in ("PRN", "REL"):
                    got[ext] = run.export("d", f"{n}.{ext}", od,
                                          allow_clobber=a.reuse)
                results[n] = dict(status=classify(tr, n), outputs=got)
                print(f"   {n}: {results[n]}", flush=True)
            out.write(".", f"transcript-batch{i // a.batch_size}.txt", tr)
        finally:
            if not a.keep_run:
                run.cleanup()
    summary = "".join(
        f"{n}\t{r['status']}\tPRN={r['outputs'].get('PRN')} "
        f"REL={r['outputs'].get('REL')}\n"
        for n, r in sorted(results.items()))
    out.write(".", "summary.txt", summary)
    print("summary:", sum(1 for r in results.values() if r["status"] == "ok"),
          "ok /", len(results), "->", out.dir)


if __name__ == "__main__":
    try:
        main()
    except SafetyError as e:
        print(f"SAFETY: {e}", file=sys.stderr)
        sys.exit(3)
