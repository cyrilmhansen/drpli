#!/usr/bin/env python3
"""[E2E-42/P2c] Pre-registration helper: predicted CODE/DATA for the P2c bank.

The cost model is the one [E2E-42/P2b] calibrated -- see
../e2e42-p2b/predict_sizes.py's header -- extended with the SKIP and PAGE
statement costs MEASURED from DR's own objects, not invented:

  FILE PUT attach (CREATE:41 and COPYLPT's file PUTs, all six):
      01AA 2A xx xx  lxi h,*C
      01AD ED 52 06  lxi d,0652      <- the named-file stream control block
      01B0 01 xx xx  lxi b,*CODE     <- resume address = the NEXT statement
      01B3 CD xx xx  call ?SIOOP                                = 12 bytes
  PUT close, both routes:            call ?QIOOP                 =  3
  SKIP with a literal/absent count:  mvi a,n (2) + call ?SKPOP (3) =  5
      CREATE 01B6 MVI A,01 / 01B8 CALL ?SKPOP
      COPYLPT 02A1 MVI A,04 / 02A3 CALL ?SKPOP   -- same length, count 4
  SKIP with an EXPRESSION count:     lhld *D (3) + mov a,l (1)
                                     + call ?SKPOP (3)            =  7
      COPYLPT 0318 LHLD *D(0102) / 031B MOV A,L / 031C CALL ?SKPOP
  PAGE:                              call ?PAGOP                  =  3
      COPYLPT 0221 CALL ?PAGOP, between the attach and the close.

The bare FILE SKIP is therefore 12+5+3 = 20 bytes, which is exactly CREATE's
01AA-01BD and 01E0-01F3; SKIP + one literal is 12+5+11+3 = 31, which is
exactly CREATE's 01C1-01DF.  Those two are model CROSS-CHECKS against a
program the model was not fitted to.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", ".."))
C = dict(
    START=6, CLOSE_F=6, STOPX=3,
    OPEN_LIT=29,      # literal title: MVI A,n / CALL ?SLCTS
    FILE_PRO=12,      # LXI H,*C / LXI D,0652 / LXI B,*CODE / CALL ?SIOOP
    CONS_PRO=9,       # LXI H,*D / LXI D,*CODE / CALL ?SYSPR
    PUT_CLOSE=3,      # CALL ?QIOOP, on both routes
    # item chains, measured in P2b and re-verified there against 32 objects
    LIT=11, VAR=9, FIXC=11, BIN=11, DEC=18, EDIT=18,
    # control items, measured here
    SKIP_LIT=5, SKIP_EXPR=7, PAGE=3,
    # assignment statements
    A_V=13, A_B=6,
)

def prolog(title_len, varying_title=False):
    """START + the OPEN call.  The title's bytes live in DATA, not CODE:
    measured on E46M1, whose CODE is 115 with a 9-byte title, and on E46M19
    with a 10-byte title, whose CODE is 122 -- the same OPEN cost.  The
    title LENGTH appears only as the `MVI A,n' operand, one byte either way."""
    return C["START"] + (27 if varying_title else C["OPEN_LIT"])

def epilog(closed=True):
    """CLOSE is `LXI H,*C / CALL ?QIOOP' = 6.  The final `CALL ?STOPX' is 3.
    No extra PUT close belongs here -- each PUT statement carries its own."""
    return (C["CLOSE_F"] if closed else 0) + C["STOPX"]

def file_put(items, skip="none"):
    """items: list of byte counts; skip: none | lit | expr | page"""
    sk = {"none": 0, "lit": C["SKIP_LIT"], "expr": C["SKIP_EXPR"],
          "page": C["PAGE"]}[skip]
    return C["FILE_PRO"] + sk + sum(items) + C["PUT_CLOSE"]

def cons_put(items, skip="none"):
    sk = {"none": 0, "lit": C["SKIP_LIT"], "expr": C["SKIP_EXPR"],
          "page": C["PAGE"]}[skip]
    return C["CONS_PRO"] + sk + sum(items) + C["PUT_CLOSE"]

L, V, B, D, F = C["LIT"], C["VAR"], C["BIN"], C["DEC"], C["FIXC"]

# name -> (code_pred_or_None, data_pred_or_None, notes, exported_files)
# DATA = pool cells (literals, titles) in first-use order + automatic cells,
# the layout E46M19 and E46M27 pinned; a fixed BIN/DEC cell is 2 or p/2+1.
P = {
 "E46N1":  (prolog(9) + file_put([], "lit") + epilog(),
            9,
            "bare FILE SKIP alone: 12 attach + 5 skip + 3 close = 20",
            []),
 "E46N2":  (prolog(9) + file_put([L], "lit") + epilog(),
            9 + 1,
            "SKIP then ONE literal chain: 12+5+11+3 = 31 = CREATE 01C1-01DF",
            []),
 "E46N3":  (prolog(9) + file_put([V], "lit") + epilog(),
            9 + 21,
            "SKIP then a VARYING variable: 12+5+9+3 = 29",
            []),
 "E46N4":  (prolog(9) + file_put([L, L], "lit") + epilog(),
            9 + 2,
            "SKIP then TWO literals: 12+5+11+11+3 = 42; still ONE attach",
            []),
 "E46N5":  (prolog(9) + 2 * file_put([], "lit") + epilog(),
            9,
            "two successive bare SKIPs: 20 + 20, no coalescing",
            []),
 "E46N6":  (prolog(9) + file_put([L]) + file_put([], "lit") + epilog(),
            9 + 1,
            "output THEN skip: 26 + 20",
            []),
 "E46N7":  (prolog(9) + file_put([], "lit") + file_put([L]) + epilog(),
            9 + 1,
            "skip THEN output: 20 + 26; must be E46N6 with the two blocks "
            "swapped and nothing else different",
            []),
 "E46N8":  (prolog(9) + cons_put([], "lit") + file_put([], "lit") + epilog(),
            9,
            "routing contrast: console skip 9+5+3 = 17 (REVERSE:00FE) vs "
            "file skip 20 (CREATE:41), ONE object, ?SYSPR=1 and ?SIOOP=1",
            []),
 "E46N9":  (prolog(9) + file_put([], "lit") + epilog(),
            9,
            "counted skip(2): MVI A,02 is the same 2 bytes as MVI A,01, so "
            "the same 20 as the bare form (COPYLPT skip(4) = 20)",
            []),
 # [E2E-42/P2c RESULT] THE ONE MISS, AND IT WAS A TYPED NUMBER, NOT THE MODEL.
 # This entry pre-registered 62/9; DR returned 62/10 -- CODE HIT, DATA one byte short.  The cause is
 # that `title('N10OUT DAT')' is TEN characters and I typed 9 here, while every sibling entry types
 # the length of its OWN title (N1-N9 use 'N<n>OUT DAT', nine characters, because the number is one
 # digit; N10-N18 use ten).  The model rule itself is untouched and reproduces all six executed rows
 # exactly -- DATA = title_len + sum(len(literal)) -- which is why this is recorded as a transcription
 # error in a hand-typed argument rather than a defect in [C296]'s cost model.  The PRE-REGISTERED
 # VALUE IS NOT EDITED: spec/lab-evidence/e2e42-p2c/HYPOTHESES.md keeps 62/9 as the table DR was
 # invoked against, and RESULTS.md carries the hit/miss column.  What is fixed here is the generator
 # going forward, so re-running it cannot silently re-issue the same wrong number.
 "E46N10": (prolog(10) + file_put([], "page") + epilog(),
            10,
            "FILE page: 12+3+3 = 18 (COPYLPT 0215-0226); ?PAGOP=1",
            []),
 "E46N11": (prolog(10) + file_put([L]) + file_put([], "lit")
            + file_put([L]) + epilog(),
            10 + 2,
            "runtime, item/skip/item: 26+20+26",
            ["N11OUT"]),
 "E46N12": (prolog(10) + file_put([], "lit") + file_put([L]) + epilog(),
            10 + 1,
            "runtime, skip before any output: 20+26",
            ["N12OUT"]),
 "E46N13": (prolog(10) + file_put([L], "lit") + epilog(),
            10 + 3,
            "runtime, CREATE:44's own shape: 31",
            ["N13OUT"]),
 "E46N14": (prolog(10) + file_put([L]) + 3 * file_put([], "lit")
            + file_put([L]) + epilog(),
            10 + 2,
            "runtime, three successive SKIPs: 26+20+20+20+26",
            ["N14OUT"]),
 "E46N15": (prolog(10) + cons_put([L]) + file_put([L]) + file_put([], "lit")
            + file_put([L]) + cons_put([L]) + C["CLOSE_F"] + C["STOPX"],
            10 + 3 + 1 + 1 + 5,
            "runtime routing: 2 file PUTs with a SKIP between, and a "
            "?SYSPR PUT on each side of them",
            ["N15OUT"]),
 "E46N16": (prolog(10) + 2 * file_put([L]) + epilog(),
            10 + 2,
            "runtime CONTROL, the same two items with NO skip: 26+26.  "
            "E46N11's file minus E46N16's file IS the bytes of one SKIP.",
            ["N16OUT"]),
 "E46N17": (prolog(10) + file_put([V, V, V, V, D, V], "none")
            + file_put([], "lit") + file_put([L], "lit")
            + file_put([], "lit") + epilog(),
            10 + 3 + (30 + 1) + (30 + 1) + (20 + 1) + (10 + 1) + (6 // 2 + 1)
            + (12 + 1),
            "CREATE:39-45 spelled out: 78 + 20 + 31 + 20",
            []),
 "E46N18": (prolog(10) + C["A_B"] + file_put([], "expr") + epilog(),
            10 + 2,
            "expression skip count: 12 + (LHLD 3 + MOV A,L 1 + SKPOP 3) + 3 "
            "= 22 (COPYLPT 030C-0321)",
            []),
 # protocol pair: identical program, the ONLY difference is line endings
 "E46N19": (prolog(10) + C["A_V"] + file_put([V]) + epilog(),
            10 + 5 + 11,
            "PROTOCOL CONTROL, strict CRLF: expected to compile",
            []),
 "E46N20": (prolog(10) + C["A_V"] + file_put([V]) + epilog(),
            10 + 5 + 11,
            "PROTOCOL DISCRIMINATOR, the SAME program with bare LF on every "
            "line including the last.  [C303] predicts refusal.  The "
            "artifacts predict something narrower: E46M33 as ACCEPTED by DR "
            "has 8 bare-LF body lines and 1 CRLF (its last), and DR listed "
            "all 9 lines with correct numbers, so a bare-LF BODY is read "
            "fine; E46M36, the probe that died of UNEXPECTED EOF, is the one "
            "whose LAST line ends in LF before the ^Z.  The two hypotheses "
            "this probe separates are 'LF anywhere' and 'LF on the last "
            "line': refuse => the latter is not what differs (LF anywhere "
            "holds); compile => the last line's CR is what mattered and "
            "[C303]'s wording is wrong.",
            []),
}

P.update({# ---- the four controls P2c keeps refused: PAGE is E46N10 (predicted above
 # as an ACCEPT, because COPYLPT:53 measures DR emitting it); these three are
 # predicted REFUSALS by US, and their DR verdict is the question.
 "E46N21": (None, None,
            "FILE LINE.  Predicted: DR ACCEPTS (LINE is a PL/I PUT control and "
            "the compiler has a control-item switch to fall through to), and "
            "we refuse at `file_items' by class.  If DR refuses, that is a "
            "DR-side gap and our refusal needs no justification.",
            []),
 "E46N22": (None, None,
            "FILE AFTER.  Predicted: DR ACCEPTS and we die in the PARSER "
            "(AFTER is not a PUT option key), which is one STAGE earlier than "
            "the codegen refusals -- a parse negative, not a lowering "
            "negative, and recorded as such.",
            []),
 "E46N23": (None, None, "FILE BEFORE, the mirror of E46N22.", [])
})


def selftest():
    """The model must reproduce objects it was NOT fitted to."""
    checks = [
        ("CREATE:41 bare FILE SKIP", 0x01BD - 0x01AA + 1,
         C["FILE_PRO"] + C["SKIP_LIT"] + C["PUT_CLOSE"]),
        ("CREATE:44 FILE SKIP LIST", 0x01DF - 0x01C1 + 1,
         C["FILE_PRO"] + C["SKIP_LIT"] + C["LIT"] + C["PUT_CLOSE"]),
        ("COPYLPT:67 skip(4)", 0x02A8 - 0x0295 + 1,
         C["FILE_PRO"] + C["SKIP_LIT"] + C["PUT_CLOSE"]),
        ("COPYLPT:81 skip(spaces)", 0x0321 - 0x030C + 1,
         C["FILE_PRO"] + C["SKIP_EXPR"] + C["PUT_CLOSE"]),
        ("COPYLPT:53 page", 0x0226 - 0x0215 + 1,
         C["FILE_PRO"] + C["PAGE"] + C["PUT_CLOSE"]),
    ]
    bad = 0
    for what, got, want in checks:
        ok = got == want
        if not ok:
            bad += 1
        print("  %-30s measured %3d  model %3d  %s"
              % (what, got, want, "OK" if ok else "MISMATCH"))
    return bad


if __name__ == "__main__":
    print("model cross-check against DR objects it was not fitted to:")
    if selftest():
        print("REFUSED: the cost model does not reproduce measured spans")
        sys.exit(1)
    print()
    print("%-9s %6s %6s   %s" % ("probe", "CODE", "DATA", "basis"))
    for k in sorted(P, key=lambda s: int(re.sub(r"[A-Z]", "", s[4:]))):
        code, data, why, _ = P[k]
        cs = "?" if code is None else str(code)
        ds = "?" if data is None else str(data)
        print("%-9s %6s %6s   %s" % (k, cs, ds, why))
