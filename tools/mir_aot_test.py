#!/usr/bin/env python3
"""E2E-54/P1-m0 native MIR AOT runner (PLAN §P1-m0.7).

Panels, per the pre-registration — every command a DIRECT rc, separate
processes, nothing batched:

  positives M01/M02/M03 (exports calc/m02/m03, expected 42/45/10) and,
  since E2E-54/P1-m2 §P1-m2.8 item 1, N2 (export n2, expected 2 — the
  pre-registered if-without-else positive: x = 1; the guard x = 1 is TRUE;
  the THEN arm assigns 2; no ELSE ⇒ the returned value is 2, hand-derived
  in the PLAN before any run):
    P1  pli80mir twice in FRESH processes: rc 0, byte-equal deterministic
        stdout, stdout == the reviewed hir/mir-expected/M*.mir pin, and the
        -o file byte-equal stdout (success writes BOTH, §P1-m0.5).
    P2  mir2o -f M.mir M.o rc 0 — this run IS the MIR-parser acceptance
        check (brief §8).
    P3  native-artifact evidence into build/mir-aot/: readelf -h (must be
        Type REL + Machine Advanced Micro Devices X86-64), readelf -r, nm
        (must list `T pli80_<name>`), objdump -d, ldd of the final program
        (must NOT list libmir/MADC/OCaml — only libc/vdso/loader).
    P4  gcc link with native_check.c -DENTRY=pli80_<name> -DEXPECTED=<v>;
        TWO fresh executions: rc 0 and stdout exactly "<v>\\n".
    P5  pipeline proof: the SAME fixture through pli80hir.exe exits 0
        (the HIR path itself is green — brief §5, no bypass).

  negatives N1, N3..N7 (N2 became a positive at P1-m2; its stale refusal
    pins were deleted per §P1-m2.8): pinned rc (hir/mir-expected/N*.rc), ZERO stdout,
    pinned stderr bytes (N*.stderr.txt), deterministic across two fresh
    processes, and NO -o file (refusal totality — no misleading artifact,
    brief §5).  The emitter is NEVER run for negatives.

  corruption controls (non-vacuity, brief §7 / falsifier T9):
    C-a  M01 MIR with the emitted `mul` replaced by `add`: re-emit,
         re-link against EXPECTED=42 — MUST fail natively, reporting 13.
    C-b  the UNMODIFIED M01 .o with EXPECTED=43 — MUST fail natively.
    If a control "passes", THIS RUNNER FAILS.

The expected results 42/45/10 are the INDEPENDENT hand-computed values of
PLAN §P1-m0.6, recorded there BEFORE any run; they live only in the table
below and the PLAN — never in generated artifacts.  Expected FILES
(hir/mir-expected/) are measured-first pins (PLAN §P1-m0.9 step 4) and
this runner NEVER regenerates or overwrites them.

Prerequisites (separate commands, per the work order):
    (cd ocaml && dune build)                  # pli80mir.exe, pli80hir.exe
    sh tools/mir_aot/build_native.sh          # build/p1m0-deps/mir2o
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLIMIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
PLIHIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80hir.exe"
MIR2O = REPO / "build" / "p1m0-deps" / "mir2o"
FIXDIR = REPO / "hir" / "mir-fixtures"
EXPDIR = REPO / "hir" / "mir-expected"
DRIVER = REPO / "tools" / "mir_aot" / "native_check.c"
OUTDIR = REPO / "build" / "mir-aot"

# PLAN §P1-m0.6 — independent hand-computed expected results (fixture,
# export/entry name, expected return value).  NEVER re-fit from output.
POSITIVES = [("M01", "calc", 42), ("M02", "m02", 45), ("M03", "m03", 10),
             ("N2", "n2", 2)]  # N2: §P1-m2.8 item 1, independent value 2
# fixture -> proc name (--export); §P1-m0.2/§P1-m0.6 negative table
# (N2 moved to POSITIVES per §P1-m2.8 item 1).
NEGATIVES = [("N1", "n1"), ("N3", "n3"), ("N4", "n4"),
             ("N5", "n5"), ("N6", "n6"), ("N7", "n7")]

ENV = dict(os.environ, LC_ALL="C")  # stable toolchain messages for evidence
FAILURES: list[str] = []
OKS = 0  # §P1-m2.8 item 3: the check count is MEASURED, never a hardcoded formula


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    global OKS
    OKS += 1
    print(f"ok    {msg}")


def run(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], capture_output=True,
                          timeout=120, env=ENV)


def require_tools() -> bool:
    missing = [str(p) for p in (PLIMIR, PLIHIR, MIR2O, DRIVER) if not p.exists()]
    if missing:
        fail(f"prerequisites missing: {', '.join(missing)} — run "
             "'(cd ocaml && dune build)' and 'sh tools/mir_aot/build_native.sh'")
        return False
    return True


def positive_panel(name: str, export: str, expected: int) -> bytes | None:
    """Run the full positive panel; return the reviewed MIR bytes on success
    (needed by corruption control C-a), else None."""
    fx = FIXDIR / f"{name}.pli"
    pin = (EXPDIR / f"{name}.mir").read_bytes()
    outs = []
    rcs = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        r = run([PLIMIR, "--export", export, "-o", o_file, fx])
        rcs.append((r.returncode, r))
        if r.returncode != 0:
            fail(f"{name} run{i}: pli80mir rc {r.returncode} (expected 0); "
                 f"stderr: {r.stderr.decode(errors='replace')[:200]}")
            return None
        if r.stdout != pin:
            fail(f"{name} run{i}: stdout != reviewed pin hir/mir-expected/{name}.mir")
            return None
        if not o_file.exists():
            fail(f"{name} run{i}: -o file absent after rc 0")
            return None
        if o_file.read_bytes() != r.stdout:
            fail(f"{name} run{i}: -o file != stdout bytes")
            return None
        outs.append(r.stdout)
    if outs[0] != outs[1] or rcs[0][1].stderr != rcs[1][1].stderr:
        fail(f"{name}: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"{name} P1: rc 0, deterministic x2 fresh procs, stdout == pin, -o == stdout")

    mir_file = OUTDIR / f"{name}.mir"
    shutil.copyfile(OUTDIR / f"{name}.run1.mir", mir_file)  # the REAL CLI artifact feeds the emitter
    obj = OUTDIR / f"{name}.o"
    r = run([MIR2O, "-f", mir_file, obj])
    if r.returncode != 0 or not obj.exists():
        fail(f"{name} P2: mir2o rc {r.returncode} / object absent — MIR parser "
             f"or emitter failed; stderr: {r.stderr.decode(errors='replace')[:200]}")
        return None
    ok(f"{name} P2: mir2o rc 0 (MIR parser acceptance + object emitted)")

    ev = {}
    for tool, args, key in (
        ("readelf", ["readelf", "-h", obj], "readelf_h"),
        ("readelf", ["readelf", "-r", obj], "readelf_r"),
        ("nm", ["nm", obj], "nm"),
        ("objdump", ["objdump", "-d", obj], "objdump_d"),
    ):
        r = run(args)
        if r.returncode != 0:
            fail(f"{name} P3: {tool} rc {r.returncode}")
            return None
        ev[key] = r
        (OUTDIR / f"{name}.{key}.txt").write_bytes(r.stdout)
    ty = re.search(r"^\s*Type:\s+(.*)$", ev["readelf_h"].stdout.decode(), re.M)
    mach = re.search(r"^\s*Machine:\s+(.*)$", ev["readelf_h"].stdout.decode(), re.M)
    if not ty or "REL" not in ty.group(1):
        fail(f"{name} P3: readelf -h Type is not REL ({ty.group(1) if ty else 'no Type line'})")
        return None
    if not mach or "X86-64" not in mach.group(1):
        fail(f"{name} P3: readelf -h Machine is not X86-64")
        return None
    if not re.search(r"\bT pli80_" + re.escape(export) + r"\b", ev["nm"].stdout.decode()):
        fail(f"{name} P3: nm does not list T pli80_{export}")
        return None
    ok(f"{name} P3: ELF evidence REL/X86-64, nm T pli80_{export}, "
       f"readelf -r/objdump -d captured to build/mir-aot/")

    exe = OUTDIR / f"{name}.exe"
    r = run(["gcc", "-O2", f"-DENTRY=pli80_{export}", f"-DEXPECTED={expected}",
             DRIVER, obj, "-o", exe])
    if r.returncode != 0:
        fail(f"{name} P4: gcc link rc {r.returncode}; stderr: "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    vals = []
    for i in (1, 2):
        r = run([exe])
        if r.returncode != 0 or r.stdout != f"{expected}\n".encode():
            fail(f"{name} P4: native run{i} rc {r.returncode} stdout "
                 f"{r.stdout!r} (expected rc 0 and {expected!r})")
            return None
        vals.append(r.stdout)
    if vals[0] != vals[1]:
        fail(f"{name} P4: native runs disagree (nondeterminism)")
        return None
    ok(f"{name} P4: linked, EXECUTED in two fresh procs -> {expected} (independent "
       f"§P1-m0.6 value, verified by execution)")

    r = run(["ldd", exe])
    ldd_txt = (r.stdout + r.stderr).decode(errors="replace")
    (OUTDIR / f"{name}.ldd.txt").write_text(ldd_txt)
    bad = [lib for lib in ("libmir", "madc", "MADC", "ocaml", "cma", "cmxs")
           if lib.lower() in ldd_txt.lower()]
    if r.returncode != 0 or bad:
        fail(f"{name} P3: ldd lists {bad or 'error'} — runtime must not need MIR/"
             f"MADC/OCaml")
        return None
    for line in ldd_txt.splitlines():
        dep = line.strip().split(" ")[0]
        if dep and not (dep.startswith("linux-vdso") or dep.startswith("libc.so")
                        or dep.startswith("/lib64/ld-linux") or dep.startswith("ld-linux")):
            fail(f"{name} P3: unexpected dynamic dependency: {line.strip()}")
            return None
    ok(f"{name} P3: ldd of final program lists ONLY libc/vdso/loader "
       f"(no MIR/MADC/OCaml runtime dependency)")

    r = run([PLIHIR, fx])
    if r.returncode != 0:
        fail(f"{name} P5: pipeline proof — pli80hir.exe rc {r.returncode} on the "
             f"same fixture")
        return None
    ok(f"{name} P5: same fixture lowers through the existing HIR path rc 0 "
       f"(no bypass)")
    return pin


def negative_panel(name: str, export: str) -> None:
    fx = FIXDIR / f"{name}.pli"
    exp_rc = int((EXPDIR / f"{name}.rc").read_text().strip())
    exp_err = (EXPDIR / f"{name}.stderr.txt").read_bytes()
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        r = run([PLIMIR, "--export", export, "-o", o_file, fx])
        if r.returncode != exp_rc:
            fail(f"{name} run{i}: rc {r.returncode} != pinned {exp_rc}")
            return
        if r.stdout != b"":
            fail(f"{name} run{i}: stdout not ZERO ({len(r.stdout)} B)")
            return
        if r.stderr != exp_err:
            fail(f"{name} run{i}: stderr bytes != pin "
                 f"({r.stderr!r} vs {exp_err!r})")
            return
        if o_file.exists():
            fail(f"{name} run{i}: REFUSAL PRODUCED an -o file — misleading artifact")
            return
    ok(f"{name}: rc {exp_rc}, ZERO stdout, pinned stderr, deterministic x2, "
       f"NO artifact (emitter never reached)")


def corruption_controls(m01_mir: bytes) -> None:
    """T9 non-vacuity: BOTH controls must FAIL natively; if either passes,
    this runner fails."""
    # C-a: change the emitted arithmetic (mul -> add): 6+7 = 13 != 42.
    needle = b"\tmul t3, t1, t2\n"
    if m01_mir.count(needle) != 1:
        fail("C-a: M01 pin does not contain exactly one 'mul t3, t1, t2' — "
             "corruption control cannot be applied honestly")
        return
    corrupted = m01_mir.replace(needle, b"\tadd t3, t1, t2\n")
    cmir = OUTDIR / "corrupt_mul2add.mir"
    cmir.write_bytes(corrupted)
    cobj = OUTDIR / "corrupt_mul2add.o"
    r = run([MIR2O, "-f", cmir, cobj])
    if r.returncode != 0:
        fail(f"C-a: mir2o on corrupted MIR rc {r.returncode} (expected 0)")
        return
    cexe = OUTDIR / "corrupt_mul2add.exe"
    r = run(["gcc", "-O2", "-DENTRY=pli80_calc", "-DEXPECTED=42", DRIVER, cobj, "-o", cexe])
    if r.returncode != 0:
        fail(f"C-a: link of corrupted object rc {r.returncode}")
        return
    r = run([cexe])
    if r.returncode == 0 or r.stdout != b"13\n":
        fail(f"C-a: corruption control PASSED the gate — rc {r.returncode} stdout "
             f"{r.stdout!r}; expected native mismatch (13 != 42)")
        return
    ok("C-a: mul->add — native test FAILED as designed (execution reported 13 != 42; "
       "the pass is an EXECUTION result, not a tautology)")
    # C-b: same unmodified .o, wrong expected value baked into the driver.
    bexe = OUTDIR / "corrupt_expected43.exe"
    r = run(["gcc", "-O2", "-DENTRY=pli80_calc", "-DEXPECTED=43", DRIVER,
             OUTDIR / "M01.o", "-o", bexe])
    if r.returncode != 0:
        fail(f"C-b: link with -DEXPECTED=43 rc {r.returncode}")
        return
    r = run([bexe])
    if r.returncode == 0 or r.stdout != b"42\n":
        fail(f"C-b: wrong-expectation control PASSED the gate — rc {r.returncode} "
             f"stdout {r.stdout!r}; expected nonzero for 42 != 43")
        return
    ok("C-b: EXPECTED=43 against the real 42 — native test FAILED as designed")


def main() -> int:
    if not require_tools():
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    m01_mir: bytes | None = None
    for name, export, expected in POSITIVES:
        mir = positive_panel(name, export, expected)
        if mir is not None and name == "M01":
            m01_mir = mir
    for name, export in NEGATIVES:
        negative_panel(name, export)
    if m01_mir is None:
        fail("corruption controls skipped: M01 positive panel did not complete")
    else:
        corruption_controls(m01_mir)
    if FAILURES:
        print(f"\nMIR AOT RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    if OKS != len(POSITIVES) * 6 + len(NEGATIVES) + 2:
        fail(f"summary: {OKS} ok-lines != expected panel arithmetic "
             f"({len(POSITIVES)}x6 + {len(NEGATIVES)} + 2)")
        return 1
    pos_vals = "/".join(str(e) for _, _, e in POSITIVES)
    print(f"\nMIR AOT RUNNER PASSED: {OKS} checks — positives {pos_vals} EXECUTED "
          f"(independent §P1-m0.6 + §P1-m2.8-1), {len(NEGATIVES)} negatives refuse "
          f"with zero artifacts, both corruption controls fail natively")
    return 0


if __name__ == "__main__":
    sys.exit(main())
