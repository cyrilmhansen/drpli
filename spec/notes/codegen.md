# PL/I-80 code generation — `$C` phase notes (v1)

Oracle: compile with `$C` → interleaved `; LINE nnnn` + disassembly
(`addr  MNEM  operands`), tail `CODE SIZE / DATA AREA / FREE SYMS`.
Parser: `tools/ctrace.py` (summary / --full / CALL histogram).
Goldens: golden/probe47..53 (20 micro-probes P071x/P072x/P073D/P060A
+ P080A–T, P081 I/K2/M/Q, P082I, P084K).

## 1. Program frame
* Prologue (every program): `LXI B,0200 ; CALL ?START` — B = initial
  stack/base page hint, ?START builds the runtime context.
* Epilogue: `CALL ?STOPX` after the last source line.
* Nested procedures/handlers are subroutines: ON-handler code is inline
  terminated by `RET` [P073D] — handlers are REAL subroutines called
  through the context chain.

## 2. Pseudo-register model
Code uses NAMED register slots stored in memory (`LHLD/SHLD X A(off)`):
`A, B, Z` (16-bit working) + `P` (pointer scratch) [P084K] + the real
`HL/DE/BC` pairs + RTL *stack* operand class `ST` (see
spec/notes/plilib-entrypoints.txt ABI rows: `fa44s ST ST ST` etc).
Typical inline pattern for bin(15) arithmetic [P071A `z=a+b-1`]:
```
LHLD A A(0000)   ; reg-slot A = a
XCHG             ; (HL→DE)
LHLD B A(0002)   ; slot B = b        (note: B slot ≠ DE reg)
DAD  D           ; HL = A+B result
DCX  H           ; -1 constant folded as DCX H!
SHLD Z A(0004)   ; store to z
```
⇒ the $V stack machine lowers to 16-bit inline ops when operand size
fits; constants ≤ 0xFF use `LXI H,imm`, bigger ones the data pool
(`LXI H,* S(k)` + `CALL ?DLDOP`) [P071A L3 vs P080B].

## 3. Inline vs helper decision (observed so far)
| construct | codegen |
|---|---|
| int ≤15-bit +,-,const-1..±small | inline `DAD D` / `DCX H` / `INX H` |
| int * / / (var × var) | `CALL ?IM22N/?ID22N/?IS22N` (DE,HL→HL) [P080A] |
| bit ≤8 | pure byte ops `LDA/ANA/STA/MVI M` [P080G, P082I] |
| decimal +,-,*,/ | `?DADOP ?DMUOP ?DDVOP` + loads `?DLDOP/?DSTOP` + rescale `?QDDSR/?QDDSL` [P080B/P071D] |
| decimal compare | `?DCMOP` [P080H] |
| float +,-,*,/,cmp | `?FA44M ?FS44? ?FM44M ?FD44M ?FC44M` families (suffix = operand addressing s/m/l/r) |
| exponentiation | `?IEXOP` (int const exp) / `?DEXOP` |
| conversions | `?Q*`: QDI15, QI15D/F, QFI15, QDCOP/QCDOP/QICOP, QFCMS, QF4X8/QX8F4, FX44S... |
| char copy/concat/substr | `?CS3AD ?SCCCM ?SJSCM ?SMCCM` + loads `?SLCTS/?SLVTS`, stores `?SSCFS/?SSVFS` |
| based access | `LHLD P A(p)` then DIRECT `MVI M,imm`/`MOV E,M;INX H` [P084K] |
| allocate/free | `LXI H,size ; CALL ?ALLOP ; SHLD P` / `LHLD P ; CALL ?FREOP` |
| goto/labels | plain `JMP addr` [P072C] |
| if | compare sets flags then conditional branch (exact form per type below) |
| ON/SIGNAL/REVERT | `CALL ?ONCOP/?SIGOP/?REVOP` with `ILD`-slot args |
| put list | `?SLCTS`→? or `CALL ?SYSPR` + `?PNCOP/?PNVOP` + `?QIOOP` [P080N] |
| get list | `?SYSIN ?GNVOP ?SLCTS` [P080O] |
| picture edit | `?EDITF ?EDTOV` (+ descriptor pool `* S(k)` refs) [P080P] |
| file open/close | `?OIOOP ?SIOOP ?CIOOP` + QCI/QCO [P081Q] |
| ext entry call args | staged via `MVI A,n; CALL ?xxx`?? see P081M (AST desc) — details next batch |

## 4. RTL routine inventory
* 57 distinct `?NAME` call targets across the 20-specimen corpus —
  **100% resolve against the PLILIB.IRL index** (384 entries;
  `spec/notes/plilib-routines.txt`; IRL format: header 128B + index
  entries `?NAME \xFE e r b` + REL section [LINK-80 guide §1.7]).
* Naming grammar: `{family}{width}{src}{dst}` — width '22' = 16-bit
  int, '44' = 4-byte float; suffix s=stack, m=memory(DE/HL),
  l/r = operand-side variants. ABI table (params→result registers,
  156 rows) extracted from LINK-80/Librarian guide §5.2 into
  `spec/notes/plilib-entrypoints.txt`.
* Guide also documents (READ PROJECT, later): §4.3 param passing,
  §4.4 per-type function return conventions, §5.1 stack subroutines
  (ALLWDS/STKSIZ/NOTWD), App A–D PLIDIO/DIO* CP/M interface listings.

## 5. Data area
`DATA AREA = nnnn` per program = static bytes incl. pool; pool
constants referenced as `* S(k)` matching the $S dump statics.

## 6. Open $C questions (next batteries)
1. branch encodings for IFC/CCT (JC vs CMP form), DO WHILE/TO loop
   skeletons (back-edge placement, BY increment), 2. function-call
   sequence (result via Z? RETURN convention), 3. array element
   addressing (OFF/SB → IMUL? ?IX???), 4. FORMAT descriptor operand
   passing to ?EDITF, 5. struct copy (?SMV??), 6. external-entry
   linkage form (JMP vector? LDOS?), 7. recursion/reentrancy handling
   of A/B/Z slots across nested calls, 8. exact ?START context layout
   (with PLILIB disassembly via App listings).
