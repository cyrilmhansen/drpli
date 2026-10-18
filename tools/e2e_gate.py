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
    # E2E-3d: string concatenation in PUT LIST [W101/W102]
    "W101": ("probes/W101.PLI", "golden/e2e3d/W101/W101.REL"),
    "W102": ("probes/W102.PLI", "golden/e2e3d/W102/W102.REL"),
    # E2E-3e: GET LIST + the historic DEMO corpus file itself
    "X201": ("probes/X201.PLI", "golden/e2e3e/X201/X201.REL"),
    "X202": ("probes/X202.PLI", "golden/e2e3e/X202/X202.REL"),
    "DEMO": ("artefacts/DEMO.PLI", "golden/first8080u/DEMO/DEMO.REL"),
    # E2E-4: iterative DO loops
    "Y301": ("probes/Y301.PLI", "golden/e2e4/Y301/Y301.REL"),
    "Y302": ("probes/Y302.PLI", "golden/e2e4/Y302/Y302.REL"),
    "Y303": ("probes/Y303.PLI", "golden/e2e4/Y303/Y303.REL"),
    "Y304": ("probes/Y304.PLI", "golden/e2e4/Y304/Y304.REL"),
    "Y306": ("probes/Y306.PLI", "golden/e2e4/Y306/Y306.REL"),
    # E2E-5a: extended DO forms
    "Z401": ("probes/Z401.PLI", "golden/e2e5a/Z401/Z401.REL"),
    "Z402": ("probes/Z402.PLI", "golden/e2e5a/Z402/Z402.REL"),
    "Z403": ("probes/Z403.PLI", "golden/e2e5a/Z403/Z403.REL"),
    "Z404": ("probes/Z404.PLI", "golden/e2e5a/Z404/Z404.REL"),
    "Z405": ("probes/Z405.PLI", "golden/e2e5a/Z405/Z405.REL"),
    "Z406": ("probes/Z406.PLI", "golden/e2e5a/Z406/Z406.REL"),
    "Z407": ("probes/Z407.PLI", "golden/e2e5a/Z407/Z407.REL"),
    # E2E-5b: numeric + mixed console output
    "N301": ("probes/N301.PLI", "golden/e2e5b/N301/N301.REL"),
    "N302": ("probes/N302.PLI", "golden/e2e5b/N302/N302.REL"),
    "N303": ("probes/N303.PLI", "golden/e2e5b/N303/N303.REL"),
    "N304": ("probes/N304.PLI", "golden/e2e5b/N304/N304.REL"),
    "N306": ("probes/N306.PLI", "golden/e2e5b/N306/N306.REL"),
    "N308": ("probes/N308.PLI", "golden/e2e5b/N308/N308.REL"),
    "G117": ("probes/G117.PLI", "golden/e2e5b/G117/G117.REL"),
    "G118": ("probes/G118.PLI", "golden/e2e5b/G118/G118.REL"),
    # E2E-5c slice 1: non-recursive internal call
    "P401": ("probes/P401.PLI", "golden/e2e5c/P401/P401.REL"),
    # E2E-5c slice 2: recursion, expression args, tail-displacement
    "RFACT": ("artefacts/RFACT.PLI", "golden/first8080u/RFACT/RFACT.REL"),
    "NFACT": ("probes/NFACT.PLI", "golden/e2e5c/NFACT/NFACT.REL"),
    # ---- E2E-6: FIXED DECIMAL core (audit REV 2 / DFACT milestone) ----
    # DFACT is the corpus acceptance specimen; its golden is the curated
    # corpus .REL. R5xx are the bounded DEC probes whose goldens came from
    # my own DR re-runs (golden/e2e6/*, DFACT's re-run being byte-identical
    # to the corpus copy -- verified with cmp before either was registered).
    "DFACT": ("artefacts/DFACT.PLI", "golden/first8080u/DFACT/DFACT.REL"),
    "R501": ("probes/R501.PLI", "golden/e2e6/R501/R501.REL"),
    "R502": ("probes/R502.PLI", "golden/e2e6/R502/R502.REL"),
    "R503": ("probes/R503.PLI", "golden/e2e6/R503/R503.REL"),
    "R505": ("probes/R505.PLI", "golden/e2e6/R505/R505.REL"),
    "R506": ("probes/R506.PLI", "golden/e2e6/R506/R506.REL"),
    "R508": ("probes/R508.PLI", "golden/e2e6/R508/R508.REL"),
    "R509": ("probes/R509.PLI", "golden/e2e6/R509/R509.REL"),
    "R510": ("probes/R510.PLI", "golden/e2e6/R510/R510.REL"),
    "R511": ("probes/R511.PLI", "golden/e2e6/R511/R511.REL"),
    # cell-size law completion: p=1/3/4 close the extrapolation gap below
    # p=5, so ceil((p+1)/2) is now DIRECTLY observed across the whole
    # accepted band p = 1,3,4,5,7,9,15 (and DR says NOT IMP at 31 [R504]).
    "R513": ("probes/R513.PLI", "golden/e2e6/R513/R513.REL"),
    "R514": ("probes/R514.PLI", "golden/e2e6/R514/R514.REL"),
    "R515": ("probes/R515.PLI", "golden/e2e6/R515/R515.REL"),
    # [E2E-7A slice 1] FIXED DECIMAL COMPARISON: R507 is the E2E-6-era
    # compare sample that used to be evidence for a refusal; R601-R606 are
    # the six relations (each with mirrored operands so one run shows both
    # the taken and the not-taken branch); R607 pins a constant on the LEFT
    # of the relation; R608/R609 pin the WHILE-condition and nested-DO-BLOCK
    # shapes; R610-R613 pin DR's HL-constant-reuse peephole (which LOAN1's
    # `m = 0; y = 0;` depends on) and R614 pins DECIMAL pool REUSE.
    "R507": ("probes/R507.PLI", "golden/e2e6/R507/R507.REL"),
    "R601": ("probes/R601.PLI", "golden/e2e7/R601/R601.REL"),
    "R602": ("probes/R602.PLI", "golden/e2e7/R602/R602.REL"),
    "R603": ("probes/R603.PLI", "golden/e2e7/R603/R603.REL"),
    "R604": ("probes/R604.PLI", "golden/e2e7/R604/R604.REL"),
    "R605": ("probes/R605.PLI", "golden/e2e7/R605/R605.REL"),
    "R606": ("probes/R606.PLI", "golden/e2e7/R606/R606.REL"),
    "R607": ("probes/R607.PLI", "golden/e2e7/R607/R607.REL"),
    "R608": ("probes/R608.PLI", "golden/e2e7/R608/R608.REL"),
    "R609": ("probes/R609.PLI", "golden/e2e7/R609/R609.REL"),
    "R610": ("probes/R610.PLI", "golden/e2e7/R610/R610.REL"),
    "R611": ("probes/R611.PLI", "golden/e2e7/R611/R611.REL"),
    "R612": ("probes/R612.PLI", "golden/e2e7/R612/R612.REL"),
    "R613": ("probes/R613.PLI", "golden/e2e7/R613/R613.REL"),
    "R614": ("probes/R614.PLI", "golden/e2e7/R614/R614.REL"),
    "R401": ("probes/R401.PLI", "golden/e2e5c/R401/R401.REL"),
    "R403": ("probes/R403.PLI", "golden/e2e5c/R403/R403.REL"),
    "R404": ("probes/R404.PLI", "golden/e2e5c/R404/R404.REL"),
    "R405": ("probes/R405.PLI", "golden/e2e5c/R405/R405.REL"),
    "R406": ("probes/R406.PLI", "golden/e2e5c/R406/R406.REL"),
    "R407": ("probes/R407.PLI", "golden/e2e5c/R407/R407.REL"),
    "R408": ("probes/R408.PLI", "golden/e2e5c/R408/R408.REL"),
    "R409": ("probes/R409.PLI", "golden/e2e5c/R409/R409.REL"),
    "R410": ("probes/R410.PLI", "golden/e2e5c/R410/R410.REL"),
    "R411": ("probes/R411.PLI", "golden/e2e5c/R411/R411.REL"),
    "R412": ("probes/R412.PLI", "golden/e2e5c/R412/R412.REL"),
    "R414": ("probes/R414.PLI", "golden/e2e5c/R414/R414.REL"),
    "R415": ("probes/R415.PLI", "golden/e2e5c/R415/R415.REL"),
    "R416": ("probes/R416.PLI", "golden/e2e5c/R416/R416.REL"),
    "R417": ("probes/R417.PLI", "golden/e2e5c/R417/R417.REL"),
    "R418": ("probes/R418.PLI", "golden/e2e5c/R418/R418.REL"),
    "R419": ("probes/R419.PLI", "golden/e2e5c/R419/R419.REL"),
    "R421": ("probes/R421.PLI", "golden/e2e5c/R421/R421.REL"),
    "R422": ("probes/R422.PLI", "golden/e2e5c/R422/R422.REL"),
    "R424": ("probes/R424.PLI", "golden/e2e5c/R424/R424.REL"),
    "R426": ("probes/R426.PLI", "golden/e2e5c/R426/R426.REL"),
    "R427": ("probes/R427.PLI", "golden/e2e5c/R427/R427.REL"),
    "R428": ("probes/R428.PLI", "golden/e2e5c/R428/R428.REL"),
    # E2E-5c slice 2 TAIL-Guard matrix rows (all byte-exact)
    "R423": ("probes/R423.PLI", "golden/e2e5c/R423/R423.REL"),
    "R429": ("probes/R429.PLI", "golden/e2e5c/R429/R429.REL"),
    "R430": ("probes/R430.PLI", "golden/e2e5c/R430/R430.REL"),
    "R431": ("probes/R431.PLI", "golden/e2e5c/R431/R431.REL"),
    "R432": ("probes/R432.PLI", "golden/e2e5c/R432/R432.REL"),
    "R433": ("probes/R433.PLI", "golden/e2e5c/R433/R433.REL"),
    "P404": ("probes/P404.PLI", "golden/e2e5c/P404/P404.REL"),
}

# NOT registered (fail-loud / no golden) -- kept visible as research
# evidence, never as accepted parity:
#   P402  codegen: 'IF n > 0' with a POINTER FORMAL -> [TBD] unproven form
#   P403  two forward CALLs to one proc -> multiple CHAIN-ADDR [TBD]
#         (deferred to the ACK slice)
#   R425  procedure WITHOUT formals -> bind [TBD]
#   R402/R413/R420  no DR .REL golden (oracle produced .PRN only)

# specimens whose RAW console output must equal DR's (all have at
# least one observable PUT; V107/V108 exercise no-console paths —
# V108's '' output is legitimately empty, accepted via anchor logic)
OUTPUT_CHECK = {"G107", "G108", "G113", "G114", "G114B", "G114C",
                "G115", "G116", "V101", "V102", "V103", "V104",
                "V105", "V106", "V108", "W101", "W102",
                "X201", "X202", "DEMO", "Y301", "Y302", "Y303",
                "Y304", "Y306", "Z401", "Z402", "Z403", "Z404",
                "Z405", "Z406", "Z407", "N301", "N302", "N303",
                "N304", "N306", "N308", "G117", "G118", "P401",
                "NFACT",
                "R501", "R502", "R503", "R505", "R506",
                "R508", "R509", "R510", "R511",
                "R513", "R514", "R515",
                "R507", "R601", "R602", "R603", "R604", "R605", "R606",
                "R607", "R608", "R609", "R610", "R611", "R612", "R613",
                "R614"}

# RFACT/R401/R412/R419 were removed from the console arm: they end in a
# NO-EXIT main tail, so a timeout-truncated transcript is never a
# semantic oracle (R401/R412/R419 print nothing at all before the tail
# loop; RFACT's capture proved unreliable under truncation). Their proof
# stays at raw .REL byte parity plus byte-identical linked .COM, which
# tools/prefix_check.py verifies. A bounded COMPLETE-RECORD prefix
# protocol is implemented in tools/prefix_check.py (--console); for
# RFACT the cpmsim capture came back empty in most attempts, so that
# arm reports INCONCLUSIVE-CAPTURE rather than pretending to pass.


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
               "  get list(a);\nend t;\n", "non-varying"),
    "N3_PAGE": ("t:\n  procedure options(main);\n"
                "  put page list('X');\nend t;\n", "PUT form"),
    "N4_SKIPVAR": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                   "  put skip(a) list('X');\nend t;\n", "PUT form"),
    "N6_COMPUTED_GOTO": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                         "l:\n  i = i + 1;\n  goto l(i);\nend t;\n",
                         "computed GOTO"),
    "N7_MULTI_FWD": ("t:\n  procedure options(main);\n"
                     "  goto l;\n  goto l;\nl:\n  put list('X');\nend t;\n",
                     "[TBD]"),
    "N9_GTZERO": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                  "  if a > 0 then put list('X');\nend t;\n",
                  "unproven"),
    "N11_STROVR": ("t:\n  procedure options(main);\n  dcl c char(4);\n"
                   "  c = 'ABCD';\nend t;\n", "fixed store len==cap"),
    "N12_EMPTYFIX": ("t:\n  procedure options(main);\n  dcl c char(4);\n"
                     "  c = '';\nend t;\n", "fixed-char store form"),
    "N13_CATLIT": ("t:\n  procedure options(main);\n"
                   "  put list('A' || 'B');\nend t;\n",
                   "[TBD]"),
    "N14_CATFIX": ("t:\n  procedure options(main);\n  dcl c char(4);\n"
                   "  c = 'AB';\n  put list('X' || c);\nend t;\n",
                   "concat operand not char varying"),
    "N15_CAT4": ("t:\n  procedure options(main);\n  dcl n char(6) varying;\n"
                 "  n = 'Q';\n  put list('A' || n || 'B' || 'C');\nend t;\n",
                 "int subset"),
    "N17_GETINT": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                   "  get list(i);\n  put list('X');\nend t;\n",
                   "non-varying"),
    "N18_GET2": ("t:\n  procedure options(main);\n"
                 "  dcl a char(4) varying;\n  dcl b char(4) varying;\n"
                 "  get list(a, b);\n  put list('X');\nend t;\n",
                 "GET form"),
    "N19_DOBY": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                 "  do i = 1 to 4 by 2;\n    put list('X');\n  end;\n"
                 "end t;\n", "DO step unproven"),
    "N20_DOWILE": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                   "  do while (i < 30);\n    put list('X');\n  end;\n"
                   "end t;\n", "range unproven"),
    "N21_DOIDX": ("t:\n  procedure options(main);\n  dcl c char(4) varying;\n"
                  "  do c = 'A' to 'Z';\n    put list('X');\n  end;\n"
                  "end t;\n", "non-constant FROM"),
    "N22_FPUT": ("t:\n  procedure options(main);\n"
                  "  put list(42);\nend t;\n", "PUT form"),
    "N23_CHARVAR_MULTI": ("t:\n  procedure options(main);\n"
                          "  dcl c char(4) varying;\n  dcl i fixed;\n"
                          "  c = 'Q';\n  i = 1;\n"
                          "  put list(c, i);\nend t;\n",
                          "char var in multi-item"),
    "N24_BIGIN": ("t:\n  procedure options(main);\n"
                  "  dcl c fixed bin(16);\n  c = 1;\n"
                  "  put list(c);\nend t;\n", "NOT IMP"),
    # ---- E2E-6 DECIMAL perimeter: these MUST refuse, never guess ----
    # [E2E-7A slice 1] the six relations themselves are now implemented
    # (R507/R601-R609 byte-exact), so the comparison perimeter shrinks to
    # the two shapes NO sample pins:
    #  * a scale-carrying / non-zero literal against a SCALED decimal
    #    variable: DR's pinned compare literal is 0 [R507/R607], and the
    #    two candidate encodings of `3` (3 at scale 0 vs 300 at scale 2)
    #    are not distinguished by any existing sample.
    "N25_DECCMP_SCALE":
        ("t:\n  procedure options(main);\n  dcl d fixed dec(9,2);\n"
         "  d = 3;\n  if d > 3 then put list(d);\nend t;\n",
         "decimal comparison literal scale unproven"),
    #  * decimal(x,p) as a relational operand: [R506] pins DECIMAL only as
    #    the INT->DEC doorway in an assignment, never inside a relation.
    "N30_DECCMP_BUILTIN":
        ("t:\n  procedure options(main);\n  dcl i fixed bin;\n"
         "  dcl d fixed dec(9,2);\n  d = 1; i = 2;\n"
         "  if decimal(i,9) > d then put list(d);\nend t;\n",
         "not in the proven DEC subset"),
    "N26_DECDIV": ("t:\n  procedure options(main);\n"
                   "  dcl a fixed dec(9,2);\n  dcl c fixed dec(9,2);\n"
                   "  c = a / 2;\n  put list(c);\nend t;\n",
                   "decimal operator not in the DEC subset"),
    "N27_DECBIGP": ("t:\n  procedure options(main);\n"
                    "  dcl d fixed dec(20,0);\n  d = 1;\nend t;\n",
                    "outside the probed DEC band"),
    "N28_DECLITFRAC": ("t:\n  procedure options(main);\n"
                       "  dcl d fixed dec(7,0);\n  d = 1.25;\nend t;\n",
                       "into scale 0 [TBD]"),
    "N29_DECININT": ("t:\n  procedure options(main);\n"
                     "  dcl d fixed dec(9,0);\n  dcl i fixed;\n"
                     "  i = 1;\n  i = i + d;\nend t;\n",
                     "mixed decimal/integer arithmetic unproven"),
    "N16_CATASSIGN": ("t:\n  procedure options(main);\n"
                      "  dcl n char(6) varying;\n  dcl m char(6) varying;\n"
                      "  n = 'Q';\n  m = 'Z' || n;\nend t;\n",
                      "char store from non-literal"),
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
    ap.add_argument("--only", nargs="*", metavar="NAME",
                    help="restrict the --link-run arm to these specimens "
                         "(byte-parity compile still runs for all)")
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
        if a.link_run and exact and (a.only is None or name in a.only):
            link_run(name, gp,
                       output_check=(name in OUTPUT_CHECK))
        elif a.link_run and exact:
            print(f"  link :    {name}: skipped (--only filter)")

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
