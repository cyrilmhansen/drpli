#!/usr/bin/env python3
"""E2E-54/P1-m3 unified native procedure-call runner (PLAN §P1-m3; T10 panel).

Procedure-call programs built by the native MIR path (PL/I -> HIR -> MIR text ->
mir2o -> genuine MIR object -> glibc AND pinned Cosmopolitan static link ->
native execution) are JUDGED BY EXECUTED BYTES.  Written to §P1-m3.6/.7/.8 and
the operator amendments §P1-m3.15 (A1/A2), §P1-m3.16 (B1/B2/B3), §P1-m3.17
(C1/C2/C3) and §P1-m3.18 (D) BEFORE its first execution; every expected byte
below is COPIED FROM THE PRE-REGISTRATION (hand-derived from PL/I semantics
there) and is NEVER read back from program output.  Panels — every command a
DIRECT rc, separate processes, nothing batched:

  U0  prerequisites: pli80mir.exe / pli80hir.exe built; build/p1m0-deps/mir2o
      present (built from the COMMITTED tools/mir_aot/mir2o.c by `sh
      tools/mir_aot/build_native.sh`, which verifies the laboratory pins); the
      console runtime, the glibc native_check driver and the pinned
      Cosmopolitan toolchain identified (cosmo_link.sh --toolchain, §P1-mC K0).

  U1  positive pin panel (§P1-m3.7 steps 1-2): the THIRTEEN positives
      (CALL01..CALL10, CALLN1 per amendment D, CALLN10 per B3) — pipeline
      proof pli80hir rc 0, then pli80mir --export <entry> TWICE in FRESH
      processes: rc 0, ZERO stderr, stdout == the reviewed
      hir/mir-call-expected/<id>.mir pin, and the -o file byte-equal stdout.
      The runner NEVER regenerates or overwrites a pin.  CALL09 REVIEW law
      (§P1-m3.6): the pin shows EXACTLY TWO func items and NO `pli80_dead`.

  U2  negative panel (§P1-m3.7 step 7): the EIGHT surviving negatives
      CALLN2..CALLN9 — pinned rc (hir/mir-call-expected/CALLN*.rc), pinned
      stderr bytes, ZERO stdout, NO -o file, NO map file, deterministic across
      two fresh processes.  LAYER attribution (§P1-m3.6 table + §P1-m3.16):
      HIR layer (CALLN2/N3/N5, E07) refuses inside pli80hir rc 2 with the
      pinned stderr; BACKEND layer (CALLN4/N6/N7/N8/N9) is ADMITTED by the HIR
      (rc 0) and refused only by the MIR backend.  CALLN7 is the CALL01 text
      compiled with `-g --debug-map` (no separate fixture).  The emitter is
      NEVER run for negatives.

  U3  migration guards (§P1-m3.16 B3, §P1-m3.18 D): the retired negative pins
      CALLN1.rc/.stderr.txt and CALLN10.rc/.stderr.txt MUST NOT exist; the
      migrated positive pins CALLN1.mir and CALLN10.mir MUST be consumed by
      U1/U4.  D_elem guard arm: code inspection (§P1-m3.16 — the arm is
      end-to-end unreachable; the earlier-layer witness is recorded, no
      fixture is invented).

  U4  native legs (§P1-m3.7 steps 3-6): per positive — mir2o `-f` rc 0 on the
      PIN bytes (this run is the pinned-parser syntax authority) with the
      reached-function count in stderr; the glibc leg `gcc -O0
      -DENTRY=pli80_<entry> -DEXPECTED=<v> tools/mir_aot/native_check.c
      tools/mir_aot/pli_console.c <obj>` (g17 panel law) EXECUTED TWICE in
      fresh processes (stdout = the program's own PUT bytes + the printed
      value `<v>\n`, rc 0); the cosmo TINY console leg (`sh
      tools/mir_aot/cosmo_link.sh tiny`, WITH `tools/mir_aot/pli_console.c` +
      `tools/mir_aot/console_check.c`, `chmod +x` law) EXECUTED TWICE with
      EXACT stdout, EXACT stderr `driver-return=<v>\n` and rc 0; static laws
      (artifact starts 0x7fELF, `file` statically linked x86-64, no PT_INTERP
      via readelf -lW, and the readelf -d `no dynamic section` message read on
      STDOUT — never inferred from the rc); `nm` shows the entry `T
      pli80_<entry>` and every subsidiary as a LOCAL `t`.

  U5  non-vacuity controls (§P1-m3.8 as amended by B2/C3) — perturbations live
      ONLY in disposable copies under ignored build/mir-call/runner/; a
      committed pin is NEVER perturbed and the compiler is NEVER touched.
      IF A CONTROL PASSES, THIS RUNNER FAILS.
        C-M3a  CALL02 pin with the two func items SWAPPED (callee AFTER the
               caller): mir2o MUST rc 1 naming `undeclared name` (measured at
               g11: `ln 16: undeclared name pli80_side`), NO object — the
               emission-order law is load-bearing.
        C-M3b  CALL06B pin with the SECOND call argument `h0, hv1` -> `h0, h0`
               (B2 inverse mutation): the corrupted program MUST mir2o, link
               and EXECUTE with stdout `7\n7\n` — the alias dies — and the
               correct `2\n7\n` expectation MUST FAIL on it.  A corrupted
               artifact that still prints `2\n7\n` is a vacuous control.
        C-M3c  CALL07 pin with `add t9, t9, 1` inserted immediately BEFORE the
               callee's single `ret t9` (C3): the mutated artifact MUST stay
               VALID (mir2o rc 0 — a control that fails only because the
               parser rejects it does NOT count), link, and EXECUTE the wrong
               value: the glibc driver with the UNCHANGED `-DEXPECTED=3` must
               return rc 1 with `1\n2\n4\n4\n`, and the cosmo leg must print
               `1\n2\n4\n` with `driver-return=4\n`.

Evidence -> ignored build/mir-call/runner/.  Procedure-call semantics are DRPLi
engineering evidence, never DR claims (ZERO oracle in this slice).

Prerequisites (separate commands, §P1-m3.13):
    (cd ocaml && eval "$(opam env)" && dune build)
Run (REPO ROOT):
    eval "$(opam env)" && python3 tools/mir_aot_call_test.py
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
BACKEND = REPO / "ocaml" / "hir" / "mir_backend.ml"
FIXDIR = REPO / "hir" / "mir-call-fixtures"
EXPDIR = REPO / "hir" / "mir-call-expected"
DRIVER = REPO / "tools" / "mir_aot" / "console_check.c"
RUNTIME = REPO / "tools" / "mir_aot" / "pli_console.c"
NATIVE = REPO / "tools" / "mir_aot" / "native_check.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
OUTDIR = REPO / "build" / "mir-call" / "runner"

MODE = "tiny"  # §P1-m3.7 step 5: the tiny mode is the PROVEN link for this shape

# ---------------------------------------------------------------------------
# POSITIVES — entry, EXPECTED, cosmo stdout, reached-function count.
# EVERY byte below is COPIED FROM THE PRE-REGISTRATION (§P1-m3.6 +
# §P1-m3.15 A1/A2 + §P1-m3.16 B1/B3 + §P1-m3.17 C1/C2 + §P1-m3.18 D) and
# hand-derived from PL/I semantics there; NEVER derived from output.
# The glibc stdout is the program's own console bytes + the printed value
# "<v>\n" (native_check.c); the cosmo stderr is exactly "driver-return=<v>\n".
# ---------------------------------------------------------------------------
POSITIVES = [
    # id        entry       EXPECTED  cosmo stdout   nfuncs
    ("CALL01", "main3",     4,        b"5\n4\n",      2),  # §P1-m3.6 (brief bytes)
    ("CALL02", "call02",    2,        b"2\n",         2),  # §P1-m3.6 + A1 (x untouched)
    ("CALL03", "two",       37,       b"",            2),  # §P1-m3.6 (no console)
    ("CALL04", "chain",     91,       b"51\n",        3),  # §P1-m3.15 A2 (deepest put)
    ("CALL05", "retvoid",   9,        b"",            2),  # §P1-m3.6 (void bare ret)
    ("CALL06A", "aliasin",  7,        b"7\n",         2),  # §P1-m3.6 (alias)
    ("CALL06B", "diffal",   7,        b"2\n7\n",      2),  # §P1-m3.6 (differential)
    ("CALL07", "thrice",    3,        b"1\n2\n3\n",   2),  # §P1-m3.17 C1 (whole-RHS)
    ("CALL08", "wret",      41,       b"",            2),  # §P1-m3.17 C2 (whole-Return)
    ("CALL09", "uncalled",  3,        b"",            2),  # §P1-m3.6 (DROP law)
    ("CALL10", "mixmod",    7,        b"7\n7\n",      2),  # §P1-m3.16 B1 (mixed mode)
    ("CALLN1", "pval",      1,        b"",            2),  # §P1-m3.18 D (POSITIVE)
    ("CALLN10", "refm3a",   7,        b"",            2),  # §P1-m3.16 B3 (POSITIVE)
]

# ---------------------------------------------------------------------------
# NEGATIVES — the EIGHT surviving pinned refusals (CALLN2..CALLN9).  Layer
# (§P1-m3.6 table, amended by §P1-m3.15 A3 history, §P1-m3.16): HIR layer
# refuses inside pli80hir (rc 2, pinned stderr); BACKEND layer is admitted by
# the HIR (rc 0) and refused by pli80mir (rc 2, pinned stderr).
# ---------------------------------------------------------------------------
HIR_LAYER = {"CALLN2", "CALLN3", "CALLN5"}          # E07 class
NEGATIVES = [
    ("CALLN2", "disc",    "HIR"),
    ("CALLN3", "nar",     "HIR"),
    ("CALLN4", "cyc",     "BACKEND"),
    ("CALLN5", "vusage",  "HIR"),
    ("CALLN6", "nest2",   "BACKEND"),
    ("CALLN7", "main3",   "BACKEND"),   # the CALL01 text with -g --debug-map
    ("CALLN8", "uninit",  "BACKEND"),
    ("CALLN9", "deep9",   "BACKEND"),
]

ENV = dict(os.environ, LC_ALL="C")   # stable toolchain messages for evidence
FAILURES: list[str] = []
CHECKS = 0                           # MEASURED count (§P1-m3.10 item 6: no formula)


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"ok    {msg}")


def run(argv: list, stdin: bytes = b"", timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], input=stdin, capture_output=True,
                          timeout=timeout, env=ENV, cwd=REPO)


def record(name: str, data: bytes) -> None:
    (OUTDIR / name).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tail(text: str) -> str:
    return "\n".join(l for l in text.replace("\r", "\n").splitlines()
                     if "fixme:" not in l)[-400:]


# ---------- U0 ----------

def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, PLIHIR, MIR2O, DRIVER,
                                                  RUNTIME, NATIVE, RECIPE)
               if not p.exists()]
    if missing:
        fail(f"U0: prerequisites missing: {', '.join(missing)} — run '(cd ocaml && "
             "eval \"$(opam env)\" && dune build)' and 'sh tools/mir_aot/build_native.sh'")
        return False
    ok(f"U0: prerequisites present — {PLIMIR.name}, {PLIHIR.name}, mir2o, "
       f"{DRIVER.name}, {RUNTIME.name}, {NATIVE.name}, {RECIPE.name}")
    r = run(["sh", RECIPE, "--toolchain"], timeout=120)
    txt = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    record("TOOLCHAIN.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"U0: cosmo_link.sh --toolchain rc {r.returncode}: {txt[:300]}")
        return False
    if ("sha256=85b8c37a406d862e656ad4ec14be9f6ce474c1b436b9615e91a55208aced3f44"
            not in txt and "archive=absent" not in txt):
        fail("U0: toolchain archive hash does not match the §P1-mC.1 pin")
        return False
    if "x86_64-linux-cosmo-gcc (GCC) 14.1.0" not in txt:
        fail(f"U0: raw compiler identity not recorded: {txt[:200]!r}")
        return False
    ok("U0: pinned Cosmopolitan toolchain identity verified (§P1-mC K0 law)")
    return True


# ---------- U1 positive pin panel ----------

def positive_panel(name: str, export: str) -> bytes | None:
    """§P1-m3.7 steps 1-2: pli80hir rc 0 pipeline proof, then pli80mir TWICE in
    fresh processes — rc 0, ZERO stderr, stdout == pin, -o file == pin."""
    fx = FIXDIR / f"{name}.pli"
    pin_path = EXPDIR / f"{name}.mir"
    if not pin_path.exists():
        fail(f"U1 {name}: positive pin hir/mir-call-expected/{name}.mir ABSENT")
        return None
    pin = pin_path.read_bytes()
    r = run([PLIHIR, fx])
    record(f"{name}.hir.stdout", r.stdout)
    record(f"{name}.hir.stderr", r.stderr)
    if r.returncode != 0:
        fail(f"U1 {name}: pipeline proof pli80hir rc {r.returncode} — the HIR path "
             f"itself must be green (§P1-m3.7 step 1, no bypass); stderr "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    outs: list[bytes] = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()          # a stale artifact is never evidence
        m = run([PLIMIR, "--export", export, "-o", o_file, fx])
        if m.returncode != 0:
            fail(f"U1 {name} run{i}: pli80mir rc {m.returncode} (expected 0); stderr "
                 f"{m.stderr.decode(errors='replace')[:200]}")
            return None
        if m.stderr != b"":
            fail(f"U1 {name} run{i}: rc 0 but stderr NOT zero: {m.stderr[:120]!r}")
            return None
        if not o_file.exists():
            fail(f"U1 {name} run{i}: -o file absent after rc 0")
            return None
        if o_file.read_bytes() != m.stdout:
            fail(f"U1 {name} run{i}: -o file != stdout bytes")
            return None
        if m.stdout != pin:
            fail(f"U1 {name} run{i}: stdout != reviewed pin "
                 f"hir/mir-call-expected/{name}.mir")
            return None
        outs.append(m.stdout)
    if outs[0] != outs[1]:
        fail(f"U1 {name}: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"U1 {name}: pipeline proof rc 0; pli80mir --export {export} rc 0 x2 fresh "
       f"procs, ZERO stderr, stdout == pin == -o file ({len(outs[0])} B), "
       f"deterministic")
    return outs[0]


def call09_review_law(mir: bytes) -> None:
    """§P1-m3.6 DROP law: the pin shows EXACTLY TWO func items and NO
    `pli80_dead` (unreached sibling dropped, never emitted)."""
    funcs = re.findall(r"^(pli80_\w+):\tfunc", mir.decode(), re.M)
    if len(funcs) != 2:
        fail(f"U1 CALL09 review law: pin has {len(funcs)} func items {funcs}, "
             f"EXACTLY 2 required")
        return
    if b"pli80_dead" in mir:
        fail("U1 CALL09 review law: `pli80_dead` PRESENT in the pin — the DROP "
             "law is broken (falsifier, §P1-m3.6)")
        return
    ok(f"U1 CALL09 review law: EXACTLY 2 func items {funcs} and `pli80_dead` "
       f"absent (unreached sibling dropped)")


# ---------- U2 negative panel ----------

def negative_panel(name: str, export: str, layer: str) -> None:
    """§P1-m3.7 step 7: pinned rc + stderr bytes, ZERO stdout, NO -o file, NO
    map, x2 fresh processes; LAYER proven by the pli80hir run."""
    fx = FIXDIR / ("CALL01.pli" if name == "CALLN7" else f"{name}.pli")
    exp_rc = int((EXPDIR / f"{name}.rc").read_text().strip())
    exp_err = (EXPDIR / f"{name}.stderr.txt").read_bytes()
    # layer proof: the HIR refuses HIR-layer negatives itself, and ADMIITS the
    # backend-layer ones (the §P1-m3.6 refusal-layer table).
    h = run([PLIHIR, fx])
    if layer == "HIR":
        if h.returncode != exp_rc or h.stderr != exp_err or h.stdout != b"":
            fail(f"U2 {name} layer: HIR-E07-class negative must refuse inside "
                 f"pli80hir (rc {exp_rc}, pinned stderr, ZERO stdout); got rc "
                 f"{h.returncode}, stderr==pin {h.stderr == exp_err}")
            return
    else:
        if h.returncode != 0:
            fail(f"U2 {name} layer: BACKEND-class negative must be ADMITTED by "
                 f"pli80hir (rc 0); got rc {h.returncode} — stderr "
                 f"{h.stderr.decode(errors='replace')[:200]}")
            return
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()
        args = [PLIMIR, "--export", export]
        map_file = None
        if name == "CALLN7":
            map_file = OUTDIR / f"{name}.run{i}.p1md"
            if map_file.exists():
                map_file.unlink()
            args += ["-g", "--debug-map", map_file]
        args += ["-o", o_file, fx]
        r = run(args)
        if r.returncode != exp_rc:
            fail(f"U2 {name} run{i}: rc {r.returncode} != pinned {exp_rc}")
            return
        if r.stdout != b"":
            fail(f"U2 {name} run{i}: stdout not ZERO ({len(r.stdout)} B)")
            return
        if r.stderr != exp_err:
            fail(f"U2 {name} run{i}: stderr bytes != pin "
                 f"({r.stderr!r} vs {exp_err!r})")
            return
        if o_file.exists():
            fail(f"U2 {name} run{i}: REFUSAL PRODUCED an -o file — misleading "
                 f"artifact")
            return
        if map_file is not None and map_file.exists():
            fail(f"U2 {name} run{i}: REFUSAL PRODUCED a debug map — misleading "
                 f"artifact")
            return
    ok(f"U2 {name} [{layer}]: rc {exp_rc}, ZERO stdout, pinned stderr "
       f"({len(exp_err)} B), x2 fresh procs, NO artifact — "
       f"{exp_err.decode(errors='replace').strip()[:110]}")


# ---------- U3 migration guards ----------

def migration_guard() -> None:
    """§P1-m3.16 B3 + §P1-m3.18 D: the retired negative pairs must NOT exist;
    the migrated positive pins must be consumed (they appear in POSITIVES)."""
    for name in ("CALLN1", "CALLN10"):
        for suf in (".rc", ".stderr.txt"):
            p = EXPDIR / f"{name}{suf}"
            if p.exists():
                fail(f"U3 migration guard: retired NEGATIVE pin {name}{suf} is "
                     f"back — the {name} retirement (B3/D) must not be silently "
                     f"reversed")
            else:
                ok(f"U3 migration guard: {name}{suf} absent (retired with "
                   f"provenance, §P1-m3.16 B3 / §P1-m3.18 D)")
        if not (EXPDIR / f"{name}.mir").exists():
            fail(f"U3 migration guard: {name}.mir positive pin ABSENT")
    for name in ("CALLN1", "CALLN10"):
        if name in {p[0] for p in POSITIVES}:
            ok(f"U3 migration guard: {name}.mir is consumed as a POSITIVE pin")
    # D_elem: the guard arm is end-to-end UNREACHABLE (the array-declaration
    # law refuses earlier — §P1-m3.16, recorded class, no fixture); the runner
    # checks the static arm by code inspection only.
    src = BACKEND.read_text()
    if "D_elem" not in src:
        fail("U3 D_elem: the static refusal arm is NOT present in "
             "ocaml/hir/mir_backend.ml — the recorded §P1-m3.16 guard is gone")
    else:
        ok("U3 D_elem: static guard arm present in the backend (code "
           "inspection; the end-to-end unreachable class is recorded, "
           "§P1-m3.16)")


# ---------- U4 native legs ----------

def mir2o_leg(name: str, mir: bytes, nfuncs: int) -> Path | None:
    """§P1-m3.7 step 3: mir2o accepts the PIN bytes (the pinned-parser
    acceptance check — this run is the syntax authority); the reached-function
    count is read from stderr."""
    mir_file = OUTDIR / f"{name}.mir"
    mir_file.write_bytes(mir)          # the pin bytes, verbatim, never rewritten
    obj = OUTDIR / f"{name}.o"
    if obj.exists():
        obj.unlink()
    r = run([MIR2O, "-f", mir_file, obj], timeout=120)
    record(f"{name}.mir2o.stderr", r.stderr)
    if r.returncode != 0 or not obj.exists():
        fail(f"U4 {name}: mir2o rc {r.returncode} / object absent — the pinned "
             f"MIR parser failed; stderr {r.stderr.decode(errors='replace')[:200]}")
        return None
    if f"{nfuncs} function(s)" not in r.stderr.decode(errors="replace"):
        fail(f"U4 {name}: mir2o stderr does not report {nfuncs} function(s): "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    record(f"{name}.o.sha256", (sha256(obj) + "\n").encode())
    ok(f"U4 {name}: mir2o rc 0 on the pin bytes — {nfuncs} function(s), object "
       f"{obj.stat().st_size} B (sha recorded)")
    return obj


def glibc_leg(name: str, entry: str, expected: int, obj: Path,
              exp_stdout: bytes) -> None:
    """§P1-m3.7 step 4 (g17 panel law: -O0, native_check.c + pli_console.c):
    link once, EXECUTE twice in fresh processes."""
    exe = OUTDIR / f"{name}.glibc.exe"
    if exe.exists():
        exe.unlink()
    r = run(["gcc", "-O0", f"-DENTRY=pli80_{entry}", f"-DEXPECTED={expected}",
             NATIVE, RUNTIME, obj, "-o", exe], timeout=120)
    if r.returncode != 0 or not exe.exists():
        fail(f"U4 {name} glibc: native_check link rc {r.returncode}: "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return
    vals = []
    for i in (1, 2):
        rr = run([exe])
        vals.append((rr.returncode, rr.stdout, rr.stderr))
    record(f"{name}.glibc.obs.txt",
           repr(vals).encode() + b"\n")
    if vals != [(0, exp_stdout, b"")] * 2:
        fail(f"U4 {name} glibc: {vals} != [(0, {exp_stdout!r}, b'')] x2 fresh "
             f"procs (independent EXPECTED {expected})")
        return
    ok(f"U4 {name} glibc: native_check -DEXPECTED={expected} EXECUTED x2 fresh "
       f"procs -> {exp_stdout!r} rc 0, zero stderr")


def cosmo_leg(name: str, entry: str, expected: int, obj: Path,
              exp_stdout: bytes) -> None:
    """§P1-m3.7 step 5: cosmo TINY console link (console_check.c +
    pli_console.c), chmod +x law, EXECUTE twice in fresh processes."""
    exe = OUTDIR / f"{name}.tiny.exe"
    if exe.exists():
        exe.unlink()
    r = run(["sh", RECIPE, MODE, exe, "--", obj, RUNTIME, DRIVER,
             f"-DENTRY=pli80_{entry}"], timeout=120)
    record(f"{name}.cosmo.link.log", r.stdout + r.stderr)
    if r.returncode != 0 or not exe.exists():
        fail(f"U4 {name} cosmo: {MODE} link rc {r.returncode} / artifact "
             f"{'absent' if not exe.exists() else 'present'}; diagnostics: "
             f"{tail((r.stdout + r.stderr).decode(errors='replace'))!r}")
        return
    os.chmod(exe, 0o755)              # the cosmo chmod +x law
    exp_err = f"driver-return={expected}\n".encode()
    runs = []
    for i in (1, 2):
        rr = run([exe])
        runs.append((rr.returncode, rr.stdout, rr.stderr))
    record(f"{name}.cosmo.obs.txt", repr(runs).encode() + b"\n")
    if runs != [(0, exp_stdout, exp_err)] * 2:
        fail(f"U4 {name} cosmo: {runs} != [(0, {exp_stdout!r}, {exp_err!r})] "
             f"x2 fresh procs (independent §P1-m3.6 bytes)")
        return
    ok(f"U4 {name} cosmo: TINY console link EXECUTED x2 fresh procs — stdout "
       f"{exp_stdout!r}, stderr {exp_err!r}, rc 0")


def static_leg(name: str, entry: str, nfuncs: int, exe: Path) -> None:
    """§P1-m3.7 step 6: static laws + nm.  The readelf -d `no dynamic section`
    message is read on STDOUT (hop-13 law — never inferred from the rc)."""
    tag = f"U4 {name}"
    head = exe.read_bytes()[:4]
    if head != b"\x7fELF":
        fail(f"{tag}: artifact starts {head!r}, not 0x7f 'ELF'")
        return
    r = run(["file", exe])
    record(f"{name}.file.txt", r.stdout + r.stderr)
    ftxt = r.stdout.decode(errors="replace")
    if not (r.returncode == 0 and "ELF 64-bit" in ftxt and "x86-64" in ftxt
            and "statically linked" in ftxt):
        fail(f"{tag}: `file` does not report a statically linked x86-64 ELF: "
             f"{ftxt!r}")
        return
    r = run(["readelf", "-lW", exe])
    record(f"{name}.readelf_l.txt", r.stdout + r.stderr)
    if r.returncode != 0 or b"INTERP" in r.stdout:
        fail(f"{tag}: readelf -lW rc {r.returncode} or PT_INTERP present — NOT "
             f"static")
        return
    r = run(["readelf", "-d", exe])
    record(f"{name}.readelf_d.txt", r.stdout + r.stderr)
    d_txt = r.stdout.decode(errors="replace")
    if "NEEDED" in d_txt or "no dynamic section" not in d_txt.lower():
        fail(f"{tag}: readelf -d STDOUT does not show the 'no dynamic section' "
             f"law (rc {r.returncode} — never inferred from the rc): "
             f"{d_txt[:160]!r}")
        return
    r = run(["nm", exe])
    record(f"{name}.nm.txt", r.stdout + r.stderr)
    if r.returncode != 0:
        fail(f"{tag}: nm rc {r.returncode}")
        return
    nm_txt = r.stdout.decode(errors="replace")
    if not re.search(r"\bT pli80_" + re.escape(entry) + r"\b", nm_txt):
        fail(f"{tag}: nm does not list T pli80_{entry}")
        return
    subs = [l.split()[2] for l in nm_txt.splitlines()
            if len(l.split()) == 3 and l.split()[1] == "t"
            and l.split()[2].startswith("pli80_")
            and l.split()[2] != f"pli80_{entry}"]
    if len(subs) != nfuncs - 1:
        fail(f"{tag}: nm shows {len(subs)} local pli80_ subsidiaries {subs}, "
             f"expected {nfuncs - 1} (the {nfuncs}-function program)")
        return
    ok(f"U4 {name}: static laws — 0x7fELF, `file` static x86-64, no PT_INTERP, "
       f"readelf -d stdout 'no dynamic section', nm T pli80_{entry} + "
       f"subsidiaries {subs} as local t")


# ---------- U5 corruption controls ----------

def control_c_m3a(mir: bytes) -> None:
    """C-M3a (§P1-m3.8): swap the two func items so the CALLEE pli80_side
    follows the caller — the pinned order law is load-bearing.  The mutated
    MIR MUST be rejected by mir2o with rc 1 `undeclared name` (measured at
    g11: `ln 16: undeclared name pli80_side`), producing NO object."""
    starts = [m.start() for m in re.finditer(r"^pli80_\w+:\tfunc", mir.decode(), re.M)]
    ends = [m.start() for m in re.finditer(r"^\tendfunc\n", mir.decode(), re.M)]
    if len(starts) != 2 or len(ends) != 2:
        fail("C-M3a: the CALL02 pin does not contain exactly 2 func items — "
             "the anchor moved; control not applied")
        return
    # the callee is the FIRST func item in the pin (entry is LAST); a pin that
    # already emits the caller first would make the control vacuous.
    if not mir.startswith(b"M0:\tmodule\n", 0) or b"pli80_side" not in mir[:starts[1]]:
        fail("C-M3a: the pinned CALL02 order is NOT callee-first — the control "
             "is vacuous against the pin")
        return
    first = mir[starts[0]:ends[0] + len(b"\tendfunc\n")]
    second = mir[starts[1]:ends[1] + len(b"\tendfunc\n")]
    mutated = mir[:starts[0]] + second + mir[ends[0] + len(b"\tendfunc\n"):starts[1]] + first
    cmir = OUTDIR / "C-M3a.mir"
    cmir.write_bytes(mutated)
    cobj = OUTDIR / "C-M3a.o"
    if cobj.exists():
        cobj.unlink()
    r = run([MIR2O, "-f", cmir, cobj], timeout=120)
    record("C-M3a.mir2o.stderr", r.stderr)
    err = r.stderr.decode(errors="replace")
    if cobj.exists():
        fail("C-M3a: the swapped MIR PRODUCED an object — mir2o accepted the "
             "caller-first order; the emission-order law is NOT load-bearing")
        return
    if r.returncode != 1 or "undeclared name" not in err:
        fail(f"C-M3a: the swapped MIR did not fail LOUDLY as predicted: rc "
             f"{r.returncode} (want 1), stderr {err[:200]!r} (want 'undeclared "
             f"name')")
        return
    ok(f"C-M3a FAILED LOUDLY as designed — callee-after-caller MIR is rejected "
       f"by mir2o: rc 1, {err.strip()[:120]} (no object)")


def control_c_m3b(mir: bytes) -> None:
    """C-M3b (§P1-m3.16 B2 inverse mutation): the SECOND call argument
    `hv1` -> `h0` — both formals then designate the SAME home; the corrupted
    program must STILL mir2o, link and EXECUTE, printing `7\n7\n` — and the
    correct pre-registered expectation `2\n7\n` must FAIL on it (the runner
    counts the DETECTION, never a positive pass)."""
    needle = b"\tcall pc1, pli80_alias, h0, hv1\n"
    if mir.count(needle) != 1:
        fail("C-M3b: the CALL06B pin does not contain exactly one "
             "'\\tcall pc1, pli80_alias, h0, hv1' — the anchor moved; control "
             "not applied")
        return
    mutated = mir.replace(needle, b"\tcall pc1, pli80_alias, h0, h0\n")
    cmir = OUTDIR / "C-M3b.mir"
    cmir.write_bytes(mutated)
    cobj = OUTDIR / "C-M3b.o"
    if cobj.exists():
        cobj.unlink()
    r = run([MIR2O, "-f", cmir, cobj], timeout=120)
    if r.returncode != 0 or not cobj.exists():
        fail(f"C-M3b: mir2o on the mutated MIR rc {r.returncode} — the control "
             f"must stay VALID (a toolchain failure is NOT the detection); "
             f"stderr {r.stderr.decode(errors='replace')[:200]}")
        return
    cexe = OUTDIR / "C-M3b.tiny.exe"
    if cexe.exists():
        cexe.unlink()
    r = run(["sh", RECIPE, MODE, cexe, "--", cobj, RUNTIME, DRIVER,
             "-DENTRY=pli80_diffal"], timeout=120)
    if r.returncode != 0 or not cexe.exists():
        fail(f"C-M3b: link of the corrupted object failed — control "
             f"inconclusive: {tail((r.stdout + r.stderr).decode(errors='replace'))!r}")
        return
    os.chmod(cexe, 0o755)
    rr = run([cexe])
    record("C-M3b.obs.txt",
           f"rc {rr.returncode} stdout {rr.stdout!r} stderr {rr.stderr!r}\n".encode())
    if rr.stdout == b"2\n7\n":
        fail("C-M3b: THE MUTATED PROGRAM PRINTS THE CORRECT BYTES — the "
             "home-vs-value discriminator is VACUOUS (a passing control is a "
             "runner failure)")
        return
    if rr.stdout != b"7\n7\n" or rr.returncode != 0 or rr.stderr != b"driver-return=7\n":
        fail(f"C-M3b: the corrupted program did not EXECUTE the predicted WRONG "
             f"behaviour: rc {rr.returncode} stdout {rr.stdout!r} stderr "
             f"{rr.stderr!r} — prediction: rc 0, stdout b'7\\n7\\n', "
             f"driver-return=7 (B2)")
        return
    ok(f"C-M3b FAILED LOUDLY as designed — the h0,hv1->h0,h0 mutant LINKS and "
       f"EXECUTES {rr.stdout!r} rc {rr.returncode} (the alias dies), which the "
       f"pre-registered {b'2\\n7\\n'!r} expectation REJECTS")


def control_c_m3c(mir: bytes) -> None:
    """C-M3c (§P1-m3.17 C3): insert `add t9, t9, 1` immediately BEFORE the
    callee pick3's single `ret t9` (t9 IS pick3's result register — verified
    in the pin).  The mutated artifact MUST stay valid (mir2o rc 0), link and
    EXECUTE the wrong value: the glibc driver with the UNCHANGED
    `-DEXPECTED=3` must return rc 1 with `1\\n2\\n4\\n4\\n`, and the cosmo leg
    must print `1\\n2\\n4\\n` with `driver-return=4\\n`."""
    needle = b"\tret t9\n"
    if mir.count(needle) != 1:
        fail("C-M3c: the CALL07 pin does not contain exactly one '\\tret t9' "
             "— the anchor moved (t9 is pick3's result register); control not "
             "applied")
        return
    mutated = mir.replace(needle, b"\tadd t9, t9, 1\n" + needle)
    if len(mutated) != len(mir) + 15:
        fail(f"C-M3c: mutated text is {len(mutated)} B, expected pin+15 "
             f"({len(mir) + 15} B) — the insert is not the one-line change")
        return
    cmir = OUTDIR / "C-M3c.mir"
    cmir.write_bytes(mutated)
    cobj = OUTDIR / "C-M3c.o"
    if cobj.exists():
        cobj.unlink()
    r = run([MIR2O, "-f", cmir, cobj], timeout=120)
    if r.returncode != 0 or not cobj.exists():
        fail(f"C-M3c: mir2o on the mutated MIR rc {r.returncode} — the control "
             f"must be VALID MIR (a parser rejection is NOT the detection); "
             f"stderr {r.stderr.decode(errors='replace')[:200]}")
        return
    # glibc leg with the UNCHANGED -DEXPECTED=3: the executed value is 4.
    gexe = OUTDIR / "C-M3c.glibc.exe"
    if gexe.exists():
        gexe.unlink()
    r = run(["gcc", "-O0", "-DENTRY=pli80_thrice", "-DEXPECTED=3",
             NATIVE, RUNTIME, cobj, "-o", gexe], timeout=120)
    if r.returncode != 0 or not gexe.exists():
        fail(f"C-M3c: glibc link of the corrupted object failed — control "
             f"inconclusive: {r.stderr.decode(errors='replace')[:200]}")
        return
    rr = run([gexe])
    record("C-M3c.glibc.obs.txt",
           f"rc {rr.returncode} stdout {rr.stdout!r} stderr {rr.stderr!r}\n".encode())
    if rr.returncode == 0 or rr.stdout != b"1\n2\n4\n4\n":
        fail(f"C-M3c: the corrupted glibc leg did NOT fail LOUDLY: rc "
             f"{rr.returncode} (want 1) stdout {rr.stdout!r} (want "
             f"b'1\\n2\\n4\\n4\\n' — the mutated value 4 vs the UNCHANGED "
             f"-DEXPECTED=3) — a control that executes 3 is VACUOUS")
        return
    # cosmo leg: the corrupted console prints the wrong value.
    cexe = OUTDIR / "C-M3c.tiny.exe"
    if cexe.exists():
        cexe.unlink()
    r = run(["sh", RECIPE, MODE, cexe, "--", cobj, RUNTIME, DRIVER,
             "-DENTRY=pli80_thrice"], timeout=120)
    if r.returncode != 0 or not cexe.exists():
        fail(f"C-M3c: cosmo link of the corrupted object failed — control "
             f"inconclusive: {tail((r.stdout + r.stderr).decode(errors='replace'))!r}")
        return
    os.chmod(cexe, 0o755)
    rc2 = run([cexe])
    record("C-M3c.cosmo.obs.txt",
           f"rc {rc2.returncode} stdout {rc2.stdout!r} stderr {rc2.stderr!r}\n".encode())
    if rc2.stdout != b"1\n2\n4\n" or rc2.stderr != b"driver-return=4\n":
        fail(f"C-M3c: the corrupted cosmo leg did not EXECUTE the predicted "
             f"wrong bytes: stdout {rc2.stdout!r} stderr {rc2.stderr!r} — "
             f"prediction b'1\\n2\\n4\\n' + driver-return=4 (C3)")
        return
    ok(f"C-M3c FAILED LOUDLY as designed — the mutated MIR is VALID (mir2o rc "
       f"0, {cobj.stat().st_size} B object, {len(mutated)} B mutated text); "
       f"the UNCHANGED -DEXPECTED=3 glibc driver returns rc 1 with "
       f"{rr.stdout!r}; the cosmo leg executes {rc2.stdout!r} "
       f"{rc2.stderr!r}")


# ---------- main ----------

def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not require_tools():
        return 1
    migration_guard()
    # U1 pins + U2 negatives.
    mirs: dict[str, bytes] = {}
    for name, entry, _exp, _cout, _nfuncs in POSITIVES:
        m = positive_panel(name, entry)
        if m is not None:
            mirs[name] = m
        if name == "CALL09" and m is not None:
            call09_review_law(m)
    for name, export, layer in NEGATIVES:
        negative_panel(name, export, layer)
    # U4 native legs — every positive through the full §P1-m3.7 panel.
    for name, entry, expected, cout, nfuncs in POSITIVES:
        if name not in mirs:
            fail(f"U4 {name}: skipped — the pin panel did not complete")
            continue
        obj = mir2o_leg(name, mirs[name], nfuncs)
        if obj is None:
            continue
        glibc_leg(name, entry, expected, obj, cout + f"{expected}\n".encode())
        cosmo_leg(name, entry, expected, obj, cout)
        exe = OUTDIR / f"{name}.tiny.exe"
        if not exe.exists():
            fail(f"U4 {name}: static laws skipped — no cosmo artifact")
            continue
        static_leg(name, entry, nfuncs, exe)
    # U5 controls always run; a missing anchor fails the control LOUDLY.
    for fid, fn in (("CALL02", control_c_m3a), ("CALL06B", control_c_m3b),
                    ("CALL07", control_c_m3c)):
        if fid in mirs:
            fn(mirs[fid])
        else:
            fail(f"U5 {fid}: the {fid} pin panel did not complete — the "
                 f"non-vacuity control cannot be applied")
    if FAILURES:
        print(f"\nCALL RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nCALL RUNNER PASSED: {CHECKS} checks — the 13 positives (CALL01..10, "
          f"CALLN1/D, CALLN10/B3) regenerate their reviewed pins in two fresh "
          f"processes with zero stderr; the 8 surviving negatives CALLN2..N9 "
          f"refuse at their pinned layers (HIR N2/N3/N5, BACKEND N4/N6/N7/N8/N9) "
          f"with pinned bytes, zero stdout, no artifact; the migration guards "
          f"hold (no retired CALLN1/CALLN10 negative pins); all 13 objects "
          f"mir2o rc 0 and EXECUTE the §P1-m3.6/.15/.16/.17/.18 bytes EXACTLY "
          f"on BOTH the glibc and cosmo-tiny legs (x2 fresh, static laws, nm "
          f"T/t); C-M3a, C-M3b and C-M3c FAILED LOUDLY as designed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
