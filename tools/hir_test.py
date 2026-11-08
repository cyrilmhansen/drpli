#!/usr/bin/env python3
"""tools/hir_test.py — E2E-54/P0 fixture runner for the HIR layer (PLAN §P0.7).

Checks, all judged against MEASURED text (pre-registered §P0.8):

  1. Fixture contract + expected dumps:
     - positive fixture (hir/expected/<name>.txt exists): rc 0, stdout byte-equal
       to the expected dump, stderr EMPTY;
     - negative fixture (hir/expected/<name>.stderr.txt + <name>.rc exist):
       rc equals the pinned value, stdout is ZERO bytes, stderr is byte-equal to
       the pinned text and contains the named diagnostic (F9 negative silence:
       a refusing run never emits partial HIR on stdout).
  2. Determinism (F4): every fixture is run TWICE in two fresh processes and the
     two stdout byte streams must be cmp-equal. (The CLI handles one file per
     process, so "two fresh processes" subsumes the in-process dimension.)
  3. F4 hex-token audit: every dump is scanned for `[0-9a-f]{6,}` address
     shapes; the documented-value allowlist starts EMPTY — any hit is a failure
     unless explicitly adjudicated and listed below.
  4. F7 separation: ocaml/lib/codegen.ml, ocaml/lib/rel80.ml, ocaml/bin/pli80c.ml
     contain ZERO references to Hir/Hir_build/Target/Diagnostic/Backend.
  5. F8 HIR purity: ocaml/hir/*.ml contain ZERO references to Rel80, Codegen,
     bytes_of, op_-prefixed opcode constants, 0x hex literals or 8080 mnemonics;
     `Hir.ty` carries no size/offset field (words verified against stripped code).

E2E-54/P1-b additions (PLAN §P1-b.4, falsifiers S5-S8):

  6. Semantic authority (S6): every POSITIVE fixture additionally runs
     ocaml/_build/default/hir/semtest.exe, which judges the LIVE env against
     bind (never against dump text). Live runs must exit 0 with stdout exactly
     `SEMANTIC-AUTHORITY OK <n> refs / <m> syms` and EMPTY stderr; the
     `--corrupt` control must exit 1 with ZERO stdout and a stderr whose every
     line starts with `SEM-FAIL:` (the tool is not vacuous).
  7. Determinism (S7): semtest also runs TWICE per positive fixture (live and
     corrupt) in fresh processes with byte-identical (rc, stdout, stderr).
  8. F10 Bind-seam audit (S5): after the comment strip, hir_build.ml mentions
     `Bind` ONLY at the cross-library alias line and the single `bind_program`
     call — the exact two lines are pinned; any other occurrence fails.
  9. S8 env independence: after the comment strip, semantic_env.ml contains no
     `\bHir\b` reference (the env is IR-independent). It also rides the F8 glob
     automatically (all ocaml/hir/*.ml).

F7/F8 grep OCaml sources AFTER stripping `(* ... *)` comments (nesting-aware),
because module headers legitimately mention Rel80/Codegen in prose. The stripper
tracks double-quoted strings (with escapes) but not char literals; measured
first-hand that these files contain no `'"'` char literals, so that shortcut is
safe for the current file set (if a future file breaks it, F7/F8 hits would be
reviewed by eye anyway — this tool never edits sources).

Documented exception (recorded in RESULTS.md §P0): the dump string
"order: target address then value" in hir.ml is an evaluation-order phrase in
language terms; no numeric address ever appears in a dump (audited by F4), so
"address" is deliberately NOT an F8 forbidden token.

CLI under test: ocaml/_build/default/hir/pli80hir.exe  (NOT bin/ — E2E-54/P0
F1 remedy: all HIR units + CLI live in the separate `pli80_hir` library dir).

Exit code: 0 only if ALL checks pass; any failure exits 1.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "ocaml" / "_build" / "default" / "hir" / "pli80hir.exe"
SEMTEST = REPO / "ocaml" / "_build" / "default" / "hir" / "semtest.exe"
FIXDIR = REPO / "hir" / "fixtures"
EXPDIR = REPO / "hir" / "expected"

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"ok    {msg}")


# ---------- OCaml nested-comment stripper ----------

def strip_ocaml_comments(src: str) -> str:
    """Remove (* ... *) comments (nesting-aware), preserving line numbers by
    keeping newlines. Double-quoted strings are passed through untouched."""
    out: list[str] = []
    i, n = 0, len(src)
    depth = 0
    in_string = False
    while i < n:
        c = src[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(src[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if depth == 0 and c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if src.startswith("(*", i):
            depth += 1
            i += 2
            continue
        if depth > 0 and src.startswith("*)", i):
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(c)
        elif c == "\n":
            out.append(c)  # keep line numbers for any diagnostic quoting
        else:
            out.append(" ")
        i += 1
    return "".join(out)


# ---------- CLI execution ----------

def run_cli(fixture: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(CLI), str(fixture)],
        capture_output=True,
        timeout=60,
    )


def run_semtest(fixture: Path, corrupt: bool = False) -> subprocess.CompletedProcess:
    argv = [str(SEMTEST)] + (["--corrupt"] if corrupt else []) + [str(fixture)]
    return subprocess.run(argv, capture_output=True, timeout=60)


# stdout of a passing live run is exactly one line of this shape (§P1-b.4)
SEM_OK_RE = re.compile(r"^SEMANTIC-AUTHORITY OK [0-9]+ refs / [0-9]+ syms\n$")


def check_semtest(fixture: Path, name: str) -> None:
    """S6/S7: live semantic-authority checks + the corrupt control."""
    for corrupt in (False, True):
        tag = "corrupt" if corrupt else "live"
        s1 = run_semtest(fixture, corrupt)
        s2 = run_semtest(fixture, corrupt)
        if (s1.returncode, s1.stdout, s1.stderr) != (s2.returncode, s2.stdout, s2.stderr):
            fail(f"{name} semtest/{tag}: non-deterministic across two fresh processes (S7)")
            continue
        if not corrupt:
            if s1.returncode != 0:
                fail(f"{name} semtest/live: rc={s1.returncode} (want 0); stderr={s1.stderr!r}")
            if s1.stderr != b"":
                fail(f"{name} semtest/live: stderr not empty: {s1.stderr!r}")
            if not SEM_OK_RE.match(s1.stdout.decode(errors='replace')):
                fail(f"{name} semtest/live: stdout {s1.stdout!r} is not exactly one "
                     "SEMANTIC-AUTHORITY OK line (S6)")
            else:
                ok(f"{name} semtest/live: rc 0, {s1.stdout.decode().strip()!r}, deterministic")
        else:
            if s1.returncode != 1:
                fail(f"{name} semtest/corrupt: rc={s1.returncode} (want 1) — the wrong-sid "
                     "control must fail loudly, never OK (S6)")
            if s1.stdout != b"":
                fail(f"{name} semtest/corrupt: control emitted {len(s1.stdout)} stdout bytes")
            lines = s1.stderr.decode(errors="replace").splitlines()
            if not lines:
                fail(f"{name} semtest/corrupt: empty stderr — control printed nothing")
            elif not all(ln.startswith("SEM-FAIL:") for ln in lines):
                fail(f"{name} semtest/corrupt: stderr lines not all SEM-FAIL: {lines!r}")
            else:
                ok(f"{name} semtest/corrupt: rc 1, ZERO stdout, {len(lines)} SEM-FAIL line(s) "
                   "(non-vacuity control)")


# ---------- checks 1, 2, 4 (fixtures) ----------

F4_ALLOW = set()  # documented hex-shaped dump values; EMPTY at P0 close


def check_fixtures() -> None:
    fixtures = sorted(FIXDIR.glob("H*.pli"))
    if not fixtures:
        fail("no fixtures found in hir/fixtures/")
        return
    for fx in fixtures:
        name = fx.stem
        exp_dump = EXPDIR / f"{name}.txt"
        exp_err = EXPDIR / f"{name}.stderr.txt"
        exp_rc = EXPDIR / f"{name}.rc"
        # determinism: two fresh processes, cmp-equal streams
        r1 = run_cli(fx)
        r2 = run_cli(fx)
        if (r1.returncode, r1.stdout, r1.stderr) != (r2.returncode, r2.stdout, r2.stderr):
            fail(f"{name}: non-deterministic output across two runs (F4)")
            continue
        if exp_dump.exists():
            expected = exp_dump.read_bytes()
            if r1.returncode != 0:
                fail(f"{name}: positive fixture rc={r1.returncode} (want 0); stderr={r1.stderr!r}")
            if r1.stderr != b"":
                fail(f"{name}: positive fixture emitted stderr: {r1.stderr!r}")
            if r1.stdout != expected:
                fail(f"{name}: stdout differs from {exp_dump.name} (F: expected-dump mismatch)")
            else:
                ok(f"{name}: rc 0, stdout == {exp_dump.name} ({len(expected)} B), stderr empty, deterministic")
            # F4 hex-token audit of the dump text
            for tok in re.findall(r"[0-9a-f]{6,}", r1.stdout.decode()):
                if tok not in F4_ALLOW:
                    fail(f"{name}: dump contains undocumented hex-shaped token {tok!r} (F4)")
            # P1-b §P1-b.4: positive fixtures additionally run the live-env
            # semantic-authority binary and its corrupt control.
            check_semtest(fx, name)
        elif exp_err.exists() and exp_rc.exists():
            want_rc = int(exp_rc.read_text().strip())
            if r1.returncode != want_rc:
                fail(f"{name}: negative fixture rc={r1.returncode}, want {want_rc}")
            if r1.stdout != b"":
                fail(f"{name}: refusing run emitted {len(r1.stdout)} stdout bytes (F9 silence)")
            want_err = exp_err.read_bytes()
            if r1.stderr != want_err:
                fail(f"{name}: stderr differs from {exp_err.name}: got {r1.stderr!r}")
            else:
                diag = want_err.split(b":", 1)[0].decode()
                ok(f"{name}: rc {want_rc}, ZERO stdout, stderr == {exp_err.name} (diagnostic {diag})")
        else:
            fail(f"{name}: no expected file (neither {name}.txt nor {name}.stderr.txt+{name}.rc)")


# ---------- checks 4, 5 (separation greps) ----------

F7_FILES = [
    REPO / "ocaml" / "lib" / "codegen.ml",
    REPO / "ocaml" / "lib" / "rel80.ml",
    REPO / "ocaml" / "bin" / "pli80c.ml",
]
F7_PATTERNS = [r"\bHir\b", r"\bHir_build\b", r"\bTarget\b", r"\bDiagnostic\b", r"\bBackend\b"]

F8_FILES = sorted((REPO / "ocaml" / "hir").glob("*.ml"))
F8_PATTERNS = [
    r"\bRel80\b",
    r"\bCodegen\b",
    r"\bbytes_of\b",
    r"\bop_[a-zA-Z_]+",          # opcode constants (word-anchored: NOT relop_name/top_authority)
    r"0x[0-9a-fA-F]+",           # raw hex opcode literals
    r"\b(MOV|MVI|LXI|DAD|INX|DCX|PCHL|SHLD|LHLD|STA|LDA|CALL|JMP|XCHG|HLT|JNZ|NZ|Z|C|M|P)\b",
    r"\b(size|offset|reloc|pool)\b",  # byte-layout vocabulary (strings included; "address" is the documented exception)
]


def stripped(path: Path) -> str:
    return strip_ocaml_comments(path.read_text())


def check_greps(label: str, files: list[Path], patterns: list[str]) -> None:
    bad = False
    for f in files:
        if not f.exists():
            fail(f"{label}: expected file missing: {f}")
            bad = True
            continue
        text = stripped(f)
        for pat in patterns:
            for m in re.finditer(pat, text):
                ln = text.count("\n", 0, m.start()) + 1
                fail(f"{label}: {f.relative_to(REPO)}:{ln} matches forbidden pattern /{pat}/ (code after comment strip)")
                bad = True
    if not bad:
        ok(f"{label}: {len(files)} files clean of {len(patterns)} patterns (after nested-comment strip)")


# ---------- P1-b seam greps (F10 / S8) ----------

# F10 (S5): the ONLY Bind occurrences allowed in hir_build.ml code are the
# cross-library alias and the single bind_program call — pinned exactly.
F10_WANT = [
    "module Bind = Pli80.Bind",
    "let plan = Bind.bind_program blk in",
]


def check_seam() -> None:
    hb = REPO / "ocaml" / "hir" / "hir_build.ml"
    code = stripped(hb)
    got = sorted(ln.strip() for ln in code.splitlines() if re.search(r"\bBind\b", ln))
    if got != sorted(F10_WANT):
        fail(f"F10 (Bind seam): hir_build.ml code lines mentioning Bind are {got!r}, "
             f"want exactly {sorted(F10_WANT)!r}")
    else:
        ok("F10 (Bind seam): hir_build.ml references Bind only at the alias and the "
           "single bind_program call")
    se = REPO / "ocaml" / "hir" / "semantic_env.ml"
    code2 = stripped(se)
    hits = list(re.finditer(r"\bHir\b", code2))
    if hits:
        for m in hits:
            ln = code2.count("\n", 0, m.start()) + 1
            fail(f"S8 (env independence): ocaml/hir/semantic_env.ml:{ln} matches \\bHir\\b "
                 "in code (after comment strip)")
    else:
        ok("S8 (env independence): semantic_env.ml code is free of \\bHir\\b (comment strip)")


def main() -> int:
    if not CLI.exists():
        print(f"ERROR: CLI not built: {CLI}\n"
              "       run: cd ocaml && eval \"$(opam env)\" && dune build", file=sys.stderr)
        return 2
    if not SEMTEST.exists():
        print(f"ERROR: semtest not built: {SEMTEST}\n"
              "       run: cd ocaml && eval \"$(opam env)\" && dune build", file=sys.stderr)
        return 2
    check_fixtures()
    check_greps("F7 separation (historical backend free of HIR refs)", F7_FILES, F7_PATTERNS)
    check_greps("F8 HIR purity (no backend/byte-layout vocabulary)", F8_FILES, F8_PATTERNS)
    check_seam()
    print()
    if FAILURES:
        print(f"HIR TEST FAILED: {len(FAILURES)} failure(s)")
        return 1
    print("HIR TEST PASSED: fixtures deterministic + F4/F7/F8/F9 + "
          "semtest S6/S7 + F10/S8 seam checks clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
