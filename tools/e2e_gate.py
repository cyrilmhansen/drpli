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
    "N23_CHARVAR_MULTI": ("t:\n  procedure options(main);\n"
                          "  dcl c char(4) varying;\n  dcl i fixed;\n"
                          "  c = 'Q';\n  i = 1;\n"
                          "  put list(c, i);\nend t;\n",
                          "char var in multi-item"),
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
    "N29_DECININT": ("t:\n  procedure options(main);\n"
                     "  dcl d fixed dec(9,0);\n  dcl i fixed;\n"
                     "  i = 1;\n  i = i + d;\nend t;\n",
                     "mixed decimal/integer arithmetic unproven"),
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
    "N58_MUL_TWO": (
        "t:\n  procedure options(main);\n  dcl x fixed;\n  x = 5;\n"
        "  x = x * 2;\n  stop;\nend t;\n",
        "MULTIPLY by literal 2 is strength-reduced"),
    "N59_MUL_ONE": (
        "t:\n  procedure options(main);\n  dcl x fixed;\n  x = 5;\n"
        "  x = x * 1;\n  stop;\nend t;\n",
        "MULTIPLY by literal 1 is strength-reduced"),
    "N60_MUL_LITERAL_LEFT": (
        "t:\n  procedure options(main);\n  dcl x fixed;\n  x = 5;\n"
        "  x = 3 * x;\n  stop;\nend t;\n",
        "LITERAL on the LEFT is commuted"),
    # ---- [E2E-10 step 2] FLOAT perimeter: every UNSAMPLED behaviour is a
    # tested negative, so a future edit cannot quietly start emitting bytes
    # for a shape DR has never shown me.
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
    "N79_ON_HANDLER_GOTO": (
        "e11f:\n  procedure options(main);\n  dcl sysin file;\n"
        "  dcl a fixed bin(15);\n  on endfile(sysin) goto out;\n"
        "out:\n  get list(a);\n  stop;\nend e11f;\n",
        "needs DR's ?RECOV label prologue"),
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
for _n in ("U1", "W1", "W2", "W3"):
    REJECTS[_n] = (open("e15src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(),
                   "right operand is a procedure call")
for _n, _m in (("ST5", "exceeds 65535"), ("ST10", "non-integer-literal"),
               ("ST8", "after an appended procedure"),
               ("ST13", "after an appended procedure"),
               ("ST14", "after an appended procedure")):
    REJECTS[_n] = (open("e15src/%s.PLI" % _n, "rb")
                   .read().replace(b"\r\n", b"\n").rstrip(b"\x1a").decode(), _m)

NEG_META = {
    "U1": ("my-gap",
     "DR COMPILES IT and its .COM RUNS CORRECTLY: sum(100) = 5050 "
     "(golden/e2e169dr/U1.output.txt).  My build printed 12488 "
     "(golden/e2e169mr/U1.output.txt) -- a WRONG VALUE, silently.  Now refused by the "
     "C139 guard; the correct add-across-a-call lowering is unknown [TBD]"),
    "W1": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e170/W1/W1.REL) -- `return (n + f(n-1))' "
     "in a RECURSIVE procedure; same add-across-a-call defect as U1 [C139]"),
    "W2": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e170/W2/W2.REL) -- local assigned then "
     "read after a recursive call; the U1 shape at depth 8 [C139]"),
    "W3": ("my-gap",
     "DR COMPILES IT: .REL emitted (golden/e2e170/W3/W3.REL) -- same, but the local is "
     "set to a LITERAL, which rules out 'copying n is what went wrong' [C139]"),
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
    "N7_MULTI_FWD": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG60/NG60.REL)"),
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
    "N23_CHARVAR_MULTI": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG09/NG09.REL)"),
    "N24_BIGIN": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG10/NG10.PRN)"),
    "N25_DECCMP_SCALE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG11/NG11.REL)"),
    "N27_DECBIGP": ("dr-refuses",
     "DR REFUSES: NOT IMP (golden/negpanel1/NG12/NG12.PRN)"),
    "N28_DECLITFRAC": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG13/NG13.REL)"),
    "N29_DECININT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG14/NG14.REL)"),
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
    "N58_MUL_TWO": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG42/NG42.REL)"),
    "N59_MUL_ONE": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG43/NG43.REL)"),
    "N60_MUL_LITERAL_LEFT": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG44/NG44.REL)"),
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
    "N79_ON_HANDLER_GOTO": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG59/NG59.REL)"),
    "N80_ON_HANDLER_BEGIN": ("my-gap",
     "DR COMPILES IT: no errors in either pass, .REL emitted (golden/negpanel1/NG61/NG61.REL)"),
    "N81_CALL_OF_VALUE_RETURNING": ("dr-refuses",
     "DR REFUSES: NOT PROC (golden/negpanel1/NG62/NG62.PRN)"),
    "N82_CALL_OF_FLOAT_RETURNING": ("dr-refuses",
     "DR REFUSES: NOT PROC (golden/negpanel1/NG63/NG63.PRN)"),
    "N83_EXPR_OF_NO_RETURNS": ("dr-refuses",
     "DR REFUSES: TYPES NOT= (golden/negpanel1/NG64/NG64.PRN)"),
}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--link-run", action="store_true")
    ap.add_argument("--skip-selftest", action="store_true",
                    help="do not run the pre-flight selftests (reldump "
                         "field-visibility + linkrun C137 undefined-symbol) "
                         "first (debug only -- a real gate run must not use it)")
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
