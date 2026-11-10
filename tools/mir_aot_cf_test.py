#!/usr/bin/env python3
"""E2E-54/P1-m2 native control-flow runner (PLAN §P1-m2.10; T10 panel).

Control-flow programs built by the native MIR path (PL/I -> HIR -> MIR text ->
mir2o -> genuine MIR object -> pinned Cosmopolitan static link -> native
execution) are JUDGED BY EXECUTED BYTES.  Written to §P1-m2.5/§P1-m2.9/§P1-m2.10
BEFORE its first execution; the expected bytes below are COPIED FROM THE
PRE-REGISTRATION (§P1-m2.5 tables, hand-computed from PL/I semantics there) and
are NEVER read back from program output.  Panels — every command a DIRECT rc,
separate processes, nothing batched:

  V0  prerequisites: pli80mir.exe / pli80hir.exe built; build/p1m0-deps/mir2o
      present (built from the COMMITTED tools/mir_aot/mir2o.c by `sh
      tools/mir_aot/build_native.sh`, which verifies the laboratory pins); the
      console runtime/driver, the glibc native_check driver and the pinned
      Cosmopolitan toolchain identified (cosmo_link.sh --toolchain, §P1-mC K0).

  V1  pin panel (§P1-m2.6 step 2): CF01..CF10 .mir regenerated in TWO fresh
      processes each: rc 0, byte-equal stdout, stdout == the reviewed
      hir/mir-cf-expected/<id>.mir pin, and the -o file byte-equal stdout.
      The runner NEVER regenerates or overwrites a pin.

  V2  negative arms (§P1-m2.5 negative table): CFN1..CFN6 pinned rc
      (hir/mir-cf-expected/CFN*.rc), pinned stderr bytes, ZERO stdout, NO -o
      file, deterministic across two fresh processes (the §P1-m0 refusal-totality
      law).  The emitter is NEVER run for negatives.

  V3  pipeline proof (§P1-m2.6 step 1): every positive fixture also lowers
      through pli80hir.exe rc 0 — the HIR path itself is green, no bypass.

  V4  native legs (§P1-m2.6 steps 3-5 + §P1-m2.5): per positive — mir2o rc 0
      (this run IS the pinned-MIR-parser acceptance check); cosmo TINY link of
      console_check.c (-DENTRY, NO -DEXPECTED: the runner judges the bytes) +
      pli_console.c + the object; `chmod +x` law; static-ELF laws (artifact
      starts 0x7fELF, `file` statically linked x86-64, NO PT_INTERP, `nm` lists
      T pli80_<name> and NO undefined pli_console_*/exit); then EVERY stdin leg
      EXECUTED in a FRESH process with EXACT stdout bytes, EXACT rc and EXACT
      `driver-return=<v>` stderr on success legs.  CF07/CF08 have no console leg
      (§P1-m2.5) and are additionally verified by the glibc native_check driver
      with EXPECTED = the returned value, twice in fresh processes.
      Determinism: one success leg per milestone re-run in a fresh process.

  V5  non-vacuity controls (§P1-m2.7) — perturbations live ONLY in disposable
      copies under ignored build/mir-cf/; a committed pin is NEVER perturbed and
      the compiler is NEVER touched.  IF A CONTROL PASSES, THIS RUNNER FAILS.
        C-M2a  CF01 MIR with the branch polarity flipped (`blt` -> `bge`): the
               program EXECUTES the wrong arm — stdin `-2\\n` prints `1\\n`
               where the independent expectation is `-1\\n`.
        C-M2b  CF06 MIR with the `jmp Lh1` backedge DELETED: stdout MUST NOT
               equal `0\\n1\\n2\\n` (prediction: exactly one iteration, `0\\n`).

  W   DWARF legs (§P1-m2.9, the existing debug-test idiom, run FROM THE REPO
      ROOT because the sidecar `file` row is the cwd-dependent absolute path):
        W1  CF01 -g sidecar: every emit-order insn counted (27 rows = 24 body +
            the 3 line-0 fail-tail records), row-by-row opcode/line table below
            (reviewed against the fixture's source lines), mir rows == hashlib
            of the pin, `var v0 x` + `var v1 y`; mir2o --debug-map rc 0 x2
            byte-identical; sections: named .debug_frame + .rela.debug_frame and
            NO .eh_frame; optlinux link + gdb BOTH ARMS at CF01.pli:5 (the IF
            line) with x and y printed (next,next discipline: one next stops AT
            the arm's first insn with a stale slot).
        W2  CF06 loop DWARF: decodedline MUST show the loop lines 4 (header AND
            backedge), 5 (body) and 6 (step); gdb break CF06.pli:5 hit THREE
            times with print i = 0, 1, 2 then a clean exit — the backedge on the
            real machine.
        W3  gdb non-vacuity: the SAME break on the NO-debug CF06 object must NOT
            resolve ("No source file named CF06.pli").
        W4  existing debug pins UNMOVED: hir/mir-expected/M05.mir and
            hir/mir-debug-expected/M05.p1md byte-equal to their pins and the M05
            debug object reproduces the frozen §P1-mD.5 sha (falsifier T9).

Evidence -> ignored build/mir-cf/runner/.  Control-flow semantics are DRPLi
engineering evidence, never DR claims (ZERO oracle in this slice).

Prerequisites (separate commands, §P1-m2.13 step 7):
    (cd ocaml && eval "$(opam env)" && dune build)
    sh tools/mir_aot/build_native.sh
Run (REPO ROOT — cwd law for the DWARF legs):
    eval "$(opam env)" && python3 tools/mir_aot_cf_test.py
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
PLIHIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80hir.exe"
MIR2O = REPO / "build" / "p1m0-deps" / "mir2o"
FIXDIR = REPO / "hir" / "mir-cf-fixtures"
EXPDIR = REPO / "hir" / "mir-cf-expected"
HISTFIX = REPO / "hir" / "mir-fixtures"
HISTEXP = REPO / "hir" / "mir-expected"
DBGEXP = REPO / "hir" / "mir-debug-expected"
DRIVER = REPO / "tools" / "mir_aot" / "console_check.c"
RUNTIME = REPO / "tools" / "mir_aot" / "pli_console.c"
NATIVE = REPO / "tools" / "mir_aot" / "native_check.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
OUTDIR = REPO / "build" / "mir-cf" / "runner"

MODE = "tiny"          # §P1-m2.6 step 4: tiny is the PROVEN mode for this shape
DEBUG_MODE = "optlinux"  # §P1-m2.9: the gdb legs run on the optlinux link

# §P1-mD.5 frozen debug object sha (falsifier T9 — NEVER re-fit).
M05_DEBUG_O_SHA = "cb263c2c69c1f31f456f8391fc7694f9418d4c32044e0ad2cc385a0e33984782"

# fixtures -> --export name (PLAN §P1-m2.5; procedure names are case-folded)
POSITIVES = [("CF01", "choose"), ("CF02", "nocls"), ("CF03", "nest"),
             ("CF04", "eqne"), ("CF05", "iocond"), ("CF06", "count"),
             ("CF07", "zero"), ("CF08", "oneit"), ("CF09", "loopcond"),
             ("CF10", "stepdn")]
NEGATIVES = [f"CFN{i}" for i in range(1, 7)]

# PLAN §P1-m2.5 — INDEPENDENT expected results, COPIED FROM THE
# PRE-REGISTRATION.  (fixture, leg, stdin, expected stdout, expected stderr or
# None = not asserted, expected rc, meaning).  Hand-computed there from PL/I
# semantics BEFORE any run; NEVER re-fit from output.
LEGS = [
    ("CF01", "lt", b"-2\n", b"-1\n", b"driver-return=-1\n", 0, "x<0 -> THEN arm y=-1"),
    ("CF01", "zero", b"0\n", b"1\n", b"driver-return=1\n", 0, "0<0 false -> ELSE arm y=1"),
    ("CF01", "gt", b"7\n", b"1\n", b"driver-return=1\n", 0, "7<0 false -> ELSE arm"),
    ("CF02", "taken", b"10\n", b"9\n", b"driver-return=9\n", 0,
     "no-ELSE: 10>5 -> y=9, join hull [7,9]"),
    ("CF02", "skip", b"5\n", b"7\n", b"driver-return=7\n", 0,
     "no-ELSE: guard false -> y keeps 7"),
    ("CF03", "neg", b"-3\n", b"-1\n", b"driver-return=-1\n", 0, "nested IF first arm"),
    ("CF03", "eq", b"0\n", b"0\n", b"driver-return=0\n", 0, "nested IF Eq arm"),
    ("CF03", "else", b"5\n", b"2\n", b"driver-return=2\n", 0, "nested IF final ELSE"),
    ("CF04", "eq", b"3\n", b"9\n", b"driver-return=9\n", 0,
     "Ne false -> y=-1; Ge true -> -1+10=9"),
    ("CF04", "ne", b"4\n", b"11\n", b"driver-return=11\n", 0,
     "Ne true -> y=1; Ge true -> 1+10=11"),
    ("CF04", "lt", b"1\n", b"-9\n", b"driver-return=-9\n", 0,
     "Ne true -> y=1; Ge false -> 1-10=-9"),
    ("CF05", "get-in-else", b"5\n7\n", b"7\n", b"driver-return=7\n", 0,
     "console GET inside the ELSE arm"),
    ("CF05", "then-arm", b"-1\n", b"-2\n", b"driver-return=-2\n", 0,
     "Le guard true -> y=-2, no second get"),
    ("CF05", "bad-in-arm", b"5\nabc\n", b"", None, 2,
     "BAD(2) read inside a branch: exit(2) via Lfail, no output"),
    ("CF05", "bad-first", b"abc\n", b"", None, 2, "BAD(2) at the first get"),
    ("CF06", "run", b"", b"0\n1\n2\n", b"driver-return=3\n", 0,
     "brief §6 verbatim: THREE genuine iterations, exit 0+1*3=3"),
    ("CF07", "run", b"", b"", b"driver-return=5\n", 0,
     "ZERO iterations: guard false at entry, exit = iv0 = 5"),
    ("CF08", "run", b"", b"", b"driver-return=3\n", 0,
     "exactly ONE iteration (Le), exit = 2 + 1*ceil(1/1) = 3"),
    ("CF09", "run", b"", b"9\n2\n", b"driver-return=2\n", 0,
     "IF inside the loop: j printed once, then i=2"),
    ("CF10", "run", b"", b"6\n4\n", b"driver-return=2\n", 0,
     "descending c=-2: exit = 6 - 2*ceil(4/2) = 2"),
]
# §P1-m2.5: CF07/CF08 have NO console expectation — the glibc native_check leg
# (EXPECTED = the returned value) is their value verification, two fresh procs.
GLIBC = {"CF07": 5, "CF08": 3}
# determinism re-runs (§P1-m2.10 V4): one m2a leg and one m2b leg
DETERMINISM_LEGS = [("CF01", "lt"), ("CF06", "run")]

# §P1-m2.9 / §P1-mD.3 — CF01 sidecar insn rows as reviewed line by line against
# the fixture source (1 count, 2 dcl x, 3 dcl y, 4 get list(x), 5 if x<0 then,
# 6 y=-1, 7 else, 8 y=1, 9 put list(y), 10 return(y)): 24 body insns + the 3
# line-0 fail-tail records = 27.  Labels ARE insns and are named `label`.
CF01_ROWS = (
    [("alloca", 4), ("call", 4), ("bne", 4), ("mov", 4)]            # get list(x)
    + [("mov", 5), ("mov", 5), ("blt", 5), ("jmp", 5)]              # guard x < 0
    + [("label", 5)]                                               # Lthen1:
    + [("mov", 6), ("neg", 6), ("mov", 6)]                          # y = -1
    + [("jmp", 5), ("label", 5)]                                    # join branch
    + [("mov", 8), ("mov", 8)]                                      # y = 1 (ELSE)
    + [("label", 5)]                                               # Ljoin1:
    + [("mov", 9), ("call", 9), ("bne", 9), ("call", 9), ("bne", 9)]  # put list(y)
    + [("mov", 10), ("ret", 10)]                                    # return (y)
    + [("label", 0), ("call", 0), ("ret", 0)]                        # Lfail tail
)
CF01_VARS = [("v0", "x"), ("v1", "y")]
# §P1-m2.9 CF06 loop rows: 3 i=0, 4 do while (header/guard/backedge/exit label),
# 5 put list(i), 6 i=i+1, 8 return (i); 22 insns, no ELSE, one var.
CF06_ROWS = (
    [("mov", 3), ("mov", 3)]
    + [("label", 4), ("mov", 4), ("mov", 4), ("bge", 4)]
    + [("mov", 5), ("call", 5), ("bne", 5), ("call", 5), ("bne", 5)]
    + [("mov", 6), ("mov", 6), ("add", 6), ("mov", 6)]
    + [("jmp", 4), ("label", 4)]
    + [("mov", 8), ("ret", 8)]
    + [("label", 0), ("call", 0), ("ret", 0)]
)
CF06_VARS = [("v0", "i")]

ENV = dict(os.environ, LC_ALL="C")   # stable toolchain messages for evidence
FAILURES: list[str] = []
CHECKS = 0                           # MEASURED count (§P1-m2.8 lesson: no formula)


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"ok    {msg}")


def run(argv: list, stdin: bytes = b"", timeout: int = 90) -> subprocess.CompletedProcess:
    # cwd=REPO — the sidecar `file` row and gdb source resolution are cwd-dependent
    return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True,
                          timeout=timeout, env=ENV, cwd=REPO)


def record(name: str, data: bytes) -> None:
    (OUTDIR / name).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tail(text: str) -> str:
    return "\n".join(l for l in text.replace("\r", "\n").splitlines()
                     if "fixme:" not in l)[-400:]


# ---------- V0 ----------

def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, PLIHIR, MIR2O, DRIVER,
                                                  RUNTIME, NATIVE, RECIPE)
               if not p.exists()]
    if missing:
        fail(f"V0: prerequisites missing: {', '.join(missing)} — run '(cd ocaml && "
             "dune build)' and 'sh tools/mir_aot/build_native.sh'")
        return False
    ok(f"V0: prerequisites present — {PLIMIR.name}, {PLIHIR.name}, mir2o, "
       f"{DRIVER.name}, {RUNTIME.name}, {NATIVE.name}, {RECIPE.name}")
    r = run(["sh", RECIPE, "--toolchain"], timeout=120)
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("TOOLCHAIN.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"V0: cosmo_link.sh --toolchain rc {r.returncode}: {txt[:300]}")
        return False
    if ("sha256=85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44"
            not in txt and "archive=absent" not in txt):
        fail("V0: toolchain archive hash does not match the §P1-mC.1 pin")
        return False
    if "x86_64-linux-cosmo-gcc (GCC) 14.1.0" not in txt:
        fail(f"V0: raw compiler identity not recorded: {txt[:200]!r}")
        return False
    ok("V0: pinned Cosmopolitan toolchain identity verified (§P1-mC K0 law)")
    return True


# ---------- V1 / V2 / V3 ----------

def mir_bytes(name: str, export: str) -> bytes | None:
    """§P1-m2.6 step 2: regenerate the fixture MIR TWICE in FRESH processes;
    rc 0, byte-equal stdout, stdout == pin, -o file == stdout."""
    fx = FIXDIR / f"{name}.pli"
    pin = (EXPDIR / f"{name}.mir").read_bytes()
    outs: list[bytes] = []
    errs: list[bytes] = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()          # a stale artifact is never evidence
        r = run([PLIMIR, "--export", export, "-o", o_file, fx], timeout=60)
        if r.returncode != 0:
            fail(f"V1 {name} run{i}: pli80mir rc {r.returncode} (expected 0); stderr "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            return None
        if not o_file.exists():
            fail(f"V1 {name} run{i}: -o file absent after rc 0")
            return None
        if o_file.read_bytes() != r.stdout:
            fail(f"V1 {name} run{i}: -o file != stdout bytes")
            return None
        if r.stdout != pin:
            fail(f"V1 {name} run{i}: stdout != reviewed pin "
                 f"hir/mir-cf-expected/{name}.mir")
            return None
        outs.append(r.stdout)
        errs.append(r.stderr)
    if outs[0] != outs[1] or errs[0] != errs[1]:
        fail(f"V1 {name}: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"V1 {name}: rc 0 x2 fresh procs, stdout == pin == -o file "
       f"({len(outs[0])} B), deterministic")
    return outs[0]


def negative_panel(name: str) -> None:
    export = name.lower()
    fx = FIXDIR / f"{name}.pli"
    exp_rc = int((EXPDIR / f"{name}.rc").read_text().strip())
    exp_err = (EXPDIR / f"{name}.stderr.txt").read_bytes()
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()
        r = run([PLIMIR, "--export", export, "-o", o_file, fx], timeout=60)
        if r.returncode != exp_rc:
            fail(f"V2 {name} run{i}: rc {r.returncode} != pinned {exp_rc}")
            return
        if r.stdout != b"":
            fail(f"V2 {name} run{i}: stdout not ZERO ({len(r.stdout)} B)")
            return
        if r.stderr != exp_err:
            fail(f"V2 {name} run{i}: stderr bytes != pin "
                 f"({r.stderr!r} vs {exp_err!r})")
            return
        if o_file.exists():
            fail(f"V2 {name} run{i}: REFUSAL PRODUCED an -o file — misleading artifact")
            return
    arm = exp_err.decode(errors="replace").strip()
    ok(f"V2 {name}: rc {exp_rc}, ZERO stdout, pinned stderr ({len(exp_err)} B), x2 "
       f"fresh procs, NO artifact — {arm[:110]}")


def pipeline_panel() -> None:
    for name, _export in POSITIVES:
        r = run([PLIHIR, FIXDIR / f"{name}.pli"], timeout=60)
        record(f"{name}.hir.stdout", r.stdout)
        record(f"{name}.hir.stderr", r.stderr)
        if r.returncode != 0:
            fail(f"V3 pipeline proof {name}: pli80hir.exe rc {r.returncode} — the HIR "
                 f"path itself must be green (§P1-m2.6 step 1, no bypass)")
            continue
        ok(f"V3 pipeline proof {name}: same fixture lowers through the existing HIR "
           f"path rc 0")


# ---------- V4 native legs ----------

def object_of(name: str, mir: bytes, tag: str) -> Path | None:
    """§P1-m2.6 step 3: mir2o accepts the MIR TEXT (the pinned-parser acceptance
    check) and emits the object; sha recorded BEFORE any link."""
    mir_file = OUTDIR / f"{name}.mir"
    mir_file.write_bytes(mir)
    obj = OUTDIR / f"{name}.o"
    if obj.exists():
        obj.unlink()
    r = run([MIR2O, "-f", mir_file, obj], timeout=120)
    if r.returncode != 0 or not obj.exists():
        fail(f"{tag} {name}: mir2o rc {r.returncode} / object absent — the pinned MIR "
             f"parser or the object emitter failed; stderr "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    record(f"{name}.o.sha256", (sha256(obj) + "\n").encode())
    return obj


def cosmo_link(mode: str, out: Path, inputs: list) -> bool:
    if out.exists():
        out.unlink()
    r = run(["sh", RECIPE, mode, out, "--", *inputs], timeout=180)
    record(f"{out.stem}.link.log", (r.stdout + r.stderr))
    if r.returncode != 0 or not out.exists():
        fail(f"{mode} link rc {r.returncode} / artifact "
             f"{'absent' if not out.exists() else 'present'} for {out.name}; "
             f"diagnostics: {tail((r.stdout + r.stderr).decode(errors='replace'))!r}")
        return False
    os.chmod(out, 0o755)          # the cosmo chmod +x law
    return True


def static_elf_panel(exe: Path, export: str, tag: str) -> bool:
    """§P1-m2.6 step 4 static-ELF laws."""
    head = exe.read_bytes()[:4]
    if head != b"\x7fELF":
        fail(f"{tag}: artifact starts {head!r}, not 0x7f 'ELF'")
        return False
    r = run(["file", exe], timeout=60)
    ftxt = r.stdout.decode(errors="replace")
    record(f"{tag.replace(' ', '_').replace('/', '_')}.file.txt", r.stdout + r.stderr)
    if not (r.returncode == 0 and "ELF 64-bit" in ftxt and "x86-64" in ftxt
            and "statically linked" in ftxt):
        fail(f"{tag}: `file` does not report a statically linked x86-64 ELF: {ftxt!r}")
        return False
    r = run(["readelf", "-lW", exe], timeout=60)
    record(f"{tag.replace(' ', '_').replace('/', '_')}.readelf_l.txt", r.stdout + r.stderr)
    if r.returncode != 0 or b"INTERP" in r.stdout:
        fail(f"{tag}: readelf -lW rc {r.returncode} or PT_INTERP present — NOT static")
        return False
    r = run(["readelf", "-d", exe], timeout=60)
    d_txt = r.stdout.decode(errors="replace")
    record(f"{tag.replace(' ', '_').replace('/', '_')}.readelf_d.txt",
           r.stdout + r.stderr)
    if "NEEDED" in d_txt or "dynamic section" not in d_txt:
        fail(f"{tag}: a dynamic section / DT_NEEDED is present — not a plain static "
             f"ELF: {d_txt[:200]!r}")
        return False
    r = run(["nm", exe], timeout=60)
    record(f"{tag.replace(' ', '_').replace('/', '_')}.nm.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"{tag}: nm rc {r.returncode}")
        return False
    nm_txt = r.stdout.decode(errors="replace")
    if not re.search(r"\bT pli80_" + re.escape(export) + r"\b", nm_txt):
        fail(f"{tag}: nm does not list T pli80_{export}")
        return False
    undef = [l.strip() for l in nm_txt.splitlines()
             if re.match(r"^ +U (pli_console_|exit)", l)]
    if undef:
        fail(f"{tag}: UNRESOLVED console/exit symbols remain: {undef}")
        return False
    ok(f"V4 {tag}: 0x7fELF, `file` static x86-64, NO PT_INTERP, NO dynamic section, "
       f"nm T pli80_{export}, no undefined pli_console_*/exit")
    return True


def leg_expect(exe: Path, stdin: bytes, exp_out: bytes, exp_err: bytes | None,
               exp_rc: int) -> tuple[bool, str]:
    """Evaluate ONE §P1-m2.5 expectation in a FRESH process."""
    r = run([exe], stdin=stdin, timeout=60)
    record(f"{exe.stem}.obs.txt",
           f"rc {r.returncode} stdin {stdin!r} stdout {r.stdout!r} stderr "
           f"{r.stderr!r}\n".encode())
    if r.stdout != exp_out:
        return False, f"stdout {r.stdout!r} != expected {exp_out!r} (rc {r.returncode})"
    if exp_err is not None and r.stderr != exp_err:
        return False, f"stderr {r.stderr!r} != expected {exp_err!r}"
    if r.returncode != exp_rc:
        return False, f"rc {r.returncode} != expected {exp_rc} (stdout {r.stdout!r})"
    obs = f"rc {r.returncode}, stdout {r.stdout!r}"
    if exp_err is not None:
        obs += f", stderr {r.stderr!r}"
    return True, obs


def run_panel(exes: dict[str, Path]) -> None:
    results: dict[tuple[str, str], str] = {}
    for name, leg, stdin, exp_out, exp_err, exp_rc, note in LEGS:
        tag = f"V4 {name}/{leg}"
        if name not in exes:
            fail(f"{tag}: skipped — no verified executable for {name}")
            continue
        passed, obs = leg_expect(exes[name], stdin, exp_out, exp_err, exp_rc)
        if not passed:
            fail(f"{tag}: {obs} — expected stdout {exp_out!r} (EXACTLY "
                 f"{len(exp_out)} B), rc {exp_rc} ({note})")
            continue
        results[(name, leg)] = obs
        ok(f"V4 {tag}: EXECUTED — {obs} [{note}]")
    # glibc native_check legs (§P1-m2.5: CF07/CF08 have no console expectation)
    for name, expected in GLIBC.items():
        objs = [OUTDIR / f"{name}.o"]
        if not objs[0].exists():
            fail(f"V4 {name} glibc: the verified object is absent")
            continue
        gexe = OUTDIR / f"{name}.glibc.exe"
        if gexe.exists():
            gexe.unlink()
        r = run(["gcc", "-O2", f"-DENTRY=pli80_{dict(POSITIVES)[name]}",
                 f"-DEXPECTED={expected}", NATIVE, objs[0], "-o", gexe], timeout=120)
        if r.returncode != 0:
            fail(f"V4 {name} glibc: native_check link rc {r.returncode}: "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            continue
        vals = []
        for i in (1, 2):
            rr = run([gexe], timeout=60)
            vals.append((rr.returncode, rr.stdout))
        exp_out = f"{expected}\n".encode()
        if vals != [(0, exp_out)] * 2:
            fail(f"V4 {name} glibc: {vals} != [(0, {exp_out!r})] x2 fresh procs "
                 f"(independent §P1-m2.5 value {expected})")
            continue
        ok(f"V4 {name} glibc native_check EXPECTED={expected}: EXECUTED in two fresh "
           f"procs -> {exp_out!r} rc 0")
    # determinism: one m2a and one m2b leg re-run in fresh processes
    for name, leg in DETERMINISM_LEGS:
        if (name, leg) not in results:
            fail(f"V4 determinism {name}/{leg}: the leg did not pass once")
            continue
        row = [l for l in LEGS if l[0] == name and l[1] == leg][0]
        passed2, obs2 = leg_expect(exes[name], row[2], row[3], row[4], row[5])
        if not passed2 or obs2 != results[(name, leg)]:
            fail(f"V4 determinism {name}/{leg}: fresh re-run disagrees ({obs2})")
            continue
        ok(f"V4 determinism {name}/{leg}: a SECOND fresh process reproduced {obs2}")


# ---------- V5 corruption controls (§P1-m2.7) ----------

def control(tag: str, mir: bytes, mutate, name: str, export: str, stdin: bytes,
            exp_out: bytes, exp_err: bytes | None, exp_rc: int,
            wrong_out: bytes, wrong_rc: int, note: str) -> None:
    """Apply `mutate` to a DISPOSABLE copy; the perturbed program must EXECUTE and
    the §P1-m2.5 expectation must FAIL while the observed bytes are the predicted
    WRONG ones (a control that passes, or that does not execute, is a runner
    failure — non-vacuity is never faked)."""
    mutated, err = mutate(mir)
    if mutated is None:
        fail(f"V5 {tag}: cannot apply honestly — {err}")
        return
    cmir = OUTDIR / f"{tag}.mir"
    cmir.write_bytes(mutated)
    cobj = OUTDIR / f"{tag}.o"
    if cobj.exists():
        cobj.unlink()
    r = run([MIR2O, "-f", cmir, cobj], timeout=120)
    if r.returncode != 0 or not cobj.exists():
        fail(f"V5 {tag}: mir2o on the corrupted MIR rc {r.returncode} — the control "
             f"is inconclusive; stderr {r.stderr.decode(errors='replace')[:200]}")
        return
    cexe = OUTDIR / f"{tag}.{MODE}.exe"
    if not cosmo_link(MODE, cexe, [DRIVER, RUNTIME, cobj, f"-DENTRY=pli80_{export}"]):
        fail(f"V5 {tag}: link of the corrupted object failed — control inconclusive")
        return
    passed, obs = leg_expect(cexe, stdin, exp_out, exp_err, exp_rc)
    rr = run([cexe], stdin=stdin, timeout=60)
    record(f"{tag}.obs.txt", f"rc {rr.returncode} stdout {rr.stdout!r} stderr "
                             f"{rr.stderr!r}\n".encode())
    if passed:
        fail(f"V5 {tag}: THE NATIVE TEST PASSED ON A CORRUPTED PROGRAM — the panel is "
             f"vacuous ({obs})")
        return
    if rr.stdout != wrong_out or rr.returncode != wrong_rc:
        fail(f"V5 {tag}: the corrupted program did not EXECUTE the predicted WRONG "
             f"behaviour: stdout {rr.stdout!r} rc {rr.returncode}, prediction "
             f"{wrong_out!r} rc {wrong_rc} — not the designed control")
        return
    ok(f"V5 {tag}: FAILED LOUDLY as designed — the perturbed program EXECUTED "
       f"{rr.stdout!r} rc {rr.returncode} (the predicted WRONG arm/behaviour) and the "
       f"§P1-m2.5 expectation ({exp_out!r}) FAILED: {note}")


def controls(mirs: dict[str, bytes]) -> None:
    # C-M2a: branch polarity flip blt -> bge on CF01; stdin -2 takes the ELSE arm.
    def flip(mir: bytes) -> tuple[bytes | None, str]:
        needle = b"\tblt Lthen1, t1, t2\n"
        if mir.count(needle) != 1:
            return None, "CF01 pin does not contain exactly one 'blt Lthen1, t1, t2'"
        return mir.replace(needle, b"\tbge Lthen1, t1, t2\n"), ""
    control("C-M2a", mirs.get("CF01", b""), flip, "CF01", "choose", b"-2\n",
            b"-1\n", b"driver-return=-1\n", 0, b"1\n", 0,
            "blt->bge flips the guard: x<0 is TRUE but the flipped branch goes to ELSE")

    # C-M2b: delete the loop backedge in CF06; exactly one iteration runs.
    def drop(mir: bytes) -> tuple[bytes | None, str]:
        lines = mir.decode().splitlines(True)
        kept = [l for l in lines if l.strip() != "jmp Lh1"]
        if len(kept) != len(lines) - 1:
            return None, ("CF06 pin does not contain exactly one 'jmp Lh1' backedge "
                          f"(found {len(lines) - len(kept)})")
        return "".join(kept).encode(), ""
    control("C-M2b", mirs.get("CF06", b""), drop, "CF06", "count", b"",
            b"0\n1\n2\n", b"driver-return=3\n", 0, b"0\n", 0,
            "backedge removal ends the loop after ONE iteration (stdout 0\\n != "
            "0\\n1\\n2\\n, exit value 1 != 3)")


# ---------- W: DWARF legs (§P1-m2.9) ----------

def sidecar_leg(tag: str, name: str, export: str, rows, vars_, pin_mir: bytes) -> bool:
    """pli80mir -g -> reviewed sidecar; then mir2o --debug-map x2 (byte-identical).
    Returns the map path status; the object is produced by the caller."""
    out = OUTDIR / f"{name}_g.mir"
    mp = OUTDIR / f"{name}_g.mir.p1md"
    for p in (out, mp):
        if p.exists():
            p.unlink()
    r = run([PLIMIR, "-g", "--export", export, "-o", out, FIXDIR / f"{name}.pli"],
            timeout=60)
    if r.returncode != 0 or not out.exists() or not mp.exists():
        fail(f"W1 {tag}: pli80mir -g rc {r.returncode} mir={out.exists()} "
             f"map={mp.exists()} — stderr {r.stderr.decode(errors='replace')[:200]}")
        return False
    if out.read_bytes() != pin_mir or r.stdout != pin_mir:
        fail(f"W1 {tag}: the -g .mir MOVED the frozen pin bytes (file/stdout != pin)")
        return False
    lines = mp.read_text().splitlines()
    got_rows = [l.split() for l in lines if l.startswith("insn ")]
    want = [(str(i), op, str(ln)) for i, (op, ln) in enumerate(rows)]
    got = [(row[2], row[3], row[4]) for row in got_rows]
    if got != want:
        bad = [(i, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w][:6]
        fail(f"W1 {tag}: sidecar insn rows differ from the reviewed table "
             f"(count {len(got)} vs {len(want)}): {bad}")
        return False
    if mp.read_text().splitlines()[1] != f"mir {hashlib.sha256(pin_mir).hexdigest()}":
        fail(f"W1 {tag}: the `mir` row is not the SHA-256 of the pinned .mir")
        return False
    got_vars = [l.split()[1:] for l in lines if l.startswith("var ")]
    if got_vars != [list(v) for v in vars_]:
        fail(f"W1 {tag}: sidecar var rows {got_vars} != {vars_}")
        return False
    objs = []
    for i in (1, 2):
        o = OUTDIR / f"{name}_dbg{i}.o"
        if o.exists():
            o.unlink()
        r = run([MIR2O, "-f", out, o, "--debug-map", mp], timeout=120)
        if r.returncode != 0 or not o.exists():
            fail(f"W1 {tag}: mir2o --debug-map run{i} rc {r.returncode} — stderr "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            return False
        objs.append(o)
    if objs[0].read_bytes() != objs[1].read_bytes():
        fail(f"W1 {tag}: the two fresh-process debug objects differ")
        return False
    record(f"{name}_dbg.o.sha256", (sha256(objs[0]) + "\n").encode())
    sec = run(["readelf", "-SW", objs[0]], timeout=60).stdout.decode(errors="replace")
    if not re.search(r"\]\s+\.debug_frame\s+PROGBITS", sec):
        fail(f"W1 {tag}: no named .debug_frame PROGBITS section"); return False
    if ".eh_frame" in sec:
        fail(f"W1 {tag}: .eh_frame still present in the debug object"); return False
    if not re.search(r"\]\s+\.rela\.debug_frame\s+RELA", sec):
        fail(f"W1 {tag}: no .rela.debug_frame RELA section"); return False
    ok(f"W1 {tag}: -g sidecar reviewed ({len(want)} insn rows = the {len(rows)}-insn "
       f"emit order with the line-0 fail tail, labels named `label`, every line the "
       f"fixture source line), mir row == hashlib, vars {vars_}; .mir == frozen pin; "
       f"mir2o --debug-map rc 0 x2 byte-identical ({objs[0].stat().st_size} B); named "
       f".debug_frame + .rela.debug_frame and NO .eh_frame")
    return objs[0]


def gdb_cf01(exe: Path) -> None:
    """§P1-m2.9: breakpoint on the IF line, BOTH arms, x and y printed.
    next,next discipline (§P1-m2 hop-5 lesson): ONE next from the branch line stops
    AT the arm's first insn, where the target slot is still stale."""
    arms = [(b"-2\n", "-1", "-2", "THEN arm"), (b"7\n", "1", "7", "ELSE arm")]
    good = True
    for stdin, want_y, want_x, note in arms:
        args = ["gdb", "-batch", "-nx", "-ex", "set pagination off",
                "-ex", "set debuginfod enabled off",
                "-ex", "break CF01.pli:5", "-ex", "run",
                "-ex", "print x", "-ex", "next", "-ex", "next",
                "-ex", "print y", "-ex", "continue"]
        r = run(args + [exe], stdin=stdin, timeout=120)
        txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
        record(f"gdb_cf01_{want_x.strip('-')}.log",
               txt.encode() + f"=== gdb rc {r.returncode} ===\n".encode())
        hits = txt.count("CF01.pli:5")
        for needle, why in ((f"$1 = {want_x}", f"x = {want_x}"),
                            (f"$2 = {want_y}", f"y = {want_y}"),
                            ("exited normally", "clean exit")):
            if needle not in txt:
                fail(f"W1 CF01 gdb {note}: {why} not observed ({needle!r} missing); "
                     f"gdb rc {r.returncode}, break hits {hits}")
                good = False
    if good:
        ok("W1 CF01 gdb: break CF01.pli:5 hit on BOTH arms and the bindings were read "
           "natively (stdin -2 -> x=-2 y=-1; stdin 7 -> x=7 y=1); both runs exited "
           "normally (next,next before print — the hop-5 stale-slot discipline)")


def gdb_cf06(exe: Path) -> None:
    """§P1-m2.9: the loop backedge on the machine — break the body line, three
    continues, i = 0 / 1 / 2."""
    args = ["gdb", "-batch", "-nx", "-ex", "set pagination off",
            "-ex", "set debuginfod enabled off",
            "-ex", "break CF06.pli:5", "-ex", "run",
            "-ex", "print i", "-ex", "continue", "-ex", "print i",
            "-ex", "continue", "-ex", "print i", "-ex", "continue"]
    r = run(args + [exe], timeout=120)
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("gdb_cf06_backedge.log",
           txt.encode() + f"=== gdb rc {r.returncode} ===\n".encode())
    hits = len(re.findall(r"Breakpoint 1, pli80_count \(\) at .*CF06\.pli:5", txt))
    want = ["$1 = 0", "$2 = 1", "$3 = 2", "exited normally", "driver-return=3"]
    missing = [w for w in want if w not in txt]
    if r.returncode != 0 or hits != 3 or missing:
        fail(f"W2 CF06 gdb backedge: gdb rc {r.returncode}, breakpoint hits {hits} "
             f"(want 3), missing {missing}; output head: {txt[:250]!r}")
        return
    ok("W2 CF06 gdb: break CF06.pli:5 hit THREE times with print i = 0, 1, 2 and the "
       "program exited normally — the loop backedge executes on the real machine")


def decodedline_cf06(obj: Path) -> None:
    r = run(["readelf", "--debug-dump=decodedline", obj], timeout=60)
    txt = r.stdout.decode(errors="replace")
    record("CF06.decodedline.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"W2 CF06 decodedline: readelf rc {r.returncode}")
        return
    rows = re.findall(r"CF06\.pli\s+(\d+)\s+0x([0-9a-f]+)", txt)
    lines = [n for n, _ in rows]
    if not rows:
        fail(f"W2 CF06 decodedline: no CF06.pli rows in:\n{txt[:400]}")
        return
    if not ({"4", "5", "6"} <= set(lines)):
        fail(f"W2 CF06 decodedline: the loop lines 4/5/6 are NOT all present: {rows}")
        return
    header4 = [a for n, a in rows if n == "4"]
    if len(header4) < 2:
        fail(f"W2 CF06 decodedline: line 4 must appear BOTH at the guard and at the "
             f"backedge jmp: {rows}")
        return
    ok(f"W2 CF06 decodedline: rows {rows} — the guard AND the backedge map to the DO "
       f"line 4, the console PUT to line 5 and the step to line 6 (§P1-m2.9 loop "
       f"line-table law)")


def dwarf_panel(mirs: dict[str, bytes]) -> None:
    if "CF01" not in mirs or "CF06" not in mirs:
        fail("W1/W2 skipped: the CF01 or CF06 pin panel did not complete")
        return
    # --- W1 CF01 both arms under gdb.
    obj = sidecar_leg("CF01", "CF01", "choose", CF01_ROWS, CF01_VARS, mirs["CF01"])
    if obj is not False and obj is not None:
        exe = OUTDIR / "CF01_dbg.exe"
        if cosmo_link(DEBUG_MODE, exe, [DRIVER, RUNTIME, obj, "-DENTRY=pli80_choose"]):
            r = run([exe], stdin=b"5\n", timeout=60)
            if (r.returncode, r.stdout) != (0, b"1\n"):
                fail(f"W1 CF01 debug exec: the DEBUG object changed the behaviour "
                     f"(rc {r.returncode} stdout {r.stdout!r}, want rc 0 b'1\\n')")
            else:
                ok("W1 CF01 debug exec: the DEBUG optlinux link EXECUTES the ELSE arm "
                   "byte-exactly (stdin 5 -> stdout 1\\n rc 0) — debug info changed no "
                   "behaviour")
                gdb_cf01(exe)
    # --- W2 CF06 loop line table + backedge.
    obj6 = sidecar_leg("CF06", "CF06", "count", CF06_ROWS, CF06_VARS, mirs["CF06"])
    if obj6 is not False and obj6 is not None:
        decodedline_cf06(obj6)
        exe6 = OUTDIR / "CF06_dbg.exe"
        if cosmo_link(DEBUG_MODE, exe6, [DRIVER, RUNTIME, obj6, "-DENTRY=pli80_count"]):
            r = run([exe6], timeout=60)
            if (r.returncode, r.stdout, r.stderr) != (0, b"0\n1\n2\n",
                                                      b"driver-return=3\n"):
                fail(f"W2 CF06 debug exec: rc {r.returncode} stdout {r.stdout!r} "
                     f"stderr {r.stderr!r} — the DEBUG object must execute the "
                     f"§P1-m2.5 bytes exactly")
                return
            ok("W2 CF06 debug exec: the DEBUG optlinux link EXECUTES 0\\n1\\n2\\n "
               "driver-return=3 rc 0 — three real iterations with debug info attached")
            gdb_cf06(exe6)
            # W3: gdb non-vacuity — the same break on the NO-debug object must not
            # resolve.  Preflight first: the no-debug artifact must still EXECUTE.
            o_plain = OUTDIR / "CF06.nodebug.o"
            if o_plain.exists():
                o_plain.unlink()
            r = run([MIR2O, "-f", OUTDIR / "CF06.mir", o_plain], timeout=120)
            exe_p = OUTDIR / "CF06.nodebug.exe"
            if r.returncode != 0 or not o_plain.exists():
                fail(f"W3: mir2o (no --debug-map) rc {r.returncode} — control "
                     f"inconclusive")
            elif not cosmo_link(DEBUG_MODE, exe_p,
                               [DRIVER, RUNTIME, o_plain, "-DENTRY=pli80_count"]):
                fail("W3: no-debug link failed — control inconclusive")
            else:
                rr = run([exe_p], timeout=60)
                if (rr.returncode, rr.stdout) != (0, b"0\n1\n2\n"):
                    fail("W3 preflight: the NO-debug artifact does not execute "
                         f"0\\n1\\n2\\n (rc {rr.returncode} {rr.stdout!r}) — the "
                         f"break failure below would be for the wrong reason")
                    return
                rg = run(["gdb", "-batch", "-nx", "-ex", "set debuginfod enabled off",
                          "-ex", "break CF06.pli:5", "-ex", "continue", exe_p],
                         timeout=120)
                t = rg.stdout.decode(errors="replace") + rg.stderr.decode(errors="replace")
                record("gdb_cf06_nodebug_control.log",
                       t.encode() + f"=== gdb rc {rg.returncode} ===\n".encode())
                if "No source file named CF06.pli" not in t or "Breakpoint 1 at" in t \
                        or rg.returncode == 0:
                    fail(f"W3: the no-debug break did NOT fail loudly (gdb rc "
                         f"{rg.returncode}): {t[:250]!r}")
                    return
                ok("W3 FAILED LOUDLY as required: the same break on the NO-debug link "
                   "resolves to nothing ('No source file named CF06.pli', gdb rc "
                   "nonzero) — the W2 evidence comes from the debug info, not from "
                   "symbols alone")


def historical_pins_panel() -> None:
    """W4 falsifier T9: nothing in P1-m2 moved an existing debug pin."""
    mpin = (HISTEXP / "M05.mir").read_bytes()
    dpin = (DBGEXP / "M05.p1md").read_bytes()
    out = OUTDIR / "M05_hist.mir"
    m = run([PLIMIR, "-g", "--export", "iorw", "-o", out, HISTFIX / "M05.pli"],
            timeout=60)
    if m.returncode != 0 or m.stdout != mpin or out.read_bytes() != mpin:
        fail("W4: M05 -g .mir differs from the frozen hir/mir-expected/M05.mir pin")
        return
    if (out.with_suffix(out.suffix + ".p1md")).read_bytes() != dpin:
        fail("W4: the M05 sidecar differs from the frozen "
             "hir/mir-debug-expected/M05.p1md pin")
        return
    o = OUTDIR / "M05_dbg.o"
    if o.exists():
        o.unlink()
    r = run([MIR2O, "-f", out, o, "--debug-map",
             out.with_suffix(out.suffix + ".p1md")], timeout=120)
    if r.returncode != 0 or sha256(o) != M05_DEBUG_O_SHA:
        got = sha256(o)[:16] if o.exists() else "absent"
        fail(f"W4: the M05 debug object sha {got} != the frozen §P1-mD.5 pin "
             f"{M05_DEBUG_O_SHA[:16]} — the CF work moved a debug byte")
        return
    ok("W4: EXISTING debug pins UNMOVED — M05.mir and M05.p1md byte-equal and the "
       "debug object reproduces the frozen §P1-mD.5 sha "
       f"{M05_DEBUG_O_SHA[:16]}... (T9 falsifier held)")


# ---------- main ----------

def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not require_tools():
        return 1
    # V1 pins + V2 negatives + V3 pipeline.
    mirs: dict[str, bytes] = {}
    for name, export in POSITIVES:
        m = mir_bytes(name, export)
        if m is not None:
            mirs[name] = m
    for name in NEGATIVES:
        negative_panel(name)
    pipeline_panel()
    # V4 native legs.
    exes: dict[str, Path] = {}
    for name, export in POSITIVES:
        if name not in mirs:
            fail(f"V4 {name}: skipped — the pin panel did not complete")
            continue
        obj = object_of(name, mirs[name], "V4")
        if obj is None:
            continue
        ok(f"V4 {name}: mir2o rc 0 — the pinned MIR parser ACCEPTS the control-flow "
           f"form (object {obj.stat().st_size} B, sha recorded before linking)")
        exe = OUTDIR / f"{name}.{MODE}.exe"
        if cosmo_link(MODE, exe, [DRIVER, RUNTIME, obj, f"-DENTRY=pli80_{export}"]):
            if static_elf_panel(exe, export, f"{name}[{MODE}]"):
                exes[name] = exe
    run_panel(exes)
    # V5 controls always run; a missing input fails the control loudly.
    controls(mirs)
    # W DWARF legs (§P1-m2.9), from the repo root.
    dwarf_panel(mirs)
    historical_pins_panel()
    if FAILURES:
        print(f"\nCF RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    legs = len(exes)
    print(f"\nCF RUNNER PASSED: {CHECKS} checks — CF01..CF10 MIR == reviewed pins in "
          f"two fresh processes; CFN1..CFN6 refuse with pinned bytes and no artifact; "
          f"all ten fixtures lower through the HIR path rc 0; {legs} genuine MIR "
          f"objects link (tiny) into plain static x86-64 ELF and EXECUTED every "
          f"§P1-m2.5 leg byte-exactly (CF01 -1/1/1, CF02 9/7, CF03 -1/0/2, CF04 "
          f"9/11/-9, CF05 7/-2/BAD2/BAD2, CF06 0\\n1\\n2\\n ret 3, CF07 5, CF08 3, "
          f"CF09 9\\n2\\n, CF10 6\\n4\\n) including the glibc legs for CF07/CF08; "
          f"C-M2a and C-M2b FAILED LOUDLY natively; the -g sidecars of CF01/CF06 "
          f"match the reviewed row tables, the debug links execute byte-exactly, gdb "
          f"reads both IF arms and the loop backedge (i = 0/1/2), the no-debug break "
          f"refuses, and the existing debug pins are UNMOVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
