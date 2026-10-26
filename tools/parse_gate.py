#!/usr/bin/env python3
"""Parser corpus gate (see spec/PERIMETER.md for the classification model):
 - all [S] sources must parse;
 - EXPECTED_REJECT: sources the ORIGINAL compiler rejects AND that our
   compiler-parity grammar also rejects;
 - STANDARD_SUPERSET: [M] sources the compiler rejects but the Subset-G
   standard (and our parser) accept — they MUST keep parsing;
 - [E2E-41/P1a] OPTION_WITNESSES: the FILE-statement option vocabulary is pinned
   against the AST dump itself (bin/pli80tree.exe), so an option cannot be silently
   dropped from an option list again.  These are PARSER witnesses only: nothing here
   claims DR compiles the shape, and every one of them still refuses in codegen
   except the `open file(f) input' / `close file(f)' pair P1b/P1c lowers."""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80parse.exe")
TREE = os.path.join(ROOT, "ocaml/_build/default/bin/pli80tree.exe")

# [E2E-41/P1a] probes/E47?.PLI -- the five option shapes the brief asks the parser to
# keep, plus the two negative shapes.  Each value is the COMPLETE dump the dumper
# must print (exact text, so option ORDER and argument boundaries are pinned too:
# ENVIRONMENT's two keyword arguments survive as a COMMA node of two call-shaped
# expressions, which is what codegen will read F(n)/B(n) out of), or REFUSE for a
# statement whose option has no DR witness.
OPTION_WITNESSES = {
    "E47A.PLI": (
        "  DCL line 3: f\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) INPUT]\n"
        "  L5: FILE-STMT CLOSE file=f opts=[FILE(f)]\n"),
    "E47B.PLI": (
        "  DCL line 3: f\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) STREAM OUTPUT "
        "TITLE('X.DAT')]\n"
        "  L5: FILE-STMT CLOSE file=f opts=[FILE(f)]\n"),
    "E47C.PLI": (
        "  DCL line 3: f\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) KEYED OUTPUT "
        "ENVIRONMENT((comma[(call f[128]), (call b[8000])]))]\n"
        "  L5: FILE-STMT CLOSE file=f opts=[FILE(f)]\n"),
    "E47D.PLI": (
        "  DCL line 3: f\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) UPDATE DIRECT "
        "ENVIRONMENT((call f[128]))]\n"
        "  L5: FILE-STMT CLOSE file=f opts=[FILE(f)]\n"),
    "E47E.PLI": (
        "  DCL line 3: f\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) STREAM PRINT PAGESIZE(24) "
        "LINESIZE(80)]\n"
        "  L5: FILE-STMT CLOSE file=f opts=[FILE(f)]\n"),
    # the BARE file form, which the LANGUAGE MANUAL brackets only for READ and
    # WRITE (`READ [FILE(fname)] INTO(v)' B.21, `WRITE [FILE(fname)] FROM(v)' B.29).
    "E47H.PLI": (
        "  DCL line 3: f\n  DCL line 3: s\n"
        "  L4: FILE-STMT READ file=f opts=[FILE(f) INTO(s)]\n"
        "  L5: FILE-STMT WRITE file=f opts=[FILE(f) FROM(s)]\n"),
    # OPEN and CLOSE do NOT bracket FILE (`OPEN FILE(fname) [file-attributes]' B.17,
    # `CLOSE FILE(fname)' B.5), and the DR side agrees: probes/P080Q.PLI is exactly
    # this program and golden/probe49/P080Q contains no .REL, while its three batch
    # siblings P080O/P080P/P080R each have one.
    "E47I.PLI": "REFUSE",
    # an option word NO DR sample places in a FILE statement: the parser must refuse
    # it, not re-read it as the following statement (which is what it did before
    # [E2E-41/P1a] -- see OPTIONS-AST-BEFORE.txt).
    "E47F.PLI": "REFUSE",
    # GET/PUT keep the old vocabulary on purpose (the EDIT arm eats FROM itself, so a
    # shared widened list would swallow an edit source), and a named GET/PUT still
    # records FILE(f) as an ON option -- defect P0 section 1(b), printed here so the
    # shape is visible instead of rediscovered.
    "E47G.PLI": (
        "  DCL line 3: f\n  DCL line 3: i\n  DCL line 3: s\n"
        "  L4: FILE-STMT OPEN file=f opts=[FILE(f) INPUT]\n"
        "  L5: GET kind=LIST items=2 opts=1 opts[FILE]\n"
        "  L6: PUT kind=LIST items=1 opts=1 opts[FILE]\n"
        "  L7: FILE-STMT READ file=f opts=[FILE(f) INTO(s) KEYTO(i)]\n"),
}


def check_option_witnesses():
    """[E2E-41/P1a] assert the parsed FILE-statement option lists, exactly."""
    fails = 0
    for name in sorted(OPTION_WITNESSES):
        want = OPTION_WITNESSES[name]
        src = os.path.join(ROOT, "probes", name)
        r = subprocess.run([TREE, src], capture_output=True, text=True)
        got = "".join("  " + l + "\n" for l in r.stdout.splitlines())
        if want == "REFUSE":
            if r.returncode == 0:
                print(f"  FAIL {name}: an option with no DR witness PARSED "
                      f"(must be refused loudly)")
                fails += 1
            elif "[TBD]" not in (r.stdout + r.stderr):
                print(f"  FAIL {name}: refused without a [TBD] marker -- a silent "
                      f"parse error is not evidence")
                fails += 1
            else:
                print(f"  ok-  {name}: unrecognised FILE option refused [TBD]")
        elif got != want:
            print(f"  FAIL {name}: AST does not match the pinned option list")
            print("       want: " + want.replace("\n", " | "))
            print("       got:  " + got.replace("\n", " | "))
            fails += 1
        else:
            print(f"  ok*  {name}: options preserved in order with their arguments")
    return fails


EXPECTED_REJECT = {
    "CALL.PLI":  "shipped source defect (dangling '*/ entry constant */')",
    "P023.PLI":  "[C] STRUCTURE keyword (not in Subset G either)",
    "P024.PLI":  "'p->.q' invalid; compiler flags SYNTAX in PASS 2",
    "P052C.PLI": "[M] binary ^ XOR: DR rejects; our parity grammar omits",
    "P052D.PLI": "[M] binary ^ XOR: DR rejects; our parity grammar omits",
    "P066B.PLI": "picture dcl group form + bare (pic) format ref: DR SYNTAX, parser rejects too",
    # [E2E-41/P1a] `open f input; get f list(i); close f;': the manual brackets
    # FILE for GET/PUT/READ/WRITE (B.12/B.20/B.21/B.29) but NOT for OPEN/CLOSE
    # (B.17/B.5, sections 9.5/9.6), and the DR side agrees -- golden/probe49/P080Q
    # holds dir.txt only, no .REL, while P080O/P080P/P080R of the same batch each
    # produced one.  Our grammar refuses the bare OPEN/CLOSE form, so this is
    # parity, not a gap.
    "P080Q.PLI": "bare FILE reference in OPEN/CLOSE: manual brackets FILE only for "
                  "READ/WRITE/GET/PUT; DR left P080Q with no .REL (golden/probe49)",
}

STANDARD_SUPERSET = {
    "P068M.PLI": "[M] short-circuit &: / |: (Subset G 6.2.2.5/6): DR p1-SYNTAX",
    "P066C.PLI": "[M] PICTURE declared type (Subset G 3.2.5): DR p1-SYNTAX",
    "P067D.PLI": "[M] $/_ identifier starts (Subset G 1.1.3): DR SYNTAX",
}

def main():
    if not os.path.exists(EXE):
        print("build first: (cd ocaml && dune build)")
        return 2
    paths = sorted(
        os.path.join(d, f)
        for d in (os.path.join(ROOT, "artefacts"), os.path.join(ROOT, "probes"))
        for f in os.listdir(d) if f.upper().endswith(".PLI")
    )
    fails = 0
    ok = rejected = 0
    for p in paths:
        name = os.path.basename(p)
        if name in OPTION_WITNESSES and OPTION_WITNESSES[name] == "REFUSE":
            continue          # owned by check_option_witnesses below: it MUST refuse
        r = subprocess.run([EXE, p], capture_output=True, text=True)
        parsed = r.returncode == 0
        if name in EXPECTED_REJECT:
            if parsed:
                print(f"  FAIL {name}: should be rejected ({EXPECTED_REJECT[name]})")
                fails += 1
            else:
                rejected += 1
        elif name in STANDARD_SUPERSET:
            if not parsed:
                print(f"  FAIL {name}: superset must parse ({STANDARD_SUPERSET[name]})")
                print("       ", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "")
                fails += 1
            else:
                print(f"  ok*  {name}: {STANDARD_SUPERSET[name]}")
                ok += 1
        else:
            if parsed:
                ok += 1
            else:
                print(f"  FAIL {name}: UNEXPECTED rejection")
                print("       ", (r.stdout or "").strip().splitlines()[-1:])
                fails += 1
    print(f"parse gate: {ok} ok / {rejected} parity-rejects / {fails} FAIL "
          f"of {len(paths)}")
    wfails = check_option_witnesses()
    print(f"file-option witnesses: {len(OPTION_WITNESSES) - wfails} ok / "
          f"{wfails} FAIL of {len(OPTION_WITNESSES)}")
    return 1 if (fails or wfails) else 0

if __name__ == "__main__":
    sys.exit(main())
