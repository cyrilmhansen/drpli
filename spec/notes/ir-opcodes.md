# PL/I-80 v1.4 $V intermediate-code opcode dictionary (seed)

Source: probes P068E*, P071A-N ($V$L transcripts golden/probe28-29, 38-39),
EXPR1-VL, P062A/P045 sets. Format per record line:
`  ## OPCODE <f1> <T> <k?> <a1> <a2> <a3> <a4> [<name/addr>]`
where `##` = seq, T = type tag (N/B/X/…), and trailing operand fields vary
by op. Records are grouped under their source statement; LIO #00XX is a
STATEMENT MARKER emitted at the start of each statement (# = statement
index, not a literal value) [decoded from P071M].

## Observed opcode census (probe38/39 + earlier)
| op | role (decoded/hypothesis) | status |
|---|---|---|
| BEG | block/procedure prologue (args carry frame size?, e.g. `0 N 0 45 00 31 00`) | ok |
| STP | procedure end / STOP marker (`0 N 0 45…`) | ok |
| LIO | per-statement marker; #index | ok |
| NID | name-identity push: variable/symbol slot ref `NAME A(offset)` | ok |
| IID/DID/FID/CID/BID | typed operand push (I bin, D dec, F float, C char, B bit) `NAME A(offset)` | ok |
| ENT | entry-reference push `#E7xx` (RTL/entry table address; prologue `CALL ?START` #E763 era) | ok |
| ILD / DLD / FLD / CLD / ALD | typed literal-load: ILD imm-width; DLD from literal pool `* S(idx)`; **ALD #E7xx = based-access RTL helper call** (q based(p)) | partial |
| IAD ISU IMU IDV IMD | binary(16-bit) + - * / mod → confirmed on P071A/B | ok |
| DAD DSU DMU DDV? | decimal + - * ; DDV not yet observed (dec divide) [batch2] | ok |
| DEX | exponentiation `2**3` (`2 N 0 05 00 00 00` = result width?) | ok |
| FMU FAD F? | float ops (`2 B 0 24` = 24-bit) ; FDV/FSU [batch2] | ok |
| CCT | character concatenation (pair with CLD/CAS) | ok |
| CAS | character store (s = … ) `2 X 0 10 00 28 00` (len…) | ok |
| BAN BOR BNG | bit AND OR NOT (bit ops; BLD = bit load) | ok |
| ILT IGT IEQ… | relational compares (bin width arg); ^=/NE uses same family? [batch2] | partial |
| IFC | IF-conditional branch (`1 N 0 01` bit cond) | ok |
| WHL / DOW | DO-WHILE head/tail pair around condition chain | ok |
| OFF / SB | array subscripting: OFF opens reference, IMU ×element-size, SB = effective addr | ok |
| IAS/DAS/FAS/CAS/BAS/NAS | typed STORE (assignment). NAS = pointer/name-target store (addr(z)); BAS = bit store; flags `2 X 0 15 00 08 00` carry width/(array?) bits | ok |
| Q?? conversions | QDI dec→int, QID?? , QIF int→float (x=z), QFD?, QFC?, QDD dec→dec rescale (`d = z` QFD; `d = x` QFC?? naming to map), QDC, QIO | mapping batch2 |
| FUN | function call evaluate `2 N 0 15` (result type) | ok |
| WHL/DOW/WHL… | loops | |
| SKP PNC PNV EDF SIO NLD | IO/print: SKP skip, PNC print char?, PNV print numeric-varying?, EDF edit-format, SIO stream-IO?, NLD newline? | partial |
| CTL xxxx | block-control records between lines (`CTL 0251` etc.) = frame/nesting control records, not ops | ok |

## Decoded evaluation-order model (from P068E5/E6 + this census)
Stack machine: operands pushed (IID/DID+DLD…), ops consume N per arity
field (`1`/`2` first arg = arity), conversions inserted per assignment
target type (QDI before IAS for dec→bin), stores last.
`z = 2+3*4`: DID*S(3)=3? push order RIGHT-to-LEFT of literals then
DMU, DAD — multiplication emitted first = post-order traversal = our
AST grouping ✓ (alignment tool: tools/vtrace.py + pli80tree).

## Field-format questions (deferred to $C/codegen phase)
- arg2 letter N/B/X meaning (numeric/binary/??expression class)
- DLD scale/width field layout; `00+02` composite forms (NAS/EDF args)
- CTL record codes (0247/0251/0252/0255…) = block boundary metadata

## Batch2 census (P072A-H, probe40)
| op | meaning | evidence |
|---|---|---|
| IEQ INE IGT IGE ILE ILT | full relational family, compare-then-branch; `^=` uses INE ✓ | P072A |
| QBI | convert bit→? (appears beside compare results) | P072A |
| **`<>` ⇒ PASS-2 SYNTAX** while `^=`/`~=` accepted (bin operands, p1 clean, ops emitted then rejected) | DR bug [PROBE 70: scope — dec/char/bit operand classes; RELNOTES-era] | P072A L4 |
| DDV FDV FSU | decimal divide, float divide/sub complete the arithmetic matrix | P072D/E |
| GTL + DFL | GOTO label reference + deferred-label ops | P072C |
| WHL/DOW + ILE | **DO TO loops**: init-store, WHL, body, ILE bound test, DOW — BY-increment folded into DOW/flags (verify via $C) | P072B |
| VID VLD VAS | **V = VARYING type letter** operand push/load/store | P072G/H |
| ENL GNV | GET LIST machinery (enter-list / get-numeric-varying) | P072G |
| OIO ENV CIO | OPEN (with opt-arg count '6 N 0 15 00 08'?), ENVersion?, CLOSE | P072H |
| QIO QDD | io-conversion; dec→dec rescale (`1 N 0 09 08` w/s) | P072D/G/H |
| LIKE attribute | `2 b like a` ⇒ compiler REJECT (diag, probe40) — [C] cut re-confirmed at IR level | P072F |

## Batch3 census (P073A-H, probe41)
| op | meaning | evidence |
|---|---|---|
| BLT CEQ DGT FEQ | comparisons are TYPE-SPECIALIZED: {I,B,C,D,F}×{EQ,NE,GT,GE,LT,LE} (ILT/IEQ.. from batch2) | P073C |
| CAS flag-bit | substr(s,i,n)=e pseudo-assign = CAS with flag 01 (offset+length pushed as ILD) — substr is INLINED, no FUN | P073B |
| QIC-inline | length(s) folds to constant store — builtin inlining | P073B |
| ONC ENC BLK SIG REV | ON unit install (cond slot #N), handler ENC + BLK block frame, SIGNAL, REVERT | P073D |
| AST | ARGUMENT STORE: external-entry call stages args into descriptor+2 slots before FUN [P073H: `* A(0002)`] | P073H |
| NID lab S(idx) | FORMAT symbol = string-pool record; named formats load by label | P073A |
| QDC PNV QIO | edit pipeline: SIO→EDF→(type-push,Qconv)→PNV→QIO | P073E/F |
| picture descriptors | same ops whatever picture length; only pool index/size differ (see binder notes) | P073E |

## Open IR questions (for $C phase)
- flags column (hi/lo: 28/01/32/54/74) = addressing/type modifiers — decode via $C
- DO-TO BY-increment folding into DOW flag bytes; ON condition-slot numbering
relational matrix (= <> > >= < <= + ^= ~=), DO TO loop ops, GOTO, ON
unit + SIGNAL + REVERT, group COPY (a=b struct), GET LIST, PUT FILE,
R(label) remote format, decimal DIVIDE, float DIVIDE/SUB, substr
pseudo-assign, bit-string compare, length()/index() builtins.
