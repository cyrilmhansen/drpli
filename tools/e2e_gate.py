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
import argparse, os, subprocess, sys, shutil, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC = os.path.join(ROOT, "ocaml/_build/default/bin/pli80c.exe")
# [E2E-12] Per-PID scratch directory.  This was a fixed path (build/e2e), so two
# overlapping gate runs wrote the SAME <name>.REL / <name>.PLI files and each could
# compare a golden against the other run's freshly-compiled output -- the failure mode
# is a plausible-looking byte-parity result that describes neither run.  I created
# exactly that race by starting a second gate while the first was still in its
# output-check phase, and killed both rather than read their numbers.  A per-PID
# directory makes concurrent runs independent; stale directories are inert scratch, and
# raw `cmp' against the goldens is unaffected.
OUT = os.path.join(ROOT, "build", "e2e-%d" % os.getpid())

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
    # [E2E-7A slice 4] LOAN1: the 4th historical corpus program accepted at
    # RAW .REL byte parity (after DEMO, RFACT, DFACT).  It is the milestone the
    # whole E2E-7 effort was aimed at: PUT SKIP, DEC +/-. */ ÷ comparison, ROUND
    # and numeric GET are all exercised by its own text.
    "LOAN1": ("artefacts/LOAN1.PLI", "golden/first8080u/LOAN1/LOAN1.REL"),
    "R501": ("probes/R501.PLI", "golden/e2e6/R501/R501.REL"),
    "R502": ("probes/R502.PLI", "golden/e2e6/R502/R502.REL"),
    "R503": ("probes/R503.PLI", "golden/e2e6/R503/R503.REL"),
    "R505": ("probes/R505.PLI", "golden/e2e6/R505/R505.REL"),
    "R506": ("probes/R506.PLI", "golden/e2e6/R506/R506.REL"),
    "R508": ("probes/R508.PLI", "golden/e2e6/R508/R508.REL"),
    "R509": ("probes/R509.PLI", "golden/e2e6/R509/R509.REL"),
    "R510": ("probes/R510.PLI", "golden/e2e6/R510/R510.REL"),
    "R511": ("probes/R511.PLI", "golden/e2e6/R511/R511.REL"),
    # [E2E-7A slice 2] R512 (`c = a / 2`) was E2E-6-era evidence for a
    # DIVIDE refusal. Divide is now proven for this shape, so it is a
    # POSITIVE specimen instead -- and the retired negative N26_DECDIV
    # ("decimal divide deferred") now has a byte-exact positive twin.
    "R512": ("probes/R512.PLI", "golden/e2e6/R512/R512.REL"),
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
    # [E2E-7A slice 3] FIXED DECIMAL ROUND (?DROUN): 8 byte-exact
    # specimens.  R813 is LOAN1's own `P = P + round(i*P/1200, 2)` line with
    # LOAN1's own declarations, isolated so the ROUND law is verified in the
    # exact shape LOAN1 needs even though GET still blocks LOAN1 itself.
    # R805/R808/R809/R810/R812 have DR goldens but REFUSE here by design
    # (see the ROUND perimeter in REJECTS) and are deliberately unregistered.
    "R801": ("probes/R801.PLI", "golden/e2e9/R801/R801.REL"),
    "R802": ("probes/R802.PLI", "golden/e2e9/R802/R802.REL"),
    "R803": ("probes/R803.PLI", "golden/e2e9/R803/R803.REL"),
    "R804": ("probes/R804.PLI", "golden/e2e9/R804/R804.REL"),
    "R806": ("probes/R806.PLI", "golden/e2e9/R806/R806.REL"),
    "R807": ("probes/R807.PLI", "golden/e2e9/R807/R807.REL"),
    "R811": ("probes/R811.PLI", "golden/e2e9/R811/R811.REL"),
    "R813": ("probes/R813.PLI", "golden/e2e9/R813/R813.REL"),
    # [E2E-7A slice 4] numeric GET (?QCDOP / ?QCIOP) and MOD-in-condition
    # (?IMDOP zero test).  R901-R907 = GET shapes, R908-R912 = MOD conditions,
    # R913/R914/R915/R917 = GET forms that were negative-panel members until
    # this slice (fixed, fixed binary, char-varying + numeric mixed, and a
    # two-char-varying list).  R916 (GET into FIXED char, which DR stores
    # with ?SSCFS) stays a refusal [N44]; its DR golden is kept as evidence.
    # ------------------------------------------------------------------
    # [E2E-8] PUT EDIT (compiled format lists, ?EDITF/?EDTOV) and DO/BY.
    # R1001-R1010, R1018-R1022: format-table shapes (f/a/skip/page, widths,
    #   replication, pool ordering).  R1011-R1015, R1023-R1028, R1030-R1033:
    #   DO index init/test/increment peepholes (rung ladder vs LXI B, rising
    #   vs falling, forever WITH and WITHOUT BY, variable FROM).  R1035/R1036:
    #   fixed-bin var-minus-var (?IS22N), a hole in the E2E-2 int subset that
    #   this slice's probing exposed.  R1037: the promoted N19_DOBY shape.
    # ------------------------------------------------------------------
    "R1001": ("probes/R1001.PLI", "golden/e2e11/R1001/R1001.REL"),
    "R1002": ("probes/R1002.PLI", "golden/e2e11/R1002/R1002.REL"),
    "R1003": ("probes/R1003.PLI", "golden/e2e11/R1003/R1003.REL"),
    "R1004": ("probes/R1004.PLI", "golden/e2e11/R1004/R1004.REL"),
    "R1005": ("probes/R1005.PLI", "golden/e2e11/R1005/R1005.REL"),
    "R1006": ("probes/R1006.PLI", "golden/e2e11/R1006/R1006.REL"),
    "R1007": ("probes/R1007.PLI", "golden/e2e11/R1007/R1007.REL"),
    "R1008": ("probes/R1008.PLI", "golden/e2e11/R1008/R1008.REL"),
    "R1009": ("probes/R1009.PLI", "golden/e2e11/R1009/R1009.REL"),
    "R1010": ("probes/R1010.PLI", "golden/e2e11/R1010/R1010.REL"),
    "R1011": ("probes/R1011.PLI", "golden/e2e11/R1011/R1011.REL"),
    "R1012": ("probes/R1012.PLI", "golden/e2e11/R1012/R1012.REL"),
    "R1013": ("probes/R1013.PLI", "golden/e2e11/R1013/R1013.REL"),
    "R1014": ("probes/R1014.PLI", "golden/e2e11/R1014/R1014.REL"),
    "R1015": ("probes/R1015.PLI", "golden/e2e11/R1015/R1015.REL"),
    "R1018": ("probes/R1018.PLI", "golden/e2e11/R1018/R1018.REL"),
    "R1019": ("probes/R1019.PLI", "golden/e2e11/R1019/R1019.REL"),
    "R1020": ("probes/R1020.PLI", "golden/e2e11/R1020/R1020.REL"),
    "R1021": ("probes/R1021.PLI", "golden/e2e11/R1021/R1021.REL"),
    "R1022": ("probes/R1022.PLI", "golden/e2e11/R1022/R1022.REL"),
    "R1023": ("probes/R1023.PLI", "golden/e2e11/R1023/R1023.REL"),
    "R1024": ("probes/R1024.PLI", "golden/e2e11/R1024/R1024.REL"),
    "R1025": ("probes/R1025.PLI", "golden/e2e11/R1025/R1025.REL"),
    "R1026": ("probes/R1026.PLI", "golden/e2e11/R1026/R1026.REL"),
    "R1027": ("probes/R1027.PLI", "golden/e2e11/R1027/R1027.REL"),
    "R1028": ("probes/R1028.PLI", "golden/e2e11/R1028/R1028.REL"),
    "R1030": ("probes/R1030.PLI", "golden/e2e11/R1030/R1030.REL"),
    "R1031": ("probes/R1031.PLI", "golden/e2e11/R1031/R1031.REL"),
    "R1032": ("probes/R1032.PLI", "golden/e2e11/R1032/R1032.REL"),
    "R1033": ("probes/R1033.PLI", "golden/e2e11/R1033/R1033.REL"),
    "R1035": ("probes/R1035.PLI", "golden/e2e11/R1035/R1035.REL"),
    "R1036": ("probes/R1036.PLI", "golden/e2e11/R1036/R1036.REL"),
    "R1037": ("probes/R1037.PLI", "golden/e2e11/R1037/R1037.REL"),
    # [E2E-8] the 5th historical corpus program: PUT EDIT + forever-with-BY
    # outer loop + variable-FROM descending inner loop.  Byte-exact.
    "IFACT": ("artefacts/IFACT.PLI", "golden/first8080u/IFACT/IFACT.REL"),
    "R901": ("probes/R901.PLI", "golden/e2e10/R901/R901.REL"),
    "R902": ("probes/R902.PLI", "golden/e2e10/R902/R902.REL"),
    "R903": ("probes/R903.PLI", "golden/e2e10/R903/R903.REL"),
    "R904": ("probes/R904.PLI", "golden/e2e10/R904/R904.REL"),
    "R905": ("probes/R905.PLI", "golden/e2e10/R905/R905.REL"),
    "R906": ("probes/R906.PLI", "golden/e2e10/R906/R906.REL"),
    "R907": ("probes/R907.PLI", "golden/e2e10/R907/R907.REL"),
    "R908": ("probes/R908.PLI", "golden/e2e10/R908/R908.REL"),
    "R909": ("probes/R909.PLI", "golden/e2e10/R909/R909.REL"),
    "R910": ("probes/R910.PLI", "golden/e2e10/R910/R910.REL"),
    "R911": ("probes/R911.PLI", "golden/e2e10/R911/R911.REL"),
    "R912": ("probes/R912.PLI", "golden/e2e10/R912/R912.REL"),
    "R913": ("probes/R913.PLI", "golden/e2e10/R913/R913.REL"),
    "R914": ("probes/R914.PLI", "golden/e2e10/R914/R914.REL"),
    "R915": ("probes/R915.PLI", "golden/e2e10/R915/R915.REL"),
    "R917": ("probes/R917.PLI", "golden/e2e10/R917/R917.REL"),
    "R701": ("probes/R701.PLI", "golden/e2e8/R701/R701.REL"),
    "R702": ("probes/R702.PLI", "golden/e2e8/R702/R702.REL"),
    "R703": ("probes/R703.PLI", "golden/e2e8/R703/R703.REL"),
    "R704": ("probes/R704.PLI", "golden/e2e8/R704/R704.REL"),
    "R705": ("probes/R705.PLI", "golden/e2e8/R705/R705.REL"),
    "R706": ("probes/R706.PLI", "golden/e2e8/R706/R706.REL"),
    "R707": ("probes/R707.PLI", "golden/e2e8/R707/R707.REL"),
    "R708": ("probes/R708.PLI", "golden/e2e8/R708/R708.REL"),
    # R709 NOT REGISTERED: DECIMAL formal parameter [TBD] (see N33)
    "R710": ("probes/R710.PLI", "golden/e2e8/R710/R710.REL"),
    "R711": ("probes/R711.PLI", "golden/e2e8/R711/R711.REL"),
    "R712": ("probes/R712.PLI", "golden/e2e8/R712/R712.REL"),
    "R713": ("probes/R713.PLI", "golden/e2e8/R713/R713.REL"),
    "R714": ("probes/R714.PLI", "golden/e2e8/R714/R714.REL"),
    "R715": ("probes/R715.PLI", "golden/e2e8/R715/R715.REL"),
    "R716": ("probes/R716.PLI", "golden/e2e8/R716/R716.REL"),
    "R717": ("probes/R717.PLI", "golden/e2e8/R717/R717.REL"),
    "R718": ("probes/R718.PLI", "golden/e2e8/R718/R718.REL"),
    "R719": ("probes/R719.PLI", "golden/e2e8/R719/R719.REL"),
    "R720": ("probes/R720.PLI", "golden/e2e8/R720/R720.REL"),
    "R721": ("probes/R721.PLI", "golden/e2e8/R721/R721.REL"),
    "R722": ("probes/R722.PLI", "golden/e2e8/R722/R722.REL"),
    "R723": ("probes/R723.PLI", "golden/e2e8/R723/R723.REL"),
    "R724": ("probes/R724.PLI", "golden/e2e8/R724/R724.REL"),
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
    # ---- [E2E-9 slice 6] multi-argument internal ABI, DEC formals, & ----
    # DECPOLY is the 6th historical corpus program accepted at RAW .REL byte
    # parity (after DEMO, RFACT, DFACT, LOAN1, IFACT).  R2030-R2038 pin the
    # arity-1..4 descriptor-block ABI and FIXED DECIMAL by-reference formals;
    # R2023-R2027 pin counted SKIP, %replace + DO WHILE('1'B) and the
    # AND-conjunction lowering; LONGNAME pins DR's 6-character external name.
    "DECPOLY": ("artefacts/DECPOLY.PLI",
                "golden/first8080u/DECPOLY/DECPOLY.REL"),

    # ---- [E2E-10 step 2] FLOAT BINARY(24) value + lowering surface ----
    # FFACT is the 7th historical corpus program accepted at RAW .REL byte
    # parity (after DEMO, RFACT, DFACT, LOAN1, IFACT, DECPOLY); its .COM and
    # 1415-byte console transcript are also byte-identical to DR's.  R30xx pin
    # the float format, literal conversion, ?FX44* operand-mode suffixes,
    # ?FN40* negation, ?FL40M/?FPRET return path and the recursive float call.
    # See C100-C103.
    "FFACT": ("artefacts/FFACT.PLI", "golden/first8080u/FFACT/FFACT.REL"),
    "R3001": ("e13src/R3001.PLI", "golden/e2e13r/R3001/R3001.REL"),
    "R3003": ("e13src/R3003.PLI", "golden/e2e13r/R3003/R3003.REL"),
    "R3006": ("e13src/R3006.PLI", "golden/e2e13r/R3006/R3006.REL"),
    "R3007": ("e13src/R3007.PLI", "golden/e2e13r/R3007/R3007.REL"),
    "R3008": ("e13src/R3008.PLI", "golden/e2e13r/R3008/R3008.REL"),
    "R3009": ("e13src/R3009.PLI", "golden/e2e13r/R3009/R3009.REL"),
    "R3010": ("e13src/R3010.PLI", "golden/e2e13r/R3010/R3010.REL"),
    "R3011": ("e13src/R3011.PLI", "golden/e2e13r/R3011/R3011.REL"),
    "R3018": ("e13src/R3018.PLI", "golden/e2e13r/R3018/R3018.REL"),
    "R3019": ("e13src/R3019.PLI", "golden/e2e13r/R3019/R3019.REL"),
    "R3020": ("e13src/R3020.PLI", "golden/e2e13r/R3020/R3020.REL"),
    "R3021": ("e13src/R3021.PLI", "golden/e2e13r/R3021/R3021.REL"),
    "R3022": ("e13src/R3022.PLI", "golden/e2e13r/R3022/R3022.REL"),
    "R3023": ("e13src/R3023.PLI", "golden/e2e13r/R3023/R3023.REL"),
    "R3024": ("e13src/R3024.PLI", "golden/e2e13r/R3024/R3024.REL"),
    "R3027": ("e13src/R3027.PLI", "golden/e2e13r/R3027/R3027.REL"),
    "R3030": ("e13src/R3030.PLI", "golden/e2e13r/R3030/R3030.REL"),
    "R3031": ("e13src/R3031.PLI", "golden/e2e13r/R3031/R3031.REL"),
    "R3032": ("e13src/R3032.PLI", "golden/e2e13r/R3032/R3032.REL"),
    "R3033": ("e13src/R3033.PLI", "golden/e2e13r/R3033/R3033.REL"),
    "R3034": ("e13src/R3034.PLI", "golden/e2e13r/R3034/R3034.REL"),
    "R3036": ("e13src/R3036.PLI", "golden/e2e13r/R3036/R3036.REL"),
    "R3042": ("e13src/R3042.PLI", "golden/e2e13r/R3042/R3042.REL"),
    "R3043": ("e13src/R3043.PLI", "golden/e2e13r/R3043/R3043.REL"),
    "R3046": ("e13src/R3046.PLI", "golden/e2e13r/R3046/R3046.REL"),
    "R3051": ("e13src/R3051.PLI", "golden/e2e13r/R3051/R3051.REL"),
    "R3052": ("e13src/R3052.PLI", "golden/e2e13r/R3052/R3052.REL"),
    "R3053": ("e13src/R3053.PLI", "golden/e2e13r/R3053/R3053.REL"),
    "R3054": ("e13src/R3054.PLI", "golden/e2e13r/R3054/R3054.REL"),
    # [E2E-10 step 3] FLOAT conditions, GET, conjunctions and the
    # cell/pointer-formal operand pairs, promoted to byte-exact gate
    # positives (each was refused or wrong before step 3):
    "R3074": ("e13src/R3074.PLI", "golden/e2e13e/R3074/R3074.REL"),
    "R3076": ("e13src/R3076.PLI", "golden/e2e13e/R3076/R3076.REL"),
    "R3077": ("e13src/R3077.PLI", "golden/e2e13e/R3077/R3077.REL"),
    "R3078": ("e13src/R3078.PLI", "golden/e2e13e/R3078/R3078.REL"),
    "R3079": ("e13src/R3079.PLI", "golden/e2e13e/R3079/R3079.REL"),
    "R3080": ("e13src/R3080.PLI", "golden/e2e13e/R3080/R3080.REL"),
    "R3081": ("e13src/R3081.PLI", "golden/e2e13e/R3081/R3081.REL"),
    "R3082": ("e13src/R3082.PLI", "golden/e2e13e/R3082/R3082.REL"),
    "R3083": ("e13src/R3083.PLI", "golden/e2e13e/R3083/R3083.REL"),
    "R3084": ("e13src/R3084.PLI", "golden/e2e13e/R3084/R3084.REL"),
    "R3085": ("e13src/R3085.PLI", "golden/e2e13e/R3085/R3085.REL"),
    "R3086": ("e13src/R3086.PLI", "golden/e2e13e/R3086/R3086.REL"),
    "R3087": ("e13src/R3087.PLI", "golden/e2e13e/R3087/R3087.REL"),
    "R3088": ("e13src/R3088.PLI", "golden/e2e13e/R3088/R3088.REL"),
    "R3089": ("e13src/R3089.PLI", "golden/e2e13e/R3089/R3089.REL"),
    "R3090": ("e13src/R3090.PLI", "golden/e2e13e/R3090/R3090.REL"),
    "R3091": ("e13src/R3091.PLI", "golden/e2e13e/R3091/R3091.REL"),
    "R3093": ("e13src/R3093.PLI", "golden/e2e13e/R3093/R3093.REL"),
    "R3095": ("e13src/R3095.PLI", "golden/e2e13e/R3095/R3095.REL"),
    "R3096": ("e13src/R3096.PLI", "golden/e2e13e/R3096/R3096.REL"),
    "R3097": ("e13src/R3097.PLI", "golden/e2e13e/R3097/R3097.REL"),
    # [E2E-10 step 3] a float expression may reference a variable declared LATER
    # in the same block; DR accepts it and mine matches [R3055].
    "R3055": ("e13src/R3055.PLI", "golden/e2e13e/R3055/R3055.REL"),
    # [E2E-10 step 3b] the formal-storage size law, 1/2/3 formals, FIXED and
    # FLOAT, recursive and not -- the specimens behind C106's correction.
    "R3104": ("e13src/R3104.PLI", "golden/e2e13e/R3104/R3104.REL"),
    "R3094": ("e13src/R3094.PLI", "golden/e2e13e/R3094/R3094.REL"),
    "R3101": ("e13src/R3101.PLI", "golden/e2e13e/R3101/R3101.REL"),
    "R3102": ("e13src/R3102.PLI", "golden/e2e13e/R3102/R3102.REL"),
    "R3098": ("e13src/R3098.PLI", "golden/e2e13e/R3098/R3098.REL"),
    "R3099": ("e13src/R3099.PLI", "golden/e2e13e/R3099/R3099.REL"),
    "R3100": ("e13src/R3100.PLI", "golden/e2e13e/R3100/R3100.REL"),
    "R3035": ("e13src/R3035.PLI", "golden/e2e13d/R3035/R3035.REL"),
    "R3061": ("e13src/R3061.PLI", "golden/e2e13d/R3061/R3061.REL"),
    "R3062": ("e13src/R3062.PLI", "golden/e2e13d/R3062/R3062.REL"),
    "R3063": ("e13src/R3063.PLI", "golden/e2e13d/R3063/R3063.REL"),
    "R3065": ("e13src/R3065.PLI", "golden/e2e13d/R3065/R3065.REL"),
    "R3066": ("e13src/R3066.PLI", "golden/e2e13d/R3066/R3066.REL"),
    "R3070": ("e13src/R3070.PLI", "golden/e2e13d/R3070/R3070.REL"),
    "R3071": ("e13src/R3071.PLI", "golden/e2e13d/R3071/R3071.REL"),
    "R3072": ("e13src/R3072.PLI", "golden/e2e13d/R3072/R3072.REL"),
    "R3073": ("e13src/R3073.PLI", "golden/e2e13d/R3073/R3073.REL"),
    "R3005": ("e13src/R3005.PLI", "golden/e2e13r/R3005/R3005.REL"),
    "R3045": ("e13src/R3045.PLI", "golden/e2e13r/R3045/R3045.REL"),
    # [E2E-11 step 1a] retired N20_DOWILE, verbatim source (see REJECTS note)
    "R3105": ("e13src/R3105.PLI", "golden/e2e11q/R3105/R3105.REL"),
    "E22A02": ("e13src/E22A02.PLI", "golden/e2e11n/E22A02/E22A02.REL"),
    "E22A03": ("e13src/E22A03.PLI", "golden/e2e11n/E22A03/E22A03.REL"),
    "E22A04": ("e13src/E22A04.PLI", "golden/e2e11n/E22A04/E22A04.REL"),
    "E22A05": ("e13src/E22A05.PLI", "golden/e2e11n/E22A05/E22A05.REL"),
    "E22A06": ("e13src/E22A06.PLI", "golden/e2e11n/E22A06/E22A06.REL"),
    "E22A07": ("e13src/E22A07.PLI", "golden/e2e11n/E22A07/E22A07.REL"),
    "E22A08": ("e13src/E22A08.PLI", "golden/e2e11n/E22A08/E22A08.REL"),
    "E22A09": ("e13src/E22A09.PLI", "golden/e2e11n/E22A09/E22A09.REL"),
    "E22A12": ("e13src/E22A12.PLI", "golden/e2e11n/E22A12/E22A12.REL"),
    "E22A16": ("e13src/E22A16.PLI", "golden/e2e11n/E22A16/E22A16.REL"),
    "E22B01": ("e13src/E22B01.PLI", "golden/e2e11n/E22B01/E22B01.REL"),
    "E22B02": ("e13src/E22B02.PLI", "golden/e2e11n/E22B02/E22B02.REL"),
    "E22B03": ("e13src/E22B03.PLI", "golden/e2e11n/E22B03/E22B03.REL"),
    "E22B04": ("e13src/E22B04.PLI", "golden/e2e11n/E22B04/E22B04.REL"),
    "E22B05": ("e13src/E22B05.PLI", "golden/e2e11n/E22B05/E22B05.REL"),
    "E22B08": ("e13src/E22B08.PLI", "golden/e2e11n/E22B08/E22B08.REL"),
    "E23A200": ("e13src/E23A200.PLI", "golden/e2e11p/E23A200/E23A200.REL"),
    "E23G1": ("e13src/E23G1.PLI", "golden/e2e11o/E23G1/E23G1.REL"),
    "E23G2": ("e13src/E23G2.PLI", "golden/e2e11o/E23G2/E23G2.REL"),
    "E23G200": ("e13src/E23G200.PLI", "golden/e2e11p/E23G200/E23G200.REL"),
    "E23G3": ("e13src/E23G3.PLI", "golden/e2e11o/E23G3/E23G3.REL"),
    "E23G4": ("e13src/E23G4.PLI", "golden/e2e11o/E23G4/E23G4.REL"),
    "E23G5": ("e13src/E23G5.PLI", "golden/e2e11o/E23G5/E23G5.REL"),
    "E23G6": ("e13src/E23G6.PLI", "golden/e2e11o/E23G6/E23G6.REL"),
    "E23G7": ("e13src/E23G7.PLI", "golden/e2e11o/E23G7/E23G7.REL"),
    "E23G8": ("e13src/E23G8.PLI", "golden/e2e11o/E23G8/E23G8.REL"),
    "E23L1": ("e13src/E23L1.PLI", "golden/e2e11o/E23L1/E23L1.REL"),
    "E23L2": ("e13src/E23L2.PLI", "golden/e2e11o/E23L2/E23L2.REL"),
    "E23L200": ("e13src/E23L200.PLI", "golden/e2e11p/E23L200/E23L200.REL"),
    "E23L3": ("e13src/E23L3.PLI", "golden/e2e11o/E23L3/E23L3.REL"),
    "E23L4": ("e13src/E23L4.PLI", "golden/e2e11o/E23L4/E23L4.REL"),
    "E23L5": ("e13src/E23L5.PLI", "golden/e2e11o/E23L5/E23L5.REL"),
    "E23L6": ("e13src/E23L6.PLI", "golden/e2e11o/E23L6/E23L6.REL"),
    "E23L7": ("e13src/E23L7.PLI", "golden/e2e11o/E23L7/E23L7.REL"),
    "E23L8": ("e13src/E23L8.PLI", "golden/e2e11o/E23L8/E23L8.REL"),
    "E23N1": ("e13src/E23N1.PLI", "golden/e2e11p/E23N1/E23N1.REL"),
    "E23N2": ("e13src/E23N2.PLI", "golden/e2e11p/E23N2/E23N2.REL"),
    "E23N200": ("e13src/E23N200.PLI", "golden/e2e11p/E23N200/E23N200.REL"),
    "E23N3": ("e13src/E23N3.PLI", "golden/e2e11p/E23N3/E23N3.REL"),
    "E23N4": ("e13src/E23N4.PLI", "golden/e2e11p/E23N4/E23N4.REL"),
    "E23N5": ("e13src/E23N5.PLI", "golden/e2e11p/E23N5/E23N5.REL"),
    "E23N6": ("e13src/E23N6.PLI", "golden/e2e11p/E23N6/E23N6.REL"),
    "E23N8": ("e13src/E23N8.PLI", "golden/e2e11p/E23N8/E23N8.REL"),
    "E20A": ("e13src/E20A.PLI", "golden/e2e11l/E20A/E20A.REL"),
    "E21A": ("e13src/E21A.PLI", "golden/e2e11m/E21A/E21A.REL"),
    "E21B": ("e13src/E21B.PLI", "golden/e2e11m/E21B/E21B.REL"),
    # [E2E-11 step 1a-ii] STATIC cells + INITIAL values: DR's single DATA area is
    # [statics][literal pool][automatics] (C114).  E11D is the strongest of these:
    # twelve static bit cells interleaved with automatics and both comparison forms.
    "E20B": ("e13src/E20B.PLI", "golden/e2e11l/E20B/E20B.REL"),
    "E20D": ("e13src/E20D.PLI", "golden/e2e11l/E20D/E20D.REL"),
    "E20E": ("e13src/E20E.PLI", "golden/e2e11l/E20E/E20E.REL"),
    "E11D": ("e13src/E11D.PLI", "golden/e2e11g/E11D/E11D.REL"),
    # [E2E-11 step 1a] DR's zero-elision law (see the N56 retirement note): a
    # literal 0 added or subtracted against a variable disappears, leaving a copy.
    "T5": ("e13src/T5.PLI", "golden/e2e11v/T5/T5.REL"),
    "T6": ("e13src/T6.PLI", "golden/e2e11v/T6/T6.REL"),
    "T7": ("e13src/T7.PLI", "golden/e2e11w/T7/T7.REL"),
    "T8": ("e13src/T8.PLI", "golden/e2e11w/T8/T8.REL"),
    "T9": ("e13src/T9.PLI", "golden/e2e11x/T9/T9.REL"),
    "T10": ("e13src/T10.PLI", "golden/e2e11x/T10/T10.REL"),
    "T12": ("e13src/T12.PLI", "golden/e2e11y/T12/T12.REL"),
    "T13": ("e13src/T13.PLI", "golden/e2e11y/T13/T13.REL"),
    "T4": ("e13src/T4.PLI", "golden/e2e11u/T4/T4.REL"),
    # [E2E-11 step 2] FILE + ON ENDFILE (SYSIN).  FLTPOLY2 is the 10th corpus
    # program and the first that needs a FILE declaration at all; it exercises
    # bit(1) + STATIC INITIAL + %replace + ON ENDFILE + a bare bit condition +
    # SYSIN GET of three float binary(24) items + a PUT LIST + a RETURNS(FLOAT)
    # call, all in one.  golden/first8080u and golden/first hold the same bytes
    # from two independent DR runs, and my fresh e2e11z recompile of the probe
    # copy matched them exactly, so the oracle itself is stable here.
    "FLTPOLY2": ("artefacts/FLTPOLY2.PLI",
                 "golden/first8080u/FLTPOLY2/FLTPOLY2.REL"),
    # the ON-registration probes, now byte-exact: E11A (handler = PUT LIST),
    # E11B (handler = assignment), E11E (plain SYSIN GET, no ON at all -- it is
    # the GET-only control for the same addressing).
    # [E2E-11 step 3] CALL as a STATEMENT, internal procedures.  E24A/E24F/E24J
    # pin the zero-argument form (`call q;` is a bare 3-byte CALL, no descriptor,
    # no auto cell) and the implicit RET that closes every procedure without
    # RETURNS (E25A: an EMPTY body is nothing but that RET).  E25C/E25D/E25G/E25H
    # pin where that RET goes when the body ends in a PUT / another procedure's
    # RETURN / a label / a nested call, and E25G is the one that proves a LABEL
    # definition ends DR's HL-constant reuse.
    "E24A": ("e13src/E24A.PLI", "golden/e2e121/E24A/E24A.REL"),    # [E2E-11 step 3b] pointer-formal stores, comparisons, and the forward-CALL
    # chain.  E25F/E27A are the multi-site chain (2 and 3 forward calls to one
    # procedure): their .REL is byte-exact AND my own linked .COM came out
    # byte-identical to DR's with every operand resolving to the callee entry,
    # which is the check that the RELOC chain -- not just the bits -- is right.
    "E24B": ("e13src/E24B.PLI", "golden/e2e121/E24B/E24B.REL"),
    "E24C": ("e13src/E24C.PLI", "golden/e2e121/E24C/E24C.REL"),
    "E24E": ("e13src/E24E.PLI", "golden/e2e121/E24E/E24E.REL"),
    "E25B": ("e13src/E25B.PLI", "golden/e2e123/E25B/E25B.REL"),
    "E25E": ("e13src/E25E.PLI", "golden/e2e123/E25E/E25E.REL"),
    "E25F": ("e13src/E25F.PLI", "golden/e2e123/E25F/E25F.REL"),
    "E26A": ("e13src/E26A.PLI", "golden/e2e125/E26A/E26A.REL"),
    "E26B": ("e13src/E26B.PLI", "golden/e2e125/E26B/E26B.REL"),
    "E26C": ("e13src/E26C.PLI", "golden/e2e125/E26C/E26C.REL"),
    "E26D": ("e13src/E26D.PLI", "golden/e2e125/E26D/E26D.REL"),
    "E26E": ("e13src/E26E.PLI", "golden/e2e125/E26E/E26E.REL"),
    "E26F": ("e13src/E26F.PLI", "golden/e2e125/E26F/E26F.REL"),
    "E26G": ("e13src/E26G.PLI", "golden/e2e125/E26G/E26G.REL"),
    "E26H": ("e13src/E26H.PLI", "golden/e2e126/E26H/E26H.REL"),
    "E27A": ("e13src/E27A.PLI", "golden/e2e129/E27A/E27A.REL"),
    "E27C": ("e13src/E27C.PLI", "golden/e2e129/E27C/E27C.REL"),    # [E2E-11 step 3c] forwarding a pointer formal as an actual.  DR writes the
    # descriptor word at RUNTIME (LHLD formal / SHLD descriptor) because the value
    # handed to the callee is the address the formal already holds.  E27B is the
    # statement form, E28A the expression form (ex-N54) -- and E28A has an
    # independently computable answer: mid(3,5) = f2(5,3) = 8, so its runtime
    # output checks the forwarding rather than merely matching DR's bytes.
    "E27B": ("e13src/E27B.PLI", "golden/e2e129/E27B/E27B.REL"),
    "E28A": ("e13src/E28A.PLI", "golden/e2e133/E28A/E28A.REL"),    # [E2E-11 step 3c] the two SEMANTIC witnesses for forwarding, both run:
    # E28B's f2 returns a*10+b, so 53 proves the forwarded argument ORDER (a swap
    # gives 35, and E28A's a+b cannot distinguish them at all); E28C mutates b two
    # levels down through a forwarded pointer, so 3 proves the descriptor reaches
    # the ORIGINAL caller's cell (2 would mean the forwarding silently copied).
    "E28B": ("e13src/E28B.PLI", "golden/e2e135/E28B/E28B.REL"),
    "E28C": ("e13src/E28C.PLI", "golden/e2e135/E28C/E28C.REL"),    # [E2E-11 step 3d] DEC/FLOAT stores through a pointer formal: DR's whole
    # change from the ordinary route is the DESTINATION OPCODE -- LXI H becomes
    # LHLD -- because ?DSTOP and ?FX44M already take the address in a register.
    # E26K gf2 is `u = v' with BOTH operands pointer formals.  E28D/E28E are
    # ex-N55 (see the retirement note above).
    "E26J": ("e13src/E26J.PLI", "golden/e2e127/E26J/E26J.REL"),
    "E26K": ("e13src/E26K.PLI", "golden/e2e127/E26K/E26K.REL"),
    "E28D": ("e13src/E28D.PLI", "golden/e2e137/E28D/E28D.REL"),
    "E28E": ("e13src/E28E.PLI", "golden/e2e138/E28E/E28E.REL"),    # [E2E-11 step 4] EXTERNAL ENTRY.  E24G is the minimal statement-position
    # call of an external entry (CHAIN-EXT on the symbol, no EXTDEF, no
    # CHAIN-ADDR); DTEST/FDTEST are the corpus programs, whose acceptance goes
    # further than this panel: linked .COM byte-identity against DR using the
    # RMAC-assembled DIV2/FDIV2 modules, plus executed output (see
    # spec/notes/e2e11-step4-external-entry.md).
    "E24G": ("e13src/E24G.PLI", "golden/e2e121/E24G/E24G.REL"),
    "DTEST": ("artefacts/DTEST.PLI", "golden/e2e141/DTEST/DTEST.REL"),
    "FDTEST": ("artefacts/FDTEST.PLI", "golden/e2e141/FDTEST/FDTEST.REL"),
    # the 1-byte index cell shapes DTEST forced out: XRA A / STA for a zero store
    # (E29A, E29D) and the DO-init form; plus the external-entry statement form.
    "E29A": ("e13src/E29A.PLI", "golden/e2e143/E29A/E29A.REL"),
    "E29D": ("e13src/E29D.PLI", "golden/e2e144/E29D/E29D.REL"),

    "E24F": ("e13src/E24F.PLI", "golden/e2e121/E24F/E24F.REL"),
    "E24J": ("e13src/E24J.PLI", "golden/e2e122/E24J/E24J.REL"),
    "E25A": ("e13src/E25A.PLI", "golden/e2e123/E25A/E25A.REL"),
    "E25C": ("e13src/E25C.PLI", "golden/e2e123/E25C/E25C.REL"),
    "E25D": ("e13src/E25D.PLI", "golden/e2e123/E25D/E25D.REL"),
    "E25G": ("e13src/E25G.PLI", "golden/e2e124/E25G/E25G.REL"),
    "E25H": ("e13src/E25H.PLI", "golden/e2e124/E25H/E25H.REL"),
    "E11A": ("e13src/E11A.PLI", "golden/e2e11g/E11A/E11A.REL"),
    "E11B": ("e13src/E11B.PLI", "golden/e2e11g/E11B/E11B.REL"),
    "E11E": ("e13src/E11E.PLI", "golden/e2e11g/E11E/E11E.REL"),
    "R3004": ("e13src/R3004.PLI", "golden/e2e13/R3004/R3004.REL"),
    "R3012": ("e13src/R3012.PLI", "golden/e2e13/R3012/R3012.REL"),
    "R3014": ("e13src/R3014.PLI", "golden/e2e13/R3014/R3014.REL"),
    "R3049": ("e13src/R3049.PLI", "golden/e2e13/R3049/R3049.REL"),
    "R3050": ("e13src/R3050.PLI", "golden/e2e13/R3050/R3050.REL"),
    # [E2E-10 step 3] the 8th and 9th historical corpus programs, both
    # FLOAT: accepted at RAW .REL byte equality against DR PL/I-80 v1.4.
    "FLTPOLY": ("artefacts/FLTPOLY.PLI", "golden/first8080u/FLTPOLY/FLTPOLY.REL"),
    "TEST": ("artefacts/TEST.PLI", "golden/first8080u/TEST/TEST.REL"),
    "R2023": ("probes/R2023.PLI", "golden/e2e12/R2023/R2023.REL"),
    "R2024": ("probes/R2024.PLI", "golden/e2e12/R2024/R2024.REL"),
    "R2025": ("probes/R2025.PLI", "golden/e2e12/R2025/R2025.REL"),
    "R2026": ("probes/R2026.PLI", "golden/e2e12/R2026/R2026.REL"),
    "R2027": ("probes/R2027.PLI", "golden/e2e12/R2027/R2027.REL"),
    "R2030": ("probes/R2030.PLI", "golden/e2e12/R2030/R2030.REL"),
    "R2031": ("probes/R2031.PLI", "golden/e2e12/R2031/R2031.REL"),
    "R2032": ("probes/R2032.PLI", "golden/e2e12/R2032/R2032.REL"),
    "R2033": ("probes/R2033.PLI", "golden/e2e12/R2033/R2033.REL"),
    "R2034": ("probes/R2034.PLI", "golden/e2e12/R2034/R2034.REL"),
    "R2035": ("probes/R2035.PLI", "golden/e2e12/R2035/R2035.REL"),
    "R2036": ("probes/R2036.PLI", "golden/e2e12/R2036/R2036.REL"),
    "R2037": ("probes/R2037.PLI", "golden/e2e12/R2037/R2037.REL"),
    "R2038": ("probes/R2038.PLI", "golden/e2e12/R2038/R2038.REL"),
    "R725": ("probes/R725.PLI", "golden/e2e8/R725/R725.REL"),
    "LONGNAME": ("probes/LONGNAME.PLI", "golden/e2e12/LONGNAME/LONGNAME.REL"),
}

# [E2E-11 step 5] procedure-only modules (no OPTIONS(MAIN)) -- C136/C137.  Each
# of these is a file whose OUTERMOST block is a procedure that is not the program
# entry point, which DR compiles as an ordinary callable module: no LXI B,0200 /
# CALL ?START, no epilogue CALL ?STOPX, DEF-PUBLIC still present, and
# END-PROGRAM carrying an ABS operand instead of CODE.  Q1-Q9 are the shapes I
# probed with (batch golden/e2e147/e2e148/e2e149); E29*/B are the cross-module
# pairs that give link+run evidence (golden/e2e150d..e2e152d).  Q4/E29H are MAIN
# programs included as controls for the same expressions.
SPECIMENS.update({
    "A":      ("artefacts/A.PLI",       "golden/first/A/A.REL"),
    "Q1":     ("e14src/Q1.PLI",         "golden/e2e148/Q1/Q1.REL"),
    "Q2":     ("e14src/Q2.PLI",         "golden/e2e148/Q2/Q2.REL"),
    "Q3":     ("e14src/Q3.PLI",         "golden/e2e148/Q3/Q3.REL"),
    "Q4":     ("e14src/Q4.PLI",         "golden/e2e147/Q4/Q4.REL"),
    "Q5":     ("e14src/Q5.PLI",         "golden/e2e148/Q5/Q5.REL"),
    "Q6":     ("e14src/Q6.PLI",         "golden/e2e148/Q6/Q6.REL"),
    "Q7":     ("e14src/Q7.PLI",         "golden/e2e148/Q7/Q7.REL"),
    "Q9":     ("e14src/Q9.PLI",         "golden/e2e149/Q9/Q9.REL"),
    "B":      ("e14src/B.PLI",          "golden/e2e152d/B/B.REL"),
    "E29F":   ("e14src/E29F.PLI",       "golden/e2e150d/E29F/E29F.REL"),
    "E29G":   ("e14src/E29G.PLI",       "golden/e2e151d/E29G/E29G.REL"),
    "E29H":   ("e14src/E29H.PLI",       "golden/e2e151d/E29H/E29H.REL"),
    "E29I":   ("e14src/E29I.PLI",       "golden/e2e152d/E29I/E29I.REL"),
    "E29J":   ("e14src/E29J.PLI",       "golden/e2e152d/E29J/E29J.REL"),
})

# [E2E-12] OPTIONS(STACK(n)): the option is ONE bit-packed 16-bit operand in the MAIN
# prologue (`LXI B,dade'), default 0x0200.  Bracketed by eleven DR objects in batches
# golden/e2e160, e2e161, e2e163: the value itself (T2 2000, T3 100, T12 1, T4 65535),
# the DEFAULT when the value is zero (T6 -> 0x0200, not 0), option order (T9), no
# interaction with a nested RECURSIVE procedure's shadow/SVBLK machinery (T15), and
# STACK on a procedure-only MODULE being byte-identical to the same module without it
# (ST7 vs ST11 -- DR drops the option silently, it is not an error).
# KEY NOTE: registered as ST1..ST15, NOT T1..T15.  T4/T6/T7/T9/T12 are already
# specimens from the e2e11u..e2e11y probe series, and a first version of this block
# used the T names: dict.update() silently REPLACED those five entries, so the gate
# would have gone on printing a clean total while five proven byte-parity checks had
# quietly disappeared.  The DR-side artifacts in golden/e2e160..163 keep their original
# T* directory names, so the mapping here is STn -> golden/.../Tn on purpose.
SPECIMENS.update({
    "ST1":     ("e15src/ST1.PLI",  "golden/e2e160/T1/T1.REL"),
    "ST2":     ("e15src/ST2.PLI",  "golden/e2e160/T2/T2.REL"),
    "ST3":     ("e15src/ST3.PLI",  "golden/e2e160/T3/T3.REL"),
    "ST4":     ("e15src/ST4.PLI",  "golden/e2e160/T4/T4.REL"),
    "ST6":     ("e15src/ST6.PLI",  "golden/e2e160/T6/T6.REL"),
    "ST7":     ("e15src/ST7.PLI",  "golden/e2e160/T7/T7.REL"),
    "ST9":     ("e15src/ST9.PLI",  "golden/e2e160/T9/T9.REL"),
    "ST11":    ("e15src/ST11.PLI", "golden/e2e161/T11/T11.REL"),
    "ST12":    ("e15src/ST12.PLI", "golden/e2e161/T12/T12.REL"),
    "ST15":    ("e15src/ST15.PLI", "golden/e2e163/T15/T15.REL"),
    # [E2E-12] V1-V6: the SAME recursive shape as the U probes, but the one whose
    # lowering IS byte-exact (`return (n * f(n-1))', MUL with the call on the right).
    # These carry the RUNTIME evidence that STACK's operand really is the stack: V3
    # (default 512, depth 400) and V6 (stack(600), depth 400) die with DR's
    # `Free Space Overwrite', while V4 (stack(2000), depth 400) completes -- sources
    # identical except the option, mine-built .COM byte-identical to DR-built.
    "V1":     ("e15src/V1.PLI",  "golden/e2e167/V1/V1.REL"),
    "V2":     ("e15src/V2.PLI",  "golden/e2e167/V2/V2.REL"),
    "V3":     ("e15src/V3.PLI",  "golden/e2e168/V3/V3.REL"),
    "V4":     ("e15src/V4.PLI",  "golden/e2e168/V4/V4.REL"),
    "V5":     ("e15src/V5.PLI",  "golden/e2e168/V5/V5.REL"),
    "V6":     ("e15src/V6.PLI",  "golden/e2e168/V6/V6.REL"),
    # Controls for the C139 call-operand guard: both byte-exact, both would have been
    # swept up by a sloppier predicate.
    "W5":     ("e15src/W5.PLI",  "golden/e2e170/W5/W5.REL"),
    "W6":     ("e15src/W6.PLI",  "golden/e2e170/W6/W6.REL"),
})

# [E2E-40/P4] THE MEMBER STORE AND READ ROUTES, PROMOTED TO BYTE-EXACT.
# These seven were carried in spec/DIVERGENT.txt as shape divergences.  Closing [C260]'s two
# class-gated clauses made every one of them byte-for-byte DR's object, so they move to the
# byte-exact panel -- which is the only panel that can say so, because the divergence panel
# FAILS loudly when a row it pins turns out to be identical.
#   E39S1 / E39S2   `g.a = 7; g.b = 9; put list(g.a + g.b)' and its bare-spelling twin: DR's own
#                   pair is byte-identical (C253) and so is mine, which is the invariant that made
#                   resolving qualification in the parser the right call.
#   E39S3           `a + h' (member + ordinary scalar) -- keeps XCHG, i.e. the control that stops
#                   the preservation rule being widened to "either operand is a member".
#   E39S5           nested level-3 structure: [E2E-40/P6] WITHDRAWS the claim written here in P4,
#                   that its CODE matched DR exactly and only DATA differed (6 vs 4).  The code
#                   PAYLOAD matched because a member address never appears in it -- the offsets live
#                   in the RELOC records, which a raw byte comparison of the code section cannot see.
#                   DR fixed up DATA+0x0 / 0x2; mine fixed up 0x2 / 0x4.  The frame was 2 bytes too
#                   large BECAUSE every nested member was at the wrong address, which is the
#                   subgroup-layout defect C264, now closed and registered below.
#   E40N1           a member of an ENCLOSING frame read from a nested procedure (C257).
#   E40Q1 / E40Q2   qualified vs disjoint-unqualified spellings of the same layout.
#   E40R1           the specimen whose value is verified by DR's own printed transcript
#                   (`g=        16', spec/RUNTIME.txt) -- byte-exact AND execution-verified.
# E27S12 is deliberately NOT registered here although its .REL is now byte-for-byte DR's (it
# measured 66/66 with 0 differing bytes): it was never on any panel, reaching this episode only as
# a DIVERGENT.txt record.  Its history -- a `my-gap' refusal pin retired by [C256], then code 64 vs
# DR 66, now 66 = 66 -- is recorded in prose and cited as a path in COVERAGE.tsv, which is honest;
# inventing a byte-exact panel entry in the same slice that claims to have closed it is not.
SPECIMENS.update({
    "E39S1":  ("artefacts/E39S1.PLI", "golden/e39a/E39S1/E39S1.REL"),
    "E39S2":  ("artefacts/E39S2.PLI", "golden/e39a/E39S2/E39S2.REL"),
    "E39S3":  ("artefacts/E39S3.PLI", "golden/e39a/E39S3/E39S3.REL"),
    "E40N1":  ("artefacts/E40N1.PLI", "golden/e40a/E40N1/E40N1.REL"),
    "E40Q1":  ("artefacts/E40Q1.PLI", "golden/e40a/E40Q1/E40Q1.REL"),
    "E40Q2":  ("artefacts/E40Q2.PLI", "golden/e40a/E40Q2/E40Q2.REL"),
    "E40R1":  ("artefacts/E40R1.PLI", "golden/e40b/E40R1/E40R1.REL"),
})

# [E2E-40/P6] three more, from the subgroup-layout rule (C264): a level-numbered item that HAS
# children reserves nothing, the running offset advances only by leaf sizes, and children start at
# the group's own offset.  Before the rule E39S5 fixed up DATA+0x2/0x4 where DR fixes up 0x0/0x2 --
# same code bytes, different addresses -- and its frame was 6 where DR's listing says 4.
#   E39S5  `1 g, 2 h, 3 a fixed, 2 b fixed'      DR DATA 4   -> 256/256 bytes identical
#   E40S1  `1 g, 2 h, 3 a fixed'  (group LAST)   DR DATA 2   -> identical.  Isolates the group's own
#          phantom cell from any level-3 -> level-2 sibling transition.
#   E40S3  `1 g, 2 h, 3 i, 4 a fixed, 2 b fixed' DR DATA 4   -> identical.  Proves the rule is "has
#          children", not "level = 3".
# E40S2 / E40S4 (two children, and a leaf before the group: both DR DATA 6 with members at 0/2/4)
# get DIVERGENT.txt rows instead: their LAYOUT is right but their code is 0x43 vs DR's 0x44, on
# `XCHG' where DR uses `PUSH H' for the second ADD of a three-term sum.  **[E2E-40/P7] CORRECTS
# what this note used to say -- that this was "the same residual E39S7 already pins".  It is not:
# E39S7 was about how a value is WRITTEN to a member (store route, now closed byte-exact), while
# E40S2/E40S4 are about how an ADDEND is PRESERVED (operand route), in a program whose stores are
# all literals and which therefore never reaches the store route at all.  E41P1/P3/P4 pass while
# E40S2/S4 stay divergent on the same build, which is the direct evidence that they are separate
# questions; a common policy is plausible and unproven.  [C261]'s both-operands-are-members
# predicate is still too narrow, and the real discriminator is unmeasured.
#   **[E2E-40/P9] CLOSED, and it was neither of the two readings on offer.**  Seven initial DR probes
#   (golden/e45; predictions for those seven written and committed before DR saw any of them),
#   followed by the eighth, E45S8 -- whose prediction is an ADDENDUM to that file, written before DR
#   saw E45S8 but after the first oracle run -- show the discriminator is the CLASS OF THE RIGHT
#   OPERAND: DR parks the left operand
#   with PUSH H / POP D exactly when the operand it is about to load into HL is an internal
#   FIXED BIN(<=15) member -- whatever the left operand is.  (ordinary, member) parks with only one
#   member present, so [C260]'s pair reading is refuted; (compound, ordinary) takes XCHG in three
#   independent samples (E45S2/S3/S5, matching MB36 [C150] and D12), so compound-left is refuted.
#   E40S2 and E40S4 are registered byte-exact below; both rows are deleted from DIVERGENT.txt.
# [E2E-40/P9] three-term FIXED ADD and the operand-preservation route.  DR's discriminator is
# the storage class of the RIGHT operand (golden/e45/E45S1..S7, predictions in
# golden/e45/PREDICTIONS.txt written before the oracle ran).  E40S2/E40S4 are DR's own objects
# that pinned this defect for five milestones and are registered here as byte-exact for the first
# time; E45S1 and E45S4 were deliberately never byte-exact on any build, so they are new
# specimens of a fixed defect rather than regressions being covered up.
SPECIMENS.update({
    "E40S2":  ("artefacts/E40S2.PLI", "golden/e40n/E40S2/E40S2.REL"),
    "E40S4":  ("artefacts/E40S4.PLI", "golden/e40n/E40S4/E40S4.REL"),
    "E45S1":  ("artefacts/E45S1.PLI", "golden/e45/E45S1/E45S1.REL"),
    "E45S2":  ("artefacts/E45S2.PLI", "golden/e45/E45S2/E45S2.REL"),
    "E45S3":  ("artefacts/E45S3.PLI", "golden/e45/E45S3/E45S3.REL"),
    "E45S4":  ("artefacts/E45S4.PLI", "golden/e45/E45S4/E45S4.REL"),
    "E45S5":  ("artefacts/E45S5.PLI", "golden/e45/E45S5/E45S5.REL"),
    "E45S7":  ("artefacts/E45S7.PLI", "golden/e45/E45S7/E45S7.REL"),
    # [E2E-40/P9 addendum] the probe that separates the two surviving disjuncts of [C271]: no store
    # follows the ADD at all, so `writes_de' cannot be what makes DR park.  DR parks (PUSH H at 003A)
    # and its .REL is 256/256 identical to this compiler's -> the right operand's class is sufficient.
    "E45S8":  ("artefacts/E45S8.PLI", "golden/e45/E45S8/E45S8.REL"),
    # [E2E-40/P10] promoted from the my-gap negative panel.  `put list(a + (b + c))': DR evaluates
    # the PARENTHESIZED right group first and parks ITS sum while it loads `a' -- measured by DR's
    # own expression fixup order (DATA+2, +4, +0 = b, c, a) -- and two things had to be true for my
    # bytes to agree: the width classifier had to see through the parens, and this ADD had to be
    # lowered right-first.  256/256 whole-file identical, and DR's linked object prints 31.
    "E45S6":  ("artefacts/E45S6.PLI", "golden/e45/E45S6/E45S6.REL"),
})

SPECIMENS.update({
    "E39S5":  ("artefacts/E39S5.PLI", "golden/e39a/E39S5/E39S5.REL"),
    "E40S1":  ("artefacts/E40S1.PLI", "golden/e40n/E40S1/E40S1.REL"),
    "E40S3":  ("artefacts/E40S3.PLI", "golden/e40n/E40S3/E40S3.REL"),
})

# [E2E-40/P7] the parked member store (C266): a store whose DESTINATION cell has a fixed DATA
# address takes that address with `LXI H', so the value must be parked -- `PUSH H / LXI H,<cell> /
# POP D / MOV M,E / INX H / MOV M,D' -- while a store to a plain cell ends in `SHLD' even for the
# same expression.  These four probes are the matrix; E39S7 (`a = a + g.b') promoted from the
# divergence panel in the same slice, and E40S2/E40S4 stayed pinned **[closed in P9: the operand-
# route question, not the store question]** (their residual is operand
#   E41P1  `a = b + 1'      member <- biased member.  DR's body is `LHLD b / INX H / PUSH H /
#          LXI H,*(DATA+0) / POP D / MOV M,E / INX H / MOV M,D': the bias belongs to the VALUE and
#          the cell is relocated to its own offset (C165's rule, second witness).  This is also the
#          falsifier for [C260]'s citation of `LHLD;INX H;SHLD': that triple does not occur in any
#          of the 1963 goldens, and DR does not park an ordinary destination here.
#   E41P2  `h = g.a'        ORDINARY scalar <- member read: `LHLD a / SHLD *(h)', no parking.
#          Completes the matrix with E41P4 and shows the rule is keyed on the DESTINATION, not on
#          whether a member is involved at all.  (Its first spelling, `declare 1 g, 2 a fixed,
#          2 b fixed, 1 h fixed', is a DR PASS-1 `STRUCTURE ?' with no .REL: a level-1 sibling
#          cannot follow nested members inside one declaration -- golden/e41p/E41P2/E41P2.PRN.)
#   E41P4  `a = b'          member <- plain member COPY: parked.  With E41P2 adjacent this proves
#          the RHS class does not select the route -- AC1 (`a(3) = b', a variable into an array
#          element) says the same thing for arrays, so the literal-vs-computed split that [C259]
#          called the discriminator at offset 0 was never the whole rule.
#   E41P3  `g.a = 7; g.b = 5; a = a + g.b'   E39S7's shape with BOTH operands initialized, so its
#          console value (12) is an independent arithmetic oracle, which E39S7's own 7 is not:
#          DR never had `b' written there, so `a + g.b' = `a + 0' and the ADD is invisible.
SPECIMENS.update({
    # [E2E-40/P7] promoted out of DIVERGENT.txt by the parked-store rule: 52 -> 57 code bytes and
    # now 256/256 identical to DR, fixups included.  Its console value is deliberately NOT on the
    # runtime panel (7 = `a + 0', `b' never written -- E41P3 is that witness instead).
    "E39S7":  ("artefacts/E39S7.PLI", "golden/e39a/E39S7/E39S7.REL"),
    "E41P1":  ("artefacts/E41P1.PLI", "golden/e41p/E41P1/E41P1.REL"),
    "E41P2":  ("artefacts/E41P2.PLI", "golden/e41p/E41P2/E41P2.REL"),
    "E41P3":  ("artefacts/E41P3.PLI", "golden/e41p/E41P3/E41P3.REL"),
    "E41P4":  ("artefacts/E41P4.PLI", "golden/e41p/E41P4/E41P4.REL"),
})

# [E2E-40/P8] The two member-store shapes P7 called "unmeasured" and left falling through to
# SHLD, measured directly.  Both are now 256/256 identical to DR, fixups included.
#   E42P1  `g.a = 5; a = a + 5'   a SELF-UPDATE of a member keeps the ladder AND keeps SHLD:
#          DR's linked image is `LHLD 19F6 / LXI B,0005 / DAD B / SHLD 19F6'.  So C266's
#          destination rule does NOT reach this case -- C165's form-4-before-form-3 precedence
#          does, the same split AC4 (`a(2) = a(2)+5') showed for an array cell.  Console 10.
#   E42P2  `a = 65535'            an out-of-range LITERAL parks: DR's decimal-conversion prefix
#          is followed by `PUSH H / LXI H,<cell> / POP D / MOV M,E / INX H / MOV M,D'.  P7's
#          comment asserted the opposite ("keeps SHLD") from the flag's bookkeeping, never from
#          DR -- C266's "literal vs computed" half needed the qualification that what matters is
#          whether the value came from hl_const IN PLACE, not whether the source text was a
#          literal.  DR's own run of E42P2 then ABORTS (`ERROR (1), Conversion'), because a
#          FIXED BIN(15) cell cannot hold 65535: the range check lives in DR's RUNTIME LIBRARY, not
#          in the code DR emits.  So it IS on the runtime panel -- and that panel turns the apparent
#          contradiction into a check: my object, linked from the byte-identical .REL through the
#          same library, aborts with byte-identical console text, so the row's expected output is an
#          ERROR MESSAGE (see spec/RUNTIME.txt).  Nothing about the bytes alone could have shown
#          either half of that [C267].

# [E2E-41/P1b] the first FILE-statement objects: OPEN / GET LIST / CLOSE of a named
# stream.  P0 measured the shape off 34 DR OPEN blocks (spec/lab-evidence/e2e41-p0/
# OPEN-BLOCKS.txt); these two probes are the byte-exact specimens that turn the measurement
# into a lowering.  The goldens are a FRESH oracle run, because E2E-33/P0 requires a
# specimen to compile, link and run under the CURRENT harness and runtime_check needs a
# .PRN beside the golden -- which golden/probe40/P072H and golden/probe50/P081Q do not
# contain.  Fresh and historical agree byte for byte (cmp of golden/e41p1 against
# golden/probe50 and golden/probe40 is silent, recorded in
# spec/lab-evidence/e2e41-p1/P081Q-REGION.txt), so nothing about the original evidence moved.
SPECIMENS.update({
    "P081Q": ("probes/P081Q.PLI", "golden/e41p1/P081Q/P081Q.REL"),
    "P072H": ("probes/P072H.PLI", "golden/e41p1/P072H/P072H.REL"),
})

# [E2E-41/P2b] the literal-TITLE stream OPEN, byte-exact.  Three witnesses of the
# 29-byte OPEN block: E17B/E18A open `stream title('$1.$1')` (5-byte literal) and
# E16C opens `stream title('E16IN DAT')` (9-byte literal).  These are the ORIGINAL
# E2E-11 oracle objects (golden/e2e11h/i/j, with .PRN beside them); DR's own listing
# puts the OPEN at c 0006 and the following GET at c 0023 -- 29 bytes, independent of
# my decoder.  Whole-file comparisons: E17B/E16C are 640 bytes, E18A 1152 (CODE
# 0x00AC / 0x0095 / 0x0131).  E18A additionally pins FOUR named-file GETs, three
# console PUTs and the DATA reloc of the title at data 0x0000 (pool FIRST, because
# the OPEN precedes the PUTs in source order).  See [C278] and
# spec/notes/e2e41-p2-literal-title-stream-open.md.
SPECIMENS.update({
    "E17B": ("e13src/E17B.PLI", "golden/e2e11i/E17B/E17B.REL"),
    "E16C": ("e13src/E16C.PLI", "golden/e2e11h/E16C/E16C.REL"),
    "E18A": ("e13src/E18A.PLI", "golden/e2e11j/E18A/E18A.REL"),
})
SPECIMENS.update({
    "E42P1":  ("artefacts/E42P1.PLI", "golden/e42p/E42P1/E42P1.REL"),
    "E42P2":  ("artefacts/E42P2.PLI", "golden/e42p/E42P2/E42P2.REL"),
})

# [E2E-40/P8a] THE MEMBER SELF-UPDATE RANGE, MEASURED AT THE MEMBER, AND THE CROSS-SPELLING
# EQUIVALENCE.  E42P1 licensed exactly one bias (+5); P8 then gate-extended the ORDINARY-
# variable window -8..16 to members and refused anything outside it (E42N3).  DR says the
# window was an artifact of which k E22A/E22B happened to sample: the ladder runs across the
# whole in-range addend and the tail stays SHLD.  Every file below is a DR-generated .REL
# compared in full (256 bytes, RELOC included -- [C264]'s rule that a CODE-byte match alone
# proves nothing about the member addresses), and mine is 256/256 identical on all of them.
#   boundaries of the old invented window: -9 (E43L2) and +17 (E43L5) -- both LADDER in DR,
#     both REFUSED by P8's gate, hence the retirement of E42N3 and this batch of specimens.
#   inside the old window, unchanged: -8 (E43L1), -1 (E43L3), +3 (E43L8), +16 (E43L4).
#   the instruction-selection break-even at a member: +3 repeats INX H, +4 switches to
#     LXI B/DAD B (E43L8 vs E43L9) -- [C165]'s |k|<=3 rule transfers.
#   cross-spelling, the Problem A pair: `a = g.a + 5' (E43L6) and `g.a = a + 5' (E43L7), both
#     byte-identical to each other and to E42P1's body -- DR's ladder keys on the CELL, so the
#     classifier's address comparison is right and the textual one P8 used for production was
#     the wrong predicate.  This is the first PROBE (not just an inference from E40Q1/E40Q2)
#     that licenses treating `a' and `g.a' as one cell inside a self-update.
#   literals: E43M1 stores 32768 at a member, byte-identical -- the lower end of the
#     32768..65535 conversion-then-park interval is now measured at a member, not composed
#     from LR7 (array cell) + E42P2 (65535).
#   extremes: E43B1C = +100 (E42N3's shape, now a specimen), E43B5C = +32767 (the largest
#     addend DR can take; LXI B,7FFF).
SPECIMENS.update({
    "E43L1":  ("artefacts/E43L1.PLI", "golden/e43l/E43L1/E43L1.REL"),
    "E43L2":  ("artefacts/E43L2.PLI", "golden/e43l/E43L2/E43L2.REL"),
    "E43L3":  ("artefacts/E43L3.PLI", "golden/e43l/E43L3/E43L3.REL"),
    "E43L4":  ("artefacts/E43L4.PLI", "golden/e43l/E43L4/E43L4.REL"),
    "E43L5":  ("artefacts/E43L5.PLI", "golden/e43l/E43L5/E43L5.REL"),
    "E43L6":  ("artefacts/E43L6.PLI", "golden/e43l/E43L6/E43L6.REL"),
    "E43L7":  ("artefacts/E43L7.PLI", "golden/e43l/E43L7/E43L7.REL"),
    "E43L8":  ("artefacts/E43L8.PLI", "golden/e43l/E43L8/E43L8.REL"),
    "E43L9":  ("artefacts/E43L9.PLI", "golden/e43l/E43L9/E43L9.REL"),
    "E43M1":  ("artefacts/E43M1.PLI", "golden/e43l/E43M1/E43M1.REL"),
    "E43B1C": ("artefacts/E43B1C.PLI", "golden/e43b/E43B1C/E43B1C.REL"),
    "E43B5C": ("artefacts/E43B5C.PLI", "golden/e43b/E43B5C/E43B5C.REL"),
    # +30000: DR links it and prints 30100, so this one is the largest-bias ARITHMETIC witness,
    # not just a byte witness (100 + 30000 fits BIN(15); E43B5C's +32767 would not).
    "E43B7C": ("artefacts/E43B7C.PLI", "golden/e43b/E43B7C/E43B7C.REL"),
    # [E2E-40/P8b] the two ends of the member ladder's addend, plus the ordinary-scalar control.
    # E44B1/E44C1 are byte-identical WITHOUT a code change: the positive literal 32768 fails the
    # ladder arm's `fits t', and DR makes the same choice -- conversion, general subtract, park.
    # E44A1 (-32767, literal in BIN(15)) is the ladder at the last addend DR has been shown to
    # reach, and it is the only one of the three whose run prints a value.
    "E44A1": ("artefacts/E44A1.PLI", "golden/e44/E44A1/E44A1.REL"),
    "E44B1": ("artefacts/E44B1.PLI", "golden/e44/E44B1/E44B1.REL"),
    "E44C1": ("artefacts/E44C1.PLI", "golden/e44/E44C1/E44C1.REL"),
    # [E2E-40/P8b] same statement as E44C1 with g.a = 1 and an extra variable: 256/256 identical too,
    # and its traceback tail (0007 = h's value) is what refuted the "g.a's value" reading of E44C1's.
    "E44D1": ("artefacts/E44D1.PLI", "golden/e44/E44D1/E44D1.REL"),
})

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
                "R512", "R513", "R514", "R515",
                "R507", "R601", "R602", "R603", "R604", "R605", "R606",
                "R607", "R608", "R609", "R610", "R611", "R612", "R613",
                "R614",
                # [E2E-7A slice 2] decimal divide/scale specimens: all
                # terminate with `stop;`, so the transcript is COMPLETE
                # and needs no bounded-prefix protocol.
                "R701",
                "R702",
                "R703",
                "R704",
                "R705",
                "R706",
                "R707",
                "R708",
                "R710",
                "R711",
                "R712",
                "R713",
                "R714",
                "R715",
                "R716",
                "R717",
                "R718",
                "R719",
                "R720",
                "R721",
                "R722",
                "R723",
                "R724",
                # [E2E-7A slice 3] ROUND specimens: all terminate with stop;
                "R801", "R802", "R803", "R804", "R806", "R807", "R811",
                "R813",
                # [E2E-41/P2b] the literal-TITLE stream opens: DR's archived runs of
                # the SAME objects (golden/e2e11iu/E17B, golden/e2e11jr/E18A) are the
                # transcript authority; the link-run arm links both arms from the
                # byte-identical .RELs and compares the RAW consoles.
                "E17B", "E18A",
                # [E2E-7A slice 4] every GET/MOD specimen ends in `stop;',
                # so its console transcript is COMPLETE and is compared
                # byte-for-byte: scripted echo, CR/LF and EOF behaviour all
                # included.
                "R901", "R902", "R903", "R904", "R905", "R906", "R907",
                "R908", "R909", "R910", "R911", "R912", "R913", "R914",
                "R915", "R917",
                # [E2E-7A slice 4] the corpus milestone: LOAN1's transcript is
                # its complete 27-row schedule, prompts included, and it
                # terminates on the scripted EOF, so console bytes are a real
                # oracle (no bounded-prefix protocol needed).
                "LOAN1",
                # [E2E-8] PUT EDIT + DO/BY specimens.  All of these end in
                # `stop;' and therefore have a COMPLETE transcript, except
                # R1030 (forever BY with no exit: its PUT is unreachable, so
                # it prints nothing and is left out of the console arm) and
                # IFACT (no-exit outer loop: verified instead through
                # tools/prefix_check.py --console --facts, a bounded
                # complete-record prefix checked against math.factorial --
                # truncation is never treated as an oracle).
                "R1001", "R1002", "R1003", "R1004", "R1005", "R1006", "R1007", "R1008", "R1009", "R1010", "R1011", "R1012", "R1013", "R1014", "R1015", "R1018", "R1019", "R1020", "R1021", "R1022", "R1023", "R1024", "R1025", "R1026", "R1027", "R1028", "R1031", "R1032", "R1033", "R1035", "R1036", "R1037"}


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
    # ------------------------------------------------------------------
    # [E2E-7A slice 3] ROUND perimeter.  Each marker is specific enough to
    # notice if the refusal REASON changes, and each shape has a DR golden
    # (golden/e2e9/) except where DR itself rejects the source.
    # ------------------------------------------------------------------
    "N36_ROUND_ONEARG": (
        "t:\n  procedure options(main);\n  dcl a fixed dec(9,3);\n"
        "  dcl y fixed dec(9,2);\n  a = 2.125;\n  y = round(a);\n"
        "  stop;\nend t;\n", "one-argument ROUND"),
    "N37_ROUND_LITERAL": (
        "t:\n  procedure options(main);\n  dcl y fixed dec(9,2);\n"
        "  y = round(2.125, 2);\n  stop;\nend t;\n",
        "ROUND of a bare literal"),
    "N38_ROUND_INTARG": (
        "t:\n  procedure options(main);\n  dcl i fixed;\n"
        "  dcl y fixed dec(9,2);\n  i = 7;\n  y = round(i, 2);\n"
        "  stop;\nend t;\n", "ROUND of a non-DECIMAL"),
    "N39_ROUND_DYNSCALE": (
        "t:\n  procedure options(main);\n  dcl a fixed dec(9,3);\n"
        "  dcl y fixed dec(9,2);\n  dcl n fixed;\n  a = 2.125;\n  n = 2;\n"
        "  y = round(a, n);\n  stop;\nend t;\n", "not an integer literal"),
    "N40_ROUND_SCALE_ABOVE": (
        "t:\n  procedure options(main);\n  dcl a fixed dec(9,3);\n"
        "  dcl y fixed dec(9,6);\n  a = 2.125;\n  y = round(a, 5);\n"
        "  stop;\nend t;\n", "digit count ABOVE the operand scale"),
    "N41_ROUND_SIMPLE_INADD": (
        "t:\n  procedure options(main);\n  dcl p fixed dec(9,2);\n"
        "  dcl a fixed dec(9,3);\n  p = 1;\n  a = 2.125;\n"
        "  p = p + round(a, 2);\n  stop;\nend t;\n",
        "ROUND with a SIMPLE argument inside"),
    "N42_ROUND_INMUL": (
        "t:\n  procedure options(main);\n  dcl p fixed dec(9,2);\n"
        "  dcl a fixed dec(9,3);\n  p = 1;\n  a = 2.125;\n"
        "  p = p * round(a, 2);\n  stop;\nend t;\n",
        "ROUND in a multiplicative"),
    "N43_ROUND_AS_DIVIDEND": (
        "t:\n  procedure options(main);\n  dcl p fixed dec(9,2);\n"
        "  dcl a fixed dec(9,3);\n  dcl b fixed dec(9,2);\n  p = 1;\n"
        "  a = 2.125;\n  b = 2;\n  p = round(a, 2) / b;\n  stop;\nend t;\n",
        "ROUND result as a DECIMAL divide"),
    "N3_PAGE": ("t:\n  procedure options(main);\n"
                "  put page list('X');\nend t;\n", "PUT form"),
    "N4_SKIPVAR": ("t:\n  procedure options(main);\n  dcl a fixed;\n"
                   "  put skip(a) list('X');\nend t;\n", "PUT form"),
    "N6_COMPUTED_GOTO": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                         "l:\n  i = i + 1;\n  goto l(i);\nend t;\n",
                         "computed GOTO"),
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
    # N19_DOBY REMOVED [E2E-8]: `DO i = 1 TO 4 BY 2' is now PROVEN (R1011,
    # R1018, R1037 byte-exact vs fresh DR).  Its perimeter moved to N51
    # (step magnitude above 2, still unsampled).
    # [E2E-11 step 1a] N20_DOWILE RETIRED: it existed because the `< const' arm
    # capped its DCX-repeat ladder at 8 and refused above.  Measuring DR's
    # constant-bias ladder (E23L1..L8/L200, E23G, E23N, E22A/B) showed the real
    # rule -- |bias|<=3 repeats DCX H, >=4 takes LXI B,two's-complement / DAD B,
    # with no upper bound -- so `i < 30' lowers as LHLD/LXI B,FFE2/DAD B exactly
    # as DR emits it.  Its verbatim source is now positive specimen R3105
    # (golden/e2e11q), byte-identical.  Same policy as N63-N66: a negative that
    # DR proves compilable is a bug in my refusal, not a perimeter member.
    # R3105 is compile-tier only: the program never assigns i, so its loop is
    # infinite, which is a runtime property with no bearing on .REL parity.
    "N21_DOIDX": ("t:\n  procedure options(main);\n  dcl c char(4) varying;\n"
                  "  do c = 'A' to 'Z';\n    put list('X');\n  end;\n"
                  "end t;\n", "DO FROM form unproven"),
    "N22_FPUT": ("t:\n  procedure options(main);\n"
                  "  put list(42);\nend t;\n", "PUT form"),
    "N24_BIGIN": ("t:\n  procedure options(main);\n"
                  "  dcl c fixed bin(16);\n  c = 1;\n"
                  # [E2E-11 step 0] marker updated: the refusal now happens in
                  # bind (earliest point the precision is known, and uncondi-
                  # tional -- the old codegen arm only fired on some use paths)
                  # with DR's own wording quoted.  Same policy, better message.
                  "  put list(c);\nend t;\n", "exceeds DR's FIXED precision limit"),
    # ---- [E2E-7A slice 2] DECIMAL divide perimeter.  Divide itself is now
    # implemented (R701-R724 byte-exact), so N26_DECDIV retires; the shapes
    # below are the ones NO sample pins and each must stay a loud refusal.
    "N31_DIV_LITERAL_NUMERATOR":
        ("t:\n  procedure options(main);\n"
         "  dcl a fixed dec(9,2);\n  dcl c fixed dec(9,2);\n"
         "  a = 6;\n  c = 1200 / a;\n  put list(c);\nend t;\n",
         "literal dividend is"),
    "N32_DIV_CHAINED":
        ("t:\n  procedure options(main);\n"
         "  dcl a fixed dec(9,2);\n  dcl b fixed dec(9,2);\n"
         "  dcl c fixed dec(9,2);\n  a = 6; b = 2;\n"
         "  c = a / b / 2;\n  put list(c);\nend t;\n",
         "unpinned dividend precision"),
    "N33_DEC_FORMAL":
        ("t:\n  procedure options(main);\n"
         "  dcl r fixed dec(9,2);\n  r = g(1);\n  put list(r);\n  stop;\n"
         "  g: procedure(x) returns(fixed dec(9,2));\n"
         "     dcl x fixed dec(9,2);\n     return (x);\n  end g;\n"
         "end t;\n",
         "FIXED DECIMAL formal is unproven"),
    # s_r > s_l + N, i.e. a quotient scale BELOW zero.  R712 proves s_r >
    # s_l is fine when the result stays >= 0 (dividend scale 2, divisor
    # product scale 4, N 6 -> scale 4), so the refused region is exactly the
    # negative one, which no sample reaches.
    "N34_DEC_NEGSCALE_DIV":
        ("t:\n  procedure options(main);\n"
         "  dcl a fixed dec(9,0);\n  dcl b fixed dec(9,8);\n"
         "  dcl c fixed dec(9,0);\n  a = 6; b = 2;\n"
         "  c = a / b;\n  put list(c);\nend t;\n",
         "negative scale"),
    "N35_DEC_STORE_SCALE_DRIFT":
        ("t:\n  procedure options(main);\n"
         "  dcl a fixed dec(9,2);\n  dcl c fixed dec(9,4);\n"
         "  a = 6;\n  c = a;\n  put list(c);\nend t;\n",
         "differing scales is"),
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
    # [E2E-7A slice 2] RETIRED: N26_DECDIV (`c = a / 2`) is now PROVEN --
    # R512's own shape compiles byte-exact, so it is registered as a
    # positive specimen instead of a refusal target.  The perimeter it used
    # to guard is now covered by N31/N32/N34/N35 above.
    "N27_DECBIGP": ("t:\n  procedure options(main);\n"
                    "  dcl d fixed dec(20,0);\n  d = 1;\nend t;\n",
                    "exceeds DR's FIXED precision limit"),
    "N28_DECLITFRAC": ("t:\n  procedure options(main);\n"
                       "  dcl d fixed dec(7,0);\n  d = 1.25;\nend t;\n",
                       "into scale 0 [TBD]"),
    "N16_CATASSIGN": ("t:\n  procedure options(main);\n"
                      "  dcl n char(6) varying;\n  dcl m char(6) varying;\n"
                      "  n = 'Q';\n  m = 'Z' || n;\nend t;\n",
                      "char store from non-literal"),
    # [E2E-7A slice 4] GET / MOD-in-condition perimeter.  The three GET
    # negatives this slice superseded (N1_GET `dcl a fixed', N17_GETINT
    # `dcl i fixed binary', N18_GET2 two char-varying items) are now
    # byte-exact POSITIVES R913/R914/R917 -- numeric GET is proven for those
    # shapes, so they no longer belong in this panel.
    "N44_GETFIXCHAR": ("t:\n  procedure options(main);\n  dcl a char(4);\n"
        "  dcl i fixed binary;\n  get list(a, i);\nend t;\n",
        "GET LIST of this target kind"),
    # DR stores a FIXED-char GET item through ?SSCFS [golden/e2e10/R916
    # route]; only ?SSVFS (char VARYING) is implemented: must refuse.
    "N45_GETSUB": ("t:\n  procedure options(main);\n  dcl x char(4);\n"
        "  dcl i fixed binary;\n  get list(x(1));\nend t;\n",
        "GET form not in E2E-3e subset"),
    # [C079] a 1-byte FIXED BIN cell takes the 0x32/STA store form; no
    # numeric-GET sample shows such a target: must refuse.
    "N46_GET1BYTEBIN": ("t:\n  procedure options(main);\n  dcl b fixed bin(1);\n"
        "  dcl q fixed binary;\n  b = 7;\n  q = b;\n  get list(b);\n"
        "end t;\n",
        "1-byte FIXED BINARY target"),
    # MOD-in-condition is proven ONLY as `= 0' / `^= 0' [R908-R912]: the
    # bare HL-zero test cannot express `> 0': must refuse.
    # ------------------------------------------------------------------
    # [E2E-8] DO/BY perimeter: shapes DR handles by a lowering my build has
    # no sample for.  Each is a TESTED refusal.
    # ------------------------------------------------------------------
    "N48_DOWHILE_CONST": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                          "  dcl s fixed;\n  s = 0;\n"
                          "  do i = 0 by 1 while (i < 4);\n"
                          "    s = s + i;\n  end;\n  stop;\nend t;\n",
                          "DO WHILE/REPEAT combo"),
    "N49_DOWHILE_ONLY": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                         "  dcl s fixed;\n  s = 0;\n"
                         "  do i = 0 while (i < 4);\n"
                         "    s = s + i;\n  end;\n  stop;\nend t;\n",
                         "DO WHILE/REPEAT combo"),
    "N50_DOZEROBOUND": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                        "  dcl s fixed;\n  s = 0;\n"
                        "  do i = 1 to 0;\n    s = s + i;\n  end;\n"
                        "  stop;\nend t;\n",
                        "DO TO bound below 1 unproven"),
    "N51_DOSTEP3": ("t:\n  procedure options(main);\n  dcl i fixed;\n"
                    "  dcl s fixed;\n  s = 0;\n"
                    "  do i = 1 to 9 by 3;\n    s = s + i;\n  end;\n"
                    "  stop;\nend t;\n",
                    "DO BY magnitude > 2 unproven"),
    # [E2E-9 slice 6] perimeter of the multi-arg / DEC-formal subset.  Each
    # is a tested negative: my build must refuse with [TBD], never guess bytes.
    "N52_DEC_FORMAL_PUT": (
        "t:\n  procedure options(main);\n  dcl r fixed dec(9,2);\n"
        "  dcl (x,y) fixed dec(9,2);\n  x = 1.5;\n  r = g(x);\n  stop;\n"
        "  g: procedure(q) returns(fixed dec(9,2));\n"
        "     dcl q fixed dec(9,2);\n     put skip list(q);\n"
        "     return (q);\n  end g;\nend t;\n",
        "PUT LIST of a FIXED DECIMAL formal is unsampled"),
    "N53_DEC_FORMAL_CONJ": (
        "t:\n  procedure options(main);\n  dcl r fixed dec(9,2);\n"
        "  dcl (x,y) fixed dec(9,2);\n  x = 1.5;\n  y = 2.5;\n"
        "  r = g(x, y);\n  stop;\n"
        "  g: procedure(q,w) returns(fixed dec(9,2));\n"
        "     dcl (q,w) fixed dec(9,2);\n     if q = 0 & w = 0 then stop;\n"
        "     return (q);\n  end g;\nend t;\n",
        "FIXED DECIMAL formal as a conjunction operand is unproven"),
    # [E2E-11 step 3c] N54_FORMAL_PASSTHRU RETIRED.  It was a capability-gap
    # negative: DR compiles `return (f2(q, p));' -- passing pointer formals on as
    # actuals -- and emits a .REL (golden/e2e133/E28A).  Sixth instance of the
    # "negative whose subject DR compiles" pattern (N56, N63-N66, N77, N55).  The
    # source is now a POSITIVE specimen, E28A, byte-exact, and the forwarding
    # lowering it needed is E27B's.
    # [E2E-11 step 3d] N55_FORMAL_STORE RETIRED -- DR compiles it.  Its source is
    # now positive specimen E28D (byte-exact), and E28E adds the semantic witness:
    # g(q) does `q = y' with y = 2.5 and is called as r = g(x), so the program
    # prints "2.50 2.50" -- the caller's own x was overwritten through the
    # pointer.  Seventh instance of the "negative whose subject DR compiles"
    # pattern (N56, N63-N66, N77, and N54 one step earlier).

    "N57_ADD_LIT_LIT": (
        "t:\n  procedure options(main);\n  dcl x fixed;\n  x = 3 + 2;\n"
        "  stop;\nend t;\n",
        "ADD between TWO INTEGER LITERALS"),
    "N61_FLOAT_TO_FIXED": (
        "t:\n  procedure options(main);\n  dcl a float;\n  dcl i fixed;\n"
        "  a = 1.5;\n  i = a;\n  stop;\nend t;\n",
        "storing a FLOAT value into a non-float variable"),
    "N62_FLOAT_BINARY14": (
        "t:\n  procedure options(main);\n  dcl g float binary(14);\n"
        "  g = 1.5;\n  stop;\nend t;\n",
        "FLOAT BINARY(14) precision unsupported"),
    # RETIRED N63_FLOAT_COMPARE_COND: FLOAT `>` in an if-condition is supported and byte-exact [R3097, R3070-R3074] -- it now belongs to the positive panel.
    # RETIRED N64_FLOAT_CONV_IN_COND: `a > 2.5` in an if-condition is supported and byte-exact [R3098, R3077] -- it now belongs to the positive panel.
    # [E2E-10 step 2] DR pins cell+cell [R3030-R3033] and formal+formal
    # [R3038] FLOAT operand pairs; a MIX of the two has no sample, so the
    # lowering must refuse rather than borrow the DEC pattern.  The call is
    # fixed-argument-free (a float variable argument, [R3061]) so the refusal
    # really comes from the operand pair inside the callee.
    # RETIRED N65_FLOAT_CELL_FORMAL_MIX: a cell mixed with a pointer formal is ordinary address-mode and byte-exact [R3099, R3082-R3086] -- it now belongs to the positive panel.
    # RETIRED N66_FLOAT_GET: GET LIST into a FLOAT variable is supported and byte-exact [R3100, R3065/R3066/R3004] -- it now belongs to the positive panel.
    # [E2E-10 step 3b] a FLOAT formal of a RECURSIVE procedure: DR copies the
    # caller's float into the callee's declared cell at body entry [R3103
    # `LXI H,X A(0010) / PUSH H / LHLD X A(000E) / XCHG / POP H / LXI B,0004 /
    # CALL <copy>`].  My lowering has no sample of that copy, and every DATA
    # address in R3103 matches while only the prologue is missing -- the most
    # dangerous kind of near-miss, so it refuses.
    "N71_RECURSIVE_FLOAT_FORMAL": (
        "t:\n  procedure options(main);\n  dcl a float;\n  dcl m float;\n"
        "  a = 1.5;\n  m = p(a);\n  put skip list(m);\n  stop;\n"
        "  p: procedure(x) returns(float binary(24)) recursive;\n"
        "     dcl (x,q) float;\n  q = x;\n     return (q);\n  end p;\nend t;\n",
        "a FLOAT formal of a RECURSIVE procedure"),
    "N67_NEGATE_CONVERTED": (
        "t:\n  procedure options(main);\n  dcl a float;\n  dcl i fixed;\n"
        "  dcl d1 float;\n  a = 1.5;\n  i = 3;\n  d1 = a * -i;\n"
        "  stop;\nend t;\n",
        "negating a ?QI15F conversion result"),
    "N68_FLOAT_BINARY_RETURN": (
        "t:\n  procedure options(main);\n  dcl d1 float;\n"
        "  d1 = g(3);\n  stop;\n"
        "  g: procedure(n) returns(fixed);\n     dcl n fixed;\n"
        "     return (n);\n  end g;\nend t;\n",
        "used as a FLOAT operand"),
    "N69_FIXED_ARG_FLOAT_FORMAL": (
        "t:\n  procedure options(main);\n  dcl a float;\n  dcl i fixed;\n"
        "  dcl d1 float;\n  a = 1.5;\n  i = 3;\n  d1 = g(i);\n  stop;\n"
        "  g: procedure(p) returns(float);\n     dcl p float;\n"
        "     return (p + p);\n  end g;\nend t;\n",
        "non-float-variable argument against a FLOAT formal"),
    "N70_FLOAT_ARG_FIXED_FORMAL": (
        "t:\n  procedure options(main);\n  dcl (a,x) float;\n"
        "  dcl d1 float;\n  a = 1.5;\n  x = 2.5;\n  d1 = g(x);\n  stop;\n"
        "  g: procedure(p) returns(fixed);\n     dcl p float;\n"
        "     dcl i fixed;\n     i = 1;\n     return (i);\n  end g;\nend t;\n",
        "used as a FLOAT operand"),
    "N72_FIXED_BIN_GT15": (
        "t:\n  procedure options(main);\n  dcl a fixed bin(31);\n  a = 1;\n"
        "  put list(a);\nend t;\n",
        "exceeds DR's FIXED precision limit"),
    # [E2E-11 step 1a] BIT(1)/STATIC refusals.  N78 agrees with DR's own language
    # rule (E20C passes pass 1, then DR's pass 2 prints NOT STATIC and emits no
    # .REL).  N74-N77 are PERIMETER refusals: all four were compiled by DR itself
    # (golden/e2e11u/T1..T4, real .REL), so each marks capability I have not
    # implemented yet -- they are pinned here so a future slice cannot regress
    # silently by dropping the refusal, and their goldens are the acceptance test.
    "N74_BIT_TO_BIT_COPY": (
        "PT1:\n  procedure options(main);\n"
        "  dcl f bit(1) static initial('1'b);\n  dcl g bit(1);\n"
        "  g = f;\n  stop;\nend PT1;\n",
        "store into BIT(1) from ident is unsampled"),
    "N75_BIT_WIDER_THAN_ONE": (
        "PT2:\n  procedure options(main);\n  dcl (b,c) bit(5);\n"
        "  b = c;\n  stop;\nend PT2;\n",
        "BIT(5) has no byte-level DR sample"),
    "N76_STATIC_INITIAL_FIXED": (
        "PT3:\n  procedure options(main);\n"
        "  dcl s fixed static initial(5);\n  s = s + 1;\n  stop;\nend PT3;\n",
        "STATIC on FIXED BINARY(15,0) is unsampled"),
    # [E2E-11 step 2] RETIRED N77_BIT_BARE_CONDITION: the bare `if f then' on a
    # BIT(1) variable is now implemented and byte-exact.  DR tests it through the
    # SIGN flag, not zero -- LDA f / ORA A / JP skip (opcode f2, "jump if positive",
    # i.e. bit 7 clear) [T4, FLTPOLY2 code 0x75-0x7A].  That is a different shape
    # from the comparison form (LDA/ANI 80/JNZ) and from the fixed-bin ident test,
    # which is why it needs its own arm, placed first so a bit condition can never
    # be captured by the fixed ladder.  T4 is a POSITIVE specimen now.
    # [E2E-11 step 2] PERIMETER refusals around ON/FILE.  All three subjects are
    # programs DR compiles, so these record capability I have not built, not
    # language limits -- and each has a DR golden to be measured against later.
    "N80_ON_HANDLER_BEGIN": (
        "e11c:\n  procedure options(main);\n  dcl sysin file;\n"
        "  dcl efile bit(1) static initial('0'b);\n"
        "  dcl x fixed bin(15);\n  on endfile(sysin) begin;\n"
        "    efile = '1'b;\n  end;\n  get list(x);\n  stop;\nend e11c;\n",
        "procedure without name"),
    "N78_INITIAL_WITHOUT_STATIC": (
        "E20C:\n  procedure options(main);\n"
        "  dcl f bit(1) initial('1'b);\n  if f = '1'b then n = 1;\n"
        "  dcl n fixed;\n  stop;\nend E20C;\n",
        "without STATIC is rejected by DR"),
    # [E2E-11 step 3] the two halves of DR's NOT PROC / TYPES NOT= split, plus
    # external ENTRY linkage.  All three are DR pass-2 diagnostics with NO .REL
    # emitted (golden/e2e121/E24D, golden/e2e122/E24H, golden/e2e122/E24I), so
    # refusing them is conformance, not a gap.  E24G is different in kind: DR
    # COMPILES it, and I refuse it on purpose -- the object-file shape is known
    # (`LXI H,*A(desc) / CALL <NAME>` + LINK-CHAIN-EXT), but linking and running
    # need the historical assembly module, so accepting it would let object-file
    # identity masquerade as executable acceptance.
    "N81_CALL_OF_VALUE_RETURNING": (
        "E24D:\n  procedure options(main);\n  declare (n, s) fixed;\n"
        "  s = 4;\n  call acc(s);\n  n = acc(s) + 1;\n  stop;\n"
        "  acc: procedure (v) returns(fixed);\n  declare v fixed;\n"
        "  return (v + 10);\n  end acc;\nend E24D;\n",
        "NOT PROC"),
    "N82_CALL_OF_FLOAT_RETURNING": (
        "E24H:\n  procedure options(main);\n  declare (a, n) fixed;\n"
        "  a = 2;\n  call hf(a);\n  stop;\n"
        "  hf: procedure (v) returns(float);\n  declare v fixed;\n"
        "  return (v * 1.5);\n  end hf;\nend E24H;\n",
        "NOT PROC"),
    "N83_EXPR_OF_NO_RETURNS": (
        "E24I:\n  procedure options(main);\n  declare (a, n) fixed;\n"
        "  a = 2;\n  n = gs(a);\n  stop;\n"
        "  gs: procedure (v);\n  declare v fixed;\n  v = v + 1;\n"
        "  end gs;\nend E24I;\n",
        "TYPES NOT="),
    # [E2E-11 step 4] N84_EXTERNAL_ENTRY_CALL RETIRED: it was MY deliberate
    # perimeter refusal, not a DR rule -- DR compiles `call ex(a);' against
    # `declare ex entry(fixed) external;' and emits E24G.REL.  The feature is now
    # implemented; E24G is a positive specimen below.  Eighth instance of the
    # "negative whose subject DR compiles" pattern.  Kept as a comment so the
    # history stays visible next to the panel.

    "N73_FIXED_DEC_GT15": (
        "t:\n  procedure options(main);\n  dcl a fixed dec(16);\n  a = 1;\n"
        "  put list(a);\nend t;\n",
        "exceeds DR's FIXED precision limit"),
    "N47_MODGT": ("t:\n  procedure options(main);\n  dcl i fixed binary;\n"
        "  i = 25;\n  if mod(i,12) > 0 then i = 1;\nend t;\n",
        "condition form not in E2E-3b subset")
}




# ---------------------------------------------------------------------------
# NEGATIVE-PANEL TAXONOMY  [E2E-11 step 4, DR verdict pass `negpanel1`]
#
# Every REJECTS source was handed to DR verbatim (CRLF + ^Z, $L$C$D, 65 programs
# in one batch) and DR's own verdict recorded here, because for most of the
# panel the interesting question is not "does my compiler refuse" -- it always
# refuses, which is trivially true -- but "does DR refuse too".  Without that
# column the panel conflates two completely different facts, and I have been
# bitten eight times by the conflation: N56, N63-N66, N77, N54, N55, N84 all
# asserted a perimeter DR happily compiled through.
#
# The result is lopsided and it matters:
#
#   DR REFUSES        11  -- language rules, DR's verbatim diagnostic recorded.
#                            These are the panel's actual semantic evidence.
#   DR COMPILES IT    54  -- MY capability gap.  The panel proves only that my
#                            build is conservative; it says nothing about DR.
#                            Each of the 54 now has a DR .REL in
#                            golden/negpanel1/<NGxx>/, i.e. a byte-exact target
#                            that already exists, so the panel doubles as a
#                            ranked implementation backlog.
#
# Two consequences held to going forward:
#   * a new negative must be classified here, and the gate fails if it is not;
#   * before touching a negative, ask DR.  Eight times in a row the answer was
#     "DR compiles it", and the ninth could easily be a tenth.
#
# Categories:
#   dr-refuses   DR's own compiler rejects the source (language rule / syntax /
#                implementation limit OF THE COMPILER, with DR's word attached)
#   my-gap       DR compiles the source and emits a .REL; my build refuses
#
# Generated from golden/negpanel1/ (DR's transcripts) rather than transcribed by
# hand, so the dict cannot drift from the evidence it summarizes; re-run
# build/mk_neg_panel.py + oracle/batch.py --tag negpanel1 to regenerate.
# [E2E-11 step 5] Q8: a procedure-only module returning FIXED DEC whose FORMAL is
# plain FIXED -- `return (x)' needs DR's FIXED->DEC conversion (CALL ?QI15D).  DR
# compiles it cleanly (golden/e2e148/Q8/Q8.REL), so this is MY gap, not a language
# limit; it is registered as a negative only because the gate must see a [TBD]
# refusal rather than a silently wrong cell.  The MODULE shape itself is fine --
# Q9 (a DEC-returning module whose formal is already DEC(5,2)) is byte-exact --
# which is what makes this a conversion gap rather than an entry-structure gap.
class NoOverwriteDict(dict):
    """[C163] A panel dict that refuses silent SUBSTITUTION.

    E2E-18 registered eight C162 controls as W1..W8 -- names ALREADY used by five accepted
    E2E-15 specimens from e15src -- and plain dict assignment replaced them without a word.
    The panel total read 536 where it should have read 541: a removal is visible, a
    replacement that keeps the name is not, and equal counts conceal it [C158].  Worse, the
    inventory was regenerated before its diff was read, so the committed record would have
    ratified the loss.  Both halves are now closed: every registration path (literal, loop,
    update) raises at import time, and add_spec() gives loop registrations a named guard.
    Retiring a specimen deliberately still works -- pop() first, then register.
    """

    def _guard(self, k):
        if k in self:
            raise ValueError(
                "panel SUBSTITUTION refused: %r is already registered as %r.  A name that is "
                "taken is a COLLISION, not an update: namespace the new key, or pop() the old "
                "one deliberately if it is really being retired [E2E-18/C163]"
                % (k, self[k]))

    def __setitem__(self, k, v):
        self._guard(k)
        dict.__setitem__(self, k, v)

    def update(self, *a, **kw):
        for src in a:
            for k in (src.keys() if hasattr(src, "keys") else [k for k, _ in src]):
                self._guard(k)
        for k in kw:
            self._guard(k)
        dict.update(self, *a, **kw)


SPECIMENS = NoOverwriteDict(SPECIMENS)
# [E2E-40/P9 -> RETIRED BY E2E-40/P10] E45S6 WAS the one negative on this panel whose DR verdict was
# MEASURED rather than unmeasured: DR compiles `put list(a + (b + c))' (golden/e45/E45S6: CODE 0x54,
# DATA 000C, console 31 in golden/e45r/E45S6.output.txt) and its own relocation order -- expression
# fixups to 0x0 0x2 0x4 0x6 0x8 0xa | 0x2 0x4 0x0 | 0x51 -- six initializers, then the expression as
# b, c, a, then the code length -- i.e. it evaluates the parenthesized right group first.
# P9 registered the refusal and stopped there, describing it as a PUT-item-classifier gap only.  It
# was TWO gaps: the width classifier had no Econd case (the actual refusal), and the generic ADD arm
# evaluated left-first, which the classifier fix alone exposed as an 11-byte difference.  P10 closes
# both; E45S6 is now a byte-exact specimen AND a runtime row, and this negative is gone.  Recorded
# here rather than deleted because a my-gap entry disappearing without explanation is indistinguishable
# from a gap that never existed.  The remaining negatives E42N1/E42N2/E42N4 stay, and E45S6's
# neighbours are narrower than P10 claimed [E2E-40/P10a]: a parenthesized MUL on the right of an ADD
# (MB34, MB35) reaches this arm and keeps its left-first route, but R722 `a + (b/d)' and LR19
# `x + (-32768)' do NOT reach this arm (decimal operands; out-of-range literal), so DIV/SUB/EXP and a
# parenthesized literal are UNSAMPLED here.  What is admitted is `(x + (y + z))' with internal members,
# nothing wider -- and the guard is `paren_add_right r' alone, since P10's conjunction was implied by
# its own left operand (spec/lab-evidence/e2e40-p10a/ARM-REACH.txt).

# [E2E-41/P1b] FILE-statement shapes DR compiles today and this compiler refuses by
# name (three in P1; E41X1 retired by P2b, see the retirement note below).  Each is
# classifiable as `my-gap' because the DR side is MEASURED, not inferred --
# the object is cited in NEG_META below.  Two further refusals (OPEN naming no mode word;
# CLOSE naming several files) are deliberately NOT registered here: both panel classes
# require knowing what DR does, and no DR object in this repository contains either shape
# (spec/notes/e2e41-p0-file-open-reconnaissance.md section 12 asks for exactly those
# probes).  They are documented in spec/lab-evidence/e2e41-p1/REFUSALS.txt instead, which
# is where an unmeasured refusal belongs.
# [E2E-41/P2b] E41X1 RETIRED.  `open file(f) title('XY'); close file(f);' refused
# because a literal TITLE was not lowered; with the E17B/E16C/E18A lowering in, the
# TITLE option itself is no longer what stops that source.  It still refuses -- but
# now at `OPEN FILE(...) naming no INPUT or STREAM has no DR witness [TBD]', because
# E41X1 names no mode and NONE of the 34 measured OPENs omits one (P0 section 12,
# probe E46C).  That refusal is UNMEASURED on the DR side, and the P1 policy at the
# head of this block is that a negative-panel entry must state a measured DR verdict
# -- so E41X1 leaves the active panel rather than being re-pinned to an unmeasured
# reason.  Its historical registration and reason are preserved here and in
# spec/notes/e2e41-p2-literal-title-stream-open.md; its exact source is NOT claimed
# byte-identical to DR (no DR object exists for it), and E17B/E16C/E18A carry the
# byte-parity claims.  It is also documented in
# spec/lab-evidence/e2e41-p2/REFUSALS.txt.

REJECTS.update({
    "E41X4": (
        "t:\n  procedure options(main);\n  dcl f file, s char(20);\n"
        "  read file(f) into(s);\nend t;\n",
        "READ of a named file has no DR witness"),
    "E41X5": (
        "t:\n  procedure options(main);\n  dcl f file;\n"
        "  put file(f) list('A');\nend t;\n",
        "PUT LIST with ON options"),
})

REJECTS = NoOverwriteDict(REJECTS)


def add_spec(key, ref):
    """Register a byte-exact specimen through the substitution guard [C163]."""
    SPECIMENS[key] = ref


REJECTS["Q8"] = (open("e14src/Q8.PLI", "rb").read().replace(b"\r\n", b"\n")
                 .rstrip(b"\x1a").decode(), "non-decimal operand")

# [E2E-12] STACK boundary probes DR itself refuses (T5, T10 -- pass-1 error, NO .REL,
# so mirroring them is perimeter parity, not a gap), and three DR-COMPILES shapes that
# expose a DIFFERENT pre-existing gap: DR places a main-block statement that follows an
# appended procedure at the epilogue address (T14: proc body code 0010-0022, then
# SET-LC code 0023 for the CALL ?STOPX), which my R423-era rule still refuses.
# [E2E-12/C139] Four shapes DR compiles and that MY lowering computes WRONG (not
# merely differently): U1's sum(100) came out 12488 instead of 5050.  Registered here
# so the gate insists on a [TBD] refusal -- a silent mis-compile is worse than a
# refusal, and before the guard these shapes fell through with neither parity nor a
# diagnostic.
# [E2E-13/C141] U1 and W1-W3 were REJECTS: my ADD-with-call-on-the-right lowering parked
# the left operand in DE across the call, so sum(100) printed 12488 instead of 5050.  DR
# defers the load until AFTER the call (CALL ; XCHG ; LHLD left ; DAD D), which is sound
# because a recursive activation's locals live in its own SVBLK shadow block restored by
# ?RSBLK.  Implemented from the six $C listings in golden/e2e174; all four are now
# byte-exact AND run to the correct independently computed values (5050, 36, 36, 8).
# The historical wrong-value artifacts stay committed: golden/e2e169mr/U1.output.txt.
for _n, _g in (("U1", "golden/e2e169d/U1/U1.REL"),
               ("W1", "golden/e2e170/W1/W1.REL"),
               ("W2", "golden/e2e170/W2/W2.REL"),
               ("W3", "golden/e2e170/W3/W3.REL")):
    SPECIMENS[_n] = ("e15src/%s.PLI" % _n, _g)
for _n, _m in (("ST5", "exceeds 65535"), ("ST10", "non-integer-literal"),
               ("ST8", "after an appended procedure"),
               ("ST13", "after an appended procedure"),
               ("ST14", "after an appended procedure")):
    REJECTS[_n] = (open("e15src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), _m)


# ---------------------------------------------------------------------------
# [E2E-13] C141: the operand-preservation and small-constant-arithmetic panels.
# Sources in e16src/, DR goldens in golden/e2e174 (P/K/M/S/T/X + e2e175 M/N,
# e2e176 N, e2e177 R, e2e179 X).  47 byte-exact, 4 refused because the .REL
# RECORD ORDER (not the instruction stream) still diverges -- see
# spec/notes/e2e13-operand-preservation-and-constants.md.
# ---------------------------------------------------------------------------
_E13_TAG = {"P1": "e2e174", "P2": "e2e174", "P3": "e2e174", "P4": "e2e174",
            "P7": "e2e174", "P8": "e2e174", "P10": "e2e174", "P11": "e2e174",
            "K1": "e2e174", "K2": "e2e174", "K3": "e2e174", "K4": "e2e174",
            "K5": "e2e174", "K6": "e2e174", "K7": "e2e174", "K8": "e2e174",
            "K9": "e2e174", "K10": "e2e174", "K11": "e2e174",
            "M0": "e2e175", "M1": "e2e175", "M2": "e2e175", "M3": "e2e175",
            "M4": "e2e175", "M6": "e2e175", "M7": "e2e175", "M16": "e2e175",
            "N4": "e2e176", "N5": "e2e176", "N6": "e2e176", "N7": "e2e176",
            "N8": "e2e176",
            "R4": "e2e177", "R5": "e2e177", "R6": "e2e177", "R8": "e2e177",
            "R10": "e2e177", "R12": "e2e177", "S5": "e2e177", "S6": "e2e177",
            "S8": "e2e177",
            # [E2E-13] keyed Y2/Y4/Y8, NOT T2/T4/T8: the file names keep DR's artifact
            # names (golden/e2e177/T4/...) and the keys avoid a COLLISION -- T4 and T8 are
            # long-standing specimens from the e2e11 series, and registering by name would
            # have replaced them.  This is the second time a regression-list key collision
            # showed up here (see the ST*/T* note above), so it is pinned with a comment.
            "Y2": "e2e177", "Y4": "e2e177", "Y8": "e2e177",
            "X1": "e2e179", "X2": "e2e179", "X3": "e2e179"}
# key -> source/artifact base name (differs for Y2/Y4/Y8, whose DR artifacts live in
# golden/e2e177/T2|T4|T8 -- keys avoid the T4/T8 collision, names stay canonical)
_E13_BASE = {"Y2": "T2", "Y4": "T4", "Y8": "T8"}
for _n, _t in _E13_TAG.items():
    _b = _E13_BASE.get(_n, _n)
    SPECIMENS[_n] = ("e16src/%s.PLI" % _b, "golden/%s/%s/%s.REL" % (_t, _b, _b))
# The C140 family that DIFFERED before this milestone and is now byte-exact.
SPECIMENS["C1"] = ("e15src/C1.PLI", "golden/e2e172/C1/C1.REL")
SPECIMENS["C4"] = ("e15src/C4.PLI", "golden/e2e172/C4/C4.REL")
SPECIMENS["C7"] = ("e15src/C7.PLI", "golden/e2e173/C7/C7.REL")
# [E2E-14/C145] P9: nested literal-actual call chain, byte-identical after the two-phase
# anonymous-cell numbering.  It is NOT in _E13_TAG -- when E2E-14 retired P9 from the negative
# panel I first anchored its registration into REJECTS, then "simplified" it away on the
# mistaken belief the tag loop already covered it, which silently DROPPED a verified specimen
# (509 instead of 478+32).  Restored explicitly; registration_audit() cannot see a removal,
# so the count is cross-checked by hand whenever the panel changes [C154].
SPECIMENS["P9"] = ("e16src/P9.PLI", "golden/e2e174/P9/P9.REL")

# ---------------------------------------------------------------------------
# [E2E-15] C148/C150/C151: DR's small-constant FIXED multiplication family, the
# operand-parking rule for compound right operands, and the *0 / >=32768 refusals.
# Sources in e18src/, DR goldens in golden/e2e186 (MB1-MB18), e2e187 (MB19-MB25),
# e2e188 (MB26-MB28), e2e189 (MB29-MB31), e2e190 (MB34-MB37), e2e195b/e2e197b/
# e2e198b (MB44-MB46, the retired N58/N59/N60 subjects).  32 byte-identical; 9 refused.
# MB41-MB43 produced NO DR object (batch not-ok) and are deliberately ABSENT: a residual
# .REL file is not evidence that DR compiled a program.
# ---------------------------------------------------------------------------
_E15_TAG = {
    "MB1": "e2e186", "MB2": "e2e186", "MB3": "e2e186", "MB4": "e2e186",
    "MB5": "e2e186", "MB6": "e2e186", "MB9": "e2e186", "MB10": "e2e186",
    "MB11": "e2e186", "MB14": "e2e186", "MB15": "e2e186", "MB16": "e2e186",
    "MB17": "e2e186", "MB18": "e2e186",
    "MB19": "e2e187", "MB20": "e2e187", "MB21": "e2e187", "MB22": "e2e187",
    "MB24": "e2e187", "MB25": "e2e187",
    "MB26": "e2e188", "MB27": "e2e188", "MB28": "e2e188",
    "MB29": "e2e189", "MB30": "e2e189",
    "MB34": "e2e190", "MB35": "e2e190", "MB36": "e2e190", "MB37": "e2e190",
    "MB44": "e2e195b", "MB45": "e2e197b", "MB46": "e2e198b",
}
for _n, _t in _E15_TAG.items():
    SPECIMENS[_n] = ("e18src/%s.PLI" % _n,
                     "golden/%s/%s/%s.REL" % (_t, _n, _n))
# [E2E-15/C148] N58_MUL_TWO / N59_MUL_ONE / N60_MUL_LITERAL_LEFT retired from the negative
# panel WITH their own goldens: C148 implemented exactly those routes and the same three
# programs (x = x*2, x = x*1, x = 3*x) are now byte-identical specimens MB44/MB45/MB46.  A
# negative is removed only when its behaviour has a golden of its own -- never merely because
# it stopped firing, which is how a real regression could hide [C154].
# [E2E-16/C152 RESOLVED] MB12 / MB38 / MB39 / MB40 retired from the negative panel WITH their
# own DR goldens: the cause was prescan DEMAND summing String.length per OCCURRENCE while
# pool_str deduplicated by CONTENT, so the pool was reserved twice and written once.  All four
# are now byte-identical specimens in _E16_TAG below.  MB7/MB8 (* 0, DR's own suspicious
# MOV L,H), MB13 (condition form) and MB23/MB31 (k >= 32768) stay refused.
for _n, _m in (("MB7", "multiply by literal 0"), ("MB8", "multiply by literal 0"),
               ("MB13", "condition form"),
               ("MB23", "32768"), ("MB31", "32768")):
    REJECTS[_n] = (open("e18src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), _m)
NEG_META_E15 = {
    "MB7": ("my-gap", "DR COMPILES IT (golden/e2e186/MB7) and lowers BOTH `n * 0' and `0 * n' "
        "to `MOV L,H', which copies H into L and does NOT produce zero -- a probable DR defect "
        "[MB8 emits byte-identical code]. I reproduce neither it (unverified) nor my old "
        "?IM22N-by-0 path (not byte-equal). Note elide_fixed_zero previously rewrote `x * 0' "
        "into `x' outright, a silent mis-compile fixed under C151 [C148]"),
    "MB8": ("my-gap", "The other operand order of MB7: DR emits `MOV L,H' for `0 * n' "
        "[golden/e2e186/MB8], byte-identical to its `n * 0' output, confirming the constant "
        "commutes for DR irrespective of route [C148]"),
    "MB13": ("my-gap", "DR COMPILES IT (golden/e2e186/MB13): `if n * 2 > 8' lowers to the multiply "
        "then `LXI B,FFF7 / DAD B / MOV A,H / ORA A / JM'. The multiply half is byte-exact here "
        "[MB1/MB24]; what refuses is my condition subset, which carries no relational test whose "
        "left operand is a constant multiply. MY gap, not a language rule [C148/C150]"),
    "MB23": ("my-gap", "DR COMPILES IT (golden/e2e186/MB23): k=65535 leaves the 16-bit register "
        "route and is loaded through the DECIMAL POOL (`PUSH H / LXI H,*S / MVI A,p / ?DLDOP / "
        "?QDI15 / POP D / ?IM22N'). My `LXI D,k' would silently truncate the operand, so "
        "refusing is a correctness requirement, not caution [C148]"),
    "MB31": ("my-gap", "DR COMPILES IT (golden/e2e189/MB31) and pins the BOUNDARY exactly: k=32767 "
        "uses `LXI D,7FFF' [MB30, byte-exact] while k=32768 switches to the decimal pool path. "
        "The constant-multiply rule therefore has a signed-16-bit ceiling, not a digit-count "
        "one [C148]"),
}

# ---------------------------------------------------------------------------
# [E2E-16/C152] The literal-pool layout rule, measured on 19 DR probes in e19src/.
# DR keeps ONE cell per distinct string CONTENT, allocated at first use, contiguous from
# data 0; a repeat reuses the address and costs no bytes; the empty literal is the one
# exception in the RECORD stream -- it registers a zero-length SET-LC block per occurrence
# [PL17: two SET-LC(data,0000), no DATA bytes].  PL14 (repeated literal in a PUT EDIT) and
# PL15 (repeated literal in a concat) produced NO DR object (diag/NOT IMP) and are absent:
# no golden, no verdict, and concat therefore keeps its per-occurrence behaviour on BOTH
# sides of demand/layout rather than an extrapolated dedup.
# ---------------------------------------------------------------------------
_E16_TAG = {
    "PL1": "e2e199", "PL2": "e2e199", "PL3": "e2e199", "PL4": "e2e199",
    "PL5": "e2e199", "PL6": "e2e199", "PL7": "e2e199", "PL8": "e2e199",
    "PL8": "e2e200", "PL9": "e2e200", "PL12": "e2e200", "PL13": "e2e200",
    "PL17": "e2e201", "PL18": "e2e202", "PL19": "e2e202", "PL20": "e2e202",
    # PL25/PL26 are the ALIASING probes for content dedup: two different variables store the
    # same literal (PL25) and a variable is re-stored after a shared literal is put (PL26).
    # Both are byte-identical AND execute to identical output in mine and DR [e16ali_mr/e16ali_dr],
    # which is what shows the shared pool cell is read-only rather than silently aliased.
    "PL25": "e2e211", "PL26": "e2e211",
    # the four retired C152 refusals, promoted with the goldens they already had
    "MB40": "e2e191", "MB12": "e2e186", "MB38": "e2e191", "MB39": "e2e191",
}
for _n, _t in _E16_TAG.items():
    _d = "golden/%s/%s/%s.REL" % (_t, _n, _n)
    _src = ("e19src/%s.PLI" % _n) if _n.startswith("PL") else ("e18src/%s.PLI" % _n)
    SPECIMENS[_n] = (_src, _d)
# Char-store shapes that refuse for a PRE-EXISTING reason unrelated to C152 -- the
# `char(1)' len==cap store and the empty store into a FIXED char.  DR compiles all four
# (goldens exist), so these are my-gap refusals, and they are exactly the probes that would
# have verified the empty-block rule through the store path instead of through PUT.
for _n, _m in (("PL10", "fixed store len==cap"), ("PL11", "fixed store len==cap"),
               ("PL16", "fixed-char store form unproven"),
               ("PL21", "fixed-char store form unproven")):
    REJECTS[_n] = (open("e19src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), _m)
NEG_META_E16 = {
    "PL10": ("my-gap", "DR COMPILES IT (golden/e2e200/PL10).  The refusal is NOT the pool rule: "
        "`c char(1)' with `c = \'W\'' is len==cap, a store form my emitter has never measured "
        "[V102/V103 cover a DIFFERENT capacity shape], so it declines before reaching the pool. "
        "PL18-PL20 measure the same dedup rule through char(3) and are byte-identical [C152]"),
    "PL11": ("my-gap", "DR COMPILES IT (golden/e2e200/PL11) and it is the probe that MEASURES "
        "char-store dedup -- two stores of 'W' pool ONE byte -- but mine refuses on the unproven "
        "len==cap `char(1)' form, not on the pool.  Recorded as evidence for the rule and as an "
        "open my-gap for the store form [C152]"),
    "PL16": ("my-gap", "DR COMPILES IT (golden/e2e201/PL16): `c = \'\'; c = \'\';' into a "
        "FIXED char(1) -- my V104 evidence covers the empty store into a VARYING char only, so "
        "the fixed-width empty form is unproven and refuses.  The empty-literal BLOCK-REGISTRATION "
        "rule it would have tested is instead verified by PL17, which is byte-identical [C152]"),
    "PL21": ("my-gap", "DR COMPILES IT (golden/e2e202/PL21) with THREE empty stores into fixed "
        "chars; same unproven fixed-empty form as PL16.  Kept refused so the fixed-width empty "
        "store is never claimed on the strength of the varying-width evidence [C152]"),
}

# ---------------------------------------------------------------------------
# [E2E-18/C162] the controls that pinned the decimal-pool under-count.  Each is byte-identical
# to DR AND all eight run to identical values in mine and in DR, matching hand-computed
# expectations (W1 5, W2 5, W3 5, W4 7, W5 6, W6 5, W7 5, W8 3)
# [golden/e18mine_link/e18mine_run vs golden/e2e221_link/e2e221_run + e2e222_link/e2e222_run].
# W2's golden needed a RE-COMPILE: the first probe generation wrote `b = 5' twice and dropped
# `d = 3', so golden/e2e221/W2 no longer described its source.  It was recompiled as e2e222
# rather than being compared against a stale object [a golden must come from the exact bytes].
# KEYS ARE "C162W*", NOT "W*": the bare W1..W6 names belong to the E2E-15 stack family.
for _n in ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"]:
    add_spec("C162" + _n, ("e22src/%s.PLI" % _n,
                           "golden/%s/%s/%s.REL" % ("e2e222" if _n == "W2" else "e2e221",
                                                    _n, _n)))


# ---------------------------------------------------------------------------
# [E2E-19/Priority 1] ONE-DIMENSIONAL ARRAY STORAGE IN THE BINDER -- LANDED.
# AR1-AR5 declare an array and use ONLY the neighbouring scalars, which isolates
# SIZING and the shift of following variables from element access (not landed).
# All five are RAW-BYTE-IDENTICAL to DR and they bracket the rule:
#   AR1 `dcl a(5) fixed, b fixed'          -> b at A(000A)  (a occupies 0000-0009)
#   AR2 scalar BEFORE and AFTER the array  -> b at 0000, c at 000A
#   AR3 explicit `a(1:5)'                  -> same size as a(5): pins LOWER:UPPER order
#   AR4 `a(0:3)'                           -> FOUR elements, b lands at 0008 (not 000A)
#   AR5 `dcl a(5) fixed bin(15)'           -> explicit type spelling, not only typeless
# AR4 pins the bound arithmetic (4*2=8), and AR3 is the probe that caught my first
# attempt having the Dim_bound orientation reversed -- it refused with "upper bound
# below lower bound", which is how the bug was found instead of papered over.
#
# AC1-AC5 are DR-compiled ELEMENT probes (nonzero-offset literal store, computed store,
# negative constant offset, self-update, element inside an expression) whose lowering is
# characterized but NOT landed [C165]: the first implementation crashed after the read
# path emitted, so it was reverted rather than shipped.  Loud refusals.
for _n in ["AR1", "AR2", "AR3", "AR4", "AR5"]:
    add_spec(_n, ("e23src/%s.PLI" % _n, "golden/e2e223/%s/%s.REL" % (_n, _n)))
_AC = ("DR COMPILES IT with NO ERROR(S) IN PASS 1/2 [golden/e2e224]; this is a MY GAP.  "
       "ARRAY STORAGE is correct now [C164: bind sizes a 1-D FIXED BINARY(15) array at "
       "2*(ub-lb+1) bytes and shifts every following automatic -- verified byte-exactly by "
       "AR1-AR5], but CONSTANT-SUBSCRIPT ELEMENT ACCESS is not landed: an element on the left "
       "still refuses as a non-simple assignment lhs, and on the right it resolves as a call.  "
       "DR's four store forms are measured (offset 0 -> SHLD; nonzero offset + literal -> "
       "LXI H,addr / MVI M,lo / INX H / MVI M,hi; nonzero offset + computed -> PUSH H / "
       "LXI H,addr / POP D / MOV M,E / INX H / MOV M,D; SAME element on both sides -> "
       "LHLD addr / bias / SHLD addr), so the lowering is fully specified.  See C165 for why "
       "the first attempt was reverted.")
NEG_META_E19 = {}
for _n in ["AC1", "AC2", "AC3", "AC4", "AC5"]:
    REJECTS[_n] = (open("e23src/%s.PLI" % _n, "rb").read()
                   .replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   # AC3 was first classified with the array CODEGEN still in the tree, where it
                   # reached the parked-ADD guard.  With only the binder landed, its array stores
                   # hit the non-simple-lhs refusal FIRST -- so all five AC probes share one marker
                   # now.  This is the marker doing its job: it refused to accept a reason that no
                   # longer matches the binary being tested.
                   "non-simple assignment lhs")
    NEG_META_E19[_n] = ("my-gap", _AC)
# [E2E-19] RD1-RD3 are element-READ probes (DR-compiled, golden/e2e225).  They refuse in
# production as an unknown-call because the store/read lowering is not landed; the read FORM is
# verified against DR (RD3: first element LHLD A(0000), last LHLD A(0000)+0008) and the blocker is
# the double-resolution of one Esuffix [C165 addendum, spec/patches/e19-array-read-attempt.patch].
_RD = ("DR COMPILES IT [golden/e2e225]; MY GAP, and a narrow one: 1-D array STORAGE is correct "
       "[C164, verified by AR1-AR5] and DR's element-READ instruction form is confirmed to match "
       "mine in isolation, but the read is not landed because one Esuffix expression is resolved "
       "more than once (once in lower_hl's own arm, again via lower_put_items_gen) and only the "
       "first resolution sees the array metadata -- so the second falls into the call path and "
       "dies on List.assoc.  Fix is to resolve subscripted names ONCE against the bound "
       "declaration [C165 addendum].")
# [E2E-20/Priority 3] RD1/RD2/RD3 RETIRED as refusals -- their own DR goldens turned
# byte-exact, which is the only sanctioned way to remove a negative [C154].  They are now
# constant-subscript element-READ SPECIMENS:
#   RD1  put skip list(a(3))            -> LHLD A(0000)+0004 + the ordinary scalar PUT tail
#   RD2  a(0:3), put skip list(a(2))    -> non-default lower bound
#   RD3  b = a(1); c = a(5)             -> FIRST and LAST element inside expressions
for _n in ["RD1", "RD2", "RD3"]:
    REJECTS.pop(_n, None)
    NEG_META_E19.pop(_n, None)
    add_spec(_n, ("e23src/%s.PLI" % _n, "golden/e2e225/%s/%s.REL" % (_n, _n)))


# [E2E-17] Independent-coverage probes from the PLI-2000 test suite
# (thirdparty/PLI-2000/pl1/{ARRAY,PASSARAY,CONV,DECY}.PL1) and the minimal DR
# probes they motivated (e21src/AB*, e21src/CB*).  DR compiles EVERY ONE of them
# with "NO ERROR(S) IN PASS 1/2" [golden/e2e214, e2e216, e2e217, e2e218, e2e219,
# e2e220], so all of these are MY gaps, never language rules.  They are registered
# as refusals because the rules are characterized but not yet implemented: arrays
# [C159] and the PROC/DCL abbreviation front-end [C160] -- plus a pre-existing pool under-count found
# by the E2E-16 demand/layout invariant [C162].  Mixed DEC/BIN arithmetic [C161] is now IMPLEMENTED
# for ADD and SUB: CB6 (direct DEC->INT, R506), CB9 (pure DEC) and, since [E2E-25], CB1-CB5, CB7,
# CONV, DECY and the self-add NG14 are all byte-exact SPECIMENS.  It stays REFUSED for MUL/DIV/EXP,
# where CB8 is a single DR sample and one sample is not a rule.
# ---------------------------------------------------------------------------
_E17_REFS = {
    "ARRAY": ("e20src", "e2e214"), "PASSARAY": ("e20src", "e2e214"),
    "CONV": ("e20src", "e2e214"), "DECY": ("e20src", "e2e214"),
    # [E2E-22/P3] AB7's shape (nested procedure declared BEFORE the main statements).  Element
    # passing works; the append layout is what stops it -- see NEG_META["EA1"].
    "EA1": ("e24src", "e2e234"),
}
for _n in ["AB%d" % i for i in range(1, 18)]:
    _E17_REFS[_n] = ("e21src", "e2e216" if int(_n[2:]) <= 7 else
                     ("e2e217" if int(_n[2:]) <= 13 else "e2e218"))
for _n in ["CB%d" % i for i in range(1, 11)]:
    _E17_REFS[_n] = ("e21src", "e2e219" if int(_n[2:]) <= 5 else "e2e220")
# markers: substrings that MUST appear in my [TBD] message, so a changed route is noticed
_E17_MARKER = {
    "ARRAY": "non-simple assignment lhs", "PASSARAY": "non-simple assignment lhs",
    # [E2E-19] AB5/AB13/AB15 now refuse EARLIER and more precisely: the binder itself
    # rejects STATIC and multi-dimensional arrays instead of falling through to a
    # scalar-sizing guess.  Markers updated to the new reason -- a pinned marker
    # exists to notice a route change, not to hide it.
    "AB5": "STATIC array is not independently characterized",
    "AB15": "STATIC array is not independently characterized",
    "AB13": "multi-dimensional or assumed-size array",
    "AB6": "ADD whose left operand must be parked across a call",
    # [E2E-25/C161] CB8 is `b = d * b'.  Mixed ADD/SUB now route, so the refusal that used to cover
    # them (and therefore CB8 as well) no longer fires; CB8 stops on lower_hl's DEC-operand guard,
    # whose message now says precisely what is unpinned -- MUL, DIV, EXP, DEC sub-expressions.  The
    # marker moved with the message: a pinned marker exists to notice a route change, not to hide one.
    "CB8": "decimal operand inside an integer expression",
    "CB9": "pool demand/layout mismatch",
    "CB10": "decimal operation on non-decimal operand",
    # [E2E-22] these three all stop on the SAME unproven shape now that arrays work
    "EA1": "main-block statement after an appended procedure",
    "AB7": "main-block statement after an appended procedure",
}
for _n, (_d, _t) in _E17_REFS.items():
    _f = "%s/%s.PLI" % (_d, _n)
    if _n in (('CB1', 'CB2', 'CB3', 'CB4', 'CB5', 'CB7', 'CONV', 'DECY')):
        # [E2E-25/C161] MIXED FIXED DECIMAL / FIXED BINARY ADD and SUB now convert the DEC operand
        # in place (`LXI H,<var> / MVI A,p / ?DLDOP / ?QDI15', p = the SOURCE precision) and then use
        # the ordinary binary lowering.  All eight are byte-identical to their own DR .REL, and the
        # six that print were LINKed and RUN against DR's .COM with byte-equal console output and
        # independently computed values: CB1 3+5=8, CB2 5+3=8, CB3 3-5=-2, CB4 5-3=2, CB5 z=d+b=8,
        # CB7 12345+5=12350 on the dec(5) route [goldens e2e219/e2e220/e2e214; mine e2e299p, DR
        # e2e306d/e2e307d/e2e308d].  CONV and DECY -- the third-party PLI-2000 programs that were the
        # original reason C161 was written down -- are byte-exact too, so the integration blocker this
        # claim named for four milestones is closed.
        add_spec(_n, (_f, "golden/%s/%s/%s.REL" % (_t, _n, _n)))
        continue
    if _n in ("CB6", "CB9"):
        # CB6: direct DEC->INT, promoted in E2E-17.  CB9: promoted by the C162 demand fix
        # [E2E-18] -- it was a refusal only because the prescan under-counted the pool.
        add_spec(_n, (_f, "golden/%s/%s/%s.REL" % (_t, _n, _n)))
        continue
    if _n == "PASSARAY":
        # [E2E-22/P4] PASSARAY is byte-exact AND its linked .COM prints exactly what DR's prints
        # (1446 bytes, line-for-line identical).  It needed three things: the variable-index
        # ladder, element-as-actual, and `put skip(one) list(...)' -- plus the DO-bound deref fix
        # below, which is what made it CORRECT rather than merely compiling.
        add_spec(_n, (_f, "golden/%s/%s/%s.REL" % (_t, _n, _n)))
        continue
    if _n == "ARRAY":
        # [E2e23] ARRAY IS NOW BYTE-EXACT.  It sat in the DIVERGENT panel through E2E-22 and its
        # single remaining cause turned out to be narrow and fully measurable, not the broad
        # register optimizer C168 had been assumed to need: see C176 and the ZS1-ZS12 block below.
        # Promotion path taken (Priority 4): authentic DR golden [golden/e2e214/ARRAY, PLI-2000
        # original, DR v1.4 NO ERRORS in both passes] -> raw .REL parity -> LINK 1.31 -> cpmsim run
        # -> output identical to DR's own .COM (75 lines) -> divergence row deleted deliberately
        # -> registered here.  DATA area unchanged (62 = 62), so no layout regression.
        add_spec(_n, (_f, "golden/%s/%s/%s.REL" % (_t, _n, _n)))
        continue
    REJECTS[_n] = (open(_f, "rb").read().replace(b"\r\n", b"\n")
                   .rstrip(b"\x1a").decode(),
                   _E17_MARKER.get(_n, "non-simple assignment lhs" if _n.startswith("AB")
                                   else "mixed decimal/integer arithmetic unproven"))
_ARR = ("DR COMPILES IT with NO ERROR(S) IN PASS 1/2 [golden/e2e214,e2e216-e2e218]; this is a "
        "MY GAP, not a language rule.  Arrays ARE implemented front to back [C164 storage in the "
        "binder, C172 runtime addressing, C175 element-as-actual]; the text below records DR's "
        "model, and the specific shape this row refuses is the one named in the message.  "
        "1-D FIXED BINARY(15): `declare a(n) fixed' = n contiguous 2-byte cells in the automatic "
        "area (a(5) occupies data 0000-0009, b lands at 000A).  CONSTANT subscript -> a DIRECT "
        "reference with offset (sub-lb)*2 (`LHLD A+0008'); zero-offset stores use SHLD, "
        "non-zero-offset stores use `LXI H,A+off / MVI M,lo / INX H / MVI M,hi'.  VARIABLE "
        "subscript -> an address LADDER whose relocated operand is `base - lower_bound*"
        "element_size' [C172 CORRECTS C159's `A+(lb-1)*size' wording: VB1 lb=0 addend 0000, "
        "AB2 lb=1 FFFE, VB2 lb=2 FFFC], in one of two forms selected by whether that operand is "
        "the plain base: bias=0 `LHLD i / DAD H / LXI D,base / DAD D' (no stack traffic) and "
        "bias<>0 `LXI H,biased / PUSH H / LHLD i / DAD H / POP D / DAD D' (the base parked on the "
        "stack per C141, because LHLD destroys HL).  `a(i+1)' adjusts the INDEX value before the "
        "doubling (`LHLD i / INX H / DAD H'), so +1 moves one element, not two [AB8].  2-D is "
        "ROW-MAJOR with the LAST subscript fastest [AB13 m(2:4,1:3), m(1,2) -> FFFC = "
        "((1-2)*3+(2-1))*2], NO bounds check is emitted, and an element passed as an actual "
        "stores the element ADDRESS into the call descriptor [C175: AB7, PASSARAY, EA2].")
_DEC = ("DR COMPILES IT [golden/e2e214, e2e219, e2e220]; MY GAP [C161].  DR converts the DEC "
        "operand IN PLACE -- `LXI H,d / MVI A,p / CALL ?DLDOP / CALL ?QDI15' gives the 16-bit "
        "value in HL, with p the SOURCE precision (03 for dec(3), 05 for dec(5)) -- and then runs "
        "its ordinary binary lowering.  The parking rule is C150 unchanged: DEC on the LEFT takes "
        "XCHG [CB1 d+b, CB3 d-b], DEC on the RIGHT takes PUSH H/POP D [CB2 b+d, CB4 b-d] because "
        "the conversion's own CALLs destroy DE.  My compiler refuses because is_dec_expr routes a "
        "mixed expression into the pure-DEC path and lower_hl has no integer-context flag, so a "
        "DEC operand cannot be distinguished from a DEC expression without an explicit marker node.")
for _n in _E17_REFS:
    if _n in ("CB6", "CB9") + ('CB1', 'CB2', 'CB3', 'CB4', 'CB5', 'CB7', 'CONV', 'DECY'):
        continue
    _base = _E17_REFS[_n][0]
    if _n.startswith("AB") or _n in ("ARRAY", "PASSARAY"):
        NEG_META_E17 if False else None
DEC_NOTE = "see _E17 above"
NEG_META_E17 = {}
for _n in _E17_REFS:
    if _n in ("CB6", "CB9") + ('CB1', 'CB2', 'CB3', 'CB4', 'CB5', 'CB7', 'CONV', 'DECY'):
        continue
    if _n.startswith("AB") or _n in ("ARRAY", "PASSARAY"):
        NEG_META_E17[_n] = ("my-gap", _ARR)
    else:
        NEG_META_E17[_n] = ("my-gap", _DEC)
# NEG_META_E17["CB9"] is GONE [E2E-18/C162 RESOLVED]: the refusal was a prescan bug, not a
# language gap.  Root cause -- prescan_stmt keys its DEC demand on the TARGET's type, so a BIN
# target with a DEC-typed rhs (`b = d + 2') fell through to prescan_expr, which has no Enumber
# arm and never sized the operand's cell: demand 2 bytes, lowering 4.  Under-counting is the
# dangerous direction (the pool base is where automatics start, so `b' lands on the decimal
# cells -- the FDTEST failure mode).  Fixed by mirroring the Vdec branch's own condition for
# non-DEC/non-FLOAT targets; CB9 is now byte-identical to DR [golden/e2e220/CB9] and is a
# SPECIMEN.  The eight W1..W8 controls [registered as C162W1..C162W8, see C163] prove the fix
# is a consistent demand RULE and not a +2 adjustment: they build, match DR byte-for-byte, and
# run to hand-computed values in BOTH compilers.
NEG_META_E17["CB10"] = ("my-gap",
    "DR COMPILES IT [golden/e2e220/CB10]: `e = b + d' with e dec(5) adds in BINARY and then "
    "converts the result BACK with `CALL ?QI15D' before ?DSTOP stores it into e.  That is the "
    "FIXED->DEC doorway already recorded as an open gap (Q8) -- DEC->INT is implemented [CB6/R506] "
    "and INT->DEC via decimal(x,p) exists [R506/R509], but a mixed expression stored into a DEC "
    "variable does neither.  Refused, not approximated [C161].")
NEG_META_E17["AB5"] = ("my-gap", _ARR + "  [E2E-19] ARRAY STORAGE is now implemented in the "
    "binder [C164], but AB5's array is STATIC: DR places a static array BELOW the pool, whose "
    "interaction with the pre-existing STATIC-on-fixed-bin guard (C114) is unsampled, so the "
    "binder refuses STATIC arrays deliberately rather than routing them through the "
    "automatic-area code that AB1-AB4 prove.  AB5 still carries two independent gaps. "
    "Element ACCESS is also still missing [C165] [golden/e2e216/AB5].")
NEG_META_E17["AB15"] = NEG_META_E17["AB5"]
NEG_META_E17["AB6"] = ("my-gap", _ARR + "  AB6 `b = a(2) + a(3)' additionally hits the C146 "
    "descriptor-placement class once the elements become computed references: DR parks the left "
    "with `PUSH H / POP D' [golden/e2e216/AB6], which is C150-consistent.")
# NEG_META_E17["CONV"] deleted [E2E-25/C161]: CONV.PL1 (`b = d + b' with d dec(3)) and
# DECY.PL1 (`a = a + c' with c dec(5)) are byte-exact SPECIMENS now, registered by the
# _E17 loop above.  Their runtime behaviour is unchanged in one respect that matters more
# than bytes: both had been REFUSED for four milestones as C161's gap, and CONV's own
# comment in e2e214 is what proved the rule is context-free -- DR converts the DEC operand
# in place whatever the target name or statement shape.  The claim text lives in
# spec/CLAIMS.md C161/C180.
# NEG_META_E17["DECY"] deleted [E2E-25/C161]: CONV.PL1 (`b = d + b' with d dec(3)) and
# DECY.PL1 (`a = a + c' with c dec(5)) are byte-exact SPECIMENS now, registered by the
# _E17 loop above.  Their runtime behaviour is unchanged in one respect that matters more
# than bytes: both had been REFUSED for four milestones as C161's gap, and CONV's own
# comment in e2e214 is what proved the rule is context-free -- DR converts the DEC operand
# in place whatever the target name or statement shape.  The claim text lives in
# spec/CLAIMS.md C161/C180.
# A NEG_META value must be (category, verdict).  A bare string here used to survive until deep
# inside run_negatives(), where `cat, _dv = ...` aborted the whole panel with a TypeError-shaped
# ValueError and 79 already-checked negatives lost their report [E2E-17].  Fail at import instead.
_bad = sorted(k for k, v in NEG_META_E17.items() if not (isinstance(v, tuple) and len(v) == 2))
if _bad:
    raise ValueError("NEG_META_E17 values must be (category, verdict) 2-tuples: %s" % _bad)

# Three shapes DR compiles that I still refuse: instruction bytes identical to DR,
# executed value correct, but the .REL RECORD PLACEMENT differs -- DR writes a call's
# descriptor record at plan time (before the left operand's code when the PUSH route puts
# other instructions first), I write it at point of use [C146].  P9 is GONE from this list:
# its divergence was anonymous-cell NUMBERING, which the two-phase numbering in bind.ml
# fixed, and it is now a byte-identical specimen [C145].
for _n in ("P5", "P6", "P12"):
    REJECTS[_n] = (open("e16src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   {"P5": "left operand must be parked across a call",
                    "P6": "right operand is a procedure call",
                    "P12": "left operand must be parked across a call"}[_n])
NEG_META_E13 = {
    "P5": ("my-gap",
     "DR COMPILES IT (golden/e2e174/P5) and my CODE BYTES ARE IDENTICAL to DR's -- I "
     "emit its own PUSH H/POP D route and both builds print 21 (golden/e2e180r/P5 = "
     "golden/e2e181r/P5).  The .REL still differs: DR writes the call's anonymous-cell "
     "LINK-SET-LC/RELOC records BEFORE the left operand's code records, I write them at "
     "point of use.  Record order is part of byte identity [C141/C142]"),
    "P12": ("my-gap",
     "DR COMPILES IT (golden/e2e174/P12); same cause as P5 -- `g(3)+g(4)' needs the left "
     "call on the stack, my instruction stream matches DR byte for byte and both print "
     "21, but the cell-allocation records serialize later than DR's [C141/C142]"),
    "P6": ("my-gap",
     "DR COMPILES IT (golden/e2e174/P6).  Route now known (PUSH H the minuend, POP D, "
     "?IS22N) and my code bytes match DR exactly; both print 91.  Refused for the same "
     "record-order reason.  IMPORTANT: my PREVIOUS route (XCHG) parked DE across the call, "
     "which any callee touching DE corrupts -- refusing is strictly safer than what ran "
     "before [C141]"),
}

# Names whose console output is compared against the DR arm under --link-run (their
# DR .RELs are the SPECIMENS goldens, so the harness can link both sides).
# [E2E-40/P4] E40R1 joins this list because the member store + ADD-preservation routes made its
# .REL byte-for-byte DR's.  That is what unlocks the link-run arm: the harness links BOTH sides and
# compares the two console transcripts, whereas spec/RUNTIME.txt can only run MINE against a value
# transcribed by hand from DR's earlier session.  Verified, not assumed -- the run prints
# `g=        16' on both sides (.COM IDENTICAL, console BYTE-EQUAL, 13 raw bytes), so DR's printed
# transcript stays the authority for the RUNTIME row AND mine now produces the same bytes.
# [E2E-40/P7] E41P1..E41P4 join because their .RELs are now byte-exact, so the harness can link
# both sides and diff the two consoles.  E41P3 is the one that matters as an ORACLE: E39S7 -- the
# program this slice's rule came from -- never writes `g.b', so DR's own run prints 7 = `a + 0' and
# the ADD is invisible in its output.  E41P3 is E39S7's shape with both operands initialized, where
# 12 = 7 + 5 can only come out of a real addition.  E41P1 (10 = 9 + 1) and E41P4 (9) are the
# biased-copy and plain-copy companions; E41P2 (7) is the ordinary-scalar control whose store DR
# does NOT park.  E39S7 itself gets no RUNTIME row on purpose: its value is not independently
# derivable, and registering it would launder a weak check into the panel.
for _n in ("U1", "W1", "W2", "W3", "P1", "P2", "P3", "P4", "P7", "P8", "P10", "P11",
           "K4", "R4", "R5", "X1", "M4", "Y8", "P9", "E40R1", "E39S5",
           "E41P1", "E41P2", "E41P3", "E41P4",
           # [E2E-40/P8] E42P1 joins: DR's own console value is 10, which only the ladder
           # (5 + 5) reaching the cell can produce.  E42P2 joins too, but as an ABORT row:
           # DR's run prints `ERROR (1), Conversion' because a FIXED BIN(15) cell cannot hold
           # 65535, the check is in the runtime library, and my object shares that library --
           # so its console is byte-identical to DR's.  Both rows are expected substrings of
           # text, not values: one pins a computed number, the other pins a refusal to compute.
           "E42P1", "E42P2"):
    OUTPUT_CHECK.add(_n)

# [E2E-40/P8] The member-store shapes with NO DR sample.  Each is refused by the classifier in
# codegen.ml BEFORE a byte is emitted (P7 left them falling through to `SHLD', which silently
# invented a store shape); the marker is the shared sentence, the `why' clause differs per shape.
# Sources are identical to artefacts/E42N*.PLI, which is what the DR oracle is asked about.
# [E2E-40/P8] same source as artefacts/E42N*.PLI, parameterised on the one statement that
# decides the shape -- so the panel and the DR-oracle artefacts cannot drift apart.
_MEMBER_SRC = ("b9e: procedure options(main);\n"
               "  declare 1 g, 2 a fixed, 2 b fixed;\n"
               "  g.a = 5;\n  g.b = 100;\n"
               "  %s\n"
               "  put list(a);\n  put list(g.b);\n  stop;\nend b9e;\n")
_MEMBER_UNSAMPLED = "internal structure MEMBER is unsampled [TBD] in DR"
REJECTS.update({
    "E42N1": (_MEMBER_SRC % "a = -5;", _MEMBER_UNSAMPLED),
    "E42N2": (_MEMBER_SRC % "a = -65535;", _MEMBER_UNSAMPLED),
    # [E2E-40/P8a] E42N3 (`a = a + 100' on an internal member) is RETIRED, not re-labelled.
    # P8 registered it as my-gap because "the ladder is sampled for -8..16 only" -- but that
    # range came from E22A02..E22A16 / E22B01..E22B08 on ORDINARY variables, which never
    # tested |k| > 16, so the bound was an artifact of my own probe set.  DR measured at the
    # member (golden/e43b/E43B1C) emits `LHLD <cell> / LXI B,0064 / DAD B / SHLD <cell>':
    # 256/256 identical to mine once the gate stopped refusing it.  Its replacement byte-exact
    # specimen is E43B1C; E43L1..L9 and E43M1 pin the boundary set, and E43B5C (+32767) the
    # upper extreme.  E42N1/E42N2 (negated literals) and E42N4 (above 65535) stay refusals --
    # DR has still never been shown those at a member.
    "E42N4": (_MEMBER_SRC % "a = 100000;", _MEMBER_UNSAMPLED),
})

NEG_META = {
    # [E2E-40/P8] all four are `my-gap', NOT `dr-refuses': DR has never been shown a member
    # store of these shapes, so nothing here claims DR rejects them.  Registering a form DR
    # would ACCEPT as a DR-negative would ratify my refusal as DR's behaviour [C256].
    # [E2E-40/P10] E45S6's `my-gap' entry retired -- see the retirement note above REJECTS.  P9's
    # description of it was right about the refusal site and wrong about the scope: fixing the
    # classifier alone did NOT produce DR's bytes, because DR also evaluates the right group first.
    "E42N1": ("my-gap", "DR VERDICT UNMEASURED: `a = -5' into an internal member.  E42P2 shows "
                        "DR parks a literal-conversion result, and the negation route "
                        "(lit_dec_neg_to_hl) has no member sample at all, so mine refuses "
                        "instead of guessing which of DR's store shapes would take it"),
    "E42N2": ("my-gap", "DR VERDICT UNMEASURED at compile, and its nearest witness is a RUNTIME "
                        "ABORT: E42P2 (`a = 65535' into the same member) links and then prints "
                        "`ERROR (1), Conversion' with a traceback (golden/e42p/E42P2.output.txt), "
                        "because a FIXED BIN(15) cell cannot hold 65535.  A negative literal of "
                        "any magnitude is therefore refused here rather than compiled into a "
                        "sequence whose runtime behaviour is unknown"),
    # [E2E-40/P8a] E42N3's entry removed: the shape it refused is now DR-measured (see the
    # REJECTS note above and golden/e43b/E43B1C).  It left the panel as a refusal and came
    # back as a byte-exact specimen, so negatives go 129 -> 128 and specimens 956 -> +E43B1C.
    "E42N4": ("my-gap", "DR VERDICT UNMEASURED: `a = 100000'.  E42P2 (65535) and LR7 (32768 at "
                        "an array cell) bound the decimal-conversion magnitudes DR is known to "
                        "emit; above 65535 nothing is sampled"),
    "ST5": ("dr-refuses",
     "DR REFUSES: 1 ERROR(S) IN PASS 1, NO .REL emitted (golden/e2e160/T5/T5.PRN) "
     "-- stack(65536) does not fit the 16-bit LXI B operand [C138]"),
    "ST10": ("dr-refuses",
     "DR REFUSES: 1 ERROR(S) IN PASS 1, NO .REL emitted (golden/e2e160/T10/T10.PRN) "
     "-- STACK's operand must be an integer literal, not an expression [C138]"),
    "ST8": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e160/T8/T8.REL) -- stack(2000) + a nested "
     "RECURSIVE procedure + `stop;' AFTER the appended procedure.  The STACK part works "
     "(T15 pins it); the refusal is the R423 append-order rule, unrelated to E2E-12"),
    "ST13": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e162/T13/T13.REL) -- same append-order "
     "gap as T14, with STACK(2000) present"),
    "ST14": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e162/T14/T14.REL) -- main-block `stop;' "
     "following an appended procedure: DR emits the CALL ?STOPX at code 0023, AFTER "
     "q's body at 0010-0022.  My rule still refuses it [R423 window was never pinned "
     "against this shape]; candidate next milestone, and a likely ACK/ACKTST blocker"),
    "Q8": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted with CALL ?QI15D "
     "(golden/e2e148/Q8/Q8.REL) -- missing route is FIXED -> DEC conversion, "
     "not the module entry shape [Q9 is byte-exact]"),
    "N3_PAGE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG25/NG25.REL)"),
    "N4_SKIPVAR": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG36/NG36.REL)"),
    "N6_COMPUTED_GOTO": ("dr-refuses",
     "DR REFUSES: ARG COUNT (golden/negpanel1/NG50/NG50.PRN)"),
    "N9_GTZERO": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG65/NG65.REL)"),
    "N11_STROVR": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG01/NG01.REL)"),
    "N12_EMPTYFIX": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG02/NG02.REL)"),
    "N13_CATLIT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG03/NG03.REL)"),
    "N14_CATFIX": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG04/NG04.REL)"),
    "N15_CAT4": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG05/NG05.REL)"),
    "N16_CATASSIGN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG06/NG06.REL)"),
    "N21_DOIDX": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG07/NG07.REL)"),
    "N22_FPUT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG08/NG08.REL)"),
    "N24_BIGIN": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG10/NG10.PRN)"),
    "N25_DECCMP_SCALE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG11/NG11.REL)"),
    "N27_DECBIGP": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG12/NG12.PRN)"),
    "N28_DECLITFRAC": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG13/NG13.REL)"),

    "N30_DECCMP_BUILTIN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG15/NG15.REL)"),
    "N31_DIV_LITERAL_NUMERATOR": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG16/NG16.REL)"),
    "N32_DIV_CHAINED": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG17/NG17.REL)"),
    "N33_DEC_FORMAL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG18/NG18.REL)"),
    "N34_DEC_NEGSCALE_DIV": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG19/NG19.REL)"),
    "N35_DEC_STORE_SCALE_DRIFT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG20/NG20.REL)"),
    "N36_ROUND_ONEARG": ("dr-refuses",
     "DR REFUSES: SYNTAX (golden/negpanel1/NG21/NG21.PRN)"),
    "N37_ROUND_LITERAL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG22/NG22.REL)"),
    "N38_ROUND_INTARG": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG23/NG23.REL)"),
    "N39_ROUND_DYNSCALE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG24/NG24.REL)"),
    "N40_ROUND_SCALE_ABOVE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG26/NG26.REL)"),
    "N41_ROUND_SIMPLE_INADD": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG27/NG27.REL)"),
    "N42_ROUND_INMUL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG28/NG28.REL)"),
    "N43_ROUND_AS_DIVIDEND": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG29/NG29.REL)"),
    "N44_GETFIXCHAR": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG30/NG30.REL)"),
    "N45_GETSUB": ("dr-refuses",
     "DR REFUSES: ARG COUNT (golden/negpanel1/NG31/NG31.PRN)"),
    "N46_GET1BYTEBIN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG32/NG32.REL)"),
    "N47_MODGT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG33/NG33.REL)"),
    "N48_DOWHILE_CONST": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG34/NG34.REL)"),
    "N49_DOWHILE_ONLY": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG35/NG35.REL)"),
    "N50_DOZEROBOUND": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG37/NG37.REL)"),
    "N51_DOSTEP3": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG38/NG38.REL)"),
    "N52_DEC_FORMAL_PUT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG39/NG39.REL)"),
    "N53_DEC_FORMAL_CONJ": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG40/NG40.REL)"),
    "N57_ADD_LIT_LIT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG41/NG41.REL)"),
    "N61_FLOAT_TO_FIXED": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG45/NG45.REL)"),
    "N62_FLOAT_BINARY14": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG46/NG46.REL)"),
    "N67_NEGATE_CONVERTED": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG47/NG47.REL)"),
    "N68_FLOAT_BINARY_RETURN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG48/NG48.REL)"),
    "N69_FIXED_ARG_FLOAT_FORMAL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG49/NG49.REL)"),
    "N70_FLOAT_ARG_FIXED_FORMAL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG51/NG51.REL)"),
    "N71_RECURSIVE_FLOAT_FORMAL": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG52/NG52.REL)"),
    "N72_FIXED_BIN_GT15": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG53/NG53.PRN)"),
    "N73_FIXED_DEC_GT15": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG54/NG54.PRN)"),
    "N74_BIT_TO_BIT_COPY": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG55/NG55.REL)"),
    "N75_BIT_WIDER_THAN_ONE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG56/NG56.REL)"),
    "N76_STATIC_INITIAL_FIXED": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG57/NG57.REL)"),
    "N78_INITIAL_WITHOUT_STATIC": ("dr-refuses",
     "DR REFUSES: NOT STATIC (golden/negpanel1/NG58/NG58.PRN)"),
    "N80_ON_HANDLER_BEGIN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG61/NG61.REL)"),
    "N81_CALL_OF_VALUE_RETURNING": ("dr-refuses",
     "DR REFUSES: NOT PROC (golden/negpanel1/NG62/NG62.PRN)"),
    "N82_CALL_OF_FLOAT_RETURNING": ("dr-refuses",
     "DR REFUSES: NOT PROC (golden/negpanel1/NG63/NG63.PRN)"),
    "N83_EXPR_OF_NO_RETURNS": ("dr-refuses",
     "DR REFUSES: TYPES NOT= (golden/negpanel1/NG64/NG64.PRN)"),
}
# [E2E-40/P1] DR's own QUALIFY refusals, registered now that my binder raises the diagnosis at the
# place DR raises it.  E39X1 (two INTERNAL structures each declaring member `a') and E40X3 (an
# internal structure plus a BASED view each declaring `a') both print `QUALIFY ?' under EVERY
# unqualified use, report `2 ERROR(S) IN PASS 2', and emit NO .REL; both transcripts are in the
# golden tree, so the marker is DR's word, not mine.  E39X1 was carried as a known WRONG-ACCEPTANCE
# through E2E-39 (my binder picked a first binding and compiled); check_qualified_uses in bind.ml
# closes it [C257].
for _n, _g in (("E39X1", "golden/e39b/E39X1/E39X1.PRN"),
               ("E40X3", "golden/e40a/E40X3/E40X3.PRN")):
    REJECTS[_n] = (open("artefacts/%s.PLI" % _n, "rb").read().replace(b"\r\n", b"\n")
                   .rstrip(b"\x1a").decode(), "QUALIFY")
    NEG_META[_n] = ("dr-refuses",
                    "DR REFUSES: `QUALIFY ?' at each unqualified use, `2 ERROR(S) IN PASS 2', no "
                    ".REL (%s) [C257]" % _g)
# [E2E-13] merged after the literal so the E13 block can sit above it.

# [E2E-24/C178] verdict evidence for the six E2E-24 probes that refuse.  All six are# programs DR COMPILED (goldens exist), so each is `my-gap': a designed [TBD] guard of mine,# never a pool-invariant failure.  Recorded here because REJECTS without NEG_META loses the# DR-vs-me verdict, which is the whole content of a negative [C139].
NEG_META_E24 = {
    'LP3': ("my-gap", 'DR compiles it (golden/e2e246/LP3) and lowers `32768 + 65535\' to the DECIMAL POOL chain (?DLDOP both, one ?DADOP, ?QDI15).  My refusal is the designed C148/N301 guard: FIXED ADD of two integer literals has no measured fold, while `0 - 7\' [N301] and `e = 0 - 2\' [N306] DO fold -- the rule is asymmetric, so it stays refused rather than guessed.  Unrelated to the bin(15) route: this shape refused at HEAD too.'),
    'LP7': ("my-gap", 'DR compiles it (golden/e2e246/LP7).  Mine refuses with C161\'s designed guard `decimal operation on non-decimal operand x\': `x\' is FIXED BINARY in a DEC-typed expression, which is exactly the mixed-mode conversion this step\'s Priority 3 would implement.  Refusing is correct: the conversion route is unmeasured, and the value would otherwise be computed wrong.'),
    'LP10': ("my-gap", 'DR compiles it (golden/e2e246/LP10).  LP10\'s only statement is `put skip list(32768)\' -- a literal as a PUT item, exactly the position this step deliberately does NOT route, so the probe says nothing about the decimal route until that PUT form lands.  Registered so the refusal is tracked rather than lost.'),
    'LP13': ("my-gap", 'DR compiles it (golden/e2e246/LP13).  Mine refuses with the designed MB31 threshold guard: MULTIPLY by a literal >= 32768 goes through the DEC pool (`PUSH H / LXI H,*S / MVI A,p / ?DLDOP / ?QDI15 / POP D / ?IM22N\') and that composition is measured only for MB31 itself, so it is refused rather than extrapolated.  LP13 is `x = 2; y = x * 32768\' -- multiply by an out-of-range constant, which is the position Priority 3 has not implemented.'),
    'ML6': ("my-gap", 'DR compiles it (golden/e2e244/ML6).  Mine refuses with the encoder\'s designed guard `DEC literal does not fit its precision [TBD]\': the literal has more digits than the declared precision, which DR\'s ?DLDOP accepts silently.  A value that cannot be packed is never emitted as a wrong packing.'),
    'ML7': ("my-gap", 'DR compiles it (golden/e2e244/ML7).  ML7 is `dcl b fixed bin(15), d fixed dec(3); b = d + 1234567890\': the 10-digit literal is packed against the dec(3) operand precision in DR\'s DEC chain, which my encoder declines. ML6 hits the same guard through `y = d + 1234567890\' with `d\' dec(5).  Both are tracked so neither is mistaken for the pool invariant.'),
}

NEG_META.update(NEG_META_E13)
NEG_META.update(NEG_META_E15)
NEG_META.update(NEG_META_E16)
NEG_META.update(NEG_META_E17)
NEG_META.update(NEG_META_E19)
NEG_META.update(NEG_META_E24)



def run_negatives():
    """Each REJECTS source must FAIL with a [TBD] refusal (never silently
    emit a REL). Returns count of failures-of-purpose (0 = healthy)."""
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    unclassified = sorted(set(REJECTS) - set(NEG_META))
    for name in unclassified:
        print(f"NEG-FAIL {name}: no NEG_META entry -- classify it (dr-refuses "
              f"or my-gap) and record DR's verdict")
    bad += len(unclassified)
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
            cat, _dv = NEG_META.get(name, ("UNCLASSIFIED", ""))
            print(f"NEG-OK   {name}: refused [TBD] ({marker})  [{cat}]")
    return bad


class RegistrationCollision(Exception):
    pass


# [E2E-20/Priorities 2-4] constant-subscript array ELEMENT ACCESS.
# These AB/AC probes were E2E-19's my-gap refusals; each one is retired only because ITS OWN
# registered DR golden turned byte-exact [C154], and each names the DR form it now reproduces:
#   AB1/AB16/AC5  offset 0            -> <value route> ; SHLD base          [form 1]
#   AB3/AB18      offset<>0, literal  -> LXI H,base+off ; MVI M,lo ; INX H ; MVI M,hi [form 2]
#   AC1/AC2       offset<>0, computed -> PUSH H ; LXI H ; POP D ; MOV M,E ; INX H ; MOV M,D [form 3]
#   AB12/AC4      same element both sides -> LHLD ; <bias> ; SHLD           [form 4]
#   AB4/AB17      explicit spelling/orientation controls
#   AB9           `b = a(5) * 3'      -- constant-multiply route, see C169
#   AB6           `b = a(2) + a(3)'   -- DR PARKS a subscripted left operand (C150 syntactic rule)
#   AB22          array LAST in a NESTED procedure's dcl (span fix C167, form 2 in a callee)
#   AB23          scalar control `b = x * 3' -- proves AB9's fix did not move scalar behaviour
_E20_PROMOTE = [
    ("AB1", "e2e216"), ("AB3", "e2e216"), ("AB4", "e2e216"), ("AB6", "e2e216"),
    ("AB9", "e2e217"), ("AB12", "e2e217"), ("AB16", "e2e218"), ("AB17", "e2e218"),
    ("AC1", "e2e224"), ("AC2", "e2e224"), ("AC3", "e2e224"), ("AC4", "e2e224"),
    ("AC5", "e2e224"),
]
# a retired negative must vanish from REJECTS *and* from whichever per-milestone meta dict
# recorded it, or the REJECTS/NEG_META symmetry audit (E2E-16) fires and the verdict evidence
# is silently orphaned.  AB*/AC* were recorded by E2E-19 and by E2E-17, so pop every map.
for _n, _tag in _E20_PROMOTE:
    REJECTS.pop(_n, None)
    for _md in (NEG_META_E15, NEG_META_E16, NEG_META_E17, NEG_META_E19, NEG_META):
        _md.pop(_n, None)
    src = "e23src/%s.PLI" % _n if os.path.exists("e23src/%s.PLI" % _n) else "e21src/%s.PLI" % _n
    add_spec(_n, (src, "golden/%s/%s/%s.REL" % (_tag, _n, _n)))
# brand-new E2E-20 probes (never refusals -- they were written to pin the span fix and the
# multiply route), each with a DR golden from golden/e2e227 and golden/e2e228.
for _n, _tag in [("AB18", "e2e227"), ("AB22", "e2e228"), ("AB23", "e2e228")]:
    add_spec(_n, ("e23src/%s.PLI" % _n, "golden/%s/%s/%s.REL" % (_tag, _n, _n)))
# [E2E-20/Priority 5] runtime-witnessed array programs.  All three are byte-identical to DR
# AND link+run to output IDENTICAL to DR's own .COM (golden/e20mine_r vs golden/e229_r), and to
# the values I computed by hand before running:
#   RT2  dcl a(0:3) fixed, t fixed  -> "1027 1283 1539 1795 5"
#        (explicit lower bound respected; the scalar AFTER the array is untouched)
#   RT3  outer w(3) + inner w(2), same NAME in two scopes, with a call in between
#        -> "1031 1287 13" then "259 515 771 9"
#        (the discriminating witness for the callee scope-swap: if the inner block resolved
#        against the caller's extents, w(1)/w(2) would land on the outer array and these
#        eight numbers could not come out right -- and the outer values would be clobbered)
#   RT4  a(2)=b (form 3) ; a(2)=a(2)+5 (form 4) ; a(4)=b+1 (form 3) ; c=a(2)+a(4) (park route)
#        -> "22 18 40"   (17 -> 22 via self-update, 18, sum 40)
for _n in ["RT2", "RT3", "RT4"]:
    add_spec(_n, ("e23src/%s.PLI" % _n, "golden/e2e229/%s/%s.REL" % (_n, _n)))

# [E2E-20/Priority 2] WHOLE-ARRAY USE -- class dr-refuses: DR itself emits no .REL for these
# (pass 1 clean, pass 2 `TYPES NOT=' -- golden/e2e230), and before this milestone MY compiler
# ACCEPTED all three and stored/loaded the array's BASE CELL as a scalar value.  That is a
# wrong-value miscompile, so the refusal is required for compatibility, not merely for hygiene.
for _n in ["GW1", "GW2", "GW3"]:
    REJECTS[_n] = (open("e23src/%s.PLI" % _n, "rb").read()
                   .replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   "whole-array reference")
NEG_META["GW1"] = ("dr-refuses",
    "DR rejects `b = a' in pass 2 with TYPES NOT= (golden/e2e230/GW1, NO .REL) [C159]. "
    "Mine previously ACCEPTED it and read the array's base cell as a scalar -- wrong value, "
    "not wrong bytes.  Now refuses via addr_of/vk_of, which is where every un-subscripted "
    "data reference flows [E2E-20 Priority 2 negative witness].")
NEG_META["GW2"] = ("dr-refuses",
    "DR rejects `a = 3' the same way (golden/e2e230/GW2, NO .REL).  Same guard, opposite "
    "direction: a store through an array name with no subscript.")
NEG_META["GW3"] = ("dr-refuses",
    "DR rejects `put skip list(a)' (golden/e2e230/GW3, NO .REL): 1 ERROR IN PASS 2.  Covers "
    "the PUT-item route, which asks vk_of and would otherwise print 2 bytes of element 1.")
# AB11 now refuses inside the CONDITION classifier rather than the assignment route, so its
# pinned marker moves to the new reason.  NB the condition path's message still RENDERS the
# subscripted name as `call a[1]' -- a diagnostic wart, not a behaviour claim: the element is
# resolved correctly everywhere the bytes are decided [C169].
# [E2E-22] AB2/AB8/AB10 are REMOVED from this list: they compile byte-exact now and were
# promoted to specimens below, which is the only sanctioned way to retire a negative [C154].
# ARRAY and PASSARAY keep their slot but their pinned reason moves -- the variable-subscript gap
# closed, so each now stops on its own NEXT missing mechanism (PUT EDIT, element-as-actual).
for _n, _mk in [("ARRAY", "PUT form not in E2E-3a subset"),
# [E2E-22] removed: PASSARAY

                ("AB7", "main-block statement after an appended procedure"),
                ("EA1", "main-block statement after an appended procedure"),
                ("AB14", "main-block statement after an appended procedure"),
                ("AB11", "(> ")]:
    if _n in REJECTS:
        # pop FIRST, deliberately: NoOverwriteDict refuses in-place assignment because a taken
        # name is normally a COLLISION [C163].  Here the source text is unchanged and only the
        # pinned marker moves to the new refusal reason, which is exactly the case the guard
        # names as a deliberate retirement -- so it is spelled as one.
        _src, _old = REJECTS.pop(_n)
        REJECTS[_n] = (_src, _mk)
        if _n in NEG_META:
            _cls, _note = NEG_META.pop(_n)
            NEG_META[_n] = (_cls, _note + "  [E2E-20 marker updated: the route moved, "
                            "so the pinned reason now names %r]" % _mk)

# ---------------------------------------------------------------------------
# [E2E-22/P1+P2] VARIABLE-INDEX ARRAY ADDRESSING -- byte-exact
# ---------------------------------------------------------------------------
# DR's address ladder, measured on AB2/AB8/AB10 + two new probes VB1/VB2 that exist ONLY to
# discriminate the lower-bound operand and the two ladder forms:
#   operand = base - lower_bound * element_size
#     VB1 lb=0 -> addend 0x0000     VB2 lb=2 -> addend 0xFFFC     AB2 lb=1 -> addend 0xFFFE
#   which RULES OUT the [C159] wording `base + (lb-1)*(-sz)' -- three goldens, three different
#   bounds, one arithmetic fact.
# Two forms, selected by whether the operand is the plain base:
#   bias 0  (VB1): LHLD idx ; DAD H ; LXI D,<base> ; DAD D                (no stack traffic)
#   bias<>0 (AB2 VB2 AB8 AB10):
#            LXI H,<biased> ; PUSH H ; LHLD idx ; DAD H ; POP D ; DAD D    (C141 parking)
# Index expressions: AB8 `a(i+1)' emits `LHLD i / INX H / DAD H', i.e. DR adjusts the INDEX VALUE
# before doubling, so +1 moves exactly one element.  Only +1 is measured; `i+k' and every other
# expression form still refuses [C159].
# Read tail `MOV E,M / INX H / MOV D,M' lands the value in DE; the DR continuations (AB2 `XCHG /
# SHLD b', AB8/AB10 `XCHG / MVI A,09' PUT tail) show DR normalizing to HL with XCHG, which is what
# lets every existing consumer work unchanged.  Store tails: literal `MVI M,lo / INX H / MVI M,hi'
# (AB2 VB1 VB2); computed `PUSH H / <ladder> / POP D / MOV M,E / INX H / MOV M,D' (AB8 AB10),
# where the ladder's own parking pair nests inside the value's parking pair.
for _n in ["AB2", "AB8", "AB10"]:
    REJECTS.pop(_n, None)
    NEG_META.pop(_n, None)
    NEG_META_E19.pop(_n, None)
    _d, _t = _E17_REFS[_n]
    add_spec(_n, ("%s/%s.PLI" % (_d, _n), "golden/%s/%s/%s.REL" % (_t, _n, _n)))
for _n in ("VB1", "VB2"):
    add_spec(_n, ("e24src/%s.PLI" % _n, "golden/e2e231/%s/%s.REL" % (_n, _n)))
# [E2E-22/P3] element-as-actual: EA2 is the Checkpoint C witness.  It passes a CONSTANT-index
# element and a VARIABLE-index element to the same procedure, whose body does `x = x + 100'.
# My .REL is byte-exact against DR [golden/e2e235/EA2], and both linked .COMs print
# "106 100" -- a(4) 6->106 and a(i)=a(2) 0->100 -- so the callee demonstrably mutated the
# ORIGINAL cells.  DR's route is the ordinary pointer-formal descriptor [C130]: LXI H,<element>
# ; SHLD <desc> (constant, AB7) and <ladder> ; SHLD <desc> (variable, PASSARAY).  bind gives an
# element actual NO temporary value cell, unlike a call actual [C145], which is why the
# anonymous-cell numbering still matches -- a temp would have added a DATA byte and shifted every
# later cell.
add_spec("EA2", ("golden/e2e235/EA2/EA2.PLI" if os.path.exists("golden/e2e235/EA2/EA2.PLI")
                 else "e24src/EA2.PLI", "golden/e2e235/EA2/EA2.REL"))
# [E2E-22/P4] ARRAY and PASSARAY leave the negative panel: PASSARAY is byte-exact (promoted
# above) and ARRAY compiles with DR-identical runtime output but non-exact bytes (DIVERGENT
# panel).  Both their REJECTS and their NEG_META/NEG_META_E17 rows must go -- the registration
# guard treats a REJECTS/NEG_META asymmetry as lost verdict evidence, and it is right: a note with
# no verdict behind it, or a verdict with no note, is exactly how a silent acceptance happens
# [C163/C171].
for _n in ("ARRAY", "PASSARAY"):
    REJECTS.pop(_n, None)
    NEG_META.pop(_n, None)
    NEG_META_E17.pop(_n, None)

# [E2E-22/P4] N4_SKIPVAR -- an E2E-8-era inline negative (`put skip(a) list(\'X\')\', "PUT form")
# -- is promoted by the SAME rule, independently: my .REL is byte-identical to DR's golden
# [golden/negpanel1/NG36/NG36.REL], which was built through a different batch than SK3/SK4.  Two
# separate DR goldens agreeing on `LHLD a / MOV A,L / CALL ?SKPOP' is worth more than one probe,
# and it is the only sanctioned way to retire a negative [C154].  The source is now committed as
# e24src/N4_SKIPVAR.PLI (space-indented, no TAB [C170]) because add_spec needs a real path.
REJECTS.pop("N4_SKIPVAR", None)
NEG_META.pop("N4_SKIPVAR", None)
add_spec("N4_SKIPVAR", ("e24src/N4_SKIPVAR.PLI", "golden/negpanel1/NG36/NG36.REL"))

# [E2E-22/P4] PUT SKIP with a RUNTIME count.  SK1/SK2 pin that the literal and string forms are
# unchanged (they were already byte-exact [G107/G108/N302]); SK3/SK4 pin DR's expression form
# `LHLD one / MOV A,L / CALL ?SKPOP' -- only the LOW byte, the same 8-bit quantity the immediate
# carries.  This single shape was all that stood between the compiler and both PLI-2000
# integration programs.
for _n in ("SK1", "SK2", "SK3", "SK4"):
    add_spec(_n, ("e24src/%s.PLI" % _n, "golden/e2e238/%s/%s.REL" % (_n, _n)))
# [E2E-22/P4] DO ... TO <formal> and DO ... FROM <formal> DREREERENCE the pointer cell.  Before
# this was fixed both sides silently used the ADDRESS as the bound -- a wrong-value miscompile:
# PASSARAY printed 69900 lines where DR prints 75, ARRAY 139580 vs 75 (linked and run, measured).
# DR's tail is the ordinary pointer-formal deref [C130]: MOV E,M / INX H / MOV D,M / XCHG.
for _n in ("DO1", "DO2"):
    add_spec(_n, ("e24src/%s.PLI" % _n, "golden/e2e239/%s/%s.REL" % (_n, _n)))
# ---------------------------------------------------------------------------
# [E2E-23/C176] DR's ZERO-STORE FORM and its ONE tracked accumulator fact.
# Twelve probes, all byte-exact, measure when DR writes `XRA A / MOV M,A / INX H / MOV M,A'
# (4 bytes) instead of `MVI M,00 / INX H / MVI M,00' (5 bytes).  ZS11/ZS12 are additionally
# linked and RUN, which is what makes the counterexamples semantic rather than cosmetic.
#   ZS1  a(3)=0                      -> XRA pair.  Note this is the CONSTANT-index route: the
#        form is not specific to pointer formals (E26A had suggested it was).
#   ZS2  two consecutive zero stores -> ONE XRA, four MOV M,A: the fact crosses a statement
#        boundary and survives `LXI H,<addr>'.
#   ZS4  zero ; b=5 ; zero           -> ONE XRA: survives `LXI H,0005 / SHLD b'.
#   ZS9  zero ; i=2 ; a(i)=0         -> ONE XRA: survives the ENTIRE variable-index ladder
#        (LXI H / PUSH H / LHLD / DAD H / POP D / DAD D) [measured, so the ladder is A-neutral].
#   ZS10 zero ; a(4)=7 ; zero        -> ONE XRA, but the 7 STILL uses `MVI M,07 / INX H /
#        MVI M,00'.  COUNTEREXAMPLE to "always XRA": the choice is made per store from the whole
#        2-byte constant, and a nonzero store neither uses nor disturbs A.  RUNTIME: `0 0 5'
#        identical to DR, so the reused A really held 0 and b was untouched.
#   ZS5  zero ; call q ; zero        -> TWO XRA.  COUNTEREXAMPLE: a call invalidates.  This is
#        C141 at byte level, and ZS12 (same shape, printing) runs to `0 0' exactly as DR does --
#        had the tracker reused A across the call, the value would depend on q's accumulator.
#   ZS7  zero ; put ... ; zero       -> TWO XRA: `MVI A,n' / `LDA' style writes invalidate.
#   ZS8  zero ; if i>1 then b=2 ; zero -> TWO XRA: the compare writes A (and the branch is a
#        merge); the implementation invalidates at both, so it cannot be wrong in either reading.
#   ZS3  a(i)=0 (variable index)     -> XRA pair, i.e. ARRAY's own site.
#   ZS6  do i=1 to 3; a(i)=0; end    -> ONE XRA inside the loop body (re-executed, so correct).
# Corpus cross-check BEFORE implementing: across 1310 DR .REL files, `MVI M,00' appears in 51 but
# the all-zero PAIR `36 00 23 36 00' appears in NONE, while `AF 77 23 77' appears in exactly three
# distinct programs (E26A, ARRAY, ALLTST) -- always as two paired stores from a single XRA.  That
# survey is what said the rule was narrow and value-triggered rather than a general peephole.
for _n in ("ZS1", "ZS2", "ZS3", "ZS4", "ZS5", "ZS6",
           "ZS7", "ZS8", "ZS9", "ZS10", "ZS11", "ZS12"):
    add_spec(_n, ("e24src/%s.PLI" % _n, "golden/e2e240/%s/%s.REL" % (_n, _n)))
# ---------------------------------------------------------------------------
# [E2E-23/P3] DR's HL-REUSE forms, measured by ZK1-ZK12 on ONE fact: HL holds a known CONSTANT.
# AB19/AB21/RT1 are the programs this came from; all three are now byte-identical AND were linked
# and run.  The forms, each from a dedicated probe:
#   ZK1 1->2 INX H | ZK4 2->1 DCX H | ZK3/ZK7 +256 INR H | ZK9 -256 DCR H
#   ZK2 1->5 MVI L,05 (only the low byte changes) | R610/LOAN1 repeat -> no reload at all
#   ZK12 array element at offset 0 then a scalar: the element store sits INSIDE the chain.  That
#        is AB19's shape, and it is what forced hl_const to be shared instead of duplicated.
#   ZK5 reuse interrupted by CALL -> DR reloads (C141's no-parking rule, at byte level).
#   ZK6 reuse interrupted by a byte-store element write, where HL becomes the element ADDRESS ->
#        DR reloads; RT1's own a(2)/a(3)/a(4) stores show the same, which is why address-bearing
#        HL never carries the fact.
# ZK8/ZK10/ZK11 are deliberately NOT specimens: they diverge on an UNRELATED cause (DR routes
# out-of-range literals through a runtime call), so they are pinned in DIVERGENT.txt instead.
for _n in ("ZK1", "ZK2", "ZK3", "ZK4", "ZK5", "ZK6", "ZK7", "ZK9", "ZK12"):
    add_spec(_n, ("e24src/%s.PLI" % _n, "golden/e2e241/%s/%s.REL" % (_n, _n)))
# [E2e23/P3] AB19/AB21/RT1 promoted out of the divergence panel.  Their remaining cause was NOT
# the broad C168 peephole E2E-22 assumed: AB19/AB21 were my element route failing to carry the
# HL-constant fact, and RT1 was a missing INR H arm.  Runtime, mine vs DR's own .COM built from
# DR's own .REL: `2 1 3', `5 1 9', `257 513 769 1025 1281 1537' -- identical in all three.
for _n, _t in (("AB19", "e2e227"), ("AB21", "e2e228"), ("RT1", "e2e229")):
    add_spec(_n, ("e23src/%s.PLI" % _n, "golden/%s/%s/%s.REL" % (_t, _n, _n)))
# NB: specimens get NO NEG_META row -- that dict is negative evidence only, and the registration
# guard refuses a REJECTS/NEG_META asymmetry because an unmatched entry silently changes what a
# verdict means [C163-class bug; caught by the guard, not by review].

# AB19 / AB21 are deliberately registered NOWHERE: they compile but are not byte-exact, because
# DR applies cross-statement constant-reuse peepholes I do not implement (`LXI H,v ; SHLD ;
# INX H ; SHLD' and `MVI L,k').  Registering a known-diverging program as either a specimen or a
# refusal would be a lie: it is not exact, and it does not refuse.  They are recorded as the
# evidence for C168 instead.

# ---------------------------------------------------------------------------
# [E2E-21/P0] SAFETY + EVIDENCE CORRECTIONS
# ---------------------------------------------------------------------------
# (a) Five corpus programs used to die with a BARE exception -- rc != 0 but no [TBD] -- which the
#     sweep counted as REFUSED and therefore hid.  rc!=0 is not evidence [C158 lesson]; [TBD] is.
#     Fixed: bind.ml's statement walker gained Salloc/Sfree arms (REVERSE, NETWORK hit a
#     Match_failure before codegen could refuse); codegen's PUT matcher gained refusals for a PUT
#     naming a FILE stream (KEYFILE) or ON options (CREATE) instead of falling off the match; and
#     two "codegen: undeclared <name>" failwiths got the [TBD] wording (REVERT: `call p(i,exit)',
#     a label used as a value).  None of this implements ALLOCATE/FREE or file I/O -- each names
#     the missing mechanism.  Registered as negatives so the fix stays tested:
# NB the five CORPUS programs that exposed these sites (REVERSE NETWORK CREATE KEYFILE REVERT)
# are deliberately NOT panel entries: their sources contain TABs, and the committed inventory is
# tab-separated, so registering them produced a malformed row -- which the gate caught by aborting
# rather than by accepting a corrupt file.  They stay visible in the sweep; these three
# space-indented probes pin the same three code sites mechanically.
# Also note PU1's finding: the PARSER records `put file(f) list(x)' as an ON OPTION, not as a
# stream, so the "ON options" arm is what a named-file PUT reaches.  Wording left as-is rather
# than rebuilt over at the end of a gated milestone; recorded here so it is not rediscovered.
for _n, _marker in [("AV1", "allocate(...)' where p is a POINTER is refused by DR itself [TBD]"),  # [E2E-26] AV1 is `p = allocate(10); free p;`: DR itself gives NO DCL + ARG COUNT + BASED REQ and no .REL (golden/e26av2/AV1/AV1.PRN), so this is a double refusal, now labelled with the statement-vs-expression reason rather than the old generic POINTER-layout message
                    ("PU1", "PUT LIST with ON options"),  # named-file PUT: outer match no catch-all
]:                       # (a third probe for the "undeclared" site would not PARSE cleanly;
                                                       # REVERT covers it in the sweep instead)
    _src = "e24src/%s.PLI" % _n
    if _n in REJECTS or _n in SPECIMENS:
        raise RegistrationCollision("%s already registered -- do not re-add [C163]" % _n)
    REJECTS[_n] = (open(_src, "rb").read().replace(b"\r\n", b"\n")
                   .rstrip(b"\x1a").decode(), _marker)
    NEG_META[_n] = ("my-gap",
        "Was a BARE crash (rc!=0, no [TBD]), which the corpus sweep counted as REFUSED and thus "
        "hid. Now a reasoned refusal; the underlying gap (%s) remains. [E2E-21/P0]" % _marker)

# (b) Divergence panel: programs that COMPILE but are NOT byte-exact [C168].  They belong to
#     neither regression panel -- a negative would claim a [TBD] that never happens, a specimen
#     would fail -- so they get a third, mechanically checked inventory, spec/DIVERGENT.txt.
#     Each row pins mine_code/dr_code/data/ndiff: if a change moves the divergence shape, or
#     makes one of these byte-exact (then it must be promoted) or makes one refuse (then it is
#     stale), the gate stops rather than letting it drift silently.
DIVERGENT_FILE = os.path.join(ROOT, "spec", "DIVERGENT.txt")

# [E2E-24/C178] DR's out-of-range FIXED literal route (decimal pool cell + ?DLDOP/?QDI15),
# implemented at the store, at both ADD operand orientations (incl. self-add, which falls through
# the measured -8..+16 ladder to the same parked form LP14 shows DR using), and at SUB with a
# plain-identifier left operand (`POP D / CALL ?IS22N', measured on LQ5/LP9/ML8).  Every byte-exact
# probe is registered here.  [E2E-25] LP8/LQ2/LQ4 were the first divergences CLOSED, and the rule
# that closed them is the NEGATIVE decimal cell: DR folds the minus into the cell (ten's complement
# in p digits, final sign nibble 9) rather than loading the magnitude and calling ?IN20N, so mine's
# truncated `LXI H,imm / CALL ?IN20N' silently COMPLETED where DR aborts.  With the signed cell all
# three are byte-identical AND their executed output matches DR's byte for byte, traceback words
# included (golden/e2e290m) -- which also disproves the earlier note that their traceback difference
# was cosmetic: it was a code-size artefact of the truncation.  The remaining shapes stay in
# spec/DIVERGENT.txt with measured bytes and are WRONG-VALUE rows, not cosmetic differences.  Refusals are pre-designed [TBD] guards with DR
# goldens in NEG_META -- none is a pool-invariant failure.
# [E2E-25] the completed ADD/SUB matrix.  Both operators, both sides, both signs, parenthesised or
# not -- every cell pinned by its own DR golden (batches e2e292d / e2e293d), because [C167] says a
# rule verified in only the orientation that hides its bug is not verified.  LR2 also proves the
# leading-zero digit-count rule survives being an ADD operand (`x + 0123456789' = p=10, 6-byte cell).
add_spec('LR2', ('artefacts/LR2.PLI', 'golden/e2e292d/LR2/LR2.REL'))
add_spec('LR3', ('artefacts/LR3.PLI', 'golden/e2e292d/LR3/LR3.REL'))
add_spec('LR11', ('artefacts/LR11.PLI', 'golden/e2e292d/LR11/LR11.REL'))
add_spec('LR17', ('artefacts/LR17.PLI', 'golden/e2e293d/LR17/LR17.REL'))
add_spec('LR18', ('artefacts/LR18.PLI', 'golden/e2e293d/LR18/LR18.REL'))
add_spec('LR19', ('artefacts/LR19.PLI', 'golden/e2e293d/LR19/LR19.REL'))
add_spec('LP1', ('artefacts/LP1.PLI', 'golden/e2e246/LP1/LP1.REL'))
add_spec('LP8', ('artefacts/LP8.PLI', 'golden/e2e246/LP8/LP8.REL'))
add_spec('LP14', ('artefacts/LP14.PLI', 'golden/e2e246/LP14/LP14.REL'))
add_spec('LP15', ('artefacts/LP15.PLI', 'golden/e2e246/LP15/LP15.REL'))
add_spec('LP2', ('artefacts/LP2.PLI', 'golden/e2e246/LP2/LP2.REL'))
add_spec('LP4', ('artefacts/LP4.PLI', 'golden/e2e246/LP4/LP4.REL'))
add_spec('LP5', ('artefacts/LP5.PLI', 'golden/e2e246/LP5/LP5.REL'))
add_spec('LP6', ('artefacts/LP6.PLI', 'golden/e2e246/LP6/LP6.REL'))
add_spec('LP9', ('artefacts/LP9.PLI', 'golden/e2e246/LP9/LP9.REL'))
add_spec('LQ1', ('artefacts/LQ1.PLI', 'golden/e2e247/LQ1/LQ1.REL'))
add_spec('LQ2', ('artefacts/LQ2.PLI', 'golden/e2e247/LQ2/LQ2.REL'))
add_spec('LQ3', ('artefacts/LQ3.PLI', 'golden/e2e247/LQ3/LQ3.REL'))
add_spec('LQ4', ('artefacts/LQ4.PLI', 'golden/e2e247/LQ4/LQ4.REL'))
add_spec('LQ5', ('artefacts/LQ5.PLI', 'golden/e2e247/LQ5/LQ5.REL'))
add_spec('LQ6', ('artefacts/LQ6.PLI', 'golden/e2e247/LQ6/LQ6.REL'))
add_spec('LQ7', ('artefacts/LQ7.PLI', 'golden/e2e247/LQ7/LQ7.REL'))
add_spec('LQ8', ('artefacts/LQ8.PLI', 'golden/e2e247/LQ8/LQ8.REL'))
add_spec('LQ9', ('artefacts/LQ9.PLI', 'golden/e2e247/LQ9/LQ9.REL'))
add_spec('LQA', ('artefacts/LQA.PLI', 'golden/e2e247/LQA/LQA.REL'))
add_spec('ML1', ('artefacts/ML1.PLI', 'golden/e2e244/ML1/ML1.REL'))
add_spec('ML10', ('artefacts/ML10.PLI', 'golden/e2e244/ML10/ML10.REL'))
add_spec('ML11', ('artefacts/ML11.PLI', 'golden/e2e244/ML11/ML11.REL'))
add_spec('ML12', ('artefacts/ML12.PLI', 'golden/e2e244/ML12/ML12.REL'))
add_spec('ML13', ('artefacts/ML13.PLI', 'golden/e2e244/ML13/ML13.REL'))
add_spec('ML14', ('artefacts/ML14.PLI', 'golden/e2e244/ML14/ML14.REL'))
add_spec('ML15', ('artefacts/ML15.PLI', 'golden/e2e244/ML15/ML15.REL'))
add_spec('ML2', ('artefacts/ML2.PLI', 'golden/e2e244/ML2/ML2.REL'))
add_spec('ML3', ('artefacts/ML3.PLI', 'golden/e2e244/ML3/ML3.REL'))
add_spec('ML4', ('artefacts/ML4.PLI', 'golden/e2e244/ML4/ML4.REL'))
add_spec('ML5', ('artefacts/ML5.PLI', 'golden/e2e244/ML5/ML5.REL'))
add_spec('ML8', ('artefacts/ML8.PLI', 'golden/e2e244/ML8/ML8.REL'))
add_spec('ML9', ('artefacts/ML9.PLI', 'golden/e2e244/ML9/ML9.REL'))
add_spec('MN1', ('artefacts/MN1.PLI', 'golden/e2e245/MN1/MN1.REL'))
add_spec('MN2', ('artefacts/MN2.PLI', 'golden/e2e245/MN2/MN2.REL'))
add_spec('MN3', ('artefacts/MN3.PLI', 'golden/e2e245/MN3/MN3.REL'))
add_spec('MN4', ('artefacts/MN4.PLI', 'golden/e2e245/MN4/MN4.REL'))
add_spec('MN5', ('artefacts/MN5.PLI', 'golden/e2e245/MN5/MN5.REL'))
add_spec('MN6', ('artefacts/MN6.PLI', 'golden/e2e245/MN6/MN6.REL'))
add_spec('MN7', ('artefacts/MN7.PLI', 'golden/e2e245/MN7/MN7.REL'))
add_spec('MN8', ('artefacts/MN8.PLI', 'golden/e2e245/MN8/MN8.REL'))
# [E2E-25/C161] `i = i + d' with d dec(9,0): the SELF-ADD form of mixed DEC/BIN.  It reaches the same
# conversion (DEC operand on the RIGHT: LHLD I / PUSH H / LXI H,D / MVI A,09 / ?DLDOP / ?QDI15 /
# POP D / DAD D) and is byte-identical to DR's NG14 [golden/negpanel1/NG14], so it leaves the negative
# panel -- the refusal it made WAS C161's gap, and that gap is closed for this shape.  Source is
# negsrc/NG14.PLI, the file DR's golden was compiled from, so the program name in the LINK header
# matches too (comparing a renamed copy looked like a 120-byte divergence and is not evidence).
add_spec('N29_DECININT', ('negsrc/NG14.PLI', 'golden/negpanel1/NG14/NG14.REL'))
for _n, _g in (('ZK8','golden/e2e241/ZK8/ZK8.REL'),('ZK10','golden/e2e241/ZK10/ZK10.REL'),('ZK11','golden/e2e241/ZK11/ZK11.REL')):
    add_spec(_n, ('e24src/%s.PLI' % _n, _g))
REJECTS['LP10'] = (open('artefacts/LP10.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), '] (line 3)")')
REJECTS['LP13'] = (open('artefacts/LP13.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), '] FIXED multiply by literal 32768 >= 327')
REJECTS['LP3'] = (open('artefacts/LP3.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), '].  Note this is ADD-specific: `j = 0 -')
REJECTS['LP7'] = (open('artefacts/LP7.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), ']")')
REJECTS['ML6'] = (open('artefacts/ML6.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), ']")')
REJECTS['ML7'] = (open('artefacts/ML7.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), ']")')

# [E2E-25] the out-of-range-literal witnesses.  Byte-identical .RELs already imply an identical
# .COM, but for these the DIVERGENCE WAS THE RUNTIME BEHAVIOUR -- DR aborts with `ERROR (1),
# Conversion' where mine used to finish silently -- so the gate itself must re-link and re-run BOTH
# arms and compare console output, not merely cmp bytes [C137/C173: only executed output is
# evidence].  This block sits AFTER every add_spec on purpose and ASSERTS membership: an earlier
# version ran before the registrations behind `if _n in SPECIMENS', so it silently added nothing and
# the link-run arm stayed mine-only.  A defensive membership test is the wrong shape here -- a name
# that is not a specimen must stop the gate, not be skipped [C163].
for _n in ("LP1", "LP5", "LP8", "LP14", "LP15", "LQ2", "LQ4", "LQ5", "LQA",
           "LR2", "LR3", "LR11", "LR17", "LR18", "LR19",
           "ML1", "ML3", "ML4", "ML8", "ML15", "ZK8", "ZK10", "ZK11",
           "CB1", "CB2", "CB3", "CB4", "CB5", "CB7", "CONV", "DECY"):
    # N29_DECININT (negsrc/NG14.PLI) is deliberately NOT here: its source has no `put', so there is
    # no console behaviour to compare, and DR's negative-panel golden stores no run transcript -- the
    # harness reports "MISSING TRANSCRIPT", which is true but uninformative.  Listing it would teach
    # the next reader to ignore that line, and the line exists to be trusted.  Its evidence is the
    # byte-identical .REL plus the fact that CONV/CB1 already pin the same conversion at run time.
    assert _n in SPECIMENS, "output-check name %s is not a specimen" % _n
    OUTPUT_CHECK.add(_n)



# [E2E-25] P0: every position where an out-of-range FIXED literal used to be truncated into a
# wrapped 16-bit immediate is now an honest [TBD] refusal, each pinned by the DR .REL it declines to
# reproduce and by a marker fragment taken from the compiler's ACTUAL stderr, not from a guess.
# Before this block existed all of these BUILT: DR aborts at run time with `ERROR (1), Conversion'
# while mine stored the wrapped value, branched on it, or passed it to a callee -- [C168]'s
# wrong-value panel, closed by refusing rather than by shipping a silent mis-compile.  Positions with
# a measured DR route (scalar store, and ADD/SUB in both orientations and both signs) convert for
# real and are SPECIMENS; these are the ones with no DR golden for MY route, so the choice was
# refusal, per [C139/C141]: a refusal is evidence, a silent mis-compile is not.
REJECTS['LP11'] = (open('artefacts/LP11.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a condition / DO-bound comparison constant')
REJECTS['LP12'] = (open('artefacts/LP12.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in an array element store')
REJECTS['LP16'] = (open('artefacts/LP16.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a procedure-call argument')
REJECTS['LR1'] = (open('artefacts/LR1.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'TWO INTEGER LITERALS')
REJECTS['LR10'] = (open('artefacts/LR10.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'FIXED multiply by literal')
REJECTS['LR12'] = (open('artefacts/LR12.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a position lowered straight into HL')
REJECTS['LR14'] = (open('artefacts/LR14.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a procedure-call argument')
REJECTS['LR15'] = (open('artefacts/LR15.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'PUT form not in E2E-3a subset')
REJECTS['LR4'] = (open('artefacts/LR4.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a condition / DO-bound comparison constant')
REJECTS['LR5'] = (open('artefacts/LR5.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in a DO-loop TO bound')
REJECTS['LR6'] = (open('artefacts/LR6.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in an array element store')
REJECTS['LR7'] = (open('artefacts/LR7.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in an array element store')
REJECTS['LR8'] = (open('artefacts/LR8.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'in an array element self-update')
REJECTS['LR9'] = (open('artefacts/LR9.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'condition form not in E2E-3b subset')

NEG_META.update({
    'LP11': ("my-gap", "DR compiles it (golden/e2e246/LP11/LP11.REL). LP11 is `if x > 32768 then y = 1' -- DR converts the comparison constant through a decimal cell (`LXI H,*S / MVI A,05 / ?DLDOP / ?QDI15 / XCHG / LHLD x / CALL ?IS22N / JP') and ABORTS at run time with `ERROR (1), Conversion', so the branch is never taken.  Mine used to bias HL by -(32768+1), which wraps to +32767, made the test come out TRUE, and EXECUTED the body: a branch DR never reaches.  The condition route is unmeasured beyond DR's single sample, so the position now refuses [C168]."),
    'LP12': ("my-gap", "DR compiles it (golden/e2e246/LP12/LP12.REL). LP12 is `z(1) = 32768' with `z(3) fixed'.  DR converts (`LXI H,*S / MVI A,05 / ?DLDOP / ?QDI15 / SHLD Z') and aborts; mine stored a wrapped 0x8000 silently.  The offset-0 element route is byte-exact in principle, but the pool DEMAND cannot be made: pdec_ctx carries scalar types only, and a `fixed dec(3)' element is also 2 bytes, so prescan cannot tell an element that converts from one that travels the decimal stack -- demanding without allocation is the [C179] failure, so the position refuses until that type plumbing exists."),
    'LP16': ("my-gap", "DR compiles it (golden/e2e246/LP16/LP16.REL). LP16 is `call p(32768)'.  DR converts into the anonymous temp cell it creates for the value argument and aborts; mine wrote the wrapped immediate, so p received a truncated value and the program completed.  Call arguments need their own demand site inside the call-argument machinery; unmeasured, so refused."),
    'LR1': ("my-gap", "DR compiles it (golden/e2e292d/LR1/LR1.REL). LR1 is `y = 32768 + 32768' -- out-of-range literals on BOTH operands.  DR compiles it (golden/e2e292d/LR1), converting each; mine refuses with its pre-existing designed guard (fixed-bin ADD of two integer literals is not constant-folded by DR).  Not a wrong-value route: a refusal, with DR's .REL as evidence."),
    'LR10': ("my-gap", "DR compiles it (golden/e2e292d/LR10/LR10.REL). LR10 is `y = 32768 * 2' -- out-of-range literal on the LEFT of a multiply.  Refused by the pre-existing MB31-family threshold guard, which measures the multiply route only for literals below 32768 (LP13 is its mirror image on the right)."),
    'LR12': ("my-gap", "DR compiles it (golden/e2e292d/LR12/LR12.REL). LR12 is `y = 100000 / 3' -- the dividend literal.  DR's code is far longer (384 bytes vs mine 256), because it converts the constant before the divide; mine truncated it.  DIV/MUL operands reach lower_hl's plain immediate path, which is now the general choke-point guard."),
    'LR14': ("my-gap", "DR compiles it (golden/e2e292d/LR14/LR14.REL). LR14 is `y = f(32768)' -- an out-of-range literal as a FUNCTION argument, i.e. LP16's shape in an expression rather than a call statement.  Same refusal, separate site, because the temp-cell store for a function call is laid down by different code."),
    'LR15': ("my-gap", "DR compiles it (golden/e2e292d/LR15/LR15.REL). LR15 is `put skip list(x, 32768)' -- an out-of-range literal as a non-final PUT item.  Mine refuses with the pre-existing E2E-3a PUT-subset guard (LP10 is the single-item case); DR converts and aborts."),
    'LR4': ("my-gap", "DR compiles it (golden/e2e292d/LR4/LR4.REL). LR4 is `if x < 32768' -- the other comparison orientation, same position as LP11, same refusal, pinned separately because the jump polarity differs (JP vs JM) and a rule tested on one operator only is not tested [C167]."),
    'LR5': ("my-gap", "DR compiles it (golden/e2e292d/LR5/LR5.REL). LR5 is `do i = 1 to 32768'.  DR converts the bound into a hidden limit cell and aborts; mine biased the loop test by a wrapped -32769, so the loop would have run.  DO bounds share the comparison ladder, and the FROM/TO literal sites are guarded independently."),
    'LR6': ("my-gap", "DR compiles it (golden/e2e292d/LR6/LR6.REL). LR6 is `z(i) = 32768' -- the dynamic-subscript element form.  Same position as LP12, different DR form (PUSH/address arithmetic), so it is pinned on its own rather than assumed."),
    'LR7': ("my-gap", "DR compiles it (golden/e2e292d/LR7/LR7.REL). LR7 is `z(2) = 32768' -- the offset<>0 byte-pair form, which truncated to `MVI M,00 / MVI M,80'.  The guard sits on litv, the one place the element store reads a literal value, so every element form is covered by it."),
    'LR8': ("my-gap", "DR compiles it (golden/e2e292d/LR8/LR8.REL). LR8 is `z(1) = z(1) + 32768' -- element self-update (DR's form 4), where the literal is inside the ADD rather than in the store position.  Restricting the routing predicate to a plain-identifier other operand was not enough: the shape fell into the self-update bias and BUILT with wrong bytes, so the bias constant is checked at its own site."),
    'LR9': ("my-gap", "DR compiles it (golden/e2e292d/LR9/LR9.REL). LR9 is `if z(1) > 32768' -- an ARRAY ELEMENT as a comparison operand.  DR compiles it; mine refuses with the pre-existing E2E-3b condition-subset guard (AB11's family), which fires before the literal check.  Pinned here so the gap has a DR golden and a measured refusal."),
})


# [E2E-25/P5] the INT -> DEC doorway, characterized over seven probes (DR batch e2e309d) so the gap
# has measured edges instead of a guess.  What is ALREADY true: an integer LITERAL into a DEC target
# (IC5 `e = 7') and the sanctioned `decimal(b,5)' builtin (IC7) are byte-exact -- both push through
# ?QI15D on the decimal stack.  What is NOT: an integer VARIABLE or expression reaching a DEC target,
# which DR converts with `CALL ?QI15D' after the value is in HL (IC1's .REL, chain-ext at code 0020).
# That is Q8's gap, unchanged by this milestone and deliberately not implemented from one shape: IC1
# is the direct case, IC2-IC4/IC6 require converting AFTER the binary combine, and DECPOLY/DFACT/
# C162W1..W8 pin the decimal store tightly enough that a change there wants all six goldens at once.
add_spec('IC5', ('artefacts/IC5.PLI', 'golden/e2e309d/IC5/IC5.REL'))
OUTPUT_CHECK.add('IC5')
add_spec('IC7', ('artefacts/IC7.PLI', 'golden/e2e309d/IC7/IC7.REL'))
OUTPUT_CHECK.add('IC7')
REJECTS['IC1'] = (open('artefacts/IC1.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'non-decimal operand')
NEG_META['IC1'] = ("my-gap", "DR COMPILES IT (golden/e2e309d/IC1/IC1.REL).  `e = b': a bare FIXED BINARY variable stored into a FIXED DEC(5) target -- stops on the decimal store's guard `decimal operation on non-decimal operand'.  The missing route is ?QI15D applied to an integer value already in HL, i.e. Q8's gap [E2e-25/P5]: characterized, pinned, not implemented.")
REJECTS['IC2'] = (open('artefacts/IC2.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'non-decimal operand')
NEG_META['IC2'] = ("my-gap", "DR COMPILES IT (golden/e2e309d/IC2/IC2.REL).  `e = d + b': mixed ADD, DEC operand on the LEFT, DEC target -- stops on the decimal store's guard `decimal operation on non-decimal operand'.  The missing route is ?QI15D applied to an integer value already in HL, i.e. Q8's gap [E2e-25/P5]: characterized, pinned, not implemented.")
REJECTS['IC3'] = (open('artefacts/IC3.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'non-decimal operand')
NEG_META['IC3'] = ("my-gap", "DR COMPILES IT (golden/e2e309d/IC3/IC3.REL).  `e = b + d': mixed ADD, DEC operand on the RIGHT, DEC target (CB10's own shape) -- stops on the decimal store's guard `decimal operation on non-decimal operand'.  The missing route is ?QI15D applied to an integer value already in HL, i.e. Q8's gap [E2e-25/P5]: characterized, pinned, not implemented.")
REJECTS['IC4'] = (open('artefacts/IC4.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'non-decimal operand')
NEG_META['IC4'] = ("my-gap", "DR COMPILES IT (golden/e2e309d/IC4/IC4.REL).  `e = b - d': mixed SUB into a DEC target -- stops on the decimal store's guard `decimal operation on non-decimal operand'.  The missing route is ?QI15D applied to an integer value already in HL, i.e. Q8's gap [E2e-25/P5]: characterized, pinned, not implemented.")
REJECTS['IC6'] = (open('artefacts/IC6.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'non-decimal operand')
NEG_META['IC6'] = ("my-gap", "DR COMPILES IT (golden/e2e309d/IC6/IC6.REL).  `e = b * 2': ordinary integer arithmetic whose RESULT must convert to DEC -- stops on the decimal store's guard `decimal operation on non-decimal operand'.  The missing route is ?QI15D applied to an integer value already in HL, i.e. Q8's gap [E2e-25/P5]: characterized, pinned, not implemented.")

# [E2E-26] POINTER storage, scalar BASED read/store, ALLOCATE and FREE.
# Twenty-one probes now agree byte-for-byte with DR, covering: a POINTER's 2-byte
# automatic cell (PD1-PD5), reading through a BASED name (P063B, P071K, PB2, PB19),
# writing a constant and a general value through it (P041 `p->q = 100', PB1, PB18,
# PB21/PB22), pointer re-pointing and copying (PB3, P086M, P067B), and the runtime
# pair `LXI H,<size> / CALL ?ALLOP / SHLD <p>' with `LHLD <p> / CALL ?FREOP'
# (PB7, PB8, PD9).  PB1, PB3 and PB7 were additionally LINKed (LINK 1.31) from MY OWN
# .REL and executed: PB7 prints `x=       100  y=       200 done', PB1 prints
# `a=        11  q=        22  b=        22', PB3 prints `first=        11
# second=        22' -- transcripts under golden/e26my_r and golden/e26my_r2.
# They are NOT in OUTPUT_CHECK: DR stored no run transcript for these batches, and
# listing them would print `MISSING TRANSCRIPT' for a fact that is true but
# uninformative [E2E-25 lesson].  The run evidence is mine-only and labelled so.
add_spec('P063B', ('probes/P063B.PLI', 'golden/e2e310d/P063B/P063B.REL'))
add_spec('P071K', ('probes/P071K.PLI', 'golden/e2e310d/P071K/P071K.REL'))
add_spec('P041', ('probes/P041.PLI', 'golden/e2e310d/P041/P041.REL'))
add_spec('P067B', ('probes/P067B.PLI', 'golden/e2e310d/P067B/P067B.REL'))
add_spec('P086M', ('probes/P086M.PLI', 'golden/e2e310d/P086M/P086M.REL'))
add_spec('PB1', ('artefacts/PB1.PLI', 'golden/e2e311d/PB1/PB1.REL'))
add_spec('PB2', ('artefacts/PB2.PLI', 'golden/e2e311d/PB2/PB2.REL'))
add_spec('PB3', ('artefacts/PB3.PLI', 'golden/e2e311d/PB3/PB3.REL'))
add_spec('PB18', ('artefacts/PB18.PLI', 'golden/e2e315d/PB18/PB18.REL'))
add_spec('PB19', ('artefacts/PB19.PLI', 'golden/e2e315d/PB19/PB19.REL'))
add_spec('PB21', ('artefacts/PB21.PLI', 'golden/e2e315d/PB21/PB21.REL'))
add_spec('PB22', ('artefacts/PB22.PLI', 'golden/e2e315d/PB22/PB22.REL'))
add_spec('PD1', ('artefacts/PD1.PLI', 'golden/e2e311d/PD1/PD1.REL'))
add_spec('PD2', ('artefacts/PD2.PLI', 'golden/e2e312d/PD2/PD2.REL'))
add_spec('PD3', ('artefacts/PD3.PLI', 'golden/e2e312d/PD3/PD3.REL'))
add_spec('PD4', ('artefacts/PD4.PLI', 'golden/e2e313d/PD4/PD4.REL'))
add_spec('PD5', ('artefacts/PD5.PLI', 'golden/e2e313d/PD5/PD5.REL'))
add_spec('PD7', ('artefacts/PD7.PLI', 'golden/e2e316d/PD7/PD7.REL'))
add_spec('PB7', ('artefacts/PB7.PLI', 'golden/e2e311d/PB7/PB7.REL'))
add_spec('PB8', ('artefacts/PB8.PLI', 'golden/e2e311d/PB8/PB8.REL'))
add_spec('PD9', ('artefacts/PD9.PLI', 'golden/e2e316d/PD9/PD9.REL'))

# [E2E-26] DR compiles these; mine refuses because the layout admits only based FIXED
# BINARY(15).  PB6/PB15 want character stores through a pointer (PB6 measures the route:
# `LHLD <p> / LXI D,<text> / MVI A,len / MOV B,A / CALL ?SMCCM'), PB13 wants a decimal
# cell, PB14 a single byte.  Pinned as my-gap so a later slice inherits goldens, not guesses.
REJECTS['PB6'] = (open('artefacts/PB6.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'BASED(P) of type')
NEG_META['PB6'] = ("my-gap", "DR COMPILES IT (golden golden/e2e311d/PB6/PB6.REL).  Based-variable store/read of a non-fixed type refuses at the layout switch; E2E-26/P2 implemented only based FIXED BINARY(15).")
REJECTS['PB13'] = (open('artefacts/PB13.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'BASED(P) of type')
NEG_META['PB13'] = ("my-gap", "DR COMPILES IT (golden golden/e2e314d/PB13/PB13.REL).  Based-variable store/read of a non-fixed type refuses at the layout switch; E2E-26/P2 implemented only based FIXED BINARY(15).")
REJECTS['PB14'] = (open('artefacts/PB14.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'BASED(P) of type')
NEG_META['PB14'] = ("my-gap", "DR COMPILES IT (golden golden/e2e314d/PB14/PB14.REL).  Based-variable store/read of a non-fixed type refuses at the layout switch; E2E-26/P2 implemented only based FIXED BINARY(15).")
REJECTS['PB15'] = (open('artefacts/PB15.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), 'BASED(P) of type')
NEG_META['PB15'] = ("my-gap", "DR COMPILES IT (golden golden/e2e314d/PB15/PB15.REL).  Based-variable store/read of a non-fixed type refuses at the layout switch; E2E-26/P2 implemented only based FIXED BINARY(15).")

# [E2E-26] PB4 (`q = q * 1') and PB20 (`q = q + q') BUILD but do not match DR byte-for-
# byte: both are arithmetic whose operand is itself read through the pointer, and DR's
# register parking for that shape is not yet characterized.  They belong to neither
# specimen nor refusal, so they go to the divergence panel [C168].

# [E2E-27] LEVEL-NUMBERED BASED STRUCTURES.  This corrects E2E-26's conclusion that DR refuses
# them: it does not.  REVERSE (artefacts/REVERSE.PLI) and NETWORK (artefacts/NETWORK.PLI) are
# historical corpus programs declaring `1 wordnode based (sentence), 2 word character(30) varying,
# 2 next pointer' (REVERSE.PLI lines 6-10) and `1 city_node based, ...' (NETWORK.PLI lines 16-22);
# DR compiles BOTH with no errors and a .REL
# (golden/e2e319d/REVERSE/REVERSE.REL -- the first8080u copy stored only the .PRN, so E2E-26 had no
# object to look at).  E2E-26's PB10/PB16/PB17 rejections were bad declaration SPELLINGS, not a
# language limit: ST11 re-runs PB16's `declare nb based(pn) nd' in isolation and DR still refuses it
# (SYNTAX + BASED REQ), so that form genuinely is not in the dialect, while ST1-ST10/ST12 prove the
# level-numbered form is.  These probes are named ST*/LN1 because S1-S13 and W1 are already panel
# keys from earlier milestones -- registering under those keys would have been a SUBSTITUTION, which
# the inventory guard refuses and an equal count would not have shown [C158].
#
# What the six accepted probes pin: members are contiguous from offset 0 with NO alignment padding
# (ST6 = fixed@0, bit(1)@2, fixed@3, allocation size 5); the structure contributes ZERO AUTO STORAGE
# (ST1's block is the pointer alone); qualified access takes its address from the QUALIFIER, not from
# the pointer the record is declared based on (ST3, ST8, and REVERSE's `allocate wordnode
# set(newnode)' followed by `newnode->next'); `free s' and `free p->s' are byte-identical (ST8 vs
# ST1); and a link read yields the stored ADDRESS, which is what makes following a list one read
# rather than an add (ST9, LN1).
#
# LN1 is the milestone's integration witness: two allocated records, FIXED and POINTER members, a
# NULL link, record B's address stored into record A's link, the link followed, B modified through
# it, and both freed.  It is byte-exact AND was LINKed twice -- from my own .REL (golden/e27my/LN1)
# and from DR's (golden/e27dr/LN1) -- then executed under cpmsim.  Both printed
#     first=        11  linked=        22  after=        33  z=        22
# z staying at 22 while `after' reports 33 is the discriminating part: z is an independent value
# copy, so following the link produced B's address rather than the member's address or the record's
# contents.  LN1 is NOT in OUTPUT_CHECK -- DR's batch stores no run transcript -- so the two-run
# comparison is the evidence, and it lives in golden/e27my_r/LN1.output.txt and
# golden/e27dr_r/LN1.output.txt.
add_spec('E27S1', ('artefacts/ST1.PLI', 'golden/e2e323d/ST1/ST1.REL'))
add_spec('E27S3', ('artefacts/ST3.PLI', 'golden/e2e323d/ST3/ST3.REL'))
add_spec('E27S8', ('artefacts/ST8.PLI', 'golden/e2e324d/ST8/ST8.REL'))
add_spec('E27S9', ('artefacts/ST9.PLI', 'golden/e2e324d/ST9/ST9.REL'))
add_spec('E27S10', ('artefacts/ST10.PLI', 'golden/e2e324d/ST10/ST10.REL'))
add_spec('E27LN1', ('artefacts/LN1.PLI', 'golden/e2e325d/LN1/LN1.REL'))

# [E2E-27] DR compiles these; mine refuses because only based FIXED and POINTER members are
# implemented.  The refusal happens AFTER the layout, so member offsets and the record size are
# already bound correctly -- extending this later is a lowering problem, not a layout re-derivation.
REJECTS['E27S7'] = (open('artefacts/ST7.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                  'BASED structure member')
NEG_META['E27S7'] = ("my-gap", "DR COMPILES IT (golden/e2e323d/ST7/ST7.REL). `2 c character(4), 2 a fixed': char(4) at offset 0, fixed at 4, record size 6. Character-member stores through a pointer are unimplemented; PB6 measures the analogous SCALAR form (LHLD <p> / LXI D,text / MVI A,len / MOV B,A / ?SMCCM), which is store_char with LHLD in place of LXI H.")
# [E2E-39/P2] RETIRED: REJECTS['E27S12'] / NEG_META['E27S12'] (a `my-gap' pin, kind=refusal, expected
# 'undeclared i2').  The row's own note said "DR COMPILES IT (golden/e2e324d/ST12/ST12.REL)", and DR's
# listing settles it: line 5 `i2 = 5' is an unqualified write to a member of an internal AUTOMATIC
# structure, PASS 1 and PASS 2 both report NO ERRORS, and a .REL exists (CODE 0042, DATA 0006).  So the
# refusal was never DR behaviour -- it pinned THIS compiler's missing member binding [C248], and the
# row was designed to be noticed when the gap closed.  It has closed: bind now resolves the bare member
# name to the owning structure's cell [C253][C256], the probe compiles, and it moves to DIVERGENT.txt
# against that authentic golden -- remaining difference: DR addresses the member THROUGH the structure
# name (`LXI H,INNER A(0004)') and its DATA area is 6 where mine is 4, while mine reaches the same cell
# directly.  Nothing about BASED members changed: E27S7 (character member) and the unqualified-BASED
# case stay refused, exactly as before.
REJECTS['E27S13'] = (open('artefacts/ST13.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   'main-block statement after an appended procedure')
NEG_META['E27S13'] = ("my-gap", "DR COMPILES IT (golden/e2e324d/ST13/ST13.REL). A REVERSE-SHAPED probe, not REVERSE's skeleton: main calls a nested procedure that allocates into a based record, stores and reads a qualified member and frees it, and main has one statement after the procedure definition. REVERSE additionally uses GET, bare `null', `^=', `return', `do while' and unqualified member access, none of which this probe contains -- so it isolates the procedure-placement blocker and nothing else.  Mine refuses BEFORE any structure work, at the main-block/appended-procedure split, which fixes the ORDER of REVERSE's blockers as measured: (1) nested-procedure statement placement, (2) CHARACTER VARYING member (ST5), (3) GET (REVERSE's `get list(newword)'). The structure machinery behind all three is already byte-exact on ST1/ST3/ST8/ST9/ST10/LN1.")
REJECTS['E27S4'] = (open('artefacts/ST4.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                  'store to unqualified')
NEG_META['E27S4'] = ("my-gap", "DR rejects this probe (golden/e2e323d/ST4: 6 pass-2 errors, NO .REL) and mine refuses too, for a narrower and defensible reason: two bare-based records plus `x = 11' unqualified, which no DR sample supports since NETWORK always writes p->city_name. Registered for the refusal mine can actually defend; the probe needs splitting to attribute DR's six errors.")
REJECTS['E27S11'] = (open('artefacts/ST11.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   'call to unknown nd')
NEG_META['E27S11'] = ("dr-refuses", "E2E-26's PB16 spelling, isolated. DR rejects it: SYNTAX + BASED REQ, NO .REL (golden/e2e324d/ST11/ST11.PRN). So `declare nb based(pn) nd' -- naming a structure type through a based declaration -- is genuinely not a form in this dialect, and E2E-26's inference from PB16/PB17 that based STRUCTURES were unsupported was wrong: the structures are fine, the spelling was not. Mine also refuses, at the binder's statement walker, because `nd' looks like a procedure call.")

NEG_META["E41X4"] = ("my-gap",
    "DR compiles READ of a named file: golden/bind1/KEYFILE/KEYFILE.REL is built from "
    "`read file(input) into(employee) keyto(k)' (KEYFILE.PLI:23) and its record-oriented "
    "chain is ?WNIOP/?RNIOP/?KEYTO.  I refuse; P1 lowers only OPEN, GET LIST and CLOSE.")
NEG_META["E41X5"] = ("my-gap",
    "DR compiles PUT of a named file: golden/e2e11h/E16D/E16D.REL contains "
    "`put file(outf) list('HELLO')' and attaches with mode word 0652H (36 such sites in "
    "spec/lab-evidence/e2e41-p0/SIOMODES.txt).  Mine refuses with the pre-existing PUT-with-"
    "options message, which is true as far as it goes -- the ?OIOOP/?SIOOP route is what is "
    "missing -- and an archived output-file comparison exists in this repository: "
    "golden/e2e11iu/E17D/OUT.DAT, exactly 128 bytes = the 13 payload bytes `'HELLO''    42' "
    "plus 115 x 0x1A.  [E2E-41/P3a] withdraws the explanation this row used to give "
    "(`from an open that spells F(128)'): E17D's OPEN has NO ENVIRONMENT clause, so the "
    "padding has no measured cause here -- observation and hypothesis are separated in "
    "spec/lab-evidence/e2e41-p3/E17D-OUT-DAT.txt [C279].")

# [E2E-28] NESTED PROCEDURE PLACEMENT.  Nine probes that DR accepts and that are byte-exact here.
# Before this milestone, codegen carried two refusals that were presented as DR layout laws:
#   "main-block statement after an appended procedure [TBD] (unproven DR append layout)" and
#   "second appended procedure after a tail guard [TBD] unproven, no multi-procedure golden".
# Neither was a law.  They were inductions over 694 accepted specimens in which every main statement
# happened to precede every procedure, so the single resumption point always WAS the epilogue [R404
# @29->44, P404 @10->2B].  ST13 -- registered as a negative in E2E-27 for exactly that reason -- is
# byte-exact now, which is the C154 condition for removing a negative: its behaviour has a golden of
# its own.  This is the C185 error shape one layer down.
#
# What DR actually does, from golden/e2e330d + e2e332d listings:
#   * every nested-procedure DECLARATION inside a main block emits a 3-byte branch-over (C3 00 00) at
#     the current address, whose operand resolves to where main's emission RESUMES after that body --
#     not to the epilogue in general.  N4: JMP @000C -> 0016 (the `w = 7' after `end sub').  N3 has
#     two declarations and two branches: @0012 -> 0020 (the next declaration) and @0020 -> 002E.
#   * when main's tail is a no-exit loop there is no resumption point and NO branch is emitted --
#     REVERSE: read_it at 001A directly after main's `JMP 0006', write_it at 0091 directly after
#     read_it's always-loop tail.  That is why the old single-guard model looked right.
#   * a nested procedure gets NO prologue of its own (read_it starts at 001A with its first
#     statement), ends with RET when its tail can fall through, and omits the RET when it cannot.
#   * a nested procedure reaches the enclosing block's variables by ABSOLUTE address -- REVERSE's
#     read_it writes `sentence = null' as LXI H,0000 / SHLD SENTENCE A(0016), SENTENCE being the main
#     block's cell.  A local of the same name is a SEPARATE cell (N6: outer W A(000C), inner W
#     A(000E)), which is the binder's scope chain doing its job.
#   * forward CALLs resolve through the existing chain mechanism unchanged (N2 calls before either
#     definition exists).
#   * a bare `RETURN;' emits RET alone and emission CONTINUES with the next statement (N7, REVERSE
#     line 29).
#   * there is NO dead-code suppression after a straight-line STOP: N8 emits `w = 2', the PUT and a
#     second CALL ?STOPX after its first stop, and N10 does the same inside a procedure body.  Both
#     are byte-exact here, so the suppression this compiler used to need is only the consecutive-stop
#     case my earlier probes tripped by having two `stop;' in a row -- which is now what the probes
#     say, not what I assumed they said.
add_spec('E28N1', ('artefacts/N1.PLI', 'golden/e2e332d/N1/N1.REL'))
add_spec('E28N2', ('artefacts/N2.PLI', 'golden/e2e332d/N2/N2.REL'))
add_spec('E28N3', ('artefacts/N3.PLI', 'golden/e2e332d/N3/N3.REL'))
add_spec('E28N4', ('artefacts/N4.PLI', 'golden/e2e332d/N4/N4.REL'))
add_spec('E28N5', ('artefacts/N5.PLI', 'golden/e2e332d/N5/N5.REL'))
add_spec('E28N6', ('artefacts/N6.PLI', 'golden/e2e332d/N6/N6.REL'))
add_spec('E28N8', ('artefacts/N8.PLI', 'golden/e2e331d/N8/N8.REL'))
add_spec('E28N10', ('artefacts/N10.PLI', 'golden/e2e331d/N10/N10.REL'))
for _n in ['E27S13']:            # promoted from refusal to specimen -- pop before re-registering
    REJECTS.pop(_n, None); NEG_META.pop(_n, None)
add_spec('E27S13', ('artefacts/ST13.PLI', 'golden/e2e324d/ST13/ST13.REL'))

# N1 and N4 are the two that matter at runtime, and they were linked and executed twice -- from MY
# .REL (golden/e28my/N1, golden/e28my/N4) and from DR's (golden/e28dr/...) -- with identical output:
#     N1  a=         2      N4  z=         7
# N4 is the discriminator: `sub' is never called, so if the branch-over were missing or mis-aimed,
# main would fall into the body, execute `w = 2' and print 2.  It prints 7 in both executions, which
# is the branch being emitted AND aimed at the right address.  N1 is the converse: the forward CALL
# reaches the body and 2 is what the body stored.  Neither is in OUTPUT_CHECK -- DR's batch stores no
# run transcript -- so the two-run comparison is the evidence, in golden/e28my_r, golden/e28my_r4,
# golden/e28dr_r and golden/e28dr_r4.

# [E2E-28] SIX REFUSALS THAT WERE WAITING ON THE PROCEDURE FIX -- promoted to byte-exact specimens.
# These six are in the panel since E2E-15/E2E-17/E2E-24 as category "my-gap", each with DR's own .REL
# recorded in its prose, and each refused only by the two append-layout rules removed above:
#   ST8  -> golden/e2e160/T8/T8.REL    STACK(2000) + a nested RECURSIVE procedure + stop after the
#                                       appended body
#   ST13 -> golden/e2e162/T13/T13.REL  same append-order gap with STACK(2000) present
#   ST14 -> golden/e2e162/T14/T14.REL  main `stop;' following an appended procedure
#   AB7  -> golden/e2e216/AB7/AB7.REL  append layout (E2E-17 panel)
#   AB14 -> golden/e2e218/AB14/AB14.REL append layout, second body (E2E-17 panel)
#   EA1  -> golden/e2e234/EA1/EA1.REL  append layout (E2E-24 panel)
# All six are byte-identical to those goldens after this milestone's change, verified against the
# pre-existing DR objects -- not against anything added today.
#
# The uncomfortable part, kept because it is the lesson: NEG_META["ST14"] said, in my own words, "DR
# emits the CALL ?STOPX at code 0023, AFTER q's body at 0010-0022.  My rule still refuses it".  A
# refusal whose rationale records the oracle doing the opposite is a bug report, not a design decision
# -- and it sat in the panel for three milestones.  The panel's job is to track DR, so the rule was
# deleted here rather than the sentence re-worded.
for _n, _g in [("ST8", "golden/e2e160/T8/T8.REL"), ("ST13", "golden/e2e162/T13/T13.REL"),
               ("ST14", "golden/e2e162/T14/T14.REL"), ("AB7", "golden/e2e216/AB7/AB7.REL"),
               ("AB14", "golden/e2e218/AB14/AB14.REL"), ("EA1", "golden/e2e234/EA1/EA1.REL")]:
    REJECTS.pop(_n, None); NEG_META.pop(_n, None)      # [C163] pop before re-registering
    add_spec(_n, ("e15src/%s.PLI" % _n if _n.startswith("ST") else
                  "e21src/%s.PLI" % _n if _n.startswith("AB") else
                  ("e24src/%s.PLI" % _n), _g))

# [E2E-28] BASED-MEMBER ADDRESSING BY OFFSET.  DR chooses the encoding by the member's record offset,
# and the crossover is measured on both sides: offsets 0-3 step with `INX H' repeated, offsets >= 4 use
# `LXI D,<offset> / DAD D'.  INX at 2 (ST3/LN1 .link, ST6 .B), INX at 3 (ST6 .C, three INX H), LXI-D at
# 4 (O5, O2), at 6 (O4, O1, O6) and at 001F (REVERSE's .next = 31).  At offset 4 the two encodings cost
# the same four bytes and DR still takes DAD, so `off <= 3' is what the samples say rather than a cost
# model I inferred.  Four byte-exact probes here cover one access per route:
#   O3  fixed member at offset 2, store + read + PUT   (the INX case, and ST3/LN1's shape)
#   O5  single CONSTANT store at offset 4              (LXI D / DAD D / MVI M,lo / INX H / MVI M,hi)
#   O6  single READ at offset 6 into a fixed variable  (LXI D / DAD D / MOV E,M / INX H / MOV D,M / XCHG)
#   O8  POINTER member store at offset 2               (null() through the measured route)
# The rule now lives in ONE encoder (member_step in codegen.ml).  Before this, the offset was spelled
# out as an inline `for _ = 1 to k do d st 0x23 done' loop at TWO read sites while the store path had a
# third copy -- so a store could reach a member one way and a read of the SAME member another.  That is
# the C179 argument for one encoder, applied to instruction selection instead of pool layout, and it was
# live: O6 (offset 6 read) emitted six INX H while O5 (offset 4 store) had already learned DAD.
add_spec('O3', ('artefacts/O3.PLI', 'golden/e2e333d/O3/O3.REL'))
add_spec('O5', ('artefacts/O5.PLI', 'golden/e2e334d/O5/O5.REL'))
add_spec('O6', ('artefacts/O6.PLI', 'golden/e2e334d/O6/O6.REL'))
add_spec('O8', ('artefacts/O8.PLI', 'golden/e2e334d/O8/O8.REL'))

# [E2E-28] DR compiles N9 (`if w = 1 then stop;' then live statements); mine refuses at the
# condition, which is the pre-existing E2E-3b condition-subset gap, not a procedure issue.
# ================================================================================================
# [E2E-29] CHARACTER VARYING STRUCTURE MEMBERS, STRING AND POINTER COMPARISON, AND REVERSE
# ================================================================================================
# REVERSE (golden/e2e319d, DR's own historical listing) is this milestone's target, and it is now
# byte-exact AND runtime-identical.  E2E-27's note recorded REVERSE's second blocker as "CHARACTER
# VARYING members", with DR's route measured but no probe pinning the bytes.  These probes pin them,
# and in doing so overturned two things this compiler had been told by its own earlier readings.
#
# 1. TWO REFUSALS WERE BUG REPORTS, NOT DESIGN DECISIONS [C188 again].  E27S5 was registered as a
#    my-gap refusal with the note "DR COMPILES IT (golden/e2e323d/ST5/ST5.REL)".  ST5 now builds
#    byte-exactly against that same golden, so it is promoted below.  N23_CHARVAR_MULTI refused
#    "char var in multi-item PUT" as unsampled; E29N23 is that exact shape (a CHARACTER VARYING item
#    beside a FIXED item) and DR compiles it with each item keeping its own chain (0022 LXI H,C /
#    SLVTS / PNCOP, then 002B LHLD I / MVI A,09 / QICOP / PNVOP).  The negative is removed here,
#    which is C154's condition: the behaviour has a golden of its own.
#
# 2. SIX OF MY FIRST EIGHT PROBES WERE REFUSED BY DR FOR A DEFECT IN MY PROBE GENERATOR, NOT BY THE
#    LANGUAGE.  They declared `p' in a shared prefix AND again in the body, and DR answered with one
#    PASS-1 error whose symbol-table row reads `DUPLIC'.  Nothing about VARYING members was
#    established until each source declared every name once.  C186(a) again: a refusal produced by my
#    own tooling is evidence about my tooling.  A second instance of the same class happened at the
#    end: renaming the probes into collision-free E29* keys wrote the sources with LF line endings,
#    and DR answered every one of them with UNEXPECTED EOF [C118].  Check the bytes you wrote.
#
# THE VARYING-MEMBER ABI (E29V2-V8, E27S5, REVERSE -- all byte-exact below):
#   * cell = 1 length byte + declared capacity.  REVERSE's `.word'@0 has `.next'@001F (30+1) and the
#     record is 0021 (33); ST5's cap-6 member has `.next'@0007 and the record is 9.  A VARYING member
#     contributes nothing to AUTO STORAGE, like every other based member [C185].
#   * literal store      LHLD <q> / [C189 step] / LXI D,*S / MVI A,cap / MVI B,len / ?SMCVM
#                        len==cap folds to MOV B,A (V3: 'ABCDEF' into character(6)); len==0 folds to
#                        a bare MVI M,00 with NO call (V8) -- both are the existing scalar store_char
#                        tails, reached through one shared destination thunk.
#   * varying -> member  LHLD <q> / [step] / LXI D,<src cell> / MVI A,cap / ?SMVVM  (V2, REVERSE)
#   * member -> member   src / PUSH H / dst / POP D / MVI A,cap / ?SMVVM            (V7)
#   * PUT read           LHLD <q> / [step] / CALL ?SLVTS / ?PNCOP      (ST5,V2,V6,V7,V8,REVERSE)
#   A is the DESTINATION capacity in every store, never the value's length; the source carries its
#   own length byte.  `w' and `p->w' lower to identical bytes (V6/V7 vs V2/V8), so one encoder
#   (vbvar_addr) serves both spellings and every route -- C179's rule in instruction selection, the
#   way C189 already did it for the offset step.
#
# STRING COMPARISON ABI (E29C1-C11, byte-exact): HL carries the RIGHT operand, DE the LEFT, and the
# helper name says what the LEFT operand is.
#   varying  = literal   LXI H,*S / LXI D,<var>  / MVI A,len / ?SCVCM
#   literal  = varying   LXI H,<var> / LXI D,*S  / MVI B,len / ?SCCVM   <- different helper AND a
#                                                                        different length register
#   member   = literal   LHLD <q> / [step] / XCHG / LXI H,*S / MVI A,len / ?SCVCM
#   literal  = member    LHLD <q> / [step] / LXI D,*S / MVI B,len / ?SCCVM -- no XCHG here, because
#                                                                        HL is already the right side;
#                                                                        that is exactly why the other
#                                                                        orientation needs it [C167]
#   varying  = varying   LXI H,right / LXI D,left / ?SCVVM
#   member   = varying   LHLD <q> / XCHG / LXI H,<cell> / ?SCVVM        (E29C10)
# `=' skips the then-body with C2, `^=' with CA.  E29C11 is the semantic witness: `s = 'A'' with
# s='AB' (lengths differ) takes the FALSE branch, printed as 0 by both objects.
#
# POINTER / NULL COMPARISON ABI (E29X1-X9): `p = null' (C2) and `p ^= null' (CA), in BOTH operand
# orientations byte-identical (X4 = X1), are LHLD <cell> / MOV A,H / ORA L / skip-byte -- the cell's
# own bits are the test and no null value is loaded.  Bare `null' and `null()' are the same value to
# DR (X1 vs X5, and REVERSE lines 14/24 use the bare form), so the parser resolves both to one AST
# node instead of carrying two spellings down two routes.  Pointer-to-pointer is a different routine
# entirely: LHLD / PUSH H / LHLD / POP D / ?NC22N, C2 for `=' (X7) and CA for `^=' (X9).  X6/X8 give
# the allocated-pointer side: with p pointing at live storage `p = null' takes the FALSE branch and
# `p ^= null' the TRUE one, executed identically by both objects.
#
# PROCEDURE-LOCAL CHARACTER VARYING AND POINTER CELLS: REVERSE's read_it declares `newword
# character(30) varying' and write_it `p pointer'; DR gives them ordinary absolute DATA cells
# (NEWWORD A(0018), P A(0039)), so the nested-procedure layout admits them with main's routes.
# E29PD1-PD3 pin the tail rule for a procedure body: a body ending in a no-exit loop gets NO trailing
# RET (PD1: 003B JMP 0034, then main's stop at 003E with no C9 between); a statement after such a
# loop is still emitted -- there is still no dead-code suppression -- and the RET comes back (PD2 at
# 0044); an exiting loop keeps its RET (PD3).  REVERSE's read_it is PD1's shape.
#
# BARE `put skip;' (E29PS1) is REVERSE line 49 at 00FE: LXI D,0252 / LXI B,0000 / CALL ?SYSPR /
# MVI A,01 / CALL ?SKPOP / CALL ?QIOOP -- the ordinary prologue, skip and QIOOP with no item, i.e.
# lower_put_items_gen with an empty item list rather than a second encoder.
#
# GET LIST needed NO change: lower_get already emitted ?SYSIN / ?GNVOP / ?SSVFS for a scalar
# CHARACTER VARYING target, which is REVERSE's `get list(newword)' at 003C-0053 byte for byte.  The
# only input-side work in this milestone was proving that, with REVERSE's two scripted runs as the
# witness.  (E2E-27's note listed GET LIST as blocker #3; it was already implemented.)
#
# RUNTIME: nine of these objects were linked beside DR's own (LINK 1.31 + PLILIB) and executed under
# cpmsim with identical scripted stdin; every transcript matched byte for byte -- E29V2 'v= HELLO',
# E29V7 'a= ONE  b= ONE', E29VB 'AB  tail', E29C1 'c1=         1', E29C11 'c11=         0', E29C9
# 'c9=         9', E29X8 'x8-notreached=         0 x8=         9', E29X9 'x9=         0', E29PS1
# '\nafter=\n' [golden/e29rt_dr_r, golden/e29rt_my_r].  REVERSE ran twice on each object:
# sentinel-first, and two sentences plus a terminating sentinel; both byte-identical
# [golden/e29dr_run{A,B}, golden/e29my_run{A,B}].  The objects executed are the objects compared.
#
# ONE DIVERGENCE: E29X3 (`do while (p ^= null)' after `p = null;').  DR reuses HL=0 straight through
# `SHLD P' and omits my LXI H,0000 -- 79 code bytes against DR's 76, data identical (3/3).  Same
# register-reuse family as PB4/PB20/E28N7/O1/O2/O4, deliberately NOT fitted: no sample establishes
# what invalidates the reuse, and C141/C189 forbid guessing into a shared encoder that 33 accepted
# witnesses depend on.  See spec/DIVERGENT.txt.
#
add_spec('E29V2', ('artefacts/E29V2.PLI', 'golden/e2e361/E29V2/E29V2.REL'))
add_spec('E29V3', ('artefacts/E29V3.PLI', 'golden/e2e361/E29V3/E29V3.REL'))
add_spec('E29V4', ('artefacts/E29V4.PLI', 'golden/e2e361/E29V4/E29V4.REL'))
add_spec('E29V6', ('artefacts/E29V6.PLI', 'golden/e2e361/E29V6/E29V6.REL'))
add_spec('E29V7', ('artefacts/E29V7.PLI', 'golden/e2e361/E29V7/E29V7.REL'))
add_spec('E29V8', ('artefacts/E29V8.PLI', 'golden/e2e361/E29V8/E29V8.REL'))
add_spec('E29V9', ('artefacts/E29V9.PLI', 'golden/e2e361/E29V9/E29V9.REL'))
add_spec('E29VA', ('artefacts/E29VA.PLI', 'golden/e2e361/E29VA/E29VA.REL'))
add_spec('E29VB', ('artefacts/E29VB.PLI', 'golden/e2e362/E29VB/E29VB.REL'))
add_spec('E29PS1', ('artefacts/E29PS1.PLI', 'golden/e2e361/E29PS1/E29PS1.REL'))
add_spec('E29C1', ('artefacts/E29C1.PLI', 'golden/e2e360/E29C1/E29C1.REL'))
add_spec('E29C2', ('artefacts/E29C2.PLI', 'golden/e2e360/E29C2/E29C2.REL'))
add_spec('E29C3', ('artefacts/E29C3.PLI', 'golden/e2e360/E29C3/E29C3.REL'))
add_spec('E29C4', ('artefacts/E29C4.PLI', 'golden/e2e360/E29C4/E29C4.REL'))
add_spec('E29C5', ('artefacts/E29C5.PLI', 'golden/e2e360/E29C5/E29C5.REL'))
add_spec('E29C6', ('artefacts/E29C6.PLI', 'golden/e2e360/E29C6/E29C6.REL'))
add_spec('E29C7', ('artefacts/E29C7.PLI', 'golden/e2e360/E29C7/E29C7.REL'))
add_spec('E29C8', ('artefacts/E29C8.PLI', 'golden/e2e360/E29C8/E29C8.REL'))
add_spec('E29C9', ('artefacts/E29C9.PLI', 'golden/e2e354d/E29C9/E29C9.REL'))
add_spec('E29C10', ('artefacts/E29C10.PLI', 'golden/e2e354d/E29C10/E29C10.REL'))
add_spec('E29C11', ('artefacts/E29C11.PLI', 'golden/e2e354d/E29C11/E29C11.REL'))
add_spec('E29X1', ('artefacts/E29X1.PLI', 'golden/e2e362/E29X1/E29X1.REL'))
add_spec('E29X2', ('artefacts/E29X2.PLI', 'golden/e2e362/E29X2/E29X2.REL'))
add_spec('E29X4', ('artefacts/E29X4.PLI', 'golden/e2e362/E29X4/E29X4.REL'))
add_spec('E29X5', ('artefacts/E29X5.PLI', 'golden/e2e362/E29X5/E29X5.REL'))
add_spec('E29X6', ('artefacts/E29X6.PLI', 'golden/e2e353d/E29X6/E29X6.REL'))
add_spec('E29X7', ('artefacts/E29X7.PLI', 'golden/e2e362/E29X7/E29X7.REL'))
add_spec('E29X8', ('artefacts/E29X8.PLI', 'golden/e2e353d/E29X8/E29X8.REL'))
add_spec('E29X9', ('artefacts/E29X9.PLI', 'golden/e2e362/E29X9/E29X9.REL'))
add_spec('E29PD1', ('artefacts/E29PD1.PLI', 'golden/e2e360/E29PD1/E29PD1.REL'))
add_spec('E29PD2', ('artefacts/E29PD2.PLI', 'golden/e2e360/E29PD2/E29PD2.REL'))
add_spec('E29PD3', ('artefacts/E29PD3.PLI', 'golden/e2e361/E29PD3/E29PD3.REL'))
add_spec('E29N23', ('artefacts/E29N23.PLI', 'golden/e2e354d/E29N23/E29N23.REL'))
add_spec('E27S5', ('artefacts/ST5.PLI', 'golden/e2e323d/ST5/ST5.REL'))
add_spec('REVERSE', ('artefacts/REVERSE.PLI', 'golden/e2e319d/REVERSE/REVERSE.REL'))


# ================================================================================================
# [E2E-30] BIT(1) STRUCTURE MEMBERS, THE POINTER TRAVERSAL LOOP, AND THE NETWORK ORACLE
# ================================================================================================
# NETWORK.PLI (golden/first8080u) is this milestone's target.  Its oracle is fully verified before
# anything was implemented: recompiling the unchanged source on the 8-inch disk's PL/I-80 v1.4 gives
# a .REL BYTE-IDENTICAL to golden/first8080u/NETWORK/NETWORK.REL and a PRN identical too [golden/
# e30net_dr], so -- exactly as C194 established for REVERSE -- the historical listing is v1.4 output,
# not some earlier generation.  The listing reports NO ERROR(S) in both passes, CODE SIZE 05B0h and
# DATA AREA 00EBh; both figures are read back out of the binary itself (201 code records ending at
# 05B0, LINK-DEF-DATA-SIZE = 00EB), not taken on trust.  The historical PRN carries no disassembly
# (switches L,D only), so a SECOND compile with '$L$D$C$S' [golden/e30net_c, 679 insruction lines]
# is the instruction-level oracle used throughout -- DR's own bytes, not a re-decoding of the .REL
# [E2E-23: a mis-decoded listing is not evidence].
#
# THE BIT(1) MEMBER ABI [C195].  A based bit is one byte reached by the SAME member_step encoder as
# every other member (bmem_addr is now shared, so `w' and `p->w' and bit and varying cannot drift
# [C179/C189]); true is bit 7, 0x80, exactly as in the scalar cell [E2E-11 step 1a].
#   store  LHLD <p> / [step] / MVI M,80  (true)  |  MVI M,00  (false)   [NETWORK 0366, 03D1]
#   test   LHLD <p> / [step] / MOV A,M / ORA A / JP <skip>              [NETWORK 038B]
# DR's NETWORK puts `.investigate' at record offset 0017 = the 21-byte cap-20 varying cell + 2 for
# total_distance -- contiguous, no padding, the C185 rule again -- in a 001C-byte record.  Byte-exact
# here: E30B1 (bit@0, store then both test outcomes), E30B5 (bit(1) in a DO WHILE), E30B7 (bit@2
# beside a fixed member), and E27S6/ST6, the offset-2 layout probe that E2E-27 pinned as a refusal
# and which is promoted below [C154].  `if p->f = '1'b' and `^=' (E30B4) stay refused: DR's
# comparison bytes for a bit member are not in any sample.
#
# THE PRE-TEST POINTER TRAVERSAL [C196].  `do p = <init> repeat(p-><link>) while(p ^= null); BODY
# end;' is NETWORK's loop, EIGHT times over (source lines 96, 119, 122, 173, 184, 198, 256, 258).
#  DR emits nine LHLD/MOV A,H/ORA L/JZ top tests, listed against lines 95(013A), 118(01B3),
#   121(01EE), 172(031B), 183(037A), 197(03E7), 233(04D9), 255(0563), 257(0579): the eight
#   traversals plus line 233's plain `do while(q^=null)', which DR ALSO tests at the top, while
#   `do while(true)' (lines 31, 54, 141, 146, 180, 222) emits no test at all.
#   init-assign  <p = from>          LHLD <from> / SHLD P            (an ordinary pointer store)
#   TEST (head)  p ^= null           LHLD P / MOV A,H / ORA L / JZ <exit>
#   BODY
#   REPEAT       <p = p->link>       LHLD P / [step] / MOV E,M / INX H / MOV D,M / XCHG / SHLD P
#   JMP back to TEST                  (so the update runs AFTER the body and the re-test gates exit)
# The init and repeat clauses are lowered by lower_assign and the top test by lower_test_skip -- no
# new encoder, and the guard variable is required to be a plain POINTER with no TO and no BY.  This
# is deliberately the pre-test shape and not an algorithmically equivalent post-test while-loop:
# reordering test/update would break raw REL parity, which is the acceptance criterion [C137].
#
# E30L1 COMPILES AND DIVERGES, and the cause is a single known one.  Mine emits 69 code bytes to
# DR's 66 (data 12/12, 173 of 256 bytes differ, first at 59); deleting one `LXI H,0000' from my
# stream makes it byte-identical to DR -- i.e. the traversal lowering itself is exact and the whole
# difference is DR reusing HL=0 across the `head = null;' and `n = 0;' stores, the same
# register-reuse family as PB4/PB20/E28N7/O1/O2/O4/E29X3.  I am NOT fitting that rule from these
# probes [C141, and the task's own instruction not to fit reuse to a single sample]; E30L1 is pinned
# as a divergence so the traversal's byte-correctness is recorded and the reuse gap stays visible.
#
# NETWORK's FIRST BLOCKER today is neither BIT nor the traversal (both now clear) but
# `find(...) returns(pointer)' [E30F1 refuses at the returns(POINTER) gate], with chained
# qualification `q->next_city->city_name' [E30C1-C3, G1] and the named-SYSIN ON ENDFILE/REVERT
# handler [E30E2/E30E3] as the next dependencies.  GET LIST into multiple items was already
# byte-exact (E30H1), so NETWORK's `get list(city1, distance, city2)' is not a blocker at all.
#
# E30T1 stores 'ABCDEFGH' (8) into a cap-6 VARYING member and is byte-exact: `MVI A,06' (the
# DESTINATION capacity) / `MVI B,08' (the SOURCE length) / `?SMCVM'.  This replaces the withdrawn
# REVERSE truncation attribution in the E2E-29 note -- the A=cap/B=len asymmetry is real and
# compile-side; DR's runtime truncation is inferred from the ABI, not yet executed, and not claimed.
#

add_spec('E30B1', ('artefacts/E30B1.PLI', 'golden/e30p1/E30B1/E30B1.REL'))
add_spec('E30B3', ('artefacts/E30B3.PLI', 'golden/e30p1/E30B3/E30B3.REL'))
add_spec('E30B5', ('artefacts/E30B5.PLI', 'golden/e30p1/E30B5/E30B5.REL'))
add_spec('E30B7', ('artefacts/E30B7.PLI', 'golden/e30p1/E30B7/E30B7.REL'))
add_spec('E30H1', ('artefacts/E30H1.PLI', 'golden/e30p1/E30H1/E30H1.REL'))
add_spec('E30T1', ('artefacts/E30T1.PLI', 'golden/e30p1/E30T1/E30T1.REL'))
add_spec('E27S6', ('artefacts/ST6.PLI', 'golden/e2e323d/ST6/ST6.REL'))


# ================================================================================================
# [E2E-30/P4] CHAINED QUALIFICATION specimen, and the register-reuse DIVERGENCES NETWORK reaches
# ================================================================================================
# E30C1 is byte-exact and is the graph-shape read NETWORK print_all needs: a TWO-level chain
# `q->next_city->city_name' where the inner qualifier is a POINTER member.  DR follows the inner
# pointer with the ordinary dereference tail and THEN reads the final member -- E30C1 0044-004B and
# NETWORK print_all 0220-0227 are the same bytes: LHLD <base> / [step to the pointer member] /
# MOV E,M / INX H / MOV D,M / XCHG / [step to the final member] / CALL ?SLVTS.  Both halves reuse
# existing encoders (bmem_addr, the deref tail, member_step), so no third addressing mechanism is
# added [C179].  A chain into a non-VARYING member (E30C2, arithmetic) and a chain inside a
# COMPARISON (E30C3) stay refused -- neither is in any golden.
#
# The graph-building witness E30G1 (two based record types, BIT flags, chained qualification,
# allocation, traversal) COMPILES and, when linked through LINK 1.31 + PLILIB, produces console
# output BYTE-IDENTICAL to DR's own E30G1 under the same input.  Its .REL is NOT byte-exact: mine
# carries 426 code bytes to DR's 419 (data area 21/21 exact), the excess being extra HL reloads
# where DR reuses a register it knows is still live -- the same register-reuse family as the eight
# pinned E2E-23/24/28/29 divergences.  It is pinned here as the strongest witness that the graph
# MECHANISM is behaviourally right while the peephole is not: correct executed behaviour, wrong
# byte-for-byte code size, cause attributed to ONE thing (register reuse) per [C140].
#
# E30B2 and E30L2/L3/L4 are the same family (all data areas EXACT, mine larger, divergence inside
# read/write sequences where DR reuses DE or HL across a member access): pinned, not fitted [C141].
# E30L5 stays REFUSED, but NOT for the reason first written here: it is the same pre-test
# traversal with `if n > 3 then p = null;' in the body, and it refuses because assigning a BARE
# `null' to a POINTER cell is unsampled -- which is also NETWORK line 239 (`q = null;').  It is a
# value-lowering gap, not a loop-orientation gap.
#
add_spec('E30C1', ('artefacts/E30C1.PLI', 'golden/e30p1/E30C1/E30C1.REL'))


# ================================================================================================
# [E2E-31/P1] RETURNS(POINTER) -- and two WRONG-VALUE defects the probes exposed
# ================================================================================================
# NETWORK's first blocker is cleared.  DR's convention, taken from seven purpose-built probes
# (golden/e31p2, e31p3, e31p5), is: the CALLEE evaluates the returned pointer into HL and exits
# with a plain RET -- E31F1 006C/006F and E31F3 for a pointer FORMAL, matching NETWORK find
# 0150/0153 and 01A9/01AC (lines 98, 106); `return(null())' is the SAME shape (`LXI H,0000 / RET',
# E31F2 005B/005E).  The CALLER is unchanged from the FIXED path -- `LXI H,*A(slot) / CALL f /
# SHLD dst' (E31F1 0006-000C; NETWORK connect line 77 at 00D2-00DE) -- which 26 byte-exact
# FIXED-return specimens already pin, so admitting POINTER adds no second calling convention
# [C179].  Byte-exact: E31F1 (allocate in callee, return, qualified store + read in caller),
# E31F3 (return a pointer formal), E31F6 (bare `null' assigned to a POINTER cell -- already
# correct; E30L5's refusal was a defect in MY probe, which wrote `repeat(p->dist)' instead of
# `repeat(p->link)', so NETWORK line 239 `q = null;' was never a blocker and matrix row 9 is
# withdrawn).  E31F7/F7B also showed `add' as a procedure name is refused by my binder as a
# conflict while DR accepts it; E31F7C renames it and is used instead.
#
# The probes then disagreed with my E2E-30 classification, and execution settled it.  Two families
# are WRONG-VALUED, not merely byte-divergent; both were previously lumped into "register reuse":
#
#   FAMILY B -- based/pointer member reads accumulated in arithmetic.  DR keeps a running value in
#   HL and brackets each dereference with PUSH H / POP D / DAD D (E31F4 0035-004F, summing
#   `a->v + b->v + c->v'); mine omits the bracketing, so it emits FEWER bytes and computes garbage.
#   Executed, linked through LINK 1.31 + PLILIB: DR prints `s=6' (the correct 1+2+3) and mine
#   prints `s=7742'.  E31F7C is NETWORK's own loop body -- `do w = head repeat(w->nx)
#   while(w ^= null); s = s + w->v; end;' -- and mine prints `sum=7768' where DR prints `sum=6'.
#   PB20 (`q = q + q' on BASED(P)) prints `q=6947' against DR's and the correct `q=6'; PB4 prints
#   `q=44' CORRECTLY, so the family is not uniformly wrong and the boundary is not yet drawn.
#   MINE-SMALLER is the tell: the eight reuse rows are all mine-LARGER.
#
#   FAMILY C -- a FIXED FORMAL parameter read in a comparison is not dereferenced.  DR loads the
#   formal cell and then reads THROUGH it (`LHLD M / MOV E,M / INX H / MOV D,M / XCHG', E31F5
#   0073-007D for `if i = m'), because a formal holds the CALLER'S ADDRESS.  Mine uses the cell
#   value directly, i.e. it compares against an address.  E31F8 (`returns(FIXED)', `if k = 0')
#   prints `r=2' where DR and the arithmetic both say `r=1' -- wrong value.  E31F2 is the same
#   defect but its value happens to survive (both branches return null(), so `r=1' is printed by
#   DR and by mine alike; only 2 bytes differ).  E31F5 is the same cause again.  This is NOT
#   returns(POINTER)-specific: E31F8 reproduces it with RETURNS(FIXED), so it predates this
#   milestone and E2E-30 never saw it because none of its probes compared a formal.
#
# Neither family is fitted here.  Both are recorded with the executed evidence that shows they are
# real defects, because a divergence panel row that says "shape differs, cause believed benign" is
# worse than useless once the program turns out to compute the wrong number [C137][C168].  The
# fixes need their own discriminating probes -- in particular what makes PB4 correct where PB20 and
# E31F4 are not, and whether FAMILY C is a general formal-deref rule that the 756 accepted
# specimens happen not to exercise in a comparison.  Changing the condition lowering without that
# evidence would be exactly the trade C179 forbids.
#
add_spec('E31F1', ('artefacts/E31F1.PLI', 'golden/e31p2/E31F1/E31F1.REL'))
add_spec('E31F3', ('artefacts/E31F3.PLI', 'golden/e31p2/E31F3/E31F3.REL'))
add_spec('E31F6', ('artefacts/E31F6.PLI', 'golden/e31p2/E31F6/E31F6.REL'))

# =====================================================================================
# [E2E-32/P1] FAMILY C IS FIXED -- and the fix is one shared load primitive, not three.
#
# Root cause, established from DR's own bytes before touching codegen: a by-reference
# formal's cell holds the ADDRESS the caller stored (DR's callee entry is `MOV E,M /
# INX H / MOV D,M / XCHG / SHLD K A(0008)' -- E31F8 0034-0038), so every read must go
# THROUGH the cell.  Mine already knew this: st.deref lists ALL formals of a
# non-recursive callee and lower_hl / cmp_load_deref already consult it.  What was
# wrong is that the property was written out a second and third time -- the `= 0' skip
# arm and the ident-vs-ident `=/^=' arm each hand-rolled their own load and forgot the
# indirection.  That is the failure mode of duplicated invariants, not of the rule.
#
# Fix: one `val_addr' primitive ("leave HL pointing at the 2-byte value": LHLD cell for
# a by-reference formal, LXI H,&cell for a plain local) used by both `= 0' sites, and the
# ident-vs-ident Eq/Ne arm routed through the EXISTING cmp_load_deref for both operands.
# For two plain locals cmp_load_deref emits exactly what that arm emitted before, so the
# 759 accepted specimens are untouched (verified: 759/759 after the change).
#
# Probe matrix, all DR-golden-first (golden/e32c), each orientation sampled separately
# because a rule checked in only one direction is not checked [C167]:
#   E32C1  LOCAL = 0 / LOCAL > 3 / conjunction          -> CONTROL, byte-exact BEFORE and
#          AFTER; printed w=2 as independently expected.  This is what proves the fix was
#          not applied too broadly.
#   E32C2  formal = 0, BOTH outcomes (f(0)=1, f(3)=2)   -> byte-exact, executed 1 and 2
#   E32C4  formal = local (k = m), both outcomes        -> byte-exact, executed 1 and 2
#   E32C5  local = formal (m = k), both outcomes        -> byte-exact, executed 1 and 2
#   E32C7  formal ^= nonzero literal                    -> byte-exact (already was), 2 and 1
#   E32C8  formal > 2 / formal < 2 on a formal          -> byte-exact (already was), 1,4,8
#   E32C9  plain VALUE read of a formal (y = k)         -> byte-exact (already was), 4 and 5
# C7/C8/C9 being already-exact is itself the finding: the bug was confined to `=' arms,
# which is why E2E-31's "formals in comparisons" phrasing was too broad to act on.
# Promoted out of the divergence panel by this fix: E31F8, E31F2, E31F5 [C154].
add_spec('E31F8', ('artefacts/E31F8.PLI', 'golden/e31p3/E31F8/E31F8.REL'))
add_spec('E31F2', ('artefacts/E31F2.PLI', 'golden/e31p2/E31F2/E31F2.REL'))
add_spec('E31F5', ('artefacts/E31F5.PLI', 'golden/e31p2/E31F5/E31F5.REL'))
for _n in ('E32C1', 'E32C2', 'E32C4', 'E32C5', 'E32C7', 'E32C8', 'E32C9'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e32c/%s/%s.REL' % (_n, _n)))

# Two ORIENTATIONS of `=' with a literal on the LEFT remain unimplemented -- and they are
# refusals of a shape DR COMPILES, so they are my-gap, not perimeter [C188]: registering
# them silently as "DR rejects this too" would misrepresent the oracle.
#   E32C3  `if 0 = k'  -> mine: "condition form not in E2E-3b subset [TBD]"
#   E32C10 `if k = 3'  -> mine refuses the same way; DR emits `LHLD K / deref ladder /
#          LXI D,0003 / ?IS22N' (golden/e32c/E32C10 0066-006B), i.e. the fix above covers
#          the LOAD but the condition-subset matcher never admits these two shapes.
REJECTS['E32C3'] = (open('artefacts/E32C3.PLI', "rb").read().replace(b"\r\n", b"\n")
                    .rstrip(b"\x1a").decode(), "condition form not in E2E-3b subset")
NEG_META['E32C3'] = ("my-gap",
    "DR COMPILES it (golden/e32c/E32C3 emits a .REL): `if 0 = k' with the LITERAL on the "
    "left of an equality whose other side is a formal.  Mine refuses with `condition form "
    "not in E2E-3b subset'.  Unrelated to Family C, which is fixed: the refusal happens "
    "before any load is chosen.")
# =====================================================================================
# [E2E-32/P2] FAMILY B IS FIXED.  The rule was mis-stated in E2E-31, and the correction
# matters: DR does NOT "bracket every dereference with PUSH H / POP D / DAD D".  It parks
# the LEFT operand in DE (`XCHG') when the RIGHT operand's lowering leaves DE alone, and
# on the STACK (`PUSH H' ... `POP D') only when the right operand's lowering writes DE --
# which the member-read ladder `MOV E,M / INX H / MOV D,M / XCHG' does, and a plain
# `LHLD m' or a literal does not.
#
# That is why PB4 was right while PB20 was not, which E2E-31 could not explain:  [C200]
#   PB4  `q = q + 4'  right = literal      -> XCHG parking is legal, DE survives -> 44 OK
#   PB20 `q = q + q'  right = member read  -> the ladder overwrote the parked value,
#                                            `DAD D' then added the ADDRESS: 6947 = 3 + &z
# The predicate in the compiler was `is a pointer FORMAL' (st.deref membership), so every
# BASED and every qualified member read on the right escaped it -- including NETWORK's
# `s = s + w->v'.  E32B1 puts all three right-operand kinds in ONE probe and is now
# byte-exact: `p->v + m' (a=12), `p->v + 3' (b=10), `p->v + p->v' (c=14).
#
# Fix = one predicate `writes_de', used by the ADD right-side test and by SUB.  The old
# reading had been wrong in BOTH directions [C167]: the E2E-15 comment in the ADD arm
# records that "any deref on either side => PUSH" added a SPURIOUS PUSH/POP pair for
# `p->v + m'.  So neither the pushing nor the not-pushing rule had been tested from both
# sides until now.
#
# SUB: the arm used to refuse ANY deref operand ("no DR sample").  E32B2/E32B4 are those
# samples, so the refusal is narrowed to the one case still unmeasured -- a pointer FORMAL
# as the minuend -- and the measured routes now lower correctly:
#   E32B4a `m - p->v' : LHLD M / PUSH H / ladder / POP D / CALL ?IS22N   -> 4  OK
#   E32B4b `p->v - m' : XCHG park, no stack pair                          -> -4 OK
#   E32B2b `q->v - p->v', E32B2c `p->v - q->v' : PUSH/POP both sides      -> 2, -2 OK
# Non-commutative operators were tested in BOTH orientations on purpose: a rule fitted
# only to `+' would have passed this whole matrix while still getting subtraction wrong.
#
# Executed against independently derived arithmetic (each image is byte-identical to
# DR's, so this validates the EXPECTATION and the oracle together, not my lowering --
# see the note on what runtime evidence can and cannot mean after C137):
#   E32B1 a=12 b=10 c=14 | E32B2 a=10 b=2 c=-2 | E32B3 a=11 b=22 c=15
#   E32B4 a=4 b=-4 c=16  | PB20 q=6            | E31F4 s=6 | E31F7C sum=6
# E31F7C is NETWORK's own accumulation shape, so the shortest-distance computation is now
# believed correct rather than merely compilable [the task's precedence for P2 over P4].
# Promoted out of the divergence panel [C154/C168]: PB20, E31F4, E31F7C.
add_spec('PB20', ('artefacts/PB20.PLI', 'golden/e2e315d/PB20/PB20.REL'))
for _n in ('E32B1', 'E32B2', 'E32B4'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e32b/%s/%s.REL' % (_n, _n)))
for _n, _g in (('E31F4', 'golden/e31p2/E31F4/E31F4.REL'),
               ('E31F7C', 'golden/e31p5/E31F7C/E31F7C.REL')):
    add_spec(_n, ('artefacts/%s.PLI' % _n, _g))

# =====================================================================================
# [E2E-32/P4] ON ENDFILE with a STATEMENT handler is byte-exact; only the GOTO form is open.
#
# E32E1 is `on endfile(sysin) n = 99;' -- registration plus an inline handler, NO label
# transfer -- and mine matches DR byte for byte (golden/e32e/E32E1).  That matters because
# the refusal text for the GOTO variant had been reading as if ON-conditions in general were
# missing.  They are not: what is missing is precisely the label-transfer plumbing, now
# isolated as four pieces by E32E2 (two GOTO handlers in one block, DR-golden captured):
#   1. at BLOCK ENTRY, `LXI H,0 / DAD SP / SHLD * A(0019)' -- the block saves SP into ONE
#      hidden cell (the `DAD SP' is an extended opcode DR's own listing prints on the next
#      line, which is why an earlier grep-based read missed it; the addresses 0006 -> 000A
#      prove the intervening instruction);
#   2. per ON unit: `LXI H,SYSIN / MVI A,05 / CALL ?ONCOP / JMP <continue> / JMP <stub>';
#   3. the stub, whose body both handlers share the cell for: `LHLD * A(0019) / SPHL /
#      CALL ?RECOV / ...';
#   4. transfer to the label block.
# CORRECTION to C201 / the E2E-31 note, made in place rather than silently: E2E-31 recorded
# "each ON-unit needs a 2-byte hidden cell".  E32E2 shows the cell is allocated ONCE PER
# BLOCK and READ by every handler in it (two `LHLD * A(0019)' against one `SHLD * A(0019)'),
# so the allocation is per-block and the cell's lifetime is the whole activation.  The rest
# of C201 (four emissions, auto-revert, ?ONCOP taking its handler from the bytes after the
# CALL) is unaffected -- and E30E2's single-ON-unit image cannot have distinguished the two,
# which is exactly the [C167] one-direction-in-one-probe failure again.
add_spec('E32E1', ('artefacts/E32E1.PLI', 'golden/e32e/E32E1/E32E1.REL'))

# =====================================================================================
# [E2E-33/P2] C203's stated cause was WRONG.  Multi-formal layout is fine; the defect is
# "exactly TWO by-reference formals and NO other local rows in the callee".
#
# C203 said "with two or more by-reference formals my DATA segment is 4 bytes too large"
# and inferred from it that NETWORK's connect (three formals) would diverge.  Four new
# DR-golden probes (golden/e33m) refute both halves:
#   E33M3  q3(a,b,c), 3 FIXED formals, no locals, return(a+b+c)   -> BYTE-EXACT
#   E33MM  f2(a,p)  mixed FIXED + POINTER formals                 -> BYTE-EXACT
#   E33ML  g2(a,b) 2 formals PLUS locals t,u                      -> BYTE-EXACT
#   E33MD  q3(a,b,c) 3 formals, no locals, WITH `if a = b'         -> BYTE-EXACT
#   E33MC  h(k,j)  2 formals, no locals, WITH `if k = j'           -> DIFFERS, +4 DATA
#   E32C6  h(k,j)  same, two call sites and two PUTs               -> DIFFERS, +4 DATA
# One formal is fine (E31F8/E32C4/C5/C8), three are fine (E33M3/E33MD), two-with-locals is
# fine (E33ML); two-without-any-other-row is not.  So the trigger is the COMBINATION, and
# the NETWORK inference in C203 is withdrawn -- connect's three formals measure clean.
# The mechanism is still unidentified: with 5 passing and 2 failing shapes I can state the
# boundary but not why the allocator behaves differently there, so nothing is fitted.
# Guessing an allocator rule from a shape I chose is exactly [C185]/[C167].
for _n in ('E33M3', 'E33MM', 'E33ML', 'E33MD'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e33m/%s/%s.REL' % (_n, _n)))

# =====================================================================================
# [E2E-34/P1] ON ... GOTO, the recovery pad, the hidden saved-SP cell and REVERT.
#
# Six probes, each written to answer ONE question and each DR-compiled first
# (oracle/batch.py E34A -- golden/e34a/, all status ok, all $L$D$C$S listings):
#   E34A2  two ON ... GOTO units to the SAME label   -> one pad, one cell, one SEL-COMMON
#   E34A3  ON/GOTO and a plain GOTO to the same label -> pad chain and plain-goto chain
#          are SEPARATE forward references (LINK-SET-LC 001C vs LINK-CHAIN-ADDR 0042)
#   E34A4  ON ... GOTO to a label defined EARLIER     -> pad still precedes the label,
#          handler JMP is an inline backward RELOC to the PAD (0x13), not to 0x1a
#   E34A5  plain GOTO backward to a PADDED label      -> lands on the pad too (shares
#          RELOC code 0x13 with the handler's JMP); the pad is the label's entry point
#   E34A6  ON ... GOTO inside a nested procedure      -> cell belongs to the procedure's
#          block, main gets none
#   E34A7  nested procedure with a formal and ON/GOTO -> the SP save sits AFTER the
#          formal pointer-copy prologue, at the block's entry
# E34A1 (statement-handler ON in a nested procedure, no GOTO) is NOT registered: it
# declares `dcl sysin file' INSIDE the procedure, which is still an unimplemented
# [TBD] refusal here ("procedure local of type FILE is unsampled").  Its DR golden is
# committed and it stays a probe; registering it as a refusal would have taught the gate
# to expect a gap that E30E2 shares and NETWORK does not, from one sample [C185].
for _n in ('E34A2', 'E34A3', 'E34A4', 'E34A5', 'E34A6', 'E34A7'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34a/%s/%s.REL' % (_n, _n)))

# [E2E-34/P1] the two negatives this milestone made obsolete, promoted rather than
# deleted: "a negative is removed only when its behaviour has a golden of its own"
# (E2E-32).  Both programs were DR-compiled under short CP/M names because the oracle
# rejects names longer than 8 characters -- N7_MULTI_FWD's content is N7MFWD's, and
# N79_ON_HANDLER_GOTO's is N79GOTO's, byte for byte apart from the name substitution.
# N7MFWD is the two-forward-GOTOs-to-one-label program that NG60.REL recorded: it is
# byte-exact WITHOUT any ON/GOTO code in it, which is the control that the new
# multi-site forward chain is a general GOTO fix and not an ON-shaped hack.
# E34B1 is the control for the DATA-segment fix: a FILE declaration and an EMPTY pool.
# DR emits no SET-LC(data,0000) there; mine emitted one for 23 rounds on the strength of
# a clause that was redundant in the only specimen that ever justified it (FLTPOLY2,
# 44 DATA bytes).
# [E2E-34/P1] E34A8: the ON ... GOTO unit inside a nested DO-block.  DR gives it no
# section of its own -- DATA AREA 001B with the cell still at 0019, i.e. main's, exactly
# as if the unit were written at main level (compare E34A4) -- and mine agrees byte for
# byte, which is the control that says `on_facts' descends DO/IF/BEGIN for the right
# reason and not by accident.
add_spec('E34A8', ('artefacts/E34A8.PLI', 'golden/e34a/E34A8/E34A8.REL'))

# [E2E-34/P1] E34A9: the same unit inside a nested UNNAMED BEGIN-block.  DR compiles it
# (golden/e34a/E34A9: DATA AREA 001B, cell 0019 = the OUTER block's, pad at 003B), and
# mine refuses with the pre-existing "procedure without name [TBD]".  Two things are
# pinned here.  First, the refusal is not a regression introduced by this milestone:
# bind.section2 allocates a saved-SP cell for any block whose on_facts.of_goto is true,
# including the nm = None branch at the nested-BEGIN call, and that cell address has no
# route out (pl_sp_cell is only exported for named blocks) -- so if lowering reached it,
# the layout would be 2 bytes longer than the code that references it.  The named-block
# refusal stands in front of that, and it must stay: this negative is the tripwire for
# [C137]'s "a bare crash / silent layout is never acceptable".  Second, DR's measurement
# above says the eventual fix is to give BEGIN-blocks the outer section's cell, NOT their
# own, so the refusal should be lifted by reusing the parent layout rather than by adding
# a per-BEGIN section.
REJECTS["E34A9_BEGIN_BLOCK_ONGOTO"] = (
    open("artefacts/E34A9.PLI", "rb").read().replace(b"\r\n", b"\n")
    .rstrip(b"\x1a").decode(), "procedure without name")
NEG_META["E34A9_BEGIN_BLOCK_ONGOTO"] = ("my-gap",
     "DR COMPILES IT: .REL emitted with DATA AREA 001B and the saved-SP cell at 0019 in "
     "the OUTER block's section (golden/e34a/E34A9/E34A9.REL)")

for _n in ('N7MFWD', 'N79GOTO', 'E34B1'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34b/%s/%s.REL' % (_n, _n)))

# [E2E-34/P4] the CHARACTER VARYING x CHARACTER VARYING comparison family, with every
# operand orientation probed separately [C167].  Before this round the shape table
# admitted two of the four load/immediate combinations, and a pair it declined did NOT
# refuse: the ident-vs-ident NUMERIC arm further down `lower_test_skip0' caught it and
# emitted ?IS22N with rc=0.  E34C2/C7/C8/C9/C10 are five comparisons that compiled
# silently wrong; C3 and C5 refused.  Nine of these ten probes were the evidence.
#   C1 `w = s'   C4 `p->w = s'   (load left, immediate right  -> XCHG)
#   C2 `s = w'   C3 `s = p->w'   (immediate left, load right  -> no parking at all;
#                                             C3 and C2 are byte-identical: `w' and
#                                             `p->w' are the same read)
#   C5 `w = p->w'  C6 `x = p->w'  C7 `p->w = x'  (both load -> PUSH H / POP D)
#   C8 `x = y'  C9 `y = x'  C10 `x = s'  (a by-reference VARYING formal: its cell holds
#                                             the descriptor address, so it is a LOAD,
#                                             not an immediate -- C8/C10 load-left,
#                                             C9 load-right)
for _n in ('E34C1', 'E34C2', 'E34C3', 'E34C4', 'E34C5',
           'E34C6', 'E34C7', 'E34C8', 'E34C9', 'E34C10'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34c/%s/%s.REL' % (_n, _n)))

# [E2E-34/P4] E34D1..D4 pin the tail-RET rule for value-returning procedures, which the
# comment at the epilogue had stated backwards ("Value-returning procedures are NOT given
# one").  D1 (body ends in an IF, no ELSE) and D2 (IF/ELSE where BOTH branches RETURN, so
# the last instruction is already a RET and DR emits one more) both end with a bare RET;
# D3 (last top-level statement = `return(3);') does not, nor do E34A5/A7 (last statement =
# GOTO), nor E31F5 (body ends inside `do while('1'b)' -- nothing falls out).  Those three
# are the controls that keep this from being "always emit RET after a value proc".
for _n in ('E34D1', 'E34D2', 'E34D3', 'E34D4'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34d/%s/%s.REL' % (_n, _n)))

# [E2E-34/P5] a based FIXED BINARY member as a comparison operand: one load primitive
# (LHLD base / member ladder / MOV E,M / INX H / MOV D,M / XCHG) plus [C204]'s parking
# rule, measured over all six relations and both orientations.  E34E3/E34E10 are the two
# probes that pin DE's arrival order; E34E5 is the member-vs-member case where the LEFT
# side's own ladder runs before the first load of the right.
for _n in ('E34E1', 'E34E2', 'E34E3', 'E34E4', 'E34E5', 'E34E6',
           'E34E7', 'E34E8', 'E34E9', 'E34E10', 'E34E11'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34e/%s/%s.REL' % (_n, _n)))

# [E2E-34/P5-P6] comparisons with a CONSTANT and with an EXPRESSION.
# F1..F5 (`= 1, 5, 255, 300, 32767') walk the shared bias ladder DCX-repeats -> LXI B ->
# DAD B and pin F3 = 32767 = 0x8001, the constant NETWORK's `infinite' expands to; they
# also pin the `=' C2 skip against F9's `^=' CA [C072].  F6..F14 pin `v = <arith expr>'
# and the two evaluation orders DR chooses: a single load plus a literal bias (F7 `d + 1',
# F14 `hp->v + 1') is lowered LEFT-first, everything that combines two non-literal
# operands (F6 sum, F8 sum with a member, F11 three operands, F12 product, F13 difference)
# is lowered RIGHT-first with the variable's PUSH/POP pair after it.  F10 (`d + e = t')
# is byte-identical to F6, which is what licenses routing by "which side is the
# expression" rather than by source order.
for _n in ('E34F1', 'E34F2', 'E34F3', 'E34F4', 'E34F5', 'E34F6', 'E34F7', 'E34F8',
           'E34F9', 'E34F10', 'E34F11', 'E34F12', 'E34F13', 'E34F14'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34f/%s/%s.REL' % (_n, _n)))

# [E2E-34/P6] two negatives promoted, because the gap each recorded is now closed and
# each has DR's own golden (E2E-32's rule: a negative is removed only when its behaviour
# has a golden of its own -- here the goldens predate the fix and the programs are
# byte-exact against them, E28N9 vs golden/e2e331d/N9, E32C10 vs golden/e32c/E32C10).
# E28N9 is `if w = 1 then stop;': the `= k' ladder (E34F4) is what compiled it.
# E32C10 is a nested `f: procedure(k) returns(fixed)' testing `if k = 3': the same ladder
# reached through the formal's deref chain (LHLD K / MOV E,M / INX H / MOV D,M / XCHG /
# DCX H x3 / MOV A,H / ORA L / skip) -- a FORMAL and a plain automatic take the SAME arm,
# which is why the ladder must run after cmp_load_deref and not before it.
add_spec('E28N9', ('artefacts/N9.PLI', 'golden/e2e331d/N9/N9.REL'))
add_spec('E32C10', ('artefacts/E32C10.PLI', 'golden/e32c/E32C10/E32C10.REL'))

# [E2E-34/P6] the CHARACTER VARYING ASSIGNMENT family.  The same one bit per operand as
# [C212]'s comparison table, with the roles fixed by the direction of the store: the
# DESTINATION address must reach HL and the SOURCE address DE.
#   G9, G10  dest imm,  src imm   LXI H,U / LXI D,S          (G10 = both orientations)
#   G2,G7,G8 dest imm,  src load  load / XCHG / LXI H,U      (member source, formal source)
#   G1, G5   dest load, src imm   dest / LXI D,S
#   G3 -- member <- member written with an explicit qualifier -- is registered below as a
#            refusal: mine has only the bare-member source shape (V7), no probe of the
#            qualified one, and it must not be guessed in.
#   G6       dest load, src load  LHLD T / PUSH H / dest ladder / POP D   (formal source:
#            NETWORK line 101 `p->city_name = city;')
# G6/G7 additionally pin that a by-reference POINTER formal base needs the deref ladder
# BEFORE member_step -- a fact [C212] keys the same way and bmem_addr used to miss.
for _n in ('E34G1', 'E34G2', 'E34G4', 'E34G5', 'E34G6', 'E34G7', 'E34G8', 'E34G9', 'E34G10'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e34g/%s/%s.REL' % (_n, _n)))
REJECTS['E34G3'] = (open('artefacts/E34G3.PLI', "rb").read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
    "codegen: storing this expression into the VARYING member")
NEG_META['E34G3'] = ("my-gap", "DR COMPILES it (golden/e34g/E34G3: `hp->vn = jq->vn' -> LHLD JQ / PUSH H / LHLD HP / POP D / MVI A,14 / CALL ?SMVVM -- the [C212] load/load frame, destination in HL).  Mine refuses: store_vbvar's member-source branch keys on an Ast.Eident whose value kind is Vbvar (the bare `w' spelling V7 uses), so a source qualified with an explicit pointer name reaches the outer refusal.  The bytes to emit are visible in the golden; the refusal is kept because no probe shows what DR does when the two members belong to records of DIFFERENT types, and E34G3 has one sample only.")

# [E2E-35/P1] ON ... GOTO / REVERT in NORMAL FLOW -- three registrations, two of them executed.
# E32E2 (golden captured in E2E-32, byte-exact since E2E-34/P1) was never in the specimen panel:
# it is the only probe that pins TWO ON units with GOTO handlers in one block, the per-BLOCK
# hidden saved-SP cell [C206], and a REVERT whose ?REVOP sits in straight-line code.  Registering
# it costs nothing and closes a shape that was previously verified once, by hand.
# E35N1/E35N2 are new DR goldens built for this phase.  Neither reads anything: they register
# `on endfile(sysin) goto h', transfer through ordinary labels, and jump to `h' -- the label that
# ON/GOTO pads.  So they exercise the pad (LHLD cell / SPHL / CALL ?RECOV) and, in E35N2, ?REVOP,
# on a path where the ENDFILE condition NEVER fires.  Nothing here simulates an EOF event: there
# is no GET in either program, so there is nothing to deliver.  Both are byte-exact against DR
# and both are in the runtime panel -- first execution of this machinery at all.
# [E2E-38/P4, E2E-39/P1] Comparison-family probes from the e37e differential campaign.
# E37C1 (local-vs-literal) and E37C3 (formal-vs-literal) were byte-exact on arrival.  E37B1/B2/B3
# are PB4's shape -- an unqualified BASED scalar compared against a literal -- with z = 1, 3, 4.
# They were registered as DIVERGENT in E2E-38 on a disassembly reading that said DR dereferences
# the base before biasing while I bias the pointer; that is true of the INSTRUCTIONS, and E2E-39
# proved the consequence is a wrong value, but NOT where [C246] put it: `q > 3' agrees with DR at
# z = 1, 3, 4 and 40 for a reason that had nothing to do with the deref, while `q = 7' silently
# disagreed (golden/e39a/E39B4 -> r= 1, mine -> r= 0) and four purpose-built variants
# (golden/e39me2/E39V1..V4) all refused to take a branch they must take.  Root cause: cmp_load_deref
# gates the deref ladder on `st.deref', which the prologue fills with the procedure's POINTER FORMALS
# only, so a BASED view (kind Vbased, no cell of its own) never got one.  With the ladder emitted for
# Vbased/Vbfix/Vbptr names [C251], all four probes are byte-exact and PB4 -- a divergence this
# project carried for eleven episodes -- retires [C252].
# The rest of the campaigns (10+ probes DR accepts and I refuse, 2 DR rejects) is NOT registered
# here: registering a refusal message as a negative would pin my wording, not DR's behaviour
# [C247][C248]; they are carried as COVERAGE rows and counted by the corpus census.
for _n in ('E37C1', 'E37C3', 'E37B1', 'E37B2', 'E37B3'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e37e/%s/%s.REL' % (_n, _n)))
# [E2E-39/P1] PB4 was the divergence-row member of this family; it is now byte-exact against the
# same golden the divergence row named, so it moves here and keeps its RUNTIME row.
add_spec('PB4', ('artefacts/PB4.PLI', 'golden/e2e311d/PB4/PB4.REL'))

for _n in ('E32E2', 'E35N1', 'E35N2'):
    _t = 'e32e' if _n == 'E32E2' else 'e35n'
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/%s/%s/%s.REL' % (_t, _n, _n)))

# [E2E-35/P2] DE-register tracking: 37 probes, each byte-exact, each pinning one clause of the
# rule.  They are registered because the alternative is a rule protected by nothing -- member_step
# and hl_zero now decide bytes on EVERY based store in the panel, and 843 specimens that all agree
# by construction cannot tell me the rule is right, only that it is stable [C167].
#   e35r (12): which member loads leave DE available (LHLD+LXI D yes, PUSH H/LHLD/POP D no,
#              XCHG no) and the offsets/edges (255 -> MVI E, 2 -> INX D repeat, 1 -> INX D).
#   e35t (8):  what KILLS the knowledge (POP D, CALL, IF with a numeric condition, MVI E,
#              DCX D to a known value, an exactly-known DE whose HIGH byte is nonzero so the
#              zero-load cannot use it) and that a small offset is still reached by INX H.
#   e35v (10): the derivation ladder's boundaries (3 INX H vs 4 DAD; 255/256/257 around MVI E;
#              DCX D; MVI E that FORGETS DE afterwards; reuse across DE-neutral stores and
#              constant loads; reuse across an INX H that moved HL).
#   e35w (7):  three back-to-back qualifying stores; the zero load taking MOV H,D/MOV L,D on a
#              pointer, on a fixed auto (through hl_const's SECOND literal-into-HL copy [C202]),
#              and on a pointer formal's member; and the label target that makes DR reload.
_E35_P2 = {
    'E35R1': 'e35r', 'E35R2': 'e35r', 'E35R3': 'e35r', 'E35R4': 'e35r',
    'E35R5': 'e35r', 'E35R6': 'e35r', 'E35R7': 'e35r', 'E35R8': 'e35r',
    'E35R9': 'e35r', 'E35R10': 'e35r', 'E35R11': 'e35r', 'E35R12': 'e35r',
    'E35T1': 'e35t', 'E35T2': 'e35t', 'E35T3': 'e35t', 'E35T4': 'e35t',
    'E35T5': 'e35t', 'E35T6': 'e35t', 'E35T7': 'e35t', 'E35T8': 'e35t',
    'E35V1': 'e35v', 'E35V2': 'e35v', 'E35V3': 'e35v', 'E35V4': 'e35v',
    'E35V5': 'e35v', 'E35V6': 'e35v', 'E35V7': 'e35v', 'E35V8': 'e35v',
    'E35V9': 'e35v', 'E35V10': 'e35v',
    'E35W1': 'e35w', 'E35W2': 'e35w', 'E35W3': 'e35w', 'E35W4': 'e35w',
    'E35W5': 'e35w', 'E35W6': 'e35w', 'E35W7': 'e35w',
}
for _n, _t in sorted(_E35_P2.items()):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/%s/%s/%s.REL' % (_t, _n, _n)))

# [E2E-35/P2] four DIVERGENT rows are now byte-exact and move to the specimen panel: O1, O2, O4
# (the +3 code bytes each, attributed in E2E-31 to "one register-reuse rule missing, in the
# value-to-HL direction") and E30B2 (the BIT(1) traversal loop, +6).  All four were Family A.
# DE tracking, not HL reuse, is what closed them -- E31F1/E27S2/PB4, the rows whose cause really
# was HL/DE LIVENESS, are unchanged.  That distinction is recorded because the attribution was
# wrong and the fix would not have been found by someone trusting it.
for _n, _t in (('O1', 'e2e333d'), ('O2', 'e2e333d'), ('O4', 'e2e333d'),
               ('E30B2', 'e30p1')):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/%s/%s/%s.REL' % (_t, _n, _n)))

def divergence_load(path=DIVERGENT_FILE):
    rows = {}
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("name\t") or line.startswith("#"):
                # [E2E-35/P0] "#" lines are the column legend.  The panel carried no
                # definition of its own columns, which is how a count of reldump DATA
                # ITEMS came to be printed and cited as "code bytes" for two episodes:
                # the numbers looked plausible and nothing in the file said what they
                # meant.  RUNTIME.txt has its own loader and is unaffected.
                continue
            p = line.split("\t")
            if len(p) != 10:
                raise ValueError("DIVERGENT.txt malformed row: %r" % line[:40])
            rows[p[0]] = (p[1], p[2], int(p[3]), int(p[4]), int(p[5]),
                          int(p[6]), int(p[7]), p[8], p[9])
    return rows

def _rel_stats(rel):
    """(code_section_bytes, data_section_bytes) -- the sizes DR's own listing prints.

    [E2E-35/P0] This function used to return `len(re.findall("DATA\\s+code", dump))', i.e. a
    count of reldump's DATA *items*, and the divergence panel printed it as "N code bytes vs
    DR M".  It is not the code-section size: DR's .REL is a bit stream in which a clear bit
    introduces one byte at the current (segment, logical address), and the relocated operand
    words are fixed up by RELOC/CHAIN-EXT items that advance that address by two without
    adding an item -- so the item count is the section size minus the fixups, and on NETWORK
    it read 1096 while DR's listing and the file's own LINK-DEF-CODE-SIZE say 0x5B0 = 1456.
    Both quantities are real; only one of them is a size, and a row that quotes the wrong one
    makes an "+5 bytes of code" claim look true when the true excess is +7.

    The replacement reads LINK-DEF-CODE-SIZE / LINK-DEF-DATA-SIZE through reldump's decoder
    (one authority, [C202]) via tools/relstats.py.  That those fields ARE the listing numbers
    is not assumed: it is checked on 2583 DR-produced sizes, zero mismatches
    (`python3 tools/relstats.py --selfcheck golden').  A .REL with no DEF-CODE-SIZE record
    raises rather than reporting 0 -- an unknown size is not a zero size.
    """
    if "relstats" not in globals():
        import importlib.util as _iu
        _spec = _iu.spec_from_file_location(
            "relstats", os.path.join(ROOT, "tools", "relstats.py"))
        globals()["relstats"] = _m = _iu.module_from_spec(_spec)
        _spec.loader.exec_module(_m)
    m = relstats.measure(rel)
    def size(seg):
        if m[seg]["declared"] is None:
            raise AssertionError("%s: no LINK-DEF-%s-SIZE record" % (rel, seg.upper()))
        return m[seg]["declared"]
    return size("code"), size("data")

def divergence_check(dv, exe):
    fails, notes = [], []
    for n, (src, g, mc, dc, md, dd, nb, verdict, _note) in sorted(dv.items()):
        if n in SPECIMENS or n in REJECTS:
            fails.append("%s: registered in BOTH the divergence panel and a regression panel" % n)
            continue
        r = subprocess.run([exe, os.path.join(ROOT, src), "/tmp/div_%s.REL" % n],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fails.append("%s: no longer compiles -- row is STALE, move it to the negative panel "
                         "or fix the refusal (%s)" % (n, r.stderr.strip().splitlines()[-1][:60]))
            continue
        mine = open("/tmp/div_%s.REL" % n, "rb").read()
        dr = open(os.path.join(ROOT, g), "rb").read()
        if mine == dr:
            fails.append("%s: NOW BYTE-EXACT -- promote it into SPECIMENS and delete the "
                         "divergence row [C168 may be partly done]" % n)
            continue
        mcode, mdata = _rel_stats("/tmp/div_%s.REL" % n)
        dcode, ddata = _rel_stats(os.path.join(ROOT, g))
        ndiff = sum(1 for a, b in zip(mine, dr) if a != b)
        if (mcode, dcode, mdata, ddata, ndiff) != (mc, dc, md, dd, nb):
            fails.append("%s: divergence SHAPE changed (code %d/%d data %d/%d ndiff %d recorded vs "                         "now %d/%d %d/%d %d) -- re-measure before accepting [C168]"
                         % (n, mc, dc, md, dd, nb, mcode, dcode, mdata, ddata, ndiff))
        else:
            # [E2E-23] this line used to HARDCODE "data agrees" and "(C168 peephole)".  Both were
            # false for the ZK8/ZK10/ZK11 rows, whose data areas differ (16 vs 19) and whose cause
            # is DR's out-of-range-literal route.  The panel must not print a statement the row
            # itself contradicts, so both now come from the measurement and from the row.
            notes.append("%s: CODE SECTION %d bytes vs DR %d, DATA SECTION %s, %d file bytes "
                         "differ -- row cause: %s"
                         % (n, mcode, dcode,
                            ("agrees (%d)" % mdata) if mdata == ddata
                            else "DIFFERS (%d vs DR %d)" % (mdata, ddata),
                            ndiff, dv[n][-1][:90]))
    return fails, notes


def divergence_remeasure(dv, exe, only=None, path=DIVERGENT_FILE):
    """[E2E-35/P2] Rewrite the measured columns of spec/DIVERGENT.txt from the gate's OWN
    measurement, keeping each row's verdict and cause text.

    The rows carried numbers that could only be produced by running the gate, and there was no
    sanctioned way to refresh them: when DE tracking changed four shapes, the stale rows failed
    with "re-measure before accepting" and the only route left was to read the numbers off the
    failure message and type them into the file by hand.  A number moved by hand is a number that
    can be moved wrongly [C198], so the writer lives beside the reader and uses the same
    `_rel_stats'.

    A row that is now BYTE-EXACT is NOT quietly dropped -- this returns it in `promoted' and
    writes nothing, because promoting means registering a specimen and deleting the row, which is
    a decision, not a measurement [C168].  A row that stopped compiling is reported the same way.
    """
    rows, changed, promoted, broken = [], [], [], []
    with open(path) as f:
        raw = f.read().split("\n")
    header = raw[0]
    for line in raw[1:]:
        if not line or line.startswith("#"):
            rows.append(line); continue
        p = line.split("\t")
        if len(p) != 10:
            raise ValueError("DIVERGENT.txt malformed row: %r" % line[:40])
        name = p[0]
        if only and name not in only:
            rows.append(line); continue
        r = subprocess.run([exe, os.path.join(ROOT, p[1]), "/tmp/divrm_%s.REL" % name],
                           capture_output=True, text=True)
        if r.returncode != 0:
            broken.append((name, r.stderr.strip().splitlines()[-1][:60])); rows.append(line); continue
        mine = open("/tmp/divrm_%s.REL" % name, "rb").read()
        dr = open(os.path.join(ROOT, p[2]), "rb").read()
        if mine == dr:
            promoted.append(name); rows.append(line); continue
        mc, md = _rel_stats("/tmp/divrm_%s.REL" % name)
        dc, dd = _rel_stats(os.path.join(ROOT, p[2]))
        nb = sum(1 for a, b in zip(mine, dr) if a != b)
        old = (int(p[3]), int(p[4]), int(p[5]), int(p[6]), int(p[7]))
        new = (mc, dc, md, dd, nb)
        rows.append("\t".join([name, p[1], p[2]] + [str(x) for x in new] + [p[8], p[9]]))
        if old != new:
            changed.append("%s: code %d/%d -> %d/%d, data %d/%d -> %d/%d, file bytes differing "
                           "%d -> %d" % (name, old[0], old[1], new[0], new[1],
                                         old[2], old[3], new[2], new[3],
                                         old[4], new[4]))
    if promoted or broken:
        for n in promoted:
            print("e2e gate: DIVERGENT %s is byte-exact -- register it as a specimen and delete "
                  "the row; nothing was rewritten" % n)
        for n, why in broken:
            print("e2e gate: DIVERGENT %s no longer compiles (%s) -- nothing was rewritten for it"
                  % (n, why))
        if changed:
            for c in changed:
                print("e2e gate: %s" % c)
        print("e2e gate: ABORTED rewrite -- %d row(s) need a decision first" % (len(promoted) + len(broken)))
        return 2
    out = "\n".join(rows)
    assert isinstance(out, str) and len(out) > 100
    with open(path + ".new", "w") as f:
        f.write(out)
    os.replace(path + ".new", path)
    print("e2e gate: DIVERGENT.txt re-measured (%d row(s) rewritten%s)"
          % (len(only) if only else len(rows) - 2, "" if not changed else ", %d changed" % len(changed)))
    return 0


def registration_audit(path, specimens, rejects, negmeta):
    """Mechanical prevention of regression-list key collisions [E2E-15/C154].

    This file has suffered key collisions three times: E2E-12 (a SPECIMENS.update() block
    silently replaced five long-standing specimens), E2E-13 (T4/T8 keys would have replaced
    existing ones) and E2E-14 (P9 was anchored into REJECTS while also being a specimen).
    Python dicts overwrite WITHOUT an error, so a collision is invisible from the panel
    output -- the gate quietly tests a smaller set than it reports.

    Two checks, each aimed at one failure mode:
      (1) STATIC, per dict-literal / .update() block: a key written twice INSIDE one
          registration block is an overwrite -- the E2E-12 shape.  A key that appears once
          per block in different blocks (REJECTS and NEG_META deliberately share names) is
          not flagged.
      (2) RUNTIME over the built dicts: no name may be both a byte-exact SPECIMENS entry and
          a REJECTS entry [the E2E-14 shape], and REJECTS/NEG_META must stay symmetric so a
          verdict explanation can never be lost.
    Negative-tested against all three induced shapes before it was wired in.
    """
    lines = open(path).read().splitlines()
    dupes = []
    k = 0
    while k < len(lines):
        ln = lines[k]
        m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.update\s*)?\([^)]*\{', ln)
        if not m:
            k += 1
            continue
        name = m.group(1)
        keys = []
        depth = 1
        j2 = k          # keys can sit on the opening line itself
        first = True
        while j2 < len(lines) and depth:
            l2 = lines[j2]
            if not first:
                depth += l2.count('{') - l2.count('}')
            first = False
            for m2 in re.finditer(r'(?:^|[{,])\s*"([A-Za-z0-9_]+)"\s*:', l2):
                keys.append((m2.group(1), j2 + 1))
            j2 += 1
        once = {}
        for key, lineno in keys:
            if key in once:
                dupes.append((name, key, once[key], lineno))
            else:
                once[key] = lineno
        k = j2
    if dupes:
        raise RegistrationCollision(
            "duplicate key inside one registration block (silently overwrites): %s"
            % ", ".join("%s[%s] lines %d and %d" % d for d in dupes))
    ov = set(specimens) & set(rejects)
    if ov:
        raise RegistrationCollision(
            "registered as BOTH a byte-exact specimen and a refusal: %s" % sorted(ov))
    bad = sorted(k for k, v in negmeta.items()
                 if not (isinstance(v, tuple) and len(v) == 2))
    if bad:
        raise RegistrationCollision(
            "NEG_META values must be (category, verdict) 2-tuples; malformed: %s -- with a bare "
            "string the panel's `cat, _dv = ...' aborts, and inventory_snapshot's v[1] silently "
            "yields ONE CHARACTER instead of the verdict, which then gets COMMITTED as if it were "
            "evidence [E2E-17, CONV/DECY]" % bad[:6])
    if set(rejects) != set(negmeta):
        raise RegistrationCollision(
            "REJECTS/NEG_META asymmetric, verdict evidence lost: rejects-only=%s "
            "negmeta-only=%s"
            % (sorted(set(rejects) - set(negmeta)), sorted(set(negmeta) - set(rejects))))
    return len(specimens) + len(rejects)


INVENTORY = os.path.join(ROOT, "spec", "INVENTORY.txt")


def rows_of(specimens):
    return list(specimens.items())


def esc(t):
    """One row per entry: a refusal's source is multi-line PL/I, and an unescaped newline
    there silently turns one inventory row into twenty, which the reader rejects as
    malformed.  Round-trips through the parser below."""
    return t.replace("\\", "\\\\").replace("\n", "\\n")


def unesc(t):
    out, i = [], 0
    while i < len(t):
        if t[i] == "\\" and i + 1 < len(t):
            nxt = t[i + 1]
            out.append("\n" if nxt == "n" else ("\\" if nxt == "\\" else nxt))
            i += 2
        else:
            out.append(t[i]); i += 1
    return "".join(out)


def inventory_snapshot(specimens, rejects, negmeta):
    """Canonical (name, kind, source, golden-or-refusal-tag) rows for the whole panel.
    A specimen's two paths ARE its identity; a refusal is keyed by its reason tag so a
    changed explanation shows up as a substitution too."""
    rows = {}
    for n, (src, gold) in specimens.items():
        rows[n] = ("specimen", src, gold)
    for n in rejects:
        rows[n] = ("refusal", rejects[n][0], negmeta.get(n, ("", ""))[1])
    return rows


def inventory_check(path, rows, write=False):
    """Mechanically checked inventory of regression identities [E2E-16/P3].

    C154 (registration_audit) compares keys WITHIN the live panel, so it can see a duplicate
    write but NOT a REMOVAL, and not a SUBSTITUTION -- and every failure this project has had
    in this area is one of those two:
      E2E-12  five long-standing specimens silently replaced by colliding keys -- the panel
              kept the same shape while testing something else;
      E2E-15  P9 dropped entirely while "simplifying" its registration -- a removal, invisible
              to a key-collision check, which is why I only noticed a total of 509.
    A count cannot catch either: removing one specimen and adding another leaves the total
    identical while the panel's coverage changes.  So this compares the exact SET of
    (name, kind, source, golden) tuples against a COMMITTED file and requires an intentional,
    reviewed `--update-inventory` whenever a specimen is added, retired or repointed.
    Exit 2 with the precise diff on any change, so an unreviewed edit cannot pass the gate.
    """
    if write:
        with open(path, "w") as fh:
            fh.write("# DR PL/I-80 e2e regression inventory -- MACHINE-MAINTAINED FILE\n")
            fh.write("# One row per panel entry: name\tkind\tsource\tgolden-or-refusal-reason\n")
            fh.write("# Add/retire/repoint a specimen with: python3 tools/e2e_gate.py --update-inventory\n")
            fh.write("# The gate aborts if this file and the live panel disagree (E2E-16/P3).\n")
            for n in sorted(rows):
                k, a, b = rows[n]
                fh.write("%s\t%s\t%s\t%s\n" % (n, k, esc(a), esc(b)))
        return []
    if not os.path.exists(path):
        return ["inventory file %s does not exist -- run --update-inventory" % path]
    old = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 4:
            return ["inventory file is malformed at: %r" % line[:60]]
        old[parts[0]] = tuple(unesc(x) for x in parts[1:])
    errs = []
    removed = sorted(set(old) - set(rows))
    added = sorted(set(rows) - set(old))
    subst = sorted(n for n in set(old) & set(rows) if old[n] != rows[n])
    if removed:
        errs.append("%d entr%s REMOVED from the panel without an inventory update: %s"
                    % (len(removed), "y" if len(removed) == 1 else "ies", removed[:12]))
    if added:
        errs.append("%d entr%s ADDED without an inventory update: %s"
                    % (len(added), "y" if len(added) == 1 else "ies", added[:12]))
    if subst:
        errs.append("%d entr%s SUBSTITUTED (same name, different reference -- a count cannot "
                    "see this): %s" % (len(subst), "y" if len(subst) == 1 else "ies", subst[:12]))
        for n in subst[:4]:
            errs.append("    %s: inventory=%s  panel=%s" % (n, old[n], rows[n]))
    return errs


# =====================================================================================
# [E2E-32/P3] INDEPENDENT-EXPECTATION RUNTIME PANEL  (opt-in: --runtime)
#
# This is deliberately NOT a second test framework.  It reuses compile_one, so the object
# it executes is the SAME bytes the byte-parity arm compares, and oracle/linkrun.py, the
# same link + cpmsim path the --link-run arm already uses.
#
# Why it exists: the positive panel proves REL identity against DR, and the divergence
# panel documents shape differences -- neither one proves a program prints the right
# NUMBER.  Both wrong-value families of this milestone were invisible to 759 byte-exact
# specimens [C137][C200], and they were caught only by executing.  This pins the
# expectations so a future change cannot silently re-break them.
#
# The three claims stay separate and the panel says which one did the work [C205]:
#   byte parity vs DR         -- the main panel, cmp on .REL
#   independent arithmetic    -- THIS panel
#   running a byte-identical  -- adds nothing about MY code; for such a row the run
#   image                       validates the expectation and DR's oracle together
# Rows whose .REL is shape-divergent (E32B3, PB4) are the non-circular ones, and their
# note field records that.
RUNTIME_FILE = os.path.join(ROOT, "spec", "RUNTIME.txt")
RUNTIME_FIELDS = ("name", "kind", "golden", "mine", "expected", "exit", "source", "note")


def runtime_load(path=RUNTIME_FILE):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("name\t"):
                continue
            p = line.split("\t")
            if len(p) != len(RUNTIME_FIELDS):
                raise ValueError("RUNTIME.txt malformed row: %r" % line[:40])
            rows.append(dict(zip(RUNTIME_FIELDS, p)))
    names = [r["name"] for r in rows]
    if len(names) != len(set(names)):
        raise ValueError("RUNTIME.txt duplicate name -- a dict overwrite would hide it [C158]")
    return rows


def runtime_check(rows, verbose=True):
    """Link and execute each row's object; return a list of failure strings."""
    import re as _re
    fails = []
    for r in rows:
        name = r["name"]
        src = r["source"] if os.path.exists(os.path.join(ROOT, r["source"])) \
            else (SPECIMENS.get(name, (None, None))[0] or r["source"])
        rel, rc, err = compile_one(name, src)
        if rc != 0:
            fails.append("RUNTIME %s: build refused (rc=%d) -- a runtime row must not "
                         "silently degrade into a refusal: %s"
                         % (name, rc, (err or "").strip().splitlines()[-1:][0][:70] if err else ""))
            continue
        golden = os.path.join(ROOT, r["golden"])
        if not os.path.exists(golden):
            fails.append("RUNTIME %s: golden %s missing" % (name, r["golden"]))
            continue
        exact = open(rel, "rb").read() == open(golden, "rb").read()
        tag = "e32rt_%s" % name
        d = os.path.join(ROOT, "golden", tag, name)
        os.makedirs(d, exist_ok=True)
        shutil.copy(rel, os.path.join(d, name + ".REL"))
        prn = os.path.splitext(r["golden"])[0] + ".PRN"
        if not os.path.exists(os.path.join(ROOT, prn)):
            fails.append("RUNTIME %s: no PRN at %s (external refs cannot resolve)" % (name, prn))
            continue
        shutil.copy(os.path.join(ROOT, prn), os.path.join(d, name + ".PRN"))
        lr = subprocess.run([sys.executable, os.path.join(ROOT, "oracle", "linkrun.py"),
                             "link", "--tag", tag, "--names", name, "--out", tag, "--reuse"],
                            capture_output=True, text=True, cwd=ROOT)
        com = os.path.join(ROOT, "golden", tag, name + ".COM")
        if lr.returncode != 0 or not os.path.exists(com):
            fails.append("RUNTIME %s: LINK failed rc=%d -- a .COM appearing is not the test "
                         "[C137]: %s" % (name, lr.returncode, (lr.stdout or "")[-80:]))
            continue
        rr = subprocess.run([sys.executable, os.path.join(ROOT, "oracle", "linkrun.py"),
                             "run", "--tag", tag, "--out", tag, "--names", name, "--reuse"],
                            capture_output=True, text=True, cwd=ROOT)
        op = os.path.join(ROOT, "golden", tag, name + ".output.txt")
        if not os.path.exists(op):
            fails.append("RUNTIME %s: no console output file (run rc=%d)" % (name, rr.returncode))
            continue
        raw = open(op, "rb").read()
        if b"timeout-or-hang" in (rr.stdout or "").encode() or "timeout" in (rr.stdout or ""):
            fails.append("RUNTIME %s: did not terminate -- execution must be observed to END "
                         "[C205]" % name)
            continue
        # raw console bytes are preserved; only CRLF->LF and PL/I edit-strip padding are
        # normalised, because `put list' pads numerics with spaces.
        norm = _re.sub(r" +", " ", raw.replace(b"\r\n", b"\n").decode("ascii", "replace"))
        # [E2E-41/P1b] an expectation may also be NEGATIVE, written `!text'.  A program with
        # no PUT statement prints nothing at all -- P081Q and P072H are `open / get / close'
        # with no output -- and "the console is empty" is not an assertion: an empty expected
        # string matches every transcript.  What IS assertable is the absence of the failure
        # DR's file runtime reports when an OPEN cannot find its FCB: `UNDEFINED FILE (1),
        # File: F=NUL' plus a traceback, measured in
        # spec/lab-evidence/e2e41-p1/RUN-P081Q-no-F.DAT.txt.  A row that demands that text be
        # ABSENT is a real test: the same staged-file machinery, run without the data file,
        # fails it.
        missing, forbidden = [], []
        for e in r["expected"].split("|"):
            if not e:
                continue
            if e.startswith("!"):
                if e[1:] in norm:
                    forbidden.append(e)
            elif e not in norm:
                missing.append(e)
        if missing or forbidden:
            fails.append("RUNTIME %s: expected %s, forbidden-but-present %s, got %r  [%s]"
                         % (name, missing, forbidden, norm[:60],
                            "byte-exact image" if exact else "shape-divergent"))
        elif verbose:
            print("  runtime %-8s OK  %-34s  [%s]"
                  % (name, norm.strip()[:34].replace("\n", " "),
                     "byte-exact image: run validates expectation+oracle, not my lowering"
                     if exact else "NON-CIRCULAR: images differ, this run is evidence about mine"))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--link-run", action="store_true")
    ap.add_argument("--skip-selftest", action="store_true",
                    help="do not run the pre-flight selftests (reldump "
                         "field-visibility + linkrun C137 undefined-symbol) "
                         "first (debug only -- a real gate run must not use it)")
    ap.add_argument("--update-inventory", action="store_true",
                    help="rewrite spec/INVENTORY.txt from the live panel, then exit -- the "
                         "only sanctioned way to add/retire/repoint a specimen [E2E-16/P3]")
    ap.add_argument("--update-divergent", nargs="*", metavar="NAME",
                    help="[E2E-35/P2] rewrite the MEASURED columns of spec/DIVERGENT.txt from "
                         "this gate's own measurement (cause text preserved); with no NAMEs, all "
                         "rows.  Refuses if any row became byte-exact or stopped compiling.")
    ap.add_argument("--only-divergent", action="store_true",
                    help="run only the --update-divergent arm, on the freshly built compiler")
    ap.add_argument("--runtime", action="store_true",
                    help="[E2E-32/P3] link and execute the spec/RUNTIME.txt panel and check "
                         "independently derived expectations (slow; opt-in)")
    ap.add_argument("--only", nargs="*", metavar="NAME",
                    help="restrict the --link-run arm to these specimens "
                         "(byte-parity compile still runs for all)")
    a = ap.parse_args()
    # [E2E-11 step 4] the decoder this gate's DIAGNOSTICS rely on is itself under
    # test.  reldump.py once hid every (SEGMENT,ADDRESS) payload, so two files whose
    # LINK-CHAIN-ADDRESS targets differed printed as identical and I recorded a
    # false byte-parity claim (C123 retraction).  A tool's blind spot is invisible
    # from inside its own output, so it is checked before any specimen is compiled;
    # raw `cmp` on .REL bytes remains the acceptance criterion either way.
    # [E2E-37/P2] the measurement system is under test too.  COVERAGE.tsv and the corpus
    # census are the only places that record "what does DR accept?", and both were wrong
    # before they were machine-checked -- a 49-file directory listing read as a 44-program
    # corpus, and a hand-written refusal count that did not add up.  They are validated on
    # every gate run, before any specimen compiles: a coverage row may not cite a probe that
    # is on no panel, a claim that does not exist, a corpus program the census does not
    # contain, or a manual page the banked OCR text does not support.
    for tool, argv in (("coverage panel", [sys.executable,
                                           os.path.join(ROOT, "tools/coverage_check.py")]),
                       ("corpus census", [sys.executable,
                                          os.path.join(ROOT, "tools/corpus_census.py"),
                                          "--verify",
                                          os.path.join(ROOT, "spec/census/corpus-census.json")])):
        rr = subprocess.run(argv, capture_output=True, text=True)
        tl = [l for l in (rr.stdout + rr.stderr).splitlines() if l.strip()]
        want = ("rows," if tool == "coverage panel" else "counts:")
        line = next((l for l in tl if want in l), tl[-1] if tl else "(no output)")
        print(f"{tool:16s} {line}")
        if tool == "coverage panel":
            for l in tl:
                if l.startswith("coverage_check: corpus") or l.startswith("coverage_check: census"):
                    print(f"{tool:16s} {l}")
        if rr.returncode != 0:
            for l in tl:
                if l.startswith(("ERROR", "FAIL", "coverage_check: corpus",
                                 "coverage_check: census")):
                    print("   " + l)
            # [E2E-40/P4] CIRCULARITY GUARD.  coverage_check.load_panel() resolves probe keys
            # against the COMMITTED spec/INVENTORY.txt, and --update-inventory writes that file
            # further down this same function -- AFTER this exit.  So the moment a specimen is
            # added to SPECIMENS and cited in COVERAGE.tsv's probes column, the normal gate fails
            # (correctly: the citation is not yet on the panel) and --update-inventory aborts
            # before it can register it.  The panel is unreachable: adding a byte-exact specimen
            # would need the inventory to already contain it.
            # In --update-inventory mode the coverage panel is therefore reported, not fatal.
            # Nothing is lost: the flag is an explicit "I am changing the panel" act, the
            # inventory guard still runs on every ordinary gate invocation (and aborted me at
            # E2E-16/P3 for exactly that), and the very next gate run re-validates coverage
            # against the freshly written inventory -- which is the sequence this exists to allow.
            if a.update_inventory:
                print("e2e gate: coverage panel errors above are NOT fatal under "
                      "--update-inventory (panel-registration cycle); the next gate run "
                      "re-validates them against the rewritten inventory")
            else:
                sys.exit(1)

    # raw `cmp` on .REL bytes remains the acceptance criterion either way.
    if not a.skip_selftest:
        # [E2E-15/C154] regression-list collisions have produced false confidence three
        # times, and a dict overwrite leaves no trace in the output -- check the panel's own
        # bookkeeping before compiling anything against it.
        inv_errs = inventory_check(INVENTORY, inventory_snapshot(SPECIMENS, REJECTS, NEG_META),
                                   write=a.update_inventory)
        if a.update_inventory:
            print("e2e gate: inventory rewritten (%d entries) -- review `git diff "
                  "spec/INVENTORY.txt' as part of this change" % len(inv_errs or rows_of(SPECIMENS)))
            return 0
        if a.only_divergent:
            # [E2E-35/P2] the measurement arm needs the same compiler the panel uses, and it
            # must NOT be run against a stale binary -- that is how a row gets re-measured
            # against bytes that no longer exist.
            _exe = os.path.join(ROOT, "ocaml", "_build", "default", "bin", "pli80c.exe")
            return divergence_remeasure(divergence_load(), _exe, only=a.update_divergent)
        if inv_errs:
            for e in inv_errs:
                print("e2e gate: INVENTORY: %s" % e)
            print("e2e gate: ABORTED -- panel and committed inventory disagree; if the change "
                  "is intentional, run --update-inventory and commit the diff")
            return 2
        try:
            registration_audit(os.path.join(ROOT, "tools", "e2e_gate.py"),
                               SPECIMENS, REJECTS, NEG_META)
        except RegistrationCollision as e:
            print("e2e gate: ABORTED -- registration collision: %s" % e)
            return 2
    if not a.skip_selftest:
        # [E2E-12/C137] the link-stage undefined-symbol detector gets the same
        # treatment as reldump's field-visibility check: it is the thing standing
        # between "a .COM appeared" and "the program can actually run", and it fails
        # silently in exactly the direction that matters (a broken link reads as
        # clean).  Pinned to golden/e2e153_l3 / _l4 plus a synthetic segment whose
        # symbol sits beyond any display window, so presentation can never again be
        # mistaken for detection.
        r = subprocess.run([sys.executable, os.path.join(ROOT, "oracle",
                                                          "linkrun.py"),
                            "selftest"], capture_output=True, text=True)
        for line in (r.stdout or "").strip().splitlines():
            print("  linkrun: " + line)
        if r.returncode != 0:
            print("e2e gate: ABORTED -- linkrun selftest failed "
                  "(C137 undefined-symbol detection)")
            if r.stderr:
                print(r.stderr.strip()[-400:])
            sys.exit(2)
        st = subprocess.run([sys.executable, os.path.join(ROOT, "tools",
                            "reldump.py"), "--selftest"], capture_output=True,
                            text=True)
        if st.returncode != 0:
            print(st.stdout.strip() or st.stderr.strip())
            print("e2e gate: ABORTED -- reldump selftest failed")
            return 2
    ok = bad = 0
    for name, (src, gold) in SPECIMENS.items():
        gp = os.path.join(ROOT, gold)
        if not os.path.exists(gp):
            print(f"GOLDEN-MISSING {name}: registered specimen has no DR object at {gold}")
            print(f"               (a SKIP is NOT a pass -- 'verify DR actually produced each "
                  f"reference object'; mistagging a probe used to hide here, E2E-16)")
            bad += 1
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
    # [E21/P0] third panel: programs that COMPILE but are not byte-exact [C168].  Checked here so
    # it cannot rot: every row must still build, still differ, and still diverge in the recorded
    # SHAPE.  Becoming byte-exact is a FAILURE ("promote it"), and so is starting to refuse.
    _dv = divergence_load()
    _dvf, _dvn = divergence_check(_dv, CC)
    for _x in _dvn:
        print("  DIV-OK   %s" % _x)
    for _x in _dvf:
        print("  DIV-FAIL %s" % _x)
    if _dvf:
        print("e2e gate: DIVERGENCE PANEL %d fail of %d" % (len(_dvf), len(_dv)))
        return 1
    print("e2e gate: divergence panel %d/%d as recorded (compiles, differs, shape pinned)"
          % (len(_dv), len(_dv)))
    # [E2E-32/P3] independent-expectation runtime arm (opt-in).  Runs after the byte and
    # divergence panels so a byte regression is reported first, and can fail the gate alone.
    if a.runtime:
        _rt = runtime_load()
        print("e2e gate: runtime panel (%d rows; the object executed is the one the byte "
              "check compares)" % len(_rt))
        _rtf = runtime_check(_rt)
        for _x in _rtf:
            print("e2e gate: %s" % _x)
        if _rtf:
            print("e2e gate: RUNTIME PANEL %d fail of %d" % (len(_rtf), len(_rt)))
            return 1
        print("e2e gate: runtime panel %d/%d as recorded (expectation + termination)"
              % (len(_rt), len(_rt)))

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
            # [E2E-41/P2b] the anchor is the COMMAND ECHO line, and linkrun's
            # ARGS puts a command tail on it (`D>E17B INF.DAT'), so a bare
            # `{name}\r\r\n' pattern never matches a tailed run -- the first
            # P2b gate run printed MISSING TRANSCRIPT for exactly that reason.
            # No OUTPUT_CHECK name had ever been run with a tail before FILE I/O
            # (ARGS was introduced for E16/E17/E18 in e2e-11), so the hole was
            # invisible; the tail is now part of the anchor.
            m = _re.search(rf"{name}(?: [^\r\n]*)?\r\r\n(.*?)(?=\nD>|I/O ran|\Z)",
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


# ==================================================================== [E2E-35/P3]
# NETWORK is BYTE-EXACT.  Its last remaining .REL difference was NOT the linkage-record
# encoding hypothesised at the end of P2 (C225 said "a LINKAGE record, not an instruction").
# Probes E35X1-X4 say something simpler and worse: a label defined in a nested procedure must
# SHADOW an identically named label in an enclosing block.  Both main and print_paths define
# `eof'; mine resolved print_paths' ON ... GOTO through an emission-ordered flat list and found
# MAIN's already-emitted pad -- an inline RELOC pointing into another block's recovery chain,
# i.e. a live wrong address.  Replacing that lookup with a scoped one took NETWORK from 1608
# differing file bytes to zero (code 1456 = DR's CODE SIZE 05B0, data 235 = DR's 00EB).
add_spec('NETWORK', ('artefacts/NETWORK.PLI', 'golden/first8080u/NETWORK/NETWORK.REL'))
# its DIVERGENT.txt row is deleted in the same step -- rows are data in that file, and the gate
# fails a row whose bytes became exact (that is how this was caught, [C168]).

# [E2E-35/P3] the six DR goldens that pin the two rules whose combination closed NETWORK.
#   X2, X3, Y1, Y2 -- a SUBROUTINE (no RETURNS) whose last top-level statement is `goto',
#     `return;' or `stop;' gets NO tail RET.  Each was mine's single extra byte, and they are
#     the positive half of a rule I had written only for value-returning procedures [C213].
#   Y3, Y4 (below, as refusals) are its controls: a `goto' followed by a live statement, or a
#     conditional goto, ends `... SHLD N / RET' in DR, so the rule is fall-out, not GOTO.
#   X1, X4 -- label shadowing, with the nested ON-unit's pad and its own label's chain.
#   X3 is the control that says shadowing was never in doubt as a mechanism: DR compiles two
#     blocks with the same label name, and NETWORK proves it is what DR does there too.
_E35_P3 = {
    'E35X1': 'e35x', 'E35X2': 'e35x', 'E35X3': 'e35x',
    'E35X4': 'e35y', 'E35Y1': 'e35y', 'E35Y2': 'e35y',
}
for _n, _t in sorted(_E35_P3.items()):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/%s/%s/%s.REL' % (_t, _n, _n)))

# [E2E-36/P2+P4] E35X5, E35Y3 and E35Y4 were registered as controlled refusals in E2E-35/P3
# because a GOTO whose label lives in an enclosing block had no rule here: mine either jumped
# into the wrong stack frame or refused.  Cross-block transfer is now implemented (program-wide
# label survey in bind.ml, scope-chain resolution in codegen.ml) and all three are BYTE-EXACT
# against their DR goldens, so per [C154] they leave the negative panel and join the specimens.
# The E2E-36 probe set goes with them: every probe DR compiled and mine now matches exactly is
# registered, because a shared encoder (the HL constant model) just changed and [C179] says the
# way to notice the collateral is to have the new shapes in the panel, not in a scratch script.
for _n, _t in (('E35X5', 'e35y'), ('E35Y3', 'e35y'), ('E35Y4', 'e35y')):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/%s/%s/%s.REL' % (_t, _n, _n)))

# the cross-block GOTO orientations that come out byte-exact.  T2/T6/T7/T11/T12/T13 are the
# mechanism matrix (same-block control, ON-unit forms, pad sharing, unreferenced target); T3/T5/T8
# are the multi-target, nested-BEGIN and enclosing-block-already-padded orientations that E2E-35
# could only refuse; T13 additionally pins [C233] (a nested BEGIN block referencing its own outer
# block's label gets no pad of its own).
for _n in ('E36T2', 'E36T3', 'E36T4', 'E36T5', 'E36T6', 'E36T7', 'E36T8', 'E36T11', 'E36T12',
           'E36T13', 'E36T14'):
    add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e36t/%s/%s.REL' % (_n, _n)))

# the HL constant-model ladder [E2E-36/P4], one probe per arm: bump (+1/+2/-1/-2: H1,H2,H3,H9,H10,
# H24,H25,H26,H27,H28), no load at all (H4,H15), MVI L in the same high byte (H5,H33,H34), the
# destination-independence of the model (H30), the kill at a label definition (H29), the kill at an
# IF join and at a conditional landing pad with an ELSE (H8,H35), CALL and test kills (H6,H7,H8),
# dead-code reuse in a nested procedure (H14), and the zero/high-byte-change reloads (H10,H13->H20).
for _n in ('E36H1', 'E36H2', 'E36H3', 'E36H4', 'E36H5', 'E36H6', 'E36H7', 'E36H8', 'E36H9',
           'E36H10', 'E36H11', 'E36H12', 'E36H14', 'E36H15', 'E36H24', 'E36H25', 'E36H26',
           'E36H27', 'E36H28', 'E36H29', 'E36H30', 'E36H32', 'E36H33', 'E36H34', 'E36H35'):
    if (os.path.exists('golden/e36h/%s/%s.REL' % (_n, _n))
            and os.path.exists('artefacts/%s.PLI' % _n)):
        add_spec(_n, ('artefacts/%s.PLI' % _n, 'golden/e36h/%s/%s.REL' % (_n, _n)))

# [E2E-36/P4] two divergences that the HL-constant work CLOSED, promoted per [C154].
# E29X3 (`p = null; do while (p ^= null); ... p = null; end;') had been pinned as "DR reuses
# HL = 0 across a preceding SHLD where mine reloads"; E30L1 is the pre-test pointer traversal
# with the same single excess load.  Both are now byte-exact against their goldens.
# E27S2's source is artefacts/ST2.PLI (the S2 slice of E2E-27), not artefacts/E27S2.PLI: the
# panel key and the file name have never been the same thing for the e2e3xx goldens.
for _n, _s, _t in (('E29X3', 'E29X3', 'e2e362'), ('E30L1', 'E30L1', 'e30p1'),
                   ('E27S2', 'ST2', 'e2e323d')):
    if os.path.exists('golden/%s/%s/%s.REL' % (_t, _s, _s)):
        add_spec(_n, ('artefacts/%s.PLI' % _s, 'golden/%s/%s/%s.REL' % (_t, _s, _s)))

# [E2E-36/P1] `GOTO <procedure entry label>' is DR's NOT LABEL error in every orientation, and mine
# refuses the same way for the same reason: a procedure name is not a transfer target, it is the
# entry of a frame that has to be CALLED.  E35X3 was the earlier witness with the same diagnosis;
# these five cover nonlocal exit, sibling entry, own-block entry and the nested-outer mix.
for _n in ('E36T9', 'E36T10', 'E36T15', 'E36T16', 'E36T17'):
    REJECTS[_n] = (open('artefacts/%s.PLI' % _n, 'rb').read().replace(b"\r\n", b"\n")
                   .rstrip(b"\x1a").decode(), "NOT LABEL")
    NEG_META[_n] = ("dr-refuses", (
        "DR diagnoses it as NOT LABEL (golden/e36t/%s/%s.PRN) and mine refuses with the same "
        "words: the target of the GOTO is the entry label of a nested procedure, which is a "
        "procedure name, not a label.  [E2E-36/P1] established this for all four orientations -- "
        "exit to an enclosing block's procedure, entry of a sibling, entry of oneself, entry of an "
        "inner procedure from the enclosing block -- so bind.ml keeps procedure entries out of a "
        "block's label set and resolve_label answers Lbl_not_label rather than resolving through "
        "the scope chain." % (_n, _n)))


if __name__ == "__main__":
    sys.exit(main())
