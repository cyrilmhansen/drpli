import re
#!/usr/bin/env python3
"""E2E-42/P2b: predicted CODE totals from the cost model pinned by   [CODE ONLY -- see below]
golden/e42p2a/ (E46L1-L18) and golden/first/ (KEYFILE, CREATE).

THIS TOOL MODELS CODE AND NOTHING ELSE.  Its docstring used to say "CODE/DATA", which it does not
live up to: there is no DATA model here, and the predicted DATA column in HYPOTHESES.md was hand
arithmetic over declared capacities.  Nine of those twenty numbers were wrong (eight one byte low,
E46M5 five high) and the reasons are set out in RESULTS.md section 7 -- chiefly that a CHARACTER
VARYING cell is capacity+1 [C291] and that the DATA segment is pool-first-then-auto, both of which
my arithmetic ignored.  Do not read a DATA number in this directory as machine-derived; the CODE
numbers are, and all 20 of them were exact.

Costs (all verified against a DR .REL in this repo, see HYPOTESES.md FP2/FP3):
  program start          6   LXI B,0200 / CALL ?START          (E46L1 0000-0005)
  OPEN literal title    29                                    (E46L1 0006-0022)
  OPEN varying title    27                                    (E46L6 0006-0020)
  CLOSE                  6   LXI H,*C / CALL ?CIOOP           (E46L1 0050-0055)
  stop/end               3   CALL ?STOPX                      (E46L1 0056-0058)
  FILE PUT prologue     12   LXI H,*C / LXI D,0652 / LXI B,*CODE / CALL ?SIOOP
  CONSOLE PUT prologue   9   LXI D,0252 / LXI B,*CODE / CALL ?SYSPR
  PUT close              3   CALL ?QIOOP
  item, CHARACTER lit   11   LXI H,*D / MVI A,n / ?SLCTS / ?PNCOP
  item, varying var      9   LXI H,*D / ?SLVTS / ?PNCOP
  item, fixed char var  11   LXI H,*D / MVI A,n / ?SLCTS / ?PNCOP
  item, fixed bin var   11   LHLD *D / MVI A,w / ?QICOP / ?PNVOP
  item, fixed dec var   18   LXI H,*D / MVI A,p / ?DLDOP / MVI A,p+3 / MVI B,s / ?QDCOP / ?PNVOP
  item, DEC literal     18
  v = 'lit' (varying)   13   ?SMCVM                           (E46L12 0006-0012)
  c = 'lit' (fixed)     13   ?SMCCM                           (E46L13 0006-0012)
  k = 42  (bin)          6   LXI H,imm / SHLD *D              (E46L14 0006-000B)
  z = 123 (dec)         16   LXI H,*D / ?DLDOP / LXI H,*D / ?DSTOP (E46L15 0006-0015)
  rec.m = 'lit'         13   ?SMCVM                           (E46J21)
"""
START, OPEN_LIT, OPEN_VAR, CLOSE_F, STOP = 6, 29, 27, 6, 3
FP, CP, PC = 12, 9, 3
LIT, VAR, FIXC, BIN, DEC = 11, 9, 11, 11, 18
A_V, A_C, A_B, A_D, A_M = 13, 13, 6, 16, 13

def prog(*stmts, open="lit"):
    head = OPEN_LIT if open == "lit" else (OPEN_VAR if open == "var" else 0)
    return START + head + sum(stmts) + STOP

def fput(items):  return FP + sum(items) + PC
def cput(items):  return CP + sum(items) + PC

# explicit per-probe arithmetic, with the CLOSE byte counted where the file is closed
def full(open_kind, stmts, close=True):
    return prog(*stmts, open=open_kind) + (CLOSE_F if close else 0)

P = {
 "E46M1": full("lit", [fput([LIT,LIT]), cput([LIT,LIT])]),
 "E46M2": full("lit", [fput([LIT]), fput([LIT])]),
 "E46M3": full("lit", [fput([LIT,LIT,LIT]), cput([LIT,LIT,LIT])]),
 "E46M4": full("lit", [fput([LIT,LIT,LIT,LIT])]),
 "E46M5": full("lit", [fput([LIT,DEC]), fput([DEC,LIT])]),
 "E46M6": full("lit", [fput([LIT,LIT,LIT])]),
 "E46M7": full("lit", [fput([VAR,VAR]), cput([VAR,VAR])]),
 "E46M8": full("lit", [fput([FIXC,FIXC]), cput([FIXC,FIXC])]),
 "E46M9": full("lit", [fput([VAR,FIXC]), fput([FIXC,VAR]), cput([VAR,FIXC]), cput([FIXC,VAR])]),
 "E46M10": full("lit", [fput([VAR,BIN]), fput([BIN,VAR]), cput([VAR,BIN]), cput([BIN,VAR])]),
 "E46M11": full("lit", [fput([VAR,DEC]), fput([DEC,VAR])]),
 "E46M12": prog(*[cput([VAR,DEC]), cput([DEC,VAR])], open=None),
 "E46M13": full("lit", [fput([BIN,DEC]), fput([DEC,BIN]), cput([BIN,DEC]), cput([DEC,BIN])]),
 "E46M14": full("lit", [fput([VAR,VAR]), fput([VAR,BIN,VAR])]),
 "E46M15": full("lit", [fput([VAR,FIXC,BIN,DEC,VAR])]),
 "E46M16": full("lit", [fput([VAR,FIXC]), fput([FIXC,VAR]), cput([VAR,FIXC])]),
 "E46M17": full("lit", [fput([FIXC]), fput([FIXC,VAR])]),
 "E46M18": full("lit", [fput([VAR,LIT,VAR]), fput([VAR,FIXC])]),
 "E46M19": full("lit", [fput([VAR,VAR,VAR,VAR,DEC,VAR])]),
 "E46M20": full("lit", [fput([VAR,VAR,VAR,VAR,DEC,VAR])]),
 "E46M21": full("lit", [fput([VAR,11])]),
 "E46M22": full("lit", [fput([VAR,FIXC])]),
 "E46M23": full("lit", [fput([VAR,12])]),
 "E46M24": full("lit", [fput([VAR,11])]),
 "E46M25": full("lit", [fput([VAR,11])]),
 "E46M26": full("lit", [fput([VAR,11])], close=False),
 "E46M27": full("lit", [A_V, A_V, fput([VAR,VAR]), fput([VAR]), fput([VAR]), fput([VAR,VAR]), cput([LIT])]),
 "E46M28": full("lit", [fput([LIT,LIT,LIT]), cput([LIT])]),
 "E46M29": full("lit", [A_V, A_B, A_D, fput([VAR,BIN,DEC]), fput([LIT,VAR]), cput([LIT])]),
 "E46M30": full("lit", [A_C, A_C, fput([FIXC,FIXC]), cput([LIT])]),
 "E46M31": full("lit", [A_M*5, A_D, fput([VAR,VAR,VAR,VAR,DEC,VAR]), cput([LIT])]),
 "E46M32": full("lit", [A_V, A_V, cput([LIT]), fput([VAR,VAR]), cput([LIT])]),
 # [E2E-42/P2b] added AFTER the 32-probe run, to pre-register the two spellings that still reach
 # the option-level refusal: a duplicated FILE option and an empty LIST.  Predictions below were
 # committed before their oracle call.
 "E46M33": full("lit", [A_V, fput([LIT])]),          # 6+29+13+26+6+3  (one attach)
 "E46M34": full("lit", [A_V, 12 + 0 + 3]),           # 6+29+13+15+6+3  (attach, no chain, close)
}
for k in sorted(P, key=lambda s: int(re.sub(r"[A-Z]","",s[4:]))):
    print(f"{k:9s} predicted CODE = {P[k]}")
