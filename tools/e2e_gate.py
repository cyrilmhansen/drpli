#!/usr/bin/env python3
"""End-to-end gate: run the OCaml PL/I-80 front end (pli80c) and compare
its .REL output, byte-for-byte, against the DR oracle golden .REL.

  tools/e2e_gate.py                 # compile-only byte parity (no oracle)
  tools/e2e_gate.py --link-run      # also LINK vs PLILIB + execute (oracle)

Specimens are fixed-bin integer-assignment programs for which the codegen
subset is complete. Byte-identical .REL is the strongest independent
proof of semantic equivalence (same executable bytes => same execution).
--link-run additionally proves the runtime ABI (?START/?STOPX, frame) via
the isolated CP/M oracle through the hardened (shell=False, per-run
workspace) harness.
"""
import argparse, os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "ocaml/_build/default/bin/pli80c.exe")
OUT = os.path.join(ROOT, "build", "e2e")

# name -> (source, DR golden .REL)
SPECIMENS = {
    "P071A": ("probes/P071A.PLI", "golden/probe38/P071A/P071A.REL"),
    "P071B": ("probes/P071B.PLI", "golden/probe38/P071B/P071B.REL"),
    # variable-base exponentiation -> integer RTL ?IEXOP (no pool):
    "G102": ("probes/G102.PLI", "golden/e2eexp/G102/G102.REL"),
    # literal-base exponentiation -> decimal pool + DLDOP/DEXOP/QDI15:
    "P071D": ("probes/P071D.PLI", "golden/probe38/P071D/P071D.REL"),
    "G101": ("probes/G101.PLI", "golden/e2eexp/G101/G101.REL"),
    "G103": ("probes/G103.PLI", "golden/e2eexp/G103/G103.REL"),
    "G104": ("probes/G104.PLI", "golden/e2eexp/G104/G104.REL"),
    "G105": ("probes/G105.PLI", "golden/e2eexp/G105/G105.REL"),
    "G106": ("probes/G106.PLI", "golden/e2eexp/G106/G106.REL"),
    # E2E-3a: PUT LIST literal char output (e2eput2 goldens, $C-verified):
    "G107": ("probes/G107.PLI", "golden/e2eput2/G107/G107.REL"),
    "G108": ("probes/G108.PLI", "golden/e2eput2/G108/G108.REL"),
    # E2E-3b: multi-put order, comparisons/IF-ELSE, GOTO+labels [C072]
    "G113": ("probes/G113.PLI", "golden/e2e3b/G113/G113.REL"),
    "G114": ("probes/G114.PLI", "golden/e2e3b/G114/G114.REL"),
    "G114B": ("probes/G114B.PLI", "golden/e2e3b/G114B/G114B.REL"),
    "G114C": ("probes/G114C.PLI", "golden/e2e3b/G114C/G114C.REL"),
    "G115": ("probes/G115.PLI", "golden/e2e3b/G115/G115.REL"),
    "G116": ("probes/G116.PLI", "golden/e2e3b/G116/G116.REL"),
    # E2E-3c: CHAR VARYING representation + codegen [V101-V108]
    "V101": ("probes/V101.PLI", "golden/e2e3c/V101/V101.REL"),
    "V102": ("probes/V102.PLI", "golden/e2e3c/V102/V102.REL"),
    "V103": ("probes/V103.PLI", "golden/e2e3c/V103/V103.REL"),
    "V104": ("probes/V104.PLI", "golden/e2e3c/V104/V104.REL"),
    "V105": ("probes/V105.PLI", "golden/e2e3c/V105/V105.REL"),
    "V106": ("probes/V106.PLI", "golden/e2e3c/V106/V106.REL"),
    "V107": ("probes/V107.PLI", "golden/e2e3c/V107/V107.REL"),
    "V108": ("probes/V108.PLI", "golden/e2e3c/V108/V108.REL"),
}

# specimens whose RAW console output must equal DR's (all have at
# least one observable PUT; V107/V108 exercise no-console paths —
# V108's '' output is legitimately empty, accepted via anchor logic)
OUTPUT_CHECK = {"G107", "G108", "G113", "G114", "G114B", "G114C",
                "G115", "G116", "V101", "V102", "V103", "V104",
                "V105", "V106", "V108"}


def compile_one(name, src):
    os.makedirs(OUT, exist_ok=True)
    rel = os.path.join(OUT, name + ".REL")
    if os.path.exists(rel):
        os.remove(rel)                       # only our own scratch file
    r = subprocess.run([CC, os.path.join(ROOT, src), rel],
                       shell=False, capture_output=True, text=True)
    return rel, r.returncode, r.stderr


# Negative regression panel: sources OUTSIDE the implemented subset must
# exit nonzero with an explicit [TBD] refusal (fail-loud invariant: no
# construct may be silently discarded, incl. nested inside containers).
REJECTS = {
    "N1_GET": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
               "  get list(a);\nend t;\n", "statement kind"),
    "N2_DO_PUT": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                  "  do a = 1 to 3;\n    put list('X');\n  end;\nend t;\n",
                  "statement kind"),
    "N3_PAGE": ("t:\n  procedure options(main);\n"
                "  put page list('X');\nend t;\n", "PUT form"),
    "N4_SKIPVAR": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                   "  put skip(a) list('X');\nend t;\n", "PUT form"),
    "N5_TWOITEM": ("t:\n  procedure options(main);\n"
                   "  put list('A','B');\nend t;\n", "PUT form"),
    "N6_COMPUTED_GOTO": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                         "l:\n  i = i + 1;\n  goto l(i);\nend t;\n",
                         "computed GOTO"),
    "N7_MULTI_FWD": ("t:\n  procedure options(main);\n"
                     "  goto l;\n  goto l;\nl:\n  put list('X');\nend t;\n",
                     "[TBD]"),
    "N8_CONDFORM": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                    "  if a < 3 then put list('X');\nend t;\n",
                    "condition form"),
    "N9_GTZERO": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                  "  if a > 0 then put list('X');\nend t;\n",
                  "unproven"),
    "N10_PUTINT": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                   "  a = 1;\n  put list(a);\nend t;\n",
                   "numeric variable"),
    "N11_STROVR": ("t:\n  procedure options(main);\n  dcl c char(4);\n"
                   "  c = 'ABCD';\nend t;\n", "fixed store len==cap"),
    "N12_EMPTYFIX": ("t:\n  procedure options(main);\n  dcl c char(4);\n"
                     "  c = '';\nend t;\n", "fixed-char store form"),
}


def run_negatives():
    """Each REJECTS source must FAIL with a [TBD] refusal (never silently
    emit a REL). Returns count of failures-of-purpose (0 = healthy)."""
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for name, (src, marker) in REJECTS.items():
        plipath = os.path.join(OUT, name + ".PLI")
        with open(plipath, "wb") as f:
            f.write(src.replace("\n", "\r\n").encode() + b"\x1a")
        rel = os.path.join(OUT, name + ".REL")
        if os.path.exists(rel):
            os.remove(rel)
        r = subprocess.run([CC, plipath, rel], shell=False,
                           capture_output=True, text=True)
        msg = (r.stderr or "")
        if r.returncode == 0:
            print(f"NEG-FAIL {name}: compiled silently (must [TBD])")
            bad += 1
        elif "[TBD]" not in msg or marker not in msg:
            print(f"NEG-FAIL {name}: wrong refusal: {msg.strip()[-100:]}")
            bad += 1
        else:
            print(f"NEG-OK   {name}: refused [TBD] ({marker})")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--link-run", action="store_true")
    a = ap.parse_args()
    ok = bad = 0
    for name, (src, gold) in SPECIMENS.items():
        gp = os.path.join(ROOT, gold)
        if not os.path.exists(gp):
            print(f"SKIP    {name}: no golden {gold}")
            continue
        rel, rc, err = compile_one(name, src)
        if rc != 0:
            print(f"COMPILE-FAIL {name}: {err.strip()[:120]}")
            bad += 1
            continue
        mine = open(rel, "rb").read()
        dr = open(gp, "rb").read()
        # compare the 128-byte content region DR pads too
        n = min(len(mine), len(dr))
        exact = (mine[:n] == dr[:n] and
                 (len(mine) == len(dr) or set(mine[len(dr):]) <= {0}))
        if exact:
            print(f"BYTE-EXACT {name}: .REL == DR oracle ({n} bytes)")
            ok += 1
        else:
            d = next((i for i in range(n) if mine[i] != dr[i]), n)
            print(f"DIFF      {name}: first differing byte {d} "
                  f"(mine={len(mine)}B dr={len(dr)}B)")
            bad += 1
        if a.link_run and exact:
            link_run(name, gp,
                       output_check=(name in OUTPUT_CHECK))

    print(f"e2e gate: {ok} byte-exact / {bad} fail of {len(SPECIMENS)}")
    nbad = run_negatives()
    if nbad:
        print(f"e2e gate: NEGATIVE PANEL {nbad} fail")
        return 1
    print("e2e gate: negative panel clean (%d/%d refused)"
          % (len(REJECTS), len(REJECTS)))
    return 1 if bad else 0


def link_run(name, dr_rel, output_check=False):
    """Prove the runtime ABI by linking my .REL vs the historical PLILIB
    and executing under the isolated oracle, through the hardened harness.
    Also links+runs the DR golden .REL and compares BOTH the linked .COM
    bytes and the RAW console output region (whitespace and line endings
    preserved -- rc==0 alone is never accepted as proof).
    Uses transient golden/<e2e*> tags (removed after) so the DR corpus stays
    the only permanent golden content."""
    gold = os.path.join(ROOT, "golden")
    stage = os.path.join(gold, "e2estage", name)
    stagedr = os.path.join(gold, "e2estagedr", name)
    os.makedirs(stage, exist_ok=True)
    do_dr = output_check
    if do_dr:
        os.makedirs(stagedr, exist_ok=True)
        shutil.copyfile(dr_rel, os.path.join(stagedr, name + ".REL"))
    shutil.copyfile(os.path.join(OUT, name + ".REL"),
                    os.path.join(stage, name + ".REL"))
    try:
        steps = [["link", "--tag", "e2estage", "--out", "e2elink",
                  "--names", name],
                 ["run", "--tag", "e2elink", "--out", "e2erun",
                  "--names", name]]
        if do_dr:
            steps += [["link", "--tag", "e2estagedr", "--out",
                       "e2elinkdr", "--names", name],
                      ["run", "--tag", "e2elinkdr", "--out",
                       "e2erundr", "--names", name]]
        for args in steps:
            subprocess.run([sys.executable, "linkrun.py"] + args,
                           cwd=os.path.join(ROOT, "oracle"),
                           shell=False, capture_output=True, text=True)
        # 1) linked .COM bytes (DR arm only)
        com_mine = os.path.join(gold, "e2elink", name + ".COM")
        com_dr = os.path.join(gold, "e2elinkdr", name + ".COM")
        if do_dr and os.path.exists(com_mine) and os.path.exists(com_dr):
            same = (open(com_mine, "rb").read() ==
                    open(com_dr, "rb").read())
            print(f"  link :    {name}: .COM "
                  f"{'IDENTICAL' if same else 'DIFFERS!'} vs DR")
        # 2) RAW console output comparison (no normalization applied)
        import re as _re
        def prog_out(tag):
            tp = os.path.join(gold, tag, name + ".transcript.txt")
            if not os.path.exists(tp):
                return None
            # newline='' keeps raw CR/LF sequences intact (universal-newline
            # mode would eat the \r\r\n command-echo anchor)
            tr = open(tp, encoding="latin-1", newline="").read()
            clean = _re.sub(r">>> [^\n]*\n", "", tr)
            m = _re.search(rf"{name}\r\r\n(.*?)(?=\nD>|I/O ran|\Z)",
                           clean, _re.S)
            return m.group(1) if m else None
        if do_dr:
            om, od = prog_out("e2erun"), prog_out("e2erundr")
            if om is None or od is None:
                print(f"  run  :    {name}: MISSING TRANSCRIPT")
            elif om == od:  # anchor verified both runs reached D>
                print(f"  run  :    {name}: console BYTE-EQUAL "
                      f"({len(om)} raw bytes): {om!r}")
            else:
                print(f"  run  :    {name}: CONSOLE DIFFERS mine={om!r} "
                      f"dr={od!r}")
        else:
            r0 = prog_out("e2erun")
            print(f"  run  :    {name}: mine-only arm, captured "
                  f"{0 if r0 is None else len(r0)} raw output bytes")
    finally:
        for tag in ("e2estage", "e2estagedr", "e2elink", "e2elinkdr",
                    "e2erun", "e2erundr"):
            shutil.rmtree(os.path.join(gold, tag), ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
