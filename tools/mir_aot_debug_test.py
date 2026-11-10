#!/usr/bin/env python3
"""E2E-54/P1-mD native-DWARF runner (PLAN §P1-mD.6, work-order step 4).

Debuggable native objects built by the MIR path (PL/I -> HIR -> MIR text +
sidecar debug map -> mir2o --debug-map -> genuine MIR object with a named
.debug_frame -> pinned Cosmopolitan static link -> native execution AND gdb
source-level session) are JUDGED BY OBSERVED BEHAVIOUR: exact executed bytes
and exact gdb output.  Every command a DIRECT rc, separate processes, NEVER
batched with builds.

Panels (contract: PLAN §P1-mD.6; environment laws §P1-mD.7):

  W0  prerequisites: pli80mir.exe built; build/p1m0-deps/mir2o present (rebuilt
      from the COMMITTED tools/mir_aot/mir2o.c by `sh tools/mir_aot/build_native.sh`,
      which verifies the laboratory pins); console runtime/driver committed;
      the pinned Cosmopolitan toolchain identified (cosmo_link.sh --toolchain).

  W1  CLI pin panel, run FROM THE REPOSITORY ROOT (the sidecar `file` row is
      cwd-dependent by the hop-6 measured law): pli80mir -g with an EXPLICIT
      --debug-map and with the DEFAULT map path (OUT.mir ^ ".p1md"); stdout and
      the .mir file byte-equal to the frozen pin hir/mir-expected/M05.mir; the
      map byte-equal to the ADDITIVE pin hir/mir-debug-expected/M05.p1md;
      determinism x2 fresh processes.

  W2  debug object: mir2o -f M05.mir M05.o --debug-map MAP rc 0 in TWO fresh
      processes, byte-identical to each other, and its sha256 recorded BEFORE
      linking EQUALS the frozen debug pin §P1-mD.5 (cb263c2c...); the .text-
      bearing sections .eh_frame/.rela.eh_frame are GONE, .debug_frame named.

  W3  readelf law panel on the debug object: named .debug_frame PROGBITS; NO
      .eh_frame and NO .rela.eh_frame anywhere; .rela.debug_frame RELA present;
      --debug-dump=decodedline names the pinned absolute source path and rows
      at 0xc0/0xd6/0x121/0x14b (lines 3,3,4,5, stmt) with the 0x176 end row —
      the addresses DERIVE from the pinned sidecar (function at 0xc0, line-map
      offsets 22/97/139, code length 182); --debug-dump=frames-interp decodes
      one CIE and one FDE pc=00000000000000c0..0000000000000176; nm T pli80_iorw.

  W4  cosmo links via tools/mir_aot/cosmo_link.sh: optlinux PRIMARY, tiny
      SECONDARY; console_check.c (-DENTRY, NO -DEXPECTED: the runner judges the
      bytes) + pli_console.c + the debug object; artifact starts 0x7fELF; the
      chmod +x law is applied by this runner before any exec.

  W5  EXEC legs (fresh process each): stdin b"77\\n" -> stdout EXACTLY b"77\\n",
      stderr EXACTLY b"driver-return=77\\n", rc 0; one optlinux re-run for
      determinism.

  W6  gdb battery on the optlinux debug exe (D1 + D2), -batch -nx with debuginfod
      OFF, stdin 77: break M05.pli:4 RESOLVES; run HITS at pli80_iorw, M05.pli:4;
      print n == $1 = 77 (D2 variable inspection); stepi advances within line 4;
      info line names the pinned range <pli80_iorw+97>..<pli80_iorw+139> (the
      sidecar line map); info source reports the pinned CU and DWARF 4 producer
      mir-debug; bt shows EXACTLY #0 pli80_iorw ... M05.pli:4 and #1 main;
      continue prints 77 and the inferior exits normally; gdb rc 0.

  W7  non-vacuity controls, each OBSERVED FAILING LOUDLY (perturbations live
      ONLY in scratch copies under ignored build/; committed sources are never
      perturbed); if a control PASSES, THIS RUNNER FAILS:
        D-C1  the NO-DEBUG link (default mir2o, no --debug-map) still EXECUTES
              77 but gdb break M05.pli:4 refuses "No source file named M05.pli"
              and gdb exits non-zero — the debug evidence is not free-standing.
        D-C2  sidecar sha row tampered -> mir2o refuses rc 8 naming "sha MISMATCH",
              NO object written.
        D-C3  insn-count tampered (one insn record deleted) and opcode tampered
              (insn 0 alloca -> add) -> mir2o refuses rc 8 naming "count MISMATCH"
              and "opcode MISMATCH", NO object written.

  W8  glibc DIAGNOSTIC-REFERENCE leg (§P1-mD.1 fact 8): gcc links the SAME debug
      object with the console runtime; the run and one gdb break/print/bt session
      are recorded as EVIDENCE ONLY — never a delivery gate, never a failure.

THE EXPECTED BYTES, ROWS AND MESSAGES BELOW ARE COPIED FROM THE PINS AND PLAN
§P1-mD (§§P1-mD.1/.3/.5/.6) AND FROM THE MEASURED FIRST-HAND LEGS OF SESSIONS
hop 6 (pins) and hop 7 (debug leg, gdb battery, rc 7/8 arms) — where they were
fixed BEFORE this runner judged anything (never-fit law).  This runner NEVER
regenerates or overwrites any expected file.

Evidence -> ignored build/mir-debug/runner/.  ZERO oracle: nothing here is a
DR claim; this is native toolchain engineering evidence.

Prerequisites (separate commands, §P1-mD.7):
    (cd ocaml && eval "$(opam env)" && dune build)
    sh tools/mir_aot/build_native.sh
Run:  eval "$(opam env)" && python3 tools/mir_aot_debug_test.py
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLIMIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
MIR2O = REPO / "build" / "p1m0-deps" / "mir2o"
DRIVER = REPO / "tools" / "mir_aot" / "console_check.c"
RUNTIME = REPO / "tools" / "mir_aot" / "pli_console.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
FIXTURE = REPO / "hir" / "mir-fixtures" / "M05.pli"
MIR_PIN = REPO / "hir" / "mir-expected" / "M05.mir"
MAP_PIN = REPO / "hir" / "mir-debug-expected" / "M05.p1md"
OUTDIR = REPO / "build" / "mir-debug" / "runner"

# §P1-mD.5 — the debug object is pinned BY SHA256, recorded (by the hop-6
# measurement) BEFORE any link; byte-identical to the hop-3 probe artifact.
DEBUG_O_SHA = "cb263c2c69c1f31f456f8391fc7694f9418d4c32044e0ad2cc385a0e33984782"

# §P1-mD.1 fact 1 + the sidecar pin: M05 iorw, lines 3/4/5; function at 0xc0,
# line-map offsets 22/97/139, code length 182 -> end 0x176.  DERIVED, not fitted.
LINE_ROWS = [("0xc0", "3"), ("0xd6", "3"), ("0x121", "4"), ("0x14b", "5")]
FDE_PC = "pc=00000000000000c0..0000000000000176"

ENV = dict(os.environ, LC_ALL="C")  # stable toolchain messages for evidence
FAILURES: list[str] = []
CHECKS = 0


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"ok    {msg}")


def run(argv: list, stdin: bytes = b"", timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True,
                          timeout=timeout, env=ENV, cwd=REPO)


def record(name: str, data: bytes) -> None:
    (OUTDIR / name).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------- W0 ----------

def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, MIR2O, DRIVER, RUNTIME,
                                                  RECIPE, FIXTURE, MIR_PIN, MAP_PIN)
               if not p.exists()]
    if missing:
        fail(f"W0: prerequisites missing: {', '.join(missing)} — run '(cd ocaml && "
             "dune build)' and 'sh tools/mir_aot/build_native.sh' first")
        return False
    ok("W0: prerequisites present — pli80mir.exe, mir2o, console runtime/driver, "
       "cosmo recipe, M05 fixture, MIR pin, sidecar pin")
    r = run(["sh", RECIPE, "--toolchain"], timeout=60)
    if r.returncode != 0:
        fail(f"W0: cosmo_link.sh --toolchain rc {r.returncode}: "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return False
    ok("W0: pinned Cosmopolitan toolchain identified (§P1-mC K0 law)")
    return True


# ---------- W1 ----------

def cli_leg(tag: str, extra_map: bool) -> Path | None:
    """pli80mir -g from the repo root; returns the MAP path actually written."""
    out = OUTDIR / f"{tag}.mir"
    if out.exists():
        out.unlink()
    argv = [PLIMIR, "-g", "--export", "iorw", "-o", out, FIXTURE]
    map_path = out.with_suffix(out.suffix + ".p1md")
    if extra_map:
        map_path = OUTDIR / f"{tag}.p1md"
        argv += ["--debug-map", map_path]
    for p in (out, map_path):
        if p.exists():
            p.unlink()
    r = run(argv, timeout=60)
    if r.returncode != 0 or not out.exists() or not map_path.exists():
        fail(f"W1 {tag}: rc {r.returncode}, mir={out.exists()}, map={map_path.exists()}"
             f" — stderr {r.stderr.decode(errors='replace')[:200]}")
        return None
    mir_bytes = out.read_bytes()
    if mir_bytes != MIR_PIN.read_bytes() or r.stdout != mir_bytes:
        fail(f"W1 {tag}: .mir bytes moved — file/pin/stdout not all byte-equal")
        return None
    if map_path.read_bytes() != MAP_PIN.read_bytes():
        fail(f"W1 {tag}: sidecar differs from the ADDITIVE pin")
        return None
    ok(f"W1 {tag}: -g wrote the .mir (== frozen pin, stdout equal) and the map "
       f"(== pinned sidecar bytes); map path law honoured "
       f"({'explicit' if extra_map else 'default OUT.mir.p1md'})")
    return map_path


def cli_panel() -> Path | None:
    maps = [cli_leg("explicit1", True), cli_leg("default1", False),
            cli_leg("explicit2", True)]
    if any(m is None for m in maps):
        return None
    if maps[0].read_bytes() != maps[2].read_bytes():
        fail("W1: the two fresh-process sidecar runs differ (determinism broken)")
        return None
    ok("W1: determinism x2 — both fresh-process maps byte-equal")
    return maps[0]


# ---------- W2 ----------

def debug_object(map_path: Path) -> Path | None:
    objs = []
    for i in (1, 2):
        o = OUTDIR / f"M05_dbg{i}.o"
        if o.exists():
            o.unlink()
        r = run([MIR2O, "-f", MIR_PIN, o, "--debug-map", map_path], timeout=60)
        if r.returncode != 0 or not o.exists():
            fail(f"W2: mir2o --debug-map run{i} rc {r.returncode} / object "
                 f"{'absent' if not o.exists() else 'present'} — stderr "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            return None
        objs.append(o)
    if objs[0].read_bytes() != objs[1].read_bytes():
        fail("W2: the two fresh-process debug objects differ")
        return None
    s = sha256(objs[0])
    if s != DEBUG_O_SHA:
        fail(f"W2: debug object sha {s[:16]}... != the frozen §P1-mD.5 pin "
             f"{DEBUG_O_SHA[:16]}...")
        return None
    ok(f"W2: mir2o --debug-map rc 0 x2, byte-identical, sha256 {s[:16]}... "
       f"== frozen debug pin (recorded BEFORE linking)")
    return objs[0]


# ---------- W3 ----------

def readelf_panel(obj: Path) -> bool:
    good = True
    sec = run(["readelf", "-SW", obj], timeout=60).stdout.decode(errors="replace")
    if not re.search(r"\]\s+\.debug_frame\s+PROGBITS", sec):
        fail("W3: no named .debug_frame PROGBITS section"); good = False
    if ".eh_frame" in sec:
        fail("W3: '.eh_frame' still present in the section panel"); good = False
    if not re.search(r"\]\s+\.rela\.debug_frame\s+RELA", sec):
        fail("W3: no .rela.debug_frame RELA section"); good = False
    if good:
        ok("W3: sections — named .debug_frame, NO .eh_frame/.rela.eh_frame, "
           ".rela.debug_frame present")
    line = run(["readelf", "--debug-dump=decodedline", obj], timeout=60).stdout
    line_txt = line.decode(errors="replace")
    cu = MAP_PIN.read_text().splitlines()[2].split(" ", 1)[1]
    if cu not in line_txt:
        fail(f"W3: decodedline does not name the pinned CU path {cu}"); good = False
    for addr, src_line in LINE_ROWS:
        pat = rf"M05\.pli\s+{src_line}\s+{addr}\b"
        if not re.search(pat, line_txt):
            fail(f"W3: decodedline row line {src_line} at {addr} missing"); good = False
    if "0x176" not in line_txt:
        fail("W3: no 0x176 end row in decodedline"); good = False
    if good:
        ok(f"W3: decodedline — CU {cu}, rows "
           f"{', '.join(f'{l}@{a}' for a, l in LINE_ROWS)} and the 0x176 end row")
    frames = run(["readelf", "--debug-dump=frames-interp", obj],
                 timeout=60).stdout.decode(errors="replace")
    if "CIE" not in frames or FDE_PC not in frames:
        fail(f"W3: frames-interp missing the CIE or the FDE {FDE_PC}"); good = False
    elif good:
        ok(f"W3: frames-interp decodes the CIE and the FDE {FDE_PC}")
    nm = run(["nm", obj], timeout=60).stdout.decode(errors="replace")
    if not re.search(r"\bT pli80_iorw\b", nm):
        fail("W3: nm shows no 'T pli80_iorw'"); good = False
    elif good:
        ok("W3: nm — T pli80_iorw")
    return good


# ---------- W4/W5 ----------

def cosmo_link(mode: str, out: Path, obj: Path) -> Path | None:
    if out.exists():
        out.unlink()
    r = run(["sh", RECIPE, mode, out, "--", DRIVER, RUNTIME, obj,
             "-DENTRY=pli80_iorw"], timeout=150)
    if r.returncode != 0 or not out.exists():
        fail(f"W4 {mode}: cosmo_link rc {r.returncode} / artifact "
             f"{'absent' if not out.exists() else 'present'}")
        return None
    if out.read_bytes()[:4] != b"\x7fELF":
        fail(f"W4 {mode}: artifact does not start with the ELF magic"); return None
    os.chmod(out, 0o755)  # the §P1-mD.7 chmod +x law
    ok(f"W4 {mode}: debug object linked to a plain ELF via the pinned recipe; "
       f"chmod +x applied")
    return out


def exec_legs(exes: dict[str, Path]) -> None:
    for mode, exe in exes.items():
        for i in (1, 2) if mode == "optlinux" else (1,):
            r = run([exe], stdin=b"77\n", timeout=60)
            if (r.returncode, r.stdout, r.stderr) != (0, b"77\n", b"driver-return=77\n"):
                fail(f"W5 {mode} run{i}: rc {r.returncode} stdout {r.stdout!r} "
                     f"stderr {r.stderr!r} — expected rc 0, b'77\\n', "
                     f"b'driver-return=77\\n'")
                continue
            ok(f"W5 {mode} run{i}: EXEC stdin 77 -> stdout EXACTLY b'77\\n', "
               f"rc 0 (fresh process)")


# ---------- W6 ----------

GDB_BATTERY = ["gdb", "-batch", "-nx", "-ex", "set debuginfod enabled off",
               "-ex", "break M05.pli:4", "-ex", "run", "-ex", "print n", "-ex", "stepi",
               "-ex", "info line *pli80_iorw+97", "-ex", "info source", "-ex", "bt",
               "-ex", "continue"]


def gdb_panel(exe: Path) -> bool:
    r = run(GDB_BATTERY + [exe], stdin=b"77\n", timeout=120)
    txt = r.stdout.decode(errors="replace")
    record("gdb_optlinux_battery.log",
           txt.encode() + f"\n=== gdb rc {r.returncode} ===\n".encode()
           + r.stderr)
    good = True

    def need(what: str, cond: bool) -> None:
        nonlocal good
        if not cond:
            fail(f"W6 gdb: MISSING — {what}"); good = False

    need("break M05.pli:4 resolved ('Breakpoint 1 at')", "Breakpoint 1 at" in txt)
    need("breakpoint hit in pli80_iorw at M05.pli:4",
         "Breakpoint 1, pli80_iorw () at" in txt and "M05.pli:4" in txt)
    need("print n == $1 = 77 (D2)", "$1 = 77" in txt)
    need("stepi stayed on line 4", re.search(r"0x[0-9a-f]+\s+4\s+put list\(n\);", txt) is not None)
    need("info line names the pinned range +97..+139",
         "Line 4 of" in txt and "<pli80_iorw+97> and ends at" in txt
         and "<pli80_iorw+139>" in txt)
    need("info source: CU M05.pli, producer mir-debug, DWARF 4",
         "Current source file is" in txt and "M05.pli" in txt
         and "Producer is mir-debug." in txt and "DWARF 4" in txt)
    m0 = re.search(r"^#0.*$", txt, re.M)
    m1 = re.search(r"^#1.*$", txt, re.M)
    need("bt #0 pli80_iorw ... M05.pli:4",
         m0 is not None and "pli80_iorw" in m0.group(0) and "M05.pli:4" in m0.group(0))
    need("bt #1 main", m1 is not None and "main" in m1.group(0))
    need("continue printed 77 and the inferior exited normally",
         "\n77\n" in txt and "exited normally" in txt)
    if r.returncode != 0:
        fail(f"W6 gdb: rc {r.returncode}"); good = False
    elif good:
        ok("W6 gdb battery GREEN: break/run/print n=77/stepi/info line +97..+139/"
           "info source DWARF4 mir-debug/bt #0 pli80_iorw at M05.pli:4 #1 main/"
           "continue exit 0 — all on the pinned optlinux debug link")
    return good


# ---------- W7 ----------

def tamper(kind: str) -> Path:
    lines = MAP_PIN.read_text().splitlines()
    if kind == "sha":
        i = next(k for k, l in enumerate(lines) if l.startswith("mir "))
        lines[i] = lines[i][:-1] + ("0" if lines[i][-1] != "0" else "1")
    elif kind == "count":
        k = [j for j, l in enumerate(lines) if l.startswith("insn ")][-1]
        del lines[k]
    elif kind == "opcode":
        j = next(k for k, l in enumerate(lines) if l.startswith("insn "))
        f = lines[j].split()
        f[3] = "add"
        lines[j] = " ".join(f)
    p = OUTDIR / f"tamper_{kind}.p1md"
    p.write_text("\n".join(lines) + "\n")
    return p


def refuse_leg(kind: str, needle: str) -> None:
    mp = tamper(kind)
    o = OUTDIR / f"t_{kind}.o"
    if o.exists():
        o.unlink()
    r = run([MIR2O, "-f", MIR_PIN, o, "--debug-map", mp], timeout=60)
    err = r.stderr.decode(errors="replace")
    if r.returncode != 8 or needle not in err or o.exists():
        fail(f"W7 D-C3 {kind}: rc {r.returncode} (want 8), reason '{needle}' "
             f"{'absent' if needle not in err else 'named'}, object "
             f"{'WRITTEN' if o.exists() else 'absent'} — stderr {err[:200]}")
        return
    ok(f"W7 D-C3 {kind}: refused rc 8 naming '{needle}', NO object written")


def controls(mir_for_link: Path) -> None:
    # D-C1: the NO-DEBUG link executes fine but gdb cannot resolve the source line.
    o = OUTDIR / "M05_nodebug.o"
    r = run([MIR2O, "-f", MIR_PIN, o], timeout=60)
    if r.returncode != 0:
        fail(f"W7 D-C1: default-path mir2o rc {r.returncode} — control not built")
        return
    exe = cosmo_link("optlinux", OUTDIR / "M05_nodebug.exe", o)
    if exe is None:
        return
    r = run([exe], stdin=b"77\n", timeout=60)
    if (r.returncode, r.stdout) != (0, b"77\n"):
        fail("W7 D-C1: the no-debug artifact no longer EXECUTES 77 — the control "
             "would fail for the wrong reason")
        return
    ok("W7 D-C1 preflight: the no-debug link EXECUTES 77 (the break failure below "
       "is about debug info, not about the binary)")
    r = run(["gdb", "-batch", "-nx", "-ex", "set debuginfod enabled off",
             "-ex", "break M05.pli:4", "-ex", "continue", exe],
            stdin=b"77\n", timeout=120)
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("gdb_nodebug_control.log", txt.encode() + f"=== gdb rc {r.returncode} ===\n".encode())
    if "No source file named M05.pli" not in txt or "Breakpoint 1 at" in txt or r.returncode == 0:
        fail(f"W7 D-C1: the no-debug break did NOT fail loudly (gdb rc "
             f"{r.returncode}); output: {txt[:200]}")
        return
    ok("W7 D-C1 FAILED LOUDLY as required: break M05.pli:4 on the no-debug link -> "
       "'No source file named M05.pli', no breakpoint, gdb rc != 0")
    # D-C2: sha tamper -> rc 8
    mp = tamper("sha")
    o2 = OUTDIR / "t_sha.o"
    if o2.exists():
        o2.unlink()
    r = run([MIR2O, "-f", MIR_PIN, o2, "--debug-map", mp], timeout=60)
    err = r.stderr.decode(errors="replace")
    if r.returncode != 8 or "sha MISMATCH" not in err or o2.exists():
        fail(f"W7 D-C2 sha tamper: rc {r.returncode} (want 8) — stderr {err[:200]}")
    else:
        ok("W7 D-C2 FAILED LOUDLY as required: sha-tampered sidecar -> rc 8 "
           "'sha MISMATCH', NO object written")
    # D-C3: count and opcode tampers -> rc 8
    refuse_leg("count", "count MISMATCH")
    refuse_leg("opcode", "opcode MISMATCH")


# ---------- W8 ----------

def glibc_evidence(obj: Path) -> None:
    """Diagnostic reference ONLY (§P1-mD.1 fact 8): never fails the suite."""
    try:
        exe = OUTDIR / "M05_glibc.exe"
        if exe.exists():
            exe.unlink()
        r = run(["gcc", "-O2", "-DENTRY=pli80_iorw", DRIVER, RUNTIME, obj, "-o", exe],
                timeout=120)
        if r.returncode != 0:
            record("glibc_link_failure.txt", r.stderr)
            print("note  W8: glibc diagnostic link failed (EVIDENCE ONLY, not a gate)")
            return
        os.chmod(exe, 0o755)
        rr = run([exe], stdin=b"77\n", timeout=60)
        rg = run(["gdb", "-batch", "-nx", "-ex", "set debuginfod enabled off",
                  "-ex", "break M05.pli:4", "-ex", "run", "-ex", "print n", "-ex", "bt",
                  "-ex", "continue", exe], stdin=b"77\n", timeout=120)
        record("glibc_evidence.txt",
               f"exec rc {rr.returncode} stdout {rr.stdout!r}\n=== gdb ===\n".encode()
               + rg.stdout + rg.stderr)
        print("note  W8: glibc diagnostic-reference evidence recorded (not a gate)")
    except Exception as e:  # noqa: BLE001 — evidence leg, never a delivery gate
        record("glibc_evidence_error.txt", str(e).encode())


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not require_tools():
        return 1
    mp = cli_panel()
    if mp is None:
        fail("debug runner aborted at W1")
        return 1
    obj = debug_object(mp)
    if obj is None:
        fail("debug runner aborted at W2")
        return 1
    readelf_panel(obj)
    exes: dict[str, Path] = {}
    for mode in ("optlinux", "tiny"):
        e = cosmo_link(mode, OUTDIR / f"M05_dbg.{mode}.exe", obj)
        if e is not None:
            exes[mode] = e
    if len(exes) != 2:
        fail("W4: both cosmo link modes (optlinux primary, tiny secondary) are required")
    exec_legs(exes)
    if "optlinux" in exes:
        gdb_panel(exes["optlinux"])
    controls(obj)
    glibc_evidence(obj)
    if FAILURES:
        print(f"\nDEBUG RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nDEBUG RUNNER PASSED: {CHECKS} checks — the -g sidecar pin and the "
          f"MIR pin are UNMOVED; mir2o --debug-map emits the frozen debug object "
          f"{DEBUG_O_SHA[:16]}... with a named .debug_frame and NO .eh_frame; the "
          f"optlinux and tiny links EXECUTE 77 byte-exactly; the full gdb battery "
          f"(break/run/print/stepi/info/bt/continue) is GREEN at M05.pli:4; all "
          f"controls D-C1/D-C2/D-C3 failed loudly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
