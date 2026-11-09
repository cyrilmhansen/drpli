#!/usr/bin/env python3
"""E2E-54/P1-m1 console-I/O runner (PLAN §P1-m1.8, work-order step 5).

Console programs built by the native MIR path (PL/I -> HIR -> MIR text -> mir2o ->
genuine MIR object -> pinned Cosmopolitan static link -> native execution) are
JUDGED BY EXECUTED BYTES.  Panels — every command a DIRECT rc, separate processes,
nothing batched:

  V0  prerequisites: pli80mir.exe/pli80hir.exe built; build/p1m0-deps/mir2o present
      ((re)built from the COMMITTED tools/mir_aot/mir2o.c by `sh
      tools/mir_aot/build_native.sh`, which verifies the laboratory pins); the
      console runtime tools/mir_aot/pli_console.c and driver
      tools/mir_aot/console_check.c committed; the pinned Cosmopolitan toolchain
      identified (cosmo_link.sh --toolchain, the §P1-mC K0 law).

  V1  CT2 NO-IO integrity (falsifier T9): M01/M02/M03 .mir regenerated in TWO fresh
      processes, byte-equal to the frozen pins; the .o emitted by the ADDITIVE mir2o
      keeps the frozen sha256 of §P1-m1.6 and is byte-identical to the §P1-m0
      build/mir-aot objects — the import-registration block changes no-IO bytes
      NOWHERE.

  V2  pin panel (this slice's fixtures): M04/M05/M06 .mir == pins in two fresh
      processes, -o file == stdout; negatives N8..N21 pinned rc + pinned stderr
      bytes, ZERO stdout, NO -o file, deterministic x2 (the §P1-m0 refusal-totality
      law — the emitter is never reached); PIPELINE PROOF: every positive fixture
      also lowers through pli80hir.exe rc 0 (the HIR dump was reviewed against
      §P1-m1.4 during measurement, §P1-m1.11 step 4).

  V3  link panel (§P1-m1.6): per positive — mir2o .o rc 0 with the sha256 recorded
      BEFORE linking; cosmo_link.sh TINY links console_check.c (-DENTRY, NO
      -DEXPECTED: the runner judges the bytes) + pli_console.c + the object; the
      artifact starts 0x7fELF, `file` reports a statically linked x86-64 ELF,
      `readelf -lW` has NO PT_INTERP, `nm` lists T pli80_<name> and NO undefined
      pli_console_*/exit (all resolved by the link).

  V4  run legs (§P1-m1.7): EXACT stdout bytes, EXACT stderr bytes on the success
      legs (the table leaves failure-leg stderr unasserted and only records it),
      exact rc; EVERY leg in a FRESH process; determinism re-run for one success
      and one failure leg.

  V5  non-vacuity controls: perturbations live ONLY in scratch copies under ignored
      build/ (committed sources are NEVER perturbed); if a control PASSES, this
      runner FAILS.
        C-a  M04 MIR with the emitted `mul` replaced by `add` — EXECUTES and prints
             13, so the expected-42 leg MUST FAIL (the bytes are judged).
        C-b  a scratch copy of pli_console.c whose get returns OK on the
             not-a-number path — the `abc` leg now exits 0 instead of 2 and MUST FAIL.
        C-c  a scratch copy returning OK with value 0 at EOF — the empty-stdin leg
             now prints 0 with rc 0 instead of rc 1 and MUST FAIL.

THE EXPECTED BYTES BELOW ARE COPIED FROM PLAN §P1-m1.7, where they were
hand-computed BEFORE any run (deviation/never-re-fit law, falsifier T11); they are
never read back from program output.  Expected FILES (hir/mir-expected/) are
measured-first pins and this runner NEVER regenerates or overwrites them.

Evidence -> ignored build/mir-console/.  Console semantics are DRPLi engineering
evidence, never DR claims (ZERO oracle in this slice).

Prerequisites (separate commands, per §P1-m1.11 step 5):
    (cd ocaml && dune build)                 # pli80mir.exe, pli80hir.exe
    sh tools/mir_aot/build_native.sh        # build/p1m0-deps/mir2o from mir2o.c
"""

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
FIXDIR = REPO / "hir" / "mir-fixtures"
EXPDIR = REPO / "hir" / "mir-expected"
DRIVER = REPO / "tools" / "mir_aot" / "console_check.c"
RUNTIME = REPO / "tools" / "mir_aot" / "pli_console.c"
RECIPE = REPO / "tools" / "mir_aot" / "cosmo_link.sh"
OUTDIR = REPO / "build" / "mir-console"
GLIBC_EVIDENCE = REPO / "build" / "mir-aot"      # §P1-m0 objects (CT2 cross-check)

MODE = "tiny"        # §P1-m1.6: the tiny mode is PROVEN for this shape (hop 2)

# fixtures -> --export name (PLAN §P1-m1.7; the console panel of THIS slice)
POSITIVES = [("M04", "io1"), ("M05", "iorw"), ("M06", "msg1")]
# the §P1-m0 no-IO panel, re-checked as CT2/T9 for the additive mir2o
NOIO = [("M01", "calc"), ("M02", "m02"), ("M03", "m03")]
# CT2 (§P1-m1.6): the frozen no-IO object hashes, recorded BEFORE any link in
# §P1-m0 step 5, re-verified in §P1-mC and §P1-m1 hop 6.  NEVER re-fit.
FROZEN_O = {
    "M01": "78656e6cbaced50ed5792742c5b6f47b043607f555364fd014d7e207fbdb0627",
    "M02": "3822f7773ff786838bed43f53863ba8774a690f7c2c01dac1b64be1d313e94d6",
    "M03": "02c15b1bec53ed3374a31e92fecf9d157f5ece7e0c326ec5ecd8aeebd0017c75",
}
NEGATIVES = [f"N{i}" for i in range(8, 22)]      # N8..N21, this slice's refusals

# PLAN §P1-m1.7 — INDEPENDENT expected behaviour, COPIED FROM THE PRE-REGISTRATION.
# (fixture, leg, stdin, expected stdout, expected stderr or None = not asserted,
#  expected rc, meaning).  Hand-computed there; NEVER re-fit from a run.
LEGS = [
    ("M04", "run", b"", b"42\n", b"driver-return=42\n", 0, "put list(x), x=42"),
    ("M05", "good", b"123\n", b"123\n", b"driver-return=123\n", 0, "get/put roundtrip"),
    ("M05", "sign+terminator", b"-42x", b"-42\n", b"driver-return=-42\n", 0,
     "sign + non-digit terminator consumed"),
    ("M05", "not-a-number", b"abc\n", b"", None, 2, "status BAD(2), no output at all"),
    ("M05", "eof", b"", b"", None, 1, "status EOF(1) — never success"),
    ("M05", "outside-W15", b"20000\n", b"", None, 3, "status RANGE(3): 20000 > 16383"),
    ("M06", "run", b"", b"DR PL/I-80 hello from Cosmo!!\n42\n", b"driver-return=42\n",
     0, "literal (29 chars) + newline + 42 + newline = EXACTLY 33 B"),
]
# determinism re-runs (§P1-m1.8 V4): one success leg and one failure leg
DETERMINISM_LEGS = [("M04", "run"), ("M05", "eof")]

ENV = dict(os.environ, LC_ALL="C")   # stable toolchain messages for evidence
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
                          timeout=timeout, env=ENV)


def record(name: str, data: bytes) -> None:
    (OUTDIR / name).write_bytes(data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ---------- V0 ----------

def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, PLIHIR, MIR2O, DRIVER,
                                                  RUNTIME, RECIPE) if not p.exists()]
    if missing:
        fail(f"V0: prerequisites missing: {', '.join(missing)} — run '(cd ocaml && "
             "dune build)' and 'sh tools/mir_aot/build_native.sh'")
        return False
    ok(f"V0: prerequisites present — {PLIHIR.name}, {PLIMIR.name}, mir2o, "
       f"{DRIVER.name}, {RUNTIME.name}, {RECIPE.name}")
    return True


def toolchain_panel() -> bool:
    """V0: the pinned Cosmopolitan toolchain is identified (§P1-mC K0 law)."""
    r = run(["sh", RECIPE, "--toolchain"])
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
    ok("V0: Cosmopolitan toolchain identity + pinned archive verified "
       "(build/mir-console/TOOLCHAIN.txt)")
    return True


# ---------- MIR / object / link helpers ----------

def mir_panel(name: str, export: str, tag: str) -> bytes | None:
    """Regenerate the fixture's MIR in TWO fresh processes; require rc 0, byte-equal
    stdout, stdout == the frozen pin and -o file == stdout."""
    fx = FIXDIR / f"{name}.pli"
    pin = (EXPDIR / f"{name}.mir").read_bytes()
    outs: list[bytes] = []
    errs: list[bytes] = []
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.{tag}{i}.mir"
        if o_file.exists():
            o_file.unlink()          # a stale artifact is never evidence
        r = run([PLIMIR, "--export", export, "-o", o_file, fx])
        if r.returncode != 0:
            fail(f"{tag} {name} run{i}: pli80mir rc {r.returncode} (expected 0); "
                 f"stderr {r.stderr.decode(errors='replace')[:200]}")
            return None
        if not o_file.exists():
            fail(f"{tag} {name} run{i}: -o file absent after rc 0")
            return None
        if o_file.read_bytes() != r.stdout:
            fail(f"{tag} {name} run{i}: -o file != stdout bytes")
            return None
        if r.stdout != pin:
            fail(f"{tag} {name} run{i}: stdout != reviewed pin "
                 f"hir/mir-expected/{name}.mir")
            return None
        outs.append(r.stdout)
        errs.append(r.stderr)
    if outs[0] != outs[1] or errs[0] != errs[1]:
        fail(f"{tag} {name}: fresh-process runs not byte-equal (determinism)")
        return None
    ok(f"{tag} {name}: rc 0 in two fresh processes, stdout == pin "
       f"hir/mir-expected/{name}.mir ({len(outs[0])} B), -o == stdout, deterministic")
    return outs[0]


def object_of(name: str, mir: bytes, tag: str) -> Path | None:
    """mir2o accepts the MIR text and emits the object; sha256 recorded BEFORE any
    link (the CT2 law of §P1-m1.6)."""
    mir_file = OUTDIR / f"{name}.mir"
    mir_file.write_bytes(mir)
    obj = OUTDIR / f"{name}.o"
    if obj.exists():
        obj.unlink()
    r = run([MIR2O, "-f", mir_file, obj])
    if r.returncode != 0 or not obj.exists():
        fail(f"{tag} {name}: mir2o rc {r.returncode} / object absent — the MIR parser "
             f"or the object emitter failed; stderr "
             f"{r.stderr.decode(errors='replace')[:200]}")
        return None
    record(f"{name}.o.sha256", (sha256(obj) + "\n").encode())
    return obj


def cosmo_link(out: Path, inputs: list) -> bool:
    r = run(["sh", RECIPE, MODE, out, "--", *inputs], timeout=180)
    record(f"{out.stem}.link.log", r.stdout + r.stderr)
    if r.returncode != 0 or not out.exists():
        tail = (r.stdout + r.stderr).decode(errors="replace").replace("\r", "\n")
        tail = "\n".join(l for l in tail.splitlines() if "fixme:" not in l)[-400:]
        fail(f"V3: cosmo_link.sh {MODE} rc {r.returncode} / artifact "
             f"{'absent' if not out.exists() else 'present'} for {out.name}; "
             f"diagnostics: {tail!r}")
        return False
    return True


def static_elf_panel(exe: Path, export: str, tag: str) -> bool:
    """V3 sanity (§P1-m1.8): plain static Linux x86-64 ELF, the MIR symbol present,
    the console imports all RESOLVED by the link."""
    head = exe.read_bytes()[:4]
    if head != b"\x7fELF":
        fail(f"{tag}: artifact starts {head!r}, not 0x7f 'ELF' — an APE/launcher file "
             f"is NOT a verified static ELF")
        return False
    r = run(["file", exe])
    record(f"{tag.replace(' ', '_')}.file.txt", r.stdout + r.stderr)
    ftxt = r.stdout.decode(errors="replace")
    if not (r.returncode == 0 and "ELF 64-bit" in ftxt and "x86-64" in ftxt
            and "statically linked" in ftxt):
        fail(f"{tag}: `file` does not report a statically linked x86-64 ELF: {ftxt!r}")
        return False
    r = run(["readelf", "-lW", exe])
    record(f"{tag.replace(' ', '_')}.readelf_l.txt", r.stdout + r.stderr)
    if r.returncode != 0 or b"INTERP" in r.stdout:
        fail(f"{tag}: readelf -lW rc {r.returncode} or PT_INTERP present — NOT static")
        return False
    r = run(["nm", exe])
    record(f"{tag.replace(' ', '_')}.nm.txt", r.stdout + r.stderr)
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
    ok(f"{tag}: 0x7fELF, `file` static x86-64 ELF, NO PT_INTERP, nm T pli80_{export} "
       f"and NO undefined pli_console_*/exit (the link resolved them)")
    return True


# ---------- V1 (CT2 / T9) ----------

def ct2_panel() -> bool:
    """The additive mir2o changes the NO-IO bytes nowhere."""
    good = True
    for name, export in NOIO:
        mir = mir_panel(name, export, "V1")
        if mir is None:
            good = False
            continue
        obj = object_of(name, mir, "V1")
        if obj is None:
            good = False
            continue
        got = sha256(obj)
        if got != FROZEN_O[name]:
            fail(f"V1 CT2 {name}: object sha {got[:16]} != the frozen §P1-m1.6 value "
                 f"{FROZEN_O[name][:16]} — the additive import block changed a no-IO "
                 f"object byte")
            good = False
            continue
        note = "no §P1-m0 object evidence present to compare"
        ref = GLIBC_EVIDENCE / f"{name}.o"
        if ref.exists():
            if sha256(ref) != got:
                fail(f"V1 CT2 {name}: object differs from the kept §P1-m0 evidence "
                     f"{ref.relative_to(REPO)}")
                good = False
                continue
            note = f"byte-identical to build/mir-aot/{name}.o"
        ok(f"V1 CT2 {name}: .mir == pin (x2 fresh), no-IO .o sha {got[:16]} EQUALS the "
           f"frozen §P1-m1.6 value, recorded BEFORE any link; {note}")
    return good


# ---------- V2 ----------

def negative_panel(name: str) -> None:
    export = name.lower()
    fx = FIXDIR / f"{name}.pli"
    exp_rc = int(text_of(EXPDIR / f"{name}.rc").strip())
    exp_err = (EXPDIR / f"{name}.stderr.txt").read_bytes()
    for i in (1, 2):
        o_file = OUTDIR / f"{name}.run{i}.mir"
        if o_file.exists():
            o_file.unlink()
        r = run([PLIMIR, "--export", export, "-o", o_file, fx])
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
    ok(f"V2 {name}: rc {exp_rc}, ZERO stdout, pinned stderr ({len(exp_err)} B), "
       f"deterministic x2 fresh procs, NO artifact — {arm[:120]}")


def pipeline_panel() -> None:
    for name, _export in POSITIVES:
        fx = FIXDIR / f"{name}.pli"
        r = run([PLIHIR, fx])
        record(f"{name}.hir.stdout", r.stdout)
        record(f"{name}.hir.stderr", r.stderr)
        if r.returncode != 0:
            fail(f"V2 pipeline proof {name}: pli80hir.exe rc {r.returncode} on the "
                 f"same fixture — the HIR path itself must be green (no bypass)")
            continue
        ok(f"V2 pipeline proof {name}: same fixture lowers through the existing HIR "
           f"path rc 0 (dump reviewed against §P1-m1.4 during measurement)")


# ---------- V3 / V4 ----------

def link_panel(name: str, export: str, mir: bytes) -> Path | None:
    obj = object_of(name, mir, "V3")
    if obj is None:
        return None
    exe = OUTDIR / f"{name}.console.{MODE}.exe"
    if exe.exists():
        exe.unlink()
    if not cosmo_link(exe, [DRIVER, RUNTIME, obj, f"-DENTRY=pli80_{export}"]):
        return None
    if not static_elf_panel(exe, export, f"V3 {name}[{MODE}]"):
        return None
    return exe


def leg_expect(exe: Path, stdin: bytes, exp_out: bytes, exp_err: bytes | None,
               exp_rc: int) -> tuple[bool, str]:
    """Evaluate ONE §P1-m1.7 expectation against a run of `exe`; returns
    (passed, observation).  Fresh process per call."""
    r = run([exe], stdin=stdin)
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


def run_panel(exes: dict[str, Path]) -> dict:
    results = {}
    for name, leg, stdin, exp_out, exp_err, exp_rc, note in LEGS:
        tag = f"V4 {name}/{leg}"
        if name not in exes:
            fail(f"{tag}: skipped — no verified executable for {name}")
            continue
        passed, obs = leg_expect(exes[name], stdin, exp_out, exp_err, exp_rc)
        record(f"{name}.{leg.replace('+', '_')}.obs.txt",
               (obs + "\n").encode())
        if not passed:
            fail(f"{tag}: {obs} — expected stdout {exp_out!r} (EXACTLY "
                 f"{len(exp_out)} B), rc {exp_rc} ({note})")
            continue
        results[(name, leg)] = obs
        extra = ""
        if name == "M06":
            extra = f" (stdout EXACTLY {len(exp_out)} B as §P1-m1.7 hand-computed)"
        ok(f"{tag}: EXECUTED — {obs} [{note}]{extra}")
    # determinism: one success leg and one failure leg, re-run in fresh processes
    for name, leg in DETERMINISM_LEGS:
        if (name, leg) not in results or name not in exes:
            fail(f"V4 determinism {name}/{leg}: the leg did not pass once")
            continue
        row = [l for l in LEGS if l[0] == name and l[1] == leg][0]
        passed2, obs2 = leg_expect(exes[name], row[2], row[3], row[4], row[5])
        if not passed2 or obs2 != results[(name, leg)]:
            fail(f"V4 determinism {name}/{leg}: fresh re-run disagrees ({obs2})")
            continue
        ok(f"V4 determinism {name}/{leg}: a SECOND fresh process reproduced "
           f"{obs2}")
    return results


# ---------- V5 controls ----------

def patched_runtime(out_name: str, needle: str, replacement: str,
                    what: str) -> Path | None:
    """Perturb a SCRATCH COPY of the committed runtime (never the committed file)."""
    src = text_of(RUNTIME)
    if src.count(needle) != 1:
        fail(f"V5 {what}: cannot apply honestly — the committed runtime does not "
             f"contain exactly one {needle!r}")
        return None
    dst = OUTDIR / out_name
    dst.write_text(src.replace(needle, replacement))
    record(f"{dst.stem}.diff.txt",
           ("\n".join([f"- {needle}", f"+ {replacement}"]) + "\n").encode())
    return dst


def control_link(name: str, export: str, runtime: Path, tag: str) -> Path | None:
    obj = OUTDIR / f"{name}.o"
    if not obj.exists():
        fail(f"{tag}: the V3 object for {name} is absent — control not applicable")
        return None
    exe = OUTDIR / f"{tag.replace('/', '_').replace(' ', '_')}.exe"
    if exe.exists():
        exe.unlink()
    if not cosmo_link(exe, [DRIVER, runtime, obj, f"-DENTRY=pli80_{export}"]):
        return None
    return exe


def controls(mirs: dict[str, bytes], exes: dict[str, Path]) -> None:
    """V5: EVERY control must make its §P1-m1.7 leg FAIL; a passing control means
    this runner fails (non-vacuity is never faked)."""
    # ---- C-a: wrong arithmetic (mul -> add): 6+7 = 13, expected 42 must FAIL.
    row = [l for l in LEGS if l[0] == "M04"][0]
    needle = b"\tmul t3, t1, t2\n"
    if "M04" not in mirs or mirs["M04"].count(needle) != 1:
        fail("V5 C-a: the reviewed M04 MIR does not contain exactly one "
             "'mul t3, t1, t2' — the control cannot be applied honestly")
    else:
        cmir = mirs["M04"].replace(needle, b"\tadd t3, t1, t2\n")
        cobj = object_of("corrupt_m04_mul2add", cmir, "V5 C-a")
        if cobj is not None:
            cexe = OUTDIR / f"corrupt_m04_mul2add.console.{MODE}.exe"
            if cexe.exists():
                cexe.unlink()
            if cosmo_link(cexe, [DRIVER, RUNTIME, cobj, "-DENTRY=pli80_io1"]):
                passed, obs = leg_expect(cexe, row[2], row[3], row[4], row[5])
                r = run([cexe], stdin=b"")
                record("corrupt_m04_mul2add.obs.txt",
                       (f"observed rc {r.returncode} stdout {r.stdout!r} stderr "
                        f"{r.stderr!r}\n").encode())
                if passed:
                    fail("V5 C-a: corruption control PASSED the §P1-m1.7 expectation "
                         f"— {obs}; the executed bytes are not being judged")
                elif r.stdout != b"13\n":
                    fail(f"V5 C-a: the corrupted program did not EXECUTE 13 (stdout "
                         f"{r.stdout!r}, rc {r.returncode}) — the control is not the "
                         f"designed one")
                else:
                    ok("V5 C-a: mul->add — the corrupted program EXECUTED 13 and the "
                       "expected-42 leg FAILED as designed (a real execution result, "
                       "not a tautology)")

    # ---- C-b: get returns OK on the not-a-number path: the abc leg must FAIL.
    row_b = [l for l in LEGS if l[0] == "M05" and l[1] == "not-a-number"][0]
    rb = patched_runtime(
        "corrupt_get_ok_on_bad.c",
        "  if (!isdigit(c)) return PLI_BAD;",
        "  if (!isdigit(c)) { *out = 0; return PLI_OK; } /* control */",
        "V5 C-b (get returns OK on BAD)")
    if rb is not None and "M05" in exes:
        cexe = control_link("M05", "iorw", rb, "V5 C-b")
        if cexe is not None:
            passed, obs = leg_expect(cexe, row_b[2], row_b[3], row_b[4], row_b[5])
            r = run([cexe], stdin=row_b[2])
            record("corrupt_get_ok_on_bad.obs.txt",
                   (f"observed rc {r.returncode} stdout {r.stdout!r} stderr "
                    f"{r.stderr!r}\n").encode())
            if passed:
                fail("V5 C-b: ignored-status control PASSED the §P1-m1.7 expectation "
                     f"— {obs}; a BAD read must never look like success")
            elif r.returncode != 0 or r.stdout != b"0\n":
                fail(f"V5 C-b: the perturbed runtime did not turn the BAD path into a "
                     f"0-with-success run (rc {r.returncode} stdout {r.stdout!r})")
            else:
                ok("V5 C-b: get-returns-OK-on-BAD — the abc leg now EXITS 0 printing 0 "
                   "and FAILED the expected rc 2 / empty stdout as designed")

    # ---- C-c: EOF treated as success: the empty-stdin leg must FAIL.
    row_c = [l for l in LEGS if l[0] == "M05" and l[1] == "eof"][0]
    rc_ = patched_runtime(
        "corrupt_get_ok_on_eof.c",
        "    if (c == EOF) return PLI_EOF;",
        "    if (c == EOF) { *out = 0; return PLI_OK; } /* control */",
        "V5 C-c (EOF as success)")
    if rc_ is not None and "M05" in exes:
        cexe = control_link("M05", "iorw", rc_, "V5 C-c")
        if cexe is not None:
            passed, obs = leg_expect(cexe, row_c[2], row_c[3], row_c[4], row_c[5])
            r = run([cexe], stdin=row_c[2])
            record("corrupt_get_ok_on_eof.obs.txt",
                   (f"observed rc {r.returncode} stdout {r.stdout!r} stderr "
                    f"{r.stderr!r}\n").encode())
            if passed:
                fail("V5 C-c: EOF-as-success control PASSED the §P1-m1.7 expectation "
                     f"— {obs}; EOF must never masquerade as a good read")
            elif r.returncode != 0 or r.stdout != b"0\n":
                fail(f"V5 C-c: the perturbed runtime did not turn EOF into a 0-with-"
                     f"success run (rc {r.returncode} stdout {r.stdout!r})")
            else:
                ok("V5 C-c: EOF-as-success — the empty-stdin leg now prints 0 with rc 0 "
                   "and FAILED the expected rc 1 / empty stdout as designed")


# ---------- main ----------

def main() -> int:
    if not require_tools():
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not toolchain_panel():
        return 1
    ct2_ok = ct2_panel()
    if not ct2_ok:
        fail("V2..V5 skipped: the CT2 no-IO integrity panel (V1) failed")
        if FAILURES:
            print(f"\nCONSOLE RUNNER: {len(FAILURES)} FAILURE(S)")
            return 1
    mirs: dict[str, bytes] = {}
    for name, export in POSITIVES:
        m = mir_panel(name, export, "V2")
        if m is not None:
            mirs[name] = m
    for name in NEGATIVES:
        negative_panel(name)
    pipeline_panel()
    exes: dict[str, Path] = {}
    for name, export in POSITIVES:
        if name not in mirs:
            fail(f"V3 {name}: skipped — the pin panel did not complete")
            continue
        e = link_panel(name, export, mirs[name])
        if e is not None:
            exes[name] = e
    run_panel(exes)
    controls(mirs, exes)   # V5 always runs; a missing input fails the control loudly
    if FAILURES:
        print(f"\nCONSOLE RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nCONSOLE RUNNER PASSED: {CHECKS} checks — CT2 no-IO objects byte-frozen "
          f"under the additive mir2o; M04/M05/M06 MIR == pins and the negatives "
          f"N8..N21 refuse with pinned bytes and no artifact; the genuine MIR objects "
          f"link (tiny) with the console runtime into plain static x86-64 ELF and "
          f"EXECUTED the §P1-m1.7 legs (42, 123, -42, BAD 2, EOF 1, RANGE 3, and the "
          f"33-byte M06 literal line) in fresh processes; all three non-vacuity "
          f"controls failed loudly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
