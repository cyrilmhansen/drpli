#!/usr/bin/env python3
"""E2E-54/P1-mC Cosmopolitan static-link runner (PLAN §P1-mC.5 step 5).

FEASIBILITY slice: the GENUINE MIR objects of §P1-m0 (PL/I -> HIR -> MIR -> mir2o,
all UNCHANGED) are linked with a PINNED official Cosmopolitan toolchain into plain
static Linux x86-64 ELF executables and EXECUTED natively.  The gcc/glibc link of
§P1-m0 is kept as a DIAGNOSTIC REFERENCE; nothing here replaces it.  The driver
tools/mir_aot/native_check.c is reused UNCHANGED — only the link command changes.

Panels (every command a DIRECT rc, separate processes, nothing batched):

  K0  toolchain identity (cosmo_link.sh --toolchain): pinned archive sha256 verified,
      raw compiler version recorded.  build/mir-cosmo/TOOLCHAIN.txt.

  K1  CT4 COSMOPOLITAN-ONLY CONTROL — a trivial C driver (start, local integer
      function, print, exit status) with NO MIR object at all, linked optlinux and
      tiny.  Proves the toolchain works on this host.  A control pass is NEVER
      described as MIR integration.

  K2  positives M01/M02/M03 (exports calc/m02/m03, independent expected 42/45/10,
      PLAN §P1-m0.6 — never re-fit here):
        P1  pli80mir in TWO fresh processes: rc 0, byte-equal stdout, stdout ==
            the frozen hir/mir-expected/M*.mir pin, -o file == stdout.
        P2  UNCHANGED mir2o emits the object, rc 0; its sha256 is recorded BEFORE
            any link (CT2) and — when the §P1-m0 evidence exists — must be
            byte-identical to build/mir-aot/M*.o: the SAME bytes feed the gcc/glibc
            link and the Cosmopolitan link.
        P3  cosmo_link.sh links driver + object into build/mir-cosmo/<n>.<mode>.exe.
        P4  CT3 ELF panel: first bytes 0x7f 'ELF' (not 'MZ' — no APE/launcher),
            `file` says ELF x86-64 statically linked, `readelf -hW` says EXEC on
            x86-64, `readelf -lW` has NO PT_INTERP, `readelf -dW` has NO dynamic
            section / NO DT_NEEDED, `nm` lists `T pli80_<name>`, `objdump -d`
            contains the MIR-originating function.  Evidence to files under
            build/mir-cosmo/.
        P5  TWO fresh executions print exactly "<expected>\\n" with rc 0.
        P6  diagnostic reference: gcc/glibc link of the SAME object still executes
            the same value (the §P1-m0 path stays green and is not demoted silently).
        P7  link determinism (M01): two separate links of the same object produce
            byte-identical executables.

  K3  mode matrix (PLAN §P1-mC.1: -mtinylinux does NOT exist in 4.0.2): M01 linked
      optlinux vs tiny, sizes/formats/sha recorded, both must print 42.

  K4  non-vacuity controls, ON THE COSMOPOLITAN PATH (brief §7):
        C-a  M01 MIR with `mul` -> `add` re-emitted and RE-LINKED WITH COSMOPOLITAN:
             must EXECUTE and report 13, and the test must FAIL.
        C-b  the UNMODIFIED M01 .o with -DEXPECTED=43: must FAIL.
      If a control passes, THIS RUNNER FAILS.

Prerequisites (separate commands, per the work order):
    (cd ocaml && dune build)                 # pli80mir.exe
    sh tools/mir_aot/build_native.sh         # build/p1m0-deps/mir2o
    toolchain pinned in build/p1mc-deps/     # see cosmo_link.sh header
"""

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLIMIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
MIR2O = REPO / "build" / "p1m0-deps" / "mir2o"
FIXDIR = REPO / "hir" / "mir-fixtures"
EXPDIR = REPO / "hir" / "mir-expected"
DRIVER = REPO / "tools" / "mir_aot" / "native_check.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
OUTDIR = REPO / "build" / "mir-cosmo"
GLIBC_EVIDENCE = REPO / "build" / "mir-aot"      # §P1-m0 objects (CT2 cross-check)

# PLAN §P1-m0.6 — independent hand-computed expected results.  NEVER re-fit.
POSITIVES = [("M01", "calc", 42), ("M02", "m02", 45), ("M03", "m03", 10)]
MODE = "optlinux"          # primary mode (Linux-optimized plain static ELF)
ALT_MODE = "tiny"          # secondary mode, recorded for the mode matrix

# CT4 control: a trivial C driver with NO MIR object involved.  Written to the
# ignored evidence directory by this runner; it is not a fixture and pins nothing.
CONTROL_C = """/* cosmo_control.c — P1-mC Cosmopolitan-only control (no MIR object). */
#include <stdio.h>

static long local_fn(void) {
  long a = 6, b = 7;
  return a * b;
}

int main(void) {
  long v = local_fn();
  printf("%ld\\n", v);
  return v == 42 ? 0 : 1;
}
"""

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


def run(argv: list[str], timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], capture_output=True,
                          timeout=timeout, env=ENV)


def record(name: str, data: bytes) -> None:
    safe = name.replace(" ", "_").replace("[", "").replace("]", "")
    (OUTDIR / safe).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cosmo_link(mode: str, out: Path, inputs: list[str]) -> bool:
    r = run(["sh", RECIPE, mode, out, "--", *inputs])
    record(f"{out.stem}.link.{mode}.log", r.stdout + r.stderr)
    if r.returncode != 0 or not out.exists():
        tail = (r.stdout + r.stderr).decode(errors="replace").replace("\r", "\n")
        tail = "\n".join(l for l in tail.splitlines() if "fixme:" not in l)[-400:]
        fail(f"cosmo_link({mode}) rc {r.returncode} / artifact "
             f"{'absent' if not out.exists() else 'present'} for {out.name}; "
             f"diagnostics: {tail!r}")
        return False
    return True


def elf_panel(exe: Path, export: str, tag: str, mir_symbol: bool = True) -> bool:
    """CT3: plain static Linux x86-64 ELF; with `mir_symbol`, MIR-originating code
    (the exported `pli80_<name>` function) must be present too.  The CT4 control
    drives mir_symbol=False — it has no MIR object and must never be labelled
    MIR integration."""
    head = exe.read_bytes()[:4]
    if head != b"\x7fELF":
        fail(f"{tag}: executable starts with {head!r}, not 0x7f 'ELF' — "
             f"an APE/launcher artifact is NOT a verified static ELF")
        return False
    r = run(["file", exe])
    record(f"{tag}.file.txt", r.stdout + r.stderr)
    txt = r.stdout.decode(errors="replace")
    if not (r.returncode == 0 and "ELF 64-bit" in txt and "x86-64" in txt
            and "statically linked" in txt):
        fail(f"{tag}: `file` does not report a statically linked x86-64 ELF: {txt!r}")
        return False
    r = run(["readelf", "-hW", exe])
    record(f"{tag}.readelf_h.txt", r.stdout + r.stderr)
    h = r.stdout.decode(errors="replace")
    ty = re.search(r"^\s*Type:\s+(.*)$", h, re.M)
    mach = re.search(r"^\s*Machine:\s+(.*)$", h, re.M)
    if r.returncode != 0 or not ty or "EXEC" not in ty.group(1) \
            or not mach or "X86-64" not in mach.group(1):
        fail(f"{tag}: readelf -h is not an x86-64 EXEC "
             f"({ty.group(1) if ty else 'no Type line'} / "
             f"{mach.group(1) if mach else 'no Machine line'})")
        return False
    r = run(["readelf", "-lW", exe])
    record(f"{tag}.readelf_l.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"{tag}: readelf -lW rc {r.returncode}")
        return False
    if b"INTERP" in r.stdout:
        fail(f"{tag}: PT_INTERP present — this is NOT a static executable")
        return False
    r = run(["readelf", "-dW", exe])
    record(f"{tag}.readelf_d.txt", r.stdout + r.stderr)
    if b"NEEDED" in r.stdout or b"dynamic section" not in r.stdout:
        fail(f"{tag}: readelf -dW shows a dynamic section / DT_NEEDED: "
             f"{r.stdout.decode(errors='replace')[:160]!r}")
        return False
    if not mir_symbol:
        ok(f"{tag}: CT3 ELF panel — 0x7fELF, `file` static x86-64, readelf -h "
           f"EXEC x86-64, NO PT_INTERP, no dynamic section/DT_NEEDED "
           f"(evidence in build/mir-cosmo/)")
        return True
    r = run(["nm", exe])
    record(f"{tag}.nm.txt", r.stdout + r.stderr)
    if not re.search(r"\bT pli80_" + re.escape(export) + r"\b",
                     r.stdout.decode(errors="replace")):
        fail(f"{tag}: nm does not list T pli80_{export}")
        return False
    r = run(["objdump", "-d", exe])
    record(f"{tag}.objdump_d.txt", r.stdout)
    if f"<pli80_{export}>:".encode() not in r.stdout:
        fail(f"{tag}: objdump -d does not contain the MIR-originating function "
             f"pli80_{export}")
        return False
    ok(f"{tag}: CT3 ELF panel — 0x7fELF, `file` static x86-64, readelf -h EXEC "
       f"x86-64, NO PT_INTERP, no dynamic section/DT_NEEDED, nm T pli80_{export}, "
       f"objdump shows pli80_{export} (evidence in build/mir-cosmo/)")
    return True


def toolchain_panel() -> bool:
    """K0: the pinned toolchain is present, verified and identified."""
    if not RECIPE.exists():
        fail(f"missing recipe {RECIPE}")
        return False
    r = run(["sh", RECIPE, "--toolchain"])
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("TOOLCHAIN.txt", (r.stdout + r.stderr))
    if r.returncode != 0:
        fail(f"cosmo_link.sh --toolchain rc {r.returncode}: {txt[:300]}")
        return False
    if "sha256=85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44" not in txt \
            and "archive=absent" not in txt:
        fail("toolchain archive hash does not match the §P1-mC.1 pin")
        return False
    if "x86_64-linux-cosmo-gcc (GCC) 14.1.0" not in txt:
        fail(f"raw compiler identity not recorded: {txt[:200]!r}")
        return False
    ident = [l for l in txt.splitlines() if l.startswith(("cosmo_root=", "archive=",
               "raw_compiler=", "loader=", "x86_64-linux-cosmo-gcc"))]
    ok("K0: toolchain identity + pinned archive verified — " + "; ".join(ident)[:220])
    return True


def control_panels() -> None:
    """K1 (CT4): Cosmopolitan-only control, recorded SEPARATELY from MIR work."""
    src = OUTDIR / "cosmo_control.c"
    src.write_text(CONTROL_C)
    for mode in (MODE, ALT_MODE):
        exe = OUTDIR / f"control.{mode}.exe"
        if not cosmo_link(mode, exe, [src]):
            continue
        if not elf_panel(exe, "", f"K1 control {mode}", mir_symbol=False):
            continue
        vals = []
        for i in (1, 2):
            r = run([exe])
            vals.append((r.returncode, r.stdout))
        if vals != [(0, b"42\n")] * 2:
            fail(f"K1 control[{mode}]: runs {vals} (expected rc 0 and 42 twice)")
            continue
        ok(f"K1 control[{mode}]: COSMOPOLITAN-ONLY control (NO MIR object) linked "
           f"static, EXECUTED 42 in two fresh procs — toolchain health only, "
           f"NOT evidence of MIR integration (CT4)")


def positive_panel(name: str, export: str, expected: int, mode: str = MODE) -> bytes | None:
    """Full positive panel; returns the reviewed MIR bytes (needed by C-a)."""
    fx = FIXDIR / f"{name}.pli"
    pin = (EXPDIR / f"{name}.mir").read_bytes()
    outs = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        r = run([PLIMIR, "--export", export, "-o", o_file, fx])
        if r.returncode != 0:
            fail(f"{name} P1: pli80mir rc {r.returncode} (expected 0); stderr "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            return None
        if r.stdout != pin or o_file.read_bytes() != r.stdout:
            fail(f"{name} P1: run{i} stdout/-o file != frozen pin "
                 f"hir/mir-expected/{name}.mir")
            return None
        outs.append(r.stdout)
    if outs[0] != outs[1]:
        fail(f"{name} P1: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"{name} P1: MIR regenerated by pli80mir in two fresh procs, byte-equal "
       f"to the frozen pin")

    mir = OUTDIR / f"{name}.mir"
    mir.write_bytes(outs[0])
    obj = OUTDIR / f"{name}.o"
    r = run([MIR2O, "-f", mir, obj])
    if r.returncode != 0 or not obj.exists():
        fail(f"{name} P2: mir2o rc {r.returncode} / object absent (unchanged "
             f"emitter); stderr {r.stderr.decode(errors='replace')[:200]}")
        return None
    obj_sha = sha256(obj)
    record(f"{name}.o.sha256", (obj_sha + "\n").encode())   # CT2: BEFORE linking
    note = "no §P1-m0 object evidence present to compare"
    if (GLIBC_EVIDENCE / f"{name}.o").exists():
        ref = sha256(GLIBC_EVIDENCE / f"{name}.o")
        if ref != obj_sha:
            fail(f"{name} P2: CT2 VIOLATED — object {obj_sha[:16]} != the object "
                 f"the gcc/glibc link used {ref[:16]}")
            return None
        note = f"byte-identical to build/mir-aot/{name}.o (the gcc/glibc link object)"
    ok(f"{name} P2: UNCHANGED mir2o emitted the object; sha256 {obj_sha[:16]} "
       f"recorded BEFORE linking; {note}")

    exe = OUTDIR / f"{name}.{mode}.exe"
    if not cosmo_link(mode, exe, [DRIVER, obj, f"-DENTRY=pli80_{export}",
                                  f"-DEXPECTED={expected}"]):
        return None
    if not elf_panel(exe, export, f"{name} P4[{mode}]"):
        return None
    vals = []
    for i in (1, 2):
        r = run([exe])
        vals.append((r.returncode, r.stdout))
    if vals != [(0, f"{expected}\n".encode())] * 2:
        fail(f"{name} P5[{mode}]: native runs {vals} — expected rc 0 and "
             f"{expected} twice (independent §P1-m0.6 value)")
        return None
    ok(f"{name} P5[{mode}]: COSMOPOLITAN-LINKED genuine MIR object EXECUTED "
       f"{expected} in two fresh processes (independent value, verified by "
       f"execution)")

    glib = OUTDIR / f"{name}.glibc.exe"
    r = run(["gcc", "-O2", f"-DENTRY=pli80_{export}", f"-DEXPECTED={expected}",
             DRIVER, obj, "-o", glib])
    if r.returncode != 0:
        fail(f"{name} P6: diagnostic gcc/glibc link rc {r.returncode}")
        return None
    r = run([glib])
    if r.returncode != 0 or r.stdout != f"{expected}\n".encode():
        fail(f"{name} P6: gcc/glibc reference run rc {r.returncode} stdout {r.stdout!r}")
        return None
    ld = run(["ldd", glib])
    record(f"{name}.glibc.ldd.txt", ld.stdout + ld.stderr)
    ok(f"{name} P6: SAME object through gcc/glibc still executes {expected} — "
       f"§P1-m0 path kept as diagnostic reference")
    return outs[0]


def link_determinism(export: str, expected: int) -> None:
    """P7: the same object linked twice with the pinned toolchain is byte-equal."""
    obj = OUTDIR / "M01.o"
    a = OUTDIR / "M01.link1.exe"
    b = OUTDIR / "M01.link2.exe"
    inputs = [DRIVER, obj, f"-DENTRY=pli80_{export}", f"-DEXPECTED={expected}"]
    if not cosmo_link(MODE, a, inputs) or not cosmo_link(MODE, b, inputs):
        return
    if sha256(a) != sha256(b):
        fail(f"P7: two links of the same object differ ({sha256(a)[:16]} vs "
             f"{sha256(b)[:16]}) — the link is not reproducible")
        return
    ok(f"P7: link determinism — {a.name}/{b.name} byte-identical "
       f"({sha256(a)[:16]})")


def mode_matrix() -> None:
    """K3: OBSERVED behaviour of the two modes 4.0.2 supports (no -mtinylinux)."""
    obj = OUTDIR / "M01.o"
    rows = []
    for mode in (MODE, ALT_MODE):
        exe = OUTDIR / f"matrix_M01.{mode}.exe"
        inputs = [DRIVER, obj, "-DENTRY=pli80_calc", "-DEXPECTED=42"]
        if not cosmo_link(mode, exe, inputs):
            return
        r = run([exe])
        f = run(["file", exe]).stdout.decode(errors="replace").strip()
        rows.append(f"{mode}: rc={r.returncode} out={r.stdout.decode().strip()} "
                    f"size={exe.stat().st_size} sha={sha256(exe)[:16]} :: {f}")
        if r.returncode != 0 or r.stdout != b"42\n":
            fail(f"K3[{mode}]: 42 not executed (rc {r.returncode} {r.stdout!r})")
            return
    record("MODES.txt", ("\n".join(rows) + "\n").encode())
    ok("K3: mode matrix — the genuine MIR object links AND executes 42 under "
       "BOTH modes this release supports (optlinux, tiny); -mtinylinux does not "
       "exist in 4.0.2 (sizes/shas in build/mir-cosmo/MODES.txt)")


def corruption_controls(m01_mir: bytes) -> None:
    """K4 non-vacuity: BOTH controls must FAIL natively on the Cosmopolitan path."""
    needle = b"\tmul t3, t1, t2\n"
    if m01_mir.count(needle) != 1:
        fail("C-a: M01 pin does not contain exactly one 'mul t3, t1, t2' — the "
             "corruption control cannot be applied honestly")
        return
    cmir = OUTDIR / "corrupt_mul2add.mir"
    cmir.write_bytes(m01_mir.replace(needle, b"\tadd t3, t1, t2\n"))
    cobj = OUTDIR / "corrupt_mul2add.o"
    r = run([MIR2O, "-f", cmir, cobj])
    if r.returncode != 0 or not cobj.exists():
        fail(f"C-a: mir2o on the corrupted MIR rc {r.returncode}")
        return
    record("corrupt_mul2add.o.sha256", (sha256(cobj) + "\n").encode())
    cexe = OUTDIR / "corrupt_mul2add.cosmo.exe"
    if not cosmo_link(MODE, cexe, [DRIVER, cobj, "-DENTRY=pli80_calc",
                                   "-DEXPECTED=42"]):
        return
    r = run([cexe])
    if r.returncode == 0 or r.stdout != b"13\n":
        fail(f"C-a: corruption control PASSED — rc {r.returncode} stdout "
             f"{r.stdout!r}; expected native failure reporting 13")
        return
    if not elf_panel(cexe, "calc", "K4 C-a"):
        return
    ok("K4 C-a: mul->add re-linked WITH COSMOPOLITAN executed 13 and FAILED the "
       "check (the pass is an execution result, not a tautology)")

    bexe = OUTDIR / "corrupt_expected43.cosmo.exe"
    if not cosmo_link(MODE, bexe, [DRIVER, OUTDIR / "M01.o", "-DENTRY=pli80_calc",
                                   "-DEXPECTED=43"]):
        return
    r = run([bexe])
    if r.returncode == 0 or r.stdout != b"42\n":
        fail(f"C-b: wrong-expectation control PASSED — rc {r.returncode} stdout "
             f"{r.stdout!r}; expected nonzero for 42 != 43")
        return
    ok("K4 C-b: EXPECTED=43 against the real 42 — Cosmopolitan-linked test FAILED "
       "as designed")


def require_tools() -> bool:
    missing = [str(p) for p in (PLIMIR, MIR2O, DRIVER, RECIPE) if not p.exists()]
    if missing:
        fail(f"prerequisites missing: {', '.join(missing)} — run '(cd ocaml && dune "
             "build)' and 'sh tools/mir_aot/build_native.sh'; the Cosmopolitan "
             "toolchain pin lives in PLAN §P1-mC.1 / cosmo_link.sh")
        return False
    return True


def main() -> int:
    if not require_tools():
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not toolchain_panel():
        return 1
    control_panels()
    m01_mir: bytes | None = None
    for name, export, expected in POSITIVES:
        mir = positive_panel(name, export, expected)
        if mir is not None and name == "M01":
            m01_mir = mir
            link_determinism(export, expected)
    mode_matrix()
    if m01_mir is None:
        fail("corruption controls skipped: the M01 positive panel did not complete")
    else:
        corruption_controls(m01_mir)
    if FAILURES:
        print(f"\nCOSMO RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nCOSMO RUNNER PASSED: {CHECKS} checks — genuine MIR objects M01/M02/M03 "
          f"linked with the pinned Cosmopolitan toolchain into plain static "
          f"Linux x86-64 ELF (no PT_INTERP, no DT_NEEDED) and EXECUTED 42/45/10 in "
          f"two fresh processes each; mode matrix optlinux+tiny; both corruption "
          f"controls fail natively; the gcc/glibc link stays green as diagnostic "
          f"reference")
    return 0


if __name__ == "__main__":
    sys.exit(main())
