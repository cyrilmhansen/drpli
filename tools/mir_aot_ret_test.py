#!/usr/bin/env python3
"""E2E-54/P1-m4 early-RETURN runner (PLAN §P1-m4.7; the mir_aot_cf_test idiom).

One conditional early RETURN(expr) with the terminating-arm join EXCLUSION,
judged on the native MIR path (PL/I -> HIR -> MIR text -> mir2o -> object ->
native link -> EXECUTED bytes).  Every expected value below is COPIED FROM THE
PRE-REGISTRATION (§P1-m4.4/§P1-m4.6, hand-derived there from PL/I semantics
BEFORE any run) and is NEVER read back from program output.  Panels — every
command a DIRECT rc, separate fresh processes, nothing batched:

  R0  prerequisites: pli80mir.exe / mir2o present, the console driver/runtime
      and the pinned Cosmopolitan toolchain identified (cosmo_link.sh
      --toolchain, §P1-mC K0 — the CF V0 law).

  R1  pin panel (§P1-m4.12 step 2): ER01/ER02 .mir regenerated in TWO fresh
      processes each: rc 0, byte-equal stdout, ZERO stderr, stdout == the
      reviewed hir/mir-ret-expected/<id>.mir pin, -o file == stdout.  The
      runner NEVER regenerates or overwrites a pin.

  R2  pipeline law (§P1-m4.4): mir2o -f on each pin rc 0 with the MEASURED
      nfuncs sentence `(2 function(s))` (never derived), and `nm` on the
      object lists `T pli80_<entry>` + `t pli80_sel` (the P1-m3 symbol law).

  R3  negative arms (§P1-m4.6): ERN1..ERN8 pinned rc (.rc), pinned stderr
      bytes (.stderr.txt), ZERO stdout, NO -o file, deterministic across two
      fresh processes.  The emitter is NEVER run for negatives.

  R4  native legs (§P1-m4.12-2 H2): per candidate — glibc console leg (gcc +
      console_check.c + pli_console.c, the runner judges the bytes; NO
      -DEXPECTED) EXECUTING the §P1-m4.4 vector, one leg re-run in a fresh
      process for determinism; cosmo TINY static link with the §P1-m2.6
      static-ELF laws (0x7fELF, `file` static x86-64, NO PT_INTERP, NO
      DT_NEEDED, nm laws) executing the SAME bytes.  The fixtures have no
      GET, so the §P1-m4.7 "BAD(2) leg where measured" is INAPPLICABLE here
      (recorded in the summary line, never silently skipped).

  R5  non-vacuity controls (§P1-m4.9) — DISPOSABLE backend mutations built
      under ignored build/e54p1m4/ret-runner/ ONLY (the committed tree is
      never mutated): the source comes from `git archive HEAD`, the mutation
      is a verbatim string replacement asserted EXACTLY ONCE, and the mutant
      is built with its own dune --build-dir.  IF A CONTROL PASSES (the
      mutation goes undetected), THIS RUNNER FAILS.
        C-M4a  join EXCLUSION removed: the terminating arm's env flows into
               the fall-through join (join_env env_then env).  The committed
               backend admits the ERCTL probe (fall env proves 127*127 =
               16129 <= W(15)); the mutant must REFUSE it — the hull
               [127,129] reaching 16641 leaves the window (E19).  A
               measurably WRONG proof, exactly the §P1-m4.9 requirement.
        C-M4b  the E18 loop-body scan deleted (no_return_in body at the
               While site).  ERN1's PINNED refusal must NOT reproduce on the
               mutant.  MEASURED FIRST (Stage C pre-run, RESULTS §P1-m4.SB):
               the mutant still refuses, but with the classifier's §P1-m4.3-4
               message at a different line — the pinned stderr bytes differ,
               so the suite detects the guard loss (recorded deviation from
               the plan's "stop refusing" wording: the classifier is a second
               guard).

Evidence -> ignored build/e54p1m4/ret-runner/.  This is DRPLi backend-engineering
evidence, never a DR claim (ZERO oracle in this slice).

Prerequisites (separate commands, §P1-m4.7):
    (cd ocaml && eval "$(opam env)" && dune build)
    sh tools/mir_aot/build_native.sh
Run (REPO ROOT):
    eval "$(opam env)" && python3 tools/mir_aot_ret_test.py
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
FIXDIR = REPO / "hir" / "mir-ret-fixtures"
EXPDIR = REPO / "hir" / "mir-ret-expected"
DRIVER = REPO / "tools" / "mir_aot" / "console_check.c"
RUNTIME = REPO / "tools" / "mir_aot" / "pli_console.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
OUTDIR = REPO / "build" / "e54p1m4" / "ret-runner"
SRCBACKEND = "hir/mir_backend.ml"          # path inside the git archive

MODE = "tiny"                              # §P1-m2.6: tiny is the PROVEN mode

# fixtures -> --export entry name (case-folded procedure names; measured at
# Stage B, §P1-m4.4 — the entry is the SELF-NAMED outer procedure)
POSITIVES = [("ER01", "earlya"), ("ER02", "earlyb")]
# §P1-m4.6 negatives, same mapping (Stage B, measured)
NEGATIVES = [("ERN1", "erloop"), ("ERN2", "erboth"), ("ERN3", "ertail"),
             ("ERN4", "erdouble"), ("ERN5", "ervoid"), ("ERN6", "ernest"),
             ("ERN7", "erwide"), ("ERN8", "ertailarm")]

# §P1-m4.4 — INDEPENDENT expected results, COPIED FROM THE PRE-REGISTRATION.
# (id, stdin, expected stdout, expected stderr, expected rc, note).  The
# fixtures carry NO stdin leg (constant actuals in the driver); the vectors
# are the hand-derived console outputs.
EXEC = {
    "ER01": (b"", b"4\n9\n4\n", b"driver-return=4\n", 0,
             "sel(2)=4 (2>5 false, fall-through), sel(7)=9 (early RETURN), "
             "sel(5)=4 (boundary: 5>5 FALSE)"),
    "ER02": (b"", b"3\n12\n", b"driver-return=12\n", 0,
             "sel(4)=3 (fall-through), sel(12)=12 (early RETURN of x)"),
}
# determinism re-runs (§P1-m2.10 V4 idiom): one leg per candidate, fresh proc
DETERMINISM = ["ER01", "ER02"]

# §P1-mC.1 pinned toolchain identity (CF V0 law, copied verbatim)
COSMO_SHA = "sha256=85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44"
COSMO_GCC = "x86_64-linux-cosmo-gcc (GCC) 14.1.0"

# C-M4a mutation: join EXCLUSION -> env flow through the join.
M4A_OLD = """                            ignore (lower_stmts env then_);
                            emit ~line "Ljoin%s:" sfx;
                            lower_stmts env rest"""
M4A_NEW = """                            let env_t = lower_stmts env then_ in
                            emit ~line "Ljoin%s:" sfx;
                            lower_stmts (join_env env_t env) rest"""
# C-M4b mutation: the E18 loop-body scan deleted from the While site.
M4B_OLD = "                      no_return_in body;\n"
M4B_NEW = ""

# The C-M4a probe (disposable fixture written by the runner under OUTDIR; the
# two-statement THEN arm rides the `then do; ... end;` idiom attested by the
# committed ERN4 fixture).  Committed backend: the fall env keeps y=[127,127]
# so 127*127 = 16129 <= W(15) = [-16383,16383] is PROVED and the program is
# ADMITTED; the C-M4a mutant hulls in the terminating arm (y=[127,129]) and
# must REFUSE the same proof obligation (129*129 = 16641 leaves the window).
ERCTL = (b"erctl: procedure returns(fixed bin(15));\r\n"
         b"   dcl x fixed bin(15), y fixed bin(15);\r\n"
         b"   x = 7;\r\n   y = 127;\r\n"
         b"   if x > 5 then do;\r\n      y = 129;\r\n      return (y);\r\n"
         b"   end;\r\n"
         b"   return (y * y);\r\nend erctl;\r\n"
         b"\x1a")

ENV = dict(os.environ, LC_ALL="C")
FAILURES: list[str] = []
CHECKS = 0                                 # MEASURED count (§P1-m2.8 law)


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"ok    {msg}")


def run(argv: list, stdin: bytes = b"", timeout: int = 120,
        cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True,
                          timeout=timeout, env=ENV, cwd=str(cwd or REPO))


def record(name: str, data: bytes) -> None:
    (OUTDIR / name).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------- R0 ----------

def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, MIR2O, DRIVER, RUNTIME,
                                                  RECIPE) if not p.exists()]
    if missing:
        fail(f"R0: prerequisites missing: {', '.join(missing)} — run '(cd ocaml && "
             "dune build)' and 'sh tools/mir_aot/build_native.sh'")
        return False
    ok(f"R0: prerequisites present — {PLIMIR.name}, mir2o, {DRIVER.name}, "
       f"{RUNTIME.name}, {RECIPE.name}")
    r = run(["sh", RECIPE, "--toolchain"], timeout=120)
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("TOOLCHAIN.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"R0: cosmo_link.sh --toolchain rc {r.returncode}: {txt[:300]}")
        return False
    if (COSMO_SHA not in txt and "archive=absent" not in txt) or COSMO_GCC not in txt:
        fail("R0: toolchain identity does not match the §P1-mC.1 pin")
        return False
    ok("R0: pinned Cosmopolitan toolchain identity verified (§P1-mC K0 law)")
    return True


# ---------- R1 / R3 ----------

def pin_panel(name: str, export: str) -> bytes | None:
    """§P1-m4.12-2: regenerate the fixture MIR TWICE in FRESH processes; rc 0,
    byte-equal stdout, ZERO stderr, stdout == pin, -o file == stdout."""
    fx = FIXDIR / f"{name}.pli"
    pin = (EXPDIR / f"{name}.mir").read_bytes()
    outs: list[bytes] = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()
        r = run([PLIMIR, "--export", export, "-o", o_file, fx], timeout=60)
        if r.returncode != 0:
            fail(f"R1 {name} run{i}: pli80mir rc {r.returncode}; stderr "
                 f"{r.stderr.decode(errors='replace')[:200]}")
            return None
        if r.stderr != b"":
            fail(f"R1 {name} run{i}: stderr NOT zero ({len(r.stderr)} B)")
            return None
        if not o_file.exists() or o_file.read_bytes() != r.stdout:
            fail(f"R1 {name} run{i}: -o file absent or != stdout bytes")
            return None
        if r.stdout != pin:
            fail(f"R1 {name} run{i}: stdout != reviewed pin "
                 f"hir/mir-ret-expected/{name}.mir")
            return None
        outs.append(r.stdout)
    if outs[0] != outs[1]:
        fail(f"R1 {name}: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"R1 {name}: rc 0 x2 fresh procs, stdout == pin == -o file "
       f"({len(outs[0])} B), ZERO stderr, deterministic")
    return outs[0]


def negative_panel(name: str, export: str) -> None:
    exp_rc = int((EXPDIR / f"{name}.rc").read_text().strip())
    exp_err = (EXPDIR / f"{name}.stderr.txt").read_bytes()
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()
        r = run([PLIMIR, "--export", export, "-o", o_file,
                 FIXDIR / f"{name}.pli"], timeout=60)
        if r.returncode != exp_rc:
            fail(f"R3 {name} run{i}: rc {r.returncode} != pinned {exp_rc}")
            return
        if r.stdout != b"":
            fail(f"R3 {name} run{i}: stdout not ZERO ({len(r.stdout)} B)")
            return
        if r.stderr != exp_err:
            fail(f"R3 {name} run{i}: stderr bytes != pin "
                 f"({r.stderr!r} vs {exp_err!r})")
            return
        if o_file.exists():
            fail(f"R3 {name} run{i}: REFUSAL PRODUCED an -o file — misleading artifact")
            return
    ok(f"R3 {name}: rc {exp_rc}, ZERO stdout, pinned stderr ({len(exp_err)} B), "
       f"x2 fresh procs, NO artifact — "
       f"{exp_err.decode(errors='replace').strip()[:110]}")


def negative_pinned_bytes(name: str, export: str) -> subprocess.CompletedProcess:
    """One fresh-process run of a negative against ANY backend exe (R5 uses it
    to show a pinned refusal is NOT reproduced by a mutated guard)."""
    return run([PLIMIR, "--export", export, "-o", OUTDIR / f"mut.{name}.o",
                FIXDIR / f"{name}.pli"], timeout=60)


# ---------- R2 ----------

def object_of(name: str, mir: bytes) -> Path | None:
    """mir2o accepts the pinned module; the (N function(s)) sentence is READ
    from stderr (§P1-m4.4: nfuncs MEASURED, never derived) and asserted."""
    mir_file = OUTDIR / f"{name}.mir"
    mir_file.write_bytes(mir)
    obj = OUTDIR / f"{name}.o"
    if obj.exists():
        obj.unlink()
    r = run([MIR2O, "-f", mir_file, obj], timeout=120)
    record(f"{name}.mir2o.stderr", r.stderr)
    if r.returncode != 0 or not obj.exists():
        fail(f"R2 {name}: mir2o rc {r.returncode} / object absent; stderr "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    if b"(2 function(s))" not in r.stderr:
        fail(f"R2 {name}: mir2o stderr does not report the measured (2 function(s)) "
             f"law: {r.stderr!r}")
        return None
    record(f"{name}.o.sha256", (sha256(obj) + "\n").encode())
    return obj


def nm_laws(obj: Path, export: str, tag: str) -> bool:
    r = run(["nm", obj], timeout=60)
    record(f"{tag}.nm.txt", r.stdout + r.stderr)
    txt = r.stdout.decode(errors="replace")
    if r.returncode != 0 or not re.search(r"\bT pli80_" + re.escape(export) + r"\b", txt):
        fail(f"R2 {tag}: nm does not list T pli80_{export} on the object")
        return False
    if " t pli80_sel" not in txt:
        fail(f"R2 {tag}: nm does not list t pli80_sel (the callee symbol law)")
        return False
    ok(f"R2 {tag}: mir2o rc 0 with (2 function(s)) measured from stderr; nm lists "
       f"T pli80_{export} + t pli80_sel on the object")
    return True


# ---------- R4 native legs ----------

def glibc_console_link(obj: Path, export: str, exe: Path) -> bool:
    if exe.exists():
        exe.unlink()
    r = run(["gcc", "-O2", f"-DENTRY=pli80_{export}", DRIVER, RUNTIME, obj,
             "-o", exe], timeout=120)
    record(f"{exe.stem}.gcc.log", r.stdout + r.stderr)
    if r.returncode != 0 or not exe.exists():
        fail(f"R4 {exe.stem}: glibc console link rc {r.returncode}: "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return False
    return True


def exec_leg(exe: Path, name: str, tag: str) -> tuple[bool, str]:
    stdin, exp_out, exp_err, exp_rc, note = EXEC[name]
    r = run([exe], stdin=stdin, timeout=60)
    record(f"{tag}.obs.txt", f"rc {r.returncode} stdout {r.stdout!r} stderr "
                             f"{r.stderr!r}\n".encode())
    if r.stdout != exp_out or r.stderr != exp_err or r.returncode != exp_rc:
        return False, (f"observed rc {r.returncode} stdout {r.stdout!r} stderr "
                       f"{r.stderr!r}; §P1-m4.4 expects rc {exp_rc} {exp_out!r} "
                       f"{exp_err!r}")
    return True, f"rc 0, stdout {r.stdout!r}, stderr {r.stderr!r} [{note}]"


def run_legs(objs: dict[str, Path]) -> None:
    for name, export in POSITIVES:
        if name not in objs:
            fail(f"R4 {name}: skipped — no verified object")
            continue
        gexe = OUTDIR / f"{name}.glibc.exe"
        if glibc_console_link(objs[name], export, gexe):
            passed, obs = exec_leg(gexe, name, f"{name}.glibc")
            if not passed:
                fail(f"R4 {name} glibc console leg: {obs}")
            else:
                ok(f"R4 {name} glibc console: EXECUTED — {obs}")
                if name in DETERMINISM:
                    passed2, obs2 = exec_leg(gexe, name, f"{name}.glibc.det")
                    if not passed2 or obs2 != obs:
                        fail(f"R4 {name} glibc determinism: fresh re-run disagrees "
                             f"({obs2})")
                    else:
                        ok(f"R4 {name} glibc determinism: SECOND fresh process "
                           f"reproduced {obs2}")
        texe = OUTDIR / f"{name}.tiny.exe"
        if cosmo_link(objs[name], export, texe):
            if static_elf_panel(texe, export, f"R4 {name} tiny"):
                passed, obs = exec_leg(texe, name, f"{name}.tiny")
                if not passed:
                    fail(f"R4 {name} cosmo tiny leg: {obs} — the tiny lane disagrees "
                         f"with the glibc lane")
                else:
                    ok(f"R4 {name} cosmo tiny: EXECUTED — {obs}")


def cosmo_link(obj: Path, export: str, out: Path) -> bool:
    if out.exists():
        out.unlink()
    r = run(["sh", RECIPE, MODE, out, "--", DRIVER, RUNTIME, obj,
             f"-DENTRY=pli80_{export}"], timeout=180)
    record(f"{out.stem}.link.log", r.stdout + r.stderr)
    if r.returncode != 0 or not out.exists():
        fail(f"R4 {out.name}: cosmo {MODE} link rc {r.returncode}; diagnostics "
             f"{(r.stdout + r.stderr).decode(errors='replace')[-300:]!r}")
        return False
    os.chmod(out, 0o755)                      # the cosmo chmod +x law
    return True


def static_elf_panel(exe: Path, export: str, tag: str) -> bool:
    head = exe.read_bytes()[:4]
    if head != b"\x7fELF":
        fail(f"{tag}: artifact starts {head!r}, not 0x7f 'ELF'")
        return False
    r = run(["file", exe], timeout=60)
    ftxt = r.stdout.decode(errors="replace")
    if not (r.returncode == 0 and "ELF 64-bit" in ftxt and "x86-64" in ftxt
            and "statically linked" in ftxt):
        fail(f"{tag}: `file` not a statically linked x86-64 ELF: {ftxt!r}")
        return False
    r = run(["readelf", "-lW", exe], timeout=60)
    if r.returncode != 0 or b"INTERP" in r.stdout:
        fail(f"{tag}: readelf -lW rc {r.returncode} or PT_INTERP present — NOT static")
        return False
    r = run(["readelf", "-d", exe], timeout=60)
    d_txt = r.stdout.decode(errors="replace")
    if "NEEDED" in d_txt or "dynamic section" not in d_txt:
        fail(f"{tag}: dynamic section / DT_NEEDED present: {d_txt[:200]!r}")
        return False
    r = run(["nm", exe], timeout=60)
    nm_txt = r.stdout.decode(errors="replace")
    if not re.search(r"\bT pli80_" + re.escape(export) + r"\b", nm_txt):
        fail(f"{tag}: nm does not list T pli80_{export}")
        return False
    undef = [l.strip() for l in nm_txt.splitlines()
             if re.match(r"^ +U (pli_console_|exit)", l)]
    if undef:
        fail(f"{tag}: UNRESOLVED console/exit symbols remain: {undef}")
        return False
    ok(f"{tag}: 0x7fELF, static x86-64, NO PT_INTERP, NO DT_NEEDED, nm T "
       f"pli80_{export}, no undefined pli_console_*/exit")
    return True


# ---------- R5 non-vacuity controls (§P1-m4.9) ----------

def build_mutant(tag: str, old: str, new: str, expect_new: str) -> Path | None:
    """git-archive the COMMITTED ocaml/ tree, apply the mutation to a disposable
    copy (asserting the anchor is EXACTLY ONE), build it in its own _build, and
    return the mutant pli80mir.exe.  Committed sources are NEVER touched."""
    root = OUTDIR / tag
    if root.exists():
        fail(f"R5 {tag}: stale mutant dir — remove {root} before re-running "
             f"(a reused mutant is never evidence)")
        return None
    root.mkdir(parents=True)
    r = run(["sh", "-c", f"git archive HEAD ocaml | tar -x -C {root}"], timeout=180)
    if r.returncode != 0:
        fail(f"R5 {tag}: git archive failed: {r.stderr.decode()[:200]}")
        return None
    f = root / "ocaml" / Path(SRCBACKEND)
    s = f.read_text()
    if s.count(old) != 1:
        fail(f"R5 {tag}: mutation anchor occurs {s.count(old)} times (must be "
             f"EXACTLY 1) — the mutation cannot be applied honestly")
        return None
    m = s.replace(old, new)
    if expect_new not in m:
        fail(f"R5 {tag}: mutated source lacks the expected marker {expect_new!r}")
        return None
    f.write_text(m)
    record(f"{tag}.mutation.txt", (s[:0] + old + "\n--->\n" + new).encode())
    b = run(["dune", "build"], timeout=900, cwd=root / "ocaml")
    record(f"{tag}.build.log", b.stdout + b.stderr)
    if b.returncode != 0:
        fail(f"R5 {tag}: mutant build rc {b.returncode} — control inconclusive")
        return None
    exe = root / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
    if not exe.exists():
        fail(f"R5 {tag}: mutant exe absent after build rc 0")
        return None
    ok(f"R5 {tag}: mutant backend built GREEN from git-archived HEAD "
       f"(disposable, committed tree UNTOUCHED)")
    return exe


def run_mutant(exe: Path, export: str, src: Path, out: Path):
    if out.exists():
        out.unlink()
    return run([exe, "--export", export, "-o", out, src], timeout=60)


def control_c_m4a() -> None:
    """Join exclusion is load-bearing: the committed backend ADMITS the ERCTL
    probe, the env-flow mutant must REFUSE it with the hull reaching 16641."""
    src = OUTDIR / "ERCTL.pli"
    src.write_bytes(ERCTL)
    # committed leg (the control needs the baseline to be an admission)
    c_out = OUTDIR / "C-M4a.committed.o"
    if c_out.exists():
        c_out.unlink()
    r = run([PLIMIR, "--export", "erctl", "-o", c_out, src], timeout=60)
    if r.returncode != 0 or not c_out.exists():
        fail(f"R5 C-M4a: the COMMITTED backend did not admit the ERCTL probe "
             f"(rc {r.returncode}) — the control is inconclusive, investigate")
        return
    ok("R5 C-M4a baseline: committed backend ADMITS ERCTL (exclusion keeps "
       "y=[127,127], 127*127=16129 proven inside W(15))")
    exe = build_mutant("c-m4a", M4A_OLD, M4A_NEW, "join_env env_t env")
    if exe is None:
        return
    m_out = OUTDIR / "C-M4a.mutant.o"
    rr = run_mutant(exe, "erctl", src, m_out)
    record("C-M4a.mutant.stderr", rr.stderr)
    if rr.returncode == 0 and m_out.exists():
        fail("R5 C-M4a: THE MUTATED BACKEND (no join exclusion) ALSO ADMITS ERCTL — "
             "the exclusion is NOT load-bearing and the control is vacuous")
        return
    if b"16641" not in rr.stderr or b"E19" not in rr.stderr:
        fail(f"R5 C-M4a: the mutant refused, but not with the predicted hull "
             f"refusal (127,129 reaching 16641 / E19): {rr.stderr!r}")
        return
    ok("R5 C-M4a: FAILED LOUDLY as designed — dropping the join exclusion leaks "
       "the terminating arm's y=[129,129] into the fall env, the hull [127,129] "
       "reaches 16641 and E19 REFUSES a program the committed backend proves and "
       "admits (a measurably WRONG proof inside the suite)")


def control_c_m4b() -> None:
    """The E18 loop-body scan still guards: ERN1's PINNED refusal must not
    reproduce once the scan is deleted."""
    exe = build_mutant("c-m4b", M4B_OLD, M4B_NEW, "let nested = ref None")
    if exe is None:
        return
    m_out = OUTDIR / "C-M4b.ern1.o"
    rr = run_mutant(exe, "erloop", FIXDIR / "ERN1.pli", m_out)
    record("C-M4b.ern1.stderr", rr.stderr)
    pin_err = (EXPDIR / "ERN1.stderr.txt").read_bytes()
    if rr.returncode == 2 and rr.stderr == pin_err and not m_out.exists():
        fail("R5 C-M4b: THE MUTANT STILL REFUSES VERBATIM — the pinned negative "
             "does NOT depend on the deleted scan: the guard deleted is NOT the "
             "guard in force (control vacuous — fix the mutation site)")
        return
    ok(f"R5 C-M4b: FAILED LOUDLY as designed — deleting the loop-body E18 scan "
       f"changes ERN1's behaviour inside the suite (mutant rc {rr.returncode}, "
       f"stderr {rr.stderr.decode(errors='replace').strip()[:110]} != the pinned "
       f"nested-RETURN bytes; recorded deviation: the §P1-m4.3 classifier is a "
       f"SECOND guard, so the mutant refuses with a DIFFERENT message rather than "
       f"admitting — the pin detects the guard loss either way)")


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not require_tools():
        print(f"RET RUNNER FAILED (R0), {CHECKS} checks before the failure")
        return 1
    mirs: dict[str, bytes] = {}
    for name, export in POSITIVES:
        m = pin_panel(name, export)
        if m is not None:
            mirs[name] = m
    objs: dict[str, Path] = {}
    for name, export in POSITIVES:
        if name in mirs:
            o = object_of(name, mirs[name])
            if o is not None and nm_laws(o, export, name):
                objs[name] = o
    for name, export in NEGATIVES:
        negative_panel(name, export)
    if len(objs) == len(POSITIVES):
        run_legs(objs)
    else:
        fail("R4: skipped native legs — not all candidates produced verified objects")
    control_c_m4a()
    control_c_m4b()
    if FAILURES:
        print(f"\nRET RUNNER FAILED: {len(FAILURES)} failures, {CHECKS} checks "
              f"measured")
        for m in FAILURES:
            print(f"  - {m}")
        return 1
    print(f"\nRET RUNNER PASSED: {CHECKS} checks — ER01/ER02 pins regenerated in "
          f"two fresh processes each and byte-equal to the reviewed pins with zero "
          f"stderr; mir2o accepts both (2-function objects, nm T/t laws); the eight "
          f"§P1-m4.6 negatives refuse with pinned bytes and no artifact in two fresh "
          f"processes each; both candidates EXECUTE the hand-derived §P1-m4.4 vectors "
          f"([4,9,4] with the 5>5 FALSE boundary leg; [3,12]) byte-exactly on the "
          f"glibc AND cosmo tiny static lanes with fresh-process determinism; no GET "
          f"in the fixtures so no BAD(2) leg applies (recorded, not skipped); "
          f"C-M4a and C-M4b FAILED LOUDLY inside the suite on disposable "
          f"git-archived mutant backends")
    return 0


if __name__ == "__main__":
    sys.exit(main())
