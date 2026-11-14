#!/usr/bin/env python3
"""E2E-54/P2-DIFF-3 Stage C — the Mir_return_summary panel tool (PLAN §P2-DIFF-3).

WHY THIS FILE EXISTS.  Stage B added the pure interprocedural return-summary
module `ocaml/hir/mir_return_summary.ml` and integrated it into the MIR
backend via `mir_backend.ml`.  The module's job is to prove a strictly smaller
return interval for a reached nonrecursive side-effect-free value procedure
than the backend would otherwise use (the full declared window W(p)).  The
integration is the single point where a summary can be used — `lower_call_e`
— and the defensive gate `in_window (window cq) iv` is the only guard.

Three independent obligations follow, and this tool is where ALL THREE are
judged:

  Y1  the MODULE ITSELF is right — `mirsumtest.exe` (the semtest/mirnumtest
      precedent, `ocaml/hir/mirsumtest.ml`) checks the module against hand-
      derived vector tables AND a second, independently written reference
      formulation (the full-domain concrete interpreter), and it carries three
      corrupt controls that must fail LOUDLY.  The exact expected stderr bytes
      of every control are pinned here as literals, never derived from a run.

  Y2  the INTEGRATION is right — the two DIF fixtures (DIF03, DIF04) are the
      ONLY real-world test cases the pre-registered plan permits.  Before the
      module the `*` was refused (HIR-E19); after it, the summary is the only
      new mechanism and both DIF sources must now compile.  This is the
      behavioural proof: the summary is used by the backend.

  Y3  the EXISTING pins are UNMOVED — the summary must NOT move any existing
      `.mir` pin.  The 32 pins that predate the Stage-D DIF03/DIF04 additions
      are re-measured from their fixtures with the post-Stage-B compiler and
      must be byte-equal to the committed pins.  This is the
      behavioural-equivalence proof.

  Y4  the module's dependency law (§P2-DIFF-3): the module imports only
      `Hir` and `Mir_numeric`; it has no `open`, no `Target`, no `Diagnostic`,
      no `Backend`, no `Mir_backend`, no `Rel80`, no `Codegen`, no `Parser`,
      no `Semantic_env`, no `Unix`.

  Y5  the hir_test panel law of the addition (the §P2-DIFF-3 invariant):
      `tools/hir_test.py` must still exit 0 with EXACTLY 220 `ok ` lines — the
      220 is a FROZEN PANEL CONSTANT, which is why the new checks live in this
      file and were NEVER added to hir_test.py — and the diff of the full log
      against the campaign baseline must be EXACTLY ONE LINE, the F8 purity
      line, whose text embeds the number of `ocaml/hir/*.ml` files.  Adding
      two files (the module and the test driver) to `ocaml/hir/` therefore
      moves that line and nothing else; the difference is DISCLOSED here, not
      hidden (the new unit is NOT put in a subdirectory to evade the F8 audit).

Prerequisites (separate commands, per the work order):
    (cd ocaml && dune build)     # pli80mir.exe, mirsumtest.exe

Every command runs with a DIRECT rc; nothing is batched.  Evidence is written
under the ignored `build/mir-return-summary/` and is NEVER committed.  This
tool never regenerates, rewrites or deletes a pin.

Zero oracle: `PLI.COM` never runs; the historical compiler is never touched.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLIMIR = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80mir.exe"
MIRSUM = REPO / "ocaml" / "_build" / "default" / "hir" / "mirsumtest.exe"
HIR_TEST = REPO / "tools" / "hir_test.py"
MODULE = REPO / "ocaml" / "hir" / "mir_return_summary.ml"
DUNE = REPO / "ocaml" / "hir" / "dune"
OUTDIR = REPO / "build" / "mir-return-summary"

# The campaign baseline of the HIR panel (git-ignored evidence, written by the
# baseline hop of §P2-DIFF-2).  Y5 is a law ABOUT THE ADDITION relative to the
# tree before it; without the baseline the law is not measured, so Y5 FAILS
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
# Y1 — the module, judged by mirsumtest.exe
# --------------------------------------------------------------------------

# The live output is the FROZEN check count of the pre-registered driver.
# The check count is a frozen constant because the vectors, the reference
# formulation and the three corrupt modes are all fixed in
# ocaml/hir/mirsumtest.ml.
LIVE_OK = b"MIR-SUM OK 55 checks\n"

# The three corrupt controls, with the EXACT stderr bytes each must produce.
# Every line is `MIRSUM-FAIL: <name> got <got> expected <want>`.  The
# perturbations are the INFERRED side only; the reference is untouched.
# These literals are hand-derived from the driver's expectation table in
# mirsumtest.ml; they are never copied from a run.
#
# --corrupt-widen:  the classifier's Known (1,3) is widened to (1,4), the
#                   const-direct's Known (7,7) is widened to (7,8), etc.
# --corrupt-narrow: the classifier's Known (1,3) is narrowed to (1,2), the
#                   const-direct's Known (7,7) is narrowed to (7,6), etc.
# --corrupt-unknown:every pid-1 Unknown is forced to Known (1,2).
CORRUPT: dict[str, list[str]] = {
    "--corrupt-widen": [
        "MIRSUM-FAIL: const-direct: got Known [7,8], expected Known [7,7]",
        "MIRSUM-FAIL: const-local: got Known [5,6], expected Known [5,5]",
        "MIRSUM-FAIL: classifier: got Known [1,4], expected Known [1,3]",
        "MIRSUM-FAIL: two-arm-hull: got Known [1,3], expected Known [1,2]",
        "MIRSUM-FAIL: missing-else-identity: got Known [1,3], expected Known [1,2]",
        "MIRSUM-FAIL: overwrite-after-join: got Known [4,5], expected Known [4,4]",
        "MIRSUM-FAIL: literal-16383: got Known [16383,16384], expected Known [16383,16383]",
        "MIRSUM-FAIL: identity-full-window: got Known [-16383,16384], expected Known [-16383,16383]",
        "MIRSUM-FAIL: classifier-narrow-precision: got Known [1,4], expected Known [1,3]",
        "MIRSUM-FAIL: boundary-neg-16383: got Known [-16383,16384], expected Known [-16383,16383]",
        "MIRSUM-FAIL: boundary-neg-op: got Known [-16383,-16382], expected Known [-16383,-16383]",
        "MIRSUM-FAIL: boundary-tight: got Known [-16383,16384], expected Known [-16383,16383]",
    ],
    "--corrupt-narrow": [
        "MIRSUM-FAIL: const-direct: got Known [7,6], expected Known [7,7]",
        "MIRSUM-FAIL: const-local: got Known [5,4], expected Known [5,5]",
        "MIRSUM-FAIL: classifier: got Known [1,2], expected Known [1,3]",
        "MIRSUM-FAIL: two-arm-hull: got Known [1,1], expected Known [1,2]",
        "MIRSUM-FAIL: missing-else-identity: got Known [1,1], expected Known [1,2]",
        "MIRSUM-FAIL: overwrite-after-join: got Known [4,3], expected Known [4,4]",
        "MIRSUM-FAIL: literal-16383: got Known [16383,16382], expected Known [16383,16383]",
        "MIRSUM-FAIL: identity-full-window: got Known [-16383,16382], expected Known [-16383,16383]",
        "MIRSUM-FAIL: classifier-narrow-precision: got Known [1,2], expected Known [1,3]",
        "MIRSUM-FAIL: boundary-neg-16383: got Known [-16383,16382], expected Known [-16383,16383]",
        "MIRSUM-FAIL: boundary-neg-op: got Known [-16383,-16384], expected Known [-16383,-16383]",
        "MIRSUM-FAIL: boundary-tight: got Known [-16383,16382], expected Known [-16383,16383]",
    ],
    "--corrupt-unknown": [
        "MIRSUM-FAIL: non-exhaustive-assign: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: effect-put: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: effect-call-s: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: effect-get: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: effect-stop: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: effect-while: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: early-return: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: return-not-last: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: bare-return: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-convert: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-relational-value: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-call-e: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-return-call: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-elem-read: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-elem-assign: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-unknown-ef: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: unsupported-condition-call: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: escape-full-window: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: escape-add-1: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: literal-16384: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: undeclared-formal-read: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: undeclared-read: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: double-declare: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: foreign-scope-declare: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: non-integer-declare: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: static-declare: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: void-proc: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: non-bin-result: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: empty-body: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: ret-p0: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: ret-p16: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: formal-p0: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: formal-p16: got Known [1,2], expected Unknown",
        "MIRSUM-FAIL: formal-non-bin: got Known [1,2], expected Unknown",
    ],
}


def live_driver() -> None:
    """Y1a: the live driver — rc 0, the exact OK line, ZERO stderr, ×2 fresh."""
    if not MIRSUM.exists():
        fail(f"Y1 prerequisites: {MIRSUM.relative_to(REPO)} missing — run "
             "'(cd ocaml && dune build)'")
        return
    for i in (1, 2):
        r = run([MIRSUM])
        if r.returncode != 0:
            fail(f"Y1 live run{i}: mirsumtest rc {r.returncode} (expected 0); "
                 f"stderr: {r.stderr.decode('utf-8', 'replace')[:600]}")
            return
        if r.stderr != b"":
            fail(f"Y1 live run{i}: stderr is not empty ({len(r.stderr)} B)")
            return
        if r.stdout != LIVE_OK:
            fail(f"Y1 live run{i}: stdout {r.stdout!r} != the frozen "
                 f"{LIVE_OK!r}")
            return
    ok(f"Y1 mirsumtest LIVE: rc 0 x2 fresh procs, stderr 0 B, stdout exactly "
       f"{LIVE_OK.decode().strip()!r} (the frozen check count)")


def corrupt_controls() -> None:
    """Y1b: the three non-vacuity controls — rc 1, ZERO stdout, pinned stderr."""
    for mode, lines in CORRUPT.items():
        want = ("\n".join(lines) + "\n").encode()
        for i in (1, 2):
            r = run([MIRSUM, mode])
            if r.returncode != 1:
                fail(f"Y1 {mode} run{i}: rc {r.returncode} (expected 1) — the "
                     f"control is VACUOUS or the driver died")
                break
            if r.stdout != b"":
                fail(f"Y1 {mode} run{i}: a FAILING driver printed "
                     f"{len(r.stdout)} B on stdout — the output contract "
                     f"(failure is stderr-only) is broken")
                break
            if r.stderr != want:
                fail(f"Y1 {mode} run{i}: stderr {r.stderr!r} != the pinned "
                     f"{want!r}")
                break
        else:
            ok(f"Y1 {mode}: rc 1 x2 fresh procs, ZERO stdout, {len(lines)} "
               f"MIRSUM-FAIL line(s) on stderr byte-equal to the pinned "
               f"control")


def usage_control() -> None:
    """Y1c: a bogus argument is a usage error (rc 2), never a silent pass."""
    r = run([MIRSUM, "--corrupt-nonsense"])
    if r.returncode != 2:
        fail(f"Y1 usage: rc {r.returncode} for an unknown mode (expected 2)")
        return
    if LIVE_OK in r.stdout or b"MIRSUM-FAIL" in r.stderr:
        fail("Y1 usage: a usage error reported a check result")
        return
    ok("Y1 usage: unknown mode -> rc 2, no OK line and no MIRSUM-FAIL line")


# --------------------------------------------------------------------------
# Y2 — the integration is right: the two DIF fixtures are accepted
# --------------------------------------------------------------------------

# DIF03 (pricing) and DIF04 (production) are the only real-world tests of the
# summary integration.  The pre-registered design: both had a `*` that was
# refused by the old backend (HIR-E19 on the full window); after the summary
# the classifier's interval [1,3] is used, and the `*` is admitted.
DIF_INTEGRATION = {
    "DIF03": "pricing",
    "DIF04": "production",
}


def dif_integration() -> None:
    """Y2: the DIF03/DIF04 fixtures now compile with the summary."""
    if not PLIMIR.exists():
        fail(f"Y2 prerequisites: {PLIMIR.relative_to(REPO)} missing — run "
             "'(cd ocaml && dune build)'")
        return
    for name, entry in DIF_INTEGRATION.items():
        src = REPO / "hir" / "dif-fixtures" / f"{name}.pli"
        if not src.exists():
            fail(f"Y2 {name}: source {src.relative_to(REPO)} is missing")
            continue
        outs = []
        for i in (1, 2):
            o_file = OUTDIR / f"{name}.it{i}.mir"
            r = run([PLIMIR, "--export", entry, "-o", o_file, src])
            if r.returncode != 0:
                fail(f"Y2 {name} run{i}: pli80mir --export {entry} rc "
                     f"{r.returncode} — the integration is BROKEN (the "
                     f"summary should have admitted the `*`): "
                     f"{r.stderr.decode('utf-8', 'replace')[:500]}")
                break
            if r.stderr != b"":
                fail(f"Y2 {name} run{i}: rc 0 but {len(r.stderr)} B of stderr")
                break
            if not o_file.exists():
                fail(f"Y2 {name} run{i}: -o file absent after rc 0")
                break
            if o_file.read_bytes() != r.stdout:
                fail(f"Y2 {name} run{i}: -o file != stdout bytes")
                break
            outs.append(r.stdout)
        else:
            if outs[0] != outs[1]:
                fail(f"Y2 {name}: the two fresh runs are not byte-equal")
                continue
            ok(f"Y2 {name}: pli80mir --export {entry} rc 0 x2, "
               f"{len(outs[0])} B, -o == stdout, ZERO stderr (the summary "
               f"admits the `*` on the classifier's return interval)")


# --------------------------------------------------------------------------
# Y3 — the existing .mir pins are UNMOVED (the behavioural-equivalence proof)
# --------------------------------------------------------------------------

# The fixture -> export-name map.  The 32 pins that existed BEFORE the
# Stage-D pins: the summary must not move ANY of them, and this is the
# behavioural-equivalence proof of that law.  The Stage-D DIF03/DIF04 pins
# are NEW outputs of the summary-enabled compiler (they are not "existing"
# pins); they are re-measured by mir_numeric_test.py X2 (dynamic pin
# enumeration, all committed pins) and byte-compared by the dual-backend
# runner's native lane on every execution.
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
}

FAMILIES = [
    ("hir/mir-expected", "hir/mir-fixtures"),
    ("hir/mir-cf-expected", "hir/mir-cf-fixtures"),
    ("hir/mir-call-expected", "hir/mir-call-fixtures"),
    ("hir/dif-expected", "hir/dif-fixtures"),
]


def pin_equivalence() -> int:
    """Y3: each pin re-measured from its fixture by the post-Stage-B compiler,
    twice in fresh processes; stdout == pin == -o file; no stderr.
    Returns the number of pins re-measured."""
    if not PLIMIR.exists():
        fail(f"Y3 prerequisites: {PLIMIR.relative_to(REPO)} missing — run "
             "'(cd ocaml && dune build)'")
        return 0
    n = 0
    for expdir, fixdir in FAMILIES:
        for pin in sorted((REPO / expdir).glob("*.mir")):
            name = pin.stem
            if name not in EXPORTS:
                continue
            fx = REPO / fixdir / f"{name}.pli"
            if not fx.exists():
                fail(f"Y3 {name}: fixture {fx.relative_to(REPO)} is missing")
                continue
            for i in (1, 2):
                o_file = OUTDIR / f"{name}.it{i}.mir"
                r = run([PLIMIR, "--export", EXPORTS[name], "-o", o_file, fx])
                if r.returncode != 0:
                    fail(f"Y3 {name} run{i}: pli80mir rc {r.returncode} — the "
                         f"summary BROKE a positive (stderr: "
                         f"{r.stderr.decode('utf-8', 'replace')[:400]})")
                    break
                if r.stderr != b"":
                    fail(f"Y3 {name} run{i}: rc 0 but {len(r.stderr)} B of "
                         f"stderr")
                    break
                if not o_file.exists():
                    fail(f"Y3 {name} run{i}: -o file absent after rc 0")
                    break
                if o_file.read_bytes() != r.stdout:
                    fail(f"Y3 {name} run{i}: -o file != stdout bytes")
                    break
                if r.stdout != pin.read_bytes():
                    fail(f"Y3 {name} run{i}: the re-measured MIR is NOT the "
                         f"committed pin {pin.relative_to(REPO)} — the "
                         f"summary MOVED a pin (STOP condition §P2-DIFF-3)")
                    break
            else:
                n += 1
    if n == 0:
        fail("Y3: NO pins re-measured — the EXPORTS map or the pin dirs are "
             "wrong")
        return n
    ok(f"Y3 pin equivalence: {n} committed .mir pins re-measured from the "
       f"committed fixtures, byte-equal to the pins, x2 fresh procs, "
       f"-o == stdout, ZERO stderr (the summary moved NOTHING)")
    return n


# --------------------------------------------------------------------------
# Y4 — the module's dependency law (§P2-DIFF-3)
# --------------------------------------------------------------------------

# The module must import only Hir and Mir_numeric.  These are the names it
# must never mention.
FORBIDDEN = [
    r"\bTarget\b", r"\bDiagnostic\b", r"\bBackend\b", r"\bMir_backend\b",
    r"\bRel80\b", r"\bCodegen\b", r"\bParser\b", r"\bSemantic_env\b",
    r"\bUnix\b", r"\bHir_build\b", r"\bMir_return_summary\b",
    r"^\s*open\s",
]


def dependency_law() -> None:
    """Y4: the module is standalone, it is in the library, and the F8 check
    is clean."""
    if not MODULE.exists():
        fail(f"Y4: {MODULE.relative_to(REPO)} is missing")
        return
    # Strip the nested-comment header the same way the F8 purity check does:
    # the check is CODE-only, so the law is tested on the code too.
    code = re.sub(r"\(\*(?:[^*]|\*(?!\)))*\*\)", "", MODULE.read_text(),
                  flags=re.S)
    hits = [pat for pat in FORBIDDEN if re.search(pat, code, flags=re.M)]
    if hits:
        fail(f"Y4 dependency law: mir_return_summary.ml code mentions {hits}")
        return
    dune = DUNE.read_text()
    m = re.search(r"\(name pli80_hir\)\s*\(modules ([^)]*)\)", dune)
    if not m or "mir_return_summary" not in m.group(1).split():
        fail("Y4: the pli80_hir (modules ...) list does not carry "
             "mir_return_summary")
        return
    ok("Y4 dependency law: mir_return_summary.ml code references no "
       "Target/Diagnostic/Backend/Mir_backend/Rel80/Codegen/Parser/"
       "Semantic_env/Unix/Hir_build/Mir_return_summary name and has no "
       "`open`; the library's (modules ...) list carries it")


# --------------------------------------------------------------------------
# Y5 — the hir_test panel law of the addition
# --------------------------------------------------------------------------

F8_RE = re.compile(
    r"^ok    F8 HIR purity \(no backend/byte-layout vocabulary\): "
    r"(\d+) files clean of 7 patterns \(after nested-comment strip\)$")


def hir_panel_law() -> None:
    """Y5: hir_test rc 0, EXACTLY 220 `ok ` lines, and the diff vs the
    campaign baseline is EXACTLY the F8 file-count line."""
    if not HIR_BASELINE.exists():
        fail(f"Y5: the campaign baseline {HIR_BASELINE.relative_to(REPO)} is "
             f"absent — the HIR panel law is a comparison against the "
             f"pre-extraction log, so it is NOT MEASURED here (never skip it)")
        return
    r = run([sys.executable, HIR_TEST], timeout=900)
    if r.returncode != 0:
        fail(f"Y5 hir_test rc {r.returncode} (expected 0); stderr: "
             f"{r.stderr.decode('utf-8', 'replace')[:400]}")
        return
    log = r.stdout.decode("utf-8", "replace").splitlines()
    n_ok = sum(1 for line in log if line.startswith("ok "))
    if n_ok != 220:
        fail(f"Y5: {n_ok} `ok ` lines, the FROZEN panel constant is 220")
        return
    if any(line.startswith("FAIL") for line in log):
        fail("Y5: the hir log contains a FAIL line despite rc 0")
        return
    base = HIR_BASELINE.read_text().splitlines()
    if len(base) != len(log):
        fail(f"Y5: the hir log has {len(log)} lines, the baseline has "
             f"{len(base)} — the addition must move EXACTLY the F8 line")
        return
    diffs = [(i, b, c) for i, (b, c) in enumerate(zip(base, log), 1) if b != c]
    if len(diffs) != 1:
        fail(f"Y5: {len(diffs)} line(s) differ from the baseline "
             f"{[i for i, _, _ in diffs]} — the only allowed difference is the "
             f"F8 file count")
        return
    i, b_line, c_line = diffs[0]
    mb, mc = F8_RE.match(b_line), F8_RE.match(c_line)
    if not (mb and mc):
        fail(f"Y5: the single differing line {i} is not the F8 purity line; "
             f"baseline {b_line!r} vs current {c_line!r}")
        return
    n_files = len(list((REPO / "ocaml" / "hir").glob("*.ml")))
    if int(mc.group(1)) != n_files:
        fail(f"Y5: the F8 line reports {mc.group(1)} files, the glob "
             f"ocaml/hir/*.ml has {n_files}")
        return
    if int(mb.group(1)) >= n_files:
        fail(f"Y5: the baseline F8 count {mb.group(1)} is not below the "
             f"current {n_files}")
        return
    ok(f"Y5 hir_test rc 0, {n_ok} `ok ` lines (the frozen 220 UNMOVED), and "
       f"the full log differs from the baseline in EXACTLY line {i} — the F8 "
       f"purity glob {mb.group(1)} -> {mc.group(1)} files (the check embeds "
       f"the ocaml/hir/*.ml count; the addition adds mir_return_summary.ml "
       f"+ mirsumtest.ml, both clean of all 7 patterns)")
    note(f"Y5 the byte-identical-log law and the 'new files live in "
         f"ocaml/hir/' law are in DIRECT CONFLICT; the resolution is DISCLOSURE "
         f"of this one-line diff, never hiding the new units in a subdirectory")


# --------------------------------------------------------------------------
# Y6 — the module's two-file structure: the summary cannot move emission
# --------------------------------------------------------------------------

def module_responsibility() -> None:
    """Y6: the module is pure: it never raises, never emits, never writes."""
    if not MODULE.exists():
        fail(f"Y6: {MODULE.relative_to(REPO)} is missing")
        return
    code = MODULE.read_text()
    for pat in [r"\braise\b", r"\bfailwith\b", r"\bprint_", r"\bprerr_",
                r"\bemit\b", r"\boutput\b", r"\bwrite\b"]:
        if re.search(pat, code, flags=re.M):
            fail(f"Y6: the module contains {pat!r} — the module must be "
                 f"pure (no raising, no printing, no emission)")
            return
    # The module must have the summary type and the summaries function.
    if not re.search(r"^type\s+summary\s*=\s*Known\s+of\s+\(int\s*\*\s*int\)\s*\|\s*Unknown", code, re.M):
        fail("Y6: the module does not define the type summary correctly")
        return
    if not re.search(r"^let\s+summaries\s+~maxp\s*", code, re.M):
        fail("Y6: the module does not define the summaries function")
        return
    ok("Y6: the module is pure (no raise/failwith/print/emit/output/write) and "
       "defines the two required types")


def require_tools() -> bool:
    missing = [str(p.relative_to(REPO)) for p in (PLIMIR, MIRSUM) if not p.exists()]
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
    dif_integration()
    n_pins = pin_equivalence()
    dependency_law()
    hir_panel_law()
    module_responsibility()
    if FAILURES:
        print(f"\nMIR-RETURN-SUMMARY PANEL: {len(FAILURES)} FAILURE(S)")
        return 1
    print(f"\nMIR-RETURN-SUMMARY PANEL PASSED: {CHECKS} checks — the module is "
          f"judged by mirsumtest (55 checks, the frozen count) and by three "
          f"corrupt controls whose exact stderr bytes are pinned; the DIF03 "
          f"and DIF04 integrations are rc 0 with the summary; the "
          f"{n_pins} pre-Stage-D committed .mir pins are byte-equal "
          f"(re-measured from the fixtures with the post-Stage-B compiler, "
          f"x2 fresh); the module's "
          f"dependency law is clean; the hir panel is rc 0 with the frozen "
          f"220 and the single disclosed F8 file-count line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
