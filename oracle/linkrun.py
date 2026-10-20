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

# [E2E-11 step 3e] extra .REL modules a program must be linked against, as
# (module, golden-tag-containing-it).  DIV2/FDIV2 are DR's own assembly sources
# assembled by RMAC from the distribution disk -- see assemble() below.
EXTRA_REL = {"DTEST": [("DIV2", "e2e140asm")],
             "FDTEST": [("FDIV2", "e2e140asm")]}

INPUTS = {
    "DEMO":       ["John\\r"],
    "X201":       ["WORLD\\r"],
    "DECPOLY":    ["1.4, 2.3, 5.67\\r", "0,0,0\\r"],
    "FLTPOLY":    ["1.4, 2.3, 5.67\\r", "0,0,0\\r"],
    # [E2E-11 step 2] FLTPOLY2 is the ENDFILE acceptance target, so its script
    # MUST end with an explicit ^Z: two computed rows, then EOF, so the handler
    # fires and the transcript distinguishes C110's three outcomes.  Relying on
    # the harness default EOF would make "nothing printed" equal "nothing
    # printed" -- which the R913-R917 note in this table already warns is not
    # evidence.  The ^Z needs its own preceding CR [C113].
    "FLTPOLY2":   ["1.4, 2.3, 5.67\\r", "2,3,4\\r", "\\x1a\\r"],
    # [E2E-7A slice 4] numeric GET probes (input script per program)
    "R901":       ["500\\r"],
    "R902":       ["1.25\\r", "3.1416\\r"],
    "R903":       ["42\\r"],
    "R904":       ["42,7.50\\r"],
    "R905":       ["17\\r"],
    "R906":       ["1.234\\r"],
    "R907":       ["\\x1a"],
    # [E2E-7A slice 4, second pass] the promoted GET shapes (R913/R914/R915/
    # R917) need real scripts: without them the harness default EOF makes the
    # transcript a 2-byte nothing-equal-to-nothing, which is NOT proof.
    "R913":       ["31\\r"],
    "R914":       ["77\\r"],
    "R915":       ["HELLO,42\\r"],
    "R917":       ["ABCD,EFGH\\r"],
    "LOAN1":      ["500\\r", "14\\r", "22.10\\r", "\\x1a"],
    "LOAN2":      ["$con\\r", "3000\\r", "14\\r", "144.03\\r", "0\\r", "11\\r", "80\\r", "12\\r", "0\\r", "\\x1a"],
    "ANNUITY":    ["32000\\r", "0\\r", "8.75\\r", "360\\r", "\\x1a"],
    "ACK":        ["\\x1a"],
    "COPY":       ["\\x1a"],
    # [E2E-11 step 1] ON ENDFILE(SYSIN) semantics probes.  Each script is
    # chosen so the transcript distinguishes handler-return / handler-re-enter
    # / handler-terminal on its own, without me assuming C102's arithmetic
    # behaviour carries over.
    "E11A":       ["\\x1a\\r"],
    "E11B":       ["7\\r", "\\x1a"],
    "E11C":       ["7\\r", "8\\r", "\\x1a\\r"],
    "E11D":       ["\\x1a"],
    "E11E":       ["\\x1a"],
    "E11F":       ["\\x1a"],
    "E12D":       ["\\x1a"],
    "E15D09":     ["\\x1a"],
}
DEFAULT_INPUT = ["\\x1a"]

# [E2E-11 step 1] DATA-FILE STAGING and OUTPUT-FILE CAPTURE.
#
# Why this exists: a SYSIN endfile cannot be OBSERVED through console scripting.
# The session script's trailing ^Z is consumed by CP/M's own command-line read,
# and once the script buffer is exhausted a program's CONIN simply blocks -- so
# E11A/E11C/E11E/E11F all reached the timeout with no handler output at all,
# which tells me nothing about ENDFILE semantics (only that the harness cannot
# ask the question).  A named disk file CAN deliver a real EOF, so the ENDFILE
# probes open a staged file instead.  This is also the answer to the
# "what does the harness need for real FILE work" question: per-run input-file
# staging (import_local, already present) plus post-run output-file export
# (export, already present) -- the gap was only that the run stage never used
# them.  Output .REL comparison stays byte-exact; output-DATA comparison uses
# the same cmp-of-raw-bytes rule, against files exported here, not transcripts.
STAGE_IN = {
    # DR ignores title('E16IN DAT') and builds the FCB from the FILE variable's
    # OWN name: the runtime asked for "INF=NUL".  So the staged file must be
    # named INF.DAT.  (Recorded as evidence, not worked around silently.)
    "E16A": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E16B": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E16C": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
}
# Command tail per program: DR's stream files name themselves from $1/$2 in
# the invocation tail (COPY.KJM's own pattern), so the tail IS the staging API.
ARGS = {
    # Measured, not guessed: DR's title('$1.$1') splits the command tail at the
    # first SPACE into name/ext, so 'E17D OUT DAT' created a CP/M file literally
    # named "out" (no extension) and 'INF DAT' never found INF.DAT -- the
    # runtime reported "File: INF=NUL".  A single dotted token is what works.
    "E17A": "INF.DAT",
    "E17B": "INF.DAT",
    "E17C": "INF.DAT",
    "E17D": "OUT.DAT",
    "E18A": "INF.DAT",
    "E18B": "INF.DAT",
}
STAGE_IN.update({
    "E17A": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E17B": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E17C": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E18A": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
    "E18B": [("d", "INF.DAT", os.path.join(PROJ, "e13dat/INF.DAT"))],
})
EXPORT_OUT = {
    # same default-naming rule: an output FILE named OUTF
    # lands as OUTF.DAT, not E16OUT.DAT
    "E16D": ["OUTF.DAT", "E16OUT.DAT"],
    "E17D": ["OUT.DAT", "OUT"],
}


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


# [E2E-11 step 5] multi-module PL/I programs: the corpus ships pairs such as
# CALL.PLI (main, declares `a entry(float) returns(float)') + A.PLI (the
# procedure-only module that defines a), and DR's own instructions for the
# MPMCALLA/MPMCALLB pair say  `link mpmcalla,mpmcallb,mpmdio'  -- every object is
# NAMED on the LINK command line.  Merely having the companion .REL present on
# D: is NOT the same operation: with `LINK D:E29G' alone, LINK resolves the
# EXTREF by auto-loading whatever module carries the symbol, and the resulting
# .COM dies at the first cross-module call WITHOUT printing anything (measured on
# both DR-built and my byte-identical objects, so this is not a codegen
# difference).  Same-tag companions, unlike EXTRA_REL's cross-tag assembly
# modules: they come from the very tag being linked, so a DR-built side and a
# mine-built side each link their own objects.
SAME_TAG_OBJS = {
    "E29F": ["A"], "E29G": ["A"], "E29J": ["A"], "E29I": ["B"],
}
# Set LINK_NO_EXTRA=1 to link WITHOUT naming companion objects, i.e. reproduce the
# auto-search form.  Needed to MEASURE what LINK actually reports there instead of
# reasoning about it -- the per-name status line is capped at 120 characters, which
# is exactly what hid whether an UNDEFINED SYMBOLS list was empty or truncated.
NO_EXTRA = bool(os.environ.get("LINK_NO_EXTRA"))


def parse_undefined(seg_text):
    """[E2E-12/C137] The undefined-symbol list LINK 1.31 prints for one program's
    link segment, or [] if it reported none.  Extracted from link() so the
    detection has a pinned regression test: LINK writes a .COM even when a
    cross-module reference is UNRESOLVED, so 'a .COM appeared' is not a pass, and
    the one signal that distinguishes success from a broken program is this list.
    seg_text must be the FULL segment (carriage returns already normalised), not
    the truncated display string -- a [:120] slice of the real transcript ends
    exactly at 'UNDEFINED SYMBOLS:' and therefore reads as clean."""
    m = re.search(r"UNDEFINED SYMBOLS:\s*\n(.*?)(?:\n\s*ABSOLUTE|\Z)",
                  seg_text, re.S)
    return re.findall(r"[A-Za-z][A-Za-z0-9$.]{0,7}", m.group(1)) if m else []


def selftest():
    """C137 regression, pinned to the two stored link transcripts (golden/e2e153_l3
    = companion NOT named, golden/e2e153_l4 = companion named).  Both produced a
    .COM; only one is usable.  If the detection ever stops separating them, the
    link stage would silently accept a program that dies at runtime -- which is
    exactly what happened here before the list was parsed."""
    cases = [
        ("golden/e2e153_l3/link-batch0.transcript.txt", "E29F", ["A"],
         "companion NOT named on the LINK command line"),
        ("golden/e2e153_l4/link-batch0.transcript.txt", "E29F", [],
         "companion named (LINK D:E29F,D:A)"),
    ]
    bad = 0
    for path, name, expect, why in cases:
        full = os.path.join(PROJ, path)
        if not os.path.exists(full):
            print(f"UNDEF-SELFTEST FAIL: missing pinned transcript {path}")
            bad += 1
            continue
        tr = open(full, encoding="utf-8", errors="replace").read()
        seg = re.search(rf">>> LINK D:{re.escape(name)}(.*?)(?=>>> |\Z)",
                        tr, re.S)
        if not seg:
            print(f"UNDEF-SELFTEST FAIL: no link segment for {name} in {path}")
            bad += 1
            continue
        got = parse_undefined(re.sub(r"\r+\n", "\n", seg.group(1)))
        ok = got == expect
        print(f"{'OK  ' if ok else 'FAIL'} undefined_symbols({os.path.basename(os.path.dirname(full))})"
              f" = {got or '[]'}  expected {expect or '[]'}  [{why}]")
        if not ok:
            bad += 1
    # The detector must not depend on what the DISPLAY shows.  This is the actual
    # lesson, and it is stronger than the one I first wrote down: I claimed the old
    # [:120] status cap hid the symbol name, but the transcript that produced that
    # reading (the first e2e150dl link) was OVERWRITTEN when I re-linked with
    # --reuse, and the surviving broken-link transcript puts `A' at character 110 --
    # INSIDE the old cap.  So that mechanism is not pinned by any artifact I still
    # have, and asserting it here would have been me testing a story instead of
    # testing the code.  What is verifiable, and what matters, is that the parser is
    # independent of presentation: a segment whose header line is long enough to push
    # the symbol past any display window must still be detected.
    synth = ("LINK D:X\n\nLINK 1.31\n\nPLILIB   RQST   X     0100   "
             + ("/SYSIN/  1C77   " * 12)
             + "\n\nUNDEFINED SYMBOLS:\n\nQ       \n\nABSOLUTE     0000\n")
    found = parse_undefined(synth)
    visible = "Q" in synth[:120].split("UNDEFINED SYMBOLS")[-1] if False else \
        bool(re.search(r"\bQ\b", synth[:120].split("UNDEFINED SYMBOLS")[-1]))
    ok = found == ["Q"] and not visible
    print(f"{'OK  ' if ok else 'FAIL'} display-independence: symbol at char "
          f"{synth.index(chr(10) + 'Q')} is beyond the old 120-char status window "
          f"and parse_undefined still returns {found}")
    if not ok:
        bad += 1

    return bad


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
                # [E2E-11 step 3e] programs whose arguments name an EXTERNAL
                # assembly routine need that module present, or LINK reports it
                # missing and the .COM is not built.
                for e2 in ([] if NO_EXTRA else SAME_TAG_OBJS.get(n, [])):
                    p3 = os.path.join(src_rel, e2, f"{e2}.REL")
                    if os.path.exists(p3):
                        run.import_local("d", p3, f"{e2}.REL")
                for extra in EXTRA_REL.get(n, []):
                    p2 = os.path.join(PROJ, "golden", extra[1], f"{extra[0]}.REL")
                    if os.path.exists(p2):
                        run.import_local("d", p2, f"{extra[0]}.REL")
            def linkcmd(n):
                mods = ",".join(([f"D:{e2}" for e2 in SAME_TAG_OBJS.get(n, [])]
                                if not NO_EXTRA else [])
                                + [f"D:{e[0]}" for e in EXTRA_REL.get(n, [])])
                return f"LINK D:{n}" + (f",{mods}" if mods else "")
            lines = ["C:"] + [linkcmd(n) for n in batchn] + ["##HALT"]
            rc, tr = session(run, lines, 40, out, f"link-batch{i // batch}")
            for n in batchn:
                ok = run.export("d", f"{n}.COM", out.dir,
                                allow_clobber=reuse)
                seg = re.search(rf">>> LINK D:{re.escape(n)}(.*?)(?=>>> |\Z)",
                                tr, re.S)
                # [E2E-11 step 5] LINK 1.31 does NOT resolve a cross-module PL/I
                # reference by searching D: -- the companion object has to be NAMED
                # on the command line (`link mpmcalla,mpmcallb,mpmdio', exactly as
                # the corpus instructions say).  What it does instead is the trap:
                # it prints `UNDEFINED SYMBOLS:` followed by the name, and STILL
                # WRITES A .COM.  That .COM runs with the reference unresolved, dies
                # at the first cross-module call, prints nothing, and returns rc=0 --
                # so a link stage that only checks "did a .COM appear" accepts a
                # broken program.  Measured: E29F+A unnamed = 7808-byte .COM, silent
                # exit; named = 8320-byte .COM, correct output.  Extract the list
                # from the FULL segment text and surface it, because the display
                # message is capped and the cap is what nearly misled me here.
                full = re.sub(r"\r+\n", "\n", seg.group(1)) if seg else ""
                um = re.search(r"UNDEFINED SYMBOLS:\s*\n(.*?)(?:\n\s*ABSOLUTE|\Z)",
                               full, re.S)
                undef = re.findall(r"[A-Za-z][A-Za-z0-9$.]{0,7}",
                                   um.group(1)) if um else []
                # [E2E-11 step 5] cap raised from 120 to 400: the old cap cut LINK's report off
                # right after "UNDEFINED SYMBOLS:", which is precisely the part that
                # mattered.  Never let a display limit hide a diagnostic.
                msg = re.sub(r"\r+\n", " | ", seg.group(1).strip())[:400] if seg else ""
                if undef:
                    print(f"   LINK-FAIL {n}: COM={ok} but UNDEFINED SYMBOLS: "
                          f"{' '.join(undef)} -- the .COM is unusable; name every "
                          f"object on the LINK command line", flush=True)
                else:
                    print(f"   {n}: COM={ok} {msg}", flush=True)
        finally:
            run.cleanup()


def assemble(ws, names, outtag, batch, reuse):
    """[E2E-11 step 3e] Assemble a historical DR assembly module with the REAL
    tool from the distribution disk, and return its .REL to golden/<outtag>/.

    Why RMAC rather than a translation: DIV2.ASM and FDIV2.ASM are written in
    Microsoft MAC-80 dialect -- `title 'division by power of two'`, `public
    div2`, `extrn ?signal`, `;` comments -- not DR ASSEMBLE syntax (NAME/
    ENTRY/EXTERNAL, `&` comments), so ASM.COM is the wrong tool and any
    "close enough" rewrite would make the resulting .REL evidence about my
    rewrite instead of about DR's module.  RMAC.COM is already staged by the
    link stage, so this uses machinery the harness has been using all along.

    Why it matters: external-ENTRY acceptance needs a DIV2.REL built from DR's
    own source through period software, so a linked DTEST.COM is a test of MY
    compiler's ENTRY lowering rather than of my assembly transcription.
    """
    out = Output(os.path.join(PROJ, "golden"), outtag, allow_reuse=reuse)
    for i in range(0, len(names), batch):
        batchn = names[i:i + batch]
        run = new_run(ws, f"asm-{outtag}-{i // batch}")
        try:
            run.mkfs("c")
            run.mkfs("d")
            for t in TOOLS:
                p = os.path.join(ORIG, t)
                if os.path.exists(p):
                    run.import_local("c", p, t)
            missing = []
            for n in batchn:
                src = None
                for cand in (os.path.join(ORIG, n + ".ASM"),
                             os.path.join(PROJ, "artefacts", n + ".ASM")):
                    if os.path.exists(cand):
                        src = cand
                        break
                if src is None:
                    missing.append(n)
                    continue
                with open(src, "rb") as f:
                    raw = f.read()
                tmp = os.path.join(out.dir, n + ".CRLF.ASM")
                crlf = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                if not crlf.endswith(b"\x1a"):
                    crlf += b"\x1a"
                with open(tmp, "wb") as f:
                    f.write(crlf)
                run.import_local("d", tmp, n + ".ASM")
            for n in missing:
                print(f"   {n}: SOURCE .ASM MISSING", flush=True)
            present = [n for n in batchn if n not in missing]
            if not present:
                continue
            lines = ["C:"] + [f"RMAC D:{b}.ASM=D:{b}.REL/L" for b in present] + ["##HALT"]
            rc, tr = session(run, lines, 40, out, f"asm-batch{i // batch}")
            for b in present:
                ok = run.export("d", f"{b}.REL", out.dir, allow_clobber=reuse)
                seg = re.search(r">>> RMAC D:" + re.escape(b) + r"(.*?)(?=>>> |\Z)",
                                tr, re.S)
                msg = re.sub(r"\r+\n", " | ", seg.group(1).strip())[:140] if seg else ""
                print(f"   {b}: REL={ok} {msg}", flush=True)
        finally:
            run.cleanup()



def run_programs(ws, names, intag, outtag, timeout, reuse, killon=None):
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
            for drive, on_disk, local in STAGE_IN.get(n, []):
                if os.path.isfile(local):
                    r.import_local(drive, local, on_disk)
            # PROMPT SYNC: after the D: switch the stale 'D>' echo can
            # satisfy a later ##WAIT, which used to abort long-running or
            # non-terminating programs before they produced anything.
            # Sending a lone CR and waiting for the FRESH prompt it
            # echoes makes the sync explicit. The extra bytes land
            # BEFORE the program's own console region, so transcript
            # extraction (anchored on 'NAME\r\r\n') is unaffected.
            tail = ([f"##KILLON {killon}"] if killon
                    else ["##WAIT \\nD>"])
            sess = (["C:", "D:", "##SEND \\r", "##WAIT \\nD>",
                     f"##SEND {n + (' ' + ARGS[n] if n in ARGS else '')}\\r"]
                    + [f"##SEND {i}" for i in INPUTS.get(n, DEFAULT_INPUT)]
                    + tail + ["##HALT"])
            rc, tr = session(r, sess, timeout, out, n)
            clean = re.sub(r">>> [^\n]*\n", "", tr)
            # [E2E-11] ARGS puts a command tail on the invocation line, so the
            # old anchor ('NAME\r\r\n') no longer matched and every tailed run
            # produced an empty output file -- a silent failure that looks
            # exactly like a program that printed nothing.  Accept the tail.
            seg = re.search(rf"{re.escape(n)}[^\n]*\r\r\n(.*?)(?=\nD>|I/O ran|\Z)",
                            clean, re.S)
            o = seg.group(1) if seg else ""
            status = "done" if rc == 0 else "timeout-or-hang"
            out.write(".", f"{n}.output.txt", re.sub(r"\r\n?", "\n", o))
            captured = []
            for fn in EXPORT_OUT.get(n, []):
                fdir = os.path.join(out.dir, n)
                os.makedirs(fdir, exist_ok=True)
                got = r.export("d", fn, fdir, allow_clobber=reuse)
                captured.append(f"{fn}={'yes' if got else 'no'}")
            if EXPORT_OUT.get(n) and not any("=yes" in c for c in captured):
                # never guess where a file went -- show the directory
                try:
                    captured.append("D:=" + " ".join(sorted(r.ls("d"))))
                except Exception as e:
                    captured.append(f"ls failed: {e}")
            print(f"   {n}: rc={rc} {status} {' '.join(captured)}".rstrip(),
                  flush=True)
        finally:
            r.cleanup()


def main():
    # [E2E-12/C137] The selftest reads pinned transcripts only: no emulator, no
    # workspace, no tag.  It therefore has to be dispatched BEFORE argparse, whose
    # --tag/--out are required for the stages that do need them.
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(1 if selftest() else 0)
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["link", "run", "asm", "selftest"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=40)
    ap.add_argument("--reuse", action="store_true",
                    help="allow overwriting an existing golden out tag")
    ap.add_argument("--killon", default=None, metavar="REGEX",
                    help="run stage: STOP (kill) the program as soon as this "
                         "regex matches its console output instead of waiting "
                         "for the D> prompt -- gives a BOUNDED transcript "
                         "prefix for non-terminating programs (E2E-5c slice "
                         "2). The transcript is still written.")
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
    if a.stage == "asm":
        assemble(ws, names, a.out, a.batch, a.reuse)
    elif a.stage == "link":
        link(ws, names, a.tag, a.out, a.batch, a.reuse)
    else:
        run_programs(ws, names, a.tag, a.out, a.timeout, a.reuse, a.killon)


if __name__ == "__main__":
    try:
        main()
    except SafetyError as e:
        print(f"SAFETY: {e}", file=sys.stderr)
        sys.exit(3)
