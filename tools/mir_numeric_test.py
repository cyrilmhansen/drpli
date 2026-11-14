#!/usr/bin/env python3
"""E2E-54/P2-DIFF-2 Stage C — the Mir_numeric panel tool (PLAN §P2-DIFF-2.4).

WHY THIS FILE EXISTS.  Stage C MOVED the pure numeric-domain algebra of the MIR
backend out of `ocaml/hir/mir_backend.ml` into `ocaml/hir/mir_numeric.ml`.  The
movement is a MOVEMENT, not a new rule (§P2-DIFF-2.4 invariant 3: no acceptance
rule is added, widened or narrowed).  Two independent obligations follow, and
this tool is where BOTH are judged:

  X1  the ALGEBRA ITSELF is right — `mirnumtest.exe` (the semtest precedent,
      `ocaml/hir/mirnumtest.ml`) checks the module against hand-derived vector
      tables AND a second, independently written reference formulation, and it
      carries four corrupt controls that must fail LOUDLY.  A control that
      stays silent would mean the check does not observe the value it claims to
      observe, so the exact expected stderr bytes of every control are pinned
      here as literals, never derived from a run.

  X2  the MOVEMENT changed NOTHING — the frozen-pin equivalence.  Every
      committed `.mir` artifact in the repository (mir-expected, mir-cf-expected,
      mir-call-expected, dif-expected; the enumeration is DYNAMIC, so the
      Stage-D DIF03/DIF04 pins are covered too) is re-measured from its
      committed fixture with the POST-EXTRACTION `pli80mir.exe`, twice in fresh
      processes, and must be byte-equal to the pin, with the `-o` file equal to
      stdout and ZERO stderr.  This is the real behavioural-equivalence proof:
      the numeric analysis is what decides every one of those artifacts.

  X3  the HIR panel law of the extraction (the §P2-DIFF-2.4-4 invariant, as
      MEASURED): `tools/hir_test.py` must still exit 0 with EXACTLY 220 `ok `
      lines — the 220 is a FROZEN PANEL CONSTANT, which is why the new checks
      live in this file and were NEVER added to hir_test.py — and the diff of
      the full log against the campaign baseline must be EXACTLY ONE LINE, the
      F8 purity line, whose text embeds the number of `ocaml/hir/*.ml` files.
      Adding two files to `ocaml/hir/` therefore moves that line and nothing
      else; the difference is DISCLOSED here, not hidden (the new unit is NOT
      put in a subdirectory to evade the F8 audit).

  X4  the module's dependency law (§P2-DIFF-2.4-2): `mir_numeric.ml` imports
      NOTHING at all — not even `Hir`.

Prerequisites (separate commands, per the work order):
    (cd ocaml && dune build)     # pli80mir.exe, mirnumtest.exe

Every command runs with a DIRECT rc; nothing is batched.  Evidence is written
under the ignored `build/mir-numeric/` and is NEVER committed.  This tool never
regenerates, rewrites or deletes a pin.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLIMIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
MIRNUM = REPO / "ocaml" / "_build" / "default" / "hir" / "mirnumtest.exe"
HIR_TEST = REPO / "tools" / "hir_test.py"
MODULE = REPO / "ocaml" / "hir" / "mir_numeric.ml"
DUNE = REPO / "ocaml" / "hir" / "dune"
OUTDIR = REPO / "build" / "mir-numeric"

# The campaign baseline of the HIR panel (git-ignored evidence, written by the
# baseline hop of §P2-DIFF-2).  X3 is a law ABOUT THE EXTRACTION relative to the
# tree before it; without the baseline the law is not measured, so X3 FAILS
# rather than skipping.
HIR_BASELINE = REPO / "build" / "e54p2diff2" / "base-hir.log"

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


def note(msg: str) -> None:
    print(f"note  {msg}")


def run(argv: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], capture_output=True,
                          timeout=timeout, env=ENV, cwd=str(REPO))


# --------------------------------------------------------------------------
# X1 — the algebra, judged by mirnumtest.exe
# --------------------------------------------------------------------------

# The live output is the FROZEN check count of the pre-registered driver: the
# vector tables, the reference formulation and the exhaustive [-6,6] envelope
# law are all fixed in ocaml/hir/mirnumtest.ml, so the count is a constant.
LIVE_OK = b"MIR-NUMERIC OK 41563 checks\n"

# The four corrupt controls, with the EXACT stderr bytes each must produce.
# Every line is `MIRNUM-FAIL: <family> <index> vs reference` — the reference
# side of one family is perturbed, so the module must DISAGREE with the
# reference on exactly those vectors that the perturbation touches.  These
# literals are hand-derived from the vector tables in mirnumtest.ml; they are
# never copied from a run.
CORRUPT: dict[str, bytes] = {
    "--corrupt-sub": b"".join(
        f"MIRNUM-FAIL: sub {i} vs reference\n".encode() for i in (0, 2, 5)),
    "--corrupt-hull": b"".join(
        f"MIRNUM-FAIL: hull {i} vs reference\n".encode() for i in (0, 1, 2)),
    "--corrupt-window": b"".join(
        f"MIRNUM-FAIL: window {i} vs reference\n".encode() for i in range(7)),
    "--corrupt-decimal": b"".join(
        f"MIRNUM-FAIL: decimal {i} vs reference\n".encode() for i in (5, 6, 7)),
}


def live_driver() -> None:
    """X1a: the live driver — rc 0, the exact OK line, ZERO stderr, ×2 fresh."""
    if not MIRNUM.exists():
        fail(f"X1 prerequisites: {MIRNUM.relative_to(REPO)} missing — run "
             "'(cd ocaml && dune build)'")
        return
    outs = []
    for i in (1, 2):
        r = run([MIRNUM])
        if r.returncode != 0:
            fail(f"X1 live run{i}: mirnumtest rc {r.returncode} (expected 0); "
                 f"stderr: {r.stderr.decode('utf-8', 'replace')[:600]}")
            return
        if r.stderr != b"":
            fail(f"X1 live run{i}: stderr is not empty ({len(r.stderr)} B)")
            return
        if r.stdout != LIVE_OK:
            fail(f"X1 live run{i}: stdout {r.stdout!r} != the frozen "
                 f"{LIVE_OK!r}")
            return
        outs.append(r.stdout)
    ok(f"X1 mirnumtest LIVE: rc 0 x2 fresh procs, stderr 0 B, stdout exactly "
       f"{LIVE_OK.decode().strip()!r} (the frozen check count), deterministic")


def corrupt_controls() -> None:
    """X1b: the four non-vacuity controls — rc 1, ZERO stdout, pinned stderr."""
    for mode, want in CORRUPT.items():
        got = []
        for i in (1, 2):
            r = run([MIRNUM, mode])
            if r.returncode != 1:
                fail(f"X1 {mode} run{i}: rc {r.returncode} (expected 1) — the "
                     f"control is VACUOUS or the driver died")
                break
            if r.stdout != b"":
                fail(f"X1 {mode} run{i}: a FAILING driver printed "
                     f"{len(r.stdout)} B on stdout — the output contract "
                     f"(failure is stderr-only) is broken")
                break
            if r.stderr != want:
                fail(f"X1 {mode} run{i}: stderr {r.stderr!r} != the pinned "
                     f"{want!r}")
                break
            got.append(r.stderr)
        else:
            n = want.count(b"\n")
            ok(f"X1 {mode}: rc 1 x2 fresh procs, ZERO stdout, {n} MIRNUM-FAIL "
               f"line(s) on stderr byte-equal to the pinned control")


def usage_control() -> None:
    """X1c: a bogus argument is a usage error (rc 2), never a silent pass."""
    r = run([MIRNUM, "--corrupt-nonsense"])
    if r.returncode != 2:
        fail(f"X1 usage: rc {r.returncode} for an unknown mode (expected 2)")
        return
    if LIVE_OK in r.stdout or b"MIRNUM-FAIL" in r.stderr:
        fail("X1 usage: a usage error reported a check result")
        return
    ok("X1 usage: unknown mode -> rc 2, no OK line and no MIRNUM-FAIL line")


# --------------------------------------------------------------------------
# X2 — the frozen-pin equivalence (the behavioural proof of the movement)
# --------------------------------------------------------------------------

# fixture -> --export entry name (the same names the panel tools use; the
# procedure names are case-folded by the compiler).
EXPORTS = {
    "M01": "calc", "M02": "m02", "M03": "m03", "M04": "io1", "M05": "iorw",
    "M06": "msg1", "N2": "n2",
    "CF01": "choose", "CF02": "nocls", "CF03": "nest", "CF04": "eqne",
    "CF05": "iocond", "CF06": "count", "CF07": "zero", "CF08": "oneit",
    "CF09": "loopcond", "CF10": "stepdn",
    "CALL01": "main3", "CALL02": "call02", "CALL03": "two", "CALL04": "chain",
    "CALL05": "retvoid", "CALL06A": "aliasin", "CALL06B": "diffal",
    "CALL07": "thrice", "CALL08": "wret", "CALL09": "uncalled",
    "CALL10": "mixmod", "CALLN1": "pval", "CALLN10": "refm3a",
    "DIF01": "tariff", "DIF02": "steps",
    "DIF03": "pricing", "DIF04": "production",
    "DIF05": "billing", "DIF06": "batch",
}

# pin dir -> fixture dir (the committed layout of the MIR campaign).
FAMILIES = [
    ("hir/mir-expected", "hir/mir-fixtures"),
    ("hir/mir-cf-expected", "hir/mir-cf-fixtures"),
    ("hir/mir-call-expected", "hir/mir-call-fixtures"),
    ("hir/dif-expected", "hir/dif-fixtures"),
]


def pins() -> list[tuple[str, Path, Path, str]]:
    """(name, pin, fixture, export) for EVERY committed .mir pin."""
    out = []
    for expdir, fixdir in FAMILIES:
        for pin in sorted((REPO / expdir).glob("*.mir")):
            name = pin.stem
            fx = REPO / fixdir / f"{name}.pli"
            out.append((name, pin, fx, EXPORTS[name]))
    return out


def pin_equivalence() -> list[str]:
    """X2: each pin re-measured from its fixture by the post-extraction
    compiler, twice in fresh processes; stdout == pin == -o file; no stderr."""
    if not PLIMIR.exists():
        fail(f"X2 prerequisites: {PLIMIR.relative_to(REPO)} missing — run "
             "'(cd ocaml && dune build)'")
        return []
    names = []
    for name, pin, fx, export in pins():
        if not fx.exists():
            fail(f"X2 {name}: fixture {fx.relative_to(REPO)} is missing")
            continue
        outs = []
        for i in (1, 2):
            o_file = OUTDIR / f"{name}.it{i}.mir"
            r = run([PLIMIR, "--export", export, "-o", o_file, fx])
            if r.returncode != 0:
                fail(f"X2 {name} run{i}: pli80mir rc {r.returncode} — the "
                     f"extraction BROKE a positive (stderr: "
                     f"{r.stderr.decode('utf-8', 'replace')[:400]})")
                break
            if r.stderr != b"":
                fail(f"X2 {name} run{i}: rc 0 but {len(r.stderr)} B of stderr")
                break
            if not o_file.exists():
                fail(f"X2 {name} run{i}: -o file absent after rc 0")
                break
            if o_file.read_bytes() != r.stdout:
                fail(f"X2 {name} run{i}: -o file != stdout bytes")
                break
            if r.stdout != pin.read_bytes():
                fail(f"X2 {name} run{i}: the re-measured MIR is NOT the "
                     f"committed pin {pin.relative_to(REPO)} — the extraction "
                     f"MOVED a pin (STOP condition §P2-DIFF-2.7-iv)")
                break
            outs.append(r.stdout)
        else:
            if outs[0] != outs[1]:
                fail(f"X2 {name}: the two fresh runs are not byte-equal")
                continue
            names.append(name)
            ok(f"X2 {name}: {len(outs[0])} B == pin {pin.relative_to(REPO)} "
               f"byte-for-byte, x2 fresh procs, -o == stdout, ZERO stderr")
    return names


# --------------------------------------------------------------------------
# X3 — the hir_test panel law of the extraction
# --------------------------------------------------------------------------

F8_RE = re.compile(
    r"^ok    F8 HIR purity \(no backend/byte-layout vocabulary\): "
    r"(\d+) files clean of 7 patterns \(after nested-comment strip\)$")


def hir_panel_law() -> None:
    """X3: hir_test rc 0, EXACTLY 220 `ok ` lines, and the diff vs the
    campaign baseline is EXACTLY the F8 file-count line."""
    if not HIR_BASELINE.exists():
        fail(f"X3: the campaign baseline {HIR_BASELINE.relative_to(REPO)} is "
             f"absent — the HIR panel law is a comparison against the "
             f"pre-extraction log, so it is NOT MEASURED here (never skip it)")
        return
    r = run([sys.executable, HIR_TEST], timeout=900)
    if r.returncode != 0:
        fail(f"X3 hir_test rc {r.returncode} (expected 0); stderr: "
             f"{r.stderr.decode('utf-8', 'replace')[:400]}")
        return
    log = r.stdout.decode("utf-8", "replace").splitlines()
    n_ok = sum(1 for line in log if line.startswith("ok "))
    if n_ok != 220:
        fail(f"X3: {n_ok} `ok ` lines, the FROZEN panel constant is 220")
        return
    if any(line.startswith("FAIL") for line in log):
        fail("X3: the hir log contains a FAIL line despite rc 0")
        return
    base = HIR_BASELINE.read_text().splitlines()
    if len(base) != len(log):
        fail(f"X3: the hir log has {len(log)} lines, the baseline has "
             f"{len(base)} — the extraction must move EXACTLY the F8 line")
        return
    diffs = [(i, b, c) for i, (b, c) in enumerate(zip(base, log), 1) if b != c]
    if len(diffs) != 1:
        fail(f"X3: {len(diffs)} line(s) differ from the baseline "
             f"{[i for i, _, _ in diffs]} — the only allowed difference is the "
             f"F8 file count")
        return
    i, b_line, c_line = diffs[0]
    mb, mc = F8_RE.match(b_line), F8_RE.match(c_line)
    if not (mb and mc):
        fail(f"X3: the single differing line {i} is not the F8 purity line; "
             f"baseline {b_line!r} vs current {c_line!r}")
        return
    n_files = len(list((REPO / "ocaml" / "hir").glob("*.ml")))
    if int(mc.group(1)) != n_files:
        fail(f"X3: the F8 line reports {mc.group(1)} files, the glob "
             f"ocaml/hir/*.ml has {n_files}")
        return
    if int(mb.group(1)) >= n_files:
        fail(f"X3: the baseline F8 count {mb.group(1)} is not below the "
             f"current {n_files}")
        return
    ok(f"X3 hir_test rc 0, {n_ok} `ok ` lines (the frozen 220 UNMOVED), and the "
       f"full log differs from the baseline in EXACTLY line {i} — the F8 purity "
       f"glob {mb.group(1)} -> {mc.group(1)} files (the check embeds the "
       f"ocaml/hir/*.ml count; the extraction adds mir_numeric.ml + "
       f"mirnumtest.ml, both clean of all 7 patterns)")
    note(f"X3 the byte-identical-log law and the 'extraction lives in "
         f"ocaml/hir/' law are in DIRECT CONFLICT; the resolution is DISCLOSURE "
         f"of this one-line diff, never hiding the new unit in a subdirectory")


# --------------------------------------------------------------------------
# X4 — the dependency law of the module (§P2-DIFF-2.4-2)
# --------------------------------------------------------------------------

# The module must import NOTHING.  These are the names it must never mention.
FORBIDDEN = [
    r"\bHir\b", r"\bHir_build\b", r"\bTarget\b", r"\bDiagnostic\b",
    r"\bBackend\b", r"\bMir_backend\b", r"\bRel80\b", r"\bCodegen\b",
    r"\bParser\b", r"\bSemantic_env\b", r"\bUnix\b", r"^\s*open\s",
]


def dependency_law() -> None:
    """X4: the module is standalone, it is in the library, and the extraction
    is a movement (the endpoint algebra is the only arithmetic it holds)."""
    if not MODULE.exists():
        fail(f"X4: {MODULE.relative_to(REPO)} is missing")
        return
    # Strip the nested-comment header the same way the F8 purity check does:
    # the check is CODE-only, so the law is tested on the code too.
    code = re.sub(r"\(\*(?:[^*]|\*(?!\)))*\*\)", "", MODULE.read_text(),
                  flags=re.S)
    hits = [pat for pat in FORBIDDEN if re.search(pat, code, flags=re.M)]
    if hits:
        fail(f"X4 dependency law: mir_numeric.ml code mentions {hits}")
        return
    dune = DUNE.read_text()
    m = re.search(r"\(name pli80_hir\)\s*\(modules ([^)]*)\)", dune)
    if not m or "mir_numeric" not in m.group(1).split():
        fail("X4: the pli80_hir (modules ...) list does not carry mir_numeric")
        return
    ok("X4 dependency law: mir_numeric.ml code references no Hir/Target/"
       "Diagnostic/Backend/Mir_backend/Rel80/Codegen/Parser/Semantic_env/Unix "
       "name and has no `open`; the library's (modules ...) list carries it")
    n = len(re.findall(r"^let ", code, flags=re.M))
    if n != 9:  # the nine lets are the whole algebra; `type iv' is a type
        fail(f"X4: the module exposes {n} top-level `let's, expected 9 "
             f"(window, in_window, show_iv, decimal_int, iv_add, iv_sub, "
             f"iv_mul, iv_neg, iv_hull) — the extraction must not grow a "
             f"second responsibility")
        return
    ok(f"X4: the module is exactly {n} top-level `let's plus the `iv' type — "
       f"the window, containment, display, the literal parser, the four "
       f"interval ops and the join hull (ONE responsibility)")


def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, MIRNUM) if not p.exists()]
    if missing:
        fail(f"prerequisites missing: {', '.join(missing)} — run "
             "'(cd ocaml && dune build)'")
        return False
    return True


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if not require_tools():
        return 1
    live_driver()
    corrupt_controls()
    usage_control()
    names = pin_equivalence()
    hir_panel_law()
    dependency_law()
    if FAILURES:
        print(f"\nMIR-NUMERIC RUNNER: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nMIR-NUMERIC RUNNER PASSED: {CHECKS} checks — the pure algebra is "
          f"judged by mirnumtest (41563 live checks, the frozen count) and by "
          f"four corrupt controls whose exact stderr bytes are pinned; "
          f"{len(names)} committed .mir pins (mir-expected, mir-cf-expected, "
          f"mir-call-expected, dif-expected) were RE-MEASURED from the "
          f"committed fixtures with the post-extraction compiler and are "
          f"byte-equal to the pins, x2 fresh processes each; the hir_test "
          f"panel is rc 0 with the frozen 220 ok lines and the single "
          f"disclosed F8 file-count line; mir_numeric.ml imports nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
