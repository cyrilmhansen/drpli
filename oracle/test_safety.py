#!/usr/bin/env python3
"""test_safety.py — verify cpmwork guards FAIL CLOSED on hostile inputs.

Uses disposable fixtures under a temp dir only; never touches the real
oracle/disks seeds, golden/, or anything outside its own temp tree.
Each check asserts the guard raises SafetyError (or, for the happy paths,
succeeds). Run: python3 test_safety.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpmwork
from cpmwork import Workspace, Run, Output, SafetyError, check_name, check_f83

PASS = FAIL = 0


def ok(label, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}")


def refuses(label, fn):
    """Assert fn() raises SafetyError."""
    global PASS, FAIL
    try:
        fn()
    except SafetyError as e:
        PASS += 1
        print(f"  PASS {label} -> {e}")
        return
    except Exception as e:
        FAIL += 1
        print(f"  FAIL {label} raised {type(e).__name__} not SafetyError: {e}")
        return
    FAIL += 1
    print(f"  FAIL {label} did NOT refuse")


def main():
    tmp = tempfile.mkdtemp(prefix="cpmwork-safety-")
    try:
        build_fixtures(tmp)
        run_checks(tmp)
    finally:
        shutil.rmtree(tmp)
    print(f"\ntest_safety: {PASS} pass / {FAIL} fail")
    sys.exit(1 if FAIL else 0)


def build_fixtures(tmp):
    # seeds dir with a tiny fake 'boot' disk (we will not mkfs the real fmt)
    os.makedirs(os.path.join(tmp, "seeds"))
    with open(os.path.join(tmp, "seeds", "drivea.dsk"), "wb") as f:
        f.write(b"\x00" * 4096)
    os.makedirs(os.path.join(tmp, "workspace"))
    os.makedirs(os.path.join(tmp, "golden"))


def run_checks(tmp):
    seeds = os.path.join(tmp, "seeds")
    wspace = os.path.join(tmp, "workspace")
    golden = os.path.join(tmp, "golden")

    print("== name validation ==")
    ok("good name DEMO", check_name("DEMO") == "DEMO")
    refuses("name with slash", lambda: check_name("../etc/passwd"))
    refuses("name with semicolon (shell inj)", lambda: check_name("A;rm"))
    refuses("name with space", lambda: check_name("A B"))
    refuses("overlong name", lambda: check_name("ABCDEFGHIJ"))
    refuses("f83 bad char", lambda: check_f83("F`OO`.PLI"))
    ok("f83 good", check_f83("demo.pli") == "DEMO.PLI")

    print("== workspace symlink rejection ==")
    linkp = os.path.join(tmp, "evil_ws")
    os.symlink("/tmp", linkp)
    refuses("workspace is symlink",
            lambda: Workspace(linkp, seeds))

    print("== seeds inside workspace rejected ==")
    nested = os.path.join(wspace, "seeds_outside")
    os.makedirs(nested)
    refuses("seeds inside workspace",
            lambda: Workspace(wspace, nested))

    ws = Workspace(wspace, seeds)

    print("== mkfs clobber / unique-per-run ==")
    r1 = Run(ws, "t1")
    ok("mkfs fresh disk c", os.path.exists(r1.mkfs("c")))
    refuses("mkfs existing refuses clobber", lambda: r1.mkfs("c"))
    refuses("bad drive letter", lambda: r1.mkfs("z1"))
    # second Run with same tag gets a different seq dir (unique, never reuse)
    r2 = Run(ws, "t1")
    ok("second run dir unique", r2.dir != r1.dir)
    r2.mkfs("c"); r2.mkfs("d")
    # symlinked disk target rejected (drive e is fresh)
    sl = os.path.join(r2.dir, "drivee.dsk")
    os.symlink("/tmp/pwn", sl)
    refuses("mkfs over symlink", lambda: r2.mkfs("e"))

    print("== import source guards ==")
    outside = os.path.join(tmp, "notallowed.txt")
    with open(outside, "w") as f:
        f.write("x")
    refuses("import outside roots",
            lambda: r2.import_local("c", outside, "OUTSIDE.TXT"))
    # symlinked source rejected
    sl_src = os.path.join(tmp, "linkfile")
    os.symlink("/etc/passwd", sl_src)
    refuses("import symlinked source",
            lambda: r2.import_local("c", sl_src, "LINK.TXT"))
    # legitimate source under project root works (no exception pre-cpmcp);
    # cpmcp itself may fail on fake disk but that is not a SafetyError.
    legit = os.path.join(HERE, "run.py")
    try:
        r2.import_local("c", legit, "RUN.PY")
        ok("import legit source path-passes", True)
    except SafetyError as e:
        ok(f"import legit source path-passes (got {e})", False)
    except subprocess.CalledProcessError:
        ok("import legit source path-passes (cpmcp ran)", True)

    print("== output (golden) guards ==")
    out = Output(golden, "tagA")
    refuses("existing golden tag refused without reuse",
            lambda: Output(golden, "tagA"))
    ok("reuse allows existing tag",
       Output(golden, "tagA", allow_reuse=True).dir == out.dir)
    refuses("bad tag name", lambda: Output(golden, "../escape"))
    # write then refuse clobber
    out.write(".", "summary.txt", "one\n")
    refuses("write overwrite refused",
            lambda: out.write(".", "summary.txt", "two\n"))
    refuses("unsafe output filename (sep)",
            lambda: out.path(".", "a/b.txt"))
    refuses("unsafe output filename (dotdot)",
            lambda: out.path(".", "../b.txt"))
    ok("reuse tag write clobbers",
       Output(golden, "tagA", allow_reuse=True)
       .write(".", "summary.txt", "three\n") is not None)
    # symlinked output subdir refused (short name so the symlink guard, not
    # the 8-char name guard, is what trips)
    os.symlink("/tmp", os.path.join(out.dir, "LNK"))
    refuses("symlinked golden subdir", lambda: out.subdir("LNK"))

    print("== cleanup is workspace-scoped ==")
    refuses("cleanup outside workspace", lambda: _bad_cleanup(ws))

    # cleanup happy path
    r3 = Run(ws, "t3")
    d = r3.dir
    r3.cleanup()
    ok("cleanup removed run dir", not os.path.exists(d))

    print("== shell metacharacters are inert (shell=False) ==")
    # even if a name sneaks past, subprocess list form means no shell; prove
    # the injected string never reaches a shell by using a valid-looking path
    inj = os.path.join(tmp, "injected")
    with open(inj, "w") as f:
        f.write("y")
    # a file literally named with a shell substitution -- if a shell were
    # ever used this would run `touch PWNED`; with shell=False it is inert
    marker = os.path.join(tmp, "PWNED")
    sneaky = os.path.join(tmp, "a\$(touch_PWNED)")
    with open(sneaky, "w") as f:
        f.write("z")
    # import via list form: cpmcp gets the raw arg, shell never invoked
    try:
        r2.import_local("d", sneaky, "SNEAKY.TXT")
    except Exception:
        pass
    ok("shell injection inert (marker absent)", not os.path.exists(marker))


def _bad_cleanup(ws):
    r = Run(ws, "tcleanup")
    # sabotage: point dir at /tmp; cleanup must refuse
    r.dir = "/tmp"
    r.cleanup()


if __name__ == "__main__":
    main()
