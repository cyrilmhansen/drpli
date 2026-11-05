#!/usr/bin/env python3
"""Ledger-integrity tests (E2E-52/P3-8 close hardening).

Deliberate falsification of the two protections added after the `0cf0688` ledger-clobber:

  1. the CONTRACT-IDENTITY INVARIANT in tools/coverage_check.py -- the ledger's ID set must
     equal spec/COVERAGE-IDS.txt exactly, so a removed, renamed or substituted contract fails
     even when every surviving row is internally valid;
  2. STATS GATING -- a failed validation never writes spec/census/coverage-stats.json; and
  3. the neutralized tools/coverage_gen.py stub -- nonzero exit, zero file writes; and
  4. that the NORMAL compile-tier gate (tools/e2e_gate.py) runs the strengthened checker in
     its pre-flight and cannot silently bypass it -- proven live: a sandbox whose spec/ is a
     link farm over the real spec/ with ONE ledger row deleted must abort the gate nonzero
     before any specimen compiles (the gate's pre-flight validators run first and exit 1 on
     the first failure, so the sandbox run reads the real tree and writes nothing).

Every mutation happens on temporary copies; the real spec/COVERAGE.tsv, the manifest, the
canonical statistics, goldens and historical evidence are asserted byte-identical after every
negative case.  No compiler, oracle, LINK-80, cpmsim or emulation is involved.

check()-style like tools/test_functional_dashboard.py: plain python3, exit 0 iff all pass.

  usage: python3 tools/test_coverage_integrity.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECK = os.path.join(HERE, "coverage_check.py")
GEN = os.path.join(HERE, "coverage_gen.py")
# NOTE: the gate test deliberately invokes tools/e2e_gate.py THROUGH THE SANDBOX PATH, never
# this file's own directory -- a real-tree gate would resolve ROOT to the valid ledger.
GATE_REL = "tools/e2e_gate.py"
LEDGER = os.path.join(ROOT, "spec/COVERAGE.tsv")
IDSFILE = os.path.join(ROOT, "spec/COVERAGE-IDS.txt")
STATS = os.path.join(ROOT, "spec/census/coverage-stats.json")

FAILURES = []
COUNT = [0]


def check(name, ok, detail=""):
    COUNT[0] += 1
    print("%-58s %s%s" % (name, "PASS" if ok else "FAIL",
                          ("  -- " + detail) if (detail and not ok) else ""))
    if not ok:
        FAILURES.append(name)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(argv, cwd=ROOT, timeout=300):
    return subprocess.run([sys.executable] + argv, capture_output=True,
                          text=True, cwd=cwd, timeout=timeout)


def ledger_lines():
    """(comment_header_lines, column_header_line, row_lines) of the REAL ledger."""
    raw = open(LEDGER).read().split("\n")
    assert raw[-1] == "", "ledger must end with a newline"
    raw = raw[:-1]
    comments = [l for l in raw if l.startswith("#")]
    body = [l for l in raw if not l.startswith("#")]
    return comments, body[0], body[1:]


def write_variant(td, comments, hdr, rows, name="variant.tsv", drop_id=None,
                  replace_id=None, with_id=None, edit=None):
    """Materialize a mutated ledger; returns its path."""
    rows = list(rows)
    if drop_id:
        rows = [r for r in rows if r.split("\t")[0] != drop_id]
    if replace_id:
        old, new, newcat = replace_id
        nr = []
        for r in rows:
            f = r.split("\t")
            if f[0] == old:
                f[0], f[1] = new, newcat
            nr.append("\t".join(f))
        rows = nr
    if with_id:  # append a copy of an existing row under a fresh id (internally valid)
        src = [r for r in rows if r.split("\t")[0] == with_id[0]][0]
        rows.append("\t".join([with_id[1]] + src.split("\t")[1:]))
    if edit:  # (row_id, column_index, new_value) -- content-only change, id untouched
        rid, col, val = edit
        rows = [("\t".join(val if i == col else f
                           for i, f in enumerate(r.split("\t"))))
                if r.split("\t")[0] == rid else r for r in rows]
    path = os.path.join(td, name)
    with open(path, "w") as f:
        f.write("\n".join(comments + [hdr] + rows) + "\n")
    return path


def main():
    comments, hdr, rows = ledger_lines()
    n = len(rows)
    ids_pre = (sha(LEDGER), sha(IDSFILE), sha(STATS))

    # T1: the current repaired ledger validates clean through the normal entry point
    #     (statistics written to a TEMP path -- the canonical snapshot is not this test's to touch).
    with tempfile.TemporaryDirectory() as td:
        r = run([CHECK, "--stats-path", os.path.join(td, "stats.json")])
        check("T1 current ledger passes (rc=0)", r.returncode == 0,
              "rc=%d %s" % (r.returncode, r.stdout[-200:]))
        check("T1 stats written to temp path",
              os.path.exists(os.path.join(td, "stats.json")), "no temp stats file")
        check("T1 ledger row count is the registered 140", "%d rows," % n in r.stdout and n == 140,
              "count=%d out=%r" % (n, r.stdout.splitlines()[:1]))

    # T2: removing one registered contract fails the NORMAL coverage_check entry point,
    #     and the canonical statistics are byte-identical afterwards (no write on failure).
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows, drop_id="COND.ON_ERROR")
        r = run([CHECK, "--tsv", tsv])  # default (canonical) --stats-path: must NOT be written
        check("T2 missing contract fails entry point (rc!=0)", r.returncode != 0, "rc=0")
        check("T2 failure names the identity invariant",
              "MISSING from the ledger" in r.stdout, r.stdout[-200:])
        check("T2 canonical stats untouched by the failure", sha(STATS) == ids_pre[2])

    # T3: renaming an existing ID fails (renamed-away row + unregistered new ID).
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows,
                            replace_id=("COND.REVERT", "COND.REVERT_RENAMED", "COND"))
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T3 renamed contract ID fails (rc!=0)", r.returncode != 0, "rc=0")
        check("T3 both halves of the set difference reported",
              "COND.REVERT is MISSING" in r.stdout and "COND.REVERT_RENAMED is NOT registered"
              in r.stdout, r.stdout[-300:])
        check("T3 temp stats not written on failure",
              not os.path.exists(os.path.join(td, "s.json")))

    # T4: a reduced-ID replacement (the 0cf0688 shape, simulated: header + first 71 rows)
    #     fails even though every surviving row is internally valid.
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows[:71], name="clobber-sim.tsv")
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T4 reduced valid-rows snapshot fails (rc!=0)", r.returncode != 0, "rc=0")
        missing = r.stdout.count("is MISSING from the ledger")
        check("T4 all 69 dropped contracts reported missing", missing == 69,
              "reported missing=%d" % missing)
        check("T4 temp stats not written on failure",
              not os.path.exists(os.path.join(td, "s.json")))

    # T5: SAME row count, one ID substituted with a well-formed unregistered ID of an
    #     existing category (NEG) -- schema-clean, identity-foul.  A pure count assertion
    #     would pass this; the exact set comparison must not.
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows,
                            replace_id=("LEX.CAT_LITERALS", "NEG.SHADOW", "NEG"))
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T5 count-preserving substitution fails (rc!=0)", r.returncode != 0, "rc=0")
        check("T5 fails ONLY on identity, not on row shape",
              "NEG.SHADOW is NOT registered" in r.stdout
              and "malformed" not in r.stdout and "unknown category" not in r.stdout,
              r.stdout[-400:])

    # T6: a legitimate content edit (boundary text) with IDs unchanged passes.
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows,
                            edit=("COND.ON_ERROR", 12,
                                  "boundary reworded by a test: nothing changed scientifically"))
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T6 content edit without ID change passes (rc=0)", r.returncode == 0,
              "rc=%d %s" % (r.returncode, r.stdout[-300:]))

    # T7: an intentional addition passes ONLY with the matching manifest update, and an
    #     unaccompanied addition fails.  (The manifest update is done in a temp copy: the
    #     real manifest changes only via reviewed commits.)
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows,
                            with_id=("PROC.TAIL_RET", "PROC.TEST_ADDED_CONTRACT"))
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T7 addition WITHOUT manifest update fails (rc!=0)", r.returncode != 0, "rc=0")
        ids2 = os.path.join(td, "COVERAGE-IDS.txt")
        with open(ids2, "w") as f:
            f.write(open(IDSFILE).read().rstrip("\n") + "\nPROC.TEST_ADDED_CONTRACT\n")
        r = run([CHECK, "--tsv", tsv, "--ids", ids2, "--stats-path", os.path.join(td, "s.json")])
        check("T7 addition with matching manifest update passes (rc=0)", r.returncode == 0,
              "rc=%d %s" % (r.returncode, r.stdout[-300:]))

    # T8: the neutralized generator refuses, writes nothing, and leaves the ledger untouched.
    pre = sha(LEDGER)
    with tempfile.TemporaryDirectory() as td:
        r = run([GEN], cwd=td)  # run from an unrelated cwd too: the stub must not care
        check("T8 coverage_gen.py exits nonzero", r.returncode != 0, "rc=%d" % r.returncode)
        check("T8 refusal explains the replacement paths",
              "COVERAGE.tsv" in (r.stdout + r.stderr)
              and "coverage_check.py" in (r.stdout + r.stderr), r.stderr[:200])
    check("T8 ledger byte-identical after invoking coverage_gen.py", sha(LEDGER) == pre)
    check("T8 no .new side file created", not os.path.exists(LEDGER + ".new"))
    check("T8 canonical stats byte-identical", sha(STATS) == ids_pre[2])
    gen_src = open(GEN).read()
    import ast
    bad = []
    for node in ast.walk(ast.parse(gen_src)):
        if isinstance(node, ast.Attribute) and node.attr in (
                "replace", "rename", "remove", "unlink", "truncate", "rmtree", "makedirs"):
            bad.append("os." + node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            mode = None
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = kw.value.value
            if mode and any(c in mode for c in "wax"):
                bad.append("open(mode=%r)" % mode)
    check("T8 stub code performs no write/rename/delete operations (AST-scanned)",
          not bad, str(bad))

    # T9: a schema-corrupted row fails and leaves canonical stats untouched.
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows, edit=("IO.PUT_SKIP", 7, "BOGUS_STATUS"))
        r = run([CHECK, "--tsv", tsv])  # canonical --stats-path on purpose
        check("T9 corrupted row fails validation (rc!=0)", r.returncode != 0, "rc=0")
        check("T9 stats publication refused", "canonical statistics NOT written" in r.stdout,
              r.stdout[-200:])
        check("T9 canonical stats byte-identical", sha(STATS) == ids_pre[2])

    # T10: the identity invariant is fail-closed against a missing manifest (it must never
    #      pass vacuously), and duplicate IDs still fail.
    r = run([CHECK, "--ids", os.path.join(tempfile.gettempdir(), "no-such-manifest-%d.txt" % os.getpid()),
             "--stats-path", os.path.join(tempfile.gettempdir(), "t10-unused.json")])
    check("T10 missing manifest fails closed (rc!=0)", r.returncode != 0, "rc=0")
    check("T10 missing manifest names itself", "manifest" in r.stdout and "missing" in r.stdout,
          r.stdout[-200:])
    with tempfile.TemporaryDirectory() as td:
        tsv = write_variant(td, comments, hdr, rows + [rows[5]])  # same id twice
        r = run([CHECK, "--tsv", tsv, "--stats-path", os.path.join(td, "s.json")])
        check("T10 duplicate row (same id) fails (rc!=0)", r.returncode != 0, "rc=0")
        check("T10 duplicate reported", "duplicate id" in r.stdout, r.stdout[-200:])

    # T11: the NORMAL compile-tier gate runs the strengthened checker in its pre-flight and
    #      cannot silently bypass it -- live probe in a link-farm sandbox: spec/COVERAGE.tsv
    #      alone is a real copy with one registered row removed; everything else resolves to
    #      the read-only real tree.  The gate aborts nonzero before compiling anything (its
    #      pre-flight validators are the first thing main() runs and sys.exit(1) on failure),
    #      so the sandbox writes nothing outside the temp directory.
    with tempfile.TemporaryDirectory() as td:
        sbx = os.path.join(td, "repo")
        os.mkdir(sbx)
        for entry in os.listdir(ROOT):
            if entry not in ("spec", ".git"):
                os.symlink(os.path.join(ROOT, entry), os.path.join(sbx, entry))
        specd = os.path.join(sbx, "spec")
        os.mkdir(specd)
        for entry in os.listdir(os.path.join(ROOT, "spec")):
            os.symlink(os.path.join(ROOT, "spec", entry), os.path.join(specd, entry))
        os.unlink(os.path.join(specd, "COVERAGE.tsv"))
        write_variant(td, comments, hdr, rows, drop_id="COND.ON_ERROR", name="x")
        shutil.copyfile(os.path.join(td, "x"), os.path.join(specd, "COVERAGE.tsv"))
        # Invoke the SANDBOXED gate path -- the real tools/e2e_gate.py would resolve ROOT to
        # the real tree and validate the real (valid) ledger, running the whole panel instead
        # of aborting at the pre-flight.
        r = run([os.path.join(sbx, "tools/e2e_gate.py")], cwd=sbx, timeout=600)
        out = r.stdout + r.stderr
        check("T11 gate aborts on a missing contract (rc!=0)", r.returncode != 0,
              "rc=%d tail=%s" % (r.returncode, out[-300:]))
        check("T11 gate reports the coverage panel failure", "coverage panel" in out, out[-300:])
        check("T11 failure is the identity invariant", "MISSING from the ledger" in out,
              out[-300:])
        check("T11 abort happened before any specimen compiled",
              "BYTE-EXACT" not in out and "divergence panel" not in out, out[-300:])
        check("T11 canonical stats byte-identical after the aborted gate", sha(STATS) == ids_pre[2])

    # Final global invariant: the real tree's ledger, manifest and stats never moved.
    check("X1 real ledger, manifest and canonical stats untouched by the whole suite",
          (sha(LEDGER), sha(IDSFILE), sha(STATS)) == ids_pre)

    print("\ntest_coverage_integrity: %d checks, %d failures"
          % (COUNT[0], len(FAILURES)))
    for f in FAILURES:
        print("  FAILED: %s" % f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
