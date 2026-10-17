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

## 7. Sequences decoded from probe54/55/60 batteries [C058]
### Branches (compare → conditional forward JMP)
* body emitted after a SKIP-jump; forward targets print as `0000`
  (LAD fixups applied by LINK at load — backward jumps are absolute!)
* int eq: `?IS22N` (sub) + `JNZ skip`; rel: sign test `MOV A,H; ORA A/L;
  JP|JM skip` (≤3 via `DCX/INX H` repeats, else `LXI B,-k; DAD B`).
* `<>`: NOT form — JZ skip. bit const compare: `LDA + ANI mask + SUI val + JNZ`
* char: `?SCCCM` (A=src len, B=dst len, HL/DE addrs) → JNZ
* `&` on conditions = EAGER: both sides computed, sign bytes combined
  `MOV A / POP B / ANA B`, JP skip. NO short-circuit codegen.
* DO WHILE: top-test, JMP back to test. DO TO/BY: init; test adds
  `-(LIMIT+1)` exit JP; increment = BY×`INX H` loop at body end, JMP back.
* GOTO = plain forward/backward JMP [P072C/P086H].
### Calls & returns
* ALL params are ADDRESSES (by reference, procs AND funcs): caller
  `LXI H,* A(k)` (static arg-block) + `CALL name`; block content =
  variable frame addresses or compile-time-initialized constant cells —
  caller emits NO staging code for constant args (data-area prefilled).
* callee entry copies the arg-pointer block into its param slots
  (byte loop `LXI D,A(...); MVI C,n; MOV A,M/STAX D` for many args;
  inline MOV E,M/SHLD for one). Body derefs through the address cell.
* RETURN value: fixed/bit/pointer → HL; float → RTL stack (`LXI H,dst;
  CALL ?FX44S`); char → stack (`?SSCFS B=len`). Matches guide §4.4.
* external entry: identical shape, symbol resolved by LINK (P086D/M, P091E).
* nested proc bodies are placed right after the ?START prologue, entry
  preceded by `JMP <main>` forward-fixup [P080L/P086C].
### Arrays [P086B/P080J]
* address = base_desc + INDEX×ELEMSIZE (1-based: constant d(2) folds to
  base+size*(n-1)); elem size 2 → `DAD H`; ≥3 → `LXI D,size; CALL ?IM22N`.
* loads/stores use the type push/store ops (MVI imm pair for int2,
  ?DLDOP/?DSTOP A=digits for dec, ?SMCCM A=len for char).
### Strings [P086G]
* concat = stack chain: ?SLCTS (load char to stack) / ?SJSCM / ?SJSTS
  (juxtapose stack+mem / stack+stack), result store ?SSCFS B=dstlen
  (truncation automatic); substr = ?CS3AD (E=pos-1?, C=len, A=srclen)
  then SMCCM; PUSH PSW carries length between loads.
### Edit / I/O [P086J/K, P080N/O/P]
* put list: `?SYSPR (LXI D,0252; LXI B,0000)` per stmt, then per item:
  load → type conv with operand codes (int ?QICOP A=09; dec ?QDCOP
  A=width B=scale; float ?QFCMS; char ?SLCTS) → ?PNVOP/?PNCOP; `?QIOOP` flush.
* put edit: `?EDITF (LXI H,*S(desc))` installed once, items → ?QDCOP →
  ?EDTOV, terminate ?QIOOP; FORMAT descriptors ARE the *S(k) pool
  records — links $S `* FORMAT STATIC` to $C operands ✓✓.
* file streams: `LXI H,<file sym>; LXI D,0652|0690; LXI B,0; CALL ?SIOOP`
  (0652=edit-out?, 0690=get/in, 0252=sysout, 0290=sysin — context-page
  control blocks at 0x0600 base); OPEN/CLOSE = ?OIOOP/?CIOOP with
  option words pushed on the real stack [P080Q].
* get list: ?SYSIN + ?GNVOP (+ JP end) + ?SSVFS B=varmax.
### Odds & ends
* null() → LXI H,0000 (zero pointer).
* pointer assign = LHLD P/SHLD plain word copy [P086M].
* allocate: size immediate `LXI H,n; CALL ?ALLOP` → SHLD pointer-slot.
* optimizer constant-reuse: after `x=1; SHLD X`, next `y=2` emits
  `INX H; SHLD Y` (HL kept live!) — byte-identity requires replicating.

## 8. Battery-3 additions (probe61-64) [C058]
### Integer ±k peephole grid (P087B/P088B/P089B, all z=a+k)
| k | code |
|---|---|
| 1..4 | `INX H` ×k |
| −1..−4 | `DCX H` ×|k| |
| first k≥5 or |k|≥5 | `LXI B,k` (16-bit) + `DAD B` |
| later 8≤k≤255 while B=00 | `MVI C,k; DAD B` (BC scratch reuse!) |
| k = prev+1..small delta | `INX B ×delta; DAD B` (12 after 10!) |
⇒ BC doubles as a chained constant accumulator; exact predicate still
open [byte-identity phase: build full k-sequence grid].
### Arrays (element multiply)
size 1 → plain add; size 2 → `DAD H`; size 4 → `DAD H` ×2 (float/char4);
size 3/5 → `LXI D,size; CALL ?IM22N`; const index folds to base offset
(1-BASED: addr = desc + (n−1)·size, desc prebiased −size).
### Strings/structs
group copy `h = g` → `LXI H,h; LXI D,g; LXI B,len; CALL ?NSTOP`;
member store = base+const offset + MVI M pair.
### Bit ops
bit(16) & → per-byte `ANA D/E`; ^b → `CMA` ×2 — pure inline;
bit↔char/dec conv: ?QB08C (A=code, B=len) + ?QX8F4/?QF4X8.
### Decimal divide rescale [P087H]
`e = d1/d2` (p,s targets): DLDOP(d1) → ?QDDSL A=shift-left (computed by
compiler: scale + divisor digits…) → DLDOP(d2) → ?DDVOP → ?QDDSR
A=shift-right → DSTOP(target digits). Rescale amounts are compile-time.
### Float literals/pool
4-byte pool records (`*S(k)`, stride 4); load = FX44M (pool→var),
arith = FA44M/FM44M (PUSH/POP stack form), store = FX44S. e-notation
and plain both pool-borne (0.25e-2 = S(0004) ✓).
### Recursion / re-entrancy [P087D]
arg block = FRAME slot (`SHLD * A(0006)` before self-CALL) — recursion
safe; `call rec;` no-arg still CALLs with dangling block ref?
### Compare-to-zero special form
`m > 0` with DEREFERENCED operand: `XRA A; CMP M; INX H; SBB M` (16-bit
CMP/SBB) instead of ?IS22N — operand-class-dependent.
### Nested loops [P087J]
inner DO-WHILE top-test + JMP back inside outer body; outer TO test
JP exit lands past outer end via forward-fixup chain; forward refs
always 0000 + LAD records (LINK-resolved) — $C shows placeholders.

## 9. DATA segment layout (reldump of probe goldens) [C063]
Data-seg comes FIRST in the stream (SET-LC data). Contents:
* Uninitialized AUTOMATIC/STATIC variables occupy NO data bytes
  (P080B: data area = reloc slots only); DATA AREA in $C counts the
  auto/static frame, not stream bytes.
* FORMAT descriptors ARE data bytes (this is the *S(k) pool):
  - F/E item 6B: `80 00 00 dd ss 81` — dd=digits, ss=scale (FF if none)
    [f(9,2)=80 00 00 09 02 81; f(4)=80 00 00 04 ff 81]
  - PICTURE item len+7: `80 00 02 cc 00 ll <chars×ll> 81`  [EX
    p'+++.++' → 80 00 02 04 00 06 2b2b2b2e2b2b 81 (13B); p'999' →
    ...03 393939 81 (10B)] — the len+7 formula = 6B header + chars +
    81 terminator; byte[3] = count of digit-class chars?? (04 vs 03)
    [grid TBD], byte[4] = V/implied-decimal related [TBD].
  - A item: `03 ww 81`?? (a(4) = '03 04 81' region, P086J) [TBD grid]
* Pool literals: decimal constants as BCD??/reloc-chained; float =
  4 raw LE bytes (FX44M loads direct); char strings raw + count.
* Inline `data` RELOCs appear INSIDE descriptors/control blocks where
  the descriptor references a variable (e.g. ?DLDOP operand chains).
TODO(byte-identity): full descriptor grid across picture classes
($ , + - 9 V . ,), f(w,s)/e(w,s)/a(w)/b(n)/x(n)/skip(n)/page/line(n)/
r(label), count prefixes — ~6 micro-specimens via $C+reldump, then the
REL writer can emit data bytes exactly.

## Addendum 2026-10-17 — fail-loud restored (found while mapping DEMO)
* `emit_program` had `| _ -> ()` for statements and `rows_of` had
  `| _ -> None` for variables: out-of-subset constructs were SILENTLY
  DROPPED. DEMO.PLI "compiled" to a 128-byte REL with code=9 (empty
  program!) instead of raising. Both defaults now failwith
  `codegen: ... [TBD]` (C067 policy). All e2e specimens regression-green.
* `pli80c.exe` did not strip CP/M ^Z padding (pli80parse did) — now
  same convention (cut at first 0x1A).
* KNOWN-COSMETIC: the new statement-kind error reports a stale line
  number ("line 2" for a line-4 PUT/GET): Sput/Sget `spos` appears to
  take the enclosing construct's position; fix alongside the I/O
  lowering slice.


## PUT LIST slice (E2E-3a, G107/G108 $C-verified)
Sequence + backpatch as CLAIMS C071. Pool: char literals enter the
SAME constant pool as decimal literals (raw ASCII bytes, no sign
nibble), allocated in emission order; auto vars remain above pool_total.
OPEN (deliberate, [TBD]): multiple pending backpatch triples ORDER is
unproven (single-put specimens only; List.rev = source order as
independent guess pending a 2-put probe); PUT to explicit FILE, PAGE,
multi-item LIST, expressions (concat/varying vars) all refused.
Tree-dumper + pli80c ^Z + discard-invariant fixes this slice (see
e2e-milestone addendum). Statement-position quirk: multi-line
`label:/ procedure` headers report the header LINE, not the stmt line
(G10x match DR numbering; t2-style files do not) -> fix before
listing-parity phases; DEMO uses the multi-line form.


## E2E-3b: comparisons, IF/ELSE, GOTO, HL-reuse (G113-G116 [C072])
* skip/exit fixups are the SAME deferred triple as the put continuation
  (C062), emitted INLINE at the point the target LC is reached;
  G113 corrected the C071 wording: LXI-B gets the NEXT-statement
  continuation, not an epilogue (single-put programs were ambiguous).
* relational (var OP var): Lt/Ge evaluate LEFT-RIGHT (XCHG form),
  Gt/Le evaluate RIGHT-LEFT, CALL ?IS22N then sign test JP/JM only
  (MOV A,H; ORA A for zero-adjacent forms; NO L-byte test);
  equality (Eq/Ne): PUSH H/POP D form + MOV A,H; ORA L (0xB5) + JNZ /
  0xCA(!). $C prints JZ for the Ne case while the REL byte is 0xCA
  ($C mnemonic-table vs emitted-byte mismatch; runtime semantics left
  OPEN — G114C counterexample executed 'N' on DR's own linked .COM).
* var = 0: direct memory test (LXI H + inline DATA reloc, MOV A,M,
  INX H, ORA M, JNZ). var > k>=1: LHLD; LXI B, -(k+1); DAD B; sign JM.
  All other const-position/operator combos remain [TBD] (N8/N9).
* label resolution: forward goto -> CHAIN-ADDR(type 12, value=operand
  slot) at the label's LC; backward goto -> inline RELOC(code,target).
* HL constant-reuse ladder (across SHLD!): k=0 & prev H-byte=0 -> MOV
  L,H; delta 1..4 down -> DCX repeats; delta 1..4 up -> INX repeats;
  else fresh LXI H. Any HL-clobbering stmt (PUT/IF/GOTO) resets the
  tracker.


## E2E-3c: CHAR VARYING + fixed char (V101-V108 [C073])
Representation: [len@0][data@1..n]; base = pool + declared offset.
Stores: varying ?SMCVM(A=cap,B=len; MOV B,A iff len==cap; len=0 -> bare
MVI M,00; len>cap passed through, RTL truncates); fixed ?SMCCM (pads).
Prints: varying ?SLVTS (H=base); fixed ?SLCTS with MVI A,cap; literals
unchanged MVI A,len. Pool: one BLOCK per string literal incl. zero-size
('' registers block -> SET-LC(data,0) emitted with no bytes); blocks
emitted SET-LC per block (addr>0). Numeric-var PUT and unproven fixed
store shapes remain [TBD].


## E2E-3d: || in PUT LIST (W101/W102 [C074])
Right-to-left emission over left-to-right pool allocation. C2: SLVTS
then SJSCM(lit,B). C3 (DEMO): SLCTS(righthand,A); LXI H,var; PUSH PSW;
SLVTS; SJSCM(lefthand,B); SJSTS; then common PNCOP/QIOOP/triple tail.
Only [lit;varying] and [lit;varying;lit]; all else [TBD].
NOTE OCAML PITFALL: a dedented `; tail` after a match's last branch
stays INSIDE that branch — paren-wrap match when a shared tail follows.


## E2E-3e: GET LIST + DEMO acceptance [X201/X202, C075/C076]
GET chain: LXI D,0290; LXI B,0000; SYSIN; GNVOP; JP(F2)->QIOOP-start
(triple after SSVFS chain); LXI H,var; MVI B,cap; SSVFS; QIOOP; cont.
DEMO.PLI -> golden 1980 DEMO.REL byte-identical; .COM + console equal
vs fresh DR AND banked run2. Gate 30/30 + NEG 18/18.


## E2E-4: DO i = a TO b [Y301-Y306 [C077]]
Static: LHLD;LXI B,-(b+1);DAD;MOV A,H;ORA;JP(F2)->exit. Dynamic: temp
store after init; head LHLD temp;XCHG;LHLD i;IS22N;JM(FA)->exit.
Temp slot = pool+auto+2k. INX-H init reuse when last_imm=from-1.
DO..END body arrives as Sdobegin (now lowered inline). ^=const kk ->
(DCX H)*kk ladder, CA skip. PITFALL: reldump masks SET-LC addr —
always raw-cmp, never trust a truncated grep of dumps.


## E2E-5a: DO WHILE / REPEAT / bare-DO block [Z401-Z407 [C078]]
WHILE: head=test insn; ladder from lower_test_skip (Econd unwrap);
exit triple after tail JMP. Lt-vs-const: DCX*k; MOV A,H; ORA A; JP.
'1'b cond = forever (no test). REPEAT(ind+1): tail-increment, no test.
BARE DO; = BLOCK (no back edge!). x=x+1 -> LHLD/INX/SHLD.
Const-store reuse: |d|<=2 ladders; same-H |d|>=3 -> MVI L; else LXI.


## E2E-5b: numeric/mixed console output [N301-N308 [C079]]
Item chain: PIlit=SLCTS+PNCOP; numeric=HL,+width,QICOP,PNVOP; ONE
QIOOP tail. width=min(9,digits(2^p-1)+4). 1-byte vars: LDA/32-store
(0x32 literal!), MUL RHS interleave. bare SKIP = skip(1). Econd on
parenthesized items. bin(p>15) = DR NOT-IMP mirror reject.
