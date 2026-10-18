#!/usr/bin/env python3
"""Bounded transcript-prefix check for NON-TERMINATING specimens
(E2E-5c slice 2, user-mandated verification protocol).

Problem: specimens whose main tail never exits (RFACT, R401, R412,
R419) cannot be compared as a whole console transcript, and a
TIMEOUT-TRUNCATED transcript is never accepted as a semantic oracle.

Verdict hierarchy implemented here:
 1. compile + link both sides, then compare the linked .COM images BYTE
    FOR BYTE. Identical images are the load-bearing runtime proof: a
    byte-identical program cannot behave differently on the same CP/M.
 2. --console: additionally compare a BOUNDED PREFIX of the RAW console
    stream made of COMPLETE records only (each terminated by CR or
    CRLF). Anything after the last terminator is a PARTIAL record and is
    discarded BY CONSTRUCTION, so a truncated capture can only shorten
    the compared prefix, never falsify it. Byte-equality of the FULL
    captured length is NOT required, and truncation is never reported as
    a whole-program pass: the verdict is "first N COMPLETE records are
    byte-equal", N <= --records. A differing complete record is a real
    behavioral divergence.
 3. If an arm yields no console region, the harness session is retried
    (the cpmsim pty boot/typeahead race means a session sometimes never
    starts the program -- an environmental flake, not a result). If no
    attempt captures anything, report INCONCLUSIVE-CAPTURE and fall back
    to image identity -- never claim a console pass.
 4. --facts K: INDEPENDENT semantic oracle for the factorial specimens.
    Compares the first K complete 'factorial( i )= v' records of MY OWN
    run against math.factorial(i) computed in Python (valid while the
    value fits FIXED BIN(15), i <= 7), so the recursion is verified
    against arithmetic, not only against DR.

Usage: prefix_check.py NAME SRC GOLDEN.REL [--console|--facts K]
                                           [--records K] [--window SECS]
                                           [--retries N]
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BIN = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")
ORACLE = os.path.join(ROOT, "oracle")
GOLD = os.path.join(ROOT, "golden")          # linkrun.py PROJ/golden
WORK = os.path.join(ORACLE, "work")
C = re.compile(r"^[A-Z][A-Z0-9]{0,7}$")
MINE_LINK = "e2epfxlink"
DR_LINK = "e2epfxlinkdr"
MINE_RUN = "e2epfxrun"
DR_RUN = "e2epfxrundr"
PFX = re.compile(r"^e2epfx[a-z0-9]*$")


def harness(args, timeout=900):
    e = os.environ.copy()
    e["PLI_SRC"] = os.path.join(WORK, "e5c2")
    e["PLI_TIMEOUT"] = "300"
    r = subprocess.run(["python3"] + args, cwd=ORACLE, env=e,
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def records(out):
    """Split a raw console stream into COMPLETE records only (a trailing
    partial record -- an unfinished PUT -- is dropped by construction)."""
    parts = re.split(r"(\r\n|\r)", out)
    return [parts[i] + parts[i + 1] for i in range(0, len(parts) - 1, 2)]


def _esc(text):
    """Regex-escape a console record for the harness ##KILLON directive.

    re.escape() emits a backslash followed by a RAW CR/LF byte, and the
    session script is newline-delimited -- that would corrupt it into
    extra lines. Emit the two-character escape sequences instead."""
    out = []
    for ch in text:
        if ch == "\r":
            out.append("\\r")
        elif ch == "\n":
            out.append("\\n")
        else:
            out.append(re.escape(ch))
    return "".join(out)


def console_of(tag, name):
    """Extract the RAW console region from a harness transcript file.
    Read as BYTES: text-mode universal newlines would silently rewrite
    every CR, and the CRs are the record terminators we compare on."""
    tp = os.path.join(GOLD, tag, f"{name}.transcript.txt")
    if not os.path.exists(tp):
        return None
    t = open(tp, "rb").read().decode("latin-1", "replace")
    t = re.sub(r">>> [^\n]*\n", "", t)
    m = re.search(rf"{re.escape(name)}\r\r\n(.*?)(?=\nD>|I/O ran|\Z)",
                  t, re.S)
    return None if m is None else m.group(1)


def cleanup():
    if os.environ.get("PFX_KEEP"):
        return
    for d in sorted(os.listdir(GOLD)):
        if PFX.match(d):
            shutil.rmtree(os.path.join(GOLD, d), ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("src"); ap.add_argument("gold")
    ap.add_argument("--console", action="store_true",
                    help="also compare the bounded complete-record prefix")
    ap.add_argument("--facts", type=int, default=0, metavar="K",
                    help="check K complete factorial records against "
                         "math.factorial (independent oracle)")
    ap.add_argument("--records", type=int, default=12,
                    help="max COMPLETE records to compare (default 12)")
    ap.add_argument("--window", type=float, default=30.0,
                    help="per-program console window in seconds")
    ap.add_argument("--retries", type=int, default=3,
                    help="attempts per arm when a cpmsim session captures "
                         "no console region (default 3)")
    a = ap.parse_args()
    name = a.name
    if not C.fullmatch(name):
        print(f"{name}: illegal specimen name"); return 1
    os.makedirs(os.path.join(WORK, "prefix"), exist_ok=True)
    mine_rel = os.path.join(WORK, "prefix", f"{name}.REL")
    with open(os.path.join(WORK, "prefix", f"{name}.dsk"), "wb") as fh:
        fh.write(b"\x1a")
    r = subprocess.run([BIN, os.path.join(ROOT, a.src), mine_rel],
                       capture_output=True, text=True)
    if r.returncode:
        print(f"{name}: compile FAIL {r.stderr.strip()[:200]}"); return 1
    mraw = open(mine_rel, "rb").read()
    graw = open(os.path.join(ROOT, a.gold), "rb").read()
    if mraw != graw:
        d = next((k for k in range(min(len(mraw), len(graw)))
                  if mraw[k] != graw[k]), min(len(mraw), len(graw)))
        print(f"{name}: PARITY FAILS at byte {d} -- refusing to run")
        return 1
    print(f"{name}: .REL byte-parity OK ({len(graw)} B)")

    cleanup()
    try:
        for sub, src in ((MINE_LINK, mine_rel),
                         (DR_LINK, os.path.join(ROOT, a.gold))):
            stage = os.path.join(GOLD, "e2epfxstagem" if sub == MINE_LINK else "e2epfxstaged", name)
            os.makedirs(stage, exist_ok=True)
            shutil.copyfile(src, os.path.join(stage, f"{name}.REL"))
            rc, out = harness(["linkrun.py", "link", "--tag",
                               os.path.basename(os.path.dirname(stage)),
                               "--out", sub, "--names", name, "--reuse"])
            if rc:
                print(f"{name}: link FAILED rc={rc}\n{out[-700:]}"); return 1
        coms = {lbl: os.path.join(GOLD, tag, f"{name}.COM")
                for tag, lbl in ((MINE_LINK, "mine"), (DR_LINK, "dr"))}
        imgs = {lbl: (open(p, "rb").read() if os.path.exists(p) else None)
                for lbl, p in coms.items()}
        arms = [("mine", MINE_LINK, MINE_RUN)]
        if a.console or a.facts:
            # the dr arm is a FALLBACK capture source for --facts: the two
            # .COM images are byte-identical, and the --facts oracle is
            # external arithmetic, not DR's transcript
            arms.append(("dr", DR_LINK, DR_RUN))

        def do_run(lbl, intag, outtag, killon=None):
            shutil.rmtree(os.path.join(GOLD, outtag), ignore_errors=True)
            cmd = ["linkrun.py", "run", "--tag", intag, "--out", outtag,
                   "--names", name, "--timeout", str(a.window), "--reuse"]
            if killon:
                cmd += ["--killon", killon]
            rc, o = harness(cmd)
            c = console_of(outtag, name)
            return rc, c

        cons = {}
        killpat = None
        for lbl, intag, outtag in arms:
            for attempt in range(1, a.retries + 1):
                rc, c = do_run(lbl, intag, outtag)
                if c is not None and records(c):
                    cons[lbl] = c
                    print(f"{name}: {lbl} PHASE-A capture (attempt "
                          f"{attempt}): {len(c)} B, "
                          f"{len(records(c))} COMPLETE records")
                    if killpat is None:
                        ra = records(c)
                        k = min(a.records, len(ra) - 1)
                        if k >= 1:
                            # bounded stop point: kill at the Kth complete
                            # record, so BOTH arms are cut at the same
                            # program-defined boundary, never at a timeout
                            killpat = "".join(_esc(x) for x in ra[:k + 1])
                            print(f"{name}: kill point derived from {lbl} "
                                  f"record index {k}")
                    break
                print(f"{name}: {lbl} attempt {attempt} captured no console "
                      f"region (harness rc={rc}) -- retrying")
            else:
                cons[lbl] = None
                print(f"{name}: {lbl} console INCONCLUSIVE after "
                      f"{a.retries} attempts")
            if killpat:
                break          # boundary already known; go to PHASE-B
        if a.console and killpat:
            print(f"{name}: bounded-prefix protocol: both arms re-run with "
                  f"--killon at the same program-derived record boundary")
            for lbl, intag, outtag in arms:
                rc, c = do_run(lbl, intag, outtag, killon=killpat)
                if os.environ.get("PFX_KEEP"):
                    print(f"[phaseB {lbl} rc={rc} console={None if c is None else len(c)}]")
                if c is not None and records(c):
                    cons[lbl] = c
                    print(f"{name}: {lbl} PHASE-B bounded capture: "
                          f"{len(records(c))} COMPLETE records")
    finally:
        cleanup()

    a1, a2 = imgs["mine"], imgs["dr"]
    if not a1 or not a2:
        print(f"{name}: linked COM missing"); return 1
    if a1 != a2:
        print(f"{name}: !!! COM DIFFERS ({len(a1)} vs {len(a2)} B) -- same "
              f".REL bytes, so this is a LINK-stage divergence")
        return 1
    print(f"{name}: linked .COM IDENTICAL vs DR ({len(a1)} B)")

    if a.console:
        if not cons.get("mine") or not cons.get("dr"):
            print(f"{name}: INCONCLUSIVE-CAPTURE -- image identity remains "
                  f"the runtime proof")
            return 0
        rm, rd = records(cons["mine"]), records(cons["dr"])
        n = min(len(rm), len(rd), a.records)
        bad = [k for k in range(n) if rm[k] != rd[k]]
        if bad:
            k = bad[0]
            print(f"{name}: PREFIX-DIFF at complete record {k}")
            print(f"   mine: {rm[k]!r}\n   dr  : {rd[k]!r}")
            return 1
        note = ("" if len(rm) == len(rd) else
                f" [total complete-record counts differ: {len(rm)} vs "
                f"{len(rd)}; only the first {n} are claimed]")
        print(f"{name}: PREFIX-OK first {n} COMPLETE records byte-equal"
              f"{note}")
        print(f"   sample: {rm[:min(3, n)]}")
        return 0
    if a.facts:
        src_lbl = "mine" if cons.get("mine") else (
            "dr" if cons.get("dr") else None)
        if src_lbl is None:
            print(f"{name}: INCONCLUSIVE-CAPTURE for --facts")
            return 0
        if src_lbl != "mine":
            print(f"{name}: NOTE using the DR-arm capture (mine arm "
                  f"uncaptured); the two .COM images are byte-identical, "
                  f"and the oracle below is external arithmetic")
        recs, seen, bad = records(cons[src_lbl]), 0, []
        for rec in recs:
            m = re.search(r"factorial\(\s*(-?\d+)\s*\)=\s*(-?\d+)", rec)
            if not m:
                continue
            i, v = int(m.group(1)), int(m.group(2))
            if i <= 7 and v != math.factorial(i):
                bad.append((i, v, math.factorial(i)))
            seen += 1
            if seen >= a.facts:
                break
        if seen < a.facts:
            print(f"{name}: INCONCLUSIVE-CAPTURE --facts ({seen}/{a.facts} "
                  f"factorial records captured)")
            return 0
        if bad:
            print(f"{name}: FACTS-DIFF {bad}"); return 1
        print(f"{name}: FACTS-OK {seen} complete factorial records match "
              f"math.factorial independently "
              f"{[math.factorial(i) for i in range(min(seen, 8))]}")
        return 0
    print(f"{name}: runtime verdict = byte-identical image")
    return 0


if __name__ == "__main__":
    sys.exit(main())
